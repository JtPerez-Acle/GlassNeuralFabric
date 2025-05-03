import { useState, useEffect } from 'react';
import { Weight } from './types';
import { WeightService } from './services/WeightService';
import WeightGraph from './components/WeightGraph';
import './App.css';

// Create weight service
const weightService = new WeightService('http://localhost:5000');

function App() {
  const [weights, setWeights] = useState<Weight[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch initial weights
    const fetchWeights = async () => {
      try {
        setLoading(true);
        const data = await weightService.getWeights();
        setWeights(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchWeights();
    
    // Subscribe to weight updates
    const unsubscribe = weightService.subscribeToWeightUpdates((weight) => {
      setWeights((prevWeights) => {
        // Replace weight if it exists, otherwise add it
        const index = prevWeights.findIndex((w) => w.id === weight.id);
        if (index >= 0) {
          const newWeights = [...prevWeights];
          newWeights[index] = weight;
          return newWeights;
        } else {
          return [...prevWeights, weight];
        }
      });
    });
    
    // Cleanup subscription
    return () => {
      unsubscribe();
    };
  }, []);
  
  return (
    <div className="app">
      <header className="app-header">
        <h1>NeuroSpacetime</h1>
        <p>Real-time neural network visualization</p>
      </header>
      
      <main className="app-content">
        {loading && <div className="loading">Loading weights...</div>}
        {error && <div className="error">Error: {error}</div>}
        
        {!loading && !error && (
          <div className="weight-graph-container">
            <h2>Weight Graph</h2>
            <WeightGraph weights={weights} />
          </div>
        )}
      </main>
      
      <footer className="app-footer">
        <p>NeuroSpacetime &copy; 2025 NeuroSpark</p>
      </footer>
    </div>
  );
}

export default App;
