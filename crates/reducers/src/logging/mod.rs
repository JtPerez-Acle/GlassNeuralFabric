//! Logging module for the NeuroSpacetime system.

mod mock_logger;

pub use mock_logger::MockLogger;

use crate::error::Error;

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
