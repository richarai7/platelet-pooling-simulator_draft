"""Detailed backpressure test"""

from simulation_engine import SimulationEngine

print("BACKPRESSURE DETAILED TEST")
print("=" * 60)

config = {
    'simulation': {'duration': 50, 'random_seed': 42},
    'devices': [
        {'id': 'fast_source', 'type': 'machine', 'capacity': 5, 'initial_state': 'Idle'},
        {'id': 'slow_dest', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle'}
    ],
    'flows': [
        # Multiple flows starting at same time, all trying to use slow_dest
        {'flow_id': 'flow1', 'from_device': 'fast_source', 'to_device': 'slow_dest', 
         'process_time_range': (2, 3), 'priority': 1, 'offset_mode': 'parallel'},
        {'flow_id': 'flow2', 'from_device': 'fast_source', 'to_device': 'slow_dest', 
         'process_time_range': (2, 3), 'priority': 1, 'offset_mode': 'parallel'},
        {'flow_id': 'flow3', 'from_device': 'fast_source', 'to_device': 'slow_dest', 
         'process_time_range': (2, 3), 'priority': 1, 'offset_mode': 'parallel'},
    ],
    'output_options': {'include_history': True, 'include_events': True}
}

engine = SimulationEngine(config)
result = engine.run()

print(f"\nResults:")
print(f"  Total events: {result['summary']['total_events']}")
print(f"  Flows completed: {result['summary']['total_flows_completed']}")

print(f"\nState History:")
for h in result['state_history']:
    print(f"  T={h['timestamp']:6.2f}s | {h['device_id']:12s} | {h['from_state']:10s} -> {h['to_state']:10s} | {h['event']}")

blocked = [h for h in result['state_history'] if 'Blocked' in h['to_state']]
print(f"\n✅ Blocked transitions: {len(blocked)}")

print(f"\nDownstream capacity check:")
print(f"  slow_dest capacity: 1")
print(f"  Flows targeting slow_dest: 3")
print(f"  Expected: Some flows should detect full capacity and enter Blocked state")
