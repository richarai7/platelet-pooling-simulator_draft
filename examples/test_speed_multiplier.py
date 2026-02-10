"""
TEST SPEED MULTIPLIER FEATURE
Demonstrates 1x, 10x, 100x, and max speed modes
"""
import requests
import json
import time

def test_speed_multiplier():
    print("="*70)
    print("SPEED MULTIPLIER TEST")
    print("="*70)
    
    # Get template
    response = requests.get("http://localhost:8000/templates/platelet-pooling")
    config = response.json()
    
    # Create a smaller test (just 3 batches for faster demo)
    from generate_multi_batch import generate_multi_batch_config
    test_config = generate_multi_batch_config(num_batches=3, batch_interval_seconds=300)
    
    # Test different speed multipliers
    speeds = [
        (None, "MAX SPEED (no waiting)"),
        (100.0, "100x ACCELERATED"),
        (10.0, "10x ACCELERATED"),
        (1.0, "REAL-TIME (1x)")
    ]
    
    print(f"\nTesting {len(speeds)} different speeds...")
    print("\nConfiguration: 3 batches × 11 steps = 33 flows")
    print("="*70)
    
    for multiplier, label in speeds:
        print(f"\n{label}")
        print("-"*70)
        
        # Update config
        test_run = json.loads(json.dumps(test_config))
        if multiplier is not None:
            test_run['simulation']['speed_multiplier'] = multiplier
        else:
            # Max speed - no multiplier field
            test_run['simulation'].pop('speed_multiplier', None)
        
        # Run and time it
        real_start = time.time()
        response = requests.post("http://localhost:8000/simulations/run", json={"config": test_run})
        real_end = time.time()
        
        result = response.json()
        sim_time = result['results']['summary']['simulation_time_seconds']
        real_time = real_end - real_start
        
        print(f"  Simulation Time: {sim_time:.1f} seconds ({sim_time/60:.1f} min)")
        print(f"  Real Wall Time:  {real_time:.2f} seconds")
        
        if multiplier and multiplier > 0:
            expected_real = sim_time / multiplier
            print(f"  Expected Real:   {expected_real:.2f} seconds (at {multiplier}x)")
        else:
            print(f"  Running at maximum CPU speed")
    
    print("\n" + "="*70)
    print("SPEED MULTIPLIER OPTIONS:")
    print("="*70)
    print()
    print("In your simulation config, add:")
    print('  "simulation": {')
    print('    "duration": 43200,')
    print('    "random_seed": 42,')
    print('    "execution_mode": "accelerated",')
    print('    "speed_multiplier": 10.0  ← ADD THIS')
    print('  }')
    print()
    print("Options:")
    print("  • No field or 0: Maximum speed (default)")
    print("  • 100.0: 100x faster than real-time")
    print("  • 10.0:  10x faster than real-time")
    print("  • 1.0:   Real-time speed (for visualization)")
    print()
    print("Use Cases:")
    print("  • Max speed: Quick what-if testing")
    print("  • 100x: Balanced (visible progress, still fast)")
    print("  • 10x: Watch simulation unfold at 10x speed")
    print("  • 1x: Real-time for live demos/visualization")
    print("="*70)

if __name__ == "__main__":
    test_speed_multiplier()
