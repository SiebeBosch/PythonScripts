import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import glob
import os

def read_ascii_grid(file_path):
    with open(file_path, 'r') as file:
        header = {}
        for _ in range(6):
            line = file.readline().strip().split()
            header[line[0]] = float(line[1])
        data = np.loadtxt(file)
    return header, data

def write_ascii_grid(file_path, header, data):
    with open(file_path, 'w') as file:
        for key, value in header.items():
            file.write(f"{key} {value}\n")
        np.savetxt(file, data, fmt='%.10f')

def read_excel_daily_precipitation(file_path):
    df = pd.read_excel(file_path, sheet_name='Basis.Neerslag.Etmaal', header=6)
    stations = {}
    for col in range(1, len(df.columns), 4):
        if col+2 < len(df.columns):  # Ensure columns are within bounds
            station_name = df.columns[col]
            x_coord = df.iloc[4, col+1]  # X coordinate in row 5
            y_coord = df.iloc[4, col+2]  # Y coordinate in row 5
            data = df.iloc[6:, [0, col]].dropna()  # Data starts in row 7
            stations[station_name] = {
                'X': x_coord,
                'Y': y_coord,
                'data': data
            }

    print(stations)
    return stations

def calculate_daily_sums(hourly_files):
    daily_sums = {}
    for date, files in hourly_files.items():
        daily_data = None
        for file in files:
            header, data = read_ascii_grid(file)
            if daily_data is None:
                daily_data = np.zeros_like(data)
            daily_data += data
        daily_sums[date] = (header, daily_data)
    return daily_sums

def spatial_interpolation(stations, grid_x, grid_y):
    points = []
    values = []
    for station, info in stations.items():
        x = info['X']
        y = info['Y']
        data = info['data'].set_index(0)
        for date, value in data.iterrows():
            points.append((x, y))
            values.append(value[1])
    interpolated = griddata(points, values, (grid_x, grid_y), method='cubic')
    return interpolated

def apply_multipliers(daily_sums, interpolated_sums):
    multipliers = {}
    for date, (header, daily_grid) in daily_sums.items():
        interpolated_grid = interpolated_sums[date]
        multiplier_grid = interpolated_grid / daily_grid
        multiplier_grid[np.isnan(multiplier_grid)] = 1
        multipliers[date] = multiplier_grid
    return multipliers

def adjust_hourly_grids(hourly_files, multipliers):
    for date, files in hourly_files.items():
        for file in files:
            header, data = read_ascii_grid(file)
            adjusted_data = data * multipliers[date]
            write_ascii_grid(file.replace('.ASC', '_adjusted.ASC'), header, adjusted_data)

def main():
    # Specify the folder containing the precipitation grids
    grids_folder = r'c:\SYNC\PROJECTEN\H3118.HenA.Begeleiding\05.Analyse\Meteobase\RASTER'

    # Initialize the dictionary to store hourly files
    hourly_files = {}

    # Use glob to find all relevant ASCII grid files in the specified folder
    for file in glob.glob(os.path.join(grids_folder, 'NSL_*.ASC')):
        date = file[4:12]
        if date not in hourly_files:
            hourly_files[date] = []
        hourly_files[date].append(file)

    daily_sums = calculate_daily_sums(hourly_files)
    
    stations = read_excel_daily_precipitation(r'c:\SYNC\PROJECTEN\H3118.HenA.Begeleiding\05.Analyse\Meteobase\Bestelling_5239_5898_etmaalstations.xlsx')
    
    # Ensure header is available by reading one of the hourly files
    sample_header, _ = read_ascii_grid(next(iter(hourly_files.values()))[0])
    
    grid_x, grid_y = np.meshgrid(
        np.arange(sample_header['xllcorner'], sample_header['xllcorner'] + sample_header['ncols'] * sample_header['cellsize'], sample_header['cellsize']),
        np.arange(sample_header['yllcorner'], sample_header['yllcorner'] + sample_header['nrows'] * sample_header['cellsize'], sample_header['cellsize'])
    )
    
    interpolated_sums = {}
    for date in daily_sums.keys():
        interpolated_sums[date] = spatial_interpolation(stations, grid_x, grid_y)
    
    multipliers = apply_multipliers(daily_sums, interpolated_sums)
    
    adjust_hourly_grids(hourly_files, multipliers)

if __name__ == "__main__":
    main()
