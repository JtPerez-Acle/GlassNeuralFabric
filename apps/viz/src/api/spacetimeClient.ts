/**
 * SpacetimeDB client for the GlassNeuralFabric visualization UI.
 * 
 * This module provides functions for connecting to SpacetimeDB and
 * subscribing to weight and snapshot updates.
 */

import { SpacetimeDBClient } from '@clockworklabs/spacetimedb-sdk';

/**
 * Weight data from SpacetimeDB.
 */
export interface Weight {
  id: string;
  value: number;
  delta: number;
  timestamp: number;
  origin_sample: string;
  agent_id?: string;
}

/**
 * Model snapshot data from SpacetimeDB.
 */
export interface ModelSnapshot {
  id: string;
  timestamp: number;
  affected_weights: string[];
  reason: string;
}

/**
 * Connect to the SpacetimeDB server.
 * 
 * @param url - The URL of the SpacetimeDB server
 * @param database - The name of the database to connect to
 * @returns A SpacetimeDB client
 */
export async function connectToSpacetimeDB(url: string, database: string): Promise<any> {
  const client = new SpacetimeDBClient(url, database);
  await client.connect();
  return client;
}

/**
 * Subscribe to weight updates from SpacetimeDB.
 * 
 * @param client - The SpacetimeDB client
 * @param callback - The callback to call when weights are updated
 * @returns A function to unsubscribe
 */
export function subscribeToWeights(client: any, callback: (weights: Weight[]) => void): () => void {
  return client.subscribe('weight', (weights: Weight[]) => {
    callback(weights);
  });
}

/**
 * Subscribe to snapshot updates from SpacetimeDB.
 * 
 * @param client - The SpacetimeDB client
 * @param callback - The callback to call when snapshots are updated
 * @returns A function to unsubscribe
 */
export function subscribeToSnapshots(client: any, callback: (snapshots: ModelSnapshot[]) => void): () => void {
  return client.subscribe('model_snapshot', (snapshots: ModelSnapshot[]) => {
    callback(snapshots);
  });
}

/**
 * Create a new model snapshot in SpacetimeDB.
 * 
 * @param client - The SpacetimeDB client
 * @param reason - The reason for creating the snapshot
 * @param affectedWeights - The IDs of the weights affected by the snapshot
 * @returns The ID of the created snapshot
 */
export async function createSnapshot(client: any, reason: string, affectedWeights: string[]): Promise<string> {
  const result = await client.call('create_snapshot', {
    reason,
    affected_weights: affectedWeights,
  });
  
  return result.id;
}
