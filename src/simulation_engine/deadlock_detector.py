"""Deadlock detection for simulation engine (FR22 implementation)."""

import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DeadlockType(Enum):
    """Types of deadlock scenarios."""
    TIMEOUT = "timeout"  # Device blocked too long
    CIRCULAR_WAIT = "circular_wait"  # Cycle in wait-for graph


@dataclass
class DeadlockInfo:
    """Information about a detected deadlock."""
    type: DeadlockType
    involved_devices: List[str]
    involved_flows: List[str]
    detection_time: float
    message: str
    wait_chain: Optional[List[str]] = None  # For circular waits


class DeadlockDetector:
    """
    Detects deadlock scenarios in simulation using dual-approach detection.
    
    Implements FR22 requirements:
    - Timeout-based detection: Identifies devices blocked too long
    - Graph-based detection: Finds circular wait-for relationships
    - Clear error reporting with involved devices
    - Support for graceful simulation termination
    
    Detection Strategies:
    1. Timeout Detection: Simple, fast, catches all stalls
    2. Graph Analysis: Precise, identifies exact circular dependencies
    """

    def __init__(self, timeout_threshold: float = 300.0) -> None:
        """
        Initialize deadlock detector.
        
        Args:
            timeout_threshold: Maximum seconds a device can be blocked (default: 5 minutes)
        """
        self.timeout_threshold = timeout_threshold
        
        # Track when each device entered BLOCKED state
        self._blocked_since: Dict[str, float] = {}
        
        # Track current wait-for relationships: device -> {flows waiting for}
        self._waiting_for: Dict[str, Set[str]] = {}
        
        # Detected deadlocks (don't report same deadlock multiple times)
        self._detected_deadlocks: Set[str] = set()
        
        logger.info(f"DeadlockDetector initialized with {timeout_threshold}s timeout threshold")
    
    def register_blocked(self, device_id: str, current_time: float, waiting_for_device: Optional[str] = None) -> None:
        """
        Register that a device has entered BLOCKED state.
        
        Args:
            device_id: Device that became blocked
            current_time: Simulation time when blocking occurred
            waiting_for_device: Device that this device is waiting for (if known)
        """
        if device_id not in self._blocked_since:
            self._blocked_since[device_id] = current_time
            logger.debug(f"Device {device_id} entered BLOCKED state at T={current_time:.2f}")
        
        # Track wait-for relationship
        if waiting_for_device:
            if device_id not in self._waiting_for:
                self._waiting_for[device_id] = set()
            self._waiting_for[device_id].add(waiting_for_device)
            logger.debug(f"Device {device_id} waiting for {waiting_for_device}")
    
    def register_unblocked(self, device_id: str) -> None:
        """
        Register that a device has exited BLOCKED state.
        
        Args:
            device_id: Device that became unblocked
        """
        if device_id in self._blocked_since:
            del self._blocked_since[device_id]
            logger.debug(f"Device {device_id} cleared BLOCKED state")
        
        # Clear wait-for relationships
        if device_id in self._waiting_for:
            del self._waiting_for[device_id]
        
        # Remove as target from other devices' wait lists
        for device, waiting_set in self._waiting_for.items():
            waiting_set.discard(device_id)
    
    def check_deadlock(self, current_time: float) -> Optional[DeadlockInfo]:
        """
        Check for deadlock conditions using both detection strategies.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            DeadlockInfo if deadlock detected, None otherwise
        """
        # Strategy 1: Timeout-based detection
        timeout_deadlock = self._check_timeout_deadlock(current_time)
        if timeout_deadlock:
            return timeout_deadlock
        
        # Strategy 2: Graph-based circular wait detection
        cycle_deadlock = self._check_circular_wait_deadlock(current_time)
        if cycle_deadlock:
            return cycle_deadlock
        
        return None
    
    def _check_timeout_deadlock(self, current_time: float) -> Optional[DeadlockInfo]:
        """
        Check if any device has been blocked longer than timeout threshold.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            DeadlockInfo if timeout exceeded, None otherwise
        """
        for device_id, blocked_since in self._blocked_since.items():
            blocked_duration = current_time - blocked_since
            
            if blocked_duration > self.timeout_threshold:
                # Generate unique deadlock key to avoid duplicates
                deadlock_key = f"timeout_{device_id}_{int(blocked_since)}"
                
                if deadlock_key not in self._detected_deadlocks:
                    self._detected_deadlocks.add(deadlock_key)
                    
                    # Find what this device is waiting for
                    waiting_for = list(self._waiting_for.get(device_id, set()))
                    
                    message = (
                        f"Timeout deadlock: Device '{device_id}' has been BLOCKED for "
                        f"{blocked_duration:.1f}s (threshold: {self.timeout_threshold}s). "
                    )
                    
                    if waiting_for:
                        message += f"Waiting for: {', '.join(waiting_for)}"
                    else:
                        message += "No downstream capacity available."
                    
                    logger.error(message)
                    
                    return DeadlockInfo(
                        type=DeadlockType.TIMEOUT,
                        involved_devices=[device_id] + waiting_for,
                        involved_flows=[],  # Not tracking specific flows in timeout detection
                        detection_time=current_time,
                        message=message
                    )
        
        return None
    
    def _check_circular_wait_deadlock(self, current_time: float) -> Optional[DeadlockInfo]:
        """
        Detect circular wait-for relationships using DFS cycle detection.
        
        Uses wait-for graph where edge A->B means "device A is waiting for device B".
        A cycle indicates circular blocking (deadlock).
        
        Args:
            current_time: Current simulation time
            
        Returns:
            DeadlockInfo if cycle detected, None otherwise
        """
        if not self._waiting_for:
            return None  # No wait relationships
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        
        def find_cycle_dfs(device: str) -> Optional[List[str]]:
            """DFS to find cycle in wait-for graph."""
            visited.add(device)
            rec_stack.add(device)
            path.append(device)
            
            # Check all devices this device is waiting for
            for waiting_for_device in self._waiting_for.get(device, set()):
                if waiting_for_device not in visited:
                    if cycle := find_cycle_dfs(waiting_for_device):
                        return cycle
                elif waiting_for_device in rec_stack:
                    # Cycle detected! Extract the cycle from path
                    cycle_start_idx = path.index(waiting_for_device)
                    cycle = path[cycle_start_idx:] + [waiting_for_device]
                    return cycle
            
            path.pop()
            rec_stack.remove(device)
            return None
        
        # Check all devices in wait-for graph
        for device in list(self._waiting_for.keys()):
            if device not in visited:
                if cycle := find_cycle_dfs(device):
                    # Generate unique deadlock key
                    cycle_key = "_".join(sorted(cycle))
                    deadlock_key = f"cycle_{cycle_key}"
                    
                    if deadlock_key not in self._detected_deadlocks:
                        self._detected_deadlocks.add(deadlock_key)
                        
                        # Build wait chain description
                        wait_chain_str = " -> ".join(cycle)
                        
                        message = (
                            f"Circular wait deadlock detected: {wait_chain_str}. "
                            f"Devices are waiting in a circle, creating a deadlock. "
                            f"Involved: {', '.join(set(cycle))}"
                        )
                        
                        logger.error(message)
                        
                        return DeadlockInfo(
                            type=DeadlockType.CIRCULAR_WAIT,
                            involved_devices=list(set(cycle)),
                            involved_flows=[],
                            detection_time=current_time,
                            message=message,
                            wait_chain=cycle
                        )
        
        return None
    
    def get_blocked_devices(self) -> List[Tuple[str, float]]:
        """
        Get list of currently blocked devices with their blocking duration.
        
        Returns:
            List of (device_id, blocked_since_time) tuples
        """
        return list(self._blocked_since.items())
    
    def get_wait_graph(self) -> Dict[str, List[str]]:
        """
        Get current wait-for graph.
        
        Returns:
            Dictionary mapping device_id -> list of devices it's waiting for
        """
        return {device: list(waiting) for device, waiting in self._waiting_for.items()}
    
    def reset(self) -> None:
        """Reset detector state (for new simulation run)."""
        self._blocked_since.clear()
        self._waiting_for.clear()
        self._detected_deadlocks.clear()
        logger.info("DeadlockDetector reset")
    
    def get_statistics(self) -> Dict:
        """
        Get detector statistics.
        
        Returns:
            Dictionary with detection statistics
        """
        return {
            "blocked_devices_count": len(self._blocked_since),
            "wait_relationships_count": sum(len(s) for s in self._waiting_for.values()),
            "deadlocks_detected": len(self._detected_deadlocks),
            "timeout_threshold": self.timeout_threshold
        }
