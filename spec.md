# Spec: Consistent Skeleton Retargeting for AMASS Data

## Project Goal

Convert raw AMASS .npz/.npy data to consistent .glb format with:

-   **Consistent skeleton**: All animations use identical bone lengths
-   **A-Pose start**: Every animation begins at frame 0 with a perfect uniform A-pose
-   **Preserve animation**: Motion characteristics and quality are maintained
-   **Pipeline ready**: Output compatible with existing retargeting pipeline

---

## Problem Statement

**Current Issues:**

1. Existing scripts (`create_glb_from_npz.py`, `retarget.py`) use SMPL-H kinematic tree but produce varying bone lengths
2. Frame 0 doesn't always start in perfect A-pose (varies by subject/take)
3. Inconsistent skeletons across animations make retargeting difficult

**Root Cause:**

-   `J_ABSOLUTE` positions are hardcoded (from SMPL model's neutral shape)
-   AMASS data varies by subject - different bone proportions per person
-   Forward kinematics uses these fixed offsets, so bone lengths are inconsistent

**Solution Direction:**
Create a canonical A-pose skeleton with fixed bone lengths, then retarget all animations to it using joint positions (IK) rather than direct FK.

---

## Project Structure

```
kikitora-internship/
├── .cursorrules.md          # AI coding assistant rules
├── .gitignore               # Excludes large data files
├── README.md                # Project overview
├── spec.md                  # This specification
│
├── config/                  # Configuration files
│   ├── SMPL_H_Armature_transforms.json
│   └── smplh.json
│
├── data/
│   ├── models/              # SMPL models and reference data
│   │   ├── amass_joints_h36m_60.pkl
│   │   └── smplh_tpose.glb
│   ├── output/              # Processed .glb outputs (generated)
│   └── raw/                 # Compressed datasets (gitignored)
│       ├── ACCAD.tar.bz2
│       ├── EKUT.tar.bz2
│       ├── TotalCapture.tar.bz2
│       └── PosePrior.tar.bz2
│
└── src/
    ├── scripts/             # Main processing scripts
    │   ├── create_glb_from_npz.py    # Creates .glb from .npz (uses frame 0 FK = inconsistent, IGNORE)
    │   └── retarget.py               # **YOUR MAIN TARGET** - fix/enhance for consistent skeleton + A-pose
    ├── utils/               # Exploration/debug tools
    │   ├── explore_amass_data.py     # Explore .npz file structure (M1 tool)
    │   └── debugger.py               # Simple .npz structure debugger (has hardcoded paths)
    └── visualization/       # Visualization tools
        ├── visualize_frame0.py      # Visualize frame 0 pose (M1 tool)
        ├── visualize_neutral_smplh.py # Visualize T-pose skeleton (hardcoded path)
        ├── visualizer.py             # Full animation visualizer (hardcoded path)
        └── smplh_debugger.py         # Debug SMPL-H model
```

**Notes:**

-   Raw data files (`.tar.bz2`, `.pkl`, `.npz`) are gitignored due to size
-   Scripts organized by purpose for maintainability
-   Output directory for processed .glb files
-   Config directory for SMPL-H constants and transforms

---

## Milestones

### M1: Analyze Current System & A-Pose Requirements

**Goal**: Understand current pipeline and define target A-pose

**Tasks:**

1. Document current data flow in existing scripts
2. Load and visualize sample AMASS .npz files
3. Compare frame 0 poses across different subjects
4. Define exact A-pose joint angles/positions (arms at ~35° from body)
5. Identify which joints need to change from current T-pose

**Acceptance Criteria:**

-   Document explaining current pipeline limitations
-   Visual comparison showing pose variations
-   Quantified A-pose spec (joint angles or positions)
-   Test: Visualize 5 different animations frame 0

**Testing Approach:**

-   Run `visualizer.py` on multiple .npz files
-   Extract frame 0 pose angles/positions
-   Create side-by-side visualizations

---

### M2: Generate Canonical A-Pose Skeleton

**Goal**: Create reference skeleton with consistent bone lengths

**Tasks:**

1. Design canonical bone lengths (use average or standard proportions)
2. Compute A-pose joint positions from these bone lengths
3. Create forward kinematics function for canonical skeleton
4. Export reference skeleton as .glb for verification
5. Generate visualization comparing canonical vs. current skeletons

**Acceptance Criteria:**

-   New constants: `CANONICAL_BONE_LENGTHS` (52 bones)
-   New constants: `CANONICAL_A_POSE_J_ABSOLUTE` (52 joint positions)
-   Function: `canonical_forward_kinematics()`
-   Output: Reference A-pose skeleton .glb file
-   Visual: Side-by-side canonical vs. current skeleton plot

**Testing Approach:**

-   Visualize canonical skeleton in Blender
-   Verify all bones have expected lengths
-   Check skeleton proportions are humanoid
-   Compare to `smplh_tpose.glb`

---

### M3: Implement Joint-to-Pose Extraction

**Goal**: Convert target joint positions back to bone rotations

**Tasks:**

1. Implement function to extract pose params from target joint positions
2. Use inverse kinematics concepts (compute bone rotations from end-effector positions)
3. Handle parent-child relationships correctly
4. Test with known poses to validate roundtrip accuracy
5. Handle root joint translation separately

**Acceptance Criteria:**

-   Function: `joint_positions_to_pose()` or `extract_pose_from_joints()`
-   Returns pose params compatible with SMPL format (156-dim: 52 joints × 3 axis-angle)
-   Mathematically validated: FK(extracted_pose) ≈ target_joints (within tolerance)
-   Supports root translation separately

**Testing Approach:**

-   Create test: T-pose → extract → FK → verify returns T-pose
-   Create test: A-pose → extract → FK → verify returns A-pose
-   Tolerance: Joint positions within 1cm
-   Visualize extracted pose to confirm it looks correct

---

### M4: Retarget Single Animation to Canonical Skeleton

**Goal**: Convert one AMASS animation to canonical skeleton with A-pose frame 0

**Tasks:**

1. Load AMASS .npz file
2. For each frame: compute joint positions using current FK
3. Retarget: adjust joint positions to canonical bone lengths
4. Extract pose from retargeted joint positions
5. Ensure frame 0 is A-pose
6. Export result as .glb

**Acceptance Criteria:**

-   Function: `retarget_to_canonical(npz_data) -> (poses, trans)`
-   Frame 0 should match canonical A-pose within tolerance
-   All frames preserve motion characteristics visually
-   Output .glb file
-   All bones in output have consistent lengths

**Testing Approach:**

-   Visual comparison: original animation vs. retargeted in Blender
-   Check frame 0 is A-pose by inspection
-   Verify smooth motion (no jittery artifacts)
-   Measure bone lengths in output .glb (should be consistent)
-   Compare multiple frames side-by-side

---

### M5: Batch Processing Pipeline

**Goal**: Process multiple .npz files to consistent .glb format

**Tasks:**

1. Scan for .npz files in directory
2. Process each file through retargeting pipeline
3. Handle errors gracefully (skip bad files, log issues)
4. Add progress reporting
5. Export results with sensible naming convention

**Acceptance Criteria:**

-   Command-line script: `python convert_all.py <input_dir> <output_dir>`
-   Processes all .npz files in directory tree
-   Progress bar or frame counter
-   Error log file
-   Output naming: `source_name.glb` or similar
-   Can handle 100+ files

**Testing Approach:**

-   Test on small subset (5-10 files)
-   Verify all outputs have consistent skeletons
-   Check all outputs start with A-pose
-   Measure processing time
-   Test error handling with corrupted file

---

### M6: Validation & Quality Assurance

**Goal**: Ensure output quality and pipeline reliability

**Tasks:**

1. Automated checks: bone lengths, A-pose frame 0, motion smoothness
2. Statistical analysis: compare distributions before/after retargeting
3. Sample multiple outputs for manual inspection
4. Performance profiling: processing time per file
5. Create comparison visualization tool

**Acceptance Criteria:**

-   Automated validation script: `python validate_outputs.py <output_dir>`
-   Validation report: % passing checks, common issues
-   Statistical report: joint velocity distributions, pose diversity
-   Sample visualizations: 10 random animations before/after
-   Performance metrics: avg time per file

**Testing Approach:**

-   Run validation on 50+ output files
-   Check 90%+ pass automated checks
-   Manual inspection of 10 random samples
-   Verify motion diversity is preserved
-   Benchmark processing speed

---

### M7: Documentation & Deployment

**Goal**: Package solution for production use

**Tasks:**

1. Update README with usage instructions
2. Document retargeting algorithm (how it works)
3. Create example notebooks for visualization
4. Add requirements.txt with all dependencies
5. Document known limitations and edge cases

**Acceptance Criteria:**

-   Complete README with setup and usage
-   Algorithm documentation (technical explanation)
-   Example visualization notebook
-   Clean code structure with comments
-   Production-ready pipeline

**Testing Approach:**

-   New user can follow README to run pipeline
-   Documentation explains algorithm clearly
-   Example notebook runs end-to-end
-   Code passes peer review for clarity

---

## Implementation Notes

### Key Decisions Needed

1. **Canonical Bone Lengths**: Use average from AMASS data? Use fixed proportions? Need measurement strategy
2. **Retargeting Method**: IK solve? Geometric fitting? Eigenpose decomposition?
3. **A-Pose Definition**: Exact angles for shoulders/arms? Based on industry standards?
4. **Root Handling**: How to handle pelvic position and global motion?

### Technical Stack

-   NumPy for numerical computation
-   SciPy for rotations and transformations
-   Matplotlib for visualization
-   Blender (bpy) for .glb export
-   Standard Python file I/O

### Constants & Data Structures

```python
# Current (hardcoded from SMPL model)
SMPL_H_PARENTS: NDArray[np.int32]  # 52 joint parent indices
J_ABSOLUTE: NDArray[np.float64]    # 52 joint positions (varies by subject)
SMPL_OFFSETS: NDArray[np.float64]   # 52 bone offsets

# New (canonical skeleton)
CANONICAL_BONE_LENGTHS: NDArray[np.float64]  # 52 bone lengths (fixed)
CANONICAL_A_POSE_J_ABSOLUTE: NDArray[np.float64]  # 52 joint positions (fixed)
```

### Estimated Timeline

-   M1-2: 2-3 days (analysis + skeleton design)
-   M3: 2-3 days (IK implementation)
-   M4: 3-4 days (retargeting logic)
-   M5: 1-2 days (batch processing)
-   M6: 2-3 days (validation)
-   M7: 1-2 days (documentation)

**Total: ~15-20 days**

---

## Success Criteria

✅ All animations use identical skeleton bone lengths  
✅ Every animation starts with perfect A-pose at frame 0  
✅ Motion characteristics preserved (no artifacts, smooth animation)  
✅ Pipeline processes 100+ files reliably  
✅ Output compatible with existing retargeting pipeline  
✅ Processing time < 10 seconds per animation file  
✅ Documentation enables production deployment

## Testing Strategy

### Test Files to Create

**`test_retargeting.py`** - Unit tests for retargeting functions:

-   Test FK roundtrip (pose → joints → pose)
-   Test A-pose frame 0 enforcement
-   Test bone length consistency

**`test_visualization.py`** - Visual comparison tests:

-   Compare original vs. retargeted animations
-   Verify frame 0 is A-pose
-   Check for motion artifacts

**`test_integration.py`** - End-to-end tests:

-   Process sample .npz → .glb
-   Verify output quality
-   Check error handling

### Visual Tests

-   Side-by-side comparisons (original vs. retargeted)
-   Frame 0 pose verification
-   Motion smoothness checks

---

## Next Steps

1. Start with M1: Analyze current system
2. At each milestone, refine the spec if needed
3. Create visual test outputs for validation
4. Iterate on retargeting algorithm quality
