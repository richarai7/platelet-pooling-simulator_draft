# Question: "Why is Azure Integration Disabled?"

## Quick Answer

**Azure integration is disabled by default** in this repository. This is intentional and by design.

## Why It's Disabled

The `ENABLE_AZURE_INTEGRATION` environment variable defaults to `false` to:

1. **Enable local development** - Developers can run simulations without Azure resources
2. **Avoid Azure costs** - No charges while developing/testing locally
3. **Simplify onboarding** - New developers can start immediately without Azure setup
4. **Maintain flexibility** - Run with or without cloud integration

## Current Implementation

In `api/main.py` (line 62):
```python
ENABLE_AZURE_INTEGRATION = os.getenv('ENABLE_AZURE_INTEGRATION', 'false').lower() == 'true'
```

Default value: `'false'` when environment variable is not set.

## How to Check Status

**Quick check:**
```bash
./check_azure_integration.sh
```

**Manual check:**
```bash
python -c "import os; print('Enabled:', os.getenv('ENABLE_AZURE_INTEGRATION', 'false'))"
```

## How to Enable

### Option 1: Environment Variable (Recommended)
```bash
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT="https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry"

# Start API
uvicorn api.main:app --reload
```

### Option 2: .env File
```bash
cat > .env << 'EOF'
ENABLE_AZURE_INTEGRATION=true
AZURE_FUNCTION_ENDPOINT=https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry
AZURE_FUNCTION_KEY=your-key
EOF

source .env
uvicorn api.main:app --reload
```

### Option 3: Permanent (Add to shell profile)
```bash
echo 'export ENABLE_AZURE_INTEGRATION=true' >> ~/.bashrc
source ~/.bashrc
```

## What Changes When Enabled?

| Aspect | Disabled (Default) | Enabled |
|--------|-------------------|---------|
| Simulations | ✅ Run normally | ✅ Run normally |
| Results | ✅ Computed | ✅ Computed |
| Azure Twins | ❌ Not updated | ✅ Updated |
| Telemetry | ❌ Not sent | ✅ Sent to Azure |
| Azure Costs | ✅ None | ⚠️ May incur costs |
| Requirements | None | Azure resources |

## Prerequisites for Enabling

Before enabling, ensure you have:

1. ✅ Azure Digital Twins instance created
2. ✅ Function App deployed (or direct ADT access configured)
3. ✅ Permissions configured:
   ```bash
   ./configure_function_permissions.sh <rg> <function-app> <dt-instance>
   ```
4. ✅ Device twins created:
   ```bash
   python azure_integration/scripts/create_linear_flow_twins.py --endpoint <endpoint>
   ```

## Verification

After enabling, verify it works:

```bash
# Check API diagnostics
curl http://localhost:8000/azure/diagnostics | jq

# Run smoke test
python smoke_test.py --skip-simulation
```

Expected output when enabled:
```
✅ Test 4: Azure Configuration
   Direct ADT: https://your-instance.api.eus.digitaltwins.azure.net
```

## Complete Documentation

- **[WHY_AZURE_INTEGRATION_DISABLED.md](WHY_AZURE_INTEGRATION_DISABLED.md)** - Complete explanation (8K+ words)
- **[README.md](README.md)** - Main documentation with E2E guide
- **[docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md)** - Troubleshooting
- **[LINEAR_FLOW_SETUP.md](LINEAR_FLOW_SETUP.md)** - Azure setup guide

## Troubleshooting

### "Still disabled after setting environment variable"

Check the value:
```bash
echo $ENABLE_AZURE_INTEGRATION
```

Must be exactly: `true`, `True`, `TRUE`, `1`, `yes`, or `on`

### "Integration enabled but nothing happens"

1. Check Function App permissions:
   ```bash
   ./configure_function_permissions.sh <rg> <function-app> <dt-instance>
   ```

2. Verify twins exist:
   ```bash
   az dt twin query --dt-name <instance> --query-command "SELECT * FROM DIGITALTWINS"
   ```

3. Check Function App logs:
   ```bash
   az webapp log tail --name <function-app> --resource-group <rg>
   ```

## Summary

✅ **Azure integration is disabled by default** - this is normal and expected

✅ **To enable**: Set `ENABLE_AZURE_INTEGRATION=true` 

✅ **To check**: Run `./check_azure_integration.sh`

✅ **For help**: See `WHY_AZURE_INTEGRATION_DISABLED.md`
