#!/usr/bin/env python3
"""Test simulation request as sent from UI"""

import requests
import json

# Get the template
print("Fetching template...")
response = requests.get("http://localhost:8000/templates/platelet-pooling-multi-batch")
template = response.json()

print(f"Template has {len(template['devices'])} devices")
print(f"Template has {len(template['flows'])} flows")
print(f"Template has output_options: {template.get('output_options')}")

# Send simulation request exactly as UI would
print("\nSending simulation request...")
payload = {
    "config": template,
    "run_name": "Test Run",
    "simulation_name": "Default Simulation",
    "export_to_json": True
}

response = requests.post(
    "http://localhost:8000/simulations/run",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"Response status: {response.status_code}")

if response.status_code == 200:
    results = response.json()
    print("\nSuccess!")
    print(f"Results keys: {results.keys()}")
    if 'results' in results:
        print(f"Results.results keys: {results['results'].keys()}")
        if 'summary' in results['results']:
            print(f"Summary: {results['results']['summary']}")
else:
    print(f"\nError: {response.text[:500]}")
