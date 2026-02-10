import { useState, useEffect } from 'react';
import { SimulationConfig } from '../types';

interface LiveDashboardProps {
  config: SimulationConfig | null;
  onRunSimulation: () => void;
  isRunning: boolean;
  results: any;
}

export function LiveDashboard({ config, onRunSimulation, isRunning, results }: LiveDashboardProps) {
  const [currentTime, setCurrentTime] = useState(0);
  const [elapsedReal, setElapsedReal] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (!isRunning) {
      setCurrentTime(0);
      setElapsedReal(0);
      return;
    }

    const startTime = Date.now();
    const interval = setInterval(() => {
      if (!isPaused) {
        const elapsed = (Date.now() - startTime) / 1000;
        setElapsedReal(elapsed);
        
        // In real-time mode, simulated time matches real time
        if (config?.simulation.execution_mode === 'real-time') {
          setCurrentTime(elapsed);
        }
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isRunning, isPaused, config]);

  const handlePause = () => {
    setIsPaused(!isPaused);
  };

  const handleStop = () => {
    // Note: Backend doesn't support mid-simulation cancellation yet
    // The simulation will continue running on the server until completion
    // This just resets the UI state
    if (window.confirm('Stop is not fully implemented. The simulation will continue running on the server. Reset UI anyway?')) {
      setCurrentTime(0);
      setElapsedReal(0);
      setIsPaused(false);
      window.location.reload(); // Force page reload to reset everything
    }
  };

  const duration = config?.simulation.duration || 0;
  const progress = duration > 0 ? Math.min((currentTime / duration) * 100, 100) : 0;
  const executionMode = config?.simulation.execution_mode || 'accelerated';

  return (
    <div className="live-dashboard">
      <h2>Simulation Control</h2>
      
      <div className="dashboard-controls">
        <button
          onClick={onRunSimulation}
          disabled={isRunning || !config}
          className="control-button start-button"
        >
          ▶ Start
        </button>
        <button
          onClick={handlePause}
          disabled={!isRunning || executionMode === 'accelerated'}
          className="control-button pause-button"
        >
          {isPaused ? '▶ Resume' : '⏸ Pause'}
        </button>
        <button
          onClick={handleStop}
          disabled={!isRunning}
          className="control-button stop-button"
        >
          ⏹ Stop
        </button>
      </div>

      {executionMode === 'accelerated' && (
        <div className="mode-notice">
          <strong>Accelerated Mode:</strong> Simulation runs at maximum speed. 
          Pause/Resume not available.
        </div>
      )}

      {isRunning && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-label">Execution Mode</div>
            <div className="stat-value">{executionMode === 'real-time' ? 'Real-Time' : 'Accelerated'}</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">Simulated Time</div>
            <div className="stat-value">{currentTime.toFixed(1)}s / {duration}s</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">Real Time Elapsed</div>
            <div className="stat-value">{elapsedReal.toFixed(1)}s</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Progress</div>
            <div className="stat-value">{progress.toFixed(0)}%</div>
          </div>
        </div>
      )}

      {isRunning && (
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
      )}

      {!isRunning && results && (
        <div className="completion-notice">
          <strong>Simulation Complete</strong>
          <p>Total events: {results.summary?.total_events || 0}</p>
          <p>Execution time: {results.metadata?.execution_time?.toFixed(3) || 0}s</p>
        </div>
      )}
    </div>
  );
}
