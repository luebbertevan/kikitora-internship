# M1 Guide: Analyze Current System & Define A-Pose Requirements

This guide will walk you through M1 step-by-step.

## 🎯 Goal of M1

Understand the current AMASS data structure and define what A-pose should look like.

---

## Step 1: Extract Sample AMASS Data

First, let's extract one dataset to explore:

```bash
# From project root
cd data/extracted

# Extract a specific subject (macOS compatible)
tar -xjf ../raw/ACCAD.tar.bz2 ACCAD/Female1Gestures_c3d/
```

Or extract everything and then find npz files:

```bash
# Extract all of ACCAD
tar -xjf ../raw/ACCAD.tar.bz2

# Then find all npz files
find ACCAD -name "*.npz" | head -10
```

**What this does:** Extracts .npz files from compressed archives so you can load them in Python.

---

## Step 2: Explore Data Structure

Use the exploration tool to understand the data:

```bash
# From project root
python3 src/utils/explore_amass_data.py data/extracted/ACCAD/Female1Gestures_c3d/
```

**What to look for:**

-   Shape of `poses` array (should be `[num_frames, 156]` for SMPL-H)
-   Shape of `trans` array (should be `[num_frames, 3]`)
-   How many frames in each animation
-   What frame 0 looks like (this will become your A-pose)

**Questions to answer:**

1. How many frames are in a typical animation?
2. What does frame 0 pose look like?
3. Does frame 0 vary across subjects?

---

## Step 3: Visualize Current Poses

The `visualizer.py` script shows animations, but has a hardcoded path. Let's modify it:

### Step 3a: Create a flexible visualizer

I'll help you create `src/visualization/visualize_frame0.py` that:

-   Takes any .npz file as input
-   Shows frame 0 pose in 3D
-   Allows side-by-side comparison

### Step 3b: Run visualization

```bash
python3 src/visualization/visualize_frame0.py "data/extracted/ACCAD/Female1Gestures_c3d/D1 - Urban 1_poses.npz"
```

Or for other files:

```bash
python3 src/visualization/visualize_frame0.py "data/extracted/ACCAD/Female1Gestures_c3d/D2 - Wait 1_poses.npz"
python3 src/visualization/visualize_frame0.py "data/extracted/ACCAD/Female1Gestures_c3d/D3 - Conversation Gestures_poses.npz"
```

**What to observe:**

-   Current frame 0 poses (are they T-pose? A-pose? Something else?)
-   Joint positions
-   Bone orientations

---

## Step 4: Compare Frame 0 Across Subjects

Create comparison visualizations of 5 different animations' frame 0:

```bash
python3 src/utils/explore_amass_data.py data/extracted/
```

Then manually inspect:

-   Do all frame 0 poses look similar?
-   What's the variation in joint positions?
-   Are arms in the same orientation?

---

## Step 5: Define Target A-Pose

**Current state:** Frame 0 might be T-pose, or varying poses

**Target state:** Frame 0 should be perfect A-pose with:

-   Arms at ~35° angle from body (not 90° like T-pose, not 0° like rest)
-   Palms facing forward
-   Body in neutral stance

**What you need to document:**

1. Current frame 0: What does it actually look like?
2. Target A-pose:
    - Shoulder angle (relative to body)
    - Elbow angle
    - Hand orientation
3. Which joints need adjustment from T-pose?

---

## Step 6: Document Current Pipeline

Read and understand existing scripts:

-   `src/scripts/create_glb_from_npz.py`
-   `src/scripts/retarget.py`

**Document:**

1. How do they work? (input → processing → output)
2. What's the current FK (forward kinematics) approach?
3. Why do bone lengths vary? (what's causing the problem?)

---

## M1 Deliverables Checklist

-   [ ] Extract and explore at least 5 AMASS .npz files
-   [ ] Document data structure (shapes, formats)
-   [ ] Create visualizations showing frame 0 poses
-   [ ] Compare frame 0 across different subjects
-   [ ] Define target A-pose specifications
-   [ ] Document how current scripts work
-   [ ] Identify which joints need to change for A-pose

---

## Next Steps After M1

Once you understand the data and define A-pose, you're ready for M2:

-   M2 will create a canonical skeleton with fixed bone lengths
-   Then M3 will implement the retargeting algorithm

---

## Getting Started Now

1. **Extract some data:**

    ```bash
    cd data/extracted
    tar -xjf ../raw/ACCAD.tar.bz2 ACCAD/Female1Gestures_c3d/
    ```

2. **Explore it:**

    ```bash
    python3 src/utils/explore_amass_data.py data/extracted/
    ```

3. **Ask questions** - Understanding the system is the foundation!
