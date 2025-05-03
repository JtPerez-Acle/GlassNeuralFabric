/**
 * Hook for using SpacetimeDB in React components.
 * 
 * This hook provides a convenient way to connect to SpacetimeDB and
 * subscribe to weight and snapshot updates.
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  connectToSpacetimeDB, 
  subscribeToWeights, 
  subscribeToSnapshots,
  createSnapshot as createSnapshotApi,
  Weight,
  ModelSnapshot
} from '../api/spacetimeClient';

/**
 * Hook for using SpacetimeDB in React components.
 * 
 * @param url - The URL of the SpacetimeDB server
 * @param database - The name of the database to connect to
 * @returns An object with SpacetimeDB state and functions
 */
export function useSpacetimeDB(url: string, database: string) {
  const [client, setClient] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [weights, setWeights] = useState<Weight[]>([]);
  const [snapshots, setSnapshots] = useState<ModelSnapshot[]>([]);
  
  // Connect to SpacetimeDB
  useEffect(() => {
    let isMounted = true;
    
    async function connect() {
      try {
        const newClient = await connectToSpacetimeDB(url, database);
        
        if (isMounted) {
          setClient(newClient);
          setIsConnected(true);
          setIsLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setIsLoading(false);
        }
      }
    }
    
    connect();
    
    return () => {
      isMounted = false;
    };
  }, [url, database]);
  
  // Subscribe to weights and snapshots
  useEffect(() => {
    if (!client) return;
    
    const unsubscribeWeights = subscribeToWeights(client, (newWeights) => {
      setWeights((prevWeights) => {
        // Merge new weights with existing weights
        const weightMap = new Map(prevWeights.map(w => [w.id, w]));
        
        for (const weight of newWeights) {
          weightMap.set(weight.id, weight);
        }
        
        return Array.from(weightMap.values());
      });
    });
    
    const unsubscribeSnapshots = subscribeToSnapshots(client, (newSnapshots) => {
      setSnapshots((prevSnapshots) => {
        // Merge new snapshots with existing snapshots
        const snapshotMap = new Map(prevSnapshots.map(s => [s.id, s]));
        
        for (const snapshot of newSnapshots) {
          snapshotMap.set(snapshot.id, snapshot);
        }
        
        return Array.from(snapshotMap.values());
      });
    });
    
    return () => {
      unsubscribeWeights();
      unsubscribeSnapshots();
    };
  }, [client]);
  
  // Create a snapshot
  const createSnapshot = useCallback(async (reason: string, affectedWeights: string[]) => {
    if (!client) {
      throw new Error('Not connected to SpacetimeDB');
    }
    
    return await createSnapshotApi(client, reason, affectedWeights);
  }, [client]);
  
  return {
    isConnected,
    isLoading,
    error,
    weights,
    snapshots,
    createSnapshot,
  };
}
