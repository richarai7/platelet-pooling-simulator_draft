#!/usr/bin/env python3
"""
Script to generate realistic 3D shapes for platelet pooling lab devices.

This script creates appropriate geometries for each device type based on
their real-world appearance and updates the GLTF template file.
"""

import json
import base64
import struct
from typing import List, Tuple, Dict, Any
import math


def create_cube_vertices(width: float, height: float, depth: float) -> Tuple[List[float], List[float], List[int]]:
    """Create vertices for a box/cuboid shape."""
    w, h, d = width/2, height/2, depth/2

    positions = [
        # Front face
        -w, -h,  d,   w, -h,  d,   w,  h,  d,  -w,  h,  d,
        # Back face
        -w, -h, -d,  -w,  h, -d,   w,  h, -d,   w, -h, -d,
        # Top face
        -w,  h, -d,  -w,  h,  d,   w,  h,  d,   w,  h, -d,
        # Bottom face
        -w, -h, -d,   w, -h, -d,   w, -h,  d,  -w, -h,  d,
        # Right face
         w, -h, -d,   w,  h, -d,   w,  h,  d,   w, -h,  d,
        # Left face
        -w, -h, -d,  -w, -h,  d,  -w,  h,  d,  -w,  h, -d
    ]

    normals = [
        # Front
        0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1,
        # Back
        0, 0, -1,  0, 0, -1,  0, 0, -1,  0, 0, -1,
        # Top
        0, 1, 0,  0, 1, 0,  0, 1, 0,  0, 1, 0,
        # Bottom
        0, -1, 0,  0, -1, 0,  0, -1, 0,  0, -1, 0,
        # Right
        1, 0, 0,  1, 0, 0,  1, 0, 0,  1, 0, 0,
        # Left
        -1, 0, 0,  -1, 0, 0,  -1, 0, 0,  -1, 0, 0
    ]

    indices = []
    for i in range(6):  # 6 faces
        offset = i * 4
        indices.extend([offset, offset+1, offset+2, offset+2, offset+3, offset])

    return positions, normals, indices


def create_cylinder_vertices(radius: float, height: float, segments: int = 16) -> Tuple[List[float], List[float], List[int]]:
    """Create vertices for a cylinder shape."""
    positions = []
    normals = []
    indices = []

    h = height / 2

    # Top and bottom centers
    top_center_idx = 0
    bottom_center_idx = segments + 1

    # Top center
    positions.extend([0, h, 0])
    normals.extend([0, 1, 0])

    # Top ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        positions.extend([x, h, z])
        normals.extend([0, 1, 0])

    # Bottom center
    positions.extend([0, -h, 0])
    normals.extend([0, -1, 0])

    # Bottom ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        positions.extend([x, -h, z])
        normals.extend([0, -1, 0])

    # Side vertices (duplicated for proper normals)
    side_start_idx = len(positions) // 3
    for i in range(segments + 1):
        angle = 2 * math.pi * (i % segments) / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        nx = math.cos(angle)
        nz = math.sin(angle)

        # Top vertex
        positions.extend([x, h, z])
        normals.extend([nx, 0, nz])

        # Bottom vertex
        positions.extend([x, -h, z])
        normals.extend([nx, 0, nz])

    # Top cap indices
    for i in range(segments):
        indices.extend([top_center_idx, i + 1, ((i + 1) % segments) + 1])

    # Bottom cap indices
    for i in range(segments):
        indices.extend([bottom_center_idx, ((i + 1) % segments) + bottom_center_idx + 1, i + bottom_center_idx + 1])

    # Side indices
    for i in range(segments):
        base = side_start_idx + i * 2
        indices.extend([base, base + 1, base + 2])
        indices.extend([base + 1, base + 3, base + 2])

    return positions, normals, indices


def vertices_to_buffer(positions: List[float], normals: List[float], indices: List[int]) -> str:
    """Convert vertex data to base64-encoded binary buffer."""
    buffer_data = bytearray()

    # Pack positions (VEC3, float)
    for pos in positions:
        buffer_data.extend(struct.pack('<f', pos))

    # Pack normals (VEC3, float)
    for norm in normals:
        buffer_data.extend(struct.pack('<f', norm))

    # Pack indices (SCALAR, unsigned short)
    for idx in indices:
        buffer_data.extend(struct.pack('<H', idx))

    return base64.b64encode(buffer_data).decode('ascii')


