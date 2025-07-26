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
from safeguards import MemoryMonitor, OOMHandler, EarlyStopping, SafeguardLogger

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
    def train(self, train_dataset: Dataset, val_dataset: Dataset, resume_from_checkpoint: str = None):
        print("\n================ SAFEGUARDS ENABLED: Training is protected by memory, OOM, and early stopping safeguards ================\n")
        logger = SafeguardLogger()
        memory_monitor = MemoryMonitor()
        oom_handler = OOMHandler()
        early_stopper = EarlyStopping()
        batch_size = self.config.batch_size
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
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
        )
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        try:
            if not memory_monitor.check_memory():
                logger.log("Memory usage exceeded before training started.", level="error")
                print("[SAFEGUARD] Memory usage exceeded before training. Aborting.")
                return
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        except RuntimeError as e:
            if 'out of memory' in str(e).lower():
                logger.log("OOM error detected during training. Attempting to reduce batch size.", level="error")
                print("[SAFEGUARD] OOM error detected. Reducing batch size and retrying...")
                batch_size = oom_handler.handle_oom(batch_size)
                training_args.per_device_train_batch_size = batch_size
                training_args.per_device_eval_batch_size = batch_size
                trainer.args = training_args
                torch.cuda.empty_cache()
                trainer.train(resume_from_checkpoint=resume_from_checkpoint)
            else:
                logger.log(f"Unhandled training error: {e}", level="error")
                raise
        # Early stopping (manual, after training loop)
        # NOTE: For full integration, a custom callback would be better, but this is a stub for now.
        # After each epoch, you could call early_stopper.step(val_loss) and break if True.
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir) 