"""Process flow controller for managing dependencies and execution order."""

from typing import List, Set, Dict


class FlowController:
    """
    Manages process flow dependencies and execution order.

    Validates device references, dependency graph, and tracks completed flows.
    MVP implementation: basic dependency checking (advanced DAG validation deferred).
    """

    def __init__(self, flows: List[dict], devices: List[str]) -> None:
        """
        Initialize flow controller with validation.

        Args:
            flows: List of flow configurations
            devices: List of valid device IDs

        Raises:
            ValueError: If validation fails
        """
        self._flows = {f["flow_id"]: f for f in flows}
        self._devices = set(devices)
        self._completed: Set[str] = set()
        self._started: Set[str] = set()  # FR21: Track flow start times for start-to-start offsets

        self._validate()

    def _validate(self) -> None:
        """
        Validate flow configuration.

        Checks:
        - Device references exist
        - Dependency references exist
        - No circular dependencies (basic check)

        Raises:
            ValueError: If validation fails
        """
        # Check device references
        for flow_id, flow in self._flows.items():
            if flow["from_device"] not in self._devices:
                raise ValueError(f"Flow {flow_id} references unknown device: {flow['from_device']}")
            if flow["to_device"] not in self._devices:
                raise ValueError(f"Flow {flow_id} references unknown device: {flow['to_device']}")

        # Check dependency references
        for flow_id, flow in self._flows.items():
            deps = flow.get("dependencies") or []
            for dep in deps:
                if dep not in self._flows:
                    raise ValueError(f"Flow {flow_id} references unknown flow dependency: {dep}")

        # Basic circular dependency check
        self._check_circular_dependencies()

    def _check_circular_dependencies(self) -> None:
        """
        Detect circular dependencies in flow graph.

        Uses DFS-based cycle detection.

        Raises:
            ValueError: If circular dependency found
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(flow_id: str) -> bool:
            visited.add(flow_id)
            rec_stack.add(flow_id)

            deps = self._flows[flow_id].get("dependencies") or []
            for dep in deps:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(flow_id)
            return False

        for flow_id in self._flows:
            if flow_id not in visited:
                if has_cycle(flow_id):
                    raise ValueError(f"Circular dependency detected involving {flow_id}")

    def get_executable_flows(self, completed: List[str]) -> List[str]:
        """
        Get flows that can execute given completed flows.

        A flow is executable if all its dependencies are completed.

        Args:
            completed: List of completed flow IDs

        Returns:
            List of executable flow IDs
        """
        completed_set = set(completed) | self._completed
        executable = []

        for flow_id, flow in self._flows.items():
            if flow_id in completed_set:
                continue  # Already completed

            deps = set(flow.get("dependencies") or [])
            if deps.issubset(completed_set):
                executable.append(flow_id)

        return executable

    def mark_completed(self, flow_id: str) -> None:
        """Mark flow as completed."""
        self._completed.add(flow_id)

    def is_completed(self, flow_id: str) -> bool:
        """Check if flow is completed."""
        return flow_id in self._completed

    def mark_started(self, flow_id: str) -> None:
        """
        Mark flow as started (FR21).
        
        Used for start-to-start offset dependency tracking.
        A flow is considered started when it begins processing,
        not when it completes.
        
        Args:
            flow_id: Flow identifier
        """
        self._started.add(flow_id)
    
    def is_started(self, flow_id: str) -> bool:
        """
        Check if flow has started (FR21).
        
        Used for start-to-start offset validation where dependent
        flows can begin once predecessors have started, not completed.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            True if flow has started processing
        """
        return flow_id in self._started
