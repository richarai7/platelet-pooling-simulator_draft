"""Tests for StateManager module."""
import pytest
from simulation_engine.state_manager import StateManager, DeviceState, InvalidTransitionError


class TestStateManager:
    """Test 4-state device model and transitions."""

    def test_device_starts_in_idle_state(self) -> None:
        """New devices should start in Idle state."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        state = mgr.get_state("device_1")
        assert state == DeviceState.IDLE

    def test_idle_to_processing_transition(self) -> None:
        """Valid transition: Idle → Processing on START_PROCESSING event."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        new_state = mgr.transition("device_1", "START_PROCESSING")
        assert new_state == DeviceState.PROCESSING
        assert mgr.get_state("device_1") == DeviceState.PROCESSING

    def test_processing_to_idle_transition(self) -> None:
        """Valid transition: Processing → Idle on COMPLETE_PROCESSING."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        new_state = mgr.transition("device_1", "COMPLETE_PROCESSING")
        
        assert new_state == DeviceState.IDLE

    def test_processing_to_blocked_transition(self) -> None:
        """Valid transition: Processing → Blocked on BACKPRESSURE_DETECTED."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        new_state = mgr.transition("device_1", "BACKPRESSURE_DETECTED")
        
        assert new_state == DeviceState.BLOCKED

    def test_blocked_to_idle_transition(self) -> None:
        """Valid transition: Blocked → Idle on BACKPRESSURE_CLEARED."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        mgr.transition("device_1", "BACKPRESSURE_DETECTED")
        new_state = mgr.transition("device_1", "BACKPRESSURE_CLEARED")
        
        assert new_state == DeviceState.IDLE

    def test_idle_to_failed_transition(self) -> None:
        """Valid transition: Idle → Failed on FAILURE_DETECTED."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        new_state = mgr.transition("device_1", "FAILURE_DETECTED")
        assert new_state == DeviceState.FAILED

    def test_failed_to_idle_transition(self) -> None:
        """Valid transition: Failed → Idle on RECOVERY_COMPLETE."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "FAILURE_DETECTED")
        new_state = mgr.transition("device_1", "RECOVERY_COMPLETE")
        
        assert new_state == DeviceState.IDLE

    def test_invalid_transition_raises_error(self) -> None:
        """Invalid transitions should raise InvalidTransitionError."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        # Cannot go directly from Idle to Blocked
        with pytest.raises(InvalidTransitionError, match="Cannot BACKPRESSURE_DETECTED from Idle"):
            mgr.transition("device_1", "BACKPRESSURE_DETECTED")

    def test_state_history_tracked(self) -> None:
        """All state transitions should be recorded in history."""
        current_time = 0.0
        mgr = StateManager(current_time_fn=lambda: current_time)
        
        current_time = 5.0
        mgr.transition("device_1", "START_PROCESSING")
        
        current_time = 10.5
        mgr.transition("device_1", "COMPLETE_PROCESSING")
        
        history = mgr.get_history("device_1")
        assert len(history) == 2
        
        assert history[0]["from_state"] == "Idle"
        assert history[0]["to_state"] == "Processing"
        assert history[0]["event"] == "START_PROCESSING"
        assert history[0]["timestamp"] == 5.0
        
        assert history[1]["from_state"] == "Processing"
        assert history[1]["to_state"] == "Idle"
        assert history[1]["timestamp"] == 10.5

    def test_get_history_for_all_devices(self) -> None:
        """Should return history for all devices when no device_id specified."""
        current_time = 0.0
        mgr = StateManager(current_time_fn=lambda: current_time)
        
        mgr.transition("device_1", "START_PROCESSING")
        mgr.transition("device_2", "START_PROCESSING")
        
        all_history = mgr.get_history()
        assert len(all_history) == 2
        
        device_ids = [h["device_id"] for h in all_history]
        assert "device_1" in device_ids
        assert "device_2" in device_ids

    def test_multiple_devices_independent_states(self) -> None:
        """Each device should maintain independent state."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        mgr.transition("device_2", "FAILURE_DETECTED")
        
        assert mgr.get_state("device_1") == DeviceState.PROCESSING
        assert mgr.get_state("device_2") == DeviceState.FAILED
        assert mgr.get_state("device_3") == DeviceState.IDLE  # Uninitialized

    def test_processing_to_failed_transition(self) -> None:
        """Valid transition: Processing → Failed on FAILURE_DETECTED."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        new_state = mgr.transition("device_1", "FAILURE_DETECTED")
        
        assert new_state == DeviceState.FAILED

    def test_blocked_to_failed_transition(self) -> None:
        """Valid transition: Blocked → Failed on FAILURE_DETECTED."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "START_PROCESSING")
        mgr.transition("device_1", "BACKPRESSURE_DETECTED")
        new_state = mgr.transition("device_1", "FAILURE_DETECTED")
        
        assert new_state == DeviceState.FAILED

    def test_cannot_transition_from_failed_except_recovery(self) -> None:
        """Failed state can only transition to Idle via RECOVERY_COMPLETE."""
        mgr = StateManager(current_time_fn=lambda: 0.0)
        
        mgr.transition("device_1", "FAILURE_DETECTED")
        
        with pytest.raises(InvalidTransitionError):
            mgr.transition("device_1", "START_PROCESSING")
