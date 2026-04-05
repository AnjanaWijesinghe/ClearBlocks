'''
This module contains functions to build the CNN model for MNIST classification.
'''

import torch
from tqdm import tqdm
import torch.nn as nn


# 5 layer CNN for MNIST
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.fc = nn.Linear(512 * 7 * 7, 10)  # Assuming input images are 28x28

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)  # 14x14
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)  # 7x7
        x = torch.relu(self.conv3(x))
        x = torch.relu(self.conv4(x))
        x = torch.relu(self.conv5(x))
        x = x.view(x.size(0), -1)  # Flatten
        return self.fc(x)
    
    
def train_model(model, X_train, y_train, epochs=5, batch_size=64, lr=0.001):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        for i in tqdm(range(0, len(X_train), batch_size), desc=f"Epoch {epoch+1}/{epochs}"):
            X_batch = X_train[i:i+batch_size]
            y_batch = y_train[i:i+batch_size]
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * X_batch.size(0)  # Accumulate loss
        avg_loss = epoch_loss / len(X_train)
        print(f"Epoch {epoch+1}/{epochs}, Average Loss: {avg_loss:.4f}")
        
    return model


def evaluate_model(model, X_test, y_test):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for i in range(0, len(X_test), 64):
            X_batch = X_test[i:i+64]
            y_batch = y_test[i:i+64]
            outputs = model(X_batch)
            _, predicted = torch.max(outputs.data, 1)
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()
    accuracy = correct / total
    print(f"Test Accuracy: {accuracy:.4f}")
    return accuracy


def save_model(model, path="mnist_cnn.pth"):
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")
    
    
def load_model(model, path="mnist_cnn.pth"):
    model.load_state_dict(torch.load(path))
    model.eval()
    
