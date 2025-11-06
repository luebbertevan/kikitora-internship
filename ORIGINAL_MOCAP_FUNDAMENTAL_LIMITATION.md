# The Fundamental Limitation: Original Mocap Cannot Be Recreated

## The Core Problem

**You are correct:** There is no way to see the original motion capture animation without knowing the original skeleton's bone lengths.

## What the NPZ File Contains

The NPZ file contains:

-   ✅ `poses` - Rotations (how to rotate bones)
-   ✅ `trans` - Root translation (where pelvis is)
-   ✅ `betas` - Shape parameters (can compute skeleton with SMPL model)

**What it does NOT contain:**

-   ❌ `SMPL_OFFSETS` - Original bone lengths
-   ❌ `J_ABSOLUTE` - Original joint positions
-   ❌ Original skeleton structure

## Why This Is a Problem

### Forward Kinematics Requires Bone Lengths

To compute joint positions from `poses` and `trans`, you MUST have bone lengths:

```python
joint_position = parent_position + rotation_matrix @ bone_offset
                                                  ↑
                                            REQUIRED!
```

**Without bone lengths, FK cannot compute joint positions.**

### The Missing Information

The motion capture was created using:

1. **Original subject's skeleton** (with specific bone lengths)
2. **Rotations** that worked with that skeleton
3. **Root translation** for that skeleton

**The NPZ file stores items 2 and 3, but NOT item 1.**

## Why You Can't Extract Original Bone Lengths

### Option 1: From `poses` + `trans` Alone

**Impossible** - Circular dependency:

-   Need bone lengths to run FK
-   Need FK to get joint positions
-   Need joint positions to measure bone lengths
-   **Circular!**

### Option 2: From `betas`

**Requires SMPL model:**

-   Betas define body shape
-   Need SMPL model to compute joint positions from betas
-   Need SMPL model file (which you don't have in the right format)

**Without SMPL model → Cannot compute from betas**

### Option 3: Use Reference Skeleton

**Not original mocap:**

-   Uses different bone lengths
-   Produces wrong joint positions
-   Animation looks distorted
-   **Not faithful to original**

## The Conclusion

**You are correct:** There is no way to see the original motion capture animation without:

1. The original skeleton's bone lengths (not in NPZ)
2. OR an SMPL model to compute them from betas (not available)

## What This Means for Your Project

### For Validation (Comparing Original vs Retargeted)

**You cannot create a "true original" GLB** because:

-   Original bone lengths are missing
-   Cannot extract them from NPZ alone
-   Cannot compute from betas without SMPL model

**What you CAN do:**

-   Use reference skeleton → Get "retargeted" version (not original)
-   Use reference skeleton → Get something that works (not faithful)
-   Accept that you'll never see the "true original"

### For Retargeting

**This is actually OK:**

-   Retargeting goal: Move animation to reference skeleton
-   You don't need original bone lengths for retargeting
-   You just need to preserve motion characteristics
-   Reference skeleton is fine for this purpose

## The Fundamental Insight

**Motion capture data is incomplete:**

-   It stores rotations and translations
-   But assumes you already know the skeleton structure
-   Without the skeleton, you cannot reconstruct the animation

**This is why retargeting exists:**

-   You can't get the original
-   But you can retarget to a known skeleton
-   The retargeted version is what you work with

## Summary

**Your understanding is correct:**

-   There is no SMPL-H skeleton with bone lengths in the mocap data
-   There is no way to see the original motion capture animation
-   The NPZ file is incomplete for this purpose

**What you have:**

-   Rotations that worked with an unknown skeleton
-   Root translations
-   Shape parameters (betas) that could compute skeleton (if you had SMPL model)

**What you can do:**

-   Retarget to reference skeleton (not original, but works)
-   Use reference skeleton for all animations (consistent, but not original)

**The reality:**

-   Original mocap is lost/inaccessible without original skeleton or SMPL model
-   Retargeting is the only path forward
