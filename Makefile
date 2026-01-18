TF_BIN ?= terraform
ENV ?= dev
ENV_DIR := envs/$(ENV)

# Defaults
REGION ?= eu-west-2
KONG_NAMESPACE ?= kong-system
NODE_INSTANCE_TYPE ?= t3.small
ENV_NAME ?= $(ENV)
SKIP_CERT_MANAGER_VALIDATION ?= true
SKIP_ARGO_SYNC_WAIT ?= true
COMPACT_OUTPUT ?= false
SCALE_DOWN_AFTER_BOOTSTRAP ?= false
BOOTSTRAP_VERSION ?= v3
TF_DIR ?= $(ENV_DIR)
NODEGROUP ?=
CLEANUP_ORPHANS ?= false
ALLOW_REUSE_BUILD_ID ?= false
S3_REQUEST ?=
S3_OUTPUT_ROOT ?= envs
S3_STATE_BUCKET ?=
S3_LOCK_TABLE ?=
S3_STATE_REGION ?= $(REGION)

# Derived Variables
CLUSTER_BASE ?= $(shell awk -F'=' '/^[[:space:]]*cluster_name[[:space:]]*=/{gsub(/"/,"",$$2);gsub(/[[:space:]]/,"",$$2);print $$2;exit}' $(ENV_DIR)/terraform.tfvars 2>/dev/null)
BUILD_ID ?= $(shell awk -F'=' '/^build_id[[:space:]]*=/{gsub(/"/,"",$$2);gsub(/[[:space:]]/,"",$$2);print $$2;exit}' $(ENV_DIR)/terraform.tfvars 2>/dev/null)

# Dynamic Cluster Discovery:
# Try to find the cluster by BuildId tag. If found, use that name.
# This decouples Makefile from Terraform naming conventions.
CLUSTER_ARN := $(shell aws resourcegroupstaggingapi get-resources --tag-filters Key=BuildId,Values=$(BUILD_ID) --resource-type-filters eks:cluster --region $(REGION) --query 'ResourceTagMappingList[0].ResourceARN' --output text 2>/dev/null)
CLUSTER_FOUND := $(notdir $(CLUSTER_ARN))

# Use found cluster, or fallback to predicted name (prefix-buildid)
CLUSTER ?= $(if $(CLUSTER_FOUND),$(CLUSTER_FOUND),$(CLUSTER_BASE)-$(BUILD_ID))


ifeq ($(BOOTSTRAP_VERSION),v1)
BOOTSTRAP_SCRIPT := bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh
else ifeq ($(BOOTSTRAP_VERSION),v2)
BOOTSTRAP_SCRIPT := bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v2.sh
else ifeq ($(BOOTSTRAP_VERSION),v3)
BOOTSTRAP_SCRIPT := bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
else
$(error BOOTSTRAP_VERSION must be v1, v2, or v3)
endif

define require_build_id
	@if [ -z "$(BUILD_ID)" ]; then \
	  echo "BUILD_ID is required. Set build_id in $(ENV_DIR)/terraform.tfvars or pass BUILD_ID=..."; \
	  exit 1; \
	fi
	@if ! echo "$(BUILD_ID)" | grep -Eq '^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$$'; then \
	  echo "BUILD_ID must match dd-mm-yy-NN (example: 28-12-25-01)."; \
	  exit 1; \
	fi
	@if [ -f docs/build-timings.csv ] && [ "$(ALLOW_REUSE_BUILD_ID)" != "true" ]; then \
	  if awk -F',' -v env="$(ENV)" -v id="$(BUILD_ID)" 'NR>1 && $$4==env && $$5==id {found=1} END{exit found?0:1}' docs/build-timings.csv; then \
	    echo "BUILD_ID $(BUILD_ID) already exists for $(ENV). Use a new ID or set ALLOW_REUSE_BUILD_ID=true to reuse."; \
	    exit 1; \
	  fi; \
	fi
endef

define require_build_id_allow_reuse
	@if [ -z "$(BUILD_ID)" ]; then \
	  echo "BUILD_ID is required. Set build_id in $(ENV_DIR)/terraform.tfvars or pass BUILD_ID=..."; \
	  exit 1; \
	fi
	@if ! echo "$(BUILD_ID)" | grep -Eq '^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$$'; then \
	  echo "BUILD_ID must match dd-mm-yy-NN (example: 28-12-25-01)."; \
	  exit 1; \
	fi
endef

define require_s3_request
	@if [ -z "$(S3_REQUEST)" ]; then \
	  echo "S3_REQUEST is required. Example: make s3-apply S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml"; \
	  exit 1; \
	fi
	@if [ ! -f "$(S3_REQUEST)" ]; then \
	  echo "S3_REQUEST not found: $(S3_REQUEST)"; \
	  exit 1; \
	fi
