import subprocess
import os
import sys

#------------------------------------------------------------------------------

#parameters:
vectors_orig = sys.argv[1] #must be a list of shps separated by commas
map_tiff_geo = sys.argv[2]
quadrangle_name = sys.argv[3]
quadrangle_state = sys.argv[4]

#full path to gdal executables>
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
ogr2ogr = r'C:\OSGeo4W\bin\ogr2ogr.exe'
#the USGS quadrangle shapefile:
quadrangles = r'F:\HISTMAPS\DOWNLOADS_USGS\QUADRANGLES\USGS_24k_Topo_Map_Boundaries_NAD83inNAD27.shp'


#------------------------------------------------------------------------------
vectors_orig_list = vectors_orig.split(",")
vectors_proj_list = list()

for vector_orig in vectors_orig_list:
    print vector_orig
    
    call = gdalsrsinfo+' -o proj4 "'+vector_orig+'"'
    crs_vector=subprocess.check_output(call, shell=True).strip().replace("'","")

    call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
    crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")

    #use USGS quadrangle geometry to clip vector exactly to map area
    #first select quadrangle
    workdir,filename = os.path.split(map_tiff_geo) #all data gets stored where the map is located
    quad_select=workdir+os.sep+'quadr_'+quadrangle_name+'_'+quadrangle_state+'.shp'
    call = """%s -where "QUAD_NAME='%s' AND ST_NAME1='%s'" %s %s""" % (ogr2ogr, quadrangle_name, quadrangle_state, quad_select, quadrangles)
    print call
    response=subprocess.check_output(call, shell=True)
    print response

    #clip
    vector_clip=workdir+os.sep+os.path.split(vector_orig)[1].replace('.shp','_clip.shp')
    call = '%s -dim 2 -clipsrc %s %s %s ' % (ogr2ogr, quad_select, vector_clip, vector_orig)
    print call
    response=subprocess.check_output(call, shell=True)
    print response

    # Reproject vector geometry to same projection as raster
    vector_proj = workdir+os.sep+os.path.split(vector_orig)[1].replace('.shp','_proj.shp')
    call = ogr2ogr+' -t_srs "'+crs_raster+'" -s_srs "'+crs_vector+'" "'+vector_proj+'" "'+vector_clip+'"'
    print call
    response=subprocess.check_output(call, shell=True)
    print response
    vectors_proj_list.append(vector_proj)


#merge all clipped and projected shps into one:
print "merging...."
merged = workdir+os.sep+os.path.split(vectors_orig_list[0])[1].replace('.shp','_proj_merged.shp')
for shp in vectors_proj_list:
    call = """%s -append -update %s %s""" % (ogr2ogr, merged, shp)
    print call
    response=subprocess.check_output(call, shell=True)
    print response    



    
                
                 
