# Discrete Event Simulation Engine - Platelet Pooling Simulator

**Domain-agnostic simulation engine for operational workflow modeling, configured for platelet pooling process.**

## 🚀 Quick Start

**New to this project?**
- **[LINEAR_FLOW_SETUP.md](LINEAR_FLOW_SETUP.md)** - Complete setup guide for Azure Digital Twins integration
- **[QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md)** - Get running in 2 minutes
- **[END_TO_END_GUIDE.md](docs/END_TO_END_GUIDE.md)** - Complete instructions for all features

## 🩸 Platelet Pooling Linear Flow

This simulator models a **10-device linear flow** for platelet pooling process:

```
Buffy Coat Packs → Platelet Washing → Centrifuge → Separator Macropress → 
Resting Trolly → Agitator → Macropress → Testing Agitator → Labeling → Release
```

### Key Features

- **End-to-End Integration**: UI → API → Function App → Azure Digital Twins
- **Real-time Updates**: Live twin graph showing device states and relationships
- **Linear Flow Modeling**: Sequential processing with dependencies
- **KPI Tracking**: Idle time, processing time, throughput metrics
- **Azure Integration**: Full Digital Twins support with telemetry streaming

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│   Simulation    │────────▶│  Azure Function  │────────▶│  Azure Digital      │
│   Engine        │  HTTP   │  App             │  SDK    │  Twins              │
│   (Python)      │         │  (Telemetry)     │         │  (DTDL Graph)       │
└─────────────────┘         └──────────────────┘         └─────────────────────┘
        │                                                            │
        │                                                            │
        ▼                                                            ▼
┌─────────────────┐                                       ┌─────────────────────┐
│   FastAPI       │                                       │  Digital Twins      │
│   REST API      │                                       │  Explorer           │
└─────────────────┘                                       └─────────────────────┘
        │
        ▼
┌─────────────────┐
│   React UI      │
│   (Dashboard)   │
└─────────────────┘
```

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
- FastAPI (for API server)
- Azure CLI (for Azure Digital Twins integration)
- Azure subscription (for Digital Twins deployment)

## Installation

```bash
# Install package
pip install -e .

# Install Azure dependencies
pip install -r requirements-azure.txt

# Install dev dependencies (optional)
pip install -e ".[dev]"
```

## How to Run E2E Locally & in CI

### Prerequisites

1. **Azure Resources** (if using Azure integration):
   - Azure Digital Twins instance
   - Azure Function App (optional - direct ADT connection also supported)
   - Proper role assignments configured

2. **Local Setup**:
   - Python 3.9+
   - Dependencies installed (`pip install -r requirements.txt`)

### Local Testing (Without Azure)

For local development without Azure resources:

```bash
# 1. Start the API server
export ENABLE_AZURE_INTEGRATION=false
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 2. In another terminal, run the smoke test
python smoke_test.py --skip-simulation  # Quick test
# or
python smoke_test.py  # Full test with simulation
```

Expected output:
```
✅ Test 1: API Health Check
✅ Test 2: Template Configuration
✅ Test 3: Device ID Mapping
⏭️  Test 4: Azure Configuration (skipped: Azure integration disabled)
```

### Local Testing (With Azure)

For testing the complete E2E flow with Azure:

```bash
# 1. Configure Azure credentials
az login

# 2. Set environment variables
export ENABLE_AZURE_INTEGRATION=true
export AZURE_DIGITAL_TWINS_ENDPOINT="https://your-instance.api.eus.digitaltwins.azure.net"
# Optional: Use Function App instead of direct connection
export AZURE_FUNCTION_ENDPOINT="https://your-function.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="your-function-key"

# 3. Create twins if not already done
python azure_integration/scripts/create_linear_flow_twins.py \
  --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT

