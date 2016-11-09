import xml.dom.minidom
import numpy as np
from osgeo import ogr
from osgeo import osr
from shapely.geometry import Point
import matplotlib.pyplot as plt
from osgeo import gdal
from gdalconst import GA_ReadOnly
import subprocess

#input
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Acolita_100348_1998_24000_bag-20161013T204103Z\CA_Acolita_100348_1998_24000_bag\data\CA_Acolita_100348_1998_24000_geo.tif"
gcp_wlrd_coord_crs = '+proj=longlat +datum=NAD27 +no_defs ' 
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'


#OUTPUTS:

# a shp (_gcp_infos.shp) containing the GCP locations as pint features, attributes about GCP errors from XML file and discrepancies
# (shift and angle) obtained from backtransformation of GCP image coordinates to world coordinates using the affine transormation
#parameters extracted from the reprojected *_geo.tif
#also a PNG is outputted containing a graph about the errors in each GCP
#also a txt file containing the RMSE, errors from the XML file and obtained discrepany measures for each GCP.


#--------------------------------
def transformPoint(x,y,s_proj4,t_proj4):
    source = osr.SpatialReference()
    source.ImportFromProj4(s_proj4)  
    target = osr.SpatialReference()
    target.ImportFromProj4(t_proj4)   
    transform = osr.CoordinateTransformation(source, target)    
    point = ogr.CreateGeometryFromWkt("POINT ("+str(x)+" "+str(y)+")")
    point.Transform(transform)
    return (point.GetX(),  point.GetY())

call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")

txtfile = map_tiff_geo.replace(".tif","_GCP_infos.txt")
outfile = open(txtfile,'a') 
    

mapraster = gdal.Open(map_tiff_geo, GA_ReadOnly)
transform = mapraster.GetGeoTransform()
print transform

print >>outfile, 'affine transformation parameters'
print >>outfile, transform

print >>outfile, 'GCP errors from XML file:'
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
        print >>outfile, gcpcount, node.firstChild.nodeValue
        gcperrors.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1
print "======"
RMSE = np.sqrt(sum( i*i for i in gcperrors) / float(len(gcperrors)))
print "RMSE = ", RMSE
print >>outfile, "RMSE = ", RMSE


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

gcpUs=list()
gcpcount=1
last_gcp_found=False
while not last_gcp_found:
    tag="MarkU"+str(gcpcount)
    found=False
    for node in dom1.getElementsByTagName(tag):
        found=True
        gcpUs.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1

gcpVs=list()
gcpcount=1
last_gcp_found=False
while not last_gcp_found:
    tag="MarkV"+str(gcpcount)
    found=False
    for node in dom1.getElementsByTagName(tag):
        found=True
        gcpVs.append(float(node.firstChild.nodeValue))
    if not found:
        last_gcp_found = True
    gcpcount+=1
    
gcp_coords = zip(gcplons, gcplats,gcpUs,gcpVs)

#Xp = transform[0] + P*transform[1] + L*transform[2];
#Yp = transform[3] + P*transform[4] + L*transform[5];

shifts=[]
angles=[]

print >>outfile, 'GCP shifts obtained by backtransformation:'
count=1
for gcp in gcp_coords:
        
    Xp = transform[0] + gcp[2]*transform[1] + gcp[3]*transform[2];
    Yp = transform[3] + gcp[2]*transform[4] + gcp[3]*transform[5];   
    (Xp_trans,Yp_trans) = transformPoint(gcp[0],gcp[1],gcp_wlrd_coord_crs,crs_raster)
    
    #x_shift = Xp_trans - Xp
    #y_shift = Yp_trans - Yp
    x_shift =  Xp - Xp_trans
    y_shift =  Yp - Yp_trans

    
    shift = np.sqrt(x_shift**2+y_shift**2)
    
    #angle_deg = np.arctan(y_shift/x_shift)*180.0/np.pi
    angle_deg = np.arctan2(y_shift,x_shift)*180.0/np.pi
    
    if angle_deg<0: angle_deg = 360 + angle_deg
    
    print shift,angle_deg
    print >>outfile,count,shift,angle_deg
    shifts.append(shift)
    angles.append(angle_deg)
    count+=1

    
#print gcplons
#print gcplats

shpfile = map_tiff_geo.replace(".tif","_gcp_infos.shp")
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource(shpfile)
layer = ds.CreateLayer('', None, ogr.wkbPoint)
# Add attributes
layer.CreateField(ogr.FieldDefn('ID', ogr.OFTInteger))
layer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('err', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('shift', ogr.OFTReal))
layer.CreateField(ogr.FieldDefn('angle', ogr.OFTReal))
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
    shift = shifts[count] 
    angle = angles[count] 
    
    ## If there are multiple geometries, put the "for" loop here
    # Here's an example Shapely geometry
    point = Point([(lon, lat)])    
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', count)
    feat.SetField('lon', lon)
    feat.SetField('lat', lat)
    feat.SetField('err', err)
    feat.SetField('shift', shift)
    feat.SetField('angle', angle)
    
    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(point.wkb)
    feat.SetGeometry(geom)
    
    layer.CreateFeature(feat)
    feat = geom = None  # destroy these
    count+=1
    
# Save and close everything
ds = layer = feat = geom = None
del outfile
