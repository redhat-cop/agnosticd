# loops from {{start_tenant}} to {{end_tenant}} to create 3scale tenants.
# Each user is given tenant admin rights to their corresponding tenant.

startTenant={{start_tenant}}
endTenant={{end_tenant}}

master_access_token={{master_access_token}}
tenantAdminPasswd={{tenantAdminPasswd}}
create_tenant_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/master/api/providers.xml
output_dir={{tenant_output_dir}}
user_info_file=$output_dir/user_info_file.txt
log_file=$output_dir/tenant_provisioning.log

function createAndActivateTenants() {

    echo -en "\n\nCreating tenants $startTenant through $endTenant  \n" > $log_file
    echo -en "OCP user id\tOCP user passwd\t3scale admin URL\tAPI admin Id\tAPI admin passwd\tAPI admin access token\n\t\t\t\t\t" > $user_info_file
    

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

        echo -en "\ncreated tenant with orgName= $orgName. \n\tOutput file at: $output_dir/$output_file  \n\ttenant_access_token = $tenant_access_token \n" >> $log_file

        echo -en "\nuser$i\t{{ocp_user_passwd}}\t$orgName-admin.{{ocp_apps_domain}}\t$tenantAdminId\t$tenantAdminPasswd\t$tenant_access_token" >> $user_info_file
    done;

    echo -en "\n" >> $user_info_file

    echo -en "\n\n\nuser_info_file available at: $user_info_file \n" >> $log_file

}

mkdir -p $output_dir
createAndActivateTenants
