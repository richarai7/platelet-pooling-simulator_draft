"""
Demo: SQLite Persistence Layer
Demonstrates saving/loading scenarios and results to SQLite database
"""

from simulation_engine import SimulationEngine, ScenarioRepository, ResultsRepository
import json

print("=" * 80)
print("SQLITE PERSISTENCE DEMO")
print("=" * 80)
print()

# ============================================================================
# PART 1: Scenario Management
# ============================================================================
print("📂 PART 1: Saving Scenarios to SQLite")
print("-" * 80)

scenario_repo = ScenarioRepository("demo_scenarios.db")

# Define a healthcare scenario
healthcare_config = {
    "simulation": {"duration": 100.0, "random_seed": 42},
    "devices": [
        {
            "id": "centrifuge_001",
            "type": "centrifuge",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None,
        },
        {
            "id": "pooling_station",
            "type": "workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": None,
        },
    ],
    "flows": [
        {
            "flow_id": "spin_platelets",
            "from_device": "centrifuge_001",
            "to_device": "pooling_station",
            "process_time_range": (10.0, 20.0),
            "priority": 10,
            "dependencies": None,
        }
    ],
    "output_options": {"include_history": True, "include_events": True},
}

# Save scenario to database
scenario_id = scenario_repo.save(
    name="platelet_processing_v1",
    config=healthcare_config,
    description="Basic platelet processing workflow with 2 devices",
    tags=["healthcare", "blood-processing", "platelet"],
)

print(f"✅ Saved scenario 'platelet_processing_v1' (ID: {scenario_id})")
print()

# Define a manufacturing scenario
manufacturing_config = {
    "simulation": {"duration": 200.0, "random_seed": 123},
    "devices": [
        {
            "id": "cnc_mill_01",
            "type": "cnc_machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (60.0, 120.0),
        },
        {
            "id": "assembly_bench",
            "type": "workstation",
            "capacity": 3,
            "initial_state": "Idle",
            "recovery_time_range": None,
        },
    ],
    "flows": [
        {
            "flow_id": "mill_part",
            "from_device": "cnc_mill_01",
            "to_device": "assembly_bench",
            "process_time_range": (15.0, 25.0),
            "priority": 5,
            "dependencies": None,
        }
    ],
    "output_options": {"include_history": False, "include_events": True},
}

scenario_id = scenario_repo.save(
    name="cnc_manufacturing_v1",
    config=manufacturing_config,
    description="CNC milling and assembly workflow",
    tags=["manufacturing", "cnc", "assembly"],
)

print(f"✅ Saved scenario 'cnc_manufacturing_v1' (ID: {scenario_id})")
print()

# List all scenarios
print("📋 All saved scenarios:")
for scenario in scenario_repo.list_all():
    print(f"  - {scenario['name']}: {scenario['description']}")
    print(f"    Tags: {scenario['tags']}")
    print(f"    Created: {scenario['created_at']}")
print()

# ============================================================================
# PART 2: Loading and Running Scenarios
# ============================================================================
print("▶️  PART 2: Loading and Running Saved Scenarios")
print("-" * 80)

# Load healthcare scenario from database
loaded_config = scenario_repo.load("platelet_processing_v1")
print("✅ Loaded 'platelet_processing_v1' from database")

# Run simulation with loaded config
engine = SimulationEngine(loaded_config)
results = engine.run()

print(f"✅ Simulation complete:")
print(f"   - Total events: {results['summary']['total_events']}")
print(f"   - Flows completed: {results['summary']['total_flows_completed']}")
print(f"   - Execution time: {results['summary']['execution_time_seconds']}s")
print()

# ============================================================================
# PART 3: Saving Simulation Results
# ============================================================================
print("💾 PART 3: Saving Results to SQLite")
print("-" * 80)

results_repo = ResultsRepository("demo_results.db")

# Save results with scenario link
simulation_id = results_repo.save(results, scenario_name="platelet_processing_v1")
print(f"✅ Saved results (ID: {simulation_id})")
print()

# Run scenario again with different seed
import time
time.sleep(1)  # Ensure different timestamp
loaded_config["simulation"]["random_seed"] = 999
engine = SimulationEngine(loaded_config)
results2 = engine.run()
simulation_id2 = results_repo.save(results2, scenario_name="platelet_processing_v1")
print(f"✅ Saved second run (ID: {simulation_id2})")
print()

# ============================================================================
# PART 4: Comparing Multiple Runs
# ============================================================================
print("📊 PART 4: Comparing Multiple Simulation Runs")
print("-" * 80)

# List all runs for this scenario
runs = results_repo.list_by_scenario("platelet_processing_v1")
print(f"Found {len(runs)} simulation runs for 'platelet_processing_v1':\n")

for run in runs:
    print(f"  Run: {run['simulation_id']}")
    print(f"    Completed: {run['completed_at']}")
    print(f"    Events: {run['total_events']}")
    print(f"    Flows completed: {run['total_flows_completed']}")
    print(f"    Execution time: {run['execution_time_seconds']}s")
    print()

# ============================================================================
# PART 5: Finding Scenarios by Tags
# ============================================================================
print("🔍 PART 5: Finding Scenarios by Tags")
print("-" * 80)

# Find all healthcare scenarios
healthcare_scenarios = scenario_repo.find_by_tags(["healthcare"])
print(f"Healthcare scenarios ({len(healthcare_scenarios)}):")
for s in healthcare_scenarios:
    print(f"  - {s['name']}")
print()

# Find all manufacturing scenarios
manufacturing_scenarios = scenario_repo.find_by_tags(["manufacturing"])
print(f"Manufacturing scenarios ({len(manufacturing_scenarios)}):")
for s in manufacturing_scenarios:
    print(f"  - {s['name']}")
print()

# ============================================================================
# PART 6: Loading Historical Results
# ============================================================================
print("📂 PART 6: Loading Historical Results")
print("-" * 80)

# Load first run's detailed results
loaded_results = results_repo.load(simulation_id)
print(f"Loaded results for {simulation_id}:")
print(f"  - Devices: {loaded_results['summary']['devices_count']}")
print(f"  - State transitions: {len(loaded_results['state_history'])}")
print(f"  - Flow executions: {len(loaded_results['flows_executed'])}")
print()

print("State history (first 3 events):")
for event in loaded_results["state_history"][:3]:
    print(
        f"  T={event['timestamp']:6.2f}s: {event['device_id']:20s} "
        f"{event['from_state']:10s} -> {event['to_state']:10s}"
    )
print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("✅ DEMO COMPLETE")
print("=" * 80)
print()
print("Created databases:")
print("  - demo_scenarios.db  (2 scenarios)")
print("  - demo_results.db    (2 simulation runs)")
print()
print("Key Features Demonstrated:")
print("  ✅ Save/load configurations from SQLite")
print("  ✅ Tag-based scenario organization")
print("  ✅ Store complete simulation results")
print("  ✅ Compare multiple simulation runs")
print("  ✅ Query historical data")
print()
print("Use Cases:")
print("  - A/B testing different configurations")
print("  - Historical performance tracking")
print("  - Scenario library management")
print("  - What-if analysis comparisons")
