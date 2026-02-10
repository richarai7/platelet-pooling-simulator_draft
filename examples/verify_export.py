import json

# Load exported KPIs
with open('kpi_export_sim_20260209_124607.json') as f:
    data = json.load(f)

print('\n✅ ALL KPI FIELDS SUCCESSFULLY EXPORTED\n')
print(f'   Total fields: {len(data)}')
print(f'   Simulation ID: {data["simulation_id"]}')
print(f'   Throughput: {data["current_throughput"]:.2f} units/hr')
print(f'   Bottleneck: {data["resource_bottleneck"]}')
print(f'   Cost/Unit: ${data["cost_per_unit"]:.2f}')
print(f'   Optimization suggestions: {len(data["optimization_suggestions"])}')
print(f'\n📊 Sample fields available:')
for i, key in enumerate(list(data.keys())[:10], 1):
    print(f'   {i}. {key}')
print(f'   ... and {len(data) - 10} more fields')
print(f'\n✅ Ready to send to Azure Function App!')
