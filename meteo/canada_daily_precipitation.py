import requests
import os
import csv
from datetime import datetime, timedelta
import pandas as pd

# Station ID to name mapping
STATION_MAP = {
    44163: "Grassy_Narrows",
    #3965: "Minaki",
    # Add more stations here as needed
}

def download_data(station_id, year, month):
    station_name = STATION_MAP.get(station_id, f"Unknown_{station_id}")
    url = f"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={year}&Month={month}&Day=1&time=&timeframe=2&submit=Download+Data"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            if "Date/Time" in response.text:
                filename = f"temp_{year}_{month:02d}_{station_name}.csv"
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {filename}")
                return filename
            else:
                print(f"No data available for {station_name} (ID: {station_id}), {year}-{month:02d}")
        else:
            print(f"Failed to download data for {station_name} (ID: {station_id}), {year}-{month:02d}. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data for {station_name} (ID: {station_id}), {year}-{month:02d}: {e}")
    
    return None

def combine_csv_files(files, output_file):
    combined_data = []
    headers = None
    data_set = set()  # To keep track of unique rows

    for file in files:
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            current_headers = next(reader)
            
            if headers is None:
                headers = current_headers
                combined_data.append(headers)
            
            for row in reader:
                row_tuple = tuple(row)
                if row_tuple not in data_set:
                    data_set.add(row_tuple)
                    combined_data.append(row)
        
        os.remove(file)  # Remove the temporary file after combining

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(combined_data)

    print(f"Combined data saved to {output_file}")

def main():
    # Configure these variables as needed
    station_ids = list(STATION_MAP.keys())
    start_date = datetime(2009, 1, 1)
    end_date = datetime(2009, 4, 1)
    
    for station_id in station_ids:
        station_files = []
        current_date = start_date
        while current_date <= end_date:
            file = download_data(station_id, current_date.year, current_date.month)
            if file:
                station_files.append(file)
            
            # Move to the next month
            current_date += timedelta(days=32)
            current_date = current_date.replace(day=1)
        
        if station_files:
            station_name = STATION_MAP.get(station_id, f"Unknown_{station_id}")
            output_file = f"{station_name}_combined_data.csv"
            combine_csv_files(station_files, output_file)

if __name__ == "__main__":
    main()