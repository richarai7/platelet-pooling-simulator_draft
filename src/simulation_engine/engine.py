"""Main simulation engine orchestrator."""

import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from simulation_engine.config_manager import ConfigManager, SimulationConfig
from simulation_engine.rng import SeededRNG
from simulation_engine.event_scheduler import EventScheduler
from simulation_engine.state_manager import StateManager
from simulation_engine.flow_controller import FlowController

# Constants
FLOW_RETRY_DELAY_SECONDS = 1.0  # Delay before retrying blocked flows
GATE_RETRY_DELAY_SECONDS = 1.0  # Delay before rechecking closed gates
MAX_REAL_TIME_SLEEP_SECONDS = 3600.0  # Maximum sleep duration for real-time mode

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Main discrete event simulation engine.

    Orchestrates all components to execute configured simulation scenarios.
    Domain-agnostic design - works for any industry through configuration.
    Supports dual-speed execution: accelerated (default) or real-time.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize simulation engine.

        Args:
            config: Simulation configuration dictionary
        """
        # Validate and store configuration
        config_mgr = ConfigManager(config)
        self.config: SimulationConfig = config_mgr.validate()

        # Initialize components
        seed = self.config["simulation"]["random_seed"]
        self.rng = SeededRNG(seed)
        self.scheduler = EventScheduler()
        self.state_manager = StateManager(current_time_fn=lambda: self.scheduler.current_time)

        # Extract device IDs for flow controller
        device_ids = [d["id"] for d in self.config["devices"]]
        flows: List[Dict[Any, Any]] = self.config["flows"]  # type: ignore
        self.flow_controller = FlowController(flows, device_ids)

        # Execution mode
        self.execution_mode = self.config["simulation"].get("execution_mode", "accelerated")
        self.speed_multiplier = self.config["simulation"].get("speed_multiplier", 1.0)  # Speed factor for accelerated modes
        self._real_time_start: float = 0.0  # Real-world clock start time

        # Tracking
        self._event_count = 0
        self._flow_executions: Dict[str, int] = {}
        
        # Cancellation and pause support
        self._cancelled = False
        self._paused = False
        self._pause_requested_time: float = 0.0
        
        # Initialize device capacity tracking
        for device in self.config["devices"]:
            capacity = device.get("capacity", 1)
            self.state_manager.initialize_capacity(device["id"], capacity)
        
        # Store device configs for recovery scheduling
        self._device_configs = {d["id"]: d for d in self.config["devices"]}
        
        # Register auto-recovery callback
        self.state_manager.set_recovery_callback(self._schedule_device_recovery)

    def run(self) -> Dict[str, Any]:
        """
        Execute simulation and return results.

        Execution Modes:
        - accelerated: Process events as fast as possible (default)
        - real-time: Sync with system clock for real-time execution
        
        Speed Multiplier (optional):
        - 1.0: Real-time speed (1 sim second = 1 real second)
        - 10.0: 10x faster (1 sim second = 0.1 real seconds)
        - 100.0: 100x faster (1 sim second = 0.01 real seconds)
        - 0 or None: Maximum speed (no waiting)

        Returns:
            Dictionary containing simulation results with metadata, summary,
            device states, and optional history/events
        """
        start_time = time.time()
        
        # Initialize real-time tracking if needed
        if self.execution_mode == "real-time" or self.speed_multiplier > 0:
            self._real_time_start = time.time()

        # Schedule initial flow events
        self._schedule_initial_flows()

        # Process events until duration reached or no more events
        duration = self.config["simulation"]["duration"]
        while self.scheduler.has_events() and not self._cancelled:
            # Handle pause state
            while self._paused and not self._cancelled:
                time.sleep(0.1)  # Check pause state every 100ms
                continue
            
            if self._cancelled:
                break
            
            next_event = self.scheduler.peek_next()
            if next_event and next_event.timestamp > duration:
                break  # Exceeded simulation duration

            # Real-time mode or speed multiplier: wait until system clock catches up
            if next_event and (self.execution_mode == "real-time" or self.speed_multiplier > 0):
                # Calculate target real time based on speed multiplier
                if self.execution_mode == "real-time":
                    time_factor = 1.0  # Real-time = 1:1
                elif self.speed_multiplier > 0:
                    time_factor = 1.0 / self.speed_multiplier  # 10x = 0.1, 100x = 0.01
                else:
                    time_factor = 0  # Maximum speed (no waiting)
                
                if time_factor > 0:
                    target_real_time = self._real_time_start + (next_event.timestamp * time_factor)
                    current_real_time = time.time()
                    if current_real_time < target_real_time:
                        sleep_duration = target_real_time - current_real_time
                        # Validate sleep duration to prevent excessive waits
                        if sleep_duration > MAX_REAL_TIME_SLEEP_SECONDS:
                            logger.warning(
                                f"Sleep duration {sleep_duration}s exceeds max {MAX_REAL_TIME_SLEEP_SECONDS}s. "
                                "Capping sleep time."
                            )
                            sleep_duration = MAX_REAL_TIME_SLEEP_SECONDS
                        if sleep_duration > 0:
                            time.sleep(sleep_duration)

            self.scheduler.process_next()
            self._event_count += 1

        execution_time = time.time() - start_time

        # Generate output
        return self._generate_output(execution_time)

    def _schedule_initial_flows(self) -> None:
        """
        Schedule initial flow execution events with Universal Offset support.
        
        Universal Offset Modes:
        - parallel: All flows start at T=0 (offset=0)
        - sequence: Flow starts after previous flow completes (calculated dynamically)
        - custom: Flow starts at T=0 + start_offset
        """
        flow_start_times: Dict[str, float] = {}
        
        for flow in self.config["flows"]:
            flow_id = flow["flow_id"]
            offset_mode = flow.get("offset_mode", "parallel")  # Default: parallel
            
            # Calculate start time based on offset mode
            if offset_mode == "parallel":
                # Parallel: Start immediately at T=0 ONLY if no dependencies
                # Flows with dependencies will be triggered when dependencies complete
                dependencies = flow.get("dependencies") or []
                if dependencies:
                    # Has dependencies - don't schedule yet, wait for dependency completion
                    flow_start_times[flow_id] = -1.0  # Marker for dependency-driven
                    continue
                start_time = 0.0
                
            elif offset_mode == "custom":
                # Custom: Start at T=0 + specified offset
                start_offset = flow.get("start_offset", 0.0)
                start_time = start_offset
                
            elif offset_mode == "sequence":
                # Sequential: Start after dependencies complete
                dependencies = flow.get("dependencies") or []
                if not dependencies:
                    # Edge case: Independent sequential flow - start at T=0
                    start_time = 0.0
                else:
                    # Has dependencies - will be scheduled by dependency completion
                    flow_start_times[flow_id] = -1.0  # Marker for sequential
                    continue
                
            else:
                # Unknown mode - default to parallel
                start_time = 0.0
            
            flow_start_times[flow_id] = start_time
            
            # Schedule flow execution at calculated time
            def make_callback(fid: str) -> Callable[[], None]:
                return lambda: self._execute_flow(fid)
            
            self.scheduler.schedule(
                timestamp=start_time,
                event_id=f"flow_start_{flow_id}_0",
                callback=make_callback(flow_id),
            )

    def _execute_flow(self, flow_id: str) -> None:
        """
        Execute a single flow with Finish-to-Start prerequisite checking and gate validation.

        Args:
            flow_id: Flow to execute
        """
        try:
            # CHECK IF ALREADY COMPLETED FIRST: Don't re-execute completed flows
            if self.flow_controller.is_completed(flow_id):
                logger.debug(f"Flow {flow_id} already completed - skipping re-execution")
                return
            
            # Find flow config
            flow = next((f for f in self.config["flows"] if f["flow_id"] == flow_id), None)
            if not flow:
                logger.warning(f"Flow {flow_id} not found in configuration")
                return

            # CHECK GATES: Verify all required global conditions are active
            required_gates = flow.get("required_gates") or []
            gates = self.config.get("gates", {})
            for gate_name in required_gates:
                if not gates.get(gate_name, False):
                    # Gate is closed - reschedule this flow to check later
                    def make_gate_retry_callback(fid: str) -> Callable[[], None]:
                        return lambda: self._execute_flow(fid)
                    
                    self.scheduler.schedule(
                        timestamp=self.scheduler.current_time + GATE_RETRY_DELAY_SECONDS,
                        event_id=f"flow_gate_retry_{flow_id}_{self.scheduler.current_time}",
                        callback=make_gate_retry_callback(flow_id),
                    )
                    return  # Don't execute while gate is closed

            # FINISH-TO-START: Check if all prerequisite flows are completed
            dependencies = flow.get("dependencies") or []
            if dependencies:
                # Check if all dependencies are completed
                for dep_flow_id in dependencies:
                    if not self.flow_controller.is_completed(dep_flow_id):
                        # Prerequisites not met - reschedule this flow to check later
                        def make_retry_callback(fid: str) -> Callable[[], None]:
                            return lambda: self._execute_flow(fid)
                        
                        self.scheduler.schedule(
                            timestamp=self.scheduler.current_time + FLOW_RETRY_DELAY_SECONDS,
                            event_id=f"flow_retry_{flow_id}_{self.scheduler.current_time}",
                            callback=make_retry_callback(flow_id),
                        )
                        return  # Don't execute yet

            # Track execution
            self._flow_executions[flow_id] = self._flow_executions.get(flow_id, 0) + 1

            # BACKPRESSURE: Check if downstream device has capacity
            to_device = flow["to_device"]
            from_device = flow["from_device"]
            
            if not self.state_manager.has_capacity(to_device):
                # Downstream is full - enter BLOCKED state
                current_state = self.state_manager.get_state(from_device)
                
                if current_state.value == "Idle":
                    # Haven't started yet - just wait
                    pass
                elif current_state.value == "Processing":
                    self.state_manager.transition(from_device, "BACKPRESSURE_DETECTED")
                
                # Reschedule flow to check capacity later
                def make_backpressure_retry_callback(fid: str) -> Callable[[], None]:
                    return lambda: self._execute_flow(fid)
                
                self.scheduler.schedule(
                    timestamp=self.scheduler.current_time + FLOW_RETRY_DELAY_SECONDS,
                    event_id=f"flow_backpressure_retry_{flow_id}_{self.scheduler.current_time}",
                    callback=make_backpressure_retry_callback(flow_id),
                )
                logger.debug(f"Flow {flow_id} blocked - downstream {to_device} at capacity")
                return  # Don't execute - waiting for downstream capacity

            # Acquire capacity on source device
            if not self.state_manager.acquire_capacity(from_device, flow_id):
                # No capacity on source device - retry later
                def make_capacity_retry_callback(fid: str) -> Callable[[], None]:
                    return lambda: self._execute_flow(fid)
                
                self.scheduler.schedule(
                    timestamp=self.scheduler.current_time + FLOW_RETRY_DELAY_SECONDS,
                    event_id=f"flow_capacity_retry_{flow_id}_{self.scheduler.current_time}",
                    callback=make_capacity_retry_callback(flow_id),
                )
                logger.debug(f"Flow {flow_id} blocked - source {from_device} at capacity")
                return
            
            # Also acquire capacity on destination device (backpressure prevention)
            if not self.state_manager.acquire_capacity(to_device, flow_id):
                # Release source capacity since we can't proceed
                self.state_manager.release_capacity(from_device, flow_id)
                
                # Retry later when destination has capacity
                def make_dest_capacity_retry_callback(fid: str) -> Callable[[], None]:
                    return lambda: self._execute_flow(fid)
                
                self.scheduler.schedule(
                    timestamp=self.scheduler.current_time + FLOW_RETRY_DELAY_SECONDS,
                    event_id=f"flow_dest_capacity_retry_{flow_id}_{self.scheduler.current_time}",
                    callback=make_dest_capacity_retry_callback(flow_id),
                )
                logger.debug(f"Flow {flow_id} blocked - destination {to_device} at capacity")
                return
            
            # Clear BLOCKED state if was blocked
            current_state = self.state_manager.get_state(from_device)
            if current_state.value == "Blocked":
                self.state_manager.transition(from_device, "BACKPRESSURE_CLEARED")

            # Transition source device to Processing
            current_state = self.state_manager.get_state(from_device)

            if current_state.value == "Idle":
                self.state_manager.transition(from_device, "START_PROCESSING")

            # Sample random process time
            min_time, max_time = flow["process_time_range"]
            process_duration = self.rng.uniform(min_time, max_time)

            # Schedule completion event
            completion_time = self.scheduler.current_time + process_duration
            
            def make_completion_callback(fid: str) -> Callable[[], None]:
                return lambda: self._complete_flow(fid)
            
            self.scheduler.schedule(
                timestamp=completion_time,
                event_id=f"flow_complete_{flow_id}_{self._event_count}",
                callback=make_completion_callback(flow_id),
            )
        except Exception as e:
            logger.error(f"Error executing flow {flow_id}: {e}")
            # Don't re-raise - log and continue simulation with other flows
            # This prevents one bad flow from crashing entire simulation

    def _complete_flow(self, flow_id: str) -> None:
        """
        Complete flow execution and trigger dependent flows.

        Args:
            flow_id: Flow that completed
        """
        try:
            # Find flow config
            flow = next((f for f in self.config["flows"] if f["flow_id"] == flow_id), None)
            if not flow:
                logger.warning(f"Flow {flow_id} not found in configuration during completion")
                return

            # Transition source device back to Idle
            from_device = flow["from_device"]
            to_device = flow["to_device"]
            current_state = self.state_manager.get_state(from_device)

            if current_state.value == "Processing":
                self.state_manager.transition(from_device, "COMPLETE_PROCESSING")
            
            # Release capacity on both source and destination devices
            self.state_manager.release_capacity(from_device, flow_id)
            self.state_manager.release_capacity(to_device, flow_id)

            # Mark flow as completed in controller
            self.flow_controller.mark_completed(flow_id)

            # SEQUENTIAL MODE: Trigger any flows waiting for this one (Finish-to-Start)
            self._trigger_dependent_flows(flow_id)
        except Exception as e:
            logger.error(f"Error completing flow {flow_id}: {e}")
            # Log error but don't crash - flow completion failure shouldn't stop simulation

    def _trigger_dependent_flows(self, completed_flow_id: str) -> None:
        """
        Trigger flows that were waiting for the completed flow.

        Args:
            completed_flow_id: Flow that just completed
        """
        # Find all flows that depend on this one
        for flow in self.config["flows"]:
            dependencies = flow.get("dependencies") or []
            
            # If this flow was waiting for the completed flow
            if completed_flow_id in dependencies:
                # Check if ALL dependencies are now complete
                all_deps_complete = all(
                    self.flow_controller.is_completed(dep) 
                    for dep in dependencies
                )
                
                if all_deps_complete and not self.flow_controller.is_completed(flow["flow_id"]):
                    # Schedule this flow to execute now
                    flow_id = flow["flow_id"]
                    
                    def make_callback(fid: str) -> Callable[[], None]:
                        return lambda: self._execute_flow(fid)
                    
                    self.scheduler.schedule(
                        timestamp=self.scheduler.current_time,  # Execute immediately
                        event_id=f"flow_dep_{flow_id}_{self.scheduler.current_time}",
                        callback=make_callback(flow_id),
                    )

    def _generate_output(self, execution_time: float) -> Dict[str, Any]:
        """
        Generate structured output dictionary.

        Args:
            execution_time: Wall clock execution time in seconds

        Returns:
            Complete simulation results
        """
        output = {
            "metadata": {
                "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "duration": self.config["simulation"]["duration"],
                "random_seed": self.config["simulation"]["random_seed"],
                "completed_at": datetime.now().isoformat(),
                "engine_version": "0.1.0",
            },
            "summary": {
                "total_events": self._event_count,
                "total_flows_completed": sum(self._flow_executions.values()),
                "devices_count": len(self.config["devices"]),
                "simulation_time_seconds": self.scheduler.current_time,
                "execution_time_seconds": round(execution_time, 2),
            },
            "device_states": self._get_final_device_states(),
        }

        # Add optional sections based on output_options
        if self.config["output_options"].get("include_history"):
            output["state_history"] = self.state_manager.get_history()

        if self.config["output_options"].get("include_events"):
            output["event_timeline"] = self._get_event_timeline()

        output["flows_executed"] = self._get_flow_execution_summary()

        # Calculate KPIs
        from simulation_engine.kpi_calculator import KPICalculator
        kpi_calc = KPICalculator(output, self.config)
        output["kpis"] = kpi_calc.calculate_all_kpis()

        return output

    def _get_final_device_states(self) -> list:
        """Get final state of all devices."""
        states = []
        for device in self.config["devices"]:
            device_id = device["id"]
            final_state = self.state_manager.get_state(device_id)
            history = self.state_manager.get_history(device_id)

            states.append(
                {
                    "device_id": device_id,
                    "final_state": final_state.value,
                    "state_changes": len(history),
                }
            )

        return states

    def _get_event_timeline(self) -> list:
        """Get timeline of all events."""
        # For MVP, return state history as event timeline
        return self.state_manager.get_history()

    def _get_flow_execution_summary(self) -> list:
        """Get summary of flow executions."""
        summary = []
        for flow in self.config["flows"]:
            flow_id = flow["flow_id"]
            exec_count = self._flow_executions.get(flow_id, 0)

            summary.append({"flow_id": flow_id, "execution_count": exec_count})

        return summary

    def cancel(self) -> None:
        """
        Request cancellation of running simulation.
        
        Simulation will stop at next event processing and return partial results.
        """
        self._cancelled = True
        logger.info("Simulation cancellation requested")
    
    def pause(self) -> None:
        """
        Request pause of running simulation.
        
        Only effective in real-time mode. Simulation will pause at next event processing.
        """
        if self.execution_mode == "real-time" or self.speed_multiplier > 0:
            self._paused = True
            self._pause_requested_time = time.time()
            logger.info("Simulation pause requested")
        else:
            logger.warning("Pause not supported in accelerated mode")
    
    def resume(self) -> None:
        """
        Resume a paused simulation.
        
        Adjusts real-time tracking to account for pause duration.
        """
        if self._paused:
            pause_duration = time.time() - self._pause_requested_time
            self._real_time_start += pause_duration  # Adjust for pause time
            self._paused = False
            logger.info(f"Simulation resumed after {pause_duration:.2f}s pause")
        else:
            logger.warning("Simulation is not paused")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status.
        
        Returns:
            Dictionary with simulation state information
        """
        return {
            "current_time": self.scheduler.current_time if hasattr(self, 'scheduler') else 0,
            "event_count": self._event_count,
            "is_running": hasattr(self, 'scheduler') and self.scheduler.has_events(),
            "is_paused": self._paused,
            "is_cancelled": self._cancelled,
            "execution_mode": self.execution_mode
        }
    
    def _schedule_device_recovery(self, device_id: str) -> None:
        """
        Schedule automatic recovery for a failed device.
        
        Args:
            device_id: Device that failed
        """
        try:
            device_config = self._device_configs.get(device_id)
            if not device_config:
                logger.warning(f"Cannot schedule recovery - device {device_id} config not found")
                return
            
            recovery_range = device_config.get("recovery_time_range")
            if not recovery_range:
                logger.info(f"Device {device_id} has no recovery_time_range - will not auto-recover")
                return
            
            # Sample recovery time
            min_time, max_time = recovery_range
            recovery_duration = self.rng.uniform(min_time, max_time)
            
            # Schedule recovery completion
            recovery_time = self.scheduler.current_time + recovery_duration
            
            def make_recovery_callback(dev_id: str) -> Callable[[], None]:
                return lambda: self._complete_device_recovery(dev_id)
            
            self.scheduler.schedule(
                timestamp=recovery_time,
                event_id=f"device_recovery_{device_id}_{self.scheduler.current_time}",
                callback=make_recovery_callback(device_id),
            )
            
            logger.info(f"Device {device_id} will recover in {recovery_duration:.1f}s at T={recovery_time:.1f}")
        except Exception as e:
            logger.error(f"Error scheduling recovery for device {device_id}: {e}")
    
    def _complete_device_recovery(self, device_id: str) -> None:
        """
        Complete device recovery - transition from FAILED back to IDLE.
        
        Args:
            device_id: Device to recover
        """
        try:
            current_state = self.state_manager.get_state(device_id)
            if current_state.value == "Failed":
                self.state_manager.transition(device_id, "RECOVERY_COMPLETE")
                logger.info(f"Device {device_id} recovered and returned to IDLE state")
        except Exception as e:
            logger.error(f"Error completing recovery for device {device_id}: {e}")
