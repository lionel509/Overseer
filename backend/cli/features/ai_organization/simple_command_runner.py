#!/usr/bin/env python3
"""
Simple Command Runner - Ask users before running commands with selection
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class SimpleCommandRunner:
    """Simple command runner with user confirmation"""
    
    def __init__(self):
        """Initialize the command runner"""
        self.commands = []
        
    def add_command(self, command: str, description: str = "", category: str = "general"):
        """Add a command to the list"""
        self.commands.append({
            'command': command,
            'description': description,
            'category': category,
            'executed': False,
            'result': None
        })
    
    def add_commands(self, commands: List[Dict[str, str]]):
        """Add multiple commands at once"""
        for cmd in commands:
            self.add_command(
                command=cmd.get('command', ''),
                description=cmd.get('description', ''),
                category=cmd.get('category', 'general')
            )
    
    def _display_commands(self):
        """Display all commands with numbers"""
        if not self.commands:
            console.print("[yellow]No commands to display[/yellow]")
            return
        
        table = Table(title="Available Commands", show_header=True)
        table.add_column("#", style="cyan", width=5)
        table.add_column("Command", style="green", width=40)
        table.add_column("Description", style="yellow", width=50)
        table.add_column("Category", style="blue", width=15)
        table.add_column("Status", style="magenta", width=10)
        
        for i, cmd in enumerate(self.commands, 1):
            # Status indicator
            if cmd['executed']:
                if cmd['result'] and cmd['result'].get('success', False):
                    status = "✅ Success"
                else:
                    status = "❌ Failed"
            else:
                status = "⏳ Pending"
            
            table.add_row(
                str(i),
                cmd['command'][:38] + "..." if len(cmd['command']) > 40 else cmd['command'],
                cmd['description'][:47] + "..." if len(cmd['description']) > 50 else cmd['description'],
                cmd['category'],
                status
            )
        
        console.print(table)
    
    def _execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a single command safely"""
        try:
            console.print(f"[yellow]Executing: {command}[/yellow]")
            
            # Execute command with timeout
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                console.print(f"[green]✅ Success: {command}[/green]")
                if result.stdout:
                    console.print(f"[dim]Output: {result.stdout[:200]}...[/dim]")
                return {
                    'success': True,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                console.print(f"[red]❌ Failed: {command}[/red]")
                if result.stderr:
                    console.print(f"[dim]Error: {result.stderr[:200]}...[/dim]")
                return {
                    'success': False,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            console.print(f"[red]⏰ Timeout: {command}[/red]")
            return {
                'success': False,
                'error': 'Timeout',
                'returncode': -1
            }
        except Exception as e:
            console.print(f"[red]💥 Error: {command} - {e}[/red]")
            return {
                'success': False,
                'error': str(e),
                'returncode': -1
            }
    
    def _show_command_details(self, index: int):
        """Show detailed information about a command"""
        if index < 0 or index >= len(self.commands):
            return
        
        cmd = self.commands[index]
        
        details = f"""
[bold cyan]Command Details[/bold cyan]

[bold]Command:[/bold] {cmd['command']}
[bold]Description:[/bold] {cmd['description']}
[bold]Category:[/bold] {cmd['category']}
[bold]Status:[/bold] {'Executed' if cmd['executed'] else 'Pending'}

[bold]Full Command:[/bold]
{cmd['command']}

[bold]Description:[/bold]
{cmd['description']}
        """
        
        if cmd['executed'] and cmd['result']:
            details += f"""
[bold]Execution Result:[/bold]
• Success: {'Yes' if cmd['result'].get('success', False) else 'No'}
• Return Code: {cmd['result'].get('returncode', 'Unknown')}
• Output: {cmd['result'].get('stdout', 'None')[:500]}...
• Error: {cmd['result'].get('stderr', 'None')[:500]}...
            """
        
        console.print(Panel(details, title="Command Details", border_style="cyan"))
    
    def run_interactive(self) -> List[Dict[str, Any]]:
        """Run the interactive command selection"""
        if not self.commands:
            console.print("[yellow]No commands to run[/yellow]")
            return []
        
        console.print("[bold cyan]Simple Command Runner[/bold cyan]")
        console.print(f"Loaded {len(self.commands)} commands")
        
        while True:
            # Display commands
            self._display_commands()
            
            # Show options
            console.print("\n[bold]Options:[/bold]")
            console.print("• Enter command number to execute")
            console.print("• 'd <number>' to show command details")
            console.print("• 'a' to execute all commands")
            console.print("• 'q' to quit")
            
            # Get user input
            user_input = Prompt.ask("\n[bold green]Command[/bold green]").strip()
            
            if user_input.lower() == 'q':
                if Confirm.ask("Quit without executing remaining commands?"):
                    break
            elif user_input.lower() == 'a':
                if Confirm.ask("Execute all commands?"):
                    self._execute_all_commands()
                    break
            elif user_input.lower().startswith('d '):
                try:
                    cmd_num = int(user_input[2:])
                    if 1 <= cmd_num <= len(self.commands):
                        self._show_command_details(cmd_num - 1)
                        input("Press Enter to continue...")
                    else:
                        console.print("[red]Invalid command number[/red]")
                except ValueError:
                    console.print("[red]Invalid command number[/red]")
            else:
                try:
                    cmd_num = int(user_input)
                    if 1 <= cmd_num <= len(self.commands):
                        cmd = self.commands[cmd_num - 1]
                        if not cmd['executed']:
                            if Confirm.ask(f"Execute: {cmd['command']}?"):
                                result = self._execute_command(cmd['command'])
                                cmd['executed'] = True
                                cmd['result'] = result
                                input("Press Enter to continue...")
                        else:
                            console.print("[yellow]Command already executed[/yellow]")
                            input("Press Enter to continue...")
                    else:
                        console.print("[red]Invalid command number[/red]")
                except ValueError:
                    console.print("[red]Invalid input[/red]")
        
        # Show final results
        self._show_final_results()
        return [cmd for cmd in self.commands if cmd['executed']]
    
    def _execute_all_commands(self):
        """Execute all pending commands"""
        console.print("[yellow]Executing all commands...[/yellow]")
        
        for i, cmd in enumerate(self.commands):
            if not cmd['executed']:
                console.print(f"\n[{i+1}/{len(self.commands)}] Executing: {cmd['command']}")
                result = self._execute_command(cmd['command'])
                cmd['executed'] = True
                cmd['result'] = result
    
    def _show_final_results(self):
        """Show final execution results"""
        executed = [cmd for cmd in self.commands if cmd['executed']]
        successful = [cmd for cmd in executed if cmd['result'] and cmd['result'].get('success', False)]
        
        console.print(Panel(f"""
[bold]Execution Summary[/bold]

📊 Total Commands: {len(self.commands)}
✅ Executed: {len(executed)}
🎯 Successful: {len(successful)}
❌ Failed: {len(executed) - len(successful)}

[bold]Results:[/bold]
        """, title="Final Results", border_style="green"))
        
        if executed:
            table = Table(show_header=True)
            table.add_column("Command", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Return Code", style="yellow")
            
            for cmd in executed:
                status = "✅ Success" if cmd['result'] and cmd['result'].get('success', False) else "❌ Failed"
                return_code = cmd['result'].get('returncode', 'Unknown') if cmd['result'] else 'Unknown'
                
                table.add_row(
                    cmd['command'][:50] + "..." if len(cmd['command']) > 50 else cmd['command'],
                    status,
                    str(return_code)
                )
            
            console.print(table)

def create_system_commands() -> List[Dict[str, str]]:
    """Create a list of system monitoring commands"""
    return [
        {
            'command': 'system_profiler SPHardwareDataType',
            'description': 'Get detailed system hardware information',
            'category': 'system_info'
        },
        {
            'command': 'top -l 1 | head -10',
            'description': 'Show top 10 processes by CPU usage',
            'category': 'processes'
        },
        {
            'command': 'df -h',
            'description': 'Show disk usage information',
            'category': 'disk'
        },
        {
            'command': 'ps aux --sort=-%mem | head -5',
            'description': 'Show top 5 memory-consuming processes',
            'category': 'memory'
        },
        {
            'command': 'ls -la ~/.overseer/',
            'description': 'List Overseer configuration files',
            'category': 'config'
        },
        {
            'command': 'find . -name "*.py" -type f | head -10',
            'description': 'Find Python files in current directory',
            'category': 'files'
        },
        {
            'command': 'git status',
            'description': 'Check git repository status',
            'category': 'git'
        }
    ]

def main():
    """Main function for testing"""
    runner = SimpleCommandRunner()
    
    # Add some example commands
    commands = create_system_commands()
    runner.add_commands(commands)
    
    # Run interactive session
    results = runner.run_interactive()
    
    console.print(f"\n[green]Session completed! {len(results)} commands executed.[/green]")

if __name__ == "__main__":
    main() 