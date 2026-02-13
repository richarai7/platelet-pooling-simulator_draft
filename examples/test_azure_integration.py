"""
Test Azure Digital Twins Integration End-to-End
Demonstrates complete flow from simulation to Azure Digital Twins
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation_engine import SimulationEngine
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
from azure_integration.telemetry_streamer import TelemetryStreamer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample simulation configuration
SAMPLE_CONFIG = {
    "simulation": {
        "duration": 3600,  # 1 hour
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    "output_options": {
        "include_history": True,
        "include_flow_details": True,
        "include_events": True
    },
    "devices": [
        {
            "id": "centrifuge-01",
            "type": "centrifuge",
            "capacity": 3,  # Increased capacity
            "initial_state": "Idle",
            "recovery_time_range": (10, 20)  # Shorter recovery time
        },
        {
            "id": "separator-01",
            "type": "separator",
            "capacity": 3,  # Increased capacity
            "initial_state": "Idle",
            "recovery_time_range": (10, 20)
        },
        {
            "id": "storage-01",
            "type": "storage",
            "capacity": 50,  # Large capacity
            "initial_state": "Idle",
            "recovery_time_range": None  # No recovery needed
        }
    ],
    "flows": [
        {
            "flow_id": "batch_001_flow_01",
            "from_device": "centrifuge-01",
            "to_device": "separator-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": None
        },
        {
            "flow_id": "batch_001_flow_02",
            "from_device": "separator-01",
            "to_device": "storage-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": ["batch_001_flow_01"]
        },
        # Batch 2
        {
            "flow_id": "batch_002_flow_01",
            "from_device": "centrifuge-01",
            "to_device": "separator-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": None
        },
        {
            "flow_id": "batch_002_flow_02",
            "from_device": "separator-01",
            "to_device": "storage-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": ["batch_002_flow_01"]
        },
        # Batch 3
        {
            "flow_id": "batch_003_flow_01",
            "from_device": "centrifuge-01",
            "to_device": "separator-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": None
        },
        {
            "flow_id": "batch_003_flow_02",
            "from_device": "separator-01",
            "to_device": "storage-01",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": ["batch_003_flow_01"]
        }
    ]
}


class SimulationWithTelemetry:
    """Wrapper that streams simulation events to Azure Digital Twins"""
    
    def __init__(self, config, adt_endpoint, stream_mode="direct"):
        """
        Initialize simulation with telemetry streaming
        
        Args:
            config: Simulation configuration
            adt_endpoint: Azure Digital Twins endpoint
            stream_mode: "direct" or "function" mode
        """
        self.config = config
        self.adt_endpoint = adt_endpoint
        self.stream_mode = stream_mode
        
        # Initialize Digital Twins client
        self.dt_client = DigitalTwinsClientWrapper(
            adt_endpoint=adt_endpoint,
            batch_size=10,
            batch_interval_seconds=1.0
        )
        
        # Initialize telemetry streamer
        self.streamer = TelemetryStreamer(
            digital_twins_client=self.dt_client,
            buffer_size=100,
            batch_size=10,
            flush_interval_seconds=1.0,
            rate_limit_per_second=50
        )
        
        # Simulation engine
        self.engine = None
        self.simulation_id = None
        
    async def run_simulation_with_streaming(self):
        """Run simulation and stream telemetry to Azure Digital Twins"""
        
        logger.info("=" * 80)
        logger.info("AZURE DIGITAL TWINS INTEGRATION TEST")
        logger.info("=" * 80)
        
        # Start telemetry auto-flush
        await self.streamer.start_auto_flush()
        
        try:
            # Initialize simulation
            logger.info("\n1. Initializing simulation engine...")
            self.engine = SimulationEngine(self.config)
            self.simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create simulation twin in ADT
            logger.info(f"2. Creating simulation twin: {self.simulation_id}")
            await self.dt_client.create_or_update_twin(
                twin_id=self.simulation_id,
                model_id="dtmi:platelet:Simulation;1",
                properties={
                    "simulationId": self.simulation_id,
                    "scenarioName": "Test Scenario",
                    "startTime": datetime.now(timezone.utc).isoformat(),
                    "simulationStatus": "Initializing",
                    "totalFlowsCompleted": 0,
                    "totalEvents": 0
                }
            )
            
            # Update simulation status to Running
            await self.streamer.stream_simulation_update(
                simulation_id=self.simulation_id,
                simulation_status="Running",
                total_flows_completed=0,
                total_events=0
            )
            
            logger.info("3. Running simulation...")
            logger.info("   (Streaming telemetry to Azure Digital Twins)")
            
            # Run simulation (this is synchronous, telemetry will stream after)
            result = self.engine.run()
            
            logger.info(f"\n4. Simulation complete!")
            logger.info(f"   ✓ Flows completed: {result['summary']['total_flows_completed']}")
            logger.info(f"   ✓ Total events: {result['summary']['total_events']}")
            logger.info(f"   ✓ Simulation time: {result['summary']['simulation_time_seconds']} seconds")
            logger.info(f"   ✓ Execution time: {result['summary']['execution_time_seconds']:.2f} seconds")
            
            # Stream final device states to ADT
            logger.info("\n5. Streaming final device states to Azure Digital Twins...")
            
            # Get state history if available
            state_history_all = result.get('state_history', [])
            
            for device in result['device_states']:
                device_id = device['device_id']
                
                # Find device config for capacity
                device_config = next(
                    (d for d in self.config['devices'] if d['id'] == device_id),
                    None
                )
                capacity = device_config.get('capacity', 1) if device_config else 1
                
                # Calculate time-in-state metrics from state history
                device_history = [h for h in state_history_all if h.get('device_id') == device_id]
                total_idle = sum(h.get('duration', 0) for h in device_history if h.get('state') == 'Idle')
                total_processing = sum(h.get('duration', 0) for h in device_history if h.get('state') == 'Processing')
                total_blocked = sum(h.get('duration', 0) for h in device_history if h.get('state') == 'Blocked')
                
                await self.streamer.stream_device_update(
                    device_id=device_id,
                    status=device['final_state'],
                    in_use=0,  # Final state, nothing in use
                    capacity=capacity,
                    queue_length=0,
                    additional_properties={
                        "totalProcessed": 0,  # Not tracked in basic output
                        "totalIdleTime": total_idle,
                        "totalProcessingTime": total_processing,
                        "totalBlockedTime": total_blocked
                    }
                )
                
                logger.info(f"   ✓ Updated {device_id}")
            
            # Update simulation twin to Completed
            await self.streamer.stream_simulation_update(
                simulation_id=self.simulation_id,
                simulation_status="Completed",
                total_flows_completed=result['summary']['total_flows_completed'],
                total_events=result['summary']['total_events'],
                additional_properties={
                    "endTime": datetime.now(timezone.utc).isoformat(),
                    "simulationTimeSeconds": result['summary']['simulation_time_seconds'],
                    "executionTimeSeconds": result['summary']['execution_time_seconds']
                }
            )
            
            logger.info("   ✓ Updated simulation twin")
            
            # Final flush
            logger.info("\n6. Flushing remaining telemetry...")
            await self.streamer.stop_auto_flush()
            await self.dt_client.flush_updates()
            
            # Show buffer status
            buffer_status = self.streamer.get_buffer_status()
            logger.info(f"\n7. Buffer status:")
            logger.info(f"   • Buffer size: {buffer_status['buffer_size']}/{buffer_status['buffer_capacity']}")
            logger.info(f"   • Buffer utilization: {buffer_status['buffer_utilization']:.1f}%")
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
            logger.info("=" * 80)
            logger.info("\nNext steps:")
            logger.info("1. Open Azure Digital Twins Explorer in Azure Portal")
            logger.info("2. Navigate to your Digital Twins instance")
            logger.info("3. View the updated device twins and simulation twin")
            logger.info("4. Check the telemetry events and property changes")
            logger.info("\nTip: You can query twins using Azure Digital Twins query language:")
            logger.info(f"     SELECT * FROM digitaltwins WHERE $dtId = '{self.simulation_id}'")
            
            return result
            
        except Exception as e:
            logger.error(f"\n❌ Error during simulation: {e}")
            
            # Update simulation status to Failed
            if self.simulation_id:
                await self.streamer.stream_simulation_update(
                    simulation_id=self.simulation_id,
                    simulation_status="Failed",
                    total_flows_completed=0,
                    total_events=0,
                    additional_properties={
                        "endTime": datetime.now(timezone.utc).isoformat(),
                        "errorMessage": str(e)
                    }
                )
            
            raise
        
        finally:
            # Ensure telemetry is stopped
            if self.streamer:
                await self.streamer.stop_auto_flush()
            
            if self.dt_client:
                self.dt_client.close()


async def main():
    parser = argparse.ArgumentParser(description="Test Azure Digital Twins integration")
    parser.add_argument(
        "--endpoint",
        help="Azure Digital Twins endpoint URL (or set AZURE_DIGITAL_TWINS_ENDPOINT env var)"
    )
    parser.add_argument(
        "--mode",
        choices=["direct", "function"],
        default="direct",
        help="Streaming mode: direct (to ADT) or function (via Azure Function)"
    )
    
    args = parser.parse_args()
    
    # Get endpoint from args or environment
    endpoint = args.endpoint or os.getenv("AZURE_DIGITAL_TWINS_ENDPOINT")
    
    if not endpoint:
        logger.error("❌ Azure Digital Twins endpoint not provided!")
        logger.error("   Set --endpoint or AZURE_DIGITAL_TWINS_ENDPOINT environment variable")
        logger.error("\nExample:")
        logger.error("   export AZURE_DIGITAL_TWINS_ENDPOINT='https://your-instance.api.eus.digitaltwins.azure.net'")
        logger.error("   python examples/test_azure_integration.py")
        sys.exit(1)
    
    # Run simulation with telemetry
    sim = SimulationWithTelemetry(
        config=SAMPLE_CONFIG,
        adt_endpoint=endpoint,
        stream_mode=args.mode
    )
    
    await sim.run_simulation_with_streaming()


if __name__ == "__main__":
    asyncio.run(main())
