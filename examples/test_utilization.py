"""
STAFF/DEVICE UTILIZATION TEST
Shows how to measure and track utilization metrics
"""
import requests
import json

print("="*70)
print("STAFF/DEVICE UTILIZATION TESTING")
print("="*70)

# Get multi-batch template (need multiple batches for realistic utilization)
print("\nLoading multi-batch template...")
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch")
config = response.json()

# Enable detailed output options to get state history
config['output_options'] = {
    'include_events': True,
    'include_history': True,
    'include_state_history': True  # Critical for utilization calculation
}

print(f"✓ Loaded {len(config['flows'])} flows across {len(config['devices'])} devices")

# Run simulation
print("\nRunning simulation with state tracking...")
response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
result = response.json()

print(f"✓ Simulation complete: {result['results']['summary']['simulation_time_seconds']/60:.1f} min")

# Extract utilization metrics
print("\n" + "="*70)
print("DEVICE UTILIZATION ANALYSIS")
print("="*70)

# Check if we have KPI data
if 'kpis' in result['results']:
    kpis = result['results']['kpis']
    
    # Staff utilization (if available)
    if 'staff_utilization' in kpis:
        print(f"\n📊 Overall Staff Utilization: {kpis['staff_utilization']:.1f}%")
    
    # Per-device utilization
    if 'capacity_utilization_per_device' in kpis:
        print("\n📍 Device-by-Device Utilization:")
        print("-"*70)
        
        util_data = kpis['capacity_utilization_per_device']
        
        # Sort by utilization (highest first)
        sorted_devices = sorted(util_data.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{'Device ID':<30} {'Utilization':<15} {'Status'}")
        print("-"*70)
        
        for device_id, utilization in sorted_devices:
            # Get device capacity for context
            capacity = next((d['capacity'] for d in config['devices'] if d['id'] == device_id), 1)
            
            # Determine status
            if utilization > 80:
                status = "🔴 BOTTLENECK"
            elif utilization > 60:
                status = "🟡 High Load"
            elif utilization > 30:
                status = "🟢 Balanced"
            else:
                status = "⚪ Underutilized"
            
            print(f"{device_id:<30} {utilization:>10.1f}%   {status} (cap={capacity})")
    
    # Idle time
    if 'idle_time_percentage' in kpis:
        print(f"\n⏸️  Average Idle Time: {kpis['idle_time_percentage']:.1f}%")

# Manual calculation from device states (if state_history available)
if 'device_states' in result['results']:
    print("\n" + "="*70)
    print("DETAILED DEVICE STATE SNAPSHOT")
    print("="*70)
    
    device_states = result['results']['device_states']
    total_sim_time = result['results']['summary']['simulation_time_seconds']
    
    print(f"\nSimulation Duration: {total_sim_time:.1f} seconds ({total_sim_time/60:.1f} min)")
    print("\nFinal Device States:")
    print("-"*70)
    
    # Handle both list and dict formats
    if isinstance(device_states, list):
        for state in device_states:
            device_id = state.get('device_id', 'Unknown')
            current_state = state.get('final_state', state.get('state', 'Unknown'))
            in_use = state.get('in_use', 0)
            capacity = state.get('capacity', 1)
            
            print(f"\n{device_id}:")
            print(f"  Final State: {current_state}")
            print(f"  Capacity: {capacity}")
            print(f"  In Use at End: {in_use}/{capacity}")
    elif isinstance(device_states, dict):
        for device_id, state in device_states.items():
            current_state = state.get('state', 'Unknown')
            in_use = state.get('in_use', 0)
            capacity = state.get('capacity', 1)
            
            print(f"\n{device_id}:")
            print(f"  Final State: {current_state}")
            print(f"  Capacity: {capacity}")
            print(f"  In Use at End: {in_use}/{capacity}")

print("\n" + "="*70)
print("UTILIZATION INSIGHTS")
print("="*70)

print("""
WHAT IS UTILIZATION?
  • Percentage of time a device/staff is actively working
  • Formula: (Busy Time ÷ Total Available Time) × 100%
  • 100% = Always busy (potential bottleneck)
  • 0% = Never used (waste of resources)

OPTIMAL RANGES:
  • 70-85%: Ideal (balanced load, some buffer)
  • 85-95%: High (near capacity, minimal buffer)
  • >95%: Bottleneck (causing delays)
  • <50%: Underutilized (potential for consolidation)

HOW TO TEST UTILIZATION:

1. ENABLE STATE TRACKING:
   config['output_options'] = {
       'include_state_history': True
   }

2. RUN MULTI-BATCH SIMULATION:
   • Single batch = no competition = low utilization
   • 5+ batches = realistic workload = accurate utilization

3. CHECK KPIs:
   result['results']['kpis']['capacity_utilization_per_device']
   result['results']['kpis']['staff_utilization']

4. IDENTIFY BOTTLENECKS:
   • >80% utilization = bottleneck candidate
   • Add capacity to high-utilization devices
   • Re-run to see improvement

USE CASES:
  ✓ Staff scheduling (do we need 3 operators or 5?)
  ✓ Equipment investment (which machines are overloaded?)
  ✓ Shift planning (can we run 2 shifts or need 3?)
  ✓ Cost optimization (eliminate underutilized resources)
  ✓ Bottleneck identification (where are the delays?)
""")

print("="*70)
print("NEXT STEPS TO TEST UTILIZATION:")
print("="*70)

print("""
1. Run baseline with multi-batch config
2. Note devices with >80% utilization
3. Increase capacity of high-utilization devices
4. Re-run and compare utilization drop
5. Calculate cost vs. benefit

Example Test:
  • platelet_separator shows 95% utilization → BOTTLENECK
  • Add second unit (capacity 1 → 2)
  • Re-run: utilization drops to 47.5% → BALANCED
  • Result: 23% faster throughput, reduced queues
""")

print("="*70)
