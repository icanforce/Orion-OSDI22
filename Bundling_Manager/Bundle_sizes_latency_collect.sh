#!/bin/bash

for bundleSize in 1 2 6; do

rm Inputs.json

for i in {0..600}; do

	DOP=$((30 / $bundleSize))
	echo "{  \"src_name\": \"0\",   \"DOP\": \"$DOP\",   \"detect_prob\": 2 }" >> Inputs.json

done	

python3 Latency_collect_Standard.py arn:aws:states:us-west-2:261895940478:stateMachine:WiseFuse_Video_SM 2

done

