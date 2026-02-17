# Quick Setup Guide: Verifying Azure Digital Twins Integration

This guide helps you verify that Azure Digital Twins integration is working properly after the twin properties fix.

## Prerequisites

1. Azure Digital Twins instance created
2. Device twins created (using `azure_integration/scripts/create_linear_flow_twins.py`)
3. Azure credentials configured (`az login`)

## Step 1: Configure Environment

Create or update your `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Enable Azure integration
ENABLE_AZURE_INTEGRATION=true

# Required: Your Azure Digital Twins endpoint
AZURE_DIGITAL_TWINS_ENDPOINT=https://your-instance.api.eus.digitaltwins.azure.net

# Optional: If using Azure Function App (recommended for production)
AZURE_FUNCTION_ENDPOINT=https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry
AZURE_FUNCTION_KEY=your-function-key-here
```

Load environment:
```bash
source load_env.sh
```

## Step 2: Verify Azure Integration Status

```bash
./check_azure_integration.sh
```

Expected output:
```
========================================
Azure Integration Status
========================================
✅ Azure integration is ENABLED
✅ AZURE_DIGITAL_TWINS_ENDPOINT is configured
   Endpoint: https://your-instance.api.eus.digitaltwins.azure.net

Optional Settings:
⚠️  AZURE_FUNCTION_ENDPOINT is not set (will use direct ADT connection)
⚠️  AZURE_FUNCTION_KEY is not set
```

## Step 3: Check Existing Twins

Verify that device twins exist in your Azure Digital Twins instance:

```bash
# List all device twins
az dt twin query \
  --dt-name <your-instance-name> \
  --query-command "SELECT * FROM DIGITALTWINS WHERE IS_OF_MODEL('dtmi:platelet:Device;1')"
```

If no twins exist, create them:

```bash
python azure_integration/scripts/create_linear_flow_twins.py \
  --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT
```

## Step 4: Start the API Server

```bash
# With Azure integration enabled
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 5: Test API Endpoints

### Check API is Running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Simulation API",
  "version": "0.1.0",
  "azure_integration_enabled": true,
  "endpoints": {
    "scenarios": "/scenarios",
    "simulation": "/simulations/run",
    "templates": "/templates/platelet-pooling",
    "azure_diagnostics": "/azure/diagnostics"
  }
}
```

### Check Azure Diagnostics

```bash
curl http://localhost:8000/azure/diagnostics
```

Expected response:
```json
{
  "azure_integration_enabled": true,
  "azure_function_endpoint_configured": false,
  "azure_function_key_configured": false,
  "device_id_mapping": {
    "buffy_coat_packs": "buffy_coat_packs",
    "platelet_washing": "platelet_washing",
    ...
  }
}
```

## Step 6: Run a Test Simulation

### Option A: Use Template Configuration

```bash
curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "simulation": {
        "duration": 3600,
        "random_seed": 42,
        "execution_mode": "accelerated"
      },
      "devices": [
        {
          "id": "buffy_coat_packs",
          "type": "material",
          "capacity": 5,
          "initial_state": "Idle",
          "recovery_time_range": [60, 120],
          "metadata": {
            "location": "Lab A - Station 1"
          }
        }
      ],
      "flows": [],
      "output_options": {
        "include_history": true,
        "include_events": true
      }
    },
    "export_to_json": false
  }'
```

### Option B: Use Existing Config File

```bash
curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d @<(cat platelet_pooling_config.json | jq '{config: .}')
```

### Check Response

Look for in the response:
```json
{
  "results": {
    "metadata": {
      "azure_twins_updated": 11,
      ...
    }
  }
}
```

The `azure_twins_updated` field should show the number of twins successfully updated (10 devices + 1 simulation twin).

## Step 7: Verify Twin Properties in Azure

### Using Azure Portal

1. Go to https://portal.azure.com
2. Navigate to your Azure Digital Twins instance
3. Open "Azure Digital Twins Explorer"
4. Select a device twin (e.g., `buffy_coat_packs`)
5. View "Properties" tab

Verify all properties are present:
- ✅ deviceId
- ✅ deviceType
- ✅ capacity
- ✅ status
- ✅ inUse
- ✅ utilizationRate
- ✅ queueLength
- ✅ totalProcessed
- ✅ totalIdleTime
- ✅ totalProcessingTime
- ✅ totalBlockedTime
- ✅ location
- ✅ lastUpdateTime

### Using Azure CLI

```bash
# Query a specific device twin
az dt twin show \
  --dt-name <your-instance-name> \
  --twin-id buffy_coat_packs \
  --query "{deviceId: deviceId, deviceType: deviceType, capacity: capacity, status: status, utilizationRate: utilizationRate, location: location, lastUpdateTime: lastUpdateTime}"
```

