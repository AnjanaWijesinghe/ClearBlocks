'''
This module contains utility functions for the NN.
'''

import os
import gzip
import torch
import numpy as np


def load_mnist(path="data"):
    def read_images(filename):
        with gzip.open(os.path.join(path, filename), 'rb') as f:
            # Skip magic number (4 bytes), count (4), rows (4), cols (4)
            data = np.frombuffer(f.read(), np.uint8, offset=16)
        return data.reshape(-1, 28 * 28).astype('float32') / 255.0  # Normalize to [0, 1]

    def read_labels(filename):
        with gzip.open(os.path.join(path, filename), 'rb') as f:
            return np.frombuffer(f.read(), np.uint8, offset=8)

    return (read_images("train-images-idx3-ubyte.gz"), read_labels("train-labels-idx1-ubyte.gz"),
            read_images("t10k-images-idx3-ubyte.gz"), read_labels("t10k-labels-idx1-ubyte.gz"))
    

def preprocess_data(X_train, y_train, X_test, y_test, max_samples=10000):
    # Limit to max_samples for faster training
    X_train = X_train[:max_samples]
    y_train = y_train[:max_samples]
    X_test = X_test[:max_samples]
    y_test = y_test[:max_samples]
    # Convert to PyTorch tensors
    X_train = torch.tensor(X_train).view(-1, 1, 28, 28)  # Reshape to (N, C, H, W)
    y_train = torch.tensor(y_train)
    X_test = torch.tensor(X_test).view(-1, 1, 28, 28)
    y_test = torch.tensor(y_test)
    return X_train, y_train, X_test, y_test

