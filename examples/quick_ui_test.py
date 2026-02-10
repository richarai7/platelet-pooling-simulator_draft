"""
QUICK TEST - Run multi-batch in UI via API endpoint
"""
import requests
import json

print("="*70)
print("QUICK MULTI-BATCH TEST")
print("="*70)

# Fetch multi-batch template from API
print("\n1. Fetching multi-batch template from API endpoint...")
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch")
config = response.json()

print(f"   ✅ Template loaded!")
print(f"   • Total flows: {len(config['flows'])}")
print(f"   • Total devices: {len(config['devices'])}")

# Run baseline
print("\n2. Running BASELINE simulation...")
response = requests.post("http://localhost:8000/simulations/run", json={"config": config})
result = response.json()

time_min = result['results']['summary']['simulation_time_seconds'] / 60
flows = result['results']['summary']['total_flows_completed']

print(f"   ✅ Baseline complete!")
print(f"   • Time: {time_min:.1f} minutes")
print(f"   • Flows completed: {flows:,}")

# Test capacity change
print("\n3. Testing platelet_separator capacity 1→2...")
test_config = json.loads(json.dumps(config))  # Deep copy
for device in test_config['devices']:
    if device['id'] == 'platelet_separator':
        device['capacity'] = 2

response = requests.post("http://localhost:8000/simulations/run", json={"config": test_config})
result2 = response.json()

time2_min = result2['results']['summary']['simulation_time_seconds'] / 60
improvement = ((result['results']['summary']['simulation_time_seconds'] - result2['results']['summary']['simulation_time_seconds']) 
               / result['results']['summary']['simulation_time_seconds'] * 100)

print(f"   ✅ Test complete!")
print(f"   • Time: {time2_min:.1f} minutes")
print(f"   • Improvement: {improvement:.1f}%")

print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)
print(f"\n{'Scenario':<40} {'Time':<20} {'Improvement'}")
print("-"*70)
print(f"{'Baseline (original capacities)':<40} {time_min:>10.1f} min   {0:>10.1f}%")
print(f"{'platelet_separator 1→2':<40} {time2_min:>10.1f} min   {improvement:>10.1f}%")

if improvement > 1:
    print(f"\n✅ SUCCESS! Multi-batch config shows {improvement:.1f}% improvement!")
    print("   This configuration is ready to use in your React UI!")
else:
    print(f"\n⚠️  No improvement detected")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("\nYour React UI can now use:")
print("  GET http://localhost:8000/templates/platelet-pooling-multi-batch")
print("\nOr load the file directly:")
print("  multi_batch_config.json")
print("\nSee HOW_TO_RUN_IN_UI.md for detailed instructions!")
print("="*70)
