//! Test utilities for the NeuroSpacetime system.
//!
//! This crate provides utilities for testing the NeuroSpacetime system.

use std::sync::{Arc, Mutex};
use std::collections::HashMap;

/// Mock SpacetimeDB context for testing reducers.
pub struct MockContext {
    /// Mock database for testing.
    db: MockDatabase,
    /// Mock parameters for testing.
    params: HashMap<String, String>,
    /// Mock events for testing.
    events: Arc<Mutex<Vec<(String, String)>>>,
}

impl MockContext {
    /// Create a new mock context.
    pub fn new() -> Self {
        Self {
            db: MockDatabase::new(),
            params: HashMap::new(),
            events: Arc::new(Mutex::new(Vec::new())),
        }
    }
    
    /// Get the mock database.
    pub fn db(&self) -> &MockDatabase {
        &self.db
    }
    
    /// Set a parameter value.
    pub fn set_param(&mut self, key: &str, value: &str) {
        self.params.insert(key.to_string(), value.to_string());
    }
    
    /// Get a parameter value.
    pub fn param<T: std::str::FromStr>(&self, key: &str, default: T) -> T {
        self.params
            .get(key)
            .and_then(|v| v.parse::<T>().ok())
            .unwrap_or(default)
    }
    
    /// Emit an event.
    pub fn emit<T: serde::Serialize>(&self, event_type: &str, payload: &T) -> Result<(), String> {
        let payload_json = serde_json::to_string(payload).map_err(|e| e.to_string())?;
        let mut events = self.events.lock().map_err(|e| e.to_string())?;
        events.push((event_type.to_string(), payload_json));
        Ok(())
    }
    
    /// Get all emitted events.
    pub fn get_events(&self) -> Result<Vec<(String, String)>, String> {
        let events = self.events.lock().map_err(|e| e.to_string())?;
        Ok(events.clone())
    }
}

/// Mock database for testing.
pub struct MockDatabase {
    /// Stored entities.
    entities: Arc<Mutex<HashMap<String, HashMap<String, String>>>>,
}

impl MockDatabase {
    /// Create a new mock database.
    pub fn new() -> Self {
        Self {
            entities: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    /// Set an entity in the database.
    pub fn set<T: serde::Serialize>(&self, entity: T) -> Result<(), String> {
        let entity_json = serde_json::to_string(&entity).map_err(|e| e.to_string())?;
        let entity_value: serde_json::Value = serde_json::from_str(&entity_json).map_err(|e| e.to_string())?;
        
        if let serde_json::Value::Object(obj) = entity_value {
            // Extract entity type and ID
            let type_name = std::any::type_name::<T>().split("::").last().unwrap_or("Unknown");
            let id = obj.get("id").and_then(|v| v.as_str()).unwrap_or("unknown");
            
            let mut entities = self.entities.lock().map_err(|e| e.to_string())?;
            let type_entities = entities.entry(type_name.to_string()).or_insert_with(HashMap::new);
            type_entities.insert(id.to_string(), entity_json);
        }
        
        Ok(())
    }
    
    /// Get an entity from the database.
    pub fn get<T: serde::de::DeserializeOwned>(&self, id: &str) -> Result<Option<T>, String> {
        let type_name = std::any::type_name::<T>().split("::").last().unwrap_or("Unknown");
        let entities = self.entities.lock().map_err(|e| e.to_string())?;
        
        if let Some(type_entities) = entities.get(type_name) {
            if let Some(entity_json) = type_entities.get(id) {
                let entity = serde_json::from_str::<T>(entity_json).map_err(|e| e.to_string())?;
                return Ok(Some(entity));
            }
        }
        
        Ok(None)
    }
    
    /// Scan entities by an index.
    pub fn scan_index<T: serde::de::DeserializeOwned, K: AsRef<str>>(
        &self,
        _index_name: &str,
        key: K,
    ) -> Result<Vec<Result<T, String>>, String> {
        let type_name = std::any::type_name::<T>().split("::").last().unwrap_or("Unknown");
        let entities = self.entities.lock().map_err(|e| e.to_string())?;
        
        let mut results = Vec::new();
        
        if let Some(type_entities) = entities.get(type_name) {
            for (_, entity_json) in type_entities.iter() {
                // Simple prefix matching for testing
                if entity_json.contains(&format!("\"{}.", key.as_ref())) {
                    let entity = serde_json::from_str::<T>(entity_json).map_err(|e| e.to_string())?;
                    results.push(Ok(entity));
                }
            }
        }
        
        Ok(results)
    }
}
