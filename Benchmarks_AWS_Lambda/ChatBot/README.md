# ChatBot

This folder contains the source code of the Video Analytics application


## Folder Contents

1. [SplitChatBot](SplitChatBot/): Code for **SplitChatBot** function. To deploy *SplitChatBot*, run:

```bash
./deploy_SplitChatBot.sh [S3-Bucket-Name] [Execution-role-ARN] [AWS-Account-ID]
```

2. [TrainIntentClassifier](TrainIntentClassifier/): Code for **Extract** function. To deploy *TrainIntentClassifier*, run:
   
```bash
./deploy_TrainIntent.sh [S3-Bucket-Name] [Execution-role-ARN] [AWS-Account-ID]
```

3. `deploy_application.sh`: script to deploy the entire application.

## Setup

1. The first step is for the user to fill **params.py** with user-specific access credentials, S3 bucket, and roles setup in the [Getting Started](../../README.md#getting-started).

```python
accessKeyId="DummyID" 
accessKey="DummyKey"
bucketName="DummyBucket"
LambdaRoleARN="arn:aws:iam::XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
StepRoleARN="arn:aws:iam::XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
AccountID="1234567890"
```

The contents of params.py is as follows:

* `accessKeyId`: Access key identifier of the AWS account used by the user. 
* `accessKey`: Secret Access Key of the AWS account used by the user. 
* `bucketName`: S3 bnucket that will be used to store application's packages and intermediate data.
* `LambdaRoleARN`: Lambda execution role.
* `StepRoleARN`: StepFunctions execution role.
* `AccountID`: ID of the AWS account. It can be found at [AWS Docs: Finding your AWS account ID](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html#FindingYourAWSId)


2. After adding all fields to `params.py` file, run `./deploy_application.sh` to deploy the Video-Analytics application

```bash
./deploy_application.sh
```