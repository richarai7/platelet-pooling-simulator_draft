# How to Run This Code

This guide provides step-by-step instructions for running the Platelet Pooling Simulator / Discrete Event Simulation Engine.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running Simulations](#running-simulations)
4. [Running the API Server](#running-the-api-server)
5. [Running the Web UI](#running-the-web-ui)
6. [Running Tests](#running-tests)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
  ```bash
  python --version  # Should show 3.9 or higher
  ```

### Optional (for UI/API features)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
  ```bash
  node --version  # Should show 16.x or higher
  ```

## Installation

### 1. Install Python Dependencies

Choose one of these methods:

#### Option A: Install Package (Recommended)
```bash
# Install the simulation engine package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

#### Option B: Install Requirements Only
```bash
# Install just the runtime dependencies
pip install -r requirements.txt
```

### 2. Install UI Dependencies (Optional)

If you want to run the web interface:

```bash
cd ui
npm install
cd ..
```

## Running Simulations

The simulation engine can be run in several ways:

### Method 1: Run Example Scripts

The `examples/` directory contains ready-to-run simulation examples:

#### Simple Debug Example (Quickest Test)
```bash
python examples/simple_debug.py
```

Expected output:
```
Expected: 3 flows (1 batch × 3 steps)
Total flows completed: 3
Total events: ...
Simulation time: ...s
```

#### Platelet Flow Simulation (Comprehensive Example)
```bash
python examples/platelet_flow_simulation.py
```

This will:
- Run a 12-hour platelet processing simulation
- Display detailed results
- Save output to `examples/platelet_flow_results.json`

#### Other Available Examples
```bash
# Compare centrifuge capacity scenarios
python examples/compare_centrifuge_capacity.py

# Analyze bottlenecks
python examples/bottleneck_analysis.py

# Perform what-if analysis
python examples/what_if_analysis.py

# See all examples
ls examples/*.py
```

### Method 2: Use the Simulation Engine Directly

Create your own Python script:

```python
from simulation_engine import SimulationEngine

# Define your configuration
config = {
    "simulation": {
        "duration": 10000,  # seconds
        "random_seed": 42,
        "execution_mode": "accelerated"
    },
    "devices": [
        {
            "id": "machine_1",
            "type": "machine",
            "capacity": 1,
            "recovery_time_range": (10, 20)
        }
    ],
    "flows": [
        {
            "flow_id": "process_1",
            "from_device": "machine_1",
            "to_device": "machine_1",
            "process_time_range": (100, 150),
            "priority": 1,
            "dependencies": None
        }
    ],
    "output_options": {
        "include_history": True,
        "include_events": True
    }
}

# Run the simulation
engine = SimulationEngine(config)
results = engine.run()

# Print results
print(f"Flows completed: {results['summary']['total_flows_completed']}")
print(f"Total events: {results['summary']['total_events']}")
```

Save as `my_simulation.py` and run:
```bash
python my_simulation.py
```

### Method 3: Interactive Python Session

```bash
python
```

Then in the Python REPL:
```python
>>> from simulation_engine import SimulationEngine
>>> config = {"simulation": {"duration": 1000, "random_seed": 42}, "devices": [], "flows": []}
>>> engine = SimulationEngine(config)
>>> results = engine.run()
>>> print(results['summary'])
```

## Running the API Server

The API server provides a REST interface for the simulation engine.

### 1. Install API Dependencies

```bash
pip install fastapi uvicorn
```

### 2. Start the API Server

```bash
# From the project root directory
cd api
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Access API Documentation

Open your browser to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get platelet template
curl http://localhost:8000/api/templates/platelet
```

## Running the Web UI

The web UI provides a visual interface for configuring and running simulations.

### 1. Ensure Dependencies are Installed

```bash
cd ui
npm install
```

### 2. Start the Development Server

```bash
npm run dev
```

The UI will be available at `http://localhost:5173`

### 3. Using the UI

1. Open `http://localhost:5173` in your browser
2. Load or create a simulation configuration
3. Run the simulation
4. View results and visualizations

**Note**: The UI requires the API server to be running (see previous section).

### Complete Setup (UI + API)

Terminal 1 - API Server:
```bash
cd api
uvicorn main:app --reload --port 8000
```

Terminal 2 - UI Development Server:
```bash
cd ui
npm run dev
```

Then open `http://localhost:5173` in your browser.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=simulation_engine --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest tests/test_simulation_engine.py

# Run tests matching a pattern
pytest -k "test_device"
```

### Run Type Checking

```bash
mypy src/
```

### Run Linting

```bash
pylint src/
```

### Run Code Formatting

```bash
# Check formatting
black --check src/ tests/

# Apply formatting
black src/ tests/
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'simulation_engine'`

**Solution**: Install the package:
```bash
pip install -e .
```

### SimPy Not Found

**Problem**: `ModuleNotFoundError: No module named 'simpy'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### API Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install FastAPI and Uvicorn:
```bash
pip install fastapi uvicorn
```

### UI Won't Start

**Problem**: `npm: command not found`

**Solution**: Install Node.js from https://nodejs.org/

**Problem**: `Cannot find module ...`

**Solution**: Install dependencies:
```bash
cd ui
npm install
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**: Use a different port:
```bash
# For API
uvicorn main:app --port 8001

# For UI (edit vite.config.ts to change port)
```

### Python Version Too Old

**Problem**: Features not working with Python < 3.9

**Solution**: Update Python:
- Download from https://www.python.org/downloads/
- Or use pyenv: `pyenv install 3.11`

## Quick Start Summary

**Fastest way to see the simulator in action:**

```bash
# 1. Install dependencies
pip install -e .

# 2. Run a quick example
python examples/simple_debug.py
```

**To run the full stack (UI + API):**

```bash
# Terminal 1: Install and start API
pip install fastapi uvicorn
cd api
uvicorn main:app --reload

# Terminal 2: Install and start UI
cd ui
npm install
npm run dev

# Open browser to http://localhost:5173
```

## Additional Resources

- **README.md**: Project overview and architecture
- **examples/HOW_TO_USE.md**: Detailed example usage guides
- **examples/CONFIG-TUTORIAL.md**: Configuration file tutorial
- **API Documentation**: http://localhost:8000/docs (when API is running)

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review error messages carefully
3. Ensure all prerequisites are installed
4. Check that you're in the correct directory
5. Try the simplest example first (`simple_debug.py`)

For configuration help, see `examples/CONFIG-TUTORIAL.md`
