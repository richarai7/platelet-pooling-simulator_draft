# What-If Analysis User Guide

## Overview
This simulator is a powerful what-if analysis tool that lets you test different operational setups virtually without disturbing your physical operations. Use it to make data-driven decisions about staffing, equipment, and processes.

---

## 8 Core Capabilities

### 1. 🧑‍🔬 Optimisation of Staff Allocation

**What it does:** Test different staffing levels and see their impact on productivity.

**How to use:**
1. In the Configuration panel, add devices with `type: "person"` or `type: "staff"`
2. Set `capacity: 1` for individual staff members
3. For teams, use higher capacity numbers (e.g., `capacity: 3` for a 3-person team)
4. Adjust the number of staff devices to test different allocation scenarios

**Example scenarios:**
- "What if we add 2 more quality inspectors?"
- "Can we reduce night shift staff from 5 to 3?"
- "How many technicians do we need to handle peak demand?"

**What to check in results:**
- **Staff Utilization** - Are staff overworked (>85%) or underutilized (<30%)?
- **Bottleneck Analysis** - Is staff shortage causing delays?
- **Optimization Suggestions** - Does the simulator recommend adding staff?

**Configuration example:**
```json
{
  "devices": [
    {
      "id": "inspector_1",
      "type": "person",
      "capacity": 1,
      "initial_state": "idle"
    },
    {
      "id": "tech_team",
      "type": "staff",
      "capacity": 3,
      "initial_state": "idle"
    }
  ]
}
```

---

### 2. 🏭 Optimisation of Device Utilisation

**What it does:** Identify which equipment is overused, underused, or creating bottlenecks.

**How to use:**
1. Run your simulation with current device configuration
2. Check the **Device Utilization** section in results
3. Look for devices with utilization >85% (bottlenecks) or <30% (underutilized)
4. Adjust device capacity or add/remove devices
5. Re-run to see the impact

**Example scenarios:**
- "Which machine is our bottleneck?"
- "Can we reduce from 3 centrifuges to 2?"
- "What if we double our quality check capacity?"

**What to check in results:**
- **Capacity Utilization Per Device** - Color-coded bars show usage
  - 🔴 Red (>85%): Overloaded - bottleneck candidate
  - 🟡 Yellow (60-85%): High utilization - monitor
  - 🟢 Green (<60%): Good utilization
- **Resource Bottleneck** - Identifies the constraining device
- **Idle Time Percentage** - Shows wasted capacity
- **Optimization Suggestions** - Recommends capacity changes

**Pro tip:** Use the capacity multiplier feature to quickly test 150%, 200%, or 300% capacity scenarios.

---

### 3. 📊 Supply Variation Analysis

**What it does:** Model uncertainty and variability in supply, demand, and processing times.

**How to use:**
1. For each flow, set `process_time_range: [min, max]` instead of a fixed time
2. Wider ranges = more variability
3. Use different `random_seed` values to test different scenarios
4. Compare results across multiple runs

**Example scenarios:**
- "What if processing time varies ±20%?"
- "How does supply inconsistency affect throughput?"
- "Can we handle variable batch arrival times?"

**What to check in results:**
- **Supply Variation** - Measures input variability
- **Average Cycle Time** - See how variation affects completion time
- **Peak vs Current Throughput** - Understand capacity under variable conditions

**Configuration example:**
```json
{
  "flows": [
    {
      "flow_id": "processing",
      "process_time_range": [300, 600],  // 5-10 min variability
      "from_device": "input",
      "to_device": "output"
    }
  ],
  "simulation": {
    "random_seed": 42  // Change to test different scenarios
  }
}
```

**Pro tip:** Run 5-10 simulations with different random seeds to understand the range of possible outcomes.

---

### 4. 🔄 Process Order Adjustments

**What it does:** Test different workflow sequences and process dependencies.

**How to use:**
1. Use the `dependencies` field in flows to define prerequisites
2. Use `priority` to control execution order (higher = earlier)
3. Rearrange flows to test different sequences
4. Add or remove dependency constraints

**Example scenarios:**
- "What if we do quality checks before pooling instead of after?"
- "Can we parallelize steps that are currently sequential?"
- "What's the impact of changing batch processing order?"

**What to check in results:**
- **Total Flows Completed** - Did the new order improve throughput?
- **Average Cycle Time** - Is the new sequence faster?
- **Device Utilization** - Does reordering balance the load better?

