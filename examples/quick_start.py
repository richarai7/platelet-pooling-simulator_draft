"""
Quick Start Example - Minimal Working Simulation
This is the simplest example to verify the simulation engine is working.
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


def main():
    """Run a minimal simulation to test the engine."""
    
    print("=" * 60)
    print("QUICK START SIMULATION")
    print("=" * 60)
    
    # Minimal configuration with capacity > 1
    config = {
        "simulation": {
            "duration": 1000,  # 1000 seconds
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {
                "id": "machine_a",
                "type": "machine",
                "capacity": 2,  # Increased capacity
                "recovery_time_range": None  # No recovery time for simplicity
            },
            {
                "id": "machine_b",
                "type": "machine",
                "capacity": 2,  # Increased capacity
                "recovery_time_range": None
            }
        ],
        "flows": [
            {
                "flow_id": "process_step",
                "from_device": "machine_a",
                "to_device": "machine_b",  # Different device
                "process_time_range": (50, 100),
                "priority": 1,
                "dependencies": None
            }
        ],
        "output_options": {
            "include_history": False,
            "include_events": False
        }
    }
    
    print(f"\n📋 Configuration:")
    print(f"   Duration: {config['simulation']['duration']} seconds")
    print(f"   Devices: {len(config['devices'])}")
    print(f"   Flows: {len(config['flows'])}")
    
    print(f"\n⚙️  Running simulation...")
    
    # Create and run simulation
    engine = SimulationEngine(config)
    results = engine.run()
    
    print(f"\n✅ Simulation Complete!")
    print(f"\n📊 Results:")
    print(f"   Total Events: {results['summary']['total_events']}")
    print(f"   Flows Completed: {results['summary']['total_flows_completed']}")
    print(f"   Simulation Time: {results['summary']['simulation_time_seconds']} seconds")
    print(f"   Execution Time: {results['summary']['execution_time_seconds']:.3f} seconds")
    
    print(f"\n✓ Success! The simulation engine is working correctly.")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
