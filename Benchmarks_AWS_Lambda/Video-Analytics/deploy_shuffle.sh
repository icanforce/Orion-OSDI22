#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input


cd Shuffle/; zip -r9 ../Shuffle_Package.zip ./*; cd ../

aws s3 cp Shuffle_Package.zip  s3://$1/

aws lambda create-function --function-name Shuffle --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=Shuffle_Package.zip" --handler "lambda_function.lambda_handler"

sleep 1

aws lambda update-function-configuration --function-name  Shuffle --memory-size 5000 --timeout 800

echo "Shuffle function deployed correctly with ARN:"
shuffle_arn=$(aws lambda get-function --function-name Shuffle | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $shuffle_arn

