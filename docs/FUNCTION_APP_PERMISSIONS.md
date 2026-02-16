# Function App → Azure Digital Twins Permissions Guide

**HIGH PRIORITY**: This guide addresses the most common issue preventing the E2E flow from working.

## Problem

Function App is not updating Digital Twins. Symptoms include:
- API returns 500 errors or timeout errors
- Function App logs show authentication failures
- Digital Twins Explorer shows no updates

## Root Cause

The Function App needs proper permissions to write to Azure Digital Twins. This requires:
1. Managed Identity enabled on the Function App
2. Correct role assignment on the Digital Twins instance
3. Proper endpoint configuration

## Solution Steps

### Step 1: Enable Managed Identity

Enable system-assigned managed identity for your Function App:

```bash
# Set variables
FUNCTION_APP="your-function-app-name"
RESOURCE_GROUP="your-resource-group"

# Enable managed identity
az functionapp identity assign \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP

# Get the principal ID (you'll need this for role assignment)
PRINCIPAL_ID=$(az functionapp identity show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

echo "Function App Principal ID: $PRINCIPAL_ID"
```

**Verification:**
- Go to Azure Portal → Your Function App → Identity
- You should see "System assigned" status as "On"
- Note the "Object (principal) ID" - this should match `$PRINCIPAL_ID`

### Step 2: Assign Azure Digital Twins Role

Assign the "Azure Digital Twins Data Owner" role to the Function App's managed identity:

```bash
# Set variables
DT_INSTANCE="your-digital-twins-instance"
RESOURCE_GROUP="your-resource-group"

# Assign role
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --assignee $PRINCIPAL_ID \
  --role "Azure Digital Twins Data Owner"
```

**Alternative roles** (use if you want more restrictive permissions):
- `Azure Digital Twins Data Owner` - Full access (recommended for development)
- `Azure Digital Twins Data Reader` - Read-only access (not sufficient for updates)

**Verification:**
```bash
# List role assignments
az dt role-assignment list \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP

# Look for your Function App's principal ID in the output
```

### Step 3: Configure Environment Variables

Set the correct Azure Digital Twins endpoint in your Function App settings:

```bash
# Get Digital Twins endpoint
DT_ENDPOINT=$(az dt show \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --query "hostName" -o tsv)

echo "Digital Twins Endpoint: https://$DT_ENDPOINT"

# Set environment variable in Function App
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"
```

**Verification:**
```bash
# List all app settings
az functionapp config appsettings list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='AZURE_DIGITAL_TWINS_ENDPOINT']"
```

### Step 4: Verify Network Access

Ensure your Function App can reach Azure Digital Twins:

```bash
# Check if Digital Twins instance has any network restrictions
az dt show \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --query "publicNetworkAccess"

# If result is "Disabled", you'll need to configure private endpoints
# or enable public network access
```

### Step 5: Test the Connection

Test that the Function App can update twins:

```bash
# Get Function App URL
FUNCTION_URL=$(az functionapp function show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --function-name ProcessSimulationTelemetry \
  --query "invokeUrlTemplate" -o tsv)

# Get function key (if using function-level auth)
FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

# Send test telemetry
curl -X POST "${FUNCTION_URL}?code=${FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "telemetry": [
      {
        "twin_id": "centrifuge",
        "properties": {
          "status": "Testing",
          "inUse": 1
        }
      }
    ]
  }'
```

**Expected response:**
```json
{
  "processed": 1,
  "success": 1,
  "failed": 0,
  "failed_updates": null,
  "endpoint": "https://your-instance.api.eus.digitaltwins.azure.net",
  "client_initialized": true
}
```

### Step 6: Check Function App Logs

If the test fails, check the Function App logs for detailed error messages:

```bash
# Stream logs (press Ctrl+C to stop)
az webapp log tail \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP

# Or view recent logs
az monitor activity-log list \
  --resource-group $RESOURCE_GROUP \
  --max-events 50
```

