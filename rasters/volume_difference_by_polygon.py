import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
from shapely.geometry import mapping
from rasterio.crs import CRS

def read_asc_grid(filepath, crs):
    with rasterio.open(filepath) as src:
        data = src.read(1)
        transform = src.transform
        nodata = src.nodata
        src_crs = crs  # Set the CRS directly to EPSG:28992
    return data, transform, nodata, src_crs, filepath

def calculate_volume_difference(grid1_path, grid2_path, transform, nodata1, nodata2, polygon):
    with rasterio.open(grid1_path) as src1, rasterio.open(grid2_path) as src2:
        # Mask the grids with the polygon
        out_image1, _ = mask(src1, [mapping(polygon)], crop=True)
        out_image2, _ = mask(src2, [mapping(polygon)], crop=True)
    
    # Identify nodata cells
    nodata_mask = (out_image1 == nodata1) | (out_image2 == nodata2)
    
    # Calculate the cell size (area of one cell)
    cell_size = transform[0] * abs(transform[4])  # pixel width * pixel height
    
    # Calculate the volume difference, ignoring nodata cells
    valid_diff = np.where(nodata_mask, 0, out_image2 - out_image1)
    volume_difference = valid_diff.sum() * cell_size
    return volume_difference

def main():
    # EPSG code for the projection
    epsg_code = 28992
    crs = CRS.from_epsg(epsg_code)

    # File paths
    grid1_path = r"c:\SYNC\PROJECTEN\H1298.CorioGlanaHL1617\09.Bergingsvarianten2\BUI2 aanp 2Dgrid2, CG HL16_17, T100 geactualiseerd ONTW+2 ty10 v2 latQt\dm1maxh0.asc"
    #grid2_path = r"c:\SYNC\PROJECTEN\H1298.CorioGlanaHL1617\09.Bergingsvarianten2\BUI2 aanp 2Dgrid2, CG HL16_17, T100 geactualiseerd ONTW+2 ty10 v2 VarAa@38 latQt\dm1maxh0.asc"
    #grid2_path = r"c:\SYNC\PROJECTEN\H1298.CorioGlanaHL1617\09.Bergingsvarianten2\BUI2 aanp 2Dgrid2, CG HL16_17, T100 geactualiseerd ONTW+2 ty10 v2 VarAa@40 latQt\dm1maxh0.asc"
    grid2_path = r"c:\SYNC\PROJECTEN\H1298.CorioGlanaHL1617\09.Bergingsvarianten2\BUI2 aanp 2Dgrid2, CG HL16_17, T100 geactualiseerd ONTW+2 ty10 v2 VarAa@35 latQt\dm1maxh0.asc"
    shapefile_path = r"c:\SYNC\PROJECTEN\H1298.CorioGlanaHL1617\09.Bergingsvarianten2\MaxBerging.shp"

    # Read the ASC grids
    grid1, transform1, nodata1, crs1, grid1_filepath = read_asc_grid(grid1_path, crs)
    grid2, transform2, nodata2, crs2, grid2_filepath = read_asc_grid(grid2_path, crs)
    
    if transform1 != transform2:
        raise ValueError("The two grids must have the same transform properties")
    
    if crs1 != crs2:
        raise ValueError("The two grids must have the same CRS")

    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Ensure the shapefile CRS matches the desired CRS
    if gdf.crs != crs:
        gdf = gdf.to_crs(crs)

    # Calculate volume differences for each polygon
    volume_differences = []
    for polygon in gdf.geometry:
        volume_diff = calculate_volume_difference(grid1_filepath, grid2_filepath, transform1, nodata1, nodata2, polygon)
        volume_differences.append(volume_diff)
    
    # Add the volume differences to a new column in the GeoDataFrame
    gdf['Aa35'] = volume_differences
    
    # Save the updated shapefile to a new file first to verify changes
    #new_shapefile_path = shapefile_path.replace(".shp", "_updated.shp")
    # just update the existing shapefile
    gdf.to_file(shapefile_path)
    
    # After verifying the new file, you can overwrite the original file if needed
    # gdf.to_file(shapefile_path)

if __name__ == "__main__":
    main()
