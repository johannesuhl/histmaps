# -*- coding: cp1252 -*-
import xml.dom.minidom
import numpy as np
from osgeo import ogr
from osgeo import osr
import os
from shapely.geometry import Point
import matplotlib.pyplot as plt
from osgeo import gdal
from gdalconst import GA_ReadOnly
import subprocess

#input
map_tiff_geo = r"F:\HISTMAPS\from_USC\CA_Acolita_100348_1998_24000_bag-20161013T204103Z\CA_Acolita_100348_1998_24000_bag\data\CA_Acolita_100348_1998_24000_geo.tif"
vector_2b_transformed = r'F:\HISTMAPS\DOWNLOADS_USGS\VECTOR\CA_transportation\TRAN_6_California_GU_STATEORTERRITORY_SHP\Shape\Trans_RailFeature_clip_proj.shp'

gcp_wlrd_coord_crs = '+proj=longlat +datum=NAD27 +no_defs ' 
gdalsrsinfo = r'C:\OSGeo4W\bin\gdalsrsinfo.exe'
gdallocationinfo = r'C:\OSGeo4W\bin\gdallocationinfo.exe'

outputShapefile = vector_2b_transformed.replace('.shp','_adjusted.shp')  
#--------------------------------
useGDALgeotransform = False
use1stOrderPolynomial = False
use2ndOrderPolynomial = True #<<<<----ues this parameter if gdalwarp in <mapname>_gcp.bat uses order=2
use3rdOrderPolynomial = False
#--------------------------------

#--------------------------------
def getPixelCoordsForLocation(x,y,raster,gdallocationinfo):
    call = gdallocationinfo+' -geoloc "'+raster+'" '+str(x)+' '+str(y)
    response=subprocess.check_output(call, shell=True)
    response = response.split('\r\n')[1].replace('Location: ','').replace('P','').replace('L','').replace(' ','').replace('(','').replace(')','')
    (u,v) = response.split(',')
    return (int(u),-1*int(v))

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

#--------------------------------
def reverseAffineTransform(tp,X,Y):
    #here I implement the inverse affine transformation based on manual matrix inversion using GDAL geotransform.
    x2 = (tp[5]*(X-tp[0])-tp[2]*(Y-tp[3]))/((tp[1]*tp[5])-(tp[2]*tp[4]))
    y2 = (tp[4]*(X-tp[0])-tp[1]*(Y-tp[3]))/((tp[1]*tp[5])-(tp[2]*tp[4]))
    return (x2,y2)
#--------------------------------

call = gdalsrsinfo+' -o proj4 "'+map_tiff_geo+'"'
crs_raster=subprocess.check_output(call, shell=True).strip().replace("'","")
mapraster = gdal.Open(map_tiff_geo, GA_ReadOnly)
geotransform = mapraster.GetGeoTransform()
print geotransform

gcp_wlrd_coord_crs
crs_raster
#--------------------------------read GCPs in both systems:

xmlfile = map_tiff_geo.replace("geo.tif","gcp.xml")
dom1 = xml.dom.minidom.parse(xmlfile)

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
    
gcp_coords_uv = zip(gcpUs,gcpVs)
gcp_coords_lonlat = zip(gcplons, gcplats)
gcp_coords_xy = list()
for lonlat in gcp_coords_lonlat:
    #transform lonlat into local map system:
    (x,y) = transformPoint(lonlat[0],lonlat[1],gcp_wlrd_coord_crs,crs_raster)
    gcp_coords_xy.append((x,y))


#-------------------obtain affine transformation parameters using least squares

def Fit_2ndOrder_Polynomial( from_pts, to_pts ):

    #Second order polynomial (6 coefficients per coordinate)
    #x'=k1+k2*x+k3*y+k4*x**2+k5*x*y+k6y**2
    #y'=k7+k8*x+k9*y+k10*x**2+k11*x*y+k12*y**2

    xfrom = [row[0] for row in from_pts]
    yfrom = [row[1] for row in from_pts]
    xto = [row[0] for row in to_pts]
    yto = [row[1] for row in to_pts]

    B = np.append(xto,yto) #this the is observation vector
    Alist=list() #construct the A matrix
    for i in range(0,len(xfrom)):
        #the x observations
        row=(1,xfrom[i],yfrom[i],xfrom[i]*yfrom[i],xfrom[i]**2,yfrom[i]**2,0,0,0,0,0,0)
        Alist.append(row)
    for i in range(0,len(xfrom)):  
        #the y observations
        row=(0,0,0,0,0,0,1,xfrom[i],yfrom[i],xfrom[i]*yfrom[i],xfrom[i]**2,yfrom[i]**2)
        Alist.append(row)
        
    A = np.array((Alist))
    (coeffs, r, rank, s) = np.linalg.lstsq(A, B) #here we solve the eq sys using least squares.
    return coeffs

