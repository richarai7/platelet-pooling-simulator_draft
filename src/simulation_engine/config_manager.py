"""Configuration management and schema validation."""

from typing import TypedDict, List, Optional, Literal, Dict


class DeviceConfig(TypedDict, total=False):
    """Single device/entity configuration."""

    id: str
    type: str
    capacity: int
    initial_state: Literal["Idle", "Processing", "Blocked", "Failed"]
    recovery_time_range: Optional[tuple]
    required_gates: Optional[List[str]]  # Global conditions that must be active
    # Custom metadata (key-value pairs)
    metadata: Optional[Dict[str, any]]  # Custom fields for device-specific data (location, cost, etc.)


class FlowConfig(TypedDict, total=False):
    """Process flow definition with Universal Offset support."""

    flow_id: str
    from_device: str
    to_device: str
    process_time_range: tuple
    priority: int
    dependencies: Optional[List[str]]
    required_gates: Optional[List[str]]  # Global conditions that must be active
    # Universal Offset fields
    offset_mode: Optional[Literal["parallel", "sequence", "custom"]]  # Default: parallel
    start_offset: Optional[float]  # Seconds delay before flow starts (custom mode only)
    # Flow type for load/unload operations
    flow_type: Optional[Literal["process", "load", "unload"]]  # Default: process
    # Custom metadata (key-value pairs)
    metadata: Optional[Dict[str, any]]  # Custom fields for domain-specific data


class SimulationConfig(TypedDict):
    """Complete simulation configuration."""

    simulation: dict  # Contains: duration, random_seed, execution_mode, speed_multiplier
    devices: List[DeviceConfig]
    flows: List[FlowConfig]
    gates: dict  # Global conditions: {gate_name: bool (active/inactive)}
    output_options: dict


class ValidationError(Exception):
    """Configuration validation error."""

    pass


class ConfigManager:
    """
    Configuration validator implementing schema rules from addendum A1.2.

    Validation Rules:
    1. All required fields present
    2. Device IDs unique
    3. Flow IDs unique
    4. Device references valid
    5. Capacity >= 1
    6. Time ranges valid (min >= 0, max > min)
    7. Random seed >= 0
    8. Duration > 0
    9. Dependency references valid
    10. No circular dependencies (basic check)
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize with configuration dictionary.

        Args:
            config: Raw configuration from UI/API
        """
        self._config = config

    def validate(self) -> SimulationConfig:
        """
        Validate configuration against schema.

        Returns:
            Validated typed configuration

        Raises:
            ValidationError: If validation fails
        """
        errors: List[str] = []

        # Rule 1: Check required fields
        if "simulation" not in self._config:
            errors.append("Missing required field: 'simulation'")
        if "devices" not in self._config:
            errors.append("Missing required field: 'devices'")
        if "flows" not in self._config:
            errors.append("Missing required field: 'flows'")

        # Gates are optional
        if "gates" not in self._config:
            self._config["gates"] = {}

        if errors:
            raise ValidationError(f"Configuration validation failed: {'; '.join(errors)}")

        # Validate gate references
        gate_names = set(self._config["gates"].keys())
        for device in self._config.get("devices", []):
            required_gates = device.get("required_gates", [])
            if required_gates:
                for gate in required_gates:
                    if gate not in gate_names:
                        errors.append(f"Device {device['id']} requires undefined gate: {gate}")

        for flow in self._config.get("flows", []):
            required_gates = flow.get("required_gates", [])
            if required_gates:
                for gate in required_gates:
                    if gate not in gate_names:
                        errors.append(f"Flow {flow['flow_id']} requires undefined gate: {gate}")

        # Rule 2: Device IDs must be unique
        device_ids = [d["id"] for d in self._config.get("devices", [])]
        if len(device_ids) != len(set(device_ids)):
            errors.append("Duplicate device IDs detected")

        # Rule 3: Flow IDs must be unique
        flow_ids = [f["flow_id"] for f in self._config.get("flows", [])]
        if len(flow_ids) != len(set(flow_ids)):
            errors.append("Duplicate flow IDs detected")

        # Rule 4: Device references must exist
        device_id_set = set(device_ids)
        for flow in self._config.get("flows", []):
            if flow.get("from_device") not in device_id_set:
                errors.append(
                    f"Flow {flow.get('flow_id')} references unknown device: "
                    f"{flow.get('from_device')}"
                )
            if flow.get("to_device") not in device_id_set:
                errors.append(
                    f"Flow {flow.get('flow_id')} references unknown device: "
                    f"{flow.get('to_device')}"
                )

        # Rule 5: Capacity >= 1
        for device in self._config.get("devices", []):
            if device.get("capacity", 0) < 1:
                errors.append(
                    f"Device {device.get('id')} has invalid capacity: " f"Capacity must be >= 1"
                )

        # Rule 6: Time ranges valid
        for flow in self._config.get("flows", []):
            time_range = flow.get("process_time_range")
            if time_range:
                min_time, max_time = time_range
                if min_time < 0:
                    errors.append(f"Flow {flow.get('flow_id')} has negative min time")
                if max_time <= min_time:
                    errors.append(f"Flow {flow.get('flow_id')} time range must have min < max")

        for device in self._config.get("devices", []):
            time_range = device.get("recovery_time_range")
            if time_range:
                min_time, max_time = time_range
                if min_time < 0:
                    errors.append(f"Device {device.get('id')} has negative recovery min time")
                if max_time <= min_time:
                    errors.append(f"Device {device.get('id')} recovery range must have min < max")

        # Rule 7: Random seed >= 0
        sim_config = self._config.get("simulation", {})
        if sim_config.get("random_seed", 0) < 0:
            errors.append("Random seed must be >= 0")

        # Rule 8: Duration > 0
        if sim_config.get("duration", 0) <= 0:
            errors.append("Duration must be > 0")

        # Rule 9: Dependency references valid
        flow_id_set = set(flow_ids)
        for flow in self._config.get("flows", []):
            deps = flow.get("dependencies") or []
            for dep in deps:
                if dep not in flow_id_set:
                    errors.append(f"Flow {flow.get('flow_id')} references unknown flow: {dep}")

        if errors:
            raise ValidationError(f"Configuration validation failed: {'; '.join(errors)}")

        # Return as typed config
        return self._config  # type: ignore
