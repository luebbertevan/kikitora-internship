# M1.1: Script Comparison - retarget.py vs create_glb_from_npz_fixed.py

## Overview

This document compares `src/retarget.py` and `src/originals/create_glb_from_npz_fixed.py` to identify differences, unique features, and determine what should be kept for the new approach.

---

## Function Comparison Table

| Function Name                   | retarget.py | create_glb_from_npz_fixed.py | Status                                     |
| ------------------------------- | ----------- | ---------------------------- | ------------------------------------------ |
| `axis_angle_to_rotation_matrix` | ✅          | ✅                           | **Identical**                              |
| `forward_kinematics`            | ✅          | ✅                           | **Identical**                              |
| `load_reference_pelvis`         | ✅          | ❌                           | **Unique to retarget.py**                  |
| `align_root_to_reference`       | ✅          | ❌                           | **Unique to retarget.py**                  |
| `clear_all_data_blocks`         | ❌          | ✅                           | **Unique to create_glb_from_npz_fixed.py** |
| `apply_json_pose_to_frame0`     | ✅          | ✅                           | **Identical**                              |
| `add_cube_and_parent`           | ✅          | ✅                           | **Different defaults**                     |
| `process_npz_file`              | ✅          | ✅                           | **Major differences**                      |
| `find_npz_files`                | ✅          | ✅                           | **Identical**                              |
| `main`                          | ✅          | ✅                           | **Different CLI args**                     |

---

## Functions Unique to retarget.py

### 1. `load_reference_pelvis() -> Optional[NDArray[np.float64]]`

**Location**: Lines 91-105

**Purpose**: Loads the reference pelvis position from `data/reference/smplh_target_reference.npz`

**What it does**:

-   Loads the reference NPZ file
-   Extracts `J_ABSOLUTE[0]` (pelvis position)
-   Returns the pelvis position as a (3,) array, or None if not found

**Relevance**: **KEEP** - This is needed for M3 (root alignment) and will be needed for the new approach when we load A-pose J_ABSOLUTE.

### 2. `align_root_to_reference(joint_positions, reference_pelvis) -> NDArray[np.float64]`

**Location**: Lines 108-136

**Purpose**: Aligns animation root (pelvis) to reference position

**What it does**:

-   Takes joint positions (single frame or multi-frame)
-   Calculates translation offset to move frame 0 pelvis to reference position
-   Applies offset to all joints (preserves relative motion)

**Relevance**: **EVALUATE** - This was for M3 (root alignment). For the new approach, we may not need this if we're using A-pose bone lengths directly. However, it might still be useful for ensuring consistent root positioning.

---

## Functions Unique to create_glb_from_npz_fixed.py

### 1. `clear_all_data_blocks() -> None`

**Location**: Lines 130-161

**Purpose**: Clears all Blender data blocks to prevent cross-contamination between files

**What it does**:

-   Deletes all objects
-   Removes all armatures, actions, meshes, materials
-   Resets scene frame range
-   Uses unique names for armatures/actions to prevent collisions

**Relevance**: **KEEP** - This fixes the scene clearing bug. This is critical for batch processing and should be integrated into retarget.py.

**Key Features**:

-   Removes data blocks (not just objects)
-   Prevents animation mixing between files
-   Uses unique names per file

---

## Shared Functions with Differences

### 1. `add_cube_and_parent()`

**retarget.py** (Lines 262-299):

-   Default `cube_size = 0.05`
-   Always adds cube (no option to skip)
-   Cube is always required for pipeline

**create_glb_from_npz_fixed.py** (Lines 251-288):

-   Default `cube_size = 1.0`
-   Cube is optional (controlled by `add_cube` parameter)

**Difference**: Default cube size and whether cube is required

**Decision**: **KEEP retarget.py version** - The smaller cube size (0.05) is more appropriate, and the cube requirement is part of the pipeline spec.

### 2. `process_npz_file()`

This function has **major differences**. Let me break them down:

#### Scene Clearing

**retarget.py** (Lines 321-331):

```python
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Clear all animation data to prevent cross-contamination between files
for action in bpy.data.actions:
    bpy.data.actions.remove(action)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for armature in bpy.data.armatures:
    bpy.data.armatures.remove(armature)
```

**create_glb_from_npz_fixed.py** (Line 313):

```python
# Clear ALL data blocks (not just objects) - FIXED
clear_all_data_blocks()
```

**Difference**: `create_glb_from_npz_fixed.py` uses the dedicated `clear_all_data_blocks()` function which is more thorough.

