# Rokoko Retarget Animation Operator Usage

## Sources

This documentation is derived from:

-   **Source Code Analysis**: Direct inspection of Rokoko Studio Live add-on

    -   File: `operators/retargeting.py` (lines 76-537)
    -   File: `core/retargeting.py` (helper functions)
    -   File: `properties.py` (scene properties)
    -   File: `panels/retargeting.py` (UI implementation)

-   **Official Resources**:

    -   GitHub: https://github.com/Rokoko/rokoko-studio-live-blender
    -   Documentation: https://support.rokoko.com/hc/en-us/categories/4410420388113-Rokoko-Plugins
    -   README: https://github.com/Rokoko/rokoko-studio-live-blender#readme (retargeting section)

-   **Python Console Inspection**: Direct operator inspection via `help()` and `get_rna_type()`

## Operator Details

-   **Operator**: `bpy.ops.rsl.retarget_animation`
-   **ID**: `rsl.retarget_animation`
-   **Type**: `RSL_OT_retarget_animation`
-   **Description**: Retargets the animation from the source armature to the target armature

## How It Works

The operator **does NOT take direct parameters**. Instead, it uses **scene properties** to configure the retargeting:

1. **Source Armature**: Must have `animation_data` and `action` (animation)
2. **Target Armature**: The destination armature
3. **Bone Mapping List**: Maps source bones to target bones
4. **Settings**: Auto-scaling, pose mode, etc.

## Required Setup

### 1. Set Source and Target Armatures

```python
import bpy

# Set source armature (must have animation)
bpy.context.scene.rsl_retargeting_armature_source = source_armature_object

# Set target armature
bpy.context.scene.rsl_retargeting_armature_target = target_armature_object
```

**Requirements:**

-   Source armature must have `animation_data` and `action`
-   Source and target must be different armatures
-   Both must be `ARMATURE` type objects

### 2. Build Bone Mapping List

You can either:

-   **Auto-detect**: Use `bpy.ops.rsl.build_bone_list` to automatically match bones
-   **Manual**: Manually add bone mappings to `context.scene.rsl_retargeting_bone_list`

#### Auto-detect (Recommended first try):

```python
# This will automatically detect and match bones
bpy.ops.rsl.build_bone_list()
```

#### Manual bone mapping:

```python
scene = bpy.context.scene
bone_list = scene.rsl_retargeting_bone_list

# Add a bone mapping
bone_item = bone_list.add()
bone_item.bone_name_source = "LeftShoulder"  # Source bone name
bone_item.bone_name_target = "L_Shoulder"     # Target bone name
bone_item.bone_name_key = "L_Shoulder"       # Key for matching
```

### 3. Configure Settings (Optional)

```python
scene = bpy.context.scene

# Auto-scaling: Scale source to match target height
scene.rsl_retargeting_auto_scaling = True  # or False

# Pose mode: 'POSE' or 'REST'
scene.rsl_retargeting_use_pose = 'POSE'  # or 'REST'
```

### 4. Execute Retargeting

```python
# Execute the retargeting
bpy.ops.rsl.retarget_animation()
```

## What the Operator Does

1. **Validates** source has animation and armatures are different
2. **Builds bone mapping** from `rsl_retargeting_bone_list`
3. **Finds root bones** (bones without parents) for location retargeting
4. **Auto-scales** source armature if enabled (to match target height)
5. **Duplicates source armature** and applies transforms
6. **Creates constraints** on target armature:
    - `COPY_ROTATION` for all mapped bones
    - `COPY_LOCATION` for root bones
7. **Bakes animation** to target armature (converts constraints to keyframes)
8. **Cleans up** temporary armatures and constraints
9. **Renames action** to `{original_name} Retarget`

## Complete Example

```python
import bpy

# Get source and target armatures
source_armature = bpy.data.objects.get("SourceArmature")
target_armature = bpy.data.objects.get("TargetArmature")

# Check source has animation
if not source_armature.animation_data or not source_armature.animation_data.action:
    print("ERROR: Source armature must have animation!")
    exit(1)

# Set scene properties
scene = bpy.context.scene
scene.rsl_retargeting_armature_source = source_armature
scene.rsl_retargeting_armature_target = target_armature
scene.rsl_retargeting_auto_scaling = True
scene.rsl_retargeting_use_pose = 'POSE'

# Auto-detect bone mappings
bpy.ops.rsl.build_bone_list()

# Check if bone list was built
if not scene.rsl_retargeting_bone_list:
    print("ERROR: No bones mapped! Check bone names match.")
    exit(1)

# Execute retargeting
try:
    bpy.ops.rsl.retarget_animation()
    print("✅ Retargeting successful!")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Related Operators

-   **`bpy.ops.rsl.build_bone_list`**: Automatically builds bone mapping list
-   **`bpy.ops.rsl.add_bone_list_item`**: Adds a manual bone mapping item
-   **`bpy.ops.rsl.clear_bone_list`**: Clears all bone mappings
-   **`bpy.ops.rsl.save_custom_bones_retargeting`**: Saves custom bone mappings

## Important Notes

1. **Root bones** get both rotation AND location retargeting
2. **Non-root bones** only get rotation retargeting
3. **Auto-scaling** scales the source armature to match target height
4. **Baking** converts constraint-driven animation to keyframes
5. **Original source animation** is preserved (not modified)
6. **Target action** is renamed to `{original_name} Retarget`

## Troubleshooting

### Error: "No animation on the source armature found!"

-   Source armature must have `animation_data` and `action`
-   Check: `source_armature.animation_data.action` is not None

### Error: "Source and target armature are the same!"

-   Source and target must be different armatures

### Error: "No root bone found!"

-   Bone mapping list might be empty or incorrect
-   Try running `bpy.ops.rsl.build_bone_list()` first

### Error: "Duplicate target bone entries found!"

-   Each target bone can only be mapped once
-   Check `rsl_retargeting_bone_list` for duplicates
