"""
Complex Platelet Processing Flow Configuration
Based on the provided flow diagram showing pre-pooling and pooling processes
"""

from pathlib import Path
import sys
import json

# Add API to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_platelet_flow_config():
    """
    Create configuration based on the flow diagram.
    
    Flow stages identified:
    1. Pre-Platelet Pooling Process (left section)
    2. Pooling Process (center section)
    3. Storage and Final Processing (right section)
    """
    
    config = {
        "simulation": {
            "duration": 43200,  # 12 hours in seconds
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        
        "devices": [
            # Pre-Processing Stage
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": (180, 300)  # 3-5 minutes
            },
            {
                "id": "platelet_separator",
                "type": "machine",
                "capacity": 1,
                "recovery_time_range": (120, 180)
            },
            
            # Pooling Stage - Main Process
            {
                "id": "pooling_station",
                "type": "workstation",
                "capacity": 3,
                "recovery_time_range": (60, 120)
            },
            {
                "id": "weigh_register",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": (30, 60)
            },
            {
                "id": "sterile_connect",
                "type": "workstation",
                "capacity": 2,
                "recovery_time_range": (45, 90)
            },
            
            # Testing Stage
            {
                "id": "test_sample",
                "type": "machine",
                "capacity": 2,
                "recovery_time_range": (60, 90)
            },
            {
                "id": "quality_check",
                "type": "machine",
                "capacity": 1,
                "recovery_time_range": (30, 60)
            },
            
            # Storage and Labeling
            {
                "id": "label_station",
                "type": "workstation",
                "capacity": 2,
                "recovery_time_range": (20, 40)
            },
            {
                "id": "storage_unit",
                "type": "material",
                "capacity": 50,  # Can hold multiple units
                "recovery_time_range": (10, 20)
            },
            
            # Final Processing
            {
                "id": "final_inspection",
                "type": "machine",
                "capacity": 1,
                "recovery_time_range": (45, 75)
            },
            {
                "id": "packaging_station",
                "type": "workstation",
                "capacity": 2,
                "recovery_time_range": (30, 60)
            }
        ],
        
        "flows": [
            # Stage 1: Pre-Processing
            {
                "flow_id": "f1_centrifuge_to_separator",
                "from_device": "centrifuge",
                "to_device": "platelet_separator",
                "process_time_range": (300, 480),  # 5-8 minutes
                "priority": 1,
                "dependencies": None
            },
            
            # Stage 2: Separation to Pooling
            {
                "flow_id": "f2_separator_to_pooling",
                "from_device": "platelet_separator",
                "to_device": "pooling_station",
                "process_time_range": (600, 900),  # 10-15 minutes
                "priority": 1,
                "dependencies": ["f1_centrifuge_to_separator"]
            },
            
            # Stage 3: Pooling Process
            {
                "flow_id": "f3_pooling_to_weigh",
                "from_device": "pooling_station",
                "to_device": "weigh_register",
                "process_time_range": (420, 600),  # 7-10 minutes
                "priority": 1,
                "dependencies": ["f2_separator_to_pooling"]
            },
            
            # Stage 4: Weight Registration to Sterile Connect
            {
                "flow_id": "f4_weigh_to_sterile",
                "from_device": "weigh_register",
                "to_device": "sterile_connect",
                "process_time_range": (240, 360),  # 4-6 minutes
                "priority": 1,
                "dependencies": ["f3_pooling_to_weigh"]
            },
            
            # Stage 5: Sterile Connect to Testing
            {
                "flow_id": "f5_sterile_to_test",
                "from_device": "sterile_connect",
                "to_device": "test_sample",
                "process_time_range": (180, 300),  # 3-5 minutes
                "priority": 1,
                "dependencies": ["f4_weigh_to_sterile"]
            },
            
            # Stage 6: Testing to Quality Check
            {
                "flow_id": "f6_test_to_qc",
                "from_device": "test_sample",
                "to_device": "quality_check",
                "process_time_range": (360, 600),  # 6-10 minutes
                "priority": 1,
                "dependencies": ["f5_sterile_to_test"]
            },
            
            # Stage 7: QC to Labeling (if pass)
            {
                "flow_id": "f7_qc_to_label",
                "from_device": "quality_check",
                "to_device": "label_station",
                "process_time_range": (120, 240),  # 2-4 minutes
                "priority": 1,
                "dependencies": ["f6_test_to_qc"],
                "required_gates": ["QC_Pass"]  # Only if QC passes
            },
            
            # Stage 8: Labeling to Storage
            {
                "flow_id": "f8_label_to_storage",
                "from_device": "label_station",
                "to_device": "storage_unit",
                "process_time_range": (60, 120),  # 1-2 minutes
                "priority": 1,
                "dependencies": ["f7_qc_to_label"]
            },
            
            # Stage 9: Storage to Final Inspection
            {
                "flow_id": "f9_storage_to_inspection",
                "from_device": "storage_unit",
                "to_device": "final_inspection",
                "process_time_range": (180, 300),  # 3-5 minutes
                "priority": 1,
                "dependencies": ["f8_label_to_storage"]
            },
            
            # Stage 10: Final Inspection to Packaging
            {
                "flow_id": "f10_inspection_to_packaging",
                "from_device": "final_inspection",
                "to_device": "packaging_station",
                "process_time_range": (240, 360),  # 4-6 minutes
                "priority": 1,
                "dependencies": ["f9_storage_to_inspection"]
            },
            
            # Parallel flow: Direct pooling (if eligible)
            {
                "flow_id": "f11_direct_pool",
                "from_device": "centrifuge",
                "to_device": "pooling_station",
                "process_time_range": (480, 720),  # 8-12 minutes (faster path)
                "priority": 2,
                "dependencies": None
            }
        ],
        
        "gates": {
            "QC_Pass": True,  # Quality control gate
            "Sterile_Conditions": True,
            "Temperature_Control": True
        },
        
        "output_options": {
            "include_events": True,
            "include_history": True
        }
    }
    
    return config


def run_simulation():
    """Run the platelet flow simulation and display results."""
    print("=" * 80)
    print("COMPLEX PLATELET PROCESSING FLOW SIMULATION")
    print("=" * 80)
    
    # Create configuration
    config = create_platelet_flow_config()
    
    print(f"\n📋 Configuration Summary:")
    print(f"   Duration: {config['simulation']['duration']}s ({config['simulation']['duration']/3600:.1f} hours)")
    print(f"   Devices: {len(config['devices'])}")
    print(f"   Flows: {len(config['flows'])}")
    print(f"   Gates: {', '.join(config['gates'].keys())}")
    
    # Run simulation
    print(f"\n⚙️  Running simulation...")
    engine = SimulationEngine(config)
    results = engine.run()
    
    # Display results
    print(f"\n✅ Simulation Complete!")
    print(f"\n📊 Summary:")
    print(f"   Total Events: {results['summary']['total_events']}")
    print(f"   Flows Completed: {results['summary']['total_flows_completed']}")
    print(f"   Simulated Time: {results['summary']['simulation_time_seconds']:.1f}s")
    print(f"   Execution Time: {results['summary']['execution_time_seconds']:.3f}s")
    
    print(f"\n🔄 Flow Execution Details:")
    for flow_exec in results['flows_executed']:
        print(f"   {flow_exec['flow_id']}: {flow_exec['execution_count']} executions")
    
    print(f"\n🏭 Final Device States:")
    for device_state in results['device_states']:
        print(f"   {device_state['device_id']}: {device_state['final_state']} ({device_state['state_changes']} state changes)")
    
    # Save detailed results
    output_file = "platelet_flow_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    results = run_simulation()