**Decision**: **USE create_glb_from_npz_fixed.py approach** - The dedicated function is cleaner and more thorough.

#### Root Alignment (M3 Feature)

**retarget.py** (Lines 350-356):

```python
# M3: Align root to reference pelvis position
reference_pelvis = load_reference_pelvis()
if reference_pelvis is not None:
    joint_positions_frame0 = align_root_to_reference(joint_positions_frame0, reference_pelvis)
    print(f"✓ Aligned root to reference pelvis: {reference_pelvis}")
else:
    print("⚠️  Skipping root alignment (reference not found)")
```

**create_glb_from_npz_fixed.py**: **NOT PRESENT**

**Difference**: `retarget.py` aligns frame 0 pelvis to reference position.

**Decision**: **EVALUATE** - This was for M3. For the new approach, we may not need this if we're using A-pose bone lengths. However, it might still be useful. Mark for evaluation in M1.2.

#### Translation Offset for All Frames

**retarget.py** (Lines 413-435):

```python
# M3: Calculate translation offset from frame 0 to align with reference (once)
translation_offset = np.zeros(3)
if reference_pelvis is not None:
    # Get frame 0 pelvis position BEFORE alignment
    frame0_joints = forward_kinematics(poses[0], trans[0])
    frame0_pelvis = frame0_joints[0, :]  # Pelvis is index 0
    # Calculate the offset needed to move frame 0 pelvis to reference
    translation_offset = reference_pelvis - frame0_pelvis
    print(f"✓ Translation offset calculated: {translation_offset}")
    print(f"  This will move entire animation so frame 0 pelvis is at reference position")

# ... later in frame loop ...
# M3: Apply the same translation offset to all frames (moves entire animation)
if reference_pelvis is not None:
    joint_positions = joint_positions + translation_offset[np.newaxis, :]
```

**create_glb_from_npz_fixed.py**: **NOT PRESENT**

**Difference**: `retarget.py` applies translation offset to all frames to align entire animation.

**Decision**: **EVALUATE** - Same as root alignment above. Mark for evaluation in M1.2.

#### Unique Naming

**retarget.py** (Lines 359-360):

```python
armature_data = bpy.data.armatures.new("SMPL_H_Armature")
armature: bpy.types.Object = bpy.data.objects.new("SMPL_H_Armature", armature_data)
```

**create_glb_from_npz_fixed.py** (Lines 333-335):

```python
# Create armature with UNIQUE name per file - FIXED
unique_name = f"SMPL_H_Armature_{npz_path.stem}"
armature_data = bpy.data.armatures.new(unique_name)
armature: bpy.types.Object = bpy.data.objects.new(unique_name, armature_data)
```

**Difference**: `create_glb_from_npz_fixed.py` uses unique names per file to prevent collisions.

**Decision**: **USE create_glb_from_npz_fixed.py approach** - Unique naming prevents data block collisions.

#### Empty Naming

**retarget.py** (Lines 407-408):

```python
empty = bpy.data.objects.new(f"Empty_{joint_name}", None)
```

**create_glb_from_npz_fixed.py** (Lines 382-384):

```python
empty_name = f"Empty_{unique_name}_{joint_name}"
empty = bpy.data.objects.new(empty_name, None)
```

**Difference**: `create_glb_from_npz_fixed.py` includes unique name prefix.

**Decision**: **USE create_glb_from_npz_fixed.py approach** - Unique naming prevents collisions.

#### Action Naming

**retarget.py**: Uses default action (no explicit action creation)

**create_glb_from_npz_fixed.py** (Lines 495-499):

```python
# Create a new action with unique name - FIXED
action_name = f"Action_{unique_name}"
action = bpy.data.actions.new(action_name)
armature.data.animation_data_create()
armature.data.animation_data.action = action
```

**Difference**: `create_glb_from_npz_fixed.py` creates action with unique name.

**Decision**: **USE create_glb_from_npz_fixed.py approach** - Prevents action collisions.

#### Output Path

**retarget.py** (Line 567):

```python
output_path: Path = npz_path.with_stem(npz_path.stem + '_retargeted').with_suffix('.glb')
```

**create_glb_from_npz_fixed.py** (Lines 536-539):

```python
# Output to comparison folder
output_dir = npz_path.parent / "create_glb_output"
output_dir.mkdir(exist_ok=True)
output_path: Path = output_dir / npz_path.name.replace('.npz', '.glb')
```

**Difference**: `retarget.py` outputs next to source file with `_retargeted` suffix. `create_glb_from_npz_fixed.py` outputs to subdirectory.