# 4. Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 5. Run smoke test
python smoke_test.py
```

Expected output:
```
✅ Test 1: API Health Check
✅ Test 2: Template Configuration
✅ Test 3: Device ID Mapping
✅ Test 4: Azure Configuration
✅ Test 5: Simulation Execution
✅ Test 6: Azure Update Verification
```

### CI/CD Integration

For automated testing in CI pipelines:

```yaml
# Example GitHub Actions workflow
name: E2E Smoke Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Start API server
        run: |
          export ENABLE_AZURE_INTEGRATION=false
          uvicorn api.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
      
      - name: Run smoke test
        run: python smoke_test.py --skip-simulation
```

### Troubleshooting E2E Flow

If the E2E flow is not working:

1. **Check API is running**:
   ```bash
   curl http://localhost:8000/
   ```

2. **Verify device configuration**:
   ```bash
   curl http://localhost:8000/templates/platelet-pooling | jq '.devices[].id'
   ```

3. **Test Azure Function permissions** (if using Function App):
   ```bash
   ./configure_function_permissions.sh <resource-group> <function-app> <dt-instance>
   ```

4. **Check Function App logs**:
   ```bash
   az webapp log tail --name <function-app> --resource-group <resource-group>
   ```

5. **Verify twins exist in ADT**:
   ```bash
   az dt twin query --dt-name <instance> --query-command "SELECT * FROM DIGITALTWINS"
   ```

See [docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md) for detailed troubleshooting.

## Quick Start - Platelet Pooling Simulation

### 1. Run Local Simulation

```python
from simulation_engine import SimulationEngine

# Load the platelet pooling configuration
import json
with open('platelet_pooling_config.json') as f:
    config = json.load(f)

# Run simulation
engine = SimulationEngine(config)
results = engine.run()

print(f"Simulated {results['summary']['simulation_time_seconds']} seconds")
print(f"Completed {results['summary']['total_flows_completed']} flows")
print(f"Total events: {results['summary']['total_events']}")
```

### 2. Start API Server

```bash
# Set environment variables (optional for local testing)
export ENABLE_AZURE_INTEGRATION=false

# Start API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at `http://localhost:8000/docs`

### 3. Setup Azure Digital Twins (Production)

See **[LINEAR_FLOW_SETUP.md](LINEAR_FLOW_SETUP.md)** for complete Azure setup instructions.

Quick setup:
```bash
# 1. Create Digital Twins instance
az dt create --dt-name platelet-dt --resource-group my-rg --location eastus

# 2. Upload models
az dt model create --dt-name platelet-dt --models azure_integration/dtdl_models/*.json

# 3. Create device twins with relationships
export AZURE_DIGITAL_TWINS_ENDPOINT="https://platelet-dt.api.eus.digitaltwins.azure.net"
python azure_integration/scripts/create_linear_flow_twins.py --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT

# 4. Enable Azure integration in API
export ENABLE_AZURE_INTEGRATION=true
uvicorn api.main:app --reload
```

### 4. Test End-to-End Flow

```bash
# Run comprehensive test
python test_end_to_end_flow.py
```

This will test:
- API connection
- Azure configuration
- Digital Twin creation
- Simulation execution
- Twin updates

## Device Configuration

The platelet pooling process uses 10 devices in linear sequence:

| Device ID | Type | Capacity | Function |
|-----------|------|----------|----------|
| buffy_coat_packs | material | 10 | Initial blood product storage |
| platelet_washing | machine | 10 | Washing and preparation |
| centrifuge | machine | 10 | Separation by centrifugation |
| separator_macropress | machine | 10 | Platelet separation |
| resting_trolly | material | 15 | Temporary storage/resting |
| agitator | machine | 10 | Mixing and agitation |
| macropress | machine | 10 | Final pressing |
| testing_agitator | machine | 10 | Quality testing |
| labeling | workstation | 10 | Product labeling |
| release | workstation | 10 | Final release checkpoint |

## Digital Twin Graph

The Digital Twins graph shows:
- **10 device nodes** (one for each processing stage)
- **9 "feedsInto" relationships** (showing linear flow)
- **Real-time KPIs** (status, throughput, idle time, processing time)

View in Azure Digital Twins Explorer to see the complete graph.

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
