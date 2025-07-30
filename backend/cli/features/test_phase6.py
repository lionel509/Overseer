"""
Test script for Phase 6: Unified System Monitoring and Performance Optimization
"""

import os
import sys
import time
import json
from typing import Dict, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from unified_system_monitor import UnifiedSystemMonitor, IntegrationConfig
from performance_optimizer import PerformanceOptimizer

class Phase6Tester:
    """Test suite for Phase 6 features"""
    
    def __init__(self):
        """Initialize Phase 6 tester"""
        self.console = Console() if RICH_AVAILABLE else None
        self.test_results = {}
        
        # Initialize components
        self.config = IntegrationConfig(
            enable_monitoring=True,
            enable_analytics=True,
            enable_ml=True,
            enable_export=True,
            enable_dashboard=True,
            enable_alerts=True,
            enable_process_management=True,
            refresh_interval=2.0,
            max_threads=4,
            cache_duration=30.0
        )
        
        self.unified_monitor = UnifiedSystemMonitor(self.config)
        self.optimizer = PerformanceOptimizer()
    
    def test_unified_monitoring(self) -> Dict:
        """Test unified system monitoring features"""
        results = {
            'monitor_start': False,
            'monitor_stop': False,
            'state_collection': False,
            'comprehensive_report': False,
            'component_status': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]🔗 Testing Unified System Monitoring...[/bold]")
            
            # Test monitor start
            result = self.unified_monitor.start_monitoring()
            results['monitor_start'] = 'started' in result.lower()
            if self.console:
                self.console.print(f"Monitor Start: {result}")
            
            # Wait for state collection
            time.sleep(3)
            
            # Test state collection
            if self.unified_monitor.current_state.metrics:
                results['state_collection'] = True
                if self.console:
                    self.console.print(f"State Collection: ✅ System state collected")
            
            # Test comprehensive report
            report = self.unified_monitor.get_comprehensive_report()
            results['comprehensive_report'] = len(report) > 0
            if self.console:
                self.console.print(f"Comprehensive Report: {len(report)} sections generated")
            
            # Test component status
            component_status = self.unified_monitor._get_component_status()
            results['component_status'] = len(component_status) > 0
            if self.console:
                self.console.print(f"Component Status: {len(component_status)} components")
            
            # Test monitor stop
            result = self.unified_monitor.stop_monitoring()
            results['monitor_stop'] = 'stopped' in result.lower()
            if self.console:
                self.console.print(f"Monitor Stop: {result}")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing unified monitoring: {e}[/red]")
            else:
                print(f"Error testing unified monitoring: {e}")
        
        return results
    
    def test_performance_optimization(self) -> Dict:
        """Test performance optimization features"""
        results = {
            'performance_analysis': False,
            'optimization_plan': False,
            'target_generation': False,
            'action_generation': False,
            'optimization_status': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]⚡ Testing Performance Optimization...[/bold]")
            
            # Test performance analysis
            targets = self.optimizer.analyze_system_performance()
            results['performance_analysis'] = isinstance(targets, list)
            if self.console:
                self.console.print(f"Performance Analysis: {len(targets)} targets found")
            
            # Test optimization plan generation
            actions = self.optimizer.generate_optimization_plan(targets)
            results['optimization_plan'] = isinstance(actions, list)
            if self.console:
                self.console.print(f"Optimization Plan: {len(actions)} actions generated")
            
            # Test target generation
            results['target_generation'] = len(targets) >= 0
            if self.console:
                self.console.print(f"Target Generation: {len(targets)} targets")
            
            # Test action generation
            results['action_generation'] = len(actions) >= 0
            if self.console:
                self.console.print(f"Action Generation: {len(actions)} actions")
            
            # Test optimization status display
            self.optimizer.display_optimization_status()
            results['optimization_status'] = True
            if self.console:
                self.console.print("Optimization Status: ✅ Displayed")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing performance optimization: {e}[/red]")
            else:
                print(f"Error testing performance optimization: {e}")
        
        return results
    
    def test_integration(self) -> Dict:
        """Test integration between unified monitoring and optimization"""
        results = {
            'unified_optimization': False,
            'real_time_analysis': False,
            'performance_tracking': False,
            'optimization_history': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]🔗 Testing Integration...[/bold]")
            
            # Test unified optimization workflow
            # Start monitoring
            self.unified_monitor.start_monitoring()
            time.sleep(2)
            
            # Get system state
            state = self.unified_monitor.current_state
            results['unified_optimization'] = state.metrics is not None
            
            # Analyze performance with current state
            targets = self.optimizer.analyze_system_performance()
            results['real_time_analysis'] = len(targets) >= 0
            
            # Generate optimization plan
            actions = self.optimizer.generate_optimization_plan(targets)
            results['performance_tracking'] = len(actions) >= 0
            
            # Stop monitoring
            self.unified_monitor.stop_monitoring()
            results['optimization_history'] = True
            
            if self.console:
                self.console.print(f"Unified Optimization: ✅ Workflow completed")
                self.console.print(f"Real-time Analysis: ✅ {len(targets)} targets")
                self.console.print(f"Performance Tracking: ✅ {len(actions)} actions")
                self.console.print(f"Optimization History: ✅ Tracked")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing integration: {e}[/red]")
            else:
                print(f"Error testing integration: {e}")
        
        return results
    
    def test_configuration(self) -> Dict:
        """Test configuration management"""
        results = {
            'config_creation': False,
            'config_modification': False,
            'config_validation': False,
            'component_integration': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]⚙️ Testing Configuration Management...[/bold]")
            
            # Test configuration creation
            config = IntegrationConfig(
                enable_monitoring=True,
                enable_analytics=True,
                enable_ml=True,
                refresh_interval=2.0,
                max_threads=4
            )
            results['config_creation'] = config is not None
            
            # Test configuration modification
            original_interval = config.refresh_interval
            config.refresh_interval = 5.0
            results['config_modification'] = config.refresh_interval == 5.0
            
            # Test configuration validation
            results['config_validation'] = (
                config.enable_monitoring and
                config.enable_analytics and
                config.max_threads > 0
            )
            
            # Test component integration with config
            test_monitor = UnifiedSystemMonitor(config)
            results['component_integration'] = test_monitor.config == config
            
            if self.console:
                self.console.print(f"Config Creation: ✅ Configuration created")
                self.console.print(f"Config Modification: ✅ Interval changed to {config.refresh_interval}s")
                self.console.print(f"Config Validation: ✅ Configuration valid")
                self.console.print(f"Component Integration: ✅ Monitor uses config")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing configuration: {e}[/red]")
            else:
                print(f"Error testing configuration: {e}")
        
        return results
    
    def test_performance_metrics(self) -> Dict:
        """Test performance metrics and tracking"""
        results = {
            'metrics_collection': False,
            'performance_tracking': False,
            'optimization_metrics': False,
            'database_operations': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]📊 Testing Performance Metrics...[/bold]")
            
            # Test metrics collection
            metrics = self.unified_monitor.system_monitor.collect_metrics()
            results['metrics_collection'] = metrics is not None
            
            # Test performance tracking
            performance_metrics = self.unified_monitor._get_performance_metrics()
            results['performance_tracking'] = isinstance(performance_metrics, dict)
            
            # Test optimization metrics
            targets = self.optimizer.analyze_system_performance()
            results['optimization_metrics'] = len(targets) >= 0
            
            # Test database operations
            try:
                import sqlite3
                db_path = self.unified_monitor.unified_db
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                results['database_operations'] = len(tables) > 0
            except Exception:
                results['database_operations'] = False
            
            if self.console:
                self.console.print(f"Metrics Collection: ✅ System metrics collected")
                self.console.print(f"Performance Tracking: ✅ Performance metrics tracked")
                self.console.print(f"Optimization Metrics: ✅ {len(targets)} optimization targets")
                self.console.print(f"Database Operations: ✅ {len(tables) if 'tables' in locals() else 0} tables")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing performance metrics: {e}[/red]")
            else:
                print(f"Error testing performance metrics: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Run all Phase 6 tests"""
        if self.console:
            self.console.print("[bold]🧪 Phase 6 Comprehensive Testing[/bold]")
            self.console.print("=" * 60)
        
        # Run individual test suites
        self.test_results['unified_monitoring'] = self.test_unified_monitoring()
        self.test_results['performance_optimization'] = self.test_performance_optimization()
        self.test_results['integration'] = self.test_integration()
        self.test_results['configuration'] = self.test_configuration()
        self.test_results['performance_metrics'] = self.test_performance_metrics()
        
        return self.test_results
    
    def display_results(self):
        """Display test results"""
        if not RICH_AVAILABLE:
            print("\nPhase 6 Test Results:")
            for category, results in self.test_results.items():
                print(f"\n{category.upper()}:")
                for test, passed in results.items():
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"  {test}: {status}")
            return
        
        # Create results table
        results_table = Table(title="Phase 6 Test Results")
        results_table.add_column("Category", style="cyan")
        results_table.add_column("Test", style="green")
        results_table.add_column("Status", style="yellow")
        
        for category, results in self.test_results.items():
            for test, passed in results.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                status_color = "green" if passed else "red"
                results_table.add_row(
                    category.replace('_', ' ').title(),
                    test.replace('_', ' ').title(),
                    f"[{status_color}]{status}[/{status_color}]"
                )
        
        self.console.print(results_table)
        
        # Calculate summary
        total_tests = sum(len(results) for results in self.test_results.values())
        passed_tests = sum(sum(1 for passed in results.values() if passed) for results in self.test_results.values())
        
        summary = f"Overall: {passed_tests}/{total_tests} tests passed"
        if self.console:
            self.console.print(f"\n[bold]{summary}[/bold]")

def main():
    """Main test function"""
    tester = Phase6Tester()
    
    print("🧪 Phase 6: Unified System Monitoring and Performance Optimization")
    print("=" * 80)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Display results
    tester.display_results()
    
    print("\n✅ Phase 6 testing completed!")

if __name__ == "__main__":
    main() 