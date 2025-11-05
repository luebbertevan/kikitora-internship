# Bone Length Mismatch Explained

## What Actually Happens

### The Forward Kinematics Process

When FK runs, for each bone it does:

```python
# Line 100 in original_retarget.py
local_transform[:3, 3] = SMPL_OFFSETS[i]  # The bone vector (offset)
# Then:
global_position = parent_global_position + rotated_offset
```

**Key point:** The `SMPL_OFFSETS[i]` is the **bone vector** - it has both direction AND length.

### Concrete Example: L_Hip → L_Knee

**Scenario:** Source person has longer legs than reference

**Source Person (when animation was created):**

-   L_Hip position: `[0.1, 0, 0.95]`
-   L_Knee position: `[0.15, 0, 0.55]` (from source person's bone lengths)
-   Bone length: `0.4m` (distance from hip to knee)
-   `SMPL_OFFSETS[L_Knee]` = `[0.05, 0, -0.4]` (vector from L_Hip to L_Knee)

**Reference Person:**

-   L_Hip position: `[0.1, 0, 0.95]` (same)
-   L_Knee position: `[0.13, 0, 0.60]` (from reference bone lengths)
-   Bone length: `0.35m` (shorter!)
-   `SMPL_OFFSETS[L_Knee]` = `[0.03, 0, -0.35]` (different vector!)

**What happens in original_retarget:**

1. FK runs with **reference** `SMPL_OFFSETS` (0.35m bone)
2. Input `poses` contain rotation that worked with **source** bone (0.4m)
3. FK computes: `L_Knee = L_Hip + rotated(reference_offset)`
4. Because reference offset is shorter, L_Knee ends up at wrong position

**Example calculation:**

Source FK (what animation expects):

```
L_Knee = L_Hip + rotated([0.05, 0, -0.4])
       = [0.1, 0, 0.95] + rotated([0.05, 0, -0.4])
       = [0.15, 0, 0.55]  ✓ Correct
```

Reference FK (what original_retarget does):

```
L_Knee = L_Hip + rotated([0.03, 0, -0.35])  # Using reference bone!
       = [0.1, 0, 0.95] + rotated([0.03, 0, -0.35])
       = [0.13, 0, 0.60]  ✗ Wrong position!
```

**The rotation is the same, but the bone length is different, so the child joint position is wrong.**

---

## Why Rotations Don't Work for Different Bone Lengths

**The key insight:** Rotations are applied to the bone vector (offset). If the vector length is different, the resulting position is different.

**Mathematical explanation:**

```
Child position = Parent position + Rotation × Offset
```

If `Offset` has different length:

-   Same rotation
-   Different offset length
-   → Different child position

**Visual analogy:**

-   Imagine rotating a 10cm stick vs a 15cm stick
-   Same rotation angle
-   But the end of the stick is at a different distance from the start
-   → Different final position

---

## What "Incorrect Joint Positions" Means

**"Incorrect" means:** The joint positions don't match what the animation was designed for.

**Example:**

-   Animation was designed for person with 0.4m thigh bone
-   FK computes positions assuming 0.35m thigh bone
-   Result: Knee is 5cm too close to hip
-   Downstream joints (ankle, foot) are also wrong (cascading error)

**Visual result:**

-   Leg appears shorter than intended
-   Body proportions are wrong
-   Motion looks compressed/stretched
-   Joints don't align with where they should be

---

## What "Animation Looks Wrong" Means

**Concrete examples:**

1. **Proportions are wrong:**

    - If source person was 6ft tall, reference is 5ft 8in
    - Animation looks compressed (person appears shorter)
    - Legs/arms don't match body size

2. **Joint positions are wrong:**

    - Hand doesn't reach where it should
    - Foot doesn't touch ground when it should
    - Body parts don't align correctly

3. **Motion looks distorted:**
    - Walking stride is too short
    - Arm swing is too small
    - Overall motion doesn't match original intent

**Why this matters:**

-   Animation was created for specific body proportions
-   Using different proportions breaks the motion
-   It's like trying to fit a 6ft person's motion onto a 5ft person's skeleton

---

## About "Source Person's SMPL_OFFSETS"

**You're absolutely right - we don't have this in the code!**

I was making an assumption. Let me clarify:

**What we actually have:**

-   Input NPZ file contains `poses` and `trans`
-   We don't know what `SMPL_OFFSETS` were used to create those poses
-   Those poses were created by someone/something that had access to source person's model parameters

**What we assume:**

-   The poses were created using the source person's bone lengths (their `SMPL_OFFSETS`)
-   We don't have those values, but we know they exist
-   The poses are "encoded" assuming those bone lengths

**The real issue:**

-   We only have `poses` (rotations)
-   We don't have the source person's `SMPL_OFFSETS`
-   We use reference `SMPL_OFFSETS` instead
-   This mismatch causes wrong joint positions

**Better way to think about it:**

-   Poses are "instructions" that say "rotate bone X by Y degrees"
-   Those instructions assume specific bone lengths
-   If you use different bone lengths, the end result is wrong
-   Like trying to follow directions for a 10cm stick when you have a 15cm stick

---

## Summary

**The core problem:**

1. Input `poses` were created assuming source person's bone lengths
2. We don't have those bone lengths
3. We use reference bone lengths instead
4. FK computes wrong joint positions because bone lengths don't match
5. Wrong joint positions → animation looks wrong

**Why it matters:**

-   Rotations are applied to bone vectors
-   Different bone vector lengths → different final positions
-   Even with same rotation, wrong bone length = wrong position
-   This cascades through the skeleton

**The solution (what retargeting does):**

-   Adjust bone rotations to compensate for different bone lengths
-   Maintain target joint positions while using reference bone lengths
-   This is what "retargeting" means - adapting motion to different proportions
