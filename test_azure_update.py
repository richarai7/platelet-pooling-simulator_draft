#!/usr/bin/env python3
"""
Test Azure Digital Twins update flow
"""
import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
DT_INSTANCE = "platelet-dt-instance-new"
RESOURCE_GROUP = "platelet-rg-new"

def test_simulation_and_verify():
    """Run a simulation via API and verify twins are updated"""
    
    print("=" * 70)
    print("TESTING AZURE DIGITAL TWINS UPDATE FLOW")
    print("=" * 70)
    
    # Step 1: Get centrifuge-01 initial state
    print("\n1. Checking initial state of centrifuge-01...")
    import subprocess
    result = subprocess.run([
        "az", "dt", "twin", "show",
        "--dt-name", DT_INSTANCE,
        "--resource-group", RESOURCE_GROUP,
        "--twin-id", "centrifuge-01"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ Failed to get twin: {result.stderr}")
        return False
    
    initial_state = json.loads(result.stdout)
    initial_processed = initial_state.get("totalProcessed", 0)
    print(f"   Initial totalProcessed: {initial_processed}")
    
    # Step 2: Run simulation via API
    print("\n2. Running simulation via API...")
    config = {
        "simulation": {
            "duration": 100,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": [10, 20]
            }
        ],
        "flows": [
            {
                "flow_id": "test_flow",
                "from_device": "centrifuge",
                "to_device": "centrifuge",
                "process_time_range": [5, 10],
                "priority": 1
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/simulations/run",
            json=config,
            timeout=30
        )
        response.raise_for_status()
        sim_results = response.json()
        print(f"   ✓ Simulation completed: {sim_results.get('simulation_id')}")
        print(f"   Total events: {sim_results.get('summary', {}).get('total_events', 0)}")
        
    except Exception as e:
        print(f"   ❌ Simulation failed: {e}")
        return False
    
    # Step 3: Wait a moment for Azure Function to process
    print("\n3. Waiting for Azure Function to process...")
    import time
    time.sleep(3)
    
    # Step 4: Check updated state
    print("\n4. Checking updated state of centrifuge-01...")
    result = subprocess.run([
        "az", "dt", "twin", "show",
        "--dt-name", DT_INSTANCE,
        "--resource-group", RESOURCE_GROUP,
        "--twin-id", "centrifuge-01"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ Failed to get twin: {result.stderr}")
        return False
    
    updated_state = json.loads(result.stdout)
    updated_processed = updated_state.get("totalProcessed", 0)
    updated_idle = updated_state.get("totalIdleTime", 0)
    updated_processing = updated_state.get("totalProcessingTime", 0)
    
    print(f"   Updated totalProcessed: {updated_processed}")
    print(f"   Updated totalIdleTime: {updated_idle}")
    print(f"   Updated totalProcessingTime: {updated_processing}")
    
    # Step 5: Verify update
    print("\n5. Verification:")
    if updated_processed > initial_processed:
        print(f"   ✅ SUCCESS! Twin was updated.")
        print(f"   Processed increased by: {updated_processed - initial_processed}")
        return True
    else:
        print(f"   ❌ FAILED! Twin was NOT updated.")
        print(f"   Check API logs for Azure Function call status")
        return False

if __name__ == "__main__":
    success = test_simulation_and_verify()
    sys.exit(0 if success else 1)
