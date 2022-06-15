#!/bin/bash

# First, create a bucket on S3 to use as the host for the deployment packages
# This script takes that bucket name as the first input
# Second, create an execution role in AWS console. The execution role needs Full Lambda Access permissions
# This script takes that execution role ARN as the second input

cp params.py Split/
cp params.py Extract/
cp params.py Classify/

cd Split/var/
tar -xzvf ffprobe.tar.gz
tar -xzvf ffmpeg.tar.gz

cd ../../

cd Split/; zip -r9 ../Split_Package.zip ./*; cd ../

#zip -r9 Split_Package.zip Split/*

aws s3 cp Split_Package.zip  s3://$1/


aws lambda create-function --function-name Split --runtime python3.7 --role $2 --code "S3Bucket=$1,S3Key=Split_Package.zip" --handler "lambda_function.lambda_handler"

# Upload benchmarking videos
for f in Sample_Benchmarking_Video/*; do

    aws s3 cp $f  s3://$1/Video_Src/

done

sleep 5

aws lambda update-function-configuration --function-name  Split --memory-size 5000 --timeout 800

echo "Split function deployed correctly with ARN:"
split_arn=$(aws lambda get-function --function-name Split | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
echo $split_arn

