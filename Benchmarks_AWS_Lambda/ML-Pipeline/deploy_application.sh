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


# Upload dataset
aws s3 cp Dataset/Digits_Test.txt s3://$S3_buncket_name/ML_Pipeline/Digits_Test.txt
aws s3 cp Dataset/Digits_Test.txt s3://$S3_buncket_name/ML_Pipeline/Digits_Test_Small.txt
aws s3 cp Dataset/Digits_Train.txt s3://$S3_buncket_name/ML_Pipeline/Digits_Train.txt
aws s3 cp Dataset/Digits_Train.txt s3://$S3_buncket_name/ML_Pipeline/Digits_Train_org.txt

echo "Deploying Packages"
echo "Deploying PCA:"
./deploy_PCA.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying ParamTune"
./deploy_ParamTune.py $S3_buncket_name $Lambda_role_arn $AWS_account_id

echo "Deploying CombineModels"
./deploy_CombineModels.sh $S3_buncket_name $Lambda_role_arn $AWS_account_id


pca_arn=$(aws lambda get-function --function-name PCA | grep Arn | grep PCA | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
paramTune_arn=$(aws lambda get-function --function-name ParamTune | grep Arn | grep ParamTune | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')
combineModels_arn=$(aws lambda get-function --function-name CombineModels | grep Arn | grep CombineModels | awk -F'Arn\": "' '{print $2}' | awk -F'"' '{print $1}')

# Creating stepfunction state machnine
# This will generate a state machine and print its ARN in the console. Save the ARN in a file as it is fed to other models as input

echo "Creating StateMachine:"
aws stepfunctions create-state-machine --name "Orion_ML_SM" --definition "{   \"Comment\": \"A State Machine for LightGBM\",   \"StartAt\": \"PCA\",   \"States\": {     \"PCA\": {       \"Type\": \"Task\",       \"Resource\": \"$pca_arn\",       \"Next\": \"Parameter_Tune_Map\"     },     \"Parameter_Tune_Map\" : {       \"Type\": \"Map\",       \"InputPath\": \"$.detail\",       \"ItemsPath\": \"$.indeces\",       \"MaxConcurrency\": 100,       \"Iterator\": {          \"StartAt\": \"ParamTune\",          \"States\": {             \"ParamTune\": {              \"Type\" : \"Task\",              \"Resource\": \"$paramTune_arn\",              \"End\": true               }          }       },        \"Next\": \"CombineModels\"     },      \"CombineModels\": {       \"Type\": \"Task\",       \"Resource\": \"$combineModels_arn\",       \"End\": true     }   } }" --role-arn $Step_role_arn

