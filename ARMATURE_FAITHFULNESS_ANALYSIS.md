# How the Hardcoded Armature Affects Output Faithfulness

## The Key Question

**Does `create_glb_from_npz_fixed.py` output a faithful representation of the original motion capture data, or does the hardcoded armature interfere?**

## Short Answer

**The hardcoded armature DOES interfere** if the original subject had different bone lengths than the reference skeleton. However, if all AMASS animations use a standardized skeleton (betas ≈ 0), then it's faithful.

## What Gets Used from the NPZ File

From the **original motion capture data** (NPZ file):

-   ✅ `poses` - The rotation data (axis-angle) for each joint - **USED AS-IS**
-   ✅ `trans` - The root translation - **USED AS-IS**

## What Gets Hardcoded (Not from NPZ)

From the **hardcoded reference skeleton** (top of file):

-   ❌ `J_ABSOLUTE` - Hardcoded joint positions (lines 31-58)
-   ❌ `SMPL_OFFSETS` - Computed from hardcoded `J_ABSOLUTE` (lines 62-68)

## The Critical Line

**Line 114 in `forward_kinematics()`:**

```python
local_transform[:3, 3] = SMPL_OFFSETS[i]  # Uses HARDCODED bone lengths
```

This means:

-   The **rotations** come from the original motion capture (`poses`)
-   The **bone lengths** come from the hardcoded reference skeleton (`SMPL_OFFSETS`)

## What Happens When Bone Lengths Don't Match

### Scenario: Original subject had longer legs

**Original Motion Capture:**

-   Subject's leg bone length: 0.45m
-   Animation was created using rotations that work with 0.45m bones
-   `poses` contain rotations that assume 0.45m bone length

**What `create_glb_from_npz_fixed.py` does:**

-   Uses hardcoded reference bone length: 0.40m
-   Applies original rotations to 0.40m bones
-   Result: Joints end up at wrong positions

**Example:**

```
Original FK (with 0.45m bones):
L_Hip = [0.1, 0, 0.95]
L_Knee = [0.15, 0, 0.50]  ← Correct position

create_glb_from_npz FK (with 0.40m bones):
L_Hip = [0.1, 0, 0.95]
L_Knee = [0.13, 0, 0.55]  ← WRONG! Too high (shorter bone)
```

The animation will look **compressed** or **stretched** because:

-   The rotations are correct (from original motion)
-   But the bone lengths are wrong (from hardcoded reference)
-   FK computes wrong joint positions → wrong animation

## How the Armature is Created

**Lines 329-330:**

```python
joint_positions_frame0: NDArray[np.float64] = forward_kinematics(poses[0], trans[0])
```

The armature is created using:

1. Frame 0's `poses` (from NPZ) - ✅ Original data
2. Frame 0's `trans` (from NPZ) - ✅ Original data
3. Hardcoded `SMPL_OFFSETS` - ❌ Not from original subject

**Result:** The armature's bone lengths match the hardcoded reference, not the original subject.

## The Empties Animation

**Lines 396-401:**

```python
joint_positions: NDArray[np.float64] = forward_kinematics(poses[frame_idx], trans[frame_idx])
# ...
empties[i].location = Vector(joint_positions[i])
```

Every frame uses:

-   Original `poses[frame_idx]` - ✅
-   Original `trans[frame_idx]` - ✅
-   Hardcoded `SMPL_OFFSETS` - ❌

**Result:** All empties are positioned using FK with wrong bone lengths.

## Is This Faithful?

### If AMASS data is standardized (betas ≈ 0):

-   ✅ **FAITHFUL** - All animations use same bone lengths as the hardcoded reference
-   The hardcoded `SMPL_OFFSETS` match the original subject's bone lengths
-   FK produces correct joint positions
-   Animation looks correct

### If AMASS data has varying bone lengths (betas vary):

-   ❌ **NOT FAITHFUL** - Different subjects have different bone lengths
-   The hardcoded `SMPL_OFFSETS` don't match the original subject's bone lengths
-   FK produces incorrect joint positions
-   Animation looks compressed/stretched/distorted

## The Missing Piece: Betas

**What the NPZ file contains but we're NOT using:**

-   `betas` - Shape parameters that define the subject's body proportions
-   These could be used to compute the original subject's bone lengths
-   But `create_glb_from_npz_fixed.py` completely ignores `betas`

**Line 317-318:**

```python
poses: NDArray[np.float64] = data['poses']
trans: NDArray[np.float64] = data['trans']
# betas is NOT loaded!
```

## Summary Table

| Component                     | Source                | Used in FK? | Faithful?           |
| ----------------------------- | --------------------- | ----------- | ------------------- |
| Joint rotations (`poses`)     | NPZ (original)        | ✅ Yes      | ✅ Yes              |
| Root translation (`trans`)    | NPZ (original)        | ✅ Yes      | ✅ Yes              |
| Bone lengths (`SMPL_OFFSETS`) | Hardcoded (reference) | ✅ Yes      | ❓ Depends on betas |
| Body shape (`betas`)          | NPZ (original)        | ❌ No       | ❌ Ignored          |

## Conclusion

The hardcoded armature **does interfere** if bone lengths vary across AMASS animations. The script:

1. ✅ Uses original rotations and translations faithfully
2. ❌ Uses hardcoded bone lengths instead of computing from `betas`
3. ❌ Produces incorrect joint positions if original subject had different proportions

**To make it truly faithful**, you would need to:

1. Load `betas` from the NPZ file
2. Use an SMPL model to compute the original subject's bone lengths from `betas`
3. Use those bone lengths in FK instead of the hardcoded `SMPL_OFFSETS`

This is exactly what **bone length retargeting (M5)** would do - it would compute the original bone lengths and then retarget to the reference skeleton.
