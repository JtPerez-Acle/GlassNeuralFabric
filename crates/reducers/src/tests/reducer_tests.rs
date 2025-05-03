//! Tests for the SpacetimeDB reducers.

use crate::models::{Weight, ModelSnapshot};
use crate::reducers::{update_weight, create_snapshot, UpdateInput, SnapshotInput};
use crate::error::Error;

use spacetimedb::ReducerContext;
use spacetimedb::test_utils::{MockReducerContext, MockTableHandle};

#[test]
fn test_update_weight_new_weight() {
    // Arrange
    let mut ctx = MockReducerContext::new();
    let weight_table = MockTableHandle::<Weight>::new();
    ctx.expect_db().returns(|name| {
        assert_eq!(name, "weight");
        weight_table.clone()
    });
    
    // No existing weight with this ID
    weight_table.expect_get().returns(|id| {
        assert_eq!(id, "layer1.w1");
        Ok(None)
    });
    
    // Expect insert to be called
    weight_table.expect_insert().returns(|weight| {
        assert_eq!(weight.id, "layer1.w1");
        assert_eq!(weight.value, 0.5);
        assert_eq!(weight.delta, 0.0); // No previous value, so delta is 0
        Ok(weight.clone())
    });
    
    // Input for the reducer
    let input = UpdateInput {
        id: "layer1.w1".to_string(),
        value: 0.5,
        timestamp: 1625097600000,
        origin_sample: "sample1".to_string(),
        agent_id: None,
    };
    
    // Act
    let result = update_weight(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
}

#[test]
fn test_update_weight_existing_weight() {
    // Arrange
    let mut ctx = MockReducerContext::new();
    let weight_table = MockTableHandle::<Weight>::new();
    ctx.expect_db().returns(|name| {
        assert_eq!(name, "weight");
        weight_table.clone()
    });
    
    // Existing weight with this ID
    let existing_weight = Weight {
        id: "layer1.w1".to_string(),
        value: 0.3,
        delta: 0.0,
        timestamp: 1625097500000,
        origin_sample: "sample0".to_string(),
        agent_id: None,
    };
    
    weight_table.expect_get().returns(|id| {
        assert_eq!(id, "layer1.w1");
        Ok(Some(existing_weight.clone()))
    });
    
    // Expect insert to be called with updated weight
    weight_table.expect_insert().returns(|weight| {
        assert_eq!(weight.id, "layer1.w1");
        assert_eq!(weight.value, 0.5);
        assert_eq!(weight.delta, 0.2); // 0.5 - 0.3 = 0.2
        Ok(weight.clone())
    });
    
    // Input for the reducer
    let input = UpdateInput {
        id: "layer1.w1".to_string(),
        value: 0.5,
        timestamp: 1625097600000,
        origin_sample: "sample1".to_string(),
        agent_id: None,
    };
    
    // Act
    let result = update_weight(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
}

#[test]
fn test_update_weight_significant_change() {
    // Arrange
    let mut ctx = MockReducerContext::new();
    let weight_table = MockTableHandle::<Weight>::new();
    ctx.expect_db().returns(|name| {
        assert_eq!(name, "weight");
        weight_table.clone()
    });
    
    // Existing weight with this ID
    let existing_weight = Weight {
        id: "layer1.w1".to_string(),
        value: 0.3,
        delta: 0.0,
        timestamp: 1625097500000,
        origin_sample: "sample0".to_string(),
        agent_id: None,
    };
    
    weight_table.expect_get().returns(|id| {
        assert_eq!(id, "layer1.w1");
        Ok(Some(existing_weight.clone()))
    });
    
    // Expect insert to be called with updated weight
    weight_table.expect_insert().returns(|weight| {
        assert_eq!(weight.id, "layer1.w1");
        assert_eq!(weight.value, 0.8);
        assert_eq!(weight.delta, 0.5); // 0.8 - 0.3 = 0.5 (significant)
        Ok(weight.clone())
    });
    
    // Expect log to be called for significant change
    ctx.expect_log().returns(|level, message| {
        assert_eq!(level, "info");
        assert!(message.contains("Significant weight change detected"));
        Ok(())
    });
    
    // Input for the reducer with significant change
    let input = UpdateInput {
        id: "layer1.w1".to_string(),
        value: 0.8, // Big change from 0.3
        timestamp: 1625097600000,
        origin_sample: "sample1".to_string(),
        agent_id: None,
    };
    
    // Act
    let result = update_weight(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
}

#[test]
fn test_create_snapshot() {
    // Arrange
    let mut ctx = MockReducerContext::new();
    let snapshot_table = MockTableHandle::<ModelSnapshot>::new();
    ctx.expect_db().returns(|name| {
        assert_eq!(name, "model_snapshot");
        snapshot_table.clone()
    });
    
    // Expect insert to be called
    snapshot_table.expect_insert().returns(|snapshot| {
        assert_eq!(snapshot.reason, "Test snapshot");
        assert_eq!(snapshot.affected_weights.len(), 2);
        assert!(snapshot.affected_weights.contains(&"layer1.w1".to_string()));
        assert!(snapshot.affected_weights.contains(&"layer1.w2".to_string()));
        Ok(snapshot.clone())
    });
    
    // Input for the reducer
    let input = SnapshotInput {
        reason: "Test snapshot".to_string(),
        affected_weights: vec!["layer1.w1".to_string(), "layer1.w2".to_string()],
    };
    
    // Act
    let result = create_snapshot(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
    
    // Verify the snapshot ID is a valid UUID
    let snapshot_id = result.unwrap();
    assert!(uuid::Uuid::parse_str(&snapshot_id).is_ok());
}
