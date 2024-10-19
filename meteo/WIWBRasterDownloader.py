import argparse
import requests
import json
from datetime import datetime
import os
import sys
import time

class WIWBRasterDownloader:
    def __init__(self, credentials_path):
        print("Initializing WIWB Raster Downloader...")
        self.base_url = "https://wiwb.hydronet.com/api"
        self.auth_url = "https://login.hydronet.com/auth/realms/hydronet/protocol/openid-connect/token"
        self.client_id, self.client_secret = self.get_credentials(credentials_path)
        print("Credentials loaded successfully.")
        self.access_token = self.get_access_token()

    def get_credentials(self, path):
        print(f"Attempting to read credentials from: {path}")
        try:
            with open(path, 'r') as f:
                client_id = f.readline().strip()
                client_secret = f.readline().strip()
            if not client_id or not client_secret:
                raise ValueError("Client ID or Client Secret is missing in the credentials file")
            print("Credentials read successfully.")
            return client_id, client_secret
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found: {path}")
        except Exception as e:
            raise Exception(f"Error reading credentials: {str(e)}")

    def get_access_token(self):
        print("Requesting access token...")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.auth_url, data=data)
        response.raise_for_status()
        print("Access token obtained successfully.")
        return response.json()["access_token"]

    def download_rasters(self, data_source, variable, x_min, y_min, x_max, y_max, from_date, to_date, output_zip):
        print(f"Preparing to download rasters from {from_date} to {to_date}")
        url = f"{self.base_url}/grids/createdownload"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        
        request_body = {
            "Readers": [{
                "DataSourceCode": data_source,
                "Settings": {
                    "StartDate": from_date.strftime("%Y%m%d%H%M%S"),
                    "EndDate": to_date.strftime("%Y%m%d%H%M%S"),
                    "VariableCodes": [variable],
                    "Extent": {
                        "Xll": x_min,
                        "Yll": y_min,
                        "Xur": x_max,
                        "Yur": y_max,
                        "SpatialReference": {
                            "Epsg": 28992  # RD New (Amersfoort) projection
                        }
                    }
                }
            }],
            "Exporter": {
                "DataFormatCode": "geotiff"
            },
            "DataFlowTypeCode": "Download",
            "DataSourceCode": data_source
        }
        
        print("Sending download request...")
        response = requests.post(url, json=request_body, headers=headers)
        response.raise_for_status()
        data_flow_id = response.json().get("DataFlowId")
        print(f"Download request sent. Data flow ID: {data_flow_id}")
        
        print("Waiting for download to complete...")
        while True:
            status = self.check_download_status(data_flow_id)
            print(f"Current status: {status}")
            if status == "Finished":
                break
            elif status == "Failed":
                raise Exception("Download failed")
            time.sleep(10)  # Wait for 10 seconds before checking again

        print("Download process completed. Retrieving file...")
        download_url = f"{self.base_url}/grids/downloadfile?dataflowid={data_flow_id}"
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()

        print(f"Writing data to {output_zip}...")
        with open(output_zip, "wb") as f:
            f.write(response.content)

        print(f"Downloaded data saved to {output_zip}")

    def check_download_status(self, data_flow_id):
        url = f"{self.base_url}/entity/dataflows/get"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        request_body = {
            "DataFlowIds": [data_flow_id]
        }
        response = requests.post(url, json=request_body, headers=headers)
        response.raise_for_status()
        return response.json()["DataFlows"][str(data_flow_id)]["State"]

def main():
    parser = argparse.ArgumentParser(description="Download raster data from WIWB API")
    parser.add_argument("from_date", type=str, help="Start date (YYYYMMDD)")
    parser.add_argument("to_date", type=str, help="End date (YYYYMMDD)")
    parser.add_argument("x_min", type=float, help="Minimum X coordinate")
    parser.add_argument("y_min", type=float, help="Minimum Y coordinate")
    parser.add_argument("x_max", type=float, help="Maximum X coordinate")
    parser.add_argument("y_max", type=float, help="Maximum Y coordinate")
    parser.add_argument("results_zip", type=str, help="Output ZIP file name")
    parser.add_argument("--data_source", type=str, default="Knmi.Radar.Uncorrected", help="Data source code")
    parser.add_argument("--variable", type=str, default="P", help="Variable code")
    
    debug_path = r"c:\GITHUB\Meteobase\backend\licenses\credentials.txt"
    release_path = os.path.join(os.path.dirname(sys.executable), "licenses", "credentials.txt")
    release_path = debug_path

    default_path = debug_path if sys.flags.debug else release_path
    
    parser.add_argument("--credentials", type=str, default=default_path, help="Path to credentials file")
    
    args = parser.parse_args()

    try:
        print("Starting WIWB Raster Downloader...")
        downloader = WIWBRasterDownloader(args.credentials)

        from_date = datetime.strptime(args.from_date, "%Y%m%d")
        to_date = datetime.strptime(args.to_date, "%Y%m%d")

        print(f"Downloading data for date range: {from_date.date()} to {to_date.date()}")
        print(f"Coordinates: ({args.x_min}, {args.y_min}) to ({args.x_max}, {args.y_max})")
        print(f"Data source: {args.data_source}")
        print(f"Variable: {args.variable}")

        downloader.download_rasters(
            args.data_source,
            args.variable,
            args.x_min,
            args.y_min,
            args.x_max,
            args.y_max,
            from_date,
            to_date,
            args.results_zip
        )
        print("Download process completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()