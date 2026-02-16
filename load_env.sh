#!/bin/bash
# load_env.sh
# Helper script to load environment variables from .env file
#
# Usage:
#   source load_env.sh
#   OR
#   . load_env.sh
#
# This script reads the .env file and exports all variables

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "To create .env file:"
    echo "  1. Copy the example: cp .env.example .env"
    echo "  2. Edit .env with your Azure endpoints"
    echo "  3. Run: source load_env.sh"
    echo ""
    return 1 2>/dev/null || exit 1
fi

# Read and export variables from .env file
echo "📦 Loading environment variables from .env..."
echo ""

# Export variables (skip comments and empty lines)
while IFS= read -r line || [ -n "$line" ]; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        continue
    fi
    
    # Export the variable
    export "$line"
    
    # Extract variable name for display
    var_name="${line%%=*}"
    var_value="${line#*=}"
    
    # Mask sensitive values in output
    if [[ "$var_name" == *"KEY"* ]] || [[ "$var_name" == *"SECRET"* ]]; then
        echo "  ✓ $var_name=***hidden***"
    else
        echo "  ✓ $var_name=$var_value"
    fi
done < .env

echo ""
echo "✅ Environment variables loaded successfully!"
echo ""
echo "Next steps:"
echo "  1. Verify: ./check_azure_integration.sh"
echo "  2. Start API: uvicorn api.main:app --reload"
echo ""
