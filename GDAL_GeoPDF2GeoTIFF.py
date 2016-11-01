# -*- coding: cp1252 -*-

#SCRIPT MUST BE RUN FROM OSGEO4W SHELL!!! BECAUSE OF GDAL LIBRARY!!!!

import os, sys
import subprocess
from osgeo import gdal

indir = r'F:\HISTMAPS\DOWNLOADS_USGS\MAPS_RECENT_GEOPDF'
outdir = r'F:\HISTMAPS\DOWNLOADS_USGS\MAPS_RECENT_TIFF'
outdpi = 150





for root, dirs, files in os.walk(indir, topdown=False):
    for name in files:
        infile = os.path.join(root, name)
        outfile = os.path.join(outdir, name.replace('.pdf','_'+str(outdpi)+'_dpi.tif').replace('-','').replace(',',''))

        data_gdal = gdal.Open( infile, gdal.GA_ReadOnly )
        layers = data_gdal.GetMetadata_List("LAYERS")
        try:
            layers = [ layer.split('=')[-1] for layer in layers ]
            use_layers=''
            for layer in layers:
                if "." in layer and 'Map_Frame' in layer and not 'Projection_and_Grids' in layer:
                    use_layers = layer+","+use_layers
            use_layers = use_layers[:-1] 
            
            
            cmd = r'C:\OSGeo4W\bin\gdal_translate.exe "'+infile+'" "'+outfile+'" --config GDAL_PDF_LAYERS "'+use_layers+'" --config GDAL_PDF_BANDS 3 --config GDAL_PDF_DPI '+str(outdpi)
            print cmd
            if not os.path.exists(outfile):
                os.system(cmd)
        except:
            #if there is no layer structure in geopdf, 1st line in try block throws an error. then we convert whole pdf content to tiff.
            cmd = r'C:\OSGeo4W\bin\gdal_translate.exe "'+infile+'" "'+outfile+'" --config GDAL_PDF_BANDS 3 --config GDAL_PDF_DPI '+str(outdpi)
            print cmd
            if not os.path.exists(outfile):
                os.system(cmd)           
