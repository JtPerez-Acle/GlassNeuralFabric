//! NeuroSpacetime Reducers
//!
//! This crate provides the SpacetimeDB reducers for the NeuroSpacetime system.
//! It defines the database schema and reducer functions for processing neural
//! network state updates. It follows a modular architecture with clear separation
//! of concerns and is developed using Test Driven Development principles.

// Core modules
pub mod models;
pub mod reducers;
pub mod error;

// Support modules
pub mod storage;
pub mod logging;
pub mod weight_processor;

#[cfg(test)]
mod tests;

// Re-export key types for convenience
pub use models::{Weight, WeightUpdate, ModelSnapshot};
pub use reducers::{update_weight, create_snapshot};
pub use error::Error;
pub use weight_processor::WeightProcessor;
pub use storage::StateStorage;
pub use logging::Logger;

// We'll use the spacetimedb-sdk for integration instead of the spacetimedb crate
