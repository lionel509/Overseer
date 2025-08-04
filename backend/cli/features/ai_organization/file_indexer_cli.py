#!/usr/bin/env python3
"""
File Indexer CLI - Interactive interface for enhanced file indexing
"""

import os
import sys
import time
import sqlite3
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from features.ai_organization.enhanced_file_indexer import EnhancedFileIndexer

console = Console()

class FileIndexerCLI:
    """Interactive CLI for the enhanced file indexer"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.indexer = EnhancedFileIndexer()
        
    def show_help(self):
        """Show help information"""
        console.print(Panel("""
[bold cyan]Enhanced File Indexer CLI[/bold cyan]

[bold green]Commands:[/bold green]
• index <path>          - Index files in directory
• search <query>        - Search files by description
• stats                 - Show indexing statistics
• info <file>           - Show detailed file information
• reindex <path>        - Re-index directory (force update)
• clear                 - Clear all indexed files
• help                  - Show this help

[bold yellow]Examples:[/bold yellow]
• index .               - Index current directory
• index ~/Documents     - Index Documents folder
• search "python function" - Find Python files with functions
• search "configuration" - Find config files
• info /path/to/file.py - Show file details

[bold blue]Features:[/bold blue]
• Local-only indexing (no cloud dependencies)
• Semantic search by file content
• Automatic file type detection
• Content analysis and tagging
• Complexity scoring
• Fast incremental updates

Type 'exit' to return to main CLI
        """, title="File Indexer Help", border_style="blue"))
    
    def index_directory(self, directory_path: str, force: bool = False):
        """Index a directory"""
        try:
            if not os.path.exists(directory_path):
                console.print(f"[red]Directory does not exist: {directory_path}[/red]")
                return
            
            console.print(f"[yellow]Indexing directory: {directory_path}[/yellow]")
            
            if force:
                console.print("[yellow]Force re-indexing enabled[/yellow]")
            
            # Index the directory
            stats = self.indexer.index_directory(directory_path, recursive=True)
            
            # Display results
            console.print(Panel(f"""
[bold green]Indexing Complete![/bold green]

📁 Directory: {directory_path}
📊 Total files found: {stats['total_files']}
✅ Successfully indexed: {stats['indexed_files']}
⏭️  Skipped (unsupported): {stats['skipped_files']}
❌ Errors: {stats['errors']}

[bold cyan]File Types:[/bold cyan]
{chr(10).join([f"• {file_type}: {count}" for file_type, count in stats['file_types'].items()])}
            """, title="Indexing Results", border_style="green"))
            
        except Exception as e:
            console.print(f"[red]Error indexing directory: {e}[/red]")
    
    def search_files(self, query: str, limit: int = 20):
        """Search files by description"""
        try:
            console.print(f"[yellow]Searching for: {query}[/yellow]")
            
            results = self.indexer.search_files(query, limit=limit)
            
            if not results:
                console.print("[yellow]No files found matching your query.[/yellow]")
                return
            
            console.print(f"[green]Found {len(results)} files:[/green]")
            self.indexer.display_search_results(results)
            
        except Exception as e:
            console.print(f"[red]Error searching files: {e}[/red]")
    
    def show_file_info(self, file_path: str):
        """Show detailed information about a file"""
        try:
            info = self.indexer.get_file_info(file_path)
            
            if not info:
                console.print(f"[red]File not found in index: {file_path}[/red]")
                return
            
            console.print(Panel(f"""
[bold cyan]File Information[/bold cyan]

📁 Path: {info['file_path']}
🔍 Type: {info['file_type']}
📏 Size: {info['file_size']:,} bytes
🕒 Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['last_modified']))}
📅 Indexed: {info['last_indexed']}

[bold yellow]Analysis:[/bold yellow]
📝 Category: {info['file_category']}
🌐 Language: {info['language']}
📊 Complexity: {info['complexity_score']:.2f}

