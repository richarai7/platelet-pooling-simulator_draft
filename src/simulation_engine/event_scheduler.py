"""Event scheduler with Future Event List (FEL) using heapq."""

import heapq
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Dict


@dataclass(order=True)
class Event:
    """
    Simulation event with timestamp and callback.

    Events are ordered by timestamp, then by insertion order (tie-breaker).
    """

    timestamp: float
    insertion_order: int = field(compare=True)
    event_id: str = field(compare=False)
    callback: Callable[[], None] = field(compare=False)


class EventScheduler:
    """
    Future Event List (FEL) manager using heapq priority queue.

    Maintains events in timestamp order with O(log n) insertion/removal.
    Advances simulation clock event-by-event (no ticking).
    """

    def __init__(self) -> None:
        """Initialize empty event scheduler."""
        self._heap: List[Event] = []
        self._current_time: float = 0.0
        self._insertion_counter: int = 0
        self._event_registry: Dict[str, Event] = {}

    @property
    def current_time(self) -> float:
        """Get current simulation time."""
        return self._current_time

    def schedule(self, timestamp: float, event_id: str, callback: Callable[[], None]) -> None:
        """
        Schedule event at specific timestamp.

        Args:
            timestamp: When event should execute
            event_id: Unique identifier for event
            callback: Function to execute when event fires

        Raises:
            ValueError: If timestamp is in the past
        """
        if timestamp < self._current_time:
            raise ValueError(
                f"Cannot schedule event in the past "
                f"(current={self._current_time}, requested={timestamp})"
            )

        event = Event(
            timestamp=timestamp,
            insertion_order=self._insertion_counter,
            event_id=event_id,
            callback=callback,
        )

        heapq.heappush(self._heap, event)
        self._event_registry[event_id] = event
        self._insertion_counter += 1

    def process_next(self) -> None:
        """
        Process next event in chronological order.

        Advances simulation clock to event timestamp and executes callback.

        Raises:
            RuntimeError: If no events available to process
        """
        if not self._heap:
            raise RuntimeError("No events to process")

        event = heapq.heappop(self._heap)

        # Remove from registry
        if event.event_id in self._event_registry:
            del self._event_registry[event.event_id]

        # Advance simulation clock
        self._current_time = event.timestamp

        # Execute callback
        event.callback()

    def peek_next(self) -> Optional[Event]:
        """
        Inspect next event without processing it.

        Returns:
            Next event or None if scheduler empty
        """
        return self._heap[0] if self._heap else None

    def cancel(self, event_id: str) -> bool:
        """
        Cancel scheduled event before execution.

        Args:
            event_id: ID of event to cancel

        Returns:
            True if event was cancelled, False if not found
        """
        if event_id not in self._event_registry:
            return False

        event = self._event_registry[event_id]
        del self._event_registry[event_id]

        # Mark event as cancelled (heap will skip it during processing)
        # We don't remove from heap directly (expensive O(n) operation)
        # Instead, we'll check registry during process_next

        # Rebuild heap without cancelled event
        self._heap = [e for e in self._heap if e.event_id != event_id]
        heapq.heapify(self._heap)

        return True

    def has_events(self) -> bool:
        """Check if any events pending."""
        return len(self._heap) > 0

    def get_pending_events(self) -> List[Event]:
        """
        Get all pending events in timestamp order.

        Returns:
            Sorted list of pending events
        """
        return sorted(self._heap)
