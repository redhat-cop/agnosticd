ENV_TYPE=binder-aap2-default
GUID=$(ENV_TYPE)-01
PLAYBOOK_DIR=ansible

# Vars - binder vars

VARS_DIR=~/vars
VARS_FILE=$(VARS_DIR)/binder-aap2-default-vars.yaml

# Secrets - all creds e.g. AAP2, and cloud creds

SECRETS_DIR=~/secrets
SECRETS_FILE=$(SECRETS_DIR)/secrets-binder-aap2-default.yaml
# SECRETS_FILE=~/secrets/secret-binder-aap2-default.yaml

# Defaults for output

OUTPUT_DIR=$(OUTPUT_DIR_BASE)/$(OUTPUT_DIR_SUB_DIR)
OUTPUT_DIR_BASE=/tmp/output_dir
OUTPUT_DIR_SUB_DIR=$(GUID)

: ## TIP! make supports tab completion with *modern* shells e.g. zsh etc
: ## e.g. make depl<TAB> == make deploy 

EXTRA_ARGS=

# Adjust to taste

: ## TIP! make supports tab completion with *modern* shells e.g. zsh etc
: ## e.g. make depl<TAB> == make deploy 
: ## 

.SILENT: setup my-env  #ssh-target

help: ## Show this help - technically unnecessary as `make` alone will do
help: ## 
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", ($$2=="" ? "" : $$1 ),  $$2}' | less

# Thanks to victoria.dev for the above syntax
# https://victoria.dev/blog/how-to-create-a-self-documenting-makefile/

setup: ## Any setup tasks prior to deploy
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

deploy: ## Run binder - assumes you have a running AAP2
deploy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
deploy: ## 
	cd ../../.. ; \
	mkdir -p $(OUTPUT_DIR); \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(VARS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e cloud_provider=none \
		$(EXTRA_ARGS)

		# -e @$(SECRETS_FILE) \
			#
user-info: ## user-info ent-demo-automate-the-enterprise
user-info: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
user-info: ## 
	cat $(OUTPUT_DIR)/user-info.yaml

user-data: ## user-data ent-demo-automate-the-enterprise
user-data: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
user-data: ## 
	cat $(OUTPUT_DIR)/user-data.yaml

exit-make-help: ## You're in less - type q to exit
