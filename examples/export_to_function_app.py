"""
Export simulation KPIs to Azure Function App or API endpoint
Formats all metrics for downstream processing
"""

import json
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator


def run_simulation_and_export(
    config: dict,
    function_app_url: str = None,
    export_to_file: bool = True
):
    """
    Run simulation, calculate all KPIs, and export to function app.
    
    Args:
        config: Simulation configuration
        function_app_url: Azure Function App endpoint URL (optional)
        export_to_file: Save to JSON file (default True)
    
    Returns:
        Dictionary with all KPIs
    """
    
    print("\n" + "=" * 90)
    print("  RUNNING SIMULATION & CALCULATING KPIs")
    print("=" * 90)
    
    # Run simulation
    print("\n1. Executing simulation...")
    engine = SimulationEngine(config)
    result = engine.run()
    
    print(f"   ✓ Simulation complete")
    print(f"   • Time: {result['summary']['simulation_time_seconds'] / 60:.1f} minutes")
    print(f"   • Flows completed: {result['summary']['total_flows_completed']}")
    
    # Calculate KPIs
    print("\n2. Calculating comprehensive KPIs...")
    calculator = KPICalculator(result, config)
    all_kpis = calculator.calculate_all_kpis()
    
    print(f"   ✓ {len(all_kpis)} KPIs calculated")
    
    # Export to file
    if export_to_file:
        output_file = f"kpi_export_{all_kpis['simulation_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(all_kpis, f, indent=2, default=str)
        
        print(f"\n3. Exported to file: {output_file}")
    
    # Send to Function App
    if function_app_url:
        print(f"\n4. Sending to Function App: {function_app_url}")
        
        try:
            response = requests.post(
                function_app_url,
                json=all_kpis,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✓ Successfully sent to function app")
                print(f"   • Response: {response.json()}")
            else:
                print(f"   ✗ Error: Status {response.status_code}")
                print(f"   • Response: {response.text}")
        
        except Exception as e:
            print(f"   ✗ Failed to send: {e}")
    
    # Display key metrics
    print("\n" + "=" * 90)
    print("  KEY PERFORMANCE INDICATORS")
    print("=" * 90)
    
    print(f"\n📊 PRODUCTION METRICS:")
    print(f"   • Total Units Created: {all_kpis['total_units_created']}")
    print(f"   • Quality Pass Rate: {all_kpis['quality_pass_rate']:.1f}%")
    print(f"   • Current Throughput: {all_kpis['current_throughput']:.2f} units/hour")
    print(f"   • Average Cycle Time: {all_kpis['average_cycle_time']:.1f} seconds")
    
    print(f"\n⚙️  UTILIZATION:")
    capacity_util = all_kpis['capacity_utilization_per_device']
    for device, util in list(capacity_util.items())[:5]:
        print(f"   • {device}: {util:.1f}%")
    
    print(f"\n💰 COST ANALYSIS:")
    print(f"   • Total Operating Cost: ${all_kpis['total_operating_cost']:.2f}")
    print(f"   • Cost Per Unit: ${all_kpis['cost_per_unit']:.2f}")
    print(f"   • Waste Rate: {all_kpis['waste_rate']:.1f}%")
    print(f"   • Waste Cost: ${all_kpis['waste_cost']:.2f}")
    
    print(f"\n🎯 BOTTLENECK ANALYSIS:")
    print(f"   • Identified Bottleneck: {all_kpis['resource_bottleneck']}")
    print(f"   • Max Queue Length: {all_kpis['max_queue_length']}")
    
    if all_kpis['optimization_suggestions']:
        print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
        for suggestion in all_kpis['optimization_suggestions'][:3]:
            print(f"   • {suggestion}")
    
    print("\n" + "=" * 90 + "\n")
    
    return all_kpis


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    
    # Example configuration
    config = {
        "simulation": {
            "duration": 100000,
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        "output_options": {
            "include_history": True,
            "include_flow_details": True
        },
        # Add cost parameters
        "labor_cost": 1000,
        "material_cost": 50,
        "overhead_cost": 500,
        "cost_per_unit": 75,
        "baseline_throughput": 5.0,
        
        # Scenario info
        "run_name": "Baseline_Run_001",
        "scenario_name": "Platelet Pooling - Baseline",
        
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": 2,
             "recovery_time_range": (1, 2)},
            {"id": "separator", "type": "machine", "capacity": 2,
             "recovery_time_range": (1, 2)},
            {"id": "quality", "type": "machine", "capacity": 1,
             "recovery_time_range": (1, 2)}
        ],
        "flows": [
            {"flow_id": "batch1_centrifuge", "from_device": "centrifuge",
             "to_device": "separator", "process_time_range": (300, 480),
             "priority": 1, "dependencies": None},
            {"flow_id": "batch1_separator", "from_device": "separator",
             "to_device": "quality", "process_time_range": (600, 900),
             "priority": 1, "dependencies": ["batch1_centrifuge"]},
            {"flow_id": "batch1_quality", "from_device": "quality",
             "to_device": "quality", "process_time_range": (180, 300),
             "priority": 1, "dependencies": ["batch1_separator"]},
            
            {"flow_id": "batch2_centrifuge", "from_device": "centrifuge",
             "to_device": "separator", "process_time_range": (300, 480),
             "priority": 1, "dependencies": None},
            {"flow_id": "batch2_separator", "from_device": "separator",
             "to_device": "quality", "process_time_range": (600, 900),
             "priority": 1, "dependencies": ["batch2_centrifuge"]},
            {"flow_id": "batch2_quality", "from_device": "quality",
             "to_device": "quality", "process_time_range": (180, 300),
             "priority": 1, "dependencies": ["batch2_separator"]},
        ]
    }
    
    # Run and export
    # Option 1: Export to file only
    kpis = run_simulation_and_export(config, export_to_file=True)
    
    # Option 2: Send to Azure Function App
    # FUNCTION_APP_URL = "https://your-function-app.azurewebsites.net/api/ProcessSimulationKPIs"
    # kpis = run_simulation_and_export(config, function_app_url=FUNCTION_APP_URL)
    
    print(f"\n✅ All {len(kpis)} KPIs ready for function app processing")
    print(f"📄 Data exported to: kpi_export_{kpis['simulation_id']}.json")
