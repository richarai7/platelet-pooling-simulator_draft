#!/usr/bin/env python3
"""Test with explicit capacity verification and module reload."""

import sys
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

# Force reload of templates module
import templates
importlib.reload(templates)

from simulation_engine import SimulationEngine
from templates import get_multi_batch_template

print("\n" + "="*70)
print("TESTING WITH FORCE RELOAD")
print("="*70)

# Get config
config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Verify capacities are actually updated
print("\n✓ Verifying all device capacities:")
for device in config['devices']:
    cap = device['capacity']
    symbol = "✓" if cap >= 3 else "⚠️"
    print(f"  {symbol} {device['id']:<25} capacity: {cap}")

# Also check the base template
print("\n✓ Checking base template (should still have lower capacities for single-batch):")
from templates import get_platelet_template
base = get_platelet_template()
print(f"  Base centrifuge capacity: {base['devices'][0]['capacity']}")
print(f"  Multi-batch centrifuge capacity: {config['devices'][0]['capacity']}")

if base['devices'][0]['capacity'] == config['devices'][0]['capacity']:
    print("\n⚠️  WARNING: Base and multi-batch have same capacity - template may not be working correctly")
else:
    print("\n✓ Templates are distinct")

print("\n" + "-"*70)
print("Running simulation...")
print("-"*70)

engine = SimulationEngine(config)
results = engine.run()

if 'error' in results:
    print(f"\n❌ DEADLOCK: {results['error']['message']}")
else:
    print(f"\n✅ SUCCESS!")
    print(f"   Flows completed: {results['summary']['total_flows_completed']}")
    print(f"   Duration: {results['summary']['simulation_time_seconds']/3600:.2f} hours")

print("\n" + "="*70 + "\n")
