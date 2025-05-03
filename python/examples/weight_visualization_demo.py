"""
Weight Visualization Demo for GlassNeuralFabric

This example demonstrates how to use GlassNeuralFabric to:
1. Capture weight changes during model training
2. Analyze significant weight changes
3. Visualize weight evolution over time
4. Create model snapshots at key points

The script trains a simple neural network on MNIST and visualizes
the weight changes in real-time using matplotlib.
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
from collections import defaultdict
import threading
import queue

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

class WeightVisualizer:
    """Visualizes weight changes during training"""
    
    def __init__(self):
        self.weight_history = defaultdict(list)
        self.delta_history = defaultdict(list)
        self.timestamps = defaultdict(list)
        self.snapshots = []
        self.data_queue = queue.Queue()
        self.running = True
        
        # Set up the plot
        plt.ion()  # Enable interactive mode
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.suptitle('Neural Network Weight Evolution', fontsize=16)
        
        self.ax1.set_title('Weight Values Over Time')
        self.ax1.set_xlabel('Training Steps')
        self.ax1.set_ylabel('Weight Value')
        
        self.ax2.set_title('Weight Deltas Over Time')
        self.ax2.set_xlabel('Training Steps')
        self.ax2.set_ylabel('Weight Delta')
        
        # Start the visualization thread
        self.viz_thread = threading.Thread(target=self._update_visualization)
        self.viz_thread.daemon = True
        self.viz_thread.start()
    
    def process_weight_update(self, weight: CapturedWeight):
        """Process a weight update from the capture module"""
        self.data_queue.put(weight)
    
    def add_snapshot(self, reason: str):
        """Add a model snapshot marker"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.snapshots.append((len(next(iter(self.weight_history.values()), [])), reason, timestamp))
    
    def _update_visualization(self):
        """Update the visualization with new data"""
        colors = plt.cm.tab10.colors
        while self.running:
            # Process all available updates
            updates = []
            while not self.data_queue.empty():
                try:
                    updates.append(self.data_queue.get_nowait())
                except queue.Empty:
                    break
            
            if updates:
                # Process the updates
                for weight in updates:
                    layer_id = weight.id
                    self.weight_history[layer_id].append(weight.value)
                    self.delta_history[layer_id].append(weight.delta)
                    self.timestamps[layer_id].append(weight.timestamp)
                
                # Clear the plots
                self.ax1.clear()
                self.ax2.clear()
                
                # Set titles
                self.ax1.set_title('Weight Values Over Time')
                self.ax1.set_xlabel('Training Steps')
                self.ax1.set_ylabel('Weight Value')
                
                self.ax2.set_title('Weight Deltas Over Time')
                self.ax2.set_xlabel('Training Steps')
                self.ax2.set_ylabel('Weight Delta')
                
                # Plot the weight histories
                for i, (layer_id, values) in enumerate(self.weight_history.items()):
                    color = colors[i % len(colors)]
                    x = range(len(values))
                    self.ax1.plot(x, values, label=layer_id, color=color)
                    self.ax2.plot(x, self.delta_history[layer_id], label=layer_id, color=color)
                
                # Add snapshot markers
                for step, reason, timestamp in self.snapshots:
                    self.ax1.axvline(x=step, color='r', linestyle='--', alpha=0.5)
                    self.ax2.axvline(x=step, color='r', linestyle='--', alpha=0.5)
                    self.ax1.text(step, self.ax1.get_ylim()[1] * 0.9, f"{reason} ({timestamp})", 
                                 rotation=90, verticalalignment='top')
                
                # Add legends
                self.ax1.legend(loc='upper right')
                self.ax2.legend(loc='upper right')
                
                # Draw the plot
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            
            # Sleep to avoid consuming too much CPU
            time.sleep(0.1)
    
    def stop(self):
        """Stop the visualization thread"""
        self.running = False
        self.viz_thread.join(timeout=1.0)
        plt.ioff()
        plt.close(self.fig)
    
    def save_data(self, filename="weight_history.json"):
        """Save the collected data to a JSON file"""
        data = {
            "weight_history": {k: v for k, v in self.weight_history.items()},
            "delta_history": {k: v for k, v in self.delta_history.items()},
            "timestamps": {k: v for k, v in self.timestamps.items()},
            "snapshots": self.snapshots
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filename}")

class CustomEndpoint:
    """Custom endpoint to receive weight updates"""
    
    def __init__(self, visualizer):
        self.visualizer = visualizer
    
    def handle_update(self, weight_data):
        """Handle a weight update from the capture module"""
        for item in weight_data:
            weight = CapturedWeight(
                id=item["id"],
                value=item["value"],
                delta=item["delta"],
                timestamp=item["timestamp"],
                origin_sample=item["origin_sample"],
                agent_id=item.get("agent_id")
            )
            self.visualizer.process_weight_update(weight)
        
        return {"status": "success", "message": f"Processed {len(weight_data)} updates"}

def start_mock_server(endpoint, port=5000):
    """Start a mock server to receive weight updates"""
    import threading
    import http.server
    import socketserver
    from http import HTTPStatus
    import json
    
    class RequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            response = endpoint.handle_update(data)
            
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    handler = RequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()

def main():
    # Set up device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Create visualizer
    visualizer = WeightVisualizer()
    
    # Create custom endpoint
    endpoint = CustomEndpoint(visualizer)
    
    # Start mock server in a separate thread
    server_thread = threading.Thread(target=start_mock_server, args=(endpoint,))
    server_thread.daemon = True
    server_thread.start()
    
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
        sig_level=0.001,  # Capture changes greater than 0.001
        batch_interval=0.2,  # Send updates every 0.2 seconds
        endpoint="http://localhost:5000",
        include_layers=["fc1.weight", "fc2.weight"]  # Only capture these layers
    )
    
    # Attach the bridge to the model
    capture = attach_capture(model, config)
    
    # Set up loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    # Train the model
    print("Starting training...")
    num_epochs = 3
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        # Add a snapshot at the start of each epoch
        visualizer.add_snapshot(f"Epoch {epoch+1} Start")
        
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
                
                # Add a snapshot at regular intervals
                if batch_idx % 300 == 299:
                    visualizer.add_snapshot(f"Batch {batch_idx+1}")
        
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
        
        # Add a snapshot at the end of each epoch
        visualizer.add_snapshot(f"Epoch {epoch+1} End (Acc: {accuracy:.2f}%)")
    
    print("Training complete!")
    
    # Detach the bridge
    capture.detach_from_model()
    
    # Save the collected data
    visualizer.save_data()
    
    # Keep the program running to allow viewing the visualization
    print("Visualization is active. Press Ctrl+C to exit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        visualizer.stop()

if __name__ == "__main__":
    main()
