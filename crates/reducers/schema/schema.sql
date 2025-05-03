-- SpacetimeDB Schema for GlassNeuralFabric
-- This schema defines the tables and indexes for the GlassNeuralFabric system.

-- Weight table for storing neural network weights
CREATE TABLE weight (
    -- Unique identifier for the weight (e.g., "layer1.weight.0.1")
    id TEXT PRIMARY KEY,
    
    -- Current value of the weight
    value REAL NOT NULL,
    
    -- Change in value since the last update
    delta REAL NOT NULL,
    
    -- Timestamp of the update (milliseconds since epoch)
    timestamp BIGINT NOT NULL,
    
    -- Identifier of the sample that triggered this update
    origin_sample TEXT NOT NULL,
    
    -- Optional identifier of the agent that made the update
    agent_id TEXT
);

-- Index for querying weights by timestamp
CREATE INDEX by_time ON weight(timestamp);

-- Index for querying weights by layer (using the prefix of the id)
CREATE INDEX by_layer ON weight(id);

-- ModelSnapshot table for storing snapshots of the model
CREATE TABLE model_snapshot (
    -- Unique identifier for the snapshot
    id TEXT PRIMARY KEY,
    
    -- Timestamp of the snapshot (milliseconds since epoch)
    timestamp BIGINT NOT NULL,
    
    -- List of weight IDs affected by this snapshot (stored as JSON array)
    affected_weights JSON NOT NULL,
    
    -- Reason for creating the snapshot
    reason TEXT NOT NULL
);

-- Index for querying snapshots by timestamp
CREATE INDEX snapshot_by_time ON model_snapshot(timestamp);

-- Function to extract layer ID from weight ID
CREATE FUNCTION extract_layer_id(weight_id TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN split_part(weight_id, '.', 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- View for aggregating weight statistics by layer
CREATE VIEW layer_stats AS
SELECT 
    extract_layer_id(id) AS layer_id,
    COUNT(*) AS weight_count,
    AVG(value) AS avg_value,
    AVG(ABS(delta)) AS avg_delta,
    MAX(ABS(delta)) AS max_delta,
    MIN(timestamp) AS first_update,
    MAX(timestamp) AS last_update
FROM weight
GROUP BY layer_id;
