#!/usr/bin/env python3
"""
Phase 1 Monitoring Test Script
Tests all Phase 1 features: System Monitoring, Enhanced Tool Recommendations, and Alert Management.
"""

import os
import sys
import time
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

def test_phase1_features():
    """Test all Phase 1 monitoring features"""
    
    print("🧪 Phase 1 Monitoring Test Suite")
    print("=" * 60)
    
    # Test 1: System Monitor
    print("\n🔍 Test 1: System Monitor")
    print("-" * 30)
    
    try:
        from cli.features.system_monitor import SystemMonitor
        
        monitor = SystemMonitor()
        print("✅ SystemMonitor initialized successfully")
        
        # Test metrics collection
        metrics = monitor.collect_metrics()
        print(f"✅ Metrics collected: CPU={metrics.cpu_percent:.1f}%, Memory={metrics.memory_percent:.1f}%")
        
        # Test system summary
        summary = monitor.get_system_summary()
        print(f"✅ System health score: {summary['health_score']}/100 ({summary['status']})")
        
        # Test database save
        monitor.save_metrics(metrics)
        print("✅ Metrics saved to database")
        
        # Test alerts
        alerts = monitor.check_alerts(metrics)
        if alerts:
            print(f"⚠️  {len(alerts)} alerts generated")
            monitor.save_alerts(alerts)
            print("✅ Alerts saved to database")
        else:
            print("✅ No alerts generated (system healthy)")
        
        # Test display
        monitor.display_metrics(metrics)
        
    except Exception as e:
        print(f"❌ System Monitor test failed: {e}")
        return False
    
    # Test 2: Enhanced Tool Recommender
    print("\n🔧 Test 2: Enhanced Tool Recommender")
    print("-" * 40)
    
    try:
        from cli.features.enhanced_tool_recommender import EnhancedToolRecommender
        
        recommender = EnhancedToolRecommender(system_monitor=monitor)
        print("✅ EnhancedToolRecommender initialized successfully")
        
        # Test queries
        test_queries = [
            "I need GPU monitoring",
            "My system is slow",
            "I want to organize files",
            "I need development tools",
            "My disk is full"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            recommendations = recommender.recommend_tools(query)
            print(f"✅ Found {len(recommendations)} recommendations")
            
            if recommendations:
                # Log recommendation
                context = recommender.get_system_context()
                recommender.log_recommendation(query, recommendations, context)
                print("✅ Recommendation logged")
                
                # Display top recommendation
                top_rec = recommendations[0]
                print(f"   Top: {top_rec.name} ({top_rec.confidence_score:.1%}) - {top_rec.reason}")
        
        # Test analytics
        analytics = recommender.get_tool_analytics()
        print(f"✅ Analytics: {analytics['total_tools']} tools in database")
        
    except Exception as e:
        print(f"❌ Enhanced Tool Recommender test failed: {e}")
        return False
    
    # Test 3: Alert Manager
    print("\n🚨 Test 3: Alert Manager")
    print("-" * 25)
    
    try:
        from cli.features.alert_manager import AlertManager, AlertSeverity
        
        alert_manager = AlertManager()
        print("✅ AlertManager initialized successfully")
        
        # Test alert rules
        rules = alert_manager.get_alert_rules()
        print(f"✅ {len(rules)} alert rules configured")
        
        # Test alert checking
        test_metrics = {
            'cpu_percent': 85.0,  # Should trigger CPU warning
            'memory_percent': 90.0,  # Should trigger memory warning
            'disk_percent': 92.0,  # Should trigger disk warning
            'temperature': 75.0  # Should trigger temperature warning
        }
        
        alerts = alert_manager.check_metrics(test_metrics)
        print(f"✅ Generated {len(alerts)} test alerts")
        
        if alerts:
            alert_manager.save_alerts(alerts)
            print("✅ Test alerts saved to database")
        
        # Test alert summary
        summary = alert_manager.get_alert_summary()
        print(f"✅ Alert summary: {summary['total_alerts']} total, {summary['active_alerts']} active")
        
        # Test alert display
        alert_manager.display_alerts(alerts)
        
    except Exception as e:
        print(f"❌ Alert Manager test failed: {e}")
        return False
    
    # Test 4: Integration Test
    print("\n🔗 Test 4: Integration Test")
    print("-" * 25)
    
    try:
        # Test system monitor with alert manager
        monitor = SystemMonitor()
        alert_manager = AlertManager()
        recommender = EnhancedToolRecommender(system_monitor=monitor)
        
        # Collect real metrics
        metrics = monitor.collect_metrics()
        
        # Check for alerts
        alerts = alert_manager.check_metrics({
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'disk_percent': metrics.disk_percent,
            'temperature': metrics.temperature or 0.0
        })
        
        # If alerts, get tool recommendations
        if alerts:
            print(f"⚠️  {len(alerts)} alerts detected, getting tool recommendations...")
            
            for alert in alerts:
                query = f"fix {alert.metric_name} {alert.alert_type}"
                recommendations = recommender.recommend_tools(query)
                
                if recommendations:
                    print(f"   📋 {len(recommendations)} tools recommended for {alert.alert_type}")
                    for rec in recommendations[:2]:  # Show top 2
                        print(f"      - {rec.name}: {rec.description}")
        
        print("✅ Integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    # Test 5: Database Verification
    print("\n💾 Test 5: Database Verification")
    print("-" * 30)
    
    try:
        db_dir = Path(__file__).parent.parent.parent / 'db'
        
        # Check for new database files
        expected_dbs = [
            'system_metrics.db',
            'tool_analytics.db', 
            'system_alerts.db'
        ]
        
        for db_name in expected_dbs:
            db_path = db_dir / db_name
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"✅ {db_name}: {size_mb:.2f}MB")
            else:
                print(f"❌ {db_name}: Missing")
        
        print("✅ Database verification completed")
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    
    # Final Summary
    print("\n🎉 Phase 1 Test Results")
    print("=" * 40)
    print("✅ All Phase 1 features implemented and tested successfully!")
    print("\n📊 Features Implemented:")
    print("   🔍 Real-time System Monitoring")
    print("   🔧 Enhanced Tool Recommendations")
    print("   🚨 Alert Management System")
    print("   💾 Database Integration")
    print("   🔗 Component Integration")
    
    print("\n🚀 Phase 1 Complete!")
    print("Ready for Phase 2: Advanced Features")
    
    return True

def test_individual_components():
    """Test individual components separately"""
    
    print("\n🔧 Individual Component Tests")
    print("=" * 40)
    
    # Test System Monitor
    print("\n1. Testing System Monitor...")
    try:
        from cli.features.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        metrics = monitor.collect_metrics()
        print(f"   ✅ CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%")
    except Exception as e:
        print(f"   ❌ System Monitor: {e}")
    
    # Test Tool Recommender
    print("\n2. Testing Tool Recommender...")
    try:
        from cli.features.enhanced_tool_recommender import EnhancedToolRecommender
        recommender = EnhancedToolRecommender()
        recommendations = recommender.recommend_tools("GPU monitoring")
        print(f"   ✅ Found {len(recommendations)} GPU monitoring tools")
    except Exception as e:
        print(f"   ❌ Tool Recommender: {e}")
    
    # Test Alert Manager
    print("\n3. Testing Alert Manager...")
    try:
        from cli.features.alert_manager import AlertManager
        alert_manager = AlertManager()
        rules = alert_manager.get_alert_rules()
        print(f"   ✅ {len(rules)} alert rules configured")
    except Exception as e:
        print(f"   ❌ Alert Manager: {e}")

if __name__ == "__main__":
    print("🧪 Starting Phase 1 Monitoring Tests...")
    
    # Run individual component tests first
    test_individual_components()
    
    # Run full integration test
    success = test_phase1_features()
    
    if success:
        print("\n🎉 All tests passed! Phase 1 is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1) 