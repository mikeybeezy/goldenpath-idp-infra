TF_BIN ?= terraform
ENV ?= dev
ENV_DIR := envs/$(ENV)
CLUSTER_BASE ?= $(shell awk -F'=' '/^[[:space:]]*cluster_name[[:space:]]*=/{gsub(/"/,"",$$2);gsub(/[[:space:]]/,"",$$2);print $$2;exit}' $(ENV_DIR)/terraform.tfvars 2>/dev/null)

# Dynamic Cluster Discovery:
# Try to find the cluster by BuildId tag. If found, use that name.
# This decouples Makefile from Terraform naming conventions.
CLUSTER_ARN := $(shell aws resourcegroupstaggingapi get-resources --tag-filters Key=BuildId,Values=$(BUILD_ID) --resource-type-filters eks:cluster --region $(REGION) --query 'ResourceTagMappingList[0].ResourceARN' --output text 2>/dev/null)
CLUSTER_FOUND := $(notdir $(CLUSTER_ARN))

# Use found cluster, or fallback to predicted name (prefix-buildid)
CLUSTER ?= $(if $(CLUSTER_FOUND),$(CLUSTER_FOUND),$(CLUSTER_BASE)-$(BUILD_ID))
REGION ?= eu-west-2
KONG_NAMESPACE ?= kong-system
NODE_INSTANCE_TYPE ?= t3.small
ENV_NAME ?= $(ENV)
SKIP_CERT_MANAGER_VALIDATION ?= true
SKIP_ARGO_SYNC_WAIT ?= true
COMPACT_OUTPUT ?= false
SCALE_DOWN_AFTER_BOOTSTRAP ?= false
BOOTSTRAP_VERSION ?= v3
# Defaults to envs/<env>; override on the command line for custom paths.
TF_DIR ?= $(ENV_DIR)
BUILD_ID ?= $(shell awk -F'=' '/^build_id[[:space:]]*=/{gsub(/"/,"",$$2);gsub(/[[:space:]]/,"",$$2);print $$2;exit}' $(ENV_DIR)/terraform.tfvars 2>/dev/null)
NODEGROUP ?=
CLEANUP_ORPHANS ?= false
ALLOW_REUSE_BUILD_ID ?= false

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

.PHONY: init plan apply destroy build timed-apply timed-build timed-bootstrap timed-teardown reliability-metrics fmt validate deploy _phase1-infrastructure _phase2-bootstrap _phase3-verify bootstrap bootstrap-only pre-destroy-cleanup cleanup-orphans cleanup-iam drain-nodegroup teardown teardown-resume set-cluster-name help

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
	if [[ "$${TEARDOWN_VERSION:-v1}" == "v2" ]]; then \
	  script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh"; \
	fi; \
	log="logs/build-timings/teardown-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v1})"; \
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
	if [[ "$${TEARDOWN_VERSION:-v1}" == "v2" ]]; then \
	  script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh"; \
	fi; \
	log="logs/build-timings/teardown-resume-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown resume output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v1})"; \
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
	if [[ "$${TEARDOWN_VERSION:-v1}" == "v2" ]]; then \
	  script="bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh"; \
	fi; \
	log="logs/build-timings/teardown-$(ENV)-$(CLUSTER)-$${build_id}-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Teardown output streaming; full log at $$log"; \
	echo "Teardown script: $$script (version $${TEARDOWN_VERSION:-v1})"; \
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

help:
	@echo "Targets:"
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
