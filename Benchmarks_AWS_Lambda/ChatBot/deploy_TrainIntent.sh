#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input

cp params.py TrainIntentClassifier/


cd TrainIntentClassifier/; zip -r9 ../TrainIntentClassifier_Package.zip ./*; cd ../

#zip -r9 TrainIntentClassifier_Package.zip TrainIntentClassifier/*

aws s3 cp TrainIntentClassifier_Package.zip  s3://$1/


aws lambda create-function --function-name TrainIntentClassifier --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=TrainIntentClassifier_Package.zip" --handler "lambda_function.lambda_handler"

sleep 5

aws lambda update-function-configuration --function-name  TrainIntentClassifier --memory-size 10000 --timeout 800 --layers arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python37-SciPy1x:35

echo "TrainIntentClassifier function deployed correctly with ARN:"
TrainIntentClassifier_arn=$(aws lambda get-function --function-name TrainIntentClassifier | grep Arn | grep TrainIntentClassifier | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $TrainIntentClassifier_arn

