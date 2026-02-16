# Azure Digital Twins Integration Guide

## Overview

This guide walks you through setting up the complete end-to-end flow from simulation to Azure Digital Twins visualization.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│   Simulation    │────────▶│  Azure Function  │────────▶│  Azure Digital      │
│   Engine        │  HTTP   │  App             │  SDK    │  Twins              │
│   (Python)      │         │  (Telemetry)     │         │  (DTDL Graph)       │
└─────────────────┘         └──────────────────┘         └─────────────────────┘
        │                                                            │
        │                                                            │
        ▼                                                            ▼
┌─────────────────┐                                       ┌─────────────────────┐
│   SQLite DB     │                                       │  Azure Data         │
│   (Config)      │                                       │  Explorer (ADX)     │
└─────────────────┘                                       └─────────────────────┘
        
        ▲                                                            │
        │                                                            │
        │                                                            ▼
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│   React UI      │◀────────│  WebSocket/      │◀────────│  SignalR Service    │
│   (Dashboard)   │  Events │  SignalR         │  Events │  (Real-time)        │
└─────────────────┘         └──────────────────┘         └─────────────────────┘
```

## Prerequisites

### Azure Resources Required

1. **Azure Digital Twins Instance**
   - Region: Choose closest to your location
   - Pricing: Standard tier

2. **Azure Function App**
   - Runtime: Python 3.9+
   - Plan: Consumption or Premium (for better cold-start performance)

3. **Azure Data Explorer (ADX)** (Optional for POC)
   - Cluster size: Dev/Test for POC
   - Database: Create one for simulation data

4. **Azure SignalR Service** (Optional for real-time UI)
   - Pricing tier: Free or Standard

### Local Development Tools

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Install Python dependencies
pip install azure-identity azure-digitaltwins-core azure-functions
```

## Step 1: Create Azure Digital Twins Instance

### Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource" → Search for "Azure Digital Twins"
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Select closest region
   - **Resource Name**: `platelet-dt-instance` (must be globally unique)
4. Click "Review + Create" → "Create"
5. Wait for deployment (2-3 minutes)
6. Note the **Host Name**: `https://platelet-dt-instance.api.eus.digitaltwins.azure.net`

### Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name platelet-rg-new --location eastus

# Create Digital Twins instance
az dt create \
  --dt-name platelet-dt-instance-new \
  --resource-group platelet-rg-new \
  --location eastus

# Get the endpoint
az dt show --dt-name platelet-dt-instance-new --resource-group platelet-rg-new --query "hostName" -o tsv
```

## Step 2: Upload DTDL Models

### Upload Models to Azure Digital Twins

**First, grant yourself permissions:**

```bash
# Get your Azure account email
USER_EMAIL=$(az account show --query user.name -o tsv)

# Grant permissions (this may take 1-2 minutes to propagate)
az dt role-assignment create \
  --dt-name platelet-dt-instance-new \
  --resource-group platelet-rg-new \
  --assignee $USER_EMAIL \
  --role "Azure Digital Twins Data Owner"
```

**Then upload the models:**

```bash
# Set your instance name
DT_INSTANCE="platelet-dt-instance-new"
RESOURCE_GROUP="platelet-rg-new"

# Upload Device model
az dt model create \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --models azure_integration/dtdl_models/Device.json

# Upload ProcessFlow model
az dt model create \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --models azure_integration/dtdl_models/ProcessFlow.json

# Upload Simulation model
az dt model create \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --models azure_integration/dtdl_models/Simulation.json

# Verify models uploaded
az dt model list \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP
```

### Create Initial Device Twins

```bash
# Example: Create device twins for 12 physical devices
# Device 1: Centrifuge
az dt twin create \
  --dt-name $DT_INSTANCE \
  --dtmi "dtmi:platelet:Device;1" \
  --twin-id "centrifuge-01" \
  --properties '{
    "deviceId": "centrifuge-01",
    "deviceType": "centrifuge",
    "status": "Idle",
    "capacity": 2,
    "inUse": 0,
    "utilizationRate": 0.0,
    "queueLength": 0,
    "totalProcessed": 0,
    "location": "Lab A - Station 1"
  }'

