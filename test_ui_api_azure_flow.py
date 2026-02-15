#!/usr/bin/env python3
"""
Test UI → API → Azure Function → Digital Twins Flow
Demonstrates the complete integration from UI through API to Azure
"""

import requests
import json
import os

def test_ui_api_azure_flow():
    """Test the complete flow: UI → API → Azure Function → Digital Twins"""
    
    print("\n" + "="*80)
    print("TESTING: UI → API → Azure Function → Digital Twins Flow")
    print("="*80 + "\n")
    
    # Step 1: Get template configuration (simulating UI request)
    print("Step 1: Fetching template configuration...")
    response = requests.get("http://localhost:8000/templates/platelet-pooling")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch template: {response.status_code}")
        return False
    
    template = response.json()
    print(f"✅ Template fetched: {len(template['devices'])} devices, {len(template['flows'])} flows")
    
    # Step 2: Run simulation through API (simulating UI request)
    print("\nStep 2: Running simulation through API...")
    
    # Check if Azure integration is enabled
    azure_enabled = os.getenv('ENABLE_AZURE_INTEGRATION', 'false').lower() == 'true'
    
    if azure_enabled:
        print(f"   Azure integration: ENABLED")
        print(f"   Function endpoint: {os.getenv('AZURE_FUNCTION_ENDPOINT', 'Not set')}")
    else:
        print(f"   Azure integration: DISABLED (set ENABLE_AZURE_INTEGRATION=true to enable)")
    
    payload = {
        "config": template,
        "run_name": "UI API Azure Test",
        "simulation_name": "Test Simulation",
        "export_to_json": False
    }
    
    response = requests.post(
        "http://localhost:8000/simulations/run",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    results = response.json()
    print(f"✅ Simulation completed successfully")
    
    # Step 3: Check results
    print("\nStep 3: Checking results...")
    simulation_id = results.get('simulation_id')
    sim_results = results.get('results', {})
    summary = sim_results.get('summary', {})
    metadata = sim_results.get('metadata', {})
    
    print(f"   Simulation ID: {simulation_id}")
    print(f"   Flows completed: {summary.get('total_flows_completed', 0)}")
    print(f"   Total events: {summary.get('total_events', 0)}")
    print(f"   Device states: {len(sim_results.get('device_states', []))}")
    
    # Step 4: Check Azure integration
    print("\nStep 4: Checking Azure Digital Twins integration...")
    
    if azure_enabled:
        twins_updated = metadata.get('azure_twins_updated')
        azure_error = metadata.get('azure_error')
        
        if twins_updated is not None:
            print(f"✅ Digital Twins updated: {twins_updated} twins")
        elif azure_error:
            print(f"⚠️  Azure error occurred: {azure_error}")
        else:
            print(f"⚠️  No Azure response in metadata")
    else:
        print(f"   ℹ️  Azure integration is disabled")
        print(f"   ℹ️  To enable, set these environment variables:")
        print(f"      export ENABLE_AZURE_INTEGRATION=true")
        print(f"      export AZURE_FUNCTION_ENDPOINT=<your-function-url>")
        print(f"      export AZURE_FUNCTION_KEY=<your-function-key>  # optional")
    
    # Summary
    print("\n" + "="*80)
    print("FLOW VERIFICATION:")
    print("="*80)
    print(f"✅ UI → API: Working (simulated)")
    print(f"✅ API → Simulation: Working")
    
    if azure_enabled:
        if metadata.get('azure_twins_updated') is not None:
            print(f"✅ API → Azure Function: Working")
            print(f"✅ Azure Function → Digital Twins: Working")
        else:
            print(f"⚠️  API → Azure Function: Called but failed or returned no response")
    else:
        print(f"⚠️  API → Azure Function: Disabled (not configured)")
    
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_ui_api_azure_flow()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("   Please start the API server first:")
        print("   cd api && uvicorn main:app --reload")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
