"""Tests for FlowController module."""
import pytest
from simulation_engine.flow_controller import FlowController


class TestFlowController:
    """Test process flow management and dependencies."""

    def test_validate_simple_flow(self) -> None:
        """Single flow with no dependencies should validate successfully."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "device_a",
                "to_device": "device_b",
                "dependencies": None
            }
        ]
        devices = ["device_a", "device_b"]
        
        controller = FlowController(flows, devices)
        # No exception = success

    def test_validate_flow_references_invalid_device(self) -> None:
        """Flow referencing non-existent device should fail validation."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "device_a",
                "to_device": "device_999",  # Does not exist
                "dependencies": None
            }
        ]
        devices = ["device_a", "device_b"]
        
        with pytest.raises(ValueError, match="references unknown device"):
            FlowController(flows, devices)

    def test_validate_dependency_references_invalid_flow(self) -> None:
        """Flow with non-existent dependency should fail validation."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "device_a",
                "to_device": "device_b",
                "dependencies": ["flow_999"]  # Does not exist
            }
        ]
        devices = ["device_a", "device_b"]
        
        with pytest.raises(ValueError, match="references unknown flow"):
            FlowController(flows, devices)

    def test_detect_circular_dependency(self) -> None:
        """Circular dependencies should be detected."""
        flows = [
            {
                "flow_id": "flow_a",
                "from_device": "dev_1",
                "to_device": "dev_2",
                "dependencies": ["flow_b"]
            },
            {
                "flow_id": "flow_b",
                "from_device": "dev_2",
                "to_device": "dev_1",
                "dependencies": ["flow_a"]  # Circular!
            }
        ]
        devices = ["dev_1", "dev_2"]
        
        with pytest.raises(ValueError, match="Circular dependency"):
            FlowController(flows, devices)

    def test_get_executable_flows_no_dependencies(self) -> None:
        """Flows without dependencies are immediately executable."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "dev_a",
                "to_device": "dev_b",
                "dependencies": None
            },
            {
                "flow_id": "flow_2",
                "from_device": "dev_c",
                "to_device": "dev_d",
                "dependencies": []
            }
        ]
        devices = ["dev_a", "dev_b", "dev_c", "dev_d"]
        
        controller = FlowController(flows, devices)
        executable = controller.get_executable_flows(completed=[])
        
        assert "flow_1" in executable
        assert "flow_2" in executable

    def test_get_executable_flows_with_dependencies(self) -> None:
        """Flows executable only when dependencies completed."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "dev_a",
                "to_device": "dev_b",
                "dependencies": None
            },
            {
                "flow_id": "flow_2",
                "from_device": "dev_b",
                "to_device": "dev_c",
                "dependencies": ["flow_1"]
            }
        ]
        devices = ["dev_a", "dev_b", "dev_c"]
        
        controller = FlowController(flows, devices)
        
        # Initially only flow_1 executable
        executable = controller.get_executable_flows(completed=[])
        assert "flow_1" in executable
        assert "flow_2" not in executable
        
        # After flow_1 completes, flow_2 becomes executable
        executable = controller.get_executable_flows(completed=["flow_1"])
        assert "flow_2" in executable

    def test_mark_flow_completed(self) -> None:
        """Should track completed flows."""
        flows = [
            {
                "flow_id": "flow_1",
                "from_device": "dev_a",
                "to_device": "dev_b",
                "dependencies": None
            }
        ]
        devices = ["dev_a", "dev_b"]
        
        controller = FlowController(flows, devices)
        
        assert not controller.is_completed("flow_1")
        controller.mark_completed("flow_1")
        assert controller.is_completed("flow_1")
