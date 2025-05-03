# Modular Architecture Guidelines

This document outlines the modular architecture principles that all developers must follow when implementing features for the NeuroSpacetime project.

## Core Architecture Principles

### 1. Single Responsibility Principle

Each module should have one and only one reason to change. This means that a module should have a single, well-defined responsibility.

### 2. Interface Segregation

Modules should expose minimal, well-defined interfaces. Clients should not depend on interfaces they don't use.

### 3. Dependency Inversion

High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

### 4. Loose Coupling

Modules should have minimal knowledge of other modules. Changes in one module should not require changes in others.

### 5. High Cohesion

Related functionality should be grouped together within a module. Unrelated functionality should be separated into different modules.

## System Modules

The NeuroSpacetime system is divided into the following modules:

### 1. Data Capture Module

**Responsibility**: Capture neural network state during training.

**Key Components**:
- PyTorch hooks for weight capture
- Gradient capture utilities
- Activation capture utilities
- Batching and filtering logic

**Interface**:
```python
class NeuralCapture:
    """Interface for neural network state capture."""
    
    def attach_to_model(self, model: torch.nn.Module) -> None:
        """Attach capture hooks to a PyTorch model."""
        pass
        
    def detach_from_model(self) -> None:
        """Remove capture hooks from the model."""
        pass
        
    def set_capture_config(self, config: CaptureConfig) -> None:
        """Configure what data to capture and at what frequency."""
        pass
        
    def get_captured_data(self) -> List[CapturedData]:
        """Get the currently captured data."""
        pass
```

### 2. Data Processing Module

**Responsibility**: Process and analyze neural network data.

**Key Components**:
- Weight change reducers
- Gradient analysis utilities
- Anomaly detection algorithms
- Statistical analysis functions

**Interface**:
```rust
/// Interface for weight processing
pub trait WeightProcessor {
    /// Process a batch of weight updates
    fn process_weight_batch(&self, updates: Vec<WeightUpdate>) -> Result<(), Error>;
    
    /// Detect significant changes in weights
    fn detect_significant_changes(&self, threshold: f64) -> Result<Vec<Weight>, Error>;
    
    /// Create a snapshot of the current model state
    fn create_model_snapshot(&self, reason: String) -> Result<ModelSnapshot, Error>;
}

/// Interface for gradient analysis
pub trait GradientAnalyzer {
    /// Analyze gradients for anomalies
    fn detect_gradient_anomalies(&self, gradients: Vec<Gradient>) -> Result<Vec<Anomaly>, Error>;
    
    /// Calculate gradient statistics
    fn calculate_gradient_stats(&self, gradients: Vec<Gradient>) -> Result<GradientStats, Error>;
}
```

### 3. Storage Module

**Responsibility**: Manage persistence of neural network state.

**Key Components**:
- SpacetimeDB schema
- Query utilities
- Data access layer
- Caching mechanisms

**Interface**:
```rust
/// Interface for neural network state storage
pub trait StateStorage {
    /// Store a weight update
    fn store_weight(&self, weight: Weight) -> Result<(), Error>;
    
    /// Retrieve weights by layer
    fn get_weights_by_layer(&self, layer_id: &str) -> Result<Vec<Weight>, Error>;
    
    /// Retrieve weights by time range
    fn get_weights_by_time_range(&self, start: i64, end: i64) -> Result<Vec<Weight>, Error>;
    
    /// Store a model snapshot
    fn store_snapshot(&self, snapshot: ModelSnapshot) -> Result<(), Error>;
    
    /// Retrieve snapshots by time range
    fn get_snapshots_by_time_range(&self, start: i64, end: i64) -> Result<Vec<ModelSnapshot>, Error>;
}
```

### 4. Visualization Module

**Responsibility**: Render neural network state and dynamics.

**Key Components**:
- Graph visualization components
- Timeline visualization
- Heatmap components
- Animation utilities

**Interface**:
```typescript
// Interface for weight visualization
interface WeightVisualizer {
  // Render weights as a graph
  renderWeightGraph(weights: Weight[], options?: GraphOptions): void;
  
  // Render weight changes over time
  renderWeightTimeline(weights: Weight[], timeRange: TimeRange): void;
  
  // Render weight heatmap
  renderWeightHeatmap(weights: Weight[], options?: HeatmapOptions): void;
}

// Interface for gradient visualization
interface GradientVisualizer {
  // Render gradient flow through the network
  renderGradientFlow(gradients: Gradient[]): void;
  
  // Render gradient distribution
  renderGradientDistribution(gradients: Gradient[]): void;
  
  // Render gradient anomalies
  renderGradientAnomalies(anomalies: Anomaly[]): void;
}
```

