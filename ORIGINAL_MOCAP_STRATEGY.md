# Strategy: Extract Original Motion Capture (No Reference Skeleton)

## Goal

Create a GLB that represents the **original motion capture data** without any retargeting to a reference skeleton. This will be used for validation to compare original mocap vs retargeted output.

## Problem

To compute joint positions from `poses` and `trans` using forward kinematics, we need **bone lengths** (`SMPL_OFFSETS`). The current approach uses hardcoded `J_ABSOLUTE_REFERENCE`, which makes the output non-faithful.

## Solution Options

### Option 1: Compute Original Bone Lengths from T-Pose Frame

**Idea**: If we can find a frame where the subject is in a neutral pose (T-pose or A-pose), we can measure the bone lengths directly from the joint positions.

**Steps**:

1. Find a frame with minimal rotations (T-pose or near T-pose)
2. Run FK with some initial bone lengths (even if approximate)
3. Measure actual bone lengths from resulting joint positions
4. Use those measured bone lengths for all frames

**Problem**: We still need bone lengths to run FK in the first place (chicken-and-egg).

**Solution**: Use a two-pass approach:

-   **Pass 1**: Use approximate/reference bone lengths to find T-pose frame
-   **Pass 2**: For T-pose frame, measure actual bone lengths from joint positions
-   **Pass 3**: Use measured bone lengths for all frames

### Option 2: Use Betas + SMPL Model

**Idea**: Load `betas` from NPZ and use SMPL model to compute original bone lengths.

**Steps**:

1. Load `betas` from NPZ file
2. Load SMPL model (`.pkl` file)
3. Use SMPL model to compute `J_ABSOLUTE` from `betas`
4. Compute `SMPL_OFFSETS` from that `J_ABSOLUTE`
5. Use those offsets in FK

**Requirements**:

-   SMPL model files (`.pkl`)
-   SMPL model loading code
-   Functions to compute joint positions from betas

### Option 3: Extract from NPZ File Directly

**Idea**: Some NPZ files might contain `J_ABSOLUTE` or bone length information directly.

**Check**: Inspect NPZ file keys to see if original bone lengths are stored.

### Option 4: Use Zero Poses Frame

**Idea**: If there's a frame with zero rotations (or near-zero), we can compute bone lengths from that frame.

**Steps**:

1. Find frame with `poses` ≈ 0 (or minimal rotations)
2. For that frame, FK with `poses=0` and `trans` gives us joint positions
3. But wait - we still need bone lengths to do FK...

**Actually**: If `poses=0` (all rotations are identity), then:

-   `joint_positions = FK(poses=0, trans, smpl_offsets)`
-   The joint positions depend on `smpl_offsets` (bone lengths)
-   We can't solve this without knowing bone lengths first

## Recommended Approach: Hybrid Two-Pass

### Strategy

1. **Load betas**: Check if `betas` are available in NPZ
2. **If betas available and SMPL model available**:
    - Use SMPL model to compute original `J_ABSOLUTE` from `betas`
    - Compute `SMPL_OFFSETS` from that
    - Use in FK → **FAITHFUL**
3. **If betas not available or SMPL model not available**:
    - Use reference bone lengths to find T-pose frame
    - Measure bone lengths from T-pose joint positions
    - Use measured bone lengths for all frames
    - **May not be perfectly faithful but closer than using reference**

### Implementation Plan

```python
def get_original_bone_lengths(npz_data):
    """
    Extract original bone lengths from NPZ data.

    Returns:
        smpl_offsets: Original bone offsets (52, 3)
        method: How they were computed ("betas", "tpose_measurement", "fallback")
    """
    # Try Option 2 first: Use betas + SMPL model
    if 'betas' in npz_data and has_smpl_model():
        betas = npz_data['betas']
        j_absolute = compute_j_absolute_from_betas(betas)  # Requires SMPL model
        smpl_offsets = compute_smpl_offsets(j_absolute)
        return smpl_offsets, "betas"

    # Try Option 3: Check if NPZ has bone lengths directly
    if 'J_ABSOLUTE' in npz_data:
        j_absolute = npz_data['J_ABSOLUTE']
        smpl_offsets = compute_smpl_offsets(j_absolute)
        return smpl_offsets, "npz_direct"

    # Fallback: Use T-pose measurement
    # This requires finding a T-pose frame and measuring
    # For now, return None and use reference (with warning)
    return None, "fallback"
```

## Immediate Solution (Without SMPL Model)

Since we don't have SMPL model yet, we can:

1. **Check NPZ structure**: See if original bone lengths are stored
2. **Use fallback warning**: If no original bone lengths available, warn user but still proceed
3. **Document limitation**: Clearly state that without SMPL model or NPZ bone lengths, we can't be fully faithful

## Questions to Answer

1. **Do NPZ files contain original `J_ABSOLUTE` or bone lengths?**
    - Check a few NPZ files to see what keys they contain
2. **Is there an SMPL model available in the project?**
    - Look for `.pkl` files
    - Check if there's SMPL loading code
3. **Can we infer bone lengths from animation data?**
    - Maybe measure from multiple frames and average?
    - Or use a specific frame that's known to be T-pose?

## Next Steps

1. Inspect NPZ files to see what data is available
2. Check if SMPL model files exist
3. Implement the hybrid approach based on available data
4. Create a script that tries all methods and reports which one was used
