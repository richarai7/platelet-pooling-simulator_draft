# End-to-End Execution Guide for Platelet Pooling Simulation with Azure Digital Twins

This guide provides step-by-step instructions for running the complete end-to-end platelet pooling simulation with Azure Digital Twins integration.

## Overview

The end-to-end solution provides:

1. **Automatic Device Synchronization**: Devices from your configuration file are automatically created/updated in Azure Digital Twins
2. **Real-Time Telemetry Streaming**: Simulation events are streamed to Azure Digital Twins in real-time
3. **Live Twin Graph Updates**: The digital twin graph reflects the current state of your simulation
4. **Accelerated Mode Support**: Run simulations at high speed (e.g., 100x faster than real-time)
5. **Mock Mode**: Test locally without Azure subscription

## Prerequisites

### For Local Testing (Mock Mode)
- Python 3.9+
- No Azure subscription required

### For Production Deployment
- Azure subscription
- Azure CLI installed (`az --version`)
- Python 3.9+
- Azure Digital Twins instance

## Quick Start

### Option 1: Test Locally (Mock Mode) - 2 Minutes

Perfect for development and testing without Azure costs:

```bash
# Navigate to project directory
cd platelet-pooling-simulator_draft

# Run simulation in mock mode
python run_simulation_with_adt.py \
  --config default_config.json \
  --mock
```

**Expected Output:**
```
================================================================================
SYNCHRONIZING DEVICE TWINS WITH CONFIGURATION
================================================================================
Found 11 devices in configuration
Syncing device: centrifuge
  ✓ Synced centrifuge
...
✅ Device synchronization complete

================================================================================
RUNNING SIMULATION WITH AZURE DIGITAL TWINS INTEGRATION
================================================================================
✓ Telemetry streaming enabled

1. Creating simulation twin: sim_20260214_123456

2. Initializing simulation engine...

3. Running simulation...
   Execution mode: Accelerated (100x speed)

4. Simulation complete!
   ✓ Flows completed: 20
   ✓ Total events: 145
   ✓ Simulation time: 43200 seconds
   ✓ Execution time: 0.52 seconds

5. Streaming final device states to Azure Digital Twins...
   ✓ Updated centrifuge: Idle
   ...

================================================================================
✅ SIMULATION AND SYNC COMPLETE!
================================================================================
```

### Option 2: Deploy to Azure (Production) - 15 Minutes

#### Step 1: Create Azure Resources (5 minutes)

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name platelet-rg \
  --location eastus

# Create Digital Twins instance
az dt create \
  --dt-name platelet-dt-instance \
  --resource-group platelet-rg \
  --location eastus

# Get the endpoint URL
ENDPOINT=$(az dt show \
  --dt-name platelet-dt-instance \
  --resource-group platelet-rg \
  --query "hostName" -o tsv)

echo "Azure Digital Twins Endpoint: https://$ENDPOINT"
```

#### Step 2: Upload DTDL Models (2 minutes)

```bash
# Upload all three models
az dt model create \
  --dt-name platelet-dt-instance \
  --models azure_integration/dtdl_models/Device.json

az dt model create \
  --dt-name platelet-dt-instance \
  --models azure_integration/dtdl_models/ProcessFlow.json

az dt model create \
  --dt-name platelet-dt-instance \
  --models azure_integration/dtdl_models/Simulation.json

# Verify models uploaded
az dt model list --dt-name platelet-dt-instance
```

#### Step 3: Grant Permissions (1 minute)

```bash
# Grant yourself permissions
az dt role-assignment create \
  --dt-name platelet-dt-instance \
  --assignee $(az ad signed-in-user show --query "userPrincipalName" -o tsv) \
  --role "Azure Digital Twins Data Owner"
```

#### Step 4: Run Simulation (1 minute)

```bash
# Set environment variable
export AZURE_DIGITAL_TWINS_ENDPOINT="https://$ENDPOINT"

# Run simulation with Azure Digital Twins
python run_simulation_with_adt.py \
  --config default_config.json
