#!/usr/bin/env python3
"""
CLI interface for the Overseer Monitoring Dashboard
Provides command-line options to launch the dashboard with different configurations.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Overseer System Monitor Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  overseer-dashboard                    # Launch dashboard with default settings
  overseer-dashboard --refresh 1       # Update every 1 second
  overseer-dashboard --view processes  # Start in processes view
  overseer-dashboard --config config.json  # Use custom config file
        """
    )
    
    parser.add_argument(
        '--refresh', '-r',
        type=int,
        default=2,
        help='Refresh rate in seconds (default: 2)'
    )
    
    parser.add_argument(
        '--view', '-v',
        choices=['overview', 'processes', 'alerts', 'tools'],
        default='overview',
        help='Initial view (default: overview)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--no-colors', '-n',
        action='store_true',
        help='Disable colors (for compatibility)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='Overseer Dashboard v26.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.refresh < 1 or args.refresh > 10:
        print("Error: Refresh rate must be between 1 and 10 seconds")
        sys.exit(1)
    
    # Load configuration
    config = {}
    if args.config:
        try:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    # Add CLI arguments to config
    config.update({
        'refresh_rate': args.refresh,
        'initial_view': args.view,
        'no_colors': args.no_colors,
        'debug': args.debug
    })
    
    # Check dependencies
    try:
        import psutil
    except ImportError:
        print("Error: psutil is required. Install with: pip install psutil")
        sys.exit(1)
    
    try:
        import curses
    except ImportError:
        print("Error: curses is required for the dashboard interface")
        print("On Windows, install windows-curses: pip install windows-curses")
        sys.exit(1)
    
    # Launch dashboard
    try:
        from cli.features.monitoring_dashboard import MonitoringDashboard
        
        print("🚀 Starting Overseer System Monitor Dashboard...")
        print(f"   Refresh rate: {args.refresh}s")
        print(f"   Initial view: {args.view}")
        print("   Press 'h' for help, 'q' to quit")
        print("   Press Ctrl+C to exit")
        print()
        
        dashboard = MonitoringDashboard(config=config)
        
        # Set initial state from config
        if 'initial_view' in config:
            dashboard.state.current_view = config['initial_view']
        if 'refresh_rate' in config:
            dashboard.state.refresh_rate = config['refresh_rate']
        
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 