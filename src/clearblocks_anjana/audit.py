'''
This module contains functions for auditing the AI model training process by using the captured metadata to verify the integrity of the training process.
'''

import os
import torch
from argparse import ArgumentParser

# Custom script imports
from . import utils
from . import build_model
from . import blockchain as bc
from . import blockchain_utils as bc_utils


def parse_args():
    parser = ArgumentParser(description="Audit the AI model training process using blockchain-anchored metadata.")
    parser.add_argument("-p", "--path", type=str, required=True, help="Path to the captured data JSON file to audit.")
    parser.add_argument("-d", "--data_dir", type=str, required=True, help="Path to the directory containing the training data (e.g., MNIST).")
    return parser.parse_args()


def main():
    args = parse_args()
    
    # File to validate
    data_capture_path = args.path
    # Directory containing the training data
    training_data_path = args.data_dir
    
    temp_dir = ".temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Verify the captured data against the blockchain
    is_valid, block_index = bc.verify_blockchain_entry(data_capture_path)
    if not is_valid:
        print("Metadata integrity verification failed! The captured data does not match any entry in the blockchain.")
        return
    
    print(f"Metadata integrity verified! The captured data is anchored in block #{block_index}. Proceeding with audit...")
    
    # Initialize data capture
    metadata = bc_utils.get_captured_data(data_capture_path)
    # Set random seed for reproducibility
    torch.manual_seed(metadata["json"]["random_seed"])
    
    # Verify training data integrity
    is_valid = bc_utils.verify_captured_data("training_data", training_data_path, metadata)
    if not is_valid:
        return
    
    # Load and preprocess data
    X_train, y_train, X_test, y_test = utils.load_mnist(training_data_path)
    X_train, y_train, X_test, y_test = utils.preprocess_data(X_train, y_train, X_test, y_test, max_samples=5000)

    # Build and train model
    model = build_model.CNN()
    
    # define hyperparameters
    epochs = metadata["json"]["epochs"]
    batch_size = metadata["json"]["batch_size"]
    learning_rate = metadata["json"]["learning_rate"]
    model = build_model.train_model(model, X_train, y_train, epochs=epochs, batch_size=batch_size, lr=learning_rate)

    # Evaluate model
    accuracy = build_model.evaluate_model(model, X_test, y_test)

    weights_name = metadata["json"]["weights_name"]
    weights_path = os.path.join(temp_dir, weights_name)
    # save model
    build_model.save_model(model, weights_path)
    
    # verify the model weights hash against the captured hash
    bc_utils.verify_captured_data("weights", weights_path, metadata)
    

if __name__ == "__main__":
    main()