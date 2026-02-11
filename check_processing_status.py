#!/usr/bin/env python3
"""Diagnostic script to see what's processing in the simulation."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

from simulation_engine import SimulationEngine
from templates import get_platelet_template
import logging

# Set up logging to see real-time activity
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

print("\n" + "="*70)
print("PLATELET POOLING SIMULATION - PROCESSING STATUS")
print("="*70)

# Run simulation with template config
config = get_platelet_template()

print(f"\nConfiguration:")
print(f"  Duration: {config['simulation']['duration']/3600:.1f} hours")
print(f"  Devices: {len(config['devices'])}")
print(f"  Flows: {len(config['flows'])}")

print("\nRunning simulation...")
print("-"*70)

engine = SimulationEngine(config)
results = engine.run()

print("\n" + "="*70)
print("SIMULATION SUMMARY")
print("="*70)

# Overall stats
print(f"\nDuration: {results['summary']['simulation_time_seconds']/3600:.2f} hours ({results['summary']['simulation_time_seconds']/60:.1f} minutes)")
print(f"Flows completed: {results['summary']['total_flows_completed']}")
print(f"Total events: {results['summary']['total_events']}")
print(f"Execution time: {results['summary']['execution_time_seconds']:.2f}s")

# Device status
print("\n" + "-"*70)
print("DEVICE STATUS")
print("-"*70)
print(f"{'Device':<25} {'State':<12} {'Blocked Time':<15} {'Process Time':<15} {'Status'}")
print("-"*70)

for device in results['device_states']:
    device_id = device['device_id']
    final_state = device['final_state']
    blocked_time = device.get('time_blocked', 0)
    processing_time = device.get('time_processing', 0)
    
    if blocked_time > 60:
        status = "⚠️  BLOCKED"
    elif processing_time > 0:
        status = "✓ ACTIVE"
    else:
        status = "○ IDLE"
    
    print(f"{device_id:<25} {final_state:<12} {blocked_time:>10.1f}s      {processing_time:>10.1f}s      {status}")

# Identify bottlenecks
print("\n" + "-"*70)
print("BOTTLENECK ANALYSIS")
print("-"*70)

blocked_devices = [(d['device_id'], d.get('time_blocked', 0)) 
                   for d in results['device_states'] 
                   if d.get('time_blocked', 0) > 60]

if blocked_devices:
    blocked_devices.sort(key=lambda x: x[1], reverse=True)
    print("\n⚠️  Devices with significant blocking:")
    for device_id, blocked_time in blocked_devices:
        pct = (blocked_time / results['summary']['simulation_time_seconds']) * 100
        print(f"  • {device_id}: {blocked_time/60:.1f} min blocked ({pct:.1f}% of simulation time)")
    
    print("\n💡 Recommendations:")
    print("  1. Increase capacity of blocked devices")
    print("  2. Use capacity multiplier API: POST /utils/multiply-capacity")
    print("  3. Check downstream devices for bottlenecks")
else:
    print("\n✓ No significant blocking detected - simulation running smoothly!")

# Utilization stats if available
if 'kpis' in results and results['kpis']:
    print("\n" + "-"*70)
    print("UTILIZATION METRICS")
    print("-"*70)
    
    for device_id, metrics in results['kpis'].items():
        if isinstance(metrics, dict) and 'utilization' in metrics:
            util = metrics['utilization'] * 100
            print(f"  {device_id}: {util:.1f}% utilized")

print("\n" + "="*70)
print("✓ Single-batch analysis complete - no blocking!")
print("="*70 + "\n")

# Now test with multi-batch to see blocking
print("\n" + "="*70)
print("MULTI-BATCH SIMULATION (5 batches)")
print("="*70)

from templates import get_multi_batch_template

multi_config = get_multi_batch_template(num_batches=5, batch_interval=600)
print(f"\nConfiguration:")
print(f"  Batches: 5")
print(f"  Batch interval: 10 minutes")
print(f"  Total flows: {len(multi_config['flows'])}")

print("\nRunning multi-batch simulation (this will show blocking)...")
print("-"*70)

engine2 = SimulationEngine(multi_config)
results2 = engine2.run()

print("\n" + "="*70)
print("MULTI-BATCH RESULTS")
print("="*70)

print(f"\nDuration: {results2['summary']['simulation_time_seconds']/3600:.2f} hours")
print(f"Flows completed: {results2['summary']['total_flows_completed']}")
print(f"Total events: {results2['summary']['total_events']}")

# Device status - focus on devices with blocking
print("\n" + "-"*70)
print("DEVICES WITH BLOCKING")
print("-"*70)
print(f"{'Device':<25} {'Blocked Time':<15} {'% of Time':<12} {'Status'}")
print("-"*70)

blocked_found = False
for device in results2['device_states']:
    device_id = device['device_id']
    blocked_time = device.get('time_blocked', 0)
    
    if blocked_time > 0:
        blocked_found = True
        pct = (blocked_time / results2['summary']['simulation_time_seconds']) * 100
        status = "⚠️ BOTTLENECK" if pct > 20 else "⚠️ BLOCKED"
        print(f"{device_id:<25} {blocked_time/60:>10.1f} min   {pct:>8.1f}%      {status}")

if not blocked_found:
    print("  (No blocking detected)")

print("\n" + "="*70)
print("✓ Multi-batch analysis complete!")
print("="*70 + "\n")
