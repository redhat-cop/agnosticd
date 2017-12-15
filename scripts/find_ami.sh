#!/bin/bash

name=$1
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text)
do
  echo "${region}: $(aws ec2 describe-images --owners amazon --filters Name=name,Values=${name} --query "reverse(sort_by(Images, &CreationDate))[0].ImageId" --output text --region $region)"
done
