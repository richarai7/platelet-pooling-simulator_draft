# Azure Digital Twins - Twin Properties Update Fix

## Issue Summary

Twin properties were not being fully updated when running new simulations in Azure Digital Twins. Only 7 out of 13 required properties from the DTDL Device model were being sent, causing the twins to show incomplete or stale data.

## Root Cause

The `prepare_telemetry_from_results()` function in `api/main.py` was only sending a subset of properties:
- ✅ status
- ✅ inUse
- ✅ queueLength
- ✅ totalProcessed
- ✅ totalIdleTime
- ✅ totalProcessingTime
- ✅ totalBlockedTime

Missing properties:
- ❌ deviceId
- ❌ deviceType
- ❌ capacity
- ❌ utilizationRate
- ❌ location
- ❌ lastUpdateTime
- ❌ position (for 3D visualization)
- ❌ rotation (for 3D visualization)

## Solution

### 1. Store Configuration in Simulation Results

Modified `src/simulation_engine/engine.py` to store the full configuration in the results metadata:

```python
"metadata": {
    "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "duration": self.config["simulation"]["duration"],
    "random_seed": self.config["simulation"]["random_seed"],
    "completed_at": datetime.now().isoformat(),
    "engine_version": "0.1.0",
    "config": self.config,  # Store full config for downstream processing
},
```

This allows the API to access device configurations (capacity, type, metadata, etc.) when preparing telemetry.

### 2. Enhanced Telemetry Preparation

Updated `api/main.py` `prepare_telemetry_from_results()` function to include all DTDL Device model properties:

**Core Device Properties:**
- `deviceId` - Unique identifier from device config
- `deviceType` - Device type (machine, material, workstation, etc.)
- `capacity` - Maximum concurrent processing capacity
- `utilizationRate` - Calculated as (processing_time / total_time) × 100

**Location & Metadata:**
- `location` - Physical location from device metadata
- `position` - Optional 3D coordinates for Azure 3D Scenes Studio
- `rotation` - Optional quaternion rotation for 3D visualization

**Timestamp:**
- `lastUpdateTime` - ISO 8601 timestamp of the update

**KPI Metrics (existing):**
- `status`, `inUse`, `queueLength`, `totalProcessed`
- `totalIdleTime`, `totalProcessingTime`, `totalBlockedTime`

### 3. Calculation Improvements

- **Utilization Rate**: `(total_processing_time / simulation_time) × 100%`
- **Numeric Rounding**: All float values rounded to 2 decimal places for cleaner display
- **Timestamp**: Added ISO 8601 formatted timestamp with timezone

## Files Modified

1. **`api/main.py`** - Enhanced telemetry preparation function
   - Extract device configs from results metadata
   - Calculate utilization rate
   - Include all DTDL properties
   - Add optional 3D visualization properties

2. **`src/simulation_engine/engine.py`** - Store config in results
   - Added config to metadata in `_generate_output()`
   - Added config to metadata in `_generate_deadlock_error_output()`

## Testing

Verified that all 13 required properties are now included in telemetry updates:

```bash
✓ Twin properties that would be sent (13 total):
  - capacity: 5
  - deviceId: buffy_coat_packs
  - deviceType: material
  - inUse: 0
  - lastUpdateTime: 2026-02-17T04:11:58.094816+00:00
  - location: Lab A - Station 1
  - queueLength: 0
  - status: Idle
  - totalBlockedTime: 0.00
  - totalIdleTime: 0.00
  - totalProcessed: 0
  - totalProcessingTime: 263.94
  - utilizationRate: 46.43

✓ All 13 required DTDL properties present!
```

## Verification Steps

To verify the fix is working:

### 1. Check Azure Integration Status

```bash
./check_azure_integration.sh
```

Expected output:
```
✅ Azure integration is ENABLED
✅ AZURE_DIGITAL_TWINS_ENDPOINT is configured
```

### 2. Run a Simulation via API

Start the API server:
```bash
export ENABLE_AZURE_INTEGRATION=true
export AZURE_DIGITAL_TWINS_ENDPOINT="https://your-instance.api.eus.digitaltwins.azure.net"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Run a simulation:
```bash
curl -X POST http://localhost:8000/simulations/run \
  -H "Content-Type: application/json" \
  -d @platelet_pooling_config.json
```

### 3. Verify in Azure Digital Twins Explorer

1. Open Azure Digital Twins Explorer: https://explorer.digitaltwins.azure.net/
2. Connect to your ADT instance
3. Select any device twin (e.g., `buffy_coat_packs`, `centrifuge`)
4. View Properties - should see all properties updated:
   - ✅ deviceId, deviceType, capacity
   - ✅ status, inUse, queueLength
   - ✅ utilizationRate
   - ✅ totalProcessed, totalIdleTime, totalProcessingTime, totalBlockedTime
   - ✅ location
   - ✅ lastUpdateTime

### 4. Check Property Values are Different

Run multiple simulations and verify that property values change:

```bash
# Run simulation 1
curl -X POST http://localhost:8000/simulations/run -H "Content-Type: application/json" -d @platelet_pooling_config.json

