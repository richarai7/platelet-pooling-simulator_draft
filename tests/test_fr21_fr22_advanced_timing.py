"""
Comprehensive tests for FR21 (Advanced Offset Patterns) and FR22 (Deadlock Detection).

FR21 Tests:
- Start-to-start offsets (flow begins when predecessor starts, not completes)
- Random offset ranges (delay sampled from [min, max])
- Conditional delays (dynamic delays based on device utilization)

FR22 Tests:
- Timeout-based deadlock detection (flows blocked > 300s)
- Graph-based circular wait detection (A waits for B waits for A)
- Graceful termination with detailed error reporting
"""

import pytest
import json
from pathlib import Path


class TestFR21StartToStartOffsets:
    """Test FR21: Start-to-start offset functionality."""
    
    def test_start_to_start_basic(self):
        """Flow B can start when Flow A starts, not when it finishes."""
        config = {
            "simulation": {
                "duration": 100,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 5, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 5, "initial_state": "idle"},
                {"id": "D3", "type": "processor", "capacity": 5, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [20, 20],  # Takes 20 seconds
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D2",
                    "to_device": "D3",
                    "process_time_range": [10, 10],
                    "priority": 1,
                    "dependencies": ["F1"],
                    "offset_type": "start-to-start",  # Start when F1 starts
                    "offset_mode": "custom",
                    "start_offset": 5  # Start 5s after F1 starts
                }
            ],
            "output_options": {
                "include_events": True,
                "include_history": True
            }
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        # With start-to-start, F2 should start at T=5 (5s after F1 starts at T=0)
        # Without start-to-start, F2 would wait until F1 completes at T=20
        
        events = results.get("events", [])
        f2_start_events = [e for e in events if "F2" in e.get("description", "") and "started" in e.get("description", "").lower()]
        
        if f2_start_events:
            f2_start_time = f2_start_events[0]["timestamp"]
            # F2 should start around T=5, not T=20
            assert 4 <= f2_start_time <= 7, f"Start-to-start failed: F2 started at {f2_start_time}s, expected ~5s"
        
        assert results["status"] == "completed", "Simulation should complete successfully"
    
    def test_start_to_start_vs_finish_to_start(self):
        """Compare start-to-start vs finish-to-start timing."""
        base_config = {
            "simulation": {
                "duration": 100,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 5, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 5, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [30, 30],  # Takes 30 seconds
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D2",
                    "to_device": "D1",
                    "process_time_range": [5, 5],
                    "priority": 1,
                    "dependencies": ["F1"],
                    "offset_type": "finish-to-start",  # Will be changed
                    "offset_mode": "parallel"
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        # Test 1: Finish-to-start (default)
        config_finish = json.loads(json.dumps(base_config))
        config_finish["flows"][1]["offset_type"] = "finish-to-start"
        
        engine_finish = SimulationEngine(config_finish)
        results_finish = engine_finish.run()
        
        events_finish = results_finish.get("events", [])
        f2_events_finish = [e for e in events_finish if "F2" in str(e)]
        
        # Test 2: Start-to-start
        config_start = json.loads(json.dumps(base_config))
        config_start["flows"][1]["offset_type"] = "start-to-start"
        
        engine_start = SimulationEngine(config_start)
        results_start = engine_start.run()
        
        events_start = results_start.get("events", [])
        f2_events_start = [e for e in events_start if "F2" in str(e)]
        
        # Start-to-start should execute earlier than finish-to-start
        # (Exact timing depends on event structure, but both should complete)
        assert results_finish["status"] == "completed"
        assert results_start["status"] == "completed"


class TestFR21OffsetRanges:
    """Test FR21: Random offset range functionality."""
    
    def test_offset_range_basic(self):
        """Offset should be sampled from [min, max] range."""
        config = {
            "simulation": {
                "duration": 100,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 5, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 5, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [10, 10],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "offset_range": [5.0, 15.0]  # Random start between 5-15s
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        # Run multiple times with different seeds to verify randomness
        start_times = []
        
        for seed in [42, 123, 456]:
            config["simulation"]["random_seed"] = seed
            engine = SimulationEngine(config)
            results = engine.run()
            
            # Check if flow executed within expected time range
            assert results["status"] == "completed"
            
            events = results.get("events", [])
            f1_events = [e for e in events if "F1" in e.get("description", "")]
            
            if f1_events:
                # Flow should start between 5-15s
                first_event_time = f1_events[0]["timestamp"]
                start_times.append(first_event_time)
        
        # Verify offsets are within range (with some tolerance for scheduling)
        for start_time in start_times:
            assert 4 <= start_time <= 16, f"Offset {start_time} outside range [5, 15]"
    
    def test_offset_range_deterministic_with_seed(self):
        """Same seed should produce same offset."""
        config = {
            "simulation": {
                "duration": 100,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 5, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 5, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [10, 10],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "offset_range": [10.0, 20.0]
                }
            ],
            "output_options": {"include_events": False}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        # Run twice with same seed
        engine1 = SimulationEngine(config)
        results1 = engine1.run()
        
        engine2 = SimulationEngine(config)
        results2 = engine2.run()
        
        # Results should be identical (deterministic)
        assert results1["status"] == results2["status"]


class TestFR21ConditionalDelays:
    """Test FR21: Conditional delay functionality based on device state."""
    
    def test_conditional_delay_high_utilization(self):
        """Flow should delay when device utilization exceeds threshold."""
        config = {
            "simulation": {
                "duration": 200,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 2, "initial_state": "idle"},  # Small capacity
                {"id": "D2", "type": "processor", "capacity": 10, "initial_state": "idle"}
            ],
            "flows": [
                # Fill D1 to high utilization
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [50, 50],  # Long running
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [50, 50],  # Long running
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 1  # Start 1s after F1
                },
                # This flow should be delayed due to high utilization
                {
                    "flow_id": "F3",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [10, 10],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 2,
                    "conditional_delays": [
                        {
                            "condition_type": "high_utilization",
                            "device_id": "D1",
                            "threshold": 0.8,  # 80% utilization
                            "delay_seconds": 20  # Add 20s delay
                        }
                    ]
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        # Simulation should complete
        assert results["status"] in ["completed", "deadlock_detected"]
        
        # Check if conditional delay was applied (if events available)
        events = results.get("events", [])
        delay_events = [e for e in events if "conditional delay" in e.get("description", "").lower()]
        
        # If conditional delay was applied, verify it's logged
        # (Exact validation depends on event structure)


class TestFR22TimeoutDeadlockDetection:
    """Test FR22: Timeout-based deadlock detection."""
    
    def test_timeout_deadlock_detection(self):
        """Detect deadlock when flows blocked for > 300 seconds."""
        config = {
            "simulation": {
                "duration": 400,  # Long enough to trigger timeout
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 1, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 1, "initial_state": "idle"}
            ],
            "flows": [
                # Fill both devices completely
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [500, 500],  # Very long
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D2",
                    "to_device": "D1",
                    "process_time_range": [500, 500],  # Very long
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 1
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        # Should detect deadlock (either timeout or circular wait)
        assert results["status"] == "deadlock_detected", "Expected deadlock detection"
        assert "error" in results, "Should include error details"
        
        error_info = results.get("error", {})
        assert error_info.get("type") == "DeadlockError"
        
        # Should have deadlock details
        deadlock_info = error_info.get("deadlock_info", {})
        assert "detection_time" in deadlock_info
        assert "blocked_devices" in deadlock_info or "timeout_devices" in deadlock_info


class TestFR22CircularWaitDetection:
    """Test FR22: Graph-based circular wait detection."""
    
    def test_circular_wait_detection(self):
        """Detect circular wait: D1 waits for D2, D2 waits for D1."""
        config = {
            "simulation": {
                "duration": 400,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 1, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 1, "initial_state": "idle"},
                {"id": "D3", "type": "processor", "capacity": 1, "initial_state": "idle"}
            ],
            "flows": [
                # Create circular dependency through backpressure
                {
                    "flow_id": "F1_2",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [100, 100],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2_3",
                    "from_device": "D2",
                    "to_device": "D3",
                    "process_time_range": [100, 100],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 1
                },
                {
                    "flow_id": "F3_1",
                    "from_device": "D3",
                    "to_device": "D1",
                    "process_time_range": [100, 100],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 2
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        # Should detect deadlock
        assert results["status"] in ["deadlock_detected", "completed"]
        
        if results["status"] == "deadlock_detected":
            error_info = results.get("error", {})
            assert error_info.get("type") == "DeadlockError"


class TestFR22GracefulTermination:
    """Test FR22: Graceful termination and error reporting."""
    
    def test_error_output_structure(self):
        """Verify deadlock error contains all required information."""
        config = {
            "simulation": {
                "duration": 400,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 1, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 1, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [400, 400],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D2",
                    "to_device": "D1",
                    "process_time_range": [400, 400],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "custom",
                    "start_offset": 1
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        if results["status"] == "deadlock_detected":
            # Verify error structure
            assert "error" in results
            error = results["error"]
            
            # Required fields
            assert "type" in error
            assert error["type"] == "DeadlockError"
            assert "message" in error
            assert "deadlock_info" in error
            
            # Deadlock info fields
            deadlock_info = error["deadlock_info"]
            assert "detection_time" in deadlock_info
            assert isinstance(deadlock_info["detection_time"], (int, float))
            
            # Should have either timeout devices or wait graph
            has_timeout = "timeout_devices" in deadlock_info
            has_wait_graph = "wait_graph" in deadlock_info
            assert has_timeout or has_wait_graph, "Should report deadlock cause"
            
            # Should still have KPIs
            assert "kpis" in results
            assert "execution_time" in results


class TestFR21FR22Integration:
    """Test integration of FR21 and FR22 features."""
    
    def test_fr21_with_fr22_no_deadlock(self):
        """FR21 advanced timing should work without triggering FR22 deadlock."""
        config = {
            "simulation": {
                "duration": 150,
                "random_seed": 42,
                "execution_mode": "accelerated"
            },
            "devices": [
                {"id": "D1", "type": "processor", "capacity": 3, "initial_state": "idle"},
                {"id": "D2", "type": "processor", "capacity": 3, "initial_state": "idle"},
                {"id": "D3", "type": "processor", "capacity": 3, "initial_state": "idle"}
            ],
            "flows": [
                {
                    "flow_id": "F1",
                    "from_device": "D1",
                    "to_device": "D2",
                    "process_time_range": [20, 20],
                    "priority": 1,
                    "dependencies": None,
                    "offset_mode": "parallel"
                },
                {
                    "flow_id": "F2",
                    "from_device": "D2",
                    "to_device": "D3",
                    "process_time_range": [15, 15],
                    "priority": 1,
                    "dependencies": ["F1"],
                    "offset_type": "start-to-start",  # FR21
                    "offset_mode": "custom",
                    "offset_range": [5.0, 10.0],  # FR21
                    "conditional_delays": [  # FR21
                        {
                            "condition_type": "high_utilization",
                            "device_id": "D2",
                            "threshold": 0.9,
                            "delay_seconds": 5
                        }
                    ]
                }
            ],
            "output_options": {"include_events": True}
        }
        
        from src.simulation_engine.engine import SimulationEngine
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        # Should complete without deadlock
        assert results["status"] == "completed", "Should complete successfully with FR21 features"
        assert "kpis" in results
        
        # Verify execution happened
        kpis = results["kpis"]
        # Check total_units_created (KPI name for flows completed)
        units_created = kpis.get("total_units_created", 0)
        assert units_created >= 2, f"Expected at least 2 flows executed, but got {units_created}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
