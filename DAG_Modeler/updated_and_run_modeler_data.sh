#!/bin/bash

# This script updates the data in the modeler using the generated profiles in DAG_Profiler
# First, execute DAG_Profiler to generate profiles as profile_*_ML, profile_*_ChatBot, profile_*_Video 

echo "Updating modeler's data for ML application"

cp ../DAG_Profiler/profile_*_ML/* DAG_Modeler/bin/Debug/ML_Pipeline_Data/

echo "Updating modeler's data for ChatBot application"
cp ../DAG_Profiler/profile_*_ChatBot/* DAG_Modeler/bin/Debug/ChatBot_Data/

echo "Updating modeler's data for Video application"
cp ../DAG_Profiler/profile_*_Video/* DAG_Modeler/bin/Debug/Video_Analytics_Data/ 

echo "Updated moedler's data"
echo "Rnning Modeler"
echo "========================"

cd DAG_Modeler/bin/Debug/
./DAG_Modeler.exe | grep 'VM\|BFS'
cd ../../../
