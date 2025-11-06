# Why retarget.py Doesn't Have Cross-Contamination Issue

## The Question

Based on visual testing, `retarget.py` does not seem to have the cross-contamination issue that `create_glb_from_npz_fixed.py` was designed to fix. Why is that?

## Comparison of Scene Clearing Code

### retarget.py (Lines 321-331)

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

### create_glb_from_npz_fixed.py (Lines 130-161)

```python
def clear_all_data_blocks() -> None:
    # Clear objects first (this removes references)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Clear data blocks (these persist even after object deletion)
    for armature in list(bpy.data.armatures):  # ← Uses list()
        bpy.data.armatures.remove(armature)

    for action in list(bpy.data.actions):  # ← Uses list()
        bpy.data.actions.remove(action)

    for mesh in list(bpy.data.meshes):  # ← Uses list()
        bpy.data.meshes.remove(mesh)

    # Materials (additional cleanup)
    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)

    # Reset scene frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 0
```

## Key Differences

### 1. **List Conversion (`list()` wrapper)**

**retarget.py**: Iterates directly over `bpy.data.actions`, `bpy.data.meshes`, `bpy.data.armatures`

**create_glb_from_npz_fixed.py**: Uses `list(bpy.data.actions)` to create a snapshot before iteration

**Why this matters**:

-   When you iterate over a collection and remove items during iteration, you can skip items or get errors
-   Using `list()` creates a snapshot, so you iterate over a fixed list while removing from the original collection
-   **However**, in practice, if you're removing ALL items, this might not cause issues if the iteration completes

### 2. **Manual Clearing is Sufficient**

**The real reason `retarget.py` works**: It manually removes **all** data blocks before creating new ones:

```python
for action in bpy.data.actions:
    bpy.data.actions.remove(action)  # Removes ALL actions
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)  # Removes ALL meshes
for armature in bpy.data.armatures:
    bpy.data.armatures.remove(armature)  # Removes ALL armatures
```

Since it removes **everything**, there are no leftover data blocks to cause collisions, even if names are reused.

### 3. **Why create_glb_from_npz.py Had the Issue**

The **original** `create_glb_from_npz.py` (not the fixed version) only did:

```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
```

This **only deletes objects**, not the underlying data blocks (armatures, actions, meshes). So when processing the second file:

-   Old armature data block still exists with name "SMPL_H_Armature"
-   New armature tries to use same name "SMPL_H_Armature"
-   Blender reuses or mixes the old data block → cross-contamination

### 4. **Why retarget.py Works**

`retarget.py` **explicitly removes all data blocks** before creating new ones:

1. Deletes objects (removes references)
2. **Removes all actions** (no leftover animations)
3. **Removes all meshes** (no leftover meshes)
4. **Removes all armatures** (no leftover armatures)

Since everything is cleared, even if you create a new armature with the same name "SMPL_H_Armature", there's no old data block to collide with.

### 5. **Why create_glb_from_npz_fixed.py Uses Unique Names**

`create_glb_from_npz_fixed.py` uses unique names **as a belt-and-suspenders approach**:

-   It has `clear_all_data_blocks()` which should be sufficient
-   But it also uses unique names (`SMPL_H_Armature_{filename}`) as extra protection
-   This ensures that even if clearing fails or is incomplete, names won't collide

## Conclusion

**`retarget.py` doesn't have cross-contamination because:**

1. ✅ It **manually removes ALL data blocks** (actions, meshes, armatures) before creating new ones
2. ✅ Since everything is cleared, there are no leftover data blocks to cause collisions
3. ✅ Even with non-unique names, there's nothing to collide with

**The original `create_glb_from_npz.py` had the issue because:**

1. ❌ It **only deleted objects**, not data blocks
2. ❌ Data blocks persisted in memory
3. ❌ New objects with same names reused old data blocks

**`create_glb_from_npz_fixed.py` is more robust because:**

1. ✅ Uses `list()` wrapper (safer iteration)
2. ✅ Clears all data blocks (like retarget.py)
3. ✅ Uses unique names (extra protection)
4. ✅ Resets scene frame range (cleaner state)

## Recommendation

**For retarget.py**: The current approach works, but could be improved by:

1. Using `list()` wrapper for safer iteration (defensive programming)
2. Optionally using unique names (extra safety, but not strictly necessary if clearing works)
3. Resetting scene frame range (cleaner state)

The manual clearing in `retarget.py` is sufficient, but the `clear_all_data_blocks()` function is cleaner and more maintainable.
