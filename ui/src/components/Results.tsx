import React, { useState } from 'react';
import { SimulationResults } from '../types';
import { DeadlockModal } from './DeadlockModal';

interface ResultsProps {
  results: SimulationResults | null;
}

export function Results({ results }: ResultsProps) {
  const [showGuide, setShowGuide] = useState(false);
  const [showDeadlockModal, setShowDeadlockModal] = useState(false);

  // Safe rendering helper to prevent "Objects are not valid as React child" errors
  const safeRender = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  // Show deadlock modal if deadlock detected
  React.useEffect(() => {
    if (results?.status === 'deadlock_detected') {
      setShowDeadlockModal(true);
    }
  }, [results]);

  if (!results) {
    return (
      <div className="results">
        <h2>Simulation Results</h2>
        <div className="guide-prompt">
          <p>Run a simulation to see results here.</p>
          <button 
            onClick={() => setShowGuide(!showGuide)}
            className="guide-button"
          >
            📖 What-If Analysis Guide
          </button>
          {showGuide && (
            <div className="guide-panel">
              <h3>8 What-If Analysis Capabilities</h3>
              <ol>
                <li><strong>Staff Allocation</strong> - Test different staffing levels (set type="person")</li>
                <li><strong>Device Utilization</strong> - Identify bottlenecks and optimize equipment</li>
                <li><strong>Supply Variation</strong> - Model uncertainty with process_time_range</li>
                <li><strong>Process Order</strong> - Adjust dependencies and priorities</li>
                <li><strong>Product Release</strong> - Measure throughput and output</li>
                <li><strong>Constraints</strong> - Model capacity limits, gates, and recovery times</li>
                <li><strong>Outcome Forecasting</strong> - Predict future capacity needs</li>
                <li><strong>Capacity Forecasting</strong> - Test different capacity scenarios</li>
              </ol>
              <p><em>See WHAT_IF_ANALYSIS_GUIDE.md for detailed instructions on using each capability.</em></p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="results">
      <div className="results-header">
        <h2>Simulation Results</h2>
        <button 
          onClick={() => setShowGuide(!showGuide)}
          className="guide-button-small"
        >
          {showGuide ? '✖ Close Guide' : '📖 Analysis Guide'}
        </button>
      </div>

      {/* Deadlock Status Banner */}
      {results.status === 'deadlock_detected' && (
        <div className="status-banner error" style={{
          padding: '16px',
          backgroundColor: '#fef2f2',
          border: '2px solid #dc2626',
          borderRadius: '8px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>🚨</span>
            <div>
              <strong style={{ color: '#dc2626', fontSize: '16px' }}>Deadlock Detected</strong>
              <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#991b1b' }}>
                Simulation terminated due to circular dependency or timeout. Click for details.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowDeadlockModal(true)}
            style={{
              padding: '10px 20px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px'
            }}
          >
            View Details →
          </button>
        </div>
      )}

      {showGuide && (
        <div className="guide-panel active">
          <h3>What-If Analysis Quick Reference</h3>
          <div className="guide-grid">
            <div className="guide-item">
              <strong>1. Staff Allocation</strong>
              <p>Check staff utilization below. Red bars (&gt;85%) = overworked.</p>
            </div>
            <div className="guide-item">
              <strong>2. Device Utilization</strong>
              <p>See Device Utilization section. Bottleneck shows the constraint.</p>
            </div>
            <div className="guide-item">
              <strong>3. Supply Variation</strong>
              <p>Compare runs with different random seeds to see variation impact.</p>
            </div>
            <div className="guide-item">
              <strong>4. Process Order</strong>
              <p>Modify flow dependencies and compare cycle times.</p>
            </div>
            <div className="guide-item">
              <strong>5. Product Release</strong>
              <p>See Total Units Created and Current Throughput metrics.</p>
            </div>
            <div className="guide-item">
              <strong>6. Constraints</strong>
              <p>Check capacity limits and constraint violations below.</p>
            </div>
            <div className="guide-item">
              <strong>7. Outcome Forecasting</strong>
              <p>Review Optimization Suggestions for future capacity needs.</p>
            </div>
            <div className="guide-item">
              <strong>8. Capacity Forecasting</strong>
              <p>Test multiple runs with different device capacities and compare.</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Run Name and Simulation Name */}
      {results.kpis && (
        <section className="results-section">
          <div className="simulation-info">
            {results.kpis.run_name && (
              <h3 style={{ marginBottom: '0.5rem', color: '#2563eb' }}>
                Run: {safeRender(results.kpis.run_name)}
              </h3>
            )}
            {results.kpis.simulation_name && (
              <h4 style={{ marginTop: 0, color: '#64748b' }}>
                {safeRender(results.kpis.simulation_name)}
              </h4>
            )}
          </div>
        </section>
      )}

      {/* KPIs Section - Enhanced for 8 Capabilities */}
      {results.kpis && (
        <>
          {/* Capability 1: Staff Allocation Optimization */}
          <section className="results-section capability-section">
            <h3>🧑‍🔬 1. Staff Allocation Analysis</h3>
            {results.kpis.staff_count !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Total Staff:</span>
                <span className="kpi-value">{safeRender(results.kpis.staff_count)}</span>
              </div>
            )}
            {results.kpis.staff_utilization !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Staff Utilization:</span>
                <span className="kpi-value">{safeRender(results.kpis.staff_utilization)}%</span>
              </div>
            )}
            {results.kpis.capacity_utilization_per_device && (
              <div className="kpi-subsection">
                <h4>Staff/Device Breakdown</h4>
                <div className="utilization-list">
                  {Object.entries(results.kpis.capacity_utilization_per_device).map(([device, util]) => (
                    <div key={device} className="utilization-item">
                      <span className="device-name">{device}:</span>
                      <div className="utilization-bar">
                        <div 
                          className="utilization-fill" 
                          style={{ 
                            width: `${util}%`,
                            backgroundColor: util > 85 ? '#E31837' : util > 60 ? '#FF6F40' : '#7FCC72'
                          }}
                        />
                      </div>
                      <span className="utilization-value">{util.toFixed(1)}%</span>
                      {util > 85 && <span className="warning-badge">⚠️ Overloaded</span>}
                      {util < 30 && <span className="info-badge">ℹ️ Underutilized</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Capability 2: Device Utilization Optimization */}
          <section className="results-section capability-section">
            <h3>🏭 2. Device Utilization Optimization</h3>
            
            {/* Device Health */}
            {results.kpis.device_health && (
              <div className="kpi-subsection">
                <h4>Device Health Status</h4>
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

            {/* Bottleneck */}
            {results.kpis.resource_bottleneck && (
              <div className="kpi-subsection bottleneck-highlight">
                <h4>⚠️ Bottleneck Identified</h4>
                <p className="bottleneck-text">
                  <strong>{safeRender(results.kpis.resource_bottleneck)}</strong> is constraining your throughput.
                </p>
                <p className="help-text">
                  💡 Focus optimization efforts here for maximum impact.
                </p>
              </div>
            )}

            {/* Idle Time */}
            {results.kpis.idle_time_percentage !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Average Idle Time:</span>
                <span className="kpi-value">{safeRender(results.kpis.idle_time_percentage)}%</span>
              </div>
            )}
          </section>

          {/* Capability 3: Supply Variation Analysis */}
          <section className="results-section capability-section">
            <h3>📊 3. Supply Variation Analysis</h3>
            {results.kpis.supply_variation !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Supply Variation:</span>
                <span className="kpi-value">
                  {typeof results.kpis.supply_variation === 'object' 
                    ? JSON.stringify(results.kpis.supply_variation) 
                    : results.kpis.supply_variation}
                </span>
              </div>
            )}
            {results.kpis.input_supply_rate !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Input Supply Rate:</span>
                <span className="kpi-value">
                  {typeof results.kpis.input_supply_rate === 'object' 
                    ? JSON.stringify(results.kpis.input_supply_rate) 
                    : results.kpis.input_supply_rate}
                </span>
              </div>
            )}
            {results.metadata?.random_seed !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Random Seed Used:</span>
                <span className="kpi-value">{safeRender(results.metadata.random_seed)}</span>
                <span className="help-text">Run with different seeds to test variability</span>
              </div>
            )}
          </section>

          {/* Capability 4: Process Order Adjustments */}
          <section className="results-section capability-section">
            <h3>🔄 4. Process Order Impact</h3>
            {results.kpis.average_cycle_time !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Average Cycle Time:</span>
                <span className="kpi-value">{safeRender(results.kpis.average_cycle_time)}s</span>
              </div>
            )}
            {results.kpis.time_to_first_unit !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Time to First Unit:</span>
                <span className="kpi-value">{safeRender(results.kpis.time_to_first_unit)}s</span>
              </div>
            )}
            <p className="help-text">
              💡 Modify flow dependencies to test different process sequences
            </p>
          </section>

          {/* Capability 5: Product Release Measurement */}
          <section className="results-section capability-section">
            <h3>📦 5. Product Release Measurement</h3>
            {results.kpis.total_units_created !== undefined && (
              <div className="kpi-row highlight">
                <span className="kpi-label">Total Units Created:</span>
                <span className="kpi-value large">{safeRender(results.kpis.total_units_created)}</span>
              </div>
            )}
            {results.kpis.product_release_volume !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Product Release Volume:</span>
                <span className="kpi-value">
                  {typeof results.kpis.product_release_volume === 'object' 
                    ? JSON.stringify(results.kpis.product_release_volume) 
                    : results.kpis.product_release_volume}
                </span>
              </div>
            )}
            {results.kpis.current_throughput !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Current Throughput:</span>
                <span className="kpi-value">{safeRender(results.kpis.current_throughput)} units/hour</span>
              </div>
            )}
            {results.kpis.peak_throughput !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Peak Throughput:</span>
                <span className="kpi-value">{safeRender(results.kpis.peak_throughput)} units/hour</span>
              </div>
            )}
          </section>

          {/* Capability 6: Constraint Modelling */}
          <section className="results-section capability-section">
            <h3>🚧 6. Constraint Modeling</h3>
            {results.kpis.constraint_violations !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Constraint Violations:</span>
                <span className="kpi-value">{safeRender(results.kpis.constraint_violations)}</span>
              </div>
            )}
            {results.kpis.max_queue_length !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Max Queue Length:</span>
                <span className="kpi-value">{safeRender(results.kpis.max_queue_length)}</span>
              </div>
            )}
            {results.kpis.units_in_queue !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Current Units in Queue:</span>
                <span className="kpi-value">{safeRender(results.kpis.units_in_queue)}</span>
              </div>
            )}
            <p className="help-text">
              💡 Configure capacity limits, gates, and recovery times to model constraints
            </p>
          </section>

          {/* Capability 7: Outcome Forecasting */}
          <section className="results-section capability-section">
            <h3>🔮 7. Outcome Forecasting</h3>
            {results.kpis.demand_forecast !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Demand Forecast:</span>
                <span className="kpi-value">
                  {typeof results.kpis.demand_forecast === 'object' 
                    ? JSON.stringify(results.kpis.demand_forecast) 
                    : results.kpis.demand_forecast}
                </span>
              </div>
            )}
            {/* Only show optimization suggestions for successful simulations, not deadlocks */}
            {results.status !== 'deadlock_detected' && results.kpis.optimization_suggestions && results.kpis.optimization_suggestions.length > 0 && (
              <div className="kpi-subsection">
                <h4>💡 Optimization Suggestions</h4>
                <ul className="suggestions-list">
                  {results.kpis.optimization_suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {/* Capability 8: Productivity and Capacity Forecasting */}
          <section className="results-section capability-section">
            <h3>📈 8. Productivity & Capacity Forecasting</h3>
            {results.kpis.comparison_to_baseline !== undefined && (
              <div className="kpi-subsection">
                <h4>Baseline Comparison</h4>
                {typeof results.kpis.comparison_to_baseline === 'object' && results.kpis.comparison_to_baseline !== null ? (
                  <>
                    {(results.kpis.comparison_to_baseline as any).current !== undefined && (
                      <div className="kpi-row">
                        <span className="kpi-label">Current:</span>
                        <span className="kpi-value">{safeRender((results.kpis.comparison_to_baseline as any).current)}</span>
                      </div>
                    )}
                    {(results.kpis.comparison_to_baseline as any).baseline !== undefined && (
                      <div className="kpi-row">
                        <span className="kpi-label">Baseline:</span>
                        <span className="kpi-value">{safeRender((results.kpis.comparison_to_baseline as any).baseline)}</span>
                      </div>
                    )}
                    {(results.kpis.comparison_to_baseline as any).difference !== undefined && (
                      <div className="kpi-row">
                        <span className="kpi-label">Difference:</span>
                        <span className={`kpi-value ${(results.kpis.comparison_to_baseline as any).difference > 0 ? 'positive' : 'negative'}`}>
                          {(results.kpis.comparison_to_baseline as any).difference > 0 ? '+' : ''}{safeRender((results.kpis.comparison_to_baseline as any).difference)}
                        </span>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="kpi-row">
                    <span className="kpi-label">vs Baseline:</span>
                    <span className="kpi-value">{safeRender(results.kpis.comparison_to_baseline)}</span>
                  </div>
                )}
              </div>
            )}
            {results.kpis.cost_per_unit !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Cost per Unit:</span>
                <span className="kpi-value">${safeRender(results.kpis.cost_per_unit)}</span>
              </div>
            )}
            {results.kpis.total_operating_cost !== undefined && (
              <div className="kpi-row">
                <span className="kpi-label">Total Operating Cost:</span>
                <span className="kpi-value">${safeRender(results.kpis.total_operating_cost)}</span>
              </div>
            )}
            <div className="capacity-test-helper">
              <p className="help-text">
                💡 <strong>Quick Capacity Test:</strong> Use different device capacities and compare these metrics:
              </p>
              <ul className="help-list">
                <li>Total Units Created (higher = better)</li>
                <li>Average Cycle Time (lower = better)</li>
                <li>Cost per Unit (lower = better)</li>
              </ul>
            </div>
          </section>
        </>
      )}

      {/* Legacy KPI Section (for any KPIs not covered above) */}
      {results.kpis && (
        <section className="results-section">
          <h3>Additional Metrics</h3>
          
          {/* Quality Metrics */}
          {results.kpis.quality_pass_rate !== undefined && (
            <div className="kpi-row">
              <span className="kpi-label">Quality Pass Rate:</span>
              <span className="kpi-value">{safeRender(results.kpis.quality_pass_rate)}%</span>
            </div>
          )}
          {results.kpis.failed_units_count !== undefined && (
            <div className="kpi-row">
              <span className="kpi-label">Failed Units:</span>
              <span className="kpi-value">{safeRender(results.kpis.failed_units_count)}</span>
            </div>
          )}
          {results.kpis.waste_rate !== undefined && (
            <div className="kpi-row">
              <span className="kpi-label">Waste Rate:</span>
              <span className="kpi-value">{safeRender(results.kpis.waste_rate)}%</span>
            </div>
          )}
        </section>
      )}
      
      {results.metadata && (
        <section className="results-section">
          <h3>Metadata</h3>
          <div className="metadata">
            <p><strong>Duration:</strong> {safeRender(results.metadata.duration)} seconds</p>
            <p><strong>Random Seed:</strong> {safeRender(results.metadata.random_seed)}</p>
            {results.metadata.start_time && (
              <p><strong>Start Time:</strong> {safeRender(results.metadata.start_time)}</p>
            )}
            {results.metadata.end_time && (
              <p><strong>End Time:</strong> {safeRender(results.metadata.end_time)}</p>
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

      {/* Deadlock Modal (FR22) */}
      {showDeadlockModal && results.status === 'deadlock_detected' && (
        <DeadlockModal 
          results={results} 
          onClose={() => setShowDeadlockModal(false)} 
        />
      )}
    </div>
  );
}
