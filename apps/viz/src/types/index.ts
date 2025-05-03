/**
 * Type definitions for the NeuroSpacetime visualization module.
 */

/**
 * Weight model representing a neural network weight.
 */
export interface Weight {
  /** Unique identifier for the weight (e.g., "layer1.w1") */
  id: string;
  
  /** Current value of the weight */
  value: number;
  
  /** Change in value since the last update */
  delta: number;
  
  /** Timestamp of the update (milliseconds since epoch) */
  timestamp: number;
  
  /** Identifier for the sample that triggered this update */
  origin_sample: string;
  
  /** Optional identifier for the agent that updated this weight */
  agent_id: string | null;
}

/**
 * Model snapshot representing the state of the model at a point in time.
 */
export interface ModelSnapshot {
  /** Unique identifier for the snapshot */
  id: string;
  
  /** Timestamp of the snapshot (milliseconds since epoch) */
  timestamp: number;
  
  /** List of weight IDs affected by this snapshot */
  affected_weights: string[];
  
  /** Reason for creating the snapshot */
  reason: string;
}

/**
 * Gradient information for a layer.
 */
export interface Gradient {
  /** Unique identifier for the gradient (e.g., "layer1.grad") */
  id: string;
  
  /** L2 norm of the gradient */
  norm: number;
  
  /** Mean value of the gradient */
  mean: number;
  
  /** Variance of the gradient */
  variance: number;
  
  /** Timestamp of the update (milliseconds since epoch) */
  timestamp: number;
  
  /** Identifier for the sample that triggered this update */
  origin_sample: string;
  
  /** Optional identifier for the agent that updated this gradient */
  agent_id: string | null;
}

/**
 * Anomaly detected in the neural network.
 */
export interface Anomaly {
  /** Unique identifier for the anomaly */
  id: string;
  
  /** Type of anomaly (e.g., "vanishing_gradient", "exploding_gradient") */
  anomaly_type: string;
  
  /** Severity of the anomaly (0.0 to 1.0) */
  severity: number;
  
  /** Timestamp of the anomaly (milliseconds since epoch) */
  timestamp: number;
  
  /** Description of the anomaly */
  description: string;
  
  /** Affected weights or gradients */
  affected_elements: string[];
}
