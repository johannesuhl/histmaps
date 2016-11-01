import sys, os
import zipfile
import numpy

folder =  r'F:\HISTMAPS\DOWNLOADS_USGS\TIFF_CA'
ratios = list()
for fn in os.listdir(folder):
    try:
        name = os.path.join(folder,fn)
        fileobj = zipfile.ZipFile(name)

        for info in fileobj.infolist():
            ratio = float(info.file_size) / float(info.compress_size)
            ratios.append(ratio)
    except:
        print fn, 'not readable'

print 'average compression rate:', numpy.mean(ratios)
