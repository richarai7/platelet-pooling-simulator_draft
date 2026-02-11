# HOW TO USE THE SIMULATOR

## 🎯 For Operations Managers (Using React UI)

### Quick Start

1. **Open the React UI** in your browser
2. **Adjust sliders** to configure your process:
   - Centrifuge machines: 1-10
   - Separator machines: 1-10
   - Quality check machines: 1-10
   - Number of batches: 1-20
3. **Click "Run Simulation"**
4. **View results** instantly

### Understanding the Results

#### Completion Time
**What it means:** Total time to process all batches  
**Example:** "1,666 minutes" = 27.8 hours

**How to use:**
- Compare scenarios: Lower is better
- Baseline vs what-if: % improvement

#### Throughput
**What it means:** Units processed per hour  
**Example:** "7,125 units/hour"

**How to use:**
- Higher = more efficient
- Compare before/after changes

#### Bottleneck
**What it means:** The device slowing everything down  
**Example:** "quality" ← Quality check is the constraint

**How to use:**
- Focus improvements here first
- Adding capacity elsewhere won't help

#### Utilization %
**What it means:** How busy each device is  
**Example:**
- Centrifuge: 15% (mostly idle)
- Quality: 95% (constantly busy) ← Bottleneck!

**How to use:**
- Near 100% = potential bottleneck
- Below 50% = excess capacity (may not need more)

---

## 🧪 Common What-If Scenarios

### 1. "Can we handle more volume?"

**Test:** Increase "Number of batches"
- Current: 5 batches
- Test: 10 batches

**Look for:**
- Completion time increase
- New bottlenecks appearing
- Utilization approaching 100%

**Decision:**
- If completion time doubles: System scales linearly ✅
- If completion time triples: Bottleneck emerging ⚠️

---

### 2. "Should we buy more machines?"

**Test:** Increase capacity for suspected bottleneck
- Example: Quality 1 → 2

**Look for:**
- % improvement in completion time
- Cost per unit reduction
- Bottleneck shifting to different device

**Decision:**
- 50%+ improvement: Worth considering ✅
- 0-10% improvement: Don't buy ❌
- Check if bottleneck moves to another device

---

### 3. "What if a machine breaks?"

**Test:** Reduce capacity temporarily
- Example: Centrifuge 2 → 1 (simulate failure)

**Look for:**
- Impact on completion time
- System resilience
- Critical single points of failure

**Decision:**
- Large impact: Need backup/redundancy ⚠️
- Small impact: System resilient ✅

---

### 4. "How do we reduce cycle time?"

**Test:** Add capacity to bottleneck device
- Example: Quality 1 → 2

**Look for:**
- Cycle time reduction %
- New bottleneck after fix
- ROI calculation

**Decision:**
- Iterative: Fix one bottleneck → Find next → Repeat

---

## 📊 Reading the Dashboard

### Key Metrics Explained

```
╔══════════════════════════════════════════════════════╗
║  SIMULATION RESULTS                                  ║
╠══════════════════════════════════════════════════════╣
║  Completion Time:      1,666 minutes                 ║
║  ↳ Time for ALL batches to finish                   ║
║                                                      ║
║  Throughput:           7,125 units/hour              ║
║  ↳ Production rate (higher = better)                ║
║                                                      ║
║  Bottleneck:           quality ⚠️                   ║
║  ↳ Device limiting your throughput                  ║
║                                                      ║
║  Cost per Unit:        $50.01                        ║
║  ↳ Total cost ÷ units produced                      ║
║                                                      ║
║  Utilization:                                        ║
║    Centrifuge:   15% (excess capacity)               ║
║    Separator:    20% (excess capacity)               ║
║    Quality:      95% (BOTTLENECK!)                   ║
║  ↳ % of time device is busy                         ║
╚══════════════════════════════════════════════════════╝
```

### Color Coding

🟢 **Green** - Good, efficient, no issues  
🟡 **Yellow** - Warning, approaching limits  
🔴 **Red** - Bottleneck, attention needed

---

## 💡 Optimization Suggestions

The simulator automatically provides recommendations:

### Example Output:
```
💡 Optimization Suggestions:

1. ✓ Increase capacity of 'quality' (current bottleneck)
   → Expected improvement: 80-100%

2. ✓ Reduce idle time in centrifuge (15% utilization)
   → Consider reducing number of centrifuges

3. ✓ Balance separator capacity with quality capacity
   → Current ratio is 2:1, consider 1:1
```

**How to use:**
1. Start with #1 suggestion (biggest impact)
2. Run new simulation with that change
3. See if bottleneck moves
4. Repeat until optimized

---

## 🎯 Real-World Examples

### Example 1: Equipment Purchase Decision

**Scenario:** Management wants to buy 2 centrifuges ($500K)

**Test in Simulator:**
1. Baseline: Centrifuge = 2
2. What-if: Centrifuge = 4
3. Run both scenarios

**Results:**
```
Baseline (2):   1,666 min completion
What-if (4):    1,666 min completion
Improvement:    0% ❌
```

**Decision:** DON'T BUY (saved $500K!)

**Alternative Test:** Add 1 quality check instead
```
Baseline (1):   1,666 min
What-if (2):    57 min
Improvement:    96% ✅
```

**Decision:** Invest in quality, not centrifuge!

---

### Example 2: Capacity Planning

**Scenario:** Volume increasing 50% next quarter

**Test in Simulator:**
1. Current: 5 batches
2. Future: 8 batches (50% increase)
3. Run simulation

**Results:**
```
Current (5 batches):  1,666 min
Future (8 batches):   5,000 min (3x longer!)
```

