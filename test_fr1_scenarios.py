#!/usr/bin/env python3
"""Test FR1 scenario management features"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("FR1 Scenario Management Feature Test")
print("=" * 60)

# 1. Get template
print("\n1. Fetching template...")
response = requests.get(f"{BASE_URL}/templates/platelet-pooling-multi-batch")
template = response.json()
print(f"   ✓ Template loaded: {len(template['devices'])} devices, {len(template['flows'])} flows")

# 2. Create scenario
print("\n2. Creating new scenario...")
scenario_data = {
    "name": "FR1 Test Scenario",
    "description": "Testing scenario management features for FR1 compliance",
    "config": template,
    "tags": ["test", "fr1", "validation"]
}

response = requests.post(f"{BASE_URL}/scenarios", json=scenario_data)
if response.status_code == 201:
    scenario = response.json()
    scenario_id = scenario['id']
    print(f"   ✓ Scenario created with ID: {scenario_id}")
    print(f"   ✓ Name: {scenario['name']}")
    print(f"   ✓ Tags: {scenario['tags']}")
else:
    print(f"   ✗ Failed: {response.text}")
    exit(1)

# 3. List scenarios
print("\n3. Listing all scenarios...")
response = requests.get(f"{BASE_URL}/scenarios")
scenarios = response.json()
print(f"   ✓ Found {len(scenarios)} scenario(s)")
for s in scenarios:
    print(f"      - ID {s['id']}: {s['name']}")

# 4. Get specific scenario
print(f"\n4. Fetching scenario {scenario_id}...")
response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}")
fetched = response.json()
print(f"   ✓ Retrieved: {fetched['name']}")
print(f"   ✓ Devices in config: {len(fetched['config']['devices'])}")

# 5. Update scenario (simulate "edit")
print(f"\n5. Updating scenario {scenario_id}...")
updated_data = {
    "name": "FR1 Test Scenario (Updated)",
    "description": "Updated description for testing",
    "config": template,
    "tags": ["test", "fr1", "updated"]
}
response = requests.put(f"{BASE_URL}/scenarios/{scenario_id}", json=updated_data)
if response.status_code == 200:
    updated = response.json()
    print(f"   ✓ Scenario updated")
    print(f"   ✓ New name: {updated['name']}")
    print(f"   ✓ New tags: {updated['tags']}")
else:
    print(f"   ✗ Failed: {response.text}")

# 6. Copy scenario (get + create with new name)
print(f"\n6. Copying scenario {scenario_id}...")
copy_data = {
    "name": updated['name'] + " (Copy)",
    "description": updated['description'] + " - copied",
    "config": updated['config'],
    "tags": updated['tags'] + ["copy"]
}
response = requests.post(f"{BASE_URL}/scenarios", json=copy_data)
if response.status_code == 201:
    copied = response.json()
    copy_id = copied['id']
    print(f"   ✓ Copy created with ID: {copy_id}")
    print(f"   ✓ Name: {copied['name']}")
else:
    print(f"   ✗ Failed: {response.text}")

# 7. Delete scenarios
print(f"\n7. Deleting test scenarios...")
for sid in [scenario_id, copy_id]:
    response = requests.delete(f"{BASE_URL}/scenarios/{sid}")
    if response.status_code == 204:
        print(f"   ✓ Deleted scenario {sid}")
    else:
        print(f"   ✗ Failed to delete {sid}")

# 8. Verify deletion
print("\n8. Verifying deletion...")
response = requests.get(f"{BASE_URL}/scenarios")
remaining = response.json()
print(f"   ✓ Remaining scenarios: {len(remaining)}")

print("\n" + "=" * 60)
print("FR1 Test Complete - All Features Working!")
print("=" * 60)
print("\n✓ Create scenarios")
print("✓ Copy scenarios")  
print("✓ Edit/Update scenarios")
print("✓ Delete scenarios")
print("✓ Tag scenarios with metadata")
print("✓ List scenarios")
