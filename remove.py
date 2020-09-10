#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:21:10 2019

@author: jlee
"""

import numpy as np
import glob, os

dir_rerun = '/data/jlee/HSCv6/A2199/1/Red/rerun/'


# --------------------------------------------- #
# ----- Directories (rerun : calibration) ----- #
# --------------------------------------------- #
direc = [dir_rerun+'calib_bias/',
         dir_rerun+'calib_dark/',
         dir_rerun+'calib_flat/',
         dir_rerun+'calib_sky/']

# ----- Removing & writing removing log files ----- #
current_dir = os.getcwd()    # dwarf:/data/jlee/HSCv6/M81/Bell
for k in np.arange(len(direc)):
    print('# ----- Working on '+direc[k]+' ----- #'+'\n')
    os.chdir(direc[k])
    os.system('rm -rfv * > rmlog.txt')
os.chdir(current_dir)


# ---------------------------------------- #
# ----- Directories (rerun : object) ----- #
# ---------------------------------------- #
dir_obj = dir_rerun+'object/'
os.chdir(dir_obj)
sub_dir = sorted(glob.glob('*'))
direc = []
for k in sub_dir:
    try:
        test_integer = int(k)
        direc.append(dir_obj+k+'/')
    except ValueError:
        if (k == 'deepCoadd'):
            direc.append(dir_obj+k+'/')
        else:
            continue

# ----- Removing & writing removing log files ----- #
current_dir = os.getcwd()    # dwarf:/data/jlee/HSCv6/M81/Bell
for k in np.arange(len(direc)):
    print('# ----- Working on '+direc[k]+' ----- #'+'\n')
    os.chdir(direc[k])
    os.system('rm -rfv * > rmlog.txt')
os.chdir(current_dir)
