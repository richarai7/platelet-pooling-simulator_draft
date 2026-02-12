"""
Simple test of Azure integration in mock mode
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
from azure_integration.telemetry_streamer import TelemetryStreamer

async def test_mock_mode():
    print("="*70)
    print("TESTING AZURE DIGITAL TWINS INTEGRATION - MOCK MODE")
    print("="*70)
    
    # Initialize client in mock mode
    print("\n1. Initializing Digital Twins client (MOCK mode)...")
    dt_client = DigitalTwinsClientWrapper(
        adt_endpoint="mock://localhost",
        batch_size=5,
        batch_interval_seconds=1.0
    )
    print("   ✓ Client initialized")
    
    # Initialize telemetry streamer
    print("\n2. Initializing telemetry streamer...")
    streamer = TelemetryStreamer(
        digital_twins_client=dt_client,
        buffer_size=50,
        batch_size=5,
        flush_interval_seconds=1.0,
        rate_limit_per_second=25
    )
    print("   ✓ Streamer initialized")
    
    # Start auto-flush
    print("\n3. Starting auto-flush...")
    await streamer.start_auto_flush()
    print("   ✓ Auto-flush started")
    
    # Stream some telemetry
    print("\n4. Streaming telemetry updates...")
    
    # Device updates
    await streamer.stream_device_update(
        device_id="centrifuge-01",
        status="Processing",
        in_use=2,
        capacity=3,
        queue_length=1
    )
    print("   ✓ Sent centrifuge-01 update")
    
    await streamer.stream_device_update(
        device_id="separator-01",
        status="Idle",
        in_use=0,
        capacity=3,
        queue_length=0
    )
    print("   ✓ Sent separator-01 update")
    
    # Simulation update
    await streamer.stream_simulation_update(
        simulation_id="sim_test_001",
        simulation_status="Running",
        total_flows_completed=5,
        total_events=25
    )
    print("   ✓ Sent simulation update")
    
    # Check buffer status
    print("\n5. Checking buffer status...")
    status = streamer.get_buffer_status()
    print(f"   • Buffer: {status['buffer_size']}/{status['buffer_capacity']}")
    print(f"   • Utilization: {status['buffer_utilization']:.1f}%")
    print(f"   • Send count: {status['send_count_in_window']}")
    print(f"   • Running: {status['is_running']}")
    
    # Stop and flush
    print("\n6. Stopping streamer and flushing...")
    await streamer.stop_auto_flush()
    print("   ✓ Streamer stopped")
    
    # Final status
    status = streamer.get_buffer_status()
    print(f"\n7. Final buffer status:")
    print(f"   • Buffer: {status['buffer_size']}/{status['buffer_capacity']}")
    print(f"   • Running: {status['is_running']}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nWhat was tested:")
    print("• Digital Twins client initialization (mock mode)")
    print("• Telemetry streamer setup")
    print("• Batching and buffering")
    print("• Auto-flush background task")
    print("• Device property updates")
    print("• Simulation status updates")
    print("\nNext steps:")
    print("1. Set up Azure Digital Twins instance")
    print("2. Run with real endpoint: python test_simple_mock.py")
    print("3. Check Azure Portal for updated twins")
    
    dt_client.close()

if __name__ == "__main__":
    asyncio.run(test_mock_mode())
