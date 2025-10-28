# M1 Progress Tracking

## Completed Steps

### ✅ Step 1: Extract Sample Data

-   Extracted 6 animation files from ACCAD dataset
-   Location: `data/extracted/ACCAD/Female1Gestures_c3d/`
-   Files extracted:
    -   D1 - Urban 1
    -   D2 - Wait 1
    -   D3 - Conversation Gestures
    -   D5 - Random Stuff 2
    -   D6 - CartWheel
    -   Female1 Subj Calibration

### ✅ Step 2: Explore Data Structure

**Findings:**

-   Each animation has ~4,624 frames
-   Frame rate: 120 fps
-   Data format: SMPL-H (52 joints × 3 axis-angle = 156 params)
-   Translation data: (num_frames, 3)
-   Pose data: (num_frames, 156)

**Frame 0 observations:**

-   Translation varies significantly across files (X std dev: 1.31m, Y: 0.36m, Z: 0.01m)
-   Pose parameters vary across different animations
-   Each animation starts in a different pose

### ✅ Step 3: Visualize Frame 0

**Status:** ✅ COMPLETED - Visualized all 6 files

**Current observations:**

-   **Frame 0 pose:** Neutral/Rest pose with arms at sides
-   **NOT A-pose (arms at ~35° from body)**
-   **NOT T-pose (arms at 90° perpendicular to body)**
-   **Current:** Arms at 0° relative to body (at the sides)
-   **Consistency:** All Female1Gestures_c3d files start from identical neutral pose
-   **Pose characteristics:** Natural standing pose, palms facing thighs, suitable for animation starting point

**Visualized files:**

-   D1 - Urban 1
-   D2 - Wait 1
-   D3 - Conversation Gestures
-   D5 - Random Stuff 2
-   D6 - CartWheel
-   Female1 Subj Calibration

**Key finding:** Frame 0 is in **rest pose** (arms at sides), NOT A-pose or T-pose.

## Questions to Answer

-   [x] What is the current frame 0 pose?
    -   **Answer:** Rest pose (arms at 0° at the sides)
-   [x] How consistent are frame 0 poses across different animations?
    -   **Answer:** Very consistent within Female1Gestures_c3d - all identical neutral pose
-   [ ] What angle are the arms at in current poses?
    -   **Answer:** 0° (arms at sides)
-   [ ] What should the target A-pose look like?
    -   **Answer:** Arms at ~35° from body, palms forward, more natural than T-pose

## Target A-Pose Specifications

**Current Frame 0:** Rest pose (arms at 0°)
**Target Frame 0:** A-pose (arms at ~35°)

**A-Pose Definition (from project visuals):**

-   Shoulder angle from body: ~35° (NOT 0° like rest pose, NOT 90° like T-pose)
-   Arms: Fairly straight, forming A-shape
-   Elbow angle: Slight bend (~15-20° max)
-   Hand orientation: **Facing INWARD** (palms toward body)
-   Legs: **Straight** (not bent)
-   Body stance: Upright, neutral, ready for animation
-   Why A-pose? Better for retargeting pipeline - allows natural motion range

**Note:** Assuming based on project visuals. Seeking reference data to confirm.

## Next Steps for M1

-   [ ] Document: Why current rest pose won't work for their pipeline
-   [ ] Define exact joint angles for A-pose transformation
-   [ ] Create visualization showing T-pose vs A-pose vs current rest pose
-   [ ] Plan how to transform rest pose → A-pose