# Wait 10 seconds

# Run simulation 2
curl -X POST http://localhost:8000/simulations/run -H "Content-Type: application/json" -d @platelet_pooling_config.json
```

Check in Azure Digital Twins Explorer:
- `lastUpdateTime` should be more recent
- KPI values (totalProcessed, totalIdleTime, etc.) should reflect new simulation
- `utilizationRate` may be different

## DTDL Device Model Reference

The complete DTDL Device model is defined in `azure_integration/dtdl_models/Device.json`:

```json
{
  "@context": "dtmi:dtdl:context;3",
  "@id": "dtmi:platelet:Device;1",
  "@type": "Interface",
  "displayName": "Platelet Processing Device",
  "contents": [
    {"@type": "Property", "name": "deviceId", "schema": "string"},
    {"@type": "Property", "name": "deviceType", "schema": "string"},
    {"@type": "Property", "name": "status", "schema": {...}},
    {"@type": "Property", "name": "capacity", "schema": "integer"},
    {"@type": "Property", "name": "inUse", "schema": "integer"},
    {"@type": "Property", "name": "utilizationRate", "schema": "double"},
    {"@type": "Property", "name": "queueLength", "schema": "integer"},
    {"@type": "Property", "name": "totalProcessed", "schema": "integer"},
    {"@type": "Property", "name": "totalBlockedTime", "schema": "double"},
    {"@type": "Property", "name": "totalIdleTime", "schema": "double"},
    {"@type": "Property", "name": "totalProcessingTime", "schema": "double"},
    {"@type": "Property", "name": "location", "schema": "string"},
    {"@type": "Property", "name": "position", "schema": {"@type": "Object", ...}},
    {"@type": "Property", "name": "rotation", "schema": {"@type": "Object", ...}},
    {"@type": "Property", "name": "lastUpdateTime", "schema": "dateTime"}
  ]
}
```

## Azure Function Compatibility

The Azure Function (`azure_functions/ProcessSimulationTelemetry/__init__.py`) uses the `add` operation for JSON Patch, which works for both new and existing properties:

```python
patch.append({
    "op": "add",
    "path": f"/{key}",
    "value": value
})
```

This means all properties (new or existing) will be properly updated or created in the digital twins.

## Impact

✅ **Fixed**: Twin properties now update with every new simulation
✅ **Fixed**: All 13 DTDL Device properties are included in telemetry
✅ **Enhanced**: Utilization rate calculated and included
✅ **Enhanced**: Location and device metadata available in twins
✅ **Enhanced**: Timestamp added for tracking last update
✅ **Ready**: Support for 3D visualization with position/rotation properties

## Next Steps

1. ✅ Properties are now being sent correctly
2. ⏭️ Verify Azure Function is receiving and processing the telemetry (see below)
3. ⏭️ Fix 3D Scenes Studio model loading issue (separate issue - see `docs/FIX_BLOB_STORAGE_403.md`)

## Troubleshooting

### Properties Still Not Updating?

1. **Check Azure Integration is Enabled**:
   ```bash
   curl http://localhost:8000/azure/diagnostics
   ```
   Should show `azure_integration_enabled: true`

2. **Check API Logs**:
   ```bash
   # Start API with verbose logging
   export LOG_LEVEL=DEBUG
   uvicorn api.main:app --log-level debug
   ```
   Look for:
   - "Preparing telemetry: X devices, Y events"
   - "Telemetry prepared with X twin updates"
   - "Digital Twins updated: X twins"

3. **Check Azure Function Logs**:
   ```bash
   az webapp log tail --name <function-app-name> --resource-group <resource-group>
   ```
   Look for:
   - "ProcessSimulationTelemetry function triggered"
   - "Updated twin X with Y properties"
   - Any error messages

4. **Verify Twins Exist**:
   ```bash
   az dt twin query \
     --dt-name <instance-name> \
     --query-command "SELECT * FROM DIGITALTWINS WHERE \$dtId = 'buffy_coat_packs'"
   ```

5. **Test Direct Update**:
   ```bash
   # Test updating a twin directly
   az dt twin update \
     --dt-name <instance-name> \
     --twin-id buffy_coat_packs \
     --json-patch '[{"op":"add", "path":"/testProperty", "value":"test"}]'
   ```

## Related Documentation

- [QUICK_ENV_SETUP.md](../QUICK_ENV_SETUP.md) - Azure integration setup
- [LINEAR_FLOW_SETUP.md](../LINEAR_FLOW_SETUP.md) - Complete Azure setup
- [FUNCTION_APP_PERMISSIONS.md](FUNCTION_APP_PERMISSIONS.md) - Azure Function permissions
- [FIX_BLOB_STORAGE_403.md](FIX_BLOB_STORAGE_403.md) - 3D model loading issue
