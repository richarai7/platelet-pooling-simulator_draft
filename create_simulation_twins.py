#!/usr/bin/env python3
"""
Auto-create Digital Twin devices from simulation configuration
This ensures all required twins exist before running simulations
"""

from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
import json
import sys

# Device IDs that need to be created
DEVICE_TWINS = [
    {"twin_id": "centrifuge", "deviceType": "centrifuge", "capacity": 10},
    {"twin_id": "platelet_separator", "deviceType": "separator", "capacity": 10},
    {"twin_id": "pooling_station", "deviceType": "workstation", "capacity": 15},
    {"twin_id": "weigh_register", "deviceType": "machine", "capacity": 10},
    {"twin_id": "sterile_connect", "deviceType": "workstation", "capacity": 10},
    {"twin_id": "test_sample", "deviceType": "machine", "capacity": 10},
    {"twin_id": "quality_check", "deviceType": "quality_station", "capacity": 10},
    {"twin_id": "label_station", "deviceType": "workstation", "capacity": 10},
    {"twin_id": "storage_unit", "deviceType": "storage", "capacity": 50},
    {"twin_id": "final_inspection", "deviceType": "machine", "capacity": 10},
    {"twin_id": "packaging_station", "deviceType": "workstation", "capacity": 10},
]

def create_device_twins(endpoint: str):
    """Create all device twins required for simulation"""
    
    print(f"Connecting to Azure Digital Twins: {endpoint}")
    credential = DefaultAzureCredential()
    client = DigitalTwinsClient(endpoint, credential)
    
    print(f"\nCreating {len(DEVICE_TWINS)} device twins...")
    print("=" * 70)
    
    created = 0
    updated = 0
    errors = 0
    
    for device in DEVICE_TWINS:
        twin_id = device["twin_id"]
        
        try:
            # Check if twin exists
            twin_exists = False
            try:
                client.get_digital_twin(twin_id)
                twin_exists = True
            except:
                twin_exists = False
            
            # Create twin data
            twin_data = {
                "$metadata": {
                    "$model": "dtmi:platelet:Device;1"
                },
                "$dtId": twin_id,
                "deviceId": twin_id,
                "deviceType": device["deviceType"],
                "status": "Idle",
                "capacity": device["capacity"],
                "inUse": 0,
                "utilizationRate": 0.0,
                "queueLength": 0,
                "totalProcessed": 0,
                "totalIdleTime": 0.0,
                "totalProcessingTime": 0.0,
                "totalBlockedTime": 0.0,
                "location": "Simulation Device"
            }
            
            # Create or update twin
            client.upsert_digital_twin(twin_id, twin_data)
            
            if twin_exists:
                print(f"✓ Updated: {twin_id:<25} ({device['deviceType']})")
                updated += 1
            else:
                print(f"✓ Created: {twin_id:<25} ({device['deviceType']})")
                created += 1
                
        except Exception as e:
            print(f"✗ Failed: {twin_id:<25} - {str(e)[:50]}")
            errors += 1
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Errors:  {errors}")
    print(f"  Total:   {len(DEVICE_TWINS)}")
    
    if errors == 0:
        print("\n✓ All device twins are ready for simulation!")
        return 0
    else:
        print("\n✗ Some twins failed to create")
        return 1


if __name__ == "__main__":
    endpoint = "https://platelet-dt-instance-new.api.eus.digitaltwins.azure.net"
    
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
    
    exit_code = create_device_twins(endpoint)
    sys.exit(exit_code)
