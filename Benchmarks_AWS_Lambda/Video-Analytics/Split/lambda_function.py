#!/usr/bin/env python
import os
import json
import boto3
from boto3.s3.transfer import TransferConfig
import subprocess
import re
import time
from params import *

FFMPEG_STATIC = "var/ffmpeg"

length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

def lambda_handler(event, context):
    if('dummy' in event) and (event['dummy'] == 1):
         print(accessKeyId)
         print(accessKey)
         print(bucketName) 
         print("Dummy call, doing nothing")
         return

    #print(subprocess.call([FFMPEG_STATIC]))
    s3_client = boto3.client(
        's3',
        aws_access_key_id=accessKeyId,
        aws_secret_access_key=accessKey
    )
    bucket_name = bucketName
    config = TransferConfig(use_threads=False)
    filename = "/tmp/src.mp4"
    f = open(filename, "wb")
    print(event)
    src_video=event['src_name']
    DOP=int(event['DOP'])
    detect_prob=int(event['detect_prob'])
    s3_client.download_fileobj(bucket_name, "Video_Src/min_"+src_video+".mp4" , f, Config=config)
    f.close()

    output = subprocess.Popen(FFMPEG_STATIC + " -i '"+filename+"' 2>&1 | grep 'Duration'",
                              shell = True,
                              stdout = subprocess.PIPE
    ).stdout.read().decode("utf-8")

    print(output)
    matches = re_length.search(output)
    count=0
    millis_list=[]
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                       int(matches.group(2)) * 60 + \
                       int(matches.group(3))
        print("Video length in seconds: "+str(video_length))

        start=0
        chunk_size=2 # in seconds
        while (start < video_length):
              end=min(video_length-start,chunk_size)
              millis = int(round(time.time() * 1000))
              millis_list.append(millis)
              chunk_video_name = 'min_' + src_video + "_" + str(count) + "_" + str(millis) + '.mp4'
              subprocess.call([FFMPEG_STATIC, '-i', filename, '-ss', str(start) , '-t', str(end),'-c', 'copy', '/tmp/'+chunk_video_name])
              
              count=count+1
              start=start+chunk_size
              s3_client.upload_file("/tmp/" + chunk_video_name, bucket_name, "Video_Chunks_Step/"+chunk_video_name, Config=config)
    print("Done!") 

    payload=count/DOP
    listOfDics = []   
    currentList = []
    currentMillis = []
    for i in range(count):
        if len(currentList) < payload:
           currentList.append(i)
           currentMillis.append(millis_list[i]) 
        if len(currentList) == payload:
           tempDic = {}
           tempDic['values'] = currentList
           tempDic['source_id'] = src_video
           tempDic['millis'] = currentMillis
           tempDic['detect_prob'] = detect_prob		   
           listOfDics.append(tempDic)
           currentList = []
           currentMillis = []

    returnedObj = {
      "detail": {
        "indeces": listOfDics 
        }
    }
    print(returnedObj)
    return returnedObj

