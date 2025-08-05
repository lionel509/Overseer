#!/usr/bin/env python3
"""
Model Manager for Overseer
Handles downloading, installing, and managing AI models during app installation
"""

import os
import sys
import json
import hashlib
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

class ModelManager:
    """Manages AI model downloads and installations"""
    
    def __init__(self, models_dir: Optional[str] = None):
        """Initialize the model manager"""
        self.models_dir = Path(models_dir) if models_dir else Path.home() / ".overseer" / "models"
        self.config_file = Path.home() / ".overseer" / "model_config.json"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Model configurations
        self.available_models = {
            "gemma-3n-2b": {
                "name": "Gemma 3n 2B",
                "description": "Lightweight Gemma model for basic AI tasks",
                "size": "2.1GB",
                "url": "https://huggingface.co/google/gemma-3n-2b",
                "files": [
                    "config.json",
                    "pytorch_model.bin",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json"
                ],
                "recommended": True,
                "requirements": ["transformers>=4.35.0", "torch>=2.0.0"]
            },
            "gemma-3n-9b": {
                "name": "Gemma 3n 9B", 
                "description": "Full-featured Gemma model for advanced AI tasks",
                "size": "8.7GB",
                "url": "https://huggingface.co/google/gemma-3n-9b",
                "files": [
                    "config.json",
                    "pytorch_model-00001-of-00004.bin",
                    "pytorch_model-00002-of-00004.bin", 
                    "pytorch_model-00003-of-00004.bin",
                    "pytorch_model-00004-of-00004.bin",
                    "pytorch_model.bin.index.json",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json"
                ],
                "recommended": False,
                "requirements": ["transformers>=4.35.0", "torch>=2.0.0"]
            },
            "gemma-3n-27b": {
                "name": "Gemma 3n 27B",
                "description": "Enterprise-grade Gemma model for complex AI tasks",
                "size": "25.2GB", 
                "url": "https://huggingface.co/google/gemma-3n-27b",
                "files": [
                    "config.json",
                    "pytorch_model-00001-of-00011.bin",
                    "pytorch_model-00002-of-00011.bin",
                    "pytorch_model-00003-of-00011.bin",
                    "pytorch_model-00004-of-00011.bin",
                    "pytorch_model-00005-of-00011.bin",
                    "pytorch_model-00006-of-00011.bin",
                    "pytorch_model-00007-of-00011.bin",
                    "pytorch_model-00008-of-00011.bin",
                    "pytorch_model-00009-of-00011.bin",
                    "pytorch_model-00010-of-00011.bin",
                    "pytorch_model-00011-of-00011.bin",
                    "pytorch_model.bin.index.json",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json"
                ],
                "recommended": False,
                "requirements": ["transformers>=4.35.0", "torch>=2.0.0"]
            }
        }
    
    def show_model_selection(self) -> List[str]:
        """Show available models and let user select which to download"""
        console.print(Panel.fit(
            "[bold cyan]🤖 AI Model Selection[/bold cyan]\n"
            "Choose which AI models to download for local inference",
            border_style="cyan"
        ))
        
        # Create selection table
        table = Table(title="Available AI Models", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=3)
        table.add_column("Model", style="green", width=20)
        table.add_column("Size", style="yellow", width=8) 
        table.add_column("Description", style="white", width=40)
        table.add_column("Recommended", style="blue", width=12)
        
        for i, (model_id, model_info) in enumerate(self.available_models.items(), 1):
            recommended = "✅ Yes" if model_info["recommended"] else "⚪ No"
            table.add_row(
                str(i),
                model_info["name"],
                model_info["size"],
                model_info["description"],
                recommended
            )
        
        console.print(table)
        
        console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
        console.print("• [green]Gemma 3n 2B[/green] - Best for most users (lightweight, fast)")
        console.print("• [yellow]Gemma 3n 9B[/yellow] - Better accuracy, requires more resources")
        console.print("• [red]Gemma 3n 27B[/red] - Enterprise use, requires significant resources")
        
        # Get user selection
        console.print("\n[bold cyan]Selection Options:[/bold cyan]")
        console.print("• Enter model numbers (e.g., '1,2' for multiple models)")
        console.print("• Press Enter for recommended model (Gemma 3n 2B)")
        console.print("• Type 'none' to skip model download")
        
        while True:
            selection = input("\nEnter your choice: ").strip()
            
            if not selection:
                # Default to recommended model
                return ["gemma-3n-2b"]
            elif selection.lower() == "none":
                return []
            else:
                try:
                    # Parse selection
                    selected_ids = []
                    for num in selection.split(","):
                        num = num.strip()
                        if num.isdigit():
                            index = int(num) - 1
                            if 0 <= index < len(self.available_models):
                                model_id = list(self.available_models.keys())[index]
                                selected_ids.append(model_id)
                            else:
                                console.print(f"[red]Invalid model number: {num}[/red]")
                                break
                        else:
                            console.print(f"[red]Invalid input: {num}[/red]")
                            break
                    else:
                        if selected_ids:
                            return selected_ids
                        else:
                            console.print("[red]No valid models selected[/red]")
                except Exception as e:
                    console.print(f"[red]Error parsing selection: {e}[/red]")
    
    def check_disk_space(self, models_to_download: List[str]) -> bool:
        """Check if there's enough disk space for the selected models"""
        total_size_gb = 0
        for model_id in models_to_download:
            model_info = self.available_models[model_id]
            size_str = model_info["size"]
            # Parse size (e.g., "2.1GB" -> 2.1)
            size_gb = float(size_str.replace("GB", ""))
            total_size_gb += size_gb
        
        # Get available disk space
        stat = os.statvfs(self.models_dir)
        available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        
        console.print(f"\n[bold yellow]Disk Space Check:[/bold yellow]")
        console.print(f"Required space: {total_size_gb:.1f}GB")
        console.print(f"Available space: {available_gb:.1f}GB")
        
        if available_gb < total_size_gb * 1.2:  # 20% buffer
            console.print(f"[red]❌ Insufficient disk space![/red]")
            console.print(f"[yellow]Please free up at least {total_size_gb * 1.2 - available_gb:.1f}GB[/yellow]")
            return False
        else:
            console.print(f"[green]✅ Sufficient disk space available[/green]")
            return True
    
    def install_model_dependencies(self, models_to_download: List[str]) -> bool:
        """Install required dependencies for the selected models"""
        console.print("\n[bold cyan]📦 Installing Model Dependencies...[/bold cyan]")
        
        # Collect all unique requirements
        all_requirements = set()
        for model_id in models_to_download:
            model_info = self.available_models[model_id]
            all_requirements.update(model_info["requirements"])
        
        success_count = 0
        total_count = len(all_requirements)
        
        for requirement in all_requirements:
            try:
                console.print(f"Installing {requirement}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", requirement
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    console.print(f"[green]✅ {requirement}[/green]")
                    success_count += 1
                else:
                    console.print(f"[red]❌ {requirement}: {result.stderr}[/red]")
            except Exception as e:
                console.print(f"[red]❌ {requirement}: {e}[/red]")
        
        if success_count == total_count:
            console.print(f"[green]✅ All dependencies installed successfully![/green]")
            return True
        else:
            console.print(f"[yellow]⚠️ {success_count}/{total_count} dependencies installed[/yellow]")
            return success_count > 0
    
    def download_model_file(self, url: str, filepath: Path, progress: Progress, task_id: TaskID) -> bool:
        """Download a single model file with progress tracking"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            progress.update(task_id, total=total_size)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error downloading {filepath.name}: {e}[/red]")
            return False
    
    def download_from_huggingface(self, model_id: str) -> bool:
        """Download model from Hugging Face using git and git-lfs"""
        model_info = self.available_models[model_id]
        model_path = self.models_dir / model_id
        
        console.print(f"\n[bold cyan]📥 Downloading {model_info['name']}...[/bold cyan]")
        
        try:
            # Check if git-lfs is installed
            result = subprocess.run(["git", "lfs", "version"], capture_output=True)
            if result.returncode != 0:
                console.print("[yellow]Installing git-lfs...[/yellow]")
                # Try to install git-lfs
                subprocess.run(["git", "lfs", "install"], check=True)
            
            # Clone the repository
            console.print(f"Cloning {model_info['url']}...")
            result = subprocess.run([
                "git", "clone", model_info["url"], str(model_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"[green]✅ {model_info['name']} downloaded successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to download {model_info['name']}: {result.stderr}[/red]")
                return False
                
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Git error: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Download error: {e}[/red]")
            return False
    
    def download_models(self, models_to_download: List[str]) -> bool:
        """Download the selected models"""
        if not models_to_download:
            console.print("[yellow]No models selected for download[/yellow]")
            return True
        
        console.print(f"\n[bold cyan]🚀 Starting download of {len(models_to_download)} model(s)...[/bold cyan]")
        
        success_count = 0
        for model_id in models_to_download:
            if self.download_from_huggingface(model_id):
                success_count += 1
                # Update config with downloaded model
                self.update_model_config(model_id, "downloaded")
        
        if success_count == len(models_to_download):
            console.print(f"[green]🎉 All {success_count} models downloaded successfully![/green]")
            return True
        else:
            console.print(f"[yellow]⚠️ {success_count}/{len(models_to_download)} models downloaded[/yellow]")
            return success_count > 0
    
    def update_model_config(self, model_id: str, status: str):
        """Update the model configuration file"""
        config = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        
        if "models" not in config:
            config["models"] = {}
        
        config["models"][model_id] = {
            "status": status,
            "path": str(self.models_dir / model_id),
            "downloaded_at": None if status != "downloaded" else str(Path().cwd())
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def list_installed_models(self) -> Dict[str, Dict]:
        """List all installed models"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get("models", {})
        except:
            return {}
    
    def verify_model_installation(self, model_id: str) -> bool:
        """Verify that a model is properly installed"""
        model_path = self.models_dir / model_id
        if not model_path.exists():
            return False
        
        model_info = self.available_models[model_id]
        required_files = model_info["files"]
        
        for filename in required_files:
            if not (model_path / filename).exists():
                return False
        
        return True
    
    def setup_models_for_installation(self) -> Tuple[bool, List[str]]:
        """Main method to handle model setup during installation"""
        console.print(Panel.fit(
            "[bold green]🧠 AI Model Setup[/bold green]\n"
            "Setting up local AI models for intelligent system management",
            border_style="green"
        ))
        
        # Show model selection
        selected_models = self.show_model_selection()
        
        if not selected_models:
            console.print("[yellow]Skipping model download. You can download models later using the model manager.[/yellow]")
            return True, []
        
        # Check disk space
        if not self.check_disk_space(selected_models):
            console.print("[red]Aborting model download due to insufficient disk space.[/red]")
            return False, []
        
        # Install dependencies
        if not self.install_model_dependencies(selected_models):
            console.print("[red]Failed to install required dependencies.[/red]")
            return False, []
        
        # Download models
        success = self.download_models(selected_models)
        
        if success:
            console.print("\n[bold green]🎉 Model setup completed successfully![/bold green]")
            console.print("\n[bold cyan]Next steps:[/bold cyan]")
            console.print("• Models are stored in: " + str(self.models_dir))
            console.print("• Configure Overseer to use local models in settings")
            console.print("• Test the installation with: overseer --test-llm")
            
        return success, selected_models

def main():
    """Test the model manager"""
    manager = ModelManager()
    success, models = manager.setup_models_for_installation()
    
    if success:
        console.print(f"\n[green]✅ Setup completed with {len(models)} models[/green]")
    else:
        console.print(f"\n[red]❌ Setup failed[/red]")

if __name__ == "__main__":
    main()