# Device 2: Platelet Separator
az dt twin create \
  --dt-name $DT_INSTANCE \
  --dtmi "dtmi:platelet:Device;1" \
  --twin-id "separator-01" \
  --properties '{
    "deviceId": "separator-01",
    "deviceType": "separator",
    "status": "Idle",
    "capacity": 2,
    "inUse": 0,
    "utilizationRate": 0.0,
    "queueLength": 0,
    "totalProcessed": 0,
    "location": "Lab A - Station 2"
  }'

# Continue for all 12 devices...
# centrifuge-02, separator-02, macopress-01, macopress-02, etc.
```

Alternatively, use the provided script (creates all 12 devices automatically):

```bash
# First, ensure Azure SDK is installed
pip install azure-identity azure-digitaltwins-core

# Get Digital Twins endpoint
DT_ENDPOINT=$(az dt show --dt-name platelet-dt-instance-new --resource-group platelet-rg-new --query "hostName" -o tsv)

# Create all device twins using default configuration
python azure_integration/scripts/create_device_twins.py \
  --endpoint "https://$DT_ENDPOINT"
```

## Step 3: Deploy Azure Function App

### Create Function App in Azure

```bash
# Create storage account (required for Functions)
az storage account create \
  --name plateletfuncstoragenew \
  --location eastus \
  --resource-group platelet-rg-new \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group platelet-rg-new \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name platelet-function-app-new \
  --storage-account plateletfuncstoragenew \
  --os-type Linux
```

### Configure Function App Settings

```bash
# Get Digital Twins endpoint
DT_ENDPOINT=$(az dt show --dt-name $DT_INSTANCE --resource-group platelet-rg-new --query "hostName" -o tsv)

# Set environment variable
az functionapp config appsettings set \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new \
  --settings AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"
```

### Enable System-Assigned Managed Identity

```bash
# Enable managed identity
az functionapp identity assign \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new

# Get the principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new \
  --query principalId -o tsv)

# Grant Function App permissions to Digital Twins
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --assignee $PRINCIPAL_ID \
  --role "Azure Digital Twins Data Owner"
```

### Deploy Function Code

```bash
# Navigate to azure_functions directory
cd azure_functions

# Deploy to Azure

npm install -g azure-functions-core-tools@4 --unsafe-perm true

func azure functionapp publish platelet-function-app-new --python




# 2nd Approach-
cd /workspaces/platelet-pooling-simulator_draft/azure_functions

zip -r function.zip . -x "*.pyc" -x "__pycache__/*"

az functionapp deployment source config-zip \
  --resource-group platelet-rg-new \
  --name platelet-function-app-new \
  --src function.zip

# Verify deployment
az functionapp function show \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new \
  --function-name ProcessSimulationTelemetry
```

### Get Function URL and Key

```bash
# Get function URL
FUNCTION_URL=$(az functionapp function show \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new \
  --function-name ProcessSimulationTelemetry \
  --query "invokeUrlTemplate" -o tsv)

# Get function key
FUNCTION_KEY=$(az functionapp keys list \
  --name platelet-function-app-new \
  --resource-group platelet-rg-new \
  --query "functionKeys.default" -o tsv)

echo "Function Endpoint: $FUNCTION_URL"
echo "Function Key: $FUNCTION_KEY"
```

## Step 4: Configure Simulation Engine

### Update Configuration File

Create or update `azure_config.json`:

```json
{
  "azure_digital_twins": {
    "endpoint": "https://platelet-dt-instance.api.eus.digitaltwins.azure.net",
    "batch_size": 10,
    "batch_interval_seconds": 1.0,
    "rate_limit_per_second": 50
  },
  "azure_function": {
    "endpoint": "https://platelet-function-app.azurewebsites.net/api/ProcessSimulationTelemetry",
    "function_key": "YOUR_FUNCTION_KEY_HERE"
  },
  "telemetry": {
    "enabled": true,
    "stream_mode": "function_app",
    "buffer_size": 100
  }
}
```

### Set Environment Variables

```bash
# For local development
export AZURE_DIGITAL_TWINS_ENDPOINT="https://platelet-dt-instance.api.eus.digitaltwins.azure.net"
export AZURE_FUNCTION_ENDPOINT="https://platelet-function-app.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="YOUR_FUNCTION_KEY_HERE"

