# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 22:17:34 2022

@author: SiebeBosch
"""

import rasterio
from rasterio.fill import fillnodata

srcfile = r"c:\SYNC\PROJECTEN\H3111.Brede.Watersysteemevaluatie.Geleenbeek\07.Resultaten\Scenario's\Geactualiseerd8\mr3_iter3_T25\dm1maxh0.asc"
dstfile = r"c:\SYNC\PROJECTEN\H3111.Brede.Watersysteemevaluatie.Geleenbeek\07.Resultaten\Scenario's\Geactualiseerd8\mr3_iter3_T25\dm1maxh0_gapfill.tif"

with rasterio.open(srcfile) as src:
    profile = src.profile
    arr = src.read(1)
    arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=10, smoothing_iterations=0)

with rasterio.open(dstfile, 'w', **profile) as dest:
    dest.write_band(1, arr_filled)
    
    