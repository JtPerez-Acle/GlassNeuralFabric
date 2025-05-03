//! Storage module for the NeuroSpacetime system.

mod mock_storage;

pub use mock_storage::MockStateStorage;

use crate::models::{Weight, ModelSnapshot};
use crate::error::Error;

/// Interface for neural network state storage
pub trait StateStorage {
    /// Store a weight update
    fn store_weight(&self, weight: Weight) -> Result<(), Error>;
    
    /// Retrieve weights by layer
    fn get_weights_by_layer(&self, layer_id: &str) -> Result<Vec<Weight>, Error>;
    
    /// Retrieve weights by time range
    fn get_weights_by_time_range(&self, start: i64, end: i64) -> Result<Vec<Weight>, Error>;
    
    /// Retrieve a weight by ID
    fn get_weight_by_id(&self, id: &str) -> Result<Option<Weight>, Error>;
    
    /// Store a model snapshot
    fn store_snapshot(&self, snapshot: ModelSnapshot) -> Result<(), Error>;
    
    /// Retrieve snapshots by time range
    fn get_snapshots_by_time_range(&self, start: i64, end: i64) -> Result<Vec<ModelSnapshot>, Error>;
    
    /// Retrieve a snapshot by ID
    fn get_snapshot_by_id(&self, id: &str) -> Result<Option<ModelSnapshot>, Error>;
}
