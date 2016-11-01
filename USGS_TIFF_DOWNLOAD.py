import sys, os
import shutil
import urllib2
import csv

outfolder =  r'F:\HISTMAPS\DOWNLOADS_USGS\TIFF_CA'
csvfile = r'F:\HISTMAPS\csv\ca_historic_maps.csv'
with open(csvfile, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    rowcount=0
    for row in csvreader:
        rowcount+=1
        
        for download_url in row:
            if 'https:' in download_url:
                try:
                    filename = download_url.split('/')[-1]
                    outfile = outfolder+os.sep+filename

                    if os.path.exists(outfile):
                        print 'EXISTS', outfile
                        continue
                    
                    #print download_url, outfile
                    req = urllib2.urlopen(download_url.replace(' ','%20'))

                    with open(outfile, 'wb') as fp:
                        shutil.copyfileobj(req, fp)

                    print download_url, 'OK'
                    del fp
                except:
                    print 'ERROR downloading', download_url
