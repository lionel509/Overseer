#!/usr/bin/env python3
"""
Overseer CLI Tools Package
Provides various tools for system management and file operations
"""

from .file_search_tool import FileSearchTool
from .command_processor_tool import CommandProcessorTool
from .tool_recommender_tool import ToolRecommenderTool
from .real_time_stats_tool import RealTimeStatsTool
from .file_selector import FileSelector

__version__ = '1.0.0'
__author__ = 'Overseer Team'

# Available tools
AVAILABLE_TOOLS = {
    'file_search': {
        'class': FileSearchTool,
        'description': 'Advanced file search with filtering capabilities',
        'category': 'files'
    },
    'command_processor': {
        'class': CommandProcessorTool,
        'description': 'Command execution and history management',
        'category': 'system'
    },
    'tool_recommender': {
        'class': ToolRecommenderTool,
        'description': 'Intelligent tool recommendations based on system context',
        'category': 'productivity'
    },
    'real_time_stats': {
        'class': RealTimeStatsTool,
        'description': 'Real-time system monitoring and performance tracking',
        'category': 'monitoring'
    },
    'file_selector': {
        'class': FileSelector,
        'description': 'Interactive file selection with menu interface',
        'category': 'files'
    }
}

def get_available_tools():
    """Get dictionary of available tools"""
    return AVAILABLE_TOOLS

def create_tool(tool_name: str):
    """Create a tool instance by name"""
    if tool_name in AVAILABLE_TOOLS:
        tool_class = AVAILABLE_TOOLS[tool_name]['class']
        return tool_class()
    return None

def list_tools():
    """List all available tools"""
    print("Available Tools:")
    print("=" * 50)
    for name, info in AVAILABLE_TOOLS.items():
        print(f"{name}:")
        print(f"  Description: {info['description']}")
        print(f"  Category: {info['category']}")
        print()

__all__ = [
    'FileSearchTool',
    'CommandProcessorTool', 
    'ToolRecommenderTool',
    'RealTimeStatsTool',
    'FileSelector',
    'get_available_tools',
    'create_tool',
    'list_tools',
    'AVAILABLE_TOOLS'
] 