### 5. Analytics Module

**Responsibility**: Provide insights and anomaly detection.

**Key Components**:
- Anomaly detection algorithms
- Trend analysis utilities
- Comparative analysis functions
- Reporting utilities

**Interface**:
```rust
/// Interface for neural network analytics
pub trait NetworkAnalytics {
    /// Analyze training progress
    fn analyze_training_progress(&self, weights: Vec<Weight>) -> Result<TrainingProgress, Error>;
    
    /// Detect anomalies in training
    fn detect_anomalies(&self, weights: Vec<Weight>, gradients: Vec<Gradient>) -> Result<Vec<Anomaly>, Error>;
    
    /// Compare model snapshots
    fn compare_snapshots(&self, snapshot1: ModelSnapshot, snapshot2: ModelSnapshot) -> Result<SnapshotDiff, Error>;
    
    /// Generate training report
    fn generate_report(&self, timeRange: TimeRange) -> Result<TrainingReport, Error>;
}
```

## Cross-Cutting Concerns

### 1. Configuration Module

**Responsibility**: Manage system configuration.

**Interface**:
```rust
/// Interface for configuration management
pub trait ConfigManager {
    /// Get a configuration value
    fn get<T: DeserializeOwned>(&self, key: &str) -> Result<T, Error>;
    
    /// Set a configuration value
    fn set<T: Serialize>(&self, key: &str, value: T) -> Result<(), Error>;
    
    /// Load configuration from a file
    fn load_from_file(&self, path: &str) -> Result<(), Error>;
    
    /// Save configuration to a file
    fn save_to_file(&self, path: &str) -> Result<(), Error>;
}
```

### 2. Logging and Monitoring Module

**Responsibility**: Provide logging and monitoring capabilities.

**Interface**:
```rust
/// Interface for logging and monitoring
pub trait Logger {
    /// Log an informational message
    fn info(&self, message: &str) -> Result<(), Error>;
    
    /// Log a warning message
    fn warn(&self, message: &str) -> Result<(), Error>;
    
    /// Log an error message
    fn error(&self, message: &str) -> Result<(), Error>;
    
    /// Log a metric
    fn log_metric(&self, name: &str, value: f64) -> Result<(), Error>;
}
```

### 3. Security Module

**Responsibility**: Manage authentication and authorization.

**Interface**:
```rust
/// Interface for security management
pub trait SecurityManager {
    /// Authenticate a user
    fn authenticate(&self, username: &str, password: &str) -> Result<AuthToken, Error>;
    
    /// Authorize an action
    fn authorize(&self, token: &AuthToken, action: &str) -> Result<bool, Error>;
    
    /// Generate a new token
    fn generate_token(&self, user_id: &str) -> Result<AuthToken, Error>;
    
    /// Validate a token
    fn validate_token(&self, token: &AuthToken) -> Result<bool, Error>;
}
```

## Module Interaction Patterns

### 1. Dependency Injection

Modules should receive their dependencies rather than creating them:

```rust
// Bad: Creating dependencies directly
pub struct WeightProcessorImpl {
    storage: StateStorageImpl,
    logger: LoggerImpl,
}

// Good: Receiving dependencies through constructor
pub struct WeightProcessorImpl<S: StateStorage, L: Logger> {
    storage: S,
    logger: L,
}

impl<S: StateStorage, L: Logger> WeightProcessorImpl<S, L> {
    pub fn new(storage: S, logger: L) -> Self {
        Self { storage, logger }
    }
}
```

### 2. Event-Based Communication

Modules should communicate through events when appropriate:

```rust
// Event definition
pub struct WeightChangedEvent {
    pub weight_id: String,
    pub old_value: f64,
    pub new_value: f64,
    pub timestamp: i64,
}

// Event publisher
pub trait EventPublisher {
    fn publish<T: Event>(&self, event: T) -> Result<(), Error>;
}

// Event subscriber
pub trait EventSubscriber<T: Event> {
    fn on_event(&self, event: T) -> Result<(), Error>;
}
```

### 3. Adapter Pattern

Use adapters to convert between module interfaces:

```rust
// External service with incompatible interface
pub struct ExternalGradientService {
    pub fn get_gradients(&self) -> Vec<ExternalGradient> {
        // ...
    }
}

// Adapter to convert to our interface
pub struct GradientServiceAdapter {
    external_service: ExternalGradientService,
}

impl GradientAnalyzer for GradientServiceAdapter {
    fn detect_gradient_anomalies(&self, _gradients: Vec<Gradient>) -> Result<Vec<Anomaly>, Error> {
        let external_gradients = self.external_service.get_gradients();
        let converted_gradients = external_gradients.into_iter()
            .map(convert_gradient)
            .collect();
        
        // Use converted gradients with our logic
        // ...
        
        Ok(vec![])
    }
    
    // ...
}
```

