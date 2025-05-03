//! Tests for the weight processor module.
//!
//! These tests follow the Test Driven Development approach:
//! 1. Write a failing test
//! 2. Implement minimal code to make the test pass
//! 3. Refactor while maintaining passing tests

use crate::weight_processor::{WeightProcessor, WeightProcessorImpl};
use crate::models::WeightUpdate;
use crate::storage::MockStateStorage;
use crate::logging::MockLogger;

/// Test fixture for weight processor tests
struct WeightProcessorFixture {
    /// Mock storage for testing
    storage: MockStateStorage,
    /// Mock logger for testing
    logger: MockLogger,
    /// Processor under test
    processor: WeightProcessorImpl<MockStateStorage, MockLogger>,
}

impl WeightProcessorFixture {
    /// Create a new test fixture
    fn new() -> Self {
        let storage = MockStateStorage::new();
        let logger = MockLogger::new();
        let processor = WeightProcessorImpl::new(
            storage.clone(),
            logger.clone(),
            0.5, // significance threshold
        );

        Self {
            storage,
            logger,
            processor,
        }
    }

    /// Create a fixture with pre-populated weights
    fn with_weights() -> Self {
        let fixture = Self::new();

        // Create weight updates
        let updates = vec![
            WeightUpdate {
                id: "layer1.w1".to_string(),
                value: 0.4, // Initial value
                timestamp: 1625097500000, // Earlier timestamp
                origin_sample: "sample0".to_string(),
                agent_id: None,
            },
            WeightUpdate {
                id: "layer1.w2".to_string(),
                value: -0.1, // Initial value
                timestamp: 1625097500000, // Earlier timestamp
                origin_sample: "sample0".to_string(),
                agent_id: None,
            },
            WeightUpdate {
                id: "layer2.w1".to_string(),
                value: 0.1, // Initial value
                timestamp: 1625097500000, // Earlier timestamp
                origin_sample: "sample0".to_string(),
                agent_id: None,
            },
        ];

        // Process initial updates
        fixture.processor.process_weight_batch(updates).unwrap();

        // Create second batch of updates with deltas
        let updates2 = vec![
            WeightUpdate {
                id: "layer1.w1".to_string(),
                value: 0.5, // Delta: 0.1
                timestamp: 1625097600000,
                origin_sample: "sample1".to_string(),
                agent_id: None,
            },
            WeightUpdate {
                id: "layer1.w2".to_string(),
                value: -0.3, // Delta: -0.2
                timestamp: 1625097600000,
                origin_sample: "sample1".to_string(),
                agent_id: None,
            },
            WeightUpdate {
                id: "layer2.w1".to_string(),
                value: 0.7, // Delta: 0.6
                timestamp: 1625097600000,
                origin_sample: "sample1".to_string(),
                agent_id: None,
            },
        ];

        // Process second batch
        fixture.processor.process_weight_batch(updates2).unwrap();

        fixture
    }
}

#[test]
fn test_process_weight_batch_stores_weights() {
    // Arrange
    let fixture = WeightProcessorFixture::new();
    let updates = vec![
        WeightUpdate {
            id: "layer1.w1".to_string(),
            value: 0.5,
            timestamp: 1625097600000,
            origin_sample: "sample1".to_string(),
            agent_id: None,
        },
        WeightUpdate {
            id: "layer1.w2".to_string(),
            value: -0.3,
            timestamp: 1625097600000,
            origin_sample: "sample1".to_string(),
            agent_id: None,
        },
    ];

    // Act
    let result = fixture.processor.process_weight_batch(updates);

    // Assert
    assert!(result.is_ok());

    // Verify weights were stored
    let stored_weights = fixture.storage.get_all_weights().unwrap();
    assert_eq!(stored_weights.len(), 2);

    // Verify first weight
    let weight1 = stored_weights.iter().find(|w| w.id == "layer1.w1").unwrap();
    assert_eq!(weight1.value, 0.5);
    assert_eq!(weight1.delta, 0.0); // First update, no previous value

    // Verify second weight
    let weight2 = stored_weights.iter().find(|w| w.id == "layer1.w2").unwrap();
    assert_eq!(weight2.value, -0.3);
    assert_eq!(weight2.delta, 0.0); // First update, no previous value

    // Verify log messages
    let log_messages = fixture.logger.get_messages();
    assert!(log_messages.contains(&"Processing batch of 2 weight updates".to_string()));
}

#[test]
fn test_process_weight_batch_calculates_delta() {
    // Arrange
    let fixture = WeightProcessorFixture::with_weights();
    let updates = vec![
        WeightUpdate {
            id: "layer1.w1".to_string(),
            value: 0.6, // Changed from 0.5 to 0.6
            timestamp: 1625097700000,
            origin_sample: "sample2".to_string(),
            agent_id: None,
        },
    ];

    // Act
    let result = fixture.processor.process_weight_batch(updates);

    // Assert
    assert!(result.is_ok());

    // Verify weight was updated with correct delta
    let stored_weights = fixture.storage.get_all_weights().unwrap();
    let weight = stored_weights.iter().find(|w| w.id == "layer1.w1" && w.timestamp == 1625097700000).unwrap();
    assert_eq!(weight.value, 0.6);
    assert!(weight.delta >= 0.09 && weight.delta <= 0.11); // 0.6 - 0.5 = 0.1 (allow for floating point imprecision)
}

#[test]
fn test_detect_significant_changes_finds_outliers() {
    // Arrange
    let fixture = WeightProcessorFixture::with_weights();

    // Act
    let result = fixture.processor.detect_significant_changes(0.5);

    // Assert
    assert!(result.is_ok());
    let significant_weights = result.unwrap();

    // Only layer2.w1 has delta > 0.5
    assert_eq!(significant_weights.len(), 1);
    assert_eq!(significant_weights[0].id, "layer2.w1");
    assert_eq!(significant_weights[0].delta, 0.6);
}

