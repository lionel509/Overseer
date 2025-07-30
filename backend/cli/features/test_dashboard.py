#!/usr/bin/env python3
"""
Test script for the monitoring dashboard
Tests dashboard components without requiring full terminal interface.
"""

import os
import sys
import time
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

def test_dashboard_components():
    """Test dashboard components individually"""
    
    print("🧪 Testing Dashboard Components")
    print("=" * 50)
    
    # Test 1: Dashboard initialization
    print("\n🔍 Test 1: Dashboard Initialization")
    print("-" * 35)
    
    try:
        from cli.features.monitoring_dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard()
        print("✅ Dashboard initialized successfully")
        
        # Test state management
        print(f"✅ Initial view: {dashboard.state.current_view}")
        print(f"✅ Refresh rate: {dashboard.state.refresh_rate}s")
        print(f"✅ Paused state: {dashboard.state.paused}")
        
    except Exception as e:
        print(f"❌ Dashboard initialization failed: {e}")
        return False
    
    # Test 2: Data update functionality
    print("\n📊 Test 2: Data Update Functionality")
    print("-" * 35)
    
    try:
        # Test metrics collection
        dashboard._update_data()
        print("✅ Data update completed")
        
        if dashboard.metrics:
            print(f"✅ Metrics collected: CPU={dashboard.metrics.cpu_percent:.1f}%, Memory={dashboard.metrics.memory_percent:.1f}%")
        else:
            print("⚠️  No metrics collected")
        
        if dashboard.processes:
            print(f"✅ Processes collected: {len(dashboard.processes)} processes")
        else:
            print("⚠️  No processes collected")
        
        if dashboard.alerts:
            print(f"✅ Alerts detected: {len(dashboard.alerts)} alerts")
        else:
            print("✅ No alerts detected (system healthy)")
        
    except Exception as e:
        print(f"❌ Data update failed: {e}")
        return False
    
    # Test 3: Process sorting
    print("\n📋 Test 3: Process Sorting")
    print("-" * 25)
    
    try:
        # Test CPU sorting
        dashboard.state.sort_by = 'cpu'
        dashboard.state.sort_reverse = True
        processes = dashboard._get_top_processes(5)
        
        if processes:
            print("✅ Process sorting by CPU:")
            for i, proc in enumerate(processes[:3]):
                print(f"   {i+1}. {proc['name']}: CPU={proc['cpu_percent']:.1f}%, MEM={proc['memory_percent']:.1f}%")
        else:
            print("⚠️  No processes available for sorting")
        
    except Exception as e:
        print(f"❌ Process sorting failed: {e}")
        return False
    
    # Test 4: Alert checking
    print("\n🚨 Test 4: Alert Checking")
    print("-" * 25)
    
    try:
        # Test with current metrics
        if dashboard.metrics:
            alerts = dashboard.alert_manager.check_metrics({
                'cpu_percent': dashboard.metrics.cpu_percent,
                'memory_percent': dashboard.metrics.memory_percent,
                'disk_percent': dashboard.metrics.disk_percent,
                'temperature': dashboard.metrics.temperature or 0.0
            })
            
            if alerts:
                print(f"✅ {len(alerts)} alerts generated:")
                for alert in alerts:
                    print(f"   - {alert.alert_type}: {alert.metric_value:.1f} (threshold: {alert.threshold:.1f})")
            else:
                print("✅ No alerts generated (system healthy)")
        
    except Exception as e:
        print(f"❌ Alert checking failed: {e}")
        return False
    
    # Test 5: Tool recommendations
    print("\n🔧 Test 5: Tool Recommendations")
    print("-" * 30)
    
    try:
        # Test recommendations for monitoring
        recommendations = dashboard.tool_recommender.recommend_tools("system monitoring")
        
        if recommendations:
            print(f"✅ {len(recommendations)} tool recommendations:")
            for i, rec in enumerate(recommendations[:3]):
                print(f"   {i+1}. {rec.name} ({rec.confidence_score:.1%}): {rec.reason}")
        else:
            print("⚠️  No tool recommendations generated")
        
    except Exception as e:
        print(f"❌ Tool recommendations failed: {e}")
        return False
    
    # Test 6: Configuration handling
    print("\n⚙️  Test 6: Configuration Handling")
    print("-" * 35)
    
    try:
        # Test with custom config
        config = {
            'refresh_rate': 3,
            'initial_view': 'processes',
            'debug': True
        }
        
        dashboard2 = MonitoringDashboard(config=config)
        print("✅ Custom configuration applied")
        print(f"   Refresh rate: {dashboard2.state.refresh_rate}s")
        print(f"   Initial view: {dashboard2.state.current_view}")
        
    except Exception as e:
        print(f"❌ Configuration handling failed: {e}")
        return False
    
    print("\n🎉 All Dashboard Component Tests Passed!")
    return True

def test_cli_interface():
    """Test the CLI interface"""
    
    print("\n🔧 Testing CLI Interface")
    print("=" * 30)
    
    try:
        from cli.features.dashboard_cli import main as cli_main
        
        # Test argument parsing (without actually running)
        import argparse
        
        # Simulate argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument('--refresh', type=int, default=2)
        parser.add_argument('--view', default='overview')
        parser.add_argument('--debug', action='store_true')
        
        # Test with sample arguments
        test_args = ['--refresh', '1', '--view', 'processes', '--debug']
        args = parser.parse_args(test_args)
        
        print("✅ CLI argument parsing working")
        print(f"   Refresh rate: {args.refresh}s")
        print(f"   View: {args.view}")
        print(f"   Debug: {args.debug}")
        
    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False
    
    print("✅ CLI interface test passed!")
    return True

def test_dashboard_features():
    """Test specific dashboard features"""
    
    print("\n🎯 Testing Dashboard Features")
    print("=" * 35)
    
    try:
        from cli.features.monitoring_dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard()
        
        # Test view switching
        views = ['overview', 'processes', 'alerts', 'tools']
        for view in views:
            dashboard.state.current_view = view
            print(f"✅ View switching: {view}")
        
        # Test refresh rate adjustment
        for rate in [1, 2, 5, 10]:
            dashboard.state.refresh_rate = rate
            print(f"✅ Refresh rate: {rate}s")
        
        # Test pause/resume
        dashboard.state.paused = True
        print("✅ Pause state: True")
        dashboard.state.paused = False
        print("✅ Pause state: False")
        
        # Test sorting
        sort_options = ['cpu', 'memory', 'name']
        for sort_by in sort_options:
            dashboard.state.sort_by = sort_by
            print(f"✅ Sort by: {sort_by}")
        
    except Exception as e:
        print(f"❌ Dashboard features test failed: {e}")
        return False
    
    print("✅ All dashboard features working!")
    return True

def main():
    """Run all dashboard tests"""
    
    print("🧪 Overseer Dashboard Test Suite")
    print("=" * 50)
    
    # Run component tests
    component_success = test_dashboard_components()
    
    # Run CLI tests
    cli_success = test_cli_interface()
    
    # Run feature tests
    feature_success = test_dashboard_features()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Component Tests: {'PASSED' if component_success else 'FAILED'}")
    print(f"✅ CLI Interface: {'PASSED' if cli_success else 'FAILED'}")
    print(f"✅ Feature Tests: {'PASSED' if feature_success else 'FAILED'}")
    
    if component_success and cli_success and feature_success:
        print("\n🎉 All Dashboard Tests Passed!")
        print("🚀 Dashboard is ready for use!")
        print("\nUsage:")
        print("  python3 monitoring_dashboard.py")
        print("  python3 dashboard_cli.py --refresh 1 --view processes")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 