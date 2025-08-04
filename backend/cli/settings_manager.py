"""
Advanced Settings Manager for Overseer
Provides comprehensive settings management with advanced mode showing all options.
"""

import os
import json
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure console
console = Console() if RICH_AVAILABLE else None

@dataclass
class SettingDefinition:
    """Definition for a configuration setting"""
    name: str
    type: str  # 'bool', 'int', 'float', 'string', 'list'
    default: Any
    description: str
    category: str
    advanced: bool = False
    options: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class AdvancedSettingsManager:
    """
    Advanced settings manager with comprehensive configuration options.
    Provides both basic and advanced modes with all settings defaulting to "no".
    """
    
    def __init__(self, config_path: str = None):
        """Initialize settings manager"""
        if config_path is None:
            config_path = os.path.expanduser('~/.overseer/config.json')
        
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Define all available settings
        self.settings_definitions = self._define_all_settings()
        
        # Load current configuration
        self.config = self.load_config()
    
    def _define_all_settings(self) -> Dict[str, SettingDefinition]:
        """Define all available settings with comprehensive options"""
        return {
            # === BASIC LLM CONFIGURATION ===
            'llm_mode': SettingDefinition(
                name='llm_mode',
                type='string',
                default='local',
                description='Choose between local LLM or online Gemini API',
                category='LLM Configuration',
                options=['local', 'gemini']
            ),
            'gemini_api_key': SettingDefinition(
                name='gemini_api_key',
                type='string',
                default='',
                description='Your Gemini API key for online LLM access',
                category='LLM Configuration',
                advanced=True
            ),
            'gemini_model_name': SettingDefinition(
                name='gemini_model_name',
                type='string',
                default='gemini-2.5-flash-lite',
                description='Specific Gemini model to use',
                category='LLM Configuration',
                advanced=True
            ),
            'gemini_max_tokens': SettingDefinition(
                name='gemini_max_tokens',
                type='int',
                default=2048,
                description='Maximum tokens for Gemini responses',
                category='LLM Configuration',
                advanced=True,
                min_value=1,
                max_value=8192
            ),
            'gemini_temperature': SettingDefinition(
                name='gemini_temperature',
                type='float',
                default=0.7,
                description='Controls response creativity (higher = more creative)',
                category='LLM Configuration',
                advanced=True,
                min_value=0.0,
                max_value=1.0
            ),
            'local_model_name': SettingDefinition(
                name='local_model_name',
                type='string',
                default='google/gemma-1.1-3b-it',
                description='Local model to use for inference',
                category='LLM Configuration',
                advanced=True
            ),
            'local_max_tokens': SettingDefinition(
                name='local_max_tokens',
                type='int',
                default=1024,
                description='Maximum tokens for local model responses',
                category='LLM Configuration',
                advanced=True,
                min_value=1,
                max_value=4096
            ),
            'local_temperature': SettingDefinition(
                name='local_temperature',
                type='float',
                default=0.7,
                description='Controls local model response creativity',
                category='LLM Configuration',
                advanced=True,
                min_value=0.0,
                max_value=1.0
            ),
            
            # === SYSTEM BEHAVIOR SETTINGS ===
            'debug': SettingDefinition(
                name='debug',
                type='bool',
                default=False,
                description='Enable debug mode for detailed logging',
                category='System Behavior'
            ),
            'log': SettingDefinition(
                name='log',
                type='bool',
                default=False,
                description='Enable general logging',
                category='System Behavior'
            ),
            'verbose_output': SettingDefinition(
                name='verbose_output',
                type='bool',
                default=False,
                description='Show detailed output for operations',
                category='System Behavior'
            ),
            'show_progress': SettingDefinition(
                name='show_progress',
                type='bool',
                default=True,
                description='Display progress bars for long operations',
                category='System Behavior'
            ),
            'auto_save': SettingDefinition(
                name='auto_save',
                type='bool',
                default=True,
                description='Automatically save session data',
                category='System Behavior'
            ),
            
            # === FILE MANAGEMENT SETTINGS ===
            'file_indexing': SettingDefinition(
                name='file_indexing',
                type='bool',
                default=False,
                description='Enable file indexing for faster searches',
                category='File Management'
            ),
            'auto_organize_enabled': SettingDefinition(
                name='auto_organize_enabled',
                type='bool',
                default=True,
                description='Enable automatic file organization',
                category='File Management'
            ),
            'max_files_per_folder': SettingDefinition(
                name='max_files_per_folder',
                type='int',
                default=100,
                description='Maximum files per folder during auto-organize',
                category='File Management',
                min_value=1,
                max_value=1000
            ),
            'confirm_moves': SettingDefinition(
                name='confirm_moves',
                type='bool',
                default=True,
                description='Ask for confirmation before moving files',
                category='File Management'
            ),
            'backup_before_move': SettingDefinition(
                name='backup_before_move',
                type='bool',
                default=False,
                description='Create backup before moving files',
                category='File Management'
            ),
            'scan_hidden_files': SettingDefinition(
                name='scan_hidden_files',
                type='bool',
                default=False,
                description='Include hidden files in scans',
                category='File Management'
            ),
            'exclude_patterns': SettingDefinition(
                name='exclude_patterns',
                type='string',
                default='*.tmp,*.log,.DS_Store',
                description='Comma-separated file patterns to exclude',
                category='File Management'
            ),
            
            # === SECURITY SETTINGS ===
            'full_control': SettingDefinition(
                name='full_control',
                type='bool',
                default=False,
                description='Enable full control mode (bypass confirmations)',
                category='Security'
            ),
            'always_confirm_commands': SettingDefinition(
                name='always_confirm_commands',
                type='bool',
                default=True,
                description='Always confirm before running system commands',
                category='Security'
            ),
            'sandbox_mode': SettingDefinition(
                name='sandbox_mode',
                type='string',
                default='simulation',
                description='Default sandbox mode for command execution',
                category='Security',
                options=['dry_run', 'simulation', 'isolated', 'validation']
            ),
            'command_timeout': SettingDefinition(
                name='command_timeout',
                type='int',
                default=30,
                description='Timeout for command execution (seconds)',
                category='Security',
                min_value=1,
                max_value=300
            ),
            'secure_config': SettingDefinition(
                name='secure_config',
                type='bool',
                default=False,
                description='Enable secure configuration mode',
                category='Security',
                advanced=True
            ),
            'encrypt_sensitive_data': SettingDefinition(
                name='encrypt_sensitive_data',
                type='bool',
                default=False,
                description='Encrypt sensitive configuration data',
                category='Security',
                advanced=True
            ),
            
            # === SEARCH AND INDEXING SETTINGS ===
            'search_depth': SettingDefinition(
                name='search_depth',
                type='int',
                default=3,
                description='Maximum search depth for file operations',
                category='Search & Indexing',
                min_value=1,
                max_value=10
            ),
            'fuzzy_search': SettingDefinition(
                name='fuzzy_search',
                type='bool',
                default=True,
                description='Enable fuzzy search for file names',
                category='Search & Indexing'
            ),
            'search_in_content': SettingDefinition(
                name='search_in_content',
                type='bool',
                default=False,
                description='Search within file contents',
                category='Search & Indexing'
            ),
            'max_file_size': SettingDefinition(
                name='max_file_size',
                type='int',
                default=100,
                description='Maximum file size for content search (MB)',
                category='Search & Indexing',
                min_value=1,
                max_value=1000
            ),
            'index_file_types': SettingDefinition(
                name='index_file_types',
                type='string',
                default='txt,md,py,js,html,css,json,xml',
                description='File types to index for content search',
                category='Search & Indexing'
            ),
            
            # === UI AND INTERACTION SETTINGS ===
            'color_output': SettingDefinition(
                name='color_output',
                type='bool',
                default=True,
                description='Enable colored output in terminal',
                category='UI & Interaction'
            ),
            'interactive_mode': SettingDefinition(
                name='interactive_mode',
                type='bool',
                default=True,
                description='Enable interactive mode for user input',
                category='UI & Interaction'
            ),
            'auto_complete': SettingDefinition(
                name='auto_complete',
                type='bool',
                default=True,
                description='Enable command auto-completion',
                category='UI & Interaction'
            ),
            'show_suggestions': SettingDefinition(
                name='show_suggestions',
                type='bool',
                default=True,
                description='Show command suggestions',
                category='UI & Interaction'
            ),
            'prompt_style': SettingDefinition(
                name='prompt_style',
                type='string',
                default='simple',
                description='Command prompt style',
                category='UI & Interaction',
                options=['simple', 'detailed', 'minimal'],
                advanced=True
            ),
            
            # === PERFORMANCE SETTINGS ===
            'max_threads': SettingDefinition(
                name='max_threads',
                type='int',
                default=4,
                description='Maximum number of threads for operations',
                category='Performance',
                min_value=1,
                max_value=16
            ),
            'cache_size': SettingDefinition(
                name='cache_size',
                type='int',
                default=50,
                description='Cache size for frequently accessed data',
                category='Performance',
                min_value=10,
                max_value=500
            ),
            'memory_limit': SettingDefinition(
                name='memory_limit',
                type='int',
                default=512,
                description='Memory limit for operations (MB)',
                category='Performance',
                min_value=64,
                max_value=4096
            ),
            'batch_size': SettingDefinition(
                name='batch_size',
                type='int',
                default=100,
                description='Batch size for file operations',
                category='Performance',
                min_value=10,
                max_value=1000
            ),
            'lazy_loading': SettingDefinition(
                name='lazy_loading',
                type='bool',
                default=True,
                description='Enable lazy loading for better performance',
                category='Performance'
            ),
            
            # === NOTIFICATION SETTINGS ===
            'enable_notifications': SettingDefinition(
                name='enable_notifications',
                type='bool',
                default=False,
                description='Enable system notifications',
                category='Notifications'
            ),
            'notification_sound': SettingDefinition(
                name='notification_sound',
                type='bool',
                default=False,
                description='Play sounds for notifications',
                category='Notifications'
            ),
            'email_notifications': SettingDefinition(
                name='email_notifications',
                type='bool',
                default=False,
                description='Send email notifications',
                category='Notifications'
            ),
            'notification_level': SettingDefinition(
                name='notification_level',
                type='string',
                default='info',
                description='Minimum notification level',
                category='Notifications',
                options=['debug', 'info', 'warning', 'error'],
                advanced=True
            ),
            
            # === FOLDER CONFIGURATION ===
            'folders': SettingDefinition(
                name='folders',
                type='list',
                default=['~/Downloads'],
                description='Folders to watch and organize',
                category='Folder Configuration'
            ),
            'auto_scan_folders': SettingDefinition(
                name='auto_scan_folders',
                type='bool',
                default=True,
                description='Automatically scan watched folders',
                category='Folder Configuration'
            ),
            'folder_scan_interval': SettingDefinition(
                name='folder_scan_interval',
                type='int',
                default=60,
                description='How often to scan folders (minutes)',
                category='Folder Configuration',
                min_value=1,
                max_value=1440
            ),
            'recursive_scan': SettingDefinition(
                name='recursive_scan',
                type='bool',
                default=True,
                description='Scan folders recursively',
                category='Folder Configuration'
            ),
            
            # === ADVANCED SETTINGS ===
            'log_level': SettingDefinition(
                name='log_level',
                type='string',
                default='INFO',
                description='Logging level',
                category='Advanced',
                options=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                advanced=True
            ),
            'log_file': SettingDefinition(
                name='log_file',
                type='string',
                default='~/.overseer/overseer.log',
                description='Path to log file',
                category='Advanced',
                advanced=True
            ),
            'temp_dir': SettingDefinition(
                name='temp_dir',
                type='string',
                default='/tmp/overseer',
                description='Directory for temporary files',
                category='Advanced',
                advanced=True
            ),
            'backup_dir': SettingDefinition(
                name='backup_dir',
                type='string',
                default='~/.overseer/backups',
                description='Directory for file backups',
                category='Advanced',
                advanced=True
            ),
            'config_backup': SettingDefinition(
                name='config_backup',
                type='bool',
                default=False,
                description='Automatically backup configuration',
                category='Advanced',
                advanced=True
            ),
            'auto_update': SettingDefinition(
                name='auto_update',
                type='bool',
                default=False,
                description='Automatically check for updates',
                category='Advanced',
                advanced=True
            ),
            'telemetry': SettingDefinition(
                name='telemetry',
                type='bool',
                default=False,
                description='Enable usage telemetry',
                category='Advanced',
                advanced=True
            ),
            'experimental_features': SettingDefinition(
                name='experimental_features',
                type='bool',
                default=False,
                description='Enable experimental features',
                category='Advanced',
                advanced=True
            ),
            'custom_plugins': SettingDefinition(
                name='custom_plugins',
                type='list',
                default=[],
                description='Custom plugin directories',
                category='Advanced',
                advanced=True
            ),
            'api_endpoint': SettingDefinition(
                name='api_endpoint',
                type='string',
                default='',
                description='Custom API endpoint',
                category='Advanced',
                advanced=True
            ),
            'timeout_settings': SettingDefinition(
                name='timeout_settings',
                type='string',
                default='30,60,120',
                description='Timeout settings (connect,read,write)',
                category='Advanced',
                advanced=True
            ),
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with defaults"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                console.print(f'[yellow]Warning: Could not load config: {e}[/yellow]')
                config = {}
        else:
            config = {}
        
        # Apply defaults for missing settings
        for name, definition in self.settings_definitions.items():
            if name not in config:
                config[name] = definition.default
        
        return config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Set secure permissions for sensitive files
            if config.get('secure_config', False):
                os.chmod(self.config_path, 0o600)
            
            console.print(f'[green]Configuration saved to {self.config_path}[/green]')
        except Exception as e:
            console.print(f'[red]Error saving config: {e}[/red]')
    
    def get_setting_value(self, name: str) -> Any:
        """Get current value of a setting"""
        return self.config.get(name, self.settings_definitions[name].default)
    
    def set_setting_value(self, name: str, value: Any):
        """Set value of a setting"""
        if name in self.settings_definitions:
            definition = self.settings_definitions[name]
            
            # Validate value
            if definition.type == 'bool':
                if isinstance(value, str):
                    value = value.lower() in ['true', 'yes', '1', 'on']
                else:
                    value = bool(value)
            elif definition.type == 'int':
                value = int(value)
                if definition.min_value is not None:
                    value = max(value, definition.min_value)
                if definition.max_value is not None:
                    value = min(value, definition.max_value)
            elif definition.type == 'float':
                value = float(value)
                if definition.min_value is not None:
                    value = max(value, definition.min_value)
                if definition.max_value is not None:
                    value = min(value, definition.max_value)
            elif definition.type == 'string' and definition.options:
                if value not in definition.options:
                    console.print(f'[yellow]Warning: Invalid option "{value}" for {name}. Using default.[/yellow]')
                    value = definition.default
            
            self.config[name] = value
        else:
            console.print(f'[red]Unknown setting: {name}[/red]')
    
    def show_settings(self, advanced_mode: bool = False):
        """Display current settings"""
        if not RICH_AVAILABLE:
            print("Rich not available for formatted display")
            return
        
        # Group settings by category
        categories = {}
        for name, definition in self.settings_definitions.items():
            if not advanced_mode or definition.advanced:
                category = definition.category
                if category not in categories:
                    categories[category] = []
                categories[category].append((name, definition))
        
        # Display settings by category
        for category, settings in categories.items():
            table = Table(title=f"{category} Settings")
            table.add_column("Setting", style="cyan")
            table.add_column("Type", style="blue")
            table.add_column("Current Value", style="green")
            table.add_column("Default", style="yellow")
            table.add_column("Description", style="white")
            
            for name, definition in settings:
                current_value = self.get_setting_value(name)
                default_value = definition.default
                
                # Format values for display
                if definition.type == 'list':
                    current_str = str(current_value) if current_value else '[]'
                    default_str = str(default_value) if default_value else '[]'
                else:
                    current_str = str(current_value)
                    default_str = str(default_value)
                
                table.add_row(
                    name,
                    definition.type,
                    current_str,
                    default_str,
                    definition.description
                )
            
            console.print(table)
            console.print()
    
    def interactive_settings_editor(self, advanced_mode: bool = False):
        """Interactive settings editor"""
        if not RICH_AVAILABLE:
            print("Rich not available for interactive editor")
            return
        
        console.print(Panel(
            f"[bold blue]Overseer Settings Editor[/bold blue]\n"
            f"Mode: {'Advanced' if advanced_mode else 'Basic'}\n"
            f"Config file: {self.config_path}",
            title="Settings"
        ))
        
        # Get settings to edit
        settings_to_edit = []
        for name, definition in self.settings_definitions.items():
            if not advanced_mode or definition.advanced:
                settings_to_edit.append((name, definition))
        
        # Sort by category and name
        settings_to_edit.sort(key=lambda x: (x[1].category, x[0]))
        
        # Edit settings
        for name, definition in settings_to_edit:
            current_value = self.get_setting_value(name)
            
            console.print(f"\n[bold cyan]{definition.name}[/bold cyan]")
            console.print(f"Category: {definition.category}")
            console.print(f"Description: {definition.description}")
            console.print(f"Type: {definition.type}")
            
            if definition.options:
                console.print(f"Options: {', '.join(definition.options)}")
            
            if definition.min_value is not None or definition.max_value is not None:
                range_str = f"[{definition.min_value or '∞'}, {definition.max_value or '∞'}]"
                console.print(f"Range: {range_str}")
            
            console.print(f"Current value: [green]{current_value}[/green]")
            console.print(f"Default value: [yellow]{definition.default}[/yellow]")
            
            # Get new value
            if definition.type == 'bool':
                new_value = Confirm.ask(
                    f"Enable {definition.name}?",
                    default=bool(current_value)
                )
            elif definition.type == 'int':
                new_value = Prompt.ask(
                    f"Enter new value for {definition.name}",
                    default=str(current_value)
                )
                try:
                    new_value = int(new_value)
                except ValueError:
                    console.print(f"[red]Invalid integer value. Keeping current value.[/red]")
                    continue
            elif definition.type == 'float':
                new_value = Prompt.ask(
                    f"Enter new value for {definition.name}",
                    default=str(current_value)
                )
                try:
                    new_value = float(new_value)
                except ValueError:
                    console.print(f"[red]Invalid float value. Keeping current value.[/red]")
                    continue
            elif definition.type == 'string' and definition.options:
                console.print(f"Options: {', '.join(definition.options)}")
                new_value = Prompt.ask(
                    f"Enter new value for {definition.name}",
                    choices=definition.options,
                    default=str(current_value)
                )
            elif definition.type == 'string':
                new_value = Prompt.ask(
                    f"Enter new value for {definition.name}",
                    default=str(current_value)
                )
            elif definition.type == 'list':
                current_str = ','.join(current_value) if current_value else ''
                new_value_str = Prompt.ask(
                    f"Enter new value for {definition.name} (comma-separated)",
                    default=current_str
                )
                new_value = [item.strip() for item in new_value_str.split(',') if item.strip()]
            else:
                console.print(f"[red]Unknown type {definition.type}. Skipping.[/red]")
                continue
            
            # Set the new value
            self.set_setting_value(name, new_value)
            console.print(f"[green]Updated {name} to {new_value}[/green]")
        
        # Save configuration
        if Confirm.ask("Save changes?"):
            self.save_config()
        else:
            console.print("[yellow]Changes not saved.[/yellow]")
    
    def reset_to_defaults(self, advanced_mode: bool = False):
        """Reset settings to defaults"""
        if not RICH_AVAILABLE:
            print("Rich not available for confirmation")
            return
        
        if Confirm.ask("Reset all settings to defaults?"):
            for name, definition in self.settings_definitions.items():
                if not advanced_mode or definition.advanced:
                    self.config[name] = definition.default
            
            self.save_config()
            console.print("[green]Settings reset to defaults.[/green]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
    
    def export_config(self, filename: str = None):
        """Export configuration to file"""
        if filename is None:
            filename = f"overseer_config_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            console.print(f"[green]Configuration exported to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting config: {e}[/red]")
    
    def import_config(self, filename: str):
        """Import configuration from file"""
        try:
            with open(filename, 'r') as f:
                imported_config = json.load(f)
            
            # Validate imported settings
            for name, value in imported_config.items():
                if name in self.settings_definitions:
                    self.set_setting_value(name, value)
                else:
                    console.print(f"[yellow]Warning: Unknown setting {name} in imported config[/yellow]")
            
            self.save_config()
            console.print(f"[green]Configuration imported from {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error importing config: {e}[/red]")

def main():
    """Main function for settings manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Overseer Advanced Settings Manager')
    parser.add_argument('--advanced', action='store_true', help='Show advanced settings')
    parser.add_argument('--show', action='store_true', help='Show current settings')
    parser.add_argument('--edit', action='store_true', help='Interactive settings editor')
    parser.add_argument('--reset', action='store_true', help='Reset to defaults')
    parser.add_argument('--export', type=str, help='Export configuration to file')
    parser.add_argument('--import', dest='import_file', type=str, help='Import configuration from file')
    parser.add_argument('--config', type=str, help='Custom config file path')
    
    args = parser.parse_args()
    
    # Initialize settings manager
    settings_manager = AdvancedSettingsManager(args.config)
    
    if args.show:
        settings_manager.show_settings(advanced_mode=args.advanced)
    elif args.edit:
        settings_manager.interactive_settings_editor(advanced_mode=args.advanced)
    elif args.reset:
        settings_manager.reset_to_defaults(advanced_mode=args.advanced)
    elif args.export:
        settings_manager.export_config(args.export)
    elif args.import_file:
        settings_manager.import_config(args.import_file)
    else:
        # Default: show settings
        settings_manager.show_settings(advanced_mode=args.advanced)

if __name__ == "__main__":
    main() 