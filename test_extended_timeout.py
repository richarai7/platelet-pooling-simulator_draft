#!/usr/bin/env python3
"""Test with increased deadlock timeout and detailed event tracking."""

import sys
from pathlib import Path
import importlib
import logging

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

# Reload templates
import templates
importlib.reload(templates)

from simulation_engine import SimulationEngine
from templates import get_multi_batch_template

# Enable INFO logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(message)s'
)

print("\n" + "="*70)
print("MULTI-BATCH WITH EXTENDED DEADLOCK TIMEOUT")
print("="*70)

config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Increase deadlock timeout to 600 seconds (10 minutes) instead of default 300s
config['simulation']['deadlock_timeout'] = 600

print(f"\nConfiguration:")
print(f"  Batches: 5")
print(f"  Deadlock timeout: {config['simulation']['deadlock_timeout']}s (10 min)")
print(f"  Total flows: {len(config['flows'])}")

print("\nDevice capacities:")
for device in config['devices']:
    print(f"  {device['id']:<25} capacity: {device['capacity']}")

print("\n" + "-"*70)
print("Running simulation with extended timeout...")
print("-"*70 + "\n")

engine = SimulationEngine(config)
results = engine.run()

print("\n" + "="*70)
print("RESULTS")
print("="*70)

if 'error' in results:
    print(f"\n❌ DEADLOCK STILL OCCURRED!")
    print(f"Type: {results['error']['deadlock_info']['deadlock_type']}")
    print(f"Message: {results['error']['message']}")
    
    if results['error']['deadlock_info'].get('wait_graph'):
        print("\nWait graph:")
        for dev, waiting in results['error']['deadlock_info']['wait_graph'].items():
            print(f"  {dev} waiting for: {waiting}")
else:
    print(f"\n✅ SUCCESS - NO DEADLOCK!")
    print(f"   Flows completed: {results['summary']['total_flows_completed']}")
    print(f"   Duration: {results['summary']['simulation_time_seconds']/3600:.2f} hours ({results['summary']['simulation_time_seconds']/60:.1f} min)")
    print(f"   Total events: {results['summary']['total_events']}")
    
    # Check for any blocking
    print("\n   Device blocking summary:")
    any_blocked = False
    for device in results['device_states']:
        blocked_time = device.get('time_blocked', 0)
        if blocked_time > 0:
            any_blocked = True
            print(f"     {device['device_id']}: {blocked_time/60:.1f} min blocked")
    
    if not any_blocked:
        print("     No blocking detected!")

print("\n" + "="*70 + "\n")
