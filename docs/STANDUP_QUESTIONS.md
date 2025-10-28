# Questions for Tomorrow's Standup

## Critical Questions

### 1. Reference Data - Do you have a working example of correctly formatted data?

**What I need:** One example of properly formatted .glb with:

-   Perfect A-pose frame 0
-   Consistent skeleton (uniform bone lengths)

**Why:** This would solve both unknowns:

-   What "perfect A-pose" looks like
-   What "consistent skeleton" means

**Question:** Can I access the training pipeline's expected input format? Or any existing correctly formatted animations?

### 2. Design Approach - Should the system accept ANY target skeleton/pose?

**Proposed approach:**

-   Build a general retargeting function
-   Input: any AMASS .npz file
-   Target: any armature + pose (e.g., A-pose skeleton, T-pose skeleton, custom skeleton)
-   Output: retargeted animation

**Benefits:**

-   Solves current A-pose requirement
-   Flexible for future use cases
-   One implementation handles all scenarios

**Question:** Is this the right approach, or should I focus only on the A-pose requirement?

---

## What I Completed Today (M1)

**Analysis:**

-   ✅ Extracted and analyzed AMASS data
-   ✅ Visualized frame 0 poses (all in rest pose, arms at 0°, NOT A-pose)
-   ✅ Set up project structure with organized files
-   ✅ Created exploration and visualization tools

**Finding:**

-   Frame 0 is **rest pose** (arms at sides, 0°)
-   Need to transform to **A-pose** (assuming ~35° arms based on project visuals)
-   No A-pose examples exist in AMASS data
-   Need reference to know exact target format

**Next:** Ready to implement M2-M4 once I have target spec or reference data
