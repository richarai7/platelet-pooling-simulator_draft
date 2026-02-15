#!/bin/bash
# Complete Azure Deployment and Testing Script
# This script deploys all Azure resources and tests the complete flow

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║     Azure Digital Twins - Complete Deployment and Testing Script         ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
RESOURCE_GROUP="platelet-rg"
LOCATION="eastus"
DT_INSTANCE="platelet-dt-$(date +%s)"  # Unique name with timestamp
FUNCTION_APP="platelet-func-$(date +%s)"
STORAGE_ACCOUNT="plateletstore$(date +%s | cut -c 1-10)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Azure Login
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Azure Login"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if az account show &>/dev/null; then
    log_info "Already logged in to Azure"
    SUBSCRIPTION=$(az account show --query name -o tsv)
    log_info "Using subscription: $SUBSCRIPTION"
else
    echo "Please log in to Azure..."
    az login
fi

# Step 2: Create Resource Group
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Create Resource Group"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if az group show --name $RESOURCE_GROUP &>/dev/null; then
    log_warn "Resource group '$RESOURCE_GROUP' already exists"
else
    az group create --name $RESOURCE_GROUP --location $LOCATION
    log_info "Created resource group: $RESOURCE_GROUP"
fi

# Step 3: Create Digital Twins Instance
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Create Azure Digital Twins Instance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Creating Digital Twins instance: $DT_INSTANCE"
az dt create \
    --dt-name $DT_INSTANCE \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

log_info "Digital Twins instance created: $DT_INSTANCE"

# Get Digital Twins endpoint
DT_ENDPOINT=$(az dt show --dt-name $DT_INSTANCE --resource-group $RESOURCE_GROUP --query "hostName" -o tsv)
log_info "Endpoint: https://$DT_ENDPOINT"

# Step 4: Grant Permissions
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Grant Permissions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

USER_ID=$(az ad signed-in-user show --query id -o tsv)
az dt role-assignment create \
    --dt-name $DT_INSTANCE \
    --assignee $USER_ID \
    --role "Azure Digital Twins Data Owner"

log_info "Granted 'Azure Digital Twins Data Owner' role to current user"

# Step 5: Upload DTDL Models
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Upload DTDL Models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "azure_integration/dtdl_models" ]; then
    az dt model create \
        --dt-name $DT_INSTANCE \
        --models azure_integration/dtdl_models/*.json
    log_info "DTDL models uploaded"
else
    log_error "DTDL models directory not found"
    exit 1
fi

# Step 6: Create Storage Account for Function App
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Create Storage Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

az storage account create \
    --name $STORAGE_ACCOUNT \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_LRS

log_info "Storage account created: $STORAGE_ACCOUNT"

# Step 7: Create Function App
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7: Create Function App"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --name $FUNCTION_APP \
    --storage-account $STORAGE_ACCOUNT \
    --os-type Linux

log_info "Function App created: $FUNCTION_APP"

# Step 8: Configure Function App
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 8: Configure Function App"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings "AZURE_DIGITAL_TWINS_ENDPOINT=https://$DT_ENDPOINT"

log_info "Function App configured with Digital Twins endpoint"

# Step 9: Enable Managed Identity
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 9: Enable Managed Identity and Grant Permissions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

az functionapp identity assign \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP

PRINCIPAL_ID=$(az functionapp identity show \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query principalId -o tsv)

az dt role-assignment create \
    --dt-name $DT_INSTANCE \
    --assignee $PRINCIPAL_ID \
    --role "Azure Digital Twins Data Owner"

log_info "Managed identity enabled and permissions granted"

# Step 10: Deploy Function Code
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 10: Deploy Function Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v func &>/dev/null && [ -d "azure_functions" ]; then
    cd azure_functions
    func azure functionapp publish $FUNCTION_APP --python
    cd ..
    log_info "Function App deployed"
else
    log_warn "Azure Functions Core Tools not found or azure_functions directory missing"
    log_warn "Skipping function deployment - install with: npm install -g azure-functions-core-tools@4"
fi

# Step 11: Get Function URL
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 11: Get Function App Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FUNCTION_URL=$(az functionapp function show \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --function-name ProcessSimulationTelemetry \
    --query "invokeUrlTemplate" -o tsv 2>/dev/null || echo "Not available yet")

log_info "Function URL: $FUNCTION_URL"

# Create configuration file
cat > azure_deployment_config.env << EOF
# Azure Deployment Configuration
# Generated: $(date)

# Digital Twins
export AZURE_DIGITAL_TWINS_ENDPOINT=https://$DT_ENDPOINT
export DT_INSTANCE=$DT_INSTANCE

# Function App
export AZURE_FUNCTION_ENDPOINT=$FUNCTION_URL
export FUNCTION_APP=$FUNCTION_APP

# Resource Group
export RESOURCE_GROUP=$RESOURCE_GROUP
export LOCATION=$LOCATION

# For API Integration
export ENABLE_AZURE_INTEGRATION=true
EOF

log_info "Configuration saved to: azure_deployment_config.env"

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                     DEPLOYMENT COMPLETED!                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Resource Group:        $RESOURCE_GROUP"
echo "Location:              $LOCATION"
echo "Digital Twins:         $DT_INSTANCE"
echo "Function App:          $FUNCTION_APP"
echo "Storage Account:       $STORAGE_ACCOUNT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Load configuration:"
echo "   source azure_deployment_config.env"
echo ""
echo "2. Create device twins:"
echo "   python azure_integration/scripts/create_device_twins.py --endpoint https://$DT_ENDPOINT"
echo ""
echo "3. Test the integration:"
echo "   ./test_azure_deployment.sh"
echo ""
echo "4. Run simulation from UI:"
echo "   cd api && uvicorn main:app --reload"
echo "   cd ui && npm run dev"
echo ""
echo "5. Verify in Azure Portal:"
echo "   https://portal.azure.com → Digital Twins Explorer"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
