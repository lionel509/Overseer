# Training & Model Customization
## Gemma 3n Fine-tuning and Dataset Integration

### 🎓 **Training Overview**

#### **Training Objectives**
- **Domain Specialization**: Fine-tune Gemma 3n for system administration tasks
- **Command Understanding**: Improve natural language to system command translation
- **Tool Recommendations**: Enhance software suggestion accuracy
- **Context Awareness**: Better understanding of system state and user context
- **Personalization**: Adapt to individual user preferences and workflows

#### **Training Data Sources**
- **Kaggle Datasets**: Public datasets for system administration and command line usage
- **User Interactions**: Anonymous usage patterns and command histories
- **Documentation**: Software documentation and help text
- **Community Data**: Stack Overflow, GitHub issues, and technical forums
- **Synthetic Data**: Generated examples for edge cases and rare scenarios

### 📊 **Kaggle Dataset Integration**

#### **Dataset Collection Strategy**
```python
# kaggle_data_collector.py
import kaggle
import pandas as pd
import os
from typing import List, Dict

class KaggleDataCollector:
    def __init__(self, api_key_path: str = "~/.kaggle/kaggle.json"):
        """Initialize Kaggle API client"""
        self.api = kaggle.KaggleApi()
        self.api.authenticate()
    
    def search_relevant_datasets(self) -> List[Dict]:
        """Search for datasets relevant to system administration"""
        search_terms = [
            "system administration",
            "command line",
            "shell commands",
            "system monitoring",
            "file management",
            "developer tools",
            "software recommendations",
            "system performance"
        ]
        
        relevant_datasets = []
        for term in search_terms:
            datasets = self.api.dataset_list(search=term, sort_by="relevance")
            relevant_datasets.extend(datasets)
        
        return relevant_datasets
    
    def download_dataset(self, dataset_id: str, path: str = "./datasets"):
        """Download a specific dataset"""
        try:
            self.api.dataset_download_files(dataset_id, path=path, unzip=True)
            print(f"Downloaded dataset: {dataset_id}")
        except Exception as e:
            print(f"Error downloading {dataset_id}: {e}")
    
    def process_system_commands_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Process system commands dataset for training"""
        # Load and clean the dataset
        df = pd.read_csv(dataset_path)
        
        # Filter for relevant commands
        relevant_commands = df[df['command'].str.contains(
            'ls|cd|grep|find|top|ps|kill|chmod|chown|tar|zip|git|npm|pip|docker',
            case=False, na=False
        )]
        
        # Create training examples
        training_data = []
        for _, row in relevant_commands.iterrows():
            training_data.append({
                'input': f"User wants to: {row['description']}",
                'output': f"Command: {row['command']}\nExplanation: {row['explanation']}"
            })
        
        return pd.DataFrame(training_data)
```

#### **Priority Datasets for Download**
1. **System Administration Commands**: Command line usage patterns
2. **Software Tools Database**: Comprehensive software catalog with descriptions
3. **System Performance Metrics**: Historical performance data
4. **Developer Workflow Data**: Common development tasks and solutions
5. **Security Vulnerability Data**: CVE database and security recommendations
6. **File System Patterns**: Common file organization and naming conventions

### 🔧 **Model Training Pipeline**

#### **Training Configuration**
```python
# training_config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainingConfig:
    # Model Configuration
    base_model: str = "gemma-3n-4b"
    use_2b_submodel: bool = True
    enable_mix_and_match: bool = True
    
    # Training Parameters
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 4
    
    # Data Configuration
    max_sequence_length: int = 2048
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Output Configuration
    output_dir: str = "./models/overseer-gemma-3n"
    save_steps: int = 500
    eval_steps: int = 100
    
    # Hardware Configuration
    use_gpu: bool = True
    mixed_precision: bool = True
    dataloader_num_workers: int = 4
```

#### **Fine-tuning Implementation**
```python
# fine_tuning.py
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer
)
from datasets import Dataset
import pandas as pd
from typing import Dict, List

class OverseerTrainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        self.model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            torch_dtype=torch.float16 if config.mixed_precision else torch.float32
        )
        
        # Add special tokens for system context
        special_tokens = {
            "additional_special_tokens": [
                "<system>", "</system>",
                "<command>", "</command>",
                "<file>", "</file>",
                "<output>", "</output>"
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def prepare_dataset(self, data: List[Dict]) -> Dataset:
        """Prepare training dataset"""
        def tokenize_function(examples):
            # Format: "<system>context</system>User: input\nAssistant: output"
            formatted_texts = []
            for i in range(len(examples['input'])):
                text = f"User: {examples['input'][i]}\nAssistant: {examples['output'][i]}"
                formatted_texts.append(text)
            
            # Tokenize
            tokenized = self.tokenizer(
                formatted_texts,
                truncation=True,
                padding="max_length",
                max_length=self.config.max_sequence_length,
                return_tensors="pt"
            )
            
            # Labels are the same as input_ids for causal LM
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        dataset = Dataset.from_dict({
            'input': [item['input'] for item in data],
            'output': [item['output'] for item in data]
        })
        
        return dataset.map(tokenize_function, batched=True)
    
    def train(self, train_dataset: Dataset, val_dataset: Dataset):
        """Train the model"""
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=50,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=self.config.mixed_precision,
            dataloader_num_workers=self.config.dataloader_num_workers,
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
```

