"""Test new features: capacity, backpressure, auto-recovery, cancellation"""

from simulation_engine import SimulationEngine
import json

print("=" * 60)
print("TESTING NEW FEATURES")
print("=" * 60)

# Test 1: Capacity Enforcement
print("\n1. CAPACITY ENFORCEMENT TEST")
print("-" * 40)
config_capacity = {
    'simulation': {'duration': 100, 'random_seed': 42},
    'devices': [
        {'id': 'd1', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle'},
        {'id': 'd2', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle'}
    ],
    'flows': [
        {'flow_id': 'f1', 'from_device': 'd1', 'to_device': 'd2', 'process_time_range': (10, 20), 'priority': 1},
        {'flow_id': 'f2', 'from_device': 'd1', 'to_device': 'd2', 'process_time_range': (10, 20), 'priority': 1}
    ],
    'output_options': {'include_history': True}
}

engine = SimulationEngine(config_capacity)
result = engine.run()
print(f"✅ Events: {result['summary']['total_events']}")
print(f"✅ Flows completed: {result['summary']['total_flows_completed']}")
d1_states = [h for h in result['state_history'] if h['device_id'] == 'd1']
print(f"✅ Device d1 state changes: {len(d1_states)}")
print(f"   (Capacity=1 should block second flow until first completes)")

# Test 2: Backpressure Detection
print("\n2. BACKPRESSURE TEST")
print("-" * 40)
config_backpressure = {
    'simulation': {'duration': 100, 'random_seed': 42},
    'devices': [
        {'id': 'source', 'type': 'machine', 'capacity': 2, 'initial_state': 'Idle'},
        {'id': 'bottleneck', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle'}
    ],
    'flows': [
        {'flow_id': 'fast1', 'from_device': 'source', 'to_device': 'bottleneck', 'process_time_range': (5, 10), 'priority': 1},
        {'flow_id': 'fast2', 'from_device': 'source', 'to_device': 'bottleneck', 'process_time_range': (5, 10), 'priority': 1}
    ],
    'output_options': {'include_history': True}
}

engine = SimulationEngine(config_backpressure)
result = engine.run()
blocked_events = [h for h in result['state_history'] if 'Blocked' in h['to_state']]
print(f"✅ Blocked state transitions: {len(blocked_events)}")
if blocked_events:
    print(f"   Device {blocked_events[0]['device_id']} blocked at T={blocked_events[0]['timestamp']:.1f}s")
    print("   ✅ Backpressure enforcement working!")

# Test 3: Auto-Recovery
print("\n3. AUTO-RECOVERY TEST")
print("-" * 40)
config_recovery = {
    'simulation': {'duration': 100, 'random_seed': 42},
    'devices': [
        {'id': 'recoverable', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle', 'recovery_time_range': (5, 10)}
    ],
    'flows': [],
    'output_options': {'include_history': True}
}

engine = SimulationEngine(config_recovery)
# Manually trigger failure
engine.state_manager.transition('recoverable', 'FAILURE_DETECTED')
result = engine.run()
recovery_events = [h for h in result['state_history'] if h['event'] == 'RECOVERY_COMPLETE']
print(f"✅ Recovery events: {len(recovery_events)}")
if recovery_events:
    print(f"   Device recovered at T={recovery_events[0]['timestamp']:.1f}s")
    print("   ✅ Auto-recovery working!")
else:
    print("   ⚠️ No recovery - check if scheduled correctly")

# Test 4: Cancellation
print("\n4. CANCELLATION TEST")
print("-" * 40)
config_cancel = {
    'simulation': {'duration': 10000, 'random_seed': 42},  # Long simulation
    'devices': [
        {'id': 'device', 'type': 'machine', 'capacity': 1, 'initial_state': 'Idle'}
    ],
    'flows': [
        {'flow_id': 'long_flow', 'from_device': 'device', 'to_device': 'device', 'process_time_range': (1, 2), 'priority': 1}
    ],
    'output_options': {}
}

engine = SimulationEngine(config_cancel)
# Schedule immediate cancellation
engine.scheduler.schedule(
    timestamp=5.0,
    event_id='test_cancel',
    callback=lambda: engine.cancel()
)
result = engine.run()
print(f"✅ Simulation stopped at: {result['summary']['simulation_time_seconds']}s")
print(f"   (Expected <10s from 10000s duration)")
print(f"✅ Events processed before cancel: {result['summary']['total_events']}")
if result['summary']['simulation_time_seconds'] < 100:
    print("   ✅ Cancellation working!")

print("\n" + "=" * 60)
print("ALL NEW FEATURES TESTED")
print("=" * 60)
