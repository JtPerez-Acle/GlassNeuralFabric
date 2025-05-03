# Test Driven Development Workflow

This document outlines the Test Driven Development (TDD) workflow that all developers must follow when implementing features for the NeuroSpacetime project.

## TDD Cycle

All development must follow the TDD cycle:

1. **Write a failing test** that defines the expected behavior
2. **Run the test** to verify it fails for the expected reason
3. **Write minimal implementation code** to make the test pass
4. **Run the test** to verify it passes
5. **Refactor** the code while ensuring tests continue to pass
6. **Repeat** for the next piece of functionality

## Language-Specific Testing Frameworks

### Rust Components

For Rust components, we use the following testing tools:

```rust
// Example test module in Rust
#[cfg(test)]
mod tests {
    use super::*;
    use mock_spacetime::MockContext;

    #[test]
    fn test_process_weight_changes() {
        // Arrange
        let ctx = MockContext::new();
        let input = UpdateInput {
            id: "layer1.weights.3".to_string(),
            value: 0.75,
            timestamp: 1625097600000,
            origin_sample: "sample1".to_string(),
            agent_id: None,
        };
        
        // Act
        let result = process_weight_changes(&ctx, input);
        
        // Assert
        assert!(result.is_ok());
        let stored_weight = ctx.db().get::<Weight>(&input.id).unwrap();
        assert_eq!(stored_weight.value, 0.75);
        assert_eq!(stored_weight.delta, 0.0); // First update, no previous value
    }
}
```

### Python Components

For Python components, we use pytest:

```python
# Example test for Python bridge
import pytest
from unittest.mock import MagicMock, patch
from bridge import NeuroHook

def test_neuro_hook_enqueue():
    # Arrange
    mock_model = MagicMock()
    mock_param = MagicMock()
    mock_param.data.cpu().float().mean.return_value.item.return_value = 0.5
    mock_grad = MagicMock()
    mock_grad.mean.return_value.item.return_value = 0.1
    
    # Act
    hook = NeuroHook(mock_model)
    with patch.object(hook, 'q') as mock_queue:
        hook._enqueue("layer1", mock_param, mock_grad)
    
    # Assert
    mock_queue.put.assert_called_once()
    args = mock_queue.put.call_args[0][0]
    assert args["id"] == "layer1"
    assert args["value"] == 0.5
    assert args["delta"] == 0.4  # 0.5 - 0.1
```

### TypeScript/React Components

For TypeScript components, we use Vitest:

```typescript
// Example test for React component
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import WeightGraph from './WeightGraph';

describe('WeightGraph', () => {
  it('renders graph with provided weights', () => {
    // Arrange
    const weights = [
      { id: 'layer1.w1', value: 0.5, delta: 0.1, timestamp: 1625097600000 },
      { id: 'layer1.w2', value: -0.3, delta: -0.2, timestamp: 1625097600000 }
    ];
    
    // Act
    render(<WeightGraph weights={weights} />);
    
    // Assert
    expect(screen.getByTestId('weight-graph')).toBeInTheDocument();
    expect(screen.getByText('layer1.w1')).toBeInTheDocument();
    expect(screen.getByText('layer1.w2')).toBeInTheDocument();
  });
});
```

## Test Organization

### Unit Tests

Unit tests should be organized by module and should test individual components in isolation:

- Each function/method should have multiple tests covering different scenarios
- Use mocks to isolate the component from its dependencies
- Focus on testing behavior, not implementation details
- Aim for >90% code coverage

### Integration Tests

Integration tests should verify that components work together correctly:

- Test interactions between modules
- Verify data flows correctly through the system
- Test API contracts between components
- Use realistic test data

### End-to-End Tests

End-to-end tests should verify complete user workflows:

- Test from the user's perspective
- Verify that the system works as a whole
- Focus on critical paths through the application

## Test Data Management

### Test Fixtures

Create reusable test fixtures for common test scenarios:

```rust
// Example test fixture in Rust
pub struct WeightTestFixture {
    pub weights: Vec<Weight>,
    pub context: MockContext,
}

impl WeightTestFixture {
    pub fn new() -> Self {
        let mut context = MockContext::new();
        let weights = vec![
            Weight {
                id: "layer1.w1".to_string(),
                value: 0.5,
                delta: 0.1,
                timestamp: 1625097600000,
                origin_sample: "sample1".to_string(),
                agent_id: None,
            },
            Weight {
                id: "layer1.w2".to_string(),
                value: -0.3,
                delta: -0.2,
                timestamp: 1625097600000,
                origin_sample: "sample1".to_string(),
                agent_id: None,
            },
        ];
        
        for weight in &weights {
            context.db().set(weight.clone()).unwrap();
        }
        
        Self { weights, context }
    }
}
```

### Test Data Generators

Create generators for test data:

