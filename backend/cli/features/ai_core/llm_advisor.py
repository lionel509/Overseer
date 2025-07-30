"""
LLM Advisor for System Monitoring
Provides intelligent suggestions for solving system problems using LLM integration.
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from system_monitor import SystemMonitor
from enhanced_tool_recommender import EnhancedToolRecommender
from alert_manager import AlertManager, AlertSeverity

@dataclass
class ProblemAnalysis:
    """Problem analysis data structure"""
    problem_type: str
    severity: str
    description: str
    root_cause: str
    impact: str
    suggested_solutions: List[str]
    tools_needed: List[str]
    commands: List[str]
    confidence: float

class LLMAdvisor:
    """LLM-powered system advisor for problem diagnosis and solutions"""
    
    def __init__(self, config: Dict = None):
        """Initialize LLM advisor"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.tool_recommender = EnhancedToolRecommender(system_monitor=self.system_monitor)
        self.alert_manager = AlertManager()
        
        # LLM integration (placeholder - can be replaced with actual LLM)
        self.llm_available = self._check_llm_availability()
        
        # Problem patterns and solutions
        self.problem_patterns = {
            'high_cpu': {
                'triggers': ['cpu_percent > 80', 'load_average > 5'],
                'solutions': [
                    'Identify and kill resource-intensive processes',
                    'Check for runaway processes or infinite loops',
                    'Consider upgrading CPU or optimizing applications',
                    'Monitor CPU temperature and thermal throttling'
                ],
                'tools': ['htop', 'iotop', 'atop', 'perf', 'strace'],
                'commands': [
                    'htop -p $(pgrep -d, -f "python|node|java")',
                    'iotop -o -b -n 1',
                    'ps aux --sort=-%cpu | head -10'
                ]
            },
            'high_memory': {
                'triggers': ['memory_percent > 85', 'swap_usage > 50'],
                'solutions': [
                    'Identify memory-hogging processes',
                    'Check for memory leaks in applications',
                    'Consider increasing swap space',
                    'Optimize application memory usage'
                ],
                'tools': ['htop', 'free', 'smem', 'ps_mem', 'valgrind'],
                'commands': [
                    'free -h',
                    'ps aux --sort=-%mem | head -10',
                    'smem -t -k'
                ]
            },
            'low_disk': {
                'triggers': ['disk_percent > 90', 'inode_usage > 80'],
                'solutions': [
                    'Find and remove large files',
                    'Clean up temporary files and caches',
                    'Check for log file accumulation',
                    'Consider disk expansion or cleanup'
                ],
                'tools': ['ncdu', 'du', 'df', 'baobab', 'disk_usage_analyzer'],
                'commands': [
                    'du -sh /* | sort -hr | head -10',
                    'find /tmp -type f -mtime +7 -delete',
                    'journalctl --vacuum-time=7d'
                ]
            },
            'high_temperature': {
                'triggers': ['temperature > 80'],
                'solutions': [
                    'Check CPU fan and cooling system',
                    'Reduce CPU-intensive tasks',
                    'Clean dust from cooling vents',
                    'Consider thermal paste replacement'
                ],
                'tools': ['sensors', 'lm-sensors', 'powertop', 'thermald'],
                'commands': [
                    'sensors',
                    'cat /sys/class/thermal/thermal_zone*/temp',
                    'powertop --calibrate'
                ]
            },
            'network_issues': {
                'triggers': ['network_errors > 0', 'latency > 100'],
                'solutions': [
                    'Check network interface status',
                    'Analyze network traffic patterns',
                    'Test DNS resolution',
                    'Check firewall rules'
                ],
                'tools': ['iftop', 'nethogs', 'nmap', 'ping', 'traceroute'],
                'commands': [
                    'iftop -i eth0',
                    'ping -c 5 google.com',
                    'netstat -i'
                ]
            },
            'slow_system': {
                'triggers': ['response_time > 2', 'iowait > 20'],
                'solutions': [
                    'Check for I/O bottlenecks',
                    'Analyze system load patterns',
                    'Optimize disk I/O',
                    'Consider SSD upgrade'
                ],
                'tools': ['iotop', 'iostat', 'dstat', 'atop', 'sar'],
                'commands': [
                    'iostat -x 1 5',
                    'iotop -o -b -n 1',
                    'dstat -d --disk-util'
                ]
            }
        }
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM integration is available"""
        # Placeholder for LLM availability check
        # In a real implementation, this would check for API keys, models, etc.
        return True  # Assume available for demo
    
    def analyze_system_health(self) -> Dict:
        """Analyze overall system health"""
        try:
            metrics = self.system_monitor.collect_metrics()
            alerts = self.alert_manager.check_metrics({
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'disk_percent': metrics.disk_percent,
                'temperature': metrics.temperature or 0.0
            })
            
            # Calculate health score
            health_summary = self.system_monitor.get_system_summary()
            
            # Identify problems
            problems = self._identify_problems(metrics, alerts)
            
            return {
                'timestamp': time.time(),
                'health_score': health_summary['health_score'],
                'status': health_summary['status'],
                'metrics': asdict(metrics),
                'alerts': [asdict(alert) for alert in alerts],
                'problems': problems,
                'recommendations': self._generate_recommendations(problems)
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error analyzing system health: {e}[/red]")
            return {}
    
    def _identify_problems(self, metrics, alerts) -> List[Dict]:
        """Identify system problems based on metrics and alerts"""
        problems = []
        
        # Check CPU issues
        if metrics.cpu_percent > 80:
            problems.append({
                'type': 'high_cpu',
                'severity': 'critical' if metrics.cpu_percent > 90 else 'warning',
                'value': metrics.cpu_percent,
                'threshold': 80,
                'description': f'CPU usage is high at {metrics.cpu_percent:.1f}%'
            })
        
        # Check memory issues
        if metrics.memory_percent > 85:
            problems.append({
                'type': 'high_memory',
                'severity': 'critical' if metrics.memory_percent > 95 else 'warning',
                'value': metrics.memory_percent,
                'threshold': 85,
                'description': f'Memory usage is high at {metrics.memory_percent:.1f}%'
            })
        
        # Check disk issues
        if metrics.disk_percent > 90:
            problems.append({
                'type': 'low_disk',
                'severity': 'critical' if metrics.disk_percent > 95 else 'warning',
                'value': metrics.disk_percent,
                'threshold': 90,
                'description': f'Disk usage is high at {metrics.disk_percent:.1f}%'
            })
        
        # Check temperature issues
        if metrics.temperature and metrics.temperature > 80:
            problems.append({
                'type': 'high_temperature',
                'severity': 'critical' if metrics.temperature > 85 else 'warning',
                'value': metrics.temperature,
                'threshold': 80,
                'description': f'CPU temperature is high at {metrics.temperature:.1f}°C'
            })
        
        # Check load average issues
        load_avg = metrics.load_average[0]
        cpu_count = os.cpu_count() or 1
        if load_avg > cpu_count * 2:
            problems.append({
                'type': 'slow_system',
                'severity': 'warning',
                'value': load_avg,
                'threshold': cpu_count * 2,
                'description': f'System load is high at {load_avg:.2f}'
            })
        
        return problems
    
    def _generate_recommendations(self, problems: List[Dict]) -> List[ProblemAnalysis]:
        """Generate intelligent recommendations for problems"""
        recommendations = []
        
        for problem in problems:
            problem_type = problem['type']
            
            if problem_type in self.problem_patterns:
                pattern = self.problem_patterns[problem_type]
                
                # Generate LLM-like analysis
                analysis = ProblemAnalysis(
                    problem_type=problem_type,
                    severity=problem['severity'],
                    description=problem['description'],
                    root_cause=self._analyze_root_cause(problem_type, problem),
                    impact=self._analyze_impact(problem_type, problem),
                    suggested_solutions=pattern['solutions'],
                    tools_needed=pattern['tools'],
                    commands=pattern['commands'],
                    confidence=0.85 if problem['severity'] == 'critical' else 0.75
                )
                
                recommendations.append(analysis)
        
        return recommendations
    
    def _analyze_root_cause(self, problem_type: str, problem: Dict) -> str:
        """Analyze the root cause of a problem (LLM-like analysis)"""
        root_causes = {
            'high_cpu': 'High CPU usage typically indicates resource-intensive processes, potential infinite loops, or insufficient CPU capacity for current workload.',
            'high_memory': 'High memory usage suggests memory leaks, inefficient memory management, or insufficient RAM for current applications.',
            'low_disk': 'Low disk space usually results from accumulated files, large log files, or insufficient storage allocation.',
            'high_temperature': 'High temperature indicates cooling system issues, dust accumulation, or thermal throttling due to high workload.',
            'slow_system': 'Slow system performance often stems from I/O bottlenecks, memory pressure, or CPU overload.'
        }
        
        return root_causes.get(problem_type, 'Unknown root cause')
    
    def _analyze_impact(self, problem_type: str, problem: Dict) -> str:
        """Analyze the impact of a problem (LLM-like analysis)"""
        impacts = {
            'high_cpu': 'Reduced system responsiveness, potential application crashes, and increased power consumption.',
            'high_memory': 'System slowdown, potential OOM kills, and reduced application performance.',
            'low_disk': 'Application failures, inability to save files, and potential data loss.',
            'high_temperature': 'Thermal throttling, reduced performance, and potential hardware damage.',
            'slow_system': 'Poor user experience, application timeouts, and reduced productivity.'
        }
        
        return impacts.get(problem_type, 'Unknown impact')
    
    def get_tool_recommendations(self, problem_type: str) -> List[Dict]:
        """Get tool recommendations for a specific problem"""
        if problem_type in self.problem_patterns:
            tools = self.problem_patterns[problem_type]['tools']
            recommendations = self.tool_recommender.recommend_tools(f"fix {problem_type}")
            
            # Combine with pattern-based tools
            all_tools = list(set(tools + [rec.name for rec in recommendations]))
            
            return [
                {
                    'name': tool,
                    'category': 'monitoring' if tool in ['htop', 'iotop', 'atop'] else 'diagnostic',
                    'description': f'Tool for {problem_type} analysis and resolution'
                }
                for tool in all_tools[:5]  # Top 5 tools
            ]
        
        return []
    
    def generate_action_plan(self, problems: List[Dict]) -> Dict:
        """Generate an action plan for solving problems"""
        action_plan = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'tools_needed': [],
            'estimated_time': 0
        }
        
        for problem in problems:
            problem_type = problem['type']
            severity = problem['severity']
            
            if severity == 'critical':
                action_plan['immediate_actions'].append({
                    'action': f'Address {problem_type} immediately',
                    'priority': 'high',
                    'estimated_time': '5-15 minutes'
                })
            elif severity == 'warning':
                action_plan['short_term_actions'].append({
                    'action': f'Monitor and address {problem_type}',
                    'priority': 'medium',
                    'estimated_time': '15-30 minutes'
                })
            
            # Add tools needed
            tools = self.get_tool_recommendations(problem_type)
            action_plan['tools_needed'].extend([tool['name'] for tool in tools])
        
        # Remove duplicates
        action_plan['tools_needed'] = list(set(action_plan['tools_needed']))
        
        # Calculate estimated time
        immediate_count = len(action_plan['immediate_actions'])
        short_term_count = len(action_plan['short_term_actions'])
        action_plan['estimated_time'] = immediate_count * 10 + short_term_count * 20
        
        return action_plan
    
    def display_analysis(self, analysis: Dict):
        """Display the system analysis in a formatted way"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # System health summary
        health_panel = Panel(
            f"Health Score: {analysis['health_score']}/100\n"
            f"Status: {analysis['status']}\n"
            f"Problems Found: {len(analysis['problems'])}",
            title="System Health Summary",
            border_style="green" if analysis['health_score'] > 70 else "yellow" if analysis['health_score'] > 40 else "red"
        )
        self.console.print(health_panel)
        
        # Problems table
        if analysis['problems']:
            table = Table(title="Identified Problems")
            table.add_column("Type", style="cyan")
            table.add_column("Severity", style="yellow")
            table.add_column("Description", style="green")
            table.add_column("Value", style="magenta")
            
            for problem in analysis['problems']:
                severity_color = "red" if problem['severity'] == 'critical' else "yellow"
                table.add_row(
                    problem['type'].replace('_', ' ').title(),
                    f"[{severity_color}]{problem['severity'].upper()}[/{severity_color}]",
                    problem['description'],
                    f"{problem['value']:.1f}"
                )
            
            self.console.print(table)
        
        # Recommendations
        if analysis['recommendations']:
            self.console.print("\n[bold]Intelligent Recommendations:[/bold]")
            
            for rec in analysis['recommendations']:
                rec_panel = Panel(
                    f"[bold]Problem:[/bold] {rec.description}\n"
                    f"[bold]Root Cause:[/bold] {rec.root_cause}\n"
                    f"[bold]Impact:[/bold] {rec.impact}\n"
                    f"[bold]Confidence:[/bold] {rec.confidence:.1%}\n\n"
                    f"[bold]Suggested Solutions:[/bold]\n" + 
                    "\n".join([f"• {solution}" for solution in rec.suggested_solutions[:3]]) + "\n\n"
                    f"[bold]Tools Needed:[/bold] {', '.join(rec.tools_needed[:3])}\n"
                    f"[bold]Commands:[/bold]\n" +
                    "\n".join([f"  {cmd}" for cmd in rec.commands[:2]]),
                    title=f"{rec.problem_type.replace('_', ' ').title()} Analysis",
                    border_style="red" if rec.severity == 'critical' else "yellow"
                )
                self.console.print(rec_panel)
        
        # Action plan
        action_plan = self.generate_action_plan(analysis['problems'])
        
        if action_plan['immediate_actions'] or action_plan['short_term_actions']:
            action_table = Table(title="Recommended Action Plan")
            action_table.add_column("Priority", style="cyan")
            action_table.add_column("Action", style="green")
            action_table.add_column("Time", style="yellow")
            
            for action in action_plan['immediate_actions']:
                action_table.add_row("HIGH", action['action'], action['estimated_time'])
            
            for action in action_plan['short_term_actions']:
                action_table.add_row("MEDIUM", action['action'], action['estimated_time'])
            
            self.console.print(action_table)
            
            if action_plan['tools_needed']:
                self.console.print(f"\n[bold]Tools to Install:[/bold] {', '.join(action_plan['tools_needed'])}")
                self.console.print(f"[bold]Estimated Total Time:[/bold] {action_plan['estimated_time']} minutes")

def main():
    """Main function for standalone testing"""
    advisor = LLMAdvisor()
    
    print("🤖 LLM System Advisor")
    print("=" * 50)
    
    # Analyze system health
    analysis = advisor.analyze_system_health()
    
    if analysis:
        advisor.display_analysis(analysis)
    else:
        print("❌ Could not analyze system health")

if __name__ == "__main__":
    main() 