"""
Scenario Multiplier Helper - Easily test capacity increases
"""
from typing import Dict, Any
import copy


def multiply_device_capacities(config: Dict[str, Any], multiplier: float) -> Dict[str, Any]:
    """
    Multiply all device capacities by a given multiplier.
    
    Args:
        config: Original simulation configuration
        multiplier: Factor to multiply capacities by (e.g., 2.0 for 200%, 1.5 for 150%)
    
    Returns:
        New configuration with adjusted capacities
    
    Example:
        # Double all capacities (200%)
        new_config = multiply_device_capacities(config, 2.0)
        
        # Triple all capacities (300%)
        new_config = multiply_device_capacities(config, 3.0)
        
        # 50% increase (150%)
        new_config = multiply_device_capacities(config, 1.5)
    """
    new_config = copy.deepcopy(config)
    
    for device in new_config.get('devices', []):
        original_capacity = device.get('capacity', 1)
        new_capacity = int(original_capacity * multiplier)
        # Ensure at least capacity of 1
        device['capacity'] = max(1, new_capacity)
    
    # Update scenario name to reflect change
    if 'scenario_name' in new_config:
        new_config['scenario_name'] = f"{new_config['scenario_name']}_x{multiplier}"
    else:
        new_config['scenario_name'] = f"multiplier_x{multiplier}"
    
    return new_config


def create_capacity_comparison(base_config: Dict[str, Any], 
                               multipliers: list = [1.0, 1.5, 2.0, 3.0]) -> list:
    """
    Create multiple scenario configurations with different capacity multipliers.
    
    Args:
        base_config: Original configuration
        multipliers: List of multipliers to test (default: 100%, 150%, 200%, 300%)
    
    Returns:
        List of configurations for comparison
    
    Example:
        scenarios = create_capacity_comparison(config, [1.0, 2.0, 3.0])
        # Returns: [baseline, 200% capacity, 300% capacity]
    """
    scenarios = []
    
    for mult in multipliers:
        scenario = multiply_device_capacities(base_config, mult)
        scenario['scenario_name'] = f"{int(mult * 100)}% Capacity"
        scenarios.append(scenario)
    
    return scenarios


def multiply_specific_device(config: Dict[str, Any], 
                            device_id: str, 
                            multiplier: float) -> Dict[str, Any]:
    """
    Multiply capacity of a SPECIFIC device only.
    
    Args:
        config: Original configuration
        device_id: ID of the device to modify (e.g., "centrifuge", "quality")
        multiplier: Capacity multiplier
    
    Returns:
        New configuration with adjusted device
    
    Example:
        # Only double quality check capacity
        new_config = multiply_specific_device(config, "quality", 2.0)
    """
    new_config = copy.deepcopy(config)
    
    for device in new_config.get('devices', []):
        if device.get('id') == device_id:
            original_capacity = device.get('capacity', 1)
            new_capacity = int(original_capacity * multiplier)
            device['capacity'] = max(1, new_capacity)
            break
    
    new_config['scenario_name'] = f"{device_id}_x{multiplier}"
    return new_config


if __name__ == "__main__":
    # Example usage
    base_config = {
        "devices": [
            {"id": "centrifuge", "type": "machine", "capacity": 2},
            {"id": "separator", "type": "machine", "capacity": 2},
            {"id": "quality", "type": "machine", "capacity": 1}
        ],
        "flows": [],
        "simulation": {"duration": 10000}
    }
    
    print("="*70)
    print("CAPACITY MULTIPLIER EXAMPLES")
    print("="*70)
    
    # Test 200% capacity (double everything)
    print("\n1. DOUBLE ALL CAPACITIES (200%):")
    doubled = multiply_device_capacities(base_config, 2.0)
    for device in doubled['devices']:
        print(f"   {device['id']}: {device['capacity']}")
    
    # Test 300% capacity (triple everything)  
    print("\n2. TRIPLE ALL CAPACITIES (300%):")
    tripled = multiply_device_capacities(base_config, 3.0)
    for device in tripled['devices']:
        print(f"   {device['id']}: {device['capacity']}")
    
    # Test specific device
    print("\n3. DOUBLE ONLY QUALITY:")
    quality_doubled = multiply_specific_device(base_config, "quality", 2.0)
    for device in quality_doubled['devices']:
        print(f"   {device['id']}: {device['capacity']}")
    
    # Create comparison scenarios
    print("\n4. CREATE COMPARISON SET:")
    scenarios = create_capacity_comparison(base_config, [1.0, 1.5, 2.0, 3.0])
    for scenario in scenarios:
        print(f"\n   {scenario['scenario_name']}:")
        for device in scenario['devices']:
            print(f"     {device['id']}: {device['capacity']}")
