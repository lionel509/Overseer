#!/bin/bash

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
conda install -y -c conda-forge pytorch pandas python-dotenv

# Install remaining packages with pip (inside the conda env)
<<<<<<< HEAD
pip install transformers datasets kaggle accelerate pillow timm
=======
pip install transformers datasets kaggle accelerate psutil
>>>>>>> 6dbc57b5c429104813d2331756c724e071791c43

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
echo "🎯 Training Setup Complete!"
echo ""
echo "Available training modes:"
echo "1. Standard training (faster, more resources):"
echo "   python main_training.py --download-data --continuous-learning"
echo ""
echo "2. Resource-efficient training (slower, fewer resources):"
echo "   python main_training.py --resource-efficient --download-data --continuous-learning"
echo "   or use the convenience script:"
echo "   python run_resource_efficient_training.py --download-data --continuous-learning"
echo ""
echo "Resource-efficient mode is recommended for:"
echo "   - Systems with limited RAM (< 16GB)"
echo "   - Systems with limited GPU memory (< 8GB)"
echo "   - Running other applications during training"
echo "   - Training on laptops or older hardware"
echo ""
echo "Starting standard training pipeline..."
python main_training.py --download-data --continuous-learning 