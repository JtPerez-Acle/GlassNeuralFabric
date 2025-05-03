//! Tests for the deployment script.
//!
//! These tests verify that the deployment script works correctly.

use std::process::Command;
use std::path::Path;

#[test]
fn test_deployment_script_exists() {
    // Check that the deployment script exists
    let script_path = Path::new("scripts/deploy_schema.sh");
    assert!(script_path.exists(), "Deployment script does not exist");
    
    // Check that the script is executable
    let output = Command::new("test")
        .args(["-x", script_path.to_str().unwrap()])
        .output()
        .expect("Failed to check if script is executable");
    
    assert!(output.status.success(), "Deployment script is not executable");
}

#[test]
#[ignore] // This test requires SpacetimeDB to be installed and running
fn test_deployment_script_works() {
    // Create a temporary database name for testing
    let db_name = format!("test_db_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs());
    
    // Run the deployment script
    let output = Command::new("./scripts/deploy_schema.sh")
        .args(["--db-name", &db_name])
        .output()
        .expect("Failed to run deployment script");
    
    assert!(output.status.success(), "Deployment script failed: {}", String::from_utf8_lossy(&output.stderr));
    
    // Check that the database was created
    let output = Command::new("spacetimedb")
        .args(["list"])
        .output()
        .expect("Failed to list databases");
    
    let output_str = String::from_utf8_lossy(&output.stdout);
    assert!(output_str.contains(&db_name), "Database was not created");
    
    // Clean up the test database
    let _output = Command::new("spacetimedb")
        .args(["delete", &db_name, "--force"])
        .output()
        .expect("Failed to delete test database");
}
