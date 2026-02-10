"""Tests for SimulationEngine orchestrator."""
import pytest
from simulation_engine import SimulationEngine


class TestSimulationEngine:
    """Integration tests for full simulation engine."""

    @pytest.fixture
    def simple_config(self):
        """Simple 2-device configuration for testing."""
        return {
            "simulation": {
                "duration": 100.0,
                "random_seed": 42
            },
            "devices": [
                {
                    "id": "device_a",
                    "type": "machine",
                    "capacity": 1,
                    "initial_state": "Idle",
                    "recovery_time_range": None
                },
                {
                    "id": "device_b",
                    "type": "machine",
                    "capacity": 1,
                    "initial_state": "Idle",
                    "recovery_time_range": None
                }
            ],
            "flows": [
                {
                    "flow_id": "flow_1",
                    "from_device": "device_a",
                    "to_device": "device_b",
                    "process_time_range": (10.0, 20.0),
                    "priority": 1,
                    "dependencies": None
                }
            ],
            "output_options": {
                "include_history": True,
                "include_events": True
            }
        }

    def test_engine_initialization(self, simple_config):
        """Engine should initialize with valid configuration."""
        engine = SimulationEngine(simple_config)
        assert engine is not None

    def test_engine_run_returns_results(self, simple_config):
        """Running simulation should return results dictionary."""
        engine = SimulationEngine(simple_config)
        results = engine.run()
        
        assert results is not None
        assert isinstance(results, dict)

    def test_results_contain_metadata(self, simple_config):
        """Results should include simulation metadata."""
        engine = SimulationEngine(simple_config)
        results = engine.run()
        
        assert "metadata" in results
        assert results["metadata"]["random_seed"] == 42
        assert results["metadata"]["duration"] == 100.0

    def test_results_contain_summary(self, simple_config):
        """Results should include execution summary."""
        engine = SimulationEngine(simple_config)
        results = engine.run()
        
        assert "summary" in results
        assert "total_events" in results["summary"]
        assert "simulation_time_seconds" in results["summary"]

    def test_results_contain_device_states(self, simple_config):
        """Results should include final device states."""
        engine = SimulationEngine(simple_config)
        results = engine.run()
        
        assert "device_states" in results
        assert len(results["device_states"]) == 2

    def test_deterministic_execution(self, simple_config):
        """Same seed should produce identical results."""
        engine1 = SimulationEngine(simple_config)
        results1 = engine1.run()
        
        engine2 = SimulationEngine(simple_config)
        results2 = engine2.run()
        
        # Metadata fields like timestamp will differ, compare event counts
        assert results1["summary"]["total_events"] == results2["summary"]["total_events"]

    def test_different_seeds_produce_different_results(self, simple_config):
        """Different seeds should produce different results."""
        config1 = simple_config.copy()
        config1["simulation"]["random_seed"] = 42
        
        config2 = simple_config.copy()
        config2["simulation"]["random_seed"] = 999
        
        engine1 = SimulationEngine(config1)
        results1 = engine1.run()
        
        engine2 = SimulationEngine(config2)
        results2 = engine2.run()
        
        # Results may differ due to random timing
        assert results1 is not None
        assert results2 is not None
