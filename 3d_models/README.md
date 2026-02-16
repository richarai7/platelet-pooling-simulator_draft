# 3D Models for Azure 3D Scenes Studio

This directory contains 3D model files and utilities for visualizing your Platelet Pooling Lab in Azure 3D Scenes Studio.

## Directory Structure

```
3d_models/
├── README.md                          # This file
├── add_twin_metadata_to_gltf.py       # Script to add twin metadata to GLTF files
├── templates/
│   └── platelet_lab_template.gltf     # Sample GLTF model with all 10 devices
├── metadata/
│   └── twin_mapping.json              # Device-to-twin mapping configuration
└── textures/                          # Directory for texture files (optional)
```

## Quick Start

### Option 1: Use the Provided Template

The easiest way to get started is to use the provided template model:

```bash
# 1. The template is ready to use
# Located at: templates/platelet_lab_template.gltf

# 2. Upload to Azure (see instructions below)

# 3. Configure in 3D Scenes Studio
# Follow: ../docs/3D_SCENES_STUDIO_SETUP.md
```

### Option 2: Add Metadata to Your Own Model

If you have a custom 3D model:

```bash
# 1. Ensure your model is in GLTF or GLB format
# 2. Node names should match device IDs (see below)

# 3. Add twin metadata
python add_twin_metadata_to_gltf.py \
  your_model.gltf \
  metadata/twin_mapping.json \
  your_model_with_twins.gltf

# 4. Upload the output file to Azure
```

## Template Model Details

### What's Included

The `platelet_lab_template.gltf` file includes:

- **10 device nodes** - One for each device in the platelet pooling flow
- **Simple cube geometry** - Placeholder shapes (replace with detailed models)
- **Color-coded materials** - Different colors for each device type
- **Twin metadata** - Pre-configured in node 'extras' fields
- **Spatial layout** - Devices arranged in a 2x5 grid layout

### Device Layout

The template arranges devices spatially:

```
Row 1 (z=0): buffy_coat_packs → platelet_washing → centrifuge → separator_macropress → resting_trolly
             (x=0)              (x=2)              (x=4)        (x=6)                   (x=8)

Row 2 (z=2): agitator → macropress → testing_agitator → labeling → release
             (x=0)      (x=2)        (x=4)              (x=6)      (x=8)
```

All devices are at ground level (y=0).

## Required Node Names

Your 3D model must have nodes with these exact names to map to Digital Twins:

| Node Name              | Device Type  | Description                      |
|------------------------|--------------|----------------------------------|
| buffy_coat_packs       | material     | Initial blood product storage    |
| platelet_washing       | machine      | Washing and preparation          |
| centrifuge             | machine      | Separation by centrifugation     |
| separator_macropress   | machine      | Platelet separation              |
| resting_trolly         | material     | Temporary storage/resting        |
| agitator               | machine      | Mixing and agitation             |
| macropress             | machine      | Final pressing                   |
| testing_agitator       | machine      | Quality testing                  |
| labeling               | workstation  | Product labeling                 |
| release                | workstation  | Final release checkpoint         |

## Using the Metadata Script

### Basic Usage

```bash
python add_twin_metadata_to_gltf.py <input_gltf> <mapping_json> [output_gltf]
```

### Example

```bash
python add_twin_metadata_to_gltf.py \
  my_lab.gltf \
  metadata/twin_mapping.json \
  my_lab_with_twins.gltf
```

### What It Does

The script:
1. Reads your GLTF file
2. Reads the twin mapping configuration
3. Adds metadata to each node's 'extras' field:
   - `twinId`: The Digital Twin ID
   - `deviceType`: Device type (machine, material, workstation)
   - `location`: Physical location
   - `description`: Device description
   - `capacity`: Processing capacity
   - `dtmi`: DTDL model identifier
4. Adds position and rotation if not already present
5. Saves the enhanced GLTF file

### Output Example

After running the script, each node will have metadata like:

```json
{
  "name": "centrifuge",
  "translation": [4, 0, 0],
  "rotation": [0, 0, 0, 1],
  "extras": {
    "twinId": "centrifuge",
    "deviceType": "machine",
    "location": "Lab A - Station 3",
    "description": "Separation by centrifugation",
    "capacity": 2,
    "dtmi": "dtmi:platelet:Device;1"
  }
}
```

## Creating Your Own 3D Model

### Recommended Software

