"""Test fixtures with multi-domain scenario configurations."""

# Healthcare - Platelet Pooling
HEALTHCARE_CONFIG = {
    "simulation": {"duration": 129600, "random_seed": 42},  # 36 hours
    "devices": [
        {
            "id": "centrifuge_001",
            "type": "centrifuge",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (300, 600)
        },
        {
            "id": "pooling_station",
            "type": "workstation",
            "capacity": 2,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "spin_platelets",
            "from_device": "centrifuge_001",
            "to_device": "pooling_station",
            "process_time_range": (1800, 2400),
            "priority": 10,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": True}
}

# Manufacturing - Assembly Line
MANUFACTURING_CONFIG = {
    "simulation": {"duration": 28800, "random_seed": 123},  # 8 hours
    "devices": [
        {
            "id": "cnc_mill_01",
            "type": "cnc_machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (600, 1200)
        },
        {
            "id": "assembly_bench",
            "type": "workstation",
            "capacity": 3,
            "initial_state": "Idle",
            "recovery_time_range": (180, 300)
        }
    ],
    "flows": [
        {
            "flow_id": "mill_part",
            "from_device": "cnc_mill_01",
            "to_device": "assembly_bench",
            "process_time_range": (300, 450),
            "priority": 5,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": False, "include_events": True}
}

# Logistics - Warehouse Operations
LOGISTICS_CONFIG = {
    "simulation": {"duration": 86400, "random_seed": 999},  # 24 hours
    "devices": [
        {
            "id": "forklift_a",
            "type": "forklift",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": (120, 300)
        },
        {
            "id": "loading_dock",
            "type": "dock",
            "capacity": 5,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "transport_pallet",
            "from_device": "forklift_a",
            "to_device": "loading_dock",
            "process_time_range": (180, 360),
            "priority": 1,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": False}
}

# Simple 2-device test scenario
SIMPLE_2_DEVICE_CONFIG = {
    "simulation": {"duration": 100.0, "random_seed": 42},
    "devices": [
        {
            "id": "device_a",
            "type": "machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None
        },
        {
            "id": "device_b",
            "type": "machine",
            "capacity": 1,
            "initial_state": "Idle",
            "recovery_time_range": None
        }
    ],
    "flows": [
        {
            "flow_id": "flow_ab",
            "from_device": "device_a",
            "to_device": "device_b",
            "process_time_range": (10.0, 20.0),
            "priority": 1,
            "dependencies": None
        }
    ],
    "output_options": {"include_history": True, "include_events": True}
}
