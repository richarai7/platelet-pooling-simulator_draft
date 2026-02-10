"""Tests for ConfigManager module."""
import pytest
from simulation_engine.config_manager import (
    ConfigManager,
    ValidationError,
    DeviceConfig,
    FlowConfig,
    SimulationConfig
)


class TestConfigManager:
    """Test configuration validation."""

    def test_valid_config_passes_validation(self) -> None:
        """Well-formed configuration should validate successfully."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {
                    "id": "device_1",
                    "type": "machine",
                    "capacity": 1,
                    "initial_state": "Idle",
                    "recovery_time_range": (10.0, 20.0)
                }
            ],
            "flows": [
                {
                    "flow_id": "flow_1",
                    "from_device": "device_1",
                    "to_device": "device_1",
                    "process_time_range": (5.0, 15.0),
                    "priority": 1,
                    "dependencies": None
                }
            ],
            "output_options": {"include_history": True, "include_events": True}
        }
        
        mgr = ConfigManager(config)
        validated = mgr.validate()
        
        assert validated["simulation"]["duration"] == 1000.0

    def test_missing_required_field_fails(self) -> None:
        """Configuration missing required field should fail."""
        config = {
            # Missing "simulation" field
            "devices": [],
            "flows": [],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Missing required field"):
            ConfigManager(config).validate()

    def test_duplicate_device_ids_fails(self) -> None:
        """Duplicate device IDs should fail validation."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {"id": "device_1", "type": "a", "capacity": 1, "initial_state": "Idle"},
                {"id": "device_1", "type": "b", "capacity": 1, "initial_state": "Idle"}  # Duplicate!
            ],
            "flows": [],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Duplicate device IDs"):
            ConfigManager(config).validate()

    def test_duplicate_flow_ids_fails(self) -> None:
        """Duplicate flow IDs should fail validation."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {"id": "dev_1", "type": "a", "capacity": 1, "initial_state": "Idle"}
            ],
            "flows": [
                {"flow_id": "flow_1", "from_device": "dev_1", "to_device": "dev_1",
                 "process_time_range": (1.0, 2.0), "priority": 1},
                {"flow_id": "flow_1", "from_device": "dev_1", "to_device": "dev_1",
                 "process_time_range": (1.0, 2.0), "priority": 1}  # Duplicate!
            ],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Duplicate flow IDs"):
            ConfigManager(config).validate()

    def test_flow_references_nonexistent_device_fails(self) -> None:
        """Flow referencing unknown device should fail."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {"id": "dev_1", "type": "a", "capacity": 1, "initial_state": "Idle"}
            ],
            "flows": [
                {"flow_id": "flow_1", "from_device": "dev_1", "to_device": "dev_999",
                 "process_time_range": (1.0, 2.0), "priority": 1}
            ],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="references unknown device"):
            ConfigManager(config).validate()

    def test_negative_capacity_fails(self) -> None:
        """Device capacity must be >= 1."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {"id": "dev_1", "type": "a", "capacity": 0, "initial_state": "Idle"}  # Invalid!
            ],
            "flows": [],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Capacity must be >= 1"):
            ConfigManager(config).validate()

    def test_invalid_time_range_fails(self) -> None:
        """Time range must have min < max."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": 42},
            "devices": [
                {"id": "dev_1", "type": "a", "capacity": 1, "initial_state": "Idle"}
            ],
            "flows": [
                {"flow_id": "flow_1", "from_device": "dev_1", "to_device": "dev_1",
                 "process_time_range": (10.0, 5.0), "priority": 1}  # min > max!
            ],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="must have min < max"):
            ConfigManager(config).validate()

    def test_negative_duration_fails(self) -> None:
        """Duration must be positive."""
        config = {
            "simulation": {"duration": -100.0, "random_seed": 42},
            "devices": [],
            "flows": [],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Duration must be > 0"):
            ConfigManager(config).validate()

    def test_negative_random_seed_fails(self) -> None:
        """Random seed must be non-negative."""
        config = {
            "simulation": {"duration": 1000.0, "random_seed": -5},
            "devices": [],
            "flows": [],
            "output_options": {}
        }
        
        with pytest.raises(ValidationError, match="Random seed must be >= 0"):
            ConfigManager(config).validate()
