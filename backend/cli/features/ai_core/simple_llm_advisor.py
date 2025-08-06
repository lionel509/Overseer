"""
Simple LLM Advisor for demo purposes
Provides basic system advice without external dependencies.
"""

import os
import platform
import shutil
import psutil
from datetime import datetime

class LLMAdvisor:
    """Simple LLM Advisor that provides system advice"""
    
    def __init__(self):
        self.console_available = True
        try:
            from rich.console import Console
            self.console = Console()
        except ImportError:
            self.console_available = False
    
    def _print(self, message: str, style: str = ""):
        """Print message with or without rich formatting"""
        if self.console_available and style:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def get_system_info(self) -> dict:
        """Get basic system information"""
        try:
            # Get basic system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': cpu_percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_used_percent': memory.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_used_percent': round((disk.used / disk.total) * 100, 1),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': f"Could not gather system info: {e}"}
    
    def analyze_performance_issue(self, prompt: str) -> str:
        """Analyze performance issues and provide advice"""
        prompt_lower = prompt.lower()
        advice = []
        
        # Get system info
        sys_info = self.get_system_info()
        
        if 'error' in sys_info:
            return f"System analysis unavailable: {sys_info['error']}"
        
        # Header
        advice.append("🔍 LLM ADVISOR - System Analysis")
        advice.append("=" * 40)
        
        # Basic system info
        advice.append(f"Platform: {sys_info.get('platform', 'Unknown')} | CPU Cores: {sys_info.get('cpu_count', 'Unknown')}")
        advice.append(f"Memory: {sys_info.get('memory_total_gb', 'Unknown')}GB | Disk: {sys_info.get('disk_total_gb', 'Unknown')}GB")
        advice.append("")
        
        # Current usage
        advice.append("📊 Current System Usage:")
        advice.append(f"  • CPU Usage: {sys_info.get('cpu_percent', 'Unknown')}%")
        advice.append(f"  • Memory Usage: {sys_info.get('memory_used_percent', 'Unknown')}%")
        advice.append(f"  • Disk Usage: {sys_info.get('disk_used_percent', 'Unknown')}%")
        advice.append("")
        
        # Specific advice based on prompt
        if any(word in prompt_lower for word in ['slow', 'performance', 'lag', 'freeze']):
            advice.append("🚀 Performance Optimization Advice:")
            
            if sys_info.get('cpu_percent', 0) > 80:
                advice.append("  ⚠️  High CPU usage detected!")
                advice.append("     → Check running processes with: top or htop")
                advice.append("     → Consider closing unnecessary applications")
            
            if sys_info.get('memory_used_percent', 0) > 80:
                advice.append("  ⚠️  High memory usage detected!")
                advice.append("     → Restart memory-heavy applications")
                advice.append("     → Consider adding more RAM if this persists")
            
            if sys_info.get('disk_used_percent', 0) > 90:
                advice.append("  ⚠️  Disk almost full!")
                advice.append("     → Clean up unnecessary files")
                advice.append("     → Use: du -h --max-depth=1 / to find large directories")
            
            # General advice
            advice.append("  💡 General suggestions:")
            advice.append("     → Restart your system if uptime is very high")
            advice.append("     → Check for system updates")
            advice.append("     → Run disk cleanup utilities")
            advice.append("     → Scan for malware if unexpected slowdown")
        
        elif any(word in prompt_lower for word in ['memory', 'ram']):
            advice.append("🧠 Memory Analysis:")
            advice.append(f"  • Available RAM: {sys_info.get('memory_total_gb', 'Unknown')}GB")
            advice.append(f"  • Current usage: {sys_info.get('memory_used_percent', 'Unknown')}%")
            advice.append("  💡 Memory optimization tips:")
            advice.append("     → Close unused browser tabs")
            advice.append("     → Quit applications you're not using")
            advice.append("     → Use Activity Monitor (Mac) or Task Manager (Windows)")
        
        elif any(word in prompt_lower for word in ['disk', 'storage', 'space']):
            advice.append("💾 Disk Analysis:")
            advice.append(f"  • Total storage: {sys_info.get('disk_total_gb', 'Unknown')}GB")
            advice.append(f"  • Current usage: {sys_info.get('disk_used_percent', 'Unknown')}%")
            advice.append("  💡 Storage optimization tips:")
            advice.append("     → Empty trash/recycle bin")
            advice.append("     → Clear browser cache and downloads")
            advice.append("     → Remove old files and applications")
            advice.append("     → Use cloud storage for large files")
        
        else:
            advice.append("🤖 General System Health Check:")
            advice.append("  Your system appears to be running normally.")
            advice.append("  💡 Maintenance suggestions:")
            advice.append("     → Regular restarts help clear memory")
            advice.append("     → Keep your system updated")
            advice.append("     → Monitor disk space regularly")
            advice.append("     → Run antivirus scans periodically")
        
        advice.append("")
        advice.append("📝 Need more help? Try:")
        advice.append("   • 'overseer --feature performance_optimizer'")
        advice.append("   • 'top' or 'htop' for process monitoring")
        advice.append("   • System-specific monitoring tools")
        
        return '\n'.join(advice)
    
    def run_once(self, prompt: str):
        """Run a single analysis"""
        try:
            result = self.analyze_performance_issue(prompt)
            self._print(result)
        except Exception as e:
            self._print(f"Error running analysis: {e}", "red")

if __name__ == "__main__":
    import sys
    advisor = LLMAdvisor()
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        advisor.run_once(prompt)
    else:
        print("Usage: python simple_llm_advisor.py <prompt>")
