This folder contains the conde for the DAG prewarming optimizer.

# Prewarming_Optimizer:
1. **DAG_Delay_Optimizer**: python code that applies BfS to find the best delay for each stage in the DAG. Check **DAG_Delay_Optimizer/README.md** for usage instructions and examples.
2. **Benchark_Prewarming**: python code that executes the DAG with the optimized delays on AWS Lambda. Check **Benchark_Prewarming/README.md** for usage instructions and examples.  

Use **DAG_Delay_Optimizer** to identify the optimized delays for each function in the DAG, and then use **Benchark_Prewarming** to execute the DAG on AWS Lambda with the optimized delays 
