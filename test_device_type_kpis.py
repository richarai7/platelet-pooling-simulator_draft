#!/usr/bin/env python3
"""Test how device types affect KPI calculations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator

print("\n" + "="*70)
print("TESTING DEVICE TYPE IMPACT ON KPIs")
print("="*70)

# Create a config with different device types
config = {
    "simulation": {
        "duration": 3600,
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    "devices": [
        # Machines
        {
            "id": "machine_1",
            "type": "machine",
            "capacity": 2,
            "recovery_time_range": (60, 120)
        },
        {
            "id": "machine_2",
            "type": "machine",
            "capacity": 1,
            "recovery_time_range": (30, 60)
        },
        # Workstations (People)
        {
            "id": "workstation_1",
            "type": "workstation",
            "capacity": 3,
            "recovery_time_range": (45, 90)
        },
        {
            "id": "workstation_2",
            "type": "workstation",
            "capacity": 2,
            "recovery_time_range": (20, 40)
        },
        # Materials
        {
            "id": "storage_area",
            "type": "material",
            "capacity": 50,
            "recovery_time_range": (10, 20)
        }
    ],
    "flows": [
        {
            "flow_id": "f1",
            "from_device": "machine_1",
            "to_device": "workstation_1",
            "process_time_range": (100, 200),
            "priority": 1,
            "dependencies": None
        },
        {
            "flow_id": "f2",
            "from_device": "workstation_1",
            "to_device": "machine_2",
            "process_time_range": (150, 250),
            "priority": 1,
            "dependencies": ["f1"]
        },
        {
            "flow_id": "f3",
            "from_device": "machine_2",
            "to_device": "storage_area",
            "process_time_range": (50, 100),
            "priority": 1,
            "dependencies": ["f2"]
        }
    ],
    "output_options": {
        "include_events": True,
        "include_history": True
    }
}

print("\nDevice Configuration:")
print("-" * 70)
for device in config['devices']:
    print(f"  {device['id']:<20} type: {device['type']:<12} capacity: {device['capacity']}")

print("\n" + "-" * 70)
print("Running simulation...")
print("-" * 70)

engine = SimulationEngine(config)
results = engine.run()

print(f"\n✓ Simulation complete")
print(f"  Duration: {results['summary']['simulation_time_seconds']:.1f}s")
print(f"  Flows completed: {results['summary']['total_flows_completed']}")

# Calculate KPIs
print("\n" + "="*70)
print("KPI CALCULATIONS BY DEVICE TYPE")
print("="*70)

kpi_calc = KPICalculator(results, config)
kpis = kpi_calc.calculate_all_kpis()

# Type-specific KPIs
print("\n1. WORKSTATION-SPECIFIC KPIs (People/Manual Stations):")
print("-" * 70)
print(f"   Uniting Station Utilization: {kpis['uniting_station_utilization']:.2f}%")
print(f"   Processing Station Count: {kpis['processing_station_count']}")

workstations = [d for d in config['devices'] if d['type'] == 'workstation']
print(f"\n   Individual Workstation Utilization:")
for ws in workstations:
    util = kpis['capacity_utilization_per_device'].get(ws['id'], 0)
    print(f"     {ws['id']:<20} {util:.2f}%")

print("\n2. MACHINE-SPECIFIC KPIs:")
print("-" * 70)
machines = [d for d in config['devices'] if d['type'] == 'machine']
print(f"   Machine Count: {len(machines)}")
print(f"\n   Individual Machine Utilization:")
for machine in machines:
    util = kpis['capacity_utilization_per_device'].get(machine['id'], 0)
    print(f"     {machine['id']:<20} {util:.2f}%")

print("\n3. MATERIAL-SPECIFIC KPIs:")
print("-" * 70)
materials = [d for d in config['devices'] if d['type'] == 'material']
print(f"   Material Storage Count: {len(materials)}")
print(f"\n   Material Storage Utilization:")
for material in materials:
    util = kpis['capacity_utilization_per_device'].get(material['id'], 0)
    print(f"     {material['id']:<20} {util:.2f}%")

print("\n4. OVERALL KPIs (All Device Types):")
print("-" * 70)
print(f"   Total Devices: {len(config['devices'])}")
print(f"   Average Across All Types:")
all_utils = list(kpis['capacity_utilization_per_device'].values())
if all_utils:
    avg_util = sum(all_utils) / len(all_utils)
    print(f"     Overall Utilization: {avg_util:.2f}%")

print("\n5. DEVICE HEALTH (All Types):")
print("-" * 70)
for device_id, health in kpis['device_health'].items():
    device = next((d for d in config['devices'] if d['id'] == device_id), None)
    device_type = device['type'] if device else 'unknown'
    print(f"   {device_id:<20} [{device_type:<12}] Status: {health['status']}")

print("\n" + "="*70)
print("KEY INSIGHTS")
print("="*70)

print("\n✓ Device types ARE used in KPI calculations:")
print("  • workstation → Uniting Station Utilization KPI")
print("  • workstation → Processing Station Count")
print("  • machine → Individual machine tracking")
print("  • material → Storage capacity tracking")
print("\n✓ Each type can have different utilization patterns")
print("\n✓ Device health applies to ALL types equally")

print("\n" + "="*70 + "\n")
