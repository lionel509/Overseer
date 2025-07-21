import os
from dotenv import load_dotenv
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer
)
from datasets import Dataset
from typing import Dict, List
from training_config import TrainingConfig

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class OverseerTrainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        hf_token = os.environ.get("HF_TOKEN")
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model, token=hf_token)
        self.model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            token=hf_token,
            torch_dtype=torch.float16 if config.mixed_precision else torch.float32
        )
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
        def tokenize_function(examples):
            formatted_texts = []
            for i in range(len(examples['input'])):
                text = f"User: {examples['input'][i]}\nAssistant: {examples['output'][i]}"
                formatted_texts.append(text)
            tokenized = self.tokenizer(
                formatted_texts,
                truncation=True,
                padding="max_length",
                max_length=self.config.max_sequence_length,
                return_tensors="pt"
            )
            tokenized["labels"] = tokenized["input_ids"].clone()
            return tokenized
        dataset = Dataset.from_dict({
            'input': [item['input'] for item in data],
            'output': [item['output'] for item in data]
        })
        return dataset.map(tokenize_function, batched=True)
    def train(self, train_dataset: Dataset, val_dataset: Dataset):
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
        trainer.train()
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir) 