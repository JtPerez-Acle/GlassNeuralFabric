/**
 * Tests for the WeightService.
 * 
 * These tests follow the Test Driven Development approach:
 * 1. Write a failing test
 * 2. Implement minimal code to make the test pass
 * 3. Refactor while maintaining passing tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WeightService } from './WeightService';
import { Weight } from '../types';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('WeightService', () => {
  let service: WeightService;
  
  beforeEach(() => {
    service = new WeightService('http://localhost:5000');
    vi.clearAllMocks();
  });
  
  afterEach(() => {
    vi.resetAllMocks();
  });
  
  it('should fetch weights', async () => {
    // Arrange
    const mockWeights: Weight[] = [
      {
        id: 'layer1.w1',
        value: 0.5,
        delta: 0.1,
        timestamp: 1625097600000,
        origin_sample: 'sample1',
        agent_id: null,
      },
    ];
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWeights,
    });
    
    // Act
    const result = await service.getWeights();
    
    // Assert
    expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/weights');
    expect(result).toEqual(mockWeights);
  });
  
  it('should fetch weights by layer', async () => {
    // Arrange
    const mockWeights: Weight[] = [
      {
        id: 'layer1.w1',
        value: 0.5,
        delta: 0.1,
        timestamp: 1625097600000,
        origin_sample: 'sample1',
        agent_id: null,
      },
    ];
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWeights,
    });
    
    // Act
    const result = await service.getWeightsByLayer('layer1');
    
    // Assert
    expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/weights/layer/layer1');
    expect(result).toEqual(mockWeights);
  });
  
  it('should fetch weights by time range', async () => {
    // Arrange
    const mockWeights: Weight[] = [
      {
        id: 'layer1.w1',
        value: 0.5,
        delta: 0.1,
        timestamp: 1625097600000,
        origin_sample: 'sample1',
        agent_id: null,
      },
    ];
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWeights,
    });
    
    const start = 1625097500000;
    const end = 1625097700000;
    
    // Act
    const result = await service.getWeightsByTimeRange(start, end);
    
    // Assert
    expect(mockFetch).toHaveBeenCalledWith(
      `http://localhost:5000/weights/time?start=${start}&end=${end}`
    );
    expect(result).toEqual(mockWeights);
  });
  
  it('should fetch significant weights', async () => {
    // Arrange
    const mockWeights: Weight[] = [
      {
        id: 'layer1.w1',
        value: 0.5,
        delta: 0.6,
        timestamp: 1625097600000,
        origin_sample: 'sample1',
        agent_id: null,
      },
    ];
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWeights,
    });
    
    // Act
    const result = await service.getSignificantWeights(0.5);
    
    // Assert
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:5000/weights/significant?threshold=0.5'
    );
    expect(result).toEqual(mockWeights);
  });
  
  it('should handle fetch errors', async () => {
    // Arrange
    mockFetch.mockRejectedValueOnce(new Error('Network error'));
    
    // Act & Assert
    await expect(service.getWeights()).rejects.toThrow('Failed to fetch weights: Network error');
  });
  
  it('should handle non-ok responses', async () => {
    // Arrange
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });
    
    // Act & Assert
    await expect(service.getWeights()).rejects.toThrow(
      'Failed to fetch weights: 500 Internal Server Error'
    );
  });
  
  it('should subscribe to weight updates', () => {
    // Arrange
    const mockSocket = {
      addEventListener: vi.fn(),
      send: vi.fn(),
      close: vi.fn(),
    };
    
    // Mock WebSocket constructor
    global.WebSocket = vi.fn(() => mockSocket) as any;
    
    const callback = vi.fn();
    
    // Act
    const unsubscribe = service.subscribeToWeightUpdates(callback);
    
    // Assert
    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:5000/weights/subscribe');
    expect(mockSocket.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
    
    // Test message handling
    const messageHandler = mockSocket.addEventListener.mock.calls.find(
      call => call[0] === 'message'
    )[1];
    
    const mockWeight: Weight = {
      id: 'layer1.w1',
      value: 0.5,
      delta: 0.1,
      timestamp: 1625097600000,
      origin_sample: 'sample1',
      agent_id: null,
    };
    
    messageHandler({ data: JSON.stringify(mockWeight) });
    expect(callback).toHaveBeenCalledWith(mockWeight);
    
    // Test unsubscribe
    unsubscribe();
    expect(mockSocket.close).toHaveBeenCalled();
  });
});
