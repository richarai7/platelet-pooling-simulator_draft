"""
Create Device Twins in Azure Digital Twins for Linear Platelet Flow
Initializes the 10 physical device twins for the platelet pooling simulation
with relationships showing the linear flow
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


# Device configuration for linear platelet pooling flow
LINEAR_FLOW_DEVICES = [
    {
        "twin_id": "buffy_coat_packs",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "buffy_coat_packs",
            "deviceType": "buffy_coat_packs",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 1",
            "position": {"x": 0, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "platelet_washing",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "platelet_washing",
            "deviceType": "platelet_washing",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 2",
            "position": {"x": 2, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "centrifuge",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "centrifuge",
            "deviceType": "centrifuge",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab A - Station 3",
            "position": {"x": 4, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "separator_macropress",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "separator_macropress",
            "deviceType": "separator_macropress",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 1",
            "position": {"x": 6, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "resting_trolly",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "resting_trolly",
            "deviceType": "resting_trolly",
            "status": "Idle",
            "capacity": 15,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 2",
            "position": {"x": 8, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "agitator",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "agitator",
            "deviceType": "agitator",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab B - Station 3",
            "position": {"x": 0, "y": 0, "z": 2},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "macropress",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "macropress",
            "deviceType": "macropress",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab C - Station 1",
            "position": {"x": 2, "y": 0, "z": 2},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "testing_agitator",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "testing_agitator",
            "deviceType": "testing_agitator",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab C - Station 2",
            "position": {"x": 4, "y": 0, "z": 2},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "labeling",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "labeling",
            "deviceType": "labeling",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab C - Station 3",
            "position": {"x": 6, "y": 0, "z": 2},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    },
    {
        "twin_id": "release",
        "model_id": "dtmi:platelet:Device;1",
        "properties": {
            "deviceId": "release",
            "deviceType": "release",
            "status": "Idle",
            "capacity": 10,
            "inUse": 0,
            "utilizationRate": 0.0,
            "queueLength": 0,
            "totalProcessed": 0,
            "totalBlockedTime": 0.0,
            "totalIdleTime": 0.0,
            "totalProcessingTime": 0.0,
            "location": "Lab D - Release Area",
            "position": {"x": 8, "y": 0, "z": 2},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
        }
    }
]


# Relationships showing the linear flow
LINEAR_FLOW_RELATIONSHIPS = [
    {
        "source_twin_id": "buffy_coat_packs",
        "relationship_id": "buffy_to_washing",
        "target_twin_id": "platelet_washing",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "platelet_washing",
        "relationship_id": "washing_to_centrifuge",
        "target_twin_id": "centrifuge",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "centrifuge",
        "relationship_id": "centrifuge_to_separator",
        "target_twin_id": "separator_macropress",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "separator_macropress",
        "relationship_id": "separator_to_resting",
        "target_twin_id": "resting_trolly",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "resting_trolly",
        "relationship_id": "resting_to_agitator",
        "target_twin_id": "agitator",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "agitator",
        "relationship_id": "agitator_to_macropress",
        "target_twin_id": "macropress",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "macropress",
        "relationship_id": "macropress_to_testing",
        "target_twin_id": "testing_agitator",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "testing_agitator",
        "relationship_id": "testing_to_labeling",
        "target_twin_id": "labeling",
        "relationship_name": "feedsInto"
    },
    {
        "source_twin_id": "labeling",
        "relationship_id": "labeling_to_release",
        "target_twin_id": "release",
        "relationship_name": "feedsInto"
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


async def create_relationships(endpoint: str, relationships: list):
    """
    Create relationships between device twins
    
    Args:
        endpoint: Azure Digital Twins endpoint URL
        relationships: List of relationship configurations
    """
    logger.info(f"\nCreating relationships to show linear flow...")
    client = DigitalTwinsClientWrapper(endpoint)
    
    success_count = 0
    failed_relationships = []
    
    for rel in relationships:
        source_id = rel["source_twin_id"]
        rel_id = rel["relationship_id"]
        target_id = rel["target_twin_id"]
        rel_name = rel["relationship_name"]
        
        logger.info(f"Creating relationship: {source_id} -> {target_id}")
        
        success = await client.create_relationship(
            source_twin_id=source_id,
            relationship_id=rel_id,
            target_twin_id=target_id,
            relationship_name=rel_name
        )
        
        if success:
            success_count += 1
            logger.info(f"✓ Created relationship {rel_id}")
        else:
            failed_relationships.append(rel_id)
            logger.error(f"✗ Failed to create relationship {rel_id}")
    
    logger.info(f"\nSummary: {success_count}/{len(relationships)} relationships created successfully")
    
    if failed_relationships:
        logger.error(f"Failed relationships: {', '.join(failed_relationships)}")
        return False
    
    return True


async def main():
    parser = argparse.ArgumentParser(description="Create device twins and relationships in Azure Digital Twins")
    parser.add_argument(
        "--endpoint",
        required=True,
        help="Azure Digital Twins endpoint URL"
    )
    parser.add_argument(
        "--twins-only",
        action="store_true",
        help="Create only twins, skip relationships"
    )
    parser.add_argument(
        "--relationships-only",
        action="store_true",
        help="Create only relationships, skip twins"
    )
    
    args = parser.parse_args()
    
    overall_success = True
    
    # Create twins
    if not args.relationships_only:
        logger.info("=" * 70)
        logger.info("CREATING DEVICE TWINS")
        logger.info("=" * 70)
        success = await create_device_twins(args.endpoint, LINEAR_FLOW_DEVICES)
        overall_success = overall_success and success
    
    # Create relationships
    if not args.twins_only:
        logger.info("\n" + "=" * 70)
        logger.info("CREATING RELATIONSHIPS")
        logger.info("=" * 70)
        success = await create_relationships(args.endpoint, LINEAR_FLOW_RELATIONSHIPS)
        overall_success = overall_success and success
    
    if overall_success:
        logger.info("\n✅ All operations completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Verify twins and relationships in Azure Digital Twins Explorer")
        logger.info("2. Run a simulation to test telemetry streaming")
        logger.info("3. Check real-time updates in the twin graph")
    else:
        logger.error("\n❌ Some operations failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
