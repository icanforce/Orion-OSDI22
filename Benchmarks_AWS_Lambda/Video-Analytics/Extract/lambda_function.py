#!/usr/bin/env python
import os
from urllib.parse import unquote_plus
import json
import boto3
from boto3.s3.transfer import TransferConfig
import subprocess
import re
import time
from params import *

FFMPEG_STATIC = "var/ffmpeg"


def lambda_handler(event, context):
    if('dummy' in event) and (event['dummy'] == 1):
       print("Dummy call, doing nothing")
       return {"Extract Got Dummy" : "Dummy call, doing nothing"}

    #print(subprocess.call([FFMPEG_STATIC]))
    s3_client = boto3.client(
        's3',
        aws_access_key_id=accessKeyId,
        aws_secret_access_key=accessKey
    )
    config = TransferConfig(use_threads=False)
    bucket_name = bucketName
    print(event)
    list_of_chunks = event['values']
    src_video = event['source_id']
    millis_list = event['millis']
    detect_prob = event['detect_prob']
    count=0
    extract_millis = []
    for record in list_of_chunks:
        filename = "/tmp/chunk_" + str(record) + ".mp4"
        f = open(filename, "wb")
        key = "Video_Chunks_Step/min_"+str(src_video)
        key = key +"_"+str(record)+"_"
        key = key + str(millis_list[count])+".mp4"

        count = count + 1

        s3_client.download_fileobj(bucket_name, key , f, Config=config)
        f.close()
        millis = int(round(time.time() * 1000))
        extract_millis.append(millis)

        frame_name = key.replace("Video_Chunks_Step/","").replace("min", "frame").replace(".mp4","_" + str(millis) + ".jpg")
        subprocess.call([FFMPEG_STATIC, '-i', filename, '-frames:v', "1" , "-q:v","1", '/tmp/'+frame_name])
        try:
            s3_client.upload_file("/tmp/"+frame_name, bucket_name, "Video_Frames_Step/"+frame_name, Config=config)
        except:
            s3_client.upload_file("var/Frame_1.jpg", bucket_name, "Video_Frames_Step/"+frame_name, Config=config)
    print("Done!") 

    obj= {
        'statusCode': 200,
        'counter': count,
        'millis1': millis_list,
        'millis2': extract_millis,
        'source_id': src_video,
        'detect_prob': detect_prob,		
        'values': list_of_chunks,
        'body': json.dumps('Download/Split/Upload Successful!'),
        
    }
    #print(obj)
    return obj


