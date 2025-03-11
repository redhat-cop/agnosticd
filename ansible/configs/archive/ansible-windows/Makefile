GUID=win-00
ENVTYPE=ansible-windows
BASESUFFIX='.example.opentlc.com'
CLOUDPROVIDER=ec2
REGION=us-east-1
HOSTZONEID='Z3IHLWJZOU9SRT'
KEYNAME=ocpkey
SECRET=~/secrets/aws-gpte-windows.yml

deploy:
	ansible-playbook ansible/main.yml \
		-e "guid=$(GUID)" \
		-e "env_type=$(ENVTYPE)" \
		-e "key_name=$(KEYNAME)" \
		-e "subdomain_base_suffix=$(BASESUFFIX)" \
		-e "cloud_provider=$(CLOUDPROVIDER)" \
		-e "aws_region=$(REGION)" \
		-e "HostedZoneId=$(HOSTZONEID)" \
		-e "email=name@example.com" \
		-e guid=win-$(GUID) \
		-e @$(SECRET)

destroy:
	ansible-playbook ansible/destroy.yml \
		-e "guid=$(GUID)" \
		-e "env_type=$(ENVTYPE)" \
		-e "key_name=$(KEYNAME)" \
		-e "subdomain_base_suffix=$(BASESUFFIX)" \
		-e "cloud_provider=$(CLOUDPROVIDER)" \
		-e "aws_region=$(REGION)" \
		-e "HostedZoneId=$(HOSTZONEID)" \
		-e "email=name@example.com" \
		-e guid=win-$(GUID)
		-e @$(SECRET)
