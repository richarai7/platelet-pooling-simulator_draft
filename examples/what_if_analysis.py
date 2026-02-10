"""
What-If Analysis Framework
Demonstrates how to test different scenarios and measure their impacts
"""

from pathlib import Path
import sys
import json
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def base_config() -> Dict[str, Any]:
    """Create base configuration."""
    return {
        "simulation": {
            "duration": 43200,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": 2, "recovery_time_range": (180, 300)},
            {"id": "platelet_separator", "type": "machine", "capacity": 1, "recovery_time_range": (120, 180)},
            {"id": "pooling_station", "type": "workstation", "capacity": 3, "recovery_time_range": (60, 120)},
            {"id": "weigh_register", "type": "machine", "capacity": 2, "recovery_time_range": (30, 60)},
            {"id": "sterile_connect", "type": "workstation", "capacity": 2, "recovery_time_range": (45, 90)},
            {"id": "test_sample", "type": "machine", "capacity": 2, "recovery_time_range": (60, 90)},
            {"id": "quality_check", "type": "machine", "capacity": 1, "recovery_time_range": (30, 60)},
            {"id": "label_station", "type": "workstation", "capacity": 2, "recovery_time_range": (20, 40)},
            {"id": "storage_unit", "type": "material", "capacity": 50, "recovery_time_range": (10, 20)},
            {"id": "final_inspection", "type": "machine", "capacity": 1, "recovery_time_range": (45, 75)},
            {"id": "packaging_station", "type": "workstation", "capacity": 2, "recovery_time_range": (30, 60)}
        ],
        "flows": [
            {"flow_id": "f1", "from_device": "centrifuge", "to_device": "platelet_separator", 
             "process_time_range": (300, 480), "priority": 1, "dependencies": None},
            {"flow_id": "f2", "from_device": "platelet_separator", "to_device": "pooling_station", 
             "process_time_range": (600, 900), "priority": 1, "dependencies": ["f1"]},
            {"flow_id": "f3", "from_device": "pooling_station", "to_device": "weigh_register", 
             "process_time_range": (420, 600), "priority": 1, "dependencies": ["f2"]},
            {"flow_id": "f4", "from_device": "weigh_register", "to_device": "sterile_connect", 
             "process_time_range": (240, 360), "priority": 1, "dependencies": ["f3"]},
            {"flow_id": "f5", "from_device": "sterile_connect", "to_device": "test_sample", 
             "process_time_range": (180, 300), "priority": 1, "dependencies": ["f4"]},
            {"flow_id": "f6", "from_device": "test_sample", "to_device": "quality_check", 
             "process_time_range": (360, 600), "priority": 1, "dependencies": ["f5"]},
            {"flow_id": "f7", "from_device": "quality_check", "to_device": "label_station", 
             "process_time_range": (120, 240), "priority": 1, "dependencies": ["f6"], "required_gates": ["QC_Pass"]},
            {"flow_id": "f8", "from_device": "label_station", "to_device": "storage_unit", 
             "process_time_range": (60, 120), "priority": 1, "dependencies": ["f7"]},
            {"flow_id": "f9", "from_device": "storage_unit", "to_device": "final_inspection", 
             "process_time_range": (180, 300), "priority": 1, "dependencies": ["f8"]},
            {"flow_id": "f10", "from_device": "final_inspection", "to_device": "packaging_station", 
             "process_time_range": (240, 360), "priority": 1, "dependencies": ["f9"]},
        ],
        "gates": {"QC_Pass": True, "Sterile_Conditions": True, "Temperature_Control": True},
        "output_options": {"include_events": True, "include_history": True}
    }


