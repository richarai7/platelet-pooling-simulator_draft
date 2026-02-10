"""
Demo: Domain-Agnostic Simulation Engine
Demonstrates the same engine running three different industries
"""

from simulation_engine import SimulationEngine
import json

print("=" * 70)
print("DISCRETE EVENT SIMULATION ENGINE - DOMAIN-AGNOSTIC DEMO")
print("=" * 70)
print()

# Demo 1: Healthcare - Platelet Pooling
print("📊 DEMO 1: Healthcare - Blood Processing")
print("-" * 70)

healthcare_config = {
    "simulation": {"duration": 100.0, "random_seed": 42},
    "devices": [
        {
            "id": "centrifuge_001",
            "type": "centrifuge",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None
        },
        {
            "id": "pooling_station",
            "type": "workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "spin_platelets",
            "from_device": "centrifuge_001",
            "to_device": "pooling_station",
            "process_time_range": (10.0, 20.0),
            "priority": 10,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": True}
}

engine = SimulationEngine(healthcare_config)
results = engine.run()

print(f"✓ Simulated {results['summary']['simulation_time_seconds']}s of blood processing")
print(f"✓ Processed {results['summary']['total_flows_completed']} platelet units")
print(f"✓ Execution time: {results['summary']['execution_time_seconds']}s")
print(f"✓ Total events: {results['summary']['total_events']}")
print()

# Demo 2: Manufacturing - Assembly Line
print("🏭 DEMO 2: Manufacturing - CNC Machining")
print("-" * 70)

manufacturing_config = {
    "simulation": {"duration": 100.0, "random_seed": 123},
    "devices": [
        {
            "id": "cnc_mill_01",
            "type": "cnc_machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None
        },
        {
            "id": "assembly_bench",
            "type": "workstation",
            "capacity": 3,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "mill_part",
            "from_device": "cnc_mill_01",
            "to_device": "assembly_bench",
            "process_time_range": (15.0, 25.0),
            "priority": 5,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": False, "include_events": True}
}

engine = SimulationEngine(manufacturing_config)
results = engine.run()

print(f"✓ Simulated {results['summary']['simulation_time_seconds']}s of manufacturing")
print(f"✓ Machined {results['summary']['total_flows_completed']} parts")
print(f"✓ Execution time: {results['summary']['execution_time_seconds']}s")
print(f"✓ Total events: {results['summary']['total_events']}")
print()

# Demo 3: Logistics - Warehouse Operations
print("📦 DEMO 3: Logistics - Warehouse Operations")
print("-" * 70)

logistics_config = {
    "simulation": {"duration": 100.0, "random_seed": 999},
    "devices": [
        {
            "id": "forklift_a",
            "type": "forklift",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None
        },
        {
            "id": "loading_dock",
            "type": "dock",
            "capacity": 5,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "transport_pallet",
            "from_device": "forklift_a",
            "to_device": "loading_dock",
            "process_time_range": (8.0, 12.0),
            "priority": 1,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": False}
}

engine = SimulationEngine(logistics_config)
results = engine.run()

print(f"✓ Simulated {results['summary']['simulation_time_seconds']}s of warehouse ops")
print(f"✓ Transported {results['summary']['total_flows_completed']} pallets")
print(f"✓ Execution time: {results['summary']['execution_time_seconds']}s")
print(f"✓ Total events: {results['summary']['total_events']}")
print()

print("=" * 70)
print("✅ PROOF OF DOMAIN-AGNOSTIC DESIGN")
print("=" * 70)
print("Same engine code executed:")
print("  • Healthcare: Blood processing workflow")
print("  • Manufacturing: CNC machining operations")
print("  • Logistics: Warehouse pallet transport")
print()
print("Only configuration changed - ZERO code changes required!")
print("=" * 70)
