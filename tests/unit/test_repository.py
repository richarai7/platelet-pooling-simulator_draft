"""Tests for SQLite repository layer."""

import pytest
import tempfile
import os
from simulation_engine.repository import ScenarioRepository, ResultsRepository


class TestScenarioRepository:
    """Tests for ScenarioRepository."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        # Force close any open connections before deleting file (Windows fix)
        import gc
        gc.collect()
        try:
            if os.path.exists(path):
                os.unlink(path)
        except PermissionError:
            # File still locked - try again after brief delay
            import time
            time.sleep(0.1)
            if os.path.exists(path):
                os.unlink(path)

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository instance."""
        return ScenarioRepository(temp_db)

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "simulation": {"duration": 100.0, "random_seed": 42},
            "devices": [
                {
                    "id": "device_1",
                    "type": "machine",
                    "capacity": 1,
                    "initial_state": "Idle",
                    "recovery_time_range": None,
                }
            ],
            "flows": [
                {
                    "flow_id": "flow_1",
                    "from_device": "device_1",
                    "to_device": "device_1",
                    "process_time_range": (10.0, 20.0),
                    "priority": 1,
                    "dependencies": None,
                }
            ],
            "output_options": {"include_history": True, "include_events": True},
        }

    def test_save_scenario(self, repo, sample_config):
        """Test saving scenario to database."""
        scenario_id = repo.save(
            name="test_scenario",
            config=sample_config,
            description="Test scenario",
            tags=["test", "demo"],
        )

        assert scenario_id > 0

    def test_load_scenario_by_name(self, repo, sample_config):
        """Test loading scenario by name."""
        repo.save("test_scenario", sample_config)
        loaded_config = repo.load("test_scenario")

        # JSON serialization converts tuples to lists, so compare with normalization
        assert loaded_config["simulation"] == sample_config["simulation"]
        assert loaded_config["devices"] == sample_config["devices"]
        assert loaded_config["output_options"] == sample_config["output_options"]
        # Flows contain tuples that become lists in JSON
        assert loaded_config["flows"][0]["flow_id"] == sample_config["flows"][0]["flow_id"]
        assert list(loaded_config["flows"][0]["process_time_range"]) == list(sample_config["flows"][0]["process_time_range"])

    def test_load_scenario_by_id(self, repo, sample_config):
        """Test loading scenario by ID."""
        scenario_id = repo.save("test_scenario", sample_config)
        loaded_config = repo.load_by_id(scenario_id)

        # JSON serialization converts tuples to lists, so compare with normalization
        assert loaded_config["simulation"] == sample_config["simulation"]
        assert loaded_config["devices"] == sample_config["devices"]
        assert loaded_config["output_options"] == sample_config["output_options"]
        assert loaded_config["flows"][0]["flow_id"] == sample_config["flows"][0]["flow_id"]

    def test_update_scenario(self, repo, sample_config):
        """Test updating existing scenario."""
        repo.save("test_scenario", sample_config)

        # Modify config
        sample_config["simulation"]["duration"] = 200.0
        repo.update("test_scenario", sample_config, "Updated description")

        # Verify update
        loaded_config = repo.load("test_scenario")
        assert loaded_config["simulation"]["duration"] == 200.0

    def test_delete_scenario(self, repo, sample_config):
        """Test deleting scenario."""
        repo.save("test_scenario", sample_config)
        repo.delete("test_scenario")

        with pytest.raises(KeyError, match="not found"):
            repo.load("test_scenario")

    def test_list_all_scenarios(self, repo, sample_config):
        """Test listing all scenarios."""
        repo.save("scenario_1", sample_config, tags=["test"])
        repo.save("scenario_2", sample_config, tags=["demo"])

        scenarios = repo.list_all()
        assert len(scenarios) == 2
        assert scenarios[0]["name"] == "scenario_1"
        assert scenarios[1]["name"] == "scenario_2"

    def test_find_by_tags(self, repo, sample_config):
        """Test finding scenarios by tags."""
        repo.save("scenario_1", sample_config, tags=["healthcare", "blood"])
        repo.save("scenario_2", sample_config, tags=["manufacturing", "cnc"])
        repo.save("scenario_3", sample_config, tags=["healthcare", "surgery"])

        # Find healthcare scenarios
        results = repo.find_by_tags(["healthcare"])
        assert len(results) == 2

        # Find blood or cnc scenarios
        results = repo.find_by_tags(["blood", "cnc"])
        assert len(results) == 2

    def test_duplicate_name_raises_error(self, repo, sample_config):
        """Test that duplicate names raise ValueError."""
        repo.save("test_scenario", sample_config)

        with pytest.raises(ValueError, match="already exists"):
            repo.save("test_scenario", sample_config)

    def test_load_nonexistent_raises_error(self, repo):
        """Test that loading nonexistent scenario raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            repo.load("nonexistent")

    def test_update_nonexistent_raises_error(self, repo, sample_config):
        """Test that updating nonexistent scenario raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            repo.update("nonexistent", sample_config)

    def test_delete_nonexistent_raises_error(self, repo):
        """Test that deleting nonexistent scenario raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            repo.delete("nonexistent")


class TestResultsRepository:
    """Tests for ResultsRepository."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        # Force close any open connections before deleting file (Windows fix)
        import gc
        gc.collect()
        try:
            if os.path.exists(path):
                os.unlink(path)
        except PermissionError:
            # File still locked - try again after brief delay
            import time
            time.sleep(0.1)
            if os.path.exists(path):
                os.unlink(path)

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository instance."""
        return ResultsRepository(temp_db)

    @pytest.fixture
    def sample_results(self):
        """Sample results for testing."""
        return {
            "metadata": {
                "simulation_id": "sim_20260206_120000",
                "duration": 100.0,
                "random_seed": 42,
                "completed_at": "2026-02-06T12:00:00",
                "engine_version": "0.1.0",
            },
            "summary": {
                "total_events": 50,
                "total_flows_completed": 25,
                "devices_count": 2,
                "simulation_time_seconds": 100.0,
                "execution_time_seconds": 0.05,
            },
            "state_history": [
                {
                    "device_id": "device_1",
                    "timestamp": 0.0,
                    "from_state": "Idle",
                    "to_state": "Processing",
                    "event": "START_PROCESSING",
                },
                {
                    "device_id": "device_1",
                    "timestamp": 10.0,
                    "from_state": "Processing",
                    "to_state": "Idle",
                    "event": "COMPLETE_PROCESSING",
                },
            ],
            "flows_executed": [{"flow_id": "flow_1", "execution_count": 25}],
        }

    def test_save_results(self, repo, sample_results):
        """Test saving simulation results."""
        simulation_id = repo.save(sample_results, scenario_name="test_scenario")
        assert simulation_id == "sim_20260206_120000"

    def test_load_results(self, repo, sample_results):
        """Test loading simulation results."""
        repo.save(sample_results, scenario_name="test_scenario")
        loaded = repo.load("sim_20260206_120000")

        assert loaded["metadata"]["simulation_id"] == "sim_20260206_120000"
        assert loaded["summary"]["total_events"] == 50
        assert len(loaded["state_history"]) == 2
        assert len(loaded["flows_executed"]) == 1

    def test_list_by_scenario(self, repo, sample_results):
        """Test listing results by scenario name."""
        # Save multiple runs of same scenario
        sample_results["metadata"]["simulation_id"] = "sim_run_1"
        repo.save(sample_results, scenario_name="test_scenario")

        sample_results["metadata"]["simulation_id"] = "sim_run_2"
        repo.save(sample_results, scenario_name="test_scenario")

        # List results
        results = repo.list_by_scenario("test_scenario")
        assert len(results) == 2

    def test_delete_results(self, repo, sample_results):
        """Test deleting simulation results."""
        simulation_id = repo.save(sample_results)
        repo.delete(simulation_id)

        with pytest.raises(KeyError, match="not found"):
            repo.load(simulation_id)

    def test_load_nonexistent_raises_error(self, repo):
        """Test that loading nonexistent results raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            repo.load("nonexistent_id")

    def test_delete_nonexistent_raises_error(self, repo):
        """Test that deleting nonexistent results raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            repo.delete("nonexistent_id")

    def test_get_device_utilization(self, repo, sample_results):
        """Test calculating device utilization."""
        simulation_id = repo.save(sample_results)
        utilization = repo.get_device_utilization(simulation_id)

        assert "device_1" in utilization
        assert 0 <= utilization["device_1"] <= 100
