import rasterio
import geopandas as gpd
import numpy as np
from rasterio.features import geometry_mask
from shapely.geometry import Point, LineString

# Replace with your file paths
elevation_tiff = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\01.GIS\\UK_ND_Lidar_2022_DTM_20221230_05_interpolated.tif'
channel_shapefile = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\03.ChannelBuilder\\input\\Rivers_subselection_refined.shp'
output_tiff = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\03.ChannelBuilder\\output\\excavated_elevation.tif'

# Read GeoTIFF and polyline shapefile
with rasterio.open(elevation_tiff) as elevation_src:
    elevation = elevation_src.read(1)
    elevation_transform = elevation_src.transform

channels = gpd.read_file(channel_shapefile)

# Define a function to interpolate trapezium properties at a specific point
def interpolate_properties(dist, channel):
    bed_level = channel['BEDLEVELUP'] + dist * (channel['BEDLEVELDN'] - channel['BEDLEVELUP'])
    bed_width = channel['BEDWIDTHUP'] + dist * (channel['BEDWIDTHDN'] - channel['BEDWIDTHUP'])
    slope = channel['SLOPEUP'] + dist * (channel['SLOPEDN'] - channel['SLOPEUP'])
    return bed_level, bed_width, slope

def nearest_channel_segment(point, linestring):
    min_dist = float('inf')
    nearest_segment = None
    nearest_fraction = None

    for i in range(len(linestring.coords) - 1):
        segment = LineString([linestring.coords[i], linestring.coords[i + 1]])
        dist = point.distance(segment)
        if dist < min_dist:
            min_dist = dist
            nearest_segment = segment
            nearest_fraction = segment.project(point) / segment.length

    return nearest_segment, nearest_fraction

# Excavate the elevation grid
for _, channel in channels.iterrows():
    linestring = channel['geometry']
    max_buf_distance = channel['BEDWIDTHUP'] / 2 + 5 * channel['SLOPEUP']
    buffer = linestring.buffer(max_buf_distance)

    # Convert the buffer to a mask
    mask = geometry_mask([buffer], transform=elevation_transform, out_shape=elevation.shape, invert=True)

    # Iterate through the grid cells within the buffered area
    for row, col in np.argwhere(mask):
        x, y = elevation_src.xy(row, col)
        point = Point(x, y)

        # Get the nearest channel segment and the distance along it
        nearest_segment, nearest_fraction = nearest_channel_segment(point, linestring)

        # Interpolate the trapezium properties at the nearest point on the channel
        dist = nearest_segment.length * nearest_fraction
        bed_level, bed_width, slope = interpolate_properties(dist, channel)

        # Calculate the perpendicular distance from the point to the channel
        perp_dist = point.distance(nearest_segment)

        # Excavate the grid cell if it is within the trapezium area
        if perp_dist <= bed_width / 2:
            horizontal_dist = bed_width / 2 - perp_dist
            vertical_dist = horizontal_dist / slope
            depth = min(vertical_dist, 5)  # Limit depth to 5 m

            new_elevation = bed_level - depth
            if new_elevation < elevation[row, col]:
                elevation[row, col] = new_elevation

# Save the modified elevation grid to a new GeoTIFF file
with rasterio.open(
    output_tiff,
    'w',
    driver='GTiff',
    height=elevation_src.height,
    width=elevation_src.width,
    count=1,
    dtype=elevation_src.dtypes[0],
    crs=elevation_src.crs,
    transform=elevation_transform,
) as dst:
    dst.write(elevation, 1)
