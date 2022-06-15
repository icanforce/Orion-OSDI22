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


echo "Deploying Packages"
echo "Deploying SplitChatBot:"
./deploy_SplitChatBot.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying TrainIntentClassifier:"
./deploy_TrainIntent.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

SplitChatBot_arn=$(aws lambda get-function --function-name SplitChatBot | grep Arn | grep SplitChatBot | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
TrainIntentClassifier_arn=$(aws lambda get-function --function-name TrainIntentClassifier | grep Arn | grep TrainIntentClassifier | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
# Creating stepfunction state machnine
# This will generate a state machine and print its ARN in the console. Save the ARN in a file as it is fed to other models as input

echo "Creating StateMachine:"
aws stepfunctions create-state-machine --name "Orion_ChatBot_SM" --definition "{  \"Comment\": \"A State Machine for LightGBM\",  \"StartAt\": \"SplitChatBot\",  \"States\": {    \"SplitChatBot\": {      \"Type\": \"Task\",      \"Resource\": \"$SplitChatBot_arn\",      \"Next\": \"Train_LR_Map\"    },    \"Train_LR_Map\" : {      \"Type\": \"Map\",      \"InputPath\": \"$.detail\",      \"ItemsPath\": \"$.indeces\",      \"MaxConcurrency\": 100,      \"Iterator\": {         \"StartAt\": \"TrainIntentClassifier\",         \"States\": {            \"TrainIntentClassifier\": {             \"Type\" : \"Task\",             \"Resource\": \"$TrainIntentClassifier_arn\",             \"End\": true              }         }      },       \"End\": true    }  }}" --role-arn $Step_role_arn

