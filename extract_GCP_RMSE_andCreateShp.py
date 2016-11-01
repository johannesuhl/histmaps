import xml.dom.minidom
import numpy as np
from osgeo import ogr
from osgeo import osr
from shapely.geometry import Point
import numpy as np
import matplotlib.pyplot as plt

#input
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Acolita_100348_1998_24000_bag-20161013T204103Z\CA_Acolita_100348_1998_24000_bag\data\CA_Acolita_100348_1998_24000_geo.tif"
gcp_wlrd_coord_crs = '+proj=longlat +datum=NAD27 +no_defs ' 

#--------------------------------

xmlfile = map_tiff_geo.replace("geo.tif","gcp.xml")
dom1 = xml.dom.minidom.parse(xmlfile)
gcperrors=list()
gcpcount=1
last_gcp_found=False
while not last_gcp_found:
    errortag="MarkError"+str(gcpcount)
    found=False
    for node in dom1.getElementsByTagName(errortag):
        found=True
        print gcpcount, node.firstChild.nodeValue
        gcperrors.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1
print "======"
RMSE = np.sqrt(sum( i*i for i in gcperrors) / float(len(gcperrors)))
print "RMSE = ", RMSE


#create barplot of the errors
outpng = map_tiff_geo.replace(".tif","_GCPs.png")
ind = np.arange(len(gcperrors))  # the x locations for the groups
width = 0.35       # the width of the bars
fig, ax = plt.subplots()
rects1 = ax.bar(ind, gcperrors, width, color='r')
# add some text for labels, title and axes ticks
ax.set_xlabel('GCP')
ax.set_ylabel('Error Magnitude in px')
ax.set_title('GCP Errors, RMSE = '+str(RMSE))
plt.show()
fig.savefig(outpng) 


# write GCPs to SHP for visualization:
gcplons=list()
gcpcount=1
last_gcp_found=False
while not last_gcp_found:
    tag="MarkLongitude"+str(gcpcount)
    found=False
    for node in dom1.getElementsByTagName(tag):
        found=True
        gcplons.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1

gcplats=list()
gcpcount=1
last_gcp_found=False
while not last_gcp_found:
    tag="MarkLatitude"+str(gcpcount)
    found=False
    for node in dom1.getElementsByTagName(tag):
        found=True
        gcplats.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1
    
#print gcplons
#print gcplats

shpfile = map_tiff_geo.replace(".tif",".shp")
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource(shpfile)
layer = ds.CreateLayer('', None, ogr.wkbPoint)
# Add attributes
layer.CreateField(ogr.FieldDefn('ID', ogr.OFTInteger))
layer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('err', ogr.OFTReal))
defn = layer.GetLayerDefn()
#create prj file:
spatialRef = osr.SpatialReference()
spatialRef.ImportFromProj4(gcp_wlrd_coord_crs)
spatialRef.MorphToESRI()
file = open(shpfile.replace('.shp','.prj'), 'w')
file.write(spatialRef.ExportToWkt())
file.close()


count=0
for lon in gcplons:
    lat = gcplats[count]   
    err = gcperrors[count] 
    ## If there are multiple geometries, put the "for" loop here
    # Here's an example Shapely geometry
    point = Point([(lon, lat)])    
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', count)
    feat.SetField('lon', lon)
    feat.SetField('lat', lat)
    feat.SetField('err', err)
    
    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(point.wkb)
    feat.SetGeometry(geom)
    
    layer.CreateFeature(feat)
    feat = geom = None  # destroy these
    count+=1
    
# Save and close everything
ds = layer = feat = geom = None

