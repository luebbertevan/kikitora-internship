# Why the Frame 0 A-Pose Override Doesn’t Work (Yet)

## Current Pipeline

1. Build an armature using FK of the mocap frame 0 (`forward_kinematics(poses[0], trans[0])`).
2. Create empties and keyframe them on every frame.
3. For frame 0, manually set each empty to the Blender A‑pose position (`J_ABSOLUTE_APOSE`).
4. Constrain the armature to the empties:
    ```python
    copy_loc = pose_bone.constraints.new('COPY_LOCATION')   # latest attempt, or no copy_loc earlier
    track = pose_bone.constraints.new('DAMPED_TRACK')
    ```
5. Bake; remove empties.

On paper this should give you frame 0 = A-pose, followed by the mocap animation. In practice it fails for structural reasons.

## Key Problems

### 1. Bones inherit their origin from parents (hierarchical system)

Even if you set the empties to A-pose coordinates, a child bone’s head is the parent’s tail. `DAMPED_TRACK` only aims the bone; it doesn’t move the head. So the hierarchy keeps reproducing the mocap rest pose:

```
Bone head position = parent tail
```

Once Blender evaluates the constraints the chain snaps back to where it was built.

### 2. Copying bone location introduces double transforms

If you add:

```python
copy_loc = pose_bone.constraints.new('COPY_LOCATION')
copy_loc.target_space = copy_loc.owner_space = 'WORLD'
```

you force the bone head to the empty’s absolute position. But the parent transform still applies, so the bone gets translated twice. Distances between head/tail change and the rig appears stretched/exploded. (That’s the regression you saw.)

### 3. Root alignment still matters

The root (pelvis) alignment earlier (`align_root_to_reference`) only adjusted translation. If we want frame 0 to be the A-pose rest pose, we should rebuild the armature from `J_ABSOLUTE_APOSE` _and_ compute the mocap rotations relative to that rest pose. Merely overriding frame 0 empties doesn’t change the underlying FK calculations.

## Code Snapshot (relevant sections)

```python
# Build armature (current code)
joint_positions_frame0_raw = forward_kinematics(poses[0], trans[0])
joint_positions_frame0 = align_root_to_reference(joint_positions_frame0_raw, reference_pelvis)

# Set empties at frame 0
bpy.context.scene.frame_set(0)
for i, empty in enumerate(empties):
    empty.location = Vector(J_ABSOLUTE_APOSE[i])
    empty.keyframe_insert(data_path="location", frame=0)

# Add constraints (simplified)
copy_loc = pose_bone.constraints.new('COPY_LOCATION')        # recent attempt
track = pose_bone.constraints.new('DAMPED_TRACK')
```

Because the armature was built from mocap frame 0 lengths and parent geometry, those new empties don’t match the rest offsets. The constraints either leave the bone heads in place (no copy_loc) or apply duplicate transforms (copy_loc).

## What Would Work

1. **Rebuild armature from the A-pose** – set rest positions = `J_ABSOLUTE_APOSE`, recompute `SMPL_OFFSETS` accordingly. Then apply the frame 0 empties—no mismatch.
2. **Convert mocap rotations** so frame 0 is identity relative to the A-pose rest pose (i.e. re-bake `poses` to that rest pose). Then FK alone would produce frame 0 = A-pose, no empties override required.
3. **Instead of constraints** apply the A-pose onto the armature (pose mode) before baking, so the bones actually rest in that posture.
4. Use a more sophisticated constraint/driver setup that mixes local and global transforms but respects the hierarchy—a lot more work than switching the rest data or the mocap rotations.

Until we adopt one of those strategies, overriding frame 0 empties while leaving the armature built for the mocap T-pose rest pose will keep producing a mangled frame 0.
