# 🚀 HOW TO RUN MULTI-BATCH CONFIG IN REACT UI

## ✅ API Endpoint Ready!

The multi-batch configuration is now available at:

```
GET http://localhost:8000/templates/platelet-pooling-multi-batch
```

**Parameters:**
- `batches` - Number of batches (default: 5)
- `interval` - Seconds between arrivals (default: 600 = 10 min)

---

## Option 1: Load Via Template Selector (If UI Supports It)

If your React UI has a **template dropdown/selector**:

1. Look for "platelet-pooling-multi-batch" in the template list
2. Select it
3. Click "Load Template" or similar button
4. You should see **55 flows** loaded (not 11)
5. Run the simulation

---

## Option 2: Test Directly Via API (Quick Validation)

**Open a new terminal and run this:**

```bash
# Test 1: Baseline
curl -X POST http://localhost:8000/simulations/run ^
  -H "Content-Type: application/json" ^
  -d "{\"config\": $(curl -s http://localhost:8000/templates/platelet-pooling-multi-batch)}"
```

**You should see:**
- Completion time: ~130 minutes
- Flows completed: ~14,000+

---

## Option 3: Simple Python Test Script

**Run this to see it working:**

```bash
python -c "import requests; config = requests.get('http://localhost:8000/templates/platelet-pooling-multi-batch').json(); result = requests.post('http://localhost:8000/simulations/run', json={'config': config}).json(); print(f\"Time: {result['results']['summary']['simulation_time_seconds']/60:.1f} min\"); print(f\"Flows: {result['results']['summary']['total_flows_completed']}\")"
```

---

## Option 4: Update React UI To Use New Template

If your React UI currently fetches from `/templates/platelet-pooling`, you can:

### A. Add Template Selector

**In your React component:**

```javascript
const [selectedTemplate, setSelectedTemplate] = useState('platelet-pooling');

// Fetch template
const loadTemplate = async () => {
  const response = await fetch(
    `http://localhost:8000/templates/${selectedTemplate}`
  );
  const config = await response.json();
  setConfig(config);
};

// In your JSX
<select onChange={(e) => setSelectedTemplate(e.target.value)}>
  <option value="platelet-pooling">Single Flow (11 flows)</option>
  <option value="platelet-pooling-multi-batch">Multi-Batch (55 flows)</option>
</select>
<button onClick={loadTemplate}>Load Template</button>
```

### B. Change Default Template

**Or simply change the default fetch URL:**

```javascript
// Old:
fetch('http://localhost:8000/templates/platelet-pooling')

// New (multi-batch):
fetch('http://localhost:8000/templates/platelet-pooling-multi-batch')
```

---

## Option 5: Manual Config Upload (If UI Has It)

If your React UI has a **"Upload Config"** or **"Import JSON"** feature:

1. Use the saved file: `multi_batch_config.json`
2. Click "Upload" or "Import"
3. Load it into the simulator
4. Run it

---

## What You'll See With Multi-Batch

### ✅ Baseline Run
- **130.8 minutes** to complete all 5 batches
- ~14,000+ flows executed
- Shows queuing at bottleneck devices

### ✅ Test Capacity Change
Change `platelet_separator` from capacity=1 to capacity=2:

- **100.7 minutes** to complete
- **23% improvement!** 🎉
- Saves 30 minutes

### ✅ Non-Bottleneck Test
Change `pooling_station` from capacity=3 to capacity=6:

- **130.8 minutes** (same as baseline)
- **0% improvement** (correctly identifies non-bottleneck)

---

## Quick Test Command

**Run this now to prove it works:**

```bash
cd C:\Users\rrai3\AIAgent\simulation-engine
python generate_multi_batch.py
```

This will:
1. Generate the config
2. Test baseline (130 min)
3. Test platelet_separator 1→2 (100 min, **23% faster**)
4. Test pooling_station 3→6 (130 min, no change)

---

## Files Created

✅ **multi_batch_config.json** - The configuration file
✅ **generate_multi_batch.py** - Generator script
✅ **API endpoint** - `/templates/platelet-pooling-multi-batch`

---

## Need Help With React UI?

If you need help modifying your React code to use this template, share:

1. The component file that loads templates
2. Or show me where templates are fetched
3. I'll update it to support multi-batch

**What would you like to do next?**
