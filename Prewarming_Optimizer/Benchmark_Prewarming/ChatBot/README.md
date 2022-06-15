This folder contains the benchmarking scripts to compare prewarming to No prewarming

## Usage:

```
For prewarming:
./E2E_collect_with_prewarming.sh <Number_of_runs>

For no prewarming:
./E2E_collect_No_prewarming.sh <Number_of_runs>

recommended:
Number_of_runs=10
```

## Expected Outputs:
Latency with prewarming:
E2E Latency: 11.309002876281738 seconds
E2E Latency: 13.977751016616821 seconds

Latency with No prewarming:
E2E Latency: 13.653421640396118 seconds
E2E Latency: 12.719837427139282 seconds
