#!/usr/bin/env python3
"""
Test End-to-End Flow: UI → API → Function App → Digital Twin
Comprehensive testing and diagnostics for the complete flow
"""

import requests
import json
import sys
import time
import os
import subprocess
from typing import Dict, Any, Optional

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
DT_INSTANCE = os.getenv("DT_INSTANCE", "platelet-dt-instance-new")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP", "platelet-rg-new")
AZURE_DIGITAL_TWINS_ENDPOINT = os.getenv("AZURE_DIGITAL_TWINS_ENDPOINT")

# Test configuration
TEST_DEVICE_ID = "centrifuge"  # This will be updated to match new devices


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_api_connection() -> bool:
    """Test if API is running and reachable"""
    print_section("1. Testing API Connection")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ API is running: {data.get('message')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Azure Integration Enabled: {data.get('azure_integration_enabled')}")
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print(f"   Make sure API is running: uvicorn api.main:app --reload")
        return False


def test_azure_diagnostics() -> Dict[str, Any]:
    """Test Azure integration configuration"""
    print_section("2. Testing Azure Configuration")
    
    try:
        response = requests.get(f"{API_URL}/azure/diagnostics", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"Azure Integration Enabled: {data.get('azure_integration_enabled')}")
        print(f"Azure Function Endpoint Configured: {data.get('azure_function_endpoint_configured')}")
        print(f"Azure Function Key Configured: {data.get('azure_function_key_configured')}")
        
        print("\nDevice ID Mapping:")
        for sim_id, twin_id in data.get('device_id_mapping', {}).items():
            print(f"  {sim_id} → {twin_id}")
        
        if not data.get('azure_integration_enabled'):
            print("\n⚠️  Azure integration is disabled")
            print("   Set ENABLE_AZURE_INTEGRATION=true to enable")
        
        return data
        
    except Exception as e:
        print(f"❌ Azure diagnostics failed: {e}")
        return {}


def check_azure_cli_login() -> bool:
    """Check if Azure CLI is logged in"""
    print_section("3. Checking Azure CLI Login")
    
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            print(f"✅ Logged in to Azure")
            print(f"   Account: {account_info.get('user', {}).get('name')}")
            print(f"   Subscription: {account_info.get('name')}")
            return True
        else:
            print(f"❌ Not logged in to Azure")
            print(f"   Run: az login")
            return False
            
    except Exception as e:
        print(f"❌ Azure CLI check failed: {e}")
        print(f"   Make sure Azure CLI is installed")
        return False


def list_digital_twins() -> bool:
    """List all twins in the Digital Twins instance"""
    print_section("4. Listing Digital Twins")
    
    if not AZURE_DIGITAL_TWINS_ENDPOINT:
        print("❌ AZURE_DIGITAL_TWINS_ENDPOINT not set")
        return False
    
    try:
        result = subprocess.run(
            ["az", "dt", "twin", "query",
             "--dt-name", DT_INSTANCE,
             "--resource-group", RESOURCE_GROUP,
             "--query-command", "SELECT * FROM DIGITALTWINS"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            twins = json.loads(result.stdout)
            print(f"✅ Found {len(twins)} twins in Digital Twins instance")
            
            for twin in twins:
                twin_id = twin.get('$dtId')
                device_type = twin.get('deviceType', 'unknown')
                status = twin.get('status', 'unknown')
                print(f"   - {twin_id} (type: {device_type}, status: {status})")
            
            return len(twins) > 0
        else:
            print(f"❌ Failed to list twins: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ List twins failed: {e}")
        return False


def run_test_simulation() -> Optional[Dict[str, Any]]:
    """Run a simple test simulation"""
    print_section("5. Running Test Simulation")
    
    # Simple configuration with new device
    config = {
        "simulation": {
            "duration": 500,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": [10, 20]
            },
            {
                "id": "platelet_washing",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": [10, 20]
            }
        ],
        "flows": [
            {
                "flow_id": "test_flow_1",
                "from_device": "centrifuge",
                "to_device": "platelet_washing",
                "process_time_range": [50, 100],
                "priority": 1,
                "dependencies": None,
                "arrival_time": 0
            },
            {
                "flow_id": "test_flow_2",
                "from_device": "centrifuge",
                "to_device": "platelet_washing",
                "process_time_range": [50, 100],
                "priority": 1,
                "dependencies": None,
                "arrival_time": 100
            }
        ],
        "output_options": {
            "include_events": True,
            "include_history": True
        }
    }
    
    try:
        print("Sending simulation request to API...")
        response = requests.post(
            f"{API_URL}/simulations/run",
            json=config,
            timeout=60
        )
        response.raise_for_status()
        results = response.json()
        
        print(f"✅ Simulation completed")
        print(f"   Simulation ID: {results.get('simulation_id')}")
        print(f"   Total Events: {results.get('results', {}).get('summary', {}).get('total_events')}")
        print(f"   Simulation Time: {results.get('results', {}).get('summary', {}).get('simulation_time_seconds')}s")
        
        # Check Azure metadata
        metadata = results.get('results', {}).get('metadata', {})
        azure_twins_updated = metadata.get('azure_twins_updated')
        azure_error = metadata.get('azure_error')
        
        if azure_twins_updated is not None:
            print(f"\n   Azure Twins Updated: {azure_twins_updated}")
        if azure_error:
            print(f"   Azure Error: {azure_error}")
        
        return results
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return None


def verify_twin_update(twin_id: str) -> bool:
    """Verify that a twin was updated"""
    print_section(f"6. Verifying Twin Update: {twin_id}")
    
    try:
        result = subprocess.run(
            ["az", "dt", "twin", "show",
             "--dt-name", DT_INSTANCE,
             "--resource-group", RESOURCE_GROUP,
             "--twin-id", twin_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            twin = json.loads(result.stdout)
            print(f"✅ Twin {twin_id} found")
            print(f"   Device Type: {twin.get('deviceType')}")
            print(f"   Status: {twin.get('status')}")
            print(f"   Total Processed: {twin.get('totalProcessed', 0)}")
            print(f"   Total Idle Time: {twin.get('totalIdleTime', 0)}")
            print(f"   Total Processing Time: {twin.get('totalProcessingTime', 0)}")
            print(f"   Last Update Time: {twin.get('lastUpdateTime', 'N/A')}")
            
            # Check if twin has been updated recently
            if twin.get('totalProcessed', 0) > 0:
                print(f"\n✅ Twin has been updated with simulation data!")
                return True
            else:
                print(f"\n⚠️  Twin exists but may not have been updated")
                return False
        else:
            print(f"❌ Twin {twin_id} not found: {result.stderr}")
            print(f"\n   You may need to create the twin first:")
            print(f"   python azure_integration/scripts/create_linear_flow_twins.py \\")
            print(f"     --endpoint {AZURE_DIGITAL_TWINS_ENDPOINT}")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🔍" * 40)
    print("   END-TO-END FLOW TESTING & DIAGNOSTICS")
    print("🔍" * 40)
    
    # Track overall success
    all_passed = True
    
    # Test 1: API Connection
    if not test_api_connection():
        print("\n❌ CRITICAL: API is not running. Please start the API first.")
        return False
    
    # Test 2: Azure Configuration
    azure_config = test_azure_diagnostics()
    
    # Test 3: Azure CLI
    azure_cli_ok = check_azure_cli_login()
    
    # Test 4: List Digital Twins
    if azure_cli_ok:
        twins_exist = list_digital_twins()
        if not twins_exist:
            print("\n⚠️  No twins found. Creating twins first...")
            print("   Run: python azure_integration/scripts/create_linear_flow_twins.py")
            all_passed = False
    
    # Test 5: Run Simulation
    if azure_config.get('azure_integration_enabled'):
        print("\n⏳ Waiting 2 seconds before running simulation...")
        time.sleep(2)
        
        sim_results = run_test_simulation()
        
        if sim_results:
            # Wait for Azure Function to process
            print("\n⏳ Waiting 5 seconds for Azure Function to process...")
            time.sleep(5)
            
            # Test 6: Verify twin update
            if azure_cli_ok:
                verify_twin_update("centrifuge")
        else:
            all_passed = False
    else:
        print("\n⚠️  Skipping simulation test (Azure integration disabled)")
    
    # Summary
    print_section("SUMMARY")
    if all_passed:
        print("✅ All tests passed!")
        print("\nThe end-to-end flow is working:")
        print("  UI/Client → API → Function App → Digital Twins")
    else:
        print("⚠️  Some tests failed or were skipped")
        print("\nTroubleshooting steps:")
        print("1. Ensure API is running: uvicorn api.main:app --reload")
        print("2. Set environment variables:")
        print("   export ENABLE_AZURE_INTEGRATION=true")
        print("   export AZURE_DIGITAL_TWINS_ENDPOINT='https://your-instance.api.eus.digitaltwins.azure.net'")
        print("   export AZURE_FUNCTION_ENDPOINT='https://your-function.azurewebsites.net/api/ProcessSimulationTelemetry'")
        print("3. Login to Azure: az login")
        print("4. Create twins: python azure_integration/scripts/create_linear_flow_twins.py --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