- **Blender** (Free, open source): [Download](https://www.blender.org/)
- **SketchUp** (Free for personal use): [Download](https://www.sketchup.com/)
- **3DS Max** (Professional): [Download](https://www.autodesk.com/products/3ds-max/)

### Modeling Guidelines

1. **Keep it simple**: Start with basic shapes
2. **Optimize polygon count**: Aim for < 50,000 triangles total
3. **Use appropriate scale**: 1 unit = 1 meter
4. **Name nodes correctly**: Must match device IDs exactly
5. **Test early**: Export and validate frequently

### Export Settings (Blender Example)

1. Select all device objects
2. File → Export → glTF 2.0
3. Settings:
   - Format: **glTF Embedded (.gltf)** or **glTF Binary (.glb)**
   - Include: **Selected Objects**
   - Transform: **+Y Up**
   - Geometry: **Apply Modifiers**
   - Material: **Export**
4. Export

### Validating Your GLTF

Use the official glTF Validator:

```bash
# Online: https://github.khronos.org/glTF-Validator/

# Or install locally
npm install -g gltf-validator

# Validate your file
gltf-validator your_model.gltf
```

## Uploading to Azure

### Step 1: Create Storage Account

```bash
az storage account create \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --location eastus \
  --sku Standard_LRS
```

### Step 2: Create Container

```bash
az storage container create \
  --account-name plateletmodels \
  --name models \
  --public-access blob
```

### Step 3: Upload Model

```bash
az storage blob upload \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf \
  --file templates/platelet_lab_template.gltf
```

### Step 4: Get URL

```bash
az storage blob url \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf
```

Save this URL - you'll need it for 3D Scenes Studio configuration.

## Twin Mapping Configuration

The `metadata/twin_mapping.json` file defines how 3D nodes map to Digital Twins:

```json
{
  "version": "1.0",
  "description": "Mapping between GLTF nodes and Azure Digital Twin IDs",
  "dtdl_version": "3",
  "model_id": "dtmi:platelet:Device;1",
  "mappings": [
    {
      "node_name": "centrifuge",
      "twin_id": "centrifuge",
      "device_type": "machine",
      "location": "Lab A - Station 3",
      "description": "Separation by centrifugation",
      "capacity": 2,
      "position": {"x": 4, "y": 0, "z": 0},
      "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
    }
    // ... more devices
  ]
}
```

### Customizing Mappings

Edit `metadata/twin_mapping.json` to:
- Change device positions
- Update descriptions
- Modify capacity values
- Add custom metadata fields

## Integration with Azure Digital Twins

### Prerequisites

Before using the 3D model, ensure:

1. **DTDL Models are uploaded**:
   ```bash
   az dt model create \
     --dt-name <your-adt-instance> \
     --models azure_integration/dtdl_models/Device.json
   ```

2. **Device twins are created with spatial properties**:
   ```bash
   python azure_integration/scripts/create_linear_flow_twins.py \
     --endpoint https://<your-adt-instance>.api.eus.digitaltwins.azure.net
   ```

3. **Twins have position and rotation properties**:
   - The enhanced Device DTDL model includes `position` and `rotation` fields
   - These are automatically set when creating twins with the updated script

## Troubleshooting

### Model Not Loading

**Problem**: GLTF file fails to load in 3D Scenes Studio

**Solutions**:
- Verify file is valid GLTF 2.0 (use gltf-validator)
- Check file size (must be < 100MB)
- Ensure blob storage URL is publicly accessible
- Test URL in browser: should download the file

### Nodes Not Found

**Problem**: Cannot find nodes to map to twins

**Solutions**:
- Check node names match exactly (case-sensitive)
- Verify nodes exist: open GLTF in text editor, search for `"nodes"`
- Use the metadata script to add node names if missing

### Metadata Not Working

**Problem**: Twin metadata not appearing in 3D Scenes Studio

**Solutions**:
- Verify 'extras' field was added to nodes
- Check JSON syntax is valid
- Re-upload the model after adding metadata

## Advanced Topics

### Adding Textures

1. Create a `textures/` directory
2. Add texture image files (PNG, JPG)
3. Reference textures in GLTF materials
4. Upload textures to the same blob container

### Animations

To add animations:
1. Create animations in your 3D software
2. Export with animations included
3. In 3D Scenes Studio, map animations to twin properties
4. Configure triggers (e.g., rotate when status="Processing")

### Multiple Scenes

Create different views:
- **Overview**: All devices visible
- **Lab A**: First 3 devices only
- **Lab B/C**: Specific lab areas
- **Process Flow**: Follow material through pipeline

## Resources

- **Complete Setup Guide**: [../docs/3D_SCENES_STUDIO_SETUP.md](../docs/3D_SCENES_STUDIO_SETUP.md)
- **Azure 3D Scenes Studio**: [Microsoft Docs](https://learn.microsoft.com/azure/digital-twins/concepts-3d-scenes-studio)
- **GLTF Specification**: [Khronos GLTF 2.0](https://www.khronos.org/gltf/)
- **Blender GLTF Guide**: [Blender Manual](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the complete setup guide
- Open an issue in the repository
- Contact the development team

## Next Steps

After preparing your 3D model:

1. ✅ **Upload to Azure Blob Storage**
2. ✅ **Follow the 3D Scenes Studio Setup Guide**
3. ✅ **Configure visual behaviors** for device status
4. ✅ **Test with simulation** to see real-time updates
5. 🔄 **Customize and enhance** the model for your needs

---

**Generated for**: Platelet Pooling Simulator - Azure Digital Twins Integration
**Model Type**: GLTF 2.0
**Target Platform**: Azure 3D Scenes Studio
**DTDL Version**: 3
