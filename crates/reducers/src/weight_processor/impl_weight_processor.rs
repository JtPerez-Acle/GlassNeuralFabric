//! Implementation of the WeightProcessor trait.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use chrono::Utc;
use uuid::Uuid;

use crate::models::{Weight, WeightUpdate, ModelSnapshot};
use crate::storage::StateStorage;
use crate::logging::Logger;
use crate::error::Error;
use crate::weight_processor::WeightProcessor;

/// Implementation of the WeightProcessor trait
pub struct WeightProcessorImpl<S: StateStorage, L: Logger> {
    /// Storage for weights and snapshots
    storage: S,
    
    /// Logger for logging and monitoring
    logger: L,
    
    /// Threshold for significant weight changes
    significance_threshold: f64,
    
    /// Cache of weights by layer
    layer_cache: Arc<Mutex<HashMap<String, Vec<Weight>>>>,
}

impl<S: StateStorage, L: Logger> WeightProcessorImpl<S, L> {
    /// Create a new weight processor
    pub fn new(storage: S, logger: L, significance_threshold: f64) -> Self {
        Self {
            storage,
            logger,
            significance_threshold,
            layer_cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    /// Extract layer ID from weight ID
    fn get_layer_id_from_weight_id(&self, weight_id: &str) -> String {
        weight_id.split('.').next().unwrap_or("unknown").to_string()
    }
    
    /// Update the layer cache with a new weight
    fn update_layer_cache(&self, weight: &Weight) -> Result<(), Error> {
        let layer_id = self.get_layer_id_from_weight_id(&weight.id);
        let mut cache = self.layer_cache.lock().map_err(|_| Error::LockError)?;
        
        let layer_weights = cache.entry(layer_id).or_insert_with(Vec::new);
        
        // Remove any existing weight with the same ID
        layer_weights.retain(|w| w.id != weight.id);
        
        // Add the new weight
        layer_weights.push(weight.clone());
        
        Ok(())
    }
}

impl<S: StateStorage, L: Logger> WeightProcessor for WeightProcessorImpl<S, L> {
    fn process_weight_batch(&self, updates: Vec<WeightUpdate>) -> Result<(), Error> {
        self.logger.info(&format!("Processing batch of {} weight updates", updates.len()))?;
        
        for update in updates {
            // Get previous weight to calculate delta
            let prev_weight = self.storage.get_weight_by_id(&update.id)?;
            let delta = match prev_weight {
                Some(w) => update.value - w.value,
                None => 0.0, // First update, no previous value
            };
            
            // Create new weight with calculated delta
            let weight = Weight {
                id: update.id.clone(),
                value: update.value,
                delta,
                timestamp: update.timestamp,
                origin_sample: update.origin_sample.clone(),
                agent_id: update.agent_id.clone(),
            };
            
            // Store the weight
            self.storage.store_weight(weight.clone())?;
            
            // Update cache
            self.update_layer_cache(&weight)?;
            
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
        
        let cache = self.layer_cache.lock().map_err(|_| Error::LockError)?;
        let mut significant_weights = Vec::new();
        
        for (_, weights) in cache.iter() {
            for weight in weights {
                if weight.delta.abs() >= threshold {
                    significant_weights.push(weight.clone());
                }
            }
        }
        
        // Sort by delta magnitude (descending)
        significant_weights.sort_by(|a, b| b.delta.abs().partial_cmp(&a.delta.abs()).unwrap());
        
        self.logger.info(&format!("Found {} significant weight changes", significant_weights.len()))?;
        
        Ok(significant_weights)
    }
    
    fn create_model_snapshot(&self, reason: String) -> Result<ModelSnapshot, Error> {
        self.logger.info(&format!("Creating model snapshot: {}", reason))?;
        
        let timestamp = Utc::now().timestamp_millis();
        let snapshot_id = format!("snapshot_{}", Uuid::new_v4());
        
        // Collect affected weights
        let cache = self.layer_cache.lock().map_err(|_| Error::LockError)?;
        let mut affected_weights = Vec::new();
        
        for (_, weights) in cache.iter() {
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
