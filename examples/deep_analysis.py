"""
DEEP ANALYSIS - Find the REAL constraint
"""
import requests
import json

print("="*70)
print("DEEP FLOW ANALYSIS")
print("="*70)

# Get template
response = requests.get("http://localhost:8000/templates/platelet-pooling")
config = response.json()

print("\n1. DEVICE CAPACITIES:")
print("-"*70)
for device in sorted(config['devices'], key=lambda d: d['capacity']):
    print(f"{device['id']:<30} capacity={device['capacity']}")

print("\n2. FLOW DEPENDENCIES:")
print("-"*70)
for flow in config['flows']:
    deps = flow.get('dependencies', [])
    deps_str = ', '.join(deps) if deps else 'NONE (starts immediately)'
    print(f"\n{flow['id']}:")
    print(f"  Device: {flow['device_id']}")
    print(f"  Process Time: {flow['process_time_seconds']}s")
    print(f"  Depends On: {deps_str}")

print("\n3. CRITICAL PATH ANALYSIS:")
print("-"*70)

# Build dependency graph
flow_dict = {f['id']: f for f in config['flows']}

def get_critical_path(flow_id, visited=None):
    if visited is None:
        visited = set()
    
    if flow_id in visited:
        return 0
    
    visited.add(flow_id)
    flow = flow_dict.get(flow_id)
    if not flow:
        return 0
    
    process_time = flow['process_time_seconds']
    dependencies = flow.get('dependencies', [])
    
    if not dependencies:
        return process_time
    
    max_dep_time = max((get_critical_path(dep, visited.copy()) for dep in dependencies), default=0)
    return max_dep_time + process_time

print("\nLongest paths (critical path candidates):")
path_times = []
for flow in config['flows']:
    total_time = get_critical_path(flow['id'])
    path_times.append((flow['id'], total_time))

for flow_id, time in sorted(path_times, key=lambda x: -x[1])[:5]:
    print(f"  {flow_id}: {time}s ({time/60:.1f} min)")

print("\n4. BATCH STRUCTURE:")
print("-"*70)
batches = {}
for flow in config['flows']:
    batch = flow.get('batch_id', 'unknown')
    if batch not in batches:
        batches[batch] = []
    batches[batch].append(flow['id'])

print(f"\nNumber of batches: {len(batches)}")
for batch_id, flows in sorted(batches.items()):
    print(f"\n{batch_id}: {len(flows)} flows")
    for flow_id in flows:
        flow = flow_dict[flow_id]
        print(f"  • {flow_id} on {flow['device_id']}")

print("\n5. PARALLEL vs SEQUENTIAL:")
print("-"*70)

# Check if flows can run in parallel
def count_parallel_flows():
    # Group by batch and device
    device_usage = {}
    for flow in config['flows']:
        device = flow['device_id']
        batch = flow.get('batch_id')
        key = f"{batch}-{device}"
        if key not in device_usage:
            device_usage[key] = []
        device_usage[key].append(flow['id'])
    
    print("\nFlows competing for same device in same batch:")
    for key, flows in device_usage.items():
        if len(flows) > 1:
            print(f"  {key}: {len(flows)} flows → {', '.join(flows)}")

count_parallel_flows()

print("\n" + "="*70)
print("HYPOTHESIS:")
print("="*70)
print("\nIf completion time is ALWAYS 3387s regardless of capacity changes,")
print("then the constraint is NOT device capacity, but:")
print("  1. Sequential dependencies (critical path)")
print("  2. Batch processing (all batches must complete)")
print("  3. Configuration has flows that CANNOT overlap")
print("\nThe 3387s might be the sum of all sequential steps!")
print("="*70)
