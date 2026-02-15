import sys
import json
import sqlite3
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Add parent/src to path for simulation_engine imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulation_engine import SimulationEngine
from simulation_engine.repository import ScenarioRepository, ResultsRepository
from simulation_engine.config_manager import ValidationError

from .models import (
    ScenarioCreateRequest,
    ScenarioResponse,
    SimulationRunRequest,
    SimulationResultsResponse
)
from .templates import get_platelet_template

# Add parent directory for capacity_multiplier
sys.path.insert(0, str(Path(__file__).parent.parent))
from capacity_multiplier import multiply_device_capacities, create_capacity_comparison


# Initialize FastAPI app
app = FastAPI(
    title="Simulation API",
    version="0.1.0",
    description="REST API for platelet pooling simulation configuration and execution"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Accept"],
)

# Initialize repositories
scenario_repo = ScenarioRepository(db_path="scenarios.db")
results_repo = ResultsRepository(db_path="scenarios.db")

# Active simulations tracking: {simulation_id: engine_instance}
active_simulations: Dict[str, SimulationEngine] = {}

# Azure Function configuration
AZURE_FUNCTION_ENDPOINT = os.getenv('AZURE_FUNCTION_ENDPOINT')
AZURE_FUNCTION_KEY = os.getenv('AZURE_FUNCTION_KEY')
ENABLE_AZURE_INTEGRATION = os.getenv('ENABLE_AZURE_INTEGRATION', 'false').lower() == 'true'


def prepare_telemetry_from_results(results: Dict[str, Any], simulation_id: str) -> Dict[str, Any]:
    """
    Prepare telemetry payload from simulation results for Azure Function
    
    Args:
        results: Simulation results dictionary
        simulation_id: Unique simulation identifier
    
    Returns:
        Telemetry payload in format expected by Azure Function
    """
    telemetry_batch = []
    
    # Add simulation twin telemetry
    simulation_telemetry = {
        "twin_id": simulation_id,
        "properties": {
            "simulationId": simulation_id,
            "simulationStatus": "Completed",
            "totalFlowsCompleted": results.get('summary', {}).get('total_flows_completed', 0),
            "totalEvents": results.get('summary', {}).get('total_events', 0),
            "simulationTimeSeconds": results.get('summary', {}).get('simulation_time_seconds', 0),
            "executionTimeSeconds": results.get('summary', {}).get('execution_time_seconds', 0)
        }
    }
    telemetry_batch.append(simulation_telemetry)
    
    # Add device telemetry from final states
    device_states = results.get('device_states', [])
    event_timeline = results.get('event_timeline', [])
    simulation_time = results.get('summary', {}).get('simulation_time_seconds', 0)
    
    for device in device_states:
        device_id = device.get('device_id')
        if not device_id:
            continue
        
        # Calculate metrics from event timeline (similar to run_simulation_with_adt.py)
        device_events = [e for e in event_timeline if e.get('device_id') == device_id]
        
        total_idle = 0.0
        total_processing = 0.0
        total_blocked = 0.0
        total_processed = 0
        
        current_state = 'Idle'
        last_timestamp = 0.0
        
        for event in device_events:
            duration = event['timestamp'] - last_timestamp
            
            if current_state == 'Idle':
                total_idle += duration
            elif current_state == 'Processing':
                total_processing += duration
            elif current_state == 'Blocked':
                total_blocked += duration
            
            if event['event'] == 'COMPLETE_PROCESSING':
                total_processed += 1
            
            current_state = event['to_state']
            last_timestamp = event['timestamp']
        
        # Add final state duration
        if device_events:
            final_duration = simulation_time - last_timestamp
            if current_state == 'Idle':
                total_idle += final_duration
            elif current_state == 'Processing':
                total_processing += final_duration
            elif current_state == 'Blocked':
                total_blocked += final_duration
        else:
            total_idle = simulation_time
        
        device_telemetry = {
            "twin_id": device_id,
            "properties": {
                "status": device.get('final_state', 'Idle'),
                "inUse": 0,
                "queueLength": 0,
                "totalProcessed": total_processed,
                "totalIdleTime": total_idle,
                "totalProcessingTime": total_processing,
                "totalBlockedTime": total_blocked
            }
        }
        telemetry_batch.append(device_telemetry)
    
    return {"telemetry": telemetry_batch}