### 📈 **Training Data Preparation**

#### **System Commands Dataset**
```python
# data_preparation.py
import json
import pandas as pd
from typing import List, Dict, Tuple

class SystemCommandsDataset:
    def __init__(self):
        self.commands_data = []
    
    def load_kaggle_data(self, kaggle_collector: KaggleDataCollector):
        """Load and process Kaggle datasets"""
        # Download relevant datasets
        datasets_to_download = [
            "system-administration-commands",
            "linux-shell-commands",
            "developer-tools-database",
            "software-recommendations",
            "system-performance-metrics"
        ]
        
        for dataset_id in datasets_to_download:
            try:
                kaggle_collector.download_dataset(dataset_id)
                print(f"Processing dataset: {dataset_id}")
                # Process each dataset based on its structure
                self.process_dataset(f"./datasets/{dataset_id}")
            except Exception as e:
                print(f"Could not process {dataset_id}: {e}")
    
    def create_training_examples(self) -> List[Dict]:
        """Create training examples from processed data"""
        training_examples = []
        
        # Command explanation examples
        for cmd in self.commands_data:
            training_examples.append({
                'input': f"How do I {cmd['description']}?",
                'output': f"You can use the command: `{cmd['command']}`\n\n{cmd['explanation']}"
            })
        
        # Tool recommendation examples
        training_examples.extend([
            {
                'input': "I need a tool for monitoring GPU usage",
                'output': "I recommend these GPU monitoring tools:\n1. nvitop - Interactive GPU monitoring\n2. nvidia-smi - Built-in NVIDIA tool\n3. htop with GPU support\n\nWhich would you like to install?"
            },
            {
                'input': "Find files related to machine learning",
                'output': "I'll search for ML-related files using semantic analysis...\n<command>find . -name '*.py' -exec grep -l 'machine learning\\|tensorflow\\|pytorch' {} \\;</command>"
            }
        ])
        
        return training_examples
    
    def generate_synthetic_data(self) -> List[Dict]:
        """Generate synthetic training data for edge cases"""
        synthetic_examples = []
        
        # Common typos and corrections
        typos = [
            ("git pus", "git push"),
            ("ls -la", "ls -la"),  # correct
            ("cd ..", "cd .."),    # correct
            ("grpe", "grep"),
            ("tial", "tail"),
            ("killl", "kill")
        ]
        
        for typo, correction in typos:
            synthetic_examples.append({
                'input': f"I typed: {typo}",
                'output': f"Did you mean: `{correction}`? I can run the corrected command for you."
            })
        
        return synthetic_examples
```

### 🔄 **Continuous Learning Pipeline**

#### **User Interaction Learning**
```python
# continuous_learning.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class ContinuousLearningManager:
    def __init__(self, db_path: str = "user_interactions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing interactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                ai_response TEXT,
                user_feedback INTEGER,  -- 1 for positive, -1 for negative, 0 for neutral
                context TEXT,  -- JSON string of system context
                success BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_interaction(self, user_input: str, ai_response: str, 
                       context: Dict, success: bool = True,
                       feedback: int = 0):
        """Log user interaction for future training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_interactions 
            (user_input, ai_response, user_feedback, context, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_input, ai_response, feedback, json.dumps(context), success))
        
        conn.commit()
        conn.close()
    
    def get_training_data(self, min_feedback: int = 0) -> List[Dict]:
        """Extract training data from user interactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_input, ai_response, context 
            FROM user_interactions 
            WHERE user_feedback >= ? AND success = 1
            ORDER BY timestamp DESC
        ''', (min_feedback,))
        
        results = cursor.fetchall()
        conn.close()
        
        training_data = []
        for user_input, ai_response, context in results:
            training_data.append({
                'input': user_input,
                'output': ai_response,
                'context': json.loads(context)
            })
        
        return training_data
    
    def should_retrain(self, threshold: int = 1000) -> bool:
        """Check if model should be retrained based on new data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM user_interactions 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        recent_interactions = cursor.fetchone()[0]
        conn.close()
        
        return recent_interactions >= threshold
```

