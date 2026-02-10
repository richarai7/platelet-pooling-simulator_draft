"""
SIMPLE EXPLANATION: How Device Failures Work

Shows the recovery mechanism step-by-step
"""

print("\n" + "=" * 80)
print("HOW DEVICE FAILURES & RECOVERY WORK IN THE SIMULATOR")
print("=" * 80)

print("""
SCENARIO: Centrifuge breaks down during platelet processing

┌─────────────────────────────────────────────────────────────────────────┐
│ TIMELINE OF EVENTS                                                      │
└─────────────────────────────────────────────────────────────────────────┘

T=0 min     🟢 Centrifuge is IDLE (ready to work)
            • Batch 1 arrives
            • Centrifuge starts processing

T=2 min     🟡 Centrifuge is PROCESSING (working on Batch 1)
            • Batch 2 arrives
            • Batch 2 waits (centrifuge at capacity)

T=4 min     🔴 DEVICE FAILURE! Centrifuge FAILED
            • Work on Batch 1 interrupted
            • Batch 1 stays in queue (doesn't disappear!)
            • Batch 2 still waiting
            • System automatically schedules recovery

            ⏰ Recovery scheduled: 3-5 minutes (random)
            
            ⏳ WAITING... (centrifuge unavailable)

T=8 min     🔧 DEVICE RECOVERED! Centrifuge back to IDLE
            • Centrifuge ready again
            • Batch 1 resumes automatically
            • System picks up where it left off

T=10 min    ✅ Batch 1 completes
            • Batch 2 starts processing
            • Back to normal operation

┌─────────────────────────────────────────────────────────────────────────┐
│ IMPACT ON THROUGHPUT                                                    │
└─────────────────────────────────────────────────────────────────────────┘

Without failure:  Batch 1 done at T=8 min
With failure:     Batch 1 done at T=10 min
                  ─────────────────────────
                  DELAY: 2 minutes


┌─────────────────────────────────────────────────────────────────────────┐
│ STATE TRANSITIONS                                                       │
└─────────────────────────────────────────────────────────────────────────┘

Device State Flow:
  IDLE ──START_PROCESSING──> PROCESSING ──DEVICE_FAILED──> FAILED
                                                              │
                                                              │
                                    IDLE <──RECOVERY_COMPLETE─┘

Work stays in the system! Nothing is lost during failure.


┌─────────────────────────────────────────────────────────────────────────┐
│ WHAT YOU CONTROL                                                        │
└─────────────────────────────────────────────────────────────────────────┘

In your device configuration:

{
    "id": "centrifuge",
    "capacity": 2,                      ← How many batches at once
    "recovery_time_range": (180, 300)   ← 3-5 min to fix when it breaks
}

• Shorter recovery time = Less downtime
• Higher capacity = More resilience (backup machines running)


┌─────────────────────────────────────────────────────────────────────────┐
│ REAL-WORLD EXAMPLES                                                     │
└─────────────────────────────────────────────────────────────────────────┘

recovery_time_range: (30, 60)    = "Quick fix" (minor jam, reset button)
recovery_time_range: (180, 300)  = "Medium fix" (technician call, 3-5 min)
recovery_time_range: (600, 1800) = "Major fix" (repair needed, 10-30 min)


┌─────────────────────────────────────────────────────────────────────────┐
│ WHY BACKUP MACHINES HELP                                                │
└─────────────────────────────────────────────────────────────────────────┘

1 Centrifuge (capacity=1):
  ❌ If it fails → EVERYTHING stops

2 Centrifuges (capacity=2):  
  ✅ If one fails → Other one keeps working!
  ⚠️  50% capacity during failure
  
3 Centrifuges (capacity=3):
  ✅✅ If one fails → Still have 66% capacity!
  💪 More resilient to failures


┌─────────────────────────────────────────────────────────────────────────┐
│ HOW TO TEST FAILURE SCENARIOS                                           │
└─────────────────────────────────────────────────────────────────────────┘

Option 1: Adjust recovery_time_range in your config
  • Longer recovery = Simulates more severe failures
  • Compare baseline vs long-recovery scenario

Option 2: Reduce capacity then compare
  • Simulate "one machine down" by reducing capacity
  • Example: capacity 3→2 = one machine failed permanently

Option 3: Run Monte Carlo simulations
  • Run same scenario 100 times
  • Randomness in recovery times shows variance
  • See best/worst case outcomes

""")

print("=" * 80)
print("\n✅ The simulator AUTOMATICALLY handles recovery!")
print("   You don't need to code anything - just set recovery_time_range\n")
print("=" * 80 + "\n")