endef

define require_s3_backend
	@if [ -z "$(S3_STATE_BUCKET)" ] || [ -z "$(S3_LOCK_TABLE)" ]; then \
	  echo "S3_STATE_BUCKET and S3_LOCK_TABLE are required."; \
	  echo "Example: make s3-apply S3_REQUEST=... S3_STATE_BUCKET=goldenpath-idp-dev-bucket S3_LOCK_TABLE=goldenpath-idp-dev-locks"; \
	  exit 1; \
	fi
endef

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

.PHONY: init plan apply destroy build timed-apply timed-build timed-bootstrap timed-teardown reliability-metrics fmt validate deploy _phase1-infrastructure _phase2-bootstrap _phase3-verify bootstrap bootstrap-only pre-destroy-cleanup cleanup-orphans cleanup-iam drain-nodegroup teardown teardown-resume set-cluster-name help s3-validate s3-generate s3-apply rds-init rds-plan rds-apply rds-status rds-provision rds-provision-dry-run rds-provision-auto rds-provision-auto-dry-run apply-persistent bootstrap-persistent deploy-persistent teardown-persistent

init:
	$(TF_BIN) -chdir=$(ENV_DIR) init

plan:
	$(TF_BIN) -chdir=$(ENV_DIR) plan

apply:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	build_id=$(BUILD_ID); \
	log="logs/build-timings/apply-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Terraform apply output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

destroy:
	$(TF_BIN) -chdir=$(ENV_DIR) destroy

################################################################################
# S3 Request (Contract-Driven)
################################################################################

s3-validate:
	$(call require_s3_request)
	python3 scripts/s3_request_parser.py \
		--mode validate \
		--input-files "$(S3_REQUEST)"

s3-generate:
	$(call require_s3_request)
	python3 scripts/s3_request_parser.py \
		--mode generate \
		--input-files "$(S3_REQUEST)" \
		--output-root "$(S3_OUTPUT_ROOT)"

s3-apply:
	$(call require_s3_request)
	$(call require_s3_backend)
	@bash -c '\
	set -euo pipefail; \
	python3 scripts/s3_request_parser.py --mode validate --input-files "$(S3_REQUEST)"; \
	python3 scripts/s3_request_parser.py --mode generate --input-files "$(S3_REQUEST)" --output-root "$(S3_OUTPUT_ROOT)"; \
	S3_ENV=$$(python3 -c "import sys, yaml; d=yaml.safe_load(open(sys.argv[1])) or {}; print(d.get(\"environment\") or d.get(\"metadata\", {}).get(\"environment\"))" "$(S3_REQUEST)"); \
	S3_ID=$$(python3 -c "import sys, yaml; d=yaml.safe_load(open(sys.argv[1])) or {}; print(d.get(\"id\") or d.get(\"metadata\", {}).get(\"id\"))" "$(S3_REQUEST)"); \
	if [ -z "$$S3_ENV" ] || [ -z "$$S3_ID" ]; then \
	  echo "Failed to resolve environment or id from $(S3_REQUEST)"; \
	  exit 1; \
	fi; \
	STATE_KEY="envs/$${S3_ENV}/s3/$${S3_ID}/terraform.tfstate"; \
	$(TF_BIN) -chdir=envs/$${S3_ENV} init \
	  -backend-config="bucket=$(S3_STATE_BUCKET)" \
	  -backend-config="key=$${STATE_KEY}" \
	  -backend-config="region=$(S3_STATE_REGION)" \
	  -backend-config="dynamodb_table=$(S3_LOCK_TABLE)" \
	  -backend-config="encrypt=true"; \
	$(TF_BIN) -chdir=envs/$${S3_ENV} apply -auto-approve -input=false -no-color \
	  -var-file="s3/generated/$${S3_ID}.auto.tfvars.json"; \
	'

build:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	set -e; \
	build_id=$(BUILD_ID); \
	log="logs/build-timings/build-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Build output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply; \
	SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	ENV_NAME=$(ENV_NAME) \
	SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	ENABLE_TF_K8S_RESOURCES=$(ENABLE_TF_K8S_RESOURCES) \
	SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	TF_DIR=$(TF_DIR) \
	bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

timed-apply:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	set -e; \
	start=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	start_epoch=$$(date -u +%s); \
	build_id=$(BUILD_ID); \
	log="logs/build-timings/$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Terraform apply output streaming; full log at $$log"; \
	( time $(TF_BIN) -chdir=$(ENV_DIR) apply ) 2>&1 | tee "$$log"; \
	status=$${PIPESTATUS[0]}; \
	end_epoch=$$(date -u +%s); \
	duration=$$((end_epoch-start_epoch)); \
	end=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "$$start,$$end,terraform-apply,$(ENV),$$build_id,$$duration,$$status,, $$log" | sed "s/, /,/g" >> docs/build-timings.csv; \
	exit $$status; \
	'