def Apply_2ndOrder_Polynomial(x,y,coeffs): 

    xtrans=coeffs[0]+coeffs[1]*x+coeffs[2]*y+coeffs[3]*x*y+coeffs[4]*x**2+coeffs[5]*y**2
    ytrans=coeffs[6]+coeffs[7]*x+coeffs[8]*y+coeffs[9]*x*y+coeffs[10]*x**2+coeffs[11]*y**2

    return(xtrans,ytrans)

def Fit_3rdOrder_Polynomial( from_pts, to_pts ):

    #Second order polynomial (6 coefficients per coordinate)
    #x'=k1+k2*x+k3*y+k4*x**2+k5*x*y+k6y**2 + k7xy² + k8yx² + k9x²y²
    #y'=k10+k11*x+k12*y+k13*x**2+k14*x*y+k15*y**2  + k16xy² + k17yx² + k18x²y²

    xfrom = [row[0] for row in from_pts]
    yfrom = [row[1] for row in from_pts]
    xto = [row[0] for row in to_pts]
    yto = [row[1] for row in to_pts]

    B = np.append(xto,yto) #this the is observation vector
    Alist=list() #construct the A matrix
    for i in range(0,len(xfrom)):
        #the x observations
        row=(1,xfrom[i],yfrom[i],xfrom[i]*yfrom[i],xfrom[i]**2,yfrom[i]**2,xfrom[i]*(yfrom[i]**2),(xfrom[i]**2)*yfrom[i],xfrom[i]**3,yfrom[i]**3,0,0,0,0,0,0,0,0,0,0)
        Alist.append(row)
    for i in range(0,len(xfrom)):  
        #the y observations
        row=(0,0,0,0,0,0,0,0,0,0,1,xfrom[i],yfrom[i],xfrom[i]*yfrom[i],xfrom[i]**2,yfrom[i]**2,xfrom[i]*(yfrom[i]**2),(xfrom[i]**2)*yfrom[i],xfrom[i]**3,yfrom[i]**3)
        Alist.append(row)
        
    A = np.array((Alist))
    (coeffs, r, rank, s) = np.linalg.lstsq(A, B) #here we solve the eq sys using least squares.
    print (coeffs, r, rank, s)
    return coeffs

def Apply_3rdOrder_Polynomial(x,y,coeffs):

    xtrans=coeffs[0]+coeffs[1]*x+coeffs[2]*y+coeffs[3]*x*y+coeffs[4]*x**2+coeffs[5]*y**2+coeffs[6]*x*(y**2) +coeffs[7]*y*(x**2)+coeffs[8]*(x**3)+coeffs[9]*(y**3)
    ytrans=coeffs[10]+coeffs[11]*x+coeffs[12]*y+coeffs[13]*x*y+coeffs[14]*x**2+coeffs[15]*y**2+coeffs[16]*x*(y**2)+coeffs[17]*y*(x**2)+coeffs[18]*(x**3)+coeffs[19]*(y**3)

    return(xtrans,ytrans)


#-------------------obtain affine transformation parameters using least squares

