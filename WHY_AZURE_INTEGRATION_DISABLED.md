# Azure Integration Configuration

## Quick Answer

**Azure integration is enabled by default to automatically update Digital Twin properties after simulations.**

This ensures that ADT properties (totalIdleTime, totalProcessed, totalBlockedTime, etc.) are always updated with the latest simulation data.

Users can disable Azure integration if needed for local development without Azure resources by setting `ENABLE_AZURE_INTEGRATION=false`.

## Current Status

Check the current status:
```bash
# In the API code (api/main.py line 62):
ENABLE_AZURE_INTEGRATION = os.getenv('ENABLE_AZURE_INTEGRATION', 'true').lower() == 'true'

# Default value is 'true' when environment variable is not set
```

You can verify this by running:
```bash
python -c "import os; print('Azure Integration:', os.getenv('ENABLE_AZURE_INTEGRATION', 'true'))"
```

## How to Disable Azure Integration (for local development)

### Option 1: Set Environment Variable (Recommended)

**For the current terminal session:**
```bash
export ENABLE_AZURE_INTEGRATION=false

# Then start the API
cd api
uvicorn main:app --reload
```

**For permanent configuration (add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export ENABLE_AZURE_INTEGRATION=false' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: Using .env File

Create a `.env` file in the project root:
```bash
cat > .env << 'EOF'
ENABLE_AZURE_INTEGRATION=false
EOF
```

Then load it before starting the API:
```bash
source .env
uvicorn api.main:app --reload
```

### Option 3: Docker/Container Deployment

```bash
docker run -e ENABLE_AZURE_INTEGRATION=false \
  your-image
```

### Option 4: Azure App Service Configuration

```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-rg \
  --settings \
    ENABLE_AZURE_INTEGRATION=false
```

## Prerequisites for Azure Integration (Enabled by Default)

When Azure integration is enabled (the default), ensure you have:

1. **Azure Digital Twins instance** created and configured
2. **Azure Function App** deployed (or direct ADT access)
3. **Proper permissions** configured:
   - Function App has Managed Identity enabled
   - Function App has "Azure Digital Twins Data Owner" role
4. **Device twins** created in Azure Digital Twins

### Quick Setup Script

Use the automated setup script:
```bash
./configure_function_permissions.sh <resource-group> <function-app> <dt-instance>
```

This will:
- Enable Managed Identity
- Assign required roles
- Configure endpoint
- Verify configuration

## Verify Azure Integration Status

### Method 1: API Diagnostics Endpoint

```bash
curl http://localhost:8000/azure/diagnostics | jq
```

Response will show:
```json
{
  "azure_integration_enabled": true/false,
  "azure_function_endpoint_configured": true/false,
  "azure_function_key_configured": true/false,
  "device_id_mapping": {...}
}
```

### Method 2: Smoke Test

```bash
python smoke_test.py --skip-simulation
```

This will report:
- ✅ Test 4: Azure Configuration (if enabled)
- ⏭️  Test 4: Azure Configuration (skipped: Azure integration disabled) (if disabled)

### Method 3: Check Environment

```bash
python -c "
import os
enabled = os.getenv('ENABLE_AZURE_INTEGRATION', 'false').lower() == 'true'
print(f'Azure Integration Enabled: {enabled}')
print(f'Function Endpoint: {os.getenv(\"AZURE_FUNCTION_ENDPOINT\", \"Not set\")}')
print(f'Function Key: {\"Set\" if os.getenv(\"AZURE_FUNCTION_KEY\") else \"Not set\"}')
"
```

## What Happens When Disabled vs Enabled?

### When ENABLED (default):
- ✅ Simulations run normally
- ✅ Results computed and returned
- ✅ Telemetry sent to Azure Function/Digital Twins
- ✅ Device twins updated in real-time with latest properties
- ✅ ADT properties (totalIdleTime, totalProcessed, etc.) always current
- ✅ Relationships tracked
- ⚠️  Requires Azure resources configured
- ⚠️  May incur Azure costs

### When DISABLED (for local dev):
- ✅ Simulations run normally
- ✅ Results are computed and returned
- ✅ No Azure costs incurred
- ❌ No Digital Twins updates
- ❌ No telemetry sent to Azure
- ℹ️  API logs: "Azure integration is disabled"

## Troubleshooting

### "Azure integration is disabled" message
**Cause**: `ENABLE_AZURE_INTEGRATION` environment variable is explicitly set to 'false'

**Solution (if you want it enabled)**:
Remove the environment variable to use the default, or set it to 'true':
```bash
unset ENABLE_AZURE_INTEGRATION
# OR
export ENABLE_AZURE_INTEGRATION=true
```

### Environment variable is set but still disabled
**Cause**: Variable might be set incorrectly

**Check**:
```bash
# These are ALL considered false:
ENABLE_AZURE_INTEGRATION=false
ENABLE_AZURE_INTEGRATION=False
ENABLE_AZURE_INTEGRATION=FALSE
ENABLE_AZURE_INTEGRATION=0
ENABLE_AZURE_INTEGRATION=no
ENABLE_AZURE_INTEGRATION=""

# Only these are considered true:
ENABLE_AZURE_INTEGRATION=true
ENABLE_AZURE_INTEGRATION=True
ENABLE_AZURE_INTEGRATION=TRUE
ENABLE_AZURE_INTEGRATION=1
ENABLE_AZURE_INTEGRATION=yes
ENABLE_AZURE_INTEGRATION=on

# Not set = default is TRUE (enabled)
# (unset ENABLE_AZURE_INTEGRATION)
```

**Solution**: Use lowercase `true` or unset the variable:
```bash
export ENABLE_AZURE_INTEGRATION=true
# OR
unset ENABLE_AZURE_INTEGRATION
```

### Integration enabled but no updates in Azure
**Possible causes**:
1. Function App permissions not configured → Run `./configure_function_permissions.sh`
2. Twins don't exist → Run `python azure_integration/scripts/create_linear_flow_twins.py`
3. Function endpoint wrong → Check `AZURE_FUNCTION_ENDPOINT` value
4. Network/firewall issues → Check Azure Function logs

See [docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md) for detailed troubleshooting.

## Architecture: How It Works

```
┌─────────────────┐
│   Simulation    │
│   Engine        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Server    │◄─── ENABLE_AZURE_INTEGRATION=true/false
│   (FastAPI)     │
└────────┬────────┘
         │
         │ if enabled
         ▼
┌─────────────────┐         ┌─────────────────────┐
│  Azure Function │────────▶│  Azure Digital      │
│  App            │  SDK    │  Twins              │
└─────────────────┘         └─────────────────────┘
```

## Complete Setup Example

### 1. Local Development (No Azure)
```bash
# Default - nothing to configure
cd api
uvicorn main:app --reload
# Azure integration: DISABLED ✓
```

### 2. Local Development (With Azure)
```bash
# Set environment variables
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT="https://platelet-func.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="abc123..."

# Start API
cd api
uvicorn main:app --reload
# Azure integration: ENABLED ✓
```

### 3. Production Deployment
```bash
# Configure in Azure App Service
az webapp config appsettings set \
  --name platelet-api \
  --resource-group platelet-rg \
  --settings ENABLE_AZURE_INTEGRATION=true

# Deploy
az webapp deployment source config-zip \
  --resource-group platelet-rg \
  --name platelet-api \
  --src app.zip
# Azure integration: ENABLED ✓
```

## Related Documentation

- **[README.md](README.md)** - Main documentation with E2E guide
- **[docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md)** - Permission troubleshooting
- **[LINEAR_FLOW_SETUP.md](LINEAR_FLOW_SETUP.md)** - Complete Azure setup
- **[ENHANCEMENT_2_SUMMARY.md](ENHANCEMENT_2_SUMMARY.md)** - Implementation details
- **[docs/UI_API_AZURE_INTEGRATION.md](docs/UI_API_AZURE_INTEGRATION.md)** - Integration guide

## Summary

**Azure integration is enabled by default** to ensure ADT properties are always updated with the latest simulation data.

**To disable (for local dev)**: Set `ENABLE_AZURE_INTEGRATION=false` environment variable.

**To verify**: Run `python smoke_test.py --skip-simulation` or check `/azure/diagnostics` endpoint.

**For help**: See troubleshooting guides in `docs/FUNCTION_APP_PERMISSIONS.md`
