import os
import fiona

# get the absolute path of the directory of the script
dir_path = os.path.dirname(os.path.realpath(__file__))

# relative path to your geopackage
relative_path = "../data/HyDAMO_2_2_BAF_met_wasmachine.gpkg"

# create absolute path
abs_file_path = os.path.join(dir_path, relative_path)

# Path to new geopackage, based on the original name
new_path = os.path.join(dir_path, "../data/HyDAMO_2_2_BAF_met_wasmachine_modified.gpkg")

# Layer to remove
layer_to_remove = "layer_name"

# Iterate over layers in the geopackage
with fiona.Env():
    with fiona.open(abs_file_path) as src:
        layers = src.listlayers()
        for layer in layers:
            if layer != layer_to_remove:
                # Copy layers except the one to remove to the new geopackage
                with fiona.open(new_path, 'a', layer=layer, schema=src.schema, driver='GPKG', crs=src.crs) as dst:
                    records = [r for r in src if src.name == layer]
                    dst.writerecords(records)