# Or create .env file
cat > .env << EOF
AZURE_DIGITAL_TWINS_ENDPOINT=https://platelet-dt-instance.api.eus.digitaltwins.azure.net
AZURE_FUNCTION_ENDPOINT=https://platelet-function-app.azurewebsites.net/api/ProcessSimulationTelemetry
AZURE_FUNCTION_KEY=YOUR_FUNCTION_KEY_HERE
EOF
```

## Step 5: Run End-to-End Test

### Test 1: Direct Digital Twins Connection (Local)

```bash
# Run simulation with direct ADT connection
python examples/test_azure_integration.py \
  --mode direct \
  --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT

# Expected output:
# ✓ Connected to Azure Digital Twins
# ✓ Running simulation...
# ✓ Streaming telemetry to ADT
# ✓ Simulation complete: 50 flows processed
# ✓ All device twins updated successfully
```

### Test 2: Via Azure Function (Production Mode)

```bash
# Run simulation via Function App
python examples/test_azure_integration.py \
  --mode function \
  --endpoint "$AZURE_FUNCTION_ENDPOINT?code=$AZURE_FUNCTION_KEY"

# Expected output:
# ✓ Connected to Function App
# ✓ Running simulation...
# ✓ Sending telemetry batches to Function
# ✓ Function response: 200 OK
# ✓ Simulation complete: 50 flows processed
```

### Test 3: Verify in Azure Portal

1. Go to Azure Portal → Your Digital Twins instance
2. Click "Azure Digital Twins Explorer"
3. You should see:
   - Device twins with updated properties
   - Real-time status changes
   - Telemetry events

## Step 6: Real-Time Visualization (Optional)

### Setup SignalR Service

```bash
# Create SignalR Service
az signalr create \
  --name platelet-signalr \
  --resource-group platelet-rg-new \
  --sku Free_F1 \
  --location eastus

# Get connection string
az signalr key list \
  --name platelet-signalr \
  --resource-group platelet-rg-new \
  --query primaryConnectionString -o tsv
```

### Configure React UI

Update `ui/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_SIGNALR_URL=https://platelet-signalr.service.signalr.net
VITE_ADT_ENDPOINT=https://platelet-dt-instance.api.eus.digitaltwins.azure.net
```

### Run UI Dashboard

```bash
cd ui
npm install
npm run dev

# Open browser to http://localhost:5173
# You should see:
# - Real-time device status updates
# - Live telemetry graphs
# - 3D visualization (if configured)
```

## Step 7: Setup Historical Data (ADX)

### Create Azure Data Explorer

```bash
# Create ADX cluster
az kusto cluster create \
  --cluster-name plateletadx \
  --resource-group platelet-rg-new \
  --location eastus \
  --sku name="Dev(No SLA)_Standard_E2a_v4" tier="Basic"

# Create database
az kusto database create \
  --cluster-name plateletadx \
  --database-name SimulationHistory \
  --resource-group platelet-rg-new \
  --read-write-database soft-delete-period=P365D hot-cache-period=P31D
```

### Setup Data History Connection

```bash
# Create data history connection from ADT to ADX
az dt data-history connection create adx \
  --dt-name $DT_INSTANCE \
  --cn adx-connection \
  --adx-cluster-name plateletadx \
  --adx-database-name SimulationHistory \
  --adx-property-events-table DevicePropertyChanges \
  --adx-twin-lifecycle-events-table TwinLifecycleEvents \
  --resource-group platelet-rg-new
```

### Query Historical Data

```kql
// In ADX query editor

// Get all device state changes in last hour
DevicePropertyChanges
| where TimeGenerated > ago(1h)
| where Name == "status"
| project TimeGenerated, TwinId, Value
| order by TimeGenerated desc

// Calculate average utilization
DevicePropertyChanges
| where Name == "utilizationRate"
| summarize AvgUtilization=avg(todouble(Value)) by TwinId
| order by AvgUtilization desc

