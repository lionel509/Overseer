#!/usr/bin/env python3
"""
File Selector Tool
Provides interactive select menu for choosing files and directories
"""

import os
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json

class FileSelector:
    """Interactive file selector with menu interface"""
    
    def __init__(self):
        self.current_path = os.getcwd()
        self.history = []
        self.favorites = []
        self.max_display = 20
        
    def get_directory_contents(self, path: str = None) -> Dict[str, Any]:
        """Get contents of a directory with file/directory information"""
        if path is None:
            path = self.current_path
            
        try:
            items = []
            path_obj = Path(path)
            
            # Get all items in directory
            for item in path_obj.iterdir():
                try:
                    stat = item.stat()
                    item_info = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'hidden': item.name.startswith('.'),
                        'extension': item.suffix if item.is_file() else ''
                    }
                    items.append(item_info)
                except (PermissionError, OSError):
                    continue
            
            # Sort items: directories first, then files, alphabetically
            items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
            
            return {
                'success': True,
                'data': {
                    'current_path': path,
                    'items': items,
                    'parent_path': str(path_obj.parent) if path_obj.parent != path_obj else None,
                    'total_items': len(items)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error reading directory {path}: {str(e)}"
            }
    
    def select_file_interactive(self, start_path: str = None, file_types: List[str] = None) -> Dict[str, Any]:
        """Interactive file selection with menu"""
        if start_path is None:
            start_path = self.current_path
            
        self.current_path = start_path
        selected_files = []
        
        print(f"\n📁 File Selector - Current Directory: {self.current_path}")
        print("=" * 60)
        
        while True:
            # Get directory contents
            result = self.get_directory_contents(self.current_path)
            if not result['success']:
                print(f"❌ Error: {result['error']}")
                return {'success': False, 'error': result['error']}
            
            data = result['data']
            items = data['items']
            
            # Display menu
            self._display_menu(items, file_types)
            
            # Get user input
            choice = self._get_user_choice(len(items))
            
            if choice == 'q':
                # Quit
                break
            elif choice == 'b':
                # Go back
                if data['parent_path']:
                    self.current_path = data['parent_path']
                    self.history.append(self.current_path)
            elif choice == 'h':
                # Go home
                self.current_path = os.path.expanduser('~')
                self.history.append(self.current_path)
            elif choice == 'f':
                # Add current directory to favorites
                if self.current_path not in self.favorites:
                    self.favorites.append(self.current_path)
                    print(f"✅ Added {self.current_path} to favorites")
            elif choice == 's':
                # Show favorites
                self._show_favorites()
            elif choice == 't':
                # Toggle file type filter
                file_types = self._toggle_file_types(file_types)
            elif choice == 'a':
                # Select all files in current directory
                files = [item for item in items if item['type'] == 'file']
                if file_types:
                    files = [f for f in files if f['extension'] in file_types]
                selected_files.extend([f['path'] for f in files])
                print(f"✅ Selected {len(files)} files")
            elif choice == 'c':
                # Confirm selection
                if selected_files:
                    print(f"✅ Final selection: {len(selected_files)} files")
                    return {
                        'success': True,
                        'data': {
                            'selected_files': selected_files,
                            'current_path': self.current_path
                        }
                    }
                else:
                    print("⚠️  No files selected")
            elif choice.isdigit():
                # Select specific item
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    item = items[idx]
                    if item['type'] == 'directory':
                        # Navigate to directory
                        self.current_path = item['path']
                        self.history.append(self.current_path)
                    else:
                        # Select file
                        if file_types is None or item['extension'] in file_types:
                            if item['path'] not in selected_files:
                                selected_files.append(item['path'])
                                print(f"✅ Selected: {item['name']}")
                            else:
                                selected_files.remove(item['path'])
                                print(f"❌ Deselected: {item['name']}")
                        else:
                            print(f"⚠️  File type {item['extension']} not in filter")
            else:
                print("❌ Invalid choice. Please try again.")
        
        return {
            'success': True,
            'data': {
                'selected_files': selected_files,
                'current_path': self.current_path
            }
        }
    
    def _display_menu(self, items: List[Dict], file_types: List[str] = None):
        """Display the file selection menu"""
        print(f"\n📂 Contents of: {self.current_path}")
        print("-" * 60)
        
        # Show filter status
        if file_types:
            print(f"🔍 Filter: {', '.join(file_types)} files only")
        else:
            print("🔍 Filter: All files")
        
        # Display items
        for i, item in enumerate(items[:self.max_display], 1):
            icon = "📁" if item['type'] == 'directory' else "📄"
            size = self._format_size(item['size']) if item['type'] == 'file' else ""
            hidden = " (hidden)" if item['hidden'] else ""
            selected = " ✓" if item['path'] in getattr(self, '_selected_files', []) else ""
            
            print(f"{i:2d}. {icon} {item['name']}{hidden}{selected} {size}")
        
        if len(items) > self.max_display:
            print(f"... and {len(items) - self.max_display} more items")
        
        # Show commands
        print("\n" + "-" * 60)
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
    
    def _get_user_choice(self, max_items: int) -> str:
        """Get user choice from input"""
        while True:
            try:
                choice = input("\nEnter choice: ").strip().lower()
                if choice in ['q', 'b', 'h', 'f', 's', 't', 'a', 'c']:
                    return choice
                elif choice.isdigit():
                    idx = int(choice)
                    if 1 <= idx <= max_items:
                        return choice
                    else:
                        print(f"❌ Please enter a number between 1 and {max_items}")
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                return 'q'
            except EOFError:
                return 'q'
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def _show_favorites(self):
        """Show favorite directories"""
        if not self.favorites:
            print("📝 No favorites saved")
            return
        
        print("\n⭐ Favorites:")
        for i, fav in enumerate(self.favorites, 1):
            print(f"{i}. {fav}")
        
        choice = input("Enter number to navigate to favorite (or press Enter to continue): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.favorites):
                self.current_path = self.favorites[idx]
                print(f"✅ Navigated to: {self.current_path}")
    
    def _toggle_file_types(self, current_types: List[str] = None) -> List[str]:
        """Toggle file type filter"""
        common_types = ['.py', '.js', '.ts', '.json', '.txt', '.md', '.html', '.css', '.xml', '.csv']
        
        if current_types is None:
            print("\n📋 Available file types:")
            for i, ext in enumerate(common_types, 1):
                print(f"{i}. {ext}")
            print("0. All files")
            
            choice = input("Select file type filter (or press Enter for all): ").strip()
            if choice == '0' or choice == '':
                return None
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(common_types):
                    return [common_types[idx]]
        
        return None
    
    def select_files_by_pattern(self, pattern: str, base_path: str = None, recursive: bool = True) -> Dict[str, Any]:
        """Select files by pattern with interactive confirmation"""
        if base_path is None:
            base_path = self.current_path
        
        # Find files matching pattern
        if recursive:
            pattern_path = os.path.join(base_path, "**", pattern)
            files = glob.glob(pattern_path, recursive=True)
        else:
            pattern_path = os.path.join(base_path, pattern)
            files = glob.glob(pattern_path)
        
        if not files:
            return {
                'success': False,
                'error': f"No files found matching pattern: {pattern}"
            }
        
        # Convert to file info
        file_items = []
        for file_path in files:
            try:
                path_obj = Path(file_path)
                stat = path_obj.stat()
                file_items.append({
                    'name': path_obj.name,
                    'path': file_path,
                    'type': 'file',
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'hidden': path_obj.name.startswith('.'),
                    'extension': path_obj.suffix
                })
            except (PermissionError, OSError):
                continue
        
        # Sort by name
        file_items.sort(key=lambda x: x['name'].lower())
        
        print(f"\n🔍 Found {len(file_items)} files matching pattern: {pattern}")
        print("=" * 60)
        
        # Display files for selection
        selected_files = []
        for i, item in enumerate(file_items, 1):
            size = self._format_size(item['size'])
            print(f"{i:2d}. 📄 {item['name']} ({size})")
        
        print("\nCommands:")
        print("  [number] - Select/deselect file")
        print("  a        - Select all files")
        print("  c        - Confirm selection")
        print("  q        - Quit without selection")
        
        while True:
            choice = input("\nEnter choice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'a':
                selected_files = [item['path'] for item in file_items]
                print(f"✅ Selected all {len(selected_files)} files")
            elif choice == 'c':
                if selected_files:
                    print(f"✅ Final selection: {len(selected_files)} files")
                    return {
                        'success': True,
                        'data': {
                            'selected_files': selected_files,
                            'pattern': pattern,
                            'base_path': base_path
                        }
                    }
                else:
                    print("⚠️  No files selected")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(file_items):
                    item = file_items[idx]
                    if item['path'] in selected_files:
                        selected_files.remove(item['path'])
                        print(f"❌ Deselected: {item['name']}")
                    else:
                        selected_files.append(item['path'])
                        print(f"✅ Selected: {item['name']}")
            else:
                print("❌ Invalid choice. Please try again.")
        
        return {
            'success': True,
            'data': {
                'selected_files': selected_files,
                'pattern': pattern,
                'base_path': base_path
            }
        }
    
    def get_recent_files(self, max_files: int = 10) -> Dict[str, Any]:
        """Get recently accessed files"""
        try:
            # This is a simplified implementation
            # In a real system, you'd track file access times
            recent_files = []
            home_dir = os.path.expanduser('~')
            
            # Look for common file types in home directory
            for ext in ['.py', '.js', '.txt', '.md', '.json']:
                pattern = os.path.join(home_dir, f"**/*{ext}")
                files = glob.glob(pattern, recursive=True)
                for file_path in files[:5]:  # Limit per extension
                    try:
                        path_obj = Path(file_path)
                        stat = path_obj.stat()
                        recent_files.append({
                            'name': path_obj.name,
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'extension': path_obj.suffix
                        })
                    except (PermissionError, OSError):
                        continue
            
            # Sort by modification time (most recent first)
            recent_files.sort(key=lambda x: x['modified'], reverse=True)
            
            return {
                'success': True,
                'data': {
                    'recent_files': recent_files[:max_files]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting recent files: {str(e)}"
            }
    
    def save_selection(self, selected_files: List[str], name: str = None) -> Dict[str, Any]:
        """Save current selection for later use"""
        if name is None:
            name = f"selection_{len(self.history)}"
        
        selection_data = {
            'name': name,
            'files': selected_files,
            'timestamp': time.time(),
            'count': len(selected_files)
        }
        
        # Save to a simple JSON file
        selections_file = os.path.expanduser('~/.overseer_selections.json')
        try:
            if os.path.exists(selections_file):
                with open(selections_file, 'r') as f:
                    selections = json.load(f)
            else:
                selections = {}
            
            selections[name] = selection_data
            
            with open(selections_file, 'w') as f:
                json.dump(selections, f, indent=2)
            
            return {
                'success': True,
                'data': {
                    'name': name,
                    'saved_files': len(selected_files)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error saving selection: {str(e)}"
            }
    
    def load_selection(self, name: str) -> Dict[str, Any]:
        """Load a previously saved selection"""
        selections_file = os.path.expanduser('~/.overseer_selections.json')
        
        try:
            if not os.path.exists(selections_file):
                return {
                    'success': False,
                    'error': "No saved selections found"
                }
            
            with open(selections_file, 'r') as f:
                selections = json.load(f)
            
            if name not in selections:
                return {
                    'success': False,
                    'error': f"Selection '{name}' not found"
                }
            
            selection = selections[name]
            
            # Verify files still exist
            existing_files = []
            for file_path in selection['files']:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
            
            return {
                'success': True,
                'data': {
                    'name': name,
                    'files': existing_files,
                    'original_count': len(selection['files']),
                    'existing_count': len(existing_files),
                    'timestamp': selection['timestamp']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error loading selection: {str(e)}"
            }

# Import time module for timestamp
import time 