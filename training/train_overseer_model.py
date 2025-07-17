#!/usr/bin/env python3
"""
Overseer AI Model Training Script
Google Gemma 3n Fine-tuning for System Assistant Tasks

This standalone Python script provides a comprehensive pipeline for training the Overseer AI 
system assistant using Google's Gemma 3n model. All configuration is loaded from .env file.

Usage:
    python train_overseer_model.py

Prerequisites:
    - Python 3.9+ with virtual environment
    - CUDA-compatible GPU (recommended)
    - .env file configured with training parameters
    - At least 16GB RAM for model training
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import argparse
import re

# ML and NLP libraries
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    pipeline, BitsAndBytesConfig
)
from datasets import Dataset as HFDataset, load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Kaggle API for dataset download
try:
    import kaggle
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

# Environment management
from dotenv import load_dotenv

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('training.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_environment_config():
    """Load configuration from environment variables"""
    # Find and load .env file
    script_dir = Path(__file__).parent
    workspace_dir = script_dir.parent
    env_file_path = workspace_dir / ".env"
    
    logger.info(f"🔍 Loading .env from: {env_file_path}")
    logger.info(f"📁 .env file exists: {env_file_path.exists()}")
    
    if not env_file_path.exists():
        logger.error(f"❌ .env file not found at {env_file_path}")
        logger.error("Please create a .env file based on .env.example")
        sys.exit(1)
    
    # Load the .env file with override=True to ensure it takes precedence
    loaded = load_dotenv(dotenv_path=env_file_path, override=True)
    logger.info(f"✅ .env loaded successfully: {loaded}")
    
    # Verify critical variables
    model_name = os.getenv('MODEL_NAME')
    hf_model = os.getenv('HUGGING_FACE_MODEL')
    logger.info(f"🔧 MODEL_NAME from env: '{model_name}'")
    logger.info(f"🔧 HUGGING_FACE_MODEL from env: '{hf_model}'")
    
    if not model_name or not hf_model:
        logger.error("❌ Critical environment variables missing!")
        sys.exit(1)

def get_env_value(key: str, default_value=None, value_type=str):
    """Get environment variable with type conversion and default value"""
    value = os.getenv(key, default_value)
    if value is None:
        return None
    
    if value_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif value_type == int:
        return int(value)
    elif value_type == float:
        return float(value)
    else:
        return value

def load_configuration():
    """Load all configuration from environment variables"""
    config = {}
    
    # Model Configuration
    config['MODEL_NAME'] = get_env_value("MODEL_NAME", "gemma3n:latest")
    config['HUGGING_FACE_MODEL'] = get_env_value("HUGGING_FACE_MODEL", "google/gemma-3n-9b-it")
    config['BASE_MODEL_PATH'] = get_env_value("BASE_MODEL_PATH", "./models/base_gemma")
    config['FINE_TUNED_MODEL_PATH'] = get_env_value("FINE_TUNED_MODEL_PATH", "./models/overseer_gemma")
    
    # Training Configuration
    config['OUTPUT_DIR'] = get_env_value("OUTPUT_DIR", "./outputs/overseer_gemma_lora")
    config['NUM_TRAIN_EPOCHS'] = get_env_value("NUM_TRAIN_EPOCHS", 3, int)
    config['PER_DEVICE_TRAIN_BATCH_SIZE'] = get_env_value("PER_DEVICE_TRAIN_BATCH_SIZE", 1, int)
    config['PER_DEVICE_EVAL_BATCH_SIZE'] = get_env_value("PER_DEVICE_EVAL_BATCH_SIZE", 1, int)
    config['GRADIENT_ACCUMULATION_STEPS'] = get_env_value("GRADIENT_ACCUMULATION_STEPS", 8, int)
    config['WARMUP_STEPS'] = get_env_value("WARMUP_STEPS", 50, int)
    config['LEARNING_RATE'] = get_env_value("LEARNING_RATE", 2e-4, float)
    config['WEIGHT_DECAY'] = get_env_value("WEIGHT_DECAY", 0.01, float)
    config['LOGGING_STEPS'] = get_env_value("LOGGING_STEPS", 10, int)
    config['SAVE_STEPS'] = get_env_value("SAVE_STEPS", 100, int)
    config['EVAL_STEPS'] = get_env_value("EVAL_STEPS", 100, int)
    config['MAX_GRAD_NORM'] = get_env_value("MAX_GRAD_NORM", 1.0, float)
    config['MAX_STEPS'] = get_env_value("MAX_STEPS", 500, int)
    config['DATALOADER_NUM_WORKERS'] = get_env_value("DATALOADER_NUM_WORKERS", 4, int)
    
    # LoRA Configuration
    config['LORA_RANK'] = get_env_value("LORA_RANK", 16, int)
    config['LORA_ALPHA'] = get_env_value("LORA_ALPHA", 32, int)
    config['LORA_DROPOUT'] = get_env_value("LORA_DROPOUT", 0.1, float)
    
    # Dataset Configuration
    config['KAGGLE_DATASET_IT_HELPDESK'] = get_env_value("KAGGLE_DATASET_IT_HELPDESK", "amandalund/it-help-desk-tickets")
    config['KAGGLE_DATASET_CUSTOMER_SUPPORT'] = get_env_value("KAGGLE_DATASET_CUSTOMER_SUPPORT", "thoughtvector/customer-support-on-twitter")
    config['KAGGLE_DATASET_NETFLIX_SHOWS'] = get_env_value("KAGGLE_DATASET_NETFLIX_SHOWS", "shivamb/netflix-shows")
    config['KAGGLE_DATASET_ARXIV'] = get_env_value("KAGGLE_DATASET_ARXIV", "Cornell-University/arxiv")
    config['KAGGLE_USERNAME'] = get_env_value("KAGGLE_USERNAME")
    config['KAGGLE_KEY'] = get_env_value("KAGGLE_KEY")
    
    # Data Preprocessing
    config['MAX_LENGTH'] = get_env_value("MAX_LENGTH", 512, int)
    config['TEST_SIZE'] = get_env_value("TEST_SIZE", 0.2, float)
    config['VAL_SIZE'] = get_env_value("VAL_SIZE", 0.1, float)
    
    # Deployment Configuration
    config['EXPORT_PATH'] = get_env_value("EXPORT_PATH", "./models/overseer_deployed")
    config['OLLAMA_MODEL_NAME'] = get_env_value("OLLAMA_MODEL_NAME", "overseer-gemma")
    
    # Evaluation Configuration
    config['MAX_NEW_TOKENS'] = get_env_value("MAX_NEW_TOKENS", 150, int)
    config['TEMPERATURE'] = get_env_value("TEMPERATURE", 0.7, float)
    config['TOP_P'] = get_env_value("TOP_P", 0.9, float)
    config['TOP_K'] = get_env_value("TOP_K", 40, int)
    config['REPEAT_PENALTY'] = get_env_value("REPEAT_PENALTY", 1.1, float)
    config['NUM_CTX'] = get_env_value("NUM_CTX", 2048, int)
    
    # System Configuration
    config['RANDOM_SEED'] = get_env_value("RANDOM_SEED", 42, int)
    config['LOG_LEVEL'] = get_env_value("LOG_LEVEL", "INFO")
    
    return config

def check_system_requirements():
    """Check system requirements for training"""
    logger.info("🔧 Checking system requirements...")
    
    # Check PyTorch installation
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")
        logger.info(f"GPU device: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        logger.warning("⚠️  CUDA not available, training will be slow on CPU")
    
    # Check available memory
    import psutil
    memory = psutil.virtual_memory()
    logger.info(f"System RAM: {memory.total / 1024**3:.1f} GB available")
    
    if memory.total < 16 * 1024**3:  # Less than 16GB
        logger.warning("⚠️  Less than 16GB RAM available, consider reducing batch size")

def create_directories(config):
    """Create necessary directories"""
    directories = [
        "./models",
        "./data", 
        "./outputs",
        config['OUTPUT_DIR'],
        config['EXPORT_PATH']
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"📁 Created directory: {directory}")

def setup_kaggle_api():
    """Setup Kaggle API credentials"""
    if not KAGGLE_AVAILABLE:
        logger.error("❌ Kaggle API not installed. Install with: pip install kaggle")
        return False
    
    # Check for Kaggle credentials
    kaggle_json_path = Path.home() / '.kaggle' / 'kaggle.json'
    if not kaggle_json_path.exists():
        logger.warning("⚠️  Kaggle credentials not found at ~/.kaggle/kaggle.json")
        logger.info("💡 You can download datasets manually or set up Kaggle API credentials")
        return False
    
    logger.info("✅ Kaggle API credentials found")
    return True

def download_kaggle_dataset(dataset_name: str, download_path: str) -> bool:
    """Download a Kaggle dataset"""
    try:
        if not KAGGLE_AVAILABLE:
            logger.warning(f"⚠️  Kaggle API not available, skipping {dataset_name}")
            return False
            
        logger.info(f"📥 Downloading Kaggle dataset: {dataset_name}")
        
        # Create download directory
        os.makedirs(download_path, exist_ok=True)
        
        # Download and extract dataset
        kaggle.api.dataset_download_files(
            dataset_name, 
            path=download_path, 
            unzip=True
        )
        
        logger.info(f"✅ Downloaded {dataset_name} to {download_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {dataset_name}: {e}")
        return False

def load_it_helpdesk_dataset(data_path: str) -> pd.DataFrame:
    """Load and process IT Help Desk tickets dataset"""
    try:
        # Look for CSV files in the dataset directory
        csv_files = list(Path(data_path).glob("*.csv"))
        if not csv_files:
            logger.warning(f"⚠️  No CSV files found in {data_path}")
            return pd.DataFrame()
        
        # Load the main CSV file
        df = pd.read_csv(csv_files[0])
        logger.info(f"📊 Loaded IT Help Desk dataset: {len(df)} records")
        
        # Process the dataset for instruction-response format
        processed_data = []
        
        for _, row in df.iterrows():
            # Use ticket description as user query and resolution as response
            if 'Description' in df.columns and 'Resolution' in df.columns:
                if pd.notna(row['Description']) and pd.notna(row['Resolution']):
                    processed_data.append({
                        'instruction': str(row['Description']).strip(),
                        'response': str(row['Resolution']).strip(),
                        'category': 'it_support'
                    })
            elif 'ticket_description' in df.columns and 'resolution' in df.columns:
                if pd.notna(row['ticket_description']) and pd.notna(row['resolution']):
                    processed_data.append({
                        'instruction': str(row['ticket_description']).strip(),
                        'response': str(row['resolution']).strip(),
                        'category': 'it_support'
                    })
        
        result_df = pd.DataFrame(processed_data)
        logger.info(f"✅ Processed IT Help Desk dataset: {len(result_df)} instruction-response pairs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to load IT Help Desk dataset: {e}")
        return pd.DataFrame()

def load_customer_support_dataset(data_path: str) -> pd.DataFrame:
    """Load and process Customer Support Twitter dataset"""
    try:
        csv_files = list(Path(data_path).glob("*.csv"))
        if not csv_files:
            logger.warning(f"⚠️  No CSV files found in {data_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"📊 Loaded Customer Support dataset: {len(df)} records")
        
        processed_data = []
        
        for _, row in df.iterrows():
            # Use customer tweet as instruction and company response as response
            if 'text' in df.columns and 'response_tweet_text' in df.columns:
                if pd.notna(row['text']) and pd.notna(row['response_tweet_text']):
                    processed_data.append({
                        'instruction': str(row['text']).strip(),
                        'response': str(row['response_tweet_text']).strip(),
                        'category': 'customer_support'
                    })
        
        result_df = pd.DataFrame(processed_data)
        logger.info(f"✅ Processed Customer Support dataset: {len(result_df)} instruction-response pairs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to load Customer Support dataset: {e}")
        return pd.DataFrame()

def load_netflix_dataset(data_path: str) -> pd.DataFrame:
    """Load and process Netflix shows dataset for recommendation tasks"""
    try:
        csv_files = list(Path(data_path).glob("*.csv"))
        if not csv_files:
            logger.warning(f"⚠️  No CSV files found in {data_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"📊 Loaded Netflix dataset: {len(df)} records")
        
        processed_data = []
        
        # Create instruction-response pairs for content recommendations
        for _, row in df.iterrows():
            if 'title' in df.columns and 'description' in df.columns:
                if pd.notna(row['title']) and pd.notna(row['description']):
                    # Create recommendation-style questions
                    instruction = f"Tell me about the show/movie '{row['title']}'"
                    response = f"'{row['title']}' is {str(row['description']).strip()}"
                    
                    if 'genre' in df.columns and pd.notna(row['genre']):
                        response += f" It belongs to the {row['genre']} genre."
                    
                    if 'release_year' in df.columns and pd.notna(row['release_year']):
                        response += f" It was released in {row['release_year']}."
                    
                    processed_data.append({
                        'instruction': instruction,
                        'response': response,
                        'category': 'content_recommendation'
                    })
        
        result_df = pd.DataFrame(processed_data)
        logger.info(f"✅ Processed Netflix dataset: {len(result_df)} instruction-response pairs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to load Netflix dataset: {e}")
        return pd.DataFrame()

def load_arxiv_dataset(data_path: str) -> pd.DataFrame:
    """Load and process ArXiv papers dataset for academic assistance"""
    try:
        csv_files = list(Path(data_path).glob("*.csv"))
        json_files = list(Path(data_path).glob("*.json"))
        
        if not csv_files and not json_files:
            logger.warning(f"⚠️  No CSV or JSON files found in {data_path}")
            return pd.DataFrame()
        
        # Try to load CSV first, then JSON
        if csv_files:
            df = pd.read_csv(csv_files[0])
        else:
            df = pd.read_json(json_files[0], lines=True)
            
        logger.info(f"📊 Loaded ArXiv dataset: {len(df)} records")
        
        processed_data = []
        
        # Create instruction-response pairs for academic assistance
        for _, row in df.iterrows():
            if 'title' in df.columns and 'abstract' in df.columns:
                if pd.notna(row['title']) and pd.notna(row['abstract']):
                    instruction = f"Explain the research paper titled '{row['title']}'"
                    response = f"This paper, '{row['title']}', presents research on: {str(row['abstract']).strip()}"
                    
                    if 'categories' in df.columns and pd.notna(row['categories']):
                        response += f" This work falls under the categories: {row['categories']}."
                    
                    processed_data.append({
                        'instruction': instruction,
                        'response': response,
                        'category': 'academic_assistance'
                    })
        
        result_df = pd.DataFrame(processed_data)
        logger.info(f"✅ Processed ArXiv dataset: {len(result_df)} instruction-response pairs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to load ArXiv dataset: {e}")
        return pd.DataFrame()

def create_comprehensive_dataset(config):
    """Create a comprehensive dataset by combining multiple Kaggle datasets"""
    logger.info("🔧 Creating comprehensive dataset from Kaggle sources...")
    
    # Setup Kaggle API
    kaggle_available = setup_kaggle_api()
    
    # Create data directory
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    all_datasets = []
    
    # Dataset configurations
    datasets_config = [
        {
            'name': config['KAGGLE_DATASET_IT_HELPDESK'],
            'path': data_dir / "it_helpdesk",
            'loader': load_it_helpdesk_dataset
        },
        {
            'name': config['KAGGLE_DATASET_CUSTOMER_SUPPORT'],
            'path': data_dir / "customer_support",
            'loader': load_customer_support_dataset
        },
        {
            'name': config['KAGGLE_DATASET_NETFLIX_SHOWS'],
            'path': data_dir / "netflix",
            'loader': load_netflix_dataset
        },
        {
            'name': config['KAGGLE_DATASET_ARXIV'],
            'path': data_dir / "arxiv",
            'loader': load_arxiv_dataset
        }
    ]
    
    # Download and process each dataset
    for dataset_config in datasets_config:
        logger.info(f"\n📊 Processing dataset: {dataset_config['name']}")
        
        # Download dataset if Kaggle API is available
        if kaggle_available:
            download_success = download_kaggle_dataset(
                dataset_config['name'], 
                str(dataset_config['path'])
            )
        else:
            download_success = dataset_config['path'].exists()
            if not download_success:
                logger.warning(f"⚠️  Dataset directory {dataset_config['path']} not found")
        
        # Load and process dataset
        if download_success or dataset_config['path'].exists():
            df = dataset_config['loader'](str(dataset_config['path']))
            if not df.empty:
                all_datasets.append(df)
                logger.info(f"✅ Added {len(df)} samples from {dataset_config['name']}")
            else:
                logger.warning(f"⚠️  No data loaded from {dataset_config['name']}")
        else:
            logger.warning(f"⚠️  Skipping {dataset_config['name']} - not available")
    
    # Combine all datasets
    if all_datasets:
        combined_df = pd.concat(all_datasets, ignore_index=True)
        logger.info(f"✅ Combined dataset created with {len(combined_df)} total samples")
        logger.info(f"📋 Categories: {combined_df['category'].value_counts().to_dict()}")
        
        # Save combined dataset
        combined_df.to_csv(data_dir / "combined_overseer_dataset.csv", index=False)
        logger.info(f"💾 Saved combined dataset to {data_dir / 'combined_overseer_dataset.csv'}")
        
        return combined_df
    else:
        # Fallback to synthetic dataset if no real data available
        logger.warning("⚠️  No real datasets available, creating fallback synthetic dataset")
        return create_fallback_synthetic_dataset()

def create_fallback_synthetic_dataset():
    """Create a fallback synthetic dataset when real datasets are not available"""
    logger.info("🔧 Creating fallback synthetic system assistant dataset...")
    
    # Enhanced system assistant conversations
    system_conversations = [
        {
            "instruction": "How do I check my CPU usage?",
            "response": "You can check CPU usage using several methods:\n1. Use 'top' command for real-time monitoring\n2. Use 'htop' for a more user-friendly interface\n3. Use 'ps aux' to see process-specific usage\n4. Use 'vmstat' for system statistics",
            "category": "system_monitoring"
        },
        {
            "instruction": "My system is running slow, what should I check?",
            "response": "When your system is slow, check these areas:\n1. CPU usage with 'top' or 'htop'\n2. Memory usage with 'free -h'\n3. Disk space with 'df -h'\n4. Disk I/O with 'iotop'\n5. Network usage with 'nethogs'\n6. Running processes with 'ps aux'",
            "category": "system_monitoring"
        },
        {
            "instruction": "How do I find large files on my system?",
            "response": "To find large files, use these commands:\n1. 'find / -type f -size +100M' - files larger than 100MB\n2. 'du -sh /*' - directory sizes\n3. 'ncdu' - interactive disk usage analyzer\n4. 'find / -type f -exec ls -la {} + | sort -k5 -nr | head -20' - top 20 largest files",
            "category": "file_management"
        },
        {
            "instruction": "What's the best way to monitor system performance?",
            "response": "For comprehensive system monitoring:\n1. Use 'htop' for real-time process monitoring\n2. Use 'iotop' for disk I/O monitoring\n3. Use 'netstat' or 'ss' for network connections\n4. Use 'vmstat' for virtual memory statistics\n5. Set up continuous monitoring with tools like 'sar' or 'dstat'\n6. Consider system monitoring tools like Nagios or Zabbix for advanced monitoring",
            "category": "system_monitoring"
        },
        {
            "instruction": "How do I organize my files better?",
            "response": "Here are effective file organization strategies:\n1. Create a clear folder structure\n2. Use descriptive names for files and folders\n3. Implement a consistent naming convention\n4. Use tags or metadata when available\n5. Regularly clean up unnecessary files\n6. Use tools like 'find' to locate files quickly",
            "category": "file_management"
        },
        {
            "instruction": "How can I find duplicate files?",
            "response": "To find duplicate files:\n1. Use 'fdupes' command: 'fdupes -r /path/to/directory'\n2. Use 'rdfind' for advanced deduplication\n3. Use Python script with hashlib for custom solutions\n4. GUI tools like 'dupeGuru' for visual interface\n5. Use 'find' with MD5 checksums for manual checking",
            "category": "file_management"
        },
        {
            "instruction": "How do I clean up disk space?",
            "response": "To clean up disk space:\n1. Remove temporary files: 'sudo rm -rf /tmp/*'\n2. Clean package cache: 'sudo apt-get clean' (Ubuntu/Debian)\n3. Remove old logs: 'sudo journalctl --vacuum-time=7d'\n4. Find large files: 'find / -type f -size +100M'\n5. Use disk cleanup tools like 'bleachbit'\n6. Remove old kernels and unused packages",
            "category": "system_maintenance"
        },
        {
            "instruction": "What should I do if my system won't boot?",
            "response": "For boot issues, try these steps:\n1. Check hardware connections and power\n2. Boot from recovery mode or live USB\n3. Check disk health with 'fsck'\n4. Review boot logs: 'journalctl -b'\n5. Check GRUB configuration\n6. Restore from backup if available\n7. Consider reinstalling bootloader",
            "category": "troubleshooting"
        },
        {
            "instruction": "How do I secure my system better?",
            "response": "To improve system security:\n1. Keep system updated: 'sudo apt update && sudo apt upgrade'\n2. Use strong passwords and 2FA\n3. Configure firewall: 'ufw enable'\n4. Disable unnecessary services\n5. Use SSH keys instead of passwords\n6. Regular security audits with tools like 'lynis'\n7. Monitor system logs for suspicious activity",
            "category": "security"
        },
        {
            "instruction": "How can I automate system backups?",
            "response": "To automate backups:\n1. Use 'rsync' for file synchronization\n2. Set up cron jobs for scheduled backups\n3. Use tools like 'duplicity' for encrypted backups\n4. Configure cloud storage integration\n5. Test backup restoration regularly\n6. Create backup scripts with error handling\n7. Monitor backup job success/failure",
            "category": "system_maintenance"
        },
        # Add more diverse examples
        {
            "instruction": "How do I troubleshoot network connectivity issues?",
            "response": "To troubleshoot network issues:\n1. Check physical connections\n2. Use 'ping' to test connectivity\n3. Check DNS with 'nslookup' or 'dig'\n4. Verify IP configuration with 'ip addr'\n5. Check routing table with 'ip route'\n6. Test with 'traceroute' for path analysis\n7. Review network logs and firewall rules",
            "category": "network_troubleshooting"
        },
        {
            "instruction": "What are the best practices for system maintenance?",
            "response": "System maintenance best practices:\n1. Regular system updates and patches\n2. Monitor disk space and clean up regularly\n3. Check system logs for errors\n4. Backup important data consistently\n5. Monitor system performance metrics\n6. Update and rotate log files\n7. Review and update security configurations\n8. Document changes and maintenance activities",
            "category": "system_maintenance"
        }
    ]
    
    # Save synthetic dataset
    df = pd.DataFrame(system_conversations)
    df.to_csv("./data/fallback_synthetic_dataset.csv", index=False)
    logger.info(f"✅ Created fallback synthetic dataset with {len(df)} examples")
    logger.info(f"📋 Categories: {df['category'].unique()}")
    
    return df

def format_instruction_response(instruction: str, response: str) -> str:
    """Format instruction-response pair for training"""
    return f"""<|im_start|>system