timed-build:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	set -e; \
	start=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	start_epoch=$$(date -u +%s); \
	build_id=$(BUILD_ID); \
	flags="ENV_NAME=$${ENV_NAME} NODE_INSTANCE_TYPE=$${NODE_INSTANCE_TYPE} SKIP_ARGO_SYNC_WAIT=$${SKIP_ARGO_SYNC_WAIT} SKIP_CERT_MANAGER_VALIDATION=$${SKIP_CERT_MANAGER_VALIDATION} COMPACT_OUTPUT=$${COMPACT_OUTPUT} ENABLE_TF_K8S_RESOURCES=$${ENABLE_TF_K8S_RESOURCES} SCALE_DOWN_AFTER_BOOTSTRAP=$${SCALE_DOWN_AFTER_BOOTSTRAP}"; \
	log="logs/build-timings/build-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Build output streaming; full log at $$log"; \
	( time $(TF_BIN) -chdir=$(ENV_DIR) apply && \
	  SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	  NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	  ENV_NAME=$(ENV_NAME) \
	  SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	  COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	  ENABLE_TF_K8S_RESOURCES=$(ENABLE_TF_K8S_RESOURCES) \
	  SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	  TF_DIR=$(TF_DIR) \
	  bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE) ) 2>&1 | tee "$$log"; \
	status=$${PIPESTATUS[0]}; \
	end_epoch=$$(date -u +%s); \
	duration=$$((end_epoch-start_epoch)); \
	end=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "$$start,$$end,build,$(ENV),$${build_id},$${duration},$${status},\"$$flags\",$$log" >> docs/build-timings.csv; \
	exit $$status; \
	'

fmt:
	$(TF_BIN) fmt -recursive

validate:
	$(TF_BIN) -chdir=$(ENV_DIR) validate

################################################################################
# Seamless Deployment (Two-Phase with Single Command)
################################################################################

deploy:
	$(call require_build_id)
	@echo "🚀 Starting seamless deployment for $(ENV) with BUILD_ID=$(BUILD_ID)"
	@$(MAKE) _phase1-infrastructure ENV=$(ENV) BUILD_ID=$(BUILD_ID)
	@$(MAKE) rds-provision-auto ENV=$(ENV) BUILD_ID=$(BUILD_ID)
	@$(MAKE) _phase2-bootstrap ENV=$(ENV) BUILD_ID=$(BUILD_ID)
	@$(MAKE) _phase3-verify ENV=$(ENV)
	@echo "✅ Deployment complete! Cluster ready."

_phase1-infrastructure:
	$(call require_build_id)
	@echo "📦 Phase 1: Building infrastructure..."
	@mkdir -p logs/build-timings
	@bash -c 'set -e; \
	log="logs/build-timings/terraform-apply-$(ENV)-$(CLUSTER)-$(BUILD_ID)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Infrastructure apply output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply \
		-var="build_id=$(BUILD_ID)" \
		-var="enable_k8s_resources=true" \
		-var="apply_kubernetes_addons=false" \
		-var="allow_build_id_reuse=$(ALLOW_REUSE_BUILD_ID)" \
		-auto-approve 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'
	@bash scripts/record-build-timing.sh $(ENV) $(BUILD_ID) terraform-apply
	@echo "✅ Infrastructure ready (including service accounts)"

_phase2-bootstrap:
	$(call require_build_id_allow_reuse)
	@echo "🔧 Phase 2: Bootstrapping platform..."
	@mkdir -p logs/build-timings
	@bash -c 'set -e; \
	log="logs/build-timings/bootstrap-$(ENV)-$(CLUSTER)-$(BUILD_ID)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Bootstrap output streaming; full log at $$log"; \
	SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	ENV_NAME=$(ENV_NAME) \
	ENABLE_TF_K8S_RESOURCES=false \
	CONFIRM_TF_APPLY=true \
	TF_DIR=$(ENV_DIR) \
	bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'
	@bash scripts/record-build-timing.sh $(ENV) $(BUILD_ID) bootstrap
	@echo "✅ Platform bootstrapped"

_phase3-verify:
	@echo "✅ Phase 3: Verifying deployment..."
	@kubectl get nodes || echo "⚠️  Warning: Could not verify nodes"
	@kubectl -n argocd get applications || echo "⚠️  Warning: Could not verify ArgoCD applications"
	@echo "✅ All systems operational"

bootstrap:
	$(call require_build_id_allow_reuse)
	@mkdir -p logs/build-timings
	@bash -c '\
	build_id=$(BUILD_ID); \
	log="logs/build-timings/bootstrap-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Bootstrap output streaming; full log at $$log"; \
	SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	ENV_NAME=$(ENV_NAME) \
	SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	TF_DIR=$(TF_DIR) \
	bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

