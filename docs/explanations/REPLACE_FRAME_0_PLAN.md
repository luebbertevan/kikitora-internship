# Replace Frame 0 With Blender A-Pose (Using Empties)

Goal: make frame 0 of the exported animation identical to the Blender A-pose from `New-A-Pose.blend`, without touching the rest of the frames. We’ll use the empties-driven pipeline in `create_glb_from_npz_fixed.py`. Instead of solving for local axis-angle rotations, we directly set the empties at frame 0 to the target A-pose world positions, then bake as usual.

---

## Requirements / Inputs

-   `data/reference/apose_from_blender.npz` – contains `J_ABSOLUTE` with the target A-pose joint world positions (extracted from Blender).
-   `create_glb_from_npz_fixed.py` – pipeline that:
    -   Builds empties for each joint.
    -   Uses FK to set empties at every frame.
    -   Constrains + bakes the armature from those empties.

---

## Step-by-Step Plan

1. **Load A-pose world positions**

    - At script startup (before processing NPZ frames), load `J_ABSOLUTE_APOSE = np.load(...)["J_ABSOLUTE"]`.

2. **Create empties as usual**

    - For each joint, make an empty object (already implemented in `create_glb_from_npz_fixed.py`).

3. **Frame 0 override**

    - After creating empties and before looping through FK frames, set scene to frame 0.
    - For each empty `i`, assign `empty.location = Vector(J_ABSOLUTE_APOSE[i])` and insert a location keyframe at frame 0.
    - This locks the empties to the exact A-pose world coordinates for frame 0.

4. **Process remaining frames**

    - For frames `1..N-1`, run the existing FK loop (computing `forward_kinematics` on the mocap data) and keyframe empties normally.

5. **Bake constraints**

    - Same as before: constrain armature to empties, bake to keyframes, remove empties. The baked frame 0 will now match the A-pose.

6. **Export GLB**
    - No changes to the export step.

---

## Pseudocode Snippet

```python
# After empties are created, before FK loop
bpy.context.scene.frame_set(0)
for i, empty in enumerate(empties):
    empty.location = Vector(J_ABSOLUTE_APOSE[i])
    empty.keyframe_insert(data_path="location", frame=0)

# Continue with FK loop starting at frame 1
for frame_idx in range(1, len(poses)):
    bpy.context.scene.frame_set(frame_idx)
    joint_positions = forward_kinematics(poses[frame_idx], trans[frame_idx])
    for i, empty in enumerate(empties):
        empty.location = Vector(joint_positions[i])
        empty.keyframe_insert(data_path="location", frame=frame_idx)
```

---

## Validation Checklist

1. Import the resulting GLB into Blender. Frame 0 should visually match `New-A-Pose.blend`.
2. Check frame 1+ to ensure mocap animation continues unchanged.
3. Optional: run FK on frame 0 after baking to confirm joint positions ≈ `J_ABSOLUTE_APOSE`.

---

## Notes

-   Refresh `apose_from_blender.npz` whenever you tweak the A-pose in Blender.
-   This method avoids reconstructing local rotations—empties act as authoritative world-space targets.
-   `retarget.py` can keep using its FK logic; for the empties pipeline, only frame 0 empties need overwriting.