def calculate_bounds(positions: List[float]) -> Tuple[List[float], List[float]]:
    """Calculate min and max bounds for positions."""
    num_vertices = len(positions) // 3
    x_vals = [positions[i*3] for i in range(num_vertices)]
    y_vals = [positions[i*3+1] for i in range(num_vertices)]
    z_vals = [positions[i*3+2] for i in range(num_vertices)]

    return [min(x_vals), min(y_vals), min(z_vals)], [max(x_vals), max(y_vals), max(z_vals)]


def create_device_geometries() -> Dict[str, Dict[str, Any]]:
    """Create geometry data for each device type."""
    devices = {}

    # 1. Buffy Coat Pack - small packet type (flat rectangular box)
    positions, normals, indices = create_cube_vertices(0.3, 0.1, 0.4)
    devices['buffy_coat_packs'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Small packet shape'
    }

    # 2. Platelet Washer - mini washing machine (compact box with slightly taller height)
    positions, normals, indices = create_cube_vertices(0.6, 0.8, 0.6)
    devices['platelet_washing'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Mini washing machine shape'
    }

    # 3. Centrifuge - top load washing machine (taller box, square base)
    positions, normals, indices = create_cube_vertices(0.8, 1.2, 0.8)
    devices['centrifuge'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Top-load washing machine shape'
    }

    # 4. Separator - cylinder shape machine
    positions, normals, indices = create_cylinder_vertices(0.4, 1.0, 16)
    devices['separator_macropress'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Cylindrical separator shape'
    }

    # 5. Resting Trolly - clinical trolly (wide, low rectangular platform)
    positions, normals, indices = create_cube_vertices(1.0, 0.4, 0.6)
    devices['resting_trolly'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Clinical trolly shape'
    }

    # 6. Agitator - Big fridge (tall, deep rectangular box)
    positions, normals, indices = create_cube_vertices(1.0, 1.8, 0.8)
    devices['agitator'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Big fridge shape'
    }

    # 7. Macropress - microwave type (wide, shallow box)
    positions, normals, indices = create_cube_vertices(0.8, 0.5, 0.6)
    devices['macropress'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Microwave shape'
    }

    # 8. Testing Agitator - Big fridge (same as agitator)
    positions, normals, indices = create_cube_vertices(1.0, 1.8, 0.8)
    devices['testing_agitator'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Big fridge shape'
    }

    # 9. Labeling - printing machine (medium box, desktop size)
    positions, normals, indices = create_cube_vertices(0.7, 0.5, 0.5)
    devices['labeling'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Printing machine shape'
    }

    # 10. Release - bench (long, low rectangular shape)
    positions, normals, indices = create_cube_vertices(1.5, 0.4, 0.5)
    devices['release'] = {
        'positions': positions,
        'normals': normals,
        'indices': indices,
        'description': 'Bench shape'
    }

    return devices


