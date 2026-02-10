"""
OPERATIONS MANAGER SCENARIO RUNNER
Simple tool to compare "what-if" scenarios for platelet pooling

NO device failures - just pure throughput comparison
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_platelet_config(centrifuge_capacity=2, separator_capacity=2, quality_capacity=1, num_batches=5):
    """
    Create platelet pooling configuration.
    
    Args:
        centrifuge_capacity: Number of centrifuge machines
        separator_capacity: Number of separator machines  
        quality_capacity: Number of quality check machines
        num_batches: Number of blood batches to process
    
    Returns:
        Configuration dictionary
    """
    
    config = {
        "simulation": {
            "duration": 100000,  # Long enough to complete
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": True
        },
        "devices": [
            # CENTRIFUGE: Spin blood to separate components
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": (1, 2)},  # Minimal failures for clean comparison
            
            # SEPARATOR: Extract platelets
            {"id": "separator", "type": "machine", "capacity": separator_capacity,
             "recovery_time_range": (1, 2)},
            
            # QUALITY: Final quality check
            {"id": "quality", "type": "machine", "capacity": quality_capacity,
             "recovery_time_range": (1, 2)}
        ],
        "flows": []
    }
    
    # Each batch goes through 3 steps
    for batch in range(1, num_batches + 1):
        config["flows"].extend([
            # Step 1: Centrifuge (5-8 min)
            {"flow_id": f"batch{batch}_centrifuge",
             "from_device": "centrifuge", "to_device": "separator",
             "process_time_range": (300, 480), "priority": 1,
             "dependencies": None},  # All batches start immediately
            
            # Step 2: Separator (10-15 min) 
            {"flow_id": f"batch{batch}_separator",
             "from_device": "separator", "to_device": "quality",
             "process_time_range": (600, 900), "priority": 1,
             "dependencies": [f"batch{batch}_centrifuge"]},
            
            # Step 3: Quality (3-5 min)
            {"flow_id": f"batch{batch}_quality",
             "from_device": "quality", "to_device": "quality",
             "process_time_range": (180, 300), "priority": 1,
             "dependencies": [f"batch{batch}_separator"]}
        ])
    
    return config


def run_scenario(scenario_name, **device_capacities):
    """Run a scenario and return results."""
    
    num_batches = 5
    config = create_platelet_config(num_batches=num_batches, **device_capacities)
    engine = SimulationEngine(config)
    result = engine.run()
    
    # Calculate metrics
    total_flows = num_batches * 3  # 3 steps per batch
    flows_completed = len([f for f in result.get('flows_executed', []) if f['execution_count'] > 0])
    completion_time_min = result['summary']['simulation_time_seconds'] / 60
    
    print(f"\n{scenario_name}:")
    print(f"  Centrifuges: {device_capacities.get('centrifuge_capacity', 2)}")
    print(f"  Separators:  {device_capacities.get('separator_capacity', 2)}")
    print(f"  Quality:     {device_capacities.get('quality_capacity', 1)}")
    print(f"  ─────────────────────────────")
    print(f"  Time to complete: {completion_time_min:.1f} minutes")
    print(f"  Batches processed: {flows_completed // 3}/{num_batches}")
    print(f"  Total flows: {flows_completed}/{total_flows}")
    
    return {
        'time': completion_time_min,
        'flows': flows_completed,
        'batches': flows_completed // 3
    }


def main():
    """Run comparison scenarios."""
    
    print("=" * 90)
    print("  OPERATIONS MANAGER: Platelet Pooling What-If Analysis")
    print("=" * 90)
    print("\nQuestion: Should we add 2 more centrifuge machines?")
    print("Each batch goes through: Centrifuge → Separator → Quality Check\n")
    
    # BASELINE: Current setup
    baseline = run_scenario(
        "🔵 BASELINE (Current Setup)",
        centrifuge_capacity=2,
        separator_capacity=2,
        quality_capacity=1
    )
    
    # SCENARIO 1: Add 2 centrifuges
    scenario1 = run_scenario(
        "🟢 SCENARIO 1: +2 Centrifuges (2→4)",
        centrifuge_capacity=4,
        separator_capacity=2,
        quality_capacity=1
    )
    
    # SCENARIO 2: Add 1 separator instead
    scenario2 = run_scenario(
        "🟡 SCENARIO 2: +1 Separator (2→3)",
        centrifuge_capacity=2,
        separator_capacity=3,
        quality_capacity=1
    )
    
    # SCENARIO 3: Add 1 quality check instead
    scenario3 = run_scenario(
        "🟠 SCENARIO 3: +1 Quality Check (1→2)",
        centrifuge_capacity=2,
        separator_capacity=2,
        quality_capacity=2
    )
    
    # COMPARISON
    print("\n" + "=" * 90)
    print("  📊 IMPACT COMPARISON")
    print("=" * 90)
    
    scenarios = [
        ("Add 2 Centrifuges", scenario1),
        ("Add 1 Separator", scenario2),
        ("Add 1 Quality Check", scenario3)
    ]
    
    print(f"\n{'Scenario':<25} {'Time (min)':<15} {'Time Saved':<15} {'Improvement':<15}")
    print("-" * 90)
    print(f"{'BASELINE':<25} {baseline['time']:<15.1f} {'-':<15} {'-':<15}")
    
    for name, result in scenarios:
        time_saved = baseline['time'] - result['time']
        improvement = (time_saved / baseline['time'] * 100) if baseline['time'] > 0 else 0
        print(f"{name:<25} {result['time']:<15.1f} {time_saved:<15.1f} {improvement:<14.1f}%")
    
    # RECOMMENDATION
    print("\n" + "=" * 90)
    print("  🎯 RECOMMENDATION")
    print("=" * 90)
    
    best = max(scenarios, key=lambda x: (baseline['time'] - x[1]['time']) / baseline['time'])
    best_improvement = ((baseline['time'] - best[1]['time']) / baseline['time'] * 100)
    
    print(f"\n  Best option: {best[0]}")
    print(f"  Improvement: {best_improvement:.1f}% faster")
    print(f"  Time saved: {baseline['time'] - best[1]['time']:.1f} minutes per 5 batches")
    
    if best_improvement > 15:
        print(f"\n  ✅ STRONG RECOMMENDATION: Implement this change")
        print(f"     Significant throughput improvement!")
    elif best_improvement > 5:
        print(f"\n  ⚠️  MODERATE RECOMMENDATION: Worth considering")
        print(f"     Decent improvement, analyze cost/benefit")
    else:
        print(f"\n  ❌ NOT RECOMMENDED: Minimal impact")
        print(f"     Only {best_improvement:.1f}% faster - not worth the investment")
        print(f"     System appears well-balanced already")
    
    print("\n" + "=" * 90 + "\n")


if __name__ == "__main__":
    main()
