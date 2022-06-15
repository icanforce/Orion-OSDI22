#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input 
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input
# Finally, include the AWS account number as the third parameter
#
# Example: ./deploy_classify.sh <S3-Bucket-Name> <Execution-Role-ARN> <AWS-Account-ID>

cp params.py /ParamTune


func_name='ParamTune'

cd ParamTune/

docker build -t param-tune-img .

cd ../

pwd=$(aws ecr get-login-password --region us-west-2)

aws ecr delete-repository --repository-name param-tune-img

aws ecr create-repository --repository-name param-tune-img

docker login -u AWS -p $pwd $3.dkr.ecr.us-west-2.amazonaws.com

docker tag  param-tune-img:latest $3.dkr.ecr.us-west-2.amazonaws.com/param-tune-img:latest

docker push $3.dkr.ecr.us-west-2.amazonaws.com/param-tune-img:latest

aws lambda create-function --function-name $func_name --role $2 --code "ImageUri=$3.dkr.ecr.us-west-2.amazonaws.com/param-tune-img:latest" --package-type "Image"

echo "Sleeping for 2.5 minutes before updating the function's memory size and timeout"

sleep 150

aws lambda update-function-configuration --function-name  $func_name --memory-size 10000 --timeout 800
