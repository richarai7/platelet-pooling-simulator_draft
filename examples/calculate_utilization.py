"""
COMPREHENSIVE UTILIZATION CALCULATOR
Calculates staff/device utilization from event history
"""
import requests
import json
from collections import defaultdict

def calculate_utilization_from_events(result, config):
    """Calculate utilization by analyzing event history."""
    
    if 'events' not in result['results']:
        print("⚠️  No event history available. Enable output_options.include_events")
        return None
    
    events = result['results']['events']
    total_sim_time = result['results']['summary']['simulation_time_seconds']
    
    # Track device busy times
    device_busy_time = defaultdict(float)
    device_start_times = {}  # Track when device started being busy
    
    # Get device capacities
    device_capacity = {d['id']: d['capacity'] for d in config['devices']}
    
    # Process events chronologically
    for event in sorted(events, key=lambda e: e['timestamp']):
        device_id = event.get('device_id')
        event_type = event['event_type']
        timestamp = event['timestamp']
        
        if not device_id:
            continue
        
        # Track processing start/end
        if event_type == 'flow_start':
            # Device becomes busy
            if device_id not in device_start_times:
                device_start_times[device_id] = timestamp
        
        elif event_type == 'flow_complete':
            # Device finishes work
            if device_id in device_start_times:
                start_time = device_start_times[device_id]
                busy_duration = timestamp - start_time
                device_busy_time[device_id] += busy_duration
                del device_start_times[device_id]
    
    # Calculate utilization percentages
    utilization = {}
    for device_id, busy_time in device_busy_time.items():
        capacity = device_capacity.get(device_id, 1)
        available_time = total_sim_time * capacity
        util_pct = (busy_time / available_time * 100) if available_time > 0 else 0
        utilization[device_id] = min(100.0, util_pct)
    
    # Add devices with zero utilization
    for device_id in device_capacity:
        if device_id not in utilization:
            utilization[device_id] = 0.0
    
    return utilization


print("="*70)
print("COMPREHENSIVE UTILIZATION ANALYSIS")
print("="*70)

# Get multi-batch template
print("\nStep 1: Loading multi-batch configuration...")
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch?batches=5&interval=600")
config = response.json()

# Enable event tracking
config['output_options'] = {
    'include_events': True,
    'include_history': True
}

print(f"✓ {len(config['flows'])} flows, {len(config['devices'])} devices")

# Run simulation
print("\nStep 2: Running simulation with event tracking...")
response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
result = response.json()

sim_time = result['results']['summary']['simulation_time_seconds']
print(f"✓ Complete: {sim_time:.1f}s ({sim_time/60:.1f} min)")

# Calculate utilization
print("\nStep 3: Analyzing utilization from event history...")
utilization = calculate_utilization_from_events(result, config)

if utilization:
    print("\n" + "="*70)
    print("DEVICE UTILIZATION REPORT")
    print("="*70)
    
    # Sort by utilization (highest first)
    sorted_util = sorted(utilization.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Device':<30} {'Capacity':<10} {'Utilization':<15} {'Status'}")
    print("-"*70)
    
    for device_id, util_pct in sorted_util:
        capacity = next((d['capacity'] for d in config['devices'] if d['id'] == device_id), 1)
        
        # Status indicator
        if util_pct > 85:
            status = "🔴 BOTTLENECK"
        elif util_pct > 70:
            status = "🟡 High Load"
        elif util_pct > 40:
            status = "🟢 Balanced"
        elif util_pct > 10:
            status = "⚪ Light Load"
        else:
            status = "⭕ Idle"
        
        print(f"{device_id:<30} {capacity:<10} {util_pct:>10.1f}%   {status}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("UTILIZATION SUMMARY")
    print("="*70)
    
    avg_util = sum(utilization.values()) / len(utilization)
    bottlenecks = [d for d, u in utilization.items() if u > 85]
    underutilized = [d for d, u in utilization.items() if u < 30]
    
    print(f"\n📊 Average Utilization: {avg_util:.1f}%")
    print(f"\n🔴 Bottlenecks (>85% util): {len(bottlenecks)}")
    if bottlenecks:
        for device in bottlenecks:
            print(f"   • {device}: {utilization[device]:.1f}%")
    
    print(f"\n⚪ Underutilized (<30% util): {len(underutilized)}")
    if underutilized:
        for device in underutilized:
            print(f"   • {device}: {utilization[device]:.1f}%")
    
    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    
    if bottlenecks:
        print("\n🔴 Address Bottlenecks:")
        for device in bottlenecks:
            capacity = next((d['capacity'] for d in config['devices'] if d['id'] == device_id), 1)
            print(f"   • {device}: Increase capacity from {capacity} → {capacity + 1}")
            print(f"     Expected impact: ~{utilization[device]/2:.1f}% utilization")
    
    if underutilized:
        print("\n⚪ Optimize Underutilized Resources:")
        for device in underutilized:
            print(f"   • {device}: Consider reducing capacity or consolidating")
    
    if not bottlenecks and not underutilized:
        print("\n✅ System is well-balanced!")
        print("   All devices operating in optimal 30-85% range")

print("\n" + "="*70)
print("HOW TO USE UTILIZATION DATA")
print("="*70)

print("""
STAFF SCHEDULING:
  • High utilization (>80%) → Need more staff/shifts
  • Low utilization (<30%) → Can reduce staff or combine roles
  
EQUIPMENT INVESTMENT:
  • Bottleneck devices → Prioritize capacity additions
  • Calculate ROI: cost of equipment vs. throughput gain
  
PROCESS OPTIMIZATION:
  • Balance workload across devices
  • Consider parallel processing for bottlenecks
  • Reduce idle time on underutilized resources

TESTING SCENARIOS:
  1. Baseline: Current configuration
  2. Test: Add capacity to bottleneck device
  3. Measure: Utilization drop and throughput increase
  4. Decide: Cost vs. benefit analysis
""")

print("="*70)
