#!/usr/bin/env python3
"""
Test file for ToolRecommenderTool
Tests all functionality of the tool recommender tool
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cli.tools.tool_recommender_tool import ToolRecommenderTool

class TestToolRecommenderTool(unittest.TestCase):
    """Test cases for ToolRecommenderTool"""
    
    def setUp(self):
        """Set up test environment"""
        self.tool = ToolRecommenderTool()
    
    def test_get_system_context(self):
        """Test getting system context"""
        context = self.tool.get_system_context()
        
        self.assertIsInstance(context, dict)
        self.assertIn('cpu_usage', context)
        self.assertIn('memory_usage', context)
        self.assertIn('disk_usage', context)
        self.assertIn('network_activity', context)
        self.assertIn('time_of_day', context)
        self.assertIn('day_of_week', context)
        
        # Check value ranges
        self.assertGreaterEqual(context['cpu_usage'], 0)
        self.assertLessEqual(context['cpu_usage'], 100)
        self.assertGreaterEqual(context['memory_usage'], 0)
        self.assertLessEqual(context['memory_usage'], 100)
    
    def test_generate_recommendations_basic(self):
        """Test basic recommendation generation"""
        result = self.tool.generate_recommendations()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)
        
        if result['data']:
            recommendation = result['data'][0]
            self.assertIn('name', recommendation)
            self.assertIn('description', recommendation)
            self.assertIn('category', recommendation)
            self.assertIn('priority', recommendation)
            self.assertIn('reason', recommendation)
    
    def test_generate_recommendations_with_context(self):
        """Test recommendation generation with custom context"""
        custom_context = {
            'cpu_usage': 90.0,
            'memory_usage': 85.0,
            'disk_usage': 75.0,
            'network_activity': True,
            'time_of_day': 'morning',
            'day_of_week': 'monday'
        }
        
        result = self.tool.generate_recommendations(custom_context)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)
    
    def test_generate_recommendations_high_cpu(self):
        """Test recommendations for high CPU usage"""
        context = {'cpu_usage': 95.0, 'memory_usage': 50.0, 'disk_usage': 50.0}
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        # Should recommend performance tools
        tool_names = [rec['name'] for rec in result['data']]
        performance_tools = ['process_manager', 'system_monitor', 'performance_analyzer']
        
        for tool in performance_tools:
            if tool in self.tool.tool_database:
                # At least one performance tool should be recommended
                self.assertTrue(any(tool in rec['name'].lower() for rec in result['data']))
    
    def test_generate_recommendations_high_memory(self):
        """Test recommendations for high memory usage"""
        context = {'cpu_usage': 50.0, 'memory_usage': 95.0, 'disk_usage': 50.0}
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        # Should recommend memory management tools
        tool_names = [rec['name'] for rec in result['data']]
        memory_tools = ['memory_analyzer', 'process_manager']
        
        for tool in memory_tools:
            if tool in self.tool.tool_database:
                # At least one memory tool should be recommended
                self.assertTrue(any(tool in rec['name'].lower() for rec in result['data']))
    
    def test_generate_recommendations_high_disk(self):
        """Test recommendations for high disk usage"""
        context = {'cpu_usage': 50.0, 'memory_usage': 50.0, 'disk_usage': 95.0}
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        # Should recommend disk management tools
        tool_names = [rec['name'] for rec in result['data']]
        disk_tools = ['disk_cleaner', 'file_organizer', 'storage_analyzer']
        
        for tool in disk_tools:
            if tool in self.tool.tool_database:
                # At least one disk tool should be recommended
                self.assertTrue(any(tool in rec['name'].lower() for rec in result['data']))
    
    def test_generate_recommendations_morning_time(self):
        """Test recommendations for morning time"""
        context = {'cpu_usage': 50.0, 'memory_usage': 50.0, 'disk_usage': 50.0, 'time_of_day': 'morning'}
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        # Should recommend productivity tools for morning
        tool_names = [rec['name'] for rec in result['data']]
        morning_tools = ['task_manager', 'productivity_tracker', 'daily_planner']
        
        for tool in morning_tools:
            if tool in self.tool.tool_database:
                # At least one morning tool should be recommended
                self.assertTrue(any(tool in rec['name'].lower() for rec in result['data']))
    
    def test_record_tool_usage(self):
        """Test recording tool usage"""
        tool_id = 'test_tool'
        
        # Record usage
        self.tool.record_tool_usage(tool_id)
        
        # Check that usage was recorded
        stats = self.tool.get_tool_usage_stats()
        self.assertIn(tool_id, stats)
        self.assertEqual(stats[tool_id]['usage_count'], 1)
    
    def test_get_tool_usage_stats(self):
        """Test getting tool usage statistics"""
        # Record some usage
        self.tool.record_tool_usage('tool1')
        self.tool.record_tool_usage('tool1')
        self.tool.record_tool_usage('tool2')
        
        stats = self.tool.get_tool_usage_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('tool1', stats)
        self.assertIn('tool2', stats)
        self.assertEqual(stats['tool1']['usage_count'], 2)
        self.assertEqual(stats['tool2']['usage_count'], 1)
    
    def test_get_available_tools(self):
        """Test getting available tools"""
        tools = self.tool.get_available_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check tool structure
        tool = tools[0]
        self.assertIn('id', tool)
        self.assertIn('name', tool)
        self.assertIn('description', tool)
        self.assertIn('category', tool)
        self.assertIn('triggers', tool)
    
    def test_get_categories(self):
        """Test getting tool categories"""
        categories = self.tool.get_categories()
        
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        # Check that categories are unique
        self.assertEqual(len(categories), len(set(categories)))
    
    def test_get_tools_by_category(self):
        """Test getting tools by category"""
        categories = self.tool.get_categories()
        
        if categories:
            category = categories[0]
            tools = self.tool.get_tools_by_category(category)
            
            self.assertIsInstance(tools, list)
            
            # All tools should belong to the specified category
            for tool in tools:
                self.assertEqual(tool['category'], category)
    
    def test_priority_calculation(self):
        """Test priority calculation logic"""
        context = {
            'cpu_usage': 90.0,
            'memory_usage': 85.0,
            'disk_usage': 75.0,
            'network_activity': True,
            'time_of_day': 'morning'
        }
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        # Check that priorities are calculated
        for recommendation in result['data']:
            self.assertIn('priority', recommendation)
            self.assertIsInstance(recommendation['priority'], (int, float))
            self.assertGreaterEqual(recommendation['priority'], 0)
            self.assertLessEqual(recommendation['priority'], 100)
    
    def test_recommendation_reasons(self):
        """Test that recommendations include reasons"""
        context = {'cpu_usage': 95.0}
        
        result = self.tool.generate_recommendations(context)
        
        self.assertTrue(result['success'])
        
        for recommendation in result['data']:
            self.assertIn('reason', recommendation)
            self.assertIsInstance(recommendation['reason'], str)
            self.assertGreater(len(recommendation['reason']), 0)
    
    def test_empty_context_handling(self):
        """Test handling of empty context"""
        result = self.tool.generate_recommendations({})
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_none_context_handling(self):
        """Test handling of None context"""
        result = self.tool.generate_recommendations(None)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_invalid_tool_id_handling(self):
        """Test handling of invalid tool IDs"""
        # Should not raise an exception
        self.tool.record_tool_usage('invalid_tool_id')
        
        stats = self.tool.get_tool_usage_stats()
        self.assertIn('invalid_tool_id', stats)
    
    def test_recommendation_filtering(self):
        """Test that recommendations are filtered based on context"""
        # Test with low system usage
        low_context = {'cpu_usage': 10.0, 'memory_usage': 20.0, 'disk_usage': 30.0}
        low_result = self.tool.generate_recommendations(low_context)
        
        # Test with high system usage
        high_context = {'cpu_usage': 90.0, 'memory_usage': 85.0, 'disk_usage': 80.0}
        high_result = self.tool.generate_recommendations(high_context)
        
        # Should get different recommendations
        low_tools = [rec['name'] for rec in low_result['data']]
        high_tools = [rec['name'] for rec in high_result['data']]
        
        # At least some recommendations should be different
        self.assertNotEqual(set(low_tools), set(high_tools))
    
    def test_recommendation_consistency(self):
        """Test that recommendations are consistent for same context"""
        context = {'cpu_usage': 75.0, 'memory_usage': 60.0}
        
        result1 = self.tool.generate_recommendations(context)
        result2 = self.tool.generate_recommendations(context)
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        
        # Should have same number of recommendations
        self.assertEqual(len(result1['data']), len(result2['data']))
    
    def test_tool_database_structure(self):
        """Test that tool database has correct structure"""
        for tool_id, tool_info in self.tool.tool_database.items():
            self.assertIn('name', tool_info)
            self.assertIn('description', tool_info)
            self.assertIn('category', tool_info)
            self.assertIn('triggers', tool_info)
            self.assertIn('action', tool_info)
            
            # Check triggers structure
            triggers = tool_info['triggers']
            self.assertIsInstance(triggers, dict)
            
            # Check that trigger values are valid
            for trigger_type, threshold in triggers.items():
                if trigger_type in ['high_cpu', 'high_memory', 'high_disk']:
                    self.assertIsInstance(threshold, (int, float))
                    self.assertGreaterEqual(threshold, 0)
                    self.assertLessEqual(threshold, 100)

if __name__ == '__main__':
    unittest.main() 