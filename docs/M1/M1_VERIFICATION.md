# M1 Verification: Frame 0 Pose Analysis

## Verification Results

### Tested Files

1. **Female1Gestures_c3d (6 files)**

    - D1 - Urban 1
    - D2 - Wait 1
    - D3 - Conversation Gestures
    - D5 - Random Stuff 2
    - D6 - CartWheel
    - Female1 Subj Calibration

    **Result:** All have identical rest pose frame 0 (arms at 0°, at sides)

2. **s007 subject**

    - QkWalk1_poses.npz

    **Result:** Same rest pose pattern (different subject, same pose type)

### Finding Confirmed

✅ **Frame 0 is consistently in REST POSE across different subjects**

-   Arms at sides (0°)
-   NOT A-pose (would be 35°)
-   NOT T-pose (would be 90°)

## No A-Pose Examples Found

**Important:** There are NO examples of A-pose in the current AMASS data.

**Why this matters:**

-   The project requires you to CREATE the A-pose transformation
-   You cannot copy an existing A-pose from the data
-   You must transform rest pose → A-pose yourself

## What Exists in the Codebase

### T-Pose Reference

-   `visualize_neutral_smplh.py` - Visualizes SMPL-H T-pose
-   `src/scripts/retarget.py` - Creates T-pose armatures (but you need A-pose!)

### Current State

-   Frame 0 = Rest pose (0° arms)
-   Existing code = T-pose (90° arms)
-   Target = A-pose (35° arms) ← THIS NEEDS TO BE CREATED

## Implication

**Your task:** You need to mathematically/computationally create A-pose from rest pose.

**This is the core of M2-M3:**

1. Define exact A-pose angles (35° shoulders)
2. Transform frame 0: rest pose → A-pose
3. Preserve motion in all subsequent frames
4. Ensure consistent skeleton bone lengths

## Verification Complete

**Conclusion:** Your finding is CORRECT. Frame 0 is rest pose, not A-pose, and no A-pose examples exist in the data. You must create the A-pose transformation from scratch.
