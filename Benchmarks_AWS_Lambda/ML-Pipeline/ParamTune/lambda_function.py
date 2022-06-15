import lightgbm as lgb
import boto3
import numpy as np
from boto3.s3.transfer import TransferConfig
import json
import random
import time
import os
from multiprocessing import Process, Manager
from params import *


def handler(event, context):
 if('dummy' in event) and (event['dummy'] == 1):
      print("Dummy call in ML Tune, doing nothing")
      return {"out":"Dummy call in ML Tune, doing nothing"}
		    
 #context = "0,15"
 #os.system("taskset -p --cpu-list " + context  + " %d" % os.getpid())
 start_time = int(round(time.time() * 1000))
 s3_client = boto3.client(
  's3',
  aws_access_key_id=accessKeyId,
  aws_secret_access_key=accessKey
 )
 bucket_name = bucketName
 config = TransferConfig(use_threads=False)

 filename = "/tmp/Digits_Train_Transform.txt"
 f = open(filename, "wb")
 start_download = int(round(time.time() * 1000))
 for i in range(1):
     s3_client.download_fileobj(bucket_name, "ML_Pipeline/train_pca_transform_2.txt" , f, Config=config)
 end_download = int(round(time.time() * 1000))
 
 start_process = int(round(time.time() * 1000))
 f.close()
 end_time = int(round(time.time() * 1000))
 train_data = np.genfromtxt('/tmp/Digits_Train_Transform.txt', delimiter='\t')
 
 print("train data shape")
 print(train_data.shape)

 
 y_train = train_data[0:5000,0]
 X_train = train_data[0:5000,1:train_data.shape[1]]
 #lgb_train = lgb.Dataset(X_train, y_train)

 print(type(y_train))
 #print(type(lgb_train))
 manager = Manager() 
 return_dict = manager.dict()  
 process_dict = manager.dict()
 upload_dict = manager.dict()
 num_of_trees=event['num_of_trees']
 depthes=event['max_depth'] 
 feature_fractions=event['feature_fraction']
 for runs in range(len(num_of_trees)): 
     # Use multiple processes to train trees in parallel
     threads=event['threads']
     ths = []
     for t in range(threads):
         ths.append(Process(target=train_tree, args=(t, X_train, y_train, event, num_of_trees[runs], depthes[runs], feature_fractions[runs], s3_client,  bucket_name, config, return_dict, num_of_trees[runs], process_dict, upload_dict)))
     for t in range(threads):
         ths[t].start()
     for t in range(threads):
         ths[t].join()
 end_process = int(round(time.time() * 1000))		 
 print("download duration: " + str(end_time-start_time))
 end_time = int(round(time.time() * 1000))
 e2e=end_time-start_time
 print("E2E duration: " + str(e2e))
 j= {
        'statusCode': 200,
        'body': json.dumps('Done Training Threads = ' + str(threads)),
        'key1': event['key1'],
        'duration': e2e,		
        'trees_max_depthes': return_dict.keys(),		
        'accuracies': return_dict.values(),
        'process_times': process_dict.values(),
        'upload_times': upload_dict.values(),
        'download_times': (end_download - start_download),
        'PCA_Download':  event['PCA_Download'],
        'PCA_Process': event['PCA_Process'],
        'PCA_Upload': event['PCA_Upload']
 }
 print(j)
 return(j)

def train_tree(t_index, X_train, y_train, event, num_of_trees, max_depth, feature_fraction,  s3_client, bucket_name, config, return_dict, runs, process_dict, upload_dict): 
 lgb_train = lgb.Dataset(X_train, y_train)
 _id=str(event['mod_index']) + "_" + str(t_index)
 chance = 0.8  #round(random.random()/2 + 0.5,1)
 params = {
    'boosting_type': 'gbdt',
    'objective': 'multiclass',
    'num_classes' : 10,
    'metric': {'multi_logloss'},
    'num_leaves': 50,
    'learning_rate': 0.05,
    'feature_fraction': feature_fraction,
    'bagging_fraction': chance, # If model indexes are 1->20, this makes feature_fraction: 0.7->0.9
    'bagging_freq': 5,
    'max_depth': max_depth,
    'verbose': -1,
    'num_threads': 2
 }
 print('Starting training...')
 start_process = int(round(time.time() * 1000))
 gbm = lgb.train(params,
                lgb_train,
                num_boost_round=num_of_trees, # number of trees
                valid_sets=lgb_train,
                early_stopping_rounds=5)

 y_pred = gbm.predict(X_train, num_iteration=gbm.best_iteration)
 count_match=0
 for i in range(len(y_pred)):
     #print(y_pred[i])
     #print(y_train[i])
     result = np.where(y_pred[i] == np.amax(y_pred[i]))[0]
     #print(result)
     #print(y_train[i])
     if result == y_train[i]:
        count_match = count_match +1    
 acc = count_match/len(y_pred)
 end_process = int(round(time.time() * 1000))
 

 model_name="lightGBM_model_" + str(_id) + ".txt"
 gbm.save_model("/tmp/" + model_name)
 print("Ready to uploaded " + model_name )
 start_upload = int(round(time.time() * 1000))
 s3_client.upload_file("/tmp/" + model_name, bucket_name, "ML_Pipeline/"+model_name, Config=config)
 end_upload = int(round(time.time() * 1000))

 print("model uploaded " + model_name )

 #end_time = int(round(time.time() * 1000))
 #print("duration: " + str(end_time-start_time))
 #subfilename = "Train_" + event['key1'] + "_id_" + str(_id) + "_start_" + str(start_time) + "_end_"+ str(end_time)
 #filename = "/tmp/" + subfilename
 #f = open(filename, "w")
 #f.write(filename)
 #f.close()
 #s3_client.upload_file(filename, bucket_name, "LightGBM_Times/" + subfilename, Config=config)

 return_dict[str(runs) + "_" + str(max_depth) + "_" + str(feature_fraction)] = acc
 process_dict[str(runs) + "_" + str(max_depth) + "_" + str(feature_fraction)] = (end_process - start_process)
 upload_dict[str(runs) + "_" + str(max_depth) + "_" + str(feature_fraction)] = (end_upload - start_upload)
 return {
        'statusCode': 200,
        'body': json.dumps('Done Training With Accuracy = ' + str(acc)),
        '_id': _id,
        'key1': event['key1']
 }


