"""
Find the real bottleneck in platelet pooling process
Shows which device is actually limiting your throughput
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(device_capacities=None):
    """Create baseline config with optional capacity overrides."""
    
    baseline = {
        "centrifuge": 2,
        "platelet_separator": 1,
        "pooling_station": 3,
        "weigh_register": 2,
        "sterile_connect": 2,
        "test_sample": 2,
        "quality_check": 1,
        "label_station": 2,
        "storage_unit": 50,
        "final_inspection": 1,
        "packaging_station": 2
    }
    
    if device_capacities:
        baseline.update(device_capacities)
    
    return {
        "simulation": {
            "duration": 43200,  # 12 hours
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": False
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": baseline["centrifuge"], 
             "recovery_time_range": (180, 300)},
            {"id": "platelet_separator", "type": "machine", "capacity": baseline["platelet_separator"],
             "recovery_time_range": (120, 180)},
            {"id": "pooling_station", "type": "workstation", "capacity": baseline["pooling_station"],
             "recovery_time_range": (60, 120)},
            {"id": "weigh_register", "type": "machine", "capacity": baseline["weigh_register"],
             "recovery_time_range": (30, 60)},
            {"id": "sterile_connect", "type": "workstation", "capacity": baseline["sterile_connect"],
             "recovery_time_range": (45, 90)},
            {"id": "test_sample", "type": "machine", "capacity": baseline["test_sample"],
             "recovery_time_range": (60, 90)},
            {"id": "quality_check", "type": "machine", "capacity": baseline["quality_check"],
             "recovery_time_range": (30, 60)},
            {"id": "label_station", "type": "workstation", "capacity": baseline["label_station"],
             "recovery_time_range": (20, 40)},
            {"id": "storage_unit", "type": "material", "capacity": baseline["storage_unit"],
             "recovery_time_range": (10, 20)},
            {"id": "final_inspection", "type": "machine", "capacity": baseline["final_inspection"],
             "recovery_time_range": (45, 75)},
            {"id": "packaging_station", "type": "workstation", "capacity": baseline["packaging_station"],
             "recovery_time_range": (30, 60)}
        ],
        "flows": [
            {"flow_id": "f1_centrifuge_to_separator", "from_device": "centrifuge",
             "to_device": "platelet_separator", "process_time_range": (300, 480), "priority": 1},
            {"flow_id": "f2_separator_to_pooling", "from_device": "platelet_separator",
             "to_device": "pooling_station", "process_time_range": (600, 900), "priority": 1,
             "dependencies": ["f1_centrifuge_to_separator"]},
            {"flow_id": "f3_pooling_to_weigh", "from_device": "pooling_station",
             "to_device": "weigh_register", "process_time_range": (180, 300), "priority": 1,
             "dependencies": ["f2_separator_to_pooling"]},
            {"flow_id": "f4_weigh_to_sterile", "from_device": "weigh_register",
             "to_device": "sterile_connect", "process_time_range": (120, 240), "priority": 1,
             "dependencies": ["f3_pooling_to_weigh"]},
            {"flow_id": "f5_sterile_to_test", "from_device": "sterile_connect",
             "to_device": "test_sample", "process_time_range": (240, 360), "priority": 1,
             "dependencies": ["f4_weigh_to_sterile"]},
            {"flow_id": "f6_test_to_quality", "from_device": "test_sample",
             "to_device": "quality_check", "process_time_range": (180, 300), "priority": 1,
             "dependencies": ["f5_sterile_to_test"]},
            {"flow_id": "f7_quality_to_label", "from_device": "quality_check",
             "to_device": "label_station", "process_time_range": (120, 180), "priority": 1,
             "dependencies": ["f6_test_to_quality"]},
            {"flow_id": "f8_label_to_storage", "from_device": "label_station",
             "to_device": "storage_unit", "process_time_range": (60, 120), "priority": 1,
             "dependencies": ["f7_quality_to_label"]},
            {"flow_id": "f9_storage_to_inspection", "from_device": "storage_unit",
             "to_device": "final_inspection", "process_time_range": (150, 240), "priority": 1,
             "dependencies": ["f8_label_to_storage"]},
            {"flow_id": "f10_inspection_to_packaging", "from_device": "final_inspection",
             "to_device": "packaging_station", "process_time_range": (180, 300), "priority": 1,
             "dependencies": ["f9_storage_to_inspection"]},
            {"flow_id": "f11_packaging_complete", "from_device": "packaging_station",
             "to_device": "packaging_station", "process_time_range": (120, 180), "priority": 1,
             "dependencies": ["f10_inspection_to_packaging"]}
        ]
    }


def analyze_bottleneck():
    """Find which device is the bottleneck by testing each one."""
    
    print("=" * 100)
    print("BOTTLENECK ANALYSIS - Platelet Pooling Process")
    print("=" * 100)
    print("\nStrategy: Double capacity of each device and measure throughput improvement")
    print("The device with the BIGGEST improvement is your bottleneck!\n")
    
    # Run baseline
    print("Running BASELINE simulation (current capacities)...")
    baseline_config = create_config()
    baseline_engine = SimulationEngine(baseline_config)
    baseline_result = baseline_engine.run()
    baseline_time = baseline_result['summary']['simulation_time_seconds']
    baseline_flows = baseline_result['summary']['total_flows_completed']
    
    print(f"✓ Baseline: {baseline_flows} flows in {baseline_time:.1f}s ({baseline_time/60:.1f} min)\n")
    
    # Test each device
    devices_to_test = [
        "centrifuge", "platelet_separator", "pooling_station", 
        "quality_check", "final_inspection"
    ]
    
    results = []
    
    print("Testing each device (doubling capacity):")
    print("-" * 100)
    
    for device in devices_to_test:
        # Get current capacity
        current_capacity = next(d['capacity'] for d in baseline_config['devices'] if d['id'] == device)
        new_capacity = current_capacity * 2
        
        # Run with doubled capacity
        config = create_config({device: new_capacity})
        engine = SimulationEngine(config)
        result = engine.run()
        
        test_time = result['summary']['simulation_time_seconds']
        test_flows = result['summary']['total_flows_completed']
        
        # Calculate improvement
        time_saved = baseline_time - test_time
        time_improvement = (time_saved / baseline_time) * 100 if baseline_time > 0 else 0
        flow_increase = test_flows - baseline_flows
        
        results.append({
            'device': device,
            'current_capacity': current_capacity,
            'new_capacity': new_capacity,
            'time_saved': time_saved,
            'time_improvement': time_improvement,
            'flow_increase': flow_increase,
            'completion_time': test_time
        })
        
        print(f"{device:<25} {current_capacity}→{new_capacity:<3}  "
              f"Time: {test_time:>7.1f}s  "
              f"Saved: {time_saved:>6.1f}s ({time_improvement:>5.1f}%)  "
              f"Flows: +{flow_increase}")
    
    # Sort by improvement
    results.sort(key=lambda x: x['time_improvement'], reverse=True)
    
    print("\n" + "=" * 100)
    print("BOTTLENECK RANKING (Highest Impact First)")
    print("=" * 100)
    
    for i, r in enumerate(results, 1):
        emoji = "🔴" if i == 1 else "🟡" if i == 2 else "🟢"
        print(f"{i}. {emoji} {r['device']:<25} "
              f"Throughput gain: {r['time_improvement']:>5.1f}%  "
              f"({r['time_saved']:.1f}s saved, +{r['flow_increase']} flows)")
    
    # Recommendations
    print("\n" + "=" * 100)
    print("💡 RECOMMENDATIONS")
    print("=" * 100)
    
    top_bottleneck = results[0]
    
    if top_bottleneck['time_improvement'] > 5:
        print(f"\n🎯 PRIMARY BOTTLENECK: {top_bottleneck['device'].upper()}")
        print(f"   Current capacity: {top_bottleneck['current_capacity']}")
        print(f"   Recommended: Increase to {top_bottleneck['new_capacity']} (or more)")
        print(f"   Expected gain: {top_bottleneck['time_improvement']:.1f}% faster throughput")
    else:
        print("\n✓ No major bottleneck detected - system is well-balanced!")
        print("  All devices have similar impact when capacity is increased.")
    
    if top_bottleneck['device'] != 'centrifuge':
        print(f"\n⚠️  IMPORTANT: Adding more centrifuges will NOT help!")
        print(f"   The {top_bottleneck['device']} is limiting your throughput, not the centrifuge.")
        print(f"   Focus on {top_bottleneck['device']} capacity first.")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    analyze_bottleneck()