def run_scenario(name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Run a simulation scenario and return results."""
    print(f"\n{'='*80}")
    print(f"Scenario: {name}")
    print(f"{'='*80}")
    
    engine = SimulationEngine(config)
    result = engine.run()
    
    summary = result['summary']
    print(f"✓ Events: {summary['total_events']:,} | Flows: {summary['total_flows_completed']} | "
          f"Time: {summary['simulation_time_seconds']:.1f}s ({summary['simulation_time_seconds']/3600:.2f}h)")
    
    return result


def what_if_analysis():
    """Run comprehensive what-if analysis."""
    print("=" * 80)
    print("WHAT-IF ANALYSIS FRAMEWORK")
    print("=" * 80)
    
    scenarios = {}
    
    # ===== SCENARIO 1: BASELINE =====
    config1 = base_config()
    scenarios["1. Baseline"] = run_scenario("1. Baseline (Single Batch)", config1)
    
    # ===== SCENARIO 2: MULTIPLE BATCHES (creates actual bottleneck) =====
    config2 = base_config()
    # Duplicate flows to simulate 5 batches running through the system
    config2["flows"] = []
    for batch in range(1, 6):
        for i in range(1, 11):
            flow = {
                "flow_id": f"batch{batch}_f{i}",
                "from_device": config1["flows"][i-1]["from_device"],
                "to_device": config1["flows"][i-1]["to_device"],
                "process_time_range": config1["flows"][i-1]["process_time_range"],
                "priority": batch,
                "dependencies": [f"batch{batch}_f{i-1}"] if i > 1 else None,
                "required_gates": config1["flows"][i-1].get("required_gates", [])
            }
            config2["flows"].append(flow)
    
    scenarios["2. Multiple Batches (5x)"] = run_scenario("2. Five Batches Competing for Resources", config2)
    
    # ===== SCENARIO 3: INCREASED BOTTLENECK CAPACITY =====
    config3 = base_config()
    config3["flows"] = config2["flows"].copy()  # Same 5 batches
    # Increase capacity of single-capacity devices
    for device in config3["devices"]:
        if device["id"] in ["platelet_separator", "quality_check", "final_inspection"]:
            device["capacity"] = 3  # Triple capacity
    
    scenarios["3. High Capacity (5 batches)"] = run_scenario("3. Five Batches + 3x Capacity on Bottlenecks", config3)
    
    # ===== SCENARIO 4: QUALITY GATE CLOSED =====
    config4 = base_config()
    config4["gates"]["QC_Pass"] = False  # Gate closed - f7 will be blocked
    scenarios["4. QC Gate Closed"] = run_scenario("4. Quality Gate CLOSED (blocks f7→f10)", config4)
    
    # ===== SCENARIO 5: FASTER PROCESSING =====
    config5 = base_config()
    # Reduce all process times by 50%
    for flow in config5["flows"]:
        old_min, old_max = flow["process_time_range"]
        flow["process_time_range"] = (old_min // 2, old_max // 2)
    
    scenarios["5. 50% Faster Processing"] = run_scenario("5. All Process Times Reduced by 50%", config5)
    
    # ===== SCENARIO 6: SLOWER RECOVERY TIMES =====
    config6 = base_config()
    # Double all device recovery times
    for device in config6["devices"]:
        if device["recovery_time_range"]:
            old_min, old_max = device["recovery_time_range"]
            device["recovery_time_range"] = (old_min * 2, old_max * 2)
    
    scenarios["6. 2x Slower Recovery"] = run_scenario("6. Device Recovery Times Doubled", config6)
    
    # ===== SCENARIO 7: REMOVE DEPENDENCIES (parallel) =====
    config7 = base_config()
    # Remove all dependencies - everything runs in parallel
    for flow in config7["flows"]:
        flow["dependencies"] = None
    
    scenarios["7. No Dependencies"] = run_scenario("7. All Flows Run in Parallel (no dependencies)", config7)
    
    # ===== SCENARIO 8: LIMITED STORAGE =====
    config8 = base_config()
    # Reduce storage capacity dramatically
    for device in config8["devices"]:
        if device["id"] == "storage_unit":
            device["capacity"] = 1  # Only 1 unit at a time
    
    scenarios["8. Limited Storage"] = run_scenario("8. Storage Unit Capacity = 1 (bottleneck)", config8)
    
    # ===== COMPARISON TABLE =====
    print("\n" + "=" * 80)
    print("WHAT-IF COMPARISON TABLE")
    print("=" * 80)
    
    baseline_time = scenarios["1. Baseline"]['summary']['simulation_time_seconds']
    
    print(f"\n{'Scenario':<40} {'Time (s)':<12} {'Time (h)':<10} {'Events':<10} {'vs Baseline':<12}")
    print("-" * 80)
    
    for name, result in scenarios.items():
        sim_time = result['summary']['simulation_time_seconds']
        hours = sim_time / 3600
        events = result['summary']['total_events']
        diff = ((sim_time - baseline_time) / baseline_time * 100)
        
        print(f"{name:<40} {sim_time:<12.1f} {hours:<10.2f} {events:<10,} {diff:+.1f}%")
    
    # ===== KEY INSIGHTS =====
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    
    batch1_time = scenarios["1. Baseline"]['summary']['simulation_time_seconds']
    batch5_time = scenarios["2. Multiple Batches (5x)"]['summary']['simulation_time_seconds']
    batch5_highcap = scenarios["3. High Capacity (5 batches)"]['summary']['simulation_time_seconds']
    gate_closed = scenarios["4. QC Gate Closed"]['summary']['simulation_time_seconds']
    faster_proc = scenarios["5. 50% Faster Processing"]['summary']['simulation_time_seconds']
    no_deps = scenarios["7. No Dependencies"]['summary']['simulation_time_seconds']
    
    print(f"\n1️⃣  WORKLOAD IMPACT:")
    print(f"   • Single batch: {batch1_time:.1f}s")
    print(f"   • Five batches: {batch5_time:.1f}s ({batch5_time/batch1_time:.1f}x slower)")
    print(f"   💡 Multiple batches create resource contention = bottlenecks appear!")
    
    print(f"\n2️⃣  CAPACITY IMPROVEMENT:")
    print(f"   • 5 batches @ normal capacity: {batch5_time:.1f}s")
    print(f"   • 5 batches @ 3x capacity: {batch5_highcap:.1f}s")
    print(f"   • Time saved: {batch5_time - batch5_highcap:.1f}s ({(batch5_time-batch5_highcap)/batch5_time*100:.1f}%)")
    print(f"   💡 Increasing bottleneck capacity reduces completion time!")
    
    print(f"\n3️⃣  GATE CONTROL IMPACT:")
    print(f"   • Gate open: {batch1_time:.1f}s")
    print(f"   • Gate closed: {gate_closed:.1f}s")
    if gate_closed > batch1_time * 1.1:
        print(f"   💡 Closing QC_Pass gate blocks downstream flows!")
    else:
        print(f"   💡 Gate has minimal impact (flows complete before reaching it)")
    
    print(f"\n4️⃣  PROCESS SPEED IMPACT:")
    print(f"   • Normal speed: {batch1_time:.1f}s")
    print(f"   • 50% faster: {faster_proc:.1f}s ({(batch1_time-faster_proc)/batch1_time*100:.1f}% improvement)")
    print(f"   💡 Faster processing = proportional time reduction!")
    
    print(f"\n5️⃣  DEPENDENCY IMPACT:")
    print(f"   • Sequential (with dependencies): {batch1_time:.1f}s")
    print(f"   • Parallel (no dependencies): {no_deps:.1f}s")
    print(f"   💡 Removing dependencies shows max parallelization benefit!")
    
    # ===== HOW TO USE =====
    print("\n" + "=" * 80)
    print("HOW TO CREATE YOUR OWN WHAT-IF SCENARIOS")
    print("=" * 80)
    
    print("""
📋 SCENARIO TYPES YOU CAN TEST:

1. WORKLOAD CHANGES:
   - Add more flow instances (batches)
   - Change priorities
   - Add new parallel flows
   
2. RESOURCE CHANGES:
   - Increase/decrease device capacities
   - Add/remove devices
   - Modify recovery times
   
3. PROCESS CHANGES:
   - Adjust process_time_range (faster/slower)
   - Change dependencies (sequential vs parallel)
   - Modify flow priorities
   
4. CONSTRAINT CHANGES:
   - Open/close gates (True/False)
   - Add required_gates to flows
   - Reduce storage capacity
   
5. OPERATIONAL CHANGES:
   - Different random seeds (variability)
   - Shorter/longer simulation duration
   - Real-time vs accelerated execution

💡 EXAMPLE USE CASES:

• "What if we add 10 more batches?" → Multiply flows
• "What if QC fails?" → Set QC_Pass gate = False
• "What if we buy 2 more machines?" → Increase capacity
• "What if process is 20% faster?" → Reduce process_time_range
• "What if storage breaks?" → Set storage capacity = 0 or very low
• "What if we remove dependencies?" → Set dependencies = None
• "What if we run 24/7 for a week?" → Increase duration to 604800s

📊 To create your own scenario:
   1. Copy base_config()
   2. Modify devices, flows, gates, or simulation params
   3. Run scenario and compare results
   4. Analyze time, events, and completion differences
""")
    
    # Save results
    with open("what_if_analysis_results.json", "w") as f:
        json.dump(scenarios, f, indent=2)
    
    print(f"\n💾 Full results saved to: what_if_analysis_results.json")
    print("=" * 80)


if __name__ == "__main__":
    what_if_analysis()
