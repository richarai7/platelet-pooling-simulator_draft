"""
Platelet Pooling Simulation - Full 12-Device Configuration
Based on POC requirements and workshop results
"""

from simulation_engine import SimulationEngine
import json
from datetime import datetime

print("=" * 80)
print("PLATELET POOLING SIMULATOR - 12-Device Workflow Demo")
print("=" * 80)
print()

# Full 12-device platelet pooling configuration
# Process flow: Reception → Separation → Pooling → Testing → Quality Check → Storage → Packaging
platelet_config = {
    "simulation": {
        "duration": 129600,  # 36 hours (POC requirement)
        "random_seed": 42     # Deterministic execution
    },
    "devices": [
        # Reception/Pre-Processing (Stage 1)
        {
            "id": "reception_01",
            "type": "reception_station",
            "capacity": 2,  # Can handle 2 units simultaneously
            "initial_state": "Idle",
            "recovery_time_range": (60, 120)  # 1-2 minutes between units
        },
        
        # Separation Devices (Stage 2) - Parallel processing
        {
            "id": "separator_01",
            "type": "centrifuge_separator",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)  # 5-10 minutes recovery
        },
        {
            "id": "separator_02",
            "type": "centrifuge_separator",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)
        },
        
        # Pooling Stations (Stage 3) - Parallel processing
        {
            "id": "pooling_station_01",
            "type": "pooling_workstation",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (180, 300)  # 3-5 minutes
        },
        {
            "id": "pooling_station_02",
            "type": "pooling_workstation",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (180, 300)
        },
        
        # Testing Labs (Stage 4) - Parallel processing
        {
            "id": "testing_lab_01",
            "type": "testing_equipment",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (240, 420)  # 4-7 minutes
        },
        {
            "id": "testing_lab_02",
            "type": "testing_equipment",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (240, 420)
        },
        
        # Quality Check (Stage 5)
        {
            "id": "quality_check",
            "type": "quality_station",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (120, 180)  # 2-3 minutes
        },
        
        # Storage Buffer (Stage 6)
        {
            "id": "storage_unit",
            "type": "storage_buffer",
            "capacity": 10,  # Can hold multiple units
            "initial_state": "Idle",
            "recovery_time_range": None  # No recovery needed
        },
        
        # Final Packaging (Stage 7)
        {
            "id": "packaging_station",
            "type": "packaging_workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": (90, 150)  # 1.5-2.5 minutes
        },
        
        # Waste Management (error handling)
        {
            "id": "waste_management",
            "type": "waste_disposal",
            "capacity": 5,
            "initial_state": "Idle",
            "recovery_time_range": None
        },
        
        # Post-Processing (final prep)
        {
            "id": "post_processing",
            "type": "final_prep_station",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (60, 90)
        }
    ],
    
    "flows": [
        # Stage 1: Reception to Separation (distributes to both separators)
        {
            "flow_id": "reception_to_sep1",
            "from_device": "reception_01",
            "to_device": "separator_01",
            "process_time_range": (300, 600),  # 5-10 minutes reception processing
            "priority": 10,
            "dependencies": None
        },
        {
            "flow_id": "reception_to_sep2",
            "from_device": "reception_01",
            "to_device": "separator_02",
            "process_time_range": (300, 600),
            "priority": 10,
            "dependencies": None
        },
        
        # Stage 2: Separation to Pooling (parallel merge)
        {
            "flow_id": "sep1_to_pool1",
            "from_device": "separator_01",
            "to_device": "pooling_station_01",
            "process_time_range": (1800, 2400),  # 30-40 minutes separation
            "priority": 9,
            "dependencies": None
        },
        {
            "flow_id": "sep1_to_pool2",
            "from_device": "separator_01",
            "to_device": "pooling_station_02",
            "process_time_range": (1800, 2400),
            "priority": 9,
            "dependencies": None
        },
        {
            "flow_id": "sep2_to_pool1",
            "from_device": "separator_02",
            "to_device": "pooling_station_01",
            "process_time_range": (1800, 2400),
            "priority": 9,
            "dependencies": None
        },
        {
            "flow_id": "sep2_to_pool2",
            "from_device": "separator_02",
            "to_device": "pooling_station_02",
            "process_time_range": (1800, 2400),
            "priority": 9,
            "dependencies": None
        },
        
        # Stage 3: Pooling to Testing
        {
            "flow_id": "pool1_to_test1",
            "from_device": "pooling_station_01",
            "to_device": "testing_lab_01",
            "process_time_range": (600, 900),  # 10-15 minutes pooling
            "priority": 8,
            "dependencies": None
        },
        {
            "flow_id": "pool1_to_test2",
            "from_device": "pooling_station_01",
            "to_device": "testing_lab_02",
            "process_time_range": (600, 900),
            "priority": 8,
            "dependencies": None
        },
        {
            "flow_id": "pool2_to_test1",
            "from_device": "pooling_station_02",
            "to_device": "testing_lab_01",
            "process_time_range": (600, 900),
            "priority": 8,
            "dependencies": None
        },
        {
            "flow_id": "pool2_to_test2",
            "from_device": "pooling_station_02",
            "to_device": "testing_lab_02",
            "process_time_range": (600, 900),
            "priority": 8,
            "dependencies": None
        },
        
        # Stage 4: Testing to Quality Check
        {
            "flow_id": "test1_to_quality",
            "from_device": "testing_lab_01",
            "to_device": "quality_check",
            "process_time_range": (900, 1200),  # 15-20 minutes testing
            "priority": 7,
            "dependencies": None
        },
        {
            "flow_id": "test2_to_quality",
            "from_device": "testing_lab_02",
            "to_device": "quality_check",
            "process_time_range": (900, 1200),
            "priority": 7,
            "dependencies": None
        },
        
        # Stage 5: Quality Check to Storage
        {
            "flow_id": "quality_to_storage",
            "from_device": "quality_check",
            "to_device": "storage_unit",
            "process_time_range": (180, 300),  # 3-5 minutes quality check
            "priority": 6,
            "dependencies": None
        },
        
        # Stage 6: Storage to Packaging
        {
            "flow_id": "storage_to_packaging",
            "from_device": "storage_unit",
            "to_device": "packaging_station",
            "process_time_range": (120, 240),  # 2-4 minutes retrieval
            "priority": 5,
            "dependencies": None
        },
        
        # Stage 7: Packaging to Post-Processing
        {
            "flow_id": "packaging_to_post",
            "from_device": "packaging_station",
            "to_device": "post_processing",
            "process_time_range": (300, 480),  # 5-8 minutes packaging
            "priority": 4,
            "dependencies": None
        },
        
        # Error flow: Any stage to waste (quality failures)
        {
            "flow_id": "quality_to_waste",
            "from_device": "quality_check",
            "to_device": "waste_management",
            "process_time_range": (60, 120),  # 1-2 minutes disposal
            "priority": 1,
            "dependencies": None
        }
    ],
    
    "output_options": {
        "include_history": True,   # Track all state transitions
        "include_events": True     # Track all simulation events
    }
}

