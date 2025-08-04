"""
AI-Powered System Analyzer
Uses LLM to provide specialized recommendations and detailed analysis of system performance.
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

class AISystemAnalyzer:
    """AI-powered system analysis and recommendations"""
    
    def __init__(self):
        self.console = Console()
        self.analysis_history = []
    
    def get_comprehensive_system_data(self) -> Dict:
        """Collect comprehensive system data for AI analysis"""
        try:
            # Basic system info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Process analysis
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent', 'status', 'create_time', 'memory_info']):
                try:
                    memory_percent = proc.info['memory_percent'] or 0.0
                    cpu_percent = proc.info['cpu_percent'] or 0.0
                    memory_mb = (proc.info['memory_info'].rss / 1024 / 1024) if proc.info['memory_info'] else 0.0
                    age_hours = (time.time() - proc.info['create_time']) / 3600 if proc.info['create_time'] else 0
                    
                    if memory_percent > 1.0:  # Only include significant processes
                        processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'memory_percent': memory_percent,
                            'memory_mb': memory_mb,
                            'cpu_percent': cpu_percent,
                            'age_hours': age_hours,
                            'status': proc.info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            # Network info
            network = psutil.net_io_counters()
            
            # Battery info (if available)
            battery = None
            try:
                battery = psutil.sensors_battery()
            except:
                pass
            
            return {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu,
                    'cpu_count': psutil.cpu_count(),
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
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv,
                    'battery_percent': battery.percent if battery else None,
                    'battery_plugged': battery.power_plugged if battery else None
                },
                'processes': processes[:15],  # Top 15 memory users
                'analysis': {
                    'high_memory_processes': [p for p in processes if p['memory_percent'] > 5],
                    'long_running_processes': [p for p in processes if p['age_hours'] > 24],
                    'potential_memory_leaks': [p for p in processes if p['memory_percent'] > 3 and p['age_hours'] > 12],
                    'browser_processes': [p for p in processes if any(b in p['name'].lower() for b in ['chrome', 'firefox', 'safari', 'edge', 'webkit'])],
                    'system_processes': [p for p in processes if any(s in p['name'].lower() for s in ['system', 'kernel', 'init', 'systemd'])],
                    'user_applications': [p for p in processes if not any(s in p['name'].lower() for s in ['system', 'kernel', 'init', 'systemd', 'chrome', 'firefox', 'safari', 'edge', 'webkit'])]
                }
            }
        except Exception as e:
            console.print(f"[red]Error collecting system data: {e}[/red]")
            return {}
    
    def generate_ai_analysis_prompt(self, system_data: Dict) -> str:
        """Generate a detailed prompt for AI analysis"""
        memory_info = system_data['system']
        processes = system_data['processes']
        analysis = system_data['analysis']
        
        prompt = f"""
# System Performance Analysis Request

## Current System State:
- **CPU Usage**: {memory_info['cpu_percent']:.1f}%
- **Memory Usage**: {memory_info['memory_percent']:.1f}% ({memory_info['memory_used_gb']:.1f}GB / {memory_info['memory_total_gb']:.1f}GB)
- **Swap Usage**: {memory_info['swap_percent']:.1f}% ({memory_info['swap_used_gb']:.1f}GB)
- **Disk Usage**: {memory_info['disk_percent']:.1f}%
- **Battery**: {memory_info['battery_percent']}% {'(Plugged)' if memory_info['battery_plugged'] else '(Unplugged)' if memory_info['battery_percent'] else '(N/A)'}

## Top Memory-Using Processes:
"""
        
        for i, proc in enumerate(processes[:10], 1):
            prompt += f"{i}. {proc['name']} (PID: {proc['pid']}) - {proc['memory_percent']:.1f}% ({proc['memory_mb']:.1f}MB) - {proc['age_hours']:.1f}h old\n"
        
        prompt += f"""
## Analysis Categories:
- **High Memory Processes**: {len(analysis['high_memory_processes'])} processes using >5% memory
- **Long Running**: {len(analysis['long_running_processes'])} processes running >24h
- **Potential Memory Leaks**: {len(analysis['potential_memory_leaks'])} processes with high memory + long runtime
- **Browser Processes**: {len(analysis['browser_processes'])} browser-related processes
- **System Processes**: {len(analysis['system_processes'])} system processes
- **User Applications**: {len(analysis['user_applications'])} user applications

