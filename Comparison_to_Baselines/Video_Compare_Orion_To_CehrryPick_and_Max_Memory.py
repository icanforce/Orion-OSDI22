# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with AWS Step Functions to
create and run state machines.
"""
from StepFunction_util import *
import json
import logging
from botocore.exceptions import ClientError
import boto3
import sys
import time
import random
import string
from datetime import datetime
import os

def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)



def event_log_extract(events):
	function_durations_by_name = {}
	#print(events)
	events_id_dict = {}
	#print("num of events:" + str(len(events)))
	for event in events:
		#event = json.loads(event_str)
		#print(event)
		events_id_dict[event["id"]] = event
		if(event["type"] == "LambdaFunctionSucceeded" or event["type"] == "MapStateSucceeded"):
			#print(event)
			#print("**********************")
			time_stamp_end = event["timestamp"]
			task_type = event["type"]
			prev_event = event
			while(task_type != "TaskStateEntered" and task_type != "MapStateEntered"): #TaskStateEntered stateEnteredEventDetails["name"]
				prev_event = events_id_dict[prev_event["previousEventId"]]
				task_type = prev_event["type"]
			time_stamp_start = prev_event["timestamp"]
			function_name = prev_event["stateEnteredEventDetails"]["name"]
			elapsed_time = int((time_stamp_end - time_stamp_start).total_seconds() * 1000)
			#print(function_name + "\t" + str(elapsed_time))
			if(function_name not in function_durations_by_name):
				function_durations_by_name[function_name] = []
			function_durations_by_name[function_name].append(elapsed_time)
	e2e_start_time = events[0]["timestamp"]
	e2e_end_time = events[-1]["timestamp"]
	function_durations_by_name["E2E"] = [int((e2e_end_time-e2e_start_time).total_seconds() * 1000)]
	return function_durations_by_name

	

def main():
	
	args = sys.argv[1:]
	logger = logging.getLogger(__name__)

	lambda_client = boto3.client('lambda')
	stepFunctions_client = boto3.client('stepfunctions')
	if(len(args) == 0):
		print("Please enter the DAG's arn as the first argument")
		return

	if(len(args) == 1):
		 print("Please enter the number of profiling runs as the second argument")
		 return

	#Example usage:  StepFunctionsStateMachine(stepFunctions_client, "arn:aws:XXXXXXXXXXXX")
	DAG_arn = args[0]
	Num_of_runs = int(args[1])
	step_controler = StepFunctionsStateMachine(stepFunctions_client, DAG_arn)

	memorySizes = [2560]
	print("collecting data for memory sizes of:")
	print(memorySizes)
	
	print("lambda function names/arns in the DAG")


	# Extract all function arns from the DAG
	describe_out = step_controler.describe()
	#print(describe_out['definition'])
	j_def = json.loads(describe_out['definition'])
	describe_out_unrolled = recursive_items(j_def)
	function_arns = []
	for key, value in describe_out_unrolled:
		if(key == "Resource"):
			#print(key, value)
			function_arns.append(value)
	print("Identified the following functions in the DAG")
	print(function_arns)

	letters = string.ascii_lowercase
	profile_hash = ''.join(random.choice(letters) for i in range(10))

	Memsize_By_Approach_Dict = {"Orion": {"Split": 3008, "Extract": 1728, "Shuffle": 1728, "Classify": 10240}, "Best_Memory": {"Split":8000, "Extract":8000, "Shuffle":8000, "Classify":8000}, "CherryPick": {"Split":4844, "Extract":8196, "Shuffle":7105, "Classify":9645}}
	BundleSize_By_Approach_Dict = {"Orion": 5, "Best_Memory": 1,  "CherryPick": 1}

	approach_performance_dict = {}
	approach_cost_dict = {}
	for approach in BundleSize_By_Approach_Dict:
		letters = string.ascii_lowercase
		profile_hash = approach + "_" + ''.join(random.choice(letters) for i in range(10))
		print("Collecting E2E latency for  " + str(approach))
		os.makedirs("profile_"+ profile_hash)
		print("Created folder profile_"+ profile_hash + " with profiled runtimes")
			
		runtimes_by_name = {} # dictionary to save the runtimes of each function by name. Function_name -> List of runtimes
		# change the memory sizes for all functions in the DAG
		memSizes = Memsize_By_Approach_Dict[approach]
		for i in range(len(function_arns)):
			func_name = function_arns[i].split(":")[-1]
			print("setting memory size for " + func_name + " to " + str(memSizes[func_name]))
			response = lambda_client.update_function_configuration(FunctionName=function_arns[i], MemorySize=int(memSizes[func_name]))

		time.sleep(5)

		# load profiling runs' inputs from file
		input_dict_list = []
		f = open("Video_Inputs.json", "r")
		lines = f.readlines()

		for l in lines:
			j = json.loads(l)
			j["DOP"] = str(int(30/BundleSize_By_Approach_Dict[approach]))
			input_dict_list.append(j)


		# execute the DAG for Num_of_runs times
		input_id = 0
		for run_id in range(Num_of_runs):

			letters = string.ascii_lowercase
			run_hash = ''.join(random.choice(letters) for i in range(10))
			run_name = "run_" + run_hash
			run_arn = step_controler.start_run(run_name, input_dict_list[input_id])
			input_id += 1

			# if number of inputs < number of runs, we re-iterate over the inputs
			if(input_id > len(input_dict_list)):
				input_id = 0

			run_succeeded = False
			for i in range(200): # Busy loop until success or until 1000 seconds have elapsed
				arn_describtion = step_controler.describe_execution(run_arn)
				#print(arn_describtion)
				#print("+++++++++++++++++++++++++++++++++++++++++++")
				if(arn_describtion['status'] == 'SUCCEEDED'):
					run_succeeded = True
					break
				elif(arn_describtion['status'] == 'FAILED'):
					break
				time.sleep(5)

			if(run_succeeded == True):
				print("Run " + str(run_id) + "/" + str(Num_of_runs) + " succeeded")
				response = step_controler.get_run_logs(run_arn)
				runtimes = event_log_extract(response["events"])
				for key in runtimes:
					if(key not in runtimes_by_name):
						runtimes_by_name[key] = []
					runtimes_by_name[key].append(runtimes[key])
		print("+++++++++++++++++++++++++++++++++++++++++++")
		print("+++++++++++++++++++++++++++++++++++++++++++")
		print("For memory size of: " + str(memSizes) + " and approach of: " + str(approach))
		print(runtimes_by_name["E2E"])
		# add bundle E2E Latency to dict, ignore the first execution (cold start) 
		approach_performance_dict[approach] = runtimes_by_name["E2E"][1:]
		approach_cost_dict[approach] = 0
		for key in runtimes_by_name:
			if(key != "E2E"):
				sum_all_times = 0
				id = 0
				for l in runtimes_by_name[key]:
					sum_all_times += sum(l) * memSizes[key]
					i += 1
				approach_cost_dict[approach] += sum_all_times * 0.0000166667 
		out_file_name = "profile_"+ profile_hash + "//" + "rs_" + approach + ".txt"
		num_of_runs = len(runtimes_by_name["E2E"])
		if("Classify" in runtimes_by_name):
			f = open(out_file_name, 'w')
			for run_id in range(num_of_runs):
				line = "Video:" + str(run_id) + " Chunk:" + str(run_id) +  " E2E:" + str(max(runtimes_by_name["E2E"][run_id])) +  " Split:" + str(max(runtimes_by_name["Split"][run_id])) +  " Extract:" + str(max(runtimes_by_name["Extract"][run_id])) +  " Classify:" + str(max(runtimes_by_name["Classify"][run_id]))
				f.write(line + "\n")
			f.close()
		else:
			f = open(out_file_name, 'w')
			for run_id in range(num_of_runs):
				line = "E2E:" + str(max(runtimes_by_name["E2E"][run_id]))
				for key in runtimes_by_name:
					line = line + " " + key + ":" + str(max(runtimes_by_name[key][run_id]))
				f.write(line + "\n")
			f.close()
	print(approach_performance_dict)
	print("========================")
	for approach in approach_performance_dict:
		approach_performance_dict[approach].sort()
		P50 = approach_performance_dict[approach][int(len(approach_performance_dict[approach])*50/100)]
		P95 = approach_performance_dict[approach][int(len(approach_performance_dict[approach])*95/100)]
		print("Approach: " + str(approach) + " has a P50 latency of " + str(P50) + " ms , a P95 of " + str(P95) + " ms, and a cost of 1K runs " + str(int(approach_cost_dict[approach])) + "$")

main()
