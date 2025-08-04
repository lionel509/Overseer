#!/usr/bin/env python3
"""
Advanced Settings CLI for Overseer
Simple command-line interface for the advanced settings manager.
"""

import sys
import os
import time
from pathlib import Path

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from settings_manager import AdvancedSettingsManager

def main():
    """Main CLI function for advanced settings"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Overseer Advanced Settings Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_settings.py                    # Show basic settings
  python advanced_settings.py --advanced        # Show all settings (advanced mode)
  python advanced_settings.py --edit            # Interactive editor (basic mode)
  python advanced_settings.py --edit --advanced # Interactive editor (advanced mode)
  python advanced_settings.py --reset           # Reset to defaults
  python advanced_settings.py --export config.json  # Export configuration
  python advanced_settings.py --import config.json  # Import configuration
        """
    )
    
    parser.add_argument('--advanced', action='store_true', 
                       help='Show/use advanced settings (shows all options)')
    parser.add_argument('--show', action='store_true', 
                       help='Show current settings')
    parser.add_argument('--edit', action='store_true', 
                       help='Interactive settings editor')
    parser.add_argument('--reset', action='store_true', 
                       help='Reset settings to defaults')
    parser.add_argument('--export', type=str, metavar='FILE',
                       help='Export configuration to file')
    parser.add_argument('--import', dest='import_file', type=str, metavar='FILE',
                       help='Import configuration from file')
    parser.add_argument('--config', type=str, metavar='PATH',
                       help='Custom config file path')
    parser.add_argument('--defaults', action='store_true',
                       help='Show default values for all settings')
    parser.add_argument('--validate', action='store_true',
                       help='Validate current configuration')
    
    args = parser.parse_args()
    
    # Initialize settings manager
    try:
        settings_manager = AdvancedSettingsManager(args.config)
    except Exception as e:
        print(f"Error initializing settings manager: {e}")
        sys.exit(1)
    
    # Handle different commands
    if args.show:
        print(f"\n{'='*60}")
        print(f"Overseer Settings - {'Advanced' if args.advanced else 'Basic'} Mode")
        print(f"{'='*60}")
        settings_manager.show_settings(advanced_mode=args.advanced)
        
    elif args.edit:
        print(f"\n{'='*60}")
        print(f"Overseer Settings Editor - {'Advanced' if args.advanced else 'Basic'} Mode")
        print(f"{'='*60}")
        settings_manager.interactive_settings_editor(advanced_mode=args.advanced)
        
    elif args.reset:
        print(f"\n{'='*60}")
        print(f"Reset Settings - {'Advanced' if args.advanced else 'Basic'} Mode")
        print(f"{'='*60}")
        settings_manager.reset_to_defaults(advanced_mode=args.advanced)
        
    elif args.export:
        print(f"\n{'='*60}")
        print(f"Export Configuration")
        print(f"{'='*60}")
        settings_manager.export_config(args.export)
        
    elif args.import_file:
        print(f"\n{'='*60}")
        print(f"Import Configuration")
        print(f"{'='*60}")
        settings_manager.import_config(args.import_file)
        
    elif args.defaults:
        print(f"\n{'='*60}")
        print(f"Default Settings - {'Advanced' if args.advanced else 'Basic'} Mode")
        print(f"{'='*60}")
        show_defaults(settings_manager, args.advanced)
        
    elif args.validate:
        print(f"\n{'='*60}")
        print(f"Validate Configuration")
        print(f"{'='*60}")
        validate_config(settings_manager)
        
    else:
        # Default: show settings
        print(f"\n{'='*60}")
        print(f"Overseer Settings - {'Advanced' if args.advanced else 'Basic'} Mode")
        print(f"{'='*60}")
        settings_manager.show_settings(advanced_mode=args.advanced)
        
        print(f"\n{'='*60}")
        print("Usage Options:")
        print(f"{'='*60}")
        print("  --show                    Show current settings")
        print("  --edit                    Interactive settings editor")
        print("  --reset                   Reset to defaults")
        print("  --export FILE             Export configuration")
        print("  --import FILE             Import configuration")
        print("  --defaults                Show default values")
        print("  --validate                Validate configuration")
        print("  --advanced                Show advanced settings")
        print("  --config PATH             Custom config file")
        print("\nExamples:")
        print("  python advanced_settings.py --advanced --edit")
        print("  python advanced_settings.py --show --advanced")
        print("  python advanced_settings.py --reset --advanced")

def show_defaults(settings_manager, advanced_mode=False):
    """Show default values for all settings"""
    print("\nDefault Settings:")
    print("-" * 60)
    
    # Group by category
    categories = {}
    for name, definition in settings_manager.settings_definitions.items():
        if not advanced_mode or definition.advanced:
            category = definition.category
            if category not in categories:
                categories[category] = []
            categories[category].append((name, definition))
    
    for category, settings in categories.items():
        print(f"\n{category}:")
        print("-" * len(category))
        for name, definition in settings:
            default_str = str(definition.default)
            if definition.type == 'list':
                default_str = f"[{', '.join(definition.default)}]"
            print(f"  {name}: {default_str} ({definition.type})")
            print(f"    {definition.description}")

def validate_config(settings_manager):
    """Validate current configuration"""
    print("\nValidating configuration...")
    
    errors = []
    warnings = []
    
    for name, definition in settings_manager.settings_definitions.items():
        value = settings_manager.get_setting_value(name)
        
        # Check type
        if definition.type == 'bool' and not isinstance(value, bool):
            errors.append(f"{name}: Expected bool, got {type(value).__name__}")
        elif definition.type == 'int' and not isinstance(value, int):
            errors.append(f"{name}: Expected int, got {type(value).__name__}")
        elif definition.type == 'float' and not isinstance(value, (int, float)):
            errors.append(f"{name}: Expected float, got {type(value).__name__}")
        elif definition.type == 'string' and not isinstance(value, str):
            errors.append(f"{name}: Expected string, got {type(value).__name__}")
        elif definition.type == 'list' and not isinstance(value, list):
            errors.append(f"{name}: Expected list, got {type(value).__name__}")
        
        # Check range
        if definition.min_value is not None and value < definition.min_value:
            errors.append(f"{name}: Value {value} below minimum {definition.min_value}")
        if definition.max_value is not None and value > definition.max_value:
            errors.append(f"{name}: Value {value} above maximum {definition.max_value}")
        
        # Check options
        if definition.options and value not in definition.options:
            errors.append(f"{name}: Value '{value}' not in options {definition.options}")
        
        # Check for empty required strings
        if definition.type == 'string' and not value and name in ['gemini_api_key']:
            warnings.append(f"{name}: Empty value may cause issues")
    
    # Report results
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ No validation errors found")
    
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ Configuration is valid")

if __name__ == "__main__":
    main() 