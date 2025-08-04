#!/usr/bin/env python3
"""
Demo script for FileSelector
Shows how to use the interactive file selector
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from cli.tools import FileSelector

def demo_file_selector():
    """Demo the file selector functionality"""
    print("🎯 File Selector Demo")
    print("=" * 50)
    
    # Create file selector
    selector = FileSelector()
    
    print("1. Getting directory contents...")
    result = selector.get_directory_contents(".")
    
    if result['success']:
        data = result['data']
        print(f"✅ Current directory: {data['current_path']}")
        print(f"📁 Total items: {data['total_items']}")
        
        # Show first few items
        print("\n📂 Directory contents:")
        for i, item in enumerate(data['items'][:10], 1):
            icon = "📁" if item['type'] == 'directory' else "📄"
            size = selector._format_size(item['size']) if item['type'] == 'file' else ""
            hidden = " (hidden)" if item['hidden'] else ""
            print(f"  {i:2d}. {icon} {item['name']}{hidden} {size}")
        
        if len(data['items']) > 10:
            print(f"  ... and {len(data['items']) - 10} more items")
    
    print("\n2. Testing file pattern selection...")
    pattern_result = selector.select_files_by_pattern("*.py", ".", recursive=True)
    
    if pattern_result['success']:
        data = pattern_result['data']
        print(f"✅ Found {len(data['selected_files'])} Python files")
        for file_path in data['selected_files'][:5]:  # Show first 5
            print(f"  📄 {os.path.basename(file_path)}")
        if len(data['selected_files']) > 5:
            print(f"  ... and {len(data['selected_files']) - 5} more")
    
    print("\n3. Testing recent files...")
    recent_result = selector.get_recent_files(max_files=5)
    
    if recent_result['success']:
        data = recent_result['data']
        print(f"✅ Found {len(data['recent_files'])} recent files")
        for file_info in data['recent_files'][:3]:  # Show first 3
            size = selector._format_size(file_info['size'])
            print(f"  📄 {file_info['name']} ({size})")
    
    print("\n4. Testing save/load functionality...")
    test_files = [
        os.path.join(".", "demo_file_selector.py"),
        os.path.join(".", "test_all_tools.py")
    ]
    
    # Save selection
    save_result = selector.save_selection(test_files, "demo_selection")
    if save_result['success']:
        print(f"✅ Saved selection: {save_result['data']['name']}")
        
        # Load selection
        load_result = selector.load_selection("demo_selection")
        if load_result['success']:
            data = load_result['data']
            print(f"✅ Loaded selection: {data['name']}")
            print(f"📁 Files: {data['existing_count']}/{data['original_count']}")
    
    print("\n5. Testing favorites...")
    selector.favorites.append(".")
    selector.favorites.append(os.path.expanduser("~"))
    print(f"⭐ Favorites: {len(selector.favorites)} directories")
    for fav in selector.favorites:
        print(f"  📁 {fav}")
    
    print("\n6. Testing history...")
    selector.history.append(".")
    selector.history.append(os.path.expanduser("~"))
    print(f"📚 History: {len(selector.history)} entries")
    for hist in selector.history:
        print(f"  📁 {hist}")
    
    print("\n🎉 File Selector Demo Complete!")
    print("\nFeatures demonstrated:")
    print("  ✅ Directory browsing with file/directory info")
    print("  ✅ File pattern matching and selection")
    print("  ✅ Recent files detection")
    print("  ✅ Save/load file selections")
    print("  ✅ Favorites management")
    print("  ✅ Navigation history")
    print("  ✅ File size formatting")
    print("  ✅ Hidden file detection")
    print("  ✅ File type filtering")

def demo_interactive_selection():
    """Demo interactive file selection (simulated)"""
    print("\n🎮 Interactive File Selection Demo")
    print("=" * 50)
    print("This would show an interactive menu like:")
    print()
    print("📁 File Selector - Current Directory: /path/to/directory")
    print("=" * 60)
    print("📂 Contents of: /path/to/directory")
    print("-" * 60)
    print("🔍 Filter: All files")
    print()
    print(" 1. 📁 subdirectory")
    print(" 2. 📄 file1.py (1.2KB)")
    print(" 3. 📄 file2.js (856B)")
    print(" 4. 📄 readme.txt (2.1KB)")
    print(" 5. 📄 .hidden (hidden) (128B)")
    print()
    print("-" * 60)
    print("Commands:")
    print("  [number] - Select/deselect file or navigate directory")
    print("  a        - Select all files in current directory")
    print("  b        - Go back to parent directory")
    print("  h        - Go to home directory")
    print("  f        - Add current directory to favorites")
    print("  s        - Show favorites")
    print("  t        - Toggle file type filter")
    print("  c        - Confirm selection")
    print("  q        - Quit without selection")
    print()
    print("Enter choice: ")

if __name__ == "__main__":
    demo_file_selector()
    demo_interactive_selection() 