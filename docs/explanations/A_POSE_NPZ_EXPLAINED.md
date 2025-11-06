# A-Pose Reference NPZ File Explained

## File Location

`data/reference/smplh_target_reference.npz`

## What This File Contains

This NPZ file defines the **reference A-pose skeleton** that all retargeted animations should match at frame 0.

### Data Structure

The file contains 3 arrays:

1. **`J_ABSOLUTE`** - Shape: `(52, 3)`

    - 52 joint positions in A-pose (in meters)
    - Each row is one joint: `[X, Y, Z]` coordinates
    - Coordinate system: Z-up (Blender/glTF standard)

2. **`SMPL_OFFSETS`** - Shape: `(52, 3)`

    - Relative offsets for forward kinematics computation
    - For root joint (Pelvis): offset = absolute position
    - For other joints: offset = position relative to parent joint
    - Used by `forward_kinematics()` function

3. **`JOINT_NAMES`** - Shape: `(52,)`
    - Array of joint names matching the indices

## Key Joint Positions

### Root Joint (Pelvis - Index 0)

```
Position: [0.000000, 0.000000, 0.989836] m
Z-height: ~99 cm (ground level if this is at origin)
```

### Major Body Joints

-   **L_Hip** (index 1): `[0.100649, 0.006839, 0.967312]` m
-   **R_Hip** (index 2): `[-0.100649, 0.006839, 0.967311]` m
-   **Spine1** (index 3): `[0.000001, -0.009904, 1.071714]` m
-   **Neck** (index 12): `[0.000002, 0.038720, 1.565123]` m
-   **Head** (index 15): `[0.000004, 0.025178, 1.653713]` m
-   **L_Shoulder** (index 16): `[0.186155, 0.069121, 1.477104]` m
-   **R_Shoulder** (index 17): `[-0.186180, 0.069128, 1.477289]` m

### Key Measurements

-   **Hip width**: ~20.1 cm (distance between L_Hip and R_Hip)
-   **Height range**: ~96.7 cm (lowest joint) to ~165.4 cm (highest joint)
-   **Pelvis height**: ~99.0 cm from origin

## How It's Used

### In `retarget.py`:

```python
reference_pelvis = load_reference_pelvis()  # Loads J_ABSOLUTE[0]
# Aligns animation so frame 0 pelvis matches this position
joint_positions = align_root_to_reference(joint_positions, reference_pelvis)
```

### In `validate_frame0_apose_validated.py`:

```python
reference_positions = load_reference_positions()  # Loads J_ABSOLUTE
# Compares GLB frame 0 joint positions to these reference positions
errors = np.linalg.norm(glb_positions - reference_positions, axis=1)
```

### In `convert_reference_to_glb_validated.py`:

```python
ref_data = np.load('smplh_target_reference.npz')
J_ABSOLUTE = ref_data['J_ABSOLUTE']
# Creates armature bones directly from these positions
bone.head = Vector(J_ABSOLUTE[i])
```

## Understanding SMPL_OFFSETS

### For Root Joint (Pelvis):

-   `SMPL_OFFSETS[0] == J_ABSOLUTE[0]`
-   The offset IS the absolute position (no parent)

### For Child Joints:

-   `SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent]`
-   Example: L_Hip offset = L_Hip position - Pelvis position
-   These offsets are used in forward kinematics to compute joint positions from pose parameters

### Why Both J_ABSOLUTE and SMPL_OFFSETS?

-   **J_ABSOLUTE**: Used for:

    -   Reference alignment (where should pelvis be?)
    -   Validation (does frame 0 match this?)
    -   Creating reference GLBs

-   **SMPL_OFFSETS**: Used for:
    -   Forward kinematics computation (pose parameters → joint positions)
    -   Building the kinematic chain during FK

## Coordinate System

-   **Units**: Meters (not centimeters)
-   **Axes**:
    -   X: Right (positive) / Left (negative)
    -   Y: Forward (positive) / Backward (negative)
    -   Z: Up (positive) / Down (negative)
-   **Origin**: Typically at ground level, pelvis at Z ≈ 0.99 m

## Visual Representation

```
                    Head (1.65m)
                      |
                    Neck (1.57m)
                      |
              L_Shoulder  R_Shoulder
                      \   /
                    Spine3
                      |
                    Spine2
                      |
                    Spine1 (1.07m)
                      |
                    Pelvis (0.99m) ← Root
                    /   |   \
                L_Hip  R_Hip
                 |      |
              L_Knee  R_Knee
                 |      |
            L_Ankle  R_Ankle
                 |      |
             L_Foot  R_Foot
```

## Key Takeaways

1. **This is the target A-pose** - All animations should have frame 0 matching this
2. **Pelvis is at origin** - X=0, Y=0, Z≈0.99m (ground level)
3. **Units are meters** - All coordinates in meters, not centimeters
4. **52 joints total** - SMPL-H skeleton has 52 joints (22 body + 30 hand)
5. **Used for alignment** - `retarget.py` shifts entire animation so frame 0 pelvis matches this
6. **Used for validation** - Validation scripts check if frame 0 joints match these positions

## Related Files

-   `data/reference/smplh_target.glb` - Visual reference GLB (same skeleton, no animation)
-   `data/reference/reference_apose_10frames.glb` - Multi-frame GLB for testing validation
-   Created by: `src/utils/reference/extract_smplh_from_fbx.py` (M2 milestone)