**Configuration example:**
```json
{
  "flows": [
    {
      "flow_id": "step_1",
      "dependencies": null,  // No prerequisites
      "priority": 10
    },
    {
      "flow_id": "step_2",
      "dependencies": ["step_1"],  // Requires step_1 first
      "priority": 5
    }
  ]
}
```

**Pro tip:** Use the dependency visualization (if available) to see your workflow as a graph.

---

### 5. 📦 Product Release Measurement

**What it does:** Track and measure product output rates and timing.

**How to use:**
1. Run your simulation
2. Check output metrics in results
3. Compare against targets or baselines
4. Test different configurations to improve release rates

**Example scenarios:**
- "How many units can we produce per shift?"
- "What's our average time-to-market?"
- "Can we meet a 20% increase in demand?"

**What to check in results:**
- **Product Release Volume** - Total units completed
- **Total Units Created** - Raw production count
- **Current Throughput** - Units per hour
- **Peak Throughput** - Maximum sustainable rate
- **Time to First Unit** - How quickly production starts

**Comparison method:**
1. Run baseline simulation (save results)
2. Make configuration changes
3. Run new simulation
4. Compare release volumes and rates

---

### 6. 🚧 Constraint Modelling

**What it does:** Model real-world limitations like capacity, downtime, and operational constraints.

**How to use:**

**Capacity constraints:**
- Set device `capacity` to limit concurrent operations
- Lower capacity = more restrictive

**Recovery time (downtime):**
- Set `recovery_time_range: [min, max]` for maintenance/cleanup
- Models machine reset time between operations

**Gates (operational constraints):**
- Add `gates` for conditions like "Power On", "Shift Active", "Quality Control Enabled"
- Assign gates to devices/flows with `required_gates`
- Toggle gates true/false to test impact

**Example scenarios:**
- "What if machines need 5-10 min cleanup between batches?"
- "What's the impact of shift changes (8-hour windows)?"
- "How does planned maintenance affect throughput?"

**What to check in results:**
- **Constraint Violations** - Shows when constraints were hit
- **Blocked Time** - How often devices are waiting
- **Queue Lengths** - Backlog due to constraints

**Configuration example:**
```json
{
  "devices": [
    {
      "id": "machine_1",
      "capacity": 2,  // Can handle 2 jobs at once
      "recovery_time_range": [300, 600]  // 5-10 min reset
    }
  ],
  "gates": {
    "Day_Shift": true,
    "Quality_Check_Available": true
  },
  "flows": [
    {
      "flow_id": "inspection",
      "required_gates": ["Quality_Check_Available"]
    }
  ]
}
```

---

### 7. 🔮 Outcome Forecasting

**What it does:** Predict future capacity needs and outcomes based on trends.

**How to use:**
1. Run simulations with current setup
2. Review **Demand Forecast** KPIs
3. Check **Optimization Suggestions** for recommendations
4. Test suggested changes to validate forecasts

**Example scenarios:**
- "If demand grows 30%, what capacity do we need?"
- "What equipment should we invest in next year?"
- "Can our current setup handle projected growth?"

**What to check in results:**
- **Demand Forecast** - Predicted future capacity requirements
- **Optimization Suggestions** - Specific recommendations
- **Resource Bottleneck** - Current constraint that will limit growth
- **Comparison to Baseline** - How scenarios compare

**Pro tip:** Run multiple scenarios (pessimistic, realistic, optimistic) to bracket your forecast range.

---

### 8. 📈 Productivity and Capacity Forecasting

**What it does:** Predict performance under different capacity configurations.

**How to use:**

**Method 1: Manual capacity testing**
1. Set baseline device capacities
2. Run simulation, note results
3. Increase capacities (e.g., double them)
4. Run again and compare

**Method 2: Use capacity multiplier**
1. Create baseline configuration
2. Use the API endpoint `/utils/multiply-capacity` with multipliers [1.0, 1.5, 2.0, 3.0]
3. Compare results across scenarios

**Example scenarios:**
- "What if we add 50% more capacity across all devices?"
- "How much faster would we be with double capacity?"
- "What's the minimum capacity to meet demand?"

