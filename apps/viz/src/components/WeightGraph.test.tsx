/**
 * Tests for the WeightGraph component.
 * 
 * These tests follow the Test Driven Development approach:
 * 1. Write a failing test
 * 2. Implement minimal code to make the test pass
 * 3. Refactor while maintaining passing tests
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import WeightGraph from './WeightGraph';
import { Weight } from '../types';

// Mock cytoscape
vi.mock('react-cytoscapejs', () => ({
  default: vi.fn(({ elements, style, layout, cy }) => {
    // Call the cy callback with a mock cytoscape instance
    if (cy) {
      cy({
        on: vi.fn(),
        elements: vi.fn(() => ({
          style: vi.fn(),
        })),
        style: vi.fn(),
        layout: vi.fn(() => ({
          run: vi.fn(),
        })),
        center: vi.fn(),
        fit: vi.fn(),
      });
    }
    
    return (
      <div data-testid="cytoscape-mock">
        <div data-testid="cytoscape-elements">{JSON.stringify(elements)}</div>
        <div data-testid="cytoscape-style">{JSON.stringify(style)}</div>
        <div data-testid="cytoscape-layout">{JSON.stringify(layout)}</div>
      </div>
    );
  }),
}));

describe('WeightGraph', () => {
  // Sample weights for testing
  const sampleWeights: Weight[] = [
    {
      id: 'layer1.w1',
      value: 0.5,
      delta: 0.1,
      timestamp: 1625097600000,
      origin_sample: 'sample1',
      agent_id: null,
    },
    {
      id: 'layer1.w2',
      value: -0.3,
      delta: -0.2,
      timestamp: 1625097600000,
      origin_sample: 'sample1',
      agent_id: null,
    },
    {
      id: 'layer2.w1',
      value: 0.7,
      delta: 0.6,
      timestamp: 1625097600000,
      origin_sample: 'sample1',
      agent_id: null,
    },
  ];
  
  it('renders without crashing', () => {
    // Arrange & Act
    render(<WeightGraph weights={[]} />);
    
    // Assert
    expect(screen.getByTestId('weight-graph')).toBeInTheDocument();
  });
  
  it('renders with weights', () => {
    // Arrange & Act
    render(<WeightGraph weights={sampleWeights} />);
    
    // Assert
    const elementsJson = screen.getByTestId('cytoscape-elements').textContent;
    const elements = JSON.parse(elementsJson || '[]');
    
    // Should have nodes for layers and weights
    expect(elements.length).toBeGreaterThan(0);
    
    // Check for layer nodes
    const layerNodes = elements.filter((el: any) => 
      el.data && el.data.id && el.data.id.startsWith('layer')
    );
    expect(layerNodes.length).toBeGreaterThan(0);
    
    // Check for weight nodes
    const weightNodes = elements.filter((el: any) => 
      el.data && el.data.id && el.data.id.includes('.w')
    );
    expect(weightNodes.length).toBe(3);
  });
  
  it('applies different styles based on weight values', () => {
    // Arrange & Act
    render(<WeightGraph weights={sampleWeights} />);
    
    // Assert
    const styleJson = screen.getByTestId('cytoscape-style').textContent;
    const style = JSON.parse(styleJson || '[]');
    
    // Should have styles for nodes
    expect(style.length).toBeGreaterThan(0);
    
    // Check for node color style
    const nodeColorStyle = style.find((s: any) => 
      s.selector === 'node' && s.style && s.style.backgroundColor
    );
    expect(nodeColorStyle).toBeDefined();
  });
  
  it('uses a force-directed layout', () => {
    // Arrange & Act
    render(<WeightGraph weights={sampleWeights} />);
    
    // Assert
    const layoutJson = screen.getByTestId('cytoscape-layout').textContent;
    const layout = JSON.parse(layoutJson || '{}');
    
    // Should use a force-directed layout
    expect(layout.name).toBe('cose');
  });
  
  it('handles empty weights array', () => {
    // Arrange & Act
    render(<WeightGraph weights={[]} />);
    
    // Assert
    const elementsJson = screen.getByTestId('cytoscape-elements').textContent;
    const elements = JSON.parse(elementsJson || '[]');
    
    // Should have no elements
    expect(elements.length).toBe(0);
  });
  
  it('updates when weights change', () => {
    // Arrange
    const { rerender } = render(<WeightGraph weights={[]} />);
    
    // Initial render should have no weight nodes
    let elementsJson = screen.getByTestId('cytoscape-elements').textContent;
    let elements = JSON.parse(elementsJson || '[]');
    expect(elements.length).toBe(0);
    
    // Act - update with weights
    rerender(<WeightGraph weights={sampleWeights} />);
    
    // Assert
    elementsJson = screen.getByTestId('cytoscape-elements').textContent;
    elements = JSON.parse(elementsJson || '[]');
    
    // Should now have elements
    expect(elements.length).toBeGreaterThan(0);
    
    // Check for weight nodes
    const weightNodes = elements.filter((el: any) => 
      el.data && el.data.id && el.data.id.includes('.w')
    );
    expect(weightNodes.length).toBe(3);
  });
  
  it('applies highlight style to significant weights', () => {
    // Arrange
    const significantWeights: Weight[] = [
      {
        id: 'layer1.w1',
        value: 0.5,
        delta: 0.9, // Large delta
        timestamp: 1625097600000,
        origin_sample: 'sample1',
        agent_id: null,
      },
    ];
    
    // Act
    render(<WeightGraph weights={significantWeights} />);
    
    // Assert
    const styleJson = screen.getByTestId('cytoscape-style').textContent;
    const style = JSON.parse(styleJson || '[]');
    
    // Should have a style for significant weights
    const significantStyle = style.find((s: any) => 
      s.selector.includes('significant')
    );
    expect(significantStyle).toBeDefined();
  });
});
