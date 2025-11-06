# Understanding Checklist - Retargeting Pipeline

This checklist helps you systematically understand the core retargeting codebase. Work through each section to build your understanding.

## 🎯 Core Files to Understand (Priority Order)

### 1. `src/originals/create_glb_from_npz.py` ⭐ FOUNDATION

**Status:** Original working script - this is your reference implementation

**Key Concepts to Verify:**

-   [ ] **Forward Kinematics (FK) function** - How pose parameters → joint positions
-   [ ] **Axis-angle to rotation matrix conversion** - Rodrigues' formula implementation
-   [x] **SMPL-H kinematic tree structure** - Parent-child relationships (52 joints)
-   [ ] **Joint positions computation** - How `J_ABSOLUTE` and `SMPL_OFFSETS` are used
-   [ ] **Armature creation from frame 0** - Why frame 0 pose determines bone structure
-   [ ] **Empty-based animation system** - Why empties track joints, then constraints
-   [ ] **Constraint system** - COPY_LOCATION, STRETCH_TO, DAMPED_TRACK usage
-   [ ] **Baking process** - How constraints → keyframes on armature bones
-   [ ] **Frame 0 handling** - Why frame 0 is computed separately for armature creation

**Critical Understanding:**

-   Why using frame 0 FK positions for armature bones (not T-pose)
-   The empty → constraint → bake workflow (why not direct bone positioning)
-   How global transforms chain through parent hierarchy

---

### 2. `src/retarget.py` ⭐ CURRENT IMPLEMENTATION

**Status:** Modified version of create_glb_from_npz.py with retargeting features

**Key Differences to Understand (vs create_glb_from_npz.py):**

-   [ ] **Root alignment (M3 feature)** - `align_root_to_reference()` function
-   [ ] **Reference pelvis loading** - `load_reference_pelvis()` from NPZ
-   [ ] **Translation offset application** - How entire animation is shifted
-   [ ] **When alignment happens** - Frame 0 armature creation AND all animation frames
-   [ ] **Output filename** - `_retargeted` suffix added
-   [ ] **Cube always added** - Default behavior (no flag needed)

**Critical Understanding:**

-   Why alignment happens twice (frame 0 armature + all frames in animation loop)
-   How translation offset preserves relative motion
-   The relationship between reference pelvis and frame 0 pelvis

**Questions to Answer:**

-   What happens if reference pelvis can't be loaded?
-   How does this affect the final GLB output?
-   Are there any edge cases where alignment fails?

---

### 3. `src/utils/reference/convert_reference_to_glb_validated.py` 📋 REFERENCE GENERATION

**Status:** Validated script for creating reference GLBs

**Key Concepts to Verify:**

-   [ ] **NPZ loading** - Reading `smplh_target_reference.npz`
-   [ ] **Armature creation from NPZ data** - Using `J_ABSOLUTE` directly (no FK)
-   [ ] **Bone structure** - How bones are created from joint positions
-   [ ] **Multiple frames of same pose** - Why/how it creates N frames
-   [ ] **Identity rotations** - What "A-pose" means (all rotations = identity)
-   [ ] **Rest pose vs pose mode** - The difference between edit bones and pose bones

**Critical Understanding:**

-   This creates a **static reference GLB** (all frames identical A-pose)
-   No FK computation needed - uses pre-computed joint positions
-   Used for validation/testing, not animation retargeting
-   Why cube is added (pipeline requirement)

**Questions to Answer:**

-   When would you use this script vs the main retarget.py?
-   What is the relationship between the NPZ reference and the GLB reference?

---

### 4. `src/utils/validation/validate_frame0_apose_validated.py` ✅ VALIDATION TOOL

**Status:** Validated script for checking frame 0 correctness

**Key Concepts to Verify:**

-   [ ] **GLB import and parsing** - How to extract joint positions from GLB
-   [ ] **Frame 0 extraction** - Getting joint positions at frame 0
-   [ ] **Rest pose vs pose mode detection** - When to use edit bones vs pose bones
-   [ ] **Reference comparison** - Comparing GLB joints to reference NPZ
-   [ ] **Error calculation** - Distance metrics (max, mean, median)
-   [ ] **Threshold checking** - What "pass" vs "fail" means (1mm default)
-   [ ] **Batch validation** - Processing multiple files

**Critical Understanding:**

-   Validation happens **after** retargeting - checks if it worked
-   Uses same reference NPZ that retarget.py uses for alignment
-   Frame 0 must match reference A-pose for M4 success
-   Error reporting helps identify which joints are wrong

**Questions to Answer:**

-   What does it mean if validation passes? Fails?
-   How do errors help diagnose retargeting issues?
-   What's the difference between this and validate_root_alignment.py?

---

## 🔗 Critical Dependencies & Reference Files

### Data Files (Must Understand Format):

-   [ ] **`data/reference/smplh_target_reference.npz`**

    -   What keys does it contain? (`J_ABSOLUTE`, `SMPL_OFFSETS`, `JOINT_NAMES`)
    -   What coordinate system? (meters, Z-up)
    -   What is `J_ABSOLUTE`? (52×3 joint positions in A-pose)
    -   What is `SMPL_OFFSETS`? (relative offsets for FK)

-   [ ] **Input NPZ files (AMASS data)**
    -   What keys? (`poses`, `trans`, `mocap_framerate`)
    -   What is `poses` shape? (num_frames × 156 for SMPL-H)
    -   What is `trans`? (num_frames × 3 root translations)
    -   How are poses encoded? (axis-angle format, 3 values per joint)

