# NeuroSpacetime Architecture Overview

This document provides a high-level overview of the NeuroSpacetime system architecture, focusing on the modular design and component interactions.

## System Architecture

NeuroSpacetime follows a modular architecture with clear separation of concerns. The system is divided into several key modules, each with a specific responsibility:

![System Architecture Diagram](./architecture_diagram.png)

## Core Modules

### 1. Data Capture Module

**Responsibility**: Capture neural network state during training.

This module hooks into PyTorch training loops to capture weight changes, gradients, and activations. It filters and batches the data before sending it to the Data Processing Module.

**Key Components**:
- PyTorch hooks for weight capture
- Gradient capture utilities
- Activation capture utilities
- Batching and filtering logic

**Technology**: Python, PyTorch

### 2. Data Processing Module

**Responsibility**: Process and analyze neural network data.

This module receives data from the Data Capture Module, processes it, and stores it in the Storage Module. It also performs analysis on the data to detect anomalies and significant changes.

**Key Components**:
- Weight change reducers
- Gradient analysis utilities
- Anomaly detection algorithms
- Statistical analysis functions

**Technology**: Rust, WASM, SpacetimeDB

### 3. Storage Module

**Responsibility**: Manage persistence of neural network state.

This module stores the processed data in a database and provides query capabilities for retrieving the data.

**Key Components**:
- SpacetimeDB schema
- Query utilities
- Data access layer
- Caching mechanisms

**Technology**: SpacetimeDB, Rust

### 4. Visualization Module

**Responsibility**: Render neural network state and dynamics.

This module retrieves data from the Storage Module and renders it in a user interface. It provides various visualizations of the neural network state and dynamics.

**Key Components**:
- Graph visualization components
- Timeline visualization
- Heatmap components
- Animation utilities

**Technology**: TypeScript, React, Cytoscape.js

### 5. Analytics Module

**Responsibility**: Provide insights and anomaly detection.

This module analyzes the neural network data to provide insights and detect anomalies. It also generates reports and alerts.

**Key Components**:
- Anomaly detection algorithms
- Trend analysis utilities
- Comparative analysis functions
- Reporting utilities

**Technology**: Rust, WASM, SpacetimeDB

## Cross-Cutting Concerns

### 1. Configuration Module

**Responsibility**: Manage system configuration.

This module provides a centralized way to configure the system. It handles environment-specific settings and runtime-configurable parameters.

### 2. Logging and Monitoring Module

**Responsibility**: Provide logging and monitoring capabilities.

This module provides logging and monitoring capabilities for the system. It handles log collection, metrics, and alerting.

### 3. Security Module

**Responsibility**: Manage authentication and authorization.

This module handles authentication, authorization, and secure communication between components.

## Data Flow

1. The **Data Capture Module** hooks into a PyTorch training loop and captures weight changes, gradients, and activations.
2. The captured data is filtered and batched before being sent to the **Data Processing Module**.
3. The **Data Processing Module** processes the data, performs analysis, and stores it in the **Storage Module**.
4. The **Visualization Module** retrieves data from the **Storage Module** and renders it in the user interface.
5. The **Analytics Module** analyzes the data to provide insights and detect anomalies.

## Module Interactions

Modules interact through well-defined interfaces:

- **Data Capture → Data Processing**: HTTP/WebSocket API
- **Data Processing → Storage**: SpacetimeDB API
- **Storage → Visualization**: SpacetimeDB Live Queries
- **Storage → Analytics**: SpacetimeDB API
- **Analytics → Visualization**: Event-based communication

## Deployment Architecture

NeuroSpacetime can be deployed in various configurations:

1. **Local Development**: All components run on the developer's machine.
2. **Single-Server Deployment**: All components run on a single server.
3. **Distributed Deployment**: Components run on separate servers for scalability.

![Deployment Architecture Diagram](./deployment_diagram.png)

## Technology Stack

- **Rust 1.79+**: Server-side logic, reducers
- **Python 3.11**: PyTorch integration, bridge
- **TypeScript 5.5 / React + Vite**: Visualization UI
- **SpacetimeDB**: Storage and real-time queries
- **WebAssembly (WASM)**: Portable execution of Rust code
- **Docker**: Containerization for deployment

## Development Principles

### Test Driven Development (TDD)

All development follows TDD principles:
1. Write tests first
2. Implement minimal code to pass tests
3. Refactor while maintaining passing tests

### Modular Architecture

The system is designed with modularity in mind:
1. Clear module boundaries
2. Well-defined interfaces
3. Loose coupling between modules
4. High cohesion within modules

## Conclusion

The NeuroSpacetime architecture is designed to be modular, testable, and scalable. By following the principles outlined in this document, we can build a system that is maintainable, extensible, and robust.
