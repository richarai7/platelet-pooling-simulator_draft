from typing import Dict, Any


def get_platelet_template() -> Dict[str, Any]:
    """Return complex platelet processing flow configuration template.
    
    Based on the platelet flow diagram with pre-pooling, pooling, and final processing stages.
    Includes 11 devices, 11 flows with dependencies, and 3 quality gates.
    Times are in seconds.
    """
    return {
        "simulation": {
            "duration": 43200,  # 12 hours in seconds
            "random_seed": 42,
            "execution_mode": "accelerated"
        },
        
        "devices": [
            # Pre-Processing Stage
            {
                "id": "centrifuge",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support (5 batches × 2 flows each)
                "recovery_time_range": (180, 300)  # 3-5 minutes
            },
            {
                "id": "platelet_separator",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (120, 180)
            },
            
            # Pooling Stage - Main Process
            {
                "id": "pooling_station",
                "type": "workstation",
                "capacity": 15,  # Optimized for multi-batch support (receives 2 flows per batch)
                "recovery_time_range": (60, 120)
            },
            {
                "id": "weigh_register",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (30, 60)
            },
            {
                "id": "sterile_connect",
                "type": "workstation",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (45, 90)
            },
            
            # Testing Stage
            {
                "id": "test_sample",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (60, 90)
            },
            {
                "id": "quality_check",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (30, 60)
            },
            
            # Storage and Labeling
            {
                "id": "label_station",
                "type": "workstation",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (20, 40)
            },
            {
                "id": "storage_unit",
                "type": "material",
                "capacity": 50,  # Can hold multiple units
                "recovery_time_range": (10, 20)
            },
            
            # Final Processing
            {
                "id": "final_inspection",
                "type": "machine",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (45, 75)
            },
            {
                "id": "packaging_station",
                "type": "workstation",
                "capacity": 10,  # Optimized for multi-batch support
                "recovery_time_range": (30, 60)
            }
        ],
        
        "flows": [
            # Stage 1: Pre-Processing
            {
                "flow_id": "f1_centrifuge_to_separator",
                "from_device": "centrifuge",
                "to_device": "platelet_separator",
                "process_time_range": (300, 480),  # 5-8 minutes
                "priority": 1,
                "dependencies": None
            },
            
            # Stage 2: Separation to Pooling
            {
                "flow_id": "f2_separator_to_pooling",
                "from_device": "platelet_separator",
                "to_device": "pooling_station",
                "process_time_range": (600, 900),  # 10-15 minutes
                "priority": 1,
                "dependencies": ["f1_centrifuge_to_separator"]
            },
            
            # Stage 3: Pooling Process
            {
                "flow_id": "f3_pooling_to_weigh",
                "from_device": "pooling_station",
                "to_device": "weigh_register",
                "process_time_range": (420, 600),  # 7-10 minutes
                "priority": 1,
                "dependencies": ["f2_separator_to_pooling"]
            },
            
            # Stage 4: Weight Registration to Sterile Connect
            {
                "flow_id": "f4_weigh_to_sterile",
                "from_device": "weigh_register",
                "to_device": "sterile_connect",
                "process_time_range": (240, 360),  # 4-6 minutes
                "priority": 1,
                "dependencies": ["f3_pooling_to_weigh"]
            },
            
            # Stage 5: Sterile Connect to Testing
            {
                "flow_id": "f5_sterile_to_test",
                "from_device": "sterile_connect",
                "to_device": "test_sample",
                "process_time_range": (180, 300),  # 3-5 minutes
                "priority": 1,
                "dependencies": ["f4_weigh_to_sterile"]
            },
            
            # Stage 6: Testing to Quality Check
            {
                "flow_id": "f6_test_to_qc",
                "from_device": "test_sample",
                "to_device": "quality_check",
                "process_time_range": (360, 600),  # 6-10 minutes
                "priority": 1,
                "dependencies": ["f5_sterile_to_test"]
            },
            
            # Stage 7: QC to Labeling (if pass)
            {
                "flow_id": "f7_qc_to_label",
                "from_device": "quality_check",
                "to_device": "label_station",
                "process_time_range": (120, 240),  # 2-4 minutes
                "priority": 1,
                "dependencies": ["f6_test_to_qc"],
                "required_gates": ["QC_Pass"]  # Only if QC passes
            },
            
            # Stage 8: Labeling to Storage
            {
                "flow_id": "f8_label_to_storage",
                "from_device": "label_station",
                "to_device": "storage_unit",
                "process_time_range": (60, 120),  # 1-2 minutes
                "priority": 1,
                "dependencies": ["f7_qc_to_label"]
            },
            
            # Stage 9: Storage to Final Inspection
            {
                "flow_id": "f9_storage_to_inspection",
                "from_device": "storage_unit",
                "to_device": "final_inspection",
                "process_time_range": (180, 300),  # 3-5 minutes
                "priority": 1,
                "dependencies": ["f8_label_to_storage"]
            },
            
            # Stage 10: Final Inspection to Packaging
            {
                "flow_id": "f10_inspection_to_packaging",
                "from_device": "final_inspection",
                "to_device": "packaging_station",
                "process_time_range": (240, 360),  # 4-6 minutes
                "priority": 1,
                "dependencies": ["f9_storage_to_inspection"]
            },
            
            # Parallel flow: Direct pooling (if eligible)
            {
                "flow_id": "f11_direct_pool",
                "from_device": "centrifuge",
                "to_device": "pooling_station",
                "process_time_range": (480, 720),  # 8-12 minutes (faster path)
                "priority": 2,
                "dependencies": None
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
