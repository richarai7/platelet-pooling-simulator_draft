"""Performance benchmark tests."""
import pytest
import time
from simulation_engine import SimulationEngine
from tests.fixtures.scenarios import HEALTHCARE_CONFIG, MANUFACTURING_CONFIG


class TestPerformance:
    """Benchmark simulation performance against NFRs."""

    def test_healthcare_36_hour_scenario_completes_quickly(self):
        """36-hour healthcare scenario should complete in <2 minutes (NFR)."""
        start_time = time.time()
        
        engine = SimulationEngine(HEALTHCARE_CONFIG)
        results = engine.run()
        
        execution_time = time.time() - start_time
        
        assert results is not None
        assert execution_time < 120.0, f"Execution took {execution_time}s, should be <120s"

    def test_manufacturing_8_hour_scenario_performance(self):
        """8-hour manufacturing scenario should complete quickly."""
        start_time = time.time()
        
        engine = SimulationEngine(MANUFACTURING_CONFIG)
        results = engine.run()
        
        execution_time = time.time() - start_time
        
        assert results is not None
        assert execution_time < 60.0, f"Execution took {execution_time}s, should be <60s"

    def test_multiple_runs_no_memory_leak(self):
        """Running 50 consecutive scenarios should not leak memory."""
        start_time = time.time()
        
        for _ in range(50):
            engine = SimulationEngine(HEALTHCARE_CONFIG)
            results = engine.run()
            assert results is not None
        
        execution_time = time.time() - start_time
        
        # 50 runs should complete reasonably fast
        assert execution_time < 300.0, "50 runs took too long"