```

The script will:
1. ✅ Connect to Azure Digital Twins
2. ✅ Create/update 11 device twins from configuration
3. ✅ Create simulation twin
4. ✅ Run simulation in accelerated mode (100x speed)
5. ✅ Stream telemetry updates to Azure
6. ✅ Update all device twins with final states

#### Step 5: Verify in Azure Portal (2 minutes)

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to your Digital Twins instance: `platelet-dt-instance`
3. Click **"Azure Digital Twins Explorer"**
4. Run query to see all twins:
   ```sql
   SELECT * FROM digitaltwins
   ```
5. You should see:
   - 11 device twins (centrifuge, platelet_separator, etc.)
   - 1 simulation twin (sim_YYYYMMDD_HHMMSS)
   - All with updated properties and relationships

## Configuration Guide

### Default Configuration (`default_config.json`)

The default configuration includes:

**Simulation Settings:**
```json
{
  "simulation": {
    "duration": 43200,          // 12 hours of simulation time
    "random_seed": 42,          // For reproducibility
    "execution_mode": "accelerated",
    "speed_multiplier": 100,    // Run 100x faster than real-time
    "scenario_name": "Default Platelet Pooling Scenario"
  }
}
```

**Devices (11 total):**
1. `centrifuge` (capacity: 2)
2. `platelet_separator` (capacity: 1)
3. `pooling_station` (capacity: 3)
4. `weigh_register` (capacity: 2)
5. `sterile_connect` (capacity: 2)
6. `test_sample` (capacity: 2)
7. `quality_check` (capacity: 1)
8. `label_station` (capacity: 2)
9. `storage_unit` (capacity: 50)
10. `final_inspection` (capacity: 1)
11. `packaging_station` (capacity: 2)

Each device includes:
- Capacity
- Recovery time ranges
- Metadata (location, manufacturer, model, etc.)

**Process Flows (20 total):**
- 2 batches (batch_001, batch_002)
- 10 flows per batch through the complete production line
- Dependencies to ensure correct sequencing

### Customizing the Configuration

You can create your own configuration by:

1. **Copy the default:**
   ```bash
   cp default_config.json my_config.json
   ```

2. **Modify devices:**
   - Add/remove devices
   - Change capacities
   - Update metadata

3. **Adjust simulation:**
   - Change `duration` for longer/shorter runs
   - Adjust `speed_multiplier` (1 = real-time, 100 = 100x faster)
   - Set `execution_mode` to "real-time" or "accelerated"

4. **Run with custom config:**
   ```bash
   python run_simulation_with_adt.py --config my_config.json
   ```

## Command-Line Options

```bash
python run_simulation_with_adt.py [OPTIONS]

Required:
  --config CONFIG        Path to simulation configuration JSON file

Optional:
  --endpoint ENDPOINT    Azure Digital Twins endpoint URL
                        (or use AZURE_DIGITAL_TWINS_ENDPOINT env var)
  --mock                Use mock mode (no Azure connection)
  --no-sync             Skip device twin synchronization
  --no-telemetry        Disable real-time telemetry streaming

Examples:

# Mock mode (local testing)
python run_simulation_with_adt.py --config default_config.json --mock

# Azure mode with endpoint
python run_simulation_with_adt.py \
  --config default_config.json \
  --endpoint https://platelet-dt-instance.api.eus.digitaltwins.azure.net

# Azure mode with environment variable
export AZURE_DIGITAL_TWINS_ENDPOINT="https://..."
python run_simulation_with_adt.py --config default_config.json

# Skip device sync (if twins already exist)
python run_simulation_with_adt.py \
  --config default_config.json \
  --no-sync

# Run without telemetry (only final state updates)
python run_simulation_with_adt.py \
  --config default_config.json \
  --no-telemetry
```

## Understanding Execution Modes

### Accelerated Mode (Default)

**Configuration:**
```json
{
  "execution_mode": "accelerated",
  "speed_multiplier": 100
}
```

**Behavior:**
- Simulation runs 100x faster than real-time
- 12 hours (43,200 seconds) of simulation time runs in ~432 seconds (~7 minutes)
- Perfect for testing and what-if scenarios
- All logic and timing relationships are preserved

**Use Cases:**
- Testing configurations quickly
- Running multiple scenarios
- What-if analysis
- Performance testing

### Real-Time Mode

**Configuration:**
```json
{
  "execution_mode": "real-time",
  "speed_multiplier": 1
}
```

**Behavior:**
- Simulation runs at 1:1 real-time speed
- 1 simulation second = 1 real-world second
- Useful for live demonstrations and monitoring

**Use Cases:**
- Live demonstrations
- Training
- Real-time monitoring integration

### Maximum Speed Mode

**Configuration:**
```json
{
  "execution_mode": "accelerated"
  // No speed_multiplier specified
}
```

**Behavior:**
- Simulation runs as fast as CPU allows
- No artificial delays
- Fastest execution possible

## Device Twin Synchronization

### Automatic Synchronization

When you run the script, it automatically:

1. **Reads devices from configuration**
   ```json
   {
     "devices": [
       {
         "id": "centrifuge",
         "type": "machine",
         "capacity": 2,
         "metadata": {...}
       }
     ]
   }
   ```

2. **Creates/updates twins in Azure Digital Twins**
   - Twin ID: Same as device ID from config
   - Model: `dtmi:platelet:Device;1`
   - Properties: All device properties + metadata

3. **Handles additions/deletions**
   - New devices in config → Created in Azure
   - Existing devices → Updated with latest properties
   - Devices can be removed from config (twins remain unless explicitly deleted)

### Manual Device Management

You can also create device twins manually:

```bash
# Create twins from config
python azure_integration/scripts/create_device_twins.py \
  --endpoint https://platelet-dt-instance.api.eus.digitaltwins.azure.net
