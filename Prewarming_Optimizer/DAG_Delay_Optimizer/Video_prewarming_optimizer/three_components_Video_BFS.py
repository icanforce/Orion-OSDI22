import random
import math

def getE2EandUtilDist(d_s:int, d3_s: int):
	d_ms = d_s * 1000
	d3 = d3_s * 1000
	n = 10000
	file1 = open('dist_Split.txt', 'r')
	file2 = open('dist_Extract.txt', 'r')
	file3 = open('dist_Detect.txt', 'r')
	Lines = file1.readlines()
	Lines2 = file2.readlines()
	Lines3 = file3.readlines()
	Comp1 = []
	for line in Lines:
		Comp1.append(float(line.strip()))
	Comp2 = []
	for line in Lines2:
	    Comp2.append(float(line.strip()))
	Comp3 = []	
	for line in Lines3:
		Comp3.append(float(line.strip()))

	#print(Comp1)
	F1_times = [random.choice(Comp1) for i in range(n)]
	#print(F1_times)
	F2_times = [random.choice(Comp2) for i in range(n)]
	F3_times = [random.choice(Comp3) for i in range(n)]

	E2E_list = []
	Util_list = []
	Util_per_Sec = []
	Init_f2 = 350
	Init_f3 = 4615

	for i,f1 in enumerate(F1_times):
		d = d_ms
		if(d_ms > f1):
			d = f1
		f2 = F2_times[i]
		f3 = F3_times[i]
		f1_f2 = f2 + max(f1,d + Init_f2)
		#print(f1_f2)
		#print(str(d3 + Init_f3))
		E2E = f3 + max(f1_f2, d3 + Init_f3)

		E2E_list.append(E2E)
		util = 0
		if( f1 <= (d + Init_f2)):
			util = 1		    
			
		else:	
			util = 1/(1 +  (( f1-(d + Init_f2) )  /  (f1 + Init_f2 + f2)) + (f1_f2 - (d3 + Init_f3)) / (f1 + f2 + f3 + Init_f2 + Init_f3))
		Util_list.append(util)
		Util_per_Sec.append(util/E2E)
	E2E_list.sort()
	Util_per_Sec.sort()
	Util_list.sort(reverse=True)# For Util, the higher the better
	#print(F1_times)
	#print(E2E_list)
	#print(Util_list)
	#print("P50 E2E:" + str(sum(E2E_list)/len(E2E_list)))
	#print("P50 Util:" + str( sum(Util_list)/ len(Util_list)))
	#print("P95 E2E:" + str(E2E_list[int(n/100*95)]))
	#print("P95 Util:" + str(Util_list[ int(n/100*95)] ))
	#print("P95 Util-per-sec:" + str(Util_per_Sec[ int(n/100*95)] ))

	return Util_per_Sec[ int(n/100*95)]
	#return Util_list[ int(n/100*95)]

d2_curr = 0
d3_curr = 0
v = 0
while(True):
		v2 = round(getE2EandUtilDist(d2_curr + 0.1, d3_curr), 10)
		v3 = round(getE2EandUtilDist(d2_curr, d3_curr + 0.1), 10)
		if(v2 <= v and v3 <= v):
			break
		if(v2 > v3):
			v = v2
			d2_curr = d2_curr + 0.1
			print("Increamenting prewarming delay of Split->Extract")
		else:
			v = v3
			d3_curr = d3_curr + 0.1
			print("Increamenting prewarming delay of Extract->Classify")

print("=========== Best Prewarming Delays: Split->Extract: " + str(round(d2_curr,2)) + " seconds Extract->Classify: " + str(round(d3_curr,2)) + " seconds")
print("=========== Corresponding Estimated Utilization:: " + str(v))

