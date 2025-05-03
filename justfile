# NeuroSpacetime justfile
# This file contains commands for development, testing, and deployment

# Default command shows help
default:
    @just --list

# Setup the development environment
setup:
    @echo "Setting up development environment..."
    rustup target add wasm32-unknown-unknown
    pip install -r python/requirements.txt
    cd apps/viz && npm install
    cd apps/admin && npm install
    pre-commit install

# Build reducers for SpacetimeDB
build-reducers:
    @echo "Building reducers for SpacetimeDB..."
    cd crates/reducers && cargo build --target wasm32-unknown-unknown --release

# Deploy SpacetimeDB schema
deploy-schema db="neurospace" force="":
    @echo "Deploying SpacetimeDB schema to {{db}}..."
    cd crates/reducers && ./scripts/deploy_schema.sh --db-name {{db}} {{force}}

# Publish reducers to SpacetimeDB
publish-reducers db="neurospace":
    @echo "Publishing reducers to SpacetimeDB..."
    cd crates/reducers && cargo build --target wasm32-unknown-unknown --release
    spacetimedb publish {{db}} -c -p crates/reducers

# Run SpacetimeDB with reducers hot-loaded
run-stdb:
    @echo "Starting SpacetimeDB..."
    spacetimedb start --project-path crates/reducers --hot-reload

# Run SpacetimeDB tests
test-stdb:
    @echo "Running SpacetimeDB tests..."
    cd crates/reducers && cargo test

# Run the visualization UI in development mode
dev-viz:
    @echo "Starting visualization UI..."
    cd apps/viz && npm run dev

# Run a demo training model with the bridge
train-demo:
    @echo "Running demo training model..."
    cd python/examples && python mnist_demo.py

# Run everything concurrently
all:
    @echo "Starting all components..."
    just run-stdb & just dev-viz & just train-demo

# Run Rust tests
test-rust:
    @echo "Running Rust tests..."
    cd crates/reducers && cargo test
    cd crates/common && cargo test
    cd crates/test-utils && cargo test

# Run Python tests
test-python:
    @echo "Running Python tests..."
    cd python && pytest

# Run TypeScript tests
test-ts:
    @echo "Running TypeScript tests..."
    cd apps/viz && npm test
    cd apps/admin && npm test

# Run all tests
test-all:
    @echo "Running all tests..."
    just test-rust
    just test-python
    just test-ts

# Run tests in watch mode
test-watch module:
    @echo "Running tests in watch mode for {{module}}..."
    cd {{module}} && cargo watch -x test

# Check test coverage
coverage:
    @echo "Checking test coverage..."
    cd crates/reducers && cargo tarpaulin
    cd python && pytest --cov
    cd apps/viz && npm run coverage

# Run integration tests
test-integration:
    @echo "Running integration tests..."
    cd tests && cargo test

# Run end-to-end tests
test-e2e:
    @echo "Running end-to-end tests..."
    cd tests && npm run e2e

# Create a new module
new-module name:
    @echo "Creating new module {{name}}..."
    mkdir -p crates/{{name}}/src
    cp docs/templates/MODULE_INTERFACE_TEMPLATE.md crates/{{name}}/README.md
    echo 'pub mod {{name}};' > crates/{{name}}/src/lib.rs
    echo 'pub trait {{pascal_case(name)}} {' > crates/{{name}}/src/{{name}}.rs
    echo '    // TODO: Define interface' >> crates/{{name}}/src/{{name}}.rs
    echo '}' >> crates/{{name}}/src/{{name}}.rs
    echo '' >> crates/{{name}}/src/{{name}}.rs
    echo '#[cfg(test)]' >> crates/{{name}}/src/{{name}}.rs
    echo 'mod tests {' >> crates/{{name}}/src/{{name}}.rs
    echo '    use super::*;' >> crates/{{name}}/src/{{name}}.rs
    echo '' >> crates/{{name}}/src/{{name}}.rs
    echo '    #[test]' >> crates/{{name}}/src/{{name}}.rs
    echo '    fn test_{{name}}() {' >> crates/{{name}}/src/{{name}}.rs
    echo '        // TODO: Write tests' >> crates/{{name}}/src/{{name}}.rs
    echo '    }' >> crates/{{name}}/src/{{name}}.rs
    echo '}' >> crates/{{name}}/src/{{name}}.rs

# Run Rust linter
lint-rust:
    @echo "Running Rust linter..."
    cd crates && cargo clippy -- -D warnings

# Run Python linter
lint-python:
    @echo "Running Python linter..."
    cd python && ruff check .

# Run TypeScript linter
lint-ts:
    @echo "Running TypeScript linter..."
    cd apps/viz && npm run lint
    cd apps/admin && npm run lint

# Run all linters
lint-all:
    @echo "Running all linters..."
    just lint-rust
    just lint-python
    just lint-ts

# Format Rust code
fmt-rust:
    @echo "Formatting Rust code..."
    cd crates && cargo fmt

# Format Python code
fmt-python:
    @echo "Formatting Python code..."
    cd python && ruff format .

# Format TypeScript code
fmt-ts:
    @echo "Formatting TypeScript code..."
    cd apps/viz && npm run format
    cd apps/admin && npm run format

# Format all code
fmt-all:
    @echo "Formatting all code..."
    just fmt-rust
    just fmt-python
    just fmt-ts

# Generate Rust documentation
doc-rust:
    @echo "Generating Rust documentation..."
    cd crates && cargo doc --no-deps --open

# Generate Python documentation
doc-python:
    @echo "Generating Python documentation..."
    cd python && pdoc --html --output-dir docs bridge

# Generate TypeScript documentation
doc-ts:
    @echo "Generating TypeScript documentation..."
    cd apps/viz && npm run docs
    cd apps/admin && npm run docs

# Generate all documentation
doc-all:
    @echo "Generating all documentation..."
    just doc-rust
    just doc-python
    just doc-ts

# Build Docker images
docker-build:
    @echo "Building Docker images..."
    docker-compose build

# Run in Docker
docker-run:
    @echo "Running in Docker..."
    docker-compose up

# Helper function to convert to pascal case
pascal_case name:
    @echo "{{name}}" | sed -r 's/(^|_)([a-z])/\U\2/g'
