# How to Check Current Code - Step by Step Guide

This guide provides step-by-step commands to check, test, and verify the current codebase.

## Prerequisites

Make sure you're in the project directory:
```bash
cd /home/runner/work/platelet-pooling-simulator_draft/platelet-pooling-simulator_draft
```

## Step 1: Check Installation & Dependencies

### Option A: Install as package (recommended)
```bash
pip install -e .
```

Then verify:
```bash
python -c "from simulation_engine import SimulationEngine; print('✓ Simulation engine imported successfully')"
```

### Option B: Use without installation (quick check)
The code works without installation by adding src to path:
```bash
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.') / 'src')); from simulation_engine import SimulationEngine; print('✓ Simulation engine imported successfully')"
```

**Note**: All examples below use Option B (no installation needed) for quick testing.

## Step 2: Run Unit Tests

### Run all unit tests
```bash
python -m pytest tests/unit/ -v
```

### Run a specific test file
```bash
python -m pytest tests/unit/test_event_scheduler.py -v
```

### Run integration tests
```bash
python -m pytest tests/integration/ -v
```

### Run ALL tests with coverage
```bash
python -m pytest tests/ -v --cov=simulation_engine --cov-report=term-missing
```

## Step 3: Test Basic Simulation

### Quick simulation test (one-liner)
```bash
python -c "from simulation_engine import SimulationEngine; config={'simulation':{'duration':100,'random_seed':42,'execution_mode':'accelerated'},'devices':[],'flows':[],'output_options':{'include_history':False,'include_events':False}}; results=SimulationEngine(config).run(); print(f'✓ Simulation complete! Events: {results[\"summary\"][\"total_events\"]}, Time: {results[\"summary\"][\"execution_time_seconds\"]:.3f}s')"
```

### Run with default configuration
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))
from simulation_engine import SimulationEngine
import json

with open('default_config.json', 'r') as f:
    config = json.load(f)

engine = SimulationEngine(config)
result = engine.run()

print(f'✅ Simulation successful!')
print(f'   Flows completed: {result[\"summary\"][\"total_flows_completed\"]}')
print(f'   Total events: {result[\"summary\"][\"total_events\"]}')
print(f'   Simulation time: {result[\"summary\"][\"simulation_time_seconds\"]:.2f}s')
print(f'   Execution time: {result[\"summary\"][\"execution_time_seconds\"]:.2f}s')
"
```

## Step 4: Test Azure Digital Twins Integration (Mock Mode)

### Test end-to-end simulation with Azure Digital Twins (no Azure needed)
```bash
python run_simulation_with_adt.py --config default_config.json --mock
```

Expected output:
- ✅ Device synchronization complete (11 devices)
- ✅ Simulation runs successfully
- ✅ All device twins updated with metrics
- ✅ Simulation twin created and updated

### Test with telemetry disabled
```bash
python run_simulation_with_adt.py --config default_config.json --mock --no-telemetry
```

### Test without device sync
```bash
python run_simulation_with_adt.py --config default_config.json --mock --no-sync
```

## Step 5: Check Azure Integration Components

### Test Digital Twins client wrapper
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper

client = DigitalTwinsClientWrapper(adt_endpoint='mock://localhost')
print('✓ Digital Twins client initialized successfully')
"
```

### Test telemetry streamer
```bash
python -c "
import sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
from azure_integration.telemetry_streamer import TelemetryStreamer

async def test():
    client = DigitalTwinsClientWrapper(adt_endpoint='mock://localhost')
    streamer = TelemetryStreamer(digital_twins_client=client)
    print('✓ Telemetry streamer initialized successfully')

asyncio.run(test())
"
```

## Step 6: Verify Code Quality

### Run type checking (if mypy is installed)
```bash
mypy src/simulation_engine/ --ignore-missing-imports 2>&1 | head -20
```

### Run linting (if pylint is installed)
```bash
pylint src/simulation_engine/*.py --max-line-length=120 2>&1 | head -30
```

### Check code formatting (if black is installed)
```bash
black --check src/simulation_engine/ tests/ --line-length=120 2>&1 | head -20
```

## Step 7: Test API Server (Optional)

### Start the API server
```bash
# In a separate terminal
cd api
uvicorn main:app --reload --port 8000
```

### Test API health (in another terminal)
```bash
curl http://localhost:8000/
```

### Test API endpoints
```bash
# Get template configuration
curl http://localhost:8000/templates/platelet-pooling

# Run a simulation via API
curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d '{"config":{"simulation":{"duration":100,"random_seed":42,"execution_mode":"accelerated"},"devices":[],"flows":[],"output_options":{"include_history":false,"include_events":false}}}'
```

## Step 8: Test UI (Optional)

### Install UI dependencies
```bash
cd ui
npm install
```

### Start development server
```bash
npm run dev
```

The UI should be available at http://localhost:5173

## Step 9: Check Git Status

