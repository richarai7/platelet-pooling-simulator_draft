# Azure Digital Twins End-to-End Integration

## 🎯 Overview

This implementation provides a **complete end-to-end solution** for streaming platelet pooling simulation telemetry to Azure Digital Twins in real-time. You can visualize live device states, track process flows, and analyze historical data - all synchronized with your simulation.

## ✨ Key Features

- ✅ **Real-time Telemetry Streaming** - Device states update in Azure as simulation runs
- ✅ **DTDL v3 Compliant Models** - Industry-standard digital twin definitions
- ✅ **Batching & Throttling** - Intelligent buffering to respect Azure service limits
- ✅ **Mock Mode** - Test locally without Azure subscription
- ✅ **Azure Function Integration** - Serverless telemetry processing
- ✅ **Async/Await** - High-performance streaming with Python asyncio
- ✅ **12 Physical Device Twins** - Pre-configured lab equipment models
- ✅ **Historical Data Ready** - ADX integration prepared
- ✅ **3D Visualization Ready** - Compatible with Azure 3D Scenes Studio

## 🚀 Quick Start (No Azure Required)

Test the integration locally in mock mode:

```bash
# 1. Install the project
pip install -e .

# 2. Run mock mode test (no Azure subscription needed)
python examples/test_simple_mock.py
```

**Expected Output:**
```
======================================================================
TESTING AZURE DIGITAL TWINS INTEGRATION - MOCK MODE
======================================================================

1. Initializing Digital Twins client (MOCK mode)...
   ✓ Client initialized

2. Initializing telemetry streamer...
   ✓ Streamer initialized

3. Starting auto-flush...
   ✓ Auto-flush started

4. Streaming telemetry updates...
   ✓ Sent centrifuge-01 update
   ✓ Sent separator-01 update
   ✓ Sent simulation update

✅ TEST COMPLETED SUCCESSFULLY!
```

## 📋 Prerequisites

### For Mock Mode (Local Testing)
- Python 3.9+
- No Azure subscription required

### For Production Deployment
- Azure subscription
- Azure CLI installed (`az --version`)
- Python 3.9+
- Azure Digital Twins instance (can create in 5 minutes)

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    SIMULATION LAYER                               │
├──────────────────────────────────────────────────────────────────┤
│  Simulation Engine (Python/SimPy)                                │
│  • Discrete Event Simulation                                      │
│  • 4-State Device Model (Idle/Processing/Blocked/Failed)         │
│  • Process Flow Dependencies                                      │
└───────────────┬──────────────────────────────────────────────────┘
                │ Telemetry Events
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                  INGESTION LAYER                                  │
├──────────────────────────────────────────────────────────────────┤
│  Telemetry Streamer                                               │
│  • Batching (10 updates/batch)                                    │
│  • Buffering (FIFO queue)                                         │
│  • Rate Limiting (50 updates/sec)                                 │
│  • Auto-flush (every 1 second)                                    │
└───────────────┬──────────────────────────────────────────────────┘
                │ HTTP/REST
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                  TRANSLATION LAYER (Optional)                     │
├──────────────────────────────────────────────────────────────────┤
│  Azure Function App                                               │
│  • HTTP Trigger                                                    │
│  • Batch Processing                                                │
│  • JSON Patch Updates                                              │
│  • Managed Identity Auth                                           │
└───────────────┬──────────────────────────────────────────────────┘
                │ Azure SDK
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                  DIGITAL CORE                                     │
├──────────────────────────────────────────────────────────────────┤
│  Azure Digital Twins                                              │
│  • Live Twin Graph (12 devices)                                   │
│  • DTDL v3 Models                                                  │
│  • Relationships                                                   │
│  • Telemetry Events                                                │
└───┬────────────────┬───────────────────┬─────────────────────────┘
    │                │                   │
    ▼                ▼                   ▼