You are Overseer, an AI-powered system assistant that helps users with system monitoring, file management, and technical tasks. Provide helpful, accurate, and actionable advice.
<|im_end|>
<|im_start|>user
{instruction}
<|im_end|>
<|im_start|>assistant
{response}
<|im_end|>"""

def preprocess_dataset(df):
    """Preprocess the dataset for training"""
    logger.info("🔧 Preprocessing dataset...")
    
    # Clean the data
    initial_size = len(df)
    df = df.dropna(subset=['instruction', 'response'])
    df = df[df['instruction'].str.len() > 10]  # Filter out very short instructions
    df = df[df['response'].str.len() > 20]    # Filter out very short responses
    
    # Clean text fields
    df['instruction'] = df['instruction'].str.strip()
    df['response'] = df['response'].str.strip()
    
    # Remove any empty strings after stripping
    df = df[df['instruction'] != '']
    df = df[df['response'] != '']
    
    # Format for training
    df['text'] = df.apply(lambda row: format_instruction_response(
        row['instruction'], row['response']), axis=1)
    
    logger.info(f"✅ Cleaned dataset: {len(df)} samples (removed {initial_size - len(df)} samples)")
    return df

def create_data_splits(df, config):
    """Create train/validation/test splits with robust handling of small datasets"""
    test_size = config['TEST_SIZE']
    val_size = config['VAL_SIZE']
    random_seed = config['RANDOM_SEED']
    
    logger.info(f"📊 Creating data splits (test_size={test_size}, val_size={val_size})...")
    
    # Check if we have enough data for stratified splitting
    category_counts = df['category'].value_counts()
    min_category_count = category_counts.min()
    logger.info(f"📈 Category distribution: {category_counts.to_dict()}")
    logger.info(f"📉 Minimum category count: {min_category_count}")
    
    # Calculate minimum samples needed for stratified split
    min_samples_needed = int(1 / min(test_size, val_size/(1-test_size))) + 1
    
    try:
        if min_category_count >= min_samples_needed:
            # Use stratified split if we have enough samples per category
            logger.info("✅ Using stratified split")
            
            # First split: train + val, test
            train_val_df, test_df = train_test_split(
                df, test_size=test_size, random_state=random_seed, stratify=df['category']
            )
            
            # Second split: train, val
            train_df, val_df = train_test_split(
                train_val_df, test_size=val_size/(1-test_size), random_state=random_seed, 
                stratify=train_val_df['category']
            )
        else:
            # Use random split if not enough samples for stratification
            logger.warning(f"⚠️  Insufficient samples for stratified split (min: {min_category_count}, needed: {min_samples_needed})")
            logger.info("📊 Using random split instead")
            
            # First split: train + val, test
            train_val_df, test_df = train_test_split(
                df, test_size=test_size, random_state=random_seed
            )
            
            # Second split: train, val
            train_df, val_df = train_test_split(
                train_val_df, test_size=val_size/(1-test_size), random_state=random_seed
            )
            
    except ValueError as e:
        logger.warning(f"⚠️  Stratified split failed: {e}")
        logger.info("📊 Falling back to random split")
        
        # Fallback to random split
        train_val_df, test_df = train_test_split(
            df, test_size=test_size, random_state=random_seed
        )
        
        train_df, val_df = train_test_split(
            train_val_df, test_size=val_size/(1-test_size), random_state=random_seed
        )
    
    logger.info(f"📈 Data splits:")
    logger.info(f"  Train: {len(train_df)} samples ({len(train_df)/len(df)*100:.1f}%)")
    logger.info(f"  Validation: {len(val_df)} samples ({len(val_df)/len(df)*100:.1f}%)")
    logger.info(f"  Test: {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}%)")
    
    # Log category distribution for each split
    for split_name, split_df in [("Train", train_df), ("Validation", val_df), ("Test", test_df)]:
        if 'category' in split_df.columns:
            split_categories = split_df['category'].value_counts()
            logger.info(f"  {split_name} categories: {split_categories.to_dict()}")
    
    return train_df, val_df, test_df

def tokenize_dataset(df, tokenizer, max_length):
    """Tokenize the dataset"""
    logger.info(f"🔤 Tokenizing dataset with max_length={max_length}...")
    
    def tokenize_function(examples):
        # Tokenize the text
        tokenized = tokenizer(
            examples['text'],
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        # For causal language modeling, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized
    
    # Convert to Hugging Face dataset
    dataset = HFDataset.from_pandas(df)
    
    # Tokenize
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    logger.info(f"✅ Tokenized dataset: {len(tokenized_dataset)} samples")
    return tokenized_dataset

def load_model_and_tokenizer(config):
    """Load the Gemma model and tokenizer for fine-tuning"""
    hf_model = config['HUGGING_FACE_MODEL']
    
    # Configure quantization for memory efficiency
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    
    # Load tokenizer
    logger.info("📚 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        hf_model,
        trust_remote_code=True,
        use_fast=True
    )
    
    # Add padding token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    logger.info("🧠 Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        hf_model,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
        use_cache=False
    )
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    logger.info(f"✅ Model loaded successfully")
    logger.info(f"📊 Model parameters: {model.num_parameters():,}")
    
    return model, tokenizer

def setup_lora_config(config):
    """Setup LoRA configuration for efficient fine-tuning"""
    lora_config = LoraConfig(
        r=config['LORA_RANK'],
        lora_alpha=config['LORA_ALPHA'],
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_dropout=config['LORA_DROPOUT'],
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    logger.info("🔧 LoRA configuration:")
    logger.info(f"  Rank: {lora_config.r}")
    logger.info(f"  Alpha: {lora_config.lora_alpha}")
    logger.info(f"  Target modules: {lora_config.target_modules}")
    logger.info(f"  Dropout: {lora_config.lora_dropout}")
    
    return lora_config

def setup_training_arguments(config):
    """Setup training arguments"""
    training_args = TrainingArguments(
        output_dir=config['OUTPUT_DIR'],
        num_train_epochs=config['NUM_TRAIN_EPOCHS'],
        per_device_train_batch_size=config['PER_DEVICE_TRAIN_BATCH_SIZE'],
        per_device_eval_batch_size=config['PER_DEVICE_EVAL_BATCH_SIZE'],
        gradient_accumulation_steps=config['GRADIENT_ACCUMULATION_STEPS'],
        warmup_steps=config['WARMUP_STEPS'],
        learning_rate=config['LEARNING_RATE'],
        weight_decay=config['WEIGHT_DECAY'],
        logging_steps=config['LOGGING_STEPS'],
        save_steps=config['SAVE_STEPS'],
        eval_steps=config['EVAL_STEPS'],
        max_grad_norm=config['MAX_GRAD_NORM'],
        max_steps=config['MAX_STEPS'],
        dataloader_num_workers=config['DATALOADER_NUM_WORKERS'],
        remove_unused_columns=False,
        group_by_length=True,
        report_to="none",
        fp16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_32bit",
        lr_scheduler_type="cosine",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        evaluation_strategy="steps",
        save_strategy="steps",
        logging_first_step=True,
        seed=config['RANDOM_SEED'],
    )
    
    logger.info("📊 Training configuration:")
    logger.info(f"  Epochs: {training_args.num_train_epochs}")
    logger.info(f"  Batch size: {training_args.per_device_train_batch_size}")
    logger.info(f"  Gradient accumulation: {training_args.gradient_accumulation_steps}")
    logger.info(f"  Learning rate: {training_args.learning_rate}")
    logger.info(f"  Max steps: {training_args.max_steps}")
    logger.info(f"  Output dir: {training_args.output_dir}")
    logger.info(f"  Random seed: {training_args.seed}")
    
    return training_args

def train_model(model, tokenizer, train_dataset, val_dataset, training_args, lora_config):
    """Train the model with LoRA"""
    logger.info("🔧 Setting up model for LoRA training...")
    
    # Apply LoRA to the model
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    model.print_trainable_parameters()
    
    # Setup data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Not masked language modeling
        pad_to_multiple_of=8,
    )
    
    # Setup trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )
    
    logger.info("✅ Trainer setup complete!")
    
    # Start training
    logger.info("\n🚀 Starting training...")
    logger.info("=" * 50)
    
    try:
        # Train the model
        train_result = trainer.train()
        
        # Save the model
        trainer.save_model()
        trainer.save_state()
        
        logger.info("✅ Training completed successfully!")
        logger.info(f"📊 Training metrics:")
        logger.info(f"  Final loss: {train_result.training_loss:.4f}")
        logger.info(f"  Training time: {train_result.metrics['train_runtime']:.2f}s")
        logger.info(f"  Samples per second: {train_result.metrics['train_samples_per_second']:.2f}")
        
        return trainer, train_result
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return None, None

def evaluate_model(trainer, test_dataset):
    """Evaluate the trained model"""
    if trainer is None:
        logger.error("❌ No trained model available for evaluation")
        return None
    
    logger.info("📊 Evaluating model on test set...")
    
    # Evaluate on test set
    eval_results = trainer.evaluate(test_dataset)
    
    logger.info(f"📈 Evaluation results:")
    logger.info(f"  Test loss: {eval_results['eval_loss']:.4f}")
    logger.info(f"  Test perplexity: {np.exp(eval_results['eval_loss']):.2f}")
    logger.info(f"  Evaluation time: {eval_results['eval_runtime']:.2f}s")
    
    return eval_results

def test_model_inference(model, tokenizer, config):
    """Test model inference with sample prompts"""
    if model is None or tokenizer is None:
        logger.error("❌ Model or tokenizer not available for testing")
        return
    
    test_prompts = [
        "How do I check my system's memory usage?",
        "What's the best way to find files that are taking up too much space?",
        "My computer is running slowly. What should I do?",
        "How can I monitor network traffic on my system?",
        "What are some good practices for organizing files?"
    ]
    
    logger.info("🧪 Testing model inference...")
    logger.info(f"📊 Inference parameters:")
    logger.info(f"  Max new tokens: {config['MAX_NEW_TOKENS']}")
    logger.info(f"  Temperature: {config['TEMPERATURE']}")
    logger.info(f"  Top P: {config['TOP_P']}")
    logger.info(f"  Top K: {config['TOP_K']}")
    logger.info("=" * 50)
    
    try:
        # For PEFT models, we need to merge adapters for inference
        merged_model = model.merge_and_unload()
        
        pipe = pipeline(
            "text-generation",
            model=merged_model,
            tokenizer=tokenizer,
            max_length=config['MAX_LENGTH'] + config['MAX_NEW_TOKENS'],
            do_sample=True,
            temperature=config['TEMPERATURE'],
            top_p=config['TOP_P'],
            top_k=config['TOP_K'],
            repetition_penalty=config['REPEAT_PENALTY'],
            pad_token_id=tokenizer.eos_token_id
        )
        
        for i, prompt in enumerate(test_prompts[:3], 1):  # Test first 3 prompts
            logger.info(f"\n🔍 Test {i}: {prompt}")
            logger.info("-" * 40)
            
            # Format prompt for inference
            formatted_prompt = f"""<|im_start|>system
