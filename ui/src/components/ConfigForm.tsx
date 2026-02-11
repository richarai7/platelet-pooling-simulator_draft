import { useState } from 'react';
import { SimulationConfig, Device, Flow } from '../types';

interface ConfigFormProps {
  config: SimulationConfig;
  onChange: (newConfig: SimulationConfig) => void;
}

export function ConfigForm({ config, onChange }: ConfigFormProps) {
  const [localConfig, setLocalConfig] = useState<SimulationConfig>(config);
  const [devicesExpanded, setDevicesExpanded] = useState(true);
  const [flowsExpanded, setFlowsExpanded] = useState(true);
  const [newlyAddedDevices, setNewlyAddedDevices] = useState<Set<string>>(new Set());
  const [newlyAddedFlows, setNewlyAddedFlows] = useState<Set<string>>(new Set());
  const [advancedTimingExpanded, setAdvancedTimingExpanded] = useState<Set<string>>(new Set());

  const updateDevice = (index: number, field: keyof Device, value: any) => {
    const newDevices = [...localConfig.devices];
    newDevices[index] = { ...newDevices[index], [field]: value };
    const newConfig = { ...localConfig, devices: newDevices };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const addDevice = () => {
    const newDeviceId = `device_${Date.now()}`;
    const newDevice: Device = {
      id: newDeviceId,
      type: 'machine',
      capacity: 1,
      initial_state: 'idle',
      recovery_time_range: [10, 20],
    };
    const newDevices = [...localConfig.devices, newDevice];
    const newConfig = { ...localConfig, devices: newDevices };
    setLocalConfig(newConfig);
    onChange(newConfig);
    
    // Highlight the new device
    setNewlyAddedDevices(prev => new Set(prev).add(newDeviceId));
    // Expand devices section
    setDevicesExpanded(true);
    // Remove highlight after 5 seconds
    setTimeout(() => {
      setNewlyAddedDevices(prev => {
        const newSet = new Set(prev);
        newSet.delete(newDeviceId);
        return newSet;
      });
    }, 5000);
  };

  const removeDevice = (index: number) => {
    const newDevices = localConfig.devices.filter((_, i) => i !== index);
    const newConfig = { ...localConfig, devices: newDevices };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const updateFlow = (index: number, field: keyof Flow, value: any) => {
    const newFlows = [...localConfig.flows];
    newFlows[index] = { ...newFlows[index], [field]: value };
    const newConfig = { ...localConfig, flows: newFlows };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const addFlow = () => {
    const newFlowId = `flow_${Date.now()}`;
    const newFlow: Flow = {
      flow_id: newFlowId,
      from_device: localConfig.devices[0]?.id || '',
      to_device: localConfig.devices[0]?.id || '',
      process_time_range: [10, 20],
      priority: 1,
      dependencies: [],
    };
    const newFlows = [...localConfig.flows, newFlow];
    const newConfig = { ...localConfig, flows: newFlows };
    setLocalConfig(newConfig);
    onChange(newConfig);
    
    // Highlight the new flow
    setNewlyAddedFlows(prev => new Set(prev).add(newFlowId));
    // Expand flows section
    setFlowsExpanded(true);
    // Remove highlight after 5 seconds
    setTimeout(() => {
      setNewlyAddedFlows(prev => {
        const newSet = new Set(prev);
        newSet.delete(newFlowId);
        return newSet;
      });
    }, 5000);
  };

  const removeFlow = (index: number) => {
    const newFlows = localConfig.flows.filter((_, i) => i !== index);
    const newConfig = { ...localConfig, flows: newFlows };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const toggleAdvancedTiming = (flowId: string) => {
    setAdvancedTimingExpanded(prev => {
      const newSet = new Set(prev);
      if (newSet.has(flowId)) {
        newSet.delete(flowId);
      } else {
        newSet.add(flowId);
      }
      return newSet;
    });
  };

  const updateConditionalDelay = (flowIndex: number, delayIndex: number | null, field: string, value: any) => {
    const flow = localConfig.flows[flowIndex];
    const delays = flow.conditional_delays || [];
    
    if (delayIndex === null) {
      // Add new delay
      const newDelay = {
        condition_type: 'high_utilization' as const,
        threshold: 0.8,
        delay_seconds: 10
      };
      updateFlow(flowIndex, 'conditional_delays', [...delays, newDelay]);
    } else if (field === 'remove') {
      // Remove delay
      updateFlow(flowIndex, 'conditional_delays', delays.filter((_, i) => i !== delayIndex));
    } else {
      // Update delay field
      const newDelays = [...delays];
      newDelays[delayIndex] = { ...newDelays[delayIndex], [field]: value };
      updateFlow(flowIndex, 'conditional_delays', newDelays);
    }
  };

  const updateSimulation = (field: string, value: any) => {
    const newSimulation = { ...localConfig.simulation, [field]: value };
    const newConfig = { ...localConfig, simulation: newSimulation };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const addGate = (gateName: string) => {
    const gates = localConfig.gates || {};
    const newGates = { ...gates, [gateName]: true };
    const newConfig = { ...localConfig, gates: newGates };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const toggleGate = (gateName: string) => {
    const gates = localConfig.gates || {};
    const newGates = { ...gates, [gateName]: !gates[gateName] };
    const newConfig = { ...localConfig, gates: newGates };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const removeGate = (gateName: string) => {
    const gates = localConfig.gates || {};
    const { [gateName]: _, ...newGates } = gates;
    const newConfig = { ...localConfig, gates: newGates };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);

  const validateConfiguration = () => {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check required fields
    if (!localConfig.simulation) {
      errors.push('Missing simulation settings');
    } else {
      if (localConfig.simulation.duration <= 0) {
        errors.push('Simulation duration must be greater than 0');
      }
      if (localConfig.simulation.random_seed < 0) {
        errors.push('Random seed must be >= 0');
      }
    }

    if (!localConfig.devices || localConfig.devices.length === 0) {
      errors.push('At least one device is required');
    } else {
      // Check device IDs are unique
      const deviceIds = localConfig.devices.map(d => d.id);
      const duplicates = deviceIds.filter((id, index) => deviceIds.indexOf(id) !== index);
      if (duplicates.length > 0) {
        errors.push(`Duplicate device IDs: ${duplicates.join(', ')}`);
      }

      // Check device capacities
      localConfig.devices.forEach(device => {
        if (device.capacity < 1) {
          errors.push(`Device ${device.id}: capacity must be >= 1`);
        }
        if (device.recovery_time_range) {
          const [min, max] = device.recovery_time_range;
          if (min < 0 || max < 0) {
            errors.push(`Device ${device.id}: recovery times must be >= 0`);
          }
          if (min >= max) {
            errors.push(`Device ${device.id}: recovery min must be < max`);
          }
        }
      });
    }

    if (!localConfig.flows || localConfig.flows.length === 0) {
      errors.push('At least one flow is required');
    } else {
      // Check flow IDs are unique
      const flowIds = localConfig.flows.map(f => f.flow_id);
      const duplicates = flowIds.filter((id, index) => flowIds.indexOf(id) !== index);
      if (duplicates.length > 0) {
        errors.push(`Duplicate flow IDs: ${duplicates.join(', ')}`);
      }

      // Check device references
      const deviceIdSet = new Set(localConfig.devices.map(d => d.id));
      localConfig.flows.forEach(flow => {
        if (!deviceIdSet.has(flow.from_device)) {
          errors.push(`Flow ${flow.flow_id}: unknown source device ${flow.from_device}`);
        }
        if (!deviceIdSet.has(flow.to_device)) {
          errors.push(`Flow ${flow.flow_id}: unknown target device ${flow.to_device}`);
        }
        
        const [min, max] = flow.process_time_range;
        if (min < 0 || max < 0) {
          errors.push(`Flow ${flow.flow_id}: process times must be >= 0`);
        }
        if (min >= max) {
          errors.push(`Flow ${flow.flow_id}: process min must be < max`);
        }
      });
    }

    if (!localConfig.output_options) {
      warnings.push('No output options specified - using defaults');
    }

    setValidationResult({
      valid: errors.length === 0,
      errors,
      warnings
    });
  };

  return (
    <div className="config-form">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Simulation Configuration</h2>
        <button
          type="button"
          onClick={validateConfiguration}
          className="validate-button"
          style={{
            padding: '0.5rem 1rem',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          ✓ Validate Configuration
        </button>
      </div>

      {validationResult && (
        <div style={{
          padding: '1rem',
          marginBottom: '1rem',
          borderRadius: '6px',
          border: `2px solid ${validationResult.valid ? '#7FCC72' : '#ef4444'}`,
          background: validationResult.valid ? '#ecfdf5' : '#fee'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: validationResult.valid ? '#7FCC72' : '#dc2626' }}>
            {validationResult.valid ? '✓ Configuration Valid' : '✗ Configuration Invalid'}
          </h4>
          {validationResult.errors.length > 0 && (
            <div>
              <strong style={{ color: '#dc2626' }}>Errors:</strong>
              <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                {validationResult.errors.map((error, idx) => (
                  <li key={idx} style={{ color: '#dc2626' }}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          {validationResult.warnings.length > 0 && (
            <div>
              <strong style={{ color: '#FF6F40' }}>Warnings:</strong>
              <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                {validationResult.warnings.map((warning, idx) => (
                  <li key={idx} style={{ color: '#FF6F40' }}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
          {validationResult.valid && validationResult.warnings.length === 0 && (
            <p style={{ margin: '0.5rem 0 0 0', color: '#7FCC72' }}>
              All validation checks passed. Configuration is ready to run.
            </p>
          )}
        </div>
      )}
      
      {/* Simulation Parameters */}
      <section className="config-section">
        <h3>Simulation Parameters</h3>
        <div className="form-group">
          <label>Duration (seconds):</label>
          <input
            type="number"
            value={localConfig.simulation.duration}
            onChange={(e) => updateSimulation('duration', parseInt(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Random Seed:</label>
          <input
            type="number"
            value={localConfig.simulation.random_seed}
            onChange={(e) => updateSimulation('random_seed', parseInt(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Execution Mode:</label>
          <select
            value={localConfig.simulation.execution_mode || 'accelerated'}
            onChange={(e) => updateSimulation('execution_mode', e.target.value)}
          >
            <option value="accelerated">Accelerated (Fast)</option>
            <option value="real-time">Real-Time (Clock Sync)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Speed Multiplier:</label>
          <select
            value={localConfig.simulation.speed_multiplier ?? ''}
            onChange={(e) => {
              const value = e.target.value === '' ? undefined : parseFloat(e.target.value);
              updateSimulation('speed_multiplier', value);
            }}
            title="Controls simulation pacing. Max = instant, 100x/10x = visible progress, 1x = real-time"
          >
            <option value="">Max Speed (Instant)</option>
            <option value="100">100x Accelerated</option>
            <option value="10">10x Accelerated</option>
            <option value="1">Real-Time (1x)</option>
          </select>
          <small style={{display: 'block', marginTop: '4px', color: '#666'}}>
            {localConfig.simulation.speed_multiplier === 100 && '100x faster than real-time'}
            {localConfig.simulation.speed_multiplier === 10 && '10x faster than real-time'}
            {localConfig.simulation.speed_multiplier === 1 && 'Syncs with real-world clock'}
            {(!localConfig.simulation.speed_multiplier) && 'Maximum CPU speed (default)'}
          </small>
        </div>
      </section>

      {/* Global Gates (Virtual Resources) */}
      <section className="config-section">
        <div className="section-header">
          <h3>Global Gates (Virtual Resources)</h3>
          <button
            type="button"
            onClick={() => {
              const gateName = prompt('Enter gate name (e.g., "Factory Power", "Quality Control"):');
              if (gateName && gateName.trim()) {
                addGate(gateName.trim());
              }
            }}
            className="add-button"
          >
            + Add Gate
          </button>
        </div>
        {Object.entries(localConfig.gates || {}).map(([gateName, isActive]) => (
          <div key={gateName} className="gate-config">
            <div className="item-header">
              <h4>{gateName}</h4>
              <button
                type="button"
                onClick={() => removeGate(gateName)}
                className="remove-button"
                title="Remove gate"
              >
                × Remove
              </button>
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={() => toggleGate(gateName)}
                />
                {' '}Active (flows/devices requiring this gate can proceed)
              </label>
            </div>
          </div>
        ))}
        {Object.keys(localConfig.gates || {}).length === 0 && (
          <p className="empty-notice">
            No global gates defined. Gates are optional conditions that can block flows/devices.
          </p>
        )}
      </section>

      {/* Devices */}
      <section className="config-section">
        <div className="section-header" style={{ cursor: 'pointer' }} onClick={() => setDevicesExpanded(!devicesExpanded)}>
          <h3>
            <span style={{ marginRight: '8px' }}>{devicesExpanded ? '▼' : '▶'}</span>
            Devices ({localConfig.devices.length})
          </h3>
          <button 
            type="button" 
            onClick={(e) => {
              e.stopPropagation();
              addDevice();
            }} 
            className="add-button"
          >
            + Add Device
          </button>
        </div>
        {devicesExpanded && localConfig.devices.map((device, index) => (
          <div 
            key={device.id} 
            className={`device-config ${newlyAddedDevices.has(device.id) ? 'newly-added' : ''}`}
            style={newlyAddedDevices.has(device.id) ? {
              animation: 'highlightPulse 2s ease-in-out',
              border: '2px solid #3b82f6',
              backgroundColor: '#eff6ff'
            } : {}}
          >
            <div className="item-header">
              <h4>{device.id}</h4>
              <button
                type="button"
                onClick={() => removeDevice(index)}
                className="remove-button"
                title="Remove device"
              >
                × Remove
              </button>
            </div>
            <div className="form-group">
              <label>ID:</label>
              <input
                type="text"
                value={device.id}
                onChange={(e) => updateDevice(index, 'id', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Type:</label>
              <select
                value={device.type}
                onChange={(e) => updateDevice(index, 'type', e.target.value)}
              >
                <option value="machine">Machine</option>
                <option value="person">People</option>
                <option value="material">Material</option>
              </select>
            </div>
            <div className="form-group">
              <label>Capacity:</label>
              <input
                type="number"
                value={device.capacity}
                onChange={(e) => updateDevice(index, 'capacity', parseInt(e.target.value))}
              />
            </div>
            {device.recovery_time_range && (
              <div className="form-group">
                <label>
                  Recovery Time Range (min, max):
                  <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                    {device.type === 'machine' && '⚙️ Cooldown/reset time after processing'}
                    {device.type === 'person' && '👤 Rest, breaks, or prep time between tasks'}
                    {device.type === 'material' && '📦 Replenishment or restocking time'}
                  </small>
                </label>
                <div className="range-inputs">
                  <input
                    type="number"
                    value={device.recovery_time_range[0]}
                    onChange={(e) => 
                      updateDevice(index, 'recovery_time_range', [
                        parseFloat(e.target.value),
                        device.recovery_time_range![1]
                      ])
                    }
                    placeholder="Min"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    value={device.recovery_time_range[1]}
                    onChange={(e) => 
                      updateDevice(index, 'recovery_time_range', [
                        device.recovery_time_range![0],
                        parseFloat(e.target.value)
                      ])
                    }
                    placeholder="Max"
                  />
                </div>
              </div>
            )}
            <div className="form-group">
              <label>
                Operational Cost ($/hour):
                <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                  💰 Hourly cost for this device/resource (for KPI calculations)
                </small>
              </label>
              <input
                type="number"
                step="0.01"
                value={device.operational_cost_per_hour || ''}
                onChange={(e) => updateDevice(index, 'operational_cost_per_hour', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="e.g., 50.00"
              />
            </div>
            <div className="form-group">
              <label>
                Cost per Action ($):
                <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                  💵 Fixed cost per processing action (for KPI calculations)
                </small>
              </label>
              <input
                type="number"
                step="0.01"
                value={device.cost_per_action || ''}
                onChange={(e) => updateDevice(index, 'cost_per_action', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="e.g., 5.00"
              />
            </div>
          </div>
        ))}
      </section>

      {/* Flows */}
      <section className="config-section">
        <div className="section-header" style={{ cursor: 'pointer' }} onClick={() => setFlowsExpanded(!flowsExpanded)}>
          <h3>
            <span style={{ marginRight: '8px' }}>{flowsExpanded ? '▼' : '▶'}</span>
            Flows ({localConfig.flows.length})
          </h3>
          <button 
            type="button" 
            onClick={(e) => {
              e.stopPropagation();
              addFlow();
            }} 
            className="add-button"
          >
            + Add Flow
          </button>
        </div>
        {flowsExpanded && localConfig.flows.map((flow, index) => (
          <div 
            key={flow.flow_id} 
            className={`flow-config ${newlyAddedFlows.has(flow.flow_id) ? 'newly-added' : ''}`}
            style={newlyAddedFlows.has(flow.flow_id) ? {
              animation: 'highlightPulse 2s ease-in-out',
              border: '2px solid #3b82f6',
              backgroundColor: '#eff6ff'
            } : {}}
          >
            <div className="item-header">
              <h4>{flow.flow_id}</h4>
              <button
                type="button"
                onClick={() => removeFlow(index)}
                className="remove-button"
                title="Remove flow"
              >
                × Remove
              </button>
            </div>
            <div className="form-group">
              <label>Flow ID:</label>
              <input
                type="text"
                value={flow.flow_id}
                onChange={(e) => updateFlow(index, 'flow_id', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>From Device:</label>
              <select
                value={flow.from_device}
                onChange={(e) => updateFlow(index, 'from_device', e.target.value)}
              >
                <option value="">Select device...</option>
                {localConfig.devices.map(d => (
                  <option key={d.id} value={d.id}>{d.id} ({d.type})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>To Device:</label>
              <select
                value={flow.to_device}
                onChange={(e) => updateFlow(index, 'to_device', e.target.value)}
              >
                <option value="">Select device...</option>
                {localConfig.devices.map(d => (
                  <option key={d.id} value={d.id}>{d.id} ({d.type})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Priority:</label>
              <input
                type="number"
                value={flow.priority}
                onChange={(e) => updateFlow(index, 'priority', parseInt(e.target.value))}
              />
            </div>
            
            <div className="form-group">
              <label>
                Process Time Range (min, max seconds):
                <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                  ⏱️ Duration for this flow to complete
                </small>
              </label>
              <div className="range-inputs">
                <input
                  type="number"
                  value={flow.process_time_range[0]}
                  onChange={(e) => 
                    updateFlow(index, 'process_time_range', [
                      parseFloat(e.target.value),
                      flow.process_time_range[1]
                    ])
                  }
                  placeholder="Min"
                />
                <span>to</span>
                <input
                  type="number"
                  value={flow.process_time_range[1]}
                  onChange={(e) => 
                    updateFlow(index, 'process_time_range', [
                      flow.process_time_range[0],
                      parseFloat(e.target.value)
                    ])
                  }
                  placeholder="Max"
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                Dependencies (comma-separated Flow IDs):
                <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                  🔗 Flows that must complete before this one starts
                </small>
              </label>
              <input
                type="text"
                value={flow.dependencies?.join(', ') || ''}
                onChange={(e) => {
                  const deps = e.target.value
                    .split(',')
                    .map(d => d.trim())
                    .filter(d => d.length > 0);
                  updateFlow(index, 'dependencies', deps.length > 0 ? deps : null);
                }}
                placeholder="e.g., flow_1, flow_2"
              />
            </div>

            <div className="form-group">
              <label>
                Offset Mode:
                <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                  📍 When this flow starts relative to others
                </small>
              </label>
              <select
                value={flow.offset_mode || 'parallel'}
                onChange={(e) => updateFlow(index, 'offset_mode', e.target.value)}
              >
                <option value="parallel">Parallel (start at T=0)</option>
                <option value="sequence">Sequence (after dependencies)</option>
                <option value="custom">Custom (specified offset)</option>
              </select>
            </div>

            {flow.offset_mode === 'custom' && (
              <div className="form-group">
                <label>Start Offset (seconds):</label>
                <input
                  type="number"
                  value={flow.start_offset || 0}
                  onChange={(e) => updateFlow(index, 'start_offset', parseFloat(e.target.value))}
                  placeholder="e.g., 10"
                />
              </div>
            )}

            {/* FR21: Advanced Timing Section */}
            <div className="advanced-timing-section" style={{ marginTop: '16px', borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
              <div 
                className="section-toggle"
                style={{ 
                  cursor: 'pointer', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  padding: '8px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '4px',
                  fontWeight: 500
                }}
                onClick={() => toggleAdvancedTiming(flow.flow_id)}
              >
                <span>{advancedTimingExpanded.has(flow.flow_id) ? '▼' : '▶'}</span>
                <span>Advanced Timing (FR21)</span>
                <small style={{ fontWeight: 'normal', color: '#6b7280', marginLeft: 'auto' }}>
                  Start-to-start, random delays, conditional
                </small>
              </div>

              {advancedTimingExpanded.has(flow.flow_id) && (
                <div style={{ marginTop: '12px', paddingLeft: '8px' }}>
                  
                  {/* Offset Type */}
                  <div className="form-group">
                    <label>
                      Offset Type:
                      <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                        🔄 How dependencies are evaluated
                      </small>
                    </label>
                    <select
                      value={flow.offset_type || 'finish-to-start'}
                      onChange={(e) => updateFlow(index, 'offset_type', e.target.value)}
                    >
                      <option value="finish-to-start">Finish-to-Start (wait for completion)</option>
                      <option value="start-to-start">Start-to-Start (proceed when started)</option>
                    </select>
                  </div>

                  {/* Offset Range */}
                  <div className="form-group">
                    <label>
                      Random Offset Range (seconds):
                      <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                        🎲 Random delay range [min, max] - leave empty for fixed offset
                      </small>
                    </label>
                    <div className="range-inputs">
                      <input
                        type="number"
                        value={flow.offset_range?.[0] ?? ''}
                        onChange={(e) => {
                          const val = e.target.value ? parseFloat(e.target.value) : undefined;
                          const max = flow.offset_range?.[1];
                          updateFlow(index, 'offset_range', 
                            val !== undefined && max !== undefined ? [val, max] : undefined
                          );
                        }}
                        placeholder="Min (optional)"
                      />
                      <span>to</span>
                      <input
                        type="number"
                        value={flow.offset_range?.[1] ?? ''}
                        onChange={(e) => {
                          const val = e.target.value ? parseFloat(e.target.value) : undefined;
                          const min = flow.offset_range?.[0];
                          updateFlow(index, 'offset_range', 
                            min !== undefined && val !== undefined ? [min, val] : undefined
                          );
                        }}
                        placeholder="Max (optional)"
                      />
                    </div>
                  </div>

                  {/* Conditional Delays */}
                  <div className="form-group">
                    <label>
                      Conditional Delays:
                      <small style={{display: 'block', fontWeight: 'normal', color: '#666', marginTop: '4px'}}>
                        ⚠️ Apply delays based on device state
                      </small>
                    </label>
                    
                    {(flow.conditional_delays || []).map((delay, delayIdx) => (
                      <div key={delayIdx} style={{ 
                        padding: '12px', 
                        backgroundColor: '#f3f4f6', 
                        borderRadius: '6px', 
                        marginBottom: '8px',
                        border: '1px solid #e5e7eb'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <strong style={{ fontSize: '14px' }}>Condition #{delayIdx + 1}</strong>
                          <button
                            type="button"
                            onClick={() => updateConditionalDelay(index, delayIdx, 'remove', null)}
                            style={{
                              padding: '4px 8px',
                              fontSize: '12px',
                              backgroundColor: '#ef4444',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            ✕ Remove
                          </button>
                        </div>

                        <div className="form-group" style={{ marginBottom: '8px' }}>
                          <label style={{ fontSize: '13px' }}>Condition Type:</label>
                          <select
                            value={delay.condition_type}
                            disabled
                            style={{ fontSize: '13px' }}
                          >
                            <option value="high_utilization">High Utilization</option>
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: '8px' }}>
                          <label style={{ fontSize: '13px' }}>Device ID (optional):</label>
                          <input
                            type="text"
                            value={delay.device_id || ''}
                            onChange={(e) => updateConditionalDelay(index, delayIdx, 'device_id', e.target.value || undefined)}
                            placeholder={`Default: ${flow.from_device}`}
                            style={{ fontSize: '13px' }}
                          />
                        </div>

                        <div className="form-group" style={{ marginBottom: '8px' }}>
                          <label style={{ fontSize: '13px' }}>Utilization Threshold (0.0 - 1.0):</label>
                          <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="1"
                            value={delay.threshold ?? 0.8}
                            onChange={(e) => updateConditionalDelay(index, delayIdx, 'threshold', parseFloat(e.target.value))}
                            style={{ fontSize: '13px' }}
                          />
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label style={{ fontSize: '13px' }}>Delay (seconds):</label>
                          <input
                            type="number"
                            value={delay.delay_seconds}
                            onChange={(e) => updateConditionalDelay(index, delayIdx, 'delay_seconds', parseFloat(e.target.value))}
                            style={{ fontSize: '13px' }}
                          />
                        </div>
                      </div>
                    ))}

                    <button
                      type="button"
                      onClick={() => updateConditionalDelay(index, null, '', null)}
                      style={{
                        padding: '8px 12px',
                        fontSize: '13px',
                        backgroundColor: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginTop: '8px'
                      }}
                    >
                      + Add Conditional Delay
                    </button>
                  </div>

                </div>
              )}
            </div>

          </div>
        ))}
      </section>
    </div>
  );
}
