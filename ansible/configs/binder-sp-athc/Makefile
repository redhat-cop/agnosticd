ENV_TYPE=binder-sp-athc
SANDBOX=1
# Adjust GUID to taste e.g. make deploy GUID=foo-01
GUID=binder-athc-0$(SANDBOX)
OUTPUT_DIR=~/tmp/output_dir
PLAYBOOK_DIR=ansible

# AWS Uses Sandbox creds typically
SECRETS_DIR=~/secrets
SECRETS_FILE=$(SECRETS_DIR)/secrets-binder-athc-sandbox0$(SANDBOX).yaml
VARS_DIR=~/vars
VARS_FILE=binder-vars-athc.yaml

SECRETS_ANSIBLE_VAULT_PASSWORD_FILE=$(SECRETS_DIR)/secret-ansible-vault-babylon-gpte_vault_0
SECRETS_BOOKBAG=~/secrets/bookbag-shared-410.yaml

TARGET=bastion
EXTRA_ARGS=
# Adjust to taste

: ## TIP! make supports tab completion with *modern* shells e.g. zsh etc
: ## e.g. make depl<TAB> == make deploy 
: ## 

.SILENT: setup my-env ssh-target

help: ## Show this help - technically unnecessary as `make` alone will do
help: ## 
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", ($$2=="" ? "" : $$1 ),  $$2}' | less

# Thanks to victoria.dev for the above syntax
# https://victoria.dev/blog/how-to-create-a-self-documenting-makefile/

setup: ## Virtualenvs, ANSIBLE logs, env vars etc
setup: ## 
	echo "\n\nActivate a virtualenv if required\n"
	echo "Consider export ANSIBLE_LOG_PATH=/tmp/ansible_base_aap2_infra_$(GUID).log\n\n"

my-env: ## Confirm env setup
my-env: ## Could add extra env vars like `env | grep ANSIBLE`
my-env: ## 
	type python3
	printf "Python3 version is: "
	python3 --version
	type ansible
	ansible --version
	env | grep ANSIBLE 

deploy: ## Deploy ENV_TYPE=binder-sp-athc
deploy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-athc-no-sandbox.yml 
deploy: ## 
	cd ../../.. ; \
	mkdir -p $(OUTPUT_DIR)/$(GUID); \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(VARS_DIR)/$(VARS_FILE) \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e output_dir=$(OUTPUT_DIR) \
		$(EXTRA_ARGS)

deploy-full-logging: ## Deploy with full logging
deploy-full-logging: ## infra.controller_configuration_secure_logging = false
	cd ../../.. ; \
	mkdir -p ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID); \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(VARS_DIR)/$(VARS_FILE) \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e "controller_configuration_secure_logging=false" \
		-e output_dir=$(OUTPUT_DIR) \
		$(EXTRA_ARGS)

destroy: ## Destroy ent-demo-automate-the-enterprise
destroy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
destroy: ## 
	cd ../../.. ; \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/destroy.yml \
		-e @$(VARS_DIR)/$(VARS_FILE) \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

exit-make-help: ## You're in less - type q to exit
