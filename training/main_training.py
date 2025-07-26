import argparse
import os
from dotenv import load_dotenv
from training_config import TrainingConfig
from kaggle_data_collector import KaggleDataCollector
from data_preparation import SystemCommandsDataset
from fine_tuning import OverseerTrainer
from continuous_learning import ContinuousLearningManager

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    parser = argparse.ArgumentParser(description='Train Overseer Gemma 3n Model')
    parser.add_argument('--download-data', action='store_true', help='Download fresh data from Kaggle')
    parser.add_argument('--use-existing-data', action='store_true', help='Use existing processed data')
    parser.add_argument('--continuous-learning', action='store_true', help='Include user interaction data in training')
    parser.add_argument('--resume-from-checkpoint', type=str, default=None, help='Path to checkpoint to resume training from')
    args = parser.parse_args()

    config = TrainingConfig()
    kaggle_collector = KaggleDataCollector()
    dataset_processor = SystemCommandsDataset()
    trainer = OverseerTrainer(config)

    if args.download_data:
        print('Downloading fresh data from Kaggle...')
        dataset_processor.load_kaggle_data(kaggle_collector)

    print('Preparing training data...')
    training_examples = dataset_processor.create_training_examples()
    synthetic_examples = dataset_processor.generate_synthetic_data()

    if args.continuous_learning:
        learning_manager = ContinuousLearningManager()
        user_data = learning_manager.get_training_data(min_feedback=1)
        training_examples.extend(user_data)

    all_training_data = training_examples + synthetic_examples
    train_size = int(len(all_training_data) * config.train_split)
    val_size = int(len(all_training_data) * config.val_split)
    train_data = all_training_data[:train_size]
    val_data = all_training_data[train_size:train_size + val_size]
    train_dataset = trainer.prepare_dataset(train_data)
    val_dataset = trainer.prepare_dataset(val_data)
    print(f'Starting training with {len(train_data)} training examples...')
    print("\n================ SAFEGUARDS ENABLED: Training is protected by memory, OOM, and early stopping safeguards ================\n")
    if args.resume_from_checkpoint:
        print(f"Resuming training from checkpoint: {args.resume_from_checkpoint}")
    trainer.train(train_dataset, val_dataset, resume_from_checkpoint=args.resume_from_checkpoint)
    print('Training completed!')
    print(f'Model saved to: {config.output_dir}')

if __name__ == "__main__":
    main() 