import { useState, useEffect } from 'react';
import { ConfigForm } from './components/ConfigForm';
import { Results } from './components/Results';
import { LiveDashboard } from './components/LiveDashboard';
import { SimulationConfig, SimulationResults } from './types';
import { getTemplate, runSimulation } from './api';
import './App.css';

function App() {
  const [config, setConfig] = useState<SimulationConfig | null>(null);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load template on mount
  useEffect(() => {
    async function loadTemplate() {
      try {
        const template = await getTemplate();
        setConfig(template);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load template');
      }
    }
    loadTemplate();
  }, []);

  const handleRunSimulation = async () => {
    if (!config) return;

    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const simulationResults = await runSimulation(config);
      setResults(simulationResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  if (!config) {
    return <div className="loading">Loading template...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Generic Discrete Event Simulation Engine</h1>
      </header>

      <main className="app-main">
        <div className="left-panel">
          <LiveDashboard 
            config={config}
            onRunSimulation={handleRunSimulation}
            isRunning={loading}
            results={results}
          />

          <ConfigForm config={config} onChange={setConfig} />

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        <div className="right-panel">
          <Results results={results} />
        </div>
      </main>
    </div>
  );
}

export default App;
