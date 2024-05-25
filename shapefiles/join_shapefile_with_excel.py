#pip install geopandas pandas openpyxl
import geopandas as gpd
import pandas as pd

#this script performs a join-by-ID between a shapefile and an Excel worksheet. 
#It creates a new field to the shapefile for each column in the worksheet and writes the values when matching ID is found
#Prerequisites: a shapefile with a given fieldname for the feature's ID, an Excel workbook with a given worksheet name and column name for the feature's ID.

def join_shapefile_with_excel(shapefile_path, shapefile_id_field, excel_path, excel_sheet_name, excel_id_field):
    # Load the shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Load the Excel file
    df = pd.read_excel(excel_path, sheet_name=excel_sheet_name)
    
    # Ensure the ID fields are of the same data type
    gdf[shapefile_id_field] = gdf[shapefile_id_field].astype(str)
    df[excel_id_field] = df[excel_id_field].astype(str)
    
    # Merge the data on the ID fields
    merged_gdf = gdf.merge(df, left_on=shapefile_id_field, right_on=excel_id_field, how='left')
    
    # Save the updated shapefile
    output_path = shapefile_path.replace('.shp', '_updated.shp')
    merged_gdf.to_file(output_path)

    print(f"Updated shapefile is saved as '{output_path}'")

if __name__ == "__main__":

    shapefile_path = r"c:\SYNC\SOFTWARE\CHANNEL BUILDER\TESTBANK\12.Leijgraaf\Input\Duikers.shp"
    shapefile_id_field = "ID        "
    excel_path = r"c:\GITHUB\modelleren_oppervlaktewater\06 Leijgraaf\Student\FASE1.MODELBOUW\SobekData.xlsx"
    excel_sheet_name = "Duikers"
    excel_id_field = "ID"
    
    # User inputs
    #shapefile_path = input("Enter the path to the shapefile: ")
    #shapefile_id_field = input("Enter the name of the field in the shapefile containing the IDs: ")
    #excel_path = input("Enter the path to the Excel file: ")
    #excel_sheet_name = input("Enter the name of the worksheet in the Excel file: ")
    #excel_id_field = input("Enter the name of the column in the Excel worksheet containing the IDs: ")
    
    # Execute the function
    join_shapefile_with_excel(shapefile_path, shapefile_id_field, excel_path, excel_sheet_name, excel_id_field)
