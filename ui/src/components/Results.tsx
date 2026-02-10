import React from 'react';
import { SimulationResults } from '../types';

interface ResultsProps {
  results: SimulationResults | null;
}

export function Results({ results }: ResultsProps) {
  if (!results) {
    return (
      <div className="results">
        <h2>Simulation Results</h2>
        <p>Run a simulation to see results here.</p>
      </div>
    );
  }

  return (
    <div className="results">
      <h2>Simulation Results</h2>
      
      {/* Run Name and Simulation Name */}
      {results.kpis && (
        <section className="results-section">
          <div className="simulation-info">
            {results.kpis.run_name && (
              <h3 style={{ marginBottom: '0.5rem', color: '#2563eb' }}>
                Run: {results.kpis.run_name}
              </h3>
            )}
            {results.kpis.simulation_name && (
              <h4 style={{ marginTop: 0, color: '#64748b' }}>
                {results.kpis.simulation_name}
              </h4>
            )}
          </div>
        </section>
      )}

      {/* KPIs Section */}
      {results.kpis && (
        <section className="results-section">
          <h3>Key Performance Indicators</h3>
          
          {/* Device Health */}
          {results.kpis.device_health && (
            <div className="kpi-subsection">
              <h4>Device Health</h4>
              <div className="device-health-grid">
                {Object.entries(results.kpis.device_health).map(([device, health]) => (
                  <div key={device} className={`health-badge health-${health.toLowerCase()}`}>
                    <span className="device-name">{device}</span>
                    <span className={`health-status ${health.toLowerCase()}`}>{health}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Capacity Utilization */}
          {results.kpis.capacity_utilization_per_device && (
            <div className="kpi-subsection">
              <h4>Device Utilization</h4>
              <div className="utilization-list">
                {Object.entries(results.kpis.capacity_utilization_per_device).map(([device, util]) => (
                  <div key={device} className="utilization-item">
                    <span className="device-name">{device}:</span>
                    <div className="utilization-bar">
                      <div 
                        className="utilization-fill" 
                        style={{ 
                          width: `${util}%`,
                          backgroundColor: util > 85 ? '#ef4444' : util > 60 ? '#f59e0b' : '#10b981'
                        }}
                      />
                    </div>
                    <span className="utilization-value">{util.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bottleneck */}
          {results.kpis.resource_bottleneck && (
            <div className="kpi-subsection">
              <h4>Bottleneck Analysis</h4>
              <p className="bottleneck-text">
                <strong>Identified Bottleneck:</strong> {results.kpis.resource_bottleneck}
              </p>
            </div>
          )}

          {/* Optimization Suggestions */}
          {results.kpis.optimization_suggestions && results.kpis.optimization_suggestions.length > 0 && (
            <div className="kpi-subsection">
              <h4>Optimization Suggestions</h4>
              <ul className="suggestions-list">
                {results.kpis.optimization_suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
      
      {results.metadata && (
        <section className="results-section">
          <h3>Metadata</h3>
          <div className="metadata">
            <p><strong>Duration:</strong> {results.metadata.duration} seconds</p>
            <p><strong>Random Seed:</strong> {results.metadata.random_seed}</p>
            {results.metadata.start_time && (
              <p><strong>Start Time:</strong> {results.metadata.start_time}</p>
            )}
            {results.metadata.end_time && (
              <p><strong>End Time:</strong> {results.metadata.end_time}</p>
            )}
          </div>
        </section>
      )}
      
      {results.summary && (
        <section className="results-section">
          <h3>Summary</h3>
          <pre className="json-display">
            {JSON.stringify(results.summary, null, 2)}
          </pre>
        </section>
      )}
      
      {results.device_states && (
        <section className="results-section">
          <h3>Device States</h3>
          <pre className="json-display">
            {JSON.stringify(results.device_states, null, 2)}
          </pre>
        </section>
      )}
      
      {results.events && results.events.length > 0 && (
        <section className="results-section">
          <h3>Events ({results.events.length})</h3>
          <pre className="json-display">
            {JSON.stringify(results.events, null, 2)}
          </pre>
        </section>
      )}
      
      {results.history && results.history.length > 0 && (
        <section className="results-section">
          <h3>History ({results.history.length})</h3>
          <pre className="json-display">
            {JSON.stringify(results.history, null, 2)}
          </pre>
        </section>
      )}
      
      {/* Fallback: show entire results object if structure is different */}
      {!results.metadata && !results.summary && !results.device_states && (
        <section className="results-section">
          <h3>Raw Results</h3>
          <pre className="json-display">
            {JSON.stringify(results, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
}
