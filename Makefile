TF_BIN ?= terraform
ENV ?= dev
ENV_DIR := envs/$(ENV)
CLUSTER ?= goldenpath-dev-eks-dec
REGION ?= eu-west-2
KONG_NAMESPACE ?= kong-system
NODE_INSTANCE_TYPE ?= t3.small
ENV_NAME ?= $(ENV)
SKIP_CERT_MANAGER_VALIDATION ?= true
SKIP_ARGO_SYNC_WAIT ?= true
COMPACT_OUTPUT ?= false
SCALE_DOWN_AFTER_BOOTSTRAP ?= false
TF_DIR ?= $(ENV_DIR)
BUILD_ID ?=
NODEGROUP ?=

# Usage:
#   make init ENV=dev     # terraform -chdir=envs/dev init
#   make plan ENV=staging # terraform -chdir=envs/staging plan
#   make apply ENV=prod   # terraform -chdir=envs/prod apply
#   make destroy ENV=dev
#   TF_VAR_owner_team=platform-team make plan ENV=dev
#   make bootstrap CLUSTER=goldenpath-dev-eks REGION=eu-west-2
#   make pre-destroy-cleanup CLUSTER=goldenpath-dev-eks REGION=eu-west-2
#   make cleanup-orphans BUILD_ID=<id> REGION=eu-west-2
#   make cleanup-iam
#   make drain-nodegroup NODEGROUP=dev-default
#   make teardown CLUSTER=goldenpath-dev-eks REGION=eu-west-2

.PHONY: init plan apply destroy fmt validate bootstrap pre-destroy-cleanup cleanup-orphans cleanup-iam drain-nodegroup teardown set-cluster-name help

init:
	$(TF_BIN) -chdir=$(ENV_DIR) init

plan:
	$(TF_BIN) -chdir=$(ENV_DIR) plan

apply:
	$(TF_BIN) -chdir=$(ENV_DIR) apply

destroy:
	$(TF_BIN) -chdir=$(ENV_DIR) destroy

fmt:
	$(TF_BIN) fmt -recursive

validate:
	$(TF_BIN) -chdir=$(ENV_DIR) validate

bootstrap:
	SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	ENV_NAME=$(ENV_NAME) \
	SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	TF_DIR=$(TF_DIR) \
	bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh $(CLUSTER) $(REGION) $(KONG_NAMESPACE)

pre-destroy-cleanup:
	bash bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh $(CLUSTER) $(REGION) --yes

cleanup-orphans:
	DRY_RUN=false bash bootstrap/60_tear_down_clean_up/cleanup-orphans.sh $(BUILD_ID) $(REGION)

cleanup-iam:
	bash bootstrap/60_tear_down_clean_up/cleanup-iam.sh --yes

drain-nodegroup:
	bash bootstrap/60_tear_down_clean_up/drain-nodegroup.sh $(NODEGROUP)

teardown:
	TEARDOWN_CONFIRM=true \
	TF_DIR=$(TF_DIR) \
	CLEANUP_ORPHANS=false \
	bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh $(CLUSTER) $(REGION)

set-cluster-name:
	@bash -c '\
	tfvars="$(ENV_DIR)/terraform.tfvars"; \
	if [ ! -f "$$tfvars" ]; then echo "Missing $$tfvars" >&2; exit 1; fi; \
	current=$$(sed -nE "s/^[[:space:]]*cluster_name[[:space:]]*=[[:space:]]*\"([^\"]*)\".*/\\1/p" "$$tfvars" | head -n1); \
	if [ -n "$$current" ]; then echo "cluster_name already set to $$current in $$tfvars"; exit 0; fi; \
	read -r -p "Enter cluster name: " name; \
	if [ -z "$$name" ]; then echo "cluster_name is required." >&2; exit 1; fi; \
	if grep -Eq "^[[:space:]]*#?[[:space:]]*cluster_name[[:space:]]*=" "$$tfvars"; then \
	  perl -pi -e "s/^([[:space:]]*)#?[[:space:]]*cluster_name[[:space:]]*=.*/\\1cluster_name = \\\"$$name\\\"/" "$$tfvars"; \
	else \
	  echo "  cluster_name = \\\"$$name\\\"" >> "$$tfvars"; \
	fi; \
	echo "cluster_name set to $$name in $$tfvars"; \
	'

help:
	@echo "Targets:"
	@echo "  make init ENV=dev"
	@echo "  make plan ENV=dev"
	@echo "  make apply ENV=dev"
	@echo "  make destroy ENV=dev"
	@echo "  TF_VAR_owner_team=platform-team make plan ENV=dev"
	@echo "  make fmt"
	@echo "  make validate ENV=dev"
	@echo "  make bootstrap CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make pre-destroy-cleanup CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make cleanup-orphans BUILD_ID=<id> REGION=eu-west-2"
	@echo "  make cleanup-iam"
	@echo "  make drain-nodegroup NODEGROUP=dev-default"
	@echo "  make teardown CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make set-cluster-name ENV=dev"
	@echo ""
	@echo "Bootstrap flags:"
	@echo "  NODE_INSTANCE_TYPE, ENV_NAME, SKIP_CERT_MANAGER_VALIDATION, SKIP_ARGO_SYNC_WAIT,"
	@echo "  COMPACT_OUTPUT, SCALE_DOWN_AFTER_BOOTSTRAP, TF_DIR, KONG_NAMESPACE"
