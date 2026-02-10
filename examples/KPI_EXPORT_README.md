# Exporting Simulation KPIs to Function App

## Overview

This system calculates **44 comprehensive KPIs** from your platelet pooling simulation and exports them to Azure Function Apps or any REST API endpoint for further processing.

## 📊 All Exported Fields

### Production Metrics
- `total_units_created` - Total platelet units successfully created
- `quality_pass_rate` - Percentage of units passing quality tests
- `failed_units_count` - Number of units that failed quality
- `average_cycle_time` - Average time from start to completion (seconds)
- `current_throughput` - Units created per hour
- `units_processed` - Total units processed (including failed)
- `product_release_volume` - Units released for use

### Utilization Metrics
- `uniting_station_utilization` - % time uniting stations active
- `testing_lab_utilization` - % time testing labs active
- `capacity_utilization_per_device` - % of max capacity used per device
- `idle_time_percentage` - % time each resource is idle
- `active_units_in_process` - Units being processed at simulation end

### Cost Analysis
- `total_operating_cost` - Total cost for simulation period
- `cost_per_unit` - Operating cost per unit
- `waste_rate` - % of production wasted
- `waste_cost` - Financial impact of wasted units

### Queue & Wait Metrics
- `units_in_queue` - Units currently waiting
- `avg_wait_time_per_unit` - Average time units wait in queue
- `max_queue_length` - Maximum queue size reached
- `time_to_first_unit` - Time until first unit completed

### Performance Metrics
- `peak_throughput` - Maximum throughput achieved (units/hour)
- `simulation_time_elapsed` - Simulated time elapsed (seconds)
- `input_supply_rate` - Platelet units arriving per hour

### Bottleneck Analysis
- `resource_bottleneck` - Identified bottleneck resource
- `optimization_suggestions` - Recommended process changes (array)

### Quality & Expiry
- `expired_units` - Units that aged out
- `test_results_breakdown` - Detailed quality test results
  - `passed` (count)
  - `failed` (count)
  - `reasons` (breakdown)

### Staff Metrics
- `staff_count` - Number of staff/technicians
- `staff_utilization` - % time staff actively working

### Comparison & Variance
- `comparison_to_baseline` - vs baseline throughput
  - `current` (value)
  - `baseline` (value)
  - `difference_pct` (%)
- `supply_variation` - Fluctuation in arrival rate
- `constraint_violations` - Count of limit breaches

### Forecasting
- `demand_forecast` - Projected future demand
  - `current_rate`
  - `projected_demand`
  - `variance`

### Configuration
- `run_name` - Name of this run
- `simulation_name` - Name of simulation
- `processing_station_count` - Number of uniting stations
- `testing_station_count` - Number of testing labs
- `scenario_parameters` - Full configuration object
  - `duration`
  - `random_seed`
  - `execution_mode`
  - `device_count`
  - `flow_count`

### Tracking
- `unit_transfer_tracking` - Log of units moving between devices (array)
  - `unit_id`
  - `from_device`
  - `to_device`
  - `transfer_time`
  - `completion_time`

### Visualization Data
- `3d_visualization` - Data for 3D visualization
  - `devices` (array with positions, types, utilization)
  - `flows` (array with from/to connections)
- `scenario_comparison` - Multi-scenario comparison KPIs

### Device Health
- `device_health` - Health status per device (Healthy/Warning/Critical)

### Metadata
- `export_timestamp` - When KPIs were calculated
- `simulation_id` - Unique simulation identifier

---

## 🚀 Quick Start

### 1. Basic Usage (Export to File)

```python
from export_to_function_app import run_simulation_and_export

# Your simulation config
config = {
    "simulation": {
        "duration": 28800,  # 8 hours
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    # ... device and flow configuration
}

# Run and export
kpis = run_simulation_and_export(config, export_to_file=True)

# KPIs saved to: kpi_export_<simulation_id>.json
```

### 2. Send to Azure Function App

