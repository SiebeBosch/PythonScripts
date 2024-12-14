from PIL import Image
import pillow_heif
import os

# Register HEIF opener
pillow_heif.register_heif_opener()

def convert_heic_files_in_directory(directory_path):
    """
    Convert all HEIC files in the specified directory to JPG format.
    The original files are kept, and JPG versions are created with the same name.
    """
    # Make sure the directory path exists
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist!")
        return

    # Get all files in the directory
    files = os.listdir(directory_path)
    
    # Filter for HEIC files (case insensitive)
    heic_files = [f for f in files if f.lower().endswith(('.heic', '.heif'))]
    
    if not heic_files:
        print("No HEIC files found in the directory.")
        return
    
    print(f"Found {len(heic_files)} HEIC files to convert.")
    
    # Convert each file
    for filename in heic_files:
        try:
            input_path = os.path.join(directory_path, filename)
            output_path = os.path.join(directory_path, 
                                     os.path.splitext(filename)[0] + '.jpg')
            
            print(f"Converting {filename} to JPG...")
            image = Image.open(input_path)
            image.save(output_path, "JPEG")
            print(f"Successfully converted {filename}")
            
        except Exception as e:
            print(f"Error converting {filename}: {str(e)}")
    
    print("Conversion complete!")

# Example usage
if __name__ == "__main__":
    # Replace with your directory path
    directory_path = r"c:\Dropbox\Exchange"  # or use full path like "C:/Users/..."
    convert_heic_files_in_directory(directory_path)