//! Tests for the SpacetimeDB schema definitions.

use crate::models::{Weight, ModelSnapshot};
use spacetimedb::table::TableType;

#[test]
fn test_weight_table_definition() {
    // Verify that Weight implements TableType
    assert!(Weight::table_name() == "weight");
    
    // Verify primary key
    let primary_key_columns = Weight::primary_key_column_names();
    assert_eq!(primary_key_columns.len(), 1);
    assert_eq!(primary_key_columns[0], "id");
    
    // Verify indexes
    let indexes = Weight::indexes();
    assert!(indexes.iter().any(|idx| idx.name == "by_time"));
    assert!(indexes.iter().any(|idx| idx.name == "by_layer"));
}

#[test]
fn test_model_snapshot_table_definition() {
    // Verify that ModelSnapshot implements TableType
    assert!(ModelSnapshot::table_name() == "model_snapshot");
    
    // Verify primary key
    let primary_key_columns = ModelSnapshot::primary_key_column_names();
    assert_eq!(primary_key_columns.len(), 1);
    assert_eq!(primary_key_columns[0], "id");
}

#[test]
fn test_weight_serialization() {
    // Create a Weight instance
    let weight = Weight {
        id: "layer1.w1".to_string(),
        value: 0.5,
        delta: 0.1,
        timestamp: 1625097600000,
        origin_sample: "sample1".to_string(),
        agent_id: None,
    };
    
    // Serialize to bytes
    let bytes = weight.to_bytes().unwrap();
    
    // Deserialize from bytes
    let deserialized = Weight::from_bytes(&bytes).unwrap();
    
    // Verify fields match
    assert_eq!(deserialized.id, weight.id);
    assert_eq!(deserialized.value, weight.value);
    assert_eq!(deserialized.delta, weight.delta);
    assert_eq!(deserialized.timestamp, weight.timestamp);
    assert_eq!(deserialized.origin_sample, weight.origin_sample);
    assert_eq!(deserialized.agent_id, weight.agent_id);
}

#[test]
fn test_model_snapshot_serialization() {
    // Create a ModelSnapshot instance
    let snapshot = ModelSnapshot {
        id: "snapshot1".to_string(),
        timestamp: 1625097600000,
        affected_weights: vec!["layer1.w1".to_string(), "layer1.w2".to_string()],
        reason: "Test snapshot".to_string(),
    };
    
    // Serialize to bytes
    let bytes = snapshot.to_bytes().unwrap();
    
    // Deserialize from bytes
    let deserialized = ModelSnapshot::from_bytes(&bytes).unwrap();
    
    // Verify fields match
    assert_eq!(deserialized.id, snapshot.id);
    assert_eq!(deserialized.timestamp, snapshot.timestamp);
    assert_eq!(deserialized.affected_weights, snapshot.affected_weights);
    assert_eq!(deserialized.reason, snapshot.reason);
}
