import { useState, useEffect } from 'react';
import { ConfigForm } from './components/ConfigForm';
import { Results } from './components/Results';
import { LiveDashboard } from './components/LiveDashboard';
import { SimulationConfig, SimulationResults } from './types';
import { getTemplate, runSimulation, pauseSimulation, resumeSimulation } from './api';
import './App.css';

function App() {
  const [config, setConfig] = useState<SimulationConfig | null>(null);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runName, setRunName] = useState<string>('');
  const [simulationName, setSimulationName] = useState<string>('');
  const [exportToJson, setExportToJson] = useState<boolean>(true);
  const [exportDirectory, setExportDirectory] = useState<string>('simulation_results');
  const [simulationId, setSimulationId] = useState<string | null>(null);
  const [isPaused, setIsPaused] = useState(false);

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
    setIsPaused(false);
    try {
      const { results: simulationResults, simulationId: simId } = await runSimulation(
        config,
        runName || undefined,
        simulationName || undefined,
        exportToJson,
        exportDirectory || undefined
      );
      setResults(simulationResults);
      setSimulationId(simId || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
      setSimulationId(null);
    }
  };

  const handlePause = async () => {
    if (!simulationId) return;
    
    try {
      await pauseSimulation(simulationId);
      setIsPaused(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause');
    }
  };

  const handleResume = async () => {
    if (!simulationId) return;
    
    try {
      await resumeSimulation(simulationId);
      setIsPaused(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume');
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
            onPause={handlePause}
            onResume={handleResume}
            isRunning={loading}
            isPaused={isPaused}
            results={results}
            runName={runName}
            setRunName={setRunName}
            simulationName={simulationName}
            setSimulationName={setSimulationName}
            exportToJson={exportToJson}
            setExportToJson={setExportToJson}
            exportDirectory={exportDirectory}
            setExportDirectory={setExportDirectory}
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
