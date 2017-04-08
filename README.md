# Exploiting Context in Cartographic Evolutionary Documents to Extract and Build Linked Spatial-temporal Datasets

## Python code documentation for USGS map processing and information extraction

Johannes Uhl

Department of Geography

University of Colorado Boulder

Date last modified: March 2017


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

## extract_GCP_RMSE_affine_shift_vectors_andCreateShp.py

- Creates GCP point shapefile
- Appends error to the point features
- Creates error barplot, computes RMSE
- Writes out txt file with errors
- Transform 16 grid coordinates
- Compute differences
- Decomposes in vector length and angle, appends as attributes to SHP.


## proj_vector2raster_flexibleClipExtents.py
- Similar to Proj_vector2raster.py, but different clip extents can be used, according to the following booleans:

- quadrangleIsUserSpecified = True: The clip extent is extracted from the quadrangles.shp based on the specified quadrangle name and state.

- findQuadrangleByOverlay = True: The clip extent is extracted as the underlying quadrangle from quadrangles.shp based on the location of the map. Useful for batch processing of multiple maps.

- useMapExtentInsteadOfQuadrangles = True: For maps that do not match to the quadrangle system (irregular quadrangle exents) the extent of the raster map itself is used to clip the vector data. Note: The clipped vector data will overlap with the map sheet edges (outside the actual map image).
UPDATE: If removeMapEdge = True, then the float variables edge_width_n,w,e,s will be used to clip the vector data to the actual map image. These four values have to be obtained manually in QGIS (measure tool).


In addition to that, vector data of an arbitrary coordinate reference system (CRS) can be used. The clip geometry will be reprojected into the vector CRS before clipping. Then the clipped vector data will be reprojected into the raster CRS.

## TransformVectorBasedOn2ndOrderPolynomial.py
Reads the map and the corresponding clipped and reprojected output from either of these scripts:

-	Proj_vector2raster.py
-	proj_vector2raster_flexibleClipExtents.py
-	Proj_vector2raster_andMerge_wParams.py

It will read the <mapname>_gcp.xml and based on the ground control point (GCP) coordinate pairs it will use least squares adjustment to establish a 2nd order polynomial transformation. It will transform the vector geometry and create a new shapefile. This shapefile should line up better with the raster data, since it accounts for inaccuracies in the GCPs.
Please use the Boolean parameter use2ndOrderPolynomial.

-----------

## Proposed use of the scripts for map sample extraction:

1) Use any of these scripts to clip vector data to the raster and to reproject it into the map CRS:

   -	Proj_vector2raster.py
   -	proj_vector2raster_flexibleClipExtents.py
   -	Proj_vector2raster_andMerge_wParams.py
   
2) Use the output *_clip_proj.shp from 1) to adjust the vector data to local map distorsions using

   -	TransformVectorBasedOn2ndOrderPolynomial.py. 
   
The corrected output is called *_adjusted.shp.

3) Use the output from 2) as vector input for 

   -	extractMapPatchesAlongLine.py or 
   -	extractMapPatchesAlongLinePlusNegativeSamples.py

in order to extract training and test samples from the map.

-----------

After classifying the samples you can use the following scripts to visualize the performance / outputs of the classifier:

## Creating t-SNE plots using scikit-learn, OpenCV and Matlab:

1) Use create_tSNE_data.py. This script reads all samples in a folder (or a list of folders containing samples of each class in a separate folder), stacks them to a data cube and writes the cube to a txt file.
It also creates a txt file containing the paths of all input sample files. Then the data cube is reduced to two dimensions, while maintaining the pairwise distance between the images. The resulting 2d coordinates are outputted to a txt, and a scatterplot is created and saved to file as well. See the t-SNE publication here: https://lvdmaaten.github.io/publications/papers/JMLR_2008.pdf.

2) Then use create_tSNE_plots.py. This script requires Matlab. It also needs batch_tsne_embedding.m, a Matlab script file. For each input folder, the .m file is executed in Matlab. The .m file reads the t-SNE coordinates and the txt containing the sample image filenames and creates two images: the sample images as thumbnails in their original location in the 2d t-SNE space, and a rectified version (using some nearest neighbor technique). The size of the thumbnails can be controlled in create_tSNE_plots.py as well.

## Creating nice confusion matrices using seaborn heatmaps:

confmat_viz.py contains a code snippet for plotting confusion matrices using seaborn heatmaps.

## Batch clip USGS map tif files to the actual quadrangle extents:

clip_map_to_quadrangle.py

Parameters:
- data_dir is a folder containing one or multiple maps. these should be in subfolders created by unzipping the USGS zip files using the script ApplyGCPbatForAllTiffs.py, e.g. data_dir\<mapname>\data\
- data must contain the *_geo.tif created by ApplyGCPbatForAllTiffs.py
- data must also contain quadr_<quadrangle_name>_<quadrangle_state>.shp created by the vector preprocessing script proj_vector2raster.py
- output will be *_geo_clip.tif in data_dir directly.
