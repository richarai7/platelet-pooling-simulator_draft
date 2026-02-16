================================================================================
HOW TO CHECK CURRENT CODE - QUICK REFERENCE
================================================================================

FASTEST WAY (3 commands):
--------------------------

1. Health check (5 seconds):
   python -c "import sys; sys.path.insert(0, 'src'); from simulation_engine import SimulationEngine; print('✅ OK')"

2. Full simulation (35 seconds):
   python -c "import sys, json; from pathlib import Path; sys.path.insert(0, str(Path('.') / 'src')); from simulation_engine import SimulationEngine; result = SimulationEngine(json.load(open('default_config.json'))).run(); print(f'✅ Flows: {result[\"summary\"][\"total_flows_completed\"]}, Devices: {len(result[\"device_states\"])}')"

3. Azure integration test (40 seconds):
   python run_simulation_with_adt.py --config default_config.json --mock

EXPECTED RESULTS:
-----------------
✅ Code is working!
✅ Flows: 20, Devices: 11
✅ All 11 device twins synced and updated

WHAT WORKS NOW:
---------------
✅ Device twin creation (11 devices from config)
✅ Simulation execution (20 flows, 40 events)
✅ Metrics calculation from event timeline
✅ Final state updates to all twins
✅ Mock mode (no Azure needed)
✅ Accelerated mode (100x speed)

CURRENT LIMITATION:
-------------------
⚠️  Twins updated AFTER simulation, not during (no real-time live sync yet)

FULL GUIDES:
------------
- HOW_TO_CHECK_CODE.md    - Complete step-by-step guide
- QUICK_CHECK.md          - Quick start summary
- FIXES_SUMMARY.md        - Recent fixes explained

Run this for complete test:
python run_simulation_with_adt.py --config default_config.json --mock

================================================================================