def Affine_Fit( from_pts, to_pts ):
    """Fit an affine transformation to given point sets.
      More precisely: solve (least squares fit) matrix 'A'and 't' from
      'p ~= A*q+t', given vectors 'p' and 'q'.
      Works with arbitrary dimensional vectors (2d, 3d, 4d...).

      Written by Jarno Elonen <elonen@iki.fi> in 2007.
      Placed in Public Domain.

      http://elonen.iki.fi/code/misc-notes/affine-fit/

      Based on paper "Fitting affine and orthogonal transformations
      between two sets of points, by Helmuth Späth (2003)."""

    q = from_pts
    p = to_pts
    if len(q) != len(p) or len(q)<1:
        print "from_pts and to_pts must be of same size."
        return False

    dim = len(q[0]) # num of dimensions
    if len(q) < dim:
        print "Too few points => under-determined system."
        return False

    # Make an empty (dim) x (dim+1) matrix and fill it
    c = [[0.0 for a in range(dim)] for i in range(dim+1)]
    for j in range(dim):
        for k in range(dim+1):
            for i in range(len(q)):
                qt = list(q[i]) + [1]
                c[k][j] += qt[k] * p[i][j]

    # Make an empty (dim+1) x (dim+1) matrix and fill it
    Q = [[0.0 for a in range(dim)] + [0] for i in range(dim+1)]
    for qi in q:
        qt = list(qi) + [1]
        for i in range(dim+1):
            for j in range(dim+1):
                Q[i][j] += qt[i] * qt[j]

    # Ultra simple linear system solver. Replace this if you need speed.
    def gauss_jordan(m, eps = 1.0/(10**10)):
      """Puts given matrix (2D array) into the Reduced Row Echelon Form.
         Returns True if successful, False if 'm' is singular.
         NOTE: make sure all the matrix items support fractions! Int matrix will NOT work!
         Written by Jarno Elonen in April 2005, released into Public Domain"""
      (h, w) = (len(m), len(m[0]))
      for y in range(0,h):
        maxrow = y
        for y2 in range(y+1, h):    # Find max pivot
          if abs(m[y2][y]) > abs(m[maxrow][y]):
            maxrow = y2
        (m[y], m[maxrow]) = (m[maxrow], m[y])
        if abs(m[y][y]) <= eps:     # Singular?
          return False
        for y2 in range(y+1, h):    # Eliminate column y
          c = m[y2][y] / m[y][y]
          for x in range(y, w):
            m[y2][x] -= m[y][x] * c
      for y in range(h-1, 0-1, -1): # Backsubstitute
        c  = m[y][y]
        for y2 in range(0,y):
          for x in range(w-1, y-1, -1):
            m[y2][x] -=  m[y][x] * m[y2][y] / c
        m[y][y] /= c
        for x in range(h, w):       # Normalize row y
          m[y][x] /= c
      return True

    # Augement Q with c and solve Q * a' = c by Gauss-Jordan
    M = [ Q[i] + c[i] for i in range(dim+1)]
    if not gauss_jordan(M):
        print "Error: singular matrix. Points are probably coplanar."
        return False

    # Make a result object
    class Transformation:
        """Result object that represents the transformation
           from affine fitter."""

        def To_Str(self):
            res = ""
            for j in range(dim):
                str = "x%d' = " % j
                for i in range(dim):
                    str +="x%d * %f + " % (i, M[i][j+dim+1])
                str += "%f" % M[dim][j+dim+1]
                res += str + "\n"
            return res

        def Transform(self, pt):
            res = [0.0 for a in range(dim)]
            for j in range(dim):
                for i in range(dim):
                    res[j] += pt[i] * M[i][j+dim+1]
                res[j] += M[dim][j+dim+1]
            return res
    return Transformation()

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
	
from_pt =gcp_coords_xy
to_pt = gcp_coords_uv  

if use2ndOrderPolynomial:
    coeffs_xy2uv = Fit_2ndOrder_Polynomial(from_pt, to_pt)
    coeffs_uv2xy = Fit_2ndOrder_Polynomial(to_pt, from_pt)
    print "coeffs xy2uv are:"
    print coeffs_xy2uv
    print "coeffs uv2xy are:"
    print coeffs_uv2xy
    
if use3rdOrderPolynomial:
    coeffs_xy2uv = Fit_3rdOrder_Polynomial(from_pt, to_pt)
    coeffs_uv2xy = Fit_3rdOrder_Polynomial(to_pt, from_pt)
    print "coeffs xy2uv are:"
    print coeffs_xy2uv
    print "coeffs uv2xy are:"
    print coeffs_uv2xy

if use1stOrderPolynomial:  
    trn_xy2uv = Affine_Fit(from_pt, to_pt)
    trn_uv2xy = Affine_Fit(to_pt, from_pt)
    print "Transformation trn_xy2uv is:"
    print trn_xy2uv.To_Str()
    print "Transformation trn_uv2xy is:"
    print trn_uv2xy.To_Str()

#--------------transform shapefile:------------------------------------------ 

