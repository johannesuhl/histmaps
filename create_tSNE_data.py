#Run it in Python 64bit

import numpy as np
from sklearn.manifold import TSNE
import pylab as plot
import os, cv2

sample_folders=[]
sample_folders.append(PATH_TO_SAMPLES)


#samplesize = 10000

for sample_folder in sample_folders:
    curr_folder = sample_folder.split(os.sep)[-1]
    names=list()
    for root, _, files in os.walk(sample_folder):
        for name in files:        
            if '.tif' in name:
                samplefile = os.path.join(root,name)
                names.append(samplefile)
                
    #names_sample = [ names[i] for i in sorted(random.sample(xrange(len(names)), samplesize)) ]
    alldata=list()
    
    #for samplefile in names_sample:   
    for samplefile in names:               
        img = cv2.imread(samplefile)
        vec = img.flatten()
        alldata.append(vec)
                
    alldata = np.array(alldata)
    outtxt = curr_folder+".txt"
    np.savetxt(outtxt, alldata) 
    
    namesfile = open("filenames_"+curr_folder+".txt", 'w')        
    for item in names:
    #for item in names_sample:
      print>>namesfile, item  
    
    namesfile.close()
    
    ##############################################################3
    #create t-SNE coordinates    
    X = np.loadtxt(outtxt)
    model = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    output = model.fit_transform(X) 
    np.savetxt("TSNE_coords_"+curr_folder+".txt", output)     
    
    fig = plot.figure()
    plot.gca().invert_yaxis()
    plot.scatter(output[:,1], output[:,0], 0.2) #, labels)
    plot.show()
    filename="tSNE_scatterplot_"+curr_folder+'.png'
    fig.savefig(filename)      
  

    
    
