ENV_TYPE=base-rhel-infra
SANDBOX=1
# Adjust GUID to taste e.g. make deploy GUID=foo-01
GUID=rhelsbox0$(SANDBOX)
OUTPUT_DIR=~/tmp/output_dir
PLAYBOOK_DIR=ansible

# AWS Uses Sandbox creds typically
SECRETS_DIR=~/secrets
SECRETS_FILE=$(SECRETS_DIR)/secrets-base-rhel-infra-aws-sandbox0$(SANDBOX).yaml
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

deploy: ## Deploy ent-demo-automate-the-enterprise
deploy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
deploy: ## 
	cd ../../.. ; \
	mkdir -p ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID); \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(SECRETS_BOOKBAG) \
		-e @$(SECRETS_FILE) \
		-e @$(SECRETS_BOOKBAG) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

deploy-fast: ## Deploy without package updates etc
deploy-fast: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
deploy-fast: ## 
	cd ../../.. ; \
	mkdir -p ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID); \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(SECRETS_FILE) \
		-e @$(SECRETS_BOOKBAG) \
		-e env_type=$(ENV_TYPE) \
		-e update_packages=false \
		$(EXTRA_ARGS)

destroy: ## Destroy ent-demo-automate-the-enterprise
destroy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
destroy: ## 
	cd ../../.. ; \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID).log; \
	ansible-playbook $(PLAYBOOK_DIR)/destroy.yml \
		-e @$(SECRETS_FILE) \
		-e @$(SECRETS_BOOKBAG) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

ssh-target: ## ssh to your bastion by default or use `make ssh-target target=hostname` 
ssh-target: ## Assumes an existing output_dir
ssh-target: ## 
	echo "\n\nYou may want to 'sudo su - devops' - the primary user if you are on bastion\n\n"
	ssh -F $(OUTPUT_DIR)/$(GUID)/$(ENV_TYPE)_$(GUID)_ssh_conf $(TARGET)

#	ssh -F $(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/$(ENV_TYPE)_app2sbox0$(SANDBOX)_ssh_conf $(TARGET)

last-status: ## Output last status file
last-status: ## Update status file via make status
last-status: ## 
	ls -l $(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/status.txt
	cat $(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/status.txt

# | awk '{ print \$6 " " $7 " " $8 " " $9 " " $10 }'
update-status: ## Generate status
update-status: ## Update status file
update-status: ## 
	cd ../../.. ; \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/base-app2-infra-sbox0$(SANDBOX).log; \
	ansible-playbook $(PLAYBOOK_DIR)/lifecycle_entry_point.yml \
		-e ACTION=status \
		-e @$(SECRETS_FILE) \
		-e @$(SECRETS_BOOKBAG) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

#	ansible-playbook ../../../ansible/lifecycle_entry_point.yml \
stop: ## Suspend, stop, instances
stop: ## Restart with make start
stop: ## 
stop:
	cd ../../.. ; \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/base-app2-infra-sbox0$(SANDBOX).log; \
	ansible-playbook $(PLAYBOOK_DIR)/lifecycle_entry_point.yml \
		-e ACTION=stop \
		-e @$(SECRETS_FILE) \
		-e @$(SECRETS_BOOKBAG) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

start: ## Suspend, start, instances
start: ## Restart with make start
start: ## 
	cd ../../.. ; \
	export ANSIBLE_LOG_PATH=$(OUTPUT_DIR)/aap2sbox0$(SANDBOX)/base-app2-infra-sbox0$(SANDBOX).log; \
	ansible-playbook $(PLAYBOOK_DIR)/lifecycle_entry_point.yml \
		-e ACTION=start \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		$(EXTRA_ARGS)

bounce: ## Bounce the deploy 
bounce: ## IE stop then start
bounce: ## 
bounce: stop start

exit-make-help: ## You're in less - type q to exit
