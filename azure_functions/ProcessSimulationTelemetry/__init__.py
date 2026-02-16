"""
Azure Function: ProcessSimulationTelemetry
Receives simulation telemetry and updates Azure Digital Twins

HIGH PRIORITY: This function handles the critical path for updating Digital Twins.
Includes comprehensive error handling, retry logic, and detailed logging for
troubleshooting permission and connectivity issues.
"""

import logging
import json
import os
import time
import traceback
from typing import Dict, Any, Optional, Tuple
import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.digitaltwins.core import DigitalTwinsClient
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
    ClientAuthenticationError
)


# Initialize Digital Twins client (reused across invocations)
ADT_ENDPOINT = os.environ.get("AZURE_DIGITAL_TWINS_ENDPOINT")
dt_client = None
credential = None

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 10.0  # seconds

if ADT_ENDPOINT:
    try:
        credential = ManagedIdentityCredential()
        dt_client = DigitalTwinsClient(ADT_ENDPOINT, credential)
        logging.info(f"✅ Connected to Azure Digital Twins: {ADT_ENDPOINT}")
        logging.info(f"   Using Managed Identity for authentication")
    except ClientAuthenticationError as e:
        logging.error(f"❌ Authentication failed - Check Function App Managed Identity permissions")
        logging.error(f"   Required role: 'Azure Digital Twins Data Owner' on ADT instance")
        logging.error(f"   Error details: {e}")
    except Exception as e:
        logging.error(f"❌ Failed to initialize Digital Twins client: {e}")
        logging.error(f"   Endpoint: {ADT_ENDPOINT}")
        logging.error(f"   Check: 1) Endpoint URL is correct, 2) Network connectivity, 3) Firewall rules")
else:
    logging.warning("⚠️  AZURE_DIGITAL_TWINS_ENDPOINT not configured - running in mock mode")


def update_twin_with_retry(twin_id: str, properties: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Update a Digital Twin with exponential backoff retry logic
    
    Args:
        twin_id: The ID of the twin to update
        properties: Dictionary of properties to update
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not dt_client:
        logging.warning(f"[MOCK] Would update twin {twin_id}: {properties}")
        return True, None
    
    patch = create_json_patch(properties)
    retry_delay = INITIAL_RETRY_DELAY
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            dt_client.update_digital_twin(twin_id, patch)
            if attempt > 1:
                logging.info(f"✅ Updated twin {twin_id} on attempt {attempt}")
            else:
                logging.debug(f"✅ Updated twin {twin_id}")
            return True, None
            
        except ResourceNotFoundError as e:
            error_msg = f"Twin '{twin_id}' not found in Azure Digital Twins"
            logging.error(f"❌ {error_msg}")
            logging.error(f"   Verify twin exists: az dt twin show --dt-name <instance> --twin-id {twin_id}")
            return False, error_msg
            
        except ClientAuthenticationError as e:
            error_msg = f"Authentication failed for twin {twin_id}"
            logging.error(f"❌ {error_msg}: {str(e)}")
            logging.error(f"   Check Function App has 'Azure Digital Twins Data Owner' role")
            logging.error(f"   Principal ID: Check in Azure Portal > Function App > Identity")
            return False, error_msg
            
        except HttpResponseError as e:
            status_code = e.status_code if hasattr(e, 'status_code') else 'unknown'
            error_msg = f"HTTP {status_code} error updating twin {twin_id}"
            
            # Don't retry on 4xx errors (except 429 rate limiting)
            if isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429:
                logging.error(f"❌ {error_msg}: {str(e)}")
                # Safely get response text
                try:
                    response_text = e.response.text() if hasattr(e, 'response') and hasattr(e.response, 'text') else 'Response text unavailable'
                    logging.error(f"   Response: {response_text}")
                except Exception:
                    logging.error(f"   Response: Response text unavailable")
                return False, error_msg
            
            # Retry on 5xx errors and 429
            if attempt < MAX_RETRIES:
                logging.warning(f"⚠️  {error_msg}, retrying in {retry_delay:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)  # Exponential backoff
            else:
                logging.error(f"❌ {error_msg} after {MAX_RETRIES} attempts: {str(e)}")
                return False, error_msg
                
        except ServiceRequestError as e:
            error_msg = f"Network error updating twin {twin_id}"
            if attempt < MAX_RETRIES:
                logging.warning(f"⚠️  {error_msg}, retrying in {retry_delay:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
            else:
                logging.error(f"❌ {error_msg} after {MAX_RETRIES} attempts: {str(e)}")
                logging.error(f"   Check network connectivity and firewall rules")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Unexpected error updating twin {twin_id}: {type(e).__name__}"
            logging.error(f"❌ {error_msg}: {str(e)}")
            if attempt < MAX_RETRIES:
                logging.warning(f"⚠️  Retrying in {retry_delay:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
            else:
                return False, error_msg
    
    return False, f"Failed to update twin {twin_id} after {MAX_RETRIES} attempts"


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
    
    HIGH PRIORITY: This is the critical path for E2E flow.
    Comprehensive error handling and logging to diagnose permission issues.
    """
    logging.info('🔄 ProcessSimulationTelemetry function triggered')
    
    # Log configuration for diagnostics
    logging.info(f"   ADT Endpoint: {ADT_ENDPOINT or 'NOT CONFIGURED'}")
    logging.info(f"   Client initialized: {dt_client is not None}")
    
    try:
        # Parse request body
        req_body = req.get_json()
        telemetry_batch = req_body.get('telemetry', [])
        
        if not telemetry_batch:
            logging.error("❌ No telemetry data provided in request")
            return func.HttpResponse(
                json.dumps({"error": "No telemetry data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f"📊 Processing {len(telemetry_batch)} telemetry updates")
        
        # Process each telemetry update
        success_count = 0
        failed_updates = []
        
        for idx, update in enumerate(telemetry_batch, 1):
            twin_id = update.get('twin_id')
            properties = update.get('properties', {})
            
            if not twin_id:
                error_detail = {"error": "Missing twin_id", "update": update}
                logging.error(f"❌ Update #{idx}: Missing twin_id")
                failed_updates.append(error_detail)
                continue
            
            logging.debug(f"   Update #{idx}/{len(telemetry_batch)}: {twin_id} ({len(properties)} properties)")
            
            # Update twin with retry logic
            success, error_msg = update_twin_with_retry(twin_id, properties)
            
            if success:
                success_count += 1
            else:
                failed_updates.append({
                    "twin_id": twin_id,
                    "error": error_msg or "Unknown error"
                })
        
        # Return response
        response = {
            "processed": len(telemetry_batch),
            "success": success_count,
            "failed": len(failed_updates),
            "failed_updates": failed_updates if failed_updates else None,
            "endpoint": ADT_ENDPOINT,
            "client_initialized": dt_client is not None
        }
        
        if success_count == len(telemetry_batch):
            logging.info(f"✅ Completed: All {success_count} twins updated successfully")
        elif success_count > 0:
            logging.warning(f"⚠️  Partial success: {success_count}/{len(telemetry_batch)} twins updated")
        else:
            logging.error(f"❌ All updates failed: 0/{len(telemetry_batch)} successful")
        
        status_code = 200 if not failed_updates else 207  # 207 = Multi-Status
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=status_code,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"❌ Invalid JSON in request: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload", "details": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
        logging.error(f"   Stack trace: {traceback.format_exc()}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "type": type(e).__name__,
                "details": str(e)
            }),
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
