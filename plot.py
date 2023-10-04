import matplotlib.pyplot as plt
import csv

filename = 'RSA/2023-10-03 194138_FMR.txt'
x = []
y = []
z = []

with open(filename, encoding='utf8', newline='') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        x.append(float(row[0]))
        y.append(float(row[1]))
        z.append(float(row[2]))
        
        
plt.plot(x,y)


plt.show()