```python
# Your Azure Function App endpoint
FUNCTION_APP_URL = "https://your-app.azurewebsites.net/api/ProcessKPIs"

kpis = run_simulation_and_export(
    config,
    function_app_url=FUNCTION_APP_URL,
    export_to_file=True  # Also save locally
)
```

### 3. Custom Processing

```python
from simulation_engine import SimulationEngine
from simulation_engine.kpi_calculator import KPICalculator

# Run simulation
engine = SimulationEngine(config)
result = engine.run()

# Calculate KPIs
calculator = KPICalculator(result, config)
all_kpis = calculator.calculate_all_kpis()

# Access specific KPIs
print(f"Throughput: {all_kpis['current_throughput']}")
print(f"Bottleneck: {all_kpis['resource_bottleneck']}")
print(f"Cost/Unit: ${all_kpis['cost_per_unit']:.2f}")
```

---

## 📝 Configuration Parameters

Add these to your config for cost analysis:

```python
config = {
    # ... existing simulation config
    
    # Cost parameters
    "labor_cost": 1000,          # Labor cost for simulation period
    "material_cost": 50,          # Material cost per unit
    "overhead_cost": 500,         # Fixed overhead
    "cost_per_unit": 75,          # Standard cost per unit
    
    # Baseline for comparison
    "baseline_throughput": 5.0,   # Units/hour baseline
    
    # Metadata
    "run_name": "Production_Scenario_A",
    "scenario_name": "Platelet Pooling - High Volume",
    
    # Staff (optional)
    "staff_count": 5,
    "staff_utilization": 0.85
}
```

---

## 🔌 Azure Function App Integration

### HTTP POST Request Format

```json
{
  "total_units_created": 150,
  "quality_pass_rate": 98.5,
  "current_throughput": 18.75,
  "average_cycle_time": 1200.5,
  "capacity_utilization_per_device": {
    "centrifuge": 75.3,
    "separator": 82.1,
    "quality": 95.8
  },
  "total_operating_cost": 5250.00,
  "cost_per_unit": 35.00,
  "resource_bottleneck": "quality",
  "optimization_suggestions": [
    "Increase capacity at quality",
    "Reduce waste rate (currently 1.5%)"
  ],
  "device_health": {
    "centrifuge": "Healthy",
    "separator": "Healthy",
    "quality": "Warning"
  },
  "export_timestamp": "2026-02-09T12:46:07",
  "simulation_id": "sim_20260209_124607"
}
```

### Example Azure Function (Node.js)

```javascript
module.exports = async function (context, req) {
    const kpis = req.body;
    
    // Validate KPIs
    if (!kpis.simulation_id || !kpis.total_units_created) {
        context.res = {
            status: 400,
            body: "Invalid KPI data"
        };
        return;
    }
    
    // Process KPIs (store in database, trigger alerts, etc.)
    context.log(`Processing simulation: ${kpis.simulation_id}`);
    context.log(`Throughput: ${kpis.current_throughput} units/hour`);
    context.log(`Bottleneck: ${kpis.resource_bottleneck}`);
    
    // Example: Trigger alert if bottleneck detected
    if (kpis.resource_bottleneck !== "None identified") {
        await triggerBottleneckAlert(kpis);
    }
    
    // Example: Store in Cosmos DB
    await storeInDatabase(kpis);
    
    context.res = {
        status: 200,
        body: {
            success: true,
            simulation_id: kpis.simulation_id,
            processed_at: new Date().toISOString()
        }
    };
};
```

### Example Azure Function (Python)

```python
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        kpis = req.get_json()
        
        # Validate
        if 'simulation_id' not in kpis:
            return func.HttpResponse(
                "Invalid KPI data",
                status_code=400
            )
        
        # Process KPIs
        simulation_id = kpis['simulation_id']
        throughput = kpis['current_throughput']
        bottleneck = kpis['resource_bottleneck']
        
        # Store in database, trigger workflows, etc.
        # ... your processing logic here
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'simulation_id': simulation_id,
                'message': f'Processed {kpis["total_units_created"]} units'
            }),
            status_code=200
        )
    
    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
```

