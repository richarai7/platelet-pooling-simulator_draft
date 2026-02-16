from typing import Dict, Any


def get_platelet_template() -> Dict[str, Any]:
    """Return linear platelet processing flow configuration template.
    
    Based on the updated platelet flow with 10 devices in linear sequence:
    Buffy Coat packs → Platelet washing → Centrifuge → Separator Macropress → 
    Resting Trolly → Agitator → Macropress → Testing Agitator → Labeling → Release
    
    Times are in seconds.
    """
    return {
        "simulation": {
            "duration": 43200,  # 12 hours in seconds
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        
        "devices": [
            # Stage 1: Initial Material
            {
                "id": "buffy_coat_packs",
                "type": "material",
                "capacity": 10,
                "recovery_time_range": (60, 120)
            },
            # Stage 2: Washing
            {
                "id": "platelet_washing",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (180, 300)
            },
            # Stage 3: Centrifuge
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (180, 300)
            },
            # Stage 4: Separator Macropress
            {
                "id": "separator_macropress",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (120, 240)
            },
            # Stage 5: Resting
            {
                "id": "resting_trolly",
                "type": "material",
                "capacity": 15,
                "recovery_time_range": (30, 60)
            },
            # Stage 6: Agitator
            {
                "id": "agitator",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (90, 150)
            },
            # Stage 7: Macropress
            {
                "id": "macropress",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (120, 180)
            },
            # Stage 8: Testing Agitator
            {
                "id": "testing_agitator",
                "type": "machine",
                "capacity": 10,
                "recovery_time_range": (60, 120)
            },
            # Stage 9: Labeling
            {
                "id": "labeling",
                "type": "workstation",
                "capacity": 10,
                "recovery_time_range": (30, 60)
            },
            # Stage 10: Release
            {
                "id": "release",
                "type": "workstation",
                "capacity": 10,
                "recovery_time_range": (20, 40)
            }
        ],
        
        "flows": [
            # Linear flow through all 10 devices
            {
                "flow_id": "f1_buffy_to_washing",
                "from_device": "buffy_coat_packs",
                "to_device": "platelet_washing",
                "process_time_range": (200, 300),
                "priority": 1,
                "dependencies": None
            },
            {
                "flow_id": "f2_washing_to_centrifuge",
                "from_device": "platelet_washing",
                "to_device": "centrifuge",
                "process_time_range": (300, 480),
                "priority": 1,
                "dependencies": ["f1_buffy_to_washing"]
            },
            {
                "flow_id": "f3_centrifuge_to_separator",
                "from_device": "centrifuge",
                "to_device": "separator_macropress",
                "process_time_range": (400, 600),
                "priority": 1,
                "dependencies": ["f2_washing_to_centrifuge"]
            },
            {
                "flow_id": "f4_separator_to_resting",
                "from_device": "separator_macropress",
                "to_device": "resting_trolly",
                "process_time_range": (150, 250),
                "priority": 1,
                "dependencies": ["f3_centrifuge_to_separator"]
            },
            {
                "flow_id": "f5_resting_to_agitator",
                "from_device": "resting_trolly",
                "to_device": "agitator",
                "process_time_range": (300, 450),
                "priority": 1,
                "dependencies": ["f4_separator_to_resting"]
            },
            {
                "flow_id": "f6_agitator_to_macropress",
                "from_device": "agitator",
                "to_device": "macropress",
                "process_time_range": (200, 350),
                "priority": 1,
                "dependencies": ["f5_resting_to_agitator"]
            },
            {
                "flow_id": "f7_macropress_to_testing",
                "from_device": "macropress",
                "to_device": "testing_agitator",
                "process_time_range": (250, 400),
                "priority": 1,
                "dependencies": ["f6_agitator_to_macropress"]
            },
            {
                "flow_id": "f8_testing_to_labeling",
                "from_device": "testing_agitator",
                "to_device": "labeling",
                "process_time_range": (120, 200),
                "priority": 1,
                "dependencies": ["f7_macropress_to_testing"]
            },
            {
                "flow_id": "f9_labeling_to_release",
                "from_device": "labeling",
                "to_device": "release",
                "process_time_range": (100, 150),
                "priority": 1,
                "dependencies": ["f8_testing_to_labeling"]
            }
        ],
        
        "gates": {
            "QC_Pass": True,  # Quality control gate
            "Sterile_Conditions": True,
            "Temperature_Control": True
        },
        
        "output_options": {
            "include_events": True,
            "include_history": True
        }
    }


def get_multi_batch_template(num_batches: int = 5, batch_interval: int = 600) -> Dict[str, Any]:
    """Return multi-batch platelet processing configuration.
    
    This generates a configuration with multiple batches competing for device capacity,
    demonstrating the impact of bottlenecks and capacity changes.
    
    Args:
        num_batches: Number of batches to process (default: 5)
        batch_interval: Time in seconds between batch arrivals (default: 600 = 10 min)
    
    Returns:
        Configuration dict with multiple batches
    """
    import copy
    
    # Get base template
    base_config = get_platelet_template()
    base_flows = base_config['flows']
    
    # Create multi-batch config with same devices
    multi_batch_config = {
        "simulation": base_config["simulation"],
        "devices": base_config["devices"],
        "flows": [],
        "gates": base_config.get("gates", {}),
        "output_options": base_config.get("output_options", {})
    }
    
    # Generate flows for each batch
    all_batch_flows = []
    for batch_num in range(1, num_batches + 1):
        batch_id = f"batch_{batch_num:03d}"
        batch_start_time = (batch_num - 1) * batch_interval
        
        # Create mapping from old flow IDs to new flow IDs for this batch
        flow_id_mapping = {}
        
        for flow_idx, base_flow in enumerate(base_flows):
            # Create new flow ID for this batch
            new_flow_id = f"{batch_id}_flow_{flow_idx + 1:02d}"
            old_flow_id = base_flow['flow_id']
            flow_id_mapping[old_flow_id] = new_flow_id
            
            # Copy flow and update IDs
            new_flow = copy.deepcopy(base_flow)
            new_flow['flow_id'] = new_flow_id
            new_flow['batch_id'] = batch_id
            
            # Update dependencies to reference flows within same batch
            if base_flow.get('dependencies'):
                new_flow['dependencies'] = [
                    flow_id_mapping.get(dep_id, dep_id)
                    for dep_id in base_flow['dependencies']
                ]
            
            # For the first flow in each batch, add a delay to stagger arrivals
            if not base_flow.get('dependencies'):
                new_flow['arrival_time'] = batch_start_time
            
            all_batch_flows.append(new_flow)
    
    multi_batch_config['flows'] = all_batch_flows
    
    return multi_batch_config
