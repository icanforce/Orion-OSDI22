This folder contains the code for executing the DAGs with optimized prewarming delays. Here we don't use Stepfunctions as we cannot force stepFunctions to start prewarming a container with a specific delay. Hence, we use our own orchestration.

The orchestration is based on Producer-Consumer model. The producer warms up a container (using a dummy call) after the delay duration has elapsed. When the container is warm, the consumer is notified to send the actual request. 

In order to execute for any application: run ```./E2E_collect_with_prewarming.sh 10``` to collect the latency for executing the DAG with prewarming delays. Also run ```./E2E_collect_No_prewarming.sh 10``` to execute the same DAG without prewarming.
