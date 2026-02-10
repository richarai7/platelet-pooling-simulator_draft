# HOW TO TEST 200% CAPACITY INCREASE

## 🎯 Quick Answer

**In the React UI:**

1. **Baseline run first:**
   - Note current device capacities (e.g., Centrifuge=2, Separator=2, Quality=1)
   - Click "Run Simulation"
   - Save results (completion time, throughput, etc.)

2. **Test 200% capacity (double everything):**
   - Change Centrifuge: `2` → `6` (2 × 3 = 6 for 200% increase)
   - Change Separator: `2` → `6`
   - Change Quality: `1` → `3`
   - Click "Run Simulation"
   - Compare to baseline

**Note:** 200% increase = 3× the original (100% + 200% = 300% total)

---

## 🔢 Understanding Capacity Multipliers

### Percentage vs Multiplier Confusion

| What You Want | Math | Original→New | Multiplier |
|---------------|------|-------------|-----------|
| 50% increase | +50% of original | 2→3 | 1.5× |
| 100% increase (double) | +100% of original | 2→4 | 2.0× |
| 200% increase (triple) | +200% of original | 2→6 | 3.0× |

**If you want to DOUBLE capacity:**
- That's a **100% increase**
- Multiply by **2.0**
- Example: 2 machines → 4 machines

**If you want to TRIPLE capacity:**
- That's a **200% increase**  
- Multiply by **3.0**
- Example: 2 machines → 6 machines

---

## 🖥️ Three Ways to Test in UI

### Method 1: Manual Entry (Simplest)

**Current UI approach:**

```
Device Configuration Panel:
┌─────────────────────────────────┐
│ Centrifuge                      │
│ Capacity: [2] ← Change to 6     │
│                                 │
│ Separator                       │
│ Capacity: [2] ← Change to 6     │
│                                 │
│ Quality                         │
│ Capacity: [1] ← Change to 3     │
│                                 │
│ [Run Simulation]                │
└─────────────────────────────────┘
```

**Steps:**
1. Click on capacity input field
2. Delete current number
3. Type new number (3× the original for 200% increase)
4. Press Enter or click outside field
5. Click "Run Simulation"

---

### Method 2: Use API Helper (Advanced)

**If your React UI has a "Quick Test" feature:**

Call the new `/utils/multiply-capacity` endpoint I just added:

```javascript
// In your React component
const testDoubleCapacity = async () => {
  const response = await fetch('/api/utils/multiply-capacity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      config: currentConfig,
      multiplier: 2.0  // Double all capacities
    })
  });
  
  const result = await response.json();
  setConfig(result.config);  // Apply new config
  runSimulation();           // Run with doubled capacity
};
```

**Benefits:**
- One click to multiply ALL devices
- No manual calculation
- Consistent multiplier applied

---

### Method 3: Comparison Mode (Best for Analysis)

**If you want to compare multiple capacity levels side-by-side:**

```javascript
// Create comparison scenarios
const compareCapacities = async () => {
  const response = await fetch('/api/utils/create-comparison', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      config: baselineConfig,
      multipliers: [1.0, 1.5, 2.0, 3.0]  // 100%, 150%, 200%, 300%
    })
  });
  
  const { scenarios } = await response.json();
  
  // Run all scenarios
  const results = await Promise.all(
    scenarios.map(config => runSimulation(config))
  );
  
  // Display comparison table
  displayComparison(results);
};
```

**Results display:**

```
╔══════════════════════════════════════════════════════╗
║  CAPACITY COMPARISON RESULTS                         ║
╠══════════════════════════════════════════════════════╣
║  100% (Baseline):   1,666 min   | 7,125 units/hr    ║
║  150% (+50%):       1,112 min   | 10,688 units/hr   ║
║  200% (Double):     833 min     | 14,250 units/hr   ║
║  300% (Triple):     556 min     | 21,375 units/hr   ║
╠══════════════════════════════════════════════════════╣
║  Best ROI: 200% shows optimal balance               ║
╚══════════════════════════════════════════════════════╝
```

---

## 📋 Step-by-Step Example

### Testing: "What if we increase ALL capacity by 200%?"

**Current Setup:**
- Centrifuge: 2 machines
- Separator: 2 machines
- Quality: 1 machine

**Goal:** Test with 200% increase (triple each)

**Steps:**

1. **Run Baseline:**
   ```
   Keep current settings
   Click "Run Simulation"
   
   Results:
   - Completion Time: 1,666 minutes
   - Throughput: 7,125 units/hr
   - Bottleneck: quality
   ```

2. **Modify Configuration:**
   ```
   Centrifuge:  2 → 6  (2 + 200% of 2 = 2 + 4 = 6)
   Separator:   2 → 6
   Quality:     1 → 3  (1 + 200% of 1 = 1 + 2 = 3)
   ```

