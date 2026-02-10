"""
What-If Analysis: Adding 2 More Centrifuges to Platelet Pooling
REALISTIC scenario with multiple batches running through the system
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(centrifuge_capacity, num_batches=10):
    """
    Create realistic platelet pooling config with multiple batches.
    
    Args:
        centrifuge_capacity: Number of centrifuge machines (2 or 4)
        num_batches: Number of blood donation batches to process
    """
    
    config = {
        "simulation": {
            "duration": 86400,  # 24 hours
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": True
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": (180, 300)},  # 3-5 min recovery
            {"id": "platelet_separator", "type": "machine", "capacity": 2,
             "recovery_time_range": (120, 180)},
            {"id": "pooling_station", "type": "workstation", "capacity": 3,
             "recovery_time_range": (60, 120)},
            {"id": "weigh_register", "type": "machine", "capacity": 2,
             "recovery_time_range": (30, 60)},
            {"id": "sterile_connect", "type": "workstation", "capacity": 2,
             "recovery_time_range": (45, 90)},
            {"id": "test_sample", "type": "machine", "capacity": 2,
             "recovery_time_range": (60, 90)},
            {"id": "quality_check", "type": "machine", "capacity": 1,
             "recovery_time_range": (30, 60)},
            {"id": "label_station", "type": "workstation", "capacity": 2,
             "recovery_time_range": (20, 40)},
            {"id": "storage_unit", "type": "material", "capacity": 50,
             "recovery_time_range": (10, 20)},
            {"id": "final_inspection", "type": "machine", "capacity": 1,
             "recovery_time_range": (45, 75)},
            {"id": "packaging_station", "type": "workstation", "capacity": 2,
             "recovery_time_range": (30, 60)}
        ],
        "flows": []
    }
    
    # Create flows for each batch (PARALLEL batches, not sequential!)
    for batch in range(1, num_batches + 1):
        config["flows"].extend([
            {
                "flow_id": f"b{batch}_f1_centrifuge_to_separator",
                "from_device": "centrifuge",
                "to_device": "platelet_separator",
                "process_time_range": (300, 480),  # 5-8 min
                "priority": 1,
                "dependencies": None  # Starts immediately
            },
            {
                "flow_id": f"b{batch}_f2_separator_to_pooling",
                "from_device": "platelet_separator",
                "to_device": "pooling_station",
                "process_time_range": (600, 900),  # 10-15 min
                "priority": 1,
                "dependencies": [f"b{batch}_f1_centrifuge_to_separator"]
            },
            {
                "flow_id": f"b{batch}_f3_pooling_to_weigh",
                "from_device": "pooling_station",
                "to_device": "weigh_register",
                "process_time_range": (180, 300),  # 3-5 min
                "priority": 1,
                "dependencies": [f"b{batch}_f2_separator_to_pooling"]
            },
            {
                "flow_id": f"b{batch}_f4_weigh_to_sterile",
                "from_device": "weigh_register",
                "to_device": "sterile_connect",
                "process_time_range": (120, 240),  # 2-4 min
                "priority": 1,
                "dependencies": [f"b{batch}_f3_pooling_to_weigh"]
            },
            {
                "flow_id": f"b{batch}_f5_sterile_to_test",
                "from_device": "sterile_connect",
                "to_device": "test_sample",
                "process_time_range": (240, 360),  # 4-6 min
                "priority": 1,
                "dependencies": [f"b{batch}_f4_weigh_to_sterile"]
            },
            {
                "flow_id": f"b{batch}_f6_test_to_quality",
                "from_device": "test_sample",
                "to_device": "quality_check",
                "process_time_range": (180, 300),  # 3-5 min
                "priority": 1,
                "dependencies": [f"b{batch}_f5_sterile_to_test"]
            },
            {
                "flow_id": f"b{batch}_f7_quality_to_label",
                "from_device": "quality_check",
                "to_device": "label_station",
                "process_time_range": (120, 180),  # 2-3 min
                "priority": 1,
                "dependencies": [f"b{batch}_f6_test_to_quality"]
            },
            {
                "flow_id": f"b{batch}_f8_label_to_storage",
                "from_device": "label_station",
                "to_device": "storage_unit",
                "process_time_range": (60, 120),  # 1-2 min
                "priority": 1,
                "dependencies": [f"b{batch}_f7_quality_to_label"]
            },
            {
                "flow_id": f"b{batch}_f9_storage_to_inspection",
                "from_device": "storage_unit",
                "to_device": "final_inspection",
                "process_time_range": (150, 240),  # 2.5-4 min
                "priority": 1,
                "dependencies": [f"b{batch}_f8_label_to_storage"]
            },
            {
                "flow_id": f"b{batch}_f10_inspection_to_packaging",
                "from_device": "final_inspection",
                "to_device": "packaging_station",
                "process_time_range": (180, 300),  # 3-5 min
                "priority": 1,
                "dependencies": [f"b{batch}_f9_storage_to_inspection"]
            },
            {
                "flow_id": f"b{batch}_f11_packaging_complete",
                "from_device": "packaging_station",
                "to_device": "packaging_station",
                "process_time_range": (120, 180),  # 2-3 min
                "priority": 1,
                "dependencies": [f"b{batch}_f10_inspection_to_packaging"]
            }
        ])
    
    return config


def run_comparison():
    """Compare baseline (2 centrifuges) vs adding 2 more (4 total)."""
    
    print("=" * 100)
    print("WHAT-IF ANALYSIS: Adding 2 More Centrifuges")
    print("=" * 100)
    print("\nScenario: Processing 10 batches of blood donations through platelet pooling")
    print("Question: What happens if we add 2 more centrifuge machines?\n")
    
    num_batches = 10
    results = {}
    
    for capacity in [2, 4]:
        scenario = "BASELINE (Current)" if capacity == 2 else "WHAT-IF (+2 Centrifuges)"
        print(f"\n{'='*100}")
        print(f"{scenario}: {capacity} Centrifuge Machines")
        print(f"{'='*100}")
        
        config = create_config(centrifuge_capacity=capacity, num_batches=num_batches)
        engine = SimulationEngine(config)
        result = engine.run()
        
        results[capacity] = result
        
        total_time_hours = result['summary']['simulation_time_seconds'] / 3600
        flows_per_batch = 11
        total_flows = num_batches * flows_per_batch
        completed_batches = result['summary']['total_flows_completed'] / flows_per_batch
        
        print(f"\n✓ Simulation Complete")
        print(f"  Total Time: {result['summary']['simulation_time_seconds']:.1f}s ({total_time_hours:.2f} hours)")
        print(f"  Flows Completed: {result['summary']['total_flows_completed']}/{total_flows}")
        print(f"  Batches Completed: {completed_batches:.1f}/{num_batches}")
        print(f"  Total Events: {result['summary']['total_events']:,}")
    
    # Detailed comparison
    print("\n" + "=" * 100)
    print("📊 IMPACT ANALYSIS")
    print("=" * 100)
    
    baseline = results[2]
    whatif = results[4]
    
    baseline_time = baseline['summary']['simulation_time_seconds']
    whatif_time = whatif['summary']['simulation_time_seconds']
    time_saved = baseline_time - whatif_time
    time_saved_hours = time_saved / 3600
    improvement_pct = (time_saved / baseline_time * 100) if baseline_time > 0 else 0
    
    baseline_flows = baseline['summary']['total_flows_completed']
    whatif_flows = whatif['summary']['total_flows_completed']
    flow_increase = whatif_flows - baseline_flows
    
    print(f"\n⏱️  TIME TO COMPLETE:")
    print(f"   Baseline (2 centrifuges):  {baseline_time:.1f}s ({baseline_time/3600:.2f} hours)")
    print(f"   With +2 centrifuges:       {whatif_time:.1f}s ({whatif_time/3600:.2f} hours)")
    print(f"   Time Saved:                {time_saved:.1f}s ({time_saved_hours:.2f} hours)")
    print(f"   Improvement:               {improvement_pct:.1f}% FASTER")
    
    print(f"\n📦 THROUGHPUT:")
    print(f"   Baseline:     {baseline_flows} flows completed")
    print(f"   With +2:      {whatif_flows} flows completed")
    print(f"   Increase:     +{flow_increase} flows ({flow_increase/baseline_flows*100:.1f}% more)")
    
    # Device utilization analysis
    print(f"\n🔧 DEVICE UTILIZATION:")
    print(f"   {'Device':<25} {'Baseline State':<20} {'What-If State':<20}")
    print(f"   {'-'*70}")
    
    baseline_states = {d['device_id']: d['final_state'] for d in baseline['device_states']}
    whatif_states = {d['device_id']: d['final_state'] for d in whatif['device_states']}
    
    key_devices = ["centrifuge", "platelet_separator", "quality_check", "final_inspection"]
    for device in key_devices:
        b_state = baseline_states.get(device, "N/A")
        w_state = whatif_states.get(device, "N/A")
        print(f"   {device:<25} {b_state:<20} {w_state:<20}")
    
    # Financial analysis
    print(f"\n💰 BUSINESS CASE:")
    centrifuge_cost = 250000  # Example: $250k per centrifuge
    total_investment = centrifuge_cost * 2
    
    print(f"   Investment: ${total_investment:,} (2 centrifuges @ ${centrifuge_cost:,} each)")
    
    if improvement_pct > 5:
        batches_per_day_baseline = (24 / (baseline_time / 3600)) * (baseline_flows / (num_batches * 11))
        batches_per_day_whatif = (24 / (whatif_time / 3600)) * (whatif_flows / (num_batches * 11))
        extra_batches = batches_per_day_whatif - batches_per_day_baseline
        
        print(f"   Daily Capacity Increase: {extra_batches:.1f} more batches/day")
        print(f"   Throughput Gain: {improvement_pct:.1f}%")
    else:
        print(f"   ⚠️  Warning: Only {improvement_pct:.1f}% improvement - centrifuge may NOT be the bottleneck")
    
    # Decision recommendation
    print("\n" + "=" * 100)
    print("🎯 RECOMMENDATION")
    print("=" * 100)
    
    if improvement_pct > 20:
        print(f"\n✅ STRONG RECOMMENDATION: Add the 2 centrifuges")
        print(f"   • {improvement_pct:.1f}% faster processing")
        print(f"   • {flow_increase} more flows completed")
        print(f"   • Centrifuge is clearly a bottleneck")
    elif improvement_pct > 5:
        print(f"\n⚠️  MODERATE RECOMMENDATION: Consider adding centrifuges")
        print(f"   • {improvement_pct:.1f}% improvement (moderate gain)")
        print(f"   • May want to analyze other bottlenecks first")
    else:
        print(f"\n❌ NOT RECOMMENDED: Don't add centrifuges yet")
        print(f"   • Only {improvement_pct:.1f}% improvement (minimal impact)")
        print(f"   • Centrifuge is NOT your bottleneck")
        print(f"   • Focus on other devices (quality_check, final_inspection, etc.)")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    run_comparison()