┌──────────┐  ┌─────────────┐  ┌───────────────────┐
│ 3D Scenes│  │   SignalR   │  │  Azure Data       │
│ Studio   │  │   (Live UI) │  │  Explorer (ADX)   │
│ (Visual) │  │             │  │  (Historical)     │
└──────────┘  └─────────────┘  └───────────────────┘
```

## 📦 What's Included

### 1. Azure Integration Module (`azure_integration/`)

**Digital Twins Client** (`digital_twins_client.py`)
- Async Python client for Azure Digital Twins
- Automatic batching and buffering
- Retry logic with exponential backoff
- Mock mode for local development
- 266 lines of production-ready code

**Telemetry Streamer** (`telemetry_streamer.py`)
- Real-time telemetry streaming
- FIFO buffer management
- Auto-flush background task
- Rate limiting to prevent throttling
- Callback support for WebSocket integration
- 320 lines of code

**DTDL Models** (`dtdl_models/`)
- `Device.json` - Physical device model (centrifuge, separator, etc.)
- `ProcessFlow.json` - Process flow/batch tracking
- `Simulation.json` - Simulation run metadata
- All DTDL v3 compliant
- Includes telemetry events and relationships

**Helper Scripts** (`scripts/`)
- `create_device_twins.py` - Initialize 12 device twins in Azure
- Configurable device definitions
- Batch creation with error handling

### 2. Azure Function App (`azure_functions/`)

**ProcessSimulationTelemetry Function**
- HTTP-triggered serverless function
- Receives batched telemetry from simulation
- Updates Digital Twins using JSON Patch
- Error handling and logging
- Multi-status response codes (200/207/400/500)

**Configuration Files**
- `function.json` - Function trigger configuration
- `host.json` - Function app settings
- `requirements.txt` - Dependencies
- `local.settings.json` - Local development settings

### 3. Documentation (`docs/`)

**AZURE_SETUP_GUIDE.md** (15KB)
- Step-by-step deployment instructions
- Azure CLI commands for all resources
- Troubleshooting section
- Performance optimization tips
- Cost estimation ($6-325/month)
- Security best practices

**README.md** (this file + integration README)
- Quick start guide
- API examples
- Testing instructions
- Architecture diagrams

### 4. Examples (`examples/`)

**test_simple_mock.py**
- Simple mock mode test
- No Azure required
- Tests all components
- 120 lines

**test_azure_integration.py**
- Full end-to-end integration test
- Works with real Azure or mock mode
- Demonstrates complete flow
- 340+ lines

**create_device_twins.py**
- Helper script to initialize twins
- Configurable device definitions
- Default 12-device lab setup

## 🎮 How to Use

### Option 1: Local Development (Mock Mode)

Perfect for development and testing without Azure costs:

```bash
# Set mock endpoint
export AZURE_DIGITAL_TWINS_ENDPOINT="mock://localhost"

# Run simple test
python examples/test_simple_mock.py

# Expected: All operations logged, no Azure calls made
```

### Option 2: Direct Connection to Azure Digital Twins

Best for simple setups and development:

```bash
# 1. Set your Azure Digital Twins endpoint
export AZURE_DIGITAL_TWINS_ENDPOINT="https://your-instance.api.eus.digitaltwins.azure.net"

# 2. Login to Azure
az login

# 3. Run integration test
python examples/test_azure_integration.py --mode direct
```

### Option 3: Via Azure Function App (Production)

Best for production deployments with isolation:

```bash
# 1. Set Function App endpoint
export AZURE_FUNCTION_ENDPOINT="https://your-function.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="your-function-key"

# 2. Run integration test
python examples/test_azure_integration.py --mode function
```

### Option 4: Integrate into Your Code

```python
import asyncio
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
from azure_integration.telemetry_streamer import TelemetryStreamer

async def run_simulation_with_adt():
    # Initialize clients
    dt_client = DigitalTwinsClientWrapper(
        adt_endpoint="https://your-instance.api.eus.digitaltwins.azure.net"
    )
    
    streamer = TelemetryStreamer(dt_client)
    await streamer.start_auto_flush()
    
    # Stream telemetry during simulation
    await streamer.stream_device_update(
        device_id="centrifuge-01",
        status="Processing",
        in_use=2,
        capacity=2,
        queue_length=3
    )
    
    # Cleanup
    await streamer.stop_auto_flush()
    dt_client.close()

asyncio.run(run_simulation_with_adt())
```

## 🔧 Installation

### Minimal Install (Local Testing Only)

```bash
# Clone and install
git clone <repository-url>
cd platelet-pooling-simulator_draft
pip install -e .

# Test in mock mode (no Azure required)
python examples/test_simple_mock.py
```

### Full Install (With Azure Support)

```bash
# Install with Azure dependencies
pip install -e .
pip install -r requirements-azure.txt

