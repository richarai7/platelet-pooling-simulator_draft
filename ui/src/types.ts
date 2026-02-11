export type DeviceState = "idle" | "busy" | "recovering" | "failed";

export interface Device {
  id: string;
  type: string;
  capacity: number;
  initial_state: DeviceState;
  recovery_time_range: [number, number] | null;
  required_gates?: string[] | null;  // Gates that must be active
  // Financial parameters (FR1)
  operational_cost_per_hour?: number;
  cost_per_action?: number;
}

export interface Flow {
  flow_id: string;
  from_device: string;
  to_device: string;
  process_time_range: [number, number];
  priority: number;
  dependencies: string[] | null;
  required_gates?: string[] | null;  // Gates that must be active
  
  // Universal Offset System
  offset_mode?: "parallel" | "sequence" | "custom";
  start_offset?: number;
  
  // FR21: Advanced Offset Patterns
  offset_type?: "finish-to-start" | "start-to-start";  // Default: finish-to-start
  offset_range?: [number, number];  // Random delay range [min, max]
  conditional_delays?: Array<{
    condition_type: "high_utilization";
    device_id?: string;
    threshold?: number;
    delay_seconds: number;
  }>;
}

export interface SimulationConfig {
  simulation: {
    duration: number;
    random_seed: number;
    execution_mode?: "accelerated" | "real-time";
    speed_multiplier?: number;
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
  // FR22: Deadlock detection fields
  status?: 'completed' | 'deadlock_detected';
  execution_time?: number;
  error?: {
    type: string;
    message: string;
    deadlock_info: {
      deadlock_type: 'timeout' | 'circular_wait';
      involved_devices: string[];
      involved_flows: string[];
      detection_time: number;
      wait_chain: string[];
      wait_graph: Record<string, string[]>;
      timeout_devices?: Array<{ device_id: string; blocked_since: number }>;
      blocked_devices: Array<{ device_id: string; blocked_since: number }>;
    };
  };
  
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
    total_flows_completed?: number;
    devices_count?: number;
    simulation_time_seconds?: number;
    execution_time_seconds?: number;
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
