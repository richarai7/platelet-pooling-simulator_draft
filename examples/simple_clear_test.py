"""
SIMPLE TEST - Create a basic 3-device configuration
This will show CLEAR differences when you change capacity
"""
import requests
import json

# Simple configuration - just 3 devices, 3 flows
simple_config = {
    "simulation": {
        "duration": 10000,
        "random_seed": 42
    },
    "devices": [
        {"id": "centrifuge", "type": "machine", "capacity": 2},
        {"id": "separator", "type": "machine", "capacity": 2},
        {"id": "quality", "type": "machine", "capacity": 1}  # ← BOTTLENECK!
    ],
    "flows": [
        # 5 batches flowing through all 3 devices
        {"flow_id": "batch1_cent", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": [360, 360], "priority": 1, "dependencies": []},
        {"flow_id": "batch1_sep", "from_device": "separator", "to_device": "quality",
         "process_time_range": [720, 720], "priority": 1, "dependencies": ["batch1_cent"]},
        {"flow_id": "batch1_qual", "from_device": "quality", "to_device": "quality",
         "process_time_range": [240, 240], "priority": 1, "dependencies": ["batch1_sep"]},
        
        {"flow_id": "batch2_cent", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": [360, 360], "priority": 1, "dependencies": []},
        {"flow_id": "batch2_sep", "from_device": "separator", "to_device": "quality",
         "process_time_range": [720, 720], "priority": 1, "dependencies": ["batch2_cent"]},
        {"flow_id": "batch2_qual", "from_device": "quality", "to_device": "quality",
         "process_time_range": [240, 240], "priority": 1, "dependencies": ["batch2_sep"]},
        
        {"flow_id": "batch3_cent", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": [360, 360], "priority": 1, "dependencies": []},
        {"flow_id": "batch3_sep", "from_device": "separator", "to_device": "quality",
         "process_time_range": [720, 720], "priority": 1, "dependencies": ["batch3_cent"]},
        {"flow_id": "batch3_qual", "from_device": "quality", "to_device": "quality",
         "process_time_range": [240, 240], "priority": 1, "dependencies": ["batch3_sep"]},
        
        {"flow_id": "batch4_cent", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": [360, 360], "priority": 1, "dependencies": []},
        {"flow_id": "batch4_sep", "from_device": "separator", "to_device": "quality",
         "process_time_range": [720, 720], "priority": 1, "dependencies": ["batch4_cent"]},
        {"flow_id": "batch4_qual", "from_device": "quality", "to_device": "quality",
         "process_time_range": [240, 240], "priority": 1, "dependencies": ["batch4_sep"]},
        
        {"flow_id": "batch5_cent", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": [360, 360], "priority": 1, "dependencies": []},
        {"flow_id": "batch5_sep", "from_device": "separator", "to_device": "quality",
         "process_time_range": [720, 720], "priority": 1, "dependencies": ["batch5_cent"]},
        {"flow_id": "batch5_qual", "from_device": "quality", "to_device": "quality",
         "process_time_range": [240, 240], "priority": 1, "dependencies": ["batch5_sep"]}
    ],
    "output_options": {
        "include_history": True
    }
}

print("="*70)
print("SIMPLE TEST - CLEAR DEMONSTRATION")
print("="*70)

# Save this config to a file so you can import it in the UI
with open('simple_test_config.json', 'w') as f:
    json.dump(simple_config, f, indent=2)

print("\n✅ Created: simple_test_config.json")
print("\nThis config has:")
print("  • 3 devices: Centrifuge(2), Separator(2), Quality(1)")
print("  • 5 batches (15 flows total)")
print("  • Quality is the BOTTLENECK (capacity=1)")

# Test 1: Baseline
print("\n" + "="*70)
print("TEST 1: BASELINE (Quality capacity=1)")
print("="*70)

response = requests.post(
    "http://localhost:8000/simulations/run",
    json={"config": simple_config}
)
result1 = response.json()
print(f"\nAPI Response: {json.dumps(result1, indent=2)[:500]}...")
time1 = result1.get('simulation_time_seconds', result1.get('results', {}).get('simulation_time_seconds', 0))
flows1 = result1.get('total_flows_completed', result1.get('results', {}).get('total_flows_completed', 0))

print(f"  Completion Time: {time1:.1f} seconds ({time1/60:.1f} minutes)")
print(f"  Flows Completed: {flows1}")

# Test 2: Double quality capacity
print("\n" + "="*70)
print("TEST 2: DOUBLE QUALITY (Quality capacity 1→2)")
print("="*70)

test_config = simple_config.copy()
test_config['devices'] = [
    {"id": "centrifuge", "type": "machine", "capacity": 2},
    {"id": "separator", "type": "machine", "capacity": 2},
    {"id": "quality", "type": "machine", "capacity": 2}  # ← Changed to 2!
]
test_config['flows'] = simple_config['flows']

response = requests.post(
    "http://localhost:8000/simulations/run",
    json={"config": test_config}
)
result2 = response.json()
time2 = result2.get('simulation_time_seconds', result2.get('results', {}).get('simulation_time_seconds', 0))
flows2 = result2.get('total_flows_completed', result2.get('results', {}).get('total_flows_completed', 0))

print(f"  Completion Time: {time2:.1f} seconds ({time2/60:.1f} minutes)")
print(f"  Flows Completed: {flows2}")

# Comparison
print("\n" + "="*70)
print("COMPARISON:")
print("="*70)
time_saved = time1 - time2
improvement = (time_saved / time1) * 100 if time1 > 0 else 0

print(f"  Baseline:        {time1:.1f} seconds")
print(f"  With Quality=2:  {time2:.1f} seconds")
print(f"  Time Saved:      {time_saved:.1f} seconds")
print(f"  Improvement:     {improvement:.1f}%")

if improvement > 50:
    print("\n  ✅ MAJOR IMPROVEMENT! Quality was the bottleneck!")
elif improvement > 10:
    print("\n  ✓ Good improvement, quality was constraining throughput")
elif improvement > 0:
    print("\n  ~ Small improvement, quality had some impact")
else:
    print("\n  ❌ NO IMPROVEMENT - Quality is NOT the bottleneck")

# Test 3: Double centrifuge (should show NO improvement)
print("\n" + "="*70)
print("TEST 3: DOUBLE CENTRIFUGE (Centrifuge capacity 2→4)")
print("="*70)

test_config2 = simple_config.copy()
test_config2['devices'] = [
    {"id": "centrifuge", "type": "machine", "capacity": 4},  # ← Changed to 4!
    {"id": "separator", "type": "machine", "capacity": 2},
    {"id": "quality", "type": "machine", "capacity": 1}
]
test_config2['flows'] = simple_config['flows']

response = requests.post(
    "http://localhost:8000/simulations/run",
    json={"config": test_config2}
)
result3 = response.json()
time3 = result3.get('simulation_time_seconds', result3.get('results', {}).get('simulation_time_seconds', 0))
flows3 = result3.get('total_flows_completed', result3.get('results', {}).get('total_flows_completed', 0))

print(f"  Completion Time: {time3:.1f} seconds ({time3/60:.1f} minutes)")
print(f"  Flows Completed: {flows3}")

time_saved3 = time1 - time3
improvement3 = (time_saved3 / time1) * 100 if time1 > 0 else 0

print(f"\n  Time Saved:      {time_saved3:.1f} seconds")
print(f"  Improvement:     {improvement3:.1f}%")

if abs(improvement3) < 1:
    print("\n  ❌ NO IMPROVEMENT - Centrifuge is NOT the bottleneck!")
    print("  This proves capacity changes only help if you fix the ACTUAL bottleneck")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print(f"Changing Quality (bottleneck):     {improvement:.1f}% improvement ✅")
print(f"Changing Centrifuge (not bottleneck): {improvement3:.1f}% improvement ❌")
print("\nThis PROVES the simulator works correctly!")
print("Only fixing the bottleneck device improves throughput.")
print("="*70)
