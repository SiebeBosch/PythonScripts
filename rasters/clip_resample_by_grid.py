import rasterio
from rasterio.windows import from_bounds
import numpy as np

def clip_and_resample(input_tiff, reference_asc, output_tiff):
    # Read the reference ASC file
    with rasterio.open(reference_asc) as ref:
        ref_profile = ref.profile
        ref_bounds = ref.bounds
        ref_transform = ref.transform
    
    # Read the input GeoTIFF
    with rasterio.open(input_tiff) as src:
        # Get the window of the input that matches the reference bounds
        window = from_bounds(*ref_bounds, src.transform)
        
        # Read the data from the window
        data = src.read(1, window=window)
        
        # Resample the data to match the reference resolution
        new_shape = (ref_profile['height'], ref_profile['width'])
        resampled_data = np.resize(data, new_shape)
        
        # Update the profile for the output file
        dst_profile = src.profile.copy()
        dst_profile.update({
            'transform': ref_transform,
            'width': ref_profile['width'],
            'height': ref_profile['height']
        })
        
        # Create the output file
        with rasterio.open(output_tiff, 'w', **dst_profile) as dst:
            dst.write(resampled_data, 1)

# Example usage
input_tiff = r'c:\\SYNC\\PROJECTEN\\H3140.RWANDA\\02.Steps\\01a.NewDTMAssessment\\ALL 4 WETLANDS.tif'
reference_asc = r'c:\\SYNC\\PROJECTEN\\H3140.RWANDA\\02.Steps\\01a.NewDTMAssessment\\lidar_dem_10m_corrected.asc'
output_tiff = r'c:\\SYNC\\PROJECTEN\\H3140.RWANDA\\02.Steps\\01a.NewDTMAssessment\\ALL 4 WETLANDS_Model.tif'

crs = 'PROJCRS["ITRF_2005",BASEGEOGCRS["ITRF2005",DATUM["International Terrestrial Reference Frame 2005",ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1]],ID["EPSG",6896]],PRIMEM["Greenwich",0,ANGLEUNIT["Degree",0.0174532925199433]]],CONVERSION["unnamed",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["Degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",30,ANGLEUNIT["Degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9999,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",5000000,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1,ID["EPSG",9001]]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1,ID["EPSG",9001]]]]'

clip_and_resample(input_tiff, reference_asc, output_tiff, crs)
