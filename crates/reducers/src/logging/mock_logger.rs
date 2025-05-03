//! Mock implementation of the Logger trait for testing.

use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use std::clone::Clone;

use crate::logging::Logger;
use crate::error::Error;

/// Mock implementation of Logger for testing
#[derive(Clone)]
pub struct MockLogger {
    /// Stored log messages
    messages: Arc<Mutex<Vec<String>>>,
    /// Stored metrics
    metrics: Arc<Mutex<HashMap<String, f64>>>,
}

impl MockLogger {
    /// Create a new mock logger
    pub fn new() -> Self {
        Self {
            messages: Arc::new(Mutex::new(Vec::new())),
            metrics: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    /// Get all stored log messages (for testing)
    pub fn get_messages(&self) -> Vec<String> {
        let messages = self.messages.lock().unwrap();
        messages.clone()
    }
    
    /// Get all stored metrics (for testing)
    pub fn get_metrics(&self) -> HashMap<String, f64> {
        let metrics = self.metrics.lock().unwrap();
        metrics.clone()
    }
}

impl Logger for MockLogger {
    fn info(&self, message: &str) -> Result<(), Error> {
        let mut messages = self.messages.lock().map_err(|_| Error::LockError)?;
        messages.push(message.to_string());
        Ok(())
    }
    
    fn warn(&self, message: &str) -> Result<(), Error> {
        let mut messages = self.messages.lock().map_err(|_| Error::LockError)?;
        messages.push(format!("WARNING: {}", message));
        Ok(())
    }
    
    fn error(&self, message: &str) -> Result<(), Error> {
        let mut messages = self.messages.lock().map_err(|_| Error::LockError)?;
        messages.push(format!("ERROR: {}", message));
        Ok(())
    }
    
    fn log_metric(&self, name: &str, value: f64) -> Result<(), Error> {
        let mut metrics = self.metrics.lock().map_err(|_| Error::LockError)?;
        metrics.insert(name.to_string(), value);
        Ok(())
    }
}
