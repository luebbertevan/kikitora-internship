# M1 Progress

## What I Found

**Frame 0 poses are inconsistent across different subjects/datasets.**

-   Current frame 0 is typically in REST POSE (arms at 0°, at sides)
-   NOT A-pose (would need 35° arms)
-   Different subjects have different starting poses
-   Bone lengths vary across animations (not consistent skeleton)

## What I Need

-   Reference data showing correct A-pose skeleton with consistent bone lengths
-   See `STANDUP_QUESTIONS.md` for what to ask mentor

## Files Analyzed

-   Female1Gestures: 6 files (D1-D6, Calibration)
-   s007: 1 file
-   All have identical rest pose frame 0

-   Each animation has ~4,624 frames
-   Frame rate: 120 fps
-   Data format: SMPL-H (52 joints × 3 axis-angle = 156 params)
-   Translation data: (num_frames, 3)
-   Pose data: (num_frames, 156)
