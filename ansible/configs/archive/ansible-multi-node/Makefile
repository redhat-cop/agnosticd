GUID=00
OSP_CLUSTER=red

help:
	echo "Basic usage:"
	echo "      make deploy <OSP_CLUSTER=<color>> GUID=nn"
	echo "      make destroy <OSP_CLUSTER=<color>> GUID=nn"

deploy:
	ansible-playbook main.yml \
		-e @configs/ansible-multi-node/sample_vars/multitier_app_with_tower.yml \
		-e@~/secrets/openstack-$(OSP_CLUSTER)-secret.yml \
		-e@~/secrets/yum-server.yml \
		-e guid=multi-$(GUID)

destroy:
	ansible-playbook destroy.yml \
		-e @configs/ansible-multi-node/sample_vars/multitier_app_with_tower.yml \
		-e@~/secrets/openstack-$(OSP_CLUSTER)-secret.yml \
		-e guid=multi-$(GUID)

