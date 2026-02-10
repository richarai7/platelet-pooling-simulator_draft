"""
Debug script to understand what's happening in the simulation
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def create_simple_config(centrifuge_capacity):
    """Very simple: 3 batches, 3 steps each."""
    
    config = {
        "simulation": {
            "duration": 10000,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": True,
            "include_flow_details": True
        },
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge_capacity,
             "recovery_time_range": (10, 20)},
            {"id": "separator", "type": "machine", "capacity": 2,
             "recovery_time_range": (10, 20)},
            {"id": "quality", "type": "machine", "capacity": 2,
             "recovery_time_range": (10, 20)}
        ],
        "flows": []
    }
    
    # Just 3 batches, 3 steps each = 9 total flows
    for batch in range(1, 4):  # Batches 1, 2, 3
        config["flows"].extend([
            {"flow_id": f"b{batch}_step1",
             "from_device": "centrifuge", "to_device": "separator",
             "process_time_range": (100, 150), "priority": 1,
             "dependencies": None},  # All start at T=0
            
            {"flow_id": f"b{batch}_step2",
             "from_device": "separator", "to_device": "quality",
             "process_time_range": (100, 150), "priority": 1,
             "dependencies": [f"b{batch}_step1"]},
            
            {"flow_id": f"b{batch}_step3",
             "from_device": "quality", "to_device": "quality",
             "process_time_range": (100, 150), "priority": 1,
             "dependencies": [f"b{batch}_step2"]}
        ])
    
    return config


def debug():
    """Run and show what's actually happening."""
    
    print("\n" + "="*80)
    print("DEBUGGING: 3 Batches, 3 Steps Each (9 total flows)")
    print("="*80)
    
    for capacity in [1, 2]:
        print(f"\n{'─'*80}")
        print(f"Centrifuge Capacity: {capacity}")
        print(f"{'─'*80}")
        
        config = create_simple_config(capacity)
        engine = SimulationEngine(config)
        result = engine.run()
        
        print(f"\nRESULTS:")
        print(f"  Total flows expected: 9 (3 batches × 3 steps)")
        print(f"  Flows completed: {result['summary']['total_flows_completed']}")
        print(f"  Total time: {result['summary']['simulation_time_seconds']:.1f}s")
        print(f"  Total events: {result['summary']['total_events']}")
        
        # Show flow details
        if 'flow_details' in result:
            print(f"\n  Flow execution details:")
            completed = [f for f in result['flow_details'] if f.get('end_time') is not None]
            print(f"    Completed flows: {len(completed)}/9")
            
            # Group by batch
            for batch in range(1, 4):
                batch_flows = [f for f in completed if f['flow_id'].startswith(f'b{batch}_')]
                print(f"    Batch {batch}: {len(batch_flows)}/3 steps completed")
        
        # Show device final states
        print(f"\n  Device states:")
        for device in result['device_states']:
            print(f"    {device['device_id']}: {device['final_state']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    debug()
