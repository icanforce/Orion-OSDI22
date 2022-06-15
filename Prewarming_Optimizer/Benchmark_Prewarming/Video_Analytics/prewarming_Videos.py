import boto3
import time
import os
import random
from multiprocessing import Process, Queue, Lock, Manager
import json

manager = Manager()
shared_dict_payloads = manager.dict()
shared_dict_payloads["Split"] = ['{ "src_name" : "5", "DOP" : "5", "detect_prob" : 2 }']
shared_dict_payloads["Extract"] = []
shared_dict_payloads["Classify"] = []

def invokeRealFunction(fname, payload, lock):
    lambda_client = boto3.client('lambda')
    client = boto3.client('logs')
    print("Executing " + fname + " with " + payload)
    out = lambda_client.invoke(FunctionName=fname,
                            InvocationType='RequestResponse',
                            #LogType='Tail',							
                            Payload=payload)

    if(fname == "Classify"):
        time.sleep(0.5)
        print("done!")
        #response_log_stream = client.describe_log_streams(logGroupName="/aws/lambda/"+fname, orderBy="LastEventTime", descending=True)
        #stream_name = response_log_stream['logStreams'][0]['logStreamName']
        #response = client.get_log_events(logGroupName="/aws/lambda/"+fname, logStreamName=stream_name)	
        #print("***** Logs ****************")
        #for i in response['events']:
        #    if("REPORT RequestId" in i['message']):
        #       print(i)
        #print(response['events'][-3:])
    	
    #print(response)
    #print(out)
    #print(out['LogResult'])    
    data = out['Payload'].read()
    encoding = 'utf-8'
    data_str = str(data,encoding)
    if(fname == "Split"):
        with lock:
          y = json.loads(data_str)
          list_js = y["detail"]["indeces"]
          shared_dict_payloads["Extract"] = [str(j).replace("'", "\"") for j in list_js] 
          print(" adding data to shared_dict_payloads[Extract]: " + data_str)
          print(len(shared_dict_payloads["Extract"]))
  
    elif(fname == "Extract"):
        with lock:
          currentList = shared_dict_payloads["Classify"]
          currentList.append(data_str)
          shared_dict_payloads["Classify"] = currentList
          print(" adding data to shared_dict_payloads[\"Classify\"]: " + data_str)
          print(len(shared_dict_payloads["Classify"]))	  

      
    print(fname)
    print("********************")
    print(data)
    print("********************")

def invokeDummyFunction(fname, queue, sleep_time):
    time.sleep(sleep_time)
    lambda_client = boto3.client('lambda')
    lambda_payload = '{"dummy": 1}'
    out = lambda_client.invoke(FunctionName=fname, 
                            InvocationType='RequestResponse',
                                      Payload=lambda_payload)

    queue.put(fname)
    print("prewarmed: " + fname)
    data = out['Payload'].read()
    print(data)

# Producer function that places data on the Queue, acting as our prewarming thread
def producer(queue, lock, functions_sleep_times):
    # Synchronize access to the console
    with lock:
        print('Starting prewarmer => {}'.format(os.getpid()))
         
    # Place our names on the Queue
    prewarmers = []
    for tuple_data in functions_sleep_times:
        for instance in range(tuple_data[1]):
            print("Prewarming: " + tuple_data[0])
            prewarmers.append(Process(target=invokeDummyFunction, args=(tuple_data[0], queue, tuple_data[2])))
        
    for p in prewarmers:
        p.start()
    for p in prewarmers:
        p.join()
        
    # Synchronize access to the console
    with lock:
        print('Prewarmer {} exiting...'.format(os.getpid()))
 
 
# The consumer function takes data off of the Queue, acting as our executing thread
def consumer(queue, lock, functions_num_of_inputs):
    # Synchronize access to the console
    with lock:
        print('Starting consumer => {}'.format(os.getpid()))
     
    # Run indefinitely
    executed = set()
    while True:
         
        # If the queue is empty, queue.get() will block until the queue has data
        fname = queue.get()
        #with lock:
        #     print('{} got {}'.format(os.getpid(), fname))
        num_instances = len(shared_dict_payloads[fname])
        if(fname in executed):
          continue
        if(num_instances < functions_num_of_inputs[fname]):
           queue.put(fname)
           continue
        executed.add(fname)  
        with lock:
             print('{} entered {}'.format(os.getpid(), fname))
        if(fname in shared_dict_payloads):
             print("**** found "  + fname + " in dict_payloads")
             num_instances = len(shared_dict_payloads[fname])
             print("num instances of " + fname + " are: " + str(num_instances))
             procs = []
             for  i in range(num_instances):
                  payload =  shared_dict_payloads[fname][i]
                  #print("***** executing " + fname +" payload " + payload )
                  proc = Process(target=invokeRealFunction, args=(fname, payload, lock))
                  procs.append(proc)
                  proc.start()
             for p in procs:
                  p.join()
     
             if(fname == "Classify"):
                break
        # Synchronize access to the console
        with lock:
            print('{} Done {}'.format(os.getpid(), fname))

if __name__ == '__main__':
    start_time = time.time() 
    # Tuples of: <Function names>, <Num of workers>, <Delay> 
    functions_sleep_times = [("Split",1, 0), ("Extract",5, 2.5), ("Classify",5, 0.1)]
    functions_num_of_inputs = {"Split": 1, "Extract": 5, "Classify": 5}
    # Create the Queue object
    queue = Queue()

    # Create payloads dictionary

    # Create a lock object to synchronize resource access
    lock = Lock()
 
    # Create our producer (Prewarming) processes by passing the producer function and it's arguments
    prewarmer = Process(target=producer, args=(queue, lock, functions_sleep_times))
 
    # Create consumer processes
    executer = Process(target=consumer, args=(queue, lock, functions_num_of_inputs))
         
    #executer.daemon = True
 
    # Start the producers and consumer
    # The Python VM will launch new independent processes for each Process object
 
    prewarmer.start()
    executer.start()
 
    # Like threading, we have a join() method that synchronizes our program
    prewarmer.join()
    executer.join()

    print("E2E Latenct : " + str((time.time() - start_time)) + " seconds ")

