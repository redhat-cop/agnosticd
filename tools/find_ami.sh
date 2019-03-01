#!/bin/bash

# Generate yaml containing image information for each region

search_images() {
    owner=$1
    pattern=$2
    ispublic=$3
    aws ec2 describe-images \
        --owners ${owner} \
        --filters "Name=name,Values=${pattern}" "Name=is-public,Values=${ispublic}" \
        --query "reverse(sort_by(Images, &CreationDate))[0].{name: Name, id: ImageId}" \
        --output text \
        --region $region | awk '{print $1 " # " $2}'
}

#for region in us-east-1
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text --region us-east-1)
do
    echo "${region}:"
    echo -n "  RHEL75GOLD: "
    search_images 309956199498 'RHEL-7.5*Access*' false

    echo -n "  RHEL74GOLD: "
    search_images 309956199498 'RHEL-7.4*Access*' false

    echo -n "  RHEL75: "
    search_images 309956199498 'RHEL-7.5*' true

    echo -n "  RHEL74: "
    search_images 309956199498 'RHEL-7.4*' true

    echo -n "  WIN2012R2: "
    search_images 801119661308 'Windows_Server-2012-R2_RTM-English-64Bit-Base*' true
done

# For azure
# az vm image list --output table -p RedHat --all --sku 7-RAW
