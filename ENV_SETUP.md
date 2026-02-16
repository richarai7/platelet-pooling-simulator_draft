# Environment Configuration (.env file)

This directory contains environment configuration files for Azure integration.

## Quick Start

### 1. Create .env file

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual Azure endpoints
nano .env  # or use your preferred editor
```

### 2. Update the values in .env

Replace the placeholder values with your actual Azure endpoints:

```bash
ENABLE_AZURE_INTEGRATION=true
AZURE_FUNCTION_ENDPOINT=https://YOUR-ACTUAL-FUNCTION-APP.azurewebsites.net/api/ProcessSimulationTelemetry
AZURE_FUNCTION_KEY=YOUR-ACTUAL-FUNCTION-KEY
AZURE_DIGITAL_TWINS_ENDPOINT=https://YOUR-ACTUAL-INSTANCE.api.eus.digitaltwins.azure.net
```

### 3. Load the environment variables

```bash
# Load variables into current shell
source load_env.sh

# Verify they are loaded
./check_azure_integration.sh
```

### 4. Start the API

```bash
uvicorn api.main:app --reload
```

## Environment Variables Explained

### ENABLE_AZURE_INTEGRATION
- **Required**: Yes
- **Type**: Boolean (true/false)
- **Default**: false
- **Description**: Enables or disables Azure Digital Twins integration
- **Example**: `ENABLE_AZURE_INTEGRATION=true`

### AZURE_FUNCTION_ENDPOINT
- **Required**: Conditional (if using Function App mode)
- **Type**: URL
- **Description**: Azure Function App endpoint for telemetry processing
- **Format**: `https://<function-app>.azurewebsites.net/api/ProcessSimulationTelemetry`
- **Example**: `AZURE_FUNCTION_ENDPOINT=https://platelet-func.azurewebsites.net/api/ProcessSimulationTelemetry`

### AZURE_FUNCTION_KEY
- **Required**: No (optional)
- **Type**: String
- **Description**: Azure Function App authentication key
- **Note**: Can be included in the URL as a query parameter (?code=<key>) instead
- **Example**: `AZURE_FUNCTION_KEY=abc123xyz789...`

### AZURE_DIGITAL_TWINS_ENDPOINT
- **Required**: Conditional (if using direct mode or as fallback)
- **Type**: URL
- **Description**: Azure Digital Twins instance endpoint
- **Format**: `https://<instance-name>.api.<region>.digitaltwins.azure.net`
- **Example**: `AZURE_DIGITAL_TWINS_ENDPOINT=https://platelet-dt.api.eus.digitaltwins.azure.net`

## How It Works

1. The `.env` file contains key=value pairs
2. The `load_env.sh` script reads this file and exports each variable
3. The API code (`api/main.py`) reads these variables using `os.getenv()`
4. Variables control Azure integration behavior

## File Structure

```
.
├── .env                    # Your local configuration (gitignored)
├── .env.example            # Template file (committed to repo)
├── load_env.sh             # Helper script to load .env
└── ENV_SETUP.md            # This file
```

## Security Notes

⚠️ **IMPORTANT**: 
- The `.env` file is listed in `.gitignore` and will NOT be committed to the repository
- Never commit actual Azure credentials or keys to version control
- Use `.env.example` as a template for others
- Keep your `.env` file secure and never share it

## Alternative Methods

If you prefer not to use the .env file, you can:

### 1. Export directly in your shell

```bash
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT="https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="your-key"
export AZURE_DIGITAL_TWINS_ENDPOINT="https://your-instance.api.eus.digitaltwins.azure.net"
```

### 2. Add to your shell profile

Add the export commands to `~/.bashrc` or `~/.zshrc` for persistence.

### 3. Use Docker environment variables

```bash
docker run -e ENABLE_AZURE_INTEGRATION=true \
  -e AZURE_FUNCTION_ENDPOINT="https://..." \
  -e AZURE_FUNCTION_KEY="..." \
  -e AZURE_DIGITAL_TWINS_ENDPOINT="https://..." \
  your-image
```

## Troubleshooting

### Variables not loading

```bash
# Make sure you SOURCE the script (not run it)
source load_env.sh  # ✓ Correct
./load_env.sh       # ✗ Wrong - creates new shell
```

### Check if variables are set

```bash
echo $ENABLE_AZURE_INTEGRATION
echo $AZURE_FUNCTION_ENDPOINT
```

### Azure integration still disabled

```bash
# Use the check script
./check_azure_integration.sh

# Or manually check
python -c "import os; print('Enabled:', os.getenv('ENABLE_AZURE_INTEGRATION', 'false'))"
```

## Getting Azure Endpoints

If you don't have Azure resources yet, see:
- **[LINEAR_FLOW_SETUP.md](LINEAR_FLOW_SETUP.md)** - Complete Azure setup
- **[docs/AZURE_SETUP_GUIDE.md](docs/AZURE_SETUP_GUIDE.md)** - Detailed deployment guide
- **[docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md)** - Permission configuration

## Related Documentation

- [WHY_AZURE_INTEGRATION_DISABLED.md](WHY_AZURE_INTEGRATION_DISABLED.md) - Why Azure is disabled by default
- [README.md](README.md) - Main project documentation
- [check_azure_integration.sh](check_azure_integration.sh) - Status check script
- [configure_function_permissions.sh](configure_function_permissions.sh) - Permission setup
