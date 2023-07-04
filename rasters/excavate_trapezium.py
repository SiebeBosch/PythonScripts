import rasterio
import geopandas as gpd
import numpy as np
from rasterio.features import geometry_mask
from shapely.geometry import Point, LineString, box
from rtree import index

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
        print(f"Segment: {segment}, Distance: {dist}, Min Distance: {min_dist}")

    return nearest_segment, nearest_fraction


elevation_tiff = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\01.GIS\\UK_ND_Lidar_2022_DTM_20221230_05_interpolated.tif'
channel_shapefile = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\03.ChannelBuilder\\input\\Rivers_subselection_refined.shp'
output_tiff = 'C:\\SYNC\\PROJECTEN\\H3115.SIBELCO.Pilots\\02.Devon\\01.GIS\\UK_ND_Lidar_2022_DTM_20221230_05_interpolated_excavated.tif'
maxdepth = 3

with rasterio.open(elevation_tiff) as elevation_src:
    elevation = elevation_src.read(1)
    elevation_transform = elevation_src.transform

channels = gpd.read_file(channel_shapefile)

idx = index.Index()

mask = np.zeros(elevation.shape, dtype=bool)
for _, channel in channels.iterrows():
    linestring = channel['geometry']
    max_buf_distance = channel['BEDWIDTHUP'] / 2 + maxdepth * channel['SLOPEUP']
    buffer = linestring.buffer(max_buf_distance)
    masked = geometry_mask([buffer], transform=elevation_transform, out_shape=elevation.shape, invert=True)
    mask |= masked

    cell_id = 0
    for row, col in np.argwhere(masked):
        x, y = elevation_src.xy(row, col)
        idx.insert(cell_id, (x, y, x, y), (row, col))
        cell_id += 1

total_channels = len(channels)

for channel_idx, (_, channel) in enumerate(channels.iterrows(), start=1):
    print(f"Processing channel {channel_idx} of {total_channels}")

    linestring = channel['geometry']
    max_buf_distance = channel['BEDWIDTHUP'] / 2 + maxdepth * channel['SLOPEUP']
    buffer = linestring.buffer(max_buf_distance)
    bounds = buffer.bounds

    for item in idx.intersection(bounds, objects=True):
        x_min, y_min, x_max, y_max = item.bbox
        row, col = item.object
        x, y = elevation_src.xy(row, col)
        point = Point(x, y)
        
        # Rest of the code

        nearest_segment, nearest_fraction = nearest_channel_segment(point, linestring)
        bed_level_up = channel['BEDLEVELUP']
        bed_level_dn = channel['BEDLEVELDN']
        bed_width_up = channel['BEDWIDTHUP']
        bed_width_dn = channel['BEDWIDTHDN']
        slope_up = channel['SLOPEUP']
        slope_dn = channel['SLOPEDN']


        bed_level = bed_level_up + nearest_fraction * (bed_level_dn - bed_level_up)
        bed_width = bed_width_up + nearest_fraction * (bed_width_dn - bed_width_up)
       
        slope = slope_up + nearest_fraction * (slope_dn - slope_up)

        dist_from_channel = point.distance(nearest_segment)

        if dist_from_channel <= bed_width / 2:
            z_min = bed_level - dist_from_channel / slope
            z_max = bed_level + dist_from_channel / slope
            z = elevation[row, col]

            if z_min <= z <= z_max:
                elevation[row, col] = max(z_min, z - maxdepth)
    break

# Save the modified elevation grid to a new GeoTIFF

with rasterio.open(
    output_tiff,
    'w',
    driver='GTiff',
    height=elevation.shape[0],
    width=elevation.shape[1],
    count=1,
    dtype=elevation.dtype,
    crs=elevation_src.crs,
    transform=elevation_transform,
) as dst:
    dst.write(elevation, 1)
