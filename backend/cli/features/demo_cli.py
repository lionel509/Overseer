#!/usr/bin/env python3
"""
CLI interface for the LLM Demo Mode
Provides command-line options for running different demo scenarios.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

def main():
    """Main CLI function for demo mode"""
    parser = argparse.ArgumentParser(
        description="Overseer LLM Demo Mode - Intelligent System Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 demo_cli.py --real-analysis          # Analyze your real system
  python3 demo_cli.py --scenario high-cpu      # Run high CPU demo
  python3 demo_cli.py --scenario high-memory   # Run memory pressure demo
  python3 demo_cli.py --scenario low-disk      # Run disk space demo
  python3 demo_cli.py --scenario slow-system   # Run system slowdown demo
  python3 demo_cli.py --interactive            # Run interactive demo
  python3 demo_cli.py --all-scenarios          # Run all demo scenarios
        """
    )
    
    parser.add_argument(
        '--real-analysis', '-r',
        action='store_true',
        help='Analyze your real system with LLM advisor'
    )
    
    parser.add_argument(
        '--scenario', '-s',
        choices=['high-cpu', 'high-memory', 'low-disk', 'slow-system'],
        help='Run a specific demo scenario'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run interactive step-by-step demo'
    )
    
    parser.add_argument(
        '--all-scenarios', '-a',
        action='store_true',
        help='Run all demo scenarios sequentially'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--no-rich', '-n',
        action='store_true',
        help='Disable rich formatting (for compatibility)'
    )
    
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='Overseer LLM Demo v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    try:
        import psutil
    except ImportError:
        print("Error: psutil is required. Install with: pip install psutil")
        sys.exit(1)
    
    try:
        from rich.console import Console
        RICH_AVAILABLE = True
    except ImportError:
        if not args.no_rich:
            print("Warning: rich library not available. Install with: pip install rich")
        RICH_AVAILABLE = False
    
    # Import demo components
    try:
        from demo_mode import DemoMode
        from llm_advisor import LLMAdvisor
    except ImportError as e:
        print(f"Error importing demo components: {e}")
        sys.exit(1)
    
    # Run demo based on arguments
    if args.real_analysis:
        run_real_analysis(args)
    elif args.scenario:
        run_scenario_demo(args.scenario, args)
    elif args.interactive:
        run_interactive_demo(args)
    elif args.all_scenarios:
        run_all_scenarios(args)
    else:
        # No arguments provided, show help
        parser.print_help()
        print("\nTry one of these examples:")
        print("  python3 demo_cli.py --real-analysis")
        print("  python3 demo_cli.py --scenario high-cpu")
        print("  python3 demo_cli.py --interactive")

def run_real_analysis(args):
    """Run real system analysis"""
    print("🔍 Running Real System Analysis with LLM Advisor...")
    
    try:
        from llm_advisor import LLMAdvisor
        
        advisor = LLMAdvisor()
        analysis = advisor.analyze_system_health()
        
        if analysis:
            print("✅ Analysis completed successfully!")
            advisor.display_analysis(analysis)
        else:
            print("❌ Could not analyze system")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def run_scenario_demo(scenario_name, args):
    """Run a specific demo scenario"""
    print(f"🎭 Running {scenario_name.replace('-', ' ').title()} Demo...")
    
    try:
        from demo_mode import DemoMode
        
        demo = DemoMode()
        
        # Map CLI scenario names to demo scenario keys
        scenario_map = {
            'high-cpu': 'high_cpu',
            'high-memory': 'high_memory',
            'low-disk': 'low_disk',
            'slow-system': 'slow_system'
        }
        
        scenario_key = scenario_map.get(scenario_name)
        if scenario_key:
            demo.run_demo_scenario(scenario_key)
        else:
            print(f"❌ Unknown scenario: {scenario_name}")
            
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def run_interactive_demo(args):
    """Run interactive demo"""
    print("🎮 Starting Interactive LLM Demo...")
    
    try:
        from demo_mode import DemoMode
        
        demo = DemoMode()
        demo.run_interactive_demo()
        
    except Exception as e:
        print(f"❌ Error running interactive demo: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def run_all_scenarios(args):
    """Run all demo scenarios"""
    print("🎬 Running All Demo Scenarios...")
    
    scenarios = ['high_cpu', 'high_memory', 'low_disk', 'slow_system']
    
    try:
        from demo_mode import DemoMode
        
        demo = DemoMode()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{len(scenarios)}] Running {scenario.replace('_', ' ').title()} Demo...")
            demo.run_demo_scenario(scenario)
            
            if i < len(scenarios):
                input("\nPress Enter to continue to next scenario...")
        
        print("\n✅ All demo scenarios completed!")
        
    except Exception as e:
        print(f"❌ Error running scenarios: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def show_demo_info():
    """Show information about available demos"""
    print("🤖 Overseer LLM Demo Mode")
    print("=" * 40)
    print("\nAvailable Demo Types:")
    print("• Real System Analysis - Analyze your actual system")
    print("• High CPU Demo - Simulate high CPU usage")
    print("• High Memory Demo - Simulate memory pressure")
    print("• Low Disk Demo - Simulate disk space issues")
    print("• Slow System Demo - Simulate overall slowdown")
    print("• Interactive Demo - Step-by-step problem solving")
    print("\nLLM Features Demonstrated:")
    print("• Intelligent problem identification")
    print("• Root cause analysis")
    print("• Impact assessment")
    print("• Solution generation")
    print("• Tool recommendations")
    print("• Action plan creation")

if __name__ == "__main__":
    main() 