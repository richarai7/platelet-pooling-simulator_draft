"""
CREATE PROPER MULTI-BATCH CONFIG
This will show capacity actually matters!
"""
import requests
import json

print("="*70)
print("CREATING MULTI-BATCH CONFIGURATION")
print("="*70)

# Get base template
response = requests.get("http://localhost:8000/templates/platelet-pooling")
config = response.json()

# Check if there are gates
print(f"\nGates in template: {config.get('gates', [])}")

# Add arrival gate to generate multiple batches
config['gates'] = [
    {
        "gate_id": "arrival_gate",
        "gate_type": "arrival",
        "arrival_distribution": "fixed",
        "arrival_rate": 600,  # New batch every 10 minutes
        "max_arrivals": 5,    # 5 batches total
        "target_flow": "f1_centrifuge_to_separator"  # First flow in process
    }
]

print("\nAdded arrival gate:")
print(f"  • Type: arrival")
print(f"  • Interval: 600s (10 minutes)")
print(f"  • Total batches: 5")
print(f"  • Target: f1_centrifuge_to_separator")

# Save config
with open('multi_batch_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✅ Saved to: multi_batch_config.json")

# Run baseline
print("\n" + "="*70)
print("TEST 1: BASELINE (5 batches, original capacities)")
print("="*70)

response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
result = response.json()

time1 = result['results']['summary']['simulation_time_seconds']
flows1 = result['results']['summary']['total_flows_completed']

print(f"Completion Time: {time1:.1f}s ({time1/60:.1f} min)")
print(f"Flows Completed: {flows1}")

# Test with doubled capacity on bottleneck
print("\n" + "="*70)
print("TEST 2: DOUBLE platelet_separator capacity (1→2)")
print("="*70)

test2_config = json.loads(json.dumps(config))  # Deep copy
for device in test2_config['devices']:
    if device['id'] == 'platelet_separator':
        device['capacity'] = 2
        print(f"Changed {device['id']}: capacity 1 → 2")

response = requests.post("http://localhost:8000/simulations/run", json={"config": test2_config})
result2 = response.json()

time2 = result2['results']['summary']['simulation_time_seconds']
flows2 = result2['results']['summary']['total_flows_completed']

print(f"Completion Time: {time2:.1f}s ({time2/60:.1f} min)")
print(f"Flows Completed: {flows2}")

improvement = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
print(f"\n→ Time saved: {time1 - time2:.1f}s")
print(f"→ Improvement: {improvement:.1f}%")

if abs(improvement) > 1:
    print(f"→ ✅ CAPACITY MATTERS with multiple batches!")
else:
    print(f"→ Still no improvement - gate config may need adjustment")

print("\n" + "="*70)
print("EXPLANATION:")
print("="*70)
print("\nThe original template had only 1 material unit flowing through.")
print("With only 1 unit, device capacity doesn't matter!")
print("\nWith arrival gates generating 5 batches:")
print("  • Batches compete for device capacity")
print("  • Bottleneck devices create queues")
print("  • Adding capacity reduces wait time")
print("\nThis is how real production works - multiple jobs competing!")
print("="*70)
