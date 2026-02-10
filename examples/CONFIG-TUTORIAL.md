# How to Create Simulation Configurations

## Quick Start: 3-Step Process

### Step 1: Define Your Devices

Every device needs 5 properties:

```python
{
    "id": "unique_device_name",           # Must be unique across all devices
    "type": "device_category",            # Any string - for YOUR reference only
    "capacity": 1,                        # How many units can process simultaneously
    "initial_state": "Idle",              # Always start with "Idle"
    "recovery_time_range": (min, max)     # (seconds) or None if no recovery
}
```

**Examples:**

```python
# Healthcare: Centrifuge (single-unit processor)
{
    "id": "centrifuge_001",
    "type": "centrifuge",         # YOUR label
    "capacity": 1,                # Processes 1 unit at a time
    "initial_state": "Idle",
    "recovery_time_range": (300, 600)  # 5-10 minutes cleanup between runs
}

# Manufacturing: Assembly bench (handles 3 workers)
{
    "id": "assembly_bench_A",
    "type": "workstation",
    "capacity": 3,                # 3 concurrent workers
    "initial_state": "Idle",
    "recovery_time_range": (180, 300)  # 3-5 minutes tool change
}

# Logistics: Loading dock (no recovery time)
{
    "id": "loading_dock_main",
    "type": "dock",
    "capacity": 5,                # 5 trucks simultaneously
    "initial_state": "Idle",
    "recovery_time_range": None   # No downtime between trucks
}
```

---

### Step 2: Define Process Flows

Each flow connects two devices:

```python
{
    "flow_id": "unique_flow_name",
    "from_device": "source_device_id",    # Must match a device ID
    "to_device": "destination_device_id", # Must match a device ID
    "process_time_range": (min, max),     # How long processing takes (seconds)
    "priority": 10,                       # Higher = more important
    "dependencies": None                  # List of flow_ids or None
}
```

**Universal Offset Modes (Flow Scheduling)**

Control WHEN flows start execution using `offset_mode`:

```python
# PARALLEL MODE (default): All flows start at time 0
{
    "flow_id": "simultaneous_1",
    "offset_mode": "parallel",  # Optional - this is the default
    # ... other fields
}

# CUSTOM MODE: Start at specified offset from T=0
{
    "flow_id": "delayed_start",
    "offset_mode": "custom",
    "start_offset": 300.0,  # Start 5 minutes (300s) into simulation
    # ... other fields
}

# SEQUENCE MODE: Start only after dependencies complete (Finish-to-Start)
{
    "flow_id": "second_stage",
    "offset_mode": "sequence",
    "dependencies": ["first_stage"],  # Wait for this flow to complete
    # ... other fields
}
```

**Real-World Example: Staggered Production Line**

```python
# 3 production lines, start 10 minutes apart to spread resource load
{
    "flow_id": "line_1",
    "offset_mode": "parallel",  # Starts at T=0
    # ...
},
{
    "flow_id": "line_2",
    "offset_mode": "custom",
    "start_offset": 600.0,  # Starts at T=10 min
    # ...
},
{
    "flow_id": "line_3",
    "offset_mode": "custom",
    "start_offset": 1200.0,  # Starts at T=20 min
    # ...
}
```

**Sequential Workflow Example: Blood Processing**

```python
# Step 1: Centrifuge separates blood (starts immediately)
{
    "flow_id": "separation",
    "from_device": "centrifuge",
    "to_device": "holding_area",
    "offset_mode": "parallel",  # Starts at T=0
    "dependencies": None,
    # ...
},
# Step 2: Pooling only starts AFTER separation completes
{
    "flow_id": "pooling",
    "from_device": "holding_area",
    "to_device": "pool_station",
    "offset_mode": "sequence",  # Waits for dependency
    "dependencies": ["separation"],  # Blocked until this completes
    # ...
},
# Step 3: Testing only starts AFTER pooling completes
{
    "flow_id": "quality_test",
    "from_device": "pool_station",
    "to_device": "testing_lab",
    "offset_mode": "sequence",
    "dependencies": ["pooling"],  # Waits for pooling
    # ...
}
```

