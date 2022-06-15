#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input

cp params.py PCA/


cd PCA/; zip -r9 ../PCA_Package.zip ./*; cd ../

# upload package
aws s3 cp PCA_Package.zip  s3://$1/

aws lambda create-function --function-name PCA --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=PCA_Package.zip" --handler "lambda_function.lambda_handler"

sleep 1

aws lambda update-function-configuration --function-name  PCA --memory-size 5000 --timeout 800 --layers arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python37-SciPy1x:35

echo "PCA function deployed correctly with ARN:"
pca_arn=$(aws lambda get-function --function-name PCA | grep Arn | grep PCA | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $pca_arn