**Decision**: **USE retarget.py approach** - Outputting next to source with `_retargeted` suffix is cleaner and matches the new approach.

#### Cube Handling

**retarget.py** (Line 564):

```python
# Add cube (always required for pipeline)
cube: bpy.types.Object = add_cube_and_parent(armature, cube_size, cube_location)
```

**create_glb_from_npz_fixed.py** (Lines 530-533):

```python
# Add cube if requested
cube: Optional[bpy.types.Object] = None
if add_cube:
    cube = add_cube_and_parent(armature, cube_size, cube_location)
```

**Difference**: `retarget.py` always adds cube. `create_glb_from_npz_fixed.py` makes it optional.

**Decision**: **USE retarget.py approach** - Cube is required for pipeline per spec.

### 3. `main()`

#### Command-Line Arguments

**retarget.py** has:

-   `--export-target-apose` - Export A-pose reference GLB
-   `--json-pose` - JSON pose override
-   `--limit` - Limit number of files
-   `--cube-size` (default: 0.05)
-   `--cube-location` (default: 0, 0, 0)
-   `--output` - Output directory (for A-pose export)

**create_glb_from_npz_fixed.py** has:

-   `--json-pose` - JSON pose override
-   `--limit` - Limit number of files
-   `--add-cube` - Flag to add cube (optional)
-   `--cube-size` (default: 1.0)
-   `--cube-location` (default: 0, 0, 0)

**Differences**:

1. `retarget.py` has `--export-target-apose` flag (M2 feature)
2. `retarget.py` has `--output` for A-pose export
3. `create_glb_from_npz_fixed.py` has `--add-cube` flag (cube is optional)
4. Different default cube sizes

**Decision**: **EVALUATE** - The `--export-target-apose` feature might be stale (M2 is done). The cube handling should match the pipeline requirement (always add cube).

---

## Summary of Unique Features

### retarget.py Unique Features

1. **Root Alignment (M3)**:

    - `load_reference_pelvis()` - Loads reference pelvis position
    - `align_root_to_reference()` - Aligns animation to reference pelvis
    - Translation offset applied to all frames

2. **A-Pose Export**:

    - `--export-target-apose` flag in main()
    - Inline helper functions `_load_target_reference()` and `_create_armature_from_target()`

3. **Always Add Cube**:

    - Cube is always added (not optional)
    - Default cube size: 0.05

4. **Output Naming**:
    - Outputs with `_retargeted` suffix next to source file

### create_glb_from_npz_fixed.py Unique Features

1. **Scene Clearing Fix**:

    - `clear_all_data_blocks()` function
    - More thorough data block cleanup

2. **Unique Naming**:

    - Unique armature names per file
    - Unique empty names per file
    - Unique action names per file
    - Prevents data block collisions

3. **Optional Cube**:

    - Cube is optional (`--add-cube` flag)
    - Default cube size: 1.0

4. **Output Directory**:
    - Outputs to `create_glb_output/` subdirectory

---

## Key Differences in Shared Functions

### `forward_kinematics()`

**Status**: **IDENTICAL** - Both functions are exactly the same.

### `axis_angle_to_rotation_matrix()`

**Status**: **IDENTICAL** - Both functions are exactly the same.

### `apply_json_pose_to_frame0()`

**Status**: **IDENTICAL** - Both functions are exactly the same.

### `find_npz_files()`

**Status**: **IDENTICAL** - Both functions are exactly the same.

---

## Recommendations for M1.2 (Stale Code Analysis)

### Features to Keep:

1. ✅ `clear_all_data_blocks()` from `create_glb_from_npz_fixed.py` - Fixes scene clearing bug
2. ✅ Unique naming approach from `create_glb_from_npz_fixed.py` - Prevents collisions
3. ✅ `load_reference_pelvis()` from `retarget.py` - Will be needed for loading A-pose
4. ✅ Always add cube (retarget.py approach) - Required by pipeline
5. ✅ Output with `_retargeted` suffix (retarget.py approach) - Cleaner naming

### Features to Evaluate:

1. ⚠️ `align_root_to_reference()` - Was for M3, may not be needed for new approach
2. ⚠️ Translation offset for all frames - Part of M3, may not be needed
3. ⚠️ `--export-target-apose` flag - M2 is done, may be stale
4. ⚠️ JSON pose override - May not be needed if we're setting frame 0 to A-pose directly

### Features to Remove:

1. ❌ Optional cube flag - Cube should always be added
2. ❌ Output to subdirectory - Should output next to source file

---

## Next Steps

This comparison will be used in **M1.2** to make final decisions about what code to keep, remove, or modify for the new approach.