### See what files have changed
```bash
git status
```

### See detailed changes
```bash
git diff
```

### See recent commits
```bash
git log --oneline -10
```

## Step 10: Comprehensive Test Suite

### Run the comprehensive test script
```bash
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))

import asyncio
import json

print("\n" + "="*80)
print("COMPREHENSIVE CODE CHECK")
print("="*80 + "\n")

# Test 1: Import simulation engine
try:
    from simulation_engine import SimulationEngine
    print("✅ Test 1: Simulation engine imports successfully")
except Exception as e:
    print(f"❌ Test 1 FAILED: {e}")

# Test 2: Run basic simulation
try:
    config = {
        "simulation": {"duration": 100, "random_seed": 42, "execution_mode": "accelerated"},
        "devices": [], "flows": [],
        "output_options": {"include_history": False, "include_events": False}
    }
    engine = SimulationEngine(config)
    result = engine.run()
    assert result['summary']['total_events'] >= 0
    print("✅ Test 2: Basic simulation runs successfully")
except Exception as e:
    print(f"❌ Test 2 FAILED: {e}")

# Test 3: Run with default config
try:
    with open('default_config.json', 'r') as f:
        config = json.load(f)
    engine = SimulationEngine(config)
    result = engine.run()
    assert result['summary']['total_flows_completed'] == 20
    assert len(result['device_states']) == 11
    print(f"✅ Test 3: Default config simulation runs successfully")
    print(f"   - Flows completed: {result['summary']['total_flows_completed']}")
    print(f"   - Devices tracked: {len(result['device_states'])}")
except Exception as e:
    print(f"❌ Test 3 FAILED: {e}")

# Test 4: Azure integration imports
try:
    from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
    from azure_integration.telemetry_streamer import TelemetryStreamer
    print("✅ Test 4: Azure integration components import successfully")
except Exception as e:
    print(f"❌ Test 4 FAILED: {e}")

# Test 5: End-to-end ADT simulation (mock mode)
try:
    from run_simulation_with_adt import SimulationADTRunner
    
    async def test_adt():
        with open('default_config.json', 'r') as f:
            config = json.load(f)
        
        runner = SimulationADTRunner(
            config=config,
            adt_endpoint='mock://localhost',
            sync_devices=True,
            stream_telemetry=True
        )
        
        result = await runner.run_complete_flow()
        assert len(result['device_states']) == 11
        return result
    
    result = asyncio.run(test_adt())
    print("✅ Test 5: End-to-end Azure Digital Twins integration works")
    print(f"   - All 11 device twins synced and updated")
except Exception as e:
    print(f"❌ Test 5 FAILED: {e}")

print("\n" + "="*80)
print("COMPREHENSIVE CHECK COMPLETE")
print("="*80 + "\n")
EOF
```

## Quick Reference: Most Important Commands

### 1. Quick health check
```bash
python -c "from simulation_engine import SimulationEngine; print('✓ OK')"
```

### 2. Run unit tests
```bash
python -m pytest tests/unit/ -v
```

### 3. Test default simulation
```bash
python run_simulation_with_adt.py --config default_config.json --mock
```

### 4. Run all tests
```bash
python -m pytest tests/ -v
```

### 5. Check git status
```bash
git status && git log --oneline -5
```

## Troubleshooting

### If imports fail
```bash
# Reinstall in development mode
pip install -e .
```

### If pytest not found
```bash
pip install pytest pytest-cov
```

### If Azure SDK warnings appear
```bash
# These are expected in mock mode and can be ignored
# To install Azure SDK (optional):
pip install azure-identity azure-digitaltwins-core
```

### If tests fail
```bash
# Check Python version (requires 3.8+)
python --version

# Check installed packages
pip list | grep -E "pytest|simulation"

# Run with more verbose output
python -m pytest tests/unit/ -vv -s
```

## Expected Results

### Unit Tests
- Should show all tests passing (green)
- Typical run time: 1-5 seconds

### Default Simulation
- 20 flows completed
- 40 events processed
- 11 devices tracked
- Execution time: 30-40 seconds (100x accelerated mode)

### Azure Digital Twins Integration (Mock)
- 11 device twins created
- Simulation twin created
- All twins updated with final metrics
- No errors or exceptions

## Next Steps

After verifying the code works:

1. **For production Azure deployment**: See `AZURE_INTEGRATION_COMPLETE.md`
2. **For UI development**: See `docs/guides/UI_CHANGES.md`
3. **For API usage**: See `api/README.md`
4. **For understanding the fixes**: See `FIXES_SUMMARY.md`

## File Structure Reference

```
.
├── src/simulation_engine/      # Core simulation engine
├── azure_integration/          # Azure Digital Twins integration
├── run_simulation_with_adt.py # Main end-to-end runner
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── api/                        # FastAPI backend
├── ui/                         # React UI
├── default_config.json         # Default configuration
└── requirements.txt            # Python dependencies
```
