"""
Telemetry Streaming Service
Streams simulation events to Azure Digital Twins with batching and throttling
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from collections import deque
import time


class TelemetryStreamer:
    """
    Manages real-time streaming of simulation telemetry to Azure Digital Twins
    with buffering, batching, and throttling
    """
    
    def __init__(
        self,
        digital_twins_client,
        buffer_size: int = 100,
        batch_size: int = 10,
        flush_interval_seconds: float = 1.0,
        rate_limit_per_second: int = 50
    ):
        """
        Initialize telemetry streamer
        
        Args:
            digital_twins_client: Instance of DigitalTwinsClientWrapper
            buffer_size: Maximum size of the telemetry buffer
            batch_size: Number of updates to send in each batch
            flush_interval_seconds: Time to wait before auto-flushing
            rate_limit_per_second: Maximum updates per second to ADT
        """
        self.dt_client = digital_twins_client
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self.rate_limit_per_second = rate_limit_per_second
        self.logger = logging.getLogger(__name__)
        
        # Telemetry buffer (FIFO queue)
        self._buffer: deque = deque(maxlen=buffer_size)
        
        # Rate limiting
        self._last_send_time = time.time()
        self._send_count_in_window = 0
        self._window_start_time = time.time()
        
        # Background tasks
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None
        
        # Callbacks for telemetry events
        self._callbacks: List[Callable] = []
        
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback to be called when telemetry is streamed
        Useful for WebSocket broadcasting or logging
        
        Args:
            callback: Function that takes telemetry dict as argument
        """
        self._callbacks.append(callback)
        
    async def stream_device_update(
        self,
        device_id: str,
        status: str,
        in_use: int,
        capacity: int,
        queue_length: int = 0,
        additional_properties: Optional[Dict[str, Any]] = None
    ):
        """
        Stream device state update to Digital Twins
        
        Args:
            device_id: ID of the device
            status: Device status (Idle/Processing/Blocked/Failed)
            in_use: Current number in use
            capacity: Total capacity
            queue_length: Number of items queued
            additional_properties: Additional properties to update
        """
        utilization_rate = (in_use / capacity * 100) if capacity > 0 else 0
        
        properties = {
            "status": status,
            "inUse": in_use,
            "capacity": capacity,
            "utilizationRate": utilization_rate,
            "queueLength": queue_length,
            "lastUpdateTime": datetime.utcnow().isoformat() + "Z"
        }
        
        if additional_properties:
            properties.update(additional_properties)
        
        telemetry = {
            "twin_id": device_id,
            "properties": properties,
            "timestamp": datetime.utcnow(),
            "type": "device_update"
        }
        
        await self._queue_telemetry(telemetry)
        
    async def stream_flow_update(
        self,
        flow_id: str,
        flow_status: str,
        current_device: Optional[str] = None,
        additional_properties: Optional[Dict[str, Any]] = None
    ):
        """
        Stream process flow update to Digital Twins
        
        Args:
            flow_id: ID of the flow
            flow_status: Status (Waiting/InProgress/Completed/Failed)
            current_device: Device currently processing the flow
            additional_properties: Additional properties to update
        """
        properties = {
            "flowStatus": flow_status,
            "lastUpdateTime": datetime.utcnow().isoformat() + "Z"
        }
        
        if current_device:
            properties["currentDevice"] = current_device
        
        if additional_properties:
            properties.update(additional_properties)
        
        telemetry = {
            "twin_id": flow_id,
            "properties": properties,
            "timestamp": datetime.utcnow(),
            "type": "flow_update"
        }
        
        await self._queue_telemetry(telemetry)
        
    async def stream_simulation_update(
        self,
        simulation_id: str,
        simulation_status: str,
        total_flows_completed: int,
        total_events: int,
        additional_properties: Optional[Dict[str, Any]] = None
    ):
        """
        Stream simulation run update to Digital Twins
        
        Args:
            simulation_id: ID of the simulation run
            simulation_status: Status (Initializing/Running/Completed/Failed)
            total_flows_completed: Number of flows completed
            total_events: Number of events processed
            additional_properties: Additional properties to update
        """
        properties = {
            "simulationStatus": simulation_status,
            "totalFlowsCompleted": total_flows_completed,
            "totalEvents": total_events,
            "lastUpdateTime": datetime.utcnow().isoformat() + "Z"
        }
        
        if additional_properties:
            properties.update(additional_properties)
        
        telemetry = {
            "twin_id": simulation_id,
            "properties": properties,
            "timestamp": datetime.utcnow(),
            "type": "simulation_update"
        }
        
        await self._queue_telemetry(telemetry)
        
    async def _queue_telemetry(self, telemetry: Dict[str, Any]):
        """
        Add telemetry to buffer and trigger callbacks
        
        Args:
            telemetry: Telemetry data to queue
        """
        self._buffer.append(telemetry)
        
        # Notify callbacks (e.g., for WebSocket broadcasting)
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(telemetry)
                else:
                    callback(telemetry)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
        
        # Check if we should flush immediately
        if len(self._buffer) >= self.batch_size:
            await self._flush_buffer()
            
    async def _flush_buffer(self):
        """
        Flush buffered telemetry to Digital Twins with rate limiting
        """
        if not self._buffer:
            return
        
        # Rate limiting check
        current_time = time.time()
        if current_time - self._window_start_time >= 1.0:
            # Reset window
            self._window_start_time = current_time
            self._send_count_in_window = 0
        
        # Process telemetry in batches
        batch = []
        while self._buffer and len(batch) < self.batch_size:
            if self._send_count_in_window >= self.rate_limit_per_second:
                # Rate limit reached, wait for next window
                self.logger.debug("Rate limit reached, delaying flush")
                await asyncio.sleep(0.1)
                break
            
            telemetry = self._buffer.popleft()
            batch.append(telemetry)
        
        # Send batch to Digital Twins
        for telemetry in batch:
            try:
                await self.dt_client.update_twin_properties(
                    twin_id=telemetry["twin_id"],
                    properties=telemetry["properties"],
                    flush_immediately=False
                )
                self._send_count_in_window += 1
                self._last_send_time = time.time()
                
            except Exception as e:
                self.logger.error(f"Failed to send telemetry for {telemetry['twin_id']}: {e}")
        
        # Flush the Digital Twins client batch
        await self.dt_client.flush_updates()
        
    async def start_auto_flush(self):
        """
        Start background task for periodic buffer flushing
        """
        if self._running:
            return
        
        self._running = True
        self._flush_task = asyncio.create_task(self._auto_flush_loop())
        self.logger.info("Started auto-flush task")
        
    async def stop_auto_flush(self):
        """
        Stop background flushing task
        """
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_buffer()
        self.logger.info("Stopped auto-flush task")
        
    async def _auto_flush_loop(self):
        """
        Background task that periodically flushes the buffer
        """
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Auto-flush error: {e}")
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """
        Get current buffer status for monitoring
        
        Returns:
            Dictionary with buffer statistics
        """
        return {
            "buffer_size": len(self._buffer),
            "buffer_capacity": self.buffer_size,
            "buffer_utilization": len(self._buffer) / self.buffer_size * 100,
            "send_count_in_window": self._send_count_in_window,
            "rate_limit": self.rate_limit_per_second,
            "is_running": self._running
        }
