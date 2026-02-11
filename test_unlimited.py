#!/usr/bin/env python3
"""Test with unlimited capacity to isolate the issue."""

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
print("MULTI-BATCH WITH UNLIMITED CAPACITY")
print("="*70)

config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Set ALL devices to unlimited capacity
for device in config['devices']:
    device['capacity'] = 100  # Effectively unlimited

# Increase deadlock timeout
config['simulation']['deadlock_timeout'] = 1200  # 20 minutes

print(f"\nConfiguration:")
print(f"  All devices set to capacity: 100")
print(f"  Deadlock timeout: 20 minutes")
print(f"  Total flows: {len(config['flows'])}")

print("\n" + "-"*70)
print("Running simulation...")
print("-"*70)

engine = SimulationEngine(config)
results = engine.run()

print("\n" + "="*70)
print("RESULTS")
print("="*70)

if 'error' in results:
    print(f"\n❌ DEADLOCK EVEN WITH UNLIMITED CAPACITY!")
    print(f"This suggests a BUG in the simulation logic, not a capacity issue.")
    print(f"\nError: {results['error']['message']}")
else:
    print(f"\n✅ SUCCESS!")
    print(f"   Flows completed: {results['summary']['total_flows_completed']}")
    print(f"   Duration: {results['summary']['simulation_time_seconds']/60:.1f} min")
    print(f"   Events: {results['summary']['total_events']}")

print("\n" + "="*70 + "\n")
