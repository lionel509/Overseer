import pandas as pd
from typing import List, Dict

class SystemCommandsDataset:
    def __init__(self):
        self.commands_data = []
    
    def load_kaggle_data(self, kaggle_collector):
        """Load and process Kaggle datasets"""
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
    
    def process_dataset(self, dataset_path: str):
        # Placeholder for dataset-specific processing logic
        pass
    
    def create_training_examples(self) -> List[Dict]:
        """Create training examples from processed data"""
        training_examples = []
        for cmd in self.commands_data:
            training_examples.append({
                'input': f"How do I {cmd['description']}?",
                'output': f"You can use the command: `{cmd['command']}`\n\n{cmd['explanation']}"
            })
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
        typos = [
            ("git pus", "git push"),
            ("ls -la", "ls -la"),
            ("cd ..", "cd .."),
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