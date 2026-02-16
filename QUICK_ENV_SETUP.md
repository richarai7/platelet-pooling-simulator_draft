# Quick Reference: Azure Integration Setup

## ⚡ 3-Step Quick Start

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit with your Azure endpoints
nano .env  # Update the placeholder URLs

# 3. Load and verify
source load_env.sh
./check_azure_integration.sh
```

## 📋 What to Put in .env

Replace these placeholder values with your actual Azure endpoints:

```bash
ENABLE_AZURE_INTEGRATION=true

# Get this from Azure Portal → Function App → Overview
AZURE_FUNCTION_ENDPOINT=https://YOUR-FUNCTION-APP.azurewebsites.net/api/ProcessSimulationTelemetry

# Get this from Azure Portal → Function App → Function Keys
AZURE_FUNCTION_KEY=YOUR-FUNCTION-KEY

# Get this from Azure Portal → Digital Twins → Overview → Host name
AZURE_DIGITAL_TWINS_ENDPOINT=https://YOUR-INSTANCE.api.REGION.digitaltwins.azure.net
```

## 🎯 Expected Results

After loading .env, `./check_azure_integration.sh` should show:

```
ENABLE_AZURE_INTEGRATION:      ✓ true (ENABLED)
AZURE_FUNCTION_ENDPOINT:       ✓ Set
AZURE_FUNCTION_KEY:            ✓ Set
AZURE_DIGITAL_TWINS_ENDPOINT:  ✓ Set

✓ Azure Integration: ENABLED
```

## 🔧 Commands

| Action | Command |
|--------|---------|
| Create .env | `cp .env.example .env` |
| Edit .env | `nano .env` |
| Load variables | `source load_env.sh` |
| Check status | `./check_azure_integration.sh` |
| Start API | `uvicorn api.main:app --reload` |
| Run tests | `python smoke_test.py` |

## 📖 Full Documentation

- **[ENV_SETUP.md](ENV_SETUP.md)** - Complete .env guide
- **[WHY_AZURE_INTEGRATION_DISABLED.md](WHY_AZURE_INTEGRATION_DISABLED.md)** - Why it's disabled
- **[docs/FUNCTION_APP_PERMISSIONS.md](docs/FUNCTION_APP_PERMISSIONS.md)** - Setup Azure permissions

## 🚨 Common Issues

### "Azure integration is disabled"
→ Make sure you ran `source load_env.sh` (not just `./load_env.sh`)

### ".env file not found"
→ Run `cp .env.example .env` first

### "Variables not set"
→ Check you're in the same terminal where you ran `source load_env.sh`

## 💡 Pro Tips

- Use `source load_env.sh` every time you open a new terminal
- Add it to your shell startup script for persistence
- Keep `.env` secure - it's gitignored automatically
- Use `.env.example` to share configuration templates
