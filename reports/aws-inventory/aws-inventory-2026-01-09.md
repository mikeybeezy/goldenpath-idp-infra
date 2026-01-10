# AWS Inventory Report (2026-01-09T23:55:30Z)

## Summary
- Total resources: 33
- Tagged: 31
- Untagged: 2
- Tag violations: 30

## Notes
- Tagging API only returns resources that are tagged or were previously tagged.
- Resources that have never been tagged may not appear.

## Missing Tags (sample)
- REDACTED / eu-west-2 / cloudformation / arn:aws:cloudformation:eu-west-2:REDACTED:stack/eksctl-devops-test-cluster-cluster/0295e760-df58-11f0-94ab-0a5259aeb55d — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:instance/i-02c3f30e4da9835e7 — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-0a47288eafb977e8d — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-0327f0cf0ba0d9821 — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:vpc/vpc-0fabff1a751926ada — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / elasticloadbalancing / arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-83562ef1e8/93e16c82f0466f3d — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / elasticloadbalancing / arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-5944eeee31/002e4ee4c7f7869c — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / dynamodb / arn:aws:dynamodb:eu-west-2:REDACTED:table/goldenpath-idp-dev-db — missing: Owner, Environment
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:instance/i-0f1000de1f4b16da9 — missing: Owner, Environment, Project
- REDACTED / eu-west-2 / ec2 / arn:aws:ec2:eu-west-2:REDACTED:instance/i-0afb3e96ff95cc3c8 — missing: Owner, Environment, Project

## Tag Violations (sample)
- None

## Resource List
| Account | Region | Service | Resource | Owner | Environment | Project | Cost Center | ARN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REDACTED | eu-west-2 | cloudformation | 0295e760-df58-11f0-94ab-0a5259aeb55d |  |  |  |  | arn:aws:cloudformation:eu-west-2:REDACTED:stack/eksctl-devops-test-cluster-cluster/0295e760-df58-11f0-94ab-0a5259aeb55d |
| REDACTED | eu-west-2 | ec2 | i-02c3f30e4da9835e7 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-02c3f30e4da9835e7 |
| REDACTED | eu-west-2 | ec2 | subnet-0a47288eafb977e8d |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-0a47288eafb977e8d |
| REDACTED | eu-west-2 | ec2 | subnet-0327f0cf0ba0d9821 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-0327f0cf0ba0d9821 |
| REDACTED | eu-west-2 | ec2 | vpc-0fabff1a751926ada |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:vpc/vpc-0fabff1a751926ada |
| REDACTED | eu-west-2 | elasticloadbalancing | 93e16c82f0466f3d |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-83562ef1e8/93e16c82f0466f3d |
| REDACTED | eu-west-2 | elasticloadbalancing | 002e4ee4c7f7869c |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-5944eeee31/002e4ee4c7f7869c |
| REDACTED | eu-west-2 | dynamodb | goldenpath-idp-dev-db |  |  | goldenpath-idp |  | arn:aws:dynamodb:eu-west-2:REDACTED:table/goldenpath-idp-dev-db |
| REDACTED | eu-west-2 | ec2 | i-0f1000de1f4b16da9 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-0f1000de1f4b16da9 |
| REDACTED | eu-west-2 | ec2 | i-0797141a8096f60b4 | platform-team | dev | goldenpath-idp |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-0797141a8096f60b4 |
| REDACTED | eu-west-2 | ec2 | i-0afb3e96ff95cc3c8 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-0afb3e96ff95cc3c8 |
| REDACTED | eu-west-2 | ec2 | igw-0f40d4eb861e3c421 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:internet-gateway/igw-0f40d4eb861e3c421 |
| REDACTED | eu-west-2 | ec2 | rtb-07b270a34baf6cb71 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:route-table/rtb-07b270a34baf6cb71 |
| REDACTED | eu-west-2 | ecr | new-wp-reg2 | platform-team | dev | goldenpath-idp |  | arn:aws:ecr:eu-west-2:REDACTED:repository/new-wp-reg2 |
| REDACTED | eu-west-2 | ecr | new-app-16 | platform-team | dev | goldenpath-idp |  | arn:aws:ecr:eu-west-2:REDACTED:repository/new-app-16 |
| REDACTED | eu-west-2 | elasticloadbalancing | b6fded0e71616a1b |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-ac023efb05/b6fded0e71616a1b |
| REDACTED | eu-west-2 | elasticloadbalancing | 227470327add6447 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-41aca50275/227470327add6447 |
| REDACTED | eu-west-2 | s3 | scaletific-tf-example-bucket |  |  |  |  | arn:aws:s3::REDACTED:scaletific-tf-example-bucket |
| REDACTED | eu-west-2 | ec2 | i-060833062687fc3a6 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-060833062687fc3a6 |
| REDACTED | eu-west-2 | ec2 | i-0203205294d028ced |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-0203205294d028ced |
| REDACTED | eu-west-2 | ec2 | sg-0372a187d2c06c58d |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:security-group/sg-0372a187d2c06c58d |
| REDACTED | eu-west-2 | elasticloadbalancing | fbf458a3de5705b2 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-d1199ec405/fbf458a3de5705b2 |
| REDACTED | eu-west-2 | elasticloadbalancing | f25b96c176b0a975 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-d5288aeef4/f25b96c176b0a975 |
| REDACTED | eu-west-2 | elasticloadbalancing | ab63ca4d28d0a9e3 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-4a2bc5e66f/ab63ca4d28d0a9e3 |
| REDACTED | eu-west-2 | elasticloadbalancing | 9074add92cfd8b30 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-343df266be/9074add92cfd8b30 |
| REDACTED | eu-west-2 | events | AutoScalingManagedRule |  |  |  |  | arn:aws:events:eu-west-2:REDACTED:rule/AutoScalingManagedRule |
| REDACTED | eu-west-2 | ec2 | i-098732f13286d01c5 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-098732f13286d01c5 |
| REDACTED | eu-west-2 | ec2 | i-06a0025afa512d274 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:instance/i-06a0025afa512d274 |
| REDACTED | eu-west-2 | ec2 | rtb-0d3df8280459577bf |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:route-table/rtb-0d3df8280459577bf |
| REDACTED | eu-west-2 | ec2 | subnet-0f660ecc366ce4999 |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-0f660ecc366ce4999 |
| REDACTED | eu-west-2 | ec2 | subnet-06fefe7ffb40e67ca |  |  |  |  | arn:aws:ec2:eu-west-2:REDACTED:subnet/subnet-06fefe7ffb40e67ca |
| REDACTED | eu-west-2 | elasticloadbalancing | 33f09f42e5e45fe5 |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-ac64c6feae/33f09f42e5e45fe5 |
| REDACTED | eu-west-2 | elasticloadbalancing | 1d8c74272392143d |  |  |  |  | arn:aws:elasticloadbalancing:eu-west-2:REDACTED:targetgroup/k8s-kongsyst-devkongk-d5ef5ff115/1d8c74272392143d |