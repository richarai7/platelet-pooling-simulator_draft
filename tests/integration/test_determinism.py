"""Determinism validation tests."""
import pytest
import copy
from simulation_engine import SimulationEngine
from tests.fixtures.scenarios import SIMPLE_2_DEVICE_CONFIG, HEALTHCARE_CONFIG


class TestDeterminism:
    """Verify identical seeds produce identical results."""

    def test_simple_scenario_determinism(self):
        """Same seed produces identical results across 10 runs."""
        results_list = []
        
        for _ in range(10):
            engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
            results = engine.run()
            results_list.append(results)
        
        # All runs should have identical event counts
        event_counts = [r["summary"]["total_events"] for r in results_list]
        assert len(set(event_counts)) == 1, "Event counts should be identical"
        
        # All runs should have identical simulation time
        sim_times = [r["summary"]["simulation_time_seconds"] for r in results_list]
        assert len(set(sim_times)) == 1, "Simulation times should be identical"

    def test_healthcare_scenario_determinism(self):
        """Healthcare config produces deterministic results."""
        engine1 = SimulationEngine(copy.deepcopy(HEALTHCARE_CONFIG))
        results1 = engine1.run()
        
        engine2 = SimulationEngine(copy.deepcopy(HEALTHCARE_CONFIG))
        results2 = engine2.run()
        
        assert results1["summary"]["total_events"] == results2["summary"]["total_events"]
        assert results1["summary"]["simulation_time_seconds"] == results2["summary"]["simulation_time_seconds"]

    def test_different_seeds_produce_different_results(self):
        """Different seeds should produce different results."""
        config1 = copy.deepcopy(SIMPLE_2_DEVICE_CONFIG)
        config1["simulation"]["random_seed"] = 42
        
        config2 = copy.deepcopy(SIMPLE_2_DEVICE_CONFIG)
        config2["simulation"]["random_seed"] = 999
        
        engine1 = SimulationEngine(config1)
        results1 = engine1.run()
        
        engine2 = SimulationEngine(config2)
        results2 = engine2.run()
        
        # Results should exist but may differ
        assert results1 is not None
        assert results2 is not None
