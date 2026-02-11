import { SimulationConfig, SimulationResults, Scenario } from './types';

// In dev mode, use empty string to use Vite's proxy
// In production, use the configured URL or default
const API_BASE_URL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

console.log('API Base URL:', API_BASE_URL);

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  console.log('Fetching:', url);
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options?.headers,
    },
  });

  console.log('Response status:', response.status);
  
  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const error = await response.json();
      console.error('API Error Response:', error);
      errorDetail = error.detail || response.statusText;
    } catch (e) {
      console.error('Failed to parse error response:', e);
    }
    throw new Error(errorDetail || `HTTP ${response.status}: ${response.statusText}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();
  console.log('Response data keys:', Object.keys(data));
  return data;
}

export async function getTemplate(): Promise<SimulationConfig> {
  return fetchJSON<SimulationConfig>(`${API_BASE_URL}/templates/platelet-pooling-multi-batch`);
}

export async function runSimulation(
  config: SimulationConfig,
  runName?: string,
  simulationName?: string,
  exportToJson: boolean = true,
  exportDirectory?: string
): Promise<{ results: SimulationResults; simulationId?: string }> {
  console.log('API: Sending simulation request with:', {
    hasDevices: !!config.devices,
    deviceCount: config.devices?.length,
    devicesType: Array.isArray(config.devices) ? 'array' : typeof config.devices,
    hasFlows: !!config.flows,
    hasSimulation: !!config.simulation,
    hasOutputOptions: !!config.output_options
  });
  
  const response = await fetchJSON<{ 
    results: SimulationResults; 
    json_export_path?: string;
    simulation_id?: string;
  }>(
    `${API_BASE_URL}/simulations/run`,
    {
      method: 'POST',
      body: JSON.stringify({ 
        config,
        run_name: runName,
        simulation_name: simulationName,
        export_to_json: exportToJson,
        export_directory: exportDirectory
      }),
    }
  );
  
  console.log('API: Received response:', {
    hasResults: !!response.results,
    resultsKeys: response.results ? Object.keys(response.results) : []
  });
  
  // Add json export path to results if available
  if (response.json_export_path) {
    response.results.json_export_path = response.json_export_path;
  }
  
  return {
    results: response.results,
    simulationId: response.simulation_id
  };
}

export async function pauseSimulation(simulationId: string): Promise<void> {
  await fetchJSON(`${API_BASE_URL}/simulations/${simulationId}/pause`, {
    method: 'POST',
  });
}

export async function resumeSimulation(simulationId: string): Promise<void> {
  await fetchJSON(`${API_BASE_URL}/simulations/${simulationId}/resume`, {
    method: 'POST',
  });
}

export async function getSimulationStatus(simulationId: string): Promise<any> {
  return fetchJSON(`${API_BASE_URL}/simulations/${simulationId}/status`);
}

export async function saveScenario(
  name: string,
  description: string,
  config: SimulationConfig,
  tags?: string[]
): Promise<Scenario> {
  return fetchJSON<Scenario>(`${API_BASE_URL}/scenarios`, {
    method: 'POST',
    body: JSON.stringify({ name, description, config, tags }),
  });
}

export async function updateScenario(
  id: number,
  name: string,
  description: string,
  config: SimulationConfig,
  tags?: string[]
): Promise<Scenario> {
  return fetchJSON<Scenario>(`${API_BASE_URL}/scenarios/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ name, description, config, tags }),
  });
}

export async function listScenarios(): Promise<Scenario[]> {
  return fetchJSON<Scenario[]>(`${API_BASE_URL}/scenarios`);
}

export async function getScenario(id: number): Promise<Scenario> {
  return fetchJSON<Scenario>(`${API_BASE_URL}/scenarios/${id}`);
}

export async function deleteScenario(id: number): Promise<void> {
  return fetchJSON<void>(`${API_BASE_URL}/scenarios/${id}`, {
    method: 'DELETE',
  });
}
