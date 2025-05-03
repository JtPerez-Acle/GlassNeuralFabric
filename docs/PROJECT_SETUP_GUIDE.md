# NeuroSpacetime Project Setup Guide

This guide provides instructions for setting up the NeuroSpacetime project development environment with a focus on Test Driven Development (TDD) and modular architecture.

## Prerequisites

- **Rust 1.79+** with `wasm32-unknown-unknown` target
- **Python 3.11+** with `venv` module
- **Node.js 18+** with npm or yarn
- **SpacetimeDB CLI** (for local development)
- **just** command runner
- **Docker** (for containerized development and testing)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/neurospace-time.git
cd neurospace-time
```

### 2. Install Development Tools

```bash
# Install just command runner
cargo install just

# Install SpacetimeDB CLI
cargo install spacetimedb-cli

# Add wasm32 target
rustup target add wasm32-unknown-unknown

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Set Up Project Components

```bash
# Run the setup script
just setup
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Rust dependencies
- Install Node.js dependencies
- Set up pre-commit hooks
- Initialize SpacetimeDB

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
neurospace-time/
├── crates/                  # Rust crates
│   ├── reducers/            # SpacetimeDB reducers
│   ├── common/              # Shared Rust code
│   └── test-utils/          # Testing utilities
├── python/                  # Python code
│   ├── bridge/              # PyTorch bridge
│   ├── examples/            # Example models
│   └── tests/               # Python tests
├── apps/                    # Frontend applications
│   ├── viz/                 # Visualization UI
│   └── admin/               # Admin UI
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
│   ├── templates/           # Templates for new modules
│   └── architecture/        # Architecture documentation
├── tests/                   # Integration tests
├── .github/                 # GitHub Actions workflows
└── justfile                 # Command definitions
```

## Development Workflow

### 1. Start with Tests

Following TDD principles, always start by writing tests:

```bash
# Create a new module with test scaffolding
just new-module <module-name>
```

This will create:
- Module interface file
- Test file with initial test cases
- Implementation skeleton

### 2. Run Tests

```bash
# Run Rust tests
just test-rust

# Run Python tests
just test-python

# Run TypeScript tests
just test-ts

# Run all tests
just test-all
```

### 3. Implement Features

After writing failing tests, implement the features to make the tests pass:

```bash
# Run tests in watch mode during development
just test-watch <module-name>
```

### 4. Run the Development Environment

```bash
# Start SpacetimeDB
just run-stdb

# Start the visualization UI
just dev-viz

# Run a demo training model
just train-demo

# Run everything concurrently
just all
```

## Testing Guidelines

### Unit Testing

Each module should have comprehensive unit tests:

```bash
# Check test coverage
just coverage

# Run specific tests
just test-rust -- <test-name>
```

### Integration Testing

Integration tests verify that modules work together correctly:

```bash
# Run integration tests
just test-integration
```

### End-to-End Testing

End-to-end tests verify complete user workflows:

```bash
# Run end-to-end tests
just test-e2e
```

## Modular Architecture Guidelines

### Creating New Modules

When creating a new module:

1. Define the module's responsibility (single responsibility principle)
2. Define the module's interface (what it provides to other modules)
3. Define the module's dependencies (what it needs from other modules)
4. Write tests for the module's interface
5. Implement the module

```bash
# Create a new module
just new-module <module-name>
```

### Module Dependencies

Modules should depend on interfaces, not implementations:

```rust
// Good: Depending on an interface
pub struct MyModule<S: Storage, L: Logger> {
    storage: S,
    logger: L,
}

// Bad: Depending on a concrete implementation
pub struct MyModule {
    storage: StorageImpl,
    logger: LoggerImpl,
}
```

### Cross-Module Communication

Modules should communicate through well-defined interfaces:

```rust
// Define events for communication
pub struct WeightChangedEvent {
    pub weight_id: String,
    pub old_value: f64,
    pub new_value: f64,
}

// Publish events
event_bus.publish(WeightChangedEvent {
    weight_id: "layer1.w1".to_string(),
    old_value: 0.5,
    new_value: 0.6,
});

// Subscribe to events
event_bus.subscribe::<WeightChangedEvent>(|event| {
    // Handle event
});
```

## Code Quality Tools

The project uses several tools to maintain code quality:

### Linting

```bash
# Run Rust linter
just lint-rust

# Run Python linter
just lint-python

# Run TypeScript linter
just lint-ts

# Run all linters
just lint-all
```

### Formatting

```bash
# Format Rust code
just fmt-rust

# Format Python code
just fmt-python

# Format TypeScript code
just fmt-ts

# Format all code
just fmt-all
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality:

- Linting
- Formatting
- Type checking
- Test running

## Continuous Integration

The project uses GitHub Actions for continuous integration:

- Tests run on every pull request
- Linting and formatting checks
- Test coverage reports
- WASM compilation verification
- Docker image building

## Documentation

### Generating Documentation

```bash
# Generate Rust documentation
just doc-rust

# Generate Python documentation
just doc-python

# Generate TypeScript documentation
just doc-ts

# Generate all documentation
just doc-all
```

### Architecture Documentation

The project's architecture is documented in the `docs/architecture` directory:

- `OVERVIEW.md`: High-level overview of the system
- `MODULES.md`: Description of each module and its responsibilities
- `INTERFACES.md`: Definition of module interfaces
- `DATA_FLOW.md`: Description of data flow through the system

## Conclusion

By following this setup guide and adhering to the TDD and modular architecture principles, you'll be able to contribute effectively to the NeuroSpacetime project. Remember:

1. **Start with tests**: Write tests before implementing features
2. **Follow modular architecture**: Keep modules focused and loosely coupled
3. **Use the provided tools**: Leverage the project's tooling for development
4. **Consult the documentation**: Refer to the architecture documentation when in doubt
