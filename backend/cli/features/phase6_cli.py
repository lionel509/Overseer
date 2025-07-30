"""
Phase 6 CLI Interface
Provides command-line access to unified system monitoring and performance optimization features.
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

from unified_system_monitor import UnifiedSystemMonitor, IntegrationConfig
from performance_optimizer import PerformanceOptimizer

class Phase6CLI:
    """Phase 6 CLI interface for unified system monitoring and optimization"""
    
    def __init__(self):
        """Initialize Phase 6 CLI"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Initialize components
        self.config = IntegrationConfig(
            enable_monitoring=True,
            enable_analytics=True,
            enable_ml=True,
            enable_export=True,
            enable_dashboard=True,
            enable_alerts=True,
            enable_process_management=True,
            refresh_interval=3.0,
            max_threads=4,
            cache_duration=30.0
        )
        
        self.unified_monitor = UnifiedSystemMonitor(self.config)
        self.optimizer = PerformanceOptimizer()
        
        # CLI options
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Phase 6: Unified System Monitoring and Performance Optimization",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start unified monitoring
  python phase6_cli.py monitor --start --auto-optimize
  
  # Stop unified monitoring
  python phase6_cli.py monitor --stop
  
  # Get unified status
  python phase6_cli.py status --detailed
  
  # Analyze performance
  python phase6_cli.py optimize --analyze
  
  # Generate optimization plan
  python phase6_cli.py optimize --plan
  
  # Execute optimizations (demo mode)
  python phase6_cli.py optimize --execute --demo
  
  # Get comprehensive report
  python phase6_cli.py report --comprehensive
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Unified system monitoring')
        monitor_parser.add_argument('--start', action='store_true', 
                                 help='Start unified monitoring')
        monitor_parser.add_argument('--stop', action='store_true', 
                                 help='Stop unified monitoring')
        monitor_parser.add_argument('--auto-optimize', action='store_true', 
                                 help='Enable auto-optimization')
        monitor_parser.add_argument('--refresh-interval', type=float, default=3.0, 
                                 help='Monitoring refresh interval (seconds)')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        status_parser.add_argument('--detailed', action='store_true', 
                                help='Show detailed status information')
        status_parser.add_argument('--components', action='store_true', 
                                help='Show component status')
        
        # Optimize command
        optimize_parser = subparsers.add_parser('optimize', help='Performance optimization')
        optimize_parser.add_argument('--analyze', action='store_true', 
                                  help='Analyze system performance')
        optimize_parser.add_argument('--plan', action='store_true', 
                                  help='Generate optimization plan')
        optimize_parser.add_argument('--execute', action='store_true', 
                                  help='Execute optimizations')
        optimize_parser.add_argument('--demo', action='store_true', 
                                  help='Demo mode (no actual execution)')
        optimize_parser.add_argument('--auto', action='store_true', 
                                  help='Auto-optimize based on thresholds')
        
        # Report command
        report_parser = subparsers.add_parser('report', help='Generate reports')
        report_parser.add_argument('--comprehensive', action='store_true', 
                                help='Generate comprehensive system report')
        report_parser.add_argument('--optimization', action='store_true', 
                                help='Generate optimization report')
        report_parser.add_argument('--performance', action='store_true', 
                                help='Generate performance report')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument('--show', action='store_true', 
                                help='Show current configuration')
        config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), 
                                help='Set configuration value')
        config_parser.add_argument('--reset', action='store_true', 
                                help='Reset to default configuration')
        
        return parser
    
    def run(self, args: List[str] = None):
        """Run the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return
        
        try:
            if parsed_args.command == 'monitor':
                self._handle_monitor(parsed_args)
            elif parsed_args.command == 'status':
                self._handle_status(parsed_args)
            elif parsed_args.command == 'optimize':
                self._handle_optimize(parsed_args)
            elif parsed_args.command == 'report':
                self._handle_report(parsed_args)
            elif parsed_args.command == 'config':
                self._handle_config(parsed_args)
            else:
                self.parser.print_help()
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
            else:
                print(f"Error: {e}")
    
    def _handle_monitor(self, args):
        """Handle monitor command"""
        if args.start:
            if self.console:
                self.console.print("[bold]🚀 Starting unified system monitoring...[/bold]")
            
            # Update configuration if provided
            if args.refresh_interval:
                self.config.refresh_interval = args.refresh_interval
            
            if args.auto_optimize:
                self.optimizer.auto_optimize = True
            
            result = self.unified_monitor.start_monitoring()
            if self.console:
                self.console.print(f"[green]{result}[/green]")
            else:
                print(result)
        
        elif args.stop:
            if self.console:
                self.console.print("[bold]🛑 Stopping unified system monitoring...[/bold]")
            
            result = self.unified_monitor.stop_monitoring()
            if self.console:
                self.console.print(f"[yellow]{result}[/yellow]")
            else:
                print(result)
    
    def _handle_status(self, args):
        """Handle status command"""
        if args.detailed:
            if self.console:
                self.console.print("[bold]📊 Detailed System Status[/bold]")
                self.unified_monitor.display_unified_status()
                
                if args.components:
                    self.console.print("\n[bold]🔧 Component Status[/bold]")
                    component_status = self.unified_monitor._get_component_status()
                    for component, status in component_status.items():
                        status_color = "green" if status == 'active' else "red"
                        self.console.print(f"[{status_color}]{component}: {status}[/{status_color}]")
            else:
                print("Detailed system status:")
                self.unified_monitor.display_unified_status()
        else:
            if self.console:
                self.console.print("[bold]📊 System Status[/bold]")
                self.unified_monitor.display_unified_status()
            else:
                print("System status:")
                self.unified_monitor.display_unified_status()
    
    def _handle_optimize(self, args):
        """Handle optimize command"""
        if args.analyze:
            if self.console:
                self.console.print("[bold]🔍 Analyzing system performance...[/bold]")
            
            targets = self.optimizer.analyze_system_performance()
            
            if self.console:
                self.console.print(f"[green]Found {len(targets)} optimization targets[/green]")
                for target in targets:
                    priority_color = "red" if target.priority == 'high' else "yellow"
                    self.console.print(f"[{priority_color}]{target.description}[/{priority_color]}")
            else:
                print(f"Found {len(targets)} optimization targets")
                for target in targets:
                    print(f"  - {target.description} (Priority: {target.priority})")
        
        elif args.plan:
            if self.console:
                self.console.print("[bold]📋 Generating optimization plan...[/bold]")
            
            # First analyze, then generate plan
            targets = self.optimizer.analyze_system_performance()
            actions = self.optimizer.generate_optimization_plan(targets)
            
            if self.console:
                self.console.print(f"[green]Generated {len(actions)} optimization actions[/green]")
                for action in actions:
                    priority_color = "red" if action.priority == 'high' else "yellow"
                    self.console.print(f"[{priority_color}]{action.description}[/{priority_color]}")
            else:
                print(f"Generated {len(actions)} optimization actions")
                for action in actions:
                    print(f"  - {action.description} (Priority: {action.priority})")
        
        elif args.execute:
            if self.console:
                self.console.print("[bold]⚡ Executing optimizations...[/bold]")
            
            # Generate and execute optimizations
            targets = self.optimizer.analyze_system_performance()
            actions = self.optimizer.generate_optimization_plan(targets)
            
            if args.demo:
                if self.console:
                    self.console.print("[yellow]Demo mode - not actually executing optimizations[/yellow]")
                    for action in actions[:5]:  # Show first 5 actions
                        self.console.print(f"[blue]Would execute: {action.description}[/blue]")
                else:
                    print("Demo mode - not actually executing optimizations")
                    for action in actions[:5]:
                        print(f"  Would execute: {action.description}")
            else:
                results = self.optimizer.execute_optimization_actions(actions)
                
                if self.console:
                    self.console.print(f"[green]Optimization completed: {results['successful']} successful, {results['failed']} failed[/green]")
                    self.console.print(f"[blue]Total benefit: {results['total_benefit']:.1f}%[/blue]")
                else:
                    print(f"Optimization completed: {results['successful']} successful, {results['failed']} failed")
                    print(f"Total benefit: {results['total_benefit']:.1f}%")
        
        elif args.auto:
            if self.console:
                self.console.print("[bold]🤖 Auto-optimization mode[/bold]")
            
            # Enable auto-optimization
            self.optimizer.auto_optimize = True
            
            if self.console:
                self.console.print("[green]Auto-optimization enabled[/green]")
            else:
                print("Auto-optimization enabled")
    
    def _handle_report(self, args):
        """Handle report command"""
        if args.comprehensive:
            if self.console:
                self.console.print("[bold]📋 Generating comprehensive system report...[/bold]")
            
            report = self.unified_monitor.get_comprehensive_report()
            
            if self.console:
                self.console.print(f"[green]Comprehensive report generated with {len(report)} sections[/green]")
                self.console.print(f"[blue]System Health: {report.get('system_state', {}).get('health_score', 0):.1f}%[/blue]")
                self.console.print(f"[blue]Performance Score: {report.get('system_state', {}).get('performance_score', 0):.1f}%[/blue]")
            else:
                print(f"Comprehensive report generated with {len(report)} sections")
                print(f"System Health: {report.get('system_state', {}).get('health_score', 0):.1f}%")
                print(f"Performance Score: {report.get('system_state', {}).get('performance_score', 0):.1f}%")
        
        elif args.optimization:
            if self.console:
                self.console.print("[bold]📊 Generating optimization report...[/bold]")
            
            # Generate optimization report
            targets = self.optimizer.analyze_system_performance()
            actions = self.optimizer.generate_optimization_plan(targets)
            
            report = {
                'targets_found': len(targets),
                'actions_generated': len(actions),
                'high_priority_actions': len([a for a in actions if a.priority == 'high']),
                'estimated_total_benefit': sum(a.estimated_benefit for a in actions)
            }
            
            if self.console:
                self.console.print(f"[green]Optimization report generated[/green]")
                self.console.print(f"[blue]Targets found: {report['targets_found']}[/blue]")
                self.console.print(f"[blue]Actions generated: {report['actions_generated']}[/blue]")
                self.console.print(f"[blue]Estimated benefit: {report['estimated_total_benefit']:.1f}%[/blue]")
            else:
                print(f"Optimization report generated")
                print(f"Targets found: {report['targets_found']}")
                print(f"Actions generated: {report['actions_generated']}")
                print(f"Estimated benefit: {report['estimated_total_benefit']:.1f}%")
        
        elif args.performance:
            if self.console:
                self.console.print("[bold]📈 Generating performance report...[/bold]")
            
            # Display performance status
            self.optimizer.display_optimization_status()
    
    def _handle_config(self, args):
        """Handle config command"""
        if args.show:
            if self.console:
                self.console.print("[bold]⚙️ Current Configuration[/bold]")
                
                config_table = Table()
                config_table.add_column("Setting", style="cyan")
                config_table.add_column("Value", style="green")
                
                config_table.add_row("Enable Monitoring", str(self.config.enable_monitoring))
                config_table.add_row("Enable Analytics", str(self.config.enable_analytics))
                config_table.add_row("Enable ML", str(self.config.enable_ml))
                config_table.add_row("Enable Export", str(self.config.enable_export))
                config_table.add_row("Enable Dashboard", str(self.config.enable_dashboard))
                config_table.add_row("Enable Alerts", str(self.config.enable_alerts))
                config_table.add_row("Enable Process Management", str(self.config.enable_process_management))
                config_table.add_row("Refresh Interval", f"{self.config.refresh_interval}s")
                config_table.add_row("Max Threads", str(self.config.max_threads))
                config_table.add_row("Cache Duration", f"{self.config.cache_duration}s")
                
                self.console.print(config_table)
            else:
                print("Current Configuration:")
                print(f"  Enable Monitoring: {self.config.enable_monitoring}")
                print(f"  Enable Analytics: {self.config.enable_analytics}")
                print(f"  Enable ML: {self.config.enable_ml}")
                print(f"  Enable Export: {self.config.enable_export}")
                print(f"  Enable Dashboard: {self.config.enable_dashboard}")
                print(f"  Enable Alerts: {self.config.enable_alerts}")
                print(f"  Enable Process Management: {self.config.enable_process_management}")
                print(f"  Refresh Interval: {self.config.refresh_interval}s")
                print(f"  Max Threads: {self.config.max_threads}")
                print(f"  Cache Duration: {self.config.cache_duration}s")
        
        elif args.set:
            key, value = args.set
            if self.console:
                self.console.print(f"[bold]⚙️ Setting {key} = {value}[/bold]")
            
            # Update configuration
            if hasattr(self.config, key):
                # Convert value to appropriate type
                current_value = getattr(self.config, key)
                if isinstance(current_value, bool):
                    new_value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    new_value = int(value)
                elif isinstance(current_value, float):
                    new_value = float(value)
                else:
                    new_value = value
                
                setattr(self.config, key, new_value)
                
                if self.console:
                    self.console.print(f"[green]Configuration updated: {key} = {new_value}[/green]")
                else:
                    print(f"Configuration updated: {key} = {new_value}")
            else:
                if self.console:
                    self.console.print(f"[red]Unknown configuration key: {key}[/red]")
                else:
                    print(f"Unknown configuration key: {key}")
        
        elif args.reset:
            if self.console:
                self.console.print("[bold]🔄 Resetting to default configuration...[/bold]")
            
            # Reset to default configuration
            self.config = IntegrationConfig()
            
            if self.console:
                self.console.print("[green]Configuration reset to defaults[/green]")
            else:
                print("Configuration reset to defaults")

def main():
    """Main function"""
    cli = Phase6CLI()
    cli.run()

if __name__ == "__main__":
    main() 