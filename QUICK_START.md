# Quick Start Guide

Get the Platelet Pooling Simulator running in 2 minutes!

## Step 1: Install Python Package

```bash
pip install -e .
```

## Step 2: Verify Installation

```bash
# Test that the package is installed
python -c "from simulation_engine import SimulationEngine; print('✓ Installation successful!')"
```

## Step 3: Run Your First Simulation

### Option A: Run a Unit Test

```bash
python -m pytest tests/unit/test_event_scheduler.py::TestEventScheduler::test_empty_scheduler_has_no_events -v
```

### Option B: Run a Python One-Liner

```bash
python -c "from simulation_engine import SimulationEngine; config={'simulation':{'duration':100,'random_seed':42,'execution_mode':'accelerated'},'devices':[],'flows':[],'output_options':{'include_history':False,'include_events':False}}; results=SimulationEngine(config).run(); print(f'✓ Simulation complete! Events: {results[\"summary\"][\"total_events\"]}')"
```

### Option C: Create a Python Script

Create a file called `test_sim.py`:

```python
from simulation_engine import SimulationEngine

config = {
    "simulation": {
        "duration": 100,
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    "devices": [],
    "flows": [],
    "output_options": {
        "include_history": False,
        "include_events": False
    }
}

engine = SimulationEngine(config)
results = engine.run()

print(f"✓ Simulation successful!")
print(f"Total events: {results['summary']['total_events']}")
print(f"Execution time: {results['summary']['execution_time_seconds']:.3f}s")
```

Then run it:

```bash
python test_sim.py
```

## What's Next?

You now have a working simulation engine! Here are some next steps:

1. **Learn More**: See [HOW_TO_RUN.md](HOW_TO_RUN.md) for detailed instructions
2. **Run the API**: See [HOW_TO_RUN.md#running-the-api-server](HOW_TO_RUN.md#running-the-api-server)
3. **Explore Examples**: Check the `examples/` directory for more complex simulations
4. **Read the Docs**: See [README.md](README.md) for architecture and features

## Troubleshooting

**Import Error?**
```bash
# Make sure you installed with -e flag
pip install -e .
```

**Missing SimPy?**
```bash
pip install simpy
```

**Still Having Issues?**

Check the full guide: [HOW_TO_RUN.md](HOW_TO_RUN.md#troubleshooting)
