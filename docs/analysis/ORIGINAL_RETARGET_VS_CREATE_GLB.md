# original_retarget.py vs create_glb_from_npz.py

## Are They The Same?

**No, they are fundamentally different approaches**, even though they share some code.

## Similarities

Both files share:

-   ✅ Same `J_ABSOLUTE` and `SMPL_OFFSETS` (hardcoded T-pose values)
-   ✅ Same `forward_kinematics()` function (same logic)
-   ✅ Same `axis_angle_to_rotation_matrix()` function
-   ✅ Same SMPL-H skeleton structure (`SMPL_H_PARENTS`, `JOINT_NAMES`)
-   ✅ Both create Blender armatures
-   ✅ Both export to GLB

## Key Differences

### 1. **Armature Creation**

**original_retarget.py:**

```python
def create_tpose_armature():
    # Uses T-pose (zero poses) to create armature
    zero_poses = np.zeros((52, 3))
    zero_trans = np.zeros(3)
    tpose_joints = forward_kinematics(zero_poses, zero_trans)
    # Creates bones from T-pose positions
```

**create_glb_from_npz.py:**

```python
# Uses frame 0 pose (actual animation frame) to create armature
joint_positions_frame0 = forward_kinematics(poses[0], trans[0])
# Creates bones from frame 0 positions
```

**Difference:** original_retarget uses T-pose, create_glb_from_npz uses frame 0 pose.

### 2. **Animation Approach**

**original_retarget.py:**

-   **Direct bone rotation approach**
-   Computes FK joint positions for each frame
-   Computes bone rotations to match those positions
-   Applies rotations directly to bones as quaternions
-   No empties, no constraints

```python
def retarget_animation():
    for frame_idx in range(num_frames):
        frame_joints = forward_kinematics(poses[frame_idx], trans[frame_idx])

        for i in range(52):
            # Compute rotation to point toward target
            rotation = compute_bone_rotation(head, tail, target_pos)
            pose_bone.rotation_quaternion = rotation
            pose_bone.keyframe_insert(data_path="rotation_quaternion")
```

**create_glb_from_npz.py:**

-   **Empties + constraints approach**
-   Computes FK joint positions for each frame
-   Creates empties at those positions
-   Adds constraints (STRETCH_TO, COPY_LOCATION, DAMPED_TRACK) to make bones follow empties
-   Bakes constraints to keyframes

```python
# Create empties
for i in range(52):
    empty = bpy.data.objects.new(f"Empty_{joint_name}", None)
    # Set empty position from FK
    empty.location = Vector(joint_positions[i])

# Add constraints
for i in range(52):
    constraint = pose_bone.constraints.new('STRETCH_TO')
    constraint.target = empties[child_idx]

# Bake constraints to keyframes
bpy.ops.nla.bake(...)
```

**Difference:** original_retarget directly computes and applies rotations, create_glb_from_npz uses empties/constraints/bake.

### 3. **Bone Rotation Computation**

**original_retarget.py:**

-   Has `compute_bone_rotation()` function
-   Computes quaternion rotation from rest direction to target direction
-   Explicitly calculates rotations

**create_glb_from_npz.py:**

-   No explicit rotation computation
-   Relies on Blender constraints to compute rotations
-   Constraints handle the rotation math automatically

### 4. **Additional Features**

**create_glb_from_npz.py has:**

-   JSON pose override for frame 0 (`apply_json_pose_to_frame0()`)
-   Optional cube parented to armature (`add_cube_and_parent()`)
-   More detailed comments
-   More sophisticated constraint handling (different constraints for different bone types)

**original_retarget.py has:**

-   Simpler, more direct approach
-   No extra features

## Which Approach Is Better?

### original_retarget.py:

**Pros:**

-   Simpler, more direct
-   Explicit rotation computation (easier to understand)
-   No constraints (cleaner)

**Cons:**

-   Less flexible
-   Harder to adjust bone lengths (rotations are computed directly)
-   Doesn't support bone length retargeting easily

### create_glb_from_npz.py:

**Pros:**

-   More flexible (empties can be adjusted)
-   Constraints can be modified
-   Better for retargeting (can adjust empty positions)
-   Supports bone length retargeting (M5+)

**Cons:**

-   More complex (empties, constraints, baking)
-   Harder to understand (more moving parts)

## Summary

**They are NOT the same!**

-   **original_retarget.py**: Direct rotation approach (FK → compute rotations → apply)
-   **create_glb_from_npz.py**: Empties + constraints approach (FK → empties → constraints → bake)

**create_glb_from_npz.py is what your current `retarget.py` is based on** - it's the better foundation for retargeting because it's more flexible.

**original_retarget.py is a simpler approach** that might work for basic cases but doesn't support retargeting well.

## Code Relationship

Looking at the history:

1. `original_retarget.py` was probably an early attempt
2. `create_glb_from_npz.py` evolved from it (or was created separately)
3. `retarget.py` is based on `create_glb_from_npz.py`

They share core FK logic but have fundamentally different animation approaches.
