"""
Compare simulation results with different centrifuge capacities
"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(centrifuge_capacity):
    """Create configuration with specified centrifuge capacity."""
    return {
        "simulation": {
            "duration": 43200,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": centrifuge_capacity,
                "recovery_time_range": (180, 300)
            },
            {
                "id": "platelet_separator",
                "type": "machine",
                "capacity": 1,
                "recovery_time_range": (120, 180)
            },
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
            {
                "id": "label_station",
                "type": "workstation",
                "capacity": 2,
                "recovery_time_range": (20, 40)
            },
            {
                "id": "storage_unit",
                "type": "material",
                "capacity": 50,
                "recovery_time_range": (10, 20)
            },
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
            {
                "flow_id": "f1_centrifuge_to_separator",
                "from_device": "centrifuge",
                "to_device": "platelet_separator",
                "process_time_range": (300, 480),
                "priority": 1,
                "dependencies": None
            },
            {
                "flow_id": "f2_separator_to_pooling",
                "from_device": "platelet_separator",
                "to_device": "pooling_station",
                "process_time_range": (600, 900),
                "priority": 1,
                "dependencies": ["f1_centrifuge_to_separator"]
            },
            {
                "flow_id": "f3_pooling_to_weigh",
                "from_device": "pooling_station",
                "to_device": "weigh_register",
                "process_time_range": (420, 600),
                "priority": 1,
                "dependencies": ["f2_separator_to_pooling"]
            },
            {
                "flow_id": "f4_weigh_to_sterile",
                "from_device": "weigh_register",
                "to_device": "sterile_connect",
                "process_time_range": (240, 360),
                "priority": 1,
                "dependencies": ["f3_pooling_to_weigh"]
            },
            {
                "flow_id": "f5_sterile_to_test",
                "from_device": "sterile_connect",
                "to_device": "test_sample",
                "process_time_range": (180, 300),
                "priority": 1,
                "dependencies": ["f4_weigh_to_sterile"]
            },
            {
                "flow_id": "f6_test_to_qc",
                "from_device": "test_sample",
                "to_device": "quality_check",
                "process_time_range": (360, 600),
                "priority": 1,
                "dependencies": ["f5_sterile_to_test"]
            },
            {
                "flow_id": "f7_qc_to_label",
                "from_device": "quality_check",
                "to_device": "label_station",
                "process_time_range": (120, 240),
                "priority": 1,
                "dependencies": ["f6_test_to_qc"],
                "required_gates": ["QC_Pass"]
            },
            {
                "flow_id": "f8_label_to_storage",
                "from_device": "label_station",
                "to_device": "storage_unit",
                "process_time_range": (60, 120),
                "priority": 1,
                "dependencies": ["f7_qc_to_label"]
            },
            {
                "flow_id": "f9_storage_to_inspection",
                "from_device": "storage_unit",
                "to_device": "final_inspection",
                "process_time_range": (180, 300),
                "priority": 1,
                "dependencies": ["f8_label_to_storage"]
            },
            {
                "flow_id": "f10_inspection_to_packaging",
                "from_device": "final_inspection",
                "to_device": "packaging_station",
                "process_time_range": (240, 360),
                "priority": 1,
                "dependencies": ["f9_storage_to_inspection"]
            },
            {
                "flow_id": "f11_direct_pool",
                "from_device": "centrifuge",
                "to_device": "pooling_station",
                "process_time_range": (480, 720),
                "priority": 2,
                "dependencies": None
            }
        ],
        "gates": {
            "QC_Pass": True,
            "Sterile_Conditions": True,
            "Temperature_Control": True
        },
        "output_options": {
            "include_events": True,
            "include_history": True
        }
    }


def run_comparison():
    """Run simulations with different centrifuge capacities and compare."""
    print("=" * 100)
    print("CENTRIFUGE CAPACITY COMPARISON")
    print("=" * 100)
    
    results = {}
    
    for capacity in [2, 4]:
        print(f"\n{'='*100}")
        print(f"Running simulation with {capacity} centrifuge(s)...")
        print(f"{'='*100}")
        
        config = create_config(capacity)
        engine = SimulationEngine(config)
        result = engine.run()
        
        results[capacity] = result
        
        print(f"\n✓ Simulation completed")
        print(f"  Total Events: {result['summary']['total_events']:,}")
        print(f"  Flows Completed: {result['summary']['total_flows_completed']}")
        print(f"  Simulated Time: {result['summary']['simulation_time_seconds']:.1f}s ({result['summary']['simulation_time_seconds']/3600:.2f} hours)")
    
    # Comparison
    print("\n" + "=" * 100)
    print("COMPARISON RESULTS")
    print("=" * 100)
    
    print(f"\n{'Metric':<30} {'Capacity 2':<25} {'Capacity 4':<25} {'Difference':<20}")
    print("-" * 100)
    
    metrics = {
        "Total Events": "total_events",
        "Flows Completed": "total_flows_completed",
        "Simulated Time (s)": "simulation_time_seconds",
        "Simulated Time (hours)": lambda r: r["simulation_time_seconds"] / 3600
    }
    
    for metric_name, metric_key in metrics.items():
        if callable(metric_key):
            val_2 = metric_key(results[2]['summary'])
            val_4 = metric_key(results[4]['summary'])
        else:
            val_2 = results[2]['summary'][metric_key]
            val_4 = results[4]['summary'][metric_key]
        
        diff = val_4 - val_2
        if isinstance(val_2, float):
            print(f"{metric_name:<30} {val_2:<25.2f} {val_4:<25.2f} {diff:+.2f} ({diff/val_2*100:+.1f}%)")
        else:
            print(f"{metric_name:<30} {val_2:<25,} {val_4:<25,} {diff:+,} ({diff/val_2*100:+.1f}%)")
    
    # Device states comparison
    print(f"\n{'Device Final States':<30} {'Capacity 2':<25} {'Capacity 4':<25}")
    print("-" * 100)
    
    # Convert list to dict for easier lookup
    states_2 = {d['device_id']: d['final_state'] for d in results[2]['device_states']}
    states_4 = {d['device_id']: d['final_state'] for d in results[4]['device_states']}
    
    for device_id in ["centrifuge", "platelet_separator", "quality_check", "final_inspection"]:
        state_2 = states_2.get(device_id, "N/A")
        state_4 = states_4.get(device_id, "N/A")
        print(f"{device_id:<30} {state_2:<25} {state_4:<25}")
    
    # Performance improvement
    print("\n" + "=" * 100)
    print("INSIGHTS")
    print("=" * 100)
    
    time_diff = results[2]['summary']['simulation_time_seconds'] - results[4]['summary']['simulation_time_seconds']
    event_diff = results[4]['summary']['total_events'] - results[2]['summary']['total_events']
    
    print(f"\n✓ Doubling centrifuge capacity (2→4):")
    print(f"  • Reduces completion time by {time_diff:.1f}s ({time_diff/60:.1f} minutes)")
    print(f"  • Increases total events by {event_diff:,} ({event_diff/results[2]['summary']['total_events']*100:.1f}%)")
    print(f"  • Throughput improvement: {(1 - results[4]['summary']['simulation_time_seconds']/results[2]['summary']['simulation_time_seconds'])*100:.1f}%")
    
    total_flows = len(create_config(2)['flows'])
    if results[2]['summary']['total_flows_completed'] < total_flows:
        print(f"\n⚠ Warning: Not all flows completed in capacity=2 scenario")
        print(f"  Consider increasing simulation duration or investigating bottlenecks")
    
    # Save detailed results
    with open("comparison_results.json", "w") as f:
        json.dump({
            "capacity_2": results[2],
            "capacity_4": results[4]
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: comparison_results.json")
    print("=" * 100)


if __name__ == "__main__":
    run_comparison()