driver = ogr.GetDriverByName('ESRI Shapefile')
# get the input layer
inDataSet = driver.Open(vector_2b_transformed)
inLayer = inDataSet.GetLayer()
# input SpatialReference
inSpatialRef = osr.SpatialReference()
inSpatialRef = inLayer.GetSpatialRef()
# output SpatialReference
outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromProj4(gcp_wlrd_coord_crs)
# create the CoordinateTransformation
coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

# create the output layer
if os.path.exists(outputShapefile):
    driver.DeleteDataSource(outputShapefile)
outDataSet = driver.CreateDataSource(outputShapefile)
outLayer = outDataSet.CreateLayer("layer", geom_type=ogr.wkbLineString)
# add fields
inLayerDefn = inLayer.GetLayerDefn()
for i in range(0, inLayerDefn.GetFieldCount()):
    fieldDefn = inLayerDefn.GetFieldDefn(i)
    outLayer.CreateField(fieldDefn)
# get the output layer's feature definition
outLayerDefn = outLayer.GetLayerDefn()

for feature in inLayer:
    geom_trans1 = feature.GetGeometryRef()
    geom_wkt = geom_trans1.ExportToWkt()
    print 'local coord before', geom_wkt

    
    #now reproject gem from local to Lat Lon.
    #geom_trans1.Transform(coordTrans)   
    #geom_wkt = geom_trans1.ExportToWkt()
    #print 'in latlon', geom_wkt
    
    geom_trans2 = ogr.Geometry(ogr.wkbLineString)
    #now we have to apply the reverse affin transformation (for each vertex):
    for i in range(0, geom_trans1.GetPointCount()):

        pt = geom_trans1.GetPoint(i)
        X=pt[0]
        Y=pt[1]    
        #get pixel coords of the vertex:
        (u,v) = getPixelCoordsForLocation(X,Y,map_tiff_geo,gdallocationinfo)
        
        if use1stOrderPolynomial:
            #1st oder poly is identical to affine transf. using 3 coeffs per coorindate
            #get transformed local coords of vertex using  affine transformation based on GCPs, least squares:        
            (X_trans,Y_trans) = trn_uv2xy.Transform((u,-1*v)) #v coordinate must be negative

        if use2ndOrderPolynomial:
            #get transformed local coords of vertex using  2nd order polynomial transformation: 
            #using 6 coeffs per coordinate
            (X_trans,Y_trans) = Apply_2ndOrder_Polynomial(u,-1*v,coeffs_uv2xy)

        if use3rdOrderPolynomial:
            #get transformed local coords of vertex using  2nd order polynomial transformation: 
            #using 10 coeffs per coordinate
            (X_trans,Y_trans) = Apply_3rdOrder_Polynomial(u,-1*v,coeffs_uv2xy)   
            
        if useGDALgeotransform:
            #get transformed local coords of vertex using  GDAL geotrqansform: 
            X_trans = geotransform[0] + u*geotransform[1] + -1*v*geotransform[2]
            Y_trans = geotransform[3] + u*geotransform[4] + -1*v*geotransform[5]       
            (u2,v2) = reverseAffineTransform(geotransform,X,Y) 
            #however this will give the identical coordinates since the measurement errors are not taken into account.
            #it only transforms image and word coordinates back and forth.      
            print u,u2,v,v2
        
        print X,X_trans,Y,Y_trans
        
        geom_trans2.AddPoint(X_trans,Y_trans)
        
    geom_wkt = geom_trans2.ExportToWkt()
    print 'local coord after', geom_wkt    
    
    
    # create a new feature
    outFeature = ogr.Feature(outLayerDefn)
    # set the geometry and attribute
    outFeature.SetGeometry(geom_trans2)
    for i in range(0, outLayerDefn.GetFieldCount()):
        outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))
    # add the feature to the shapefile
    outLayer.CreateFeature(outFeature)
    # destroy the features and get the next input feature
    outFeature.Destroy()

# close the shapefiles
inDataSet.Destroy()
outDataSet.Destroy()

#create prj file:
spatialRef = osr.SpatialReference()
spatialRef.ImportFromProj4(crs_raster)
spatialRef.MorphToESRI()
file = open(outputShapefile.replace('.shp','.prj'), 'w')
file.write(spatialRef.ExportToWkt())
file.close()   
