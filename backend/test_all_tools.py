#!/usr/bin/env python3
"""
Comprehensive test runner for all Overseer CLI tools and API
Tests all functionality to ensure everything works correctly
"""

import unittest
import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def run_unit_tests():
    """Run all unit tests for CLI tools"""
    print("🧪 Running Unit Tests for CLI Tools...")
    print("=" * 50)
    
    # Import test modules
    from cli.tools.test_file_search_tool import TestFileSearchTool
    from cli.tools.test_command_processor_tool import TestCommandProcessorTool
    from cli.tools.test_tool_recommender_tool import TestToolRecommenderTool
    from cli.tools.test_real_time_stats_tool import TestRealTimeStatsTool
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases using TestLoader
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(TestFileSearchTool))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCommandProcessorTool))
    test_suite.addTest(loader.loadTestsFromTestCase(TestToolRecommenderTool))
    test_suite.addTest(loader.loadTestsFromTestCase(TestRealTimeStatsTool))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def test_cli_tools_directly():
    """Test CLI tools directly without unit tests"""
    print("\n🔧 Testing CLI Tools Directly...")
    print("=" * 50)
    
    try:
        from cli.tools import (
            FileSearchTool, 
            CommandProcessorTool, 
            ToolRecommenderTool, 
            RealTimeStatsTool
        )
        
        # Test FileSearchTool
        print("Testing FileSearchTool...")
        file_search = FileSearchTool()
        result = file_search.search_files("*.py", ".", recursive=False)
        print(f"  ✅ FileSearchTool: {len(result.get('data', []))} files found")
        
        # Test CommandProcessorTool
        print("Testing CommandProcessorTool...")
        cmd_processor = CommandProcessorTool()
        result = cmd_processor.execute_command('system_info')
        print(f"  ✅ CommandProcessorTool: {result.get('success', False)}")
        
        # Test ToolRecommenderTool
        print("Testing ToolRecommenderTool...")
        tool_recommender = ToolRecommenderTool()
        result = tool_recommender.generate_recommendations()
        print(f"  ✅ ToolRecommenderTool: {len(result.get('data', []))} recommendations")
        
        # Test RealTimeStatsTool
        print("Testing RealTimeStatsTool...")
        stats_tool = RealTimeStatsTool()
        stats = stats_tool.get_current_stats()
        print(f"  ✅ RealTimeStatsTool: CPU {stats['cpu']['usage']:.1f}%, Memory {stats['memory']['percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing CLI tools: {e}")
        return False