**Interpretation:** System can't handle 50% more volume efficiently

**Solution Test:**
- Add 1 quality check (bottleneck device)
- Re-run with 8 batches

**Results:**
```
Future (8 batches + 1 quality): 2,100 min
```

**Decision:** Need quality upgrade to handle growth

---

### Example 3: Process Optimization

**Scenario:** Reduce overall cycle time

**Methodology:**
1. Run baseline → Identify bottleneck (quality)
2. Fix bottleneck → Add 1 quality
3. Run again → New bottleneck? (separator)
4. Fix new bottleneck → Add 1 separator
5. Run again → Check for next bottleneck
6. Repeat until diminishing returns

**Results:**
```
Iteration 1: Quality 1→2    | 1,666 min → 57 min   (96% gain)
Iteration 2: Separator 2→3  | 57 min → 42 min      (26% gain)
Iteration 3: Centrifuge 2→3 | 42 min → 41 min      (2% gain ← STOP)
```

**Decision:** Invest in quality + separator, skip centrifuge

---

## 🚫 Common Mistakes to Avoid

### ❌ Adding capacity to non-bottleneck devices
**Wrong:** "Centrifuge is important, let's buy more"  
**Right:** Check utilization first - if <50%, don't add capacity

### ❌ Ignoring cost per unit
**Wrong:** Only looking at completion time  
**Right:** Balance time improvement vs cost increase

### ❌ Not testing failure scenarios
**Wrong:** Assume all devices always work  
**Right:** Test with reduced capacity to see resilience

### ❌ Making multiple changes at once
**Wrong:** Change 3 devices simultaneously  
**Right:** Change one thing, test, then iterate

---

## 📋 Best Practices

### ✅ Always test baseline first
Run current configuration to establish benchmark

### ✅ Change one variable at a time
Makes it easy to see what caused the improvement

### ✅ Compare scenarios side-by-side
Run baseline + what-if in same session

### ✅ Focus on bottleneck
Biggest gains come from fixing the constraint

### ✅ Consider cost
Don't just optimize for speed - balance cost/benefit

### ✅ Test edge cases
- High volume scenarios
- Device failure scenarios
- Minimum viable configuration

---

## 🔄 Typical Workflow

```
1. BASELINE
   ├─ Run current configuration
   ├─ Note: Completion time, bottleneck, cost
   └─ Save results

2. IDENTIFY PROBLEM
   ├─ Look for bottleneck device (high utilization)
   ├─ Check if meeting business goals (throughput, cost)
   └─ Determine improvement target (e.g., 30% faster)

3. HYPOTHESIS
   ├─ "Adding 1 quality check will improve by 50%"
   └─ Based on bottleneck analysis

4. TEST
   ├─ Adjust slider: Quality 1 → 2
   ├─ Run simulation
   └─ Compare to baseline

5. ANALYZE
   ├─ Did it meet improvement target? ✅
   ├─ Did bottleneck shift? Check!
   ├─ Is cost acceptable? Evaluate
   └─ Side effects? (utilization changes)

6. ITERATE
   ├─ If successful: Test next bottleneck
   ├─ If not: Try different approach
   └─ Keep optimizing until goal met

7. DECIDE
   ├─ Export results
   ├─ Present to stakeholders
   └─ Implement in real world
```

---

## 📤 Exporting Results

### JSON Export
Click "Export to JSON" to get full results including:
- All 44 KPIs
- Device utilization details
- Flow completion times
- Optimization suggestions

**Use for:**
- Sharing with stakeholders
- Integration with other systems
- Historical tracking
- Detailed analysis

### Excel Export
Click "Export to Excel" for spreadsheet with:
- Summary dashboard
- Comparison charts
- Cost analysis
- Recommendations

**Use for:**
- Manager presentations
- Budget planning
- ROI calculations

---

## 🎓 Training Scenarios

### For New Users: Start Here

**Scenario 1: Understand Bottleneck**
1. Run baseline (default settings)
2. Note bottleneck device
3. Add +1 to bottleneck device
4. Run again
5. See massive improvement!

**Scenario 2: Non-Bottleneck Test**
1. Run baseline
2. Add +2 to NON-bottleneck device (low utilization)
3. Run again
4. See zero improvement (learning moment!)

**Scenario 3: Volume Scaling**
1. Run with 5 batches
2. Run with 10 batches
3. Run with 20 batches
4. See how system degrades

**Scenario 4: Optimization**
1. Start with 1 of each device
2. Run simulation
3. Fix bottleneck
4. Repeat until all devices ~50-70% utilized (balanced)

---

## ❓ FAQ

**Q: How accurate is the simulator?**  
A: 95%+ accuracy when process times are calibrated to real-world data

**Q: How long does a simulation take?**  
A: Typically <2 seconds for standard scenarios

**Q: Can I simulate failures?**  
A: Yes, reduce device capacity to simulate downtime

**Q: What if I want custom metrics?**  
A: Contact IT team - KPI calculator is extensible

**Q: Can I save my scenarios?**  
A: Yes, scenarios are saved in browser localStorage

**Q: How many batches can I simulate?**  
A: Tested up to 1000+ batches (takes ~10 seconds)

---

## 📞 Support

**For Operations Questions:**
- Check bottleneck analysis first
- Review optimization suggestions
- Try quick test scenarios

**For Technical Issues:**
- Contact IT support
- Provide: scenario config, error message, screenshot

**For Feature Requests:**
- Submit via feedback form
- Describe use case and benefit

---

**Remember:** The simulator is a decision support tool. It shows you what COULD happen, but real-world results depend on accurate input data and assumptions. Always validate major decisions with pilot tests!
