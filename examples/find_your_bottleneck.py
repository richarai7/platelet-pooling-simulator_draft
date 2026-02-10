"""
Find the bottleneck in your 11-device simulation
This will tell you WHICH device to change in the UI
"""
import requests
import json

print("="*70)
print("FINDING BOTTLENECK IN YOUR 11-DEVICE SIMULATION")
print("="*70)

# Get the default template (11 devices)
response = requests.get("http://localhost:8000/templates/platelet-pooling")
config = response.json()

print(f"\nYour config has {len(config['devices'])} devices:")
for device in config['devices']:
    print(f"  - {device['id']:25s} capacity={device['capacity']}")

print(f"\nRunning simulation to find bottleneck...")

# Run with state history to track utilization
config['output_options'] = {'include_history': True}

response = requests.post(
    "http://localhost:8000/simulations/run",
    json={"config": config}
)

result = response.json()

# Check if we got the right structure
if 'simulation_time_seconds' in result:
    completion_time = result['simulation_time_seconds']
elif 'results' in result:
    if 'summary' in result['results'] and 'simulation_time_seconds' in result['results']['summary']:
        completion_time = result['results']['summary']['simulation_time_seconds']
        result = result['results']
    elif 'simulation_time_seconds' in result['results']:
        completion_time = result['results']['simulation_time_seconds']
        result = result['results']
else:
    print("\n❌ ERROR: Unexpected API response structure")
    print(json.dumps(result, indent=2)[:1000])
    exit(1)

print(f"\n✅ Simulation complete: {completion_time:.1f} seconds ({completion_time/60:.1f} minutes)")

# Analyze state history if available
state_history = result.get('state_history') or result.get('device_states')
if state_history and isinstance(state_history, dict):
    print("\n" + "="*70)
    print("DEVICE UTILIZATION ANALYSIS")
    print("="*70)
    
    utilizations = {}
    
    for device_id, events in state_history.items():
        if not events:
            continue
        
        processing_time = 0
        last_time = 0
        last_state = 'idle'
        
        for event in events:
            time = event['timestamp']
            state = event['state'].lower()
            
            if last_state == 'processing':
                processing_time += (time - last_time)
            
            last_time = time
            last_state = state
        
        total_time = completion_time
        utilization = (processing_time / total_time * 100) if total_time > 0 else 0
        utilizations[device_id] = utilization
    
    # Sort by utilization
    sorted_devices = sorted(utilizations.items(), key=lambda x: x[1], reverse=True)
    
    print("\nDevices ranked by utilization (highest = bottleneck):\n")
    
    for i, (device_id, util) in enumerate(sorted_devices):
        # Find capacity
        capacity = next((d['capacity'] for d in config['devices'] if d['id'] == device_id), '?')
        
        marker = ""
        if util > 90:
            marker = " ← BOTTLENECK! ⚠️"
        elif util > 70:
            marker = " ← High utilization"
        elif util < 20:
            marker = " ← Excess capacity"
        
        print(f"  {i+1}. {device_id:25s} {util:6.1f}% (capacity={capacity}){marker}")
    
    # Find the bottleneck
    if sorted_devices:
        bottleneck_device, bottleneck_util = sorted_devices[0]
        bottleneck_capacity = next((d['capacity'] for d in config['devices'] if d['id'] == bottleneck_device), None)
        
        print("\n" + "="*70)
        print("🎯 YOUR BOTTLENECK:")
        print("="*70)
        print(f"\nDevice: {bottleneck_device}")
        print(f"Current Capacity: {bottleneck_capacity}")
        print(f"Utilization: {bottleneck_util:.1f}%")
        
        print("\n" + "="*70)
        print("📋 TESTING INSTRUCTIONS FOR REACT UI:")
        print("="*70)
        print(f"\n1. In React UI, find device: '{bottleneck_device}'")
        print(f"2. Current capacity: {bottleneck_capacity}")
        print(f"3. Change it to: {bottleneck_capacity * 2} (double it)")
        print(f"4. Run simulation")
        print(f"5. You SHOULD see improvement from {completion_time/60:.1f} minutes")
        print(f"\n6. Then change a DIFFERENT device (like one with <20% utilization)")
        print(f"7. You should see NO improvement (proves it's not the bottleneck)")
        
else:
    print("\n⚠️  No state history available")
    print("Looking at flow completion to estimate bottleneck...")
    
    # Fallback: analyze which device appears most in flows
    device_usage = {}
    for flow in config['flows']:
        from_dev = flow.get('from_device')
        to_dev = flow.get('to_device')
        if from_dev:
            device_usage[from_dev] = device_usage.get(from_dev, 0) + 1
        if to_dev and to_dev != from_dev:
            device_usage[to_dev] = device_usage.get(to_dev, 0) + 1
    
    sorted_usage = sorted(device_usage.items(), key=lambda x: x[1], reverse=True)
    
    print("\nDevices by flow count (rough estimate):")
    for device_id, count in sorted_usage[:5]:
        capacity = next((d['capacity'] for d in config['devices'] if d['id'] == device_id), '?')
        print(f"  {device_id:25s} {count} flows, capacity={capacity}")

print("\n" + "="*70)
