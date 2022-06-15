from numpy import array
from numpy import mean
from numpy import cov
from numpy.linalg import eig
from numpy import genfromtxt
from numpy import concatenate
from numpy import savetxt
import numpy as np

import json
import random
import time
import io

import boto3
from boto3.s3.transfer import TransferConfig
from params import *

s3_client = boto3.client(
  's3',
  aws_access_key_id=accessKeyId,
  aws_secret_access_key=accessKey
 )
bucket_name = bucketName
config = TransferConfig(use_threads=False)
filename = "/tmp/Digits_Test.txt"
f = open(filename, "wb")
s3_client.download_fileobj(bucket_name, "ML_Pipeline/Digits_Test_Small.txt" , f, Config=config)
f.close()
print("Init download ###########################")

def lambda_handler(event, context):
 if('dummy' in event) and (event['dummy'] == 1):
     print("Dummy call, doing nothing")
     return
 
 
 
 start_time = int(round(time.time() * 1000))

 
 start_download = int(round(time.time() * 1000))
 filename = "/tmp/Digits_Train_Org.txt"
 f = open(filename, "wb")
 s3_client.download_fileobj(bucket_name, "ML_Pipeline/Digits_Train_org.txt" , f, Config=config)
 f.close()
 end_download = int(round(time.time() * 1000))
 
 start_process = int(round(time.time() * 1000))
 #filename = "/tmp/Digits_Test.txt"
 #f = open(filename, "wb")
 #s3_client.download_fileobj(bucket_name, "LightGBM_Data_Input/Digits_Test_Small.txt" , f, Config=config)
 #f.close()

 train_data = genfromtxt('/tmp/Digits_Train_Org.txt', delimiter='\t')
 #test_data = genfromtxt('/tmp/Digits_Test.txt', delimiter='\t')

 train_labels = train_data[:,0]
 #test_labels = test_data[:,0]

 A = train_data[:,1:train_data.shape[1]]
 #B = test_data[:,1:test_data.shape[1]]

 # calculate the mean of each column
 MA = mean(A.T, axis=1)
 #MB = mean(B.T, axis=1)

 # center columns by subtracting column means
 CA = A - MA
 #CB = B - MB

 # calculate covariance matrix of centered matrix
 VA = cov(CA.T)

 # eigendecomposition of covariance matrix
 values, vectors = eig(VA)

 # project data
 PA = vectors.T.dot(CA.T)
 #PB = vectors.T.dot(CB.T)
 
 np.save("/tmp/vectors_pca.txt", vectors)
 
 #savetxt("/tmp/vectors_pca.txt", vectors, delimiter="\t")
 #vectors.tofile("/tmp/vectors_pca.txt")
 
 #print("vectors shape:")
 #print(vectors.shape)


 first_n_A = PA.T[:,0:100].real
 #first_n_B = PB.T[:,0:10].real
 train_labels =  train_labels.reshape(train_labels.shape[0],1)
 #test_labels = test_labels.reshape(test_labels.shape[0],1)

 first_n_A_label = concatenate((train_labels, first_n_A), axis=1)
 #first_n_B_label = concatenate((test_labels, first_n_B), axis=1)

 savetxt("/tmp/Digits_Train_Transform.txt", first_n_A_label, delimiter="\t")
 #savetxt("/tmp/Digits_Test_Transform.txt", first_n_B_label, delimiter="\t")

 end_process = int(round(time.time() * 1000))
 
 start_upload = int(round(time.time() * 1000))
 s3_client.upload_file("/tmp/vectors_pca.txt.npy", bucket_name, "ML_Pipeline/vectors_pca.txt", Config=config)
 s3_client.upload_file("/tmp/Digits_Train_Transform.txt", bucket_name, "ML_Pipeline/train_pca_transform_2.txt", Config=config)

 #s3_client.upload_file("/tmp/Digits_Test_Transform.txt", bucket_name, "LightGBM_Data/test_pca_transform.txt", Config=config)

 end_upload = int(round(time.time() * 1000)) 
 end_time = int(round(time.time() * 1000))
 
 subfilename = "PCA_" + event['key1'] + "_start_" + str(start_time) + "_end_"+ str(end_time)
 filename = "/tmp/" + subfilename
 f = open(filename, "w")
 f.write(filename)
 f.close()
 s3_client.upload_file(filename, bucket_name, "ML_Pipeline/LightGBM_Times/" + subfilename, Config=config)
 
 bundle_size= event['bundle_size']
 list_hyper_params=[]
 all_runs = 4*4*4

 for feature_fraction in [0.25, 0.5, 0.75, 0.95]:
     max_depth = 10
     for num_of_trees in  [5, 10, 15, 20]:
         list_hyper_params.append((num_of_trees, max_depth, feature_fraction))

 #random.shuffle(list_hyper_params)
 #print(list_hyper_params)

 returnedDic={}
 returnedDic["detail"] = {}
 returnedDic["detail"]["indeces"] = []

 num_of_trees=[]
 max_depth=[]
 feature_fraction = []
 num_bundles=0
 count=0
 for tri in list_hyper_params:
     feature_fraction.append(tri[2])
     max_depth.append(tri[1])
     num_of_trees.append(tri[0])
     count+= 1
     if(count >= bundle_size):
        count=0
        num_bundles +=1
        j={ "mod_index":num_bundles, "PCA_Download": (end_download - start_download), "PCA_Process": (end_process - start_process), "PCA_Upload": (end_upload - start_upload) , "key1": "inv_300", "num_of_trees": num_of_trees, "max_depth": max_depth, "feature_fraction": feature_fraction, "threads": 6}
        num_of_trees=[]
        max_depth=[]
        feature_fraction = []
        returnedDic["detail"]["indeces"].append(j)

 print(returnedDic)
 return returnedDic


