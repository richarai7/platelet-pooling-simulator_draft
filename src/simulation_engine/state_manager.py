"""Device state management with 4-state model."""

from enum import Enum
from typing import Dict, List, Callable, Optional


class DeviceState(Enum):
    """4-state device model for simulation."""

    IDLE = "Idle"
    PROCESSING = "Processing"
    BLOCKED = "Blocked"
    FAILED = "Failed"


class InvalidTransitionError(Exception):
    """Raised when attempting invalid state transition."""

    pass


class StateManager:
    """
    Manages device states and transitions per state machine spec.

    State Machine (from Technical Addendum A3.2):

    | Current State | Event                  | Next State  |
    |---------------|------------------------|-------------|
    | Idle          | START_PROCESSING       | Processing  |
    | Idle          | FAILURE_DETECTED       | Failed      |
    | Processing    | COMPLETE_PROCESSING    | Idle        |
    | Processing    | FAILURE_DETECTED       | Failed      |
    | Processing    | BACKPRESSURE_DETECTED  | Blocked     |
    | Blocked       | BACKPRESSURE_CLEARED   | Idle        |
    | Blocked       | FAILURE_DETECTED       | Failed      |
    | Failed        | RECOVERY_COMPLETE      | Idle        |
    """

    def __init__(self, current_time_fn: Callable[[], float]) -> None:
        """
        Initialize state manager.

        Args:
            current_time_fn: Function returning current simulation time
        """
        self._get_sim_time = current_time_fn
        self._states: Dict[str, DeviceState] = {}
        self._history: List[dict] = []
        
        # Capacity tracking: {device_id: {'capacity': int, 'active_flows': set}}
        self._device_capacity: Dict[str, Dict] = {}
        
        # Recovery callback: called when device enters FAILED state
        self._recovery_callback: Optional[Callable[[str], None]] = None

        # State transition table (from addendum A3.2)
        self._transitions: Dict[DeviceState, Dict[str, DeviceState]] = {
            DeviceState.IDLE: {
                "START_PROCESSING": DeviceState.PROCESSING,
                "FAILURE_DETECTED": DeviceState.FAILED,
            },
            DeviceState.PROCESSING: {
                "COMPLETE_PROCESSING": DeviceState.IDLE,
                "FAILURE_DETECTED": DeviceState.FAILED,
                "BACKPRESSURE_DETECTED": DeviceState.BLOCKED,
            },
            DeviceState.BLOCKED: {
                "BACKPRESSURE_CLEARED": DeviceState.IDLE,
                "FAILURE_DETECTED": DeviceState.FAILED,
            },
            DeviceState.FAILED: {"RECOVERY_COMPLETE": DeviceState.IDLE},
        }

    def transition(self, device_id: str, event: str) -> DeviceState:
        """
        Execute state transition with validation.

        Args:
            device_id: Device to transition
            event: Event triggering transition

        Returns:
            New device state

        Raises:
            InvalidTransitionError: If transition not allowed
        """
        current_state = self._states.get(device_id, DeviceState.IDLE)

        # Validate transition
        if event not in self._transitions[current_state]:
            raise InvalidTransitionError(
                f"Cannot {event} from {current_state.value} for {device_id}"
            )

        # Execute transition
        new_state = self._transitions[current_state][event]
        self._states[device_id] = new_state

        # Record history
        self._history.append(
            {
                "device_id": device_id,
                "from_state": current_state.value,
                "to_state": new_state.value,
                "event": event,
                "timestamp": self._get_sim_time(),
            }
        )
        
        # Trigger recovery callback if device failed
        if new_state == DeviceState.FAILED and self._recovery_callback:
            self._recovery_callback(device_id)

        return new_state

    def get_state(self, device_id: str) -> DeviceState:
        """
        Get current state of device.

        Args:
            device_id: Device to query

        Returns:
            Current device state (defaults to IDLE)
        """
        return self._states.get(device_id, DeviceState.IDLE)

    def get_history(self, device_id: Optional[str] = None) -> List[dict]:
        """
        Get state transition history.

        Args:
            device_id: Specific device (or None for all devices)

        Returns:
            List of state transition records
        """
        if device_id:
            return [h for h in self._history if h["device_id"] == device_id]
        return self._history.copy()
    
    def initialize_capacity(self, device_id: str, capacity: int) -> None:
        """
        Initialize capacity tracking for a device.
        
        Args:
            device_id: Device to initialize
            capacity: Maximum concurrent flows
        """
        self._device_capacity[device_id] = {
            'capacity': capacity,
            'active_flows': set()
        }
    
    def has_capacity(self, device_id: str) -> bool:
        """
        Check if device has available capacity.
        
        Args:
            device_id: Device to check
            
        Returns:
            True if capacity available, False otherwise
        """
        if device_id not in self._device_capacity:
            return True  # No capacity limits if not initialized
        
        device_info = self._device_capacity[device_id]
        return len(device_info['active_flows']) < device_info['capacity']
    
    def acquire_capacity(self, device_id: str, flow_id: str) -> bool:
        """
        Acquire capacity slot for a flow.
        
        Args:
            device_id: Device to use
            flow_id: Flow acquiring capacity
            
        Returns:
            True if acquired, False if no capacity
        """
        if device_id not in self._device_capacity:
            return True  # No capacity limits
        
        if not self.has_capacity(device_id):
            return False
        
        self._device_capacity[device_id]['active_flows'].add(flow_id)
        return True
    
    def release_capacity(self, device_id: str, flow_id: str) -> None:
        """
        Release capacity slot after flow completes.
        
        Args:
            device_id: Device to release
            flow_id: Flow releasing capacity
        """
        if device_id in self._device_capacity:
            self._device_capacity[device_id]['active_flows'].discard(flow_id)
    
    def get_active_flow_count(self, device_id: str) -> int:
        """
        Get number of active flows on device.
        
        Args:
            device_id: Device to query
            
        Returns:
            Count of active flows
        """
        if device_id not in self._device_capacity:
            return 0
        return len(self._device_capacity[device_id]['active_flows'])
    
    def set_recovery_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback function to call when device enters FAILED state.
        
        Args:
            callback: Function that takes device_id and schedules recovery
        """
        self._recovery_callback = callback