#[test]
fn test_detect_significant_changes_with_custom_threshold() {
    // Arrange
    let fixture = WeightProcessorFixture::with_weights();

    // Act
    let result = fixture.processor.detect_significant_changes(0.15);

    // Assert
    assert!(result.is_ok());
    let significant_weights = result.unwrap();

    // Both layer1.w2 and layer2.w1 have delta > 0.15
    assert_eq!(significant_weights.len(), 2);

    // Verify weights are sorted by delta magnitude (descending)
    assert_eq!(significant_weights[0].id, "layer2.w1");
    assert_eq!(significant_weights[1].id, "layer1.w2");
}

#[test]
fn test_create_model_snapshot() {
    // Arrange
    let fixture = WeightProcessorFixture::with_weights();
    let reason = "Test snapshot".to_string();

    // Act
    let result = fixture.processor.create_model_snapshot(reason.clone());

    // Assert
    assert!(result.is_ok());
    let snapshot = result.unwrap();

    // Verify snapshot properties
    assert_eq!(snapshot.reason, reason);
    assert_eq!(snapshot.affected_weights.len(), 3);
    assert!(snapshot.affected_weights.contains(&"layer1.w1".to_string()));
    assert!(snapshot.affected_weights.contains(&"layer1.w2".to_string()));
    assert!(snapshot.affected_weights.contains(&"layer2.w1".to_string()));

    // Verify snapshot was stored
    let stored_snapshots = fixture.storage.get_all_snapshots().unwrap();
    assert_eq!(stored_snapshots.len(), 1);
    assert_eq!(stored_snapshots[0].id, snapshot.id);
}

#[test]
fn test_process_weight_batch_logs_significant_changes() {
    // Arrange
    let fixture = WeightProcessorFixture::new();

    // Create a processor with a lower significance threshold
    let processor = WeightProcessorImpl::new(
        fixture.storage.clone(),
        fixture.logger.clone(),
        0.1, // Lower threshold to ensure our changes are significant
    );

    // First batch to establish baseline
    let updates1 = vec![
        WeightUpdate {
            id: "layer1.w1".to_string(),
            value: 0.1,
            timestamp: 1625097500000,
            origin_sample: "sample1".to_string(),
            agent_id: None,
        },
        WeightUpdate {
            id: "layer2.w1".to_string(),
            value: 0.1,
            timestamp: 1625097500000,
            origin_sample: "sample1".to_string(),
            agent_id: None,
        },
    ];

    // Process first batch
    processor.process_weight_batch(updates1).unwrap();

    // Clear logger messages from the first batch
    fixture.logger.get_messages(); // This clears the messages

    // Second batch with significant changes
    let updates2 = vec![
        WeightUpdate {
            id: "layer1.w1".to_string(),
            value: 0.15, // Small change, below threshold
            timestamp: 1625097600000,
            origin_sample: "sample2".to_string(),
            agent_id: None,
        },
        WeightUpdate {
            id: "layer2.w1".to_string(),
            value: 0.5, // Large change, above threshold
            timestamp: 1625097600000,
            origin_sample: "sample2".to_string(),
            agent_id: None,
        },
    ];

    // Act
    let result = processor.process_weight_batch(updates2);

    // Assert
    assert!(result.is_ok());

    // Verify log messages for significant changes
    let log_messages = fixture.logger.get_messages();

    // Debug: Print all log messages
    println!("Log messages: {:?}", log_messages);

    // Find a message that contains both "Significant weight change detected" and "layer2.w1"
    let significant_message = log_messages.iter().find(|msg|
        msg.contains("Significant weight change detected") && msg.contains("layer2.w1")
    );
    assert!(significant_message.is_some(), "No log message found for significant weight change on layer2.w1");

    // Verify metrics were logged
    let metrics = fixture.logger.get_metrics();
    assert!(metrics.contains_key("weight_change.layer2.w1"));

    // Get the actual value and verify it's close to 0.4 (0.5 - 0.1)
    let metric_value = metrics.get("weight_change.layer2.w1").unwrap();
    assert!(metric_value > &0.3 && metric_value < &0.5, "Metric value {} is not close to 0.4", metric_value);
}

#[test]
fn test_empty_weight_batch() {
    // Arrange
    let fixture = WeightProcessorFixture::new();
    let updates = vec![];

    // Act
    let result = fixture.processor.process_weight_batch(updates);

    // Assert
    assert!(result.is_ok());

    // Verify no weights were stored
    let stored_weights = fixture.storage.get_all_weights().unwrap();
    assert_eq!(stored_weights.len(), 0);

    // Verify appropriate log message
    let log_messages = fixture.logger.get_messages();
    assert!(log_messages.contains(&"Processing batch of 0 weight updates".to_string()));
}

#[test]
fn test_detect_significant_changes_with_no_weights() {
    // Arrange
    let fixture = WeightProcessorFixture::new();

    // Act
    let result = fixture.processor.detect_significant_changes(0.5);

    // Assert
    assert!(result.is_ok());
    let significant_weights = result.unwrap();
    assert_eq!(significant_weights.len(), 0);
}

#[test]
fn test_create_model_snapshot_with_no_weights() {
    // Arrange
    let fixture = WeightProcessorFixture::new();
    let reason = "Empty snapshot".to_string();

    // Act
    let result = fixture.processor.create_model_snapshot(reason.clone());

    // Assert
    assert!(result.is_ok());
    let snapshot = result.unwrap();

    // Verify snapshot properties
    assert_eq!(snapshot.reason, reason);
    assert_eq!(snapshot.affected_weights.len(), 0);
}
