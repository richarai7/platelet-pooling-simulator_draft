# UI → API → Azure Function → Digital Twins Integration

## Overview

The system now supports the complete flow from UI through API to Azure Digital Twins:

```
UI → API → Azure Function → Digital Twins
```

## How It Works

### 1. UI Sends Request to API
The UI (React) calls the API endpoint:
```typescript
POST /simulations/run
{
  "config": { ... },
  "run_name": "...",
  "simulation_name": "..."
}
```

### 2. API Runs Simulation
The API (`api/main.py`) executes the simulation using `SimulationEngine`.

### 3. API Prepares Telemetry
After simulation completes, the API prepares telemetry in the format expected by Azure Function:
```json
{
  "telemetry": [
    {
      "twin_id": "sim_20260215_123456",
      "properties": {
        "simulationStatus": "Completed",
        "totalFlowsCompleted": 20,
        "totalEvents": 40,
        ...
      }
    },
    {
      "twin_id": "device_id",
      "properties": {
        "status": "Idle",
        "totalProcessed": 1,
        "totalIdleTime": 100.5,
        ...
      }
    }
  ]
}
```

### 4. API Calls Azure Function
The API sends the telemetry to the Azure Function via HTTP POST:
```python
POST https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry?code=<key>
```

### 5. Azure Function Updates Digital Twins
The Azure Function receives the telemetry and updates the corresponding twins in Azure Digital Twins.

## Configuration

### Environment Variables

Set these environment variables to enable the integration:

```bash
# Enable Azure integration
export ENABLE_AZURE_INTEGRATION=true

# Azure Function endpoint
export AZURE_FUNCTION_ENDPOINT=https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry

# Azure Function key (optional, can also be passed in URL)
export AZURE_FUNCTION_KEY=your_function_key_here
```

### For Local Development

1. **Without Azure** (default):
   - Azure integration is disabled by default
   - Simulation runs normally
   - No Digital Twins updates

2. **With Azure**:
   ```bash
   cd api
   export ENABLE_AZURE_INTEGRATION=true
   export AZURE_FUNCTION_ENDPOINT=<your-endpoint>
   uvicorn main:app --reload
   ```

### For Production

Set environment variables in your deployment:

**Azure App Service**:
```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-rg \
  --settings \
    ENABLE_AZURE_INTEGRATION=true \
    AZURE_FUNCTION_ENDPOINT=<endpoint> \
    AZURE_FUNCTION_KEY=<key>
```

**Docker**:
```bash
docker run -e ENABLE_AZURE_INTEGRATION=true \
  -e AZURE_FUNCTION_ENDPOINT=<endpoint> \
  -e AZURE_FUNCTION_KEY=<key> \
  your-image
```

## Testing

### 1. Start the API Server
```bash
cd api
uvicorn main:app --reload
```

### 2. Run the Test Script
```bash
# Without Azure (tests API only)
python test_ui_api_azure_flow.py

# With Azure (tests complete flow)
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT=<your-endpoint>
python test_ui_api_azure_flow.py
```

### 3. Test from UI
1. Start the UI development server
2. Run a simulation
3. Check the API logs for Azure integration messages

## API Response

The API response now includes Azure integration status in metadata:

```json
{
  "results": {
    "summary": { ... },
    "device_states": [ ... ],
    "metadata": {
      "simulation_id": "sim_20260215_123456",
      "azure_twins_updated": 12,  // Number of twins updated
      "azure_error": null          // Or error message if failed
    }
  },
  "simulation_id": "sim_20260215_123456"
}
```

## Code Changes

### Modified Files

1. **api/main.py**:
   - Added `httpx` import for async HTTP requests
   - Added environment variable configuration
   - Added `prepare_telemetry_from_results()` function
   - Added `send_telemetry_to_azure_function()` function
   - Modified `/simulations/run` endpoint to call Azure Function

### New Files

1. **test_ui_api_azure_flow.py**: Test script for the complete flow
2. **UI_API_AZURE_INTEGRATION.md**: This documentation

## Architecture Diagram

```
┌─────────┐
│   UI    │ User clicks "Run Simulation"
└─────────┘
     │
     │ POST /simulations/run
     ▼
┌─────────┐
│   API   │ 1. Runs SimulationEngine
│(FastAPI)│ 2. Prepares telemetry
└─────────┘ 3. Calls Azure Function
     │
     │ POST with telemetry
     ▼
┌──────────────────┐
│ Azure Function   │ Updates Digital Twins
│ProcessSimulation │ Returns success/failure
└──────────────────┘
     │
     │ Update twins
     ▼
┌──────────────────┐
│ Digital Twins    │ Twins updated with:
│                  │ - Simulation status
│                  │ - Device states
│                  │ - Metrics
└──────────────────┘
```

## Error Handling

- If Azure integration is disabled, simulation runs normally
- If Azure Function call fails, error is logged but simulation succeeds
- Error details are included in response metadata
- Digital Twins update failures don't affect simulation results

## Monitoring

Check API logs for Azure integration messages:

```
INFO: Digital Twins updated: 12 twins
WARNING: Azure Function endpoint not configured
ERROR: Azure Function HTTP error: 500
```

## Next Steps

1. Deploy Azure Function (see `docs/AZURE_SETUP_GUIDE.md`)
2. Configure environment variables
3. Test with UI
4. Monitor logs for errors
5. Verify twins in Azure Digital Twins Explorer

## Troubleshooting

### "Azure integration is disabled"
- Set `ENABLE_AZURE_INTEGRATION=true`

### "Azure Function endpoint not configured"
- Set `AZURE_FUNCTION_ENDPOINT` environment variable

### "Azure Function HTTP error: 401"
- Check `AZURE_FUNCTION_KEY` is correct
- Or include key in endpoint URL: `?code=<key>`

### "Azure Function request timed out"
- Check Azure Function is running
- Increase timeout in `send_telemetry_to_azure_function()`

### No twins updated
- Check Azure Function logs in Azure Portal
- Verify DTDL models are uploaded
- Check Azure Digital Twins endpoint in Function configuration