You are Overseer, an AI-powered system assistant that helps users with system monitoring, file management, and technical tasks.
<|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant
"""
            
            # Generate response
            response = pipe(formatted_prompt, max_new_tokens=config['MAX_NEW_TOKENS'], return_full_text=False)
            generated_text = response[0]['generated_text']
            
            # Clean up response
            if '<|im_end|>' in generated_text:
                generated_text = generated_text.split('<|im_end|>')[0]
            
            logger.info(f"🤖 Response: {generated_text.strip()}")
            
    except Exception as e:
        logger.error(f"❌ Inference test failed: {e}")

def export_model_for_deployment(trainer, model, tokenizer, config):
    """Export the trained model for deployment"""
    export_path = config['EXPORT_PATH']
    
    logger.info(f"📦 Exporting model for deployment to {export_path}...")
    
    if trainer is None or model is None or tokenizer is None:
        logger.error("❌ No trained model available for export")
        return False
    
    try:
        # Create export directory
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the final model
        logger.info("💾 Saving model and tokenizer...")
        trainer.save_model(export_path)
        tokenizer.save_pretrained(export_path)
        
        # Merge and save the final model (without LoRA adapters)
        merged_model_path = export_dir / "merged_model"
        merged_model_path.mkdir(exist_ok=True)
        
        logger.info("🔗 Merging LoRA adapters...")
        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(merged_model_path)
        tokenizer.save_pretrained(merged_model_path)
        
        # Save model configuration
        model_config = {
            "model_name": config['HUGGING_FACE_MODEL'],
            "training_config": {
                "num_train_epochs": config['NUM_TRAIN_EPOCHS'],
                "learning_rate": config['LEARNING_RATE'],
                "batch_size": config['PER_DEVICE_TRAIN_BATCH_SIZE'],
                "max_steps": config['MAX_STEPS'],
                "output_dir": config['OUTPUT_DIR'],
            },
            "lora_config": {
                "r": config['LORA_RANK'],
                "lora_alpha": config['LORA_ALPHA'],
                "lora_dropout": config['LORA_DROPOUT'],
            },
            "evaluation_config": {
                "max_new_tokens": config['MAX_NEW_TOKENS'],
                "temperature": config['TEMPERATURE'],
                "top_p": config['TOP_P'],
                "top_k": config['TOP_K'],
                "repeat_penalty": config['REPEAT_PENALTY'],
                "num_ctx": config['NUM_CTX'],
            },
            "export_timestamp": datetime.now().isoformat(),
            "export_path": str(export_path),
        }
        
        with open(export_dir / "model_config.json", 'w') as f:
            json.dump(model_config, f, indent=2)
        
        logger.info(f"✅ Model exported successfully to {export_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        return False

def create_ollama_integration(config):
    """Create Ollama Modelfile and deployment script"""
    export_path = config['EXPORT_PATH']
    model_name = config['OLLAMA_MODEL_NAME']
    
    logger.info(f"🐋 Creating Ollama integration for model '{model_name}'...")
    
    modelfile_content = f"""# Overseer AI System Assistant - Based on Gemma 2 9B
