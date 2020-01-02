#!/bin/bash


function sub_function(){
    sub_avail=$(hammer subscription list --organization "${org}" |grep "${subscription_name}" > /dev/null ; echo $?)
    if [ "${sub_avail}" -eq 0 ]; then
        sub_id=$(hammer subscription list --organization "${org}" |grep "${subscription_name}" |awk '{print $1}')
        echo ${sub_id}
        return
    else
        echo "${subscription_name} :  is not available"
        exit 1
    fi
}

# Parameter variables 
org="${1}"
activation_key="${2}"
subscription_name="${3}"
content_view="${4}"
life_cycle="${5}"
# Find activation key 
key_exist=$(hammer activation-key info --organization "${org}" --name "${activation_key}" >& /dev/null ; echo $? )

if [ ${key_exist} -eq 0 ]; then
    # find subscription if already exist 
    echo "Activation key exist"
    sub_name_exist=$(hammer subscription  list --organization "${org}" --activation-key "${activation_key}" |grep "${subscription_name}" |awk -F'|' '{print $3}' | sed -e 's/^\ //' -e 's/\ $//')
        if [ "${sub_name_exist}" == "${subscription_name}" ]; then  
                echo "${subscription_name} subscription already exist" 
         else   
            # Add subscription to activation key
            sub_function
            hammer activation-key add-subscription --organization "${org}" --name "${activation_key}"  --subscription-id ${sub_id}
        fi
elif [ ${key_exist} -ne 0 ]; then
    # Create new activation key
    hammer activation-key create --organization "${org}" --name "${activation_key}" --content-view "${content_view}" --lifecycle-environment "${life_cycle}" 
    # Add subscription to activation key
    sub_function
    hammer activation-key add-subscription --organization "${org}" --name "${activation_key}"  --subscription-id ${sub_id}    
fi
