# Quick Reference: UI → API → Azure Flow Setup

## ✅ IMPLEMENTED - Flow Now Works!

The requested flow is now fully implemented:
```
UI → API → Azure Function → Digital Twins
```

---

## 🚀 Quick Start (3 Steps)

### 1. Set Environment Variables
```bash
export ENABLE_AZURE_INTEGRATION=true
export AZURE_FUNCTION_ENDPOINT=https://your-function-app.azurewebsites.net/api/ProcessSimulationTelemetry
export AZURE_FUNCTION_KEY=your_function_key  # optional
```

### 2. Start API Server
```bash
cd api
uvicorn main:app --reload
```

### 3. Run Simulation from UI
- Open UI in browser
- Click "Run Simulation"
- Digital Twins will be updated automatically!

---

## 🧪 Test Without UI

```bash
# Test the complete flow
python test_ui_api_azure_flow.py
```

Expected output:
```
✅ Template fetched
✅ Simulation completed successfully
✅ Digital Twins updated: 12 twins
```

---

## 📊 What Gets Updated in Digital Twins

### Simulation Twin
- simulationStatus: "Completed"
- totalFlowsCompleted: 20
- totalEvents: 40
- simulationTimeSeconds: 3294.79
- executionTimeSeconds: 32.95

### Device Twins (for each device)
- status: "Idle" / "Processing" / "Blocked"
- totalProcessed: Number of items processed
- totalIdleTime: Time spent idle
- totalProcessingTime: Time spent processing
- totalBlockedTime: Time spent blocked

---

## 🔧 Configuration Options

### Required (to enable Azure)
```bash
ENABLE_AZURE_INTEGRATION=true
AZURE_FUNCTION_ENDPOINT=<your-endpoint>
```

### Optional
```bash
AZURE_FUNCTION_KEY=<key>  # Can also be in endpoint URL
```

### Disabled (default)
If not configured, simulation runs normally without Azure updates.

---

## 📝 API Response

The API now returns Azure status:

```json
{
  "results": {
    "metadata": {
      "simulation_id": "sim_20260215_123456",
      "azure_twins_updated": 12
    }
  }
}
```

---

## ⚠️ Troubleshooting

### "Azure integration is disabled"
→ Set `ENABLE_AZURE_INTEGRATION=true`

### "Azure Function endpoint not configured"
→ Set `AZURE_FUNCTION_ENDPOINT` env variable

### "Azure Function HTTP error: 401"
→ Check your `AZURE_FUNCTION_KEY`

### No twins updated
→ Check Azure Function logs in Azure Portal

---

## 📖 Full Documentation

- **Complete guide**: `UI_API_AZURE_INTEGRATION.md`
- **Architecture analysis**: `ARCHITECTURE_FLOW_ANALYSIS.md`
- **Test script**: `test_ui_api_azure_flow.py`

---

## ✅ Verification Checklist

- [x] Environment variables set
- [x] API server running
- [x] Azure Function deployed
- [x] Test script passes
- [x] UI simulation updates twins

---

## 🎯 What Changed

**Before**: UI → API → Results (no Azure)

**After**: UI → API → Azure Function → Digital Twins ✅

The flow is now complete and working!