async def send_telemetry_to_azure_function(telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Send telemetry to Azure Function for Digital Twins update
    
    Args:
        telemetry: Telemetry payload
    
    Returns:
        Response from Azure Function or None if disabled/failed
    """
    if not ENABLE_AZURE_INTEGRATION:
        logger.debug("Azure integration is disabled")
        return None
    
    if not AZURE_FUNCTION_ENDPOINT:
        logger.warning("Azure Function endpoint not configured")
        return None
    
    try:
        # Build request URL with function key if provided
        url = AZURE_FUNCTION_ENDPOINT
        headers = {"Content-Type": "application/json"}
        
        if AZURE_FUNCTION_KEY:
            # Add function key as query parameter
            url = f"{url}?code={AZURE_FUNCTION_KEY}"
        
        # Send telemetry to Azure Function
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=telemetry, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Azure Function response: {result.get('success', 0)}/{result.get('processed', 0)} twins updated")
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Azure Function HTTP error: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.TimeoutException:
        logger.error("Azure Function request timed out")
        return None
    except Exception as e:
        logger.error(f"Error sending telemetry to Azure Function: {e}")
        return None


@app.get("/")
def read_root():
    """API root endpoint"""
    return {
        "message": "Simulation API",
        "version": "0.1.0",
        "endpoints": {
            "scenarios": "/scenarios",
            "simulation": "/simulations/run",
            "templates": "/templates/platelet-pooling"
        }
    }


@app.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(request: ScenarioCreateRequest):
    """Create a new simulation scenario"""
    try:
        scenario_id = scenario_repo.save(
            name=request.name,
            description=request.description,
            config=request.config,
            tags=request.tags or []
        )
        # Fetch the created scenario
        config = scenario_repo.load_by_id(scenario_id)
        # Get metadata
        with sqlite3.connect(scenario_repo.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, description, created_at, updated_at, tags FROM scenarios WHERE id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
            scenario_data = dict(row)
            scenario_data['config'] = config
            # Handle tags - could be empty string or JSON
            tags_str = scenario_data.get('tags', '')
            scenario_data['tags'] = json.loads(tags_str) if tags_str and tags_str.strip() else []
        
        return ScenarioResponse(**scenario_data)
    except ValueError as e:
        # Check for duplicate name
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except sqlite3.Error as e:
        logger.error(f"Database error in create_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in create_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/scenarios", response_model=List[ScenarioResponse])
def list_scenarios():
    """List all simulation scenarios"""
    scenarios = []
    with sqlite3.connect(scenario_repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, name, description, config_json, created_at, updated_at, tags FROM scenarios ORDER BY name"
        )
        for row in cursor.fetchall():
            scenario_data = dict(row)
            scenario_data['config'] = json.loads(scenario_data['config_json'])
            del scenario_data['config_json']
            # Handle tags - could be empty string or JSON
            tags_str = scenario_data.get('tags', '')
            scenario_data['tags'] = json.loads(tags_str) if tags_str and tags_str.strip() else []
            scenarios.append(ScenarioResponse(**scenario_data))
    return scenarios


@app.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int):
    """Get a specific simulation scenario by ID"""
    try:
        with sqlite3.connect(scenario_repo.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, description, config_json, created_at, updated_at, tags FROM scenarios WHERE id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scenario with id {scenario_id} not found"
                )
            scenario_data = dict(row)
            scenario_data['config'] = json.loads(scenario_data['config_json'])
            del scenario_data['config_json']
            scenario_data['tags'] = json.loads(scenario_data['tags']) if scenario_data['tags'] else []
            return ScenarioResponse(**scenario_data)
    except HTTPException:
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(scenario_id: int, request: ScenarioCreateRequest):
    """Update an existing simulation scenario"""
    try:
        # Check if scenario exists
        with sqlite3.connect(scenario_repo.db_path) as conn:
            cursor = conn.execute("SELECT id FROM scenarios WHERE id = ?", (scenario_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scenario with id {scenario_id} not found"
                )
            
            # Update scenario
            config_json = json.dumps(request.config, indent=2, sort_keys=True)
            tags_json = json.dumps(request.tags or [])
            conn.execute(
                """UPDATE scenarios SET name = ?, description = ?, config_json = ?, tags = ?,
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (request.name, request.description, config_json, tags_json, scenario_id),
            )
            conn.commit()
            
            # Fetch updated scenario
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, description, config_json, created_at, updated_at, tags FROM scenarios WHERE id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
            scenario_data = dict(row)
            scenario_data['config'] = json.loads(scenario_data['config_json'])
            del scenario_data['config_json']
            scenario_data['tags'] = json.loads(scenario_data['tags']) if scenario_data['tags'] else []
            return ScenarioResponse(**scenario_data)
    except HTTPException:
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in update_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in update_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int):
    """Delete a simulation scenario"""
    try:
        with sqlite3.connect(scenario_repo.db_path) as conn:
            cursor = conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scenario with id {scenario_id} not found"
                )
    except HTTPException:
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in delete_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in delete_scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/simulations/run", response_model=SimulationResultsResponse)
async def run_simulation(request: SimulationRunRequest):
    """Run a simulation with the provided configuration"""
    try:
        # Initialize and run simulation engine
        engine = SimulationEngine(request.config)
        
        # Generate simulation ID for tracking
        from datetime import datetime
        sim_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Track active simulation
        active_simulations[sim_id] = engine
        
        try:
            results = engine.run()
            
            # Add run metadata to results
            if not results.get('metadata'):
                results['metadata'] = {}
            
            results['metadata']['simulation_id'] = sim_id
            if request.run_name:
                results['metadata']['run_name'] = request.run_name
            if request.simulation_name:
                results['metadata']['simulation_name'] = request.simulation_name
            
            # Export to JSON if requested
            json_export_path = None
            if request.export_to_json:
                import os
                
                # Determine export directory
                export_dir = request.export_directory or "simulation_results"
                os.makedirs(export_dir, exist_ok=True)
                
                # Generate filename with metadata
                filename_parts = []
                if request.simulation_name:
                    filename_parts.append(request.simulation_name.replace(' ', '_'))
                if request.run_name:
                    filename_parts.append(request.run_name.replace(' ', '_'))
                filename_parts.append(sim_id)
                
                filename = '_'.join(filename_parts) + '.json'
                json_export_path = os.path.join(export_dir, filename)
                
                # Write results to JSON file
                with open(json_export_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                logger.info(f"Results exported to {json_export_path}")
                results['metadata']['json_export_path'] = json_export_path
            
            # Save to database if results repository is available
            try:
                results_repo.save(
                    simulation_id=sim_id,
                    config=request.config,
                    results=results,
                    run_name=request.run_name or sim_id,
                    simulation_name=request.simulation_name
                )
                logger.info(f"Results saved to database for {sim_id}")
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")
            
            # Send telemetry to Azure Function for Digital Twins update
            azure_response = None
            if ENABLE_AZURE_INTEGRATION:
                try:
                    telemetry = prepare_telemetry_from_results(results, sim_id)
                    azure_response = await send_telemetry_to_azure_function(telemetry)
                    
                    if azure_response:
                        logger.info(f"Digital Twins updated: {azure_response.get('success', 0)} twins")
                        results['metadata']['azure_twins_updated'] = azure_response.get('success', 0)
                    else:
                        logger.warning("Azure Function call did not return a response")
                except Exception as azure_error:
                    logger.error(f"Error updating Digital Twins: {azure_error}")
                    # Don't fail the simulation if Azure update fails
                    results['metadata']['azure_error'] = str(azure_error)
            
            return SimulationResultsResponse(
                results=results,
                json_export_path=json_export_path,
                simulation_id=sim_id
            )
        finally:
            # Remove from active simulations when complete or cancelled
            active_simulations.pop(sim_id, None)
            
    except ValidationError as e:
        logger.warning(f"Validation error in run_simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration validation error: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Simulation execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulation execution failed"
        )


@app.get("/templates/platelet-pooling")
def get_platelet_pooling_template():
    """Get the platelet pooling simulation configuration template"""
    return get_platelet_template()


@app.get("/templates/platelet-pooling-multi-batch")
def get_platelet_pooling_multi_batch_template(batches: int = 5, interval: int = 600):
    """
    Get multi-batch platelet pooling configuration.
    
    Args:
        batches: Number of batches to process (default: 5)
        interval: Time in seconds between batch arrivals (default: 600 = 10 min)
    
    This template demonstrates capacity impacts by having multiple batches
    compete for device resources.
    """
    from templates import get_multi_batch_template
    return get_multi_batch_template(num_batches=batches, batch_interval=interval)


@app.post("/utils/multiply-capacity")
def multiply_capacity(request: Dict[str, Any]):
    """
    Multiply device capacities by a given factor.
    
    Request body:
    {
        "config": {...},         // Base configuration
        "multiplier": 2.0,       // 2.0 = 200%, 3.0 = 300%, 1.5 = 150%
        "device_id": null        // Optional: multiply only specific device
    }
    
    Examples:
    - multiplier: 2.0 → 200% capacity (double all devices)
    - multiplier: 3.0 → 300% capacity (triple all devices)
    - device_id: "quality", multiplier: 2.0 → Double only quality check
    """
    try:
        config = request.get("config")
        multiplier = request.get("multiplier", 2.0)
        device_id = request.get("device_id")
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'config' in request body"
            )
        
        if device_id:
            # Multiply specific device only
            from capacity_multiplier import multiply_specific_device
            new_config = multiply_specific_device(config, device_id, multiplier)
        else:
            # Multiply all devices
            new_config = multiply_device_capacities(config, multiplier)
        
        return {
            "original_capacities": {d['id']: d['capacity'] for d in config.get('devices', [])},
            "new_capacities": {d['id']: d['capacity'] for d in new_config.get('devices', [])},
            "multiplier": multiplier,
            "config": new_config
        }
    except Exception as e:
        logger.exception(f"Error in multiply_capacity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/utils/create-comparison")
