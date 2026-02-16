#!/bin/bash
# check_azure_integration.sh
#
# Quick script to check Azure integration status and provide guidance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Azure Integration Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check environment variables
ENABLE_AZURE=${ENABLE_AZURE_INTEGRATION:-false}
FUNCTION_ENDPOINT=${AZURE_FUNCTION_ENDPOINT:-}
FUNCTION_KEY=${AZURE_FUNCTION_KEY:-}
DT_ENDPOINT=${AZURE_DIGITAL_TWINS_ENDPOINT:-}

# Determine if integration is enabled
if [[ "${ENABLE_AZURE,,}" == "true" ]] || [[ "${ENABLE_AZURE}" == "1" ]] || [[ "${ENABLE_AZURE,,}" == "yes" ]] || [[ "${ENABLE_AZURE,,}" == "on" ]]; then
    INTEGRATION_ENABLED=true
else
    INTEGRATION_ENABLED=false
fi

# Status display
echo "Environment Variables:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$INTEGRATION_ENABLED" = true ]; then
    echo -e "ENABLE_AZURE_INTEGRATION:      ${GREEN}✓ true (ENABLED)${NC}"
else
    echo -e "ENABLE_AZURE_INTEGRATION:      ${RED}✗ ${ENABLE_AZURE:-not set} (DISABLED)${NC}"
fi

if [ -n "$FUNCTION_ENDPOINT" ]; then
    echo -e "AZURE_FUNCTION_ENDPOINT:       ${GREEN}✓ Set${NC}"
    echo "   ${FUNCTION_ENDPOINT:0:50}..."
else
    echo -e "AZURE_FUNCTION_ENDPOINT:       ${RED}✗ Not set${NC}"
fi

if [ -n "$FUNCTION_KEY" ]; then
    echo -e "AZURE_FUNCTION_KEY:            ${GREEN}✓ Set${NC}"
    echo "   ${FUNCTION_KEY:0:20}..."
else
    echo -e "AZURE_FUNCTION_KEY:            ${YELLOW}⚠ Not set (optional)${NC}"
fi

if [ -n "$DT_ENDPOINT" ]; then
    echo -e "AZURE_DIGITAL_TWINS_ENDPOINT:  ${GREEN}✓ Set${NC}"
    echo "   ${DT_ENDPOINT:0:50}..."
else
    echo -e "AZURE_DIGITAL_TWINS_ENDPOINT:  ${YELLOW}⚠ Not set${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Status Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$INTEGRATION_ENABLED" = true ]; then
    echo -e "${GREEN}✓ Azure Integration: ENABLED${NC}"
    echo ""
    echo "What this means:"
    echo "  • Simulations will send telemetry to Azure"
    echo "  • Digital Twins will be updated in real-time"
    echo "  • Azure resources are required"
    echo ""
    
    if [ -z "$FUNCTION_ENDPOINT" ] && [ -z "$DT_ENDPOINT" ]; then
        echo -e "${RED}⚠ WARNING: No Azure endpoints configured!${NC}"
        echo "  Set at least one of:"
        echo "    - AZURE_FUNCTION_ENDPOINT (for Function App mode)"
        echo "    - AZURE_DIGITAL_TWINS_ENDPOINT (for direct mode)"
    fi
else
    echo -e "${YELLOW}ℹ Azure Integration: DISABLED${NC}"
    echo ""
    echo "What this means:"
    echo "  • Simulations run normally (no Azure required)"
    echo "  • No telemetry sent to Azure"
    echo "  • No Digital Twins updates"
    echo "  • No Azure costs incurred"
    echo ""
    echo "This is the default for local development."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$INTEGRATION_ENABLED" = false ]; then
    echo "How to Enable Azure Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Option 1: Set environment variables in current session"
    echo ""
    echo -e "${BLUE}export ENABLE_AZURE_INTEGRATION=true${NC}"
    echo -e "${BLUE}export AZURE_FUNCTION_ENDPOINT=\"https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry\"${NC}"
    echo -e "${BLUE}export AZURE_FUNCTION_KEY=\"your-key\"  # optional${NC}"
    echo ""
    echo "Then restart the API:"
    echo -e "${BLUE}uvicorn api.main:app --reload${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Option 2: Create .env file"
    echo ""
    echo "Create a file named '.env' with:"
    echo ""
    echo -e "${BLUE}cat > .env << 'EOF'"
    echo "ENABLE_AZURE_INTEGRATION=true"
    echo "AZURE_FUNCTION_ENDPOINT=https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry"
    echo "AZURE_FUNCTION_KEY=your-key"
    echo "EOF"
    echo ""
    echo "source .env"
    echo -e "uvicorn api.main:app --reload${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Option 3: Add to shell profile (permanent)"
    echo ""
    echo -e "${BLUE}echo 'export ENABLE_AZURE_INTEGRATION=true' >> ~/.bashrc${NC}"
    echo -e "${BLUE}source ~/.bashrc${NC}"
    echo ""
else
    echo "Additional Checks & Validation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Run these commands to validate your setup:"
    echo ""
    echo "1. Check API diagnostics endpoint:"
    echo -e "   ${BLUE}curl http://localhost:8000/azure/diagnostics | jq${NC}"
    echo ""
    echo "2. Run smoke test:"
    echo -e "   ${BLUE}python smoke_test.py --skip-simulation${NC}"
    echo ""
    echo "3. Configure Function App permissions (if not done):"
    echo -e "   ${BLUE}./configure_function_permissions.sh <resource-group> <function-app> <dt-instance>${NC}"
    echo ""
    echo "4. Create device twins (if not done):"
    echo -e "   ${BLUE}python azure_integration/scripts/create_linear_flow_twins.py --endpoint \$AZURE_DIGITAL_TWINS_ENDPOINT${NC}"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "For More Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "See these documentation files:"
echo "  • WHY_AZURE_INTEGRATION_DISABLED.md - Complete explanation"
echo "  • README.md - E2E setup guide"
echo "  • docs/FUNCTION_APP_PERMISSIONS.md - Troubleshooting"
echo "  • LINEAR_FLOW_SETUP.md - Azure setup guide"
echo ""
