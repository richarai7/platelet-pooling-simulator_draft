import { SimulationConfig, SimulationResults, Scenario } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
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
): Promise<SimulationResults> {
  const response = await fetchJSON<{ results: SimulationResults; json_export_path?: string }>(
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
  
  // Add json export path to results if available
  if (response.json_export_path) {
    response.results.json_export_path = response.json_export_path;
  }
  
  return response.results;
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
