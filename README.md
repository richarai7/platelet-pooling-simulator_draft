# Discrete Event Simulation Engine

**Domain-agnostic simulation engine for operational workflow modeling across ANY industry.**

## 🚀 Quick Start

**New to this project?** See **[HOW_TO_RUN.md](HOW_TO_RUN.md)** for complete step-by-step instructions on:
- Installing dependencies
- Running your first simulation
- Starting the API server
- Using the web UI

## Overview

This simulation engine provides a pure-Python, configuration-driven discrete event simulation (DES) framework. Change your configuration to simulate healthcare, manufacturing, logistics, or any industry - no code changes required.

## Features

- **Domain-Agnostic Design**: Works for any industry through configuration
- **Temporal Processing**: Future Event List (FEL) with O(log n) event scheduling
- **State Management**: 4-state device model (Idle/Processing/Blocked/Failed)
- **Deterministic Execution**: Seeded RNG ensures reproducible results
- **Flow Control**: DAG-based dependencies with backpressure handling
- **Fast Execution**: Simulate 36 hours in <2 minutes (accelerated mode)

## Requirements

- Python 3.9+
- SimPy 4.0+

## Installation

```bash
# Install package
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### Healthcare Example (Platelet Pooling)

```python
from simulation_engine import SimulationEngine

# Configuration for blood processing workflow
config = {
    "simulation": {"duration": 129600, "random_seed": 42},  # 36 hours
    "devices": [
        {
            "id": "centrifuge_001",
            "type": "centrifuge",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)
        },
        {
            "id": "pooling_station",
            "type": "workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "spin_platelets",
            "from_device": "centrifuge_001",
            "to_device": "pooling_station",
            "process_time_range": (1800, 2400),
            "priority": 10,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": True}
}

# Run simulation
engine = SimulationEngine(config)
results = engine.run()

print(f"Simulated {results['summary']['simulation_time_seconds']} seconds")
print(f"Completed {results['summary']['total_flows_completed']} flows")
```

### Manufacturing Example (Assembly Line)

```python
config = {
    "simulation": {"duration": 28800, "random_seed": 123},  # 8 hours
    "devices": [
        {
            "id": "cnc_mill_01",
            "type": "cnc_machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (600, 1200)
        },
        {
            "id": "assembly_bench",
            "type": "workstation",
            "capacity": 3,
            "initial_state": "Idle",
            "recovery_time_range": (180, 300)
        }
    ],
    "flows": [
        {
            "flow_id": "mill_part",
            "from_device": "cnc_mill_01",
            "to_device": "assembly_bench",
            "process_time_range": (300, 450),
            "priority": 5,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": False, "include_events": True}
}

engine = SimulationEngine(config)
results = engine.run()
```

### Logistics Example (Warehouse Operations)

```python
config = {
    "simulation": {"duration": 86400, "random_seed": 999},  # 24 hours
    "devices": [
        {
            "id": "forklift_a",
            "type": "forklift",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (120, 300)
        },
        {
            "id": "loading_dock",
            "type": "dock",
            "capacity": 5,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "transport_pallet",
            "from_device": "forklift_a",
            "to_device": "loading_dock",
            "process_time_range": (180, 360),
            "priority": 1,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": False}
}

engine = SimulationEngine(config)
results = engine.run()
```

## Architecture

```
SimulationEngine
├── ConfigManager      - Schema validation
├── EventScheduler     - Future Event List (heapq)
├── StateManager       - 4-state device model
├── FlowController     - Dependencies & backpressure
└── SeededRNG          - Deterministic randomness
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=simulation_engine --cov-report=html

# Format code
black src/ tests/

# Type check
mypy src/

# Lint
pylint src/
```

## Testing

- **Unit Tests**: Component isolation with mocks
- **Integration Tests**: End-to-end simulation workflows
- **Determinism Tests**: Verify reproducibility
- **Performance Tests**: Benchmark against NFRs

## Output Format

```json
{
    "metadata": {
        "simulation_id": "sim_20260206_123456",
        "duration": 129600,
        "random_seed": 42,
        "engine_version": "0.1.0"
    },
    "summary": {
        "total_events": 1247,
        "total_flows_completed": 423,
        "simulation_time_seconds": 129600,
        "execution_time_seconds": 3.47
    },
    "device_states": [...],
    "state_history": [...],
    "event_timeline": [...]
}
```

## License

MIT
