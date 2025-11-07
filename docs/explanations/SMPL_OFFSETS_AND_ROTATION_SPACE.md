# SMPL_OFFSETS, Rotation Space, and Why Starting Pose Matters

## Critical Understanding: SMPL_OFFSETS Are NOT Just Bone Lengths

### What SMPL_OFFSETS Actually Are

**SMPL_OFFSETS are bone direction vectors, not just lengths.**

-   **Magnitude** = bone length (distance from parent to child)
-   **Direction** = bone orientation in the rest pose (which way the bone points)

Example:

-   T-pose L_Shoulder bone: points horizontally to the left
-   A-pose L_Shoulder bone: points down and to the left (~45° angle)

Both have the same **length**, but different **directions**.

### How Forward Kinematics Uses SMPL_OFFSETS

In `forward_kinematics()`:

```python
local_transform[:3, 3] = SMPL_OFFSETS[i]  # This is a VECTOR, not just a length!
```

The SMPL_OFFSETS vector is used as the **local translation** in the bone's coordinate system. Then rotations are applied:

```python
local_transform[:3, :3] = rot_mat  # Rotation from mocap
```

**The rotation is applied to the SMPL_OFFSETS vector.**

## Why Starting Pose Matters

### The Problem

1. **Mocap rotations are relative to the mocap's rest pose** (typically T-pose)
    - When mocap says "rotate shoulder 30°", it means "30° from T-pose"
2. **Your SMPL_OFFSETS are from A-pose** (after you switched)
    - The bone directions point in A-pose directions
3. **Applying T-pose rotations to A-pose bone directions = wrong result**

### Concrete Example

**Scenario**: Mocap says "rotate L_Shoulder 30° forward"

-   **If SMPL_OFFSETS is T-pose**: Bone points left (horizontal). Rotate 30° forward → points down-left. ✅ Correct
-   **If SMPL_OFFSETS is A-pose**: Bone already points down-left (~45°). Rotate 30° forward → points too far down. ❌ Wrong!

The rotation is being applied **relative to the wrong starting direction**.

### Visual Analogy

Imagine you're holding a stick:

-   **T-pose**: Stick points horizontally to your left
-   **A-pose**: Stick points down-left at 45°

Someone says "rotate the stick 30° forward":

-   From T-pose: You rotate from horizontal → 30° down. Result: 30° down from horizontal ✅
-   From A-pose: You rotate from 45° down → 75° down. Result: 30° more than before, but wrong starting point ❌

## What "Mocap Rotations Relative to Rest Pose" Means

### How Forward Kinematics Works

Forward kinematics always works relative to the **current rest pose** (defined by SMPL_OFFSETS):

1. Start with rest pose (SMPL_OFFSETS define bone directions)
2. Apply rotations to those bone directions
3. Get final joint positions

**Key Point**: Rotations are **always relative to whatever rest pose SMPL_OFFSETS defines**.

### The Problem

**Mocap rotations were created assuming a specific rest pose** (likely T-pose, the standard SMPL rest pose).

When you:

-   Change SMPL_OFFSETS to A-pose directions
-   Apply mocap rotations (which assume T-pose rest pose)
-   You get wrong results because the rotations are relative to the wrong starting pose

### Test Results

We tested: "What happens with zero rotations give?"

-   **With T-pose SMPL_OFFSETS**: Zero rotations → T-pose ✅
-   **With A-pose SMPL_OFFSETS**: Zero rotations → A-pose ✅

This confirms: Rotations are relative to whatever rest pose SMPL_OFFSETS defines.

**But**: The mocap rotations were created assuming T-pose rest pose. So when you use A-pose SMPL_OFFSETS, the mocap rotations are being applied relative to the wrong starting pose.

### What This Means

When you have:

-   Mocap `poses[0]` = `[1.64, -0.25, -0.22]` (pelvis rotation)
-   This was created assuming: "Rotate pelvis 97° from T-pose orientation"

If you apply this to A-pose SMPL_OFFSETS:

-   FK interprets it as: "Rotate pelvis 97° from A-pose orientation"
-   But the rotation was meant for T-pose, not A-pose
-   Result: Wrong rotation because it's relative to wrong starting pose

## The Pelvis Rotation Issue

### What We Found

From diagnostic script `M3_4_2_check_pelvis_rotation.py`:

-   Mocap pelvis rotation: ~97° (1.68 radians)
-   This rotates the entire skeleton
-   When applied, the armature faces the ground

### Why This Happens

The pelvis is the root bone. Its rotation affects the entire skeleton:

-   Pelvis rotates 97° → entire body rotates 97°
-   If this rotation is wrong (relative to wrong rest pose), everything is wrong

### The Fix

**Option 1**: Zero out pelvis rotation (quick fix)

-   Set `poses[:, 0:3] = 0` for all frames
-   This removes the problematic rotation

**Option 2**: Compensate for the rotation (better fix)

-   Compute what rotation is needed to align A-pose to T-pose
-   Apply inverse rotation to pelvis rotations
-   This corrects the rotation space

**Option 3**: Set frame 0 to A-pose (M4 approach)

