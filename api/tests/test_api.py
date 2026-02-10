import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, scenario_repo


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def temp_db():
    """Temporary database for testing"""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Update scenario_repo to use temp DB
    original_db = scenario_repo.db_path
    scenario_repo.db_path = path
    scenario_repo._init_schema()
    
    yield path
    
    # Cleanup
    scenario_repo.db_path = original_db
    if os.path.exists(path):
        os.unlink(path)


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Simulation API"
    assert "endpoints" in data


def test_create_scenario(client, temp_db):
    """Test creating a new scenario"""
    payload = {
        "name": "Test Scenario",
        "description": "A test scenario",
        "config": {
            "simulation": {"duration": 3600, "random_seed": 42},
            "devices": [],
            "flows": [],
            "output_options": {}
        },
        "tags": ["test"]
    }
    
    response = client.post("/scenarios", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Scenario"
    assert data["description"] == "A test scenario"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_scenario(client, temp_db):
    """Test creating duplicate scenario returns 409"""
    payload = {
        "name": "Duplicate Test",
        "description": "First scenario",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    
    # Create first scenario
    response1 = client.post("/scenarios", json=payload)
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post("/scenarios", json=payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


def test_list_scenarios(client, temp_db):
    """Test listing all scenarios"""
    # Create a scenario first
    payload = {
        "name": "List Test Scenario",
        "description": "For list testing",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    client.post("/scenarios", json=payload)
    
    # List scenarios
    response = client.get("/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "List Test Scenario"


def test_get_scenario(client, temp_db):
    """Test getting a specific scenario"""
    # Create a scenario
    payload = {
        "name": "Get Test Scenario",
        "description": "For get testing",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    create_response = client.post("/scenarios", json=payload)
    scenario_id = create_response.json()["id"]
    
    # Get the scenario
    response = client.get(f"/scenarios/{scenario_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == scenario_id
    assert data["name"] == "Get Test Scenario"


def test_get_nonexistent_scenario(client, temp_db):
    """Test getting a non-existent scenario returns 404"""
    response = client.get("/scenarios/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_scenario(client, temp_db):
    """Test updating an existing scenario"""
    # Create a scenario
    payload = {
        "name": "Original Name",
        "description": "Original description",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    create_response = client.post("/scenarios", json=payload)
    scenario_id = create_response.json()["id"]
    
    # Update the scenario
    update_payload = {
        "name": "Updated Name",
        "description": "Updated description",
        "config": {"simulation": {"duration": 7200}, "devices": [], "flows": [], "output_options": {}}
    }
    response = client.put(f"/scenarios/{scenario_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"
    assert data["config"]["simulation"]["duration"] == 7200


def test_update_nonexistent_scenario(client, temp_db):
    """Test updating a non-existent scenario returns 404"""
    payload = {
        "name": "Test",
        "description": "Test",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    response = client.put("/scenarios/99999", json=payload)
    assert response.status_code == 404


def test_delete_scenario(client, temp_db):
    """Test deleting a scenario"""
    # Create a scenario
    payload = {
        "name": "Delete Test",
        "description": "To be deleted",
        "config": {"simulation": {}, "devices": [], "flows": [], "output_options": {}}
    }
    create_response = client.post("/scenarios", json=payload)
    scenario_id = create_response.json()["id"]
    
    # Delete the scenario
    response = client.delete(f"/scenarios/{scenario_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/scenarios/{scenario_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_scenario(client, temp_db):
    """Test deleting a non-existent scenario returns 404"""
    response = client.delete("/scenarios/99999")
    assert response.status_code == 404


def test_run_simulation(client):
    """Test running a simulation"""
    payload = {
        "config": {
            "simulation": {
                "duration": 100,
                "random_seed": 42
            },
            "devices": [
                {
                    "id": "test_device",
                    "type": "workstation",
                    "capacity": 1,
                    "initial_state": "idle",
                    "process_time_range": (10, 20),
                    "recovery_time_range": None
                }
            ],
            "flows": [],
            "output_options": {
                "include_events": False,
                "include_history": False
            }
        }
    }
    
    response = client.post("/simulations/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], dict)


def test_run_simulation_with_invalid_config(client):
    """Test running simulation with invalid configuration"""
    payload = {
        "config": {
            "simulation": {},  # Missing required fields
            "devices": [],
            "flows": [],
            "output_options": {}
        }
    }
    
    response = client.post("/simulations/run", json=payload)
    assert response.status_code == 400
    assert "validation error" in response.json()["detail"].lower()


def test_get_template(client):
    """Test getting platelet pooling template"""
    response = client.get("/templates/platelet-pooling")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "simulation" in data
    assert "devices" in data
    assert "flows" in data
    assert "output_options" in data
    
    # Verify content
    assert data["simulation"]["duration"] == 28800
    assert len(data["devices"]) == 3
    assert len(data["flows"]) == 2
    
    # Verify device IDs
    device_ids = [d["id"] for d in data["devices"]]
    assert "separator_1" in device_ids
    assert "pooling_1" in device_ids
    assert "testing_1" in device_ids
