"""
MULTI-BATCH CONFIGURATION GENERATOR
Converts single-flow template into multi-batch production scenario
"""
import requests
import json
import copy

def generate_multi_batch_config(num_batches=5, batch_interval_seconds=600):
    """
    Generate multi-batch configuration from platelet-pooling template.
    
    Args:
        num_batches: Number of batches to simulate
        batch_interval_seconds: Time between batch arrivals (stagger starts)
    """
    print("="*70)
    print("MULTI-BATCH CONFIGURATION GENERATOR")
    print("="*70)
    
    # Get base template
    response = requests.get("http://localhost:8000/templates/platelet-pooling")
    base_config = response.json()
    
    print(f"\nBase template:")
    print(f"  Devices: {len(base_config['devices'])}")
    print(f"  Flows: {len(base_config['flows'])}")
    
    # Create new config with same devices
    multi_batch_config = {
        "simulation": base_config["simulation"],
        "devices": base_config["devices"],
        "flows": [],
        "gates": base_config.get("gates", {}),
        "output_options": base_config.get("output_options", {})
    }
    
    # Analyze flow dependencies to understand the sequence
    base_flows = base_config['flows']
    
    print(f"\nOriginal flow sequence:")
    for i, flow in enumerate(base_flows, 1):
        deps = flow.get('dependencies') or []
        deps_str = f" (depends on: {', '.join(deps)})" if deps else " (starts immediately)"
        print(f"  {i}. {flow['flow_id']}: {flow['from_device']} → {flow['to_device']}{deps_str}")
    
    # Generate flows for each batch
    print(f"\nGenerating {num_batches} batches...")
    
    all_batch_flows = []
    for batch_num in range(1, num_batches + 1):
        batch_id = f"batch_{batch_num:03d}"
        batch_start_time = (batch_num - 1) * batch_interval_seconds
        
        print(f"\n  Batch {batch_num} (ID: {batch_id}, starts at T={batch_start_time}s):")
        
        # Create mapping from old flow IDs to new flow IDs for this batch
        flow_id_mapping = {}
        
        for flow_idx, base_flow in enumerate(base_flows):
            # Create new flow ID for this batch
            new_flow_id = f"{batch_id}_flow_{flow_idx + 1:02d}"
            old_flow_id = base_flow['flow_id']
            flow_id_mapping[old_flow_id] = new_flow_id
            
            # Copy flow and update IDs
            new_flow = copy.deepcopy(base_flow)
            new_flow['flow_id'] = new_flow_id
            new_flow['batch_id'] = batch_id
            
            # Update dependencies to reference flows within same batch
            if base_flow.get('dependencies'):
                new_flow['dependencies'] = [
                    flow_id_mapping.get(dep_id, dep_id)
                    for dep_id in base_flow['dependencies']
                ]
            
            # For the first flow in each batch, add a delay to stagger arrivals
            # (simulate batches arriving at different times)
            if not base_flow.get('dependencies'):
                # This is a starting flow - add arrival delay
                new_flow['arrival_time'] = batch_start_time
            
            all_batch_flows.append(new_flow)
            print(f"    • {new_flow_id}")
    
    multi_batch_config['flows'] = all_batch_flows
    
    print(f"\n{'='*70}")
    print(f"GENERATED CONFIGURATION:")
    print(f"{'='*70}")
    print(f"  Total flows: {len(all_batch_flows)} ({num_batches} batches × {len(base_flows)} steps)")
    print(f"  Batch stagger: {batch_interval_seconds}s ({batch_interval_seconds/60:.1f} min)")
    print(f"  Expected behavior: Multiple batches compete for device capacity")
    
    return multi_batch_config