---

## 📤 Output Format

### JSON File Structure

```json
{
  "total_units_created": 150,
  "quality_pass_rate": 98.5,
  "failed_units_count": 2,
  "average_cycle_time": 1205.3,
  "current_throughput": 18.75,
  
  "capacity_utilization_per_device": {
    "centrifuge": 75.3,
    "separator": 82.1,
    "quality": 95.8
  },
  
  "total_operating_cost": 5250.00,
  "cost_per_unit": 35.00,
  "waste_rate": 1.5,
  "waste_cost": 150.00,
  
  "resource_bottleneck": "quality",
  "optimization_suggestions": [
    "Increase capacity at quality",
    "Reduce waste rate (currently 1.5%)"
  ],
  
  "unit_transfer_tracking": [
    {
      "unit_id": "batch1_centrifuge",
      "from_device": "centrifuge",
      "to_device": "separator",
      "transfer_time": 0.0,
      "completion_time": 380.5
    }
  ],
  
  "device_health": {
    "centrifuge": "Healthy",
    "separator": "Healthy",
    "quality": "Warning"
  },
  
  "export_timestamp": "2026-02-09T12:46:07.123456",
  "simulation_id": "sim_20260209_124607"
}
```

---

## 🎯 Common Use Cases

### 1. Real-time Monitoring Dashboard

```python
# Run simulation every hour, send to dashboard API
import schedule

def monitor_production():
    kpis = run_simulation_and_export(
        config,
        function_app_url="https://your-dashboard-api.com/update"
    )
    
    # Dashboard automatically updates with latest KPIs

schedule.every().hour.do(monitor_production)
```

### 2. What-If Scenario Comparison

```python
scenarios = [
    {"name": "Baseline", "quality_capacity": 1},
    {"name": "+1 Quality", "quality_capacity": 2},
    {"name": "+2 Quality", "quality_capacity": 3}
]

results = []
for scenario in scenarios:
    config['devices'][2]['capacity'] = scenario['quality_capacity']
    kpis = run_simulation_and_export(config, export_to_file=False)
    results.append({
        'scenario': scenario['name'],
        'throughput': kpis['current_throughput'],
        'cost': kpis['cost_per_unit']
    })

# Send comparison to function app
requests.post(FUNCTION_APP_URL + "/compare", json=results)
```

### 3. Automated Optimization

```python
# Run simulation, get suggestions, implement best one
kpis = run_simulation_and_export(config)

if kpis['optimization_suggestions']:
    best_suggestion = kpis['optimization_suggestions'][0]
    
    # Send to decision system
    requests.post(
        "https://optimization-api.com/apply",
        json={'suggestion': best_suggestion, 'kpis': kpis}
    )
```

---

## 🔧 Customization

### Add Custom KPIs

Edit `src/simulation_engine/kpi_calculator.py`:

```python
def _your_custom_kpi(self) -> float:
    """Calculate your custom metric."""
    # Your calculation logic
    return calculated_value

def calculate_all_kpis(self):
    kpis = {
        # ... existing KPIs
        "your_custom_kpi": self._your_custom_kpi(),
    }
    return kpis
```

---

## ✅ Testing

Run the test script:

```bash
python export_to_function_app.py
```

Expected output:
- ✓ Simulation complete
- ✓ 44 KPIs calculated
- ✓ Exported to JSON file
- ✓ (Optional) Sent to function app

---

## 📚 Next Steps

1. **Deploy Azure Function** - Set up your endpoint to receive KPIs
2. **Configure Database** - Store KPI history for trend analysis
3. **Build Dashboard** - Visualize KPIs in real-time
4. **Set Alerts** - Notify when bottlenecks or issues detected
5. **Automate** - Schedule regular simulations for continuous monitoring

Need help integrating with your specific function app? Let me know!
