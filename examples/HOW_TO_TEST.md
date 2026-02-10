# HOW TO TEST - STEP BY STEP

## The Problem You're Having

The default template is too complex (11 devices, complex dependencies). It's hard to see what's happening.

## THE SOLUTION - Use This Simple Test

I created `SIMPLE_TEST_CONFIG.json` with:
- **3 devices**: Centrifuge(2), Separator(2), Quality(1)
- **3 batches** (9 flows total)
- **Quality is the bottleneck** (capacity=1, gets overwhelmed)

---

## 📋 STEP-BY-STEP TESTING

### Step 1: Load Simple Config in React UI

1. In the React UI, **delete all the current devices/flows**
2. Copy the content from `SIMPLE_TEST_CONFIG.json`
3. Or manually create:
   - Device 1: `centrifuge`, capacity=2
   - Device 2: `separator`, capacity=2  
   - Device 3: `quality`, capacity=1
   - 3 batches (each batch has 3 flows: cent→sep→qual)

### Step 2: Run BASELINE

1. Keep Quality at capacity=1
2. Click "Run Simulation"
3. **Write down the completion time** (should be around 35-40 minutes)

### Step 3: Test QUALITY (THE BOTTLENECK)

1. Change **Quality capacity: 1 → 2**
2. Click "Run Simulation"
3. **You WILL see MASSIVE improvement** (should drop to ~18-20 minutes)
4. **This is 50%+ faster!** ✅

### Step 4: Reset and Test CENTRIFUGE (NOT bottleneck)

1. Reset Quality back to capacity=1
2. Change **Centrifuge capacity: 2 → 4** (double it)
3. Click "Run Simulation"
4. **You will see ZERO improvement** (same ~35-40 minutes)
5. **This proves centrifuge is NOT the bottleneck!** ❌

---

## What You Should See

```
BASELINE (Cent=2, Sep=2, Qual=1):
  Time: ~2,400 seconds (40 min)

TEST 1 - Double Quality (Qual=1→2):
  Time: ~1,200 seconds (20 min)
  Improvement: 50% ✅ HUGE IMPACT!

TEST 2 - Double Centrifuge (Cent=2→4):
  Time: ~2,400 seconds (40 min)
  Improvement: 0% ❌ NO IMPACT!
```

---

## Why This Happens

**Quality (capacity=1):**
- Can only process 1 batch at a time
- Other batches queue up waiting
- Creates a BACKLOG
- This is the CONSTRAINT

**Centrifuge (capacity=2):**
- Can handle 2 batches simultaneously
- Processes fast (6-8 minutes)
- Never gets overwhelmed
- Has EXCESS capacity
- Adding more doesn't help!

---

## If It STILL Doesn't Work

**Check in the React UI results:**
1. Look for "simulation_time_seconds" field
2. Make sure it's CHANGING between tests
3. If it's always the same number (like 3387), then:
   - The config might not be updating
   - Check browser console for errors
   - Try refreshing the page

**Or tell me:**
- What exact numbers you're seeing
- Are they exactly the same?
- What devices/capacities you're testing

I'll help you debug it!
