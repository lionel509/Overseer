#!/usr/bin/env python3
"""
Model CLI - Command line interface for managing AI models
"""

import argparse
import sys
from pathlib import Path

# Add the backend CLI to path
sys.path.append(str(Path(__file__).parent))

from model_manager import ModelManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def list_models(manager: ModelManager):
    """List all available and installed models"""
    console.print(Panel.fit(
        "[bold cyan]📋 Model Management[/bold cyan]\n"
        "Available and installed AI models",
        border_style="cyan"
    ))
    
    installed = manager.list_installed_models()
    
    # Available models table
    table = Table(title="Available Models", show_header=True, header_style="bold magenta")
    table.add_column("Model", style="green", width=20)
    table.add_column("Size", style="yellow", width=8)
    table.add_column("Status", style="cyan", width=12)
    table.add_column("Description", style="white", width=40)
    
    for model_id, model_info in manager.available_models.items():
        status = "✅ Installed" if model_id in installed and installed[model_id].get("status") == "downloaded" else "⚪ Not installed"
        table.add_row(
            model_info["name"],
            model_info["size"],
            status,
            model_info["description"]
        )
    
    console.print(table)
    
    if installed:
        console.print(f"\n[bold green]📁 Models directory:[/bold green] {manager.models_dir}")

def install_model(manager: ModelManager, model_id: str):
    """Install a specific model"""
    if model_id not in manager.available_models:
        console.print(f"[red]❌ Unknown model: {model_id}[/red]")
        console.print(f"Available models: {', '.join(manager.available_models.keys())}")
        return False
    
    console.print(f"[cyan]📥 Installing model: {model_id}[/cyan]")
    
    # Check disk space
    if not manager.check_disk_space([model_id]):
        return False
    
    # Install dependencies
    if not manager.install_model_dependencies([model_id]):
        console.print("[red]❌ Failed to install dependencies[/red]")
        return False
    
    # Download model
    success = manager.download_models([model_id])
    
    if success:
        console.print(f"[green]✅ Model {model_id} installed successfully![/green]")
        return True
    else:
        console.print(f"[red]❌ Failed to install model {model_id}[/red]")
        return False

def remove_model(manager: ModelManager, model_id: str):
    """Remove an installed model"""
    model_path = manager.models_dir / model_id
    
    if not model_path.exists():
        console.print(f"[red]❌ Model {model_id} is not installed[/red]")
        return False
    
    try:
        import shutil
        shutil.rmtree(model_path)
        
        # Update config
        manager.update_model_config(model_id, "removed")
        
        console.print(f"[green]✅ Model {model_id} removed successfully![/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Failed to remove model {model_id}: {e}[/red]")
        return False

def verify_model(manager: ModelManager, model_id: str):
    """Verify a model installation"""
    if not manager.verify_model_installation(model_id):
        console.print(f"[red]❌ Model {model_id} verification failed[/red]")
        return False
    else:
        console.print(f"[green]✅ Model {model_id} verification passed[/green]")
        return True

def interactive_setup(manager: ModelManager):
    """Interactive model setup"""
    success, models = manager.setup_models_for_installation()
    
    if success:
        console.print(f"[green]✅ Setup completed with {len(models)} models[/green]")
    else:
        console.print("[red]❌ Setup failed[/red]")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Overseer AI Model Manager")
    parser.add_argument("--models-dir", help="Custom models directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List available and installed models")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a model")
    install_parser.add_argument("model_id", help="Model ID to install")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a model")
    remove_parser.add_argument("model_id", help="Model ID to remove")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a model installation")
    verify_parser.add_argument("model_id", help="Model ID to verify")
    
    # Setup command
    subparsers.add_parser("setup", help="Interactive model setup")
    
    args = parser.parse_args()
    
    # Initialize model manager
    manager = ModelManager(args.models_dir)
    
    if args.command == "list":
        list_models(manager)
    elif args.command == "install":
        install_model(manager, args.model_id)
    elif args.command == "remove":
        remove_model(manager, args.model_id)
    elif args.command == "verify":
        verify_model(manager, args.model_id)
    elif args.command == "setup":
        interactive_setup(manager)
    else:
        # Default to listing models if no command
        list_models(manager)
        console.print("\n[bold cyan]Usage examples:[/bold cyan]")
        console.print("python model_cli.py list                    # List models")
        console.print("python model_cli.py install gemma-3n-2b     # Install model")
        console.print("python model_cli.py remove gemma-3n-2b      # Remove model")
        console.print("python model_cli.py verify gemma-3n-2b      # Verify model")
        console.print("python model_cli.py setup                   # Interactive setup")

if __name__ == "__main__":
    main()
