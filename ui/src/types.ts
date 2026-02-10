export type DeviceState = "idle" | "busy" | "recovering" | "failed";

export interface Device {
  id: string;
  type: string;
  capacity: number;
  initial_state: DeviceState;
  recovery_time_range: [number, number] | null;
  required_gates?: string[] | null;  // Gates that must be active
}

export interface Flow {
  flow_id: string;
  from_device: string;
  to_device: string;
  process_time_range: [number, number];
  priority: number;
  dependencies: string[] | null;
  required_gates?: string[] | null;  // Gates that must be active
}

export interface SimulationConfig {
  simulation: {
    duration: number;
    random_seed: number;
    execution_mode?: "accelerated" | "real-time";
  };
  devices: Device[];
  flows: Flow[];
  gates?: Record<string, boolean>;  // Global conditions
  output_options: {
    include_events?: boolean;
    include_history?: boolean;
  };
}

export interface Scenario {
  id: number;
  name: string;
  description: string;
  config: SimulationConfig;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

export interface SimulationResults {
  metadata?: {
    duration: number;
    random_seed: number;
    start_time?: string;
    end_time?: string;
    simulation_id?: string;
    run_name?: string;
    simulation_name?: string;
    json_export_path?: string;
  };
  summary?: {
    total_events?: number;
    devices?: Record<string, any>;
  };
  device_states?: Record<string, any>;
  events?: any[];
  history?: any[];
  kpis?: {
    run_name?: string;
    simulation_name?: string;
    device_health?: Record<string, string>;
    capacity_utilization_per_device?: Record<string, number>;
    resource_bottleneck?: string;
    optimization_suggestions?: string[];
    [key: string]: any;
  };
  json_export_path?: string;
}
