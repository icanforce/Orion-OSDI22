This folder shows an example for WiseFuse's Bundling Manager

## Usage
### For Video:
```

python3 Video_Bundle_Optimize_Standard.py <Video-Application-StateMachine-ARN> <Number-Of-Runs>

Recommended:
set Number-Of-Runs to 10
```

### For ML:
```

python3 ML_Bundle_Optimize_Standard.py <ML-Application-StateMachine-ARN> <Number-Of-Runs>

Recommended:
set Number-Of-Runs to 10
```

### For ChatBot:
```

python3 ChatBot_Bundle_Optimize_Standard.py <ChatBot-Application-StateMachine-ARN> <Number-Of-Runs>

Recommended:
set Number-Of-Runs to 10
```


## Expected Output
```
Bundle size: 1 has a P50 latency of [33079], a P95 of [34198] and a cost of 110527.922388736
Bundle size: 2 has a P50 latency of [25345], a P95 of [26477] and a cost of 133216.351765504
Bundle size: 5 has a P50 latency of [24400], a P95 of [24519] and a cost of 148652.49997107201
Bundle size: 10 has a P50 latency of [34825], a P95 of [36376] and a cost of 119244.697155584
```
