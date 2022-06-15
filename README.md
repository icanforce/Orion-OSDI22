
# OSDI '22: Orion
Keywords: Serverless DAGs, fusion, prewarming, VM sizes

## Introduction:
Serverless applications represented as DAGs have been growing in popularity. For many of these applications, it would be useful to estimate the end-to-end (E2E) latency and to allocate
resources to individual functions so as to meet probabilistic guarantees for the E2E latency. This goal has not been met till now due to three fundamental challenges. The first is the high
variability and correlation in the execution time of individual functions, the second is the skew in execution times of the parallel invocations, and the third is the incidence of cold starts.
In this paper, we introduce ORION to achieve these goals. We first analyze traces from a production FaaS infrastructure to identify three characteristics of serverless DAGs. We use these to motivate and to design three features. The first is a performance model that accounts for dependencies among functions in a DAG. The second is a method for bundling multiple parallel workers within a single VM thus mitigating content-based skew among these workers. The third is a method for pre-warming containers for subsequent functions in a DAG with the right lookahead time. We integrate these
three innovations and evaluate ORION on AWS Lambda with three serverless DAG applications. Our evaluation shows that compared to three competing approaches, ORION achieves up to 90% lower P95 latency or up to 53% lower $ cost.

![image](https://user-images.githubusercontent.com/22545817/163192376-b2c8bc2a-e3bb-4895-98a1-647c066bc338.png)

## Download Archive:
1. Archive is password protected. PASSWORD: vjm_orion_398

## Contents:
1. **Benchmarks-AWS-Lambda**: Source code of the evaluation applications used in Orion, the applications are to be deployed in AWS Lambda and orchestrated using AWS Step Functions. 
2. **DAG_Profiler**: This component of Orion profiles a user-defined DAG and constructs a E2E performance model. It takes as input the application's ARN (step functions) and extracts a CDF for each function/VM size in the DAG.
3. **Bundling_Manager**:  This component of Orion profiles the DAG with varying bundle sizes and shows the P50, P95 Latency and cost for each bundle size
4. **Prewarming_Optimizer**: This component of Orion uses the performance model of the DAG and decides the best prewarming delays for each function in the DAG
5. **DAG_Modeler**: This component uses the performance model of the DAG to decide the best VM size for each function in the DAG. 
6. **Comparison_to_Baselines**: This component contains the code for comparing Orion with CherryPick and Best Memory baselines. It also containts the code for Cherrypick's BO algorithm.

** Each folder contains the specific instruction for how to deploy/execute the code in that particular folder **

## Getting Started

### Requeriments

 * Amazon AWS CLI
 * Docker

### Setting up AWS Account

Orion was evaluated using Amazon AWS. We ran the experiments using three benchmark applications, which can be found at [Benchmark-AWS-Lambda](Benchmarks_AWS_Lambda/README.md). For testing ORION, reviewers must have an AWS account. The following sections broke down the steps to setup up the required AWS components.

### Setting up the Access Key

First, you need to setup an `Access Key` for your AWS account in case you do not have one. More details about setting up an access key can be found at [AWS Security Blog: Where's My Secret Access Key](https://aws.amazon.com/blogs/security/wheres-my-secret-access-key/)

It is important to write down the values for the `Access Key ID` and the `Secret Access Key`. These values are needed to configure the benchmark applications.

### Configure the AWS CLI

1. Configure AWS CLI by running `aws configure`, if it is not yet configured.
2. Enter the following: 
   * `AWS Access Key ID`
   * `AWS Secret Access Key`
   * Default region name
3. We recommend setting up a region where the user can set the memory up to 10GB since the **bundling manager** needs to setup VM up to 10GB. For more details, check [AWS re:Post/Unable to set Lambda memory over 3008MB](https://repost.aws/questions/QUKruWYNDYTSmP17jCnIz6IQ/unable-to-set-lambda-memory-over-3008-mb).

### Create a S3 bucket

1. Sign in to the AWS Management Console and open the [Amazon S3 console](https://console.aws.amazon.com/s3/).
2. Choose Create bucket.
3. The Create bucket wizard opens.
4. Under **Bucket name**, enter a DNS-compliant name for your bucket.
5. Under **AWS region** select the same region configured in the `AWS CLI`.
6. Choose Create bucket.

**Note**. More detailed instructions can be found in [AWS Docs: Creating a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).


### Create AWS Lambda execution role.

1. Open the [Roles page](https://console.aws.amazon.com/iam/home#/roles) in the IAM console.
2. Choose Create role.
3. Under Common use cases, choose Lambda.
4. Choose Next: Add Permissions.
5. Under **Permissions policies**, search for `AWSLambda_FullAccess` and check it.
6. Under **Set permissions boundary - *optional***, choose `Create role without a permissions boundary`.
7. Choose Next: Name, review, and create
8. Under **Role details**, set the Role Name to `OrionLambdaRole`.
9. Choose Create role.
10. Write down the `ARN` of the role just created (by clicking `View Role` option on the top). The `ARN` should look like as follow:

```python
# 123456789012 correspond to the account-id
arn:aws:iam::123456789012:role/OrionLambdaRole
```

**Note**. More detailed instructions can be found in [AWS Docs: AWS Lambda execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

### Create AWS Step Role

1. Open the [Roles page](https://console.aws.amazon.com/iam/home#/roles) in the IAM console.
2. Choose Create role.
3. Under **Use cases for other AWS services**, choose `Step Functions`.
4. Choose Next: Add Permissions.
5. Under **Permissions policies**, search for `AWSLambdaRole` and check it.
6. Under **Set permissions boundary - *optional***, choose `Create role without a permissions boundary`.
7. Choose Next: Name, review, and create
8. Under **Role details**, set the Role Name to `OrionStepRole`.
9. Choose Create role.
10. Write down the `ARN` of the role just created (by clicking `View Role` option on the top). The `ARN` should look like as follow:

```python
# 123456789012 correspond to the account-id
arn:aws:iam::123456789012:role/OrionStepRole
```

## Steps for reproducing Orion’s Results in AWS Lambda :
1. First, deploy an application from **Benchmarks-AWS-Lambda** in AWS StepFunctions. Check  [Benchmarks-AWS-Lambda/README.md](Benchmarks_AWS_Lambda/README.md) for more details.
2. Then, use the **DAG_Profiler** to profile and generate the latency distributions for each function in the DAG. Check [DAG_Profiler/README.md](DAG_Profiler/README.md) for more details.
3. Use **DAG_Modeler** to build the E2E performance model of the DAG, this module also contains the *VM_Size_Optimizer* to select the best VM size for each function in the DAG. Check [DAG_Modeler/README.md](DAG_Modelere/../README.md) for more details. 
4. Use **Bundling_Manager** to select the best bundle size 
5. Use **Prewarming_Optimizer** to select the best pre-warming delays for the stages in the DAG. Check  [Prewarming_Optimizer/README.md](Prewarming_Optimizer/README.md) for more details.
6. Use **Comparison_to_Baselines** to compare Orion with CherryPick and Best Memory baselines

**Note: After deploying the application (step 1), the user can go directly to "Comparison with Baselines" (step 6) since it already contains the optimized DAG parameters (VM sizes, Bundle size, and Prewarming Delays).** 

## Steps for Simulation Results:
1. **Policy_simulator** compares different prewarming policies 

