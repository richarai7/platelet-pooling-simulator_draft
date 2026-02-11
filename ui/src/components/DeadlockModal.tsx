import { SimulationResults } from '../types';
import './DeadlockModal.css';

interface DeadlockModalProps {
  results: SimulationResults;
  onClose: () => void;
}

export function DeadlockModal({ results, onClose }: DeadlockModalProps) {
  if (results.status !== 'deadlock_detected' || !results.error) {
    return null;
  }

  const error = results.error;
  const deadlockInfo = error.deadlock_info;

  const renderWaitGraph = () => {
    if (!deadlockInfo.wait_graph || Object.keys(deadlockInfo.wait_graph).length === 0) {
      return <p style={{ color: '#6b7280' }}>No wait graph available</p>;
    }

    return (
      <div className="wait-graph">
        {Object.entries(deadlockInfo.wait_graph).map(([device, waitingFor]) => (
          <div key={device} className="wait-edge">
            <span className="device-node">{device}</span>
            <span className="arrow">→</span>
            <span className="device-node">
              {Array.isArray(waitingFor) ? waitingFor.join(', ') : waitingFor}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const renderWaitChain = () => {
    if (!deadlockInfo.wait_chain || deadlockInfo.wait_chain.length === 0) {
      return null;
    }

    return (
      <div className="wait-chain">
        <h4>Circular Dependency Chain:</h4>
        <div className="chain-visualization">
          {deadlockInfo.wait_chain.map((item, idx) => (
            <div key={idx} className="chain-step">
              <span className="step-badge">{idx + 1}</span>
              <span className="step-text">{item}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTimeoutDevices = () => {
    const timeoutDevices = deadlockInfo.timeout_devices || deadlockInfo.blocked_devices;
    if (!timeoutDevices || timeoutDevices.length === 0) {
      return null;
    }

    return (
      <div className="timeout-devices">
        <h4>Blocked Devices:</h4>
        <table className="device-table">
          <thead>
            <tr>
              <th>Device ID</th>
              <th>Blocked Since (sim time)</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {timeoutDevices.map((dev: any) => {
              const duration = deadlockInfo.detection_time - dev.blocked_since;
              return (
                <tr key={dev.device_id}>
                  <td><strong>{dev.device_id}</strong></td>
                  <td>{dev.blocked_since.toFixed(1)}s</td>
                  <td className={duration >= 300 ? 'timeout-exceeded' : ''}>
                    {duration.toFixed(1)}s
                    {duration >= 300 && ' ⚠️'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content deadlock-modal" onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>
              <span className="error-icon">🚨</span>
              Deadlock Detected
            </h2>
            <p className="error-subtitle">
              Simulation terminated at T={deadlockInfo.detection_time.toFixed(1)}s
            </p>
          </div>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        {/* Error Message */}
        <div className="error-message">
          <div className="message-badge">
            {deadlockInfo.deadlock_type === 'timeout' ? '⏱️ Timeout' : '🔄 Circular Wait'}
          </div>
          <p>{error.message}</p>
        </div>

        {/* Main Content */}
        <div className="modal-body">
          
          {/* Deadlock Type & Details */}
          <div className="info-section">
            <h3>Deadlock Details</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Type:</label>
                <span className="badge">{deadlockInfo.deadlock_type}</span>
              </div>
              <div className="info-item">
                <label>Detection Time:</label>
                <span>{deadlockInfo.detection_time.toFixed(2)}s</span>
              </div>
              <div className="info-item">
                <label>Involved Devices:</label>
                <span>{deadlockInfo.involved_devices.join(', ')}</span>
              </div>
              <div className="info-item">
                <label>Involved Flows:</label>
                <span>{deadlockInfo.involved_flows.join(', ')}</span>
              </div>
            </div>
          </div>

          {/* Wait Chain (for circular wait) */}
          {renderWaitChain()}

          {/* Wait Graph Visualization */}
          <div className="info-section">
            <h3>Wait-For Graph</h3>
            <div className="graph-description">
              <p>Shows which devices are waiting for which resources:</p>
            </div>
            {renderWaitGraph()}
          </div>

          {/* Blocked Devices Table */}
          {renderTimeoutDevices()}

          {/* Simulation Summary */}
          <div className="info-section">
            <h3>Simulation Summary (Partial Results)</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <label>Total Events:</label>
                <span>{results.summary?.total_events || 0}</span>
              </div>
              <div className="summary-item">
                <label>Flows Completed:</label>
                <span>{results.summary?.total_flows_completed || 0}</span>
              </div>
              <div className="summary-item">
                <label>Simulation Time:</label>
                <span>{results.summary?.simulation_time_seconds?.toFixed(2) || 0}s</span>
              </div>
              <div className="summary-item">
                <label>Execution Time:</label>
                <span>{results.execution_time?.toFixed(3) || results.summary?.execution_time_seconds?.toFixed(3) || 0}s</span>
              </div>
            </div>
          </div>

          {/* Suggestions */}
          <div className="suggestions-section">
            <h3>💡 Suggestions to Resolve Deadlock</h3>
            <ul>
              {deadlockInfo.deadlock_type === 'timeout' && (
                <>
                  <li><strong>Review flow dependencies:</strong> Flows may be waiting indefinitely for resources that never become available</li>
                  <li><strong>Check device capacities:</strong> Ensure critical devices can handle concurrent flows (capacity ≥ max concurrent demand)</li>
                  <li><strong>Verify offset configurations:</strong> Incorrect start-to-start offsets may cause flows to block indefinitely</li>
                  <li><strong>Look for backpressure:</strong> Downstream bottlenecks may prevent upstream devices from releasing resources</li>
                  <li><strong>Consider adding timeout handling:</strong> Allow flows to fail gracefully instead of blocking forever</li>
                </>
              )}
              {deadlockInfo.deadlock_type === 'circular_wait' && (
                <>
                  <li><strong>Break the circular dependency:</strong> The wait cycle <code>{deadlockInfo.wait_chain?.join(' → ')}</code> must be eliminated</li>
                  <li><strong>Reorder flow execution:</strong> Change dependency order or add sequencing constraints</li>
                  <li><strong>Increase capacity strategically:</strong> Add capacity to <em>one</em> device in the cycle to allow concurrent processing</li>
                  <li><strong>Review timing constraints:</strong> Check offset modes and conditional delays that might force the circular pattern</li>
                  <li><strong>Consider flow batching:</strong> Group flows to reduce resource contention</li>
                </>
              )}
            </ul>
          </div>

        </div>

        {/* Footer Actions */}
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Close</button>
          <button 
            className="btn-primary"
            onClick={() => {
              // Copy deadlock info to clipboard
              const info = JSON.stringify({
                type: error.type,
                message: error.message,
                deadlock_info: deadlockInfo
              }, null, 2);
              navigator.clipboard.writeText(info);
              alert('Deadlock information copied to clipboard!');
            }}
          >
            📋 Copy Details
          </button>
        </div>

      </div>
    </div>
  );
}
