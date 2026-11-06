from pathlib import Path

def change_extensions(directory_path, old_ext, new_ext):
    # Ensure extensions start with a dot
    old_ext = f".{old_ext.lstrip('.')}"
    new_ext = f".{new_ext.lstrip('.')}"
    
    directory = Path(directory_path)
    
    # Track modified files
    counter = 0
    
    # Iterate through all files in the directory matching the old extension
    for file_path in directory.glob(f"*{old_ext}"):
        if file_path.is_file():
            # Create new path with the updated extension
            new_path = file_path.with_suffix(new_ext)
            
            # Rename the file
            file_path.rename(new_path)
            print(f"Renamed: {file_path.name} -> {new_path.name}")
            counter += 1
            
    print(f"\nSuccessfully updated {counter} files.")

# --- Example Usage ---
# Replace with your folder path, target extension, and desired extension
folder = r"." 
change_extensions(folder, "vtt", "srt")
