"""
SpacetimeDB Integration Demo for GlassNeuralFabric

This example demonstrates how to use GlassNeuralFabric with SpacetimeDB:
1. Train a simple neural network on MNIST
2. Capture weight changes and send them to SpacetimeDB
3. Create model snapshots at key points in training
4. Visualize the weight changes in real-time

Prerequisites:
- SpacetimeDB installed and running
- Schema deployed using `just deploy-schema`
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import json
import uuid
from datetime import datetime
import threading
import argparse

# Import the NeuroSpacetime bridge
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge.src import NeuroCapture, CaptureConfig, attach_capture, CapturedWeight

# Define a simple neural network
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SpacetimeDB Integration Demo for GlassNeuralFabric')
    parser.add_argument('--host', type=str, default='localhost', help='SpacetimeDB host')
    parser.add_argument('--port', type=int, default=3000, help='SpacetimeDB port')
    parser.add_argument('--db', type=str, default='neurospace', help='SpacetimeDB database name')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs to train')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--sig-level', type=float, default=0.01, help='Significance level for weight changes')
    args = parser.parse_args()
    
    # Set up device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Set up data loaders
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Create model
    model = SimpleNN().to(device)
    
    # Set up NeuroSpacetime bridge
    spacetime_endpoint = f"http://{args.host}:{args.port}/reducer/update_weight"
    snapshot_endpoint = f"http://{args.host}:{args.port}/reducer/create_snapshot"
    
    config = CaptureConfig(
        sig_level=args.sig_level,  # Capture changes greater than sig_level
        batch_interval=0.2,  # Send updates every 0.2 seconds
        endpoint=spacetime_endpoint,
        snapshot_endpoint=snapshot_endpoint,
        include_layers=["fc1.weight", "fc2.weight"]  # Only capture these layers
    )
    
    # Attach the bridge to the model
    capture = attach_capture(model, config)
    
    # Set up loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    # Train the model
    print("Starting training...")
    print(f"Sending weight updates to {spacetime_endpoint}")
    print(f"Sending snapshots to {snapshot_endpoint}")
    
    num_epochs = args.epochs
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        # Create a snapshot at the start of each epoch
        capture.create_snapshot(f"Epoch {epoch+1} Start", [])
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            output = model(data)
            loss = criterion(output, target)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            # Print statistics
            running_loss += loss.item()
            if batch_idx % 100 == 99:
                print(f"Epoch {epoch+1}/{num_epochs}, Batch {batch_idx+1}/{len(train_loader)}, Loss: {running_loss/100:.4f}")
                running_loss = 0.0
                
                # Create a snapshot at regular intervals
                if batch_idx % 300 == 299:
                    capture.create_snapshot(f"Epoch {epoch+1}, Batch {batch_idx+1}", [])
        
        # Test the model
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        accuracy = 100 * correct / total
        print(f"Epoch {epoch+1}/{num_epochs}, Accuracy: {accuracy:.2f}%")
        
        # Create a snapshot at the end of each epoch
        capture.create_snapshot(f"Epoch {epoch+1} End (Acc: {accuracy:.2f}%)", [])
    
    print("Training complete!")
    
    # Detach the bridge
    capture.detach_from_model()
    
    print("SpacetimeDB Integration Demo completed successfully!")
    print("You can now use the visualization UI to view the weight changes.")

if __name__ == "__main__":
    main()