---

**Examples:**

```python
# Simple linear flow: A → B
{
    "flow_id": "transfer_to_testing",
    "from_device": "centrifuge_001",
    "to_device": "testing_lab",
    "process_time_range": (1800, 2400),   # 30-40 minutes
    "priority": 10,
    "dependencies": None
}

# Parallel processing: A → B1 or B2
# Flow 1: A → B1
{
    "flow_id": "centrifuge_to_station1",
    "from_device": "centrifuge_001",
    "to_device": "pooling_station_01",
    "process_time_range": (600, 900),
    "priority": 9,
    "dependencies": None
}
# Flow 2: A → B2
{
    "flow_id": "centrifuge_to_station2",
    "from_device": "centrifuge_001",
    "to_device": "pooling_station_02",
    "process_time_range": (600, 900),
    "priority": 9,
    "dependencies": None
}
# Engine automatically balances load between B1 and B2
```

---

### Step 3: Configure Simulation Settings

```python
{
    "simulation": {
        "duration": 129600,         # Total time to simulate (seconds)
        "random_seed": 42           # Same seed = identical results
    },
    "devices": [ /* your devices */ ],
    "flows": [ /* your flows */ ],
    "output_options": {
        "include_history": True,    # Track all state transitions
        "include_events": True      # Include event timeline
    }
}
```

---

## Complete Example: Hospital Blood Processing

```python
from simulation_engine import SimulationEngine

config = {
    "simulation": {
        "duration": 28800,  # 8 hours
        "random_seed": 42
    },
    "devices": [
        {
            "id": "reception",
            "type": "intake_station",
            "capacity": 2,  # 2 staff members
            "initial_state": "Idle",
            "recovery_time_range": (60, 120)  # 1-2 min between patients
        },
        {
            "id": "centrifuge",
            "type": "separation_equipment",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)  # 5-10 min cleanup
        },
        {
            "id": "storage",
            "type": "refrigerator",
            "capacity": 50,  # Holds 50 units
            "initial_state": "Idle",
            "recovery_time_range": None  # No recovery
        }
    ],
    "flows": [
        {
            "flow_id": "intake_to_separation",
            "from_device": "reception",
            "to_device": "centrifuge",
            "process_time_range": (300, 600),  # 5-10 min intake
            "priority": 10,
            "dependencies": None
        },
        {
            "flow_id": "separation_to_storage",
            "from_device": "centrifuge",
            "to_device": "storage",
            "process_time_range": (1800, 2400),  # 30-40 min separation
            "priority": 9,
            "dependencies": None
        }
    ],
    "output_options": {
        "include_history": True,
        "include_events": True
    }
}

# Run it!
engine = SimulationEngine(config)
results = engine.run()

print(f"Processed {results['summary']['total_flows_completed']} units")
print(f"Execution time: {results['summary']['execution_time_seconds']}s")
```

---

## Common Patterns

### Pattern 1: Serial Workflow (A → B → C)

```python
"flows": [
    {"flow_id": "a_to_b", "from_device": "device_a", "to_device": "device_b", ...},
    {"flow_id": "b_to_c", "from_device": "device_b", "to_device": "device_c", ...}
]
```

### Pattern 2: Parallel Processing (A → B1, A → B2)

```python
"flows": [
    {"flow_id": "a_to_b1", "from_device": "device_a", "to_device": "device_b1", ...},
    {"flow_id": "a_to_b2", "from_device": "device_a", "to_device": "device_b2", ...}
]
# Engine balances between B1 and B2 automatically
```

### Pattern 3: Merging Flows (A1 → C, A2 → C)

