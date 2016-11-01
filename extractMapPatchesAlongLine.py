import subprocess
import os, sys
from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from shapely.geometry import Polygon
from shapely.wkb import loads
#------------------------------------------------------------------------------

#parameters:
vector_proj = r"F:\HISTMAPS\DOWNLOADS_USGS\VECTOR\CA_transportation\TRAN_6_California_GU_STATEORTERRITORY_SHP\Shape\Trans_RailFeature_clip_proj.shp"
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Acolita_100348_1998_24000_bag-20161013T204103Z\CA_Acolita_100348_1998_24000_bag\data\CA_Acolita_100348_1998_24000_geo.tif"
map_subsets_folder = r"F:\HISTMAPS\SEMANT_INTEGR_TEST\map_subsets"

sampledist = 40     #distance of interpolated points along the polyline
winsize = 60        #windowsize of cropped image

#full path to gdal executables
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
ogr2ogr = r'C:\OSGeo4W\bin\ogr2ogr.exe'
gdal_translate = r'C:\OSGeo4W\bin\gdal_translate.exe'

#the name and state of current map quadrangle:
quadrangle_name = "Acolita"
quadrangle_state = "California"

#--functions-------------------------------------------------------------------
def multipoly2poly(in_lyr, out_lyr):
    for in_feat in in_lyr:
        geom = in_feat.GetGeometryRef()
        if geom.GetGeometryName() == 'MULTLINESTRING':
            for geom_part in geom:
                addPolygon(geom_part.ExportToWkb(), out_lyr)
        else:
            addPolygon(geom.ExportToWkb(), out_lyr)

def addPolygon(simplePolygon, out_lyr):
    featureDefn = out_lyr.GetLayerDefn()
    polygon = ogr.CreateGeometryFromWkb(simplePolygon)
    out_feat = ogr.Feature(featureDefn)
    out_feat.SetGeometry(polygon)
    out_lyr.CreateFeature(out_feat)
    print 'Polyline added.'
#------------------------------------------------------------------------------

#make sure raster and vector are in same CRS

call = gdalsrsinfo+' -o proj4 "'+vector_proj+'"'
crs_vector=subprocess.check_output(call, shell=True).strip().replace("'","")

call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")

if not crs_vector == crs_raster:
    print 'vector and raster not in the same projection.'
    print crs_vector
    print crs_raster
    sys.exit(0)

#dissolve the vector raster to multipart feature
vector_diss=vector_proj.replace('.shp','_diss.shp')
path, table = os.path.split(vector_proj)
call = """%s %s %s -dialect sqlite -sql "SELECT ST_Union(Geometry) AS Geometry FROM '%s'" """ % (ogr2ogr, vector_diss, vector_proj, table.replace('.shp',''))
print call
response=subprocess.check_output(call, shell=True)
print response

#now split multiparts into singleparts:

gdal.UseExceptions()
driver = ogr.GetDriverByName('ESRI Shapefile')
in_ds = driver.Open(vector_diss, 0)
in_lyr = in_ds.GetLayer()
singelpt_shp = vector_diss.replace('.shp','_snglpt.shp')
if os.path.exists(singelpt_shp):
    driver.DeleteDataSource(singelpt_shp)
out_ds = driver.CreateDataSource(singelpt_shp)
out_lyr = out_ds.CreateLayer('poly', geom_type=ogr.wkbLineString)

multipoly2poly(in_lyr, out_lyr)
in_ds.Destroy()
out_ds.Destroy() 

#dissolve shp feature count
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(singelpt_shp, 0) # 0 means read-only. 1 means writeable.
if dataSource is None:
    print 'Could not open %s' % (vector_diss)
else:
    print 'Opened %s' % (vector_diss)
    layer = dataSource.GetLayer()
    featureCount = layer.GetFeatureCount()
    print "Number of features in %s: %d" % (os.path.basename(vector_diss),featureCount)

#now loop through features and extract vertex coords

dataSource = driver.Open(singelpt_shp, 0)    
layer = dataSource.GetLayer()  

pointsList = []  
for feature in layer:
    geom = feature.GetGeometryRef()
    print geom.GetPointCount()    
    if geom.GetPointCount()==0:
        #then we have MultiLineString:
        for linefeat in geom:
           points = linefeat.GetPointCount()
           for i in range(0, points):
                # GetPoint returns a tuple not a Geometry
                pt = linefeat.GetPoint(i)
                #print "%i). POINT (%d %d)" %(i, pt[0], pt[1])
      
           #interpolate points along the line:  
           geomPolyline = loads(linefeat.ExportToWkb())  
           polyLength =  geomPolyline.length            
           for x in range(0,int(polyLength),sampledist):
               pointsList.append(geomPolyline.interpolate(x))  # interpolating points along each line
           #print pointsList            

#crate shp for interploated points
pts_interpol = vector_proj.replace('.shp','_pts_interpol.shp')
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource(pts_interpol)
layer = ds.CreateLayer('', None, ogr.wkbPoint)
#create prj file:
spatialRef = osr.SpatialReference()
spatialRef.ImportFromProj4(crs_vector)
spatialRef.MorphToESRI()
file = open(pts_interpol.replace('.shp','.prj'), 'w')
file.write(spatialRef.ExportToWkt())
file.close()

# Add ID attribute
layer.CreateField(ogr.FieldDefn('ID', ogr.OFTInteger))
defn = layer.GetLayerDefn()

#loop through interpolated points and extract TIFF subset
idcount=0
for ptgeom in pointsList:    
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('ID', idcount)
    
    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(ptgeom.wkb)
    feat.SetGeometry(geom)    
    layer.CreateFeature(feat)
    feat = geom = None  # destroy these
    idcount+=1
        
    #for each interpolated location, extract subset of map:
    ulx = ptgeom.x - 0.5*winsize
    uly = ptgeom.y + 0.5*winsize
    lrx = ptgeom.x + 0.5*winsize
    lry = ptgeom.y - 0.5*winsize
     
    current_img = map_subsets_folder+os.sep+quadrangle_state+'_'+quadrangle_name+'_'+str(idcount)+'_dist'+str(sampledist)+'_win'+str(winsize)+'.tif'
    gdal_cmd = gdal_translate+' -of GTiff -projwin %s %s %s %s %s %s' % (ulx,uly,lrx,lry,map_tiff_geo,current_img)
    print gdal_cmd
    response=subprocess.check_output(gdal_cmd, shell=True)
    print response
    
# Save and close everything
ds = layer = feat = geom = None      
dataSource.Destroy() 
