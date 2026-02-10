"""Debug to see what's actually completing"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine


config = {
    "simulation": {"duration": 10000, "random_seed": 42, "execution_mode": "accelerated"},
    "output_options": {"include_history": False, "include_flow_details": True},
    "devices": [
        {"id": "centrifuge", "type": "machine", "capacity": 1, "recovery_time_range": (10, 20)},
        {"id": "separator", "type": "machine", "capacity": 2, "recovery_time_range": (10, 20)},
        {"id": "quality", "type": "machine", "capacity": 2, "recovery_time_range": (10, 20)}
    ],
    "flows": [
        {"flow_id": "b1_step1", "from_device": "centrifuge", "to_device": "separator",
         "process_time_range": (100, 150), "priority": 1, "dependencies": None},
        {"flow_id": "b1_step2", "from_device": "separator", "to_device": "quality",
         "process_time_range": (100, 150), "priority": 1, "dependencies": ["b1_step1"]},
        {"flow_id": "b1_step3", "from_device": "quality", "to_device": "quality",
         "process_time_range": (100, 150), "priority": 1, "dependencies": ["b1_step2"]}
    ]
}

engine = SimulationEngine(config)
result = engine.run()

print(f"\nExpected: 3 flows (1 batch × 3 steps)")
print(f"Total flows completed (sum of all executions): {result['summary']['total_flows_completed']}")
print(f"Total events: {result['summary']['total_events']}")
print(f"Simulation time: {result['summary']['simulation_time_seconds']:.1f}s")

print(f"\nFlow details:")
for flow_exec in result.get('flows_executed', []):
    print(f"  {flow_exec['flow_id']}: executed {flow_exec['execution_count']} times")
