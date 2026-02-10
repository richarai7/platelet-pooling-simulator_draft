import { useState } from 'react';
import { SimulationConfig, Device, Flow } from '../types';

interface ConfigFormProps {
  config: SimulationConfig;
  onChange: (newConfig: SimulationConfig) => void;
}

export function ConfigForm({ config, onChange }: ConfigFormProps) {
  const [localConfig, setLocalConfig] = useState<SimulationConfig>(config);

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
      recovery_time_range: null,
    };
    const newDevices = [...localConfig.devices, newDevice];
    const newConfig = { ...localConfig, devices: newDevices };
    setLocalConfig(newConfig);
    onChange(newConfig);
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
  };

  const removeFlow = (index: number) => {
    const newFlows = localConfig.flows.filter((_, i) => i !== index);
    const newConfig = { ...localConfig, flows: newFlows };
    setLocalConfig(newConfig);
    onChange(newConfig);
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

  return (
    <div className="config-form">
      <h2>Simulation Configuration</h2>
      
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
            value={localConfig.simulation.speed_multiplier || 0}
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              updateSimulation('speed_multiplier', value === 0 ? undefined : value);
            }}
            title="Controls simulation pacing. Max = instant, 100x/10x = visible progress, 1x = real-time"
          >
            <option value="0">Max Speed (Instant)</option>
            <option value="100">100x Accelerated</option>
            <option value="10">10x Accelerated</option>
            <option value="1">Real-Time (1x)</option>
          </select>
          <small style={{display: 'block', marginTop: '4px', color: '#666'}}>
            {localConfig.simulation.speed_multiplier === 100 && '100x faster than real-time'}
            {localConfig.simulation.speed_multiplier === 10 && '10x faster than real-time'}
            {localConfig.simulation.speed_multiplier === 1 && 'Syncs with real-world clock'}
            {(!localConfig.simulation.speed_multiplier || localConfig.simulation.speed_multiplier === 0) && 'Maximum CPU speed (default)'}
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
        <div className="section-header">
          <h3>Devices</h3>
          <button type="button" onClick={addDevice} className="add-button">
            + Add Device
          </button>
        </div>
        {localConfig.devices.map((device, index) => (
          <div key={device.id} className="device-config">
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
              <input
                type="text"
                value={device.type}
                onChange={(e) => updateDevice(index, 'type', e.target.value)}
                placeholder="machine, person, material"
              />
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
                <label>Recovery Time Range (min, max):</label>
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
          </div>
        ))}
      </section>

      {/* Flows */}
      <section className="config-section">
        <div className="section-header">
          <h3>Flows</h3>
          <button type="button" onClick={addFlow} className="add-button">
            + Add Flow
          </button>
        </div>
        {localConfig.flows.map((flow, index) => (
          <div key={flow.flow_id} className="flow-config">
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
          </div>
        ))}
      </section>
    </div>
  );
}
