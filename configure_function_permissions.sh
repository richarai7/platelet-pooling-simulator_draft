#!/bin/bash
# configure_function_permissions.sh
#
# HIGH PRIORITY: Automatically configure Function App → Azure Digital Twins permissions
# This script addresses the most common blocker for E2E flow.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables - can be overridden by environment or command line args
RESOURCE_GROUP="${1:-${RESOURCE_GROUP}}"
FUNCTION_APP="${2:-${FUNCTION_APP}}"
DT_INSTANCE="${3:-${DT_INSTANCE}}"

# Check if variables are set
if [ -z "$RESOURCE_GROUP" ] || [ -z "$FUNCTION_APP" ] || [ -z "$DT_INSTANCE" ]; then
    echo -e "${RED}❌ Error: Missing required parameters${NC}"
    echo ""
    echo "Usage: $0 <resource-group> <function-app> <dt-instance>"
    echo ""
    echo "Or set environment variables:"
    echo "  export RESOURCE_GROUP='your-rg'"
    echo "  export FUNCTION_APP='your-function-app'"
    echo "  export DT_INSTANCE='your-dt-instance'"
    echo "  $0"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Function App → Azure Digital Twins Permission Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Resource Group:   $RESOURCE_GROUP"
echo "Function App:     $FUNCTION_APP"
echo "Digital Twins:    $DT_INSTANCE"
echo ""

# Step 1: Enable Managed Identity
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Enabling System-Assigned Managed Identity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if identity already exists
EXISTING_IDENTITY=$(az functionapp identity show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_IDENTITY" ]; then
    echo -e "${GREEN}✓${NC} Managed Identity already enabled"
    PRINCIPAL_ID=$EXISTING_IDENTITY
else
    echo "Enabling Managed Identity..."
    az functionapp identity assign \
      --name $FUNCTION_APP \
      --resource-group $RESOURCE_GROUP
    
    PRINCIPAL_ID=$(az functionapp identity show \
      --name $FUNCTION_APP \
      --resource-group $RESOURCE_GROUP \
      --query principalId -o tsv)
    
    echo -e "${GREEN}✓${NC} Managed Identity enabled"
fi

echo "   Principal ID: $PRINCIPAL_ID"
echo ""

# Step 2: Assign Azure Digital Twins Role
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Assigning Azure Digital Twins Data Owner Role"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if role assignment already exists
EXISTING_ROLE=$(az dt role-assignment list \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --query "[?principalId=='$PRINCIPAL_ID'].roleDefinitionName" -o tsv 2>/dev/null || echo "")

if echo "$EXISTING_ROLE" | grep -q "Azure Digital Twins Data Owner"; then
    echo -e "${GREEN}✓${NC} Role assignment already exists"
else
    echo "Assigning role..."
    az dt role-assignment create \
      --dt-name $DT_INSTANCE \
      --assignee $PRINCIPAL_ID \
      --role "Azure Digital Twins Data Owner"
    
    echo -e "${GREEN}✓${NC} Role assigned: Azure Digital Twins Data Owner"
fi
echo ""

# Step 3: Configure Endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Configuring Azure Digital Twins Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DT_ENDPOINT=$(az dt show \
  --dt-name $DT_INSTANCE \
  --resource-group $RESOURCE_GROUP \
  --query "hostName" -o tsv)

FULL_ENDPOINT="https://$DT_ENDPOINT"
echo "   Endpoint: $FULL_ENDPOINT"

# Set environment variable
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings AZURE_DIGITAL_TWINS_ENDPOINT="$FULL_ENDPOINT" \
  --output none

echo -e "${GREEN}✓${NC} Endpoint configured in Function App settings"
echo ""

# Step 4: Verify Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Function App state
FUNCTION_STATE=$(az functionapp show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "state" -o tsv)

echo "   Function App State: $FUNCTION_STATE"

# Verify endpoint setting
CONFIGURED_ENDPOINT=$(az functionapp config appsettings list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='AZURE_DIGITAL_TWINS_ENDPOINT'].value" -o tsv)

if [ "$CONFIGURED_ENDPOINT" = "$FULL_ENDPOINT" ]; then
    echo -e "   ${GREEN}✓${NC} Endpoint setting verified"
else
    echo -e "   ${YELLOW}⚠${NC}  Endpoint mismatch detected"
    echo "      Expected: $FULL_ENDPOINT"
    echo "      Found:    $CONFIGURED_ENDPOINT"
fi

# Count twins in ADT
TWIN_COUNT=$(az dt twin query \
  --dt-name $DT_INSTANCE \
  --query-command 'SELECT COUNT() FROM DIGITALTWINS' \
  --query 'result[0].$count' -o tsv 2>/dev/null || echo "0")

echo "   Twins in ADT: $TWIN_COUNT"

if [ "$TWIN_COUNT" = "0" ]; then
    echo -e "   ${YELLOW}⚠${NC}  No twins found - you may need to create them"
    echo "      Run: python azure_integration/scripts/create_linear_flow_twins.py --endpoint $FULL_ENDPOINT"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Configuration Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration Summary:"
echo "  ✓ Managed Identity: $PRINCIPAL_ID"
echo "  ✓ Role: Azure Digital Twins Data Owner"
echo "  ✓ Endpoint: $FULL_ENDPOINT"
echo "  ✓ Function State: $FUNCTION_STATE"
echo ""
echo "Next steps:"
echo ""
echo "1. Wait for Function App to restart (may take 1-2 minutes)"
echo ""
echo "2. Test the connection:"
echo "   Run: python test_end_to_end_flow.py"
echo ""
echo "3. If issues persist, check logs:"
echo "   az webapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP"
echo ""
echo "4. Create twins if needed:"
echo "   python azure_integration/scripts/create_linear_flow_twins.py \\"
echo "     --endpoint $FULL_ENDPOINT"
echo ""
echo "For detailed troubleshooting, see: docs/FUNCTION_APP_PERMISSIONS.md"
echo ""
