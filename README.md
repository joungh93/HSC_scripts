# hscPipe6_scripts
(updated on 2020. 12. 28.)


## Description
Simple Python codes to automatically write the shell scripts for running [hscPipe6](https://hsc.mtk.nao.ac.jp/pipedoc/pipedoc_6_e/index.html)

* ``mkscr_hsc_server.py`` - when you run hscPipe6 in a single server
* ``mkscr_hsc_cluster.py`` - when you run hscPipe6 in a cluster with multiple nodes
* ``remove.py`` - when you want to remove the intermediate files after running the final step of hscPipe6


## Prerequisites
* The hscPipe6 pipeline should be installed. ([Reference link](https://hsc.mtk.nao.ac.jp/pipedoc/pipedoc_6_e/install_env_e/install.html))
* The following Python modules should be installed.
  * ``numpy >= 1.18.1``
  * ``pandas >= 1.0.1``
  * ``sqlite3`` ([Reference link](https://docs.python.org/3/library/sqlite3.html))
* You have to retrieve raw data of [Subaru/Hyper Suprime-Cam (HSC)](https://www.subarutelescope.org/Observing/Instruments/HSC/index.html) from [the SMOKA archive](https://smoka.nao.ac.jp/).

 
## Workflows
* __Making working directories__
  * Set the paths as below (bash shell):  
    ``export RAW = /your_main_working_directory/Raw``  
    ``export RED = /your_main_working_directory/Red``  
    ``export SCR = /your_main_working_directory/job``  

```
cd /your_main_working_directory/
mkdir $RAW
mkdir $RED
mkdir $SCR
```


* __Activating the pipeline environment__

```
setup-hscpipe
echo 'lsst.obs.hsc.HscMapper' > $RED/_mapper
```


* __Setting the Brighter-Fatter kernel__

```
mkdir $RED/CALIB
mkdir $RED/CALIB/BFKERNEL
cd $RED/CALIB/BFKERNEL
ln -s /hscpipe_installed_directory/hscpipe/6.7/lsst_home/stack/miniconda3-4.3.21-10a4fa6/Linux64/obs_subaru/6.7-hsc+1/hsc/brighter_fatter_kernel.pkl
```


* __Creating links to reference catalog for astrometry__

```
mkdir $RED/ref_cats
cd $RED/ref_cats
ln -s /your_data_path/astrometry_data/ps1_pv3_3pi_20170110
```


* __Setting up the transmission curve data for HSC filters & an SQL registry for raw data__

```
installTransmissionCurves.py $RED
ingestImages.py $RED $RAW/*.fits --mode=link --create
```


* __Checking all the materials with SQL scripts__  
If you want to check if raw data is categorized well, you can simply use the following SQL scripts.

```
cd $RED
sqlite3 registry.sqlite3
.header on
.table
.schema

SELECT visit,filter,field,taiObs,expId,expTime,count(visit) FROM raw WHERE field='BIAS' GROUP BY visit,field;
SELECT visit,filter,field,taiObs,expId,expTime,count(visit) FROM raw WHERE field='DARK' GROUP BY visit,field;
SELECT visit,filter,field,taiObs,expId,expTime,count(visit) FROM raw WHERE field='DOMEFLAT' GROUP BY visit,field;
SELECT visit,filter,field,taiObs,expId,expTime,count(visit) FROM raw WHERE field='YOUR_OBJECT_FIELD_NAME' AND filter='HSC-G' GROUP BY visit,field;

.q
```


* __Running the Python code for writting hscPipe6 scripts__  
Before running the Python codes, you should revise several lines in the codes (marked by ``Need to be manually revised!``) depending on your data and machine environment.

In a single server,
```
ipython
run mkscr_hsc_server.py
sh scr_preproc
sh scr_detrend
sh scr_coadd
```

In a cluster with multiple nodes,
```
ipython
run mkscr_hsc_cluster.py
qsub job_preproc
qsub job_detrend
qsub job_coadd
```


* __Removing the intermediate files__  
After finishing the final step of hscPipe6 (coadding process), you should check if the images are well created. If so, it would be better to remove the intermediate files created by the pipeline for saving the space. You should revise the first line in ``remove.py`` (marked by ``Need to be manually revised!``) depending your working path.
```
ipython
run remove.py
```


## Changelog
* 2020/09/10
  * Current version is only applicable to _**one HSC field with a single field name**_.
* 2020/12/28
  * _**Multiple HSC field data with different field names**_ is now able to be used by the updated codes.
  * Calculating average exposure time of the HSC data is also available.
* :snail:

