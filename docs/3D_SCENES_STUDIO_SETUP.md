# Azure 3D Scenes Studio Setup Guide

## Overview

This guide walks you through setting up a 3D visualization of your Platelet Pooling Lab in Azure 3D Scenes Studio, integrated with Azure Digital Twins.

## What is Azure 3D Scenes Studio?

Azure 3D Scenes Studio is a feature of Azure Digital Twins that allows you to:
- Visualize your Digital Twin graph in an interactive 3D environment
- See real-time property updates on 3D models
- Monitor device status changes with visual indicators
- Navigate through your digital representation of physical spaces

## Prerequisites

Before you begin, ensure you have:

1. **Azure Resources**
   - Azure Digital Twins instance (already deployed)
   - Azure Storage Account (for hosting GLTF model)
   - Appropriate role assignments (Azure Digital Twins Data Reader or Owner)

2. **3D Model**
   - GLTF or GLB file of your lab (template provided in this directory)
   - Model must have uniquely named nodes matching your device IDs

3. **Digital Twins**
   - Device twins already created in your ADT instance
   - DTDL models uploaded (Device.json with spatial properties)

## Quick Start

### Option 1: Use the Provided Template

We've created a basic GLTF template with simple cube representations for each device:

```bash
# The template is located at:
3d_models/templates/platelet_lab_template.gltf

# This template includes:
# - All 10 devices as colored cubes
# - Proper node names matching twin IDs
# - Twin metadata in node 'extras' fields
# - Spatial positioning in a linear layout
```

### Option 2: Create Your Own Model

If you have a custom 3D model of your lab:

1. **Export from your 3D software** (Blender, 3DS Max, SketchUp, etc.)
   - Export as GLTF 2.0 or GLB format
   - Name each device mesh/node to match the twin ID
   - Keep file size under 100MB for best performance

2. **Add twin metadata** using our script:
   ```bash
   cd 3d_models
   python add_twin_metadata_to_gltf.py \
     your_model.gltf \
     metadata/twin_mapping.json \
     your_model_with_twins.gltf
   ```

## Step-by-Step Setup

### Step 1: Prepare Your 3D Model

If you're using your own model, ensure each device is a separate named node:

**Required Node Names:**
- `buffy_coat_packs`
- `platelet_washing`
- `centrifuge`
- `separator_macropress`
- `resting_trolly`
- `agitator`
- `macropress`
- `testing_agitator`
- `labeling`
- `release`

### Step 2: Upload Model to Azure Blob Storage

```bash
# Create a storage account (if you don't have one)
az storage account create \
  --name plateletmodels \
  --resource-group <your-resource-group> \
  --location eastus \
  --sku Standard_LRS

# Create a container
az storage container create \
  --account-name plateletmodels \
  --name models \
  --public-access blob

# Upload your GLTF file
az storage blob upload \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf \
  --file 3d_models/templates/platelet_lab_template.gltf

# Get the URL
az storage blob url \
  --account-name plateletmodels \
  --container-name models \
  --name platelet_lab.gltf
```

Save the blob URL - you'll need it in the next step.

### Step 3: Update Digital Twin Models

Ensure your Device twins have the enhanced DTDL model with spatial properties:

```bash
# Re-upload the updated Device model
az dt model create \
  --dt-name <your-adt-instance> \
  --models azure_integration/dtdl_models/Device.json
```

### Step 4: Update Twins with Spatial Properties

Run the updated twin creation script to add position and rotation data:

```bash
python azure_integration/scripts/create_linear_flow_twins.py \
  --endpoint https://<your-adt-instance>.api.eus.digitaltwins.azure.net \
  --update-spatial-properties
```

Or manually update each twin with position data:

```bash
az dt twin update \
  --dt-name <your-adt-instance> \
  --twin-id buffy_coat_packs \
  --json-patch '[
    {
      "op": "add",
      "path": "/position",
      "value": {"x": 0, "y": 0, "z": 0}
    },
    {
      "op": "add",
      "path": "/rotation",
      "value": {"x": 0, "y": 0, "z": 0, "w": 1}
    }
  ]'
```

### Step 5: Access 3D Scenes Studio

1. Open the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure Digital Twins instance
3. In the left menu, click on **"3D Scenes Studio (Preview)"**

### Step 6: Create a New Scene

1. Click **"Create new scene"** or **"New scene"**
2. Enter scene details:
   - **Name**: Platelet Pooling Lab
   - **Description**: Real-time visualization of platelet processing devices
3. Click **"Create"**

### Step 7: Upload 3D Model

1. In the scene editor, click **"Add 3D environment"**
2. Choose **"From URL"** and paste your blob storage URL
   - Or choose **"Upload file"** to upload directly
3. Wait for the model to load (may take 30-60 seconds)
4. The model should appear in the 3D viewer

### Step 8: Map Elements to Digital Twins

For each device in your model:

1. Click on a 3D element (device) in the viewer
2. In the right panel, click **"Link to twin"**
3. Select the corresponding digital twin:
   - `buffy_coat_packs` element → `buffy_coat_packs` twin
   - `platelet_washing` element → `platelet_washing` twin
   - etc.
4. Repeat for all 10 devices

**Tip:** The template model has node names that exactly match twin IDs, making this easier.

### Step 9: Add Visual Behaviors

Configure how device properties are displayed:

#### A. Add Status Color Coding

1. Select a device element
2. Click **"Add behavior"**
3. Choose **"Visual rule"**
4. Configure:
   - **Property**: `status`
   - **Type**: Enum
   - **Visual mapping**:
     - `Idle` → Green color (#00FF00)
     - `Processing` → Blue color (#0000FF)
     - `Blocked` → Yellow color (#FFFF00)
     - `Failed` → Red color (#FF0000)

#### B. Add Property Widgets

1. Click **"Add widget"**
2. Choose **"Value widget"** or **"Gauge widget"**
3. Link to twin property:
   - **Utilization Rate**: Show as percentage gauge
   - **Queue Length**: Show as number
   - **Total Processed**: Show as counter
4. Position widget near the device

#### C. Add 3D Visual Effects

For advanced effects:
- **Opacity**: Make devices semi-transparent when idle
- **Overlay**: Add glow effect when processing
- **Animation**: Rotate/pulse when status changes (if supported)

### Step 10: Configure Scene Settings

Optimize the scene for your use case:

1. **Camera Settings**
   - Set default camera position for best view
   - Configure zoom limits
   - Enable/disable camera controls

2. **Lighting**
   - Adjust ambient light
   - Add directional lights for better visibility
   - Configure shadows

3. **Scene Behavior**
   - Set refresh rate (how often properties update)
   - Configure auto-rotation or animations

### Step 11: Save and Publish

1. Click **"Save"** to save your scene configuration
2. Click **"Publish"** to make it available
3. Note the scene URL for sharing

## Using the 3D Scene

### Viewing Real-Time Updates

Once configured, your 3D scene will automatically reflect changes in your digital twins:

1. **Run a simulation**:
   ```bash
   python run_simulation_with_adt.py
   ```

2. **Watch the 3D scene**:
   - Devices will change color as status changes
   - Utilization metrics will update in real-time
   - Queue lengths will increase/decrease dynamically

### Sharing the Scene

Share your scene with team members:

1. Get the scene URL from Azure Portal
2. Ensure users have appropriate Azure AD permissions
3. Users can view the scene in their browser (no installation needed)

### Embedding in Applications

You can embed the 3D scene in your own applications:

```html
<!-- Example: Embed in React UI -->
<iframe
  src="https://explorer.digitaltwins.azure.net/scenes/<scene-id>"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>
```

## Testing Your 3D Scene

### Verify Model Loading

```bash
# Check if model is accessible
curl -I <your-blob-storage-url>

# Should return: HTTP/1.1 200 OK
```

### Verify Twin Mappings

```bash
# Query twins to ensure spatial properties exist
az dt twin query \
  --dt-name <your-adt-instance> \
  --query-command "SELECT * FROM digitaltwins WHERE IS_DEFINED(position)"
```

### Test Real-Time Updates

1. Manually update a twin property:
   ```bash
   az dt twin update \
     --dt-name <your-adt-instance> \
     --twin-id centrifuge \
     --json-patch '[{"op": "replace", "path": "/status", "value": "Processing"}]'
   ```

2. Watch for the color change in the 3D scene

## Troubleshooting

### Model Not Loading

**Problem**: GLTF model fails to load in 3D Scenes Studio

**Solutions**:
- Verify blob URL is publicly accessible
- Check file size is under 100MB
- Ensure GLTF is version 2.0
- Validate GLTF using [glTF Validator](https://github.khronos.org/glTF-Validator/)

### Elements Not Mapping to Twins

**Problem**: Cannot link 3D elements to digital twins

**Solutions**:
- Verify node names in GLTF match twin IDs exactly
- Check that twins exist: `az dt twin query --dt-name <instance> --query-command "SELECT * FROM digitaltwins"`
- Ensure you have proper permissions (Digital Twins Data Reader role)

### Properties Not Updating

**Problem**: 3D scene doesn't reflect twin property changes

**Solutions**:
- Verify behavior rules are configured correctly
- Check refresh rate settings in scene configuration
- Test that twins are actually updating: `az dt twin show --dt-name <instance> --twin-id <device-id>`
- Clear browser cache and reload the scene

### Performance Issues

**Problem**: Scene is slow or laggy

**Solutions**:
- Reduce model complexity (fewer polygons)
- Decrease refresh rate
- Use GLB format instead of GLTF (more efficient)
- Optimize textures (reduce resolution)
- Limit number of visual behaviors

## Advanced Configuration

### Custom Status Colors

Edit the GLTF materials to define custom colors for each status state:

```python
# Use the provided script to modify materials
python 3d_models/scripts/update_material_colors.py \
  --gltf platelet_lab.gltf \
  --status-colors '{"Idle": "#00FF00", "Processing": "#0000FF"}'
```

### Adding Animation

If your devices have animations (e.g., rotating centrifuge):

1. Create animations in your 3D software
2. Export with GLTF animations included
3. In 3D Scenes Studio, map animations to twin properties
4. Configure triggers (e.g., play rotation when status="Processing")

### Multiple Scenes

Create different views for different purposes:

- **Overview Scene**: All 10 devices in one view
- **Lab A Scene**: Focus on first 3 devices
- **Lab B Scene**: Focus on middle devices
- **Lab C/D Scene**: Focus on final stages

## Integration with React UI

Integrate the 3D scene into your existing React dashboard:

```javascript
// Example React component
import React from 'react';

const ThreeDViewer = ({ sceneId }) => {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <iframe
        src={`https://explorer.digitaltwins.azure.net/scenes/${sceneId}`}
        width="100%"
        height="100%"
        frameBorder="0"
        title="3D Scene Viewer"
      />
    </div>
  );
};

export default ThreeDViewer;
```

## Cost Considerations

Azure 3D Scenes Studio usage is included with Azure Digital Twins:

- **3D Scenes Studio**: No additional charge
- **Blob Storage**: ~$0.018 per GB/month
- **Data Transfer**: First 100GB free, then $0.087/GB
- **ADT Operations**: Part of your ADT instance cost

**Estimated monthly cost** for 3D visualization:
- Model storage (50MB): $0.001
- Monthly bandwidth (10GB): Free
- **Total**: ~$0.001/month additional

## Best Practices

### Model Design

1. **Keep it simple**: Start with basic shapes, add detail later
2. **Name consistently**: Use exact twin IDs for node names
3. **Optimize early**: Reduce polygon count before export
4. **Test incrementally**: Verify each device mapping before moving to next

### Twin Management

1. **Always include spatial properties**: Position and rotation help with layout
2. **Use consistent units**: Meters for position, quaternions for rotation
3. **Update regularly**: Keep twin properties in sync with simulation

### Scene Configuration

1. **Start with status colors**: Most important visual feedback
2. **Add widgets gradually**: Don't overwhelm the view
3. **Test on multiple devices**: Ensure scene works on different screen sizes
4. **Document your setup**: Keep notes on behavior rules and mappings

## Next Steps

After setting up your 3D scene:

1. ✅ **Configure visual behaviors** for all device states
2. ✅ **Add KPI widgets** to show key metrics
3. ✅ **Share with stakeholders** for feedback
4. 🔄 **Integrate with React UI** for unified dashboard
5. 🔄 **Set up alerts** based on device status
6. 🔄 **Create additional scenes** for different views

## Resources

- [Azure 3D Scenes Studio Documentation](https://learn.microsoft.com/azure/digital-twins/concepts-3d-scenes-studio)
- [GLTF 2.0 Specification](https://www.khronos.org/gltf/)
- [Blender GLTF Export Guide](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)
- [glTF Validator](https://github.khronos.org/glTF-Validator/)

## Support

For issues or questions:
- Check the troubleshooting section above
- Review [Azure Digital Twins documentation](https://learn.microsoft.com/azure/digital-twins/)
- Open an issue in the repository
- Contact Azure Support for platform-specific issues