3. **Run Modified Simulation:**
   ```
   Click "Run Simulation"
   
   Results:
   - Completion Time: 556 minutes (66% faster!)
   - Throughput: 21,375 units/hr (3× increase)
   - Bottleneck: none (balanced)
   ```

4. **Compare:**
   ```
   Baseline vs 200% Increase:
   - Time saved: 1,110 minutes
   - Throughput gain: 14,250 units/hr
   - Improvement: 66.6%
   ```

---

## 🎯 What to Look For

After running the 200% capacity test, check:

### ✅ Did It Help?

**Good Signs:**
- Completion time decreased significantly (50%+ improvement)
- Throughput increased proportionally
- Bottleneck shifted or disappeared
- Queue sizes reduced to near zero

**Bad Signs:**
- Completion time barely changed (0-10% improvement)
- Same bottleneck still exists
- Waste increased (unused capacity)
- Cost/benefit doesn't justify equipment purchase

### 💡 Interpretation Examples

**Scenario A: Proportional Improvement**
```
Double capacity (2→4) → Half the time (1,666 min → 833 min)
✓ System scales well, no hidden bottlenecks
```

**Scenario B: Diminishing Returns**
```
Double capacity (2→4) → Only 20% faster (1,666 min → 1,333 min)
✗ Bottleneck elsewhere limits benefit
✗ Don't invest in doubling capacity
```

**Scenario C: Zero Impact**
```
Double capacity (2→4) → Same time (1,666 min → 1,666 min)
✗ This device is NOT the bottleneck at all!
✗ Waste of money
```

---

## 🧪 Recommended Test Sequence

**Don't just test 200% blindly!** Test a range to find the optimal point:

```javascript
// Test multiple levels
const testMultipliers = [1.0, 1.25, 1.5, 2.0, 3.0];

Results might show:
  1.0× (baseline):  1,666 min
  1.25× (+25%):     1,333 min  ← 20% improvement
  1.5× (+50%):      1,112 min  ← 33% improvement
  2.0× (double):    833 min    ← 50% improvement ✓ Good ROI
  3.0× (triple):    740 min    ← 55% improvement ✗ Diminishing returns

Conclusion: Doubling (2.0×) gives best cost/benefit ratio
```

---

## 🚫 Common Mistakes

### ❌ Multiplying when you should add

**Wrong:**
> "I want 200% capacity, so I set capacity to 2.0"

**Right:**
> "I want 200% MORE capacity (triple), so I multiply by 3"
> Original: 2 → New: 6 (that's 200% increase)

### ❌ Only changing one device

**Wrong:**
> "I only changed quality from 1 to 3"

**Problem:**
> Now quality isn't the bottleneck, but separator is!
> You solved one problem and created another

**Right:**
> Change ALL devices proportionally first
> Then optimize individual devices based on results

### ❌ Not running baseline first

**Wrong:**
> Immediately test with doubled capacity

**Right:**
> Always run baseline → Save results → Then test changes
> You need comparison to measure improvement

---

## 💾 Save Your Results

After testing, export results:

```
Baseline (100%):
  - Config: C:2, S:2, Q:1
  - Time: 1,666 min
  - Cost: $9.9M

Test 200% (+200%):
  - Config: C:6, S:6, Q:3
  - Time: 556 min
  - Cost: $3.3M
  
ROI Analysis:
  - Equipment cost: $1.5M (4 extra machines)
  - Time saved: 66%
  - Payback period: 6 months
  - Decision: APPROVED ✅
```

---

## 📞 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  CAPACITY INCREASE CHEAT SHEET                  │
├─────────────────────────────────────────────────┤
│  Want 50% more?    → Multiply by 1.5           │
│  Want to double?   → Multiply by 2.0           │
│  Want to triple?   → Multiply by 3.0           │
│  Want 200% more?   → Multiply by 3.0           │
│                                                 │
│  Examples:                                      │
│  • 2 machines + 50%  = 2 × 1.5 = 3 machines    │
│  • 2 machines + 100% = 2 × 2.0 = 4 machines    │
│  • 2 machines + 200% = 2 × 3.0 = 6 machines    │
│                                                 │
│  In UI:                                         │
│  1. Note baseline capacities                    │
│  2. Multiply each by desired factor            │
│  3. Enter new values                            │
│  4. Click "Run Simulation"                      │
│  5. Compare results                             │
└─────────────────────────────────────────────────┘
```

---

**TL;DR:** To test 200% capacity increase in your React UI:

1. Note current numbers (e.g., 2, 2, 1)
2. Triple them (6, 6, 3) ← That's 200% MORE
3. Enter new values in UI
4. Click "Run Simulation"
5. Compare to baseline

Done! 🎯
