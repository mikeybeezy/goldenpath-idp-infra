"""
AWS Secrets Manager RDS PostgreSQL Single User Rotation Lambda

This Lambda function rotates database credentials stored in AWS Secrets Manager.
It uses the single-user rotation strategy where the same user's password is updated.

Based on AWS Secrets Manager rotation template:
https://github.com/aws-samples/aws-secrets-manager-rotation-lambdas

Flow:
1. createSecret: Generate new password, store as AWSPENDING
2. setSecret: Update database user password
3. testSecret: Verify new credentials work
4. finishSecret: Move AWSPENDING to AWSCURRENT
"""

import boto3
import json
import logging
import os
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Secrets Manager rotation Lambda handler.

    Args:
        event: Lambda event containing SecretId, ClientRequestToken, Step
        context: Lambda context
    """
    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    # Setup the client
    service_client = boto3.client(
        "secretsmanager", endpoint_url=os.environ.get("SECRETS_MANAGER_ENDPOINT")
    )

    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    if not metadata["RotationEnabled"]:
        logger.error(f"Secret {arn} is not enabled for rotation")
        raise ValueError(f"Secret {arn} is not enabled for rotation")

    versions = metadata["VersionIdsToStages"]
    if token not in versions:
        logger.error(
            f"Secret version {token} has no stage for rotation of secret {arn}"
        )
        raise ValueError(
            f"Secret version {token} has no stage for rotation of secret {arn}"
        )

    if "AWSCURRENT" in versions[token]:
        logger.info(
            f"Secret version {token} already set as AWSCURRENT for secret {arn}"
        )
        return

    elif "AWSPENDING" not in versions[token]:
        logger.error(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}"
        )
        raise ValueError(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}"
        )

    # Call the appropriate step
    if step == "createSecret":
        create_secret(service_client, arn, token)
    elif step == "setSecret":
        set_secret(service_client, arn, token)
    elif step == "testSecret":
        test_secret(service_client, arn, token)
    elif step == "finishSecret":
        finish_secret(service_client, arn, token)
    else:
        raise ValueError(f"Invalid step parameter: {step}")


def create_secret(service_client, arn, token):
    """
    Create a new secret version with a generated password.
    """
    # Check if secret already exists
    current_dict = get_secret_dict(service_client, arn, "AWSCURRENT")

    # Generate a new password
    passwd = service_client.get_random_password(
        PasswordLength=32, ExcludeCharacters="/@\"'\\", ExcludePunctuation=True
    )

    # Update the secret dict with new password
    current_dict["password"] = passwd["RandomPassword"]
    current_dict["postgres-password"] = passwd["RandomPassword"]
    current_dict["admin-password"] = passwd["RandomPassword"]

    # Put the new secret version
    service_client.put_secret_value(
        SecretId=arn,
        ClientRequestToken=token,
        SecretString=json.dumps(current_dict),
        VersionStages=["AWSPENDING"],
    )
    logger.info(f"createSecret: Successfully created new secret version for {arn}")


def set_secret(service_client, arn, token):
    """
    Set the pending secret in the database.
    """
    # Get the pending secret
    pending_dict = get_secret_dict(service_client, arn, "AWSPENDING", token)

    # Get the current secret for master credentials
    current_dict = get_secret_dict(service_client, arn, "AWSCURRENT")

    # Connect to database and update password
    conn = get_connection(current_dict)
    try:
        with conn.cursor() as cursor:
            # Use current credentials to change the password
            cursor.execute(
                "ALTER USER %s WITH PASSWORD %s",
                (pending_dict["username"], pending_dict["password"]),
            )
            conn.commit()
            logger.info(
                f"setSecret: Successfully set password for user {pending_dict['username']}"
            )
    finally:
        conn.close()


def test_secret(service_client, arn, token):
    """
    Test the pending secret by connecting to the database.
    """
    pending_dict = get_secret_dict(service_client, arn, "AWSPENDING", token)

    # Try to connect with the new password
    conn = get_connection(pending_dict)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info(f"testSecret: Successfully tested new credentials for {arn}")
    finally:
        conn.close()


def finish_secret(service_client, arn, token):
    """
    Finish the rotation by marking the pending secret as current.
    """
    # Get the current version
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None
    for version, stages in metadata["VersionIdsToStages"].items():
        if "AWSCURRENT" in stages:
            if version == token:
                logger.info(
                    f"finishSecret: Version {token} already marked as AWSCURRENT for {arn}"
                )
                return
            current_version = version
            break

    # Move the staging labels
    service_client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    logger.info(
        f"finishSecret: Successfully set AWSCURRENT stage to version {token} for secret {arn}"
    )


def get_secret_dict(service_client, arn, stage, token=None):
    """
    Get the secret dictionary for the specified stage.
    """
    if token:
        secret = service_client.get_secret_value(
            SecretId=arn, VersionId=token, VersionStage=stage
        )
    else:
        secret = service_client.get_secret_value(SecretId=arn, VersionStage=stage)
    return json.loads(secret["SecretString"])


def get_connection(secret_dict):
    """
    Get a database connection using the provided credentials.
    """
    return psycopg2.connect(
        host=secret_dict["host"],
        port=int(secret_dict["port"]),
        user=secret_dict["username"],
        password=secret_dict["password"],
        database=secret_dict["dbname"],
        sslmode="require",
        connect_timeout=5,
    )