```python
# Example test data generator in Python
def generate_test_gradients(layer_count=3, neurons_per_layer=5, 
                           gradient_type="normal"):
    """Generate test gradients for a neural network.
    
    Args:
        layer_count: Number of layers
        neurons_per_layer: Number of neurons per layer
        gradient_type: Type of gradients to generate 
                      ("normal", "vanishing", "exploding")
    
    Returns:
        Dictionary mapping layer names to gradient tensors
    """
    import numpy as np
    
    gradients = {}
    
    for l in range(layer_count):
        if gradient_type == "normal":
            grad_values = np.random.normal(0, 0.1, neurons_per_layer)
        elif gradient_type == "vanishing":
            grad_values = np.random.normal(0, 0.001, neurons_per_layer)
        elif gradient_type == "exploding":
            grad_values = np.random.normal(0, 10.0, neurons_per_layer)
        
        gradients[f"layer{l+1}"] = grad_values
    
    return gradients
```

## Continuous Integration

All tests must pass in the CI pipeline before code can be merged:

- Unit tests run on every commit
- Integration tests run on pull requests
- End-to-end tests run before deployment
- Code coverage reports are generated for every build

## TDD Best Practices

1. **Write the simplest test possible** that verifies the behavior you want
2. **Write the simplest code possible** to make the test pass
3. **Refactor aggressively** once tests are passing
4. **Test behavior, not implementation** to allow for refactoring
5. **Keep tests fast** to encourage running them frequently
6. **Make tests independent** so they can run in any order
7. **Use descriptive test names** that explain the expected behavior

## Example TDD Workflow

### Step 1: Write a failing test

```rust
#[test]
fn test_detect_significant_changes_identifies_outliers() {
    // Arrange
    let fixture = WeightTestFixture::new();
    let ctx = fixture.context;
    
    let input = DetectionInput {
        threshold: 0.5,
        layer_id: "layer1".to_string(),
    };
    
    // Act
    let result = detect_significant_changes(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
    let significant_weights = result.unwrap();
    assert_eq!(significant_weights.len(), 1);
    assert_eq!(significant_weights[0].id, "layer1.w1");
}
```

### Step 2: Run the test (it fails)

```
running 1 test
test tests::test_detect_significant_changes_identifies_outliers ... FAILED

failures:

---- tests::test_detect_significant_changes_identifies_outliers ----
thread 'tests::test_detect_significant_changes_identifies_outliers' panicked at 'called `Result::unwrap()` on an `Err` value: FunctionNotImplemented', src/reducers.rs:45:18
```

### Step 3: Write minimal implementation

```rust
pub fn detect_significant_changes(ctx: &Context, input: DetectionInput) 
    -> Result<Vec<Weight>, Error> {
    
    let weights = ctx.db()
        .scan_index::<Weight, _>("by_layer", &input.layer_id)?
        .collect::<Result<Vec<_>, _>>()?;
    
    let significant = weights.into_iter()
        .filter(|w| w.delta.abs() >= input.threshold)
        .collect();
    
    Ok(significant)
}
```

### Step 4: Run the test (it passes)

```
running 1 test
test tests::test_detect_significant_changes_identifies_outliers ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

### Step 5: Refactor

```rust
pub fn detect_significant_changes(ctx: &Context, input: DetectionInput) 
    -> Result<Vec<Weight>, Error> {
    
    // Extract to a helper function for reusability
    let weights = get_weights_by_layer(ctx, &input.layer_id)?;
    
    // Use a more descriptive variable name
    let threshold = input.threshold;
    
    // Extract filtering logic for clarity
    let significant = weights.into_iter()
        .filter(|w| is_significant(w, threshold))
        .collect();
    
    Ok(significant)
}

fn get_weights_by_layer(ctx: &Context, layer_id: &str) -> Result<Vec<Weight>, Error> {
    ctx.db()
        .scan_index::<Weight, _>("by_layer", layer_id)?
        .collect::<Result<Vec<_>, _>>()
}

fn is_significant(weight: &Weight, threshold: f64) -> bool {
    weight.delta.abs() >= threshold
}
```

### Step 6: Add more tests

```rust
#[test]
fn test_detect_significant_changes_with_empty_layer() {
    // Arrange
    let ctx = MockContext::new();
    let input = DetectionInput {
        threshold: 0.5,
        layer_id: "non_existent_layer".to_string(),
    };
    
    // Act
    let result = detect_significant_changes(&ctx, input);
    
    // Assert
    assert!(result.is_ok());
    let significant_weights = result.unwrap();
    assert_eq!(significant_weights.len(), 0);
}
```

## Conclusion

Following this TDD workflow ensures that:

1. All code is tested
2. Tests document the expected behavior
3. Implementation satisfies the requirements
4. Refactoring can be done safely
5. Code quality remains high throughout the project
