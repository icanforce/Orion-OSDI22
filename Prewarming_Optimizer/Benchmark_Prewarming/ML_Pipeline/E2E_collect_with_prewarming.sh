#!/bin/bash

for mem in 10240
do

f=E2E_ML_Prewarm_100.txt
rm $f

for ((i = 1; i <= $1; i++)); do

	aws lambda update-function-configuration --function-name ParamTune --memory-size 5000
	aws lambda update-function-configuration --function-name CombineModels --memory-size 5000
	sleep 30
	aws lambda update-function-configuration --function-name ParamTune --memory-size $mem
	aws lambda update-function-configuration --function-name CombineModels --memory-size 1800
    sleep 30

	python3 prewarming_ML_Pipeline.py >> $f 
	echo "========================" >> $f
	echo "Done iteration : $i"
done	

echo "Latency with prewarming:"

more $f | grep "E2E"

done

