import os
from osgeo import gdal, osr

gdal.UseExceptions()  # Enable exceptions

def reproject_geotiff(src_path, src_proj, dst_path, dst_proj):
    try:
        # Open the source file
        src_ds = gdal.Open(src_path)
        if src_ds is None:
            print(f"Error: Unable to open {src_path}")
            return

        # Create spatial reference objects for the source and target projections
        src_srs = osr.SpatialReference()
        if src_proj.startswith('EPSG:'):
            src_srs.ImportFromEPSG(int(src_proj.split(':')[1]))
        else:
            src_srs.ImportFromWkt(src_proj)
        
        dst_srs = osr.SpatialReference()
        dst_srs.ImportFromWkt(dst_proj)

        # Print source and destination projection information
        print("Source projection:")
        print(src_srs.ExportToPrettyWkt())
        print("\nDestination projection:")
        print(dst_srs.ExportToPrettyWkt())

        # Perform the reprojection using gdal.Warp
        gdal.Warp(dst_path, src_ds, srcSRS=src_srs, dstSRS=dst_srs, resampleAlg=gdal.GRA_Bilinear)

        print(f"Reprojection complete. Output saved to {dst_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("GDAL error messages:")
        for i in range(gdal.GetLastErrorNo()):
            print(gdal.GetLastErrorMsg())

# User input
src_path = r'c:\SYNC\PROJECTEN\H3140.RWANDA\02.Steps\01a.NewDTMAssessment\ALL 4 WETLANDS.tif'
dst_path = r'c:\SYNC\PROJECTEN\H3140.RWANDA\02.Steps\01a.NewDTMAssessment\ALL 4 WETLANDS_model.tif'

# Destination projection
dst_proj = 'PROJCRS["ITRF_2005",BASEGEOGCRS["ITRF2005",DATUM["International Terrestrial Reference Frame 2005",ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1]],ID["EPSG",6896]],PRIMEM["Greenwich",0,ANGLEUNIT["Degree",0.0174532925199433]]],CONVERSION["unnamed",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["Degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",30,ANGLEUNIT["Degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9999,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",5000000,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1,ID["EPSG",9001]]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1,ID["EPSG",9001]]]]'

# Source projection
src_proj = 'EPSG:8998'

# Call the function
reproject_geotiff(src_path, src_proj, dst_path, dst_proj)