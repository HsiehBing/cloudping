#!/bin/bash


REGIONS=$(aws ec2 describe-regions \
    --all-regions \
    --query "Regions[].{Name:RegionName}" \
    --output text)

for region in $REGIONS # 注意此處使用$符號來引用變數的值
do
    export AWS_DEFAULT_REGION=$region
    chalice deploy 
done
