#!/usr/bin/env python3
"""
Demo Mode for System Monitoring with LLM Integration
Showcases intelligent problem diagnosis and solution suggestions.
"""

import os
import sys
import time
import json
from typing import Dict
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from llm_advisor import LLMAdvisor
from system_monitor import SystemMonitor
from enhanced_tool_recommender import EnhancedToolRecommender

class DemoMode:
    """Interactive demo mode for system monitoring with LLM suggestions"""
    
    def __init__(self):
        """Initialize demo mode"""
        self.console = Console() if RICH_AVAILABLE else None
        self.advisor = LLMAdvisor()
        self.system_monitor = SystemMonitor()
        self.tool_recommender = EnhancedToolRecommender()
        
        # Demo scenarios
        self.demo_scenarios = {
            'high_cpu': {
                'name': 'High CPU Usage',
                'description': 'Simulate high CPU usage scenario',
                'metrics': {'cpu_percent': 95.0, 'memory_percent': 60.0, 'disk_percent': 50.0},
                'problems': ['high_cpu'],
                'tools': ['htop', 'iotop', 'atop', 'perf'],
                'solutions': [
                    'Identify resource-intensive processes',
                    'Kill runaway processes',
                    'Optimize application performance'
                ]
            },
            'high_memory': {
                'name': 'High Memory Usage',
                'description': 'Simulate memory pressure scenario',
                'metrics': {'cpu_percent': 40.0, 'memory_percent': 92.0, 'disk_percent': 50.0},
                'problems': ['high_memory'],
                'tools': ['htop', 'free', 'smem', 'ps_mem'],
                'solutions': [
                    'Identify memory-hogging processes',
                    'Check for memory leaks',
                    'Increase swap space'
                ]
            },
            'low_disk': {
                'name': 'Low Disk Space',
                'description': 'Simulate disk space issues',
                'metrics': {'cpu_percent': 30.0, 'memory_percent': 50.0, 'disk_percent': 95.0},
                'problems': ['low_disk'],
                'tools': ['ncdu', 'du', 'df', 'baobab'],
                'solutions': [
                    'Find and remove large files',
                    'Clean up temporary files',
                    'Check log file accumulation'
                ]
            },
            'slow_system': {
                'name': 'Slow System Performance',
                'description': 'Simulate overall system slowdown',
                'metrics': {'cpu_percent': 85.0, 'memory_percent': 88.0, 'disk_percent': 90.0},
                'problems': ['high_cpu', 'high_memory', 'slow_system'],
                'tools': ['htop', 'iotop', 'dstat', 'atop'],
                'solutions': [
                    'Identify performance bottlenecks',
                    'Optimize resource usage',
                    'Consider hardware upgrades'
                ]
            }
        }
    
    def show_welcome(self):
        """Show welcome message and demo options"""
        if not self.console:
            print("Rich library required for demo mode")
            return
        
        welcome_panel = Panel(
            "[bold]🤖 Overseer System Monitor - LLM Demo Mode[/bold]\n\n"
            "This demo showcases intelligent system monitoring with LLM-powered\n"
            "problem diagnosis and solution suggestions.\n\n"
            "Features:\n"
            "• Real-time system analysis\n"
            "• Intelligent problem identification\n"
            "• LLM-powered solution suggestions\n"
            "• Tool recommendations\n"
            "• Action plan generation\n\n"
            "Choose a demo scenario or analyze your real system!",
            title="Welcome to LLM Demo Mode",
            border_style="blue"
        )
        self.console.print(welcome_panel)
    
    def show_demo_menu(self):
        """Show demo menu options"""
        menu_table = Table(title="Demo Scenarios")
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Scenario", style="green")
        menu_table.add_column("Description", style="yellow")
        
        menu_table.add_row("1", "Real System Analysis", "Analyze your actual system")
        menu_table.add_row("2", "High CPU Demo", "Simulate high CPU usage")
        menu_table.add_row("3", "High Memory Demo", "Simulate memory pressure")
        menu_table.add_row("4", "Low Disk Demo", "Simulate disk space issues")
        menu_table.add_row("5", "Slow System Demo", "Simulate overall slowdown")
        menu_table.add_row("6", "Interactive Demo", "Step-by-step problem solving")
        menu_table.add_row("q", "Quit", "Exit demo mode")
        
        self.console.print(menu_table)
    
    def run_real_analysis(self):
        """Run analysis on real system"""
        self.console.print("\n[bold]🔍 Analyzing Your Real System...[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Collecting system metrics...", total=None)
            
            # Analyze system health
            analysis = self.advisor.analyze_system_health()
            
            progress.update(task, description="Generating recommendations...")
            time.sleep(1)
            
            progress.update(task, description="Complete!")
        
        if analysis:
            self.console.print("\n[bold]📊 Real System Analysis Results:[/bold]")
            self.advisor.display_analysis(analysis)
        else:
            self.console.print("[red]❌ Could not analyze system[/red]")
    
    def run_demo_scenario(self, scenario_key: str):
        """Run a specific demo scenario"""
        if scenario_key not in self.demo_scenarios:
            self.console.print(f"[red]❌ Unknown scenario: {scenario_key}[/red]")
            return
        
        scenario = self.demo_scenarios[scenario_key]
        
        self.console.print(f"\n[bold]🎭 Running Demo: {scenario['name']}[/bold]")
        self.console.print(f"[italic]{scenario['description']}[/italic]")
        
        # Simulate the scenario
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Simulating system conditions...", total=None)
            time.sleep(2)
            
            progress.update(task, description="Analyzing problems...")
            time.sleep(1)
            
            progress.update(task, description="Generating LLM recommendations...")
            time.sleep(1)
            
            progress.update(task, description="Complete!")
        
        # Create simulated analysis
        simulated_analysis = self._create_simulated_analysis(scenario)
        
        self.console.print(f"\n[bold]🤖 LLM Analysis for {scenario['name']}:[/bold]")
        self._display_simulated_analysis(scenario, simulated_analysis)
    
    def _create_simulated_analysis(self, scenario: Dict) -> Dict:
        """Create simulated analysis for demo scenario"""
        return {
            'health_score': 45 if 'high_cpu' in scenario['problems'] else 60,
            'status': 'warning' if len(scenario['problems']) == 1 else 'critical',
            'problems': [
                {
                    'type': problem,
                    'severity': 'critical' if problem in ['high_cpu', 'high_memory'] else 'warning',
                    'value': scenario['metrics'].get(f'{problem.split("_")[1]}_percent', 85.0),
                    'description': f'Simulated {problem.replace("_", " ")} problem'
                }
                for problem in scenario['problems']
            ],
            'recommendations': [
                {
                    'problem_type': problem,
                    'severity': 'critical' if problem in ['high_cpu', 'high_memory'] else 'warning',
                    'description': f'Simulated {problem.replace("_", " ")} issue',
                    'root_cause': f'Simulated root cause for {problem}',
                    'impact': f'Simulated impact of {problem}',
                    'suggested_solutions': scenario['solutions'],
                    'tools_needed': scenario['tools'],
                    'commands': [
                        f'# Simulated command for {problem}',
                        f'# Another command for {problem}'
                    ],
                    'confidence': 0.85
                }
                for problem in scenario['problems']
            ]
        }
    
    def _display_simulated_analysis(self, scenario: Dict, analysis: Dict):
        """Display simulated analysis results"""
        # Health summary
        health_panel = Panel(
            f"Health Score: {analysis['health_score']}/100\n"
            f"Status: {analysis['status']}\n"
            f"Problems Found: {len(analysis['problems'])}\n"
            f"[italic]This is a simulated scenario for demonstration purposes[/italic]",
            title=f"Simulated Analysis - {scenario['name']}",
            border_style="yellow"
        )
        self.console.print(health_panel)
        
        # Problems
        if analysis['problems']:
            table = Table(title="Simulated Problems")
            table.add_column("Type", style="cyan")
            table.add_column("Severity", style="yellow")
            table.add_column("Description", style="green")
            
            for problem in analysis['problems']:
                severity_color = "red" if problem['severity'] == 'critical' else "yellow"
                table.add_row(
                    problem['type'].replace('_', ' ').title(),
                    f"[{severity_color}]{problem['severity'].upper()}[/{severity_color}]",
                    problem['description']
                )
            
            self.console.print(table)
        
        # LLM Recommendations
        if analysis['recommendations']:
            self.console.print("\n[bold]🤖 LLM-Powered Recommendations:[/bold]")
            
            for rec in analysis['recommendations']:
                rec_panel = Panel(
                    f"[bold]Problem:[/bold] {rec['description']}\n"
                    f"[bold]Root Cause:[/bold] {rec['root_cause']}\n"
                    f"[bold]Impact:[/bold] {rec['impact']}\n"
                    f"[bold]Confidence:[/bold] {rec['confidence']:.1%}\n\n"
                    f"[bold]Suggested Solutions:[/bold]\n" + 
                    "\n".join([f"• {solution}" for solution in rec['suggested_solutions']]) + "\n\n"
                    f"[bold]Tools Needed:[/bold] {', '.join(rec['tools_needed'])}\n"
                    f"[bold]Commands:[/bold]\n" +
                    "\n".join([f"  {cmd}" for cmd in rec['commands']]),
                    title=f"LLM Analysis - {rec['problem_type'].replace('_', ' ').title()}",
                    border_style="blue"
                )
                self.console.print(rec_panel)
    
    def run_interactive_demo(self):
        """Run interactive step-by-step demo"""
        self.console.print("\n[bold]🎮 Interactive LLM Demo[/bold]")
        self.console.print("This demo will walk you through problem-solving with LLM assistance.\n")
        
        # Step 1: System Analysis
        self.console.print("[bold]Step 1: System Analysis[/bold]")
        self.console.print("The LLM advisor analyzes your system and identifies potential issues...")
        
        analysis = self.advisor.analyze_system_health()
        
        if analysis and analysis['problems']:
            self.console.print(f"✅ Found {len(analysis['problems'])} potential issues")
            
            # Step 2: Problem Prioritization
            self.console.print("\n[bold]Step 2: Problem Prioritization[/bold]")
            self.console.print("The LLM prioritizes problems based on severity and impact...")
            
            critical_problems = [p for p in analysis['problems'] if p['severity'] == 'critical']
            warning_problems = [p for p in analysis['problems'] if p['severity'] == 'warning']
            
            if critical_problems:
                self.console.print(f"🔴 Critical issues: {len(critical_problems)}")
            if warning_problems:
                self.console.print(f"🟡 Warning issues: {len(warning_problems)}")
            
            # Step 3: Solution Generation
            self.console.print("\n[bold]Step 3: LLM Solution Generation[/bold]")
            self.console.print("The LLM generates intelligent solutions for each problem...")
            
            for problem in analysis['problems'][:2]:  # Show first 2 problems
                self.console.print(f"\n[bold]Problem:[/bold] {problem['description']}")
                
                # Get tool recommendations
                tools = self.advisor.get_tool_recommendations(problem['type'])
                if tools:
                    self.console.print(f"[bold]Recommended Tools:[/bold] {', '.join([t['name'] for t in tools[:3]])}")
                
                # Get action plan
                action_plan = self.advisor.generate_action_plan([problem])
                if action_plan['immediate_actions']:
                    self.console.print(f"[bold]Immediate Action:[/bold] {action_plan['immediate_actions'][0]['action']}")
            
            # Step 4: User Interaction
            self.console.print("\n[bold]Step 4: Interactive Problem Solving[/bold]")
            
            if Confirm.ask("Would you like to see detailed solutions for a specific problem?"):
                problem_choice = Prompt.ask(
                    "Choose a problem type",
                    choices=[p['type'] for p in analysis['problems']]
                )
                
                selected_problem = next(p for p in analysis['problems'] if p['type'] == problem_choice)
                
                self.console.print(f"\n[bold]Detailed Analysis for {selected_problem['type']}:[/bold]")
                
                # Show detailed analysis
                detailed_analysis = self.advisor._generate_recommendations([selected_problem])
                if detailed_analysis:
                    self.advisor.display_analysis({
                        'problems': [selected_problem],
                        'recommendations': detailed_analysis
                    })
        
        else:
            self.console.print("✅ No issues found - your system is healthy!")
    
    def run(self):
        """Run the demo mode"""
        if not self.console:
            print("Rich library required for demo mode")
            return
        
        self.show_welcome()
        
        while True:
            self.show_demo_menu()
            
            choice = Prompt.ask(
                "\nChoose an option",
                choices=["1", "2", "3", "4", "5", "6", "q"]
            )
            
            if choice == "q":
                self.console.print("\n👋 Thanks for trying the LLM Demo Mode!")
                break
            elif choice == "1":
                self.run_real_analysis()
            elif choice == "2":
                self.run_demo_scenario("high_cpu")
            elif choice == "3":
                self.run_demo_scenario("high_memory")
            elif choice == "4":
                self.run_demo_scenario("low_disk")
            elif choice == "5":
                self.run_demo_scenario("slow_system")
            elif choice == "6":
                self.run_interactive_demo()
            
            if Confirm.ask("\nContinue with another demo?"):
                self.console.print("\n" + "="*60 + "\n")
            else:
                break

def main():
    """Main function for demo mode"""
    demo = DemoMode()
    demo.run()

if __name__ == "__main__":
    main() 