"""Output format validation tests."""
import pytest
import copy
from simulation_engine import SimulationEngine
from tests.fixtures.scenarios import SIMPLE_2_DEVICE_CONFIG


class TestOutputFormat:
    """Verify JSON output schema compliance."""

    def test_output_contains_required_sections(self):
        """Output should have all required top-level sections."""
        engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
        results = engine.run()
        
        assert "metadata" in results
        assert "summary" in results
        assert "device_states" in results

    def test_metadata_section_complete(self):
        """Metadata section should have all required fields."""
        engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
        results = engine.run()
        
        metadata = results["metadata"]
        assert "simulation_id" in metadata
        assert "duration" in metadata
        assert "random_seed" in metadata
        assert "completed_at" in metadata
        assert "engine_version" in metadata
        
        assert metadata["duration"] == 100.0
        assert metadata["random_seed"] == 42
        assert metadata["engine_version"] == "0.1.0"

    def test_summary_section_complete(self):
        """Summary section should have all required fields."""
        engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
        results = engine.run()
        
        summary = results["summary"]
        assert "total_events" in summary
        assert "total_flows_completed" in summary
        assert "devices_count" in summary
        assert "simulation_time_seconds" in summary
        assert "execution_time_seconds" in summary
        
        assert summary["devices_count"] == 2

    def test_device_states_section_complete(self):
        """Device states section should have entries for all devices."""
        engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
        results = engine.run()
        
        device_states = results["device_states"]
        assert len(device_states) == 2
        
        for state in device_states:
            assert "device_id" in state
            assert "final_state" in state
            assert "state_changes" in state

    def test_optional_state_history_included_when_enabled(self):
        """State history should be included when output_options enabled."""
        config = copy.deepcopy(SIMPLE_2_DEVICE_CONFIG)
        config["output_options"]["include_history"] = True
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        assert "state_history" in results

    def test_optional_events_included_when_enabled(self):
        """Event timeline should be included when output_options enabled."""
        config = copy.deepcopy(SIMPLE_2_DEVICE_CONFIG)
        config["output_options"]["include_events"] = True
        
        engine = SimulationEngine(config)
        results = engine.run()
        
        assert "event_timeline" in results

    def test_flows_executed_section_present(self):
        """Flows executed summary should be present."""
        engine = SimulationEngine(copy.deepcopy(SIMPLE_2_DEVICE_CONFIG))
        results = engine.run()
        
        assert "flows_executed" in results
        assert len(results["flows_executed"]) > 0
