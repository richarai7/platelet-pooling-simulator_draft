# LOAD/UNLOAD STEPS & METADATA GUIDE

## 🎯 New Features Added

### 1. Load/Unload Flow Types
### 2. Key-Value Pair Storage (Metadata)

---

## 📦 Load/Unload Steps

### What Are They?

**Load/Unload** are special flow types that represent:
- **Load**: Moving material INTO a device (e.g., loading platelets into centrifuge)
- **Unload**: Moving material OUT OF a device (e.g., removing processed platelets)
- **Process**: Normal processing step (default behavior)

### Why Use Them?

**Benefits:**
- **Separate timing** for load vs process vs unload
- **Track logistics** separately from processing
- **Model real operations** more accurately (load time + process time + unload time)
- **Calculate KPIs** like load/unload efficiency

---

## 🔧 How to Use Load/Unload

### Example: Platelet Centrifuge with Load/Unload

**Old Way (Single Flow):**
```json
{
  "flow_id": "batch1_centrifuge",
  "from_device": "centrifuge",
  "to_device": "separator",
  "process_time_range": [360, 480],
  "flow_type": "process"
}
```
This combines load + process + unload into one step (360-480 sec total)

**New Way (Separate Steps):**
```json
[
  {
    "flow_id": "batch1_load_centrifuge",
    "from_device": "input_queue",
    "to_device": "centrifuge",
    "process_time_range": [30, 60],
    "flow_type": "load",
    "priority": 1
  },
  {
    "flow_id": "batch1_process_centrifuge",
    "from_device": "centrifuge",
    "to_device": "centrifuge",
    "process_time_range": [300, 420],
    "flow_type": "process",
    "priority": 1,
    "dependencies": ["batch1_load_centrifuge"]
  },
  {
    "flow_id": "batch1_unload_centrifuge",
    "from_device": "centrifuge",
    "to_device": "separator",
    "process_time_range": [30, 60],
    "flow_type": "unload",
    "priority": 1,
    "dependencies": ["batch1_process_centrifuge"]
  }
]
```

**Result:**
- Load: 30-60 seconds
- Process: 300-420 seconds
- Unload: 30-60 seconds
- Total: 360-540 seconds
- **You can now track each phase separately!**

---

## 🗃️ Key-Value Pair Storage (Metadata)

### What Is Metadata?

**Metadata** = Custom fields you can add to devices and flows for domain-specific data.

**Use cases:**
- Device location/coordinates (for 3D visualization)
- Cost information (equipment cost, operating cost)
- Staff requirements (how many people needed)
- Batch IDs, lot numbers, tracking codes
- Quality metrics, temperature settings
- **ANY custom data your application needs!**

---

## 🔧 How to Use Metadata

### Device Metadata Example

```json
{
  "id": "centrifuge_1",
  "type": "machine",
  "capacity": 2,
  "metadata": {
    "location": {"x": 10, "y": 5, "z": 0},
    "cost_per_hour": 50,
    "manufacturer": "BioTech Inc",
    "model": "CT-2000",
    "installation_date": "2024-01-15",
    "maintenance_schedule": "monthly",
    "operator_required": true,
    "room_id": "processing_room_a"
  }
}
```

**Benefits:**
- 3D visualization can read `location` coordinates
- Cost calculator can read `cost_per_hour`
- Maintenance system can read `maintenance_schedule`
- **Your simulator doesn't break if you add new fields!**

### Flow Metadata Example

```json
{
  "flow_id": "batch1_load_centrifuge",
  "from_device": "input_queue",
  "to_device": "centrifuge",
  "process_time_range": [30, 60],
  "flow_type": "load",
  "metadata": {
    "batch_id": "BATCH-2026-001",
    "donor_ids": ["D001", "D002", "D003"],
    "volume_ml": 450,
    "temperature_c": 22,
    "priority_level": "high",
    "requires_certification": true,
    "tracking_code": "TRK-ABC-123"
  }
}
```

**Benefits:**
- Track batch information through the process
- Export tracking codes to downstream systems
- Filter high-priority batches for analysis
- **Store ANY domain-specific data without changing code!**

---

## 📊 Full Example: Platelet Process with Load/Unload + Metadata

```json
{
  "simulation": {
    "duration": 10000,
    "random_seed": 42
  },
  "devices": [
    {
      "id": "input_queue",
      "type": "material",
      "capacity": 100,
      "metadata": {
        "location": {"x": 0, "y": 0, "z": 0},
        "area": "receiving"
      }
    },
    {
      "id": "centrifuge",
      "type": "machine",
      "capacity": 2,
      "metadata": {
        "location": {"x": 10, "y": 5, "z": 0},
        "cost_per_hour": 50,
        "operator_required": true
      }
    },
    {
      "id": "separator",
      "type": "machine",
      "capacity": 2,
      "metadata": {
        "location": {"x": 20, "y": 5, "z": 0},
        "cost_per_hour": 75,
        "requires_sterile_environment": true
      }
    }
  ],
  "flows": [
    {
      "flow_id": "batch1_load",
      "from_device": "input_queue",
      "to_device": "centrifuge",
      "process_time_range": [30, 60],
      "flow_type": "load",
      "priority": 1,
      "metadata": {
        "batch_id": "BATCH-001",
        "volume_ml": 450,
        "operator": "Staff-A"
      }
    },
    {
      "flow_id": "batch1_process",
      "from_device": "centrifuge",
      "to_device": "centrifuge",
      "process_time_range": [300, 420],
      "flow_type": "process",
      "priority": 1,
      "dependencies": ["batch1_load"],
      "metadata": {
        "batch_id": "BATCH-001",
        "rpm": 3500,
        "temperature_c": 22
      }
    },
    {
      "flow_id": "batch1_unload",
      "from_device": "centrifuge",
      "to_device": "separator",
      "process_time_range": [30, 60],
      "flow_type": "unload",
      "priority": 1,
      "dependencies": ["batch1_process"],
      "metadata": {
        "batch_id": "BATCH-001",
        "operator": "Staff-A",
        "transfer_type": "sterile_connection"
      }
    }
  ]
}
```

---

## 🎯 Use Cases

### 1. Separate Load/Unload Timing

**Problem:** Load and unload take different amounts of time than processing

**Solution:**
```json
"flow_type": "load"   → 30-60 seconds
"flow_type": "process" → 300-420 seconds  
"flow_type": "unload"  → 30-60 seconds
```

**Analysis:** Calculate load efficiency vs process efficiency separately

---

### 2. Track Batches Through Process

**Problem:** Need to track which batch went through which devices

**Solution:**
```json
"metadata": {
  "batch_id": "BATCH-001",
  "tracking_code": "TRK-ABC-123"
}
```

**Analysis:** Query simulation results by batch_id, export to tracking system

---

### 3. 3D Visualization

**Problem:** React UI needs device positions for 3D model

**Solution:**
```json
"metadata": {
  "location": {"x": 10, "y": 5, "z": 0},
  "room_id": "processing_room_a"
}
```

**Analysis:** React reads `location` metadata and positions devices in 3D scene

---

### 4. Cost Calculation

**Problem:** Need to calculate operating costs per device

**Solution:**
```json
"metadata": {
  "cost_per_hour": 50,
  "maintenance_cost_per_month": 1000
}
```

**Analysis:** KPI calculator reads metadata and computes total costs

---

### 5. Staff Tracking

**Problem:** Need to know operator requirements

**Solution:**
```json
"metadata": {
  "operator": "Staff-A",
  "certification_required": "Level-2",
  "operator_required": true
}
```

**Analysis:** Calculate staff utilization, identify certification needs

---

## 🔍 How to Query Metadata

**In simulation results:**

```python
# Access device metadata
device = config['devices'][0]
location = device.get('metadata', {}).get('location')
cost = device.get('metadata', {}).get('cost_per_hour', 0)

# Access flow metadata
flow = config['flows'][0]
batch_id = flow.get('metadata', {}).get('batch_id')
operator = flow.get('metadata', {}).get('operator')
```

**In React UI:**

```javascript
// Read device metadata
const deviceLocation = device.metadata?.location;
const deviceCost = device.metadata?.cost_per_hour || 0;

// Filter flows by type
const loadFlows = flows.filter(f => f.flow_type === 'load');
const processFlows = flows.filter(f => f.flow_type === 'process');
const unloadFlows = flows.filter(f => f.flow_type === 'unload');
```

---

## ✅ Summary

### Load/Unload Types:
- `flow_type: "load"` - Moving material into device
- `flow_type: "process"` - Processing/transformation
- `flow_type: "unload"` - Moving material out of device
- Default: `"process"` if not specified

### Metadata Fields:
- Add to **devices**: `"metadata": { ...custom fields... }`
- Add to **flows**: `"metadata": { ...custom fields... }`
- Store **anything**: location, cost, batch IDs, tracking codes, etc.
- **Backwards compatible**: Optional field, doesn't break existing configs

### Benefits:
✅ Model real operations more accurately  
✅ Track load/unload separately from processing  
✅ Store custom data without changing code  
✅ Support 3D visualization, cost tracking, batch tracking  
✅ Future-proof (add new fields anytime)  
✅ Export metadata to downstream systems  

---

**Your simulator now supports:**
1. ✅ Load/unload as distinct steps
2. ✅ Key-value pairs for custom metadata
3. ✅ Flexible, extensible configuration
4. ✅ Domain-specific data storage

Use these features in your React UI to create more detailed simulations! 🚀
