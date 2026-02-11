#!/usr/bin/env python3
"""Detailed flow analysis to understand the deadlock."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

from simulation_engine import SimulationEngine
from templates import get_multi_batch_template

print("\n" + "="*70)
print("DETAILED FLOW ANALYSIS")
print("="*70)

config = get_multi_batch_template(num_batches=5, batch_interval=600)

# Analyze flow structure
print(f"\nTotal flows: {len(config['flows'])}")

# Group flows by from_device
from_device_count = {}
for flow in config['flows']:
    from_dev = flow['from_device']
    from_device_count[from_dev] = from_device_count.get(from_dev, 0) + 1

print("\nFlows originating from each device:")
for device, count in sorted(from_device_count.items(), key=lambda x: x[1], reverse=True):
    # Get device capacity
    device_info = next((d for d in config['devices'] if d['id'] == device), None)
    capacity = device_info['capacity'] if device_info else 'N/A'
    
    status = "⚠️ OVERLOAD" if count > capacity * 2 else "✓ OK"
    print(f"  {device:<25} {count:>3} flows (capacity: {capacity:>2}) {status}")

# Analyze centrifuge specifically
print("\n" + "-"*70)
print("CENTRIFUGE ANALYSIS")
print("-"*70)

centrifuge_flows = [f for f in config['flows'] if f['from_device'] == 'centrifuge']
print(f"Total flows from centrifuge: {len(centrifuge_flows)}")

# Group by batch
batch_flows = {}
for flow in centrifuge_flows:
    batch_id = flow.get('batch_id', 'unknown')
    if batch_id not in batch_flows:
        batch_flows[batch_id] = []
    batch_flows[batch_id].append(flow)

print(f"\nFlows per batch:")
for batch_id in sorted(batch_flows.keys()):
    flows = batch_flows[batch_id]
    print(f"  {batch_id}: {len(flows)} flows")
    for flow in flows:
        to_dev = flow['to_device']
        deps = flow.get('dependencies')
        arrival = flow.get('arrival_time', 'N/A')
        print(f"    → {flow['flow_id'][:30]:<30} to {to_dev:<20} arrival_time={arrival}")

# Check if centrifuge capacity is sufficient
centrifuge_capacity = next((d['capacity'] for d in config['devices'] if d['id'] == 'centrifuge'), 0)
print(f"\nCentrifuge capacity: {centrifuge_capacity}")
print(f"Simultaneous demands: {len(centrifuge_flows)} flows over time")
print(f"Batches arriving: 5 batches, 10 min apart")
print(f"Expected simultaneous load: ~{min(5, centrifuge_capacity * 2)} batches competing")

if len(centrifuge_flows) > centrifuge_capacity * 3:
    print("\n⚠️  WARNING: Centrifuge may be overloaded!")
    print(f"   Recommendation: Increase centrifuge capacity to {len(centrifuge_flows) // 3} or higher")
else:
    print("\n✓ Centrifuge capacity should be sufficient")

print("\n" + "="*70 + "\n")
