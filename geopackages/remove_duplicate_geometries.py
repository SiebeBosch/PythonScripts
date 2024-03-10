import geopandas as gpd

# Step 1: Load the GeoPackage
gdf = gpd.read_file(r'c:\GITHUB\klimaatatlas\GIS\Watervlakken_Plus6.gpkg', layer='Watervlakken_Plus6')

# Step 2: Identify and Remove Duplicate Geometries
# This example removes rows with exactly the same geometry
gdf = gdf.drop_duplicates(subset='geometry')

# If you also want to consider attribute data in identifying duplicates, you can omit the subset parameter
# gdf = gdf.drop_duplicates()

# Step 3: Save the Cleaned Data
gdf.to_file(r'c:\GITHUB\klimaatatlas\GIS\Watervlakken_Plus7.gpkg', layer='Watervlakken_Plus7', driver='GPKG')
