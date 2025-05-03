//! Weight Processor Demo
//!
//! This example demonstrates how to use the weight processor to:
//! 1. Process weight updates
//! 2. Detect significant changes
//! 3. Create model snapshots
//!
//! It simulates a neural network training process and shows how the
//! weight processor can be used to monitor and analyze weight changes.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use rand::Rng;

use neurospace_reducers::models::{Weight, WeightUpdate, ModelSnapshot};
use neurospace_reducers::storage::{StateStorage, MockStateStorage};
use neurospace_reducers::logging::{Logger, MockLogger};
use neurospace_reducers::weight_processor::{WeightProcessor, WeightProcessorImpl};
use neurospace_reducers::error::Error;

/// Simulates a neural network layer
struct NeuralLayer {
    name: String,
    weights: HashMap<String, f64>,
}

impl NeuralLayer {
    /// Create a new neural layer
    fn new(name: &str, weight_count: usize) -> Self {
        let mut weights = HashMap::new();
        for i in 0..weight_count {
            weights.insert(format!("{}.w{}", name, i), 0.0);
        }

        Self {
            name: name.to_string(),
            weights,
        }
    }

    /// Update weights with random changes
    fn update_weights(&mut self, learning_rate: f64) -> Vec<WeightUpdate> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64;

        let mut updates = Vec::new();
        let mut rng = rand::thread_rng();

        for (id, value) in &mut self.weights {
            // Simulate weight update with some randomness
            let change = (rng.gen::<f64>() - 0.5) * learning_rate;
            *value += change;

            // Create weight update
            let update = WeightUpdate {
                id: id.clone(),
                value: *value,
                timestamp,
                origin_sample: format!("sample_{}", timestamp),
                agent_id: None,
            };

            updates.push(update);
        }

        updates
    }
}

/// Simulates a neural network
struct NeuralNetwork {
    layers: Vec<NeuralLayer>,
}

impl NeuralNetwork {
    /// Create a new neural network
    fn new() -> Self {
        Self {
            layers: vec![
                NeuralLayer::new("layer1", 3),
                NeuralLayer::new("layer2", 2),
            ],
        }
    }

    /// Perform one training step
    fn train_step(&mut self, learning_rate: f64) -> Vec<WeightUpdate> {
        let mut all_updates = Vec::new();

        for layer in &mut self.layers {
            let updates = layer.update_weights(learning_rate);
            all_updates.extend(updates);
        }

        all_updates
    }
}

/// Custom storage implementation that prints weights and snapshots
#[derive(Clone)]
struct PrintingStorage {
    inner: MockStateStorage,
}

impl PrintingStorage {
    /// Create a new printing storage
    fn new() -> Self {
        Self {
            inner: MockStateStorage::new(),
        }
    }

    /// Print all stored weights
    fn print_all_weights(&self) -> Result<(), Error> {
        let weights = self.inner.get_all_weights()?;

        println!("\n=== Stored Weights ===");
        for weight in weights {
            println!(
                "{}: value={:.4}, delta={:.4}, timestamp={}",
                weight.id, weight.value, weight.delta, weight.timestamp
            );
        }

        Ok(())
    }

    /// Print all stored snapshots
    fn print_all_snapshots(&self) -> Result<(), Error> {
        let snapshots = self.inner.get_all_snapshots()?;

        println!("\n=== Stored Snapshots ===");
        for snapshot in snapshots {
            println!(
                "ID: {}, Reason: {}, Affected weights: {}",
                snapshot.id, snapshot.reason, snapshot.affected_weights.len()
            );
            println!("  Weights: {}", snapshot.affected_weights.join(", "));
        }

        Ok(())
    }
}

impl StateStorage for PrintingStorage {
    fn store_weight(&self, weight: Weight) -> Result<(), Error> {
        self.inner.store_weight(weight)
    }

    fn get_weights_by_layer(&self, layer_id: &str) -> Result<Vec<Weight>, Error> {
        self.inner.get_weights_by_layer(layer_id)
    }

    fn get_weights_by_time_range(&self, start: i64, end: i64) -> Result<Vec<Weight>, Error> {
        self.inner.get_weights_by_time_range(start, end)
    }

