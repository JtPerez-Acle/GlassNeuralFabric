//! Models for the NeuroSpacetime system.
//!
//! This module defines the data models used in the system, including
//! the SpacetimeDB table definitions.

use serde::{Serialize, Deserialize};

/// Weight represents a single weight in a neural network.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Weight {
    /// Unique identifier for the weight (e.g., "layer1.weight.0.1")
    pub id: String,

    /// Current value of the weight
    pub value: f64,

    /// Change in value since the last update
    pub delta: f64,

    /// Timestamp of the update (milliseconds since epoch)
    pub timestamp: i64,

    /// Identifier of the sample that triggered this update
    pub origin_sample: String,

    /// Optional identifier of the agent that made the update
    pub agent_id: Option<String>,
}

/// ModelSnapshot represents a snapshot of the model at a specific point in time.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelSnapshot {
    /// Unique identifier for the snapshot
    pub id: String,

    /// Timestamp of the snapshot (milliseconds since epoch)
    pub timestamp: i64,

    /// List of weight IDs affected by this snapshot
    pub affected_weights: Vec<String>,

    /// Reason for creating the snapshot
    pub reason: String,
}

/// Weight update from the neural network.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeightUpdate {
    /// Unique identifier for the weight
    pub id: String,

    /// New value of the weight
    pub value: f64,

    /// Timestamp of the update (milliseconds since epoch)
    pub timestamp: i64,

    /// Identifier of the sample that triggered this update
    pub origin_sample: String,

    /// Optional identifier of the agent that made the update
    pub agent_id: Option<String>,
}

/// Input for the update_weight reducer.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateInput {
    /// Unique identifier for the weight
    pub id: String,

    /// New value of the weight
    pub value: f64,

    /// Timestamp of the update (milliseconds since epoch)
    pub timestamp: i64,

    /// Identifier of the sample that triggered this update
    pub origin_sample: String,

    /// Optional identifier of the agent that made the update
    pub agent_id: Option<String>,
}

/// Input for the create_snapshot reducer.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotInput {
    /// Reason for creating the snapshot
    pub reason: String,

    /// List of weight IDs affected by this snapshot
    pub affected_weights: Vec<String>,
}
