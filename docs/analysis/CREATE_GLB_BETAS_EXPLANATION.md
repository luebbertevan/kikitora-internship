# Does create_glb_from_npz.py Use Betas?

## Answer: **NO, it does NOT use betas**

## What "Creates armature from frame 0 pose" Means

**Line 296 in create_glb_from_npz.py:**

```python
joint_positions_frame0: NDArray[np.float64] = forward_kinematics(poses[0], trans[0])
```

This means:

1. It takes **frame 0** of the animation (`poses[0]`, `trans[0]`)
2. Runs **forward kinematics** to compute joint positions
3. Uses those joint positions to **create the armature bones**

**Why frame 0 instead of T-pose?**

-   Frame 0 is the actual starting pose of the animation
-   This ensures bone orientations match the animation's starting pose
-   T-pose would be zero rotations, which might not match

## Where Betas Would Be Used (But Aren't)

**Betas would be used here:**

-   Line 114: `local_transform[:3, 3] = SMPL_OFFSETS[i]`

**But SMPL_OFFSETS is computed from:**

-   Line 62-68: Hardcoded `J_ABSOLUTE` (reference T-pose values)
-   NOT from betas!

```python
# Line 62-68
SMPL_OFFSETS: NDArray[np.float64] = np.zeros((52, 3))
for i in range(52):
    parent_idx = SMPL_H_PARENTS[i]
    if parent_idx == -1:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i]  # Hardcoded reference!
    else:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]  # Hardcoded reference!
```

## What the Code Actually Does

**Line 283-285: Loads NPZ data**

```python
data = np.load(str(npz_path))
poses: NDArray[np.float64] = data['poses']
trans: NDArray[np.float64] = data['trans']
# Note: betas is NOT loaded!
```

**Line 296: Runs FK on frame 0**

```python
joint_positions_frame0 = forward_kinematics(poses[0], trans[0])
```

**Line 114 (inside FK): Uses hardcoded SMPL_OFFSETS**

```python
local_transform[:3, 3] = SMPL_OFFSETS[i]  # Hardcoded, not from betas!
```

**Line 312: Creates armature bones from FK positions**

```python
bone.head = Vector(joint_positions_frame0[i])
```

## Summary

**"Creates armature from frame 0 pose" means:**

-   Uses frame 0 `poses` and `trans` to compute joint positions via FK
-   Creates armature bones at those positions
-   **But FK uses hardcoded `SMPL_OFFSETS` (reference skeleton), NOT betas**

**The code does NOT:**

-   Load `betas` from NPZ file
-   Compute `SMPL_OFFSETS` from `betas`
-   Use source person's bone lengths

**The code DOES:**

-   Use hardcoded reference `J_ABSOLUTE` → `SMPL_OFFSETS`
-   Use frame 0 `poses` and `trans` for FK
-   Create armature from frame 0 FK positions

## Why This Matters

Just like `original_retarget.py`, `create_glb_from_npz.py` also:

-   Ignores `betas` completely
-   Uses reference bone lengths (hardcoded)
-   Assumes poses will work with reference bone lengths

This is the same issue we discussed - the poses might have been created with different bone lengths, but the code uses reference bone lengths.