    fn get_weight_by_id(&self, id: &str) -> Result<Option<Weight>, Error> {
        self.inner.get_weight_by_id(id)
    }

    fn store_snapshot(&self, snapshot: ModelSnapshot) -> Result<(), Error> {
        println!("\n>>> Created snapshot: {} ({})", snapshot.id, snapshot.reason);
        self.inner.store_snapshot(snapshot)
    }

    fn get_snapshots_by_time_range(&self, start: i64, end: i64) -> Result<Vec<ModelSnapshot>, Error> {
        self.inner.get_snapshots_by_time_range(start, end)
    }

    fn get_snapshot_by_id(&self, id: &str) -> Result<Option<ModelSnapshot>, Error> {
        self.inner.get_snapshot_by_id(id)
    }
}

/// Custom logger that prints messages and metrics
#[derive(Clone)]
struct PrintingLogger {
    inner: MockLogger,
    metrics: Arc<Mutex<HashMap<String, f64>>>,
}

impl PrintingLogger {
    /// Create a new printing logger
    fn new() -> Self {
        Self {
            inner: MockLogger::new(),
            metrics: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Print all logged metrics
    fn print_metrics(&self) {
        let metrics = self.metrics.lock().unwrap();

        println!("\n=== Logged Metrics ===");
        for (key, value) in metrics.iter() {
            println!("{}: {:.4}", key, value);
        }
    }
}

impl Logger for PrintingLogger {
    fn info(&self, message: &str) -> Result<(), Error> {
        println!("[INFO] {}", message);
        self.inner.info(message)
    }

    fn warn(&self, message: &str) -> Result<(), Error> {
        println!("[WARN] {}", message);
        self.inner.warn(message)
    }

    fn error(&self, message: &str) -> Result<(), Error> {
        println!("[ERROR] {}", message);
        self.inner.error(message)
    }

    fn log_metric(&self, name: &str, value: f64) -> Result<(), Error> {
        println!("[METRIC] {}: {:.4}", name, value);

        let mut metrics = self.metrics.lock().map_err(|_| Error::LockError)?;
        metrics.insert(name.to_string(), value);

        self.inner.log_metric(name, value)
    }
}

fn main() -> Result<(), Error> {
    println!("=== Weight Processor Demo ===");

    // Create storage and logger
    let storage = PrintingStorage::new();
    let logger = PrintingLogger::new();

    // Create weight processor with a significance threshold of 0.2
    let processor = WeightProcessorImpl::new(
        storage.clone(),
        logger.clone(),
        0.2,
    );

    // Create a neural network
    let mut network = NeuralNetwork::new();

    // Simulate training for 5 epochs
    println!("\nSimulating neural network training...");

    for epoch in 0..5 {
        println!("\n--- Epoch {} ---", epoch + 1);

        // Use different learning rates to simulate different phases of training
        let learning_rate = match epoch {
            0 => 0.5,  // Large initial updates
            1 => 0.3,
            2 => 0.2,
            3 => 0.1,
            _ => 0.05, // Small final updates
        };

        // Perform 3 training steps per epoch
        for step in 0..3 {
            println!("Epoch {}, Step {}", epoch + 1, step + 1);

            // Get weight updates from the network
            let updates = network.train_step(learning_rate);

            // Process the updates
            processor.process_weight_batch(updates)?;

            // Sleep to simulate time passing
            thread::sleep(Duration::from_millis(100));
        }

        // Detect significant changes at the end of each epoch
        let significant_changes = processor.detect_significant_changes(0.2)?;

        println!("\nSignificant changes detected: {}", significant_changes.len());
        for weight in &significant_changes {
            println!(
                "  {}: value={:.4}, delta={:.4}",
                weight.id, weight.value, weight.delta
            );
        }

        // Create a snapshot at the end of each epoch
        processor.create_model_snapshot(format!("End of epoch {}", epoch + 1))?;
    }

    // Print final state
    storage.print_all_weights()?;
    storage.print_all_snapshots()?;
    logger.print_metrics();

    println!("\nDemo completed successfully!");

    Ok(())
}
