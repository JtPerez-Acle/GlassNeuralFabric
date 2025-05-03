/**
 * Service for interacting with the weight data API.
 * 
 * This service follows the modular architecture principles with clear interfaces
 * and single responsibility. It is developed using Test Driven Development.
 */

import { Weight } from '../types';

/**
 * Service for fetching and subscribing to weight data.
 */
export class WeightService {
  private baseUrl: string;
  
  /**
   * Create a new weight service.
   * 
   * @param baseUrl - Base URL for the API
   */
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Fetch all weights.
   * 
   * @returns Promise resolving to an array of weights
   */
  async getWeights(): Promise<Weight[]> {
    try {
      const response = await fetch(`${this.baseUrl}/weights`);
      
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch weights: ${error.message}`);
    }
  }
  
  /**
   * Fetch weights for a specific layer.
   * 
   * @param layerId - ID of the layer
   * @returns Promise resolving to an array of weights
   */
  async getWeightsByLayer(layerId: string): Promise<Weight[]> {
    try {
      const response = await fetch(`${this.baseUrl}/weights/layer/${layerId}`);
      
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch weights for layer ${layerId}: ${error.message}`);
    }
  }
  
  /**
   * Fetch weights within a time range.
   * 
   * @param start - Start timestamp (milliseconds since epoch)
   * @param end - End timestamp (milliseconds since epoch)
   * @returns Promise resolving to an array of weights
   */
  async getWeightsByTimeRange(start: number, end: number): Promise<Weight[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/weights/time?start=${start}&end=${end}`
      );
      
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch weights for time range: ${error.message}`);
    }
  }
  
  /**
   * Fetch weights with significant changes.
   * 
   * @param threshold - Threshold for significant changes
   * @returns Promise resolving to an array of weights
   */
  async getSignificantWeights(threshold: number): Promise<Weight[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/weights/significant?threshold=${threshold}`
      );
      
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch significant weights: ${error.message}`);
    }
  }
  
  /**
   * Subscribe to weight updates.
   * 
   * @param callback - Function to call when a weight is updated
   * @returns Function to unsubscribe
   */
  subscribeToWeightUpdates(callback: (weight: Weight) => void): () => void {
    const socket = new WebSocket(`ws://${this.baseUrl.replace(/^https?:\/\//, '')}/weights/subscribe`);
    
    socket.addEventListener('message', (event) => {
      const weight = JSON.parse(event.data) as Weight;
      callback(weight);
    });
    
    return () => {
      socket.close();
    };
  }
}
