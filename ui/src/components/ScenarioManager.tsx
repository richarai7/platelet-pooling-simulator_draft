import { useState, useEffect } from 'react';
import { Scenario, SimulationConfig } from '../types';
import { listScenarios, saveScenario, deleteScenario, getScenario } from '../api';
import './ScenarioManager.css';

interface ScenarioManagerProps {
  onLoad: (config: SimulationConfig, scenarioName?: string) => void;
  currentConfig: SimulationConfig | null;
}

export function ScenarioManager({ onLoad, currentConfig }: ScenarioManagerProps) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [saveDescription, setSaveDescription] = useState('');
  const [saveTags, setSaveTags] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listScenarios();
      setScenarios(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!currentConfig) {
      setError('No configuration to save');
      return;
    }
    if (!saveName.trim()) {
      setError('Please enter a scenario name');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const tags = saveTags.split(',').map(t => t.trim()).filter(t => t);
      await saveScenario(saveName, saveDescription, currentConfig, tags);
      await loadScenarios();
      setShowSaveDialog(false);
      setSaveName('');
      setSaveDescription('');
      setSaveTags('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save scenario');
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async (scenario: Scenario) => {
    try {
      const fullScenario = await getScenario(scenario.id);
      onLoad(fullScenario.config, fullScenario.name);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario');
    }
  };

  const handleCopy = async (scenario: Scenario) => {
    try {
      const fullScenario = await getScenario(scenario.id);
      setSaveName(`${fullScenario.name} (Copy)`);
      setSaveDescription(fullScenario.description);
      setSaveTags(fullScenario.tags?.join(', ') || '');
      onLoad(fullScenario.config);
      setShowSaveDialog(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to copy scenario');
    }
  };

  const handleDelete = async (scenario: Scenario) => {
    if (!confirm(`Are you sure you want to delete "${scenario.name}"?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await deleteScenario(scenario.id);
      await loadScenarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scenario-manager">
      <div className="scenario-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>
          {isExpanded ? '▼' : '▶'} Scenarios ({scenarios.length})
        </h3>
        <button 
          className="btn-primary"
          onClick={(e) => {
            e.stopPropagation();
            setShowSaveDialog(true);
          }}
          disabled={!currentConfig}
        >
          💾 Save Current
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>✖</button>
        </div>
      )}

      {isExpanded && (
        <div className="scenario-list">
          {loading && <div className="loading-spinner">Loading...</div>}
          
          {!loading && scenarios.length === 0 && (
            <div className="empty-state">
              No saved scenarios. Save your current configuration to get started.
            </div>
          )}

          {!loading && scenarios.map(scenario => (
            <div key={scenario.id} className="scenario-card">
              <div className="scenario-info">
                <h4>{scenario.name}</h4>
                <p className="scenario-description">{scenario.description}</p>
                {scenario.tags && scenario.tags.length > 0 && (
                  <div className="scenario-tags">
                    {scenario.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
                <div className="scenario-meta">
                  <span className="scenario-date">
                    Created: {new Date(scenario.created_at).toLocaleDateString()}
                  </span>
                  {scenario.updated_at && scenario.updated_at !== scenario.created_at && (
                    <span className="scenario-date">
                      Updated: {new Date(scenario.updated_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <div className="scenario-actions">
                <button 
                  className="btn-load"
                  onClick={() => handleLoad(scenario)}
                  title="Load this scenario"
                >
                  📂 Load
                </button>
                <button 
                  className="btn-copy"
                  onClick={() => handleCopy(scenario)}
                  title="Copy this scenario"
                >
                  📋 Copy
                </button>
                <button 
                  className="btn-delete"
                  onClick={() => handleDelete(scenario)}
                  title="Delete this scenario"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showSaveDialog && (
        <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>Save Scenario</h3>
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                placeholder="e.g., High Capacity Setup"
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={saveDescription}
                onChange={(e) => setSaveDescription(e.target.value)}
                placeholder="Describe this scenario configuration..."
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>Tags (comma-separated)</label>
              <input
                type="text"
                value={saveTags}
                onChange={(e) => setSaveTags(e.target.value)}
                placeholder="e.g., high-volume, testing, production"
              />
            </div>
            <div className="modal-actions">
              <button 
                className="btn-secondary"
                onClick={() => {
                  setShowSaveDialog(false);
                  setSaveName('');
                  setSaveDescription('');
                  setSaveTags('');
                }}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={handleSave}
                disabled={!saveName.trim() || loading}
              >
                {loading ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
