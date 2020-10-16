f = open('./parcial1/truth.txt','r')
import os
os.system("clear")
data = []
while(True):
	line = f.readline()
	if not line:
		break
	data.append(line)

f.close()

all_truth = []


n = len(data)
for i in range(n):
	data[i] = data[i].replace('\n','')


for i in range(n):
	new_data = data[i].split(':::')
	all_truth.append(new_data)