def update_gltf_with_shapes(gltf_path: str, output_path: str) -> None:
    """Update the GLTF file with new device shapes."""
    print("Loading GLTF template...")
    with open(gltf_path, 'r', encoding='utf-8') as f:
        gltf = json.load(f)

    print("Generating device geometries...")
    device_geometries = create_device_geometries()

    # Create new accessors, bufferViews, and buffers for each device
    new_accessors = []
    new_buffer_views = []
    all_buffers_data = bytearray()

    device_names = [
        'buffy_coat_packs', 'platelet_washing', 'centrifuge', 'separator_macropress',
        'resting_trolly', 'agitator', 'macropress', 'testing_agitator',
        'labeling', 'release'
    ]

    mesh_to_accessor = {}

    for mesh_idx, device_name in enumerate(device_names):
        if device_name not in device_geometries:
            print(f"Warning: No geometry for {device_name}, using default cube")
            continue

        geom = device_geometries[device_name]
        positions = geom['positions']
        normals = geom['normals']
        indices = geom['indices']

        print(f"  Processing {device_name}: {len(positions)//3} vertices, {len(indices)//3} triangles - {geom['description']}")

        # Calculate buffer offsets
        current_offset = len(all_buffers_data)

        # Pack positions
        positions_data = bytearray()
        for pos in positions:
            positions_data.extend(struct.pack('<f', pos))
        positions_length = len(positions_data)

        # Pack normals
        normals_data = bytearray()
        for norm in normals:
            normals_data.extend(struct.pack('<f', norm))
        normals_length = len(normals_data)

        # Pack indices
        indices_data = bytearray()
        for idx in indices:
            indices_data.extend(struct.pack('<H', idx))
        indices_length = len(indices_data)

        # Calculate bounds
        min_bounds, max_bounds = calculate_bounds(positions)

        # Create accessors for this mesh
        position_accessor_idx = len(new_accessors)
        new_accessors.append({
            "bufferView": len(new_buffer_views),
            "componentType": 5126,  # FLOAT
            "count": len(positions) // 3,
            "type": "VEC3",
            "max": max_bounds,
            "min": min_bounds
        })

        normal_accessor_idx = len(new_accessors)
        new_accessors.append({
            "bufferView": len(new_buffer_views) + 1,
            "componentType": 5126,  # FLOAT
            "count": len(normals) // 3,
            "type": "VEC3"
        })

        indices_accessor_idx = len(new_accessors)
        new_accessors.append({
            "bufferView": len(new_buffer_views) + 2,
            "componentType": 5123,  # UNSIGNED_SHORT
            "count": len(indices),
            "type": "SCALAR"
        })

        # Create buffer views
        new_buffer_views.append({
            "buffer": 0,
            "byteOffset": current_offset,
            "byteLength": positions_length,
            "target": 34962  # ARRAY_BUFFER
        })

        new_buffer_views.append({
            "buffer": 0,
            "byteOffset": current_offset + positions_length,
            "byteLength": normals_length,
            "target": 34962  # ARRAY_BUFFER
        })

        new_buffer_views.append({
            "buffer": 0,
            "byteOffset": current_offset + positions_length + normals_length,
            "byteLength": indices_length,
            "target": 34963  # ELEMENT_ARRAY_BUFFER
        })

        # Append to buffer
        all_buffers_data.extend(positions_data)
        all_buffers_data.extend(normals_data)
        all_buffers_data.extend(indices_data)

        # Store mapping for updating meshes
        mesh_to_accessor[mesh_idx] = {
            'position': position_accessor_idx,
            'normal': normal_accessor_idx,
            'indices': indices_accessor_idx
        }

    # Update meshes to use new accessors
    print("Updating mesh references...")
    for mesh_idx, mesh in enumerate(gltf['meshes']):
        if mesh_idx in mesh_to_accessor:
            accessor_refs = mesh_to_accessor[mesh_idx]
            mesh['primitives'][0]['attributes']['POSITION'] = accessor_refs['position']
            mesh['primitives'][0]['attributes']['NORMAL'] = accessor_refs['normal']
            mesh['primitives'][0]['indices'] = accessor_refs['indices']

    # Replace accessors, bufferViews, and buffers
    gltf['accessors'] = new_accessors
    gltf['bufferViews'] = new_buffer_views

    # Create base64-encoded buffer
    buffer_base64 = base64.b64encode(all_buffers_data).decode('ascii')
    gltf['buffers'] = [{
        "byteLength": len(all_buffers_data),
        "uri": f"data:application/octet-stream;base64,{buffer_base64}"
    }]

    print(f"Total buffer size: {len(all_buffers_data)} bytes")

    # Save updated GLTF
    print(f"Saving updated GLTF to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gltf, f, indent=2)

    print("✓ GLTF file successfully updated with realistic device shapes!")


def main():
    """Main function."""
    import sys

    script_dir = sys.path[0] if sys.path[0] else '.'
    gltf_input = f"{script_dir}/templates/platelet_lab_template.gltf"
    gltf_output = f"{script_dir}/templates/platelet_lab_template.gltf"

    print("=" * 70)
    print("3D Device Shape Generator for Platelet Pooling Lab")
    print("=" * 70)
    print()
    print("This script generates realistic 3D shapes for lab devices:")
    print("  • Buffy Coat Pack: Small packet")
    print("  • Platelet Washer: Mini washing machine")
    print("  • Centrifuge: Top-load washing machine")
    print("  • Separator: Cylinder shape")
    print("  • Resting Trolly: Clinical trolly")
    print("  • Agitator: Big fridge")
    print("  • Macropress: Microwave type")
    print("  • Testing Agitator: Big fridge")
    print("  • Labeling: Printing machine")
    print("  • Release: Bench")
    print()

    try:
        update_gltf_with_shapes(gltf_input, gltf_output)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 70)
    print("Next steps:")
    print("  1. Review the updated GLTF file")
    print("  2. Upload to Azure Blob Storage")
    print("  3. Test in Azure 3D Scenes Studio")
    print("=" * 70)


if __name__ == '__main__':
    main()
