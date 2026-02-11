#!/usr/bin/env python3
"""Debug multi-batch simulation to see where the actual bottleneck is."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

from simulation_engine import SimulationEngine
from templates import get_multi_batch_template
import logging

# Enable detailed logging to see what's happening
logging.basicConfig(
    level=logging.ERROR,  # Only show errors
    format='[%(levelname)s] %(message)s'
)

print("\n" + "="*70)
print("MULTI-BATCH SIMULATION DEBUG")
print("="*70)

# Get the template
config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Check current capacities
print("\nCurrent Device Capacities:")
print("-"*70)
for device in config['devices']:
    print(f"  {device['id']:<25} capacity: {device['capacity']}")

print("\n" + "-"*70)
print("Running simulation with 5 batches...")
print("-"*70)

engine = SimulationEngine(config)
results = engine.run()

print("\n" + "="*70)
print("RESULTS")
print("="*70)

# Check for deadlock
if 'error' in results:
    print("\n⚠️  DEADLOCK DETECTED!")
    print(f"Type: {results['error']['deadlock_info']['deadlock_type']}")
    print(f"Message: {results['error']['message']}")
    
    print("\nBlocked devices:")
    for device in results['error']['deadlock_info']['blocked_devices']:
        print(f"  • {device['device_id']}: blocked since T={device['blocked_since']:.1f}s")
    
    print("\nWait graph (who is waiting for whom):")
    wait_graph = results['error']['deadlock_info']['wait_graph']
    for device, waiting_for in wait_graph.items():
        print(f"  {device} → waiting for: {', '.join(waiting_for)}")
    
else:
    print("\n✓ No deadlock!")
    print(f"Flows completed: {results['summary']['total_flows_completed']}")
    print(f"Duration: {results['summary']['simulation_time_seconds']/60:.1f} minutes")

# Show device blocking statistics
print("\n" + "-"*70)
print("DEVICE BLOCKING STATISTICS")
print("-"*70)
print(f"{'Device':<25} {'Blocked Time':<15} {'% of Total'}")
print("-"*70)

for device in results['device_states']:
    blocked_time = device.get('time_blocked', 0)
    if blocked_time > 0:
        pct = (blocked_time / results['summary']['simulation_time_seconds']) * 100
        print(f"{device['device_id']:<25} {blocked_time/60:>10.1f} min   {pct:>8.1f}%")

print("\n" + "="*70 + "\n")