bootstrap-only: bootstrap

pre-destroy-cleanup:
	bash bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh $(CLUSTER) $(REGION) --yes

cleanup-orphans:
	DRY_RUN=false bash bootstrap/60_tear_down_clean_up/cleanup-orphans.sh $(BUILD_ID) $(REGION)

cleanup-iam:
	bash bootstrap/60_tear_down_clean_up/cleanup-iam.sh --yes

drain-nodegroup:
	bash bootstrap/60_tear_down_clean_up/drain-nodegroup.sh $(NODEGROUP)

teardown:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	build_id=$(BUILD_ID); \
	script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh"; \
	case "$${TEARDOWN_VERSION:-v3}" in \
	  v3) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh";; \
	  v2) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh";; \
	  *) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh";; \
	esac; \
	log="logs/build-timings/teardown-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v3})"; \
	TEARDOWN_CONFIRM=true \
	TF_DIR=$(TF_DIR) \
	TF_AUTO_APPROVE=true \
	REMOVE_K8S_SA_FROM_STATE=true \
	CLEANUP_ORPHANS=$(CLEANUP_ORPHANS) \
	bash "$$script" $(CLUSTER) $(REGION) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

teardown-resume:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	build_id=$(BUILD_ID); \
	script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh"; \
	case "$${TEARDOWN_VERSION:-v3}" in \
	  v3) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh";; \
	  v2) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh";; \
	  *) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh";; \
	esac; \
	log="logs/build-timings/teardown-resume-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown resume output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v3})"; \
	TEARDOWN_CONFIRM=true \
	TF_DIR=$(TF_DIR) \
	TF_AUTO_APPROVE=true \
	REMOVE_K8S_SA_FROM_STATE=true \
	REQUIRE_KUBE_FOR_TF_DESTROY=false \
	TF_DESTROY_FALLBACK_AWS=true \
	CLEANUP_ORPHANS=$(CLEANUP_ORPHANS) \
	bash "$$script" $(CLUSTER) $(REGION) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

timed-teardown:
	$(call require_build_id)
	@mkdir -p logs/build-timings
	@bash -c '\
	set -e; \
	start=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	start_epoch=$$(date -u +%s); \
	build_id=$(BUILD_ID); \
	script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh"; \
	case "$${TEARDOWN_VERSION:-v3}" in \
	  v3) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh";; \
	  v2) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh";; \
	  *) script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh";; \
	esac; \
	log="logs/build-timings/teardown-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v3})"; \
	( time TEARDOWN_CONFIRM=true \
	  TF_DIR=$(TF_DIR) \
	  TF_AUTO_APPROVE=true \
	  REMOVE_K8S_SA_FROM_STATE=true \
	  CLEANUP_ORPHANS=$(CLEANUP_ORPHANS) \
	  bash "$$script" $(CLUSTER) $(REGION) ) 2>&1 | tee "$$log"; \
	status=$${PIPESTATUS[0]}; \
	end_epoch=$$(date -u +%s); \
	duration=$$((end_epoch-start_epoch)); \
	end=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "$$start,$$end,teardown,$(ENV),$${build_id},$${duration},$${status},,$$log" >> docs/build-timings.csv; \
	exit $$status; \
	'

timed-bootstrap:
	$(call require_build_id_allow_reuse)
	@mkdir -p logs/build-timings
	@bash -c '\
	set -e; \
	start=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	start_epoch=$$(date -u +%s); \
	build_id=$(BUILD_ID); \
	flags="ENV_NAME=$${ENV_NAME} NODE_INSTANCE_TYPE=$${NODE_INSTANCE_TYPE} SKIP_ARGO_SYNC_WAIT=$${SKIP_ARGO_SYNC_WAIT} SKIP_CERT_MANAGER_VALIDATION=$${SKIP_CERT_MANAGER_VALIDATION} COMPACT_OUTPUT=$${COMPACT_OUTPUT} ENABLE_TF_K8S_RESOURCES=$${ENABLE_TF_K8S_RESOURCES} SCALE_DOWN_AFTER_BOOTSTRAP=$${SCALE_DOWN_AFTER_BOOTSTRAP}"; \
	log="logs/build-timings/bootstrap-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Bootstrap output streaming; full log at $$log"; \
	( time SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	  NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	  ENV_NAME=$(ENV_NAME) \
	  SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	  COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	  ENABLE_TF_K8S_RESOURCES=$(ENABLE_TF_K8S_RESOURCES) \
	  SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	  TF_DIR=$(TF_DIR) \
	  bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE) ) 2>&1 | tee "$$log"; \
	status=$${PIPESTATUS[0]}; \
	end_epoch=$$(date -u +%s); \
	duration=$$((end_epoch-start_epoch)); \
	end=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "$$start,$$end,bootstrap,$(ENV),$${build_id},$${duration},$${status},\"$$flags\",$$log" >> docs/build-timings.csv; \
	exit $$status; \
	'

