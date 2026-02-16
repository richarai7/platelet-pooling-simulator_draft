#!/usr/bin/env python3
"""
Script to add Azure Digital Twin metadata to GLTF model files.

This script reads a GLTF file and a twin mapping configuration, then adds
the appropriate metadata to each node's 'extras' field for compatibility
with Azure 3D Scenes Studio.

Usage:
    python add_twin_metadata_to_gltf.py <input_gltf> <mapping_json> [output_gltf]

Example:
    python add_twin_metadata_to_gltf.py my_lab.gltf twin_mapping.json my_lab_with_twins.gltf
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_json(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved to: {file_path}")


def add_twin_metadata(gltf_data: Dict[str, Any], mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add Azure Digital Twin metadata to GLTF nodes.

    Args:
        gltf_data: Parsed GLTF JSON data
        mappings: Twin mapping configuration

    Returns:
        Modified GLTF data with twin metadata
    """
    # Create a lookup dictionary for quick access
    mapping_lookup = {
        mapping['node_name']: mapping
        for mapping in mappings.get('mappings', [])
    }

    nodes_updated = 0
    nodes_skipped = 0

    # Process each node in the GLTF
    for node in gltf_data.get('nodes', []):
        node_name = node.get('name', '')

        if node_name in mapping_lookup:
            mapping = mapping_lookup[node_name]

            # Add or update the 'extras' field
            if 'extras' not in node:
                node['extras'] = {}

            # Add twin metadata
            node['extras']['twinId'] = mapping['twin_id']
            node['extras']['deviceType'] = mapping['device_type']
            node['extras']['location'] = mapping['location']
            node['extras']['description'] = mapping['description']
            node['extras']['capacity'] = mapping['capacity']
            node['extras']['dtmi'] = mappings.get('model_id', 'dtmi:platelet:Device;1')

            # Add position if not already in node
            if 'translation' not in node and 'position' in mapping:
                pos = mapping['position']
                node['translation'] = [pos['x'], pos['y'], pos['z']]

            # Add rotation if not already in node
            if 'rotation' not in node and 'rotation' in mapping:
                rot = mapping['rotation']
                node['rotation'] = [rot['x'], rot['y'], rot['z'], rot['w']]

            nodes_updated += 1
            print(f"  ✓ Updated node: {node_name} -> twin: {mapping['twin_id']}")
        else:
            nodes_skipped += 1
            if node_name:
                print(f"  ⚠ Skipped node: {node_name} (no mapping found)")

    print(f"\nSummary:")
    print(f"  Nodes updated: {nodes_updated}")
    print(f"  Nodes skipped: {nodes_skipped}")

    return gltf_data


def main():
    """Main function to process command line arguments and execute the script."""
    if len(sys.argv) < 3:
        print("Error: Missing required arguments")
        print("\nUsage:")
        print("  python add_twin_metadata_to_gltf.py <input_gltf> <mapping_json> [output_gltf]")
        print("\nExample:")
        print("  python add_twin_metadata_to_gltf.py my_lab.gltf twin_mapping.json my_lab_with_twins.gltf")
        sys.exit(1)

    input_gltf = sys.argv[1]
    mapping_json = sys.argv[2]
    output_gltf = sys.argv[3] if len(sys.argv) > 3 else input_gltf.replace('.gltf', '_with_twins.gltf')

    # Validate input files exist
    if not Path(input_gltf).exists():
        print(f"Error: Input GLTF file not found: {input_gltf}")
        sys.exit(1)

    if not Path(mapping_json).exists():
        print(f"Error: Mapping JSON file not found: {mapping_json}")
        sys.exit(1)

    print("=" * 70)
    print("Azure Digital Twin Metadata Injector for GLTF Models")
    print("=" * 70)
    print(f"\nInput GLTF: {input_gltf}")
    print(f"Mapping file: {mapping_json}")
    print(f"Output GLTF: {output_gltf}")
    print()

    # Load the files
    print("Loading files...")
    try:
        gltf_data = load_json(input_gltf)
        print(f"  ✓ Loaded GLTF: {len(gltf_data.get('nodes', []))} nodes")
    except Exception as e:
        print(f"  ✗ Error loading GLTF: {e}")
        sys.exit(1)

    try:
        mapping_data = load_json(mapping_json)
        print(f"  ✓ Loaded mappings: {len(mapping_data.get('mappings', []))} device mappings")
    except Exception as e:
        print(f"  ✗ Error loading mappings: {e}")
        sys.exit(1)

    # Add metadata
    print("\nProcessing nodes...")
    try:
        updated_gltf = add_twin_metadata(gltf_data, mapping_data)
    except Exception as e:
        print(f"  ✗ Error processing nodes: {e}")
        sys.exit(1)

    # Save the result
    print(f"\nSaving output...")
    try:
        save_json(updated_gltf, output_gltf)
    except Exception as e:
        print(f"  ✗ Error saving output: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✓ GLTF file successfully updated with Azure Digital Twin metadata!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Upload the GLTF file to Azure Blob Storage")
    print("  2. Open Azure Digital Twins instance in Azure Portal")
    print("  3. Navigate to '3D Scenes Studio (Preview)'")
    print("  4. Create a new scene and upload this GLTF file")
    print("  5. Map each 3D element to its corresponding Digital Twin")
    print()


if __name__ == '__main__':
    main()
