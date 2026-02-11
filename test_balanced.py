#!/usr/bin/env python3
"""Find the minimum working capacities for 5-batch simulation."""

import sys
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

import templates
importlib.reload(templates)

from simulation_engine import SimulationEngine
from templates import get_multi_batch_template

print("\n" + "="*70)
print("FINDING OPTIMAL CAPACITIES FOR 5 BATCHES")
print("="*70)

config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Set balanced capacities based on load analysis
# Most devices: 5 (one per batch)
# Pooling station: 10 (receives 2 flows per batch)
# Storage, packaging: can stay higher

capacity_map = {
    "centrifuge": 10,  # High demand - 2 flows per batch
    "platelet_separator": 10,
    "pooling_station": 15,  # Receives from 2 sources per batch
    "weigh_register": 10,
    "sterile_connect": 10,
    "test_sample": 10,
    "quality_check": 10,
    "label_station": 10,
    "storage_unit": 50,  # Already high
    "final_inspection": 10,
    "packaging_station": 10
}

for device in config['devices']:
    if device['id'] in capacity_map:
        device['capacity'] = capacity_map[device['id']]

config['simulation']['deadlock_timeout'] = 900  # 15 minutes

print("\nOptimized capacities:")
for device in config['devices']:
    print(f"  {device['id']:<25} capacity: {device['capacity']}")

print("\n" + "-"*70)
print("Running simulation with balanced capacities...")
print("-"*70)

engine = SimulationEngine(config)
results = engine.run()

print("\n" + "="*70)
print("RESULTS")
print("="*70)

if 'error' in results:
    print(f"\n❌ DEADLOCK!")
    print(f"Message: {results['error']['message']}")
else:
    print(f"\n✅ SUCCESS!")
    print(f"   Flows completed: {results['summary']['total_flows_completed']}")
    print(f"   Duration: {results['summary']['simulation_time_seconds']/60:.1f} min")
    print(f"   Events: {results['summary']['total_events']}")
    
    print("\n   Blocking analysis:")
    any_blocked = False
    for device in results['device_states']:
        blocked = device.get('time_blocked', 0)
        if blocked > 60:  # More than 1 minute
            any_blocked = True
            pct = (blocked / results['summary']['simulation_time_seconds']) * 100
            print(f"     {device['device_id']:<25} {blocked/60:.1f} min ({pct:.1f}%)")
    
    if not any_blocked:
        print("     ✓ No significant blocking!")

print("\n" + "="*70 + "\n")