reliability-metrics:
	@bash scripts/reliability-metrics.sh

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

################################################################################
# Platform RDS - Standalone Bounded Context
#
# RDS is persistent infrastructure that survives cluster rebuilds.
# IMPORTANT: There is NO rds-destroy target. RDS deletion requires console
# intervention per ADR-0158. See runbook RB-0016 for break-glass procedure.
#
# Deployment order:
#   1. make rds-apply ENV=dev           # Deploy RDS first
#   2. make apply ENV=dev BUILD_ID=xx   # Then deploy EKS cluster
#   3. make bootstrap ENV=dev           # Then bootstrap
################################################################################

RDS_ENV_DIR := envs/$(ENV)-rds

rds-init:
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment directory not found: $(RDS_ENV_DIR)"; \
		echo "Available: $$(ls -d envs/*-rds 2>/dev/null || echo 'none')"; \
		exit 1; \
	fi
	$(TF_BIN) -chdir=$(RDS_ENV_DIR) init

rds-plan:
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment directory not found: $(RDS_ENV_DIR)"; \
		exit 1; \
	fi
	$(TF_BIN) -chdir=$(RDS_ENV_DIR) plan

rds-apply:
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment directory not found: $(RDS_ENV_DIR)"; \
		exit 1; \
	fi
	@echo "Applying Platform RDS for $(ENV)..."
	@echo "NOTE: RDS has deletion_protection=true and prevent_destroy lifecycle."
	@echo "      There is NO rds-destroy target. See RB-0016 for deletion procedure."
	@mkdir -p logs/build-timings
	@bash -c '\
	log="logs/build-timings/rds-apply-$(ENV)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "RDS apply output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(RDS_ENV_DIR) apply 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

rds-status:
	@echo "Platform RDS Status for $(ENV)"
	@echo "================================"
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment not configured: $(RDS_ENV_DIR)"; \
		exit 1; \
	fi
	@$(TF_BIN) -chdir=$(RDS_ENV_DIR) output -json 2>/dev/null | jq -r '. | to_entries[] | "\(.key): \(.value.value)"' 2>/dev/null || echo "Run 'make rds-init ENV=$(ENV)' first"

# Note: NO rds-destroy target exists by design.
# RDS deletion requires manual console intervention.
# See: docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md

################################################################################
# RDS User/Database Provisioning
#
# Provisions PostgreSQL roles and databases based on application_databases
# in terraform.tfvars. Requires AWS credentials with Secrets Manager access.
#
# Related: PRD-0001-rds-user-db-provisioning, ADR-0165
################################################################################

rds-provision:
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment directory not found: $(RDS_ENV_DIR)"; \
		exit 1; \
	fi
	@if [ "$(ENV)" != "dev" ] && [ "$(ALLOW_DB_PROVISION)" != "true" ]; then \
		echo "ERROR: ALLOW_DB_PROVISION=true required for non-dev environments"; \
		echo "Usage: ALLOW_DB_PROVISION=true make rds-provision ENV=$(ENV)"; \
		exit 1; \
	fi
	@echo "Provisioning RDS users and databases for $(ENV)..."
	python3 scripts/rds_provision.py \
		--env $(ENV) \
		--tfvars $(RDS_ENV_DIR)/terraform.tfvars \
		--master-secret goldenpath/$(ENV)/rds/master \
		--require-approval \
		--audit-output governance/$(ENV)/rds_provision_audit.csv \
		$(if $(BUILD_ID),--build-id $(BUILD_ID),) \
		$(if $(RUN_ID),--run-id $(RUN_ID),)

rds-provision-dry-run:
	@if [ ! -d "$(RDS_ENV_DIR)" ]; then \
		echo "RDS environment directory not found: $(RDS_ENV_DIR)"; \
		exit 1; \
	fi
	@echo "[DRY-RUN] Provisioning RDS users and databases for $(ENV)..."
	python3 scripts/rds_provision.py \
		--env $(ENV) \
		--tfvars $(RDS_ENV_DIR)/terraform.tfvars \
		--master-secret goldenpath/$(ENV)/rds/master \
		--dry-run

rds-provision-auto:
	@set -e; \
	coupled_tfvars="$(ENV_DIR)/terraform.tfvars"; \
	standalone_tfvars="$(RDS_ENV_DIR)/terraform.tfvars"; \
	mode="$(RDS_MODE)"; \
	coupled_enabled="false"; \
	if [ -f "$$coupled_tfvars" ]; then \
		coupled_enabled=$$(awk '\
			BEGIN{in=0} \
			/^[[:space:]]*rds_config[[:space:]]*=/ {in=1} \
			in && /^[[:space:]]*enabled[[:space:]]*=/ { \
				line=$$0; sub(/#.*/, "", line); split(line, a, "="); \
				gsub(/[[:space:]]/, "", a[2]); print a[2]; exit \
			} \
			in && /^[[:space:]]*}/ {in=0} \
		' "$$coupled_tfvars"); \
	fi; \
	if [ -z "$$mode" ] || [ "$$mode" = "auto" ]; then \
		if [ "$$coupled_enabled" = "true" ]; then \
			mode="coupled"; \
		elif [ -f "$$standalone_tfvars" ]; then \
			mode="standalone"; \
		else \
			echo "ERROR: Unable to detect RDS mode. Set RDS_MODE=coupled|standalone."; \
			exit 1; \
		fi; \
	fi; \
	if [ "$$mode" = "coupled" ]; then \
		tfvars="$$coupled_tfvars"; \
	elif [ "$$mode" = "standalone" ]; then \
		tfvars="$$standalone_tfvars"; \
	else \
		echo "ERROR: Invalid RDS_MODE=$$mode. Use coupled|standalone|auto."; \
		exit 1; \
	fi; \
	if [ ! -f "$$tfvars" ]; then \
		echo "ERROR: tfvars not found: $$tfvars"; \
		exit 1; \
	fi; \
	if [ "$(ENV)" != "dev" ] && [ "$(ALLOW_DB_PROVISION)" != "true" ]; then \
		echo "ERROR: ALLOW_DB_PROVISION=true required for non-dev environments"; \
		echo "Usage: ALLOW_DB_PROVISION=true make rds-provision-auto ENV=$(ENV)"; \
		exit 1; \
	fi; \
	region=$$(awk -F'=' '/^[[:space:]]*aws_region[[:space:]]*=/{gsub(/"|[[:space:]]/,"",$$2);print $$2;exit}' "$$tfvars"); \
	if [ -z "$$region" ]; then \
		echo "ERROR: aws_region not found in $$tfvars"; \
		exit 1; \
	fi; \
	echo "Provisioning RDS users and databases for $(ENV) (mode=$$mode)..."; \
	echo "Using tfvars: $$tfvars"; \
	python3 scripts/rds_provision.py \
		--env $(ENV) \
		--tfvars "$$tfvars" \
		--master-secret goldenpath/$(ENV)/rds/master \
		--region "$$region" \
		--require-approval \
		--audit-output governance/$(ENV)/rds_provision_audit.csv \
		$(if $(BUILD_ID),--build-id $(BUILD_ID),) \
		$(if $(RUN_ID),--run-id $(RUN_ID),)

rds-provision-auto-dry-run:
	@set -e; \
	coupled_tfvars="$(ENV_DIR)/terraform.tfvars"; \
	standalone_tfvars="$(RDS_ENV_DIR)/terraform.tfvars"; \
	mode="$(RDS_MODE)"; \
	coupled_enabled="false"; \
	if [ -f "$$coupled_tfvars" ]; then \
		coupled_enabled=$$(awk '\
			BEGIN{in=0} \
			/^[[:space:]]*rds_config[[:space:]]*=/ {in=1} \
			in && /^[[:space:]]*enabled[[:space:]]*=/ { \
				line=$$0; sub(/#.*/, "", line); split(line, a, "="); \
				gsub(/[[:space:]]/, "", a[2]); print a[2]; exit \
			} \
			in && /^[[:space:]]*}/ {in=0} \
		' "$$coupled_tfvars"); \
	fi; \
	if [ -z "$$mode" ] || [ "$$mode" = "auto" ]; then \
		if [ "$$coupled_enabled" = "true" ]; then \
			mode="coupled"; \
		elif [ -f "$$standalone_tfvars" ]; then \
			mode="standalone"; \
		else \
			echo "ERROR: Unable to detect RDS mode. Set RDS_MODE=coupled|standalone."; \
			exit 1; \
		fi; \
	fi; \
	if [ "$$mode" = "coupled" ]; then \
		tfvars="$$coupled_tfvars"; \
	elif [ "$$mode" = "standalone" ]; then \
		tfvars="$$standalone_tfvars"; \
	else \
		echo "ERROR: Invalid RDS_MODE=$$mode. Use coupled|standalone|auto."; \
		exit 1; \
	fi; \
	if [ ! -f "$$tfvars" ]; then \
		echo "ERROR: tfvars not found: $$tfvars"; \
		exit 1; \
	fi; \
	region=$$(awk -F'=' '/^[[:space:]]*aws_region[[:space:]]*=/{gsub(/"|[[:space:]]/,"",$$2);print $$2;exit}' "$$tfvars"); \
	if [ -z "$$region" ]; then \
		echo "ERROR: aws_region not found in $$tfvars"; \
		exit 1; \
	fi; \
	echo "[DRY-RUN] Provisioning RDS users and databases for $(ENV) (mode=$$mode)..."; \
	echo "Using tfvars: $$tfvars"; \
	python3 scripts/rds_provision.py \
		--env $(ENV) \
		--tfvars "$$tfvars" \
		--master-secret goldenpath/$(ENV)/rds/master \
		--region "$$region" \
		--dry-run

################################################################################
# Persistent Mode Targets
#
# For clusters with cluster_lifecycle=persistent, BUILD_ID is not used.
# These targets provide equivalent functionality without requiring BUILD_ID.
#
# State key: envs/<env>/terraform.tfstate (root level, not builds/<id>/)
# RDS: Allowed in persistent mode (fail-fast guard blocks ephemeral+RDS)
# Teardown: Uses ClusterName tag instead of BuildId tag
################################################################################

# Persistent cluster name - derived from tfvars or explicitly set
PERSISTENT_CLUSTER ?= $(shell awk -F'=' '/^[[:space:]]*cluster_name[[:space:]]*=/{gsub(/"/,"",$$2);gsub(/[[:space:]]/,"",$$2);print $$2;exit}' $(ENV_DIR)/terraform.tfvars 2>/dev/null)
PERSISTENT_CLUSTER_EFFECTIVE ?= $(if $(PERSISTENT_CLUSTER),$(PERSISTENT_CLUSTER),goldenpath-$(ENV)-eks)

apply-persistent:
	@echo "Applying persistent infrastructure for $(ENV)..."
	@echo "Cluster: $(PERSISTENT_CLUSTER_EFFECTIVE)"
	@echo "State key: envs/$(ENV)/terraform.tfstate"
	@mkdir -p logs/build-timings
	@bash -c '\
	log="logs/build-timings/apply-persistent-$(ENV)-$(PERSISTENT_CLUSTER_EFFECTIVE)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Terraform apply output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply \
		-var="cluster_lifecycle=persistent" \
		-var="enable_k8s_resources=true" \
		-var="apply_kubernetes_addons=false" \
		2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

bootstrap-persistent:
	@echo "Bootstrapping persistent cluster $(PERSISTENT_CLUSTER_EFFECTIVE)..."
	@mkdir -p logs/build-timings
	@bash -c '\
	log="logs/build-timings/bootstrap-persistent-$(ENV)-$(PERSISTENT_CLUSTER_EFFECTIVE)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Bootstrap output streaming; full log at $$log"; \
	SKIP_ARGO_SYNC_WAIT=$(SKIP_ARGO_SYNC_WAIT) \
	NODE_INSTANCE_TYPE=$(NODE_INSTANCE_TYPE) \
	ENV_NAME=$(ENV_NAME) \
	SKIP_CERT_MANAGER_VALIDATION=$(SKIP_CERT_MANAGER_VALIDATION) \
	COMPACT_OUTPUT=$(COMPACT_OUTPUT) \
	SCALE_DOWN_AFTER_BOOTSTRAP=$(SCALE_DOWN_AFTER_BOOTSTRAP) \
	TF_DIR=$(TF_DIR) \
	bash $(BOOTSTRAP_SCRIPT) $(PERSISTENT_CLUSTER_EFFECTIVE) $(REGION) $(KONG_NAMESPACE) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

deploy-persistent:
	@echo "Starting persistent deployment for $(ENV)"
	@echo "Cluster: $(PERSISTENT_CLUSTER_EFFECTIVE)"
	@$(MAKE) apply-persistent ENV=$(ENV) REGION=$(REGION)
	@$(MAKE) rds-provision-auto ENV=$(ENV) RDS_MODE=auto
	@$(MAKE) bootstrap-persistent ENV=$(ENV) REGION=$(REGION)
	@$(MAKE) _phase3-verify ENV=$(ENV)
	@echo "Persistent deployment complete!"

teardown-persistent:
	@if [ -z "$(ENV)" ]; then echo "ERROR: ENV required"; exit 1; fi
	@if [ -z "$(REGION)" ]; then echo "ERROR: REGION required"; exit 1; fi
	@if [ "$(CONFIRM_DESTROY)" != "yes" ]; then \
		echo ""; \
		echo "WARNING: This will destroy ALL persistent resources for $(ENV)"; \
		echo "         including EKS cluster, RDS (if coupled), and all related AWS resources."; \
		echo ""; \
		echo "Cluster: $(PERSISTENT_CLUSTER_EFFECTIVE)"; \
		echo "Region:  $(REGION)"; \
		echo "State:   envs/$(ENV)/terraform.tfstate"; \
		echo ""; \
		echo "To proceed, run:"; \
		echo "  make teardown-persistent ENV=$(ENV) REGION=$(REGION) CONFIRM_DESTROY=yes"; \
		echo ""; \
		exit 1; \
	fi
	@echo "Tearing down persistent cluster $(PERSISTENT_CLUSTER_EFFECTIVE)..."
	@mkdir -p logs/build-timings
	@bash -c '\
	log="logs/build-timings/teardown-persistent-$(ENV)-$(PERSISTENT_CLUSTER_EFFECTIVE)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown output streaming; full log at $$log"; \
	script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh"; \
	TEARDOWN_CONFIRM=true \
	TF_DIR=$(TF_DIR) \
	TF_AUTO_APPROVE=true \
	REMOVE_K8S_SA_FROM_STATE=true \
	CLEANUP_ORPHANS=$(CLEANUP_ORPHANS) \
	bash "$$script" $(PERSISTENT_CLUSTER_EFFECTIVE) $(REGION) 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

################################################################################

help:
	@echo "Targets:"
	@echo ""
	@echo "== S3 Requests (Contract-Driven) =="
	@echo "  make s3-validate S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml"
	@echo "  make s3-generate S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml"
	@echo "  make s3-apply S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml \\"
	@echo "       S3_STATE_BUCKET=goldenpath-idp-dev-bucket S3_LOCK_TABLE=goldenpath-idp-dev-locks"
	@echo "  NOTE: Uses per-bucket state key envs/<env>/s3/<id>/terraform.tfstate"
	@echo ""
	@echo "== Platform RDS (Persistent Data Layer) =="
	@echo "  make rds-init ENV=dev          # Initialize RDS Terraform"
	@echo "  make rds-plan ENV=dev          # Plan RDS changes"
	@echo "  make rds-apply ENV=dev         # Apply RDS (deploy first!)"
	@echo "  make rds-status ENV=dev        # Show RDS outputs"
	@echo "  make rds-provision ENV=dev     # Provision DB users/databases"
	@echo "  make rds-provision-dry-run ENV=dev  # Preview provisioning"
	@echo "  make rds-provision-auto ENV=dev     # Provision with mode detection"
	@echo "  make rds-provision-auto-dry-run ENV=dev  # Preview with mode detection"
	@echo "  NOTE: No rds-destroy target. See RB-0030 for deletion."
	@echo "  NOTE: Non-dev requires ALLOW_DB_PROVISION=true"
	@echo ""
	@echo "== Persistent Mode (no BUILD_ID) =="
	@echo "  make apply-persistent ENV=dev REGION=eu-west-2"
	@echo "  make bootstrap-persistent ENV=dev REGION=eu-west-2"
	@echo "  make deploy-persistent ENV=dev REGION=eu-west-2  # apply + rds-provision + bootstrap"
	@echo "  make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes"
	@echo "  NOTE: Persistent mode uses root state key (envs/<env>/terraform.tfstate)"
	@echo "  NOTE: RDS allowed in persistent mode, blocked in ephemeral"
	@echo ""
	@echo "== EKS Cluster (Ephemeral - requires BUILD_ID) =="
	@echo "  make init ENV=dev"
	@echo "  make plan ENV=dev"
	@echo "  make apply ENV=dev"
	@echo "  make destroy ENV=dev"
	@echo "  make timed-apply ENV=dev BUILD_ID=20250115-02"
	@echo "  make build ENV=dev CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make timed-build ENV=dev BUILD_ID=20250115-02 CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make timed-bootstrap ENV=dev BUILD_ID=20250115-02 CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  TF_VAR_owner_team=platform-team make plan ENV=dev"
	@echo "  make fmt"
	@echo "  make validate ENV=dev"
	@echo "  make reliability-metrics"
	@echo "  make bootstrap CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make bootstrap-only CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make pre-destroy-cleanup CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make cleanup-orphans BUILD_ID=<id> REGION=eu-west-2"
	@echo "  make cleanup-iam"
	@echo "  make drain-nodegroup NODEGROUP=dev-default"
	@echo "  make teardown CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  make timed-teardown ENV=dev BUILD_ID=20250115-02 CLUSTER=goldenpath-dev-eks REGION=eu-west-2"
	@echo "  (teardown targets set TF_AUTO_APPROVE=true by default)"
	@echo "  make set-cluster-name ENV=dev"
	@echo ""
	@echo "Bootstrap flags:"
	@echo "  NODE_INSTANCE_TYPE, ENV_NAME, SKIP_CERT_MANAGER_VALIDATION, SKIP_ARGO_SYNC_WAIT,"
	@echo "  COMPACT_OUTPUT, ENABLE_TF_K8S_RESOURCES, SCALE_DOWN_AFTER_BOOTSTRAP, TF_DIR, KONG_NAMESPACE"
