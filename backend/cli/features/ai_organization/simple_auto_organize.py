#!/usr/bin/env python3
"""
Simple auto-organize functionality for demo purposes
"""
import os
import shutil
from pathlib import Path

def auto_organize(folder_path):
    """
    Simple file organization by file type
    Args:
        folder_path: Path to the folder to organize
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    print(f"Organizing files in: {folder_path}")
    
    # Define file type mappings
    file_types = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.php']
    }
    
    # Get all files in the folder
    files = [f for f in os.listdir(folder_path) 
             if os.path.isfile(os.path.join(folder_path, f))]
    
    if not files:
        print("No files found to organize")
        return
    
    moved_count = 0
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        file_ext = Path(filename).suffix.lower()
        
        # Find appropriate category
        target_folder = None
        for category, extensions in file_types.items():
            if file_ext in extensions:
                target_folder = category
                break
        
        if not target_folder:
            target_folder = 'Other'
        
        # Create target directory if it doesn't exist
        target_dir = os.path.join(folder_path, target_folder)
        os.makedirs(target_dir, exist_ok=True)
        
        # Move file
        target_path = os.path.join(target_dir, filename)
        try:
            shutil.move(file_path, target_path)
            print(f"Moved {filename} to {target_folder}/")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    
    print(f"Successfully organized {moved_count} files")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        auto_organize(sys.argv[1])
    else:
        print("Usage: python simple_auto_organize.py <folder_path>")
