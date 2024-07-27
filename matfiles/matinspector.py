import scipy.io
import numpy as np
import pandas as pd

def inspect_mat_file(file_path):
    # Load the .mat file
    mat_contents = scipy.io.loadmat(file_path)

    # Iterate through each variable in the file
    for key, value in mat_contents.items():
        # Skip metadata variables (those starting with '__')
        if key.startswith('__'):
            continue
        
        print(f"\nDataset: {key}")
        
        # Check if it's a numpy array (most common case)
        if isinstance(value, np.ndarray):
            print(f"Type: Numpy Array")
            print(f"Shape: {value.shape}")
            
            # For 2D arrays, treat as tabular data
            if len(value.shape) == 2:
                df = pd.DataFrame(value)
                print(f"Number of rows: {df.shape[0]}")
                print(f"Number of columns: {df.shape[1]}")
                print("\nSample (first 5 rows, first 5 columns):")
                print(df.iloc[:5, :5])
            
            # For 1D arrays, just show the first few elements
            elif len(value.shape) == 1:
                print("Sample (first 5 elements):")
                print(value[:5])
            
            # For higher dimensional arrays, show shape and first few elements
            else:
                print("Sample (first few elements):")
                print(value.flatten()[:5])
        
        # Handle other types (e.g., lists, dictionaries)
        else:
            print(f"Type: {type(value)}")
            print("Sample:")
            print(value)

# Usage
file_path = r'c:\SYNC\PROJECTEN\H3116.AAenMaas.Stochasten\90.Gevoeligheidsanalyse.DenBosch\Stap0.Input_analyse\BAOUT0-800jr-1uur.mat'
inspect_mat_file(file_path)