## Example Module Implementation

### Data Capture Module Example

```python
from typing import List, Dict, Optional
import torch
import time
import uuid
import queue
import threading
import requests

class CaptureConfig:
    def __init__(self, 
                 sig_level: float = 0.1,
                 batch_interval: float = 0.5,
                 endpoint: str = "http://localhost:5000/update_weight"):
        self.sig_level = sig_level
        self.batch_interval = batch_interval
        self.endpoint = endpoint

class CapturedData:
    def __init__(self, 
                 id: str,
                 value: float,
                 delta: float,
                 timestamp: int,
                 origin_sample: str,
                 agent_id: Optional[str] = None):
        self.id = id
        self.value = value
        self.delta = delta
        self.timestamp = timestamp
        self.origin_sample = origin_sample
        self.agent_id = agent_id

class NeuroCaptureImpl:
    """Implementation of neural network state capture."""
    
    def __init__(self, config: CaptureConfig):
        self.config = config
        self.model = None
        self.q = queue.SimpleQueue()
        self.running = False
        self.thread = None
        
    def attach_to_model(self, model: torch.nn.Module) -> None:
        """Attach capture hooks to a PyTorch model."""
        self.model = model
        self._install_hooks()
        self.running = True
        self.thread = threading.Thread(target=self._drain_queue, daemon=True)
        self.thread.start()
        
    def detach_from_model(self) -> None:
        """Remove capture hooks from the model."""
        if self.model:
            # Remove hooks
            for handle in self.hook_handles:
                handle.remove()
            self.hook_handles = []
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)
            self.model = None
        
    def set_capture_config(self, config: CaptureConfig) -> None:
        """Configure what data to capture and at what frequency."""
        self.config = config
        
    def get_captured_data(self) -> List[CapturedData]:
        """Get the currently captured data."""
        # This would typically return data from a buffer or cache
        # For simplicity, we'll return an empty list
        return []
        
    def _install_hooks(self) -> None:
        """Install hooks on model parameters."""
        self.hook_handles = []
        for name, param in self.model.named_parameters():
            handle = param.register_hook(
                lambda grad, n=name, p=param: self._capture_gradient(n, p, grad)
            )
            self.hook_handles.append(handle)
    
    def _capture_gradient(self, name: str, param: torch.nn.Parameter, grad: torch.Tensor) -> None:
        """Capture gradient information during backpropagation."""
        new_val = param.data.cpu().float().mean().item()
        old_val = new_val - grad.mean().item()
        
        # Only capture significant changes
        if abs(new_val - old_val) < self.config.sig_level:
            return
            
        # Enqueue the captured data
        self.q.put(CapturedData(
            id=name,
            value=new_val,
            delta=new_val - old_val,
            timestamp=int(time.time() * 1000),
            origin_sample=str(uuid.uuid4()),
            agent_id=None
        ))
    
    def _drain_queue(self) -> None:
        """Drain the queue and send data to the endpoint."""
        while self.running:
            try:
                # Wait for a short time to batch updates
                time.sleep(self.config.batch_interval)
                
                # Collect all available updates
                batch = []
                while not self.q.empty():
                    batch.append(self.q.get())
                
                # Send the batch if not empty
                if batch:
                    self._send_batch(batch)
            except Exception as e:
                print(f"Error in drain queue: {e}")
    
    def _send_batch(self, batch: List[CapturedData]) -> None:
        """Send a batch of captured data to the endpoint."""
        try:
            # Convert to dictionaries for JSON serialization
            data = [vars(item) for item in batch]
            
            # Send to the endpoint
            requests.post(self.config.endpoint, json=data, timeout=1.0)
        except Exception as e:
            print(f"Error sending batch: {e}")
```

### Data Processing Module Example

