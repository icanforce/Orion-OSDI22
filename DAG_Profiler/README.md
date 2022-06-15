# DAG Profiler:
 In this folder, we give the code for the DAG profiler. The DAG profiler takes as input the DAG's arn (Step Functions) and performs the following steps:

 1. Extract functions' names and arns from the DAG's description
 2. Executes the same DAG N time (N is user-given, recommended value is 600 divided to 300 for training and 300 for testing)
 3. Extracts the latency CDFs for each stage in the DAG given its assigned VM size
 4. The extracted CDFs are then used by the **DAG_Modeler** to build the E2E performance model



Usage

# For Video Analytics:
```
python3 Latency_collect_Standard.py <Video_StateMachine_ARN> <Number of profiling runs> Video_Inputs.json
```

# For ML Pipeline:
```
python3 Latency_collect_Standard.py <ML_StateMahcine_ARN> <Number of profiling runs> ML_Inputs.json 
```

# For ChatBot:
```
python3 Latency_collect_Standard.py <ChatBot_StateMachine_ARN> <Number of profiling runs> ChatBot_Inputs.json 
```
 
