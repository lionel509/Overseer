#!/bin/bash

# Install required packages
pip install torch transformers datasets kaggle accelerate pandas python-dotenv

# Set up Kaggle API
echo "Setting up Kaggle API..."
mkdir -p ~/.kaggle
echo "Please place your kaggle.json file in ~/.kaggle/"

# Create directories
mkdir -p ./datasets
mkdir -p ./models
mkdir -p ./logs

# Download base model
echo "Downloading Gemma 3n base model..."
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; import os; AutoTokenizer.from_pretrained('google/gemma-3n-E4B-it', token=os.environ.get('HF_TOKEN')); AutoModelForCausalLM.from_pretrained('google/gemma-3n-E4B-it', token=os.environ.get('HF_TOKEN'))"

# Run training
echo "Starting training pipeline..."
python main_training.py --download-data --continuous-learning 