### Configuration Files:

-   [ ] **`config/mapping_fbx_to_smplh.json`**

    -   Maps FBX bone names → SMPL-H joint names
    -   Used during reference extraction (M2)

-   [ ] **`config/SMPL_H_Armature_transforms.json`**
    -   Contains transform data for SMPL-H armature
    -   Used by original scripts (check if still needed)

---

## 📚 Core Concepts Across All Files

### SMPL-H Skeleton Structure:

-   [x] **52 joints total** - What are they? (Pelvis, limbs, hands, head)
-   [x] **Kinematic tree** - Parent-child relationships (`SMPL_H_PARENTS`)
-   [x] **Joint names** - Standard naming convention
-   [x] **Root joint** - Pelvis (index 0, parent = -1)

### Coordinate Systems:

-   [x] **Units** - Meters everywhere (not centimeters)
-   [x] **Axes** - Blender/glTF uses Z-up (Y forward, X right)
-   [x] **Local vs world space** - Bone transforms are local to parent
-   [ ] **Armature space** - All bones relative to armature object origin

### Forward Kinematics:

-   [ ] **Input** - Pose parameters (axis-angle) + root translation
-   [x] **Process** - Build local transforms, chain through parents
-   [x] **Output** - World-space joint positions (52×3)
-   [ ] **Why needed** - Converts animation parameters → 3D positions

### Animation Pipeline:

-   [ ] **NPZ → FK → Empties → Constraints → Bake → GLB**
    -   Understand each step and why it's necessary
-   [ ] **Why empties?** - Indirect control of bones via constraints
-   [ ] **Why bake?** - Convert constraint-driven animation to keyframes
-   [ ] **Frame 0 special handling** - Used for armature creation

### Retargeting Concepts:

-   [ ] **Reference alignment** - Moving entire animation to match reference pelvis
-   [ ] **Preserving motion** - Translation offset applied uniformly
-   [ ] **A-pose target** - Frame 0 should match reference A-pose
-   [ ] **Bone length consistency** - Why armature is created from frame 0

---

## 🎓 Other Critical Files (Secondary Priority)

### Validation Scripts:

-   [ ] **`src/utils/validation/validate_root_alignment.py`**

    -   Checks if root (pelvis) position matches reference
    -   Simpler than frame0_apose validation (just one joint)
    -   Used for M3 milestone

-   [ ] **`src/utils/validation/validate_single_frame.py`**
    -   Validates any frame (not just frame 0)
    -   Useful for debugging specific frames
    -   Similar to frame0_apose but more flexible

### Reference Generation Scripts:

-   [ ] **`src/utils/reference/extract_smplh_from_fbx.py`** (Archive - M2)
    -   Extracted reference from FBX originally
    -   Created the smplh_target_reference.npz
    -   Understand for historical context

### Original Scripts (For Comparison):

-   [ ] **`src/originals/original_retarget.py`**
    -   Original retargeting attempt
    -   Compare with current retarget.py to see evolution

---

## ✅ Verification Questions (After Understanding)

Once you understand the files above, verify you can answer:

1. **What is the difference between `J_ABSOLUTE` and `SMPL_OFFSETS`?**
2. **Why is frame 0 used for armature creation instead of T-pose?**
3. **How does root alignment work? Does it affect all frames or just frame 0?**
4. **What is the purpose of empties in the animation pipeline?**
5. **When would you use `convert_reference_to_glb.py` vs `retarget.py`?**
6. **What does validation "pass" mean? What error threshold is used?**
7. **How does forward kinematics chain transforms through parents?**
8. **What coordinate system and units are used throughout?**
9. **Why does `retarget.py` apply translation offset twice?**
10. **What's the relationship between NPZ pose parameters and final bone rotations?**

---

## 📝 Notes Section

Use this space to write down:

-   Questions that come up while reading
-   Code sections you find confusing
-   Concepts that need deeper explanation
-   Differences you notice between files


## My Notes
- Need example of the local transform. Maybe down two bones from the pelvis. so like the hip and knee. need two frames. what does this change from frame to frame.

- I need deeper understanding of the forward kinimatics 
- what is meant by pose paremeters. and axis angle and root translation
- I understand that it chains through the parent but what is actually changing? is it just the positions represented as offsets from teh parent? or is there more like the rotatio (orientation)
- how are animation parameters different from pose paremeters or any other things
- what does this mean empties give Indirect control of bones via constraints

-NPZ → FK → Empties → Constraints → Bake → GLB
I though it was NPZ → Empties → FK  → Constraints
Is fk just a way to calculate constraints?
is bake just the term to make the glb?
what is actually stored in the glb and how is it different from teh npz

I need a way to visualize how my data is stored in a glb. how am I getting there?

I need short definitions and differences beween these things
- Pose parameters
- axis-angle
- root translation
- local transforms
- animation parameters
- constraints 
- offsets 
- empties



- deeper concerns about the approach: if a person with different enough preportions (like a very tall or short person) is transfered to the standered skeleton. how does this effect the animation? if they do a cartwheel will their hands still be one the ground? does our appraoch scale the animation like this? how can I explain this? 
---

## 🎯 Next Steps

After completing this checklist:

1. Identify which files/concepts are most confusing
2. Break down specific code sections for detailed explanation
3. Trace through execution flow with a real example
4. Compare implementations to spot differences
5. Test understanding by predicting output of code changes



## My Notes
- Need example of the local transform 