## Step 8: Run Multiple Simulations

Run 2-3 simulations and verify that properties update each time:

```bash
# Run simulation 1
curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d @<(cat platelet_pooling_config.json | jq '{config: .}')

# Wait a moment, then run simulation 2
sleep 5

curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d @<(cat platelet_pooling_config.json | jq '{config: .}')
```

Check in Azure Digital Twins Explorer:
- `lastUpdateTime` should be more recent after each simulation
- KPI values should be different between simulations (due to random seed or different configs)

## Common Issues & Solutions

### Issue 1: "azure_twins_updated": 0 or missing

**Cause**: Azure integration may not be properly configured or Azure Function/ADT connection failed.

**Solution**:
1. Check API logs: `tail -f logs/api.log` (if logging to file) or check console output
2. Look for error messages about Azure connection
3. Verify Azure credentials: `az account show`
4. Test direct ADT connection:
   ```bash
   python -c "
   from azure.identity import DefaultAzureCredential
   from azure.digitaltwins.core import DigitalTwinsClient
   endpoint = 'https://your-instance.api.eus.digitaltwins.azure.net'
   client = DigitalTwinsClient(endpoint, DefaultAzureCredential())
   twin = client.get_digital_twin('buffy_coat_packs')
   print(f'Successfully connected! Twin: {twin}')
   "
   ```

### Issue 2: Some properties not showing in Azure Digital Twins

**Cause**: Properties may not be defined in the DTDL model.

**Solution**:
1. Check DTDL model: `cat azure_integration/dtdl_models/Device.json`
2. Verify model is uploaded to Azure:
   ```bash
   az dt model show \
     --dt-name <your-instance-name> \
     --dtmi "dtmi:platelet:Device;1"
   ```
3. If model needs updating:
   ```bash
   az dt model update \
     --dt-name <your-instance-name> \
     --models azure_integration/dtdl_models/Device.json
   ```

### Issue 3: Properties showing old/stale values

**Cause**: Twins may not have been updated, or you're looking at cached data.

**Solution**:
1. Refresh Azure Digital Twins Explorer
2. Check `lastUpdateTime` property to see when twin was last updated
3. Run a new simulation and verify `lastUpdateTime` changes
4. Check API response for `azure_twins_updated` count

### Issue 4: Azure Function not receiving telemetry

**Cause**: Function endpoint or key may be incorrect, or function may not be running.

**Solution**:
1. Check function logs:
   ```bash
   az webapp log tail \
     --name <your-function-app-name> \
     --resource-group <your-resource-group>
   ```
2. Test function directly:
   ```bash
   curl -X POST https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry?code=<function-key> \
     -H "Content-Type: application/json" \
     -d '{
       "telemetry": [{
         "twin_id": "test_device",
         "properties": {"testProperty": "testValue"}
       }]
     }'
   ```
3. If function fails, use direct ADT connection by removing `AZURE_FUNCTION_ENDPOINT` from `.env`

## Success Checklist

- [ ] Azure integration status shows all green checkmarks
- [ ] API returns `azure_twins_updated` > 0 after simulation
- [ ] All device twins show updated properties in Azure Digital Twins Explorer
- [ ] `lastUpdateTime` updates with each simulation
- [ ] Property values (utilizationRate, totalProcessed, etc.) reflect simulation results
- [ ] No errors in API logs
- [ ] No errors in Azure Function logs (if using Function App)

## Next Steps

Once verification is complete:

1. **Configure 3D Visualization**: See `docs/FIX_BLOB_STORAGE_403.md` for setting up Azure 3D Scenes Studio
2. **Production Deployment**: See `deploy_azure.sh` for deploying to production
3. **Monitor Performance**: Set up Application Insights for monitoring Azure Function performance
4. **Scale Testing**: Test with larger simulations and multiple concurrent runs

## Getting Help

If you encounter issues:

1. Check logs: API server console output and Azure Function logs
2. Review documentation:
   - `docs/ADT_TWIN_PROPERTIES_FIX.md` - Details on property updates
   - `docs/FUNCTION_APP_PERMISSIONS.md` - Azure Function permissions
   - `LINEAR_FLOW_SETUP.md` - Complete Azure setup guide
3. Verify Azure resources are properly configured:
   - Azure Digital Twins instance is running
   - DTDL models are uploaded
   - Twins are created
   - Permissions are set correctly

## Related Files

- `.env.example` - Environment variable template
- `check_azure_integration.sh` - Azure integration status checker
- `platelet_pooling_config.json` - Sample simulation configuration
- `azure_integration/scripts/create_linear_flow_twins.py` - Twin creation script
- `docs/ADT_TWIN_PROPERTIES_FIX.md` - Technical details on the fix
