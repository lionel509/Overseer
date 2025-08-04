#!/usr/bin/env python3
"""
Test file for FileSearchTool
Tests all functionality of the file search tool
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cli.tools.file_search_tool import FileSearchTool

class TestFileSearchTool(unittest.TestCase):
    """Test cases for FileSearchTool"""
    
    def setUp(self):
        """Set up test environment"""
        self.tool = FileSearchTool()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_files(self):
        """Create test files for testing"""
        # Create Python files
        with open(os.path.join(self.test_dir, "test1.py"), "w") as f:
            f.write("print('Hello World')\n")
        
        with open(os.path.join(self.test_dir, "test2.py"), "w") as f:
            f.write("def test_function():\n    pass\n")
        
        # Create JavaScript files
        with open(os.path.join(self.test_dir, "script.js"), "w") as f:
            f.write("console.log('Hello');\n")
        
        # Create text files
        with open(os.path.join(self.test_dir, "readme.txt"), "w") as f:
            f.write("This is a test file\n")
        
        # Create hidden file
        with open(os.path.join(self.test_dir, ".hidden"), "w") as f:
            f.write("Hidden file\n")
        
        # Create subdirectory
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "subfile.py"), "w") as f:
            f.write("print('Subfile')\n")
    
    def test_search_files_basic(self):
        """Test basic file search functionality"""
        result = self.tool.search_files("*.py", self.test_dir)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
        
        # Check that Python files are found
        file_names = [os.path.basename(f['path']) for f in result['data']]
        self.assertIn('test1.py', file_names)
        self.assertIn('test2.py', file_names)
    
    def test_search_files_with_filters(self):
        """Test file search with filters"""
        filters = {
            'file_types': ['.py'],
            'include_hidden': False
        }
        
        result = self.tool.search_files("*.py", self.test_dir, filters=filters)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Should not include hidden files
        file_names = [os.path.basename(f['path']) for f in result['data']]
        self.assertNotIn('.hidden', file_names)
    
    def test_search_files_recursive(self):
        """Test recursive file search"""
        result = self.tool.search_files("*.py", self.test_dir, recursive=True)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Should include files in subdirectories
        file_names = [os.path.basename(f['path']) for f in result['data']]
        self.assertIn('subfile.py', file_names)
    
    def test_search_files_size_filter(self):
        """Test file search with size filter"""
        filters = {
            'size_range': {'min': 0, 'max': 50}  # Small files only
        }
        
        result = self.tool.search_files("*", self.test_dir, filters=filters)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # All files should be within size range
        for file_info in result['data']:
            self.assertLessEqual(file_info['size'], 50)
    
    def test_search_files_date_filter(self):
        """Test file search with date filter"""
        import datetime
        
        # Create a file with specific date
        test_file = os.path.join(self.test_dir, "dated_file.py")
        with open(test_file, "w") as f:
            f.write("test")
        
        # Set file modification time to yesterday
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        os.utime(test_file, (yesterday.timestamp(), yesterday.timestamp()))
        
        filters = {
            'date_range': {
                'start': (yesterday - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                'end': (yesterday + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            }
        }
        
        result = self.tool.search_files("*", self.test_dir, filters=filters)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Should find the dated file
        file_names = [os.path.basename(f['path']) for f in result['data']]
        self.assertIn('dated_file.py', file_names)
    
    def test_search_files_content_search(self):
        """Test file search with content search"""
        filters = {
            'search_in_content': True
        }
        
        result = self.tool.search_files("Hello", self.test_dir, filters=filters)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Should find files containing "Hello"
        file_names = [os.path.basename(f['path']) for f in result['data']]
        self.assertIn('test1.py', file_names)
        self.assertIn('readme.txt', file_names)
    
    def test_get_file_content(self):
        """Test getting file content"""
        test_file = os.path.join(self.test_dir, "test1.py")
        
        result = self.tool.get_file_content(test_file, max_lines=10)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('print(\'Hello World\')', result['data'])
    
    def test_get_file_content_nonexistent(self):
        """Test getting content of nonexistent file"""
        result = self.tool.get_file_content("nonexistent_file.py")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_search_history(self):
        """Test search history functionality"""
        # Perform a search
        self.tool.search_files("*.py", self.test_dir)
        
        # Get history
        history = self.tool.get_search_history()
        
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # Check history entry structure
        entry = history[0]
        self.assertIn('query', entry)
        self.assertIn('timestamp', entry)
        self.assertIn('results_count', entry)
    
    def test_clear_search_history(self):
        """Test clearing search history"""
        # Perform a search
        self.tool.search_files("*.py", self.test_dir)
        
        # Clear history
        self.tool.clear_search_history()
        
        # Check that history is empty
        history = self.tool.get_search_history()
        self.assertEqual(len(history), 0)
    
    def test_pattern_search(self):
        """Test pattern-based search"""
        result = self.tool._pattern_search("*.py", self.test_dir)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # All results should be Python files
        for file_path in result:
            self.assertTrue(file_path.endswith('.py'))
    
    def test_text_search(self):
        """Test text-based search"""
        result = self.tool._text_search("Hello", self.test_dir, search_in_content=True)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
    
    def test_get_file_info(self):
        """Test getting file information"""
        test_file = os.path.join(self.test_dir, "test1.py")
        
        file_info = self.tool._get_file_info(test_file)
        
        self.assertIsInstance(file_info, dict)
        self.assertIn('name', file_info)
        self.assertIn('path', file_info)
        self.assertIn('size', file_info)
        self.assertIn('modified', file_info)
        self.assertIn('type', file_info)
    
    def test_apply_filters(self):
        """Test filter application"""
        files = [
            {'path': 'test1.py', 'size': 20, 'type': '.py'},
            {'path': 'script.js', 'size': 30, 'type': '.js'},
            {'path': '.hidden', 'size': 10, 'type': ''}
        ]
        
        # Test file type filter
        filters = {'file_types': ['.py']}
        filtered = self.tool._apply_filters(files, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['path'], 'test1.py')
        
        # Test size filter
        filters = {'size_range': {'min': 25, 'max': 35}}
        filtered = self.tool._apply_filters(files, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['path'], 'script.js')
        
        # Test hidden files filter
        filters = {'include_hidden': False}
        filtered = self.tool._apply_filters(files, filters)
        self.assertEqual(len(filtered), 2)
        self.assertNotIn('.hidden', [f['path'] for f in filtered])

if __name__ == '__main__':
    unittest.main() 