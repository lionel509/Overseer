import kaggle
import pandas as pd
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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
        df = pd.read_csv(dataset_path)
        relevant_commands = df[df['command'].str.contains(
            'ls|cd|grep|find|top|ps|kill|chmod|chown|tar|zip|git|npm|pip|docker',
            case=False, na=False
        )]
        training_data = []
        for _, row in relevant_commands.iterrows():
            training_data.append({
                'input': f"User wants to: {row['description']}",
                'output': f"Command: {row['command']}\nExplanation: {row['explanation']}"
            })
        return pd.DataFrame(training_data) 