-   Override frame 0 to match A-pose exactly
-   This aligns the starting pose correctly
-   Frame 1+ will still have issues if rotations are relative to T-pose

## Why Changing J_ABSOLUTE Messes Up Animation

### The Chain of Dependencies

1. **J_ABSOLUTE** → defines joint positions in rest pose
2. **SMPL_OFFSETS** = computed from J_ABSOLUTE (parent-to-child vectors)
3. **Forward Kinematics** uses SMPL_OFFSETS as bone directions
4. **Mocap rotations** are applied to these bone directions
5. **Result** = joint positions after rotations

### What Happens When You Change J_ABSOLUTE

**T-pose J_ABSOLUTE**:

-   Joints in T-pose positions
-   SMPL_OFFSETS point in T-pose directions
-   Mocap rotations (relative to T-pose) applied → ✅ Correct

**A-pose J_ABSOLUTE**:

-   Joints in A-pose positions
-   SMPL_OFFSETS point in A-pose directions
-   Mocap rotations (relative to T-pose) applied → ❌ Wrong!

The bone **lengths** are the same, but the **directions** are different, so rotations produce wrong results.

## Are SMPL_OFFSETS Just Bone Lengths?

### Short Answer: NO

**SMPL_OFFSETS are 3D vectors with:**

-   **Magnitude** = bone length (distance)
-   **Direction** = bone orientation (which way it points)

### Why This Matters

In forward kinematics:

```python
local_transform[:3, 3] = SMPL_OFFSETS[i]  # Full 3D vector, not just length!
```

The entire vector (direction + length) is used. The rotation is then applied to this vector.

### Example

L_Shoulder bone:

-   **T-pose SMPL_OFFSETS**: `[0.26, 0.03, -0.01]` (points left, slightly forward)
-   **A-pose SMPL_OFFSETS**: `[0.18, 0.01, -0.19]` (points down-left)
-   **Length**: Same (~0.26m)
-   **Direction**: Different (T-pose horizontal, A-pose 45° down)

When you apply a rotation:

-   T-pose: Rotates from horizontal direction
-   A-pose: Rotates from 45° down direction
-   **Different starting directions = different results**

## The Solution

### Option 1: Keep T-pose SMPL_OFFSETS, Set Frame 0 to A-pose

-   Use T-pose bone directions (SMPL_OFFSETS)
-   Mocap rotations work correctly (relative to T-pose)
-   Override frame 0 to A-pose visually
-   **Problem**: Frame 1+ will still have wrong rotations (relative to T-pose, not A-pose)

### Option 2: Transform Mocap Rotations to A-pose Space

-   Use A-pose SMPL_OFFSETS (bone directions)
-   Transform mocap rotations from T-pose space to A-pose space
-   Apply transformed rotations
-   **Complex**: Requires computing rotation differences between T-pose and A-pose

### Option 3: Zero Pelvis Rotation + Frame 0 A-pose Override

-   Zero out problematic pelvis rotation
-   Use A-pose SMPL_OFFSETS
-   Override frame 0 to A-pose
-   **Simpler**: Fixes immediate issues, but rotations still relative to wrong pose

## Key Takeaways

1. **SMPL_OFFSETS are vectors (direction + length), not just lengths**
    - They define both bone length AND bone direction in rest pose
2. **Forward kinematics applies rotations relative to the rest pose defined by SMPL_OFFSETS**
    - Zero rotations always give you the rest pose (whatever SMPL_OFFSETS defines)
3. **The problem**: Mocap rotations were likely created assuming T-pose rest pose
    - But you're using A-pose SMPL_OFFSETS
    - So rotations are being applied relative to wrong starting pose
4. **Bone lengths being the same doesn't fix the rotation space issue**
    - Same lengths, different directions = rotations produce different results
5. **The starting pose (rest pose) matters because rotations are relative to it**

## Important Clarification

### What We Know

-   **Test confirmed**: Zero rotations with A-pose SMPL_OFFSETS → A-pose ✅
-   This proves: Rotations are relative to whatever rest pose SMPL_OFFSETS defines

### What We Don't Know (Yet)

-   **What rest pose were the mocap rotations originally created for?**
    -   Likely T-pose (standard SMPL rest pose)
    -   But we need to verify this

### How to Verify

1. **Test with T-pose SMPL_OFFSETS**:
    - Temporarily use T-pose J_ABSOLUTE
    - Apply zero rotations
    - Check if result matches T-pose
2. **Check frame 0 of mocap**:
    - What pose does frame 0 produce?
    - Does it look like T-pose or something else?
3. **Compare to known T-pose**:
    - If mocap frame 0 (with actual rotations) looks like T-pose when using T-pose SMPL_OFFSETS
    - Then mocap rotations are relative to T-pose

## The Real Question

**If mocap rotations are relative to T-pose, but you want to use A-pose SMPL_OFFSETS:**

You need to either:

1. **Transform the rotations** from T-pose space to A-pose space (complex)
2. **Keep T-pose SMPL_OFFSETS** and just override frame 0 to A-pose visually (simpler, but rotations still relative to T-pose)
3. **Find out if mocap rotations can work with A-pose** (need to verify what rest pose they expect)
