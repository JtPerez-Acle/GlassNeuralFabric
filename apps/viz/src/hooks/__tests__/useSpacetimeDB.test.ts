/**
 * Tests for the useSpacetimeDB hook.
 * 
 * These tests verify that the useSpacetimeDB hook works correctly.
 */

import { renderHook, act } from '@testing-library/react-hooks';
import { useSpacetimeDB } from '../useSpacetimeDB';

// Mock the SpacetimeDB client
jest.mock('../../api/spacetimeClient', () => {
  const mockClient = {
    connect: jest.fn().mockResolvedValue(undefined),
    subscribe: jest.fn().mockReturnValue(() => {}),
    call: jest.fn().mockResolvedValue({ id: 'test-snapshot-id' }),
  };
  
  return {
    connectToSpacetimeDB: jest.fn().mockResolvedValue(mockClient),
    subscribeToWeights: jest.fn().mockReturnValue(() => {}),
    subscribeToSnapshots: jest.fn().mockReturnValue(() => {}),
    createSnapshot: jest.fn().mockResolvedValue('test-snapshot-id'),
  };
});

describe('useSpacetimeDB', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('connects to SpacetimeDB on mount', async () => {
    const { result, waitForNextUpdate } = renderHook(() => 
      useSpacetimeDB('http://localhost:3000', 'neurospace')
    );
    
    // Initial state
    expect(result.current.isConnected).toBe(false);
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBeNull();
    
    // Wait for connection
    await waitForNextUpdate();
    
    // Connected state
    expect(result.current.isConnected).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });
  
  test('handles connection errors', async () => {
    const error = new Error('Connection failed');
    require('../../api/spacetimeClient').connectToSpacetimeDB.mockRejectedValueOnce(error);
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSpacetimeDB('http://localhost:3000', 'neurospace')
    );
    
    // Initial state
    expect(result.current.isConnected).toBe(false);
    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBeNull();
    
    // Wait for error
    await waitForNextUpdate();
    
    // Error state
    expect(result.current.isConnected).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(error);
  });
  
  test('subscribes to weights and snapshots on connection', async () => {
    const { subscribeToWeights, subscribeToSnapshots } = require('../../api/spacetimeClient');
    
    const { waitForNextUpdate } = renderHook(() => 
      useSpacetimeDB('http://localhost:3000', 'neurospace')
    );
    
    // Wait for connection
    await waitForNextUpdate();
    
    // Check subscriptions
    expect(subscribeToWeights).toHaveBeenCalled();
    expect(subscribeToSnapshots).toHaveBeenCalled();
  });
  
  test('creates a snapshot', async () => {
    const { createSnapshot } = require('../../api/spacetimeClient');
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useSpacetimeDB('http://localhost:3000', 'neurospace')
    );
    
    // Wait for connection
    await waitForNextUpdate();
    
    // Create a snapshot
    let snapshotId: string | null = null;
    await act(async () => {
      snapshotId = await result.current.createSnapshot('Test snapshot', ['layer1.w1']);
    });
    
    // Check snapshot creation
    expect(createSnapshot).toHaveBeenCalledWith(
      expect.anything(),
      'Test snapshot',
      ['layer1.w1']
    );
    
    expect(snapshotId).toBe('test-snapshot-id');
  });
});