🏷️  Tags: {', '.join(info['semantic_tags']) if info['semantic_tags'] else 'None'}

[bold green]Summary:[/bold green]
{info['content_summary']}

[bold blue]Metadata:[/bold blue]
• Lines: {info['metadata'].get('line_count', 'N/A')}
• Characters: {info['metadata'].get('char_count', 'N/A')}
• Has imports: {info['metadata'].get('has_imports', False)}
• Has functions: {info['metadata'].get('has_functions', False)}
• Has classes: {info['metadata'].get('has_classes', False)}
• Has comments: {info['metadata'].get('has_comments', False)}
            """, title="File Details", border_style="cyan"))
            
        except Exception as e:
            console.print(f"[red]Error getting file info: {e}[/red]")
    
    def show_stats(self):
        """Show indexing statistics"""
        try:
            stats = self.indexer.get_index_stats()
            
            if not stats:
                console.print("[yellow]No files indexed yet.[/yellow]")
                return
            
            # Create tables for stats
            file_types_table = Table(title="File Types", show_header=True)
            file_types_table.add_column("Type", style="cyan")
            file_types_table.add_column("Count", style="green")
            
            for file_type, count in stats['file_types'].items():
                file_types_table.add_row(file_type, str(count))
            
            categories_table = Table(title="Categories", show_header=True)
            categories_table.add_column("Category", style="yellow")
            categories_table.add_column("Count", style="green")
            
            for category, count in stats['categories'].items():
                categories_table.add_row(category, str(count))
            
            languages_table = Table(title="Languages", show_header=True)
            languages_table.add_column("Language", style="blue")
            languages_table.add_column("Count", style="green")
            
            for language, count in stats['languages'].items():
                languages_table.add_row(language, str(count))
            
            console.print(Panel(f"""
[bold green]Indexing Statistics[/bold green]

📊 Total files indexed: {stats['total_files']}
📈 Average complexity: {stats['average_complexity']:.2f}
            """, title="Overview", border_style="green"))
            
            console.print(file_types_table)
            console.print(categories_table)
            console.print(languages_table)
            
        except Exception as e:
            console.print(f"[red]Error getting stats: {e}[/red]")
    
    def clear_index(self):
        """Clear all indexed files"""
        try:
            if Confirm.ask("Are you sure you want to clear all indexed files?"):
                conn = sqlite3.connect(self.indexer.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM enhanced_file_index')
                conn.commit()
                conn.close()
                console.print("[green]All indexed files cleared.[/green]")
            else:
                console.print("[yellow]Operation cancelled.[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error clearing index: {e}[/red]")
    
    def run(self):
        """Run the interactive CLI"""
        console.print("[bold cyan]Enhanced File Indexer CLI[/bold cyan]")
        console.print("Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]FileIndexer[/bold green]")
                
                if not user_input or user_input.strip() == '':
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_index()
                    continue
                elif user_input.lower().startswith('index '):
                    path = user_input[6:].strip()
                    if path:
                        self.index_directory(path)
                    else:
                        console.print("[red]Please specify a directory path.[/red]")
                    continue
                elif user_input.lower().startswith('reindex '):
                    path = user_input[9:].strip()
                    if path:
                        self.index_directory(path, force=True)
                    else:
                        console.print("[red]Please specify a directory path.[/red]")
                    continue
                elif user_input.lower().startswith('search '):
                    query = user_input[7:].strip()
                    if query:
                        self.search_files(query)
                    else:
                        console.print("[red]Please specify a search query.[/red]")
                    continue
                elif user_input.lower().startswith('info '):
                    file_path = user_input[5:].strip()
                    if file_path:
                        self.show_file_info(file_path)
                    else:
                        console.print("[red]Please specify a file path.[/red]")
                    continue
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    console.print("Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

def main():
    """Main function"""
    cli = FileIndexerCLI()
    cli.run()

if __name__ == "__main__":
    main() 