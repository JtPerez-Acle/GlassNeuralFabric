//! Tests for the SpacetimeDB schema.
//!
//! These tests verify that our SpacetimeDB schema is correctly defined
//! and can be used to create tables and indexes in SpacetimeDB.

use std::fs;
use std::path::Path;
use std::process::Command;

#[test]
fn test_schema_file_exists() {
    // Check that the schema file exists
    let schema_path = Path::new("schema/schema.sql");
    assert!(schema_path.exists(), "Schema file does not exist");
    
    // Check that the schema file is not empty
    let schema_content = fs::read_to_string(schema_path).expect("Failed to read schema file");
    assert!(!schema_content.is_empty(), "Schema file is empty");
}

#[test]
fn test_schema_contains_required_tables() {
    // Read the schema file
    let schema_path = Path::new("schema/schema.sql");
    let schema_content = fs::read_to_string(schema_path).expect("Failed to read schema file");
    
    // Check that the schema contains the required tables
    assert!(schema_content.contains("CREATE TABLE weight"), "Schema does not contain weight table");
    assert!(schema_content.contains("CREATE TABLE model_snapshot"), "Schema does not contain model_snapshot table");
}

#[test]
fn test_schema_contains_required_indexes() {
    // Read the schema file
    let schema_path = Path::new("schema/schema.sql");
    let schema_content = fs::read_to_string(schema_path).expect("Failed to read schema file");
    
    // Check that the schema contains the required indexes
    assert!(schema_content.contains("CREATE INDEX by_time"), "Schema does not contain by_time index");
    assert!(schema_content.contains("CREATE INDEX by_layer"), "Schema does not contain by_layer index");
}

#[test]
#[ignore] // This test requires SpacetimeDB to be installed and running
fn test_schema_can_be_deployed() {
    // Create a temporary database for testing
    let db_name = format!("test_db_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs());
    
    // Deploy the schema to the temporary database
    let output = Command::new("spacetimedb")
        .args(["create", &db_name])
        .output()
        .expect("Failed to create test database");
    
    assert!(output.status.success(), "Failed to create test database");
    
    // Deploy the schema to the database
    let output = Command::new("spacetimedb")
        .args(["sql", &db_name, "-f", "schema/schema.sql"])
        .output()
        .expect("Failed to deploy schema");
    
    assert!(output.status.success(), "Failed to deploy schema");
    
    // Clean up the test database
    let _output = Command::new("spacetimedb")
        .args(["delete", &db_name, "--force"])
        .output()
        .expect("Failed to delete test database");
}
