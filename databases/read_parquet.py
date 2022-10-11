# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 22:17:34 2022

@author: SiebeBosch

inspiration: https://arrow.apache.org/docs/python/parquet.html

"""



import pyarrow.parquet as pq

import numpy as np
import pandas as pd
import pyarrow as pa

df = pd.DataFrame({'one': [-1, np.nan, 2.5],
                   'two': ['foo', 'bar', 'baz'],
                   'three': [True, False, True]},
                   index=list('abc'))

table = pa.Table.from_pandas(df)

pq.write_table(table, 'example.parquet')


prqfile = r"c:\SYNC\PROJECTEN\H3114.WaterkwaliteitKrachtkaart.Rijnland\01.Data\00.Zicht\Zicht\ET_Dim_Monster\2022\10\6\19\26\DAF899A6-F26E-418D-A6A8-0DC83296A2BC_8150_0-1.parquet"
prqfile = r"c:\SYNC\PROJECTEN\H3114.WaterkwaliteitKrachtkaart.Rijnland\01.Data\00.Zicht\Zicht\ET_Fact_HHR_Waterkwaliteit\2022\10\6\19\30\71D8C4D0-9008-4B68-988B-CF3C2E536BE2_8654_12-1.parquet"

csvfile = r"c:\SYNC\PROJECTEN\H3114.WaterkwaliteitKrachtkaart.Rijnland\01.Data\00.Zicht\Exports\test.csv"


table2 = pq.read_table(prqfile)

mytable = table2.to_pandas()
mytable.to_csv(csvfile)

"""
srcfile = r"c:\SYNC\PROJECTEN\H3111.Brede.Watersysteemevaluatie.Geleenbeek\07.Resultaten\Scenario's\Geactualiseerd8\mr3_iter3_T25\dm1maxh0.asc"
dstfile = r"c:\SYNC\PROJECTEN\H3111.Brede.Watersysteemevaluatie.Geleenbeek\07.Resultaten\Scenario's\Geactualiseerd8\mr3_iter3_T25\dm1maxh0_gapfill.tif"

with rasterio.open(srcfile) as src:
    profile = src.profile
    arr = src.read(1)
    arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=10, smoothing_iterations=0)

with rasterio.open(dstfile, 'w', **profile) as dest:
    dest.write_band(1, arr_filled)
"""    
    