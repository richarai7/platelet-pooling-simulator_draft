# Azure Digital Twins Integration - Quick Start

## Overview

This integration enables real-time streaming of simulation telemetry to Azure Digital Twins, creating a live digital representation of your platelet pooling lab.

## Features

- ✅ Real-time telemetry streaming to Azure Digital Twins
- ✅ Batching and throttling for ADT service limits
- ✅ DTDL v3 compliant models (Device, ProcessFlow, Simulation)
- ✅ Azure Function App for serverless telemetry processing
- ✅ Mock mode for local development without Azure
- ✅ Async/await support for high-performance streaming

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
# Install Azure SDK packages
pip install azure-identity azure-digitaltwins-core

# Or install all dependencies
pip install -r requirements-azure.txt
```

### 2. Run in Mock Mode (No Azure Required)

```bash
# Set mock endpoint
export AZURE_DIGITAL_TWINS_ENDPOINT="mock://localhost"

# Run test
python examples/test_azure_integration.py
```

Output:
```
✓ Connected to Azure Digital Twins (MOCK mode)
✓ Running simulation...
✓ Streaming telemetry...
✓ Simulation complete: 6 flows processed
✅ END-TO-END TEST COMPLETED SUCCESSFULLY!
```

## Azure Deployment

### Prerequisites

- Azure subscription
- Azure CLI installed
- Python 3.9+

### Step-by-Step Guide

See **[docs/AZURE_SETUP_GUIDE.md](../docs/AZURE_SETUP_GUIDE.md)** for complete deployment instructions.

**Quick summary:**

1. **Create Azure Digital Twins instance**
   ```bash
   az dt create --dt-name platelet-dt --resource-group my-rg --location eastus
   ```

2. **Upload DTDL models**
   ```bash
   az dt model create --dt-name platelet-dt --models azure_integration/dtdl_models/*.json
   ```

3. **Create device twins**
   ```bash
   python azure_integration/scripts/create_device_twins.py \
     --endpoint https://platelet-dt.api.eus.digitaltwins.azure.net
   ```

4. **Run simulation**
   ```bash
   export AZURE_DIGITAL_TWINS_ENDPOINT="https://platelet-dt.api.eus.digitaltwins.azure.net"
   python examples/test_azure_integration.py
   ```

## Architecture

```
Simulation Engine (Python)
         │
         ▼
  Telemetry Streamer
    (Batching + Throttling)
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    Direct Mode   Function Mode   Event Hub
         │              │              │
         ▼              ▼              ▼
    Azure Digital Twins Instance
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    3D Scenes      SignalR      Azure Data Explorer
    (Viz)        (Real-time)    (Historical)
```

## DTDL Models

### Device Model
- Status: Idle/Processing/Blocked/Failed
- Capacity and utilization tracking
- Queue length monitoring
- Time-in-state tracking

### ProcessFlow Model
- Flow status tracking
- Batch information
- Quality scores
- Relationships to devices

### Simulation Model
- Run metadata
- KPIs (throughput, cycle time)
- Relationships to devices

## Configuration

### Environment Variables

```bash
# Required
export AZURE_DIGITAL_TWINS_ENDPOINT="https://your-instance.api.eus.digitaltwins.azure.net"

# Optional (for Azure Function mode)
export AZURE_FUNCTION_ENDPOINT="https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry"
export AZURE_FUNCTION_KEY="your-function-key"

# Optional (authentication)
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

### Configuration File

Create `azure_config.json`:

```json
{
  "azure_digital_twins": {
    "endpoint": "https://platelet-dt.api.eus.digitaltwins.azure.net",
    "batch_size": 10,
    "batch_interval_seconds": 1.0,
    "rate_limit_per_second": 50
  },
  "telemetry": {
    "enabled": true,
    "stream_mode": "direct",
    "buffer_size": 100
  }
}
```

## API Examples

### Python API

```python
from azure_integration.digital_twins_client import DigitalTwinsClientWrapper
from azure_integration.telemetry_streamer import TelemetryStreamer

# Initialize client
dt_client = DigitalTwinsClientWrapper(
    adt_endpoint="https://platelet-dt.api.eus.digitaltwins.azure.net"
)

# Initialize streamer
streamer = TelemetryStreamer(dt_client)
await streamer.start_auto_flush()

# Stream device update
await streamer.stream_device_update(
    device_id="centrifuge-01",
    status="Processing",
    in_use=2,
    capacity=2,
    queue_length=3
)

# Stream simulation update
await streamer.stream_simulation_update(
    simulation_id="sim_20260212_123456",
    simulation_status="Running",
    total_flows_completed=10,
    total_events=150
)

# Cleanup
await streamer.stop_auto_flush()
```

### REST API (via Azure Function)

```bash
# Send telemetry to Azure Function
curl -X POST "https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "telemetry": [
      {
        "twin_id": "centrifuge-01",
        "properties": {
          "status": "Processing",
          "inUse": 2,
          "capacity": 2,
          "utilizationRate": 100.0
        }
      }
    ]
  }'
```

## Testing

### Run Tests

```bash
# Unit tests
pytest tests/test_azure_integration.py

# Integration test (requires Azure)
python examples/test_azure_integration.py --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT

# Mock mode test (no Azure required)
python examples/test_azure_integration.py --endpoint mock://localhost
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

## Performance

### Throughput

- **Direct mode**: Up to 50 updates/second (ADT rate limit)
- **Function mode**: Up to 100 updates/second (with batching)
- **Event Hub mode**: Up to 1000+ events/second

### Latency

- **Direct mode**: < 100ms per update
- **Function mode**: < 500ms (includes cold start)
- **Batching**: Updates every 1 second by default

### Optimization

For high-throughput scenarios:

```python
# Increase batch size and rate limit
streamer = TelemetryStreamer(
    dt_client,
    batch_size=50,
    batch_interval_seconds=0.5,
    rate_limit_per_second=100
)
```

## Troubleshooting

### "Authentication failed"

**Solution**: Ensure you're logged in to Azure CLI
```bash
az login
az account set --subscription "Your Subscription Name"
```

### "Twin not found"

**Solution**: Create device twins first
```bash
python azure_integration/scripts/create_device_twins.py --endpoint $AZURE_DIGITAL_TWINS_ENDPOINT
```

### "Rate limit exceeded"

**Solution**: Reduce rate limit in configuration
```python
streamer = TelemetryStreamer(dt_client, rate_limit_per_second=25)
```

## Next Steps

1. ✅ Complete Azure setup guide: [docs/AZURE_SETUP_GUIDE.md](../docs/AZURE_SETUP_GUIDE.md)
2. 🔄 Configure Azure Data Explorer for historical data
3. 🔄 Setup SignalR for real-time UI updates
4. 🔄 Add 3D Scenes Studio visualization
5. 🔄 Implement advanced KPI calculations

## Resources

- [Azure Digital Twins Documentation](https://learn.microsoft.com/azure/digital-twins/)
- [DTDL v3 Specification](https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v3/DTDL.v3.md)
- [Azure Functions Python Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Data Explorer](https://learn.microsoft.com/azure/data-explorer/)

## Support

For issues or questions:
- Create an issue in the repository
- Check [docs/AZURE_SETUP_GUIDE.md](../docs/AZURE_SETUP_GUIDE.md) troubleshooting section
- Review Azure Digital Twins documentation
