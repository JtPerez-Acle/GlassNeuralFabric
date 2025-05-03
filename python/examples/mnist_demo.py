"""
MNIST demo for the NeuroSpacetime bridge.

This example shows how to use the NeuroSpacetime bridge to visualize
the training of a simple neural network on the MNIST dataset.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
import os

# Import the NeuroSpacetime bridge
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge.src import NeuroCapture, CaptureConfig, attach_capture

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
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    # Create model
    model = SimpleNN().to(device)
    
    # Set up NeuroSpacetime bridge
    config = CaptureConfig(
        sig_level=0.01,  # Capture changes greater than 0.01
        batch_interval=0.5,  # Send updates every 0.5 seconds
        endpoint="http://localhost:5000/update_weight",
    )
    
    # Attach the bridge to the model
    capture = attach_capture(model, config)
    
    # Set up loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    # Train the model
    print("Starting training...")
    num_epochs = 5
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
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
        
        print(f"Epoch {epoch+1}/{num_epochs}, Accuracy: {100 * correct / total:.2f}%")
    
    print("Training complete!")
    
    # Detach the bridge
    capture.detach_from_model()
    
    # Keep the program running to allow viewing the visualization
    print("Press Ctrl+C to exit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
