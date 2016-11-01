import os
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt



folder = r'F:\HISTMAPS\DOWNLOADS_USGS\TIFF_CO'

years=list()
for root, dirs, files in os.walk(folder, topdown=False):
    for name in files:
        year = name.split('_')[3]
        years.append(int(year))

x = np.array( years )        

# the histogram of the data
n, bins, patches = plt.hist(x, 500, normed=0, facecolor='green')


alphab = list(set(years))
fig = plt.figure()  
n, bins, patches = plt.hist(x, 500, normed=0, facecolor='green')          
pos = np.arange(len(alphab))
ax = plt.axes()
plt.xlabel('Edition Year')
plt.ylabel('Frequency')
plt.title('CO Year Frequencies')
plt.grid(True)
plt.show()

filename=r'F:\HISTMAPS\hist_years_CO.png'
fig.savefig(filename) 

print 'Min Year', min(years)
print 'Max Year', max(years)   

        
        


    
    