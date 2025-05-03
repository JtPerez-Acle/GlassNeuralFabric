# GlassNeuralFabric Examples

This document provides an overview of the example scripts included with GlassNeuralFabric to help you understand how to use the library for monitoring and analyzing neural network training.

## Overview

GlassNeuralFabric provides tools for:

1. **Capturing weight changes** during neural network training
2. **Analyzing significant changes** to identify important updates
3. **Creating model snapshots** at key points in training
4. **Visualizing weight evolution** over time

The examples demonstrate these capabilities in both Python and Rust.

## Python Examples

### 1. MNIST Demo (`python/examples/mnist_demo.py`)

A basic example showing how to attach the NeuroCapture module to a PyTorch model training on MNIST.

**Features demonstrated:**
- Setting up the capture configuration
- Attaching the capture module to a model
- Sending weight updates to an endpoint

**Running the example:**
```bash
cd python
python examples/mnist_demo.py
```

### 2. Weight Visualization Demo (`python/examples/weight_visualization_demo.py`)

A more advanced example that visualizes weight changes during training in real-time.

**Features demonstrated:**
- Real-time visualization of weight values and deltas
- Creating and visualizing model snapshots
- Filtering which layers to capture
- Saving weight history to a JSON file

**Running the example:**
```bash
cd python
python examples/weight_visualization_demo.py
```

## Rust Examples

### 1. Weight Processor Demo (`crates/reducers/examples/weight_processor_demo.rs`)

Demonstrates how to use the weight processor directly in Rust applications.

**Features demonstrated:**
- Processing batches of weight updates
- Detecting significant weight changes
- Creating model snapshots
- Custom storage and logging implementations

**Running the example:**
```bash
cd crates/reducers
cargo run --example weight_processor_demo
```

## SpacetimeDB Integration

GlassNeuralFabric can be integrated with SpacetimeDB for real-time, scalable storage and querying of neural network state.

### 1. Setting Up SpacetimeDB

First, install SpacetimeDB:

```bash
# Install SpacetimeDB
curl -sSf https://install.spacetimedb.com | sh
```

Then, deploy the schema:

```bash
# Deploy the schema
just deploy-schema
```

### 2. Running with SpacetimeDB

Start SpacetimeDB with hot-reloading:

```bash
# Start SpacetimeDB
just run-stdb
```

Configure the Python bridge to send updates to SpacetimeDB:

```python
config = CaptureConfig(
    sig_level=0.01,
    batch_interval=0.5,
    endpoint="http://localhost:3000/reducer/update_weight",
)
```

### 3. Visualizing with SpacetimeDB

The visualization UI can connect to SpacetimeDB to display real-time updates:

```jsx
import { useSpacetimeDB } from '../hooks/useSpacetimeDB';

function WeightVisualization() {
  const {
    weights,
    snapshots,
    isConnected,
    createSnapshot
  } = useSpacetimeDB('http://localhost:3000', 'neurospace');

  // Render visualization using weights and snapshots
}
```

## Key Components

### Python Bridge

The Python bridge provides:

- `NeuroCapture`: Main class for capturing weight changes
- `CaptureConfig`: Configuration for the capture process
- `attach_capture()`: Convenience function to attach capture to a model

### Rust Reducers Crate

The Rust reducers crate provides:

- `WeightProcessor`: Trait defining weight processing operations
- `WeightProcessorImpl`: Implementation of the weight processor
- `StateStorage`: Trait for storing weights and snapshots
- `Logger`: Trait for logging and metrics

### SpacetimeDB Integration

The SpacetimeDB integration provides:

- SQL schema for storing weights and snapshots
- Deployment scripts for setting up SpacetimeDB
- React hooks for connecting to SpacetimeDB
- Real-time subscriptions to weight and snapshot updates

## Integration Guide

### Integrating with PyTorch Models

```python
import torch
from bridge.src import NeuroCapture, CaptureConfig, attach_capture

# Create your model
model = YourModel()

# Configure the capture module
config = CaptureConfig(
    sig_level=0.01,  # Capture changes greater than 0.01
    batch_interval=0.5,  # Send updates every 0.5 seconds
    endpoint="http://your-endpoint/update",
    include_layers=["layer1", "layer2"],  # Optional: only capture specific layers
)

# Attach the capture module
capture = attach_capture(model, config)

# Train your model normally
# ...

# Detach when done
capture.detach_from_model()
```

### Integrating with Rust Applications

```rust
use neurospace_reducers::models::{Weight, WeightUpdate};
use neurospace_reducers::storage::YourStorageImpl;
use neurospace_reducers::logging::YourLoggerImpl;
use neurospace_reducers::weight_processor::WeightProcessorImpl;

// Create storage and logger
let storage = YourStorageImpl::new();
let logger = YourLoggerImpl::new();

// Create weight processor
let processor = WeightProcessorImpl::new(
    storage,
    logger,
    0.1, // significance threshold
);

// Process weight updates
let updates = vec![
    WeightUpdate {
        id: "layer1.weight".to_string(),
        value: 0.5,
        timestamp: get_current_timestamp(),
        origin_sample: "sample1".to_string(),
        agent_id: None,
    },
    // More updates...
];

processor.process_weight_batch(updates)?;

// Detect significant changes
let significant_changes = processor.detect_significant_changes(0.2)?;

// Create a snapshot
processor.create_model_snapshot("Training milestone".to_string())?;
```

## Visualization

The weight visualization demo shows how to create a real-time visualization of weight changes. You can customize this to:

1. Track specific layers or weights
2. Create custom visualizations for your specific model
3. Save and load weight histories for offline analysis
4. Identify patterns in weight evolution

## Next Steps

After exploring these examples, you can:

1. Implement custom storage backends (e.g., database, cloud storage)
2. Create custom visualizations for your specific models
3. Integrate with your existing training pipelines
4. Develop anomaly detection for unusual weight changes
5. Build model debugging tools based on weight analysis

For more information, see the API documentation in the `docs` directory.
