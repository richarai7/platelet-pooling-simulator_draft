"""
Create Device Twins in Azure Digital Twins
Initializes the 12 physical device twins for the platelet pooling simulation
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from azure_integration.digital_twins_client import DigitalTwinsClientWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default device configuration for platelet pooling lab
DEFAULT_DEVICES = [
    {
        "twin_id": "centrifuge-01",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "centrifuge-01",
            "deviceType": "centrifuge",
            "status": "Idle",
            "capacity": 2,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 1"
        }
    },
    {
        "twin_id": "centrifuge-02",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "centrifuge-02",
            "deviceType": "centrifuge",
            "status": "Idle",
            "capacity": 2,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 2"
        }
    },
    {
        "twin_id": "separator-01",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "separator-01",
            "deviceType": "separator",
            "status": "Idle",
            "capacity": 2,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 3"
        }
    },
    {
        "twin_id": "separator-02",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "separator-02",
            "deviceType": "separator",
            "status": "Idle",
            "capacity": 2,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 4"
        }
    },
    {
        "twin_id": "macopress-01",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "macopress-01",
            "deviceType": "macopress",
            "status": "Idle",
            "capacity": 1,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 1"
        }
    },
    {
        "twin_id": "macopress-02",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "macopress-02",
            "deviceType": "macopress",
            "status": "Idle",
            "capacity": 1,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 2"
        }
    },
    {
        "twin_id": "quality-check-01",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "quality-check-01",
            "deviceType": "quality_station",
            "status": "Idle",
            "capacity": 1,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 3"
        }
    },
    {
        "twin_id": "storage-01",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "storage-01",
            "deviceType": "storage",
            "status": "Idle",
            "capacity": 50,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab C - Cold Storage"
        }
    }
]


async def create_device_twins(endpoint: str, devices: list):
    """
    Create device twins in Azure Digital Twins
    
    Args:
        endpoint: Azure Digital Twins endpoint URL
        devices: List of device configurations
    """
    logger.info(f"Connecting to Azure Digital Twins: {endpoint}")
    client = DigitalTwinsClientWrapper(endpoint)
    
    success_count = 0
    failed_devices = []
    
    for device in devices:
        twin_id = device["twin_id"]
        model_id = device["model_id"]
        properties = device["properties"]
        
        logger.info(f"Creating twin: {twin_id}")
        
        success = await client.create_or_update_twin(
            twin_id=twin_id,
            model_id=model_id,
            properties=properties
        )
        
        if success:
            success_count += 1
            logger.info(f"✓ Created {twin_id}")
        else:
            failed_devices.append(twin_id)
            logger.error(f"✗ Failed to create {twin_id}")
    
    logger.info(f"\nSummary: {success_count}/{len(devices)} twins created successfully")
    
    if failed_devices:
        logger.error(f"Failed devices: {', '.join(failed_devices)}")
        return False
    
    return True


async def main():
    parser = argparse.ArgumentParser(description="Create device twins in Azure Digital Twins")
    parser.add_argument(
        "--endpoint",
        required=True,
        help="Azure Digital Twins endpoint URL"
    )
    parser.add_argument(
        "--devices-config",
        help="Path to custom devices configuration JSON file"
    )
    
    args = parser.parse_args()
    
    # Load device configuration
    if args.devices_config:
        logger.info(f"Loading devices from: {args.devices_config}")
        with open(args.devices_config, 'r') as f:
            devices = json.load(f)
    else:
        logger.info("Using default device configuration")
        devices = DEFAULT_DEVICES
    
    # Create twins
    success = await create_device_twins(args.endpoint, devices)
    
    if success:
        logger.info("\n✅ All device twins created successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Verify twins in Azure Digital Twins Explorer")
        logger.info("2. Run a simulation to test telemetry streaming")
        logger.info("3. Check real-time updates in the UI dashboard")
    else:
        logger.error("\n❌ Some device twins failed to create")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