# Verify Azure CLI
az --version

# Login to Azure
az login
```

## 📚 Deployment Guide

See **[docs/AZURE_SETUP_GUIDE.md](docs/AZURE_SETUP_GUIDE.md)** for complete deployment instructions.

**Quick summary:**

```bash
# 1. Create Azure Digital Twins instance
az dt create --dt-name platelet-dt --resource-group my-rg --location eastus

# 2. Upload DTDL models
az dt model create --dt-name platelet-dt --models azure_integration/dtdl_models/*.json

# 3. Create device twins
python azure_integration/scripts/create_device_twins.py \
  --endpoint https://platelet-dt.api.eus.digitaltwins.azure.net

# 4. Deploy Function App (optional)
cd azure_functions
func azure functionapp publish my-function-app

# 5. Run simulation with telemetry
export AZURE_DIGITAL_TWINS_ENDPOINT="https://platelet-dt.api.eus.digitaltwins.azure.net"
python examples/test_azure_integration.py
```

## 🧪 Testing

### Run All Tests

```bash
# Mock mode test (fast, no Azure needed)
python examples/test_simple_mock.py

# Full integration test (requires Azure)
export AZURE_DIGITAL_TWINS_ENDPOINT="<your-adt-url>"
python examples/test_azure_integration.py
```

### Verify in Azure Portal

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to your Digital Twins instance
3. Click "Azure Digital Twins Explorer"
4. Run query:
   ```sql
   SELECT * FROM digitaltwins
   WHERE $dtId IN ['centrifuge-01', 'separator-01']
   ```
5. You should see updated device twins with real-time properties

## 📊 Performance & Scalability

### Throughput

| Mode | Updates/Second | Latency | Notes |
|------|---------------|---------|-------|
| Direct | 50 | < 100ms | ADT rate limit |
| Function App | 100 | < 500ms | With batching |
| Event Hub | 1000+ | < 1s | High throughput |

### Optimization Settings

For high-speed simulations (36 hours in < 2 minutes):

```python
streamer = TelemetryStreamer(
    dt_client,
    batch_size=50,           # Larger batches
    batch_interval_seconds=0.5,  # Faster flush
    rate_limit_per_second=100     # Higher rate
)
```

## 💰 Cost Estimation

### Development/POC
- **Mock Mode (Local)**: $0/month
- **Azure Digital Twins**: ~$5-10/month
- **Function App (Consumption)**: ~$0-5/month
- **Storage**: ~$1/month
- **Total**: **~$6-16/month**

### Production
- **Azure Digital Twins**: ~$20-50/month
- **Function App (Premium)**: ~$150/month
- **ADX (Dev cluster)**: ~$75/month
- **SignalR (Standard)**: ~$50/month
- **Total**: **~$295-325/month**

## 🔒 Security

- ✅ Managed Identity authentication (no credentials in code)
- ✅ Azure RBAC for access control
- ✅ HTTPS/TLS for all communications
- ✅ Mock mode for secure local development
- ✅ No secrets in source control

## 🐛 Troubleshooting

### "Azure SDK not installed"
```bash
pip install azure-identity azure-digitaltwins-core
```

### "Authentication failed"
```bash
# Login to Azure
az login

# Grant your user permissions
az dt role-assignment create \
  --dt-name <your-instance> \
  --assignee <your-email> \
  --role "Azure Digital Twins Data Owner"
```

### "Twin not found"
```bash
# Create device twins first
python azure_integration/scripts/create_device_twins.py \
  --endpoint <your-adt-endpoint>
```

### "Rate limit exceeded"
```python
# Reduce rate in configuration
streamer = TelemetryStreamer(
    dt_client,
    rate_limit_per_second=25  # Lower rate
)
```

## 📖 Additional Resources

- [Azure Digital Twins Docs](https://learn.microsoft.com/azure/digital-twins/)
- [DTDL v3 Specification](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v3/DTDL.v3.md)
- [Azure Functions Python Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Data Explorer](https://learn.microsoft.com/azure/data-explorer/)

## 🤝 Support

For issues or questions:
1. Check [docs/AZURE_SETUP_GUIDE.md](docs/AZURE_SETUP_GUIDE.md) troubleshooting section
2. Review Azure Digital Twins documentation
3. Create an issue in this repository

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for real-time digital twin simulation**
