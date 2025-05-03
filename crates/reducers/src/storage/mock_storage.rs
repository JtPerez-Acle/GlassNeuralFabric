//! Mock implementation of the StateStorage trait for testing.

use std::sync::{Arc, Mutex};
use std::clone::Clone;

use crate::models::{Weight, ModelSnapshot};
use crate::storage::StateStorage;
use crate::error::Error;

/// Mock implementation of StateStorage for testing
#[derive(Clone)]
pub struct MockStateStorage {
    /// Stored weights
    weights: Arc<Mutex<Vec<Weight>>>,
    /// Stored snapshots
    snapshots: Arc<Mutex<Vec<ModelSnapshot>>>,
}

impl MockStateStorage {
    /// Create a new mock storage
    pub fn new() -> Self {
        Self {
            weights: Arc::new(Mutex::new(Vec::new())),
            snapshots: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Get all stored weights (for testing)
    pub fn get_all_weights(&self) -> Result<Vec<Weight>, Error> {
        let weights = self.weights.lock().map_err(|_| Error::LockError)?;
        Ok(weights.clone())
    }

    /// Get all stored snapshots (for testing)
    pub fn get_all_snapshots(&self) -> Result<Vec<ModelSnapshot>, Error> {
        let snapshots = self.snapshots.lock().map_err(|_| Error::LockError)?;
        Ok(snapshots.clone())
    }
}

impl StateStorage for MockStateStorage {
    fn store_weight(&self, weight: Weight) -> Result<(), Error> {
        let mut weights = self.weights.lock().map_err(|_| Error::LockError)?;
        weights.push(weight);
        Ok(())
    }

    fn get_weights_by_layer(&self, layer_id: &str) -> Result<Vec<Weight>, Error> {
        let weights = self.weights.lock().map_err(|_| Error::LockError)?;
        let filtered = weights
            .iter()
            .filter(|w| w.id.starts_with(&format!("{}.", layer_id)))
            .cloned()
            .collect();
        Ok(filtered)
    }

    fn get_weights_by_time_range(&self, start: i64, end: i64) -> Result<Vec<Weight>, Error> {
        let weights = self.weights.lock().map_err(|_| Error::LockError)?;
        let filtered = weights
            .iter()
            .filter(|w| w.timestamp >= start && w.timestamp <= end)
            .cloned()
            .collect();
        Ok(filtered)
    }

    fn get_weight_by_id(&self, id: &str) -> Result<Option<Weight>, Error> {
        let weights = self.weights.lock().map_err(|_| Error::LockError)?;
        let weight = weights
            .iter()
            .filter(|w| w.id == id)
            .last()
            .cloned();
        Ok(weight)
    }

    fn store_snapshot(&self, snapshot: ModelSnapshot) -> Result<(), Error> {
        let mut snapshots = self.snapshots.lock().map_err(|_| Error::LockError)?;
        snapshots.push(snapshot);
        Ok(())
    }

    fn get_snapshots_by_time_range(&self, start: i64, end: i64) -> Result<Vec<ModelSnapshot>, Error> {
        let snapshots = self.snapshots.lock().map_err(|_| Error::LockError)?;
        let filtered = snapshots
            .iter()
            .filter(|s| s.timestamp >= start && s.timestamp <= end)
            .cloned()
            .collect();
        Ok(filtered)
    }

    fn get_snapshot_by_id(&self, id: &str) -> Result<Option<ModelSnapshot>, Error> {
        let snapshots = self.snapshots.lock().map_err(|_| Error::LockError)?;
        let snapshot = snapshots
            .iter()
            .find(|s| s.id == id)
            .cloned();
        Ok(snapshot)
    }
}
