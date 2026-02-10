"""
Test each device to find the REAL bottleneck in platelet pooling
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(device_overrides=None, num_batches=10):
    """Create config with optional device capacity overrides."""
    
    devices = {
        "centrifuge": 2,
        "platelet_separator": 2,
        "pooling_station": 3,
        "weigh_register": 2,
        "sterile_connect": 2,
        "test_sample": 2,
        "quality_check": 1,  # Low capacity - suspicious!
        "label_station": 2,
        "storage_unit": 50,
        "final_inspection": 1,  # Low capacity - suspicious!
        "packaging_station": 2
    }
    
    if device_overrides:
        devices.update(device_overrides)
    
    config = {
        "simulation": {
            "duration": 86400,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": False
        },
        "devices": [
            {"id": k, "type": "machine", "capacity": v, "recovery_time_range": (30, 90)}
            for k, v in devices.items()
        ],
        "flows": []
    }
    
    # Create parallel batches
    for batch in range(1, num_batches + 1):
        config["flows"].extend([
            {"flow_id": f"b{batch}_f1", "from_device": "centrifuge", "to_device": "platelet_separator",
             "process_time_range": (300, 480), "priority": 1, "dependencies": None},
            {"flow_id": f"b{batch}_f2", "from_device": "platelet_separator", "to_device": "pooling_station",
             "process_time_range": (600, 900), "priority": 1, "dependencies": [f"b{batch}_f1"]},
            {"flow_id": f"b{batch}_f3", "from_device": "pooling_station", "to_device": "weigh_register",
             "process_time_range": (180, 300), "priority": 1, "dependencies": [f"b{batch}_f2"]},
            {"flow_id": f"b{batch}_f4", "from_device": "weigh_register", "to_device": "sterile_connect",
             "process_time_range": (120, 240), "priority": 1, "dependencies": [f"b{batch}_f3"]},
            {"flow_id": f"b{batch}_f5", "from_device": "sterile_connect", "to_device": "test_sample",
             "process_time_range": (240, 360), "priority": 1, "dependencies": [f"b{batch}_f4"]},
            {"flow_id": f"b{batch}_f6", "from_device": "test_sample", "to_device": "quality_check",
             "process_time_range": (180, 300), "priority": 1, "dependencies": [f"b{batch}_f5"]},
            {"flow_id": f"b{batch}_f7", "from_device": "quality_check", "to_device": "label_station",
             "process_time_range": (120, 180), "priority": 1, "dependencies": [f"b{batch}_f6"]},
            {"flow_id": f"b{batch}_f8", "from_device": "label_station", "to_device": "storage_unit",
             "process_time_range": (60, 120), "priority": 1, "dependencies": [f"b{batch}_f7"]},
            {"flow_id": f"b{batch}_f9", "from_device": "storage_unit", "to_device": "final_inspection",
             "process_time_range": (150, 240), "priority": 1, "dependencies": [f"b{batch}_f8"]},
            {"flow_id": f"b{batch}_f10", "from_device": "final_inspection", "to_device": "packaging_station",
             "process_time_range": (180, 300), "priority": 1, "dependencies": [f"b{batch}_f9"]},
            {"flow_id": f"b{batch}_f11", "from_device": "packaging_station", "to_device": "packaging_station",
             "process_time_range": (120, 180), "priority": 1, "dependencies": [f"b{batch}_f10"]}
        ])
    
    return config


def find_bottleneck():
    """Test each device to find the real bottleneck."""
    
    print("=" * 100)
    print("🔍 FINDING THE REAL BOTTLENECK")
    print("=" * 100)
    
    # Baseline
    print("\nRunning BASELINE (current capacities)...")
    baseline_config = create_config()
    baseline_engine = SimulationEngine(baseline_config)
    baseline_result = baseline_engine.run()
    baseline_flows = baseline_result['summary']['total_flows_completed']
    baseline_time = baseline_result['summary']['simulation_time_seconds']
    
    print(f"✓ Baseline: {baseline_flows} flows in {baseline_time/3600:.2f} hours\n")
    
    # Test each device
    devices_to_test = [
        ("centrifuge", 2, 4),
        ("platelet_separator", 2, 4),
        ("quality_check", 1, 3),  # Current=1, test with 3
        ("final_inspection", 1, 3),  # Current=1, test with 3
        ("pooling_station", 3, 6)
    ]
    
    results = []
    
    print("Testing devices (doubling/tripling capacity):")
    print("-" * 100)
    print(f"{'Device':<25} {'Change':<12} {'Flows':<12} {'Time (hrs)':<12} {'Improvement':<15}")
    print("-" * 100)
    
    for device, current, new in devices_to_test:
        config = create_config({device: new})
        engine = SimulationEngine(config)
        result = engine.run()
        
        flows = result['summary']['total_flows_completed']
        time_hrs = result['summary']['simulation_time_seconds'] / 3600
        flow_gain = ((flows - baseline_flows) / baseline_flows * 100) if baseline_flows > 0 else 0
        time_gain = ((baseline_time - result['summary']['simulation_time_seconds']) / baseline_time * 100) if baseline_time > 0 else 0
        
        results.append({
            'device': device,
            'current': current,
            'new': new,
            'flows': flows,
            'time': time_hrs,
            'flow_gain': flow_gain,
            'time_gain': time_gain
        })
        
        print(f"{device:<25} {current}→{new:<9} {flows:<12,} {time_hrs:<12.2f} {flow_gain:>6.1f}% / {time_gain:>5.1f}%")
    
    # Sort by flow gain
    results.sort(key=lambda x: x['flow_gain'], reverse=True)
    
    print("\n" + "=" * 100)
    print("🎯 BOTTLENECK RANKING (by throughput impact)")
    print("=" * 100)
    
    for i, r in enumerate(results, 1):
        emoji = "🔴" if i == 1 else "🟡" if i == 2 else "🟢"
        print(f"{i}. {emoji} {r['device']:<25} +{r['flow_gain']:>5.1f}% throughput  ({r['current']}→{r['new']})")
    
    top = results[0]
    print(f"\n💡 PRIMARY BOTTLENECK: {top['device'].upper()}")
    print(f"   Current capacity: {top['current']}")
    print(f"   Tested with: {top['new']}")
    print(f"   Throughput gain: +{top['flow_gain']:.1f}%")
    print(f"   Time improvement: {top['time_gain']:.1f}% faster")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    find_bottleneck()
