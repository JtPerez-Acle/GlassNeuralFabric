//! Reducers for the NeuroSpacetime system.
//!
//! This module defines the reducer functions that process updates
//! to the neural network state.

use chrono::Utc;
use uuid::Uuid;
use log;

use crate::models::{Weight, ModelSnapshot, UpdateInput, SnapshotInput};
use crate::error::Error;
use crate::storage::StateStorage;

/// Update a weight in the database.
///
/// This function processes a weight update from the neural network.
/// It calculates the delta from the previous value (if any) and
/// stores the updated weight in the database.
pub fn update_weight<S: StateStorage>(
    storage: &S,
    input: UpdateInput,
    significance_threshold: f64
) -> Result<(), Error> {
    // Get previous weight if it exists
    let prev_weight = storage.get_weight_by_id(&input.id)?;

    // Calculate delta
    let delta = match prev_weight {
        Some(w) => input.value - w.value,
        None => 0.0,
    };

    // Create new weight record
    let weight = Weight {
        id: input.id,
        value: input.value,
        delta,
        timestamp: input.timestamp,
        origin_sample: input.origin_sample,
        agent_id: input.agent_id,
    };

    // Store the weight
    storage.store_weight(weight.clone())?;

    // Log significant changes
    if delta.abs() > significance_threshold {
        log::info!("Significant weight change detected: {} (delta: {})", weight.id, weight.delta);
    }

    Ok(())
}

/// Create a snapshot of the model.
///
/// This function creates a snapshot of the model at a specific point in time.
/// It records the affected weights and the reason for creating the snapshot.
pub fn create_snapshot<S: StateStorage>(
    storage: &S,
    input: SnapshotInput
) -> Result<String, Error> {
    // Generate a unique ID for the snapshot
    let snapshot_id = Uuid::new_v4().to_string();

    // Create the snapshot
    let snapshot = ModelSnapshot {
        id: snapshot_id.clone(),
        timestamp: Utc::now().timestamp_millis(),
        affected_weights: input.affected_weights,
        reason: input.reason,
    };

    // Store the snapshot
    storage.store_snapshot(snapshot)?;

    // Return the snapshot ID
    Ok(snapshot_id)
}
