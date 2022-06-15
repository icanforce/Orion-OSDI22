#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input


cp params.py Split/
cp params.py Extract/
cp params.py Classify/

cd Extract/var/
tar -xzvf ffprobe.tar.gz
tar -xzvf ffmpeg.tar.gz

cd ../../

cd Extract/; zip -r9 ../Extract_Package.zip ./*; cd ../

aws s3 cp Extract_Package.zip  s3://$1/


func_name='Extract'

aws lambda create-function --function-name $func_name --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=Extract_Package.zip" --handler "lambda_function.lambda_handler"

sleep 5

aws lambda update-function-configuration --function-name  $func_name --memory-size 5000 --timeout 800

echo "Extract function deployed correctly with ARN:"
extract_arn=$(aws lambda get-function --function-name $func_name | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $extract_arn
