//! Error types for the NeuroSpacetime system.

use std::fmt;
use std::error;

/// Error type for the NeuroSpacetime system
#[derive(Debug)]
pub enum Error {
    /// Error accessing the database
    DatabaseError(String),
    
    /// Error serializing or deserializing data
    SerializationError(String),
    
    /// Error with invalid input
    InvalidInput(String),
    
    /// Error with internal state
    InternalError(String),
    
    /// Error acquiring a lock
    LockError,
    
    /// Error with network communication
    NetworkError(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::DatabaseError(msg) => write!(f, "Database error: {}", msg),
            Error::SerializationError(msg) => write!(f, "Serialization error: {}", msg),
            Error::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            Error::InternalError(msg) => write!(f, "Internal error: {}", msg),
            Error::LockError => write!(f, "Lock acquisition failed"),
            Error::NetworkError(msg) => write!(f, "Network error: {}", msg),
        }
    }
}

impl error::Error for Error {}
