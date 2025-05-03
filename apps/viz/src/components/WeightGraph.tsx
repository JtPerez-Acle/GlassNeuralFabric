/**
 * WeightGraph component for visualizing neural network weights.
 * 
 * This component follows the modular architecture principles with clear interfaces
 * and single responsibility. It is developed using Test Driven Development.
 */

import React, { useEffect, useRef, useMemo } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';
import { Weight } from '../types';

// Register the cola layout
cytoscape.use(cola);

// Threshold for significant weight changes
const SIGNIFICANCE_THRESHOLD = 0.5;

interface WeightGraphProps {
  weights: Weight[];
  width?: string;
  height?: string;
  onNodeClick?: (weightId: string) => void;
}

/**
 * Component for visualizing neural network weights as a graph.
 */
const WeightGraph: React.FC<WeightGraphProps> = ({
  weights,
  width = '100%',
  height = '600px',
  onNodeClick,
}) => {
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  // Convert weights to cytoscape elements
  const elements = useMemo(() => {
    if (!weights.length) return [];
    
    const nodes: cytoscape.NodeDefinition[] = [];
    const edges: cytoscape.EdgeDefinition[] = [];
    const layers = new Set<string>();
    
    // Extract layer information from weight IDs
    weights.forEach(weight => {
      const layerId = weight.id.split('.')[0];
      layers.add(layerId);
    });
    
    // Create layer nodes
    layers.forEach(layerId => {
      nodes.push({
        data: {
          id: layerId,
          label: layerId,
          type: 'layer',
        },
      });
    });
    
    // Create weight nodes and edges
    weights.forEach(weight => {
      const layerId = weight.id.split('.')[0];
      
      // Add weight node
      nodes.push({
        data: {
          id: weight.id,
          label: weight.id.split('.').slice(1).join('.'),
          type: 'weight',
          value: weight.value,
          delta: weight.delta,
          timestamp: weight.timestamp,
          significant: Math.abs(weight.delta) >= SIGNIFICANCE_THRESHOLD,
        },
      });
      
      // Add edge from layer to weight
      edges.push({
        data: {
          id: `${layerId}-${weight.id}`,
          source: layerId,
          target: weight.id,
        },
      });
    });
    
    return [...nodes, ...edges];
  }, [weights]);
  
  // Define graph style
  const style = [
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'color': '#fff',
        'font-size': '12px',
      },
    },
    {
      selector: 'node[type="layer"]',
      style: {
        'background-color': '#4285f4',
        'shape': 'rectangle',
        'width': '120px',
        'height': '40px',
        'font-weight': 'bold',
        'font-size': '14px',
      },
    },
    {
      selector: 'node[type="weight"]',
      style: {
        'background-color': (ele: any) => {
          const value = ele.data('value');
          // Color based on weight value (red for negative, green for positive)
          if (value < 0) {
            return `rgb(${Math.min(255, Math.abs(value) * 255)}, 0, 0)`;
          } else {
            return `rgb(0, ${Math.min(255, value * 255)}, 0)`;
          }
        },
        'shape': 'ellipse',
        'width': '30px',
        'height': '30px',
      },
    },
    {
      selector: 'node[type="weight"][significant]',
      style: {
        'border-width': '3px',
        'border-color': '#ff9800',
        'border-style': 'solid',
        'width': '40px',
        'height': '40px',
        'font-weight': 'bold',
      },
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#ccc',
        'curve-style': 'bezier',
      },
    },
  ];
  
  // Define layout
  const layout = {
    name: 'cose',
    nodeDimensionsIncludeLabels: true,
    animate: true,
    refresh: 20,
    fit: true,
    padding: 30,
    randomize: false,
    componentSpacing: 100,
    nodeRepulsion: 400000,
    nodeOverlap: 10,
    idealEdgeLength: 100,
    edgeElasticity: 100,
    nestingFactor: 5,
    gravity: 80,
  };
  
  // Set up event handlers
  useEffect(() => {
    if (cyRef.current) {
      // Remove previous event handlers
      cyRef.current.removeAllListeners();
      
      // Add click handler for nodes
      if (onNodeClick) {
        cyRef.current.on('tap', 'node[type="weight"]', (event) => {
          const node = event.target;
          onNodeClick(node.id());
        });
      }
      
      // Fit the graph to the viewport
      cyRef.current.fit();
    }
  }, [onNodeClick]);
  
  return (
    <div data-testid="weight-graph" style={{ width, height }}>
      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: '100%' }}
        stylesheet={style}
        layout={layout}
        cy={(cy) => {
          cyRef.current = cy;
        }}
      />
    </div>
  );
};

export default WeightGraph;
