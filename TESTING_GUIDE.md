# Complete Testing Guide: Azure Digital Twins Integration

## Overview

This guide provides step-by-step instructions to:
1. ✅ Deploy Azure resources
2. ✅ Test the complete flow
3. ✅ Run simulations from UI
4. ✅ Verify twins are updating

---

## Prerequisites

### Required Tools

```bash
# 1. Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Azure Functions Core Tools (for function deployment)
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# 3. Python dependencies
pip install -r requirements.txt
pip install -r requirements-azure.txt

# 4. Node.js and npm (for UI)
# Install from: https://nodejs.org/
```

### Azure Subscription

You need an active Azure subscription. If you don't have one:
- Free trial: https://azure.microsoft.com/free/
- Or use Azure for Students

---

## Method 1: Automated Deployment (Recommended)

### Step 1: Run Deployment Script

```bash
# Make scripts executable
chmod +x deploy_azure.sh test_azure_deployment.sh

# Run deployment
./deploy_azure.sh
```

**What it does:**
- ✅ Creates resource group
- ✅ Creates Digital Twins instance
- ✅ Uploads DTDL models
- ✅ Creates Function App
- ✅ Deploys function code
- ✅ Configures permissions
- ✅ Saves configuration to `azure_deployment_config.env`

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════════════╗
║     Azure Digital Twins - Complete Deployment and Testing Script         ║
╚══════════════════════════════════════════════════════════════════════════╝

✓ Already logged in to Azure
✓ Using subscription: Your Subscription
✓ Resource group: platelet-rg
✓ Digital Twins instance created: platelet-dt-XXXXX
✓ Endpoint: https://platelet-dt-XXXXX.api.eus.digitaltwins.azure.net
...
╔══════════════════════════════════════════════════════════════════════════╗
║                     DEPLOYMENT COMPLETED!                                 ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Step 2: Load Configuration

```bash
source azure_deployment_config.env
```

### Step 3: Run Tests

```bash
./test_azure_deployment.sh
```

**What it tests:**
- ✅ Azure login status
- ✅ Digital Twins instance
- ✅ DTDL models uploaded
- ✅ Device twins created
- ✅ Simulation execution
- ✅ Twin updates verified
- ✅ API integration (if API running)

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════════════╗
║          Azure Digital Twins - Complete Testing Script                   ║
╚══════════════════════════════════════════════════════════════════════════╝

✓ Logged in as: your-email@example.com
✓ Digital Twins instance status: Succeeded
✓ Models uploaded: 2
✓ Total twins in Digital Twins: 11
✓ Simulation completed successfully
✓ Centrifuge twin updated - totalProcessed: 1

╔══════════════════════════════════════════════════════════════════════════╗
║                     TESTING COMPLETED!                                    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Method 2: Manual Step-by-Step

### Step 1: Azure Login

```bash
az login
```

Browser will open for authentication.

### Step 2: Create Resource Group

```bash
RESOURCE_GROUP="platelet-rg"
LOCATION="eastus"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 3: Create Digital Twins Instance

```bash
DT_INSTANCE="platelet-dt-$(date +%s)"

az dt create \
    --dt-name $DT_INSTANCE \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

Wait 2-3 minutes for provisioning.

### Step 4: Get Endpoint

```bash
DT_ENDPOINT=$(az dt show \
    --dt-name $DT_INSTANCE \
    --resource-group $RESOURCE_GROUP \
    --query "hostName" -o tsv)

export AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"

echo "Endpoint: $AZURE_DIGITAL_TWINS_ENDPOINT"
```

### Step 5: Grant Permissions

```bash
USER_ID=$(az ad signed-in-user show --query id -o tsv)

az dt role-assignment create \
    --dt-name $DT_INSTANCE \
    --assignee $USER_ID \
    --role "Azure Digital Twins Data Owner"
```

### Step 6: Upload DTDL Models

```bash
az dt model create \
    --dt-name $DT_INSTANCE \
    --models azure_integration/dtdl_models/*.json
```

Verify:
```bash
az dt model list --dt-name $DT_INSTANCE
```

### Step 7: Create Device Twins

```bash
python azure_integration/scripts/create_device_twins.py \
    --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT
```

Verify:
```bash
az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT COUNT() FROM digitaltwins"
```

### Step 8: Run Simulation

```bash
python run_simulation_with_adt.py --config default_config.json
```

### Step 9: Verify Twins Updated

```bash
az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge
```

---

## Testing UI → API → Azure Function Flow

### Step 1: Configure API

```bash
# Load Azure configuration
source azure_deployment_config.env

# Or manually set:
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT=<your-function-url>
```

### Step 2: Start API Server

```bash
cd api
uvicorn main:app --reload
```

### Step 3: Start UI (in another terminal)

```bash
cd ui
npm install  # First time only
npm run dev
```

### Step 4: Open Browser

Navigate to: http://localhost:5173

### Step 5: Run Simulation from UI

1. Click **"Run Simulation"** button
2. Watch the progress
3. Wait for completion

### Step 6: Verify in Azure Portal

1. Go to https://portal.azure.com
2. Navigate to your Digital Twins instance
3. Click **"Azure Digital Twins Explorer"**
4. Run query:
   ```sql
   SELECT * FROM digitaltwins
   ORDER BY $dtId
   ```
5. Check device properties:
   - `status`: Should show "Idle" or "Processing"
   - `totalProcessed`: Should be > 0
   - `totalIdleTime`: Should have values
   - `totalProcessingTime`: Should have values

---

## Verification Checklist

### ✅ Deployment Verification

- [ ] Azure login successful
- [ ] Resource group created
- [ ] Digital Twins instance created
- [ ] DTDL models uploaded (2 models minimum)
- [ ] Device twins created (11 twins minimum)
- [ ] Function App created (if using API flow)
- [ ] Permissions granted

