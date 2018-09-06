# loops from {{start_tenant}} to {{end_tenant}} to create 3scale tenants.
# Each user is given tenant admin rights to their corresponding tenant.

# TO-DOs :
#   1)  Configure smtp configmap to enable outbound emails from AMP
#   2)  Convert this entire shell script to ansible (rather than just being invoked by Ansible)

startTenant={{start_tenant}}
endTenant={{end_tenant}}

master_access_token={{master_access_token}}
tenantAdminPasswd={{tenantAdminPasswd}}
create_tenant_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/master/api/providers.xml
delete_tenant_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/master/api/providers.xml
output_dir={{tenant_output_dir}}
user_info_file=$output_dir/{{tenant_provisioning_results_file}}
log_file=$output_dir/{{tenant_provisioning_log_file}}
createGWs={{create_gws_with_each_tenant}}

create_tenants={{create_tenants}}

function prep() {
    mkdir -p $output_dir
}

function createAndActivateTenants() {

    echo -en "\n\nCreating tenants $startTenant through $endTenant  \n" > $log_file
    echo -en "GUID\tOCP user id\tOCP user passwd\t3scale admin URL\tAPI admin Id\tAPI admin passwd\tAPI admin access token\n\t\t\t\t\t" > $user_info_file
    
    curl -o $output_dir/3scale-apicast.yml https://raw.githubusercontent.com/gpe-mw-training/3scale_onpremise_implementation_labs/master/resources/rhte/3scale-apicast.yml

    for i in $(seq ${startTenant} ${endTenant}) ; do
        orgName=user$i-3scale-mt;
        tenantAdminId=user$i;
        output_file=$orgName-tenant-signup.xml
  
       # 1) Create tenant 
       curl -k  \
            -X POST \
            -d access_token=$master_access_token \
            -d org_name=$orgName \
            -d username=$tenantAdminId \
            -d password=$tenantAdminPasswd \
            -d email=$tenantAdminId%40{{ocp_apps_domain}} \
            $create_tenant_url > $output_dir/$output_file

        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 1" >> $log_file
            exit 1;
        fi


        # 2) Retrieve access_token
        eval tenant_access_token=\"`xmlstarlet sel -t -m '//access_token' -v 'value' -n $output_dir/$output_file`\"
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 2" >> $log_file
            exit 1;
        fi

        # 2.1) TO-DO :   Is there also a Provider API key that should be retrieved ???

        # 3)  determine URL to activate new user
        eval account_id=\"`xmlstarlet sel -t -m '//account' -v 'id' -n $output_dir/$output_file`\"
        eval user_id=\"`xmlstarlet sel -t -m '///user[state = "pending"]' -v 'id' -n $output_dir/$output_file`\"
        echo -en "\nactivating new user. account_id = $account_id. user_id = $user_id \n" >> $log_file
        activate_user_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/admin/api/accounts/$account_id/users/$user_id/activate.xml
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 3" >> $log_file
            exit 1;
        fi

        # 4)  activate new user
        echo -en "\n\n" >> $output_dir/$output_file
        curl -k \
             -X PUT \
             -d access_token=$master_access_token \
             $activate_user_url >> $output_dir/$output_file
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 4" >> $log_file
            exit 1;
        fi

        # 5) Give user view access to 3scale project.
        #    Assumes use of the following user name convention:   user[1-100]
        oc adm policy add-role-to-user view user$i -n {{ocp_project}}


        # 6) Create corresponding route on 3scale AMP system-provider service
        oc create route edge $orgName-provider --service=system-provider --hostname=$orgName-admin.{{ocp_apps_domain}} -n {{ocp_project}}
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 6" >> $log_file
            exit 1;
        fi

        # 7) Create corresponding route on 3scale AMP system-developer service
        oc create route edge $orgName-developer --service=system-developer --hostname=$orgName.{{ocp_apps_domain}} -n {{ocp_project}}
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 6" >> $log_file
            exit 1;
        fi


        if [ "x$createGWs" == "xtrue" ];then
            echo -en "\nwill create gateways\n" >> $log_file

            # 8) Create OCP project for GWs
            oc adm new-project $tenantAdminId-gw --admin=$tenantAdminId  --description=$tenantAdminId-gw >> $log_file
            if [ $? -ne 0 ];then
                    echo -en "\n *** ERROR: 8" >> $log_file
                    exit 1;
            fi

            THREESCALE_PORTAL_ENDPOINT=https://$tenant_access_token@$orgName-admin.{{ocp_apps_domain}}


            # 9) Create staging gateway
            oc new-app \
               -f $output_dir/3scale-apicast.yml \
               --param THREESCALE_PORTAL_ENDPOINT=$THREESCALE_PORTAL_ENDPOINT \
               --param APP_NAME=stage-apicast \
               --param ROUTE_NAME=$orgName-mt-stage-generic \
               --param WILDCARD_DOMAIN=$OCP_WILDCARD_DOMAIN \
               --param THREESCALE_DEPLOYMENT_ENV=sandbox \
               --param APICAST_CONFIGURATION_LOADER=lazy \
               -n $tenantAdminId-gw >> $log_file
                if [ $? -ne 0 ];then
                    echo -en "\n *** ERROR: 9" >> $log_file
                    exit 1;
                fi

            # 10) Create production gateway
            oc new-app \
               -f $output_dir/3scale-apicast.yml \
               --param THREESCALE_PORTAL_ENDPOINT=$THREESCALE_PORTAL_ENDPOINT \
               --param APP_NAME=prod-apicast \
               --param ROUTE_NAME=$orgName-mt-prod-generic \
               --param WILDCARD_DOMAIN=$OCP_WILDCARD_DOMAIN \
               --param THREESCALE_DEPLOYMENT_ENV=production \
               --param APICAST_CONFIGURATION_LOADER=lazy \
               -n $tenantAdminId-gw >> $log_file
                if [ $? -ne 0 ];then
                    echo -en "\n *** ERROR: 10" >> $log_file
                    exit 1;
                fi
        fi

        echo -en "\ncreated tenant with orgName= $orgName. \n\tOutput file at: $output_dir/$output_file  \n\ttenant_access_token = $tenant_access_token \n" >> $log_file

        echo -en "\n$i\tuser$i\t{{ocp_user_passwd}}\t$orgName-admin.{{ocp_apps_domain}}\t$tenantAdminId\t$tenantAdminPasswd\t$tenant_access_token" >> $user_info_file
    done;

    echo -en "\n" >> $user_info_file

    echo -en "\n\n\nuser_info_file available at: $user_info_file \n" >> $log_file

}

function deleteTenants() {

    echo -en "\n\nDeleting tenants $startTenant through $endTenant  \n" > $log_file

    for i in $(seq ${startTenant} ${endTenant}) ; do
        orgName=user$i-3scale-mt;
        tenantAdminId=user$i;

        #1) delete tenant project
        oc adm new-project $tenantAdminId-gw >> $log_file

        #2) delete routes
        oc delete route $orgName-provider -n {{ocp_project}} >> $log_file
        oc delete route $orgName-developer -n {{ocp_project}} >> $log_file

        #3) delete tenant in 3scale API Manager
        curl -k  \
            -X DELETE \
            -d access_token=$master_access_token \
            -d org_name=$orgName \
            $delete_tenant_url >> $log_file

    done

}

prep
if [ "x$create_tenants" == "xtrue"  ]; then 
    createAndActivateTenants
else
    deleteTenants
fi
