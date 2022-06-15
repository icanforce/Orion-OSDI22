#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input 
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input
# Finally, include the AWS account number as the third parameter
#
# Example: ./deploy_classify.sh <S3-Bucket-Name> <Execution-Role-ARN> <AWS-Account-ID>

cp params.py Split/
cp params.py Extract/
cp params.py Classify/


func_name='Classify'
image_name='video-analytics-image'
cd Classify/

cat params.py app_s3_step_new.py > app_s3_step.py

docker image rm $image_name

docker build -t $image_name .

cd ../

region=$(aws configure get region)
pwd=$(aws ecr get-login-password --region ${region})

aws ecr delete-repository --repository-name $image_name

aws ecr create-repository --repository-name $image_name

docker login -u AWS -p $pwd $3.dkr.ecr.${region}.amazonaws.com

docker tag  $image_name:latest $3.dkr.ecr.${region}.amazonaws.com/$image_name:latest

docker push $3.dkr.ecr.${region}.amazonaws.com/$image_name:latest

aws lambda create-function --function-name $func_name --role $2 --code "ImageUri=$3.dkr.ecr.${region}.amazonaws.com/$image_name:latest" --package-type "Image"

echo "Sleeping for 2.5 minutes before updating the function's memory size and timeout"

sleep 150

aws lambda update-function-configuration --function-name  $func_name --memory-size 10000 --timeout 800
