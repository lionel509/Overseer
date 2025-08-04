"""
LLM-Powered System Advisor
Provides advanced AI analysis using LLM APIs for sophisticated system recommendations.
"""

import psutil
import json
import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from db.system_monitoring_db import system_monitoring_db

console = Console()

class LLMSystemAdvisor:
    """LLM-powered system advisor with advanced analysis capabilities"""
    
    def __init__(self):
        self.console = Console()
        self.analysis_cache = {}
    
    def get_detailed_system_profile(self) -> Dict:
        """Get comprehensive system profile for LLM analysis"""
        try:
            # System hardware info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Process analysis with more detail
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent', 'status', 'create_time', 'memory_info', 'num_threads']):
                try:
                    memory_percent = proc.info['memory_percent'] or 0.0
                    cpu_percent = proc.info['cpu_percent'] or 0.0
                    memory_mb = (proc.info['memory_info'].rss / 1024 / 1024) if proc.info['memory_info'] else 0.0
                    age_hours = (time.time() - proc.info['create_time']) / 3600 if proc.info['create_time'] else 0
                    
                    if memory_percent > 0.5:  # Include more processes for detailed analysis
                        processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'memory_percent': memory_percent,
                            'memory_mb': memory_mb,
                            'cpu_percent': cpu_percent,
                            'age_hours': age_hours,
                            'status': proc.info['status'],
                            'threads': proc.info['num_threads'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            # Network analysis
            network = psutil.net_io_counters()
            
            # Battery analysis
            battery = None
            try:
                battery = psutil.sensors_battery()
            except:
                pass
            
            # System load
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            return {
                'timestamp': time.time(),
                'hardware': {
                    'cpu_cores': psutil.cpu_count(),
                    'cpu_percent': cpu,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_available_gb': memory.available / (1024**3),
                    'memory_percent': memory.percent,
                    'swap_total_gb': swap.total / (1024**3),
                    'swap_used_gb': swap.used / (1024**3),
                    'swap_percent': swap.percent,
                    'disk_total_gb': disk.total / (1024**3),
                    'disk_used_gb': disk.used / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100,
                    'load_average': load_avg
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'battery': {
                    'percent': battery.percent if battery else None,
                    'plugged': battery.power_plugged if battery else None,
                    'time_left': battery.secsleft if battery else None
                },
                'processes': processes[:20],  # Top 20 for detailed analysis
                'analysis': {
                    'high_memory_processes': [p for p in processes if p['memory_percent'] > 5],
                    'long_running_processes': [p for p in processes if p['age_hours'] > 24],
                    'potential_memory_leaks': [p for p in processes if p['memory_percent'] > 3 and p['age_hours'] > 12],
                    'cpu_intensive_processes': [p for p in processes if p['cpu_percent'] > 10],
                    'browser_processes': [p for p in processes if any(b in p['name'].lower() for b in ['chrome', 'firefox', 'safari', 'edge', 'webkit'])],
                    'system_processes': [p for p in processes if any(s in p['name'].lower() for s in ['system', 'kernel', 'init', 'systemd'])],
                    'user_applications': [p for p in processes if not any(s in p['name'].lower() for s in ['system', 'kernel', 'init', 'systemd', 'chrome', 'firefox', 'safari', 'edge', 'webkit'])],
                    'multi_threaded_processes': [p for p in processes if p['threads'] > 10]
                }
            }
        except Exception as e:
            console.print(f"[red]Error collecting system profile: {e}[/red]")
            return {}
    
    def generate_llm_prompt(self, system_profile: Dict) -> str:
        """Generate a sophisticated prompt for LLM analysis"""
        hw = system_profile['hardware']
        processes = system_profile['processes']
        analysis = system_profile['analysis']
        
        prompt = f"""
# Advanced System Performance Analysis

## System Hardware Profile:
- **CPU**: {hw['cpu_cores']} cores, {hw['cpu_percent']:.1f}% usage
- **Memory**: {hw['memory_percent']:.1f}% ({hw['memory_used_gb']:.1f}GB / {hw['memory_total_gb']:.1f}GB)
- **Swap**: {hw['swap_percent']:.1f}% ({hw['swap_used_gb']:.1f}GB)
- **Disk**: {hw['disk_percent']:.1f}% ({hw['disk_used_gb']:.1f}GB / {hw['disk_total_gb']:.1f}GB)
- **Load Average**: {hw['load_average'][0]:.2f}, {hw['load_average'][1]:.2f}, {hw['load_average'][2]:.2f}

## Top Memory-Using Processes (Top 10):
"""
        
        for i, proc in enumerate(processes[:10], 1):
            prompt += f"{i}. {proc['name']} (PID: {proc['pid']}) - {proc['memory_percent']:.1f}% ({proc['memory_mb']:.1f}MB) - {proc['cpu_percent']:.1f}% CPU - {proc['age_hours']:.1f}h old - {proc['threads']} threads\n"
        
        prompt += f"""
## System Analysis Summary:
- **High Memory Processes**: {len(analysis['high_memory_processes'])} processes using >5% memory
- **Long Running**: {len(analysis['long_running_processes'])} processes running >24h
- **Potential Memory Leaks**: {len(analysis['potential_memory_leaks'])} processes with high memory + long runtime
- **CPU Intensive**: {len(analysis['cpu_intensive_processes'])} processes using >10% CPU
- **Multi-threaded**: {len(analysis['multi_threaded_processes'])} processes with >10 threads
- **Browser Processes**: {len(analysis['browser_processes'])} browser-related processes
- **System Processes**: {len(analysis['system_processes'])} system processes
- **User Applications**: {len(analysis['user_applications'])} user applications

## Request for Advanced Analysis:
Please provide a comprehensive system analysis including:

1. **Performance Score**: Rate from 0-100 with detailed breakdown
2. **Critical Issues**: Identify the most serious performance problems
3. **Root Cause Analysis**: Deep dive into what's causing performance issues
4. **Immediate Actions**: Specific, prioritized steps to take now
5. **Process Optimization**: Detailed recommendations for each problematic process
6. **System Optimization**: Hardware and software optimization suggestions
7. **Prevention Strategies**: How to avoid these issues in the future
8. **Monitoring Setup**: Advanced monitoring and alerting recommendations
9. **Performance Benchmarks**: What normal performance should look like
10. **Troubleshooting Guide**: Step-by-step debugging procedures

Provide technical, actionable advice with specific commands and procedures.
"""
        
        return prompt
    
    def get_advanced_recommendations(self, system_profile: Dict) -> Dict:
        """Get advanced LLM-powered recommendations"""
        hw = system_profile['hardware']
        processes = system_profile['processes']
        analysis = system_profile['analysis']
        
        # Advanced performance scoring
        performance_score = self._calculate_advanced_score(hw, analysis)
        
        # Critical issues identification
        critical_issues = self._identify_critical_issues(hw, analysis)
        
        # Root cause analysis
        root_causes = self._analyze_root_causes(hw, processes, analysis)
        
        # Immediate actions with priority
        immediate_actions = self._get_prioritized_actions(processes, analysis)
        
        # Process-specific optimization
        process_optimization = self._get_process_optimization(processes, analysis)
        
        # System optimization
        system_optimization = self._get_system_optimization(hw, analysis)
        
        # Prevention strategies
        prevention_strategies = self._get_prevention_strategies(hw, analysis)
        
        return {
            'performance_score': performance_score,
            'critical_issues': critical_issues,
            'root_causes': root_causes,
            'immediate_actions': immediate_actions,
            'process_optimization': process_optimization,
            'system_optimization': system_optimization,
            'prevention_strategies': prevention_strategies,
            'monitoring_setup': self._get_monitoring_setup(hw),
            'performance_benchmarks': self._get_performance_benchmarks(hw),
            'troubleshooting_guide': self._get_troubleshooting_guide(hw, analysis)
        }
    
    def _calculate_advanced_score(self, hw: Dict, analysis: Dict) -> Dict:
        """Calculate advanced performance score with detailed breakdown"""
        score = 100
        breakdown = {}
        
        # Memory scoring
        if hw['memory_percent'] > 90:
            score -= 30
            breakdown['memory'] = "Critical - System may become unresponsive"
        elif hw['memory_percent'] > 80:
            score -= 20
            breakdown['memory'] = "High - Performance degradation likely"
        elif hw['memory_percent'] > 70:
            score -= 10
            breakdown['memory'] = "Moderate - Monitor for increases"
        else:
            breakdown['memory'] = "Normal - Healthy memory usage"
        
        # Swap scoring
        if hw['swap_percent'] > 80:
            score -= 25
            breakdown['swap'] = "Critical - Heavy swap usage causing slowdowns"
        elif hw['swap_percent'] > 60:
            score -= 15
            breakdown['swap'] = "High - System using virtual memory extensively"
        elif hw['swap_percent'] > 40:
            score -= 5
            breakdown['swap'] = "Moderate - Some swap usage"
        else:
            breakdown['swap'] = "Normal - Minimal swap usage"
        
        # CPU scoring
        if hw['cpu_percent'] > 90:
            score -= 20
            breakdown['cpu'] = "Critical - CPU bottleneck"
        elif hw['cpu_percent'] > 70:
            score -= 10
            breakdown['cpu'] = "High - CPU intensive operations"
        elif hw['cpu_percent'] > 50:
            score -= 5
            breakdown['cpu'] = "Moderate - Normal workload"
        else:
            breakdown['cpu'] = "Normal - Light CPU usage"
        
        # Process penalty
        if len(analysis['potential_memory_leaks']) > 3:
            score -= 10
            breakdown['processes'] = "Critical - Multiple potential memory leaks"
        elif len(analysis['potential_memory_leaks']) > 1:
            score -= 5
            breakdown['processes'] = "Moderate - Some potential memory leaks"
        else:
            breakdown['processes'] = "Normal - No significant process issues"
        
        # Determine rating
        if score >= 90:
            rating = "Excellent"
            color = "green"
        elif score >= 75:
            rating = "Good"
            color = "blue"
        elif score >= 60:
            rating = "Fair"
            color = "yellow"
        elif score >= 40:
            rating = "Poor"
            color = "red"
        else:
            rating = "Critical"
            color = "bold red"
        
        return {
            'score': score,
            'rating': rating,
            'color': color,
            'breakdown': breakdown
        }
    
    def _identify_critical_issues(self, hw: Dict, analysis: Dict) -> List[str]:
        """Identify critical system issues"""
        issues = []
        
        # Memory critical issues
        if hw['memory_percent'] > 90:
            issues.append("🚨 **CRITICAL**: Memory usage at {hw['memory_percent']:.1f}% - System may become unresponsive")
        elif hw['memory_percent'] > 80:
            issues.append("⚠️ **HIGH**: Memory usage at {hw['memory_percent']:.1f}% - Performance degradation likely")
        
        # Swap critical issues
        if hw['swap_percent'] > 80:
            issues.append("🚨 **CRITICAL**: Swap usage at {hw['swap_percent']:.1f}% - Heavy virtual memory usage causing slowdowns")
        elif hw['swap_percent'] > 60:
            issues.append("⚠️ **HIGH**: Swap usage at {hw['swap_percent']:.1f}% - System using virtual memory extensively")
        
        # Process critical issues
        if len(analysis['potential_memory_leaks']) > 3:
            issues.append("🚨 **CRITICAL**: {len(analysis['potential_memory_leaks'])} potential memory leaks detected")
        elif len(analysis['potential_memory_leaks']) > 1:
            issues.append("⚠️ **HIGH**: {len(analysis['potential_memory_leaks'])} potential memory leaks detected")
        
        # CPU critical issues
        if hw['cpu_percent'] > 90:
            issues.append("🚨 **CRITICAL**: CPU usage at {hw['cpu_percent']:.1f}% - CPU bottleneck")
        elif hw['cpu_percent'] > 70:
            issues.append("⚠️ **HIGH**: CPU usage at {hw['cpu_percent']:.1f}% - CPU intensive operations")
        
        return issues
    
    def _analyze_root_causes(self, hw: Dict, processes: List[Dict], analysis: Dict) -> List[str]:
        """Deep analysis of root causes"""
        causes = []
        
        # Memory pressure analysis
        if hw['memory_percent'] > 70:
            causes.append(f"**Memory Pressure**: {hw['memory_percent']:.1f}% memory usage is forcing system to use swap")
        
        # Swap dependency analysis
        if hw['swap_percent'] > 50:
            causes.append(f"**Swap Dependency**: {hw['swap_percent']:.1f}% swap usage indicates insufficient RAM for workload")
        
        # Process accumulation analysis
        if len(analysis['long_running_processes']) > 5:
            causes.append(f"**Process Accumulation**: {len(analysis['long_running_processes'])} processes running >24h accumulating memory")
        
        # Memory leak analysis
        if analysis['potential_memory_leaks']:
            leak_processes = [p['name'] for p in analysis['potential_memory_leaks'][:3]]
            causes.append(f"**Memory Leaks**: Potential leaks in {', '.join(leak_processes)}")
        
        # Browser memory analysis
        if analysis['browser_processes']:
            browser_memory = sum(p['memory_mb'] for p in analysis['browser_processes'])
            if browser_memory > 3000:
                causes.append(f"**Browser Memory**: Browsers consuming {browser_memory:.0f}MB - consider tab cleanup")
        
        return causes
    
    def _get_prioritized_actions(self, processes: List[Dict], analysis: Dict) -> List[Dict]:
        """Get prioritized immediate actions"""
        actions = []
        
        # Critical actions (highest priority)
        critical_processes = [p for p in processes if p['memory_percent'] > 15 and p['age_hours'] > 12]
        for proc in critical_processes[:3]:
            actions.append({
                'priority': 'CRITICAL',
                'action': f"Restart {proc['name']}",
                'reason': f"Using {proc['memory_percent']:.1f}% memory for {proc['age_hours']:.1f}h",
                'command': f"kill {proc['pid']}"
            })
        
        # High priority actions
        if analysis['browser_processes']:
            browser_memory = sum(p['memory_mb'] for p in analysis['browser_processes'])
            if browser_memory > 2000:
                actions.append({
                    'priority': 'HIGH',
                    'action': "Close browser tabs",
                    'reason': f"Browsers using {browser_memory:.0f}MB memory",
                    'command': "Close unused browser tabs"
                })
        
        # Medium priority actions
        if len(analysis['long_running_processes']) > 3:
            actions.append({
                'priority': 'MEDIUM',
                'action': "Restart long-running applications",
                'reason': f"{len(analysis['long_running_processes'])} processes running >24h",
                'command': "Restart applications that have been running for over 24 hours"
            })
        
        return actions
    
    def _get_process_optimization(self, processes: List[Dict], analysis: Dict) -> List[Dict]:
        """Get process-specific optimization recommendations"""
        optimizations = []
        
        for proc in processes[:8]:  # Top 8 processes
            if proc['memory_percent'] > 3:
                optimization = {
                    'process': proc['name'],
                    'pid': proc['pid'],
                    'memory_usage': f"{proc['memory_percent']:.1f}% ({proc['memory_mb']:.1f}MB)",
                    'age': f"{proc['age_hours']:.1f}h",
                    'recommendation': self._get_process_recommendation(proc, analysis)
                }
                optimizations.append(optimization)
        
        return optimizations
    
    def _get_process_recommendation(self, proc: Dict, analysis: Dict) -> str:
        """Get specific recommendation for a process"""
        if proc['age_hours'] > 48:
            return "Restart immediately - Very long running process"
        elif proc['age_hours'] > 24:
            return "Restart soon - Long running process"
        elif proc['memory_percent'] > 10:
            return "Monitor closely - High memory usage"
        elif proc['memory_percent'] > 5:
            return "Normal operation - Moderate memory usage"
        else:
            return "Normal operation - Low memory usage"
    
    def _get_system_optimization(self, hw: Dict, analysis: Dict) -> List[str]:
        """Get system-level optimization recommendations"""
        optimizations = []
        
        # RAM upgrade recommendation
        if hw['swap_percent'] > 50:
            optimizations.append("**Consider RAM upgrade** - High swap usage indicates insufficient RAM")
        
        # Process management
        if len(analysis['long_running_processes']) > 3:
            optimizations.append("**Implement process rotation** - Restart long-running applications regularly")
        
        # Memory management
        if hw['memory_percent'] > 70:
            optimizations.append("**Optimize memory usage** - Close unnecessary applications and browser tabs")
        
        # System monitoring
        optimizations.append("**Set up comprehensive monitoring** - Track memory, CPU, and process usage over time")
        
        return optimizations
    
    def _get_prevention_strategies(self, hw: Dict, analysis: Dict) -> List[str]:
        """Get prevention strategies"""
        strategies = []
        
        strategies.append("**Regular application restarts** - Don't leave applications running for days")
        strategies.append("**Browser tab management** - Limit open tabs and extensions")
        strategies.append("**Memory monitoring** - Set up alerts for high memory usage")
        strategies.append("**Process rotation** - Restart applications before they accumulate memory")
        strategies.append("**System maintenance** - Regular system restarts and updates")
        
        return strategies
    
    def _get_monitoring_setup(self, hw: Dict) -> List[str]:
        """Get monitoring setup recommendations"""
        return [
            "**Memory alerts**: Set up alerts when memory usage exceeds 80%",
            "**Swap monitoring**: Monitor swap usage - high swap indicates memory pressure",
            "**Process tracking**: Track process memory usage over time",
            "**Performance baselines**: Establish normal performance benchmarks",
            "**Automated cleanup**: Set up scripts to restart long-running processes"
        ]
    
    def _get_performance_benchmarks(self, hw: Dict) -> Dict:
        """Get performance benchmarks"""
        return {
            'memory': {
                'excellent': '< 60%',
                'good': '60-70%',
                'fair': '70-80%',
                'poor': '80-90%',
                'critical': '> 90%'
            },
            'swap': {
                'excellent': '< 20%',
                'good': '20-40%',
                'fair': '40-60%',
                'poor': '60-80%',
                'critical': '> 80%'
            },
            'cpu': {
                'excellent': '< 30%',
                'good': '30-50%',
                'fair': '50-70%',
                'poor': '70-90%',
                'critical': '> 90%'
            }
        }
    
    def _get_troubleshooting_guide(self, hw: Dict, analysis: Dict) -> List[str]:
        """Get troubleshooting guide"""
        guide = [
            "**Step 1**: Check memory usage with 'free -h'",
            "**Step 2**: Identify top memory users with 'ps aux --sort=-%mem | head -10'",
            "**Step 3**: Check for zombie processes with 'ps aux | grep -w Z'",
            "**Step 4**: Monitor memory over time with 'watch -n 1 free -h'",
            "**Step 5**: Restart high-memory processes identified above",
            "**Step 6**: If problems persist, consider system restart"
        ]
        
        return guide
    
    def display_advanced_analysis(self):
        """Display comprehensive advanced system analysis"""
        console.print(Panel.fit("🧠 Advanced LLM System Analysis", style="bold blue"))
        
        # Collect system profile
        system_profile = self.get_detailed_system_profile()
        if not system_profile:
            console.print("[red]Error: Could not collect system profile[/red]")
            return
        
        # Get advanced recommendations
        recommendations = self.get_advanced_recommendations(system_profile)
        
        # Display performance score
        perf = recommendations['performance_score']
        console.print(f"\n[bold {perf['color']}]Advanced Performance Score: {perf['rating']} ({perf['score']}/100)[/bold {perf['color']}]")
        
        # Display score breakdown
        breakdown_table = Table(title="Performance Score Breakdown", show_header=True, header_style="bold magenta")
        breakdown_table.add_column("Component", style="cyan")
        breakdown_table.add_column("Status", style="green")
        breakdown_table.add_column("Impact", style="yellow")
        
        for component, impact in perf['breakdown'].items():
            breakdown_table.add_row(component.title(), "Analyzed", impact)
        
        console.print(breakdown_table)
        
        # Display critical issues
        if recommendations['critical_issues']:
            console.print("\n[bold red]Critical Issues:[/bold red]")
            for issue in recommendations['critical_issues']:
                console.print(f"• {issue}")
        
        # Display root causes
        if recommendations['root_causes']:
            console.print("\n[bold red]Root Cause Analysis:[/bold red]")
            for cause in recommendations['root_causes']:
                console.print(f"• {cause}")
        
        # Display prioritized actions
        if recommendations['immediate_actions']:
            console.print("\n[bold yellow]Prioritized Immediate Actions:[/bold yellow]")
            for action in recommendations['immediate_actions']:
                console.print(f"• [{action['priority']}] {action['action']}")
                console.print(f"  Reason: {action['reason']}")
                console.print(f"  Command: {action['command']}")
                console.print("")
        
        # Display process optimization
        if recommendations['process_optimization']:
            console.print("\n[bold blue]Process Optimization Recommendations:[/bold blue]")
            for opt in recommendations['process_optimization']:
                console.print(f"• **{opt['process']}** (PID: {opt['pid']}):")
                console.print(f"  - Memory: {opt['memory_usage']}")
                console.print(f"  - Age: {opt['age']}")
                console.print(f"  - Recommendation: {opt['recommendation']}")
                console.print("")
        
        # Display system optimization
        if recommendations['system_optimization']:
            console.print("\n[bold green]System Optimization:[/bold green]")
            for opt in recommendations['system_optimization']:
                console.print(f"• {opt}")
        
        # Display prevention strategies
        if recommendations['prevention_strategies']:
            console.print("\n[bold cyan]Prevention Strategies:[/bold cyan]")
            for strategy in recommendations['prevention_strategies']:
                console.print(f"• {strategy}")
        
        # Display monitoring setup
        if recommendations['monitoring_setup']:
            console.print("\n[bold magenta]Monitoring Setup:[/bold magenta]")
            for setup in recommendations['monitoring_setup']:
                console.print(f"• {setup}")
        
        # Display performance benchmarks
        benchmarks = recommendations['performance_benchmarks']
        console.print("\n[bold white]Performance Benchmarks:[/bold white]")
        for component, levels in benchmarks.items():
            console.print(f"• **{component.title()}**:")
            for level, threshold in levels.items():
                console.print(f"  - {level.title()}: {threshold}")

def main():
    """Run advanced LLM system analysis"""
    advisor = LLMSystemAdvisor()
    advisor.display_advanced_analysis()

if __name__ == "__main__":
    main() 