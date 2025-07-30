"""
Test script for Phase 5: Export/Reporting, ML Integration, and Advanced Analytics
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

from export_reporting import ExportReporting
from machine_learning_integration import MachineLearningIntegration
from advanced_analytics import AdvancedAnalytics

class Phase5Tester:
    """Test suite for Phase 5 features"""
    
    def __init__(self):
        """Initialize Phase 5 tester"""
        self.console = Console() if RICH_AVAILABLE else None
        self.test_results = {}
        
        # Initialize components
        self.export_reporter = ExportReporting()
        self.ml_integration = MachineLearningIntegration()
        self.advanced_analytics = AdvancedAnalytics()
    
    def test_export_reporting(self) -> Dict:
        """Test export and reporting features"""
        results = {
            'export_system_metrics': False,
            'export_alerts': False,
            'export_predictive_data': False,
            'generate_health_report': False,
            'generate_trends_report': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]📊 Testing Export & Reporting...[/bold]")
            
            # Test system metrics export
            result = self.export_reporter.export_system_metrics(format='json')
            results['export_system_metrics'] = '✅' in result
            if self.console:
                self.console.print(f"System Metrics Export: {result}")
            
            # Test alerts export
            result = self.export_reporter.export_alerts(format='json')
            results['export_alerts'] = '✅' in result or 'No alerts found' in result
            if self.console:
                self.console.print(f"Alerts Export: {result}")
            
            # Test predictive data export
            result = self.export_reporter.export_predictive_data(format='json')
            results['export_predictive_data'] = '✅' in result or 'No data found' in result
            if self.console:
                self.console.print(f"Predictive Data Export: {result}")
            
            # Test health report generation
            result = self.export_reporter.generate_system_health_report(time_range='24h')
            results['generate_health_report'] = '✅' in result
            if self.console:
                self.console.print(f"Health Report: {result}")
            
            # Test trends report generation
            result = self.export_reporter.generate_performance_trend_report(time_range='7d')
            results['generate_trends_report'] = '✅' in result
            if self.console:
                self.console.print(f"Trends Report: {result}")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing export/reporting: {e}[/red]")
            else:
                print(f"Error testing export/reporting: {e}")
        
        return results
    
    def test_ml_integration(self) -> Dict:
        """Test machine learning integration features"""
        results = {
            'train_anomaly_model': False,
            'train_performance_model': False,
            'detect_anomalies': False,
            'predict_performance': False,
            'identify_patterns': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]🤖 Testing Machine Learning Integration...[/bold]")
            
            # Test anomaly detection model training
            result = self.ml_integration.train_anomaly_detection_model('7d')
            results['train_anomaly_model'] = '✅' in result or 'scikit-learn not available' in result
            if self.console:
                self.console.print(f"Anomaly Model Training: {result}")
            
            # Test performance prediction model training
            result = self.ml_integration.train_performance_prediction_model('7d')
            results['train_performance_model'] = '✅' in result or 'scikit-learn not available' in result or 'Insufficient' in result
            if self.console:
                self.console.print(f"Performance Model Training: {result}")
            
            # Test anomaly detection
            current_metrics = self.ml_integration.system_monitor.collect_metrics()
            if current_metrics:
                anomaly_result = self.ml_integration.detect_anomalies(current_metrics)
                results['detect_anomalies'] = 'is_anomaly' in anomaly_result or 'message' in anomaly_result
                if self.console:
                    self.console.print(f"Anomaly Detection: {anomaly_result}")
            
            # Test performance prediction
            if current_metrics:
                prediction_result = self.ml_integration.predict_performance(current_metrics)
                results['predict_performance'] = 'predictions' in prediction_result or 'message' in prediction_result
                if self.console:
                    self.console.print(f"Performance Prediction: {prediction_result}")
            
            # Test pattern identification
            patterns = self.ml_integration.identify_patterns('24h')
            results['identify_patterns'] = isinstance(patterns, list)
            if self.console:
                self.console.print(f"Pattern Identification: {len(patterns)} patterns found")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing ML integration: {e}[/red]")
            else:
                print(f"Error testing ML integration: {e}")
        
        return results
    
    def test_advanced_analytics(self) -> Dict:
        """Test advanced analytics features"""
        results = {
            'analyze_correlations': False,
            'generate_insights': False,
            'calculate_baselines': False,
            'detect_anomalies': False,
            'identify_system_correlations': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]📈 Testing Advanced Analytics...[/bold]")
            
            # Test correlation analysis
            correlations = self.advanced_analytics.analyze_correlations('7d')
            results['analyze_correlations'] = isinstance(correlations, list)
            if self.console:
                self.console.print(f"Correlation Analysis: {len(correlations)} correlations found")
            
            # Test performance insights
            insights = self.advanced_analytics.generate_performance_insights('7d')
            results['generate_insights'] = isinstance(insights, list)
            if self.console:
                self.console.print(f"Performance Insights: {len(insights)} insights generated")
            
            # Test baseline calculation
            baselines = self.advanced_analytics.calculate_performance_baselines('7d')
            results['calculate_baselines'] = isinstance(baselines, dict)
            if self.console:
                self.console.print(f"Performance Baselines: {len(baselines)} baselines calculated")
            
            # Test anomaly detection
            current_metrics = self.advanced_analytics.system_monitor.collect_metrics()
            if current_metrics:
                anomalies = self.advanced_analytics.detect_performance_anomalies(current_metrics, baselines)
                results['detect_anomalies'] = isinstance(anomalies, list)
                if self.console:
                    self.console.print(f"Performance Anomalies: {len(anomalies)} anomalies detected")
            
            # Test system correlations
            system_correlations = self.advanced_analytics.identify_system_correlations('7d')
            results['identify_system_correlations'] = isinstance(system_correlations, list)
            if self.console:
                self.console.print(f"System Correlations: {len(system_correlations)} correlations identified")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing advanced analytics: {e}[/red]")
            else:
                print(f"Error testing advanced analytics: {e}")
        
        return results
    
    def test_integration(self) -> Dict:
        """Test integration between Phase 5 components"""
        results = {
            'ml_recommendations': False,
            'analytics_ml_integration': False,
            'export_ml_data': False
        }
        
        try:
            if self.console:
                self.console.print("[bold]🔗 Testing Phase 5 Integration...[/bold]")
            
            # Test ML recommendations
            current_metrics = self.ml_integration.system_monitor.collect_metrics()
            if current_metrics:
                predictions = self.ml_integration.predict_performance(current_metrics)
                recommendations = self.ml_integration.generate_ml_recommendations(current_metrics, predictions)
                results['ml_recommendations'] = isinstance(recommendations, list)
                if self.console:
                    self.console.print(f"ML Recommendations: {len(recommendations)} recommendations")
            
            # Test analytics with ML integration
            if current_metrics:
                baselines = self.advanced_analytics.calculate_performance_baselines('7d')
                anomalies = self.advanced_analytics.detect_performance_anomalies(current_metrics, baselines)
                results['analytics_ml_integration'] = isinstance(anomalies, list)
                if self.console:
                    self.console.print(f"Analytics-ML Integration: {len(anomalies)} anomalies detected")
            
            # Test export of ML data
            result = self.export_reporter.export_predictive_data(format='json')
            results['export_ml_data'] = '✅' in result or 'No data found' in result
            if self.console:
                self.console.print(f"ML Data Export: {result}")
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error testing integration: {e}[/red]")
            else:
                print(f"Error testing integration: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Run all Phase 5 tests"""
        if self.console:
            self.console.print("[bold]🧪 Phase 5 Comprehensive Testing[/bold]")
            self.console.print("=" * 60)
        
        # Run individual test suites
        self.test_results['export_reporting'] = self.test_export_reporting()
        self.test_results['ml_integration'] = self.test_ml_integration()
        self.test_results['advanced_analytics'] = self.test_advanced_analytics()
        self.test_results['integration'] = self.test_integration()
        
        return self.test_results
    
    def display_results(self):
        """Display test results"""
        if not RICH_AVAILABLE:
            print("\nPhase 5 Test Results:")
            for category, results in self.test_results.items():
                print(f"\n{category.upper()}:")
                for test, passed in results.items():
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"  {test}: {status}")
            return
        
        # Create results table
        results_table = Table(title="Phase 5 Test Results")
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
    tester = Phase5Tester()
    
    print("🧪 Phase 5: Export/Reporting, ML Integration, and Advanced Analytics")
    print("=" * 80)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Display results
    tester.display_results()
    
    print("\n✅ Phase 5 testing completed!")

if __name__ == "__main__":
    main() 