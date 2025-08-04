#!/usr/bin/env python3
"""
Test file for RealTimeStatsTool
Tests all functionality of the real-time stats tool
"""

import unittest
import tempfile
import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cli.tools.real_time_stats_tool import RealTimeStatsTool

class TestRealTimeStatsTool(unittest.TestCase):
    """Test cases for RealTimeStatsTool"""
    
    def setUp(self):
        """Set up test environment"""
        self.tool = RealTimeStatsTool()
    
    def tearDown(self):
        """Clean up test environment"""
        # Stop monitoring if it's running
        if hasattr(self.tool, 'monitoring_thread') and self.tool.monitoring_thread:
            self.tool.stop_monitoring()
    
    def test_get_current_stats(self):
        """Test getting current system statistics"""
        stats = self.tool.get_current_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('cpu', stats)
        self.assertIn('memory', stats)
        self.assertIn('disk', stats)
        self.assertIn('network', stats)
        self.assertIn('timestamp', stats)
        
        # Check CPU stats
        cpu_stats = stats['cpu']
        self.assertIn('usage', cpu_stats)
        self.assertIn('count', cpu_stats)
        self.assertIn('frequency', cpu_stats)
        self.assertGreaterEqual(cpu_stats['usage'], 0)
        self.assertLessEqual(cpu_stats['usage'], 100)
        
        # Check memory stats
        memory_stats = stats['memory']
        self.assertIn('total', memory_stats)
        self.assertIn('available', memory_stats)
        self.assertIn('used', memory_stats)
        self.assertIn('percent', memory_stats)
        self.assertGreater(memory_stats['total'], 0)
        
        # Check disk stats
        disk_stats = stats['disk']
        self.assertIsInstance(disk_stats, list)
        if disk_stats:
            disk_info = disk_stats[0]
            self.assertIn('device', disk_info)
            self.assertIn('total', disk_info)
            self.assertIn('used', disk_info)
            self.assertIn('free', disk_info)
            self.assertIn('percent', disk_info)
    
    def test_start_monitoring(self):
        """Test starting monitoring"""
        result = self.tool.start_monitoring(interval=0.1)  # Fast interval for testing
        
        self.assertTrue(result['success'])
        self.assertTrue(self.tool.is_monitoring)
        self.assertIsNotNone(self.tool.monitoring_thread)
        self.assertTrue(self.tool.monitoring_thread.is_alive())
        
        # Wait a bit for some data to be collected
        time.sleep(0.3)
        
        # Check that data was collected
        history = self.tool.get_stats_history()
        self.assertGreater(len(history), 0)
    
    def test_stop_monitoring(self):
        """Test stopping monitoring"""
        # Start monitoring first
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.2)
        
        # Stop monitoring
        result = self.tool.stop_monitoring()
        
        self.assertTrue(result['success'])
        self.assertFalse(self.tool.is_monitoring)
        self.assertIsNone(self.tool.monitoring_thread)
    
    def test_get_monitoring_status(self):
        """Test getting monitoring status"""
        status = self.tool.get_monitoring_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('is_active', status)
        self.assertIn('interval', status)
        self.assertIn('data_points', status)
        self.assertIn('start_time', status)
        
        self.assertIsInstance(status['is_active'], bool)
        self.assertIsInstance(status['interval'], (int, float))
        self.assertIsInstance(status['data_points'], int)
    
    def test_get_stats_history(self):
        """Test getting statistics history"""
        # Start monitoring to collect some data
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.3)
        self.tool.stop_monitoring()
        
        history = self.tool.get_stats_history()
        
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # Check history entry structure
        entry = history[0]
        self.assertIn('cpu', entry)
        self.assertIn('memory', entry)
        self.assertIn('disk', entry)
        self.assertIn('network', entry)
        self.assertIn('timestamp', entry)
    
    def test_get_stats_history_with_limit(self):
        """Test getting statistics history with limit"""
        # Start monitoring to collect some data
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.5)
        self.tool.stop_monitoring()
        
        # Get limited history
        history = self.tool.get_stats_history(limit=2)
        
        self.assertIsInstance(history, list)
        self.assertLessEqual(len(history), 2)
    
    def test_get_stats_summary(self):
        """Test getting statistics summary"""
        # Start monitoring to collect some data
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.3)
        self.tool.stop_monitoring()
        
        summary = self.tool.get_stats_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_samples', summary)
        self.assertIn('duration', summary)
        self.assertIn('cpu_avg', summary)
        self.assertIn('memory_avg', summary)
        self.assertIn('cpu_max', summary)
        self.assertIn('memory_max', summary)
        
        self.assertGreater(summary['total_samples'], 0)
        self.assertGreater(summary['duration'], 0)
    
    def test_get_alert_thresholds(self):
        """Test getting alert thresholds"""
        thresholds = self.tool.get_alert_thresholds()
        
        self.assertIsInstance(thresholds, dict)
        self.assertIn('cpu', thresholds)
        self.assertIn('memory', thresholds)
        self.assertIn('disk', thresholds)
        
        # Check CPU thresholds
        cpu_thresholds = thresholds['cpu']
        self.assertIn('warning', cpu_thresholds)
        self.assertIn('critical', cpu_thresholds)
        self.assertLess(cpu_thresholds['warning'], cpu_thresholds['critical'])
        
        # Check memory thresholds
        memory_thresholds = thresholds['memory']
        self.assertIn('warning', memory_thresholds)
        self.assertIn('critical', memory_thresholds)
        self.assertLess(memory_thresholds['warning'], memory_thresholds['critical'])
    
    def test_set_alert_thresholds(self):
        """Test setting alert thresholds"""
        new_thresholds = {
            'cpu': {'warning': 70.0, 'critical': 90.0},
            'memory': {'warning': 75.0, 'critical': 85.0},
            'disk': {'warning': 80.0, 'critical': 95.0}
        }
        
        self.tool.set_alert_thresholds(new_thresholds)
        
        # Verify thresholds were set
        current_thresholds = self.tool.get_alert_thresholds()
        self.assertEqual(current_thresholds['cpu']['warning'], 70.0)
        self.assertEqual(current_thresholds['cpu']['critical'], 90.0)
        self.assertEqual(current_thresholds['memory']['warning'], 75.0)
        self.assertEqual(current_thresholds['memory']['critical'], 85.0)
    
    def test_check_alerts(self):
        """Test alert checking functionality"""
        # Set low thresholds to trigger alerts
        self.tool.set_alert_thresholds({
            'cpu': {'warning': 1.0, 'critical': 2.0},
            'memory': {'warning': 1.0, 'critical': 2.0},
            'disk': {'warning': 1.0, 'critical': 2.0}
        })
        
        # Get current stats (should trigger alerts)
        stats = self.tool.get_current_stats()
        alerts = self.tool._check_alerts(stats)
        
        self.assertIsInstance(alerts, list)
        # Should have some alerts due to low thresholds
        self.assertGreater(len(alerts), 0)
        
        for alert in alerts:
            self.assertIn('type', alert)
            self.assertIn('level', alert)
            self.assertIn('message', alert)
            self.assertIn('value', alert)
            self.assertIn('threshold', alert)
    
    def test_clear_history(self):
        """Test clearing statistics history"""
        # Start monitoring to collect some data
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.2)
        self.tool.stop_monitoring()
        
        # Verify data was collected
        history = self.tool.get_stats_history()
        self.assertGreater(len(history), 0)
        
        # Clear history
        self.tool.clear_history()
        
        # Verify history is empty
        history = self.tool.get_stats_history()
        self.assertEqual(len(history), 0)
    
    def test_monitoring_thread_safety(self):
        """Test that monitoring thread is thread-safe"""
        # Start monitoring
        self.tool.start_monitoring(interval=0.1)
        
        # Try to start monitoring again (should fail)
        result = self.tool.start_monitoring(interval=0.1)
        self.assertFalse(result['success'])
        
        # Stop monitoring
        self.tool.stop_monitoring()
        
        # Try to stop monitoring again (should fail)
        result = self.tool.stop_monitoring()
        self.assertFalse(result['success'])
    
    def test_data_point_limit(self):
        """Test that data points are limited"""
        # Set a small max data points
        original_max = self.tool.max_data_points
        self.tool.max_data_points = 3
        
        # Start monitoring
        self.tool.start_monitoring(interval=0.1)
        time.sleep(0.5)  # Collect more than 3 data points
        self.tool.stop_monitoring()
        
        # Check that history is limited
        history = self.tool.get_stats_history()
        self.assertLessEqual(len(history), 3)
        
        # Restore original max data points
        self.tool.max_data_points = original_max
    
    def test_concurrent_access(self):
        """Test concurrent access to the tool"""
        def get_stats():
            return self.tool.get_current_stats()
        
        def start_monitoring():
            return self.tool.start_monitoring(interval=0.1)
        
        def stop_monitoring():
            return self.tool.stop_monitoring()
        
        # Test concurrent stats retrieval
        threads = []
        results = []
        
        for _ in range(5):
            thread = threading.Thread(target=lambda: results.append(get_stats()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should succeed
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('cpu', result)
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with invalid interval
        result = self.tool.start_monitoring(interval=-1)
        self.assertFalse(result['success'])
        
        # Test with invalid thresholds
        invalid_thresholds = {
            'cpu': {'warning': 150.0, 'critical': 200.0}  # Invalid values
        }
        
        # Should handle gracefully
        self.tool.set_alert_thresholds(invalid_thresholds)
        thresholds = self.tool.get_alert_thresholds()
        self.assertIn('cpu', thresholds)
    
    def test_stats_consistency(self):
        """Test that stats are consistent across calls"""
        stats1 = self.tool.get_current_stats()
        stats2 = self.tool.get_current_stats()
        
        # Both should have same structure
        self.assertEqual(set(stats1.keys()), set(stats2.keys()))
        
        # CPU usage should be reasonable
        self.assertGreaterEqual(stats1['cpu']['usage'], 0)
        self.assertLessEqual(stats1['cpu']['usage'], 100)
        self.assertGreaterEqual(stats2['cpu']['usage'], 0)
        self.assertLessEqual(stats2['cpu']['usage'], 100)
    
    def test_network_stats(self):
        """Test network statistics collection"""
        stats = self.tool.get_current_stats()
        
        network_stats = stats['network']
        self.assertIsInstance(network_stats, list)
        
        if network_stats:
            interface = network_stats[0]
            self.assertIn('interface', interface)
            self.assertIn('bytes_sent', interface)
            self.assertIn('bytes_recv', interface)
            self.assertIn('packets_sent', interface)
            self.assertIn('packets_recv', interface)
    
    def test_disk_stats(self):
        """Test disk statistics collection"""
        stats = self.tool.get_current_stats()
        
        disk_stats = stats['disk']
        self.assertIsInstance(disk_stats, list)
        
        if disk_stats:
            disk_info = disk_stats[0]
            self.assertIn('device', disk_info)
            self.assertIn('total', disk_info)
            self.assertIn('used', disk_info)
            self.assertIn('free', disk_info)
            self.assertIn('percent', disk_info)
            
            # Check that values are reasonable
            self.assertGreater(disk_info['total'], 0)
            self.assertGreaterEqual(disk_info['used'], 0)
            self.assertGreaterEqual(disk_info['free'], 0)
            self.assertGreaterEqual(disk_info['percent'], 0)
            self.assertLessEqual(disk_info['percent'], 100)

if __name__ == '__main__':
    unittest.main() 