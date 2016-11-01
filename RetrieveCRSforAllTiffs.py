import os,subprocess
import zipfile
import shutil

zipfolder = r'F:\HISTMAPS\from_USC'
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
outfile = r'F:\HISTMAPS\PROJ_TEST\crs_summary_ca4.txt'


fetchAllCRS = True
createSummary = False

if fetchAllCRS:
    
    counter=0
    text_file = open(outfile, "w")
    for root, dirs, files in os.walk(zipfolder, topdown=False):
        for name in files:
            unzip_path = ""
            try:
                
                if '.zip' in name:
                    counter+=1
                    #if counter < 6510: #TEMP
                        #continue       #TEMP
                        
                    zip_ref = zipfile.ZipFile(zipfolder+os.sep+name, 'r')
                    unzip_path = zipfolder
                    #zip_ref.extractall(unzip_path)
                    zip_ref.close()
          
                    datapath = unzip_path+os.sep+name.replace('.zip','')
                    current_tiff_path = datapath+os.sep+'data'
                    for root2, dirs2, files2 in os.walk(current_tiff_path, topdown=False):
                        for name2 in files2:
                            splitted=name2.split('.')
                            if splitted[1]=='tif' and len(splitted)==2:
        
                                fullpath = os.path.join(root2, name2)
                                call = gdalsrsinfo+' -o wkt "'+fullpath+'"'
                                s=subprocess.check_output(call, shell=True)
                                print s
                                text_file.write(fullpath+';'+s)
                                break
            
                    #delete current_tiff_path:
                    #shutil.rmtree(datapath)
            except:
                print 'ERROR', name
        
        
    text_file.close()

if createSummary:
    allcrs=list()
    text_file = open(outfile, "r")
    for line in text_file:
        curr_crs = line.split(";")[1].replace("\r\n","")
        allcrs.append(curr_crs)
    
    allcrs=list(set(allcrs))
    for crs in allcrs:
        print crs
    
    