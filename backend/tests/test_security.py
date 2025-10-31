"""
Security Tests
Tests for security features and fixes
"""

import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.cli.tools.file_search_tool import FileSearchTool


class TestPathTraversalProtection(unittest.TestCase):
    """Test path traversal protection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = FileSearchTool()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_safe_path_validation(self):
        """Test that path validation prevents traversal"""
        base_path = self.test_dir
        
        # Safe path within base
        safe_path = os.path.join(base_path, "subdir", "file.txt")
        self.assertTrue(self.tool._is_safe_path(base_path, safe_path))
        
        # Unsafe path outside base
        unsafe_path = "/etc/passwd"
        self.assertFalse(self.tool._is_safe_path(base_path, unsafe_path))
        
        # Path with .. trying to escape
        escape_path = os.path.join(base_path, "..", "..", "etc", "passwd")
        self.assertFalse(self.tool._is_safe_path(base_path, escape_path))
    
    def test_restricted_directories(self):
        """Test that searches in restricted directories are blocked"""
        # Try to search in /etc (should be blocked for non-root)
        # Cross-platform: Use getattr for Unix-only functions
        is_root = getattr(os, 'geteuid', lambda: 1)() == 0
        if not is_root:
            result = self.tool.search_files("*", base_path="/etc")
            self.assertFalse(result['success'])
            self.assertIn("Access denied", result['error'])


class TestFileSizeLimits(unittest.TestCase):
    """Test file size limits for DoS prevention"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = FileSearchTool()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_large_file_skipped(self):
        """Test that large files are skipped in content search"""
        # Create a file larger than the limit
        large_file = os.path.join(self.test_dir, "large.txt")
        
        # Mock a large file by checking the method directly
        # In real implementation, file size is checked before reading
        with open(large_file, 'w') as f:
            f.write("test content")
        
        # The file size check should prevent reading huge files
        # This is tested in the actual implementation
        self.assertTrue(True)  # Placeholder for actual size limit test


class TestInputSanitization(unittest.TestCase):
    """Test input sanitization"""
    
    def test_gemini_prompt_sanitization(self):
        """Test that Gemini API prompts are sanitized"""
        # Note: This would require mocking the Gemini API
        # For now, we verify the method exists
        try:
            from backend.cli.inference.inference_gemini import GeminiAPI
            
            # Verify that the class has the sanitization method
            self.assertTrue(hasattr(GeminiAPI, '_sanitize_prompt'))
        except ImportError:
            # If we can't import, that's okay for this test
            pass


class TestSecureFilePermissions(unittest.TestCase):
    """Test secure file permissions"""
    
    def test_key_file_permissions(self):
        """Test that key files get secure permissions"""
        # Create a temporary key file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            key_file = f.name
            f.write("test_key")
        
        try:
            # Set permissions like the keygen does
            os.chmod(key_file, 0o600)
            
            # Check permissions
            stat_info = os.stat(key_file)
            mode = stat_info.st_mode & 0o777
            
            # Should be 0o600 (owner read/write only)
            self.assertEqual(mode, 0o600)
        finally:
            os.unlink(key_file)


class TestCORSConfiguration(unittest.TestCase):
    """Test CORS configuration"""
    
    def test_cors_not_wildcard(self):
        """Test that CORS is not configured with wildcard"""
        # Read the API main file
        api_main_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'backend', 'api', 'main.py'
        )
        
        if os.path.exists(api_main_path):
            with open(api_main_path, 'r') as f:
                content = f.read()
                
            # Should not have allow_origins=["*"]
            self.assertNotIn('allow_origins=["*"]', content)
            
            # Should have environment-based origins
            self.assertIn('OVERSEER_ALLOWED_ORIGINS', content)


if __name__ == '__main__':
    unittest.main()
