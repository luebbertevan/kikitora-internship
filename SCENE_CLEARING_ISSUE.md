# Why GLB Files Are Corrupted/Morphed (Scene Clearing Issue)

## The Problem

**Symptoms:**

-   First GLB file is correct
-   Subsequent GLB files are corrupted/morphed versions of the first
-   All animations look identical/distorted even though they come from different NPZ files

**Root Cause:** Blender data blocks (armatures, actions, meshes) persist between file processing, even after deleting objects.

## What's Happening

### The Scene Clearing Code

Both scripts do this:

```python
# Line 279-280 in create_glb_from_npz.py
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
```

**This deletes objects, but NOT data blocks!**

### What Persists

**When you delete an object, Blender keeps:**

1. **Armature data blocks** (`bpy.data.armatures`)
2. **Action data blocks** (`bpy.data.actions`) - animation keyframes
3. **Mesh data blocks** (`bpy.data.meshes`)
4. **Material data blocks**
5. **Scene-level settings** (frame ranges, etc.)

**What happens:**

1. **First file:** Creates armature "SMPL_H_Armature", adds animation action, exports → works
2. **Second file:** Deletes objects, but old armature data still exists
    - Creates new armature with same name → **overwrites/reuses old data**
    - Old animation keyframes might still be attached
    - New animation gets mixed with old animation
3. **Result:** Corrupted/morphed animation

## Why They're Not Independently Processed

**The scripts ARE trying to process independently**, but:

1. **Data blocks are shared** - Blender keeps them in memory
2. **Same names** - Both scripts create armatures named "SMPL_H_Armature"
    - First file creates it
    - Second file creates another with same name → **collision/reuse**
3. **Actions persist** - Animation keyframes from first file remain in memory
4. **No cleanup** - Data blocks aren't explicitly removed

## Specific Issues

### create_glb_from_npz.py

**Line 300:**

```python
armature_data = bpy.data.armatures.new("SMPL_H_Armature")
```

**Problem:**

-   First file: Creates "SMPL_H_Armature" → works
-   Second file: Creates "SMPL_H_Armature" again → **might reuse existing data block**
-   Old keyframes from first file might still be attached

**Line 461-471: Baking:**

```python
bpy.ops.nla.bake(...)
```

**Problem:**

-   Creates/updates action with keyframes
-   Action data persists in `bpy.data.actions`
-   Next file's action might reuse or mix with old action data

### original_retarget.py

**Line 276:**

```python
armature = create_tpose_armature()
```

**Inside `create_tpose_armature()` (line 127):**

```python
armature = bpy.data.armatures.new(name)
```

**Same problem:**

-   Creates armature with same name
-   Old armature data might persist
-   Animation from first file affects subsequent files

**Line 252: Keyframe insertion:**

```python
pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_idx)
```

**Problem:**

-   Creates/updates action
-   Action data persists between files
-   Next file's action might mix with old keyframes

## Why All Three Are Identical

**If all three GLBs are identical and distorted:**

1. **First file processes correctly** → creates armature + animation
2. **Second file:**
    - Deletes objects (but not data blocks)
    - Creates new armature → **reuses old data block**
    - Adds animation → **mixes with old keyframes**
    - Result: **Same as first file** (old data persists)
3. **Third file:** Same issue → **all three end up identical**

## What Should Be Cleared

**To truly process independently, you need to:**

1. **Clear data blocks:**

    ```python
    # Clear armatures
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)

    # Clear actions (animations)
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

    # Clear meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    ```

2. **Use unique names:**

    ```python
    armature_name = f"SMPL_H_Armature_{npz_path.stem}"
    ```

3. **Clear scene-level data:**
    ```python
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 0
    ```

## Why This Is Hard to Debug

**The issue is subtle because:**

-   Objects are deleted (looks like cleanup)
-   But data blocks persist invisibly
-   Same names cause collisions
-   Actions mix keyframes silently

**Visual inspection shows:**

-   Objects are deleted (scene looks empty)
-   But data blocks are still there (invisible)
-   Next file reuses them (corruption happens)

## Summary

**The Problem:**

-   Scripts delete **objects** but not **data blocks**
-   Data blocks (armatures, actions) persist between files
-   Same names cause collisions/reuse
-   Old animation data mixes with new

**The Result:**

-   First file works (nothing to conflict with)
-   Subsequent files corrupt (reuse old data)
-   All files end up identical (same corrupted data)

**The Fix (conceptually):**

-   Clear data blocks explicitly
-   Use unique names per file
-   Clear actions before each file
-   Properly reset scene state

This is a common Blender scripting issue - objects != data blocks!