FROM {export_path}/merged_model

# System prompt
SYSTEM \"\"\"You are Overseer, an AI-powered system assistant that helps users with:
- System monitoring and performance analysis
- File management and organization
- Technical troubleshooting
- Command-line assistance
- System optimization recommendations

You provide helpful, accurate, and actionable advice. Always prioritize user safety and system security.
\"\"\"

# Parameters from environment configuration
PARAMETER temperature {config['TEMPERATURE']}
PARAMETER top_p {config['TOP_P']}
PARAMETER top_k {config['TOP_K']}
PARAMETER repeat_penalty {config['REPEAT_PENALTY']}
PARAMETER num_ctx {config['NUM_CTX']}

# Template
TEMPLATE \"\"\"<|im_start|>system
{{{{ .System }}}}
<|im_end|>
<|im_start|>user
{{{{ .Prompt }}}}
<|im_end|>
<|im_start|>assistant
\"\"\"
"""
    
    modelfile_path = Path(export_path) / "Modelfile"
    with open(modelfile_path, 'w') as f:
        f.write(modelfile_content)
    
    logger.info(f"✅ Modelfile created at {modelfile_path}")
    
    # Create deployment script
    deployment_script = f"""#!/bin/bash
# Overseer Model Deployment Script

echo "🚀 Deploying Overseer model to Ollama..."
echo "📋 Model name: {model_name}"
echo "📁 Export path: {export_path}"

