"""SQLite persistence layer for scenarios and simulation results."""

import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class ScenarioRepository:
    """
    Manages scenario configurations in SQLite database.
    
    Provides CRUD operations for simulation scenarios.
    """

    def __init__(self, db_path: str = "simulation_scenarios.db") -> None:
        """Initialize repository with database path."""
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    config_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_scenarios_name ON scenarios(name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_scenarios_tags ON scenarios(tags)"
            )
            conn.commit()

    def save(
        self,
        name: str,
        config: Dict[str, Any],
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save scenario configuration to database."""
        config_json = json.dumps(config, indent=2, sort_keys=True)
        tags_str = ",".join(tags) if tags else ""

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "INSERT INTO scenarios (name, description, config_json, tags) VALUES (?, ?, ?, ?)",
                (name, description, config_json, tags_str),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Scenario '{name}' already exists. Use update() to modify it.")
        finally:
            if conn:
                conn.close()

    def load(self, name: str) -> Dict[str, Any]:
        """Load scenario configuration by name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT config_json FROM scenarios WHERE name = ?", (name,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Scenario '{name}' not found")
            return json.loads(row[0])

    def load_by_id(self, scenario_id: int) -> Dict[str, Any]:
        """Load scenario configuration by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT config_json FROM scenarios WHERE id = ?", (scenario_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Scenario ID {scenario_id} not found")
            return json.loads(row[0])

    def update(self, name: str, config: Dict[str, Any], description: str = "") -> None:
        """Update existing scenario."""
        config_json = json.dumps(config, indent=2, sort_keys=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """UPDATE scenarios SET config_json = ?, description = ?, 
                   updated_at = CURRENT_TIMESTAMP WHERE name = ?""",
                (config_json, description, name),
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"Scenario '{name}' not found")

    def delete(self, name: str) -> None:
        """Delete scenario by name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM scenarios WHERE name = ?", (name,))
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"Scenario '{name}' not found")

    def list_all(self) -> List[Dict[str, Any]]:
        """List all scenarios with metadata."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, description, created_at, updated_at, tags FROM scenarios ORDER BY name"
            )
            return [dict(row) for row in cursor.fetchall()]

    def find_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Find scenarios by tags."""
        tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
        tag_patterns = [f"%{tag}%" for tag in tags]
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"""SELECT id, name, description, created_at, updated_at, tags
                    FROM scenarios WHERE {tag_conditions} ORDER BY name""",
                tag_patterns,
            )
            return [dict(row) for row in cursor.fetchall()]


class ResultsRepository:
    """Manages simulation results in SQLite database."""

    def __init__(self, db_path: str = "simulation_results.db") -> None:
        """Initialize repository with database path."""
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS simulation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT UNIQUE NOT NULL,
                    scenario_name TEXT,
                    duration REAL NOT NULL,
                    random_seed INTEGER NOT NULL,
                    total_events INTEGER NOT NULL,
                    total_flows_completed INTEGER NOT NULL,
                    devices_count INTEGER NOT NULL,
                    simulation_time_seconds REAL NOT NULL,
                    execution_time_seconds REAL NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    metadata_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_state_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    event TEXT NOT NULL,
                    FOREIGN KEY (simulation_id) REFERENCES simulation_results(simulation_id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flow_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    flow_id TEXT NOT NULL,
                    execution_count INTEGER NOT NULL,
                    FOREIGN KEY (simulation_id) REFERENCES simulation_results(simulation_id) ON DELETE CASCADE
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_scenario ON simulation_results(scenario_name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_history_sim_device ON device_state_history(simulation_id, device_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_flows_sim ON flow_executions(simulation_id)"
            )
            conn.commit()

    def save(self, results: Dict[str, Any], scenario_name: Optional[str] = None) -> str:
        """Save simulation results to database."""
        metadata = results["metadata"]
        summary = results["summary"]
        simulation_id = metadata["simulation_id"]

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """INSERT INTO simulation_results (
                    simulation_id, scenario_name, duration, random_seed,
                    total_events, total_flows_completed, devices_count,
                    simulation_time_seconds, execution_time_seconds,
                    completed_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    simulation_id, scenario_name, metadata["duration"], metadata["random_seed"],
                    summary["total_events"], summary["total_flows_completed"],
                    summary["devices_count"], summary["simulation_time_seconds"],
                    summary["execution_time_seconds"], metadata["completed_at"],
                    json.dumps(metadata),
                ),
            )

            if "state_history" in results:
                for event in results["state_history"]:
                    conn.execute(
                        """INSERT INTO device_state_history (
                            simulation_id, device_id, timestamp,
                            from_state, to_state, event
                        ) VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            simulation_id, event["device_id"], event["timestamp"],
                            event["from_state"], event["to_state"], event["event"],
                        ),
                    )

            if "flows_executed" in results:
                for flow in results["flows_executed"]:
                    conn.execute(
                        "INSERT INTO flow_executions (simulation_id, flow_id, execution_count) VALUES (?, ?, ?)",
                        (simulation_id, flow["flow_id"], flow["execution_count"]),
                    )

            conn.commit()
            return simulation_id
        finally:
            if conn:
                conn.close()

    def load(self, simulation_id: str) -> Dict[str, Any]:
        """Load complete simulation results by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM simulation_results WHERE simulation_id = ?", (simulation_id,)
            )
            result_row = cursor.fetchone()
            if not result_row:
                raise KeyError(f"Simulation '{simulation_id}' not found")

            results = {
                "metadata": json.loads(result_row["metadata_json"]),
                "summary": {
                    "total_events": result_row["total_events"],
                    "total_flows_completed": result_row["total_flows_completed"],
                    "devices_count": result_row["devices_count"],
                    "simulation_time_seconds": result_row["simulation_time_seconds"],
                    "execution_time_seconds": result_row["execution_time_seconds"],
                },
            }

            cursor = conn.execute(
                """SELECT device_id, timestamp, from_state, to_state, event
                   FROM device_state_history WHERE simulation_id = ? ORDER BY timestamp""",
                (simulation_id,),
            )
            results["state_history"] = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT flow_id, execution_count FROM flow_executions WHERE simulation_id = ?",
                (simulation_id,),
            )
            results["flows_executed"] = [dict(row) for row in cursor.fetchall()]
            return results

    def list_by_scenario(self, scenario_name: str) -> List[Dict[str, Any]]:
        """List all simulation runs for a scenario."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT simulation_id, completed_at, total_events,
                       total_flows_completed, simulation_time_seconds,
                       execution_time_seconds
                   FROM simulation_results WHERE scenario_name = ?
                   ORDER BY completed_at DESC""",
                (scenario_name,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete(self, simulation_id: str) -> None:
        """Delete simulation results."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM simulation_results WHERE simulation_id = ?", (simulation_id,)
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(f"Simulation '{simulation_id}' not found")

    def get_device_utilization(self, simulation_id: str) -> Dict[str, float]:
        """Calculate device utilization from state history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT simulation_time_seconds FROM simulation_results WHERE simulation_id = ?",
                (simulation_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Simulation '{simulation_id}' not found")
            total_time = row[0]

            cursor = conn.execute(
                """SELECT device_id,
                       SUM(CASE WHEN to_state = 'Processing' THEN 1 ELSE 0 END) as processing_events
                   FROM device_state_history WHERE simulation_id = ? GROUP BY device_id""",
                (simulation_id,),
            )

            utilization = {}
            for row in cursor.fetchall():
                device_id, events = row
                utilization[device_id] = min(100.0, (events / max(1, total_time)) * 100)
            return utilization
