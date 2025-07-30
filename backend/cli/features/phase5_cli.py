"""
Phase 5 CLI Interface
Provides command-line access to export/reporting, ML integration, and advanced analytics features.
"""

import os
import sys
import argparse
import time
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from export_reporting import ExportReporting
from machine_learning_integration import MachineLearningIntegration
from advanced_analytics import AdvancedAnalytics

class Phase5CLI:
    """Phase 5 CLI interface for advanced system monitoring features"""
    
    def __init__(self):
        """Initialize Phase 5 CLI"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Initialize components
        self.export_reporter = ExportReporting()
        self.ml_integration = MachineLearningIntegration()
        self.advanced_analytics = AdvancedAnalytics()
        
        # CLI options
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Phase 5: Export/Reporting, ML Integration, and Advanced Analytics",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Export system metrics
  python phase5_cli.py export --type metrics --format json --time-range 24h
  
  # Generate system health report
  python phase5_cli.py report --type health --time-range 7d
  
  # Train ML models
  python phase5_cli.py ml --action train --models anomaly,performance
  
  # Analyze correlations
  python phase5_cli.py analytics --action correlations --time-range 7d
  
  # Generate insights
  python phase5_cli.py analytics --action insights --time-range 24h
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export data')
        export_parser.add_argument('--type', choices=['metrics', 'alerts', 'predictive'], 
                                 required=True, help='Data type to export')
        export_parser.add_argument('--format', choices=['json', 'csv', 'html'], 
                                 default='json', help='Export format')
        export_parser.add_argument('--time-range', choices=['1h', '6h', '24h', '7d', '30d'], 
                                 default='24h', help='Time range for export')
        
        # Report command
        report_parser = subparsers.add_parser('report', help='Generate reports')
        report_parser.add_argument('--type', choices=['health', 'trends'], 
                                 required=True, help='Report type')
        report_parser.add_argument('--time-range', choices=['1h', '6h', '24h', '7d', '30d'], 
                                 default='24h', help='Time range for report')
        report_parser.add_argument('--include-recommendations', action='store_true', 
                                 help='Include recommendations in report')
        
        # ML command
        ml_parser = subparsers.add_parser('ml', help='Machine learning operations')
        ml_parser.add_argument('--action', choices=['train', 'predict', 'status', 'patterns'], 
                             required=True, help='ML action to perform')
        ml_parser.add_argument('--models', choices=['anomaly', 'performance', 'all'], 
                             help='Models to train (comma-separated)')
        ml_parser.add_argument('--time-range', choices=['24h', '7d', '30d'], 
                             default='7d', help='Time range for training')
        
        # Analytics command
        analytics_parser = subparsers.add_parser('analytics', help='Advanced analytics')
        analytics_parser.add_argument('--action', choices=['correlations', 'insights', 'baselines', 'anomalies'], 
                                   required=True, help='Analytics action')
        analytics_parser.add_argument('--time-range', choices=['24h', '7d', '30d'], 
                                   default='7d', help='Time range for analysis')
        analytics_parser.add_argument('--threshold', type=float, default=0.7, 
                                   help='Correlation threshold')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        status_parser.add_argument('--detailed', action='store_true', 
                                help='Show detailed status information')
        
        return parser
    
    def run(self, args: List[str] = None):
        """Run the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return
        
        try:
            if parsed_args.command == 'export':
                self._handle_export(parsed_args)
            elif parsed_args.command == 'report':
                self._handle_report(parsed_args)
            elif parsed_args.command == 'ml':
                self._handle_ml(parsed_args)
            elif parsed_args.command == 'analytics':
                self._handle_analytics(parsed_args)
            elif parsed_args.command == 'status':
                self._handle_status(parsed_args)
            else:
                self.parser.print_help()
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
            else:
                print(f"Error: {e}")
    
    def _handle_export(self, args):
        """Handle export command"""
        if self.console:
            self.console.print(f"[bold]📊 Exporting {args.type} data...[/bold]")
        
        if args.type == 'metrics':
            result = self.export_reporter.export_system_metrics(format=args.format)
        elif args.type == 'alerts':
            result = self.export_reporter.export_alerts(format=args.format)
        elif args.type == 'predictive':
            result = self.export_reporter.export_predictive_data(format=args.format)
        else:
            result = f"Unknown export type: {args.type}"
        
        if self.console:
            self.console.print(f"[green]{result}[/green]")
        else:
            print(result)
    
    def _handle_report(self, args):
        """Handle report command"""
        if self.console:
            self.console.print(f"[bold]📋 Generating {args.type} report...[/bold]")
        
        if args.type == 'health':
            result = self.export_reporter.generate_system_health_report(
                time_range=args.time_range,
                include_recommendations=args.include_recommendations
            )
        elif args.type == 'trends':
            result = self.export_reporter.generate_performance_trend_report(
                time_range=args.time_range
            )
        else:
            result = f"Unknown report type: {args.type}"
        
        if self.console:
            self.console.print(f"[green]{result}[/green]")
        else:
            print(result)
    
    def _handle_ml(self, args):
        """Handle ML command"""
        if args.action == 'train':
            if self.console:
                self.console.print("[bold]🤖 Training ML models...[/bold]")
            
            models = args.models.split(',') if args.models else ['all']
            results = []
            
            for model in models:
                if model in ['anomaly', 'all']:
                    result = self.ml_integration.train_anomaly_detection_model(args.time_range)
                    results.append(f"Anomaly Detection: {result}")
                
                if model in ['performance', 'all']:
                    result = self.ml_integration.train_performance_prediction_model(args.time_range)
                    results.append(f"Performance Prediction: {result}")
            
            for result in results:
                if self.console:
                    self.console.print(f"[green]{result}[/green]")
                else:
                    print(result)
        
        elif args.action == 'predict':
            if self.console:
                self.console.print("[bold]🔮 Making ML predictions...[/bold]")
            
            # Get current metrics
            current_metrics = self.ml_integration.system_monitor.collect_metrics()
            if current_metrics:
                # Anomaly detection
                anomaly_result = self.ml_integration.detect_anomalies(current_metrics)
                if self.console:
                    self.console.print(f"[blue]Anomaly Detection:[/blue] {anomaly_result}")
                else:
                    print(f"Anomaly Detection: {anomaly_result}")
                
                # Performance prediction
                prediction_result = self.ml_integration.predict_performance(current_metrics)
                if self.console:
                    self.console.print(f"[blue]Performance Prediction:[/blue] {prediction_result}")
                else:
                    print(f"Performance Prediction: {prediction_result}")
            else:
                if self.console:
                    self.console.print("[red]No current metrics available for prediction[/red]")
                else:
                    print("No current metrics available for prediction")
        
        elif args.action == 'status':
            if self.console:
                self.console.print("[bold]📊 ML Model Status[/bold]")
                self.ml_integration.display_ml_status()
            else:
                models = self.ml_integration.get_model_status()
                print("ML Model Status:")
                for model_type, info in models.items():
                    print(f"  {model_type}: {info['status']} (Accuracy: {info['accuracy']})")
        
        elif args.action == 'patterns':
            if self.console:
                self.console.print("[bold]🔍 Identifying system patterns...[/bold]")
            
            patterns = self.ml_integration.identify_patterns(args.time_range)
            if self.console:
                self.console.print(f"[green]Found {len(patterns)} patterns[/green]")
                for pattern in patterns:
                    self.console.print(f"[blue]{pattern.description}[/blue]")
            else:
                print(f"Found {len(patterns)} patterns")
                for pattern in patterns:
                    print(f"  {pattern.description}")
    
    def _handle_analytics(self, args):
        """Handle analytics command"""
        if args.action == 'correlations':
            if self.console:
                self.console.print("[bold]📈 Analyzing correlations...[/bold]")
            
            correlations = self.advanced_analytics.analyze_correlations(args.time_range)
            strong_correlations = [c for c in correlations if c.significance == 'strong']
            
            if self.console:
                self.console.print(f"[green]Found {len(correlations)} correlations ({len(strong_correlations)} strong)[/green]")
                for corr in strong_correlations:
                    self.console.print(f"[blue]{corr.metric1} ↔ {corr.metric2}: {corr.correlation_value:.3f}[/blue]")
            else:
                print(f"Found {len(correlations)} correlations ({len(strong_correlations)} strong)")
                for corr in strong_correlations:
                    print(f"  {corr.metric1} ↔ {corr.metric2}: {corr.correlation_value:.3f}")
        
        elif args.action == 'insights':
            if self.console:
                self.console.print("[bold]💡 Generating performance insights...[/bold]")
            
            insights = self.advanced_analytics.generate_performance_insights(args.time_range)
            high_severity = [i for i in insights if i.severity in ['critical', 'high']]
            
            if self.console:
                self.console.print(f"[green]Generated {len(insights)} insights ({len(high_severity)} high-severity)[/green]")
                for insight in high_severity:
                    self.console.print(f"[red]{insight.description}[/red]")
            else:
                print(f"Generated {len(insights)} insights ({len(high_severity)} high-severity)")
                for insight in high_severity:
                    print(f"  {insight.description}")
        
        elif args.action == 'baselines':
            if self.console:
                self.console.print("[bold]📊 Calculating performance baselines...[/bold]")
            
            baselines = self.advanced_analytics.calculate_performance_baselines(args.time_range)
            
            if self.console:
                self.console.print(f"[green]Calculated {len(baselines)} baselines[/green]")
                for metric, baseline in baselines.items():
                    self.console.print(f"[blue]{metric}: Mean={baseline['mean']:.2f}, Std={baseline['std']:.2f}[/blue]")
            else:
                print(f"Calculated {len(baselines)} baselines")
                for metric, baseline in baselines.items():
                    print(f"  {metric}: Mean={baseline['mean']:.2f}, Std={baseline['std']:.2f}")
        
        elif args.action == 'anomalies':
            if self.console:
                self.console.print("[bold]🚨 Detecting performance anomalies...[/bold]")
            
            # Get current metrics
            current_metrics = self.advanced_analytics.system_monitor.collect_metrics()
            if current_metrics:
                baselines = self.advanced_analytics.calculate_performance_baselines(args.time_range)
                anomalies = self.advanced_analytics.detect_performance_anomalies(current_metrics, baselines)
                
                if self.console:
                    self.console.print(f"[green]Detected {len(anomalies)} anomalies[/green]")
                    for anomaly in anomalies:
                        self.console.print(f"[red]{anomaly['description']} (z-score: {anomaly['z_score']:.2f})[/red]")
                else:
                    print(f"Detected {len(anomalies)} anomalies")
                    for anomaly in anomalies:
                        print(f"  {anomaly['description']} (z-score: {anomaly['z_score']:.2f})")
            else:
                if self.console:
                    self.console.print("[red]No current metrics available for anomaly detection[/red]")
                else:
                    print("No current metrics available for anomaly detection")
    
    def _handle_status(self, args):
        """Handle status command"""
        if self.console:
            self.console.print("[bold]📊 Phase 5 System Status[/bold]")
            
            # Export/Reporting status
            self.console.print("\n[bold]Export & Reporting:[/bold]")
            self.export_reporter.display_export_options()
            
            # ML status
            self.console.print("\n[bold]Machine Learning:[/bold]")
            self.ml_integration.display_ml_status()
            
            # Analytics status
            self.console.print("\n[bold]Advanced Analytics:[/bold]")
            self.advanced_analytics.display_analytics_summary()
        else:
            print("Phase 5 System Status")
            print("====================")
            print("Export & Reporting: Available")
            print("Machine Learning: Available")
            print("Advanced Analytics: Available")

def main():
    """Main function"""
    cli = Phase5CLI()
    cli.run()

if __name__ == "__main__":
    main() 