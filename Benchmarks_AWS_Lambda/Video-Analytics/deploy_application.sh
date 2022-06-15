#!/bin/bash

# Example Usage: ./deploy_application.sh

# Reading the following parameters from params.py
S3_buncket_name=$(more params.py | grep bucketName | awk -F'\"' '{print $2}')
Lambda_role_arn=$(more params.py | grep LambdaRoleARN | awk -F'\"' '{print $2}')
Step_role_arn=$(more params.py | grep StepRoleARN | awk -F'\"' '{print $2}')
AWS_account_id=$(more params.py | grep AccountID | awk -F'\"' '{print $2}')

echo "Using the following user parameters"
echo "S3_buncket_name $S3_buncket_name"
echo "Lambda_role_arn $Lambda_role_arn"
echo "Step_role_arn $Step_role_arn"
echo "AWS_account_id $AWS_account_id"

echo "Deploying Split:"
./deploy_split.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying Extract:"
./deploy_extract.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying Shuffle:"
./deploy_shuffle.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying Classify:"
./deploy_classify.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

split_arn=$(aws lambda get-function --function-name Split | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
extract_arn=$(aws lambda get-function --function-name Extract | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
shuffle_arn=$(aws lambda get-function --function-name Shuffle | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
classify_arn=$(aws lambda get-function --function-name Classify | grep Arn | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')

echo $split_arn
echo $extract_arn
echo $shuffle_arn
echo $classify_arn



# Creating stepfunction state machnine
# This will generate a state machine and print its ARN in the console. Save the ARN in a file as it is fed to other models as input

echo "Creating StateMachine:"

aws stepfunctions create-state-machine --name "Orion_Video_SM" --definition "{   \"Comment\": \"Video Analytics DAG with varying DOPs\",   \"StartAt\": \"Split\",   \"States\": {     \"Split\": {       \"Type\": \"Task\",       \"Resource\":  \"$split_arn\",       \"Next\": \"Extract_Map\"     },     \"Extract_Map\" : {       \"Type\": \"Map\",       \"InputPath\": \"$.detail\",       \"ItemsPath\": \"$.indeces\",       \"MaxConcurrency\": 100,       \"Iterator\": {          \"StartAt\": \"Extract\",          \"States\": {             \"Extract\": {              \"Type\" : \"Task\",              \"Resource\": \"$extract_arn\",              \"End\": true               }                }       },       \"Next\": \"Shuffle\"     },      \"Shuffle\": {       \"Type\": \"Task\",       \"Resource\": \"$shuffle_arn\",       \"Next\": \"Object_Map\"     },       \"Object_Map\" : {       \"Type\": \"Map\",       \"InputPath\": \"$.detail\",       \"ItemsPath\": \"$.indeces\",       \"MaxConcurrency\": 100,       \"Iterator\": {          \"StartAt\": \"Classify\",          \"States\": {               \"Classify\": {              \"Type\" : \"Task\",              \"Resource\": \"$classify_arn\",              \"End\": true               }          }          },         \"End\": true       }         } }" --role-arn $Step_role_arn
