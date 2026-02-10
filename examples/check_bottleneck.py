"""
Quick Bottleneck Checker - Shows which device is limiting throughput
Run this to see utilization of all devices in your simulation
"""
import requests
import json

# Get the template
response = requests.get("http://localhost:8000/templates/platelet-pooling")
config = response.json()

# Run simulation with default config
print("="*70)
print("RUNNING BASELINE SIMULATION...")
print("="*70)

response = requests.post(
    "http://localhost:8000/simulations/run",
    json={"config": config}
)
result = response.json()

print("\nBASIC RESULTS:")
print(f"  Simulation Time: {result['results']['simulation_time_seconds']:.1f} seconds")
print(f"  Flows Completed: {result['results']['total_flows_completed']}")
print(f"  Total Events: {result['results']['total_events']}")

# Check state history for utilization
if 'state_history' in result['results']:
    state_history = result['results']['state_history']
    
    print("\n" + "="*70)
    print("DEVICE UTILIZATION:")
    print("="*70)
    
    # Calculate utilization for each device
    device_times = {}
    
    for device_id, events in state_history.items():
        if not events:
            continue
            
        total_time = 0
        processing_time = 0
        last_time = 0
        last_state = 'idle'
        
        for event in events:
            time = event['timestamp']
            state = event['state']
            
            if last_state == 'processing':
                processing_time += (time - last_time)
            
            total_time = time
            last_time = time
            last_state = state
        
        if total_time > 0:
            utilization = (processing_time / total_time) * 100
            device_times[device_id] = utilization
    
    # Sort by utilization (highest first)
    sorted_devices = sorted(device_times.items(), key=lambda x: x[1], reverse=True)
    
    for device_id, utilization in sorted_devices:
        marker = " ← BOTTLENECK!" if utilization > 90 else ""
        print(f"  {device_id:25s}: {utilization:6.2f}%{marker}")
    
    print("\n" + "="*70)
    print("INTERPRETATION:")
    print("="*70)
    print("• Device with highest utilization (>90%) is likely the bottleneck")
    print("• Devices with low utilization (<30%) have excess capacity")
    print("• Focus optimization on high-utilization devices")

else:
    print("\n⚠️  State history not available - check output_options in config")

print("\n" + "="*70)
print("TO TEST CAPACITY CHANGES:")
print("="*70)
print("1. Identify the bottleneck device above")
print("2. In React UI, increase that device's capacity")
print("3. Run simulation again")
print("4. Compare completion time - you should see improvement!")
