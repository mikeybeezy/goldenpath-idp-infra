TF_BIN ?= terraform
ENV ?= dev
ENV_DIR := envs/$(ENV)

# Usage:
#   make init ENV=dev     # terraform -chdir=envs/dev init
#   make plan ENV=staging # terraform -chdir=envs/staging plan
#   make apply ENV=prod   # terraform -chdir=envs/prod apply

.PHONY: init plan apply fmt validate

init:
	$(TF_BIN) -chdir=$(ENV_DIR) init

plan:
	$(TF_BIN) -chdir=$(ENV_DIR) plan

apply:
	$(TF_BIN) -chdir=$(ENV_DIR) apply

fmt:
	$(TF_BIN) fmt -recursive

validate:
	$(TF_BIN) -chdir=$(ENV_DIR) validate
