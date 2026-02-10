"""Tests for EventScheduler module."""
import pytest
from simulation_engine.event_scheduler import EventScheduler, Event


class TestEventScheduler:
    """Test Future Event List and event scheduling."""

    def test_events_processed_in_timestamp_order(self) -> None:
        """Verify events execute in chronological order."""
        scheduler = EventScheduler()
        
        results = []
        scheduler.schedule(timestamp=10.0, event_id="evt_3", callback=lambda: results.append("third"))
        scheduler.schedule(timestamp=5.0, event_id="evt_1", callback=lambda: results.append("first"))
        scheduler.schedule(timestamp=7.5, event_id="evt_2", callback=lambda: results.append("second"))
        
        while scheduler.has_events():
            scheduler.process_next()
        
        assert results == ["first", "second", "third"]

    def test_events_at_same_timestamp_fifo_order(self) -> None:
        """Events at identical timestamp should process in insertion order."""
        scheduler = EventScheduler()
        
        results = []
        scheduler.schedule(timestamp=10.0, event_id="evt_a", callback=lambda: results.append("A"))
        scheduler.schedule(timestamp=10.0, event_id="evt_b", callback=lambda: results.append("B"))
        scheduler.schedule(timestamp=10.0, event_id="evt_c", callback=lambda: results.append("C"))
        
        while scheduler.has_events():
            scheduler.process_next()
        
        assert results == ["A", "B", "C"]

    def test_current_time_advances_with_events(self) -> None:
        """Simulation clock should jump to event timestamps."""
        scheduler = EventScheduler()
        
        assert scheduler.current_time == 0.0
        
        scheduler.schedule(timestamp=5.0, event_id="evt_1", callback=lambda: None)
        scheduler.schedule(timestamp=12.3, event_id="evt_2", callback=lambda: None)
        
        scheduler.process_next()
        assert scheduler.current_time == 5.0
        
        scheduler.process_next()
        assert scheduler.current_time == 12.3

    def test_peek_next_event_without_processing(self) -> None:
        """Should be able to inspect next event without executing it."""
        scheduler = EventScheduler()
        
        scheduler.schedule(timestamp=10.0, event_id="evt_1", callback=lambda: None)
        scheduler.schedule(timestamp=5.0, event_id="evt_2", callback=lambda: None)
        
        next_event = scheduler.peek_next()
        assert next_event is not None
        assert next_event.timestamp == 5.0
        assert next_event.event_id == "evt_2"
        
        # Clock should not advance on peek
        assert scheduler.current_time == 0.0
        assert scheduler.has_events()

    def test_cancel_scheduled_event(self) -> None:
        """Should be able to cancel events before execution."""
        scheduler = EventScheduler()
        
        results = []
        scheduler.schedule(timestamp=5.0, event_id="evt_1", callback=lambda: results.append("A"))
        scheduler.schedule(timestamp=10.0, event_id="evt_2", callback=lambda: results.append("B"))
        scheduler.schedule(timestamp=15.0, event_id="evt_3", callback=lambda: results.append("C"))
        
        # Cancel middle event
        cancelled = scheduler.cancel("evt_2")
        assert cancelled is True
        
        while scheduler.has_events():
            scheduler.process_next()
        
        assert results == ["A", "C"]  # B should be skipped

    def test_cancel_nonexistent_event_returns_false(self) -> None:
        """Cancelling non-existent event should return False."""
        scheduler = EventScheduler()
        
        scheduler.schedule(timestamp=5.0, event_id="evt_1", callback=lambda: None)
        
        assert scheduler.cancel("evt_999") is False

    def test_query_pending_events(self) -> None:
        """Should be able to query all pending events."""
        scheduler = EventScheduler()
        
        scheduler.schedule(timestamp=10.0, event_id="evt_1", callback=lambda: None)
        scheduler.schedule(timestamp=5.0, event_id="evt_2", callback=lambda: None)
        scheduler.schedule(timestamp=7.0, event_id="evt_3", callback=lambda: None)
        
        pending = scheduler.get_pending_events()
        assert len(pending) == 3
        
        # Should return events in timestamp order
        assert [e.event_id for e in pending] == ["evt_2", "evt_3", "evt_1"]

    def test_no_backwards_time_travel(self) -> None:
        """Cannot schedule events in the past."""
        scheduler = EventScheduler()
        
        scheduler.schedule(timestamp=10.0, event_id="evt_1", callback=lambda: None)
        scheduler.process_next()
        
        # Current time is now 10.0, cannot schedule at 5.0
        with pytest.raises(ValueError, match="Cannot schedule event in the past"):
            scheduler.schedule(timestamp=5.0, event_id="evt_past", callback=lambda: None)

    def test_empty_scheduler_has_no_events(self) -> None:
        """Newly created scheduler should be empty."""
        scheduler = EventScheduler()
        
        assert not scheduler.has_events()
        assert scheduler.peek_next() is None
        assert len(scheduler.get_pending_events()) == 0

    def test_process_next_on_empty_raises_error(self) -> None:
        """Processing empty scheduler should raise error."""
        scheduler = EventScheduler()
        
        with pytest.raises(RuntimeError, match="No events to process"):
            scheduler.process_next()

    def test_event_with_parameters(self) -> None:
        """Events should support passing parameters to callbacks."""
        scheduler = EventScheduler()
        
        results = []
        
        def handler(device_id: str, value: int) -> None:
            results.append(f"{device_id}:{value}")
        
        scheduler.schedule(
            timestamp=5.0,
            event_id="evt_1",
            callback=lambda: handler("device_A", 42)
        )
        
        scheduler.process_next()
        assert results == ["device_A:42"]
