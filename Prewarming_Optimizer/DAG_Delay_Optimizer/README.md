This folder contains the prewarming optimizers for all 3 applications (Video, ML, and Chatbot)

The prewarming optimizer takes as input the latency distribution for each function in the DAG and generates a prewarming delay that optimizes latency and utilization

# Example Usage:
```
cd Video_prewarming_optimizer 
python3.7 three_components_Video_BFS.py 
```
```
cd ML_prewarming_optimizer 
python3.7 two_components_ML_Pipeline_BFS_Util.py
```
```
cd ChatBot_prewarming_optimizer 
python3.7 two_components_ChatBot_BFS.py
```

# Expected Output:
## For Video:
```
=========== Best Prewarming Delays: Split->Extract: 2.5 seconds Extract->Classify: 0 seconds
=========== Corresponding Estimated Utilization:: 7.65244e-05
```

## For ML:
```
=========== Best Prewarming Delays PCA->Train:3.7000000000000006 & Train->Combine:9.799999999999999
=========== Corresponing Utilization: 0.37 & P95 Latency: 15882.489999999998
```

## For ChatBot:
```
Best delay: 8.5 seconds & best util: 7.969981860321285e-05
```
