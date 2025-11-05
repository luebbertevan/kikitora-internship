# What Information is Missing from NPZ Files?

## The Core Problem

**To run Forward Kinematics (FK) and compute joint positions, you need THREE things:**

1. ✅ **`poses`** - Rotations (axis-angle) for each joint - **WE HAVE THIS**
2. ✅ **`trans`** - Root translation (pelvis position) - **WE HAVE THIS**
3. ❌ **`SMPL_OFFSETS`** - Bone lengths/offsets - **WE DON'T HAVE THIS**

## What's in the NPZ File

```python
npz_data.keys() = ['poses', 'trans', 'betas', 'gender', 'mocap_framerate', 'dmpls']
```

-   **`poses`**: (num_frames, 156) - Rotations for 52 joints × 3 axis-angle values
-   **`trans`**: (num_frames, 3) - Root translation per frame
-   **`betas`**: (16,) - Body shape parameters (can be used to compute bone lengths with SMPL model)
-   **`gender`**: Gender of subject
-   **`mocap_framerate`**: Frame rate
-   **`dmpls`**: Soft tissue deformation parameters

**What's NOT in the NPZ:**

-   ❌ `J_ABSOLUTE` - Original joint positions
-   ❌ `SMPL_OFFSETS` - Original bone lengths
-   ❌ Any explicit skeleton structure

## Why This is a Problem

### Forward Kinematics Requires Bone Lengths

FK works like this:

```python
for each joint i:
    # 1. Apply rotation from poses[i]
    rotated_offset = rotation_matrix @ SMPL_OFFSETS[i]

    # 2. Add to parent's position
    if parent == -1:  # Root
        joint_position[i] = trans + rotated_offset
    else:
        joint_position[i] = parent_position + rotated_offset
```

**The critical issue**: `SMPL_OFFSETS[i]` is the **bone vector** (length + direction). Without it, we can't compute where the joint should be!

### Example: Why Bone Lengths Matter

**Scenario**: L_Hip → L_Knee bone

**Original subject (what animation was created with):**

-   Bone length: 0.45m
-   Rotation: 30 degrees forward
-   Result: L_Knee at position `[0.1, 0, 0.55]`

**If we use wrong bone length (0.35m):**

-   Same rotation: 30 degrees forward
-   Result: L_Knee at position `[0.1, 0, 0.65]` ❌ **WRONG!**

The rotation is correct, but the bone length is wrong, so the joint ends up at the wrong position.

## Why T-Pose Extraction is Problematic

### The Chicken-and-Egg Problem

1. **To compute joint positions**, we need bone lengths
2. **To measure bone lengths**, we need joint positions
3. **Circular dependency!**

### What the Bootstrap Approach Does (and Why It Fails)

```python
# Step 1: Use rough estimates of bone lengths
bootstrap_offsets = [rough_estimates...]

# Step 2: Run FK with these estimates
joint_positions = FK(poses, trans, bootstrap_offsets)

# Step 3: Measure bone lengths from these positions
measured_offsets = measure_from_positions(joint_positions)

# Problem: These positions are WRONG because we used wrong bone lengths!
# So the measured offsets are also WRONG!
```

**The fundamental issue**: If the bootstrap bone lengths are wrong, the joint positions are wrong, so the measured bone lengths are also wrong.

## What's Actually Complicated

### 1. **Poses Assume Specific Bone Lengths**

The `poses` rotations were created assuming the original subject's bone lengths. If you use different bone lengths:

-   Joints end up at wrong positions
-   Animation looks distorted
-   Movement direction is wrong (because joints are in wrong places)

### 2. **Coordinate System Assumptions**

The `trans` and `poses` assume a specific coordinate system orientation. If the skeleton structure is wrong:

-   Wrong bone directions → wrong joint positions
-   Wrong joint positions → wrong animation direction
-   This explains the "moving in strange direction" issue

### 3. **No Direct Way to Get Bone Lengths**

The NPZ file doesn't contain bone lengths directly. The only way to get them is:

