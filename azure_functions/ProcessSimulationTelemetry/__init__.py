"""
Azure Function: ProcessSimulationTelemetry
Receives simulation telemetry and updates Azure Digital Twins
"""

import logging
import json
import os
from typing import Dict, Any
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient


# Initialize Digital Twins client (reused across invocations)
ADT_ENDPOINT = os.environ.get("AZURE_DIGITAL_TWINS_ENDPOINT")
dt_client = None

if ADT_ENDPOINT:
    try:
        credential = DefaultAzureCredential()
        dt_client = DigitalTwinsClient(ADT_ENDPOINT, credential)
        logging.info(f"Connected to Azure Digital Twins: {ADT_ENDPOINT}")
    except Exception as e:
        logging.error(f"Failed to initialize Digital Twins client: {e}")


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process incoming simulation telemetry and update Digital Twins
    
    Expected payload format:
    {
        "telemetry": [
            {
                "twin_id": "device_id",
                "properties": {
                    "status": "Processing",
                    "inUse": 2,
                    "capacity": 3,
                    ...
                }
            },
            ...
        ]
    }
    """
    logging.info('ProcessSimulationTelemetry function triggered')
    
    try:
        # Parse request body
        req_body = req.get_json()
        telemetry_batch = req_body.get('telemetry', [])
        
        if not telemetry_batch:
            return func.HttpResponse(
                json.dumps({"error": "No telemetry data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f"Processing {len(telemetry_batch)} telemetry updates")
        
        # Process each telemetry update
        success_count = 0
        failed_updates = []
        
        for update in telemetry_batch:
            twin_id = update.get('twin_id')
            properties = update.get('properties', {})
            
            if not twin_id:
                failed_updates.append({"error": "Missing twin_id", "update": update})
                continue
            
            try:
                if dt_client:
                    # Update Digital Twin
                    patch = create_json_patch(properties)
                    dt_client.update_digital_twin(twin_id, patch)
                    success_count += 1
                    logging.debug(f"Updated twin {twin_id}")
                else:
                    # Mock mode for local testing
                    logging.warning(f"[MOCK] Would update twin {twin_id}: {properties}")
                    success_count += 1
                    
            except Exception as e:
                logging.error(f"Failed to update twin {twin_id}: {e}")
                failed_updates.append({
                    "twin_id": twin_id,
                    "error": str(e)
                })
        
        # Return response
        response = {
            "processed": len(telemetry_batch),
            "success": success_count,
            "failed": len(failed_updates),
            "failed_updates": failed_updates if failed_updates else None
        }
        
        logging.info(f"Completed: {success_count}/{len(telemetry_batch)} successful")
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200 if not failed_updates else 207,  # 207 = Multi-Status
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Invalid JSON in request: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


def create_json_patch(properties: Dict[str, Any]) -> list:
    """
    Create JSON Patch document for Digital Twin property updates
    
    Args:
        properties: Dictionary of properties to update
        
    Returns:
        List of JSON Patch operations
    """
    patch = []
    for key, value in properties.items():
        patch.append({
            "op": "replace",
            "path": f"/{key}",
            "value": value
        })
    return patch
