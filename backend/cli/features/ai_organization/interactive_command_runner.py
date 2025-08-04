#!/usr/bin/env python3
"""
Interactive Command Runner - Ask users before running commands with arrow key selection
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

# For arrow key support
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    import tty
    import termios
    import select
    WINDOWS = False

console = Console()

class InteractiveCommandRunner:
    """Interactive command runner with arrow key selection"""
    
    def __init__(self):
        """Initialize the command runner"""
        self.commands = []
        self.selected_index = 0
        self.max_display = 10
        
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
    
    def _get_key(self) -> str:
        """Get a single key press, handling arrow keys"""
        if WINDOWS:
            # Windows implementation
            key = msvcrt.getch()
            if key == b'\xe0':  # Arrow key prefix
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    return 'UP'
                elif key == b'P':  # Down arrow
                    return 'DOWN'
                elif key == b'K':  # Left arrow
                    return 'LEFT'
                elif key == b'M':  # Right arrow
                    return 'RIGHT'
            elif key == b'\r':  # Enter
                return 'ENTER'
            elif key == b' ':  # Space
                return 'SPACE'
            elif key == b'q' or key == b'Q':  # Quit
                return 'QUIT'
            else:
                return key.decode('utf-8', errors='ignore')
        else:
            # Unix/Linux implementation
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # ESC sequence
                    next1, next2 = sys.stdin.read(2)
                    if next1 == '[':
                        if next2 == 'A':  # Up arrow
                            return 'UP'
                        elif next2 == 'B':  # Down arrow
                            return 'DOWN'
                        elif next2 == 'C':  # Right arrow
                            return 'RIGHT'
                        elif next2 == 'D':  # Left arrow
                            return 'LEFT'
                elif ch == '\r':  # Enter
                    return 'ENTER'
                elif ch == ' ':  # Space
                    return 'SPACE'
                elif ch == 'q' or ch == 'Q':  # Quit
                    return 'QUIT'
                else:
                    return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _display_commands(self):
        """Display commands with selection indicator"""
        if not self.commands:
            console.print("[yellow]No commands to display[/yellow]")
            return
        
        # Create table
        table = Table(title="Interactive Command Runner", show_header=True)
        table.add_column("Select", style="cyan", width=8)
        table.add_column("Command", style="green", width=40)
        table.add_column("Description", style="yellow", width=50)
        table.add_column("Category", style="blue", width=15)
        table.add_column("Status", style="magenta", width=10)
        
        # Calculate display range
        start_idx = max(0, self.selected_index - self.max_display // 2)
        end_idx = min(len(self.commands), start_idx + self.max_display)
        
        for i in range(start_idx, end_idx):
            cmd = self.commands[i]
            
            # Selection indicator
            if i == self.selected_index:
                select_indicator = "▶ [bold cyan]SELECTED[/bold cyan]"
            else:
                select_indicator = "   "
            
            # Status indicator
            if cmd['executed']:
                if cmd['result'] and cmd['result'].get('success', False):
                    status = "✅ Success"
                else:
                    status = "❌ Failed"
            else:
                status = "⏳ Pending"
            
            table.add_row(
                select_indicator,
                cmd['command'][:38] + "..." if len(cmd['command']) > 40 else cmd['command'],
                cmd['description'][:47] + "..." if len(cmd['description']) > 50 else cmd['description'],
                cmd['category'],
                status
            )
        
        console.print(table)
        
        # Show navigation help
        help_text = """
[bold]Navigation:[/bold]
• ↑/↓ Arrow keys: Move selection
• Enter: Execute selected command
• Space: Toggle command selection
• Q: Quit without executing
• A: Execute all commands
• S: Show command details
        """
        console.print(Panel(help_text, title="Help", border_style="blue"))
    
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
    
    def _show_command_details(self):
        """Show detailed information about selected command"""
        if not self.commands or self.selected_index >= len(self.commands):
            return
        
        cmd = self.commands[self.selected_index]
        
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
        input("Press Enter to continue...")
    
    def run_interactive(self) -> List[Dict[str, Any]]:
        """Run the interactive command selection"""
        if not self.commands:
            console.print("[yellow]No commands to run[/yellow]")
            return []
        
        console.print("[bold cyan]Interactive Command Runner[/bold cyan]")
        console.print(f"Loaded {len(self.commands)} commands")
        
        while True:
            # Clear screen and display commands
            os.system('clear' if os.name == 'posix' else 'cls')
            self._display_commands()
            
            # Get user input
            key = self._get_key()
            
            if key == 'UP':
                self.selected_index = max(0, self.selected_index - 1)
            elif key == 'DOWN':
                self.selected_index = min(len(self.commands) - 1, self.selected_index + 1)
            elif key == 'ENTER':
                # Execute selected command
                if self.selected_index < len(self.commands):
                    cmd = self.commands[self.selected_index]
                    if not cmd['executed']:
                        result = self._execute_command(cmd['command'])
                        cmd['executed'] = True
                        cmd['result'] = result
                        input("Press Enter to continue...")
            elif key == 'SPACE':
                # Toggle command selection (for future batch operations)
                pass
            elif key == 'S':
                # Show command details
                self._show_command_details()
            elif key == 'A':
                # Execute all commands
                if Confirm.ask("Execute all commands?"):
                    self._execute_all_commands()
                    break
            elif key == 'QUIT':
                # Quit without executing
                if Confirm.ask("Quit without executing remaining commands?"):
                    break
        
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
            'command': 'netstat -an | grep LISTEN',
            'description': 'Show listening network ports',
            'category': 'network'
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
    runner = InteractiveCommandRunner()
    
    # Add some example commands
    commands = create_system_commands()
    runner.add_commands(commands)
    
    # Run interactive session
    results = runner.run_interactive()
    
    console.print(f"\n[green]Session completed! {len(results)} commands executed.[/green]")

if __name__ == "__main__":
    main() 