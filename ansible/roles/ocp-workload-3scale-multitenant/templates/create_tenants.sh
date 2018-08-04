
startTenant={{start_tenant}}
endTenant={{end_tenant}}

master_access_token={{master_access_token}}
new_tenant_passwd=admin
create_tenant_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/master/api/providers.xml
output_dir={{tenant_output_dir}}
access_token_mapping_file=$output_dir/access_token_mapping_file.txt
log_file=$output_dir/tenant_provisioning.log

function createAndActivateTenants() {

    echo -en "\n\nCreating tenants $startTenant through $endTenant  \n" > $log_file
    echo -en "userId        access_token\n\n" > $access_token_mapping_file
    

    for i in $(seq ${startTenant} ${endTenant}) ; do
        orgName=user$i-3scale;
        userId=user$i;
        output_file=$orgName-tenant-signup.xml
  
       # 1) Create tenant 
       curl -k  \
            -X POST \
            -d access_token=$master_access_token \
            -d org_name=$orgName \
            -d username=$userId \
            -d email=$userId%40{{ocp_apps_domain}} \
            -d password=$new_tenant_passwd \
            $create_tenant_url > $output_dir/$output_file

        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 1" >> $log_file
            exit 1;
        fi


        # 2) Retrieve access_token
        eval access_token=\"`xmlstarlet sel -t -m '//access_token' -v 'value' -n $output_dir/$output_file`\"
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 2" >> $log_file
            exit 1;
        fi


        # 3)  activate new user
        eval account_id=\"`xmlstarlet sel -t -m '//account' -v 'id' -n $output_dir/$output_file`\"
        eval user_id=\"`xmlstarlet sel -t -m '///user[state = "pending"]' -v 'id' -n $output_dir/$output_file`\"
        echo -en "\nactivating new user. account_id = $account_id. user_id = $user_id \n" >> $log_file
        activate_user_url=https://{{ocp_project}}-master-admin.{{ocp_apps_domain}}/admin/api/accounts/$account_id/users/$user_id/activate.xml
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 3" >> $log_file
            exit 1;
        fi


        echo -en "\n\n" >> $output_dir/$output_file
        curl -k \
             -X PUT \
             -d access_token=$master_access_token \
             $activate_user_url >> $output_dir/$output_file
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 4" >> $log_file
            exit 1;
        fi


        # 4) Create corresponding route
        oc create route edge $orgName-provider --service=system-provider --hostname=$orgName-admin.{{ocp_apps_domain}}
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 5" >> $log_file
            exit 1;
        fi

        echo -en "\ncreated tenant with orgName= $orgName. \n\tOutput file at: $output_dir/$output_file  \n\taccess_token = $access_token \n" >> $log_file

        echo -en "\n$userId   $access_token" >> $access_token_mapping_file
    done;

    echo -en "\n" >> $access_token_mapping_file

    echo -en "\n\n\naccess_token_mapping_file available at: $access_token_mapping_file \n" >> $log_file

}

mkdir -p $output_dir
createAndActivateTenants