# Create the model in Ollama
ollama create {model_name} -f {modelfile_path}

if [ $? -eq 0 ]; then
    echo "✅ Model '{model_name}' created successfully!"
    echo "🧪 Testing model..."
    echo "What is system monitoring?" | ollama run {model_name}
else
    echo "❌ Failed to create model"
    exit 1
fi

echo "🎉 Deployment complete!"
echo "You can now use the model with: ollama run {model_name}"
"""
    
    script_path = Path(export_path) / "deploy.sh"
    with open(script_path, 'w') as f:
        f.write(deployment_script)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"✅ Deployment script created at {script_path}")
    return modelfile_path, script_path

def main():
    """Main training pipeline"""
    global logger
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("🚀 Starting Overseer AI Model Training Pipeline")
    logger.info("=" * 60)
    logger.info(f"🕐 Training started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load environment configuration
        load_environment_config()
        config = load_configuration()
        
        logger.info("\n" + "="*50)
        logger.info("✅ Configuration loaded from environment variables")
        logger.info(f"📊 Model: {config['MODEL_NAME']}")
        logger.info(f"🤗 Hugging Face model: {config['HUGGING_FACE_MODEL']}")
        logger.info(f"🎯 Training epochs: {config['NUM_TRAIN_EPOCHS']}")
        logger.info(f"🔧 LoRA rank: {config['LORA_RANK']}")
        logger.info(f"📁 Output directory: {config['OUTPUT_DIR']}")
        
        # Set random seeds for reproducibility
        torch.manual_seed(config['RANDOM_SEED'])
        np.random.seed(config['RANDOM_SEED'])
        
        # Check system requirements
        check_system_requirements()
        
        # Create directories
        create_directories(config)
        
        # Create and preprocess dataset
        logger.info("\n" + "="*50)
        logger.info("📊 STEP 1: Data Preparation")
        logger.info("="*50)
        
        raw_df = create_comprehensive_dataset(config)
        processed_df = preprocess_dataset(raw_df)
        train_df, val_df, test_df = create_data_splits(processed_df, config)
        
        # Load model and tokenizer
        logger.info("\n" + "="*50)
        logger.info("🤖 STEP 2: Model Loading")
        logger.info("="*50)
        
        model, tokenizer = load_model_and_tokenizer(config)
        
        # Tokenize datasets
        logger.info("\n" + "="*50)
        logger.info("🔤 STEP 3: Data Tokenization")
        logger.info("="*50)
        
        train_dataset = tokenize_dataset(train_df, tokenizer, config['MAX_LENGTH'])
        val_dataset = tokenize_dataset(val_df, tokenizer, config['MAX_LENGTH'])
        test_dataset = tokenize_dataset(test_df, tokenizer, config['MAX_LENGTH'])
        
        # Setup training configuration
        logger.info("\n" + "="*50)
        logger.info("⚙️  STEP 4: Training Configuration")
        logger.info("="*50)
        
        lora_config = setup_lora_config(config)
        training_args = setup_training_arguments(config)
        
        # Train the model
        logger.info("\n" + "="*50)
        logger.info("🎯 STEP 5: Model Training")
        logger.info("="*50)
        
        trainer, train_result = train_model(
            model, tokenizer, train_dataset, val_dataset, training_args, lora_config
        )
        
        if trainer is not None:
            # Evaluate the model
            logger.info("\n" + "="*50)
            logger.info("📈 STEP 6: Model Evaluation")
            logger.info("="*50)
            
            eval_results = evaluate_model(trainer, test_dataset)
            
            # Test inference
            test_model_inference(model, tokenizer, config)
            
            # Export model
            logger.info("\n" + "="*50)
            logger.info("📦 STEP 7: Model Export")
            logger.info("="*50)
            
            if export_model_for_deployment(trainer, model, tokenizer, config):
                # Create Ollama integration
                modelfile_path, script_path = create_ollama_integration(config)
                
                # Save final results
                results = {
                    "training_completed": True,
                    "train_result": train_result.metrics if train_result else None,
                    "eval_results": eval_results,
                    "export_path": config['EXPORT_PATH'],
                    "model_name": config['OLLAMA_MODEL_NAME'],
                    "training_timestamp": datetime.now().isoformat()
                }
                
                with open("training_results.json", 'w') as f:
                    json.dump(results, f, indent=2)
                
                logger.info("\n" + "🎉" + "="*48 + "🎉")
                logger.info("✅ TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
                logger.info("="*50)
                logger.info(f"📁 Model exported to: {config['EXPORT_PATH']}")
                logger.info(f"🐋 Ollama model name: {config['OLLAMA_MODEL_NAME']}")
                logger.info(f"🚀 Deploy with: cd {config['EXPORT_PATH']} && ./deploy.sh")
                logger.info(f"📊 Results saved to: training_results.json")
                logger.info("🎉" + "="*48 + "🎉")
            else:
                logger.error("❌ Model export failed")
        else:
            logger.error("❌ Training failed, skipping evaluation and export")
            
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overseer AI Model Training Pipeline")
    parser.add_argument("--config", help="Path to .env file (optional)")
    args = parser.parse_args()
    
    main()
