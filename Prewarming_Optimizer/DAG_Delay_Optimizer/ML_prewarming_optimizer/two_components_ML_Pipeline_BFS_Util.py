import random
import math

def getE2EandUtilDist(d_s:int, d3_s: int):
	d_ms = d_s * 1000
	d3 = d3_s * 1000
	n = 10000
	file1 = open('dist_PCA.txt', 'r')
	file2 = open('dist_Param.txt', 'r')
	file3 = open('dist_Combine.txt', 'r')
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
	Init_f2 = 2680
	Init_f3 = 130

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
			util = 1/(1 + 20 * (( f1-(d + Init_f2) )  /  (f1 + Init_f2 + f2)) + 2 * (f1_f2 - (d3 + Init_f3)) / (f1 + f2 + f3 + Init_f2 + Init_f3))
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

	#return Util_per_Sec[ int(n/100*95)]
	return Util_list[ int(n/100*95)], E2E_list[int(n/100*95)]

d2_curr = 3
d3_curr = 9.6
v = 0
l = 0
latency_target = 20000
while(True):
		v2, l2 = getE2EandUtilDist(d2_curr + 0.1, d3_curr)
		v2 = round(v2,2)
		v3, l3 = getE2EandUtilDist(d2_curr, d3_curr + 0.1)
		v3 = round(v3,2)
		if(v2 < v and v3 < v):
			break
		if(l2 > 20000 and l3 > 20000):
			break
		if(v2 > v3):
			v = v2
			l = l2
			d2_curr = d2_curr + 0.1
			print(" Increamenting prewarming delay of PCA->Train ")
		else:
			v = v3
			l = l3
			d3_curr = d3_curr + 0.1
			print(" Increamenting prewarming delay of Train->Combine ")

print("=========== Best Prewarming Delays PCA->Train:" + str(d2_curr) + " & Train->Combine:" + str(d3_curr))
print("=========== Corresponing Utilization: " + str(v) + " & P95 Latency: " + str(l))