## Request:
Please provide a detailed analysis including:
1. **Performance Assessment**: Rate the system performance (Excellent/Good/Fair/Poor/Critical)
2. **Root Cause Analysis**: What's causing the current performance issues?
3. **Immediate Actions**: Specific steps to take right now
4. **Process-Specific Recommendations**: Which processes to restart/close and why
5. **Long-term Solutions**: How to prevent these issues
6. **Performance Optimization**: Tips for better system performance
7. **Monitoring Recommendations**: What to watch for

Provide specific, actionable advice with technical details.
"""
        
        return prompt
    
    def get_ai_recommendations(self, system_data: Dict) -> Dict:
        """Get AI-powered recommendations (simulated for now)"""
        # This would normally call an LLM API
        # For now, I'll provide intelligent analysis based on the data
        
        memory_info = system_data['system']
        processes = system_data['processes']
        analysis = system_data['analysis']
        
        # Performance assessment
        performance_score = self._calculate_performance_score(memory_info)
        
        # Root cause analysis
        root_causes = self._identify_root_causes(memory_info, analysis)
        
        # Immediate actions
        immediate_actions = self._get_immediate_actions(processes, analysis)
        
        # Process-specific recommendations
        process_recommendations = self._get_process_recommendations(processes, analysis)
        
        # Long-term solutions
        long_term_solutions = self._get_long_term_solutions(memory_info, analysis)
        
        return {
            'performance_assessment': performance_score,
            'root_causes': root_causes,
            'immediate_actions': immediate_actions,
            'process_recommendations': process_recommendations,
            'long_term_solutions': long_term_solutions,
            'optimization_tips': self._get_optimization_tips(memory_info),
            'monitoring_recommendations': self._get_monitoring_recommendations()
        }
    
    def _calculate_performance_score(self, memory_info: Dict) -> Dict:
        """Calculate overall system performance score"""
        score = 100
        
        # Memory penalty
        if memory_info['memory_percent'] > 90:
            score -= 40
        elif memory_info['memory_percent'] > 80:
            score -= 25
        elif memory_info['memory_percent'] > 70:
            score -= 15
        
        # Swap penalty
        if memory_info['swap_percent'] > 80:
            score -= 30
        elif memory_info['swap_percent'] > 60:
            score -= 20
        elif memory_info['swap_percent'] > 40:
            score -= 10
        
        # CPU penalty
        if memory_info['cpu_percent'] > 90:
            score -= 20
        elif memory_info['cpu_percent'] > 70:
            score -= 10
        
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
            'details': {
                'memory_impact': self._get_memory_impact(memory_info['memory_percent']),
                'swap_impact': self._get_swap_impact(memory_info['swap_percent']),
                'cpu_impact': self._get_cpu_impact(memory_info['cpu_percent'])
            }
        }
    
    def _get_memory_impact(self, memory_percent: float) -> str:
        if memory_percent > 90:
            return "Critical - System may become unresponsive"
        elif memory_percent > 80:
            return "High - Performance degradation likely"
        elif memory_percent > 70:
            return "Moderate - Monitor for increases"
        else:
            return "Normal - Healthy memory usage"
    
    def _get_swap_impact(self, swap_percent: float) -> str:
        if swap_percent > 80:
            return "Critical - Heavy swap usage causing slowdowns"
        elif swap_percent > 60:
            return "High - System using virtual memory extensively"
        elif swap_percent > 40:
            return "Moderate - Some swap usage"
        else:
            return "Normal - Minimal swap usage"
    
    def _get_cpu_impact(self, cpu_percent: float) -> str:
        if cpu_percent > 90:
            return "Critical - CPU bottleneck"
        elif cpu_percent > 70:
            return "High - CPU intensive operations"
        elif cpu_percent > 50:
            return "Moderate - Normal workload"
        else:
            return "Normal - Light CPU usage"
    
    def _identify_root_causes(self, memory_info: Dict, analysis: Dict) -> List[str]:
        """Identify root causes of performance issues"""
        causes = []
        
        # High swap usage
        if memory_info['swap_percent'] > 60:
            causes.append(f"**High Swap Usage ({memory_info['swap_percent']:.1f}%)**: System is heavily using virtual memory, indicating insufficient RAM for current workload")
        
        # Memory pressure
        if memory_info['memory_percent'] > 80:
            causes.append(f"**Memory Pressure ({memory_info['memory_percent']:.1f}%)**: High memory usage is forcing the system to use swap")
        
        # Long-running processes
        if analysis['long_running_processes']:
            causes.append(f"**Long-Running Processes**: {len(analysis['long_running_processes'])} processes have been running for over 24 hours, potentially accumulating memory")
        
        # Potential memory leaks
        if analysis['potential_memory_leaks']:
            causes.append(f"**Potential Memory Leaks**: {len(analysis['potential_memory_leaks'])} processes show signs of memory leaks (high usage + long runtime)")
        
        # Browser processes
        if analysis['browser_processes']:
            browser_memory = sum(p['memory_mb'] for p in analysis['browser_processes'])
            if browser_memory > 2000:
                causes.append(f"**Browser Memory Usage**: Browsers consuming {browser_memory:.0f}MB of memory")
        
        return causes
    
    def _get_immediate_actions(self, processes: List[Dict], analysis: Dict) -> List[str]:
        """Get immediate actions to take"""
        actions = []
        
        # Critical processes to restart
        critical_processes = [p for p in processes if p['memory_percent'] > 10 and p['age_hours'] > 12]
        for proc in critical_processes[:3]:
            actions.append(f"**Restart {proc['name']}** (PID: {proc['pid']}) - Using {proc['memory_percent']:.1f}% memory for {proc['age_hours']:.1f}h")
        
        # Browser cleanup
        if analysis['browser_processes']:
            actions.append("**Close unused browser tabs** - Browser processes are consuming significant memory")
        
        # System restart if critical
        if any(p['memory_percent'] > 15 for p in processes):
            actions.append("**Consider system restart** - Multiple high-memory processes detected")
        
        return actions
    
    def _get_process_recommendations(self, processes: List[Dict], analysis: Dict) -> List[str]:
        """Get process-specific recommendations"""
        recommendations = []
        
        for proc in processes[:5]:  # Top 5 processes
            if proc['memory_percent'] > 5:
                recommendations.append(f"**{proc['name']}** (PID: {proc['pid']}):")
                recommendations.append(f"  - Memory: {proc['memory_percent']:.1f}% ({proc['memory_mb']:.1f}MB)")
                recommendations.append(f"  - Age: {proc['age_hours']:.1f} hours")
                if proc['age_hours'] > 24:
                    recommendations.append(f"  - **Action**: Restart this process (long-running)")
                elif proc['memory_percent'] > 10:
                    recommendations.append(f"  - **Action**: Monitor closely (high memory usage)")
                else:
                    recommendations.append(f"  - **Action**: Normal operation")
                recommendations.append("")
        
        return recommendations
    
    def _get_long_term_solutions(self, memory_info: Dict, analysis: Dict) -> List[str]:
        """Get long-term solutions"""
        solutions = []
        
        # RAM upgrade recommendation
        if memory_info['swap_percent'] > 50:
            solutions.append("**Consider RAM upgrade** - High swap usage indicates insufficient RAM")
        
        # Process management
        if analysis['long_running_processes']:
            solutions.append("**Implement process rotation** - Restart long-running applications regularly")
        
        # Monitoring
        solutions.append("**Set up memory monitoring** - Use tools to track memory usage over time")
        
        # Application optimization
        if analysis['browser_processes']:
            solutions.append("**Optimize browser usage** - Limit tabs and extensions")
        
        return solutions
    
    def _get_optimization_tips(self, memory_info: Dict) -> List[str]:
        """Get performance optimization tips"""
        tips = []
        
        if memory_info['swap_percent'] > 60:
            tips.append("**Reduce memory pressure** by closing unnecessary applications")
        
        if memory_info['cpu_percent'] > 70:
            tips.append("**Monitor CPU-intensive processes** and close if not needed")
        
        tips.append("**Use Activity Monitor** to identify memory-hogging applications")
        tips.append("**Restart applications regularly** instead of leaving them running for days")
        tips.append("**Limit browser tabs** - Each tab consumes memory")
        tips.append("**Check for memory leaks** in long-running applications")
        
        return tips
    
    def _get_monitoring_recommendations(self) -> List[str]:
        """Get monitoring recommendations"""
        return [
            "**Set up memory alerts** when usage exceeds 80%",
            "**Monitor swap usage** - High swap indicates memory pressure",
            "**Track process memory usage** over time to identify leaks",
            "**Use the system monitor** regularly to catch issues early",
            "**Check for zombie processes** that may be consuming resources"
        ]
    
    def _save_performance_insights(self, recommendations: Dict, system_data: Dict):
        """Save performance insights to database"""
        try:
            # Save performance assessment
            perf = recommendations['performance_assessment']
            insight = {
                'timestamp': time.time(),
                'insight_type': 'performance_assessment',
                'severity': perf['rating'].lower(),
                'description': f"System performance rated as {perf['rating']} ({perf['score']}/100)",
                'metric_name': 'overall_performance',
                'metric_value': perf['score'],
                'baseline_value': 85.0,  # Good baseline
                'deviation_percent': ((perf['score'] - 85.0) / 85.0) * 100,
                'recommendation': 'Monitor system performance and address any critical issues'
            }
            
            system_monitoring_db.save_performance_insight(insight)
            
            # Save root cause insights
            for cause in recommendations['root_causes']:
                insight = {
                    'timestamp': time.time(),
                    'insight_type': 'root_cause_analysis',
                    'severity': 'warning',
                    'description': cause,
                    'metric_name': 'system_health',
                    'metric_value': 0,
                    'baseline_value': 0,
                    'deviation_percent': 0,
                    'recommendation': 'Address root causes to improve system performance'
                }
                system_monitoring_db.save_performance_insight(insight)
                
        except Exception as e:
            console.print(f"[red]Error saving performance insights: {e}[/red]")
    
    def display_ai_analysis(self):
        """Display comprehensive AI-powered system analysis"""
        console.print(Panel.fit("🤖 AI-Powered System Analysis", style="bold blue"))
        
        # Collect system data
        system_data = self.get_comprehensive_system_data()
        if not system_data:
            console.print("[red]Error: Could not collect system data[/red]")
            return
        
        # Get AI recommendations
        recommendations = self.get_ai_recommendations(system_data)
        
        # Display performance assessment
        perf = recommendations['performance_assessment']
        console.print(f"\n[bold {perf['color']}]Performance Assessment: {perf['rating']} ({perf['score']}/100)[/bold {perf['color']}]")
        
        # Display impact details
        impact_table = Table(title="Performance Impact Analysis", show_header=True, header_style="bold magenta")
        impact_table.add_column("Component", style="cyan")
        impact_table.add_column("Status", style="green")
        impact_table.add_column("Impact", style="yellow")
        
        impact_table.add_row("Memory", f"{system_data['system']['memory_percent']:.1f}%", perf['details']['memory_impact'])
        impact_table.add_row("Swap", f"{system_data['system']['swap_percent']:.1f}%", perf['details']['swap_impact'])
        impact_table.add_row("CPU", f"{system_data['system']['cpu_percent']:.1f}%", perf['details']['cpu_impact'])
        
        console.print(impact_table)
        
        # Display root causes
        if recommendations['root_causes']:
            console.print("\n[bold red]Root Cause Analysis:[/bold red]")
            for cause in recommendations['root_causes']:
                console.print(f"• {cause}")
        
        # Display immediate actions
        if recommendations['immediate_actions']:
            console.print("\n[bold yellow]Immediate Actions:[/bold yellow]")
            for action in recommendations['immediate_actions']:
                console.print(f"• {action}")
        
        # Display process recommendations
        if recommendations['process_recommendations']:
            console.print("\n[bold blue]Process-Specific Recommendations:[/bold blue]")
            for rec in recommendations['process_recommendations']:
                console.print(rec)
        
        # Display long-term solutions
        if recommendations['long_term_solutions']:
            console.print("\n[bold green]Long-term Solutions:[/bold green]")
            for solution in recommendations['long_term_solutions']:
                console.print(f"• {solution}")
        
        # Display optimization tips
        if recommendations['optimization_tips']:
            console.print("\n[bold cyan]Performance Optimization Tips:[/bold cyan]")
            for tip in recommendations['optimization_tips']:
                console.print(f"• {tip}")
        
        # Save performance insights to database
        self._save_performance_insights(recommendations, system_data)
        
        # Display monitoring recommendations
        if recommendations['monitoring_recommendations']:
            console.print("\n[bold magenta]Monitoring Recommendations:[/bold magenta]")
            for rec in recommendations['monitoring_recommendations']:
                console.print(f"• {rec}")

def main():
    """Run AI system analysis"""
    analyzer = AISystemAnalyzer()
    analyzer.display_ai_analysis()

if __name__ == "__main__":
    main() 