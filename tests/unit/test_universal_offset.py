"""
Unit tests for Universal Offset pattern implementation.

Tests validate three offset modes:
- parallel: All flows start at time 0.0 (simultaneous execution)
- sequence: Flows start after predecessor completes (serial execution)
- custom: Flows start at specified offset from simulation start
"""

import pytest
from simulation_engine import SimulationEngine


def test_parallel_offset_mode():
    """Test parallel mode: all flows start at time 0.0."""
    config = {
        "simulation": {"duration": 50.0, "random_seed": 42},
        "devices": [
            {"id": "D1", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D2", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D3", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D4", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
        ],
        "flows": [
            {
                "flow_id": "F1",
                "from_device": "D1",
                "to_device": "D2",
                "process_time_range": (9.5, 10.5),
                "offset_mode": "parallel",
                "priority": 1,
                "dependencies": None,
            },
            {
                "flow_id": "F2",
                "from_device": "D3",
                "to_device": "D4",
                "process_time_range": (14.5, 15.5),
                "offset_mode": "parallel",
                "priority": 1,
                "dependencies": None,
            },
        ],
        "output_options": {"include_history": True, "include_events": True},
    }

    engine = SimulationEngine(config)
    results = engine.run()

    # Verify both flows started at time 0 by checking state transitions
    state_history = results["state_history"]

    # Find first START_PROCESSING events for each device
    d1_start = next((h for h in state_history if h["device_id"] == "D1" and h["event"] == "START_PROCESSING"), None)
    d3_start = next((h for h in state_history if h["device_id"] == "D3" and h["event"] == "START_PROCESSING"), None)

    assert d1_start is not None, "D1 should have started processing (F1)"
    assert d3_start is not None, "D3 should have started processing (F2)"

    # Both should start at time 0.0 (within tolerance) - parallel mode
    assert abs(d1_start["timestamp"] - 0.0) < 0.01, f"F1 (D1) should start at time 0, got {d1_start['timestamp']}"
    assert abs(d3_start["timestamp"] - 0.0) < 0.01, f"F2 (D3) should start at time 0, got {d3_start['timestamp']}"


def test_custom_offset_mode():
    """Test custom mode: flows start at specified offset times."""
    config = {
        "simulation": {"duration": 50.0, "random_seed": 42},
        "devices": [
            {"id": "D1", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D2", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D3", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D4", "type": "device", "capacity": 2, "initial_state": "Idle", "recovery_time_range": None},
        ],
        "flows": [
            {
                "flow_id": "F1",
                "from_device": "D1",
                "to_device": "D2",
                "process_time_range": (9.5, 10.5),
                "offset_mode": "custom",
                "start_offset": 5.0,  # Start at t=5.0
                "priority": 1,
                "dependencies": None,
            },
            {
                "flow_id": "F2",
                "from_device": "D3",
                "to_device": "D4",
                "process_time_range": (9.5, 10.5),
                "offset_mode": "custom",
                "start_offset": 15.0,  # Start at t=15.0
                "priority": 1,
                "dependencies": None,
            },
        ],
        "output_options": {"include_history": True, "include_events": True},
    }

    engine = SimulationEngine(config)
    results = engine.run()

    state_history = results["state_history"]

    # F1 starts D1 at t=5.0, F2 starts D3 at t=15.0
    d1_start = next((h for h in state_history if h["device_id"] == "D1" and h["event"] == "START_PROCESSING"), None)
    d3_start = next((h for h in state_history if h["device_id"] == "D3" and h["event"] == "START_PROCESSING"), None)

    assert d1_start is not None, "F1 should have started D1"
    assert d3_start is not None, "F2 should have started D3"

    # Verify custom offsets (within tolerance)
    assert abs(d1_start["timestamp"] - 5.0) < 0.1, f"F1 (D1) should start at offset 5.0, got {d1_start['timestamp']}"
    assert abs(d3_start["timestamp"] - 15.0) < 0.2, f"F2 (D3) should start at offset 15.0, got {d3_start['timestamp']}"


def test_sequence_offset_mode():
    """Test sequence mode: flows start after prerequisites complete."""
    config = {
        "simulation": {"duration": 60.0, "random_seed": 42},
        "devices": [
            {"id": "D1", "type": "device", "capacity": 1, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D2", "type": "device", "capacity": 1, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D3", "type": "device", "capacity": 1, "initial_state": "Idle", "recovery_time_range": None},
        ],
        "flows": [
            {
                "flow_id": "F1",
                "from_device": "D1",
                "to_device": "D2",  # D1 processes, sends to D2
                "process_time_range": (9.5, 10.5),
                "offset_mode": "parallel",  # Start immediately
                "priority": 1,
                "dependencies": None,
            },
            {
                "flow_id": "F2",
                "from_device": "D2",  # D2 processes (after receiving from D1)
                "to_device": "D3",
                "process_time_range": (14.5, 15.5),
                "offset_mode": "sequence",  # Start after F1 completes
                "priority": 1,
                "dependencies": ["F1"],
            },
        ],
        "output_options": {"include_history": True, "include_events": True},
    }

    engine = SimulationEngine(config)
    results = engine.run()

    state_history = results["state_history"]

    # F1: D1 processes (t=0 to t=~10)
    # F2: D2 should only start after F1 completes (after t=~10)

    # Find state transitions
    d1_processing = [h for h in state_history if h["device_id"] == "D1" and h["event"] == "START_PROCESSING"]
    d1_complete = [h for h in state_history if h["device_id"] == "D1" and h["event"] == "COMPLETE_PROCESSING"]
    d2_processing = [h for h in state_history if h["device_id"] == "D2" and h["event"] == "START_PROCESSING"]

    assert len(d1_processing) > 0, "D1 should process for F1"
    assert len(d1_complete) > 0, "D1 should complete F1"
    assert len(d2_processing) > 0, "D2 should process for F2"

    # F1 should start at t=0
    assert abs(d1_processing[0]["timestamp"] - 0.0) < 0.1, f"F1 (D1) starts at time 0, got {d1_processing[0]['timestamp']}"

    # F2 should only start after F1 fully completes (D1 completes)
    f1_complete_time = d1_complete[0]["timestamp"]
    f2_start_time = d2_processing[0]["timestamp"]
    
    assert f2_start_time >= f1_complete_time, f"F2 (D2) should start after F1 completes at {f1_complete_time}, got {f2_start_time}"


def test_default_offset_mode_is_parallel():
    """Test that flows without explicit offset_mode default to parallel."""
    config = {
        "simulation": {"duration": 30.0, "random_seed": 42},
        "devices": [
            {"id": "D1", "type": "device", "capacity": 1, "initial_state": "Idle", "recovery_time_range": None},
            {"id": "D2", "type": "device", "capacity": 1, "initial_state": "Idle", "recovery_time_range": None},
        ],
        "flows": [
            {
                "flow_id": "F1",
                "from_device": "D1",
                "to_device": "D2",
                "process_time_range": (9.5, 10.5),
                "priority": 1,
                "dependencies": None,
                # No offset_mode specified
            }
        ],
        "output_options": {"include_history": True, "include_events": True},
    }

    engine = SimulationEngine(config)
    results = engine.run()

    state_history = results["state_history"]

    # Should start at time 0 (parallel mode default)
    d1_start = next((h for h in state_history if h["device_id"] == "D1" and h["event"] == "START_PROCESSING"), None)

    assert d1_start is not None, "F1 should start D1"
    assert abs(d1_start["timestamp"] - 0.0) < 0.01, f"Default offset mode should be parallel (t=0), got {d1_start['timestamp']}"

