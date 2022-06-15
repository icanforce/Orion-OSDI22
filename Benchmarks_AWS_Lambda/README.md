# Benchmarks
This folder contains the source code of applications used to evaluate Orion in []. Below are the details of each of the three applications and how to deploy them in AWS Lambda.

## Video-Analytics: 
The application splits an input video into chunks of 10 sec. For each chunk, it extracts a representative frame. Then, the application detects the object in the frame using a [yolo5 pre-trained model](https://github.com/ultralytics/yolov5). 

The *Video-Analytics* application workflow is as follows:

![Sonic-Video](https://user-images.githubusercontent.com/22545817/158837208-cc5c7c32-3579-41e2-9934-aa7460ef41fc.png)

The Video-Analytics application consists of three serverless functions (Split, Extract, and Classify). The source code of the three functions can be found at [Benchmarks-AWS-Lambda/Video-Analytics/](Video-Analytics/README.md).

### How to Deploy:
1. Functions *Split* and *Extract* can be deployed as packages as described in [AWS Docs: Deploy Python Lambda functions with .zip file archives](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html). Notice that these two functions use FFMPEG and FFPROBE (found under /var/ directory). Please unzip the two files ffmpeg.zip and ffprobe.zip before deploying the functions.

2. Function *Classify* has large-sized dependencies (YOLOV5 pre-trained model) and cannot be deployed as a package. Instead, it should be deployed as a container image using Docker and Amazon ECR as described in [AWS Docs: Creating Lambda container images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

3. After deployment of the three functions, a state-machine should be created on AWS StepFunction using the JSON description listed here: [Benchmarks-AWS-Lambda/Video-Analytics/JsonStateMachine.json](Video-Analytics/JsonStateMachine.json)

### Steps

1. Configure the `params.py` file as indicated in the [Setup](Video-Analytics/README.md#setup) section. 
2. Deploy application using `deploy_application.sh`

```bash
cd Video-Analytics
./deploy_application.sh
```

**For more details on how to deploy Video-Analytics application, please check [Video-Analytics/README.md](Video-Analytics/README.md)** 

## ML-pipeline
The application trains a [lighGBM model](https://lightgbm.readthedocs.io/en/latest/) on the [MNIST](http://yann.lecun.com/exdb/mnist/) dataset and performs hyper parameter tuning. 

The LightGBM application workflow is as follows:

![image](https://user-images.githubusercontent.com/22545817/119402674-44861700-bcab-11eb-86e4-66f27b88a060.png)

We include the JSON description for the workflow (using StepFunctions) along with all function source codes in this repo.

The Machine Learning application consists of 3 functions: *PCA*, *ParamTune*, and *Combine*. 

### How to Deploy
1. All 3 functions can be deployed as packages. ParamTune function uses LightGBM library, which dependencies are included in the package under: [Benchmarks-AWS-Lambda/ML-Pipeline/](ML-Pipeline/README.md)

2. After deployment of the three functions, a state-machine should be created on AWS StepFunction using the JSON description listed here: `Benchmarks-AWS-Lambda/ML-Pipeline/JsonStateMachine.json`.

### Steps

1. Configure the `params.py` file as indicated in the [Setup](ML-Pipeline/README.md#setup) section. 
2. Deploy application using `deploy_application.sh`

```bash
cd ML-Pipeline
./deploy_application.sh
```
**For more details on how to deploy ML-Pipeline application, please check [ML-Pipeline/README.md](ML-Pipeline/README.md)** 


## ChatBot
Trains a one-vs-all classifier for the ChatBots Intent Recognition Dataset, available on [Kaggle](https://www.kaggle.com/datasets/elvinagammed/chatbots-intent-recognition-dataset).

The ChatBot application workflow is as follows:

![image](https://user-images.githubusercontent.com/22545817/161560599-c1efb7c3-d59d-45cd-97a1-c10dd94cbcbd.png)


We include the JSON description for the workflow (using StepFunctions) a long with all functions source codes.

### How to Deploy
1. The ChatBot application consists of 2 functions: SplitChatBot and Train-Intent-Classifier. Both functions can be deployed directly on the Lambda's console, no packaging is required.

2. After deployment of the two functions, a state-machine should be created on AWS StepFunction using the JSON description listed here: `Benchmarks-AWS-Lambda/ChatBot/JsonStateMachine.json`

### Steps

1. Configure the `params.py` file as indicated in the [Setup](ChatBot/README.md#setup) section. 
2. Deploy application using `deploy_application.sh`

```bash
cd Chatbot
./deploy_application.sh
```
**For more details on how to deploy ML-Pipeline application, please check [Chatbot/README.md](ChatBot/README.md)** 



