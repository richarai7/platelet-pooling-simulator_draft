"""
Debug version of quick start to see what's happening
"""

from pathlib import Path
import sys
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from simulation_engine import SimulationEngine


def main():
    """Run a minimal simulation with debug logging."""
    
    print("=" * 60)
    print("DEBUG SIMULATION")
    print("=" * 60)
    
    # Minimal configuration - NO FLOWS to start
    config = {
        "simulation": {
            "duration": 100,  # Just 100 seconds
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "devices": [
            {
                "id": "machine_a",
                "type": "machine",
                "capacity": 1,
                "recovery_time_range": None  # No recovery time
            }
        ],
        "flows": [
            {
                "flow_id": "test_flow",
                "from_device": "machine_a",
                "to_device": "machine_a",
                "process_time_range": (10, 20),
                "priority": 1,
                "dependencies": None
            }
        ],  # ONE SIMPLE FLOW
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
    
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
