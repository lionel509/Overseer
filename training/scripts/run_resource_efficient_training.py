#!/usr/bin/env python3
"""
Resource Efficient Training Script for Overseer

This script demonstrates how to run training in resource-efficient mode,
which trades training speed for lower system resource usage.

Usage:
    python run_resource_efficient_training.py [options]

Examples:
    # Basic resource-efficient training
    python run_resource_efficient_training.py --resource-efficient
    
    # Resource-efficient training with fresh data download
    python run_resource_efficient_training.py --resource-efficient --download-data
    
    # Resource-efficient training with continuous learning
    python run_resource_efficient_training.py --resource-efficient --continuous-learning
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Build the command
    cmd = [sys.executable, str(script_dir / "main_training.py")]
    
    # Add resource-efficient flag
    cmd.append("--resource-efficient")
    
    # Add other arguments if provided
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print("🚀 Starting resource-efficient training...")
    print(f"Command: {' '.join(cmd)}")
    print("\nResource-efficient mode features:")
    print("✅ Reduced batch size (4 instead of 16)")
    print("✅ Increased gradient accumulation (16 steps)")
    print("✅ Lower learning rate (5e-5 instead of 1e-4)")
    print("✅ Reduced sequence length (1024 instead of 2048)")
    print("✅ Fewer data loader workers (1 instead of 4)")
    print("✅ Lower memory thresholds (70% RAM, 75% GPU)")
    print("✅ Gradient checkpointing enabled")
    print("✅ FP16 precision for memory efficiency")
    print("✅ More frequent checkpoints and evaluation")
    print("\nTraining will be slower but use significantly fewer resources!")
    print("-" * 60)
    
    # Run the training
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Resource-efficient training completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main() 