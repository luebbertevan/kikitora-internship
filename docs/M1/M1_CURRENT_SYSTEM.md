# M1: Current System Analysis

## Current Frame 0 State

**Observation:** Frame 0 is in **Rest Pose** (arms at sides)

-   Arms at 0° relative to body (at the sides)
-   Not T-pose (90° arms outstretched)
-   Not A-pose (35° arms - what's needed)

## Why This Matters

The retargeting pipeline expects:

-   Frame 0 to be in **perfect A-pose**
-   Consistent skeleton bone lengths
-   A-pose allows better motion range for retargeting

Current state **doesn't meet these requirements**:

-   Frame 0 is rest pose, not A-pose
-   Bone lengths vary (we'll fix this in M2-M3)

## What Needs to Happen

1. **Transform frame 0:** Rest pose (0°) → A-pose (35°)
2. **Create canonical skeleton** with consistent bone lengths
3. **Retarget entire animation** to canonical skeleton while preserving motion

## A-Pose Definition

**Target A-Pose:**

-   Shoulders elevated to ~35° from body
-   Arms slightly bent at elbows (~15-20° from straight)
-   Palms facing forward/body
-   Natural, ready-for-animation stance
-   Better than T-pose for retargeting (more natural range)

**NOT:**

-   Rest pose (0° - too constrained)
-   T-pose (90° - unnatural starting pose)

## Transformation Required

**From:** Current rest pose (frame 0)
**To:** Perfect A-pose (frame 0)

**Affected joints:** Shoulders (13, 14), Upper arms, elbows

This transformation will happen during retargeting in M3-M4.
