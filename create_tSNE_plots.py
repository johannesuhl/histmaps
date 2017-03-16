
#this will call matlab m file to create the plots.

import os, subprocess

sample_folders=[]
sample_folders.append(PATH_TO_SAMPLES)

matlab_mfile_path = PATH_TO_M_FILE #folder where matlab .m file is located
matlab_mfile_name = 'batch_tsne_embedding' #matlab .m file name without extension
thumbnail_size = 40

for sample_folder in sample_folders:
    curr_folder = sample_folder.split(os.sep)[-1]
    coordfile = "TSNE_coords_"+curr_folder+".txt"    
    filenames = "filenames_"+curr_folder+".txt"
    
    os.chdir(matlab_mfile_path)
    call = """matlab -r %s('%s','%s','%s',%s)""" %(matlab_mfile_name,curr_folder,coordfile,filenames,thumbnail_size)
    print call
    response=subprocess.check_output(call, shell=True)
    print response
