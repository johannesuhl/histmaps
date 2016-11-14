import os,subprocess
import zipfile
import shutil

zipfolder = r'F:\HISTMAPS\from_USC\NEW'
counter=0
for root, dirs, files in os.walk(zipfolder, topdown=False):
    for name in files:
        unzip_path = ""          
        if '.zip' in name:
            counter+=1
totalfiles = counter

              
counter=0
for root, dirs, files in os.walk(zipfolder, topdown=False):
    for name in files:
        unzip_path = ""
        try:            
            if '.zip' in name:
                counter+=1
                print 'processing file', str(counter), 'out of', str(totalfiles)
                #extract ZIP file to folder:
                zip_ref = zipfile.ZipFile(zipfolder+os.sep+name, 'r')
                unzip_path = zipfolder
                zip_ref.extractall(unzip_path)
                zip_ref.close()
      
                datapath = unzip_path+os.sep+name.replace('.zip','')
                current_tiff_path = datapath+os.sep+'data'
                for root2, dirs2, files2 in os.walk(current_tiff_path, topdown=False):
                    for name2 in files2:
                        if 'gcp.bat' in name2:
                            #remove path dummies in bat file
                            print name2
                            fullpath = os.path.join(root2, name2)
                            f = open(fullpath,'r')
                            filedata = f.read()
                            f.close()                            
                            newdata = filedata.replace("OUTPUT\\","").replace("INPUT\\","")                             
                            f = open(fullpath,'w')
                            f.write(newdata)
                            f.close()  
                            #run bat file to apply GCPs:
                            os.chdir(root2)
                            s=subprocess.check_output(fullpath, shell=True)
                            print s
                            del zip_ref
                            del f
                            break
                #delete current ZIP file:
                os.remove(zipfolder+os.sep+name)
                
        except:
            print 'ERROR', name
    
    
