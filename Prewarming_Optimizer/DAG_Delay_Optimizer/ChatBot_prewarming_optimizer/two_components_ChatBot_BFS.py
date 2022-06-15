import random
import math

def getE2EandUtilDist(d_s:int):
	d_ms = d_s * 1000
	n = 10000
	file1 = open('dist_SplitChat.tx', 'r')
	file2 = open('dist_TrainIntent.tx', 'r')
	Lines = file1.readlines()
	Lines2 = file2.readlines()
	Comp1 = []
	for line in Lines:
		Comp1.append(float(line.strip()))
	Comp2 = []
	for line in Lines2:
	    Comp2.append(float(line.strip()))
	#print(Comp1)
	F1_times = [random.choice(Comp1) for i in range(n)]
	#print(F1_times)
	F2_times = [random.choice(Comp2) for i in range(n)]
	
	E2E_list = []
	Util_list = []
	Util_per_Sec = []
	Init_f2 = 1300

	for i,f1 in enumerate(F1_times):
		d = d_ms
		if(d_ms > f1):
			d = f1
		f2 = F2_times[i]
		E2E = f2 + max(f1,d + Init_f2)
		E2E_list.append(E2E)
		util = 0
		if( f1 <= (d + Init_f2)):
			util = 1		    
			
		else:	
			util = 1/(round(1 + ( f1-(d + Init_f2) )  /  (f1 + Init_f2 + f2),2))
		Util_list.append(util)
		Util_per_Sec.append(util/E2E)
	E2E_list.sort()
	Util_per_Sec.sort()
	Util_list.sort(reverse=True)# For Util, the higher the better
	#print(F1_times)
	#print(E2E_list)
	#print(Util_list)
	print("P50 E2E:" + str(sum(E2E_list)/len(E2E_list)))
	print("P50 Util:" + str( sum(Util_list)/ len(Util_list)))
	print("P95 E2E:" + str(E2E_list[int(n/100*95)]))
	print("P95 Util:" + str(Util_list[ int(n/100*95)] ))
	print("P95 Util-per-sec:" + str(Util_per_Sec[ int(n/100*95)] ))
	return Util_per_Sec[ int(n/100*95)]

best_util_latency = 0
best_delay = -1
for i in range(0,150,1):
	v= i/10
	print("=========== delay =  " + str(v))
	util = getE2EandUtilDist(v)
	if(util > best_util_latency):
		best_util_latency = util
		best_delay = v
print("Best delay: " + str(best_delay) + " seconds & best util: " + str(best_util_latency))	
	

