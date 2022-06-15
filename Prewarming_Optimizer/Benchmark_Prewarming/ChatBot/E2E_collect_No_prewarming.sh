#!/bin/bash

for mem in 10240
do

f=E2E_ChatBot_No_Prewarm_100.txt
rm $f

for ((i = 1; i <= $1; i++)); do

	aws lambda update-function-configuration --function-name TrainIntentClassifier --memory-size 5000
	sleep 30
	aws lambda update-function-configuration --function-name TrainIntentClassifier --memory-size $mem
    sleep 30

	python3 No_prewarming_ChatBot.py >> $f 
	echo "========================" >> $f
	echo "Done iteration : $i"
done	

echo "Latency with prewarming:"

more $f | grep "E2E"

done

