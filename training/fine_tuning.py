import os
from dotenv import load_dotenv
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM
)
from transformers.training_args import TrainingArguments
from transformers.trainer import Trainer
from datasets import Dataset
from typing import Dict, List
from training_config import TrainingConfig
from training_safeguards import TrainingSafeguards, MemoryThresholds, CheckpointConfig

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
        
        # Initialize training safeguards
        memory_thresholds = MemoryThresholds(
            max_ram_percent=config.max_ram_percent,
            max_gpu_memory_percent=config.max_gpu_memory_percent,
            max_swap_percent=config.max_swap_percent,
            memory_check_interval=config.memory_check_interval
        )
        checkpoint_config = CheckpointConfig(
            save_frequency=config.checkpoint_save_frequency,
            max_checkpoints=config.max_checkpoints,
            checkpoint_dir=config.checkpoint_dir,
            auto_resume=config.auto_resume
        )
        self.safeguards = TrainingSafeguards(memory_thresholds, checkpoint_config)
        
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
        # Initialize training safeguards
        self.safeguards.start_training_session()
        
        # Check for existing checkpoint to resume from
        latest_checkpoint = self.safeguards.checkpoint_manager.get_latest_checkpoint()
        resume_from_checkpoint = None
        if self.config.auto_resume and latest_checkpoint:
            resume_from_checkpoint = latest_checkpoint['checkpoint_path']
            print(f"Resuming from checkpoint: {resume_from_checkpoint}")
        
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
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=False,
            dataloader_num_workers=self.config.dataloader_num_workers,
            remove_unused_columns=False,
            # Add checkpoint resume support
            resume_from_checkpoint=resume_from_checkpoint,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        # Custom training loop with safeguards
        try:
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        except KeyboardInterrupt:
            print("\nTraining interrupted by user. Creating emergency checkpoint...")
            self.safeguards.handle_training_interruption(trainer, 0, {})
            raise
        except Exception as e:
            print(f"\nTraining error occurred: {e}")
            self.safeguards.handle_training_interruption(trainer, 0, {})
            raise
        
        # Save final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        # Print training summary
        summary = self.safeguards.get_training_summary()
        print(f"Training completed! Duration: {summary.get('training_duration_seconds', 0):.1f} seconds")
        print(f"Model saved to: {self.config.output_dir}") 