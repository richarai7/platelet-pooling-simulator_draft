# Linear Flow Setup Guide

## Overview

This guide will help you set up the complete end-to-end flow:
**UI → API → Function App → Digital Twin**

The new platelet pooling process uses a **linear flow** with 10 devices:

1. **Buffy Coat packs** → 2. **Platelet washing** → 3. **Centrifuge** → 4. **Separator Macropress** → 5. **Resting Trolly** → 6. **Agitator** → 7. **Macropress** → 8. **Testing Agitator** → 9. **Labeling** → 10. **Release**

## Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Python 3.9+
- Node.js (for UI, if applicable)

## Step 1: Azure Digital Twins Setup

### Create Azure Digital Twins Instance

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="platelet-rg-new"
LOCATION="eastus"
DT_INSTANCE="platelet-dt-instance-new"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Digital Twins instance
az dt create \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Get the endpoint
DT_ENDPOINT=$(az dt show --dt-name $DT_INSTANCE --resource-group $RESOURCE_GROUP --query "hostName" -o tsv)
echo "Digital Twins Endpoint: https://$DT_ENDPOINT"
```

### Upload DTDL Models

```bash
# Upload device model
az dt model create \
  --dt-name $DT_INSTANCE \
  --models azure_integration/dtdl_models/Device.json

# Verify models
az dt model list --dt-name $DT_INSTANCE
```

### Create Device Twins with Relationships

```bash
# Set environment variable
export AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"

# Create all 10 device twins and their relationships
python azure_integration/scripts/create_linear_flow_twins.py \
  --endpoint https://$DT_ENDPOINT

# Verify twins were created
az dt twin query \
  --dt-name $DT_INSTANCE \
  --query-command "SELECT * FROM DIGITALTWINS"
```

## Step 2: Azure Function App Setup (Optional)

The Function App acts as a middleware between the API and Digital Twins. If you skip this, the API will use direct connection to Digital Twins.

### Create Function App

```bash
# Variables
FUNCTION_APP="platelet-function-app-new"
STORAGE_ACCOUNT="plateletsa$(date +%s)"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create function app
az functionapp create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --storage-account $STORAGE_ACCOUNT \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4
```

### Configure Function App

```bash
# Set Digital Twins endpoint
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"

# Enable managed identity
az functionapp identity assign \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP

# Get the managed identity principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

# Assign Digital Twins Data Owner role
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --assignee $PRINCIPAL_ID \
  --role "Azure Digital Twins Data Owner"
```

### Deploy Function Code

```bash
cd azure_functions

# Install dependencies locally (optional, for testing)
pip install -r requirements.txt

# Create deployment package
rm -f function.zip
zip -r function.zip . -x "*.pyc" -x "__pycache__/*" -x ".python_packages/*"

# Deploy to Azure
az functionapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --src function.zip

# Get function endpoint
FUNCTION_ENDPOINT=$(az functionapp function show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --function-name ProcessSimulationTelemetry \
  --query "invokeUrlTemplate" -o tsv)

echo "Function Endpoint: $FUNCTION_ENDPOINT"

# Get function key
FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

cd ..
```

## Step 3: API Configuration

### Set Environment Variables

Create a `.env` file or export these variables:

```bash
# Required for Azure integration
export ENABLE_AZURE_INTEGRATION=true
export AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"

# Optional - if using Function App (recommended for production)
export AZURE_FUNCTION_ENDPOINT="$FUNCTION_ENDPOINT"
export AZURE_FUNCTION_KEY="$FUNCTION_KEY"
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-azure.txt
```

### Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API should now be running at `http://localhost:8000`

## Step 4: Verify the Setup

### Test API Connection

```bash
curl http://localhost:8000/

# Check Azure diagnostics
curl http://localhost:8000/azure/diagnostics
```

### Run End-to-End Test

```bash
python test_end_to_end_flow.py
```

This script will:
1. ✅ Test API connection
2. ✅ Check Azure configuration
3. ✅ Verify Azure CLI login
4. ✅ List Digital Twins
5. ✅ Run a test simulation
6. ✅ Verify twin updates

### Test with UI (if available)

1. Start the UI:
   ```bash
   cd ui
   npm install
   npm run dev
   ```

2. Open browser to `http://localhost:5173`

3. Run a simulation and verify:
   - Simulation completes successfully
   - Results show Azure twins updated
   - Check Digital Twins Explorer to see updated values

## Step 5: View Digital Twins Graph

### Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Digital Twins instance
3. Click on "Azure Digital Twins Explorer"
4. You should see a graph with 10 devices connected in linear sequence:
   - Each device shows as a node
   - Arrows show the "feedsInto" relationships
   - Click on any device to see its properties

### Using Azure CLI

```bash
# Query all twins
az dt twin query \
  --dt-name $DT_INSTANCE \
  --query-command "SELECT * FROM DIGITALTWINS"

# Query relationships
az dt twin relationship list \
  --dt-name $DT_INSTANCE \
  --twin-id buffy_coat_packs

# Get specific twin
az dt twin show \
  --dt-name $DT_INSTANCE \
  --twin-id centrifuge
```

## Troubleshooting

### Function App Returns 500

```bash
# Check function logs
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# Verify role assignment
az dt role-assignment list --dt-name $DT_INSTANCE --resource-group $RESOURCE_GROUP

# Restart function app
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

### Twins Not Updating

1. **Check if Azure integration is enabled:**
   ```bash
   curl http://localhost:8000/azure/diagnostics
   ```

2. **Verify twins exist:**
   ```bash
   az dt twin query --dt-name $DT_INSTANCE --query-command "SELECT * FROM DIGITALTWINS"
   ```

3. **Check API logs** for any errors during telemetry sending

4. **Verify environment variables** are set correctly

### Direct Connection Issues

If Function App is not working, the API will fallback to direct connection. Ensure:

1. Your local machine has Azure credentials:
   ```bash
   az login
   ```

2. You have proper permissions on the Digital Twins instance

## Device Configuration

The new linear flow uses these 10 devices:

| # | Device ID | Type | Capacity | Location |
|---|-----------|------|----------|----------|
| 1 | buffy_coat_packs | material | 10 | Lab A - Station 1 |
| 2 | platelet_washing | machine | 10 | Lab A - Station 2 |
| 3 | centrifuge | machine | 10 | Lab A - Station 3 |
| 4 | separator_macropress | machine | 10 | Lab B - Station 1 |
| 5 | resting_trolly | material | 15 | Lab B - Station 2 |
| 6 | agitator | machine | 10 | Lab B - Station 3 |
| 7 | macropress | machine | 10 | Lab C - Station 1 |
| 8 | testing_agitator | machine | 10 | Lab C - Station 2 |
| 9 | labeling | workstation | 10 | Lab C - Station 3 |
| 10 | release | workstation | 10 | Lab D - Release Area |

## Next Steps

1. ✅ Run simulations with different configurations
2. ✅ Monitor twin updates in real-time
3. ✅ Analyze bottlenecks in the linear flow
4. ✅ Export results for further analysis
5. ✅ Set up alerting based on KPIs (future enhancement)

## Additional Resources

- [Azure Digital Twins Documentation](https://docs.microsoft.com/azure/digital-twins/)
- [DTDL Models](azure_integration/dtdl_models/)
- [API Documentation](http://localhost:8000/docs)
- [Setup Guide](docs/AZURE_SETUP_GUIDE.md)