### ✅ Direct Simulation Test

- [ ] `run_simulation_with_adt.py` executes without errors
- [ ] Simulation completes (20 flows)
- [ ] Device twins show updated properties
- [ ] Simulation twin created

### ✅ UI Flow Test

- [ ] API server starts successfully
- [ ] UI loads in browser
- [ ] Simulation can be triggered from UI
- [ ] API calls Azure Function (check logs)
- [ ] Twins updated in Digital Twins

### ✅ Twin Verification

Check each device twin has:
- [ ] `status` property
- [ ] `totalProcessed` > 0
- [ ] `totalIdleTime` > 0
- [ ] `totalProcessingTime` >= 0
- [ ] `lastUpdateTime` is recent

---

## Viewing Twins in Azure Portal

### Method 1: Azure Digital Twins Explorer

1. Go to https://portal.azure.com
2. Search for your Digital Twins instance
3. Click **"Azure Digital Twins Explorer"** in left menu
4. You'll see a graph visualization

### Method 2: Query Editor

In Azure Digital Twins Explorer, use the query editor:

```sql
-- View all twins
SELECT * FROM digitaltwins

-- View only devices
SELECT * FROM digitaltwins 
WHERE IS_OF_MODEL('dtmi:platelet:Device;1')

-- View simulation twins
SELECT * FROM digitaltwins 
WHERE IS_OF_MODEL('dtmi:platelet:Simulation;1')

-- View specific device
SELECT * FROM digitaltwins 
WHERE $dtId = 'centrifuge'

-- View devices with processing
SELECT * FROM digitaltwins 
WHERE IS_OF_MODEL('dtmi:platelet:Device;1') 
AND totalProcessed > 0
```

### Method 3: Command Line

```bash
# View all twins
az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT * FROM digitaltwins"

# View specific twin
az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge

# View twin properties
az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge \
    --query "{status: status, totalProcessed: totalProcessed}"
```

---

## Troubleshooting

### Issue: "Digital Twins instance not found"

**Solution:**
```bash
# List all DT instances in subscription
az dt list --query "[].{Name:name, RG:resourceGroup}"

# Check resource group
az group show --name platelet-rg
```

### Issue: "Models not found"

**Solution:**
```bash
# List uploaded models
az dt model list --dt-name $DT_INSTANCE

# Re-upload if needed
az dt model create --dt-name $DT_INSTANCE \
    --models azure_integration/dtdl_models/*.json
```

### Issue: "Twins not updating"

**Checklist:**
1. Check endpoint is correct:
   ```bash
   echo $AZURE_DIGITAL_TWINS_ENDPOINT
   ```

2. Check permissions:
   ```bash
   az dt role-assignment list --dt-name $DT_INSTANCE
   ```

3. Test direct update:
   ```bash
   az dt twin update --dt-name $DT_INSTANCE --twin-id centrifuge \
       --json-patch '[{"op":"replace","path":"/status","value":"Testing"}]'
   ```

4. Check twin exists:
   ```bash
   az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge
   ```

### Issue: "API not calling Azure Function"

**Checklist:**
1. Check environment variables:
   ```bash
   env | grep AZURE
   ```

2. Check API logs for errors

3. Test function directly:
   ```bash
   curl -X POST "$AZURE_FUNCTION_ENDPOINT" \
       -H "Content-Type: application/json" \
       -d '{"telemetry":[{"twin_id":"test","properties":{"status":"Test"}}]}'
   ```

### Issue: "Permission denied"

**Solution:**
```bash
# Grant yourself Data Owner role
USER_ID=$(az ad signed-in-user show --query id -o tsv)
az dt role-assignment create \
    --dt-name $DT_INSTANCE \
    --assignee $USER_ID \
    --role "Azure Digital Twins Data Owner"

# Wait 1-2 minutes for propagation
```

---

## Quick Commands Reference

```bash
# Load configuration
source azure_deployment_config.env

# Deploy everything
./deploy_azure.sh

# Test everything
./test_azure_deployment.sh

# Create twins
python azure_integration/scripts/create_device_twins.py \
    --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT

# Run simulation
python run_simulation_with_adt.py --config default_config.json

# Test API flow
python test_ui_api_azure_flow.py

# View twins
az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT * FROM digitaltwins"

# Clean up (delete everything)
az group delete --name $RESOURCE_GROUP --yes
```

---

## Success Criteria

You've successfully completed testing when:

✅ All scripts run without errors
✅ Twins are visible in Azure Portal
✅ Simulation from UI updates twins
✅ Query results show updated properties
✅ All 11 device twins + simulation twin exist

---

## Cost Estimation

**Free/Trial tier:**
- Digital Twins: First 1000 messages/month free
- Function App: 1M executions/month free
- Storage: Minimal cost (~$0.01/month)

**Expected monthly cost for POC:**
- ~$5-10/month with minimal usage
- Can be reduced by deleting resources when not in use

**To minimize costs:**
```bash
# Stop Function App when not needed
az functionapp stop --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# Restart when needed
az functionapp start --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# Delete everything
az group delete --name $RESOURCE_GROUP --yes
```

---

## Next Steps

After successful testing:

1. **Customize configuration**: Edit `default_config.json`
2. **Add more devices**: Modify device twins
3. **Create dashboards**: Use Azure Dashboard or custom UI
4. **Add monitoring**: Set up Azure Monitor alerts
5. **Deploy to production**: Use separate resource groups for dev/prod

---

**Last Updated**: 2026-02-15  
**Status**: Ready for testing  
**Support**: See `TROUBLESHOOTING.md` or Azure documentation
