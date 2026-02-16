# Architecture Flow Analysis - UI to Azure Digital Twins

## Question
> "If I will run the simulator from UI, it will hit the API and then API will call the Azure func and would this update the properties of twins in digital twin? Is this the flow this code following right now?"

## Answer: **NO** - This flow is NOT currently implemented

---

## Current Architecture

### ❌ What DOES NOT Exist: UI → API → Azure Function → Digital Twins

The UI and API are **NOT** connected to Azure Digital Twins. Here's what actually happens:

```
┌────────┐
│   UI   │ ──────┐
└────────┘       │
                 │ POST /simulations/run
                 ▼
            ┌─────────┐
            │   API   │
            │(FastAPI)│
            └─────────┘
                 │
                 │ runs SimulationEngine
                 ▼
            ┌─────────────────┐
            │ Simulation Only │
            │  (No Azure)     │
            └─────────────────┘
                 │
                 │ returns results
                 ▼
            ┌────────┐
            │   UI   │
            └────────┘

Result: ❌ NO Digital Twins updated
```

### ✅ What DOES Exist: Direct Script → Azure Digital Twins

The ONLY way to update Digital Twins currently is by running `run_simulation_with_adt.py` directly:

```
┌──────────────────────────┐
│ run_simulation_with_adt.py│
└──────────────────────────┘
            │
            │ directly uses
            ▼
┌──────────────────────────┐
│DigitalTwinsClientWrapper │
└──────────────────────────┘
            │
            │ updates
            ▼
┌──────────────────────────┐
│  Azure Digital Twins     │
└──────────────────────────┘

Result: ✅ Digital Twins updated
```

---

## Code Evidence

### 1. API Does NOT Call Azure Function

**File**: `api/main.py` (lines 261-330)

```python
@app.post("/simulations/run", response_model=SimulationResultsResponse)
def run_simulation(request: SimulationRunRequest):
    """Run a simulation with the provided configuration"""
    try:
        # Initialize and run simulation engine
        engine = SimulationEngine(request.config)
        
        # Run simulation
        results = engine.run()
        
        # Return results
        return SimulationResultsResponse(
            results=results,
            json_export_path=json_export_path,
            simulation_id=sim_id
        )
```

**Analysis**: 
- ❌ No Azure Function calls
- ❌ No Digital Twins integration
- ❌ No telemetry streaming
- ✅ Only runs simulation and returns results

### 2. UI Calls API Only

**File**: `ui/src/api.ts` (lines 54-80)

```typescript
export async function runSimulation(
  config: SimulationConfig,
  runName?: string,
  simulationName?: string,
  exportToJson: boolean = true,
  exportDirectory?: string
): Promise<{ results: SimulationResults; simulationId?: string }> {
  const response = await fetchJSON<{ 
    results: SimulationResults; 
    json_export_path?: string;
    simulation_id?: string;
  }>(
    `${API_BASE_URL}/simulations/run`,
    {
      method: 'POST',
      body: JSON.stringify({ 
        config,
        run_name: runName,
        simulation_name: simulationName,
        export_to_json: exportToJson,
        export_directory: exportDirectory
      }),
    }
  );
  
  return {
    results: response.results,
    simulationId: response.simulation_id
  };
}
```

**Analysis**:
- ✅ UI calls API at `/simulations/run`
- ❌ No Azure integration in UI
- ❌ API response contains only simulation results

### 3. Azure Function Exists But Is Not Used

**File**: `azure_functions/ProcessSimulationTelemetry/__init__.py`

```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process incoming simulation telemetry and update Digital Twins
    """
    # This function CAN update Digital Twins
    # But it is NEVER called by the API
```

**Analysis**:
- ✅ Function exists and can update twins
- ❌ API does not call this function
- ❌ UI does not trigger this function

---

## Current Flows Comparison

### Flow 1: UI Simulation (Current - NO Azure)
```
1. User clicks "Run Simulation" in UI
2. UI sends POST to API /simulations/run
3. API runs SimulationEngine.run()
4. API returns results to UI
5. UI displays results

Azure Digital Twins: ❌ NOT UPDATED
```

### Flow 2: Direct Script (Current - WITH Azure)
```
1. User runs: python run_simulation_with_adt.py --config default_config.json
2. Script creates/updates device twins in Azure Digital Twins
3. Script runs simulation
4. Script updates twin properties with final states
5. Results printed to console

Azure Digital Twins: ✅ UPDATED
```

### Flow 3: Desired (NOT Implemented)
```
1. User clicks "Run Simulation" in UI
2. UI sends POST to API /simulations/run
3. API runs simulation
4. API calls Azure Function with telemetry
5. Azure Function updates Digital Twins
6. API returns results to UI

Azure Digital Twins: ❌ NOT IMPLEMENTED
```

---

## What Would Be Needed

To implement the desired flow (UI → API → Azure Function → Digital Twins), you would need:

### 1. Modify API to Call Azure Function

**Changes needed in `api/main.py`**:

```python
import httpx  # or requests

@app.post("/simulations/run", response_model=SimulationResultsResponse)
async def run_simulation(request: SimulationRunRequest):
    # Run simulation
    engine = SimulationEngine(request.config)
    results = engine.run()
    
    # NEW: Call Azure Function to update Digital Twins
    azure_function_url = os.getenv('AZURE_FUNCTION_ENDPOINT')
    if azure_function_url:
        telemetry = prepare_telemetry(results)  # Helper function needed
        async with httpx.AsyncClient() as client:
            await client.post(azure_function_url, json=telemetry)
    
    return SimulationResultsResponse(results=results, ...)
```

### 2. Add Azure Integration to API

- Add environment variables for Azure Function endpoint
- Add logic to prepare telemetry from simulation results
- Add error handling for Azure calls
- Add option to enable/disable Azure integration

### 3. OR: Direct Azure Digital Twins Integration in API

Instead of calling Azure Function, could integrate directly:

```python
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper

@app.post("/simulations/run")
async def run_simulation(request: SimulationRunRequest):
    # Run simulation
    results = engine.run()
    
    # Update Digital Twins directly
    adt_endpoint = os.getenv('AZURE_DIGITAL_TWINS_ENDPOINT')
    if adt_endpoint:
        dt_client = DigitalTwinsClientWrapper(adt_endpoint)
        await update_twins(dt_client, results)  # Helper function needed
    
    return results
```

---

## Summary

| Component | Current Status | Updates Digital Twins? |
|-----------|----------------|------------------------|
| UI | ✅ Exists | ❌ No |
| API | ✅ Exists | ❌ No |
| Azure Function | ✅ Exists | ✅ Yes (when called) |
| Direct Script | ✅ Exists | ✅ Yes |

**Current Answer**: 
- ❌ UI does NOT update Digital Twins
- ❌ API does NOT call Azure Function
- ❌ The flow UI → API → Azure Function → Digital Twins is NOT implemented

**Working Solution**: 
- ✅ Use `run_simulation_with_adt.py` script directly to update Digital Twins

---

## Files to Check

1. **API Implementation**: `api/main.py` (lines 261-330)
2. **UI API Client**: `ui/src/api.ts` (lines 54-80)
3. **Azure Function**: `azure_functions/ProcessSimulationTelemetry/__init__.py`
4. **Working Script**: `run_simulation_with_adt.py`
5. **Azure Integration**: `azure_integration/digital_twins_client.py`

---

**Created**: 2026-02-15  
**Status**: Documentation of current architecture
