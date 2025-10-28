# A-Pose Specification (From Project Visuals)

## Target A-Pose Definition

Based on project visuals and requirements:

### Key Characteristics

-   Shoulders elevated ~35° from body (not perpendicular like T-pose)
-   Arms straight
-   Hands facing **INWARD** (palms facing body)
-   **Straight legs** (not bent)

**Overall:**

-   Natural, ready-for-animation stance
-   Better for retargeting than T-pose or rest pose
-   Industry standard for character rigging

### Comparison

| Pose Type               | Arm Angle         | Hands         | Legs     |
| ----------------------- | ----------------- | ------------- | -------- |
| **Rest Pose** (current) | 0° at sides       | Side facing   | Straight |
| **A-Pose** (target)     | ~35° elevated     | Facing inward | Straight |
| **T-Pose**              | 90° perpendicular | Side facing   | Straight |

### Joint Transformations Needed

**From Rest Pose → A-Pose:**

**Shoulder joints (13: L_Collar, 14: R_Collar):**

-   Rotate upward ~35° from body
-   Rotate forward slightly

**Upper arms (16: L_Shoulder, 17: R_Shoulder):**

-   Extend to form A-shape
-   Keep relatively straight

**Elbows (18: L_Elbow, 19: R_Elbow):**

-   Slight bend (~15-20° max)
-   Not fully extended

**Hands/Wrists (20: L_Wrist, 21: R_Wrist):**

-   Rotate to face inward (palms toward body)
-   Natural downward angle

**Body/Legs:**

-   Keep same as rest pose (straight, neutral)

### Why These Specifications?

-   **Hands inward:** Based on project description/images
-   **Straight arms/legs:** Standard A-pose characteristics
-   **35° angle:** Balance between natural and retargeting-friendly
-   **Not bent knees:** Keep body upright, not in crouch

### Implementation Note

Since no A-pose examples exist in AMASS data, I need to:

1. Apply rotations to shoulder/collar joints to achieve ~35° arm elevation
2. Rotate hands to face inward
3. Maintain body and leg positions (straight stance)
4. Apply this transformation to frame 0 of all animations
