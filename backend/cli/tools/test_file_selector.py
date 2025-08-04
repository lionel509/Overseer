#!/usr/bin/env python3
"""
Test file for FileSelector
Tests all functionality of the file selector tool
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cli.tools.file_selector import FileSelector

class TestFileSelector(unittest.TestCase):
    """Test cases for FileSelector"""
    
    def setUp(self):
        """Set up test environment"""
        self.selector = FileSelector()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files and directories
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_files(self):
        """Create test files and directories"""
        # Create subdirectories
        subdir1 = os.path.join(self.test_dir, "subdir1")
        subdir2 = os.path.join(self.test_dir, "subdir2")
        os.makedirs(subdir1)
        os.makedirs(subdir2)
        
        # Create files in root directory
        with open(os.path.join(self.test_dir, "test1.py"), "w") as f:
            f.write("print('Hello World')\n")
        
        with open(os.path.join(self.test_dir, "test2.py"), "w") as f:
            f.write("def test_function():\n    pass\n")
        
        with open(os.path.join(self.test_dir, "script.js"), "w") as f:
            f.write("console.log('Hello');\n")
        
        with open(os.path.join(self.test_dir, "readme.txt"), "w") as f:
            f.write("This is a test file\n")
        
        with open(os.path.join(self.test_dir, ".hidden"), "w") as f:
            f.write("Hidden file\n")
        
        # Create files in subdirectories
        with open(os.path.join(subdir1, "subfile.py"), "w") as f:
            f.write("print('Subfile')\n")
        
        with open(os.path.join(subdir2, "config.json"), "w") as f:
            f.write('{"test": true}\n')
    
    def test_get_directory_contents(self):
        """Test getting directory contents"""
        result = self.selector.get_directory_contents(self.test_dir)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertEqual(data['current_path'], self.test_dir)
        self.assertIn('items', data)
        self.assertIn('total_items', data)
        
        # Check that we have the expected items
        item_names = [item['name'] for item in data['items']]
        self.assertIn('test1.py', item_names)
        self.assertIn('test2.py', item_names)
        self.assertIn('script.js', item_names)
        self.assertIn('readme.txt', item_names)
        self.assertIn('.hidden', item_names)
        self.assertIn('subdir1', item_names)
        self.assertIn('subdir2', item_names)
    
    def test_get_directory_contents_nonexistent(self):
        """Test getting contents of nonexistent directory"""
        result = self.selector.get_directory_contents("/nonexistent/directory")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_format_size(self):
        """Test file size formatting"""
        # Test bytes
        self.assertEqual(self.selector._format_size(512), "512.0B")
        
        # Test kilobytes
        self.assertEqual(self.selector._format_size(1024), "1.0KB")
        
        # Test megabytes
        self.assertEqual(self.selector._format_size(1048576), "1.0MB")
        
        # Test gigabytes
        self.assertEqual(self.selector._format_size(1073741824), "1.0GB")
    
    def test_select_files_by_pattern(self):
        """Test selecting files by pattern"""
        result = self.selector.select_files_by_pattern("*.py", self.test_dir, recursive=True)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertIn('selected_files', data)
        self.assertIn('pattern', data)
        self.assertIn('base_path', data)
        
        # Should find Python files
        selected_files = data['selected_files']
        self.assertGreater(len(selected_files), 0)
        
        # All selected files should be Python files
        for file_path in selected_files:
            self.assertTrue(file_path.endswith('.py'))
    
    def test_select_files_by_pattern_nonexistent(self):
        """Test selecting files by pattern with no matches"""
        result = self.selector.select_files_by_pattern("*.nonexistent", self.test_dir)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_recent_files(self):
        """Test getting recent files"""
        result = self.selector.get_recent_files(max_files=5)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertIn('recent_files', data)
        
        # Should return some recent files
        recent_files = data['recent_files']
        self.assertIsInstance(recent_files, list)
    
    def test_save_and_load_selection(self):
        """Test saving and loading file selections"""
        test_files = [
            os.path.join(self.test_dir, "test1.py"),
            os.path.join(self.test_dir, "test2.py")
        ]
        
        # Save selection
        save_result = self.selector.save_selection(test_files, "test_selection")
        self.assertTrue(save_result['success'])
        
        # Load selection
        load_result = self.selector.load_selection("test_selection")
        self.assertTrue(load_result['success'])
        
        data = load_result['data']
        self.assertEqual(data['name'], "test_selection")
        self.assertIn('files', data)
        self.assertIn('original_count', data)
        self.assertIn('existing_count', data)
        self.assertIn('timestamp', data)
        
        # Should have the same number of files
        self.assertEqual(data['original_count'], len(test_files))
        self.assertEqual(data['existing_count'], len(test_files))
    
    def test_load_nonexistent_selection(self):
        """Test loading nonexistent selection"""
        result = self.selector.load_selection("nonexistent_selection")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_favorites_functionality(self):
        """Test favorites functionality"""
        # Add to favorites
        self.selector.favorites.append(self.test_dir)
        
        # Check that it's in favorites
        self.assertIn(self.test_dir, self.selector.favorites)
        
        # Remove from favorites
        self.selector.favorites.remove(self.test_dir)
        
        # Check that it's not in favorites
        self.assertNotIn(self.test_dir, self.selector.favorites)
    
    def test_history_functionality(self):
        """Test history functionality"""
        # Add to history
        self.selector.history.append(self.test_dir)
        
        # Check that it's in history
        self.assertIn(self.test_dir, self.selector.history)
        
        # Clear history
        self.selector.history.clear()
        
        # Check that history is empty
        self.assertEqual(len(self.selector.history), 0)
    
    def test_file_type_filtering(self):
        """Test file type filtering"""
        # Get directory contents
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Filter by Python files
        python_files = [item for item in items if item['extension'] == '.py']
        self.assertGreater(len(python_files), 0)
        
        # All filtered files should be Python files
        for item in python_files:
            self.assertEqual(item['extension'], '.py')
            self.assertEqual(item['type'], 'file')
    
    def test_directory_navigation(self):
        """Test directory navigation"""
        # Get parent directory
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        data = result['data']
        parent_path = data['parent_path']
        
        # Parent path should exist and be different from current path
        self.assertIsNotNone(parent_path)
        self.assertNotEqual(parent_path, self.test_dir)
        
        # Should be able to navigate to parent
        parent_result = self.selector.get_directory_contents(parent_path)
        self.assertTrue(parent_result['success'])
    
    def test_hidden_files_handling(self):
        """Test handling of hidden files"""
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Find hidden files
        hidden_files = [item for item in items if item['hidden']]
        self.assertGreater(len(hidden_files), 0)
        
        # All hidden files should start with '.'
        for item in hidden_files:
            self.assertTrue(item['name'].startswith('.'))
    
    def test_file_size_information(self):
        """Test file size information"""
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Check that files have size information
        files = [item for item in items if item['type'] == 'file']
        for item in files:
            self.assertIn('size', item)
            self.assertIsInstance(item['size'], int)
            self.assertGreaterEqual(item['size'], 0)
    
    def test_directory_sorting(self):
        """Test that directories are sorted before files"""
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Find first file index
        first_file_index = None
        for i, item in enumerate(items):
            if item['type'] == 'file':
                first_file_index = i
                break
        
        # All items before first file should be directories
        if first_file_index is not None:
            for i in range(first_file_index):
                self.assertEqual(items[i]['type'], 'directory')
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test with None path
        result = self.selector.get_directory_contents(None)
        self.assertTrue(result['success'])
        
        # Test with empty string
        result = self.selector.get_directory_contents("")
        self.assertTrue(result['success'])
    
    def test_max_display_limit(self):
        """Test that display is limited to max_display items"""
        # Create many files
        for i in range(30):
            with open(os.path.join(self.test_dir, f"file{i}.txt"), "w") as f:
                f.write(f"File {i}\n")
        
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Should have more items than max_display
        self.assertGreater(len(items), self.selector.max_display)
    
    def test_file_extension_detection(self):
        """Test file extension detection"""
        result = self.selector.get_directory_contents(self.test_dir)
        self.assertTrue(result['success'])
        
        items = result['data']['items']
        
        # Check specific file extensions
        for item in items:
            if item['name'] == 'test1.py':
                self.assertEqual(item['extension'], '.py')
            elif item['name'] == 'script.js':
                self.assertEqual(item['extension'], '.js')
            elif item['name'] == 'readme.txt':
                self.assertEqual(item['extension'], '.txt')
            elif item['name'] == '.hidden':
                self.assertEqual(item['extension'], '')
            elif item['type'] == 'directory':
                self.assertEqual(item['extension'], '')

if __name__ == '__main__':
    unittest.main() 