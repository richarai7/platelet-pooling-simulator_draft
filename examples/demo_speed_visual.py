"""
VISUAL SPEED MULTIPLIER DEMO
Shows how speed multiplier works with visible delays
"""
import requests
import json
import time
from datetime import datetime

def run_with_progress(config, label, speed_mult=None):
    """Run simulation and show progress."""
    print(f"\n{label}")
    print("-"*70)
    
    # Update config
    test_config = json.loads(json.dumps(config))
    if speed_mult is not None:
        test_config['simulation']['speed_multiplier'] = speed_mult
    else:
        test_config['simulation'].pop('speed_multiplier', None)
    
    # Shorter simulation for demo
    test_config['simulation']['duration'] = 1000  # Just 1000 seconds
    
    print(f"Starting at: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    real_start = time.time()
    response = requests.post("http://localhost:8000/simulations/run", json={"config": test_config})
    real_end = time.time()
    
    print(f"Finished at: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    result = response.json()
    sim_time = result['results']['summary']['simulation_time_seconds']
    real_time = real_end - real_start
    
    print(f"\n  Simulation Time: {sim_time:.1f} seconds")
    print(f"  Real Wall Time:  {real_time:.3f} seconds")
    
    if speed_mult and speed_mult > 0:
        expected = sim_time / speed_mult
        print(f"  Expected Time:   {expected:.3f} seconds (at {speed_mult}x speed)")
    
    return sim_time, real_time


print("="*70)
print("SPEED MULTIPLIER VISUAL DEMONSTRATION")
print("="*70)
print("\nThis shows how speed_multiplier controls simulation pacing.")
print("We'll run a SHORT simulation (1000 sec duration) at different speeds.")
print("="*70)

# Get simple config
response = requests.get("http://localhost:8000/templates/platelet-pooling")
config = response.json()

# Run at different speeds
results = []

# MAX SPEED (instant)
sim, real = run_with_progress(config, "🚀 MAX SPEED (no speed_multiplier)")
results.append(("Max Speed", sim, real, "Instant"))

# 10x SPEED
sim, real = run_with_progress(config, "⚡ 10x ACCELERATED (speed_multiplier: 10)", 10.0)
results.append(("10x Speed", sim, real, f"{sim/10:.1f}s expected"))

# 1x SPEED (real-time)
print("\n⏱️  REAL-TIME (speed_multiplier: 1) - This will take longer!")
print("   (Simulating ~3-5 minutes of process time...)")
sim, real = run_with_progress(config, "⏱️  REAL-TIME (1x)", 1.0)
results.append(("Real-Time", sim, real, f"{sim:.1f}s expected"))

# Summary
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)
print(f"\n{'Mode':<20} {'Sim Time':<15} {'Real Time':<15} {'Notes'}")
print("-"*70)
for mode, sim_t, real_t, note in results:
    print(f"{mode:<20} {sim_t:>10.1f}s   {real_t:>10.3f}s   {note}")

print("\n" + "="*70)
print("HOW TO USE IN YOUR CONFIG:")
print("="*70)
print("""
Add "speed_multiplier" to your simulation config:

{
  "simulation": {
    "duration": 43200,
    "random_seed": 42,
    "execution_mode": "accelerated",
    "speed_multiplier": 10.0     ← Add this line
  },
  ...
}

Values:
  • Omit field: Maximum CPU speed (instant results)
  • 100.0: Run 100x faster than real-time
  • 10.0:  Run 10x faster than real-time  
  • 1.0:   Real-time (for live visualization)

Perfect for:
  ✓ Live dashboards (10x or 100x)
  ✓ Manager demos (watch it run at visible speed)
  ✓ Real-time monitoring (1x with live metrics)
  ✓ Quick testing (max speed)
""")
print("="*70)
