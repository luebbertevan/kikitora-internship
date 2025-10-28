# M1 Quick Start

## What You Need to Do

**Goal:** Understand current system and define A-pose requirements

---

## 🚀 Quick Commands

### 1. Extract sample data

```bash
cd data/extracted
tar -xjf ../raw/ACCAD.tar.bz2 ACCAD/Female1Gestures_c3d/
cd ../..
```

### 2. Explore data structure

```bash
python3 src/utils/explore_amass_data.py data/extracted/ACCAD/
```

### 3. Visualize frame 0 poses

```bash
# Find an .npz file first
find data/extracted -name "*.npz" | head -1

# Then visualize it (use quotes for files with spaces)
python3 src/visualization/visualize_frame0.py "data/extracted/ACCAD/Female1Gestures_c3d/D1 - Urban 1_poses.npz"
```

---

## 📝 What to Document

### Part 1: Current Data Structure

-   [ ] What's in a .npz file? (keys, shapes, types)
-   [ ] How many frames per animation?
-   [ ] What does the pose data look like?

### Part 2: Current Frame 0 Poses

-   [ ] Load 5 different .npz files
-   [ ] Visualize their frame 0 poses
-   [ ] Are they consistent? Different?
-   [ ] Are they T-pose, A-pose, or something else?

### Part 3: Define Target A-Pose

-   [ ] What angle should shoulders be at? (~35° from body)
-   [ ] How should arms be oriented?
-   [ ] What about hands/elbows?

### Part 4: Current Pipeline

-   [ ] Read `src/scripts/create_glb_from_npz.py`
-   [ ] Understand how forward kinematics works
-   [ ] Document why bone lengths vary

---

## 🎯 M1 Success Criteria

You'll know M1 is complete when you can answer:

1. ✅ How does the current system work?
2. ✅ What does frame 0 currently look like?
3. ✅ What should the perfect A-pose look like?
4. ✅ Which joints need to change for A-pose?

---

## Getting Help

-   Read `M1_GUIDE.md` for detailed instructions
-   Use the exploration tool: `python src/utils/explore_amass_data.py`
-   Visualize with: `python src/visualization/visualize_frame0.py`
-   Ask questions when stuck!