**Common error patterns and solutions:**

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `ClientAuthenticationError` | No managed identity or missing role | Complete Step 1 & 2 |
| `ResourceNotFoundError: Twin 'xxx' not found` | Twin doesn't exist in ADT | Run `create_linear_flow_twins.py` |
| `ServiceRequestError` | Network connectivity issue | Check Step 4 (network access) |
| `AZURE_DIGITAL_TWINS_ENDPOINT not configured` | Missing environment variable | Complete Step 3 |

## Automated Setup Script

Use this script to automatically configure permissions:

```bash
#!/bin/bash
# configure_function_permissions.sh

set -e

# Variables - UPDATE THESE
RESOURCE_GROUP="platelet-rg"
FUNCTION_APP="platelet-function-app"
DT_INSTANCE="platelet-dt-instance"

echo "Configuring Function App → Azure Digital Twins permissions..."

# 1. Enable Managed Identity
echo "Step 1: Enabling Managed Identity..."
az functionapp identity assign \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP

# 2. Get Principal ID
echo "Step 2: Getting Principal ID..."
PRINCIPAL_ID=$(az functionapp identity show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)
echo "   Principal ID: $PRINCIPAL_ID"

# 3. Assign role
echo "Step 3: Assigning Azure Digital Twins Data Owner role..."
az dt role-assignment create \
  --dt-name $DT_INSTANCE \
  --assignee $PRINCIPAL_ID \
  --role "Azure Digital Twins Data Owner"

# 4. Get and set endpoint
echo "Step 4: Configuring endpoint..."
DT_ENDPOINT=$(az dt show \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --query "hostName" -o tsv)
echo "   Endpoint: https://$DT_ENDPOINT"

az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings AZURE_DIGITAL_TWINS_ENDPOINT="https://$DT_ENDPOINT"

echo ""
echo "✅ Configuration complete!"
echo ""
echo "Next steps:"
echo "1. Restart your Function App (may take a few minutes)"
echo "2. Test with: curl \$FUNCTION_URL?code=\$FUNCTION_KEY -d '{...}'"
echo "3. Check logs with: az webapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP"
```

## Troubleshooting Checklist

Use this checklist to diagnose permission issues:

- [ ] **Managed Identity enabled?**
  ```bash
  az functionapp identity show --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
  ```

- [ ] **Role assignment exists?**
  ```bash
  az dt role-assignment list --dt-name $DT_INSTANCE --resource-group $RESOURCE_GROUP
  ```

- [ ] **Correct endpoint configured?**
  ```bash
  az functionapp config appsettings list --name $FUNCTION_APP --resource-group $RESOURCE_GROUP | grep AZURE_DIGITAL_TWINS_ENDPOINT
  ```

- [ ] **Twins exist in ADT?**
  ```bash
  az dt twin query --dt-name $DT_INSTANCE --query-command "SELECT * FROM DIGITALTWINS"
  ```

- [ ] **Function App can reach ADT?**
  - Check network/firewall rules
  - Verify public network access is enabled OR private endpoint is configured

- [ ] **Function App is running?**
  ```bash
  az functionapp show --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --query "state"
  ```

## API Version Issues

If you see errors about API versions, ensure your Function App uses compatible SDK versions:

```bash
# Check requirements.txt in azure_functions/
cat azure_functions/requirements.txt

# Should include:
# azure-digitaltwins-core>=1.2.0
# azure-identity>=1.12.0
```

## Additional Resources

- [Azure Digital Twins Role-Based Access Control](https://docs.microsoft.com/azure/digital-twins/concepts-security)
- [Managed Identities for Azure Resources](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
- [Troubleshoot Azure Digital Twins](https://docs.microsoft.com/azure/digital-twins/troubleshoot-error-codes)

## Support

If issues persist after following this guide:

1. **Capture logs** from Function App
2. **Check Azure Service Health** for outages
3. **Review recent changes** to network configuration
4. **Contact Azure Support** with logs and error messages
