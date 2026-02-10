"""
Discrete Event Simulation Engine

Domain-agnostic simulation engine for operational workflow modeling.
"""

__version__ = "0.1.0"

# Core exports
from simulation_engine.engine import SimulationEngine
from simulation_engine.repository import ScenarioRepository, ResultsRepository

__all__ = ["SimulationEngine", "ScenarioRepository", "ResultsRepository"]
from simulation_engine.config_manager import SimulationConfig, DeviceConfig, FlowConfig

__all__ = [
    "SimulationEngine",
    "SimulationConfig",
    "DeviceConfig",
    "FlowConfig",
]
