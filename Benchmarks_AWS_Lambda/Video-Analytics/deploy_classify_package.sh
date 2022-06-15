#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input


cp params.py Classify/

cd Classify/; zip -r9 ../Classify_Package.zip ./*; cd ../

aws s3 cp Classify_Package.zip  s3://$1/


func_name='Classify'

aws lambda delete-function --function-name $func_name

aws lambda create-function --function-name $func_name --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=Classify_Package.zip" --handler "lambda_function.lambda_handler"

sleep 5

aws lambda update-function-configuration --function-name  $func_name --memory-size 10000 --timeout 800  --layers arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python37-SciPy1x:35

echo "Classify function deployed correctly with ARN:"
classify_arn=$(aws lambda get-function --function-name $func_name | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $classify_arn

aws lambda invoke --function-name $func_name -invocation-type Event --payload '{ "dummy1": 1 }' response.json
