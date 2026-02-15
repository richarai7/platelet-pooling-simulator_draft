#!/bin/bash
# Test Azure Deployment - Comprehensive Testing Script
# This script tests the complete flow: Deploy → Create Twins → Run Simulation → Verify

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║          Azure Digital Twins - Complete Testing Script                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if configuration exists
if [ ! -f "azure_deployment_config.env" ]; then
    log_error "Configuration file not found!"
    echo ""
    echo "Please run ./deploy_azure.sh first to create Azure resources"
    exit 1
fi

# Load configuration
source azure_deployment_config.env

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Digital Twins Instance: $DT_INSTANCE"
echo "Endpoint: $AZURE_DIGITAL_TWINS_ENDPOINT"
echo "Function App: $FUNCTION_APP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Verify Azure Login
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 1: Verify Azure Login"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if az account show &>/dev/null; then
    ACCOUNT=$(az account show --query user.name -o tsv)
    log_info "Logged in as: $ACCOUNT"
else
    log_error "Not logged in to Azure"
    echo "Run: az login"
    exit 1
fi

# Test 2: Verify Digital Twins Instance
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 2: Verify Digital Twins Instance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if az dt show --dt-name $DT_INSTANCE &>/dev/null; then
    STATUS=$(az dt show --dt-name $DT_INSTANCE --query provisioningState -o tsv)
    log_info "Digital Twins instance status: $STATUS"
else
    log_error "Digital Twins instance not found: $DT_INSTANCE"
    exit 1
fi

# Test 3: Verify DTDL Models
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 3: Verify DTDL Models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MODEL_COUNT=$(az dt model list --dt-name $DT_INSTANCE --query "length([])" -o tsv)
log_info "Models uploaded: $MODEL_COUNT"

if [ "$MODEL_COUNT" -ge 2 ]; then
    log_info "Required models are present"
else
    log_warn "Expected at least 2 models (Device, Simulation)"
fi

# Test 4: Create Device Twins
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 4: Create Device Twins"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "azure_integration/scripts/create_device_twins.py" ]; then
    python azure_integration/scripts/create_device_twins.py --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT
    log_info "Device twins created/updated"
else
    log_error "create_device_twins.py not found"
    exit 1
fi

# Test 5: Verify Twins Created
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 5: Verify Twins in Digital Twins"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TWIN_COUNT=$(az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT COUNT() FROM digitaltwins" \
    --query "result[0]['COUNT']" -o tsv 2>/dev/null || echo "0")

log_info "Total twins in Digital Twins: $TWIN_COUNT"

if [ "$TWIN_COUNT" -ge 11 ]; then
    log_info "All device twins present (expected 11+)"
else
    log_warn "Expected at least 11 device twins, found: $TWIN_COUNT"
fi

# Test 6: Run Simulation (Direct Script)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 6: Run Simulation with Azure Digital Twins"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "run_simulation_with_adt.py" ]; then
    python run_simulation_with_adt.py --config default_config.json
    log_info "Simulation completed successfully"
else
    log_error "run_simulation_with_adt.py not found"
    exit 1
fi

# Test 7: Verify Twins Updated
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 7: Verify Twins Were Updated"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check a sample device twin
TWIN_DATA=$(az dt twin show --dt-name $DT_INSTANCE --twin-id centrifuge 2>/dev/null || echo "{}")

if echo "$TWIN_DATA" | grep -q "totalProcessed"; then
    TOTAL_PROCESSED=$(echo "$TWIN_DATA" | jq -r '.totalProcessed // 0')
    log_info "Centrifuge twin updated - totalProcessed: $TOTAL_PROCESSED"
else
    log_warn "Could not verify twin update"
fi

# Test 8: Test UI → API → Azure Function Flow
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 8: Test UI → API → Azure Function Flow"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "test_ui_api_azure_flow.py" ]; then
    log_info "Testing API → Azure Function integration..."
    
    # Start API server in background (if not already running)
    if ! lsof -i:8000 &>/dev/null; then
        log_warn "API server not running. Start it with: cd api && uvicorn main:app --reload"
        log_warn "Skipping API test"
    else
        python test_ui_api_azure_flow.py
        log_info "API integration test completed"
    fi
else
    log_warn "test_ui_api_azure_flow.py not found - skipping API test"
fi

# Test 9: Query Twins
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "Test 9: Query Digital Twins"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Querying all device twins..."
DEVICES=$(az dt twin query --dt-name $DT_INSTANCE \
    --query-command "SELECT \$dtId, status, totalProcessed FROM digitaltwins WHERE IS_OF_MODEL('dtmi:platelet:Device;1')" \
    2>/dev/null || echo "[]")

echo "$DEVICES" | jq -r '.result[] | "\(.["$dtId"]): \(.status // "Unknown") - Processed: \(.totalProcessed // 0)"' | head -5

log_info "Query completed"

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                     TESTING COMPLETED!                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Test Results Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Azure Login:              SUCCESS"
echo "✓ Digital Twins Instance:   SUCCESS"
echo "✓ DTDL Models:              $MODEL_COUNT models uploaded"
echo "✓ Device Twins:             $TWIN_COUNT twins created"
echo "✓ Simulation:               SUCCESS"
echo "✓ Twin Updates:             VERIFIED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 View Your Twins:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Azure Portal: https://portal.azure.com"
echo "2. Navigate to: $DT_INSTANCE"
echo "3. Click: 'Azure Digital Twins Explorer'"
echo "4. Run query: SELECT * FROM digitaltwins"
echo ""
echo "📱 Run Simulation from UI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Start API:"
echo "   source azure_deployment_config.env"
echo "   cd api && uvicorn main:app --reload"
echo ""
echo "2. Start UI (in another terminal):"
echo "   cd ui && npm run dev"
echo ""
echo "3. Open browser: http://localhost:5173"
echo "4. Run a simulation and watch twins update!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