```rust
use serde::{Serialize, Deserialize};
use std::collections::HashMap;

#[derive(Clone, Serialize, Deserialize)]
pub struct Weight {
    pub id: String,
    pub value: f64,
    pub delta: f64,
    pub timestamp: i64,
    pub origin_sample: String,
    pub agent_id: Option<String>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct ModelSnapshot {
    pub id: String,
    pub timestamp: i64,
    pub affected_weights: Vec<String>,
    pub reason: String,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct Anomaly {
    pub id: String,
    pub weight_id: String,
    pub anomaly_type: String,
    pub severity: f64,
    pub timestamp: i64,
    pub description: String,
}

pub trait StateStorage {
    fn store_weight(&self, weight: Weight) -> Result<(), Error>;
    fn get_weights_by_layer(&self, layer_id: &str) -> Result<Vec<Weight>, Error>;
    fn get_weights_by_time_range(&self, start: i64, end: i64) -> Result<Vec<Weight>, Error>;
    fn store_snapshot(&self, snapshot: ModelSnapshot) -> Result<(), Error>;
    fn get_snapshots_by_time_range(&self, start: i64, end: i64) -> Result<Vec<ModelSnapshot>, Error>;
}

pub trait Logger {
    fn info(&self, message: &str) -> Result<(), Error>;
    fn warn(&self, message: &str) -> Result<(), Error>;
    fn error(&self, message: &str) -> Result<(), Error>;
    fn log_metric(&self, name: &str, value: f64) -> Result<(), Error>;
}

pub struct WeightProcessorImpl<S: StateStorage, L: Logger> {
    storage: S,
    logger: L,
    significance_threshold: f64,
    layer_cache: HashMap<String, Vec<Weight>>,
}

impl<S: StateStorage, L: Logger> WeightProcessorImpl<S, L> {
    pub fn new(storage: S, logger: L, significance_threshold: f64) -> Self {
        Self {
            storage,
            logger,
            significance_threshold,
            layer_cache: HashMap::new(),
        }
    }
    
    fn get_layer_id_from_weight_id(&self, weight_id: &str) -> String {
        // Extract layer ID from weight ID (e.g., "layer1.w1" -> "layer1")
        weight_id.split('.').next().unwrap_or("unknown").to_string()
    }
}

impl<S: StateStorage, L: Logger> WeightProcessor for WeightProcessorImpl<S, L> {
    fn process_weight_batch(&self, updates: Vec<WeightUpdate>) -> Result<(), Error> {
        self.logger.info(&format!("Processing batch of {} weight updates", updates.len()))?;
        
        for update in updates {
            let weight = Weight {
                id: update.id.clone(),
                value: update.value,
                delta: update.delta,
                timestamp: update.timestamp,
                origin_sample: update.origin_sample.clone(),
                agent_id: update.agent_id.clone(),
            };
            
            // Store the weight
            self.storage.store_weight(weight.clone())?;
            
            // Update cache
            let layer_id = self.get_layer_id_from_weight_id(&weight.id);
            let layer_weights = self.layer_cache.entry(layer_id.clone()).or_insert_with(Vec::new);
            layer_weights.push(weight.clone());
            
            // Log significant changes
            if weight.delta.abs() > self.significance_threshold {
                self.logger.info(&format!(
                    "Significant weight change detected: {} (delta: {})",
                    weight.id, weight.delta
                ))?;
                
                self.logger.log_metric(&format!("weight_change.{}", weight.id), weight.delta)?;
            }
        }
        
        Ok(())
    }
    
    fn detect_significant_changes(&self, threshold: f64) -> Result<Vec<Weight>, Error> {
        self.logger.info(&format!("Detecting significant changes with threshold {}", threshold))?;
        
        let mut significant_weights = Vec::new();
        
        for (layer_id, weights) in &self.layer_cache {
            for weight in weights {
                if weight.delta.abs() >= threshold {
                    significant_weights.push(weight.clone());
                }
            }
        }
        
        self.logger.info(&format!("Found {} significant weight changes", significant_weights.len()))?;
        
        Ok(significant_weights)
    }
    
    fn create_model_snapshot(&self, reason: String) -> Result<ModelSnapshot, Error> {
        self.logger.info(&format!("Creating model snapshot: {}", reason))?;
        
        let timestamp = chrono::Utc::now().timestamp_millis();
        let snapshot_id = format!("snapshot_{}", timestamp);
        
        // Collect affected weights (for simplicity, we'll use all weights)
        let mut affected_weights = Vec::new();
        for (_, weights) in &self.layer_cache {
            for weight in weights {
                affected_weights.push(weight.id.clone());
            }
        }
        
        let snapshot = ModelSnapshot {
            id: snapshot_id,
            timestamp,
            affected_weights,
            reason,
        };
        
        // Store the snapshot
        self.storage.store_snapshot(snapshot.clone())?;
        
        self.logger.info(&format!("Created model snapshot: {}", snapshot.id))?;
        
        Ok(snapshot)
    }
}
```

## Conclusion

Following these modular architecture principles ensures that:

1. The system is maintainable and extensible
2. Components can be developed and tested independently
3. Changes in one module don't ripple through the entire system
4. The system can evolve over time without complete rewrites
5. New developers can understand and contribute to the system more easily
