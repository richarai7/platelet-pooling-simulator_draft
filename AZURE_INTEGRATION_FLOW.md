# Azure Integration Setup Flow

## Visual Guide: Enabling Azure Integration

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 1: Create .env file                                          │
│  ─────────────────────────                                          │
│                                                                     │
│  $ cp .env.example .env                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 2: Edit .env with your Azure endpoints                       │
│  ──────────────────────────────────────────                         │
│                                                                     │
│  $ nano .env                                                        │
│                                                                     │
│  Replace:                                                           │
│    AZURE_FUNCTION_ENDPOINT=https://YOUR-FUNCTION-APP...            │
│    AZURE_FUNCTION_KEY=YOUR-KEY                                     │
│    AZURE_DIGITAL_TWINS_ENDPOINT=https://YOUR-INSTANCE...           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 3: Load environment variables                                │
│  ───────────────────────────────                                    │
│                                                                     │
│  $ source load_env.sh                                              │
│                                                                     │
│  Output:                                                            │
│    ✓ ENABLE_AZURE_INTEGRATION=true                                │
│    ✓ AZURE_FUNCTION_ENDPOINT=https://...                          │
│    ✓ AZURE_FUNCTION_KEY=***hidden***                              │
│    ✓ AZURE_DIGITAL_TWINS_ENDPOINT=https://...                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 4: Verify configuration                                      │
│  ──────────────────────────                                         │
│                                                                     │
│  $ ./check_azure_integration.sh                                    │
│                                                                     │
│  Expected:                                                          │
│    ENABLE_AZURE_INTEGRATION:      ✓ true (ENABLED)                │
│    AZURE_FUNCTION_ENDPOINT:       ✓ Set                           │
│    AZURE_FUNCTION_KEY:            ✓ Set                           │
│    AZURE_DIGITAL_TWINS_ENDPOINT:  ✓ Set                           │
│                                                                     │
│    ✓ Azure Integration: ENABLED                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 5: Start the API                                             │
│  ───────────────────                                                │
│                                                                     │
│  $ uvicorn api.main:app --reload                                   │
│                                                                     │
│  The API will now use Azure integration!                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ✅ DONE!                                                           │
│                                                                     │
│  Your API is now integrated with:                                  │
│    • Azure Digital Twins                                           │
│    • Azure Function App                                            │
│    • Real-time telemetry streaming                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## How the .env File Works

```
┌─────────────┐
│   .env      │  Contains:
│   file      │  ─────────
└─────────────┘  ENABLE_AZURE_INTEGRATION=true
      │          AZURE_FUNCTION_ENDPOINT=https://...
      │          AZURE_FUNCTION_KEY=abc123
      │          AZURE_DIGITAL_TWINS_ENDPOINT=https://...
      │
      ▼
┌─────────────┐
│ load_env.sh │  Reads .env and exports each variable
│   script    │  to current shell environment
└─────────────┘
      │
      ▼
┌─────────────┐
│   Shell     │  Environment variables now available
│ Environment │  to all processes in this shell
└─────────────┘
      │
      ▼
┌─────────────┐
│  API Code   │  Reads variables using os.getenv()
│ (main.py)   │  
└─────────────┘
      │
      ▼
┌─────────────┐
│   Azure     │  API sends telemetry to Azure
│  Services   │  based on configuration
└─────────────┘
```

## File Structure

```
Repository Root
├── .env                        ← Your config (gitignored)
├── .env.example               ← Template (committed)
├── load_env.sh                ← Helper script
├── check_azure_integration.sh ← Status checker
├── ENV_SETUP.md              ← Full guide
├── QUICK_ENV_SETUP.md        ← Quick reference
└── api/
    └── main.py               ← Reads environment variables
```

## Before vs After

### BEFORE (Azure Disabled)

```bash
$ ./check_azure_integration.sh

ENABLE_AZURE_INTEGRATION:      ✗ false (DISABLED)
AZURE_FUNCTION_ENDPOINT:       ✗ Not set
AZURE_FUNCTION_KEY:            ⚠ Not set (optional)
AZURE_DIGITAL_TWINS_ENDPOINT:  ⚠ Not set

ℹ Azure Integration: DISABLED
```

### AFTER (Azure Enabled)

```bash
$ source load_env.sh
$ ./check_azure_integration.sh

ENABLE_AZURE_INTEGRATION:      ✓ true (ENABLED)
AZURE_FUNCTION_ENDPOINT:       ✓ Set
AZURE_FUNCTION_KEY:            ✓ Set
AZURE_DIGITAL_TWINS_ENDPOINT:  ✓ Set

✓ Azure Integration: ENABLED
```

## Quick Commands Reference

```bash
# First time setup
cp .env.example .env
nano .env                        # Edit with your values
source load_env.sh              # Load variables
./check_azure_integration.sh    # Verify

# Every new terminal session
source load_env.sh              # Reload variables

# Start the API
uvicorn api.main:app --reload

# Run tests
python smoke_test.py
```

## Related Documentation

- **[QUICK_ENV_SETUP.md](QUICK_ENV_SETUP.md)** - Quick reference card
- **[ENV_SETUP.md](ENV_SETUP.md)** - Complete configuration guide
- **[WHY_AZURE_INTEGRATION_DISABLED.md](WHY_AZURE_INTEGRATION_DISABLED.md)** - Background info
- **[README.md](README.md)** - Main documentation
