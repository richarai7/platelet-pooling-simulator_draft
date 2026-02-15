# Quick Start: Check Current Code

## TL;DR - The Fastest Way

### 1. Quick Health Check (5 seconds)
```bash
cd /home/runner/work/platelet-pooling-simulator_draft/platelet-pooling-simulator_draft
python -c "import sys; sys.path.insert(0, 'src'); from simulation_engine import SimulationEngine; print('✅ Code is working!')"
```

### 2. Run Full Simulation Test (35 seconds)
```bash
python -c "
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))
from simulation_engine import SimulationEngine

with open('default_config.json') as f:
    config = json.load(f)

result = SimulationEngine(config).run()
print(f'✅ SUCCESS!')
print(f'Flows: {result[\"summary\"][\"total_flows_completed\"]}, Devices: {len(result[\"device_states\"])}, Time: {result[\"summary\"][\"execution_time_seconds\"]:.1f}s')
"
```

### 3. Test Azure Digital Twins Integration (40 seconds)
```bash
python run_simulation_with_adt.py --config default_config.json --mock
```

## What You Should See

### Health Check Output:
```
✅ Code is working!
```

### Full Simulation Output:
```
✅ SUCCESS!
Flows: 20, Devices: 11, Time: 32.9s
```

### Azure Integration Output:
```
================================================================================
SYNCHRONIZING DEVICE TWINS WITH CONFIGURATION
================================================================================
Found 11 devices in configuration
Syncing device: centrifuge
  ✓ Synced centrifuge
  ... (9 more devices)
  ✓ Synced packaging_station

✅ Device synchronization complete

================================================================================
RUNNING SIMULATION WITH AZURE DIGITAL TWINS INTEGRATION
================================================================================
✓ Telemetry streaming enabled

1. Creating simulation twin: sim_20260215_XXXXXX

2. Initializing simulation engine...

3. Running simulation...
   Execution mode: Accelerated (100x speed)

4. Simulation complete!
   ✓ Flows completed: 20
   ✓ Total events: 40
   ✓ Simulation time: 3294.79 seconds
   ✓ Execution time: 32.95 seconds

5. Streaming final device states to Azure Digital Twins...
   ✓ Updated centrifuge: Idle
   ... (9 more devices)
   ✓ Updated packaging_station: Idle

================================================================================
✅ SIMULATION AND SYNC COMPLETE!
================================================================================
```

## Current Capabilities ✅

### Working Features:
1. ✅ **Device twin creation** - All 11 devices from config
2. ✅ **Simulation twin creation** - With metadata and status
3. ✅ **Simulation execution** - 20 flows, 40 events
4. ✅ **Metrics calculation** - From event timeline
5. ✅ **Final state updates** - All twins updated after completion
6. ✅ **Mock mode** - Test without Azure subscription
7. ✅ **Accelerated mode** - 100x speed (3294s sim in 33s real time)

### Current Limitation:
⚠️ **Live sync during simulation**: Twins are updated AFTER simulation completes, not in real-time during execution.

### What This Means:
- ✅ You CAN see all devices in the twin graph
- ✅ You CAN see their properties after simulation
- ✅ Adding/removing devices in config WILL update twins
- ⚠️ You CANNOT watch state changes happen live during simulation

## Full Documentation

For complete details, see:
- **HOW_TO_CHECK_CODE.md** - Comprehensive guide with all commands
- **FIXES_SUMMARY.md** - Recent fixes applied
- **AZURE_INTEGRATION_COMPLETE.md** - Full Azure integration guide
- **QUICK_START_GUIDE.md** - Getting started with Azure

## Common Issues

### "No module named simulation_engine"
**Solution**: Add src to path:
```bash
python -c "import sys; sys.path.insert(0, 'src'); from simulation_engine import SimulationEngine"
```

### "Azure SDK not installed" warning
**Solution**: This is normal in mock mode. Ignore it or install:
```bash
pip install azure-identity azure-digitaltwins-core
```

### Simulation takes too long
**Solution**: Check execution_mode in config. Should be "accelerated" with speed_multiplier: 100

## Next Steps

1. **Read the full guide**: `cat HOW_TO_CHECK_CODE.md`
2. **Deploy to Azure**: See `AZURE_INTEGRATION_COMPLETE.md`
3. **Add live sync**: See the note in line 186 of `run_simulation_with_adt.py`
4. **Run tests**: `python -m pytest tests/ -v` (requires pytest)

---

**Created**: 2026-02-15  
**Status**: All core functionality verified and working ✅
