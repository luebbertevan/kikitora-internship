# Understanding `retarget.py`

## Overview

This script retargets SMPL+H animations to a **consistent T-pose skeleton**. It uses Inverse Kinematics (IK) approach: computes joint positions from pose parameters, then computes bone rotations to match those positions.

---

## Section-by-Section Breakdown

### 1. Constants & Data Structures (Lines 16-70)

**`SMPL_H_PARENTS`** (Lines 17-24)

-   Parent indices for each of 52 joints
-   `-1` means root joint (Pelvis)
-   Defines the kinematic tree hierarchy

**`JOINT_NAMES`** (Lines 27-32)

-   52 joint names matching the parent array
-   First 22 are body joints, last 30 are hand joints (15 per hand)

**`J_ABSOLUTE`** (Lines 35-62)

-   **CRITICAL**: Hardcoded joint positions in T-pose (zero rotation state)
-   These are the "canonical" joint positions used to compute bone lengths
-   **QUESTION**: Should these come from `config/smplh.json` or `smplh_tpose.glb` instead?

**`SMPL_OFFSETS`** (Lines 64-70)

-   Computes **relative** bone offsets from parent to child
-   Formula: `offset = child_absolute_pos - parent_absolute_pos`
-   Used in forward kinematics to position child joints relative to parents

---

### 2. Utility Functions (Lines 73-111)

**`axis_angle_to_rotation_matrix()`** (Lines 73-86)

-   Converts axis-angle representation (3D vector) to rotation matrix
-   Uses Rodrigues' rotation formula
-   Standard conversion for SMPL pose parameters

**`forward_kinematics()`** (Lines 89-111)

-   **Purpose**: Converts pose parameters → joint positions in 3D space
-   **Input**:
    -   `poses`: (156,) array = 52 joints × 3 axis-angle params
    -   `trans`: (3,) root translation
-   **Process**:
    1. Reshapes poses to (52, 3)
    2. For each joint, converts axis-angle → rotation matrix
    3. Applies rotation + offset relative to parent
    4. Computes global transform by multiplying parent transforms
    5. Extracts final 3D joint positions
-   **Output**: (52, 3) array of joint positions

**KEY INSIGHT**: This function uses `SMPL_OFFSETS` which comes from hardcoded `J_ABSOLUTE`. If bone lengths are inconsistent, this propagates the problem.

---

### 3. Armature Creation (Lines 114-157)

**`create_tpose_armature()`** (Lines 114-157)

-   **Purpose**: Creates a Blender armature in T-pose with consistent bone structure
-   **Process**:
    1. Computes T-pose joint positions using FK with **zero rotations** (line 124)
    2. Creates Blender armature object
    3. For each of 52 joints:
        - Creates a bone with head = joint position
        - Sets tail = child joint position (or offset if no children)
    4. Sets up parent-child bone relationships
-   **Result**: Consistent T-pose armature in Blender

**QUESTION**: This creates T-pose, but we need A-pose at frame 0. Should this create A-pose armature instead?

---

### 4. Inverse Kinematics (Lines 160-181)

**`compute_bone_rotation()`** (Lines 160-181)

-   **Purpose**: Given a bone's rest pose and a target position, compute rotation needed
-   **Input**:
    -   `bone_head`: Rest pose head position
    -   `bone_tail`: Rest pose tail position
    -   `target_pos`: Where the child joint should be in animated frame
-   **Process**:
    1. Computes rest direction vector (bone.tail - bone.head)
    2. Computes target direction vector (target_pos - bone.head)
    3. Finds rotation quaternion that rotates rest_dir → target_dir
-   **Output**: Quaternion rotation

**This is the IK core**: It computes bone rotations from joint positions, maintaining bone lengths.

---

### 5. Animation Retargeting (Lines 184-255)

**`retarget_animation()`** (Lines 184-255)

-   **Purpose**: Applies animation to T-pose armature using IK
-   **Process**:
    1. Computes T-pose reference joint positions (line 202)
    2. Stores bone rest pose info (head/tail positions) (lines 205-216)
    3. For each frame:
        - Computes joint positions from pose params using FK (line 231)
        - For each bone:
            - Applies root translation to Pelvis (line 239)
            - Computes IK rotation to point bone toward target joint (line 248)
            - Sets rotation and keyframes it
    4. Keyframes all rotations and translations

**KEY POINT**: This uses FK to get joint positions, then IK to compute rotations. This maintains bone lengths because:

-   Armature has consistent bone lengths (T-pose)
-   IK rotations preserve those lengths
-   Only rotations change, not bone lengths

**LIMITATION**: Frame 0 will be T-pose (from `zero_poses`), not A-pose. We need to fix this.

---

### 6. File Processing (Lines 258-298)

**`process_npz_file()`** (Lines 258-298)

-   Loads .npz file
-   Creates T-pose armature
-   Retargets animation
-   Exports to .glb

**Missing**: No child cube mesh (project description says `create_glb_from_npz.py` has this solved)

---

## Key Issues Identified

1. **Bone lengths come from hardcoded `J_ABSOLUTE`** - Should use consistent reference skeleton
2. **Creates T-pose armature** - Need A-pose instead
3. **Frame 0 is T-pose** - Need to set frame 0 to A-pose after creating armature
4. **No child cube mesh** - Required by pipeline
5. **Uses hardcoded constants** - Could use `config/smplh.json` instead

---

## Questions for Standup

1. Should I replace hardcoded `J_ABSOLUTE` with data from `config/smplh.json`?
2. Should `create_tpose_armature()` become `create_apose_armature()`?
3. How do I set frame 0 to A-pose after creating armature?
4. Do I need to add child cube mesh creation (like in `create_glb_from_npz.py`)?
5. Is the IK approach (`compute_bone_rotation`) correct for maintaining consistent bone lengths?
