# Test File Template

This template provides a standard structure for writing tests following the Test Driven Development (TDD) approach in the NeuroSpacetime project.

## Rust Test Template

```rust
//! Tests for the [module name] module.

#[cfg(test)]
mod tests {
    use super::*;
    use mock_spacetime::MockContext;
    // Import other dependencies needed for testing
    
    // Setup common test fixtures
    
    struct TestFixture {
        // Fields needed for tests
    }
    
    impl TestFixture {
        fn new() -> Self {
            // Initialize test fixture
            Self {
                // Initialize fields
            }
        }
    }
    
    #[test]
    fn test_[function_name]_[scenario_being_tested]() {
        // Arrange
        let fixture = TestFixture::new();
        // Set up test data and expectations
        
        // Act
        let result = [function_being_tested]();
        
        // Assert
        assert_eq!(result, expected_result);
        // Additional assertions
    }
    
    #[test]
    fn test_[function_name]_[another_scenario]() {
        // Arrange
        
        // Act
        
        // Assert
    }
    
    // Additional tests...
}
```

## Python Test Template

```python
"""Tests for the [module name] module."""

import pytest
from unittest.mock import MagicMock, patch
from [module_path] import [ClassBeingTested]

# Setup fixtures

@pytest.fixture
def test_fixture():
    """Create a test fixture for the tests."""
    # Set up test data
    return {
        # Test data
    }

# Tests

def test_[method_name]_[scenario_being_tested](test_fixture):
    """Test that [method_name] [expected behavior]."""
    # Arrange
    instance = [ClassBeingTested]()
    # Set up test data and expectations
    
    # Act
    result = instance.[method_name]()
    
    # Assert
    assert result == expected_result
    # Additional assertions

def test_[method_name]_[another_scenario](test_fixture):
    """Test that [method_name] [expected behavior for another scenario]."""
    # Arrange
    
    # Act
    
    # Assert

# Additional tests...
```

## TypeScript Test Template

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { [ComponentBeingTested] } from './[ComponentFile]';

// Mock dependencies
vi.mock('./dependency', () => ({
  useDependency: vi.fn().mockReturnValue({
    // Mock return values
  }),
}));

describe('[ComponentBeingTested]', () => {
  // Setup
  beforeEach(() => {
    // Reset mocks and setup test environment
    vi.clearAllMocks();
  });
  
  it('should [expected behavior]', () => {
    // Arrange
    const props = {
      // Component props
    };
    
    // Act
    render(<[ComponentBeingTested] {...props} />);
    
    // Assert
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
    // Additional assertions
  });
  
  it('should [another expected behavior]', () => {
    // Arrange
    
    // Act
    
    // Assert
  });
  
  // Additional tests...
});
```

## Test Organization Guidelines

### Unit Tests

1. **Group tests by function/method**: Each function or method should have its own group of tests.
2. **Name tests descriptively**: Test names should describe the scenario being tested and the expected outcome.
3. **Follow AAA pattern**: Arrange, Act, Assert.
4. **Test edge cases**: Include tests for edge cases, error conditions, and boundary values.
5. **Keep tests independent**: Each test should be able to run independently of others.

### Integration Tests

1. **Focus on module interactions**: Test how modules work together.
2. **Use realistic data**: Use data that resembles real-world usage.
3. **Test complete workflows**: Test end-to-end workflows that span multiple modules.
4. **Minimize mocking**: Use real implementations where possible, mock only external dependencies.

## Test Data Guidelines

1. **Use fixtures for common data**: Define fixtures for data used across multiple tests.
2. **Make test data explicit**: Avoid hidden dependencies in test data.
3. **Use factories for complex objects**: Create factory functions for complex test objects.
4. **Randomize where appropriate**: Use property-based testing for scenarios where randomized inputs are valuable.

## Mocking Guidelines

1. **Mock at boundaries**: Mock external dependencies and module boundaries.
2. **Verify interactions**: Verify that mocks are called with expected arguments.
3. **Don't mock what you don't own**: Prefer integration tests for code you own, mock external dependencies.
4. **Keep mocks simple**: Mocks should return the minimal data needed for the test.

## Test Coverage Guidelines

1. **Aim for >90% code coverage**: Ensure most code paths are tested.
2. **Focus on behavior, not lines**: Coverage is a tool, not a goal.
3. **Prioritize critical paths**: Ensure critical functionality has comprehensive tests.
4. **Test error handling**: Ensure error cases are tested.

## TDD Workflow Reminder

1. **Write a failing test** that defines the expected behavior.
2. **Run the test** to verify it fails for the expected reason.
3. **Write minimal implementation code** to make the test pass.
4. **Run the test** to verify it passes.
5. **Refactor** the code while ensuring tests continue to pass.
6. **Repeat** for the next piece of functionality.
