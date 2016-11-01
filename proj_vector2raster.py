import subprocess
import os

#------------------------------------------------------------------------------

#parameters:
vector_orig = r"F:\HISTMAPS\DOWNLOADS_USGS\VECTOR\CA_transportation\TRAN_6_California_GU_STATEORTERRITORY_SHP\Shape\Trans_RailFeature.shp"
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Acolita_100348_1998_24000_bag-20161013T204103Z\CA_Acolita_100348_1998_24000_bag\data\CA_Acolita_100348_1998_24000_geo.tif"

#full path to gdal executables>
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
ogr2ogr = r'C:\OSGeo4W\bin\ogr2ogr.exe'

#the USGS quadrangle shapefile:
quadrangles = r'F:\HISTMAPS\DOWNLOADS_USGS\QUADRANGLES\USGS_24k_Topo_Map_Boundaries_NAD83inNAD27.shp'

#the name and state of current map quadrangle:
quadrangle_name = "Acolita"
quadrangle_state = "California"

#------------------------------------------------------------------------------

call = gdalsrsinfo+' -o proj4 "'+vector_orig+'"'
crs_vector=subprocess.check_output(call, shell=True).strip().replace("'","")

call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")

#use USGS quadrangle geometry to clip vector exactly to map area
#first select quadrangle
workdir,quads = os.path.split(quadrangles)
quad_select=workdir+os.sep+'quadr_'+quadrangle_name+'_'+quadrangle_state+'.shp'
call = """%s -where "QUAD_NAME='%s' AND ST_NAME1='%s'" %s %s""" % (ogr2ogr, quadrangle_name, quadrangle_state, quad_select, quadrangles)
print call
response=subprocess.check_output(call, shell=True)
print response

#clip
vector_clip=vector_orig.replace('.shp','_clip.shp')
call = '%s -dim 2 -clipsrc %s %s %s ' % (ogr2ogr, quad_select, vector_clip, vector_orig)
print call
response=subprocess.check_output(call, shell=True)
print response

# Reproject vector geometry to same projection as raster
vector_proj = vector_clip.replace('.shp','_proj.shp')
call = ogr2ogr+' -t_srs "'+crs_raster+'" -s_srs "'+crs_vector+'" "'+vector_proj+'" "'+vector_clip+'"'
print call
response=subprocess.check_output(call, shell=True)
print response
                
                
