# Using Rokoko Retarget Operator in Python Scripts

## Sources and Documentation

This documentation is based on:

-   **Source Code**: Rokoko Studio Live Blender add-on source code

    -   Location: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/`
    -   Operator implementation: `operators/retargeting.py`
    -   Helper functions: `core/retargeting.py`
    -   Properties: `properties.py`
    -   UI panel: `panels/retargeting.py`

-   **Official Documentation**:

    -   GitHub Repository: https://github.com/Rokoko/rokoko-studio-live-blender
    -   README: https://github.com/Rokoko/rokoko-studio-live-blender#readme
    -   Support Documentation: https://support.rokoko.com/hc/en-us/categories/4410420388113-Rokoko-Plugins
    -   Support Portal: https://support.rokoko.com/

-   **Video Tutorial**: https://youtu.be/Od8Ecr70A4Q (Retargeting tutorial)

-   **Add-on Metadata**:
    -   Name: "Rokoko Studio Live for Blender"
    -   Author: Rokoko Electronics ApS
    -   Version: 1.4.3 (from `__init__.py`)
    -   GitHub: https://github.com/Rokoko/rokoko-studio-live-blender#readme

## Quick Start

### Minimal Example

```python
import bpy

# 1. Set source and target armatures
scene = bpy.context.scene
scene.rsl_retargeting_armature_source = bpy.data.objects["SourceArmature"]
scene.rsl_retargeting_armature_target = bpy.data.objects["TargetArmature"]

# 2. Auto-detect bone mappings
bpy.ops.rsl.build_bone_list()

# 3. Execute retargeting
bpy.ops.rsl.retarget_animation()
```

## Complete Workflow

### Step 1: Setup Scene Properties

```python
import bpy

# Get armature objects (must exist in scene)
source_armature = bpy.data.objects.get("SourceArmature")
target_armature = bpy.data.objects.get("TargetArmature")

# Validate
if not source_armature or source_armature.type != 'ARMATURE':
    raise ValueError("Source armature not found!")

if not source_armature.animation_data or not source_armature.animation_data.action:
    raise ValueError("Source armature must have animation!")

# Set scene properties
scene = bpy.context.scene
scene.rsl_retargeting_armature_source = source_armature
scene.rsl_retargeting_armature_target = target_armature

# Optional settings
scene.rsl_retargeting_auto_scaling = True   # Auto-scale source to match target
scene.rsl_retargeting_use_pose = 'POSE'     # or 'REST'
```

### Step 2: Build Bone Mapping

**Option A: Auto-detect (Recommended)**

```python
# Automatically detect and match bones
result = bpy.ops.rsl.build_bone_list()
if result == {'FINISHED'}:
    bone_count = len(scene.rsl_retargeting_bone_list)
    print(f"Detected {bone_count} bone mappings")
```

**Option B: Manual mapping**

```python
# Clear existing mappings
scene.rsl_retargeting_bone_list.clear()

# Add bone mappings manually
bone_item = scene.rsl_retargeting_bone_list.add()
bone_item.bone_name_source = "LeftShoulder"  # Source bone
bone_item.bone_name_target = "L_Shoulder"     # Target bone
bone_item.bone_name_key = "L_Shoulder"        # Key (usually same as target)

# Add more mappings...
```

### Step 3: Execute Retargeting

```python
# Execute the retargeting
result = bpy.ops.rsl.retarget_animation()

if result == {'FINISHED'}:
    print("✅ Retargeting successful!")
    # Target armature now has the retargeted animation
    target = scene.rsl_retargeting_armature_target
    action_name = target.animation_data.action.name
    print(f"Animation: {action_name}")
else:
    print(f"Failed: {result}")
```

## Integration with Your NPZ → GLB Pipeline

### Example: After Creating GLB from NPZ

```python
import bpy
from pathlib import Path

# ... your existing code to create source armature from NPZ ...

# After you've created the source armature with animation:
source_armature = bpy.data.objects["SMPL_H_Armature"]  # Your source

# Load/create target armature (reference SMPL-H)
target_glb_path = Path("data/reference/smplh_target.glb")
bpy.ops.import_scene.gltf(filepath=str(target_glb_path))
target_armature = bpy.data.objects["SMPL_H_Armature"]  # Adjust name if needed

# Setup Rokoko retargeting
scene = bpy.context.scene
scene.rsl_retargeting_armature_source = source_armature
scene.rsl_retargeting_armature_target = target_armature
scene.rsl_retargeting_auto_scaling = True

# Auto-detect bone mappings
bpy.ops.rsl.build_bone_list()

# Execute retargeting
bpy.ops.rsl.retarget_animation()

# Export result
bpy.ops.export_scene.gltf(filepath="output_retargeted.glb")
```

## Error Handling

### Common Errors and Solutions

**Error: "No animation on the source armature found!"**

```python
# Check before setting up
if not source_armature.animation_data:
    source_armature.animation_data_create()

if not source_armature.animation_data.action:
    # Create action and add keyframes
    action = bpy.data.actions.new(name="Animation")
    source_armature.animation_data.action = action
    # ... add keyframes ...
```

**Error: "Source and target armature are the same!"**

```python
# Make sure they're different objects
assert source_armature.name != target_armature.name
```

**Error: "No root bone found!"**

```python
# Check bone list is populated
if not scene.rsl_retargeting_bone_list:
    print("Bone list is empty!")
    # Try manual mapping or check bone names match
```

**Error: "Duplicate target bone entries found!"**

```python
# Check for duplicates before retargeting
target_bones = [item.bone_name_target for item in scene.rsl_retargeting_bone_list]
duplicates = [bone for bone in set(target_bones) if target_bones.count(bone) > 1]
if duplicates:
    print(f"Duplicate mappings: {duplicates}")
```

## Helper Function

```python
def retarget_animation(source_name: str, target_name: str,
                      auto_scaling: bool = True,
                      use_auto_detect: bool = True) -> bool:
    """Complete retargeting workflow."""
    scene = bpy.context.scene

    # Get armatures
    source = bpy.data.objects.get(source_name)
    target = bpy.data.objects.get(target_name)

    if not source or not target:
        print(f"❌ Armatures not found!")
        return False

    if not source.animation_data or not source.animation_data.action:
        print(f"❌ Source has no animation!")
        return False

    # Setup
    scene.rsl_retargeting_armature_source = source
    scene.rsl_retargeting_armature_target = target
    scene.rsl_retargeting_auto_scaling = auto_scaling
    scene.rsl_retargeting_bone_list.clear()

    # Build bone mapping
    if use_auto_detect:
        if bpy.ops.rsl.build_bone_list() != {'FINISHED'}:
            print("⚠️  Auto-detection failed")
            return False

    # Execute
    if bpy.ops.rsl.retarget_animation() == {'FINISHED'}:
        print("✅ Retargeting successful!")
        return True
    else:
        print("❌ Retargeting failed")
        return False

# Usage
retarget_animation("SourceArmature", "TargetArmature")
```

## Important Notes

1. **Source armature must have animation** (`animation_data.action`)
2. **Both armatures must exist** in the scene before calling
3. **Bone names must match** (or be manually mapped) between source and target
4. **Auto-scaling** scales the source to match target height (optional)
5. **Root bones** get both rotation and location; others only get rotation
6. **Original source animation** is preserved (not modified)
7. **Target animation** is renamed to `{original_name} Retarget`

## Testing

See `tests/research/test_rokoko_retarget.py` for a complete working example.