def test_multi_batch_config(config):
    """
    Test the multi-batch configuration and show capacity impacts.
    """
    print(f"\n{'='*70}")
    print("TESTING MULTI-BATCH CONFIGURATION")
    print(f"{'='*70}")
    
    # Test 1: Baseline
    print(f"\nTEST 1: BASELINE (original capacities)")
    print("-"*70)
    
    response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    result1 = response.json()
    
    if 'error' in result1:
        print(f"❌ Simulation Error: {result1['error']}")
        return
    
    time1 = result1['results']['summary']['simulation_time_seconds']
    flows1 = result1['results']['summary']['total_flows_completed']
    
    print(f"  Completion Time: {time1:.1f}s ({time1/60:.1f} min)")
    print(f"  Flows Completed: {flows1}")
    
    # Test 2: Double capacity on a capacity=1 device
    print(f"\nTEST 2: DOUBLE platelet_separator capacity (1→2)")
    print("-"*70)
    
    test2_config = copy.deepcopy(config)
    for device in test2_config['devices']:
        if device['id'] == 'platelet_separator':
            device['capacity'] = 2
            print(f"  Changed: {device['id']} capacity 1 → 2")
    
    response = requests.post("http://localhost:8000/simulations/run", json={"config": test2_config})
    result2 = response.json()
    
    if 'error' in result2:
        print(f"❌ Simulation Error: {result2['error']}")
        return
    
    time2 = result2['results']['summary']['simulation_time_seconds']
    flows2 = result2['results']['summary']['total_flows_completed']
    
    print(f"  Completion Time: {time2:.1f}s ({time2/60:.1f} min)")
    print(f"  Flows Completed: {flows2}")
    
    improvement = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
    time_saved = time1 - time2
    
    print(f"\n  → Time saved: {time_saved:.1f}s ({time_saved/60:.1f} min)")
    print(f"  → Improvement: {improvement:.1f}%")
    
    if abs(improvement) > 1:
        print(f"  → ✅ SUCCESS! Capacity change has measurable impact!")
    else:
        print(f"  → ⚠️  No significant improvement detected")
    
    # Test 3: Double capacity on a high-capacity device (should see less/no impact)
    print(f"\nTEST 3: DOUBLE pooling_station capacity (3→6)")
    print("-"*70)
    
    test3_config = copy.deepcopy(config)
    for device in test3_config['devices']:
        if device['id'] == 'pooling_station':
            old_cap = device['capacity']
            device['capacity'] = 6
            print(f"  Changed: {device['id']} capacity {old_cap} → 6")
    
    response = requests.post("http://localhost:8000/simulations/run", json={"config": test3_config})
    result3 = response.json()
    
    if 'error' in result3:
        print(f"❌ Simulation Error: {result3['error']}")
        return
    
    time3 = result3['results']['summary']['simulation_time_seconds']
    flows3 = result3['results']['summary']['total_flows_completed']
    
    print(f"  Completion Time: {time3:.1f}s ({time3/60:.1f} min)")
    print(f"  Flows Completed: {flows3}")
    
    improvement3 = ((time1 - time3) / time1 * 100) if time1 > 0 else 0
    time_saved3 = time1 - time3
    
    print(f"\n  → Time saved: {time_saved3:.1f}s ({time_saved3/60:.1f} min)")
    print(f"  → Improvement: {improvement3:.1f}%")
    
    if abs(improvement3) < 1:
        print(f"  → ✅ Correct! Non-bottleneck device shows minimal impact")
    else:
        print(f"  → ⚠️  Unexpected improvement from high-capacity device")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n{'Scenario':<40} {'Time (min)':<15} {'Improvement':<15}")
    print("-"*70)
    print(f"{'Baseline (original)':<40} {time1/60:>10.1f} min   {0:>10.1f}%")
    print(f"{'platelet_separator 1→2':<40} {time2/60:>10.1f} min   {improvement:>10.1f}%")
    print(f"{'pooling_station 3→6':<40} {time3/60:>10.1f} min   {improvement3:>10.1f}%")
    
    print(f"\n{'='*70}")
    if abs(improvement) > 1:
        print("✅ MULTI-BATCH CONFIG WORKS!")
        print("   Capacity changes now show measurable impact on throughput!")
        print("   Bottleneck devices matter because batches compete for resources!")
    else:
        print("⚠️  Still seeing identical times - may need adjustment:")
        print("   • Check if arrival_time is supported by engine")
        print("   • Verify flows are independent enough to run in parallel")
        print("   • Consider increasing batch count or reducing interval")
    print(f"{'='*70}")


if __name__ == "__main__":
    # Generate configuration
    config = generate_multi_batch_config(
        num_batches=5,
        batch_interval_seconds=600  # 10 minutes between batches
    )
    
    # Save to file
    output_file = "multi_batch_config.json"
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {output_file}")
    
    # Test it
    test_multi_batch_config(config)
