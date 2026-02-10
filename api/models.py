from typing import Optional, List, Tuple, Dict, Any, Literal
from pydantic import BaseModel, field_validator
from datetime import datetime


class DeviceModel(BaseModel):
    id: str
    type: str
    capacity: int
    initial_state: Literal["idle", "busy", "recovering", "failed"] = "idle"
    recovery_time_range: Optional[Tuple[float, float]] = None

    @field_validator('capacity')
    @classmethod
    def capacity_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('capacity must be >= 1')
        return v

    @field_validator('recovery_time_range')
    @classmethod
    def recovery_time_range_valid(cls, v):
        if v is not None:
            if len(v) != 2:
                raise ValueError('recovery_time_range must have exactly 2 elements')
            if v[0] > v[1]:
                raise ValueError('recovery_time_range min must be <= max')
        return v


class FlowModel(BaseModel):
    flow_id: str
    from_device: str
    to_device: str
    process_time_range: Tuple[float, float]
    priority: int = 1
    dependencies: Optional[List[str]] = None

    @field_validator('process_time_range')
    @classmethod
    def process_time_range_valid(cls, v):
        if len(v) != 2:
            raise ValueError('process_time_range must have exactly 2 elements')
        if v[0] >= v[1]:
            raise ValueError('process_time_range min must be < max')
        return v


class SimulationConfigModel(BaseModel):
    simulation: Dict[str, Any]
    devices: List[DeviceModel]
    flows: List[FlowModel]
    output_options: Dict[str, Any]


class ScenarioCreateRequest(BaseModel):
    name: str
    description: str
    config: Dict[str, Any]
    tags: Optional[List[str]] = None


class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: str
    config: Dict[str, Any]
    created_at: str
    updated_at: str
    tags: Optional[List[str]] = None


class SimulationRunRequest(BaseModel):
    config: Dict[str, Any]


class SimulationResultsResponse(BaseModel):
    results: Dict[str, Any]
