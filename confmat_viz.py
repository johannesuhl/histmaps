import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

###dummy data
y_true = [2, 0, 2, 2, 0, 1]
y_pred = [0, 0, 2, 2, 0, 2]
confmat = confusion_matrix(y_true, y_pred)
###

sns.set(font_scale=1.0)
title_plot = 'Confusion matrix'      
labels = ['class 1','class 2','class 3']
fig, ax = plt.subplots()
#plt.figure()
ax = plt.axes() #annot_kws={"fmt": 'g',}
heatmap = sns.heatmap(confmat, annot=True, ax = ax, annot_kws={"size": 15}, cmap='spectral_r', fmt='.20g', xticklabels = labels, yticklabels = labels) #,  linewidths=.5   
#use annot_kws={"size": 18} if counts are max 6 digits.
#for higher values, use annot_kws={"size": 15}      
heatmap.tick_params(labelsize=15)    
ax.set_title(title_plot, fontsize=20)
#########################################
#ax.invert_xaxis() #invert axis
#ax.invert_yaxis() #invert axis
#########################################   
plt.xlabel('Test class', fontsize=15)
plt.ylabel('Reference class', fontsize=15)
plt.show()
filename='cm.png'
fig = heatmap.get_figure()
fig.savefig(filename, dpi=600) 
plt.clf()  
