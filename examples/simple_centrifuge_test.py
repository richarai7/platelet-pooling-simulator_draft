"""
SIMPLE WHAT-IF: Adding 2 More Centrifuges
Easy-to-understand comparison with just 5 batches
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_config(centrifuge_capacity):
    """Create simple config with 5 blood batches."""
    
    config = {
        "simulation": {
            "duration": 100000,  # Long enough to complete all batches
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": False,
            "include_flow_details": False
        },
        "devices": [
            # CENTRIFUGE - This is what we're testing!
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": (60, 120)},
            
            # Other devices in the platelet pooling process
            {"id": "separator", "type": "machine", "capacity": 3,
             "recovery_time_range": (50, 100)},
            {"id": "pooling", "type": "workstation", "capacity": 4,
             "recovery_time_range": (40, 80)},
            {"id": "quality_check", "type": "machine", "capacity": 3,
             "recovery_time_range": (30, 60)},
            {"id": "packaging", "type": "workstation", "capacity": 4,
             "recovery_time_range": (20, 40)}
        ],
        "flows": []
    }
    
    # Create 5 blood batches that all START at same time (parallel processing)
    for batch in range(1, 6):
        config["flows"].extend([
            # Step 1: Centrifuge (BOTTLENECK TEST)
            {"flow_id": f"batch{batch}_step1_centrifuge",
             "from_device": "centrifuge", "to_device": "separator",
             "process_time_range": (300, 400), "priority": 1,
             "dependencies": None},  # All start at T=0
            
            # Step 2: Separator
            {"flow_id": f"batch{batch}_step2_separator",
             "from_device": "separator", "to_device": "pooling",
             "process_time_range": (200, 300), "priority": 1,
             "dependencies": [f"batch{batch}_step1_centrifuge"]},
            
            # Step 3: Pooling
            {"flow_id": f"batch{batch}_step3_pooling",
             "from_device": "pooling", "to_device": "quality_check",
             "process_time_range": (150, 250), "priority": 1,
             "dependencies": [f"batch{batch}_step2_separator"]},
            
            # Step 4: Quality Check
            {"flow_id": f"batch{batch}_step4_quality",
             "from_device": "quality_check", "to_device": "packaging",
             "process_time_range": (100, 200), "priority": 1,
             "dependencies": [f"batch{batch}_step3_pooling"]},
            
            # Step 5: Packaging (final)
            {"flow_id": f"batch{batch}_step5_packaging",
             "from_device": "packaging", "to_device": "packaging",
             "process_time_range": (80, 120), "priority": 1,
             "dependencies": [f"batch{batch}_step4_quality"]}
        ])
    
    return config


def main():
    """Run comparison: 2 centrifuges vs 4 centrifuges."""
    
    print("\n" + "=" * 90)
    print("  PLATELET POOLING: What if we add 2 more CENTRIFUGE machines?")
    print("=" * 90)
    print("\nProcessing 5 blood donation batches...")
    print("All batches arrive at the same time (parallel processing)\n")
    
    results = {}
    
    # Run both scenarios
    for capacity in [2, 4]:
        scenario_name = "BASELINE" if capacity == 2 else "WHAT-IF"
        machines_desc = f"{capacity} centrifuges" + (" (current)" if capacity == 2 else " (+2 NEW)")
        
        print(f"{'─'*90}")
        print(f" {scenario_name}: {machines_desc}")
        print(f"{'─'*90}")
        
        config = create_config(capacity)
        engine = SimulationEngine(config)
        result = engine.run()
        
        results[capacity] = result
        
        # Calculate metrics
        total_time_sec = result['summary']['simulation_time_seconds']
        total_time_min = total_time_sec / 60
        flows_completed = result['summary']['total_flows_completed']
        batches_completed = flows_completed / 5  # 5 flows per batch
        
        print(f" ✓ Total time to complete: {total_time_min:.1f} minutes ({total_time_sec:.0f}s)")
        print(f" ✓ Batches completed: {batches_completed:.0f}/5")
        print(f" ✓ Total flows: {flows_completed}/25")
        print()
    
    # COMPARISON
    print("=" * 90)
    print("  📊 COMPARISON: What's the IMPACT of adding 2 more centrifuges?")
    print("=" * 90)
    
    baseline_time = results[2]['summary']['simulation_time_seconds'] / 60
    whatif_time = results[4]['summary']['simulation_time_seconds'] / 60
    time_saved = baseline_time - whatif_time
    pct_faster = (time_saved / baseline_time * 100) if baseline_time > 0 else 0
    
    baseline_flows = results[2]['summary']['total_flows_completed']
    whatif_flows = results[4]['summary']['total_flows_completed']
    
    print(f"\n⏱️  PROCESSING TIME:")
    print(f"   Current (2 centrifuges):  {baseline_time:.1f} minutes")
    print(f"   With +2 centrifuges:      {whatif_time:.1f} minutes")
    print(f"   ─────────────────────────────────────")
    print(f"   Time saved:               {time_saved:.1f} minutes")
    print(f"   Speed improvement:        {pct_faster:.1f}% FASTER")
    
    print(f"\n📦 THROUGHPUT:")
    print(f"   Current:   {baseline_flows}/25 flows completed")
    print(f"   With +2:   {whatif_flows}/25 flows completed")
    print(f"   Increase:  +{whatif_flows - baseline_flows} flows")
    
    # DECISION
    print(f"\n{'='*90}")
    print("  💡 DECISION: Should you add 2 more centrifuges?")
    print(f"{'='*90}\n")
    
    if pct_faster > 20:
        print(f"  ✅ YES - STRONG RECOMMENDATION")
        print(f"     {pct_faster:.1f}% faster! Centrifuge is clearly a bottleneck.")
        print(f"     You'll process {time_saved:.1f} minutes faster per 5 batches.")
    elif pct_faster > 10:
        print(f"  ⚠️  MAYBE - MODERATE IMPACT")
        print(f"     {pct_faster:.1f}% improvement. Could be worthwhile depending on cost.")
    elif pct_faster > 2:
        print(f"  ⚠️  PROBABLY NOT - SMALL IMPACT")
        print(f"     Only {pct_faster:.1f}% faster. Consider other improvements first.")
    else:
        print(f"  ❌ NO - DON'T DO IT")
        print(f"     Only {pct_faster:.1f}% faster! Centrifuge is NOT your bottleneck.")
        print(f"     Your money would be better spent elsewhere.")
        print(f"\n     💡 TIP: Run 'find_real_bottleneck.py' to see what IS the bottleneck.")
    
    print(f"\n{'='*90}\n")


if __name__ == "__main__":
    main()
