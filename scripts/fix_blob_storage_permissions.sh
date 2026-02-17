#!/bin/bash
# Fix Azure Blob Storage Permissions for 3D Model Access
# This script resolves 403 errors when accessing GLTF models from blob storage

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║       Fix Azure Blob Storage Permissions - 3D Model Access              ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
STORAGE_ACCOUNT="plateletmodels"
CONTAINER_NAME="models"
BLOB_NAME="platelet_lab.gltf"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}▶${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    log_error "Azure CLI is not installed. Please install it first."
    echo "   Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
log_step "Checking Azure login status..."
if ! az account show &>/dev/null; then
    log_warn "Not logged in to Azure. Please log in..."
    az login
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
log_info "Using subscription: $SUBSCRIPTION"
echo ""

# Step 1: Get Resource Group
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Finding Storage Account Resource Group"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESOURCE_GROUP=$(az storage account show \
  --name $STORAGE_ACCOUNT \
  --query resourceGroup -o tsv 2>/dev/null || echo "")

if [ -z "$RESOURCE_GROUP" ]; then
    log_error "Storage account '$STORAGE_ACCOUNT' not found!"
    echo ""
    echo "Please create the storage account first:"
    echo "  az storage account create \\"
    echo "    --name $STORAGE_ACCOUNT \\"
    echo "    --resource-group <your-resource-group> \\"
    echo "    --location eastus \\"
    echo "    --sku Standard_LRS"
    exit 1
fi

log_info "Found storage account in resource group: $RESOURCE_GROUP"
echo ""

# Step 2: Enable Blob Public Access
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Enable Anonymous Blob Access on Storage Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CURRENT_SETTING=$(az storage account show \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query allowBlobPublicAccess -o tsv)

if [ "$CURRENT_SETTING" = "false" ]; then
    log_warn "Blob public access is currently disabled"
    log_step "Enabling blob public access..."

    az storage account update \
      --name $STORAGE_ACCOUNT \
      --resource-group $RESOURCE_GROUP \
      --allow-blob-public-access true

    log_info "Blob public access enabled"
else
    log_info "Blob public access already enabled"
fi
echo ""

# Step 3: Set Container Public Access Level
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Set Container Public Access Level"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if container exists
CONTAINER_EXISTS=$(az storage container exists \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --auth-mode login \
  --query exists -o tsv 2>/dev/null || echo "false")

if [ "$CONTAINER_EXISTS" != "true" ]; then
    log_warn "Container '$CONTAINER_NAME' does not exist. Creating..."

    az storage container create \
      --name $CONTAINER_NAME \
      --account-name $STORAGE_ACCOUNT \
      --public-access blob \
      --auth-mode login

    log_info "Container created with public blob access"
else
    log_info "Container exists"

    # Update container permissions
    log_step "Setting container public access level to 'blob'..."

    az storage container set-permission \
      --name $CONTAINER_NAME \
      --account-name $STORAGE_ACCOUNT \
      --public-access blob \
      --auth-mode login

    log_info "Container permissions updated"
fi
echo ""

# Step 4: Verify Settings
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Verify Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify account-level setting
ACCOUNT_PUBLIC_ACCESS=$(az storage account show \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query allowBlobPublicAccess -o tsv)

echo "Storage Account Public Access: $ACCOUNT_PUBLIC_ACCESS"

# Verify container-level setting
CONTAINER_PUBLIC_ACCESS=$(az storage container show \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --auth-mode login \
  --query properties.publicAccess -o tsv)

echo "Container Public Access Level: $CONTAINER_PUBLIC_ACCESS"
echo ""

if [ "$ACCOUNT_PUBLIC_ACCESS" = "true" ] && [ "$CONTAINER_PUBLIC_ACCESS" = "blob" ]; then
    log_info "Configuration verified successfully!"
else
    log_error "Configuration may not be correct. Please check manually."
fi
echo ""

# Step 5: Check if blob exists and test access
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Test Blob Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BLOB_URL="https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER_NAME}/${BLOB_NAME}"

# Check if blob exists
BLOB_EXISTS=$(az storage blob exists \
  --account-name $STORAGE_ACCOUNT \
  --container-name $CONTAINER_NAME \
  --name $BLOB_NAME \
  --auth-mode login \
  --query exists -o tsv 2>/dev/null || echo "false")

if [ "$BLOB_EXISTS" != "true" ]; then
    log_warn "Blob '$BLOB_NAME' not found in container"
    echo ""
    echo "To upload the 3D model, run:"
    echo "  az storage blob upload \\"
    echo "    --account-name $STORAGE_ACCOUNT \\"
    echo "    --container-name $CONTAINER_NAME \\"
    echo "    --name $BLOB_NAME \\"
    echo "    --file 3d_models/templates/platelet_lab_template.gltf \\"
    echo "    --auth-mode login"
    echo ""
else
    log_info "Blob '$BLOB_NAME' exists"
    echo ""

    # Test public access
    log_step "Testing public access (this may take a few seconds for permissions to propagate)..."
    sleep 3

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BLOB_URL")

    if [ "$HTTP_CODE" = "200" ]; then
        log_info "✓ SUCCESS! Blob is publicly accessible"
        echo ""
        echo "URL: $BLOB_URL"
        echo ""
        echo "You can now use this URL in:"
        echo "  - Azure 3D Scenes Studio"
        echo "  - Your React application"
        echo "  - Any web browser"
    else
        log_error "Public access test failed (HTTP $HTTP_CODE)"
        echo ""
        if [ "$HTTP_CODE" = "403" ]; then
            log_warn "Still getting 403. This could be due to:"
            echo "  1. Permission propagation delay (wait 30-60 seconds and try again)"
            echo "  2. Storage account firewall rules"
            echo "  3. Network policies blocking access"
            echo ""
            echo "Wait a minute and test manually:"
            echo "  curl -I $BLOB_URL"
        fi
    fi
fi
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                            SUMMARY                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  Storage Account:    $STORAGE_ACCOUNT"
echo "  Resource Group:     $RESOURCE_GROUP"
echo "  Container:          $CONTAINER_NAME"
echo "  Blob Name:          $BLOB_NAME"
echo ""
echo "Public Access:"
echo "  Account Level:      $ACCOUNT_PUBLIC_ACCESS"
echo "  Container Level:    $CONTAINER_PUBLIC_ACCESS"
echo ""
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$BLOB_EXISTS" != "true" ]; then
    echo "1. Upload your 3D model (see command above)"
    echo "2. Test access: curl -I $BLOB_URL"
    echo "3. Use the URL in 3D Scenes Studio"
else
    echo "1. Test in browser: $BLOB_URL"
    echo "2. Reload Azure 3D Scenes Studio"
    echo "3. Load model using the URL above"
    echo "4. Clear browser cache if still seeing errors"
fi
echo ""
echo "For troubleshooting, see: docs/FIX_BLOB_STORAGE_403.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
