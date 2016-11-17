# Exploiting Context in Cartographic Evolutionary Documents to Extract and Build Linked Spatial-temporal Datasets

## Python code documentation for USGS map processing and information extraction

Johannes Uhl

Department of Geography

University of Colorado Boulder

Date last modified: 11-16-2016


### Source:
Python Scripts on GitHub: 	https://github.com/johannesuhl/histmaps

Clone URL:			 https://github.com/johannesuhl/histmaps.git

## Required libraries:
-	GDAL executables
-	GDAL python bindings
-	Shapely

## ApplyGCPbatForAllTiffs.py
-	Loops through a folder with zipped USGS tifs
-	Unzips the zip file
-	Adjusts paths in <map_name>_gcp.bat
-	Runs <map_name>_gcp.bat
- Creates the <map_name>_geo.tif (correcty georeferenced in QGIS)

## GDAL_GeoPDF2GeoTIFF.py
-	Converts a GeoPDF (as downloaded from https://viewer.nationalmap.gov into a geoTiff
-	It allows to control which layers are converted

## RetrieveCRSforAllTiffs.py
-	Loops through a folder of zipped USGS tifs
-	Unzips the zip files
-	Reads out the spatial reference system (SRS)
-	Writes the SRS parameters into a txt file

## USGS_TIFF_DOWNLOAD.py
-	Reads Amazon cloud CSV provided by USGS
-	Extracts URL of each zipped tif
-	Downloads the zip file

## USGS_TIFF_getCompressionRateStats.py
-	Loops through zipped tif files
-	Writes out compression rate for each zip file
-	Computes mean compression rate for memory requirement estimation

## USGS_TIFF_getMapEditionYears.py
-	Loops through zipped tif files
-	Extract map year from file name
-	Creates histogram of year frequencies
 
## extractMapPatchesAlongLine.py
-	Extracts positive map samples along vector features
-	Requires output <name>_proj.shp from script proj_vector2raster.py
 
## extractMapPatchesAlongLinePlusNegativeSamples.py
-	Extracts positive map samples along vector features
-	Extracts negative map samples at random locations (Nneg = Npos) not overlapping each other nor with positive samples
 
## Proj_vector2raster.py
-	Reads tif + vector data
-	Clips vector to quadrangle extent   <name>_clip.shp
-	Reprojects vector <name>_proj.shp

## Proj_vector2raster_andMerge_wParams.py
-	Reads multiple shps
-	Reads map tif
-	Clips them to quadrangle extent
-	Reprojects shps
-	Merges reprojected shps
-	Can be run in command line as follows:

proj_vector2raster_andMerge_wParams.py "input1.shp,input2.shp,input3.shp" "raster.tif" Quadr_name Quadr_State 

## proj_vector2raster_flexibleClipExtents.py
- Similar to Proj_vector2raster.py, but different clip extents can be used, according to the following booleans:

- quadrangleIsUserSpecified = True: The clip extent is extracted from the quadrangles.shp based on the specified quadrangle name and state.

- findQuadrangleByOverlay = True: The clip extent is extracted as the underlying quadrangle from quadrangles.shp based on the location of the map. Useful for batch processing of multiple maps.

- useMapExtentInsteadOfQuadrangles = True: For maps that do not match to the quadrangle system (irregular quadrangle exents) the extent of the raster map itself is used to clip the vector data. Note: The clipped vector data will overlap with the map sheet edges (outside the actual map image).

In addition to that, vector data of an arbitrary coordinate reference system (CRS) can be used. The clip geometry will be reprojected into the vector CRS before clipping. Then the clipped vector data will be reprojected into the raster CRS.

## TransformVectorBasedOn2ndOrderPolynomial.py
Reads the map the corresponding clipped and reprojected output from either of these scripts:

-	Proj_vector2raster.py
-	proj_vector2raster_flexibleClipExtents.py
-	Proj_vector2raster_andMerge_wParams.py

It will read the <mapname>_gcp.xml and based on the ground control point (GCP) coordinate pairs it will use least squares adjustment to establish a 2nd order polynomial transformation. It will transform the vector geometry and create a new shapefile. This shapefile should line up better with the raster data, since it accounts for inaccuracies in the GCPs.
Please use the Boolean parameter use2ndOrderPolynomial.

