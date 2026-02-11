import { useState, useEffect } from 'react';
import { ConfigForm } from './components/ConfigForm';
import { Results } from './components/Results';
import { LiveDashboard } from './components/LiveDashboard';
import { WhatIfQuickReference } from './components/WhatIfQuickReference';
import { ScenarioManager } from './components/ScenarioManager';
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
  const [showQuickReference, setShowQuickReference] = useState(false);

  // Load template on mount
  useEffect(() => {
    async function loadTemplate() {
      try {
        console.log('Loading template from API...');
        const template = await getTemplate();
        console.log('Template loaded successfully:', template);
        setConfig(template);
      } catch (err) {
        console.error('Failed to load template:', err);
        setError(err instanceof Error ? err.message : 'Failed to load template');
      }
    }
    loadTemplate();
  }, []);

  const handleRunSimulation = async () => {
    if (!config) return;

    // Validate config structure before sending
    if (!config.simulation) {
      setError('Invalid configuration: missing simulation settings');
      return;
    }
    if (!Array.isArray(config.devices) || config.devices.length === 0) {
      setError('Invalid configuration: devices must be a non-empty array');
      return;
    }
    if (!Array.isArray(config.flows) || config.flows.length === 0) {
      setError('Invalid configuration: flows must be a non-empty array');
      return;
    }
    if (!config.output_options) {
      setError('Invalid configuration: missing output_options');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setIsPaused(false);
    try {
      console.log('Running simulation with config:', {
        deviceCount: config.devices.length,
        flowCount: config.flows.length,
        hasOutputOptions: !!config.output_options,
        simulation: config.simulation
      });
      const { results: simulationResults, simulationId: simId } = await runSimulation(
        config,
        runName || undefined,
        simulationName || undefined,
        exportToJson,
        exportDirectory || undefined
      );
      console.log('Simulation results received:', {
        hasMetadata: !!simulationResults.metadata,
        hasSummary: !!simulationResults.summary,
        hasKpis: !!simulationResults.kpis
      });
      setResults(simulationResults);
      setSimulationId(simId || null);
    } catch (err) {
      console.error('Simulation error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Simulation failed';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
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

  if (!config && !error) {
    return <div className="loading">Loading template...</div>;
  }

  if (error && !config) {
    return (
      <div className="error-container" style={{ padding: '2rem', textAlign: 'center' }}>
        <div className="error-message" style={{ 
          backgroundColor: '#fee', 
          border: '1px solid #fcc', 
          padding: '1rem',
          borderRadius: '4px',
          maxWidth: '600px',
          margin: '2rem auto'
        }}>
          <strong>Error loading template:</strong> {error}
          <br /><br />
          <button onClick={() => window.location.reload()} style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Retry
          </button>
        </div>
        <div style={{ marginTop: '2rem', color: '#666' }}>
          <p>Troubleshooting tips:</p>
          <ul style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
            <li>Verify the backend API is running on port 8000</li>
            <li>Check browser console for detailed error messages</li>
            <li>Ensure CORS is properly configured</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Generic Discrete Event Simulation Engine</h1>
          <button 
            onClick={() => setShowQuickReference(true)}
            className="guide-button-small"
            style={{ fontSize: '1rem', padding: '0.75rem 1.5rem' }}
          >
            📖 What-If Analysis Guide
          </button>
        </div>
      </header>

      {showQuickReference && (
        <WhatIfQuickReference onClose={() => setShowQuickReference(false)} />
      )}

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

          <ScenarioManager 
            onLoad={(loadedConfig, scenarioName) => {
              setConfig(loadedConfig);
              if (scenarioName) {
                setSimulationName(scenarioName);
              }
            }}
            currentConfig={config}
          />

          {config ? (
            <ConfigForm config={config} onChange={setConfig} />
          ) : (
            <div className="loading-message">Loading configuration template...</div>
          )}

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
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