```python
"flows": [
    {"flow_id": "a1_to_c", "from_device": "device_a1", "to_device": "device_c", ...},
    {"flow_id": "a2_to_c", "from_device": "device_a2", "to_device": "device_c", ...}
]
# If C is at capacity, A1 and A2 will be blocked (backpressure)
```

### Pattern 4: Quality/Error Routing

```python
"flows": [
    # Main path
    {"flow_id": "process_ok", "from_device": "quality_check", "to_device": "storage", ...},
    # Error path
    {"flow_id": "process_failed", "from_device": "quality_check", "to_device": "waste", ...}
]
```

---

## Time Conversions

```python
# Seconds → Minutes → Hours
1 minute  = 60 seconds
1 hour    = 3600 seconds
1 day     = 86400 seconds
8 hours   = 28800 seconds
36 hours  = 129600 seconds

# Examples:
"duration": 3600 * 8,              # 8-hour shift
"process_time_range": (60, 120),   # 1-2 minutes
"recovery_time_range": (300, 600), # 5-10 minutes
```

---

## Validation Checklist

✅ **Every device has a unique ID**  
✅ **All from_device and to_device reference existing device IDs**  
✅ **Capacity is ≥ 1 for all devices**  
✅ **All time ranges have min < max**  
✅ **recovery_time_range is tuple or None**  
✅ **Duration > 0**  
✅ **Random seed ≥ 0**

---

## What-If Scenarios

### Scenario 1: Baseline (Current State)
```python
devices = [
    {"id": "machine_1", "capacity": 1, ...},
    {"id": "machine_2", "capacity": 1, ...}
]
```

### Scenario 2: Add Equipment
```python
devices = [
    {"id": "machine_1", "capacity": 1, ...},
    {"id": "machine_2", "capacity": 1, ...},
    {"id": "machine_3", "capacity": 1, ...}  # NEW!
]
flows = [
    # Add flow to new machine
    {"flow_id": "to_machine_3", "from_device": "...", "to_device": "machine_3", ...}
]
```

### Scenario 3: Faster Processing
```python
# Baseline: 30-40 minutes
"process_time_range": (1800, 2400)

# Scenario: Improved training reduces to 20-30 minutes
"process_time_range": (1200, 1800)
```

### Scenario 4: Different Staffing
```python
# Baseline: 1 technician
"capacity": 1

# Scenario: Add 2nd technician
"capacity": 2
```

---

## Reading Results

```python
results = engine.run()

# High-level summary
print(results['summary'])
# {
#   'total_events': 1247,
#   'total_flows_completed': 423,
#   'simulation_time_seconds': 129600,
#   'execution_time_seconds': 3.47
# }

# Per-device final states
for device in results['device_states']:
    print(f"{device['device_id']}: {device['final_state']}, {device['state_changes']} transitions")

# Full state history (if enabled)
for event in results['state_history']:
    print(f"{event['timestamp']}s: {event['device_id']} {event['from_state']} → {event['to_state']}")

# Flow execution counts
for flow in results['flows_executed']:
    print(f"{flow['flow_id']}: executed {flow['execution_count']} times")
```

---

## Pro Tips

1. **Start Simple**: 2-3 devices, linear flow, then add complexity
2. **Use Realistic Times**: Match your actual process (or use historical data)
3. **Same Seed = Reproducible**: Use `random_seed: 42` for consistent testing
4. **Capacity = Bottleneck Control**: Increase capacity to reduce backpressure
5. **State Changes = Activity**: High state changes = busy device (potential bottleneck)
6. **Save Configs**: Store as JSON files for scenario comparison

---

## Domain-Agnostic Examples

The engine works for ANY industry - just change the configuration:

- **Healthcare**: Blood processing, patient flow, surgery scheduling
- **Manufacturing**: Assembly lines, CNC machining, quality control
- **Logistics**: Warehouse ops, shipping, cross-docking
- **Service**: Call centers, restaurant kitchens, retail checkout
- **IT**: Server processing, batch jobs, data pipelines

**Same engine, different config. Zero code changes required.**
