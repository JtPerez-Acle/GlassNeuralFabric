/**
 * Tests for the SpacetimeDB client.
 * 
 * These tests verify that the SpacetimeDB client works correctly.
 */

import { 
  connectToSpacetimeDB, 
  subscribeToWeights, 
  subscribeToSnapshots,
  createSnapshot
} from '../spacetimeClient';

// Mock the SpacetimeDB client
jest.mock('@clockworklabs/spacetimedb-sdk', () => {
  const mockClient = {
    connect: jest.fn().mockResolvedValue(undefined),
    subscribe: jest.fn().mockReturnValue(() => {}),
    call: jest.fn().mockResolvedValue({ id: 'test-snapshot-id' }),
  };
  
  return {
    SpacetimeDBClient: jest.fn().mockImplementation(() => mockClient),
  };
});

describe('SpacetimeDB Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('connectToSpacetimeDB connects to the SpacetimeDB server', async () => {
    const client = await connectToSpacetimeDB('http://localhost:3000', 'neurospace');
    
    expect(client).toBeDefined();
    expect(client.connect).toHaveBeenCalled();
  });
  
  test('subscribeToWeights subscribes to weight updates', () => {
    const client = {
      subscribe: jest.fn().mockReturnValue(() => {}),
    };
    
    const callback = jest.fn();
    const unsubscribe = subscribeToWeights(client, callback);
    
    expect(client.subscribe).toHaveBeenCalledWith('weight', expect.any(Function));
    expect(unsubscribe).toBeDefined();
  });
  
  test('subscribeToSnapshots subscribes to snapshot updates', () => {
    const client = {
      subscribe: jest.fn().mockReturnValue(() => {}),
    };
    
    const callback = jest.fn();
    const unsubscribe = subscribeToSnapshots(client, callback);
    
    expect(client.subscribe).toHaveBeenCalledWith('model_snapshot', expect.any(Function));
    expect(unsubscribe).toBeDefined();
  });
  
  test('createSnapshot creates a new snapshot', async () => {
    const client = {
      call: jest.fn().mockResolvedValue({ id: 'test-snapshot-id' }),
    };
    
    const result = await createSnapshot(client, 'Test snapshot', ['layer1.w1', 'layer1.w2']);
    
    expect(client.call).toHaveBeenCalledWith(
      'create_snapshot',
      {
        reason: 'Test snapshot',
        affected_weights: ['layer1.w1', 'layer1.w2'],
      }
    );
    
    expect(result).toBe('test-snapshot-id');
  });
});
