"""
Compare simulation results with different quality_check and final_inspection capacities
"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(qc_capacity, inspection_capacity):
    """Create configuration with specified capacities."""
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
                "capacity": 2,
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
                "capacity": qc_capacity,
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
                "capacity": inspection_capacity,
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
    """Run simulations with different capacities and compare."""
    print("=" * 100)
    print("BOTTLENECK ANALYSIS: QUALITY_CHECK vs FINAL_INSPECTION")
    print("=" * 100)
    
    scenarios = {
        "Baseline (QC=1, Insp=1)": (1, 1),
        "QC Increased (QC=4, Insp=1)": (4, 1),
        "Inspection Increased (QC=1, Insp=4)": (1, 4),
        "Both Increased (QC=4, Insp=4)": (4, 4),
    }
    
    results = {}
    
    for scenario_name, (qc_cap, insp_cap) in scenarios.items():
        print(f"\n{'='*100}")
        print(f"Running: {scenario_name}")
        print(f"{'='*100}")
        
        config = create_config(qc_cap, insp_cap)
        engine = SimulationEngine(config)
        result = engine.run()
        
        results[scenario_name] = result
        
        print(f"\n✓ Simulation completed")
        print(f"  Total Events: {result['summary']['total_events']:,}")
        print(f"  Flows Completed: {result['summary']['total_flows_completed']}")
        print(f"  Simulated Time: {result['summary']['simulation_time_seconds']:.1f}s ({result['summary']['simulation_time_seconds']/3600:.2f} hours)")
        print(f"  Execution Time: {result['summary']['execution_time_seconds']:.3f}s")
    
    # Comparison Table
    print("\n" + "=" * 100)
    print("COMPARISON RESULTS")
    print("=" * 100)
    
    baseline_time = results["Baseline (QC=1, Insp=1)"]['summary']['simulation_time_seconds']
    
    print(f"\n{'Scenario':<35} {'Sim Time (s)':<15} {'Time (hrs)':<12} {'Events':<10} {'Improvement':<15}")
    print("-" * 100)
    
    for scenario_name in scenarios.keys():
        result = results[scenario_name]['summary']
        sim_time = result['simulation_time_seconds']
        hours = sim_time / 3600
        events = result['total_events']
        improvement = ((baseline_time - sim_time) / baseline_time * 100)
        
        print(f"{scenario_name:<35} {sim_time:<15.1f} {hours:<12.2f} {events:<10,} {improvement:+.1f}%")
    
    # Detailed Analysis
    print("\n" + "=" * 100)
    print("BOTTLENECK ANALYSIS")
    print("=" * 100)
    
    baseline = results["Baseline (QC=1, Insp=1)"]['summary']['simulation_time_seconds']
    qc_only = results["QC Increased (QC=4, Insp=1)"]['summary']['simulation_time_seconds']
    insp_only = results["Inspection Increased (QC=1, Insp=4)"]['summary']['simulation_time_seconds']
    both = results["Both Increased (QC=4, Insp=4)"]['summary']['simulation_time_seconds']
    
    qc_impact = ((baseline - qc_only) / baseline * 100)
    insp_impact = ((baseline - insp_only) / baseline * 100)
    combined_impact = ((baseline - both) / baseline * 100)
    
    print(f"\n📊 Impact Analysis:")
    print(f"  • Baseline time: {baseline:.1f}s ({baseline/3600:.2f} hours)")
    print(f"\n  • Quality Check capacity 1→4:")
    print(f"    - Time: {baseline:.1f}s → {qc_only:.1f}s")
    print(f"    - Improvement: {qc_impact:+.1f}%")
    
    print(f"\n  • Final Inspection capacity 1→4:")
    print(f"    - Time: {baseline:.1f}s → {insp_only:.1f}s")
    print(f"    - Improvement: {insp_impact:+.1f}%")
    
    print(f"\n  • Both capacity 1→4:")
    print(f"    - Time: {baseline:.1f}s → {both:.1f}s")
    print(f"    - Improvement: {combined_impact:+.1f}%")
    
    # Determine bottleneck
    print("\n" + "=" * 100)
    print("CONCLUSION")
    print("=" * 100)
    
    if abs(qc_impact) < 0.1 and abs(insp_impact) < 0.1:
        print("\n❌ Neither quality_check nor final_inspection is the bottleneck!")
        print("\n💡 The bottleneck is likely:")
        print("   • The sequential dependency chain itself (Finish-to-Start constraints)")
        print("   • Need to analyze device utilization and blocking times")
        print("   • Consider parallel processing paths or reducing process times")
    elif qc_impact > insp_impact:
        print(f"\n🎯 BOTTLENECK IDENTIFIED: quality_check")
        print(f"   • Increasing QC capacity improves throughput by {qc_impact:.1f}%")
        print(f"   • Final inspection has minimal impact ({insp_impact:.1f}%)")
    elif insp_impact > qc_impact:
        print(f"\n🎯 BOTTLENECK IDENTIFIED: final_inspection")
        print(f"   • Increasing inspection capacity improves throughput by {insp_impact:.1f}%")
        print(f"   • Quality check has minimal impact ({qc_impact:.1f}%)")
    else:
        print(f"\n🎯 SHARED BOTTLENECK: Both quality_check and final_inspection")
        print(f"   • Both contribute equally to the constraint")
        print(f"   • Combined improvement: {combined_impact:.1f}%")
    
    # Save detailed results
    with open("bottleneck_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: bottleneck_analysis_results.json")
    print("=" * 100)


if __name__ == "__main__":
    run_comparison()