-   **Option A**: Use `betas` + SMPL model to compute original bone lengths
-   **Option B**: Infer from animation data (problematic, as we've seen)
-   **Option C**: Use a reference skeleton (defeats the purpose of "original mocap")

## Why Axis/Orientation Issues Occur

### Wrong Bone Directions

If bone lengths are extracted incorrectly:

-   Bones point in wrong directions
-   Skeleton structure is wrong
-   Joints are in wrong positions relative to each other

### Example:

**Correct skeleton:**

```
Pelvis → Spine1 (upward +Z)
Spine1 → Spine2 (upward +Z)
```

**Wrong skeleton (if bone extraction is off):**

```
Pelvis → Spine1 (maybe wrong direction)
Spine1 → Spine2 (maybe wrong direction)
```

This causes the entire animation to be oriented incorrectly.

## What Information is Actually Missing?

### The Missing Piece: Original Bone Lengths

**The NPZ file contains:**

-   ✅ How to rotate bones (`poses`)
-   ✅ Where the root is (`trans`)
-   ❌ How long bones are (bone lengths)

**Why this matters:**

-   Rotations alone don't tell you where joints are
-   You need: `rotation` + `bone_length` → joint position
-   Without bone lengths, FK can't compute positions

### The Root Cause

The motion capture data was created using a specific skeleton (with specific bone lengths). The NPZ file stores:

-   The rotations that worked with that skeleton
-   But NOT the skeleton structure itself

**Analogy**:

-   It's like having a recipe that says "rotate 30 degrees" but doesn't tell you how long the arm is
-   You need to know the arm length to figure out where the hand ends up

## Solutions

### Option 1: Use Betas + SMPL Model (Best)

If `betas` are available:

1. Load SMPL model
2. Use `betas` to compute original `J_ABSOLUTE`
3. Compute `SMPL_OFFSETS` from `J_ABSOLUTE`
4. Use in FK → **FAITHFUL**

**Problem**: Requires SMPL model files and code

### Option 2: Check if NPZ Contains Original Data

Some NPZ files might contain:

-   `J_ABSOLUTE` - Original joint positions
-   Or other skeleton structure data

**Check**: Inspect NPZ keys to see what's available

### Option 3: Use Reference Skeleton (Not Original)

Use a reference skeleton (like `J_ABSOLUTE_REFERENCE`):

-   **Pro**: Works reliably
-   **Con**: Not faithful to original (uses wrong bone lengths)

### Option 4: Accept Limitations

If we can't get original bone lengths:

-   Use reference skeleton
-   Document that output is not fully faithful
-   Use for retargeting, not for "original mocap" validation

## Why the Bootstrap Approach Causes Orientation Issues

### The Problem with Hardcoded Bootstrap Offsets

In the script, I used hardcoded offsets like:

```python
3: np.array([0.0, 0.0, 0.1]),   # Spine1 - assumes upward in +Z
1: np.array([0.05, 0.0, -0.2]),  # L_Hip - assumes left in +X, down in -Z
```

**These assumptions are WRONG because:**

1. **Coordinate system unknown**: We don't know if the original animation uses Z-up, Y-up, or a different orientation
2. **Bone directions unknown**: We don't know which way bones point in the original skeleton
3. **Wrong assumptions → wrong skeleton → wrong animation**

### Example of What Goes Wrong

**If the original animation uses Y-up (not Z-up):**

-   Bootstrap assumes Spine1 is at `[0, 0, 0.1]` (Z-up)
-   But original might have Spine1 at `[0, 0.1, 0]` (Y-up)
-   Result: Entire skeleton is rotated 90 degrees
-   Animation moves in wrong direction

**If bone directions are wrong:**

-   Bootstrap assumes L_Hip points left in +X
-   But original might have L_Hip pointing differently
-   Result: Skeleton structure is wrong
-   Joints end up in wrong positions
-   Animation looks distorted

## Why T-Pose Extraction Can't Fix This

### The Circular Dependency

1. **To measure bone directions**, we need to run FK to see where joints are
2. **To run FK**, we need bone directions (SMPL_OFFSETS)
3. **Circular!**

### The Bootstrap Approach is Fundamentally Flawed

```python
# Step 1: Use WRONG bone directions (hardcoded assumptions)
bootstrap_offsets = [wrong_directions...]

# Step 2: Run FK with wrong directions
joint_positions = FK(poses, trans, bootstrap_offsets)
# Result: Joints are in WRONG positions (wrong coordinate system)

# Step 3: Measure bone lengths from wrong positions
measured_offsets = measure_from_positions(joint_positions)
# Result: Measured offsets have WRONG directions (because positions were wrong)

# Step 4: Use wrong offsets for all frames
# Result: Entire animation is oriented incorrectly
```

**The fundamental issue**: If the initial bone directions are wrong, everything downstream is wrong, and we can't recover from it.

## What Information is Actually Missing?

### Missing Information in NPZ:

1. **Bone lengths** - How long each bone is
2. **Bone directions** - Which way each bone points (coordinate system)
3. **Skeleton structure** - The original skeleton's rest pose

### What We Have:

-   ✅ `poses` - Rotations (but these assume specific bone lengths/directions)
-   ✅ `trans` - Root translation (but in what coordinate system?)
-   ✅ `betas` - Shape parameters (can compute bone lengths with SMPL model)

### Why `betas` + SMPL Model is the Solution

The `betas` parameters define the original subject's body shape. With an SMPL model:

1. `betas` → Original `J_ABSOLUTE` (joint positions)
2. `J_ABSOLUTE` → `SMPL_OFFSETS` (bone lengths AND directions)
3. Use in FK → **Correct orientation and bone lengths**

**This is the ONLY way to get original bone lengths AND directions without a reference skeleton.**

## Conclusion

**What's missing**:

1. Bone lengths (`SMPL_OFFSETS` magnitudes)
2. Bone directions (`SMPL_OFFSETS` directions - coordinate system)
3. Original skeleton structure

**Why it's complicated**:

-   FK requires bone lengths AND directions to compute positions
-   NPZ doesn't contain bone lengths or directions
-   Extracting from animation data requires bootstrap (which is wrong if assumptions are wrong)
-   Wrong assumptions → wrong skeleton → wrong animation orientation

**Why the T-pose extraction step fails**:

-   We still need bootstrap with assumptions about bone directions
-   If assumptions are wrong (wrong coordinate system), skeleton is wrong
-   Can't recover from wrong bootstrap assumptions

**The real solution**:

1. Use `betas` + SMPL model to compute original `J_ABSOLUTE` and `SMPL_OFFSETS`
2. OR use a reference skeleton (but then it's not "original mocap")
3. OR accept that we can't extract original mocap without additional information

**The fundamental problem**: You cannot extract bone lengths AND directions from `poses` + `trans` alone. You need either:

-   `betas` + SMPL model (to compute original skeleton)
-   A reference skeleton (but then it's not original)
-   Some other source of skeleton structure information
