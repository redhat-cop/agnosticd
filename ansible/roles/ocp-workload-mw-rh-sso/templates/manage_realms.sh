# loops from {{start_realm}} to {{end_realm}} to create RH-SSO realms.
# Each user is given access to almost all functionality of their corresponding RH-SSO realm.

# TO-DOs :
#   1)  Convert this entire shell script to ansible (rather than just being invoked by Ansible)

startRealm={{start_realm}}
endRealm={{end_realm}}

realm_template=generic-realm.json

retrieve_token_url=https://sso-{{ocp_project}}.{{ocp_apps_domain}}/auth/realms/master/protocol/openid-connect/token
create_realm_url=https://sso-{{ocp_project}}.{{ocp_apps_domain}}/auth/admin/realms
delete_realm_sub_url=https://sso-{{ocp_project}}.{{ocp_apps_domain}}/auth/admin/realms
output_dir={{realm_output_dir}}
log_file=$output_dir/{{realm_provisioning_log_file}}

realmAdminUserId={{SSO_ADMIN_USERNAME}}
realmAdminPasswd={{SSO_ADMIN_PASSWORD}}

create_realms={{create_realms}}

function prep() {
    mkdir -p $output_dir
}

function createAndActivateRealms() {

    echo -en "\n\nCreating realms $startRealm through $endRealm  \n" > $log_file

    for i in $(seq ${startRealm} ${endRealm}) ; do
        realmId=realm$i;
        output_file=$realmId-create.json
        echo -en "\n\n\n\n**** Creating realm: $realmId  \n" >> $log_file

        if [ "x$TKN" == "x" ];then
            getToken
        fi

        # 2) Copy and variable substition of realm json
        cp /tmp/$realm_template $output_dir/$realmId-realm.json
        sed -i 's/changeme/'"$realmId"'/g' $output_dir/$realmId-realm.json
        if [ $? -ne 0 ];then
            echo -en "\n *** ERROR: 2" >> $log_file
            exit 1;
        fi
  
        # 3) Create realm 
        postRealm
        if [ $status -eq 401 ];then
            echo -en "\n Refreshing token" >> $log_file
            getToken
            postRealm
        fi
        if [ $status -ne 201 ];then
            echo -en "\n\t*** ERROR: 3 Create realm response code = $status\n\t" >> $log_file
            cat $output_dir/$output_file >> $log_file
            echo -en "\n\tCreate POST request: \n\tcurl -k -s -w %{http_code} $create_realm_url -X POST -H \"Authorization: Bearer $TKN\" -H \"Content-Type: application/json;charset=UTF-8\" --data \"@$output_dir/$realmId-realm.json\" -o $output_dir/$output_file\n" >> $log_file
            exit 1;
        fi

        sleep 5

    done;
}

function deleteRealms() {

    echo -en "\n\nDeleting realms $startRealm through $endRealm  \n" > $log_file

    for i in $(seq ${startRealm} ${endRealm}) ; do
        realmId=realm$i;
        echo -en "\n\n\n\n**** Delete realm: $realmId  \n" >> $log_file
        output_file=$realmId-delete.json

        if [ "x$TKN" == "x" ];then
            getToken
        fi 

        delete_realm_url=$delete_realm_sub_url/$realmId
        deleteRealm
        if [ $status -eq 401 ];then
            echo -en "\n Refreshing token" >> $log_file
            getToken
            deleteRealm
        fi
        if [ $status -ne 204 ];then
            echo -en "\n *** ERROR: 3 Delete realm response code = $status\n\t" >> $log_file
            echo -en "\n\tDelete request: \n\tcurl -k -s -w %{http_code} $delete_realm_url -X DELETE -H \"Authorization: Bearer $TKN\" -o $output_dir/$output_file\n" >> $log_file
            cat $output_dir/$output_file >> $log_file
        fi

    done

}

function getToken() {
        # echo -en "\nRetrive token request :  curl -k -X POST \"$retrieve_token_url\" -H \"Content-Type: application/x-www-form-urlencoded\" -d \"username=$realmAdminUserId\" -d \"password=$realmAdminPasswd\" -d \"grant_type=password\" -d \"client_id=admin-cli\"  \n" >> $log_file

        TKN=$(curl -k -X POST "$retrieve_token_url" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=$realmAdminUserId" \
            -d "password=$realmAdminPasswd" \
            -d "grant_type=password" \
            -d "client_id=admin-cli" \
            | sed 's/.*access_token":"//g' | sed 's/".*//g')
}

function postRealm() {
        status=$(curl -k -s -w %{http_code} \
            $create_realm_url \
            -X POST \
            -H "Authorization: Bearer $TKN" \
            -H "Content-Type: application/json;charset=UTF-8" \
            --data "@$output_dir/$realmId-realm.json" \
            -o $output_dir/$output_file)
        # echo -en "\n\tpostRealm: outputDir= $output_dir/$output_file\n\tResponse status = $status" >> $log_file
}

function deleteRealm() {
        status=$(curl -k -s -w %{http_code} \
            $delete_realm_url \
            -X DELETE \
            -H "Authorization: Bearer $TKN" \
            -o $output_dir/$output_file)
}



prep
if [ "x$create_realms" == "xtrue"  ]; then 
    createAndActivateRealms
else
    deleteRealms
fi