### 🎯 **Training Execution Pipeline**

#### **Main Training Script**
```python
# main_training.py
import argparse
from pathlib import Path
import torch

def main():
    parser = argparse.ArgumentParser(description='Train Overseer Gemma 3n Model')
    parser.add_argument('--config', type=str, default='training_config.py',
                       help='Path to training configuration')
    parser.add_argument('--download-data', action='store_true',
                       help='Download fresh data from Kaggle')
    parser.add_argument('--use-existing-data', action='store_true',
                       help='Use existing processed data')
    parser.add_argument('--continuous-learning', action='store_true',
                       help='Include user interaction data in training')
    
    args = parser.parse_args()
    
    # Initialize components
    config = TrainingConfig()
    kaggle_collector = KaggleDataCollector()
    dataset_processor = SystemCommandsDataset()
    trainer = OverseerTrainer(config)
    
    # Prepare training data
    if args.download_data:
        print("Downloading fresh data from Kaggle...")
        dataset_processor.load_kaggle_data(kaggle_collector)
    
    # Load and prepare datasets
    print("Preparing training data...")
    training_examples = dataset_processor.create_training_examples()
    synthetic_examples = dataset_processor.generate_synthetic_data()
    
    # Add continuous learning data if requested
    if args.continuous_learning:
        learning_manager = ContinuousLearningManager()
        user_data = learning_manager.get_training_data(min_feedback=1)
        training_examples.extend(user_data)
    
    # Combine all training data
    all_training_data = training_examples + synthetic_examples
    
    # Split data
    train_size = int(len(all_training_data) * config.train_split)
    val_size = int(len(all_training_data) * config.val_split)
    
    train_data = all_training_data[:train_size]
    val_data = all_training_data[train_size:train_size + val_size]
    
    # Prepare datasets
    train_dataset = trainer.prepare_dataset(train_data)
    val_dataset = trainer.prepare_dataset(val_data)
    
    # Start training
    print(f"Starting training with {len(train_data)} training examples...")
    trainer.train(train_dataset, val_dataset)
    
    print("Training completed!")
    print(f"Model saved to: {config.output_dir}")

if __name__ == "__main__":
    main()
```

### 🚀 **Training Deployment**

#### **Setup Instructions**
```bash
# setup_training.sh
#!/bin/bash

# Install required packages
pip install torch transformers datasets kaggle accelerate

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
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('gemma-3n-4b'); AutoModelForCausalLM.from_pretrained('gemma-3n-4b')"

# Run training
echo "Starting training pipeline..."
python main_training.py --download-data --continuous-learning
```

#### **Training Monitoring**
```python
# training_monitor.py
import wandb
from transformers import TrainerCallback

class OverseerTrainingCallback(TrainerCallback):
    def __init__(self):
        wandb.init(project="overseer-gemma-3n-training")
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            wandb.log(logs)
    
    def on_train_end(self, args, state, control, **kwargs):
        wandb.finish()
```

### 📊 **Training Evaluation**

#### **Model Evaluation Metrics**
- **Perplexity**: Language modeling quality
- **BLEU Score**: Command generation accuracy
- **Task Success Rate**: System command execution success
- **Response Time**: Inference speed benchmarks
- **Memory Usage**: Resource consumption during inference

#### **Evaluation Script**
```python
# evaluation.py
from transformers import pipeline
import json
import time
from typing import List, Dict

class ModelEvaluator:
    def __init__(self, model_path: str):
        self.model = pipeline('text-generation', model=model_path)
    
    def evaluate_command_generation(self, test_cases: List[Dict]) -> Dict:
        """Evaluate command generation accuracy"""
        results = {
            'total_tests': len(test_cases),
            'successful_commands': 0,
            'average_response_time': 0,
            'command_accuracy': 0
        }
        
        total_time = 0
        for test_case in test_cases:
            start_time = time.time()
            response = self.model(test_case['input'], max_length=512)
            end_time = time.time()
            
            total_time += (end_time - start_time)
            
            # Check if response contains expected command
            if test_case['expected_command'] in response[0]['generated_text']:
                results['successful_commands'] += 1
        
        results['average_response_time'] = total_time / len(test_cases)
        results['command_accuracy'] = results['successful_commands'] / len(test_cases)
        
        return results
```

**Ready to start training?** This comprehensive training pipeline will create a specialized Gemma 3n model perfectly suited for system administration tasks! 🤖
