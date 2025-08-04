#!/usr/bin/env python3
"""
Interactive Command Recommender for System Monitoring with LLM Integration
"""
import psutil
import subprocess
import time
import json
import re
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align

console = Console()

class InteractiveCommandRecommender:
    """Interactive command recommender with LLM-powered dynamic recommendations"""
    
    def __init__(self):
        self.commands = []
        self.current_index = 0
        self.page_size = 5
        self.llm_backend = None
        self._load_llm_backend()
    
    def _load_llm_backend(self):
        """Load LLM backend for command generation"""
        try:
            # Try to load the LLM backend from the main CLI
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            from overseer_cli import get_llm_backend, load_config
            config = load_config()
            self.llm_backend = get_llm_backend(config)
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load LLM backend: {e}[/yellow]")
            console.print("[yellow]Falling back to static command recommendations[/yellow]")
            self.llm_backend = None
        
    def get_system_commands(self) -> List[Dict]:
        """Get recommended system commands based on current state"""
        commands = []
        
        # Memory-related commands
        commands.append({
            'name': 'Top Memory Users',
            'command': 'ps aux --sort=-%mem | head -10',
            'description': 'Show top 10 memory-consuming processes',
            'category': 'Memory',
            'priority': 'high'
        })
        
        commands.append({
            'name': 'Memory Usage Overview',
            'command': 'vm_stat',
            'description': 'Display memory usage in human-readable format (macOS)',
            'category': 'Memory',
            'priority': 'medium'
        })
        
        commands.append({
            'name': 'Memory Usage Monitor',
            'command': 'top -l 1 | grep PhysMem',
            'description': 'Monitor memory usage in real-time (macOS)',
            'category': 'Memory',
            'priority': 'medium'
        })
        
        commands.append({
            'name': 'Zombie Process Check',
            'command': 'ps aux | grep -w Z',
            'description': 'Check for zombie processes',
            'category': 'Memory',
            'priority': 'low'
        })
        
        # CPU-related commands
        commands.append({
            'name': 'Top CPU Users',
            'command': 'ps aux --sort=-%cpu | head -10',
            'description': 'Show top 10 CPU-consuming processes',
            'category': 'CPU',
            'priority': 'high'
        })
        
        commands.append({
            'name': 'CPU Load Average',
            'command': 'uptime',
            'description': 'Show system load average',
            'category': 'CPU',
            'priority': 'medium'
        })
        
        commands.append({
            'name': 'CPU Usage Monitor',
            'command': 'top -l 1 | head -10',
            'description': 'Show current CPU usage (macOS)',
            'category': 'CPU',
            'priority': 'medium'
        })
        
        # Disk-related commands
        commands.append({
            'name': 'Disk Usage',
            'command': 'df -h',
            'description': 'Show disk usage by filesystem',
            'category': 'Disk',
            'priority': 'high'
        })
        
        commands.append({
            'name': 'Large Files Finder',
            'command': 'find / -type f -size +100M 2>/dev/null | head -10',
            'description': 'Find files larger than 100MB',
            'category': 'Disk',
            'priority': 'medium'
        })
        
        commands.append({
            'name': 'Disk Space Monitor',
            'command': 'du -sh /* 2>/dev/null | sort -hr | head -10',
            'description': 'Show largest directories',
            'category': 'Disk',
            'priority': 'medium'
        })
        
        # Network-related commands
        commands.append({
            'name': 'Network Connections',
            'command': 'netstat -tuln | head -10',
            'description': 'Show active network connections',
            'category': 'Network',
            'priority': 'medium'
        })
        
        commands.append({
            'name': 'Network Usage',
            'command': 'netstat -i',
            'description': 'Show network interface statistics (macOS)',
            'category': 'Network',
            'priority': 'low'
        })
        
        # System health commands
        commands.append({
            'name': 'System Uptime',
            'command': 'uptime',
            'description': 'Show system uptime and load',
            'category': 'System',
            'priority': 'low'
        })
        
        commands.append({
            'name': 'Process Count',
            'command': 'ps aux | wc -l',
            'description': 'Count total running processes',
            'category': 'System',
            'priority': 'low'
        })
        
        commands.append({
            'name': 'Kill High Memory Process',
            'command': 'echo "Use: kill -9 <PID> to kill specific process"',
            'description': 'Template for killing high-memory processes',
            'category': 'System',
            'priority': 'high'
        })
        
        return commands
    
    def generate_llm_commands(self, system_stats: Dict) -> List[Dict]:
        """Generate commands using LLM based on current system state"""
        if not self.llm_backend:
            return self.get_system_commands()
        
        try:
            # Create system analysis prompt
            prompt = self._create_system_analysis_prompt(system_stats)
            
            # Get LLM response
            response = self.llm_backend.run(prompt)
            
            # Parse LLM response into commands
            commands = self._parse_llm_response(response)
            
            if commands:
                console.print(f"[green]✓ Generated {len(commands)} LLM-powered command recommendations[/green]")
                return commands
            else:
                console.print(f"[yellow]⚠ LLM response could not be parsed, using fallback commands[/yellow]")
                return self.get_system_commands()
                
        except Exception as e:
            console.print(f"[red]Error generating LLM commands: {e}[/red]")
            console.print(f"[yellow]Falling back to static command recommendations[/yellow]")
            return self.get_system_commands()
    
    def _create_system_analysis_prompt(self, system_stats: Dict) -> str:
        """Create prompt for LLM to analyze system and recommend commands"""
        cpu_percent = system_stats.get('cpu', {}).get('percent', 0)
        memory_percent = system_stats.get('memory', {}).get('percent', 0)
        disk_percent = system_stats.get('disk', {}).get('percent', 0)
        
        prompt = f"""
You are a system administration expert. Analyze the current system state and recommend the most useful commands for troubleshooting and monitoring.

Current System State:
- CPU Usage: {cpu_percent:.1f}%
- Memory Usage: {memory_percent:.1f}%
- Disk Usage: {disk_percent:.1f}%

Based on this system state, recommend 8-12 specific, actionable commands that would be most useful for:
1. Diagnosing any issues
2. Monitoring system health
3. Troubleshooting performance problems
4. Gathering system information

For each command, provide:
- A descriptive name
- The exact command to run
- A brief description of what it does
- Priority level (high/medium/low)
- Category (Memory/CPU/Disk/Network/System)

Format your response as a JSON array of objects with these fields:
- name: descriptive name
- command: exact command to run
- description: what the command does
- category: Memory/CPU/Disk/Network/System
- priority: high/medium/low

Focus on macOS-compatible commands. Prioritize commands that would be most useful given the current system state.

Example format:
[
  {{
    "name": "Check Memory Usage",
    "command": "vm_stat",
    "description": "Display detailed memory statistics",
    "category": "Memory",
    "priority": "high"
  }}
]

Respond with ONLY the JSON array, no additional text.
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured command list"""
        try:
            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            commands = json.loads(cleaned_response)
            
            # Validate command structure
            valid_commands = []
            for cmd in commands:
                if isinstance(cmd, dict) and all(key in cmd for key in ['name', 'command', 'description', 'category', 'priority']):
                    # Ensure command is safe (no dangerous commands)
                    if self._is_safe_command(cmd['command']):
                        valid_commands.append(cmd)
            
            return valid_commands
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            console.print(f"[red]Error parsing LLM response: {e}[/red]")
            return []
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        dangerous_patterns = [
            r'\brm\s+-rf\b',  # rm -rf
            r'\bmkfs\b',      # format filesystem
            r'\bdd\b',        # dd command
            r'\bchmod\s+777\b',  # dangerous chmod
            r'\bchown\s+root\b', # dangerous chown
            r'\bsudo\b',      # sudo commands
            r'\bsu\b',        # su commands
            r'\bkillall\b',   # killall
            r'\bshutdown\b',  # shutdown
            r'\breboot\b',    # reboot
            r'\bhalt\b',      # halt
            r'\bpoweroff\b',  # poweroff
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        return True
    
    def analyze_system_and_recommend(self) -> List[Dict]:
        """Analyze system and return LLM-powered prioritized commands"""
        try:
            # Get current system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Create system stats dict for LLM
            system_stats = {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'percent': memory.percent,
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used
                },
                'disk': {
                    'percent': disk.percent,
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free
                }
            }
            
            # Use LLM to generate dynamic commands
            if self.llm_backend:
                console.print("[cyan]🤖 Using LLM to generate intelligent command recommendations...[/cyan]")
                commands = self.generate_llm_commands(system_stats)
            else:
                console.print("[yellow]⚠ Using fallback static command recommendations[/yellow]")
                commands = self.get_system_commands()
            
            # Sort by priority (high first)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            commands.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
            
            return commands
            
        except Exception as e:
            console.print(f"[red]Error analyzing system: {e}[/red]")
            return self.get_system_commands()
    
    def display_command_table(self, commands: List[Dict], start_idx: int = 0):
        """Display commands in a scrollable table"""
        if not commands:
            console.print("[yellow]No commands available[/yellow]")
            return
        
        end_idx = min(start_idx + self.page_size, len(commands))
        current_commands = commands[start_idx:end_idx]
        
        # Create table
        table = Table(title=f"Recommended Commands ({start_idx + 1}-{end_idx} of {len(commands)})", 
                     show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Name", style="green", width=25)
        table.add_column("Command", style="blue", width=40)
        table.add_column("Description", style="yellow", width=50)
        table.add_column("Category", style="red", width=10)
        table.add_column("Priority", style="white", width=8)
        
        for i, cmd in enumerate(current_commands, start_idx + 1):
            # Color code priority
            priority_style = "bold red" if cmd['priority'] == 'high' else "bold yellow" if cmd['priority'] == 'medium' else "white"
            
            table.add_row(
                str(i),
                cmd['name'],
                cmd['command'][:38] + "..." if len(cmd['command']) > 40 else cmd['command'],
                cmd['description'],
                cmd['category'],
                cmd['priority'],
                style=priority_style
            )
        
        console.print(table)
        
        # Show navigation info
        if len(commands) > self.page_size:
            console.print(f"\n[cyan]Navigation:[/cyan] [n]ext, [p]revious, [q]uit, [1-{len(commands)}] to select")
        else:
            console.print(f"\n[cyan]Navigation:[/cyan] [q]uit, [1-{len(commands)}] to select")
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a command and return result"""
        try:
            console.print(f"\n[green]Executing:[/green] {command}")
            
            # Use timeout to prevent hanging
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, str(e)
    
    def show_command_details(self, command: Dict):
        """Show detailed information about a command"""
        console.print(f"\n[bold cyan]Command Details:[/bold cyan]")
        console.print(f"Name: {command['name']}")
        console.print(f"Command: {command['command']}")
        console.print(f"Description: {command['description']}")
        console.print(f"Category: {command['category']}")
        console.print(f"Priority: {command['priority']}")
        
        # Ask if user wants to execute
        if Confirm.ask(f"\nDo you want to execute this command?"):
            success, output = self.execute_command(command['command'])
            
            if success:
                console.print(f"\n[green]Command executed successfully:[/green]")
                console.print(Panel(output, title="Output", border_style="green"))
            else:
                console.print(f"\n[red]Command failed:[/red]")
                console.print(Panel(output, title="Error", border_style="red"))
    
    def run_interactive(self):
        """Run the interactive command recommender"""
        console.print(Panel.fit(
            "[bold cyan]Interactive Command Recommender[/bold cyan]\n"
            "Analyzing your system and recommending useful commands...",
            border_style="cyan"
        ))
        
        # Get recommended commands
        commands = self.analyze_system_and_recommend()
        
        if not commands:
            console.print("[red]No commands available[/red]")
            return
        
        # Show system analysis
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            console.print(f"\n[bold yellow]System Analysis:[/bold yellow]")
            console.print(f"CPU Usage: {cpu_percent:.1f}%")
            console.print(f"Memory Usage: {memory.percent:.1f}%")
            console.print(f"Disk Usage: {disk.percent:.1f}%")
            
            if memory.percent > 80 or cpu_percent > 80 or disk.percent > 80:
                console.print(f"\n[bold red]⚠️  System resources are under pressure![/bold red]")
                console.print(f"[yellow]High priority commands are recommended.[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error analyzing system: {e}[/red]")
        
        # Interactive loop
        current_page = 0
        while True:
            console.print("\n" + "="*80)
            self.display_command_table(commands, current_page * self.page_size)
            
            # Get user input
            user_input = Prompt.ask("\n[cyan]Enter command number, navigation (n/p/q), or 'help':[/cyan]")
            
            if user_input.lower() == 'q' or user_input.lower() == 'quit':
                console.print("[yellow]Exiting command recommender...[/yellow]")
                break
            elif user_input.lower() == 'n' or user_input.lower() == 'next':
                if (current_page + 1) * self.page_size < len(commands):
                    current_page += 1
                else:
                    console.print("[yellow]Already at last page[/yellow]")
            elif user_input.lower() == 'p' or user_input.lower() == 'prev' or user_input.lower() == 'previous':
                if current_page > 0:
                    current_page -= 1
                else:
                    console.print("[yellow]Already at first page[/yellow]")
            elif user_input.lower() == 'help':
                console.print(Panel(
                    "[bold cyan]Navigation Help:[/bold cyan]\n"
                    "• Enter a number (1-{}) to select and execute a command\n"
                    "• 'n' or 'next' to go to next page\n"
                    "• 'p' or 'prev' to go to previous page\n"
                    "• 'q' or 'quit' to exit\n"
                    "• 'help' to show this help".format(len(commands)),
                    title="Help",
                    border_style="cyan"
                ))
            else:
                try:
                    command_num = int(user_input)
                    if 1 <= command_num <= len(commands):
                        selected_command = commands[command_num - 1]
                        self.show_command_details(selected_command)
                    else:
                        console.print(f"[red]Invalid command number. Please enter 1-{len(commands)}[/red]")
                except ValueError:
                    console.print("[red]Invalid input. Please enter a number or navigation command.[/red]")

def get_command_recommender():
    """Lazy load command recommender"""
    return InteractiveCommandRecommender()

def show_interactive_commands():
    """Show interactive command recommender"""
    recommender = get_command_recommender()
    recommender.run_interactive()

if __name__ == "__main__":
    show_interactive_commands() 