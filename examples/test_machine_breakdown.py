"""
PRACTICAL FAILURE TEST: What if one machine breaks down?
Compares normal operation vs "one machine down" scenarios
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(centrifuge_capacity, separator_capacity, quality_capacity):
    """Create simple platelet config."""
    
    config = {
        "simulation": {
            "duration": 100000,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": True
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": (1, 2)},
            {"id": "separator", "type": "machine", "capacity": separator_capacity,
             "recovery_time_range": (1, 2)},
            {"id": "quality", "type": "machine", "capacity": quality_capacity,
             "recovery_time_range": (1, 2)}
        ],
        "flows": []
    }
    
    # 5 batches
    for batch in range(1, 6):
        config["flows"].extend([
            {"flow_id": f"batch{batch}_centrifuge",
             "from_device": "centrifuge", "to_device": "separator",
             "process_time_range": (300, 480), "priority": 1, "dependencies": None},
            {"flow_id": f"batch{batch}_separator",
             "from_device": "separator", "to_device": "quality",
             "process_time_range": (600, 900), "priority": 1,
             "dependencies": [f"batch{batch}_centrifuge"]},
            {"flow_id": f"batch{batch}_quality",
             "from_device": "quality", "to_device": "quality",
             "process_time_range": (180, 300), "priority": 1,
             "dependencies": [f"batch{batch}_separator"]}
        ])
    
    return config


def main():
    print("\n" + "=" * 90)
    print("  MACHINE BREAKDOWN SCENARIOS: What if a machine fails?")
    print("=" * 90)
    print("\nSimulating: One machine breaks and stays down")
    print("Question: How much does it hurt throughput?\n")
    
    # BASELINE: All machines working
    print(f"{'─'*90}")
    print(" 🟢 BASELINE: All machines working normally")
    print(f"{'─'*90}")
    config = create_config(centrifuge_capacity=2, separator_capacity=2, quality_capacity=1)
    engine = SimulationEngine(config)
    result = engine.run()
    baseline_time = result['summary']['simulation_time_seconds'] / 60
    flows = len([f for f in result.get('flows_executed', []) if f['execution_count'] > 0])
    print(f" Centrifuges: 2 ✓  |  Separators: 2 ✓  |  Quality: 1 ✓")
    print(f" Time: {baseline_time:.1f} minutes  |  Batches: {flows//3}/5")
    
    # SCENARIO 1: One centrifuge down
    print(f"\n{'─'*90}")
    print(" 🔴 SCENARIO 1: One centrifuge breaks (2→1)")
    print(f"{'─'*90}")
    config = create_config(centrifuge_capacity=1, separator_capacity=2, quality_capacity=1)
    engine = SimulationEngine(config)
    result = engine.run()
    s1_time = result['summary']['simulation_time_seconds'] / 60
    flows = len([f for f in result.get('flows_executed', []) if f['execution_count'] > 0])
    print(f" Centrifuges: 1 ❌ (one down)  |  Separators: 2 ✓  |  Quality: 1 ✓")
    print(f" Time: {s1_time:.1f} minutes  |  Batches: {flows//3}/5")
    print(f" Impact: +{s1_time - baseline_time:.1f} min delay ({((s1_time/baseline_time - 1)*100):.1f}% slower)")
    
    # SCENARIO 2: One separator down
    print(f"\n{'─'*90}")
    print(" 🔴 SCENARIO 2: One separator breaks (2→1)")
    print(f"{'─'*90}")
    config = create_config(centrifuge_capacity=2, separator_capacity=1, quality_capacity=1)
    engine = SimulationEngine(config)
    result = engine.run()
    s2_time = result['summary']['simulation_time_seconds'] / 60
    flows = len([f for f in result.get('flows_executed', []) if f['execution_count'] > 0])
    print(f" Centrifuges: 2 ✓  |  Separators: 1 ❌ (one down)  |  Quality: 1 ✓")
    print(f" Time: {s2_time:.1f} minutes  |  Batches: {flows//3}/5")
    print(f" Impact: +{s2_time - baseline_time:.1f} min delay ({((s2_time/baseline_time - 1)*100):.1f}% slower)")
    
    # SCENARIO 3: Quality check machine down (only have 1, so this is critical!)
    print(f"\n{'─'*90}")
    print(" 🔴 SCENARIO 3: Quality check has NO backup (already at 1)")
    print(f"{'─'*90}")
    print(f" Centrifuges: 2 ✓  |  Separators: 2 ✓  |  Quality: 1 ⚠️  (no backup!)")
    print(f" If this machine fails → ENTIRE PROCESS STOPS")
    print(f" This is your CRITICAL SINGLE POINT OF FAILURE!")
    
    # COMPARISON
    print("\n" + "=" * 90)
    print("  📊 COMPARISON: Which failure hurts most?")
    print("=" * 90)
    
    print(f"\n{'Scenario':<40} {'Time (min)':<15} {'Extra Delay':<20}")
    print("-" * 90)
    print(f"{'Baseline (all working)':<40} {baseline_time:<15.1f} {'-':<20}")
    print(f"{'Centrifuge failure (2→1)':<40} {s1_time:<15.1f} {f'+{s1_time - baseline_time:.1f} min':<20}")
    print(f"{'Separator failure (2→1)':<40} {s2_time:<15.1f} {f'+{s2_time - baseline_time:.1f} min':<20}")
    
    # RECOMMENDATION
    print("\n" + "=" * 90)
    print("  💡 RECOMMENDATIONS")
    print("=" * 90)
    
    print(f"\n  1️⃣  CRITICAL: Add backup quality check machine (capacity 1→2)")
    print(f"     Currently NO backup - single point of failure!")
    print(f"     If it breaks, everything stops.")
    
    worst_delay = max(s1_time - baseline_time, s2_time - baseline_time)
    
    if worst_delay > baseline_time * 0.2:
        print(f"\n  2️⃣  HIGH PRIORITY: Add redundancy to other machines")
        print(f"     Failures cause {worst_delay:.0f}+ minute delays")
        print(f"     Consider spare machines for quick replacement")
    
    print(f"\n  3️⃣  Preventive Maintenance Schedule:")
    print(f"     • Regular maintenance = Fewer unexpected failures")
    print(f"     • Schedule during low-volume periods")
    print(f"     • Keep spare parts on hand for quick repairs")
    
    print("\n" + "=" * 90 + "\n")


if __name__ == "__main__":
    main()
