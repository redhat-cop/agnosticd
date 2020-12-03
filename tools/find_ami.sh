#!/bin/bash

# Generate yaml containing image information for each region

profile=gpte

search_images() {
    owner=$1
    pattern=$2
    ispublic=$3
    aws ec2 describe-images \
        --profile $profile \
        --owners ${owner} \
        --filters "Name=name,Values=${pattern}" "Name=is-public,Values=${ispublic}" \
        --query "reverse(sort_by(Images, &CreationDate))[*].{name: Name, id: ImageId}" \
        --output text \
        --region $region | awk '{print $1 " # " $2}'
}

search_last_image() {
    owner=$1
    pattern=$2
    ispublic=$3
    aws ec2 describe-images \
        --profile $profile \
        --owners ${owner} \
        --filters "Name=name,Values=${pattern}" "Name=is-public,Values=${ispublic}" \
        --query "reverse(sort_by(Images, &CreationDate))[0].{name: Name, id: ImageId}" \
        --output text \
        --region $region | awk '{print $1 " # " $2}'
}

#for region in us-east-1
for region in $(aws ec2 --profile $profile describe-regions --query "Regions[].RegionName" --output text --region us-east-1)
do
    echo "${region}:"
    echo -n "  RHEL82GOLD: "
    search_last_image 309956199498 'RHEL-8.2*x86_64*Access*' false

    echo -n "  RHEL81GOLD: "
    search_last_image 309956199498 'RHEL-8.1*x86_64*Access*' false

    echo -n "  RHEL77GOLD: "
    search_last_image 309956199498 'RHEL-7.7*x86_64*Access*' false

    echo -n "  RHEL75GOLD: "
    search_last_image 309956199498 'RHEL-7.5*x86_64*Access*' false

    echo -n "  RHEL74GOLD: "
    search_last_image 309956199498 'RHEL-7.4*x86_64*Access*' false

    echo -n "  RHEL81NBDE: "
    search_last_image 719622469867 'rhel81nbde' false

    echo -n "  RHEL82: "
    search_last_image 309956199498 'RHEL-8.2*x86_64*' true

    echo -n "  RHEL81: "
    search_last_image 309956199498 'RHEL-8.1*x86_64*' true

    echo -n "  RHEL78: "
    search_last_image 309956199498 'RHEL-7.8*x86_64*' true

    echo -n "  RHEL77: "
    search_last_image 309956199498 'RHEL-7.7*x86_64*' true

    echo -n "  RHEL75: "
    search_last_image 309956199498 'RHEL-7.5*x86_64*' true

    echo -n "  RHEL74: "
    search_last_image 309956199498 'RHEL-7.4*x86_64*' true

    echo -n "  WIN2012R2: "
    search_last_image 801119661308 'Windows_Server-2012-R2_RTM-English-64Bit-Base*' true

    echo -n "  WIN2019: "
    search_last_image 801119661308 'Windows_Server-2019-English-Full-Base-*' true
done

# For azure
# az vm image list --output table -p RedHat --all --sku 7-RAW
