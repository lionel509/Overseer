#!/bin/bash

echo "🔋 Resource-Efficient Training Setup for Overseer"
echo "================================================"
echo ""

# Activate conda environment
if command -v conda &> /dev/null; then
    if conda info --envs | grep -q '^overseer[[:space:]]'; then
        echo "Activating conda environment 'overseer'..."
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate overseer
    else
        echo "Conda environment 'overseer' does not exist. Please create it first."
        exit 1
    fi
else
    echo "Conda is not installed or not in PATH. Please install Anaconda or Miniconda."
    exit 1
fi

# Install required packages with conda (if not already installed)
echo "Installing required packages..."
conda install -y -c conda-forge pytorch pandas python-dotenv

# Install remaining packages with pip (inside the conda env)
pip install transformers datasets kaggle accelerate psutil

# Set up Kaggle API
echo "Setting up Kaggle API..."
mkdir -p ~/.kaggle
echo "Please place your kaggle.json file in ~/.kaggle/"

# Create directories
mkdir -p ./datasets
mkdir -p ./models
mkdir -p ./logs
mkdir -p ./checkpoints

# Download base model
echo "Downloading Gemma 3n base model..."
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; import os; AutoTokenizer.from_pretrained('google/gemma-3n-E4B-it', token=os.environ.get('HF_TOKEN')); AutoModelForCausalLM.from_pretrained('google/gemma-3n-E4B-it', token=os.environ.get('HF_TOKEN'))"

echo ""
echo "✅ Resource-Efficient Training Setup Complete!"
echo ""
echo "🎯 Resource-Efficient Mode Features:"
echo "   • Reduced batch size (4 instead of 16)"
echo "   • Increased gradient accumulation (16 steps)"
echo "   • Lower learning rate (5e-5 instead of 1e-4)"
echo "   • Reduced sequence length (1024 instead of 2048)"
echo "   • Fewer data loader workers (1 instead of 4)"
echo "   • Lower memory thresholds (70% RAM, 75% GPU)"
echo "   • Gradient checkpointing enabled"
echo "   • FP16 precision for memory efficiency"
echo "   • More frequent checkpoints and evaluation"
echo ""
echo "💡 Recommended for systems with:"
echo "   • Limited RAM (< 16GB)"
echo "   • Limited GPU memory (< 8GB)"
echo "   • Need to run other applications during training"
echo "   • Older hardware or laptops"
echo ""
echo "🚀 Starting resource-efficient training..."
echo ""

# Run resource-efficient training
python run_resource_efficient_training.py --download-data --continuous-learning 