# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 20:00:10 2017

@author: Johannes
"""

import os,subprocess

# data_dir is a folder containing one or multiple maps. these should be in subfolders created by unzipping the USGS zip files
# using the script ApplyGCPbatForAllTiffs.py
#e.g. data_dir\<mapname>\data\
#data must contain the *_geo.tif created by ApplyGCPbatForAllTiffs.py
#data must also contain quadr_<quadrangle_name>_<quadrangle_state>.shp created by the vector preprocessing script proj_vector2raster.py
#output will be *_geo_clip.tif in data_dir directly.

data_dir = r'F:\HISTMAPS\BLDG_EXTRACTION\maps_processed'
state = "Colorado"
gdalwarp = r'C:\OSGeo4W\bin\gdalwarp.exe' #not necessary if gdal is in system PATH variable


for root, _, files in os.walk(data_dir):
    for name in files:        
        if 'geo.tif' in name and not '.aux.xml' in name:
            
            tif_file = os.path.join(root,name)
            print(tif_file)  
            workdir,filename = os.path.split(tif_file)
            map_name = name.split('_')[1]  

            quadrangle_name = map_name
            quadrangle_state = state            
            quad_shp=workdir+os.sep+'quadr_'+quadrangle_name+'_'+quadrangle_state+'.shp' #must exist from neg samples creation
            quad_shp_noPath = os.path.split(quad_shp)[1].replace('.shp','')

            #clip raster to quadrangle
            map_clipped =  data_dir+os.sep+name.replace('.tif','_clip.tif')
            
            call = gdalwarp+' -of GTiff -cutline "'+quad_shp+'" -cl "'+quad_shp_noPath+'" -crop_to_cutline "'+tif_file+'" "'+map_clipped+'"'
            print call
            response=subprocess.check_output(call, shell=True) 
            print response