```

## Live Synchronization

### What Gets Synchronized

During simulation execution:

1. **Device States** (real-time)
   - Status: Idle/Processing/Blocked/Failed
   - In-use count
   - Queue length
   - Utilization rate

2. **Simulation Progress** (real-time)
   - Status: Initializing/Running/Completed
   - Total flows completed
   - Total events processed
   - Execution time

3. **Final Results** (at completion)
   - Time in each state (idle, processing, blocked)
   - Total processed count
   - Final device states

### Viewing Live Updates

**Option 1: Azure Digital Twins Explorer**
1. Open Azure Portal
2. Navigate to your Digital Twins instance
3. Click "Azure Digital Twins Explorer"
4. Select a twin to see live property updates
5. Refresh to see changes as simulation runs

**Option 2: Query API**
```bash
# Get current state of a device
az dt twin show \
  --dt-name platelet-dt-instance \
  --twin-id centrifuge

# Query all devices
az dt twin query \
  --dt-name platelet-dt-instance \
  --query-command "SELECT * FROM digitaltwins T WHERE IS_OF_MODEL(T, 'dtmi:platelet:Device;1')"
```

## Troubleshooting

### Issue: Accelerated mode not working (running at real-time speed)

**Solution:** Check your configuration file has both settings:
```json
{
  "simulation": {
    "execution_mode": "accelerated",
    "speed_multiplier": 100
  }
}
```

### Issue: "Azure Digital Twins endpoint not provided"

**Solution:** Either:
- Use `--endpoint` flag: `--endpoint https://...`
- Set environment variable: `export AZURE_DIGITAL_TWINS_ENDPOINT="https://..."`
- Use `--mock` for local testing

### Issue: "Authentication failed"

**Solution:**
```bash
# Re-login to Azure
az login

# Verify you have the correct role
az dt role-assignment list --dt-name platelet-dt-instance
```

### Issue: "Twin not found"

**Solution:** Run with device sync enabled (default):
```bash
python run_simulation_with_adt.py --config default_config.json
```

### Issue: Simulation runs too fast/slow

**Solution:** Adjust `speed_multiplier`:
- Faster: Increase value (e.g., 200, 500, 1000)
- Slower: Decrease value (e.g., 10, 5, 2)
- Real-time: Set to 1
- Maximum speed: Remove the setting

## Cost Considerations

### Development/Testing
- **Mock Mode**: $0/month (no Azure resources)
- **Azure Digital Twins**: ~$5-10/month (basic tier)
- **Total**: ~$5-10/month

### Production
- **Azure Digital Twins**: ~$20-50/month (includes queries)
- **Function App** (optional): ~$150/month (Premium plan)
- **SignalR** (optional): ~$50/month (for real-time UI)
- **Total**: ~$70-250/month

## Next Steps

After successfully running the simulation:

1. **Explore the Digital Twin Graph**
   - View device relationships
   - Query historical data
   - Analyze patterns

2. **Run Multiple Scenarios**
   - Create different configurations
   - Compare results
   - Identify bottlenecks

3. **Integrate with Dashboards**
   - Use SignalR for real-time updates
   - Build custom visualizations
   - Create KPI dashboards

4. **Advanced Analytics**
   - Export data to Azure Data Explorer
   - Create Power BI reports
   - Implement predictive analytics

## Support

For issues or questions:
1. Check this guide first
2. Review `AZURE_INTEGRATION_README.md`
3. Check `docs/AZURE_SETUP_GUIDE.md`
4. Create an issue in the repository

---

**Built with ❤️ for real-time digital twin simulation**
