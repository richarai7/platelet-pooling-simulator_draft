"""
WEB UI FOR PLATELET POOLING SIMULATOR
No-code interface for Operations Managers to run what-if scenarios
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import sys
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator

app = Flask(__name__)

# Store simulation results
simulation_history = []


def create_config(centrifuge=2, separator=2, quality=1, batches=5):
    """Create simulation configuration from UI parameters."""
    
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
        "run_name": f"UI_Run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "scenario_name": f"C{centrifuge}_S{separator}_Q{quality}_B{batches}",
        "labor_cost": 1000,
        "material_cost": 50,
        "overhead_cost": 500,
        "cost_per_unit": 75,
        "baseline_throughput": 5.0,
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": centrifuge,
             "recovery_time_range": (1, 2)},
            {"id": "separator", "type": "machine", "capacity": separator,
             "recovery_time_range": (1, 2)},
            {"id": "quality", "type": "machine", "capacity": quality,
             "recovery_time_range": (1, 2)}
        ],
        "flows": []
    }
    
    # Create flows for each batch
    for batch in range(1, batches + 1):
        config["flows"].extend([
            {"flow_id": f"batch{batch}_centrifuge",
             "from_device": "centrifuge", "to_device": "separator",
             "process_time_range": (300, 480), "priority": 1, "dependencies": None},
            {"flow_id": f"batch{batch}_separator",
             "from_device": "separator", "to_device": "quality",
             "process_time_range": (600, 900), "priority": 1,
             "dependencies": [f"batch{batch}_centrifuge"]},
            {"flow_id": f"batch{batch}_quality",
             "from_device": "quality", "to_device": "quality",
             "process_time_range": (180, 300), "priority": 1,
             "dependencies": [f"batch{batch}_separator"]}
        ])
    
    return config


@app.route('/')
def index():
    """Main UI page."""
    return render_template('index.html')


@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    """Run simulation with user-specified parameters."""
    
    try:
        data = request.json
        
        # Get parameters from UI
        centrifuge = int(data.get('centrifuge', 2))
        separator = int(data.get('separator', 2))
        quality = int(data.get('quality', 1))
        batches = int(data.get('batches', 5))
        
        # Create config
        config = create_config(centrifuge, separator, quality, batches)
        
        # Run simulation
        engine = SimulationEngine(config)
        result = engine.run()
        
        # Calculate KPIs
        calculator = KPICalculator(result, config)
        kpis = calculator.calculate_all_kpis()
        
        # Store in history
        simulation_result = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'centrifuge': centrifuge,
                'separator': separator,
                'quality': quality,
                'batches': batches
            },
            'kpis': {
                'throughput': round(kpis['current_throughput'], 2),
                'cycle_time': round(kpis['average_cycle_time'], 1),
                'completion_time': round(kpis['simulation_time_elapsed'] / 60, 1),
                'units_created': kpis['total_units_created'],
                'bottleneck': kpis['resource_bottleneck'],
                'cost_per_unit': round(kpis['cost_per_unit'], 2),
                'utilization': {
                    'centrifuge': round(kpis['capacity_utilization_per_device'].get('centrifuge', 0), 1),
                    'separator': round(kpis['capacity_utilization_per_device'].get('separator', 0), 1),
                    'quality': round(kpis['capacity_utilization_per_device'].get('quality', 0), 1)
                },
                'suggestions': kpis['optimization_suggestions'][:3]
            }
        }
        
        simulation_history.append(simulation_result)
        
        return jsonify({
            'success': True,
            'result': simulation_result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare_scenarios', methods=['POST'])
def compare_scenarios():
    """Compare multiple what-if scenarios."""
    
    try:
        data = request.json
        scenarios = data.get('scenarios', [])
        
        results = []
        
        for scenario in scenarios:
            # Run each scenario
            config = create_config(
                centrifuge=scenario.get('centrifuge', 2),
                separator=scenario.get('separator', 2),
                quality=scenario.get('quality', 1),
                batches=scenario.get('batches', 5)
            )
            
            engine = SimulationEngine(config)
            result = engine.run()
            
            calculator = KPICalculator(result, config)
            kpis = calculator.calculate_all_kpis()
            
            results.append({
                'name': scenario.get('name', 'Scenario'),
                'config': scenario,
                'throughput': round(kpis['current_throughput'], 2),
                'completion_time': round(kpis['simulation_time_elapsed'] / 60, 1),
                'cost_per_unit': round(kpis['cost_per_unit'], 2),
                'bottleneck': kpis['resource_bottleneck']
            })
        
        return jsonify({
            'success': True,
            'comparison': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history')
def get_history():
    """Get simulation history."""
    return jsonify({
        'success': True,
        'history': simulation_history[-10:]  # Last 10 runs
    })


@app.route('/api/export/<int:index>')
def export_result(index):
    """Export simulation result as JSON."""
    
    if index >= len(simulation_history):
        return jsonify({'success': False, 'error': 'Invalid index'}), 404
    
    result = simulation_history[index]
    filename = f"simulation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    return send_file(filename, as_attachment=True)


@app.route('/api/quick_test/<test_type>')
def quick_test(test_type):
    """Run predefined test scenarios."""
    
    test_configs = {
        'baseline': {'centrifuge': 2, 'separator': 2, 'quality': 1, 'batches': 5},
        'add_centrifuge': {'centrifuge': 4, 'separator': 2, 'quality': 1, 'batches': 5},
        'add_quality': {'centrifuge': 2, 'separator': 2, 'quality': 2, 'batches': 5},
        'high_volume': {'centrifuge': 2, 'separator': 2, 'quality': 1, 'batches': 10}
    }
    
    if test_type not in test_configs:
        return jsonify({'success': False, 'error': 'Unknown test type'}), 400
    
    config_params = test_configs[test_type]
    config = create_config(**config_params)
    
    engine = SimulationEngine(config)
    result = engine.run()
    
    calculator = KPICalculator(result, config)
    kpis = calculator.calculate_all_kpis()
    
    return jsonify({
        'success': True,
        'test_type': test_type,
        'result': {
            'throughput': round(kpis['current_throughput'], 2),
            'completion_time': round(kpis['simulation_time_elapsed'] / 60, 1),
            'bottleneck': kpis['resource_bottleneck'],
            'cost_per_unit': round(kpis['cost_per_unit'], 2),
            'suggestions': kpis['optimization_suggestions'][:3]
        }
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🎯 PLATELET POOLING SIMULATOR - WEB UI")
    print("="*70)
    print("\n  Starting server...")
    print("  Open your browser to: http://localhost:5000")
    print("\n  Features:")
    print("  • Adjust device capacities with sliders")
    print("  • Run what-if scenarios")
    print("  • Compare multiple scenarios")
    print("  • See bottleneck analysis")
    print("  • Export results\n")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000)