def create_comparison(request: Dict[str, Any]):
    """
    Create multiple scenario configurations for capacity comparison.
    
    Request body:
    {
        "config": {...},                           // Base configuration
        "multipliers": [1.0, 1.5, 2.0, 3.0]       // Factors to test
    }
    
    Returns array of configs: baseline (100%), 150%, 200%, 300%
    """
    try:
        config = request.get("config")
        multipliers = request.get("multipliers", [1.0, 1.5, 2.0, 3.0])
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'config' in request body"
            )
        
        scenarios = create_capacity_comparison(config, multipliers)
        
        return {
            "scenarios": scenarios,
            "count": len(scenarios),
            "multipliers": multipliers
        }
    except Exception as e:
        logger.exception(f"Error in create_comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/simulations/active")
def get_active_simulations():
    """Get list of currently running simulations"""
    return {
        "active_count": len(active_simulations),
        "simulation_ids": list(active_simulations.keys())
    }


@app.get("/simulations/{simulation_id}/status")
def get_simulation_status(simulation_id: str):
    """Get status of a running simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found or already completed"
        )
    
    try:
        engine = active_simulations[simulation_id]
        status_info = engine.get_status()
        
        return {
            "simulation_id": simulation_id,
            "status": status_info
        }
    except Exception as e:
        logger.exception(f"Error getting simulation status {simulation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get simulation status"
        )


@app.post("/simulations/{simulation_id}/pause")
def pause_simulation(simulation_id: str):
    """Pause a running simulation (real-time mode only)"""
    if simulation_id not in active_simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found or already completed"
        )
    
    try:
        engine = active_simulations[simulation_id]
        engine.pause()
        logger.info(f"Pause requested for simulation {simulation_id}")
        
        return {
            "message": f"Simulation {simulation_id} pause requested",
            "note": "Only effective in real-time mode. Simulation will pause at next event."
        }
    except Exception as e:
        logger.exception(f"Error pausing simulation {simulation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause simulation"
        )


@app.post("/simulations/{simulation_id}/resume")
def resume_simulation(simulation_id: str):
    """Resume a paused simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found or already completed"
        )
    
    try:
        engine = active_simulations[simulation_id]
        engine.resume()
        logger.info(f"Resume requested for simulation {simulation_id}")
        
        return {
            "message": f"Simulation {simulation_id} resumed"
        }
    except Exception as e:
        logger.exception(f"Error resuming simulation {simulation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume simulation"
        )


@app.post("/simulations/{simulation_id}/cancel")
def cancel_simulation(simulation_id: str):
    """Cancel a running simulation"""
    if simulation_id not in active_simulations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found or already completed"
        )
    
    try:
        engine = active_simulations[simulation_id]
        engine.cancel()
        logger.info(f"Cancellation requested for simulation {simulation_id}")
        
        return {
            "message": f"Simulation {simulation_id} cancellation requested",
            "note": "Simulation will stop at next event processing and return partial results"
        }
    except Exception as e:
        logger.exception(f"Error cancelling simulation {simulation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel simulation"
        )
