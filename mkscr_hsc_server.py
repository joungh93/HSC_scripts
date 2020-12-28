#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:22:10 2020

@author: jlee
"""


import sqlite3
import numpy as np
import pandas as pd


# ----- Need to be manually revised! ----- #
wdir = '/data/jlee/HSC_virgo/MACSJ0916-JFG1/'    # The main working directory
dir_red = wdir+'Red/'    # Reduction directory
dir_scr = wdir+'job/'    # The directory which includes the script files
# objfld = 'M0916'    # Object field name
ncores = 56    # Number of cores
make_fringe = True    # y-band (NB0921, NB0926, and NB0973 are not available yet.) (default: False)
use_discrete = False    # use makeDiscreteSkyMap.py instead of makeSkyMap.py (default: True)
ra0_deg, dec0_deg, rad_deg, pixscl = 139.053750, -0.416944, 0.5, 0.168    # Only activated when use_discrete = False
# ---------------------------------------- #


# ----- Extracting data from SQL database ----- #
con = sqlite3.connect(dir_red+'registry.sqlite3')
cur = con.cursor()

# Bias
query_bias = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE field='BIAS' GROUP BY visit,field"
cur.execute(query_bias)
db_bias = cur.fetchall()
db_bias = pd.DataFrame(db_bias, columns=('visit','filter','field','taiObs','expId','expTime'))

# Dark
query_dark = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE field='DARK' GROUP BY visit,field"
cur.execute(query_dark)
db_dark = cur.fetchall()
db_dark = pd.DataFrame(db_dark, columns=('visit','filter','field','taiObs','expId','expTime'))

# Flat
query_flat = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE field='DOMEFLAT' GROUP BY visit,field"
cur.execute(query_flat)
db_flat = cur.fetchall()
db_flat = pd.DataFrame(db_flat, columns=('visit','filter','field','taiObs','expId','expTime'))

filt = np.unique(db_flat['filter'].values)
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	query = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE field='DOMEFLAT' AND filter='"+filt[i]+"' GROUP BY visit,field"
	cur.execute(query)
	exec('db_flat_'+flt+' = cur.fetchall()')
	exec("db_flat_"+flt+" = pd.DataFrame(db_flat_"+flt+", columns=('visit','filter','field','taiObs','expId','expTime'))")

# Object
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	query = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE NOT field IN ('BIAS','DARK','DOMEFLAT') AND filter='"+filt[i]+"' GROUP BY visit,field"
	# query = "SELECT visit,filter,field,taiObs,expId,expTime FROM raw WHERE field='"+objfld+"' AND filter='"+filt[i]+"' GROUP BY visit,field"
	cur.execute(query)
	exec('db_obj_'+flt+' = cur.fetchall()')
	exec("db_obj_"+flt+" = pd.DataFrame(db_obj_"+flt+", columns=('visit','filter','field','taiObs','expId','expTime'))")

con.close()


# ----- Making strings including visit numbers ----- #
field = ['bias', 'dark', 'flat', 'obj']

for i in np.arange(len(field)):
	if (field[i] in ['bias', 'dark']):
		exec('db = db_'+field[i])
		vis = ''
		for k in np.arange(len(db)):
			if (k == np.arange(len(db))[-1]):
				vis += str(db['visit'][k])
			else:
				vis += str(db['visit'][k])+'^'
		print('# ----- '+field[i]+' ----- #')
		print(vis)
		exec('vis_'+field[i]+' = vis')

	if (field[i] in ['flat', 'obj']):
		for j in np.arange(len(filt)):
			flt = filt[j].split('HSC-')[1]
			exec('db = db_'+field[i]+'_'+flt)
			vis = ''
			for k in np.arange(len(db)):
				if (k == np.arange(len(db))[-1]):
					vis += str(db['visit'][k])
				else:
					vis += str(db['visit'][k])+'^'
			print('# ----- '+field[i]+' ('+filt[j]+') ----- #')
			print(vis)
			exec('vis_'+field[i]+'_'+flt+' = vis')

			if (field[i] == 'obj'):
				texpTime = np.sum(db['expTime'].values)
				print(f'Total exposure time: {texpTime:.1f} sec')


# ----- Writing HSC scripts ----- #

### A script for preproc
f = open(dir_scr+'scr_preproc','w')

f.write("rm -rfv "+dir_red+"rerun"+"\n")
for cal in field[:-1]+['sky']:
    f.write("rm -rfv "+dir_red+"CALIB/"+cal.upper()+"\n")
if make_fringe:
    f.write("rm -rfv "+dir_red+"CALIB/FRINGE"+"\n")
f.write("rm -rfv "+dir_red+"CALIB/calibRegistry*"+"\n")
f.write("export OMP_NUM_THREADS=1"+"\n")
f.write("\n")

# Making Bias data
f.write("constructBias.py "+dir_red+" --calib "+dir_red+"CALIB --rerun calib_bias --id field='BIAS' visit="+ \
	    vis_bias+" --batch-type=smp --cores=%d 2>&1 | tee log_bias" %(ncores)+"\n")
f.write("\n")
f.write("ingestCalibs.py "+dir_red+" --calib "+dir_red+"CALIB '"+dir_red+"rerun/calib_bias/BIAS/*/*/BIAS-*.fits' --validity=1000"+"\n")
f.write("\n")

# Making Dark data
f.write("constructDark.py "+dir_red+" --calib "+dir_red+"CALIB --rerun calib_dark --id field='DARK' visit="+ \
	    vis_dark+" --batch-type=smp --cores=%d 2>&1 | tee log_dark" %(ncores)+"\n")
f.write("\n")
f.write("ingestCalibs.py "+dir_red+" --calib "+dir_red+"CALIB '"+dir_red+"rerun/calib_dark/DARK/*/*/DARK-*.fits' --validity=1000"+"\n")
f.write("\n") 

# Making Flat data
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_flat = vis_flat_"+flt)
	f.write("\n")
	f.write("constructFlat.py "+dir_red+" --calib "+dir_red+"CALIB --rerun calib_flat --id visit="+ \
		    vis_flat+" --batch-type=smp --cores=%d 2>&1 | tee log_flat_" %(ncores)+flt+"\n")
f.write("\n")
f.write("ingestCalibs.py "+dir_red+" --calib "+dir_red+"CALIB '"+dir_red+"rerun/calib_flat/FLAT/*/*/FLAT-*.fits' --validity=1000"+"\n")
f.write("\n")

# Making Fringe data (now, y-band only)
if make_fringe:
	vis_fringe = vis_obj_Y
	flt = "Y"
	f.write("\n")
	f.write("constructFringe.py "+dir_red+" --calib "+dir_red+"CALIB --rerun calib_fringe --id visit="+ \
		    vis_fringe+" --batch-type=smp --cores=%d 2>&1 | tee log_fringe_" %(ncores)+flt+"\n")
	f.write("\n")
	f.write("ingestCalibs.py "+dir_red+" --calib "+dir_red+"CALIB '"+dir_red+"rerun/calib_fringe/FRINGE/*/*/FRINGE-*.fits' --validity=1000"+"\n")
	f.write("\n")

# Making Sky data
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_sky = vis_obj_"+flt)
	f.write("\n")
	f.write("constructSky.py "+dir_red+" --calib "+dir_red+"CALIB --rerun calib_sky --id visit="+ \
		    vis_sky+" --batch-type=smp --cores=%d 2>&1 | tee log_sky_" %(ncores)+flt+"\n")
f.write("\n")
f.write("ingestCalibs.py "+dir_red+" --calib "+dir_red+"CALIB '"+dir_red+"rerun/calib_sky/SKY/*/*/SKY-*.fits' --validity=1000"+"\n")
f.write("\n")	

f.write("cp -rpv "+dir_red+"CALIB/calibRegistry.sqlite3 "+dir_red+"CALIB/calibRegistry_preproc"+"\n")
f.write("rm -rfv "+dir_red+"CALIB/calibRegistry.sqlite3"+"\n")

f.close()


### A script for detrend
f = open(dir_scr+'scr_detrend', 'w')

f.write("rm -rfv "+dir_red+"CALIB/calibRegistry.sqlite3"+"\n")
f.write("cp -rpv "+dir_red+"CALIB/calibRegistry_preproc "+dir_red+"CALIB/calibRegistry.sqlite3"+"\n")
f.write("export OMP_NUM_THREADS=1"+"\n")
f.write("\n")

# Single-visit processing, detrending, and calibration
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_obj = vis_obj_"+flt)
	# f.write("singleFrameDriver.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id field='"+objfld+"' filter='"+filt[i]+"' visit="+ \
	#         vis_obj+" --batch-type=smp --cores=%d 2>&1 | tee log_obj_" %(ncores)+flt+"\n")
	f.write("singleFrameDriver.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id filter='"+filt[i]+"' visit="+ \
	        vis_obj+" --batch-type=smp --cores=%d 2>&1 | tee log_obj_" %(ncores)+flt+"\n")

f.close()


### A script for coadd
f = open(dir_scr+'scr_coadd','w')

f.write("export OMP_NUM_THREADS=1"+"\n")
f.write("\n")

# Define tract
vis_obj_tot = ''
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	if (i == np.arange(len(filt))[-1]):
		exec("vis_obj_tot += vis_obj_"+flt)
	else:
		exec("vis_obj_tot += vis_obj_"+flt+"+'^'")
if use_discrete:
	f.write("makeDiscreteSkyMap.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id visit="+vis_obj_tot+" 2>&1 | tee log_tract0"+"\n")
else:
	f.write("cp -rpv "+dir_red+"rerun/object/repositoryCfg.yaml "+dir_red+"rerun/object/old_repositoryCfg.yaml"+"\n")
	f.write("sed '3s/.*/_mapperArgs: {}/g' "+dir_red+"rerun/object/repositoryCfg.yaml > "+dir_red+"rerun/object/map_repositoryCfg.yaml"+"\n")
	f.write("sed -i '7s/.*/  _mapperArgs: {}/g' "+dir_red+"rerun/object/map_repositoryCfg.yaml"+"\n")
	f.write("cp -rpv "+dir_red+"rerun/object/map_repositoryCfg.yaml "+dir_red+"rerun/object/repositoryCfg.yaml"+"\n")
	f.write("\n")
	f.write("echo '"+'root.skyMap = "discrete"'+"' > overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].raList = [%.6f]' %(ra0_deg)+"' >> overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].decList = [%.6f]' %(dec0_deg)+"' >> overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].radiusList = [%.2f]' %(rad_deg)+"' >> overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].pixelScale = %.3f' %(pixscl)+"' >> overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].projection = "TAN"'+"' >> overrides.config"+"\n")
	f.write("echo '"+'root.skyMap["discrete"].tractOverlap = 0'+"' >> overrides.config"+"\n")
	f.write("\n")
	f.write("makeSkyMap.py "+dir_red+" --rerun object --configfile overrides.config 2>&1 | tee log_tract0"+"\n")
	f.write("cp -rpv "+dir_red+"rerun/object/old_repositoryCfg.yaml "+dir_red+"rerun/object/repositoryCfg.yaml"+"\n")
f.write("\n")

# Mosaicking
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_obj = vis_obj_"+flt)
	f.write("mosaic.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id filter='"+filt[i]+"' visit="+ \
		    vis_obj+" tract=0 ccd=0..103 --diagnostics --diagDir "+dir_red+"rerun/mosaic_diag 2>&1 | tee log_mosaic0_"+flt+"\n")	
f.write("\n")

# Applying the mosaic solution to each visit/CCD data
f.write("calibrateExposure.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id visit="+vis_obj_tot+ \
	    " tract=0 ccd=0..103 -j %d 2>&1 | tee log_calexp" %(ncores)+"\n")
f.write("calibrateCatalog.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id visit="+vis_obj_tot+ \
        " tract=0 ccd=0..103 --config doApplyCalib=True -j %d 2>&1 | tee log_calcat" %(ncores)+"\n")
f.write("\n")

# Writing a background model
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_obj = vis_obj_"+flt)
	f.write("skyCorrection.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id visit="+ \
            vis_obj+" --batch-type=smp --cores=%d 2>&1 | tee log_skycorr0_" %(ncores)+flt+"\n")
f.write("\n")

# Coadding images
for i in np.arange(len(filt)):
	flt = filt[i].split('HSC-')[1]
	exec("vis_obj = vis_obj_"+flt)
	f.write("coaddDriver.py "+dir_red+" --calib "+dir_red+"CALIB --rerun object --id filter='"+filt[i]+"' tract=0 --selectId visit="+ \
            vis_obj+" --batch-type=smp --cores=%d 2>&1 | tee log_coadd0_" %(ncores)+flt+"\n")

f.close()

