#!/bin/sh

## LOOP FOR TENANTS

# loops from START_TENANT to END_TENANT to create tenant projects and applications.
# Each user is given admin rights to their corresponding projects.

startTenant={{start_tenant}}
endTenant={{end_tenant}}
user_info_file=$output_dir/{{tenant_provisioning_results_file}}

output_dir={{tenant_output_dir}}

log_file=$output_dir/{{tenant_provisioning_log_file}}
create_tenants={{create_tenants}}

function prep() {
    mkdir -p $output_dir
    oc delete template sso72-x509-https -n openshift
    oc create -f {{ rhsso_template_yml }} -n openshift
}


function createAndActivateTenants() {

    echo -en "\n\nCreating tenants $startTenant through $endTenant  \n" > $log_file

    for i in $(seq ${startTenant} ${endTenant}) ; do

	   
		tenantId=user$i;

		echo "Now starting deployment for user :" $tenantId;

		    # Give users view access to the infra projects lab-infra & rhdm

		oc adm policy add-role-to-user view $tenantId -n api-lifecycle
		oc adm policy add-role-to-user view $tenantId -n rhdm

		# Create project for user sso (ephemeral)

		    oc adm new-project $tenantId-sso --admin=$tenantId  --description=$tenantId 

		sleep 5s;

		# Install SSO (ephemeral)

		oc project $tenantId-sso
		sleep 5s;
		oc create serviceaccount sso-service-account
		oc policy add-role-to-user view system:serviceaccount:$tenantId-sso:sso-service-account

		oc new-app --template=sso72-x509-https --param HOSTNAME_HTTP=$tenantId-sso-unsecured.apps.{{subdomain_base}} --param HOSTNAME_HTTPS=$tenantId-sso.apps.{{subdomain_base}} --param SSO_ADMIN_USERNAME={{tenantSSOUser}} --param SSO_ADMIN_PASSWORD={{tenantSSOPasswd}} --param SSO_SERVICE_USERNAME=admin --param SSO_SERVICE_PASSWORD=password --param SSO_REALM=3scaleRealm >> $log_file

		sleep 5s;
		# Create project for Syndesis


		    oc adm new-project $tenantId-fuse-ignite --admin=$tenantId  --description=$tenantId 

		sleep 5s;

		# Install Syndesis

		oc project $tenantId-fuse-ignite

		bash /tmp/install-syndesis --setup

		bash /tmp/install-syndesis --grant $tenantId

		bash /tmp/install-syndesis --route $tenantId-fuse-ignite.apps.{{subdomain_base}} --open --tag=1.5.4-20180910 >> $log_file


		# Create NodeJS client project

		    oc adm new-project $tenantId-client --admin=$tenantId  --description=$tenantId 
		sleep 5s;

		# Create Gateway Routes

		oc project $tenantId-gw
		sleep 5s;
		# Delete the default route created
		oc delete route --all

		# Provision new routes for Quoting app

		oc create route edge quote-stage --service="stage-apicast" --hostname=$tenantId-quote-stage.apps.{{subdomain_base}} 
		oc create route edge quote-prod --service="prod-apicast" --hostname=$tenantId-quote-prod.apps.{{subdomain_base}}  

		# Resume deployment of apicast gateways

		oc rollout resume deployment stage-apicast

		oc rollout resume deployment prod-apicast


        echo -en "\ncreated tenant with id = $tenantId. \n\tOutput file at: $output_dir/$output_file \n" >> $log_file

    done;

    echo -en "\n" >> $user_info_file

    echo -en "\n\n\nuser_info_file available at: $user_info_file \n" >> $log_file

}

function deleteTenants() {

    echo -en "\n\nDeleting tenants $startTenant through $endTenant  \n" > $log_file

    for i in $(seq ${startTenant} ${endTenant}) ; do

        tenantAdminId=user$i;

        #1) delete tenant fuse ignite project
        oc delete project $tenantAdminId-fuse-ignite >> $log_file

        #2) delete tenant sso project
		oc delete project $tenantAdminId-sso >> $log_file

        #3) delete tenant client project
		oc delete project $tenantAdminId-client >> $log_file

		oc project $tenantId-gw
		sleep 5s;
		# Delete the stage route created
		oc delete route --all  >> $log_file



    done

}

prep
if [ "x$create_tenants" == "xtrue"  ]; then 
    createAndActivateTenants
else
    deleteTenants
fi
