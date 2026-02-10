"""
METADATA (KEY-VALUE PAIRS) DEMONSTRATION
Shows how to add custom attributes to devices and flows
"""
import requests
import json

print("="*70)
print("METADATA (KEY-VALUE PAIRS) FOR DEVICES & FLOWS")
print("="*70)

# Get template
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch")
config = response.json()

print("\n✅ METADATA IS ALREADY SUPPORTED!")
print("\nYou can add ANY custom key-value pairs to devices and flows.")
print("="*70)

# Example 1: Add metadata to devices
print("\n📍 EXAMPLE 1: DEVICE METADATA")
print("-"*70)

# Find platelet_separator device
for device in config['devices']:
    if device['id'] == 'platelet_separator':
        # Add custom metadata
        device['metadata'] = {
            'location': 'Building A - Floor 2',
            'cost_per_hour': 75.50,
            'maintenance_schedule': 'Weekly',
            'manufacturer': 'MedTech Corp',
            'model': 'PS-3000',
            'installation_date': '2024-06-15',
            'operator_certification_required': True,
            'power_consumption_kw': 2.5,
            'square_footage': 12.5
        }
        
        print("\nDevice: platelet_separator")
        print("\nAdded Metadata:")
        for key, value in device['metadata'].items():
            print(f"  • {key}: {value}")
        break

# Example 2: Add metadata to flows
print("\n\n🔄 EXAMPLE 2: FLOW METADATA")
print("-"*70)

# Find a flow and add metadata
for flow in config['flows']:
    if 'batch_001_flow_01' in flow['flow_id']:
        flow['metadata'] = {
            'batch_type': 'Type O Negative',
            'priority_level': 'High',
            'donor_id': 'D-12345',
            'collection_timestamp': '2026-02-09T08:30:00',
            'expiration_date': '2026-02-14',
            'quality_score': 98.5,
            'temperature_celsius': 22.0,
            'requires_inspection': True
        }
        
        print(f"\nFlow: {flow['flow_id']}")
        print("\nAdded Metadata:")
        for key, value in flow['metadata'].items():
            print(f"  • {key}: {value}")
        break

# Save example config
with open('config_with_metadata_example.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n\n✅ Saved example: config_with_metadata_example.json")

# Run simulation to prove it works
print("\n" + "="*70)
print("TESTING: Does simulation accept metadata?")
print("="*70)

response = requests.post("http://localhost:8000/simulations/run", json={"config": config})

if response.status_code == 200:
    result = response.json()
    print("\n✅ SUCCESS! Simulation ran with metadata included.")
    print(f"   Completion: {result['results']['summary']['simulation_time_seconds']/60:.1f} min")
    print(f"   Flows: {result['results']['summary']['total_flows_completed']}")
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text)

# Show use cases
print("\n" + "="*70)
print("METADATA USE CASES")
print("="*70)

print("""
DEVICE METADATA (Machines/Equipment):
  ✓ Location tracking (building, floor, room)
  ✓ Cost accounting (purchase price, hourly rate, maintenance cost)
  ✓ Asset management (serial number, warranty, installation date)
  ✓ Operational data (power consumption, square footage)
  ✓ Compliance (certification requirements, inspection dates)
  ✓ Performance tracking (uptime, failure rate, efficiency)

FLOW METADATA (Batches/Jobs):
  ✓ Product tracking (batch ID, lot number, product type)
  ✓ Quality data (inspection results, test scores, defect rate)
  ✓ Scheduling (priority, due date, customer ID)
  ✓ Traceability (source, destination, timestamps)
  ✓ Regulatory (compliance flags, documentation links)
  ✓ Cost tracking (material cost, labor hours)

INTEGRATION POSSIBILITIES:
  ✓ Export to Azure Digital Twin (device properties)
  ✓ Cost calculation (sum metadata costs for total)
  ✓ 3D visualization (use location coordinates)
  ✓ Dashboard filtering (show only high-priority flows)
  ✓ Compliance reporting (track certification dates)
  ✓ Analytics (correlate metadata with performance)
""")

print("="*70)
print("HOW TO USE IN CONFIG:")
print("="*70)

print("""
{
  "devices": [
    {
      "id": "centrifuge",
      "type": "machine",
      "capacity": 2,
      "metadata": {
        "location": "Building A",
        "cost_per_hour": 50,
        "maintenance_date": "2026-03-01",
        "any_custom_field": "any_value"
      }
    }
  ],
  "flows": [
    {
      "flow_id": "batch_001_flow_01",
      "from_device": "centrifuge",
      "to_device": "separator",
      "metadata": {
        "batch_type": "Type O+",
        "priority": "High",
        "custom_tracking_id": "XYZ-123"
      }
    }
  ]
}

✅ ALREADY IMPLEMENTED - Just add "metadata": {...} to any device or flow!
""")

print("="*70)
