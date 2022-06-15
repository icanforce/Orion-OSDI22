import boto3
import time
import os
import random
from multiprocessing import Process, Queue, Lock, Manager
import json

manager = Manager()
shared_dict_payloads = manager.dict()
shared_dict_payloads["SplitChatBot"] = ['{  "skew": 1,   "bundle_size": 2,   "Network_Bound": 1  }']
shared_dict_payloads["TrainIntentClassifier"] = []


def invokeRealFunction(fname, payload, lock):
    lambda_client = boto3.client('lambda')
    print("Executing " + fname + " with " + payload)
    out = lambda_client.invoke(FunctionName=fname,
                            InvocationType='RequestResponse',
                                      Payload=payload)

    
    print(out)
    data = out['Payload'].read()
    encoding = 'utf-8'
    data_str = str(data,encoding)
    if(fname == "SplitChatBot"):
      y = json.loads(str(data, encoding))
      list_js = y["detail"]["indeces"]
      shared_dict_payloads["TrainIntentClassifier"] = [str(j).replace("'", "\"") for j in list_js]
      
    elif(fname == "Parameter_Tune"):
        with lock:
          print(" adding data to shared_dict_payloads[\"CombineModels\"]: " + data_str)
          currentList = shared_dict_payloads["CombineModels"]
          currentList.append(data_str)
          shared_dict_payloads["CombineModels"] = currentList
          print(len(shared_dict_payloads["CombineModels"]))	  

    #elif(fname == "CombineModels):
      
    print(fname)
    print("********************")
    print(data)
    print("********************")

# Parameter_Tune 
def invokeDummyFunction(fname, queue, sleep_time):
    time.sleep(sleep_time)
    lambda_client = boto3.client('lambda')
    lambda_payload = '{"dummy": 1}'
    #out = lambda_client.invoke(FunctionName=fname, 
    #                        InvocationType='RequestResponse',
    #                                  Payload=lambda_payload)

    queue.put(fname)

# Producer function that places data on the Queue, acting as our prewarming thread
def producer(queue, lock, functions_sleep_times):
    # Synchronize access to the console
    with lock:
        print('Starting prewarmer => {}'.format(os.getpid()))
         
    # Place our names on the Queue
    prewarmers = []
    for tuple_data in functions_sleep_times:
        for instance in range(tuple_data[1]):
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
        if(fname in executed):
          continue
        num_instances = len(shared_dict_payloads[fname])
        print("num instances of " + fname + " are: " + str(num_instances)) 
        if(num_instances < functions_num_of_inputs[fname]):
            queue.put(fname)
            continue
        executed.add(fname)	  
        with lock:
             print('{} got {}'.format(os.getpid(), fname))
        if(fname in shared_dict_payloads):
             print("**** found "  + fname + " in dict_payloads")
             num_instances = len(shared_dict_payloads[fname])
             print("num instances of " + fname + " are: " + str(num_instances))
             procs = []
             for  i in range(num_instances):
                  if(fname == "CombineModels"):
                     payload = str(shared_dict_payloads[fname]).replace("'","").replace("\\", "").replace("\"\"", "\"")
                  else:
                     payload =  shared_dict_payloads[fname][i]
                  #print("***** executing " + fname +" payload " + payload )
                  proc = Process(target=invokeRealFunction, args=(fname, payload, lock))
                  procs.append(proc)
                  proc.start()
             for p in procs:
                  p.join()
     
             if(fname == "TrainIntentClassifier"):
                break
        # Synchronize access to the console
        with lock:
            print('{} got {}'.format(os.getpid(), fname))

if __name__ == '__main__':
    start_time = time.time() 
    # Tuples of: <Function names>, <Num of workers>, <Delay> 
    functions_sleep_times = [("SplitChatBot",1, 0), ("TrainIntentClassifier",11, 0.5)]
    functions_num_of_inputs = {"SplitChatBot": 1, "TrainIntentClassifier": 11}
    # Create the Queue object
    queue = Queue()


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

    print("E2E Latency: " + str((time.time() - start_time)) + " seconds ")

