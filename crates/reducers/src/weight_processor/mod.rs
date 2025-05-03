//! Weight processor module for the NeuroSpacetime system.

mod impl_weight_processor;

pub use impl_weight_processor::WeightProcessorImpl;

use crate::models::{Weight, WeightUpdate, ModelSnapshot};
use crate::error::Error;

/// Interface for weight processing
pub trait WeightProcessor {
    /// Process a batch of weight updates
    fn process_weight_batch(&self, updates: Vec<WeightUpdate>) -> Result<(), Error>;
    
    /// Detect significant changes in weights
    fn detect_significant_changes(&self, threshold: f64) -> Result<Vec<Weight>, Error>;
    
    /// Create a snapshot of the current model state
    fn create_model_snapshot(&self, reason: String) -> Result<ModelSnapshot, Error>;
}
