"""Test device health monitoring in the simulator."""

from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator

# Configuration with devices that might fail/block
config = {
    "simulation": {
        "duration": 7200,  # 2 hours
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    "devices": [
        {
            "id": "device_001",
            "type": "centrifuge",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)  # Can fail temporarily
        },
        {
            "id": "device_002",
            "type": "workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": None  # Won't fail
        },
        {
            "id": "device_003",
            "type": "testing_lab",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (600, 900)  # Can fail
        }
    ],
    "flows": [
        {
            "flow_id": "flow_001",
            "from_device": "device_001",
            "to_device": "device_002",
            "process_time_range": (600, 1200),
            "priority": 10,
            "dependencies": None
        },
        {
            "flow_id": "flow_002",
            "from_device": "device_002",
            "to_device": "device_003",
            "process_time_range": (300, 600),
            "priority": 5,
            "dependencies": None
        }
    ],
    "output_options": {
        "include_history": True,
        "include_events": True
    }
}

# Run simulation
print("🔧 Running simulation to test device health...")
engine = SimulationEngine(config)
results = engine.run()

# Calculate KPIs (includes device health)
print("\n📊 Calculating KPIs with device health status...")
kpi_calc = KPICalculator(results, config)
kpis = kpi_calc.calculate()

# Display device health
print("\n💚 DEVICE HEALTH STATUS:")
print("=" * 50)
for device_id, health_status in kpis['device_health'].items():
    status_icon = {
        'Healthy': '✅',
        'Warning': '⚠️',
        'Critical': '🔴'
    }.get(health_status, '❓')
    
    print(f"{status_icon} {device_id}: {health_status}")

# Show final device states
print("\n📋 FINAL DEVICE STATES:")
print("=" * 50)
if 'device_states' in results:
    for device in results['device_states']:
        print(f"  {device['device_id']}: {device['final_state']}")

# Show utilization (can indicate blocking)
print("\n⚙️ DEVICE UTILIZATION:")
print("=" * 50)
for device_id, util in kpis['capacity_utilization_per_device'].items():
    print(f"  {device_id}: {util:.1f}%")

print("\n✅ Test complete!")