# Run the simulation
print("🏥 STARTING 36-HOUR PLATELET POOLING SIMULATION")
print(f"   - Duration: {platelet_config['simulation']['duration']/3600:.1f} hours")
print(f"   - Devices: {len(platelet_config['devices'])}")
print(f"   - Process flows: {len(platelet_config['flows'])}")
print(f"   - Random seed: {platelet_config['simulation']['random_seed']}")
print()

start_time = datetime.now()
engine = SimulationEngine(platelet_config)
results = engine.run()
end_time = datetime.now()
execution_time = (end_time - start_time).total_seconds()

print("✅ SIMULATION COMPLETE")
print("-" * 80)
print(f"⏱️  Execution time: {execution_time:.2f}s (target: <120s)")
print(f"📊 Total events processed: {results['summary']['total_events']}")
print(f"🔄 Flows completed: {results['summary']['total_flows_completed']}")
print(f"⏰ Simulated time: {results['summary']['simulation_time_seconds']/3600:.1f} hours")
print()

# Device activity summary
print("📈 DEVICE ACTIVITY:")
print("-" * 80)
for device in results['device_states']:
    state = device['final_state']
    changes = device['state_changes']
    device_id = device['device_id']
    
    # Calculate activity level from state changes
    if changes > 10:
        marker = "🔴"  # High activity
    elif changes > 3:
        marker = "🟡"  # Medium activity
    else:
        marker = "🟢"  # Low activity
    
    print(f"{marker} {device_id:25s} Final: {state:10s} | State changes: {changes}")

print()
print("💡 INSIGHTS:")
print("-" * 80)

# Find most active devices
active_devices = sorted(results['device_states'], key=lambda d: d['state_changes'], reverse=True)[:3]
if active_devices[0]['state_changes'] > 5:
    print("⚠️  MOST ACTIVE DEVICES (potential bottlenecks):")
    for device in active_devices:
        if device['state_changes'] > 5:
            print(f"   - {device['device_id']}: {device['state_changes']} state changes")
else:
    print("✅ Low activity overall - system may be under-loaded")

# Find idle devices
idle_devices = [d for d in results['device_states'] if d['state_changes'] == 0]
if idle_devices:
    print()
    print("📉 IDLE DEVICES (never used - cost optimization opportunity):")
    for device in idle_devices:
        print(f"   - {device['device_id']}")

print()
print("=" * 80)
print("💾 Saving detailed results to platelet_simulation_results.json...")

# Save full results
with open('platelet_simulation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✅ Results saved!")
print()
print("🎯 NEXT STEPS:")
print("   1. Review device utilization to identify bottlenecks")
print("   2. Create variation scenarios (add devices, change timing)")
print("   3. Compare scenarios to find optimal configuration")
print("   4. Use this data to calculate 41 KPIs per POC requirements")
