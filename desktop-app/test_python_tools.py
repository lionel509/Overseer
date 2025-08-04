#!/usr/bin/env python3
"""
Test script for Python tools in Overseer CLI
Tests all the new tools: file search, command processor, tool recommender, and real-time stats
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

def test_file_search_tool():
    """Test the file search tool"""
    print("🧪 Testing File Search Tool...")
    
    try:
        from cli.tools import FileSearchTool
        
        tool = FileSearchTool()
        
        # Test basic search
        result = tool.search_files("*.py", base_path=".", recursive=False)
        print(f"   📁 Basic search: {len(result.get('data', []))} files found")
        
        # Test with filters
        filters = {
            'file_types': ['.py'],
            'size_range': {'min': 0, 'max': 1000000},
            'include_hidden': False
        }
        result = tool.search_files("test", base_path=".", filters=filters)
        print(f"   🔍 Filtered search: {len(result.get('data', []))} files found")
        
        # Test search history
        history = tool.get_search_history()
        print(f"   📚 Search history: {len(history)} entries")
        
        print("✅ File search tool test passed")
        return True
        
    except Exception as e:
        print(f"❌ File search tool test failed: {e}")
        return False

def test_command_processor_tool():
    """Test the command processor tool"""
    print("🧪 Testing Command Processor Tool...")
    
    try:
        from cli.tools import CommandProcessorTool
        
        tool = CommandProcessorTool()
        
        # Test built-in commands
        commands = ['system_info', 'memory_usage', 'disk_usage', 'network_status']
        
        for cmd in commands:
            result = tool.execute_command(cmd)
            if result['success']:
                print(f"   ✅ {cmd}: Success")
            else:
                print(f"   ❌ {cmd}: {result.get('error', 'Unknown error')}")
        
        # Test command history
        history = tool.get_command_history()
        print(f"   📚 Command history: {len(history)} entries")
        
        # Test supported commands
        supported = tool.get_supported_commands()
        print(f"   🛠️  Supported commands: {len(supported)} commands")
        
        print("✅ Command processor tool test passed")
        return True
        
    except Exception as e:
        print(f"❌ Command processor tool test failed: {e}")
        return False

def test_tool_recommender_tool():
    """Test the tool recommender tool"""
    print("🧪 Testing Tool Recommender Tool...")
    
    try:
        from cli.tools import ToolRecommenderTool
        
        tool = ToolRecommenderTool()
        
        # Test system context
        context = tool.get_system_context()
        print(f"   📊 System context: CPU={context.get('cpu_usage', 0):.1f}%, "
              f"Memory={context.get('memory_usage', 0):.1f}%, "
              f"Disk={context.get('disk_usage', 0):.1f}%")
        
        # Test recommendations
        result = tool.generate_recommendations()
        if result['success']:
            recommendations = result['data']
            print(f"   💡 Generated {len(recommendations)} recommendations")
            
            for rec in recommendations[:3]:  # Show first 3
                print(f"      - {rec['name']} ({rec['priority']}): {rec['reason']}")
        else:
            print(f"   ❌ Failed to generate recommendations: {result.get('error')}")
        
        # Test tool usage tracking
        tool.record_tool_usage('system_monitor')
        tool.record_tool_usage('file_search')
        stats = tool.get_tool_usage_stats()
        print(f"   📈 Tool usage stats: {stats['total_usage']} total uses")
        
        # Test available tools
        tools = tool.get_available_tools()
        print(f"   🛠️  Available tools: {len(tools)} tools")
        
        # Test categories
        categories = tool.get_categories()
        print(f"   📂 Categories: {', '.join(categories)}")
        
        print("✅ Tool recommender tool test passed")
        return True
        
    except Exception as e:
        print(f"❌ Tool recommender tool test failed: {e}")
        return False

def test_real_time_stats_tool():
    """Test the real-time stats tool"""
    print("🧪 Testing Real-Time Stats Tool...")
    
    try:
        from cli.tools import RealTimeStatsTool
        
        tool = RealTimeStatsTool()
        
        # Test current stats
        stats = tool.get_current_stats()
        print(f"   📊 Current stats: CPU={stats['cpu']['usage']:.1f}%, "
              f"Memory={stats['memory']['percent']:.1f}%, "
              f"Disk={stats['disk']['percent']:.1f}%")
        
        # Test monitoring start/stop
        start_result = tool.start_monitoring(interval=1.0)
        print(f"   ▶️  Start monitoring: {start_result['success']}")
        
        if start_result['success']:
            time.sleep(2)  # Let it collect some data
            
            # Get some stats while monitoring
            for i in range(3):
                current_stats = tool.get_current_stats()
                print(f"      Sample {i+1}: CPU={current_stats['cpu']['usage']:.1f}%")
                time.sleep(1)
            
            stop_result = tool.stop_monitoring()
            print(f"   ⏹️  Stop monitoring: {stop_result['success']}")
        
        # Test stats history
        history = tool.get_stats_history(5)
        print(f"   📚 Stats history: {len(history)} samples")
        
        # Test summary
        summary = tool.get_stats_summary()
        if 'error' not in summary:
            print(f"   📈 Summary: {summary['total_samples']} samples, "
                  f"Avg CPU={summary['averages']['cpu']:.1f}%")
        
        # Test alert thresholds
        thresholds = tool.get_alert_thresholds()
        print(f"   🚨 Alert thresholds: CPU warning={thresholds['cpu']['warning']}%, "
              f"critical={thresholds['cpu']['critical']}%")
        
        print("✅ Real-time stats tool test passed")
        return True
        
    except Exception as e:
        print(f"❌ Real-time stats tool test failed: {e}")
        return False

def test_backend_integration():
    """Test the backend integration with all tools"""
    print("🧪 Testing Backend Integration...")
    
    try:
        from backend_integration import DesktopBackendIntegration
        
        integration = DesktopBackendIntegration()
        
        # Test tool recommendations
        result = integration.handle_command("tool_recommendations")
        if result['success']:
            recommendations = result['data']
            print(f"   💡 Integration tool recommendations: {len(recommendations)} found")
        else:
            print(f"   ❌ Integration tool recommendations failed: {result.get('error')}")
        
        # Test real-time monitoring
        start_result = integration.handle_command("start_real_time_monitoring")
        print(f"   ▶️  Integration start monitoring: {start_result['success']}")
        
        if start_result['success']:
            time.sleep(2)
            
            # Get real-time stats
            stats_result = integration.handle_command("get_real_time_stats")
            if stats_result['success']:
                stats = stats_result['data']
                print(f"   📊 Integration real-time stats: CPU={stats['cpu']['usage']:.1f}%")
            else:
                print(f"   ❌ Integration real-time stats failed: {stats_result.get('error')}")
            
            # Stop monitoring
            stop_result = integration.handle_command("stop_real_time_monitoring")
            print(f"   ⏹️  Integration stop monitoring: {stop_result['success']}")
        
        # Test command execution
        cmd_result = integration.handle_command("execute_command", ["system_info"])
        if cmd_result['success']:
            print(f"   ✅ Integration command execution: Success")
        else:
            print(f"   ❌ Integration command execution failed: {cmd_result.get('error')}")
        
        print("✅ Backend integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

def test_tool_package():
    """Test the tools package functionality"""
    print("🧪 Testing Tools Package...")
    
    try:
        from cli.tools import get_available_tools, create_tool, list_tools
        
        # Test available tools
        tools = get_available_tools()
        print(f"   🛠️  Available tools: {len(tools)} tools")
        
        for name, info in tools.items():
            print(f"      - {name}: {info['description']} ({info['category']})")
        
        # Test tool creation
        file_search_tool = create_tool('file_search')
        print(f"   ✅ Created file search tool: {type(file_search_tool).__name__}")
        
        command_processor_tool = create_tool('command_processor')
        print(f"   ✅ Created command processor tool: {type(command_processor_tool).__name__}")
        
        tool_recommender_tool = create_tool('tool_recommender')
        print(f"   ✅ Created tool recommender tool: {type(tool_recommender_tool).__name__}")
        
        real_time_stats_tool = create_tool('real_time_stats')
        print(f"   ✅ Created real-time stats tool: {type(real_time_stats_tool).__name__}")
        
        print("✅ Tools package test passed")
        return True
        
    except Exception as e:
        print(f"❌ Tools package test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Python Tools for Overseer CLI...")
    print("=" * 60)
    
    tests = [
        ("File Search Tool", test_file_search_tool),
        ("Command Processor Tool", test_command_processor_tool),
        ("Tool Recommender Tool", test_tool_recommender_tool),
        ("Real-Time Stats Tool", test_real_time_stats_tool),
        ("Tools Package", test_tool_package),
        ("Backend Integration", test_backend_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("🎉 Python Tools Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Python tools are working correctly!")
        print("\nThe CLI now supports:")
        print("• Advanced file search with filtering")
        print("• Command processing and history management")
        print("• Intelligent tool recommendations")
        print("• Real-time system monitoring")
        print("• Comprehensive backend integration")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    main() 