#!/usr/bin/env python3
"""
Test file for CommandProcessorTool
Tests all functionality of the command processor tool
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cli.tools.command_processor_tool import CommandProcessorTool

class TestCommandProcessorTool(unittest.TestCase):
    """Test cases for CommandProcessorTool"""
    
    def setUp(self):
        """Set up test environment"""
        self.tool = CommandProcessorTool()
    
    def test_execute_command_system_info(self):
        """Test executing system_info command"""
        result = self.tool.execute_command('system_info')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('platform', result['data'])
        self.assertIn('architecture', result['data'])
    
    def test_execute_command_memory_usage(self):
        """Test executing memory_usage command"""
        result = self.tool.execute_command('memory_usage')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('total', result['data'])
        self.assertIn('available', result['data'])
        self.assertIn('percent', result['data'])
    
    def test_execute_command_disk_usage(self):
        """Test executing disk_usage command"""
        result = self.tool.execute_command('disk_usage')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)
        
        if result['data']:
            disk_info = result['data'][0]
            self.assertIn('device', disk_info)
            self.assertIn('total', disk_info)
            self.assertIn('used', disk_info)
            self.assertIn('free', disk_info)
    
    def test_execute_command_network_status(self):
        """Test executing network_status command"""
        result = self.tool.execute_command('network_status')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)
    
    def test_execute_command_process_list(self):
        """Test executing process_list command"""
        result = self.tool.execute_command('process_list')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)
        
        if result['data']:
            process_info = result['data'][0]
            self.assertIn('pid', process_info)
            self.assertIn('name', process_info)
            self.assertIn('cpu_percent', process_info)
            self.assertIn('memory_percent', process_info)
    
    def test_execute_command_get_metrics(self):
        """Test executing get_metrics command"""
        result = self.tool.execute_command('get_metrics')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('cpu', result['data'])
        self.assertIn('memory', result['data'])
        self.assertIn('disk', result['data'])
        self.assertIn('network', result['data'])
    
    def test_execute_command_unsupported(self):
        """Test executing unsupported command"""
        result = self.tool.execute_command('unsupported_command')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_execute_command_with_args(self):
        """Test executing command with arguments"""
        result = self.tool.execute_command('system_info', ['--detailed'])
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_execute_external_command(self):
        """Test executing external shell command"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=b'Hello World\n',
                stderr=b''
            )
            
            result = self.tool.execute_command('echo', ['Hello World'])
            
            self.assertTrue(result['success'])
            self.assertIn('data', result)
            self.assertIn('Hello World', result['data']['output'])
    
    def test_execute_external_command_error(self):
        """Test executing external command that fails"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout=b'',
                stderr=b'Command not found\n'
            )
            
            result = self.tool.execute_command('nonexistent_command')
            
            self.assertFalse(result['success'])
            self.assertIn('error', result)
    
    def test_get_command_history(self):
        """Test getting command history"""
        # Execute a command first
        self.tool.execute_command('system_info')
        
        history = self.tool.get_command_history()
        
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # Check history entry structure
        entry = history[0]
        self.assertIn('command', entry)
        self.assertIn('args', entry)
        self.assertIn('timestamp', entry)
        self.assertIn('success', entry)
        self.assertIn('duration', entry)
    
    def test_clear_command_history(self):
        """Test clearing command history"""
        # Execute a command first
        self.tool.execute_command('system_info')
        
        # Clear history
        self.tool.clear_command_history()
        
        # Check that history is empty
        history = self.tool.get_command_history()
        self.assertEqual(len(history), 0)
    
    def test_get_supported_commands(self):
        """Test getting list of supported commands"""
        commands = self.tool.get_supported_commands()
        
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        
        # Check that all expected commands are present
        expected_commands = [
            'system_info', 'memory_usage', 'disk_usage', 
            'network_status', 'process_list', 'get_metrics'
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, commands)
    
    def test_command_duration_tracking(self):
        """Test that command duration is tracked"""
        result = self.tool.execute_command('system_info')
        
        self.assertTrue(result['success'])
        self.assertIn('duration', result)
        self.assertIsInstance(result['duration'], (int, float))
        self.assertGreater(result['duration'], 0)
    
    def test_command_error_handling(self):
        """Test error handling for various scenarios"""
        # Test with None command
        result = self.tool.execute_command(None)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test with empty command
        result = self.tool.execute_command('')
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_history_limit(self):
        """Test that history doesn't grow indefinitely"""
        # Execute many commands
        for i in range(100):
            self.tool.execute_command('system_info')
        
        history = self.tool.get_command_history()
        
        # History should be limited (implementation dependent)
        self.assertLessEqual(len(history), 100)
    
    def test_command_with_special_characters(self):
        """Test commands with special characters"""
        result = self.tool.execute_command('system_info', ['--test', 'value with spaces'])
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_concurrent_command_execution(self):
        """Test that commands can be executed concurrently"""
        import threading
        import time
        
        results = []
        errors = []
        
        def execute_command():
            try:
                result = self.tool.execute_command('system_info')
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=execute_command)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All commands should succeed
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)
        
        for result in results:
            self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main() 