**What to check in results:**
- **Capacity Utilization Per Device** - Before/after comparison
- **Total Units Created** - Production improvement
- **Average Cycle Time** - Speed improvement
- **Cost per Unit** - Efficiency gains

**Comparison table example:**

| Scenario | Capacity | Units/Hour | Cycle Time | Bottleneck |
|----------|----------|------------|------------|------------|
| Baseline | 100% | 12.5 | 450s | Quality |
| +50% | 150% | 15.2 | 380s | Quality |
| +100% | 200% | 18.7 | 310s | Separator |
| +200% | 300% | 22.1 | 265s | None |

**Pro tip:** The point where adding capacity stops helping is your current bottleneck.

---

## Quick Start Workflows

### 🎯 Finding Your Bottleneck
1. Run simulation with current config
2. Look at **Device Utilization** - device with highest % is likely the bottleneck
3. Check **Resource Bottleneck** field - confirms the constraint
4. Read **Optimization Suggestions** - tells you how to fix it

### 🎯 Testing a "What-If" Scenario
1. Define your question (e.g., "What if we add 2 more inspectors?")
2. Make the configuration change (add 2 inspector devices)
3. Give it a meaningful **Run Name** (e.g., "2 Additional Inspectors Test")
4. Run simulation
5. Compare results to your baseline
6. Check if optimization suggestions change

### 🎯 Comparing Multiple Scenarios
1. Run baseline - note the **Product Release Volume** and **Throughput**
2. For each scenario:
   - Make changes
   - Use descriptive **Run Name**
   - Run simulation
   - Save or screenshot results
3. Create comparison table with key metrics
4. Make decision based on data

---

## Tips for Success

### 🎓 Best Practices
- **Always establish a baseline** - Run current state first for comparison
- **Change one thing at a time** - Makes it clear what caused improvements
- **Use descriptive run names** - "Baseline", "Add 2 Staff", "Double Quality Capacity"
- **Test edge cases** - Best case, worst case, and realistic scenarios
- **Validate with multiple seeds** - Run 3-5 times with different random seeds
- **Document your assumptions** - What does each configuration represent?

### 🚀 Power User Features
- **Batch testing** - Use the API to run multiple scenarios automatically
- **JSON export** - Save all results for detailed analysis in Excel/Python
- **Capacity multiplier** - Quick way to test 150%, 200%, 300% scenarios
- **Gates** - Model shift schedules, maintenance windows, resource availability

### ⚠️ Common Mistakes
- ❌ Not establishing a baseline for comparison
- ❌ Changing too many variables at once
- ❌ Using too-short simulation duration (use 8+ hours for meaningful results)
- ❌ Ignoring the random seed (results vary without fixed seed)
- ❌ Not checking if bottleneck shifted after changes

---

## Example Use Cases

### Use Case 1: Equipment Purchase Decision
**Question:** Should we buy a $500K second quality check machine?

**Steps:**
1. Run baseline with 1 quality check machine
2. Note: Utilization at 95%, identified as bottleneck
3. Change quality check capacity from 1 to 2
4. Run simulation
5. Compare: Throughput increased 96%, cycle time reduced 97%
6. **Decision:** Yes, purchase is justified - massive improvement

### Use Case 2: Staff Scheduling
**Question:** Can we reduce weekend shift from 5 to 3 staff?

**Steps:**
1. Run baseline with 5 weekend staff
2. Change to 3 staff devices
3. Run simulation
4. Check: Staff utilization jumps to 92%, bottleneck shifts to staff
5. Check: Throughput drops 15%
6. **Decision:** No, would create bottleneck and reduce output

### Use Case 3: Process Optimization
**Question:** Should we do quality checks before or after pooling?

**Steps:**
1. Run baseline with current order
2. Modify flow dependencies to resequence steps
3. Run simulation
4. Compare: No significant change in throughput or cycle time
5. Check: Device utilization pattern similar
6. **Decision:** Order doesn't matter - choose based on other factors

---

## Need Help?

- Check the **Optimization Suggestions** in results - they're specific to your scenario
- Look for devices with >85% utilization - they're your bottlenecks
- Compare your results to the example scenarios in `/examples` folder
- Red utilization bars mean overloaded, green means good capacity
- If uncertain, test 3-5 scenarios and choose the best performer

Remember: The simulator is a decision-support tool. Use it to test ideas before spending money on equipment or making operational changes!
