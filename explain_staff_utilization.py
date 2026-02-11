#!/usr/bin/env python3
"""Test current staff utilization calculation and show how to improve it."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "api"))

from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator
from api.templates import get_platelet_template

print("\n" + "="*70)
print("CURRENT STAFF UTILIZATION CALCULATION")
print("="*70)

# Get the template
config = get_platelet_template()

print("\nCurrent Device Types in Template:")
print("-" * 70)
type_counts = {}
for device in config['devices']:
    dtype = device['type']
    type_counts[dtype] = type_counts.get(dtype, 0) + 1
    print(f"  {device['id']:<25} type: {dtype}")

print(f"\nType Summary:")
for dtype, count in type_counts.items():
    print(f"  {dtype}: {count} devices")

# Run simulation
print("\n" + "-" * 70)
print("Running simulation...")
print("-" * 70)

engine = SimulationEngine(config)
results = engine.run()

# Calculate KPIs
kpi_calc = KPICalculator(results, config)
kpis = kpi_calc.calculate_all_kpis()

print("\n" + "="*70)
print("CURRENT STAFF METRICS")
print("="*70)

print(f"\n1. Staff Count: {kpis['staff_count']}")
print(f"   ⚠️  This comes from config.get('staff_count', 0)")
print(f"   ⚠️  NOT calculated from device types!")

print(f"\n2. Staff Utilization: {kpis['staff_utilization']:.2f}%")
print(f"   ⚠️  This comes from config.get('staff_utilization', 0.0)")
print(f"   ⚠️  It's a PLACEHOLDER - not actually calculated!")

print(f"\n3. Uniting Station Utilization: {kpis['uniting_station_utilization']:.2f}%")
print(f"   ✓ This IS calculated from workstation device types")
print(f"   ✓ Average of: {[d['id'] for d in config['devices'] if d['type'] == 'workstation']}")

print("\n" + "="*70)
print("HOW IT CURRENTLY WORKS")
print("="*70)

print("\nFrom kpi_calculator.py lines 285-292:")
print("""
    def _staff_count(self) -> int:
        '''Number of staff/technicians working.'''
        return self.config.get('staff_count', 0)  # ← Reads from config
    
    def _staff_utilization(self) -> float:
        '''% time staff actively working.'''
        # Placeholder - would need staff tracking in config
        return self.config.get('staff_utilization', 0.0)  # ← Reads from config
""")

print("\n⚠️  PROBLEM: These don't use device types at all!")
print("   They expect manual configuration values that aren't set.")

print("\n" + "="*70)
print("WHAT HAPPENS IF YOU ADD 'people' TYPE")
print("="*70)

print("\nScenario: Change some devices from 'workstation' to 'people'")
print("-" * 70)

# Create modified config
import copy
modified_config = copy.deepcopy(config)

# Change workstation to people
for device in modified_config['devices']:
    if device['type'] == 'workstation':
        device['type'] = 'people'  # New type

print("\nModified device types:")
for device in modified_config['devices']:
    if device['type'] == 'people':
        print(f"  {device['id']:<25} type: {device['type']} (was: workstation)")

# Run modified simulation
engine2 = SimulationEngine(modified_config)
results2 = engine2.run()

kpi_calc2 = KPICalculator(results2, modified_config)
kpis2 = kpi_calc2.calculate_all_kpis()

print("\nKPI Results with 'people' type:")
print("-" * 70)
print(f"  Uniting Station Utilization: {kpis2['uniting_station_utilization']:.2f}%")
print(f"  Staff Count: {kpis2['staff_count']}")
print(f"  Staff Utilization: {kpis2['staff_utilization']:.2f}%")

print("\n❌ IMPACT:")
print("  • Uniting Station Utilization dropped to 0% (no workstations found)")
print("  • Staff Count still 0 (doesn't check 'people' type)")
print("  • Staff Utilization still 0% (doesn't check 'people' type)")

print("\n" + "="*70)
print("RECOMMENDATION: IMPROVE STAFF UTILIZATION CALCULATION")
print("="*70)

print("""
OPTION 1: Use 'workstation' type consistently
  ✓ Already works with current code
  ✓ Uniting Station Utilization calculates automatically
  ✗ Name might be confusing (not specifically "people")

OPTION 2: Add 'people' type and update KPI calculator
  ✓ More intuitive naming
  ✓ Separate people from equipment/workstations
  ✗ Requires code change in kpi_calculator.py

OPTION 3: Add calculated staff metrics
  Change _staff_utilization() to:
  
    def _staff_utilization(self) -> float:
        # Option A: Use same as workstation utilization
        return self._device_type_utilization("workstation")
        
        # OR Option B: Use 'people' type if exists
        people_util = self._device_type_utilization("people")
        workstation_util = self._device_type_utilization("workstation")
        return people_util if people_util > 0 else workstation_util
  
  And _staff_count() to:
  
    def _staff_count(self) -> int:
        # Count people or workstation devices
        return sum(1 for d in self.config['devices'] 
                   if d.get('type') in ['people', 'workstation'])
""")

print("\n" + "="*70)
print("CURRENT STATE SUMMARY")
print("="*70)

print("""
✓ You HAVE workstation types (4 devices):
  - pooling_station
  - sterile_connect
  - label_station
  - packaging_station

✓ Uniting Station Utilization DOES calculate from workstation type

❌ staff_count: Returns 0 (not calculated from types)
❌ staff_utilization: Returns 0% (not calculated from types)

✅ EASY FIX: These are just placeholders waiting to be implemented!
""")

print("\n" + "="*70 + "\n")
