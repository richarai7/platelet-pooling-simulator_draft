"""
WORKING UTILIZATION CALCULATOR
Uses actual event_timeline from API
"""
import requests
import json
from collections import defaultdict

print("="*70)
print("STAFF/DEVICE UTILIZATION ANALYZER")
print("="*70)

# Get multi-batch configuration
print("\n📥 Loading multi-batch template (5 batches)...")
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch")
config = response.json()

print(f"   ✓ {len(config['devices'])} devices")
print(f"   ✓ {len(config['flows'])} flows")

# Run simulation
print("\n⚙️  Running simulation...")
response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
result = response.json()

sim_time = result['results']['summary']['simulation_time_seconds']
print(f"   ✓ Simulation complete: {sim_time/60:.1f} minutes")

# Calculate utilization from event timeline
print("\n📊 Calculating utilization...")

event_timeline = result['results'].get('event_timeline', [])
total_sim_time = sim_time

# Track device busy periods
device_active_periods = defaultdict(list)  # List of (start, end) tuples
device_current_start = {}  # Currently active flows

# Get device capacities
device_info = {d['id']: {'capacity': d['capacity'], 'type': d.get('type', 'device')} 
               for d in config['devices']}

# Process events
for event in event_timeline:
    device_id = event.get('device_id')
    event_type = event['event']  # Using 'event' field, not 'type'
    timestamp = event['timestamp']
    from_state = event.get('from_state')
    to_state = event.get('to_state')
    
    if not device_id:
        continue
    
    if event_type == 'START_PROCESSING' or to_state == 'Processing':
        # Device starts processing - mark as busy
        if device_id not in device_current_start:
            device_current_start[device_id] = timestamp
    
    elif event_type == 'COMPLETE_PROCESSING' or (from_state == 'Processing' and to_state == 'Idle'):
        # Device finishes processing - record busy period
        if device_id in device_current_start:
            start_time = device_current_start[device_id]
            device_active_periods[device_id].append((start_time, timestamp))
            del device_current_start[device_id]

# Calculate total busy time for each device
device_utilization = {}

for device_id, info in device_info.items():
    periods = device_active_periods.get(device_id, [])
    
    # Sum up all busy periods
    total_busy_time = sum(end - start for start, end in periods)
    
    # Calculate utilization (accounting for capacity)
    capacity = info['capacity']
    available_time = total_sim_time * capacity
    utilization_pct = (total_busy_time / available_time * 100) if available_time > 0 else 0
    
    device_utilization[device_id] = {
        'utilization': min(100.0, utilization_pct),
        'busy_time': total_busy_time,
        'available_time': available_time,
        'capacity': capacity,
        'type': info['type'],
        'num_jobs': len(periods)
    }

# Display results
print("\n" + "="*70)
print("UTILIZATION REPORT")
print("="*70)

# Sort by utilization (highest first)
sorted_devices = sorted(device_utilization.items(), 
                        key=lambda x: x[1]['utilization'], 
                        reverse=True)

print(f"\n{'Device':<25} {'Type':<12} {'Cap':<5} {'Jobs':<6} {'Util%':<8} {'Status'}")
print("-"*70)

for device_id, data in sorted_devices:
    util = data['utilization']
    
    # Status indicator
    if util > 85:
        status = "🔴 BOTTLENECK"
    elif util > 70:
        status = "🟡 High"
    elif util > 40:
        status = "🟢 Balanced"
    else:
        status = "⚪ Low"
    
    print(f"{device_id:<25} {data['type']:<12} {data['capacity']:<5} "
          f"{data['num_jobs']:<6} {util:>6.1f}%  {status}")

# Summary stats
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

avg_util = sum(d['utilization'] for d in device_utilization.values()) / len(device_utilization)
bottlenecks = [(d, data) for d, data in device_utilization.items() if data['utilization'] > 85]
high_load = [(d, data) for d, data in device_utilization.items() if 70 < data['utilization'] <= 85]
underutilized = [(d, data) for d, data in device_utilization.items() if data['utilization'] < 30]

print(f"\n📊 Average Utilization: {avg_util:.1f}%")
print(f"   Total Simulation Time: {total_sim_time/60:.1f} minutes")
print(f"   Total Events Processed: {len(event_timeline)}")

print(f"\n🔴 Bottlenecks (>85% utilization): {len(bottlenecks)}")
for device, data in bottlenecks:
    print(f"   • {device}: {data['utilization']:.1f}% (capacity={data['capacity']}, jobs={data['num_jobs']})")

print(f"\n🟡 High Load (70-85% utilization): {len(high_load)}")
for device, data in high_load:
    print(f"   • {device}: {data['utilization']:.1f}% (capacity={data['capacity']}, jobs={data['num_jobs']})")

print(f"\n⚪ Underutilized (<30% utilization): {len(underutilized)}")
for device, data in underutilized:
    print(f"   • {device}: {data['utilization']:.1f}% (capacity={data['capacity']}, jobs={data['num_jobs']})")

# Recommendations
print("\n" + "="*70)
print("💡 ACTIONABLE RECOMMENDATIONS")
print("="*70)

if bottlenecks:
    print("\n🎯 PRIORITY 1: Address Bottlenecks")
    for device, data in bottlenecks:
        new_capacity = data['capacity'] + 1
        expected_new_util = data['utilization'] * data['capacity'] / new_capacity
        improvement = data['utilization'] - expected_new_util
        
        print(f"\n   {device}:")
        print(f"   • Current: {data['capacity']} units at {data['utilization']:.1f}% utilization")
        print(f"   • Recommendation: Add 1 unit (total={new_capacity})")
        print(f"   • Expected result: ~{expected_new_util:.1f}% utilization")
        print(f"   • Benefit: {improvement:.1f}% capacity freed up")

if high_load:
    print("\n⚠️  PRIORITY 2: Monitor High Load Devices")
    for device, data in high_load:
        print(f"   • {device}: {data['utilization']:.1f}% - Watch for increasing workload")

if underutilized:
    print("\n💰 COST OPTIMIZATION: Underutilized Resources")
    for device, data in underutilized:
        if data['capacity'] > 1:
            print(f"   • {device}: Consider reducing capacity {data['capacity']} → {data['capacity']-1}")
        else:
            print(f"   • {device}: {data['utilization']:.1f}% idle - verify if needed")

print("\n" + "="*70)
print("📈 HOW TO TEST CAPACITY CHANGES")
print("="*70)

if bottlenecks:
    top_bottleneck = bottlenecks[0][0]
    print(f"""
Example: Test increasing {top_bottleneck} capacity

1. IN REACT UI:
   • Find device: {top_bottleneck}
   • Change capacity from {device_utilization[top_bottleneck]['capacity']} → {device_utilization[top_bottleneck]['capacity'] + 1}
   • Run simulation
   • Compare completion time

2. VIA API:
   config['devices'].find({top_bottleneck}).capacity = {device_utilization[top_bottleneck]['capacity'] + 1}
   
3. MEASURE IMPACT:
   • Baseline: {sim_time/60:.1f} minutes
   • With increased capacity: Should improve
   • Calculate ROI: Time saved vs. equipment cost
""")
else:
    print("\n✅ No bottlenecks detected!")
    print("   System is well-balanced for current workload.")

print("="*70)
