# Comparison with Baselines:

We compare to two baselines, Cherrypick and Best_Memory
To show the E2E latency and cost for each, run the following command:
```
Compare_Orion_To_CehrryPick_and_Max_Memory.py <Video-Analytics-ARN> <Number-of-Runs>

Recommended:
Number-of-Runs = 100
```

Expected ourput:
```
Approach: Orion has a P50 latency of [9864], a P95 of [16761] and a cost of 83003
Approach: CherryPick has a P50 latency of [12993], a P95 of [19392] and a cost of 322726
Approach: Best_Memory has a P50 latency of [13112], a P95 of [26011] and a cost of 263159
```

# Run Cherrypick to get the best memory sizes: 
CherryPick: Uses Bayesian Optimization (BO) to select the best vector of VM sizes for a target latency

Usage:
```
python3 CherryPick_Optimized_VM_Sizes.py <DAG-ShateMachine-ARN> <Latency-Target-ms>

recommended:
Latency-Target = 25000 #(25 seconds)
```

## Expected Output:
# Video
```
Identified the following functions in the DAG
['arn:aws:XXXXXXXXXXXXXXXXX:Split', 'arn:aws:XXXXXXXXXXXXXXXXXXX:Extract', 'arn:aws:XXXXXXXXXXXXXXXXXXXX:Shuffle', 'arn:aws:XXXXXXXXXXXXXXXXXXXXx:Classify']

Best VM sizes configs:
[4844 8196 7105 9645]

```

# ML-Pipeline
```
Identified the following functions in the DAG
['arn:aws:lambda:XXXXXXXXXXXXXXXXXX:PCA', 'arn:aws:lambda:XXXXXXXXXXXXXXXXXX:ParamTune', 'arn:aws:lambda:XXXXXXXXXXXXXXXXXX:CombineModels']

Best VM sizes configs:
[ 953.9677783  8861.98997701 5424.28417541]
```

# ChatBot
```
Identified the following functions in the DAG
['arn:aws:lambda:XXXXXXXXXXXXXXXXXX:SplitChatBot', 'arn:aws:lambda:XXXXXXXXXXXXXXXXXX:TrainIntentClassifier']

Best VM sizes configs:
[5456.98864924 1085.74601692]
```
