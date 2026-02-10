"""
DEVICE FAILURE IMPACT ANALYSIS
Shows what happens when devices fail and how long recovery takes
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config_with_failures(centrifuge_capacity=2, failure_rate="none"):
    """
    Create config with different failure scenarios.
    
    Args:
        centrifuge_capacity: Number of centrifuge machines
        failure_rate: "none", "low", "medium", "high"
    """
    
    # Set recovery times based on failure rate
    if failure_rate == "none":
        recovery = (1, 2)  # Minimal (essentially no failures)
    elif failure_rate == "low":
        recovery = (60, 120)  # 1-2 minutes to fix
    elif failure_rate == "medium":
        recovery = (180, 300)  # 3-5 minutes to fix
    else:  # high
        recovery = (300, 600)  # 5-10 minutes to fix
    
    config = {
        "simulation": {
            "duration": 100000,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": True,  # Track all state changes
            "include_flow_details": True
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": recovery},
            {"id": "separator", "type": "machine", "capacity": 2,
             "recovery_time_range": recovery},
            {"id": "quality", "type": "machine", "capacity": 1,
             "recovery_time_range": recovery}
        ],
        "flows": []
    }
    
    # 5 batches through the process
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


def analyze_failures():
    """Compare scenarios with different failure rates."""
    
    print("\n" + "=" * 90)
    print("  DEVICE FAILURE IMPACT ANALYSIS")
    print("=" * 90)
    print("\nSimulating 5 blood batches with different failure rates...")
    print("All scenarios: 2 centrifuges, 2 separators, 1 quality check\n")
    
    results = {}
    
    scenarios = [
        ("No Failures (Perfect Conditions)", "none"),
        ("Low Failures (1-2 min recovery)", "low"),
        ("Medium Failures (3-5 min recovery)", "medium"),
        ("High Failures (5-10 min recovery)", "high")
    ]
    
    for scenario_name, failure_rate in scenarios:
        print(f"{'─'*90}")
        print(f" {scenario_name}")
        print(f"{'─'*90}")
        
        config = create_config_with_failures(centrifuge_capacity=2, failure_rate=failure_rate)
        engine = SimulationEngine(config)
        result = engine.run()
        
        # Analyze state history for failures
        failures = {}
        if 'state_history' in result:
            for event in result['state_history']:
                device = event['device_id']
                if event['to_state'] == 'Failed':
                    failures[device] = failures.get(device, 0) + 1
        
        time_min = result['summary']['simulation_time_seconds'] / 60
        flows_completed = len([f for f in result.get('flows_executed', []) if f['execution_count'] > 0])
        
        results[failure_rate] = {
            'time': time_min,
            'flows': flows_completed,
            'failures': failures
        }
        
        print(f" ✓ Time to complete: {time_min:.1f} minutes")
        print(f" ✓ Batches processed: {flows_completed // 3}/5")
        print(f" ✓ Device failures:")
        if failures:
            for device, count in failures.items():
                print(f"    - {device}: {count} failures")
        else:
            print(f"    - No failures recorded")
        print()
    
    # COMPARISON
    print("=" * 90)
    print("  📊 IMPACT OF DEVICE FAILURES")
    print("=" * 90)
    
    baseline = results['none']
    
    print(f"\n{'Scenario':<35} {'Time (min)':<15} {'Extra Time':<15} {'Impact':<15}")
    print("-" * 90)
    print(f"{'Perfect (No Failures)':<35} {baseline['time']:<15.1f} {'-':<15} {'-':<15}")
    
    for name, rate in scenarios[1:]:
        extra_time = results[rate]['time'] - baseline['time']
        impact_pct = (extra_time / baseline['time'] * 100) if baseline['time'] > 0 else 0
        print(f"{name:<35} {results[rate]['time']:<15.1f} {extra_time:<15.1f} {impact_pct:<14.1f}%")
    
    # INSIGHTS
    print("\n" + "=" * 90)
    print("  💡 INSIGHTS")
    print("=" * 90)
    
    high_impact = results['high']
    extra_time = high_impact['time'] - baseline['time']
    
    print(f"\n  ⚠️  Device failures can significantly impact throughput!")
    print(f"  • Perfect conditions: {baseline['time']:.1f} minutes")
    print(f"  • With frequent failures: {high_impact['time']:.1f} minutes")
    print(f"  • Extra downtime: {extra_time:.1f} minutes ({(extra_time/baseline['time']*100):.1f}% slower)")
    
    print(f"\n  🔧 What this means:")
    print(f"  • Preventive maintenance is critical")
    print(f"  • Having backup machines helps (redundancy)")
    print(f"  • Fast repair response reduces impact")
    
    # WHAT-IF: Add redundancy
    print("\n" + "=" * 90)
    print("  🛡️  REDUNDANCY TEST: What if we add backup machines?")
    print("=" * 90)
    
    print(f"\n  Testing: Add 1 extra centrifuge as backup (2→3)")
    print(f"  Scenario: Medium failure rate (3-5 min recovery)\n")
    
    # Run with extra capacity
    config_backup = create_config_with_failures(centrifuge_capacity=3, failure_rate="medium")
    engine_backup = SimulationEngine(config_backup)
    result_backup = engine_backup.run()
    
    time_backup = result_backup['summary']['simulation_time_seconds'] / 60
    time_without_backup = results['medium']['time']
    improvement = ((time_without_backup - time_backup) / time_without_backup * 100)
    
    print(f"  • Without backup (2 centrifuges): {time_without_backup:.1f} minutes")
    print(f"  • With backup (3 centrifuges): {time_backup:.1f} minutes")
    print(f"  • Improvement: {improvement:.1f}% faster (more resilient to failures)")
    
    if improvement > 10:
        print(f"\n  ✅ Backup machines provide good protection against failures!")
    else:
        print(f"\n  ⚠️  Backup didn't help much - bottleneck is elsewhere")
    
    print("\n" + "=" * 90 + "\n")


if __name__ == "__main__":
    analyze_failures()
