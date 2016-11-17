import subprocess
import os, sys
from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from gdalconst import GA_ReadOnly
#------------------------------------------------------------------------------

#parameters:
vector_orig = r"F:\HISTMAPS\DOWNLOADS_USGS\VECTOR\CA_transportation\TRAN_6_California_GU_STATEORTERRITORY_SHP\Shape\Trans_RailFeature.shp"
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Artesia_288070_1925_24000_bag\data\CA_Artesia_288070_1925_24000_geo.tif"

#full path to gdal executables>
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
ogr2ogr = r'C:\OSGeo4W\bin\ogr2ogr.exe'
gdaltindex = r'C:\OSGeo4W\bin\gdaltindex.exe'

#the USGS quadrangle shapefile:
quadrangles = r'F:\HISTMAPS\DOWNLOADS_USGS\QUADRANGLES\USGS_24k_Topo_Map_Boundaries_NAD83inNAD27.shp'

quadrangleIsUserSpecified = False
if quadrangleIsUserSpecified:
    #the name and state of current map quadrangle:
    quadrangle_name = "Acolita"
    quadrangle_state = "California"

findQuadrangleByOverlay = False
useMapExtentInsteadOfQuadrangles = True

#------------------------------------------------------------------------------

call = gdalsrsinfo+' -o proj4 "'+vector_orig+'"'
crs_vector=subprocess.check_output(call, shell=True).strip().replace("'","")

call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")

call = gdalsrsinfo+' -o proj4 "'+quadrangles+'"'
crs_quads=subprocess.check_output(call, shell=True).strip().replace("'","")


def transformPoint(x,y,s_proj4,t_proj4):
    source = osr.SpatialReference()
    source.ImportFromProj4(s_proj4)  
    target = osr.SpatialReference()
    target.ImportFromProj4(t_proj4)   
    transform = osr.CoordinateTransformation(source, target)    
    point = ogr.CreateGeometryFromWkt("POINT ("+str(x)+" "+str(y)+")")
    point.Transform(transform)
    return (point.GetX(),  point.GetY())


if quadrangleIsUserSpecified:
    #use specified USGS quadrangle geometry to clip vector exactly to map area
    #first select quadrangle
    workdir,quads = os.path.split(quadrangles)
    quad_select=workdir+os.sep+'quadr_'+quadrangle_name+'_'+quadrangle_state+'.shp'
    call = """%s -where "QUAD_NAME='%s' AND ST_NAME1='%s'" %s %s""" % (ogr2ogr, quadrangle_name, quadrangle_state, quad_select, quadrangles)
    print call
    response=subprocess.check_output(call, shell=True)
    print response

if findQuadrangleByOverlay:
    
    #get map centroid
    src = gdal.Open(map_tiff_geo, GA_ReadOnly)
    ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
    centroid_x = ulx + (0.5*src.RasterXSize * xres)
    centroid_y = uly + (0.5*src.RasterYSize * yres)
    
    #reproject the point into quadrangle SRS:
    (xtrans,ytrans) = transformPoint(centroid_x,centroid_y,crs_raster,crs_quads)

    #find quadrangle that overlaps centroid and save it in quad_select shp:
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(quadrangles, 0)
    layer = dataSource.GetLayer()

    wkt = "POINT("+str(xtrans)+" "+str(ytrans)+")"
    layer.SetSpatialFilter(ogr.CreateGeometryFromWkt(wkt))

    #create out shp
    workdir,quads = os.path.split(quadrangles)
    quad_select=workdir+os.sep+'quadr_select.shp'
    if os.path.exists(quad_select):
        driver.DeleteDataSource(quad_select)
    outDataSet = driver.CreateDataSource(quad_select)
    outLayer = outDataSet.CreateLayer("layer", geom_type=ogr.wkbPolygon)
    # add fields
    inLayerDefn = layer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()    

    for feature in layer:
        print feature.GetField("QUAD_NAME")
        # create a new feature in quad_select
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(feature.GetGeometryRef())
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # destroy the features and get the next input feature
        outFeature.Destroy()

    # close the shapefiles
    dataSource.Destroy()
    outDataSet.Destroy()
    feature.Destroy()
    #create prj file:
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromProj4(crs_quads)
    spatialRef.MorphToESRI()
    file = open(quad_select.replace('.shp','.prj'), 'w')
    file.write(spatialRef.ExportToWkt())
    file.close()    


if useMapExtentInsteadOfQuadrangles:
    #for some maps the quadrangles do not match with the raster. here we use the raster extent to clip the vector data.

    workdir,quads = os.path.split(quadrangles)
    quad_select=workdir+os.sep+'quadr_select.shp'
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(quad_select):
        driver.DeleteDataSource(quad_select)
    outDataSet = driver.CreateDataSource(quad_select)
    outLayer = outDataSet.CreateLayer("layer", geom_type=ogr.wkbPolygon)
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn() 
    # Add a new field
    new_field = ogr.FieldDefn('location', ogr.OFTString)
    outLayer.CreateField(new_field)
    # Close the Shapefile
    outDataSet.Destroy()
    
    call = '%s -t_srs "%s" "%s" "%s"' % (gdaltindex, crs_quads, quad_select, map_tiff_geo)
    print call
    response=subprocess.check_output(call, shell=True)
    print response


#check if clip rectangle and vector SRS is identical, if not, reproject rectangle to vector SRS:
if not crs_quads==crs_vector:
    print "quadrangle and vector data not in the same SRS. reprojecting the quadrangle..."
    quads_proj = quad_select.replace('.shp','_proj.shp')
    call = ogr2ogr+' -t_srs "'+crs_vector+'" -s_srs "'+crs_quads+'" "'+quads_proj+'" "'+quad_select+'"'
    print call
    response=subprocess.check_output(call, shell=True)
    print response
    quad_select = quads_proj


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
                
                