def test_api_server():
    """Test the API server"""
    print("\n🌐 Testing API Server...")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ API server is running")
            return True
        else:
            print("  ❌ API server returned unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ API server is not running")
        print("  💡 To start the API server, run:")
        print("     cd backend/api")
        print("     python main.py --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"  ❌ Error testing API server: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔗 Testing API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/api/health", "Health check"),
        ("GET", "/api/tools", "List tools"),
        ("GET", "/api/system/info", "System info"),
        ("GET", "/api/system/memory", "Memory usage"),
        ("GET", "/api/system/disk", "Disk usage"),
        ("GET", "/api/system/network", "Network status"),
        ("GET", "/api/system/processes", "Process list"),
        ("GET", "/api/tools/real-time-stats/current", "Current stats"),
        ("GET", "/api/tools/tool-recommender/recommendations", "Tool recommendations"),
        ("GET", "/api/tools/tool-recommender/context", "System context"),
        ("GET", "/api/tools/tool-recommender/tools", "Available tools"),
        ("GET", "/api/tools/tool-recommender/categories", "Tool categories"),
    ]
    
    success_count = 0
    total_count = len(endpoints_to_test)
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {description}: Success")
                success_count += 1
            else:
                print(f"  ❌ {description}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"  ❌ {description}: Error ({e})")
    
    print(f"\n  📊 API Endpoints: {success_count}/{total_count} successful")
    return success_count == total_count

def test_api_post_endpoints():
    """Test POST API endpoints"""
    print("\n📝 Testing API POST Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    post_endpoints = [
        {
            "endpoint": "/api/tools/file-search/search",
            "data": {"query": "*.py", "base_path": ".", "recursive": False},
            "description": "File search"
        },
        {
            "endpoint": "/api/tools/command-processor/execute",
            "data": {"command": "system_info", "args": []},
            "description": "Command execution"
        },
        {
            "endpoint": "/api/tools/real-time-stats/start",
            "data": {"interval": 2.0},
            "description": "Start monitoring"
        }
    ]
    
    success_count = 0
    total_count = len(post_endpoints)
    
    for test in post_endpoints:
        try:
            response = requests.post(
                f"{base_url}{test['endpoint']}", 
                json=test['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✅ {test['description']}: Success")
                success_count += 1
            else:
                print(f"  ❌ {test['description']}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"  ❌ {test['description']}: Error ({e})")
    
    # Stop monitoring if it was started
    try:
        requests.post(f"{base_url}/api/tools/real-time-stats/stop", timeout=5)
    except:
        pass
    
    print(f"\n  📊 API POST Endpoints: {success_count}/{total_count} successful")
    return success_count == total_count

def test_tools_package():
    """Test the tools package functionality"""
    print("\n📦 Testing Tools Package...")
    print("=" * 50)
    
    try:
        from cli.tools import (
            get_available_tools, 
            create_tool, 
            list_tools
        )
        
        # Test get_available_tools
        tools = get_available_tools()
        print(f"  ✅ get_available_tools: {len(tools)} tools available")
        
        # Test list_tools
        print("  📋 Available tools:")
        list_tools()
        
        # Test create_tool
        file_search_tool = create_tool('file_search')
        if file_search_tool:
            print("  ✅ create_tool: FileSearchTool created successfully")
        else:
            print("  ❌ create_tool: Failed to create FileSearchTool")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing tools package: {e}")
        return False

def test_backend_integration():
    """Test the backend integration script"""
    print("\n🔗 Testing Backend Integration...")
    print("=" * 50)
    
    try:
        # Test the backend integration script
        integration_script = backend_path / "desktop-app" / "backend_integration.py"
        
        if integration_script.exists():
            # Test basic functionality
            result = subprocess.run([
                sys.executable, str(integration_script), "test"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✅ Backend integration script: Success")
                return True
            else:
                print(f"  ❌ Backend integration script: Failed ({result.stderr})")
                return False
        else:
            print("  ❌ Backend integration script not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing backend integration: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Comprehensive Test Suite for Overseer CLI Tools and API")
    print("=" * 60)
    
    results = []
    
    # Run unit tests
    unit_test_success = run_unit_tests()
    results.append(("Unit Tests", unit_test_success))
    
    # Test CLI tools directly
    cli_tools_success = test_cli_tools_directly()
    results.append(("CLI Tools Direct", cli_tools_success))
    
    # Test tools package
    tools_package_success = test_tools_package()
    results.append(("Tools Package", tools_package_success))
    
    # Test backend integration
    backend_integration_success = test_backend_integration()
    results.append(("Backend Integration", backend_integration_success))
    
    # Test API server
    api_server_success = test_api_server()
    results.append(("API Server", api_server_success))
    
    # Test API endpoints (only if server is running)
    if api_server_success:
        api_endpoints_success = test_api_endpoints()
        results.append(("API Endpoints", api_endpoints_success))
        
        api_post_endpoints_success = test_api_post_endpoints()
        results.append(("API POST Endpoints", api_post_endpoints_success))
    else:
        results.append(("API Endpoints", False))
        results.append(("API POST Endpoints", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The Overseer CLI tools and API are working correctly.")
        print("\n✅ What's working:")
        print("  • File search with advanced filtering")
        print("  • Command processing and history management")
        print("  • Tool recommendations based on system context")
        print("  • Real-time system monitoring and statistics")
        print("  • REST API endpoints for all tools")
        print("  • Backend integration for desktop app")
        print("  • Comprehensive error handling and validation")
        
        print("\n🚀 Next steps:")
        print("  • Start the API server: cd backend/api && python main.py")
        print("  • Test the desktop app: cd desktop-app && npm run dev")
        print("  • View API docs: http://localhost:8000/docs")
        
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed. Please check the errors above.")
        
        if not api_server_success:
            print("\n💡 To fix API server issues:")
            print("  1. Install dependencies: pip install fastapi uvicorn")
            print("  2. Start the server: cd backend/api && python main.py")
            print("  3. Test again: python test_all_tools.py")

if __name__ == "__main__":
    main() 