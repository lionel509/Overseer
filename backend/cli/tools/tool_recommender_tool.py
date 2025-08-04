#!/usr/bin/env python3
"""
Tool Recommender Tool for Overseer CLI
Provides intelligent tool recommendations based on system context and user behavior
"""

import psutil
import platform
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class ToolRecommenderTool:
    def __init__(self):
        self.tool_database = {
            'system_monitor': {
                'name': 'System Monitor',
                'description': 'Real-time system performance monitoring',
                'category': 'monitoring',
                'action': 'start_monitoring',
                'icon': 'Activity',
                'triggers': ['high_cpu', 'high_memory', 'morning_time']
            },
            'file_search': {
                'name': 'File Search',
                'description': 'Advanced file search and management',
                'category': 'files',
                'action': 'file_search',
                'icon': 'Search',
                'triggers': ['file_operations', 'storage_issues']
            },
            'process_manager': {
                'name': 'Process Manager',
                'description': 'View and manage running processes',
                'category': 'system',
                'action': 'process_list',
                'icon': 'Cpu',
                'triggers': ['high_cpu', 'performance_issues']
            },
            'network_monitor': {
                'name': 'Network Monitor',
                'description': 'Monitor network activity and connections',
                'category': 'monitoring',
                'action': 'network_status',
                'icon': 'Network',
                'triggers': ['network_activity', 'connectivity_issues']
            },
            'disk_analyzer': {
                'name': 'Disk Analyzer',
                'description': 'Analyze disk usage and storage',
                'category': 'system',
                'action': 'disk_usage',
                'icon': 'HardDrive',
                'triggers': ['high_disk_usage', 'storage_issues']
            },
            'memory_analyzer': {
                'name': 'Memory Analyzer',
                'description': 'Analyze memory usage and performance',
                'category': 'system',
                'action': 'memory_usage',
                'icon': 'Memory',
                'triggers': ['high_memory', 'performance_issues']
            },
            'command_history': {
                'name': 'Command History',
                'description': 'View and reuse previous commands',
                'category': 'productivity',
                'action': 'command_history',
                'icon': 'Clock',
                'triggers': ['frequent_commands', 'productivity']
            },
            'quick_actions': {
                'name': 'Quick Actions',
                'description': 'Common system operations',
                'category': 'productivity',
                'action': 'quick_actions',
                'icon': 'Zap',
                'triggers': ['general_use', 'productivity']
            }
        }
        
        self.usage_history = {}
        self.recommendation_history = []
        
    def get_system_context(self) -> Dict[str, Any]:
        """Get current system context for recommendations"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            processes = len(psutil.pids())
            
            # Determine time of day
            hour = datetime.now().hour
            if hour < 12:
                time_of_day = 'morning'
            elif hour < 18:
                time_of_day = 'afternoon'
            else:
                time_of_day = 'evening'
            
            context = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'network_activity': network.bytes_sent > 0 or network.bytes_recv > 0,
                'active_processes': processes,
                'time_of_day': time_of_day,
                'platform': platform.system(),
                'timestamp': datetime.now().isoformat()
            }
            
            return context
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_recommendations(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate tool recommendations based on system context"""
        try:
            if context is None:
                context = self.get_system_context()
            
            if 'error' in context:
                return {
                    'success': False,
                    'error': context['error']
                }
            
            recommendations = []
            triggers = self._analyze_triggers(context)
            
            # Generate recommendations based on triggers
            for tool_id, tool_info in self.tool_database.items():
                priority = self._calculate_priority(tool_id, triggers, context)
                
                if priority > 0:
                    recommendation = {
                        'id': tool_id,
                        'name': tool_info['name'],
                        'description': tool_info['description'],
                        'category': tool_info['category'],
                        'priority': self._get_priority_level(priority),
                        'reason': self._generate_reason(tool_id, triggers, context),
                        'action': tool_info['action'],
                        'icon': tool_info['icon'],
                        'usage_count': self.usage_history.get(tool_id, 0),
                        'is_recommended': priority >= 0.7,  # High priority recommendations
                        'score': priority
                    }
                    recommendations.append(recommendation)
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            # Add to recommendation history
            self._add_to_recommendation_history(context, recommendations)
            
            return {
                'success': True,
                'data': recommendations,
                'context': context,
                'metadata': {
                    'total_recommendations': len(recommendations),
                    'high_priority_count': len([r for r in recommendations if r['is_recommended']]),
                    'generation_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_triggers(self, context: Dict[str, Any]) -> List[str]:
        """Analyze system context and identify triggers"""
        triggers = []
        
        # CPU triggers
        if context['cpu_usage'] > 80:
            triggers.append('high_cpu')
        elif context['cpu_usage'] > 60:
            triggers.append('moderate_cpu')
        
        # Memory triggers
        if context['memory_usage'] > 85:
            triggers.append('high_memory')
        elif context['memory_usage'] > 70:
            triggers.append('moderate_memory')
        
        # Disk triggers
        if context['disk_usage'] > 90:
            triggers.append('high_disk_usage')
        elif context['disk_usage'] > 80:
            triggers.append('moderate_disk_usage')
        
        # Network triggers
        if context['network_activity']:
            triggers.append('network_activity')
        
        # Time-based triggers
        if context['time_of_day'] == 'morning':
            triggers.append('morning_time')
        elif context['time_of_day'] == 'afternoon':
            triggers.append('afternoon_time')
        
        # Process triggers
        if context['active_processes'] > 200:
            triggers.append('many_processes')
        
        # General triggers
        triggers.append('general_use')
        
        return triggers
    
    def _calculate_priority(self, tool_id: str, triggers: List[str], context: Dict[str, Any]) -> float:
        """Calculate priority score for a tool based on triggers and context"""
        tool_info = self.tool_database[tool_id]
        tool_triggers = tool_info.get('triggers', [])
        
        # Base score
        score = 0.1
        
        # Trigger matching
        for trigger in triggers:
            if trigger in tool_triggers:
                score += 0.3
        
        # Usage-based adjustment
        usage_count = self.usage_history.get(tool_id, 0)
        if usage_count > 10:
            score += 0.1  # Frequently used tools get slight boost
        elif usage_count == 0:
            score += 0.2  # New tools get boost
        
        # Context-specific adjustments
        if tool_id == 'process_manager' and context['cpu_usage'] > 80:
            score += 0.4
        elif tool_id == 'memory_analyzer' and context['memory_usage'] > 85:
            score += 0.4
        elif tool_id == 'disk_analyzer' and context['disk_usage'] > 90:
            score += 0.4
        elif tool_id == 'network_monitor' and context['network_activity']:
            score += 0.3
        elif tool_id == 'system_monitor' and context['time_of_day'] == 'morning':
            score += 0.2
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _get_priority_level(self, score: float) -> str:
        """Convert score to priority level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_reason(self, tool_id: str, triggers: List[str], context: Dict[str, Any]) -> str:
        """Generate human-readable reason for recommendation"""
        tool_info = self.tool_database[tool_id]
        
        if tool_id == 'process_manager' and context['cpu_usage'] > 80:
            return f"High CPU usage detected ({context['cpu_usage']:.1f}%)"
        elif tool_id == 'memory_analyzer' and context['memory_usage'] > 85:
            return f"High memory usage detected ({context['memory_usage']:.1f}%)"
        elif tool_id == 'disk_analyzer' and context['disk_usage'] > 90:
            return f"High disk usage detected ({context['disk_usage']:.1f}%)"
        elif tool_id == 'network_monitor' and context['network_activity']:
            return "Network activity detected"
        elif tool_id == 'system_monitor' and context['time_of_day'] == 'morning':
            return "Good morning! Start your day with system monitoring"
        elif tool_id == 'quick_actions':
            return "Common system operations"
        else:
            return f"Available {tool_info['category']} tool"
    
    def record_tool_usage(self, tool_id: str):
        """Record that a tool was used"""
        self.usage_history[tool_id] = self.usage_history.get(tool_id, 0) + 1
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        total_usage = sum(self.usage_history.values())
        
        stats = {
            'total_usage': total_usage,
            'tool_usage': self.usage_history.copy(),
            'most_used': max(self.usage_history.items(), key=lambda x: x[1]) if self.usage_history else None,
            'least_used': min(self.usage_history.items(), key=lambda x: x[1]) if self.usage_history else None
        }
        
        return stats
    
    def _add_to_recommendation_history(self, context: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Add recommendation to history"""
        self.recommendation_history.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'recommendations': recommendations
        })
        
        # Keep only recent recommendations
        if len(self.recommendation_history) > 50:
            self.recommendation_history = self.recommendation_history[-50:]
    
    def get_recommendation_history(self) -> List[Dict[str, Any]]:
        """Get recommendation history"""
        return self.recommendation_history
    
    def clear_recommendation_history(self):
        """Clear recommendation history"""
        self.recommendation_history = []
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools"""
        tools = []
        for tool_id, tool_info in self.tool_database.items():
            tool = {
                'id': tool_id,
                'name': tool_info['name'],
                'description': tool_info['description'],
                'category': tool_info['category'],
                'action': tool_info['action'],
                'icon': tool_info['icon'],
                'usage_count': self.usage_history.get(tool_id, 0)
            }
            tools.append(tool)
        
        return tools
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get tools filtered by category"""
        tools = self.get_available_tools()
        return [tool for tool in tools if tool['category'] == category]
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        categories = set(tool['category'] for tool in self.tool_database.values())
        return list(categories)

