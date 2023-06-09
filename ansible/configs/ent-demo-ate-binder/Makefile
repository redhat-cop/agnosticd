# Change GUID if you are co developing :)

ENV_TYPE=ent-demo-ate-base
GUID=ate-base-01
OUTPUT_DIR=/tmp/output_dir
PLAYBOOK_DIR=ansible
SECRETS_FILE=~/secrets/secret-aws-ate-base.yml

: ## TIP! make supports tab completion with *modern* shells e.g. zsh etc
: ## e.g. make depl<TAB> == make deploy 
: ## 

help: ## Show this help - technically unnecessary as `make` alone will do
help: ## 
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Thanks to victoria.dev for the above syntax
# https://victoria.dev/blog/how-to-create-a-self-documenting-makefile/

deploy: ## Deploy ent-demo-automate-the-enterprise
deploy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
deploy: ## 
	ansible-playbook $(PLAYBOOK_DIR)/main.yml \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e guid=$(GUID)

destroy: ## Destroy ent-demo-automate-the-enterprise
destroy: ## See README.adoc for recommended contents of ~/secrets/secret-aws-ate-no-sandbox.yml 
destroy: ## 
	ansible-playbook $(PLAYBOOK_DIR)/destroy.yml \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e guid=$(GUID)

ssh-bastion: ## ssh to your bastion
ssh-bastion: ## Assumes an existing output_dir
	 ssh -F $(OUTPUT_DIR)/ent-demo-automate-the-enterprise_ate-01_ssh_conf bastion

last-status: ## Output last status file
last-status: ## Update status file via make status
last-status: ## 
	ls -l $(OUTPUT_DIR)/$(GUID)-status.txt
	cat $(OUTPUT_DIR)/$(GUID)-status.txt

# | awk '{ print \$6 " " $7 " " $8 " " $9 " " $10 }'
status: ## Generate status
status: ## Update status file
status: ## 
	ansible-playbook $(PLAYBOOK_DIR)/ansible/lifecycle_entry_point.yml \
		-e ACTION=status \
		-e @$(SECRETS_FILE) \
		-e env_type=$(ENV_TYPE) \
		-e guid=$(GUID)

#	ansible-playbook ../../../ansible/lifecycle_entry_point.yml \
stop: ## Suspend, stop, instances
stop: ## Restart with make start
stop: ## 
# stop:
# 	ansible-playbook ansible/lifecycle_entry_point.yml \
# 		-e ACTION=stop \
# 		-e @~/secrets/secret-aws-ate.yml \
# 		-e env_type=ent-demo-automate-the-enterprise \
# 		-e guid=$(GUID)