// Find bottlenecks (devices with highest blocked time)
DevicePropertyChanges
| where Name == "totalBlockedTime"
| summarize MaxBlockedTime=max(todouble(Value)) by TwinId
| order by MaxBlockedTime desc
```

## Troubleshooting

### Issue: Function App Returns 500

**Common Causes:**
1. Missing or incorrect AZURE_DIGITAL_TWINS_ENDPOINT environment variable
2. Managed Identity not properly configured
3. Role assignment not propagated
4. Cold start timeout issues
5. Python runtime/dependency issues

**Solution:**
```bash
# 1. Verify environment variable is set
az functionapp config appsettings list \
  --name platelet-function-app \
  --resource-group platelet-rg-new \
  | grep AZURE_DIGITAL_TWINS_ENDPOINT

# 2. Verify managed identity is enabled
az functionapp identity show \
  --name platelet-function-app \
  --resource-group platelet-rg-new

# 3. Re-grant permissions (wait 2-3 minutes for propagation)
PRINCIPAL_ID=$(az functionapp identity show \
  --name platelet-function-app \
  --resource-group platelet-rg-new \
  --query principalId -o tsv)

az dt role-assignment create \
  --dt-name platelet-dt-instance-new \
  --assignee $PRINCIPAL_ID \
  --role "Azure Digital Twins Data Owner"

# 4. Restart function app
az functionapp restart \
  --name platelet-function-app \
  --resource-group platelet-rg-new

# 5. Redeploy function code
cd azure_functions
rm -f function.zip
zip -r function.zip . -x "*.pyc" -x "__pycache__/*" -x ".python_packages/*"
az functionapp deployment source config-zip \
  --resource-group platelet-rg-new \
  --name platelet-function-app \
  --src function.zip
```

**Note:** The API includes automatic fallback - if the Azure Function fails, it will use direct Azure Digital Twins connection instead. This ensures your simulations always update twins successfully even if the function has issues.

### Issue: Permission Denied on Digital Twins

**Solution:**
```bash
# Grant your user account permissions
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --assignee your-email@domain.com \
  --role "Azure Digital Twins Data Owner"

# For service principal/managed identity
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --assignee <principal-id> \
  --role "Azure Digital Twins Data Owner"
```

### Issue: Twins Not Updating

**Solution:**
1. Check twin exists:
   ```bash
   az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge-01
   ```

2. Verify model is uploaded:
   ```bash
   az dt model show --dt-name $DT_INSTANCE --dtmi "dtmi:platelet:Device;1"
   ```

3. Test direct update:
   ```bash
   az dt twin update \
     --dt-name $DT_INSTANCE \
     --twin-id centrifuge-01 \
     --json-patch '[{"op":"replace","path":"/status","value":"Processing"}]'
   ```

### Issue: Rate Limiting

If you see rate limit errors:

```python
# Adjust throttling settings in azure_config.json
{
  "azure_digital_twins": {
    "batch_size": 5,  # Reduce batch size
    "batch_interval_seconds": 2.0,  # Increase interval
    "rate_limit_per_second": 25  # Reduce rate limit
  }
}
```

## Performance Optimization

### For Accelerated Simulation

When running accelerated simulations (36 hours in < 2 minutes):

1. **Increase batching:**
   ```json
   {
     "batch_size": 50,
     "batch_interval_seconds": 0.5
   }
   ```

2. **Use Function App Premium Plan:**
   ```bash
   az functionapp plan create \
     --name premium-plan \
     --resource-group platelet-rg-new \
     --sku EP1 \
     --location eastus
   ```

3. **Enable Event Hubs (optional):**
   ```bash
   # For very high throughput
   az eventhubs namespace create \
     --name platelet-events \
     --resource-group platelet-rg-new \
     --location eastus
   ```

## Cost Estimation (Monthly)

**Development/POC:**
- Azure Digital Twins: ~$5-10
- Function App (Consumption): ~$0-5
- Storage: ~$1
- **Total: ~$6-16/month**

**Production:**
- Azure Digital Twins: ~$20-50
- Function App (Premium): ~$150
- ADX (Dev cluster): ~$75
- SignalR (Standard): ~$50
- **Total: ~$295-325/month**

## Next Steps

1. ✅ Azure infrastructure deployed
2. ✅ DTDL models uploaded
3. ✅ Function App configured
4. ✅ Simulation connected
5. 🔄 Add 3D visualization
6. 🔄 Implement advanced KPIs in ADX
7. 🔄 Setup alerting and monitoring

## Support

For issues or questions:
- Check logs in Azure Portal
- Review Azure Digital Twins documentation
- See troubleshooting section above