def main():
    """CLI interface for tool recommender"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool Recommender")
    parser.add_argument("--context", action="store_true", help="Show current system context")
    parser.add_argument("--recommend", action="store_true", help="Generate recommendations")
    parser.add_argument("--usage", action="store_true", help="Show tool usage statistics")
    parser.add_argument("--tools", action="store_true", help="Show all available tools")
    parser.add_argument("--categories", action="store_true", help="Show available categories")
    parser.add_argument("--category", type=str, help="Show tools in specific category")
    parser.add_argument("--record-usage", type=str, help="Record usage of a specific tool")
    
    args = parser.parse_args()
    
    tool = ToolRecommenderTool()
    
    if args.context:
        context = tool.get_system_context()
        print("System Context:")
        print(json.dumps(context, indent=2))
    
    elif args.recommend:
        result = tool.generate_recommendations()
        if result['success']:
            print("Tool Recommendations:")
            for rec in result['data']:
                print(f"  {rec['name']} ({rec['priority']}) - {rec['reason']}")
        else:
            print(f"Error: {result['error']}")
    
    elif args.usage:
        stats = tool.get_tool_usage_stats()
        print("Tool Usage Statistics:")
        print(f"  Total usage: {stats['total_usage']}")
        print(f"  Most used: {stats['most_used']}")
        print(f"  Least used: {stats['least_used']}")
        print("  Tool usage:")
        for tool_id, count in stats['tool_usage'].items():
            print(f"    {tool_id}: {count}")
    
    elif args.tools:
        tools = tool.get_available_tools()
        print("Available Tools:")
        for t in tools:
            print(f"  {t['name']} ({t['category']}) - {t['description']}")
    
    elif args.categories:
        categories = tool.get_categories()
        print("Available Categories:")
        for cat in categories:
            print(f"  {cat}")
    
    elif args.category:
        tools = tool.get_tools_by_category(args.category)
        print(f"Tools in category '{args.category}':")
        for t in tools:
            print(f"  {t['name']} - {t['description']}")
    
    elif args.record_usage:
        tool.record_tool_usage(args.record_usage)
        print(f"Recorded usage of tool: {args.record_usage}")
    
    else:
        # Default: show recommendations
        result = tool.generate_recommendations()
        if result['success']:
            print("Tool Recommendations:")
            for rec in result['data']:
                print(f"  {rec['name']} ({rec['priority']}) - {rec['reason']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main() 