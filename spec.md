## Project Spec (Current Plan)

Overview

-   Goal: Convert AMASS `.npz` animations to GLB on a consistent SMPL‑H skeleton, frame 0 A‑pose, fixed bone lengths, correct scale/orientation, child cube included.
-   Reference: `A-Pose.FBX` defines desired bone lengths and A‑pose angles, but we remain SMPL‑H (52 joints). Extra FBX bones are ignored.
-   Clean SMPL-H Reference: `data/reference/smplh_target_reference.npz` and `data/reference/smplh_target.glb`

Guiding Principles

-   Treat FBX as a bone-length/pose reference only. Output skeleton is SMPL‑H.
-   Keep units consistent (m), armature at identity, glTF friendly.
-   Build in tiny, testable steps; each step exports viewable GLBs.

Milestones

M1 — Parity Export (DONE)

-   Implement pass‑through `.npz`→GLB export (matches original pipeline) with child cube and CLI ergonomics.
-   Acceptance: GLBs open in Blender; animation matches input FK; child cube present.
-   Tests: Compare frame positions vs FK (spot check), visual sanity.
-   Status: ✅ Complete

M2 — Clean SMPL‑H Reference (DONE)

-   Objective: Build a clean SMPL‑H armature (52 joints) whose bone lengths and rest angles approximate the FBX A‑pose. Ignore FBX extra bones.

    Tasks

    -   ✅ Inventory FBX armature and export CSV (bone_name, parent, length, children, is_end).
    -   ✅ Create explicit FBX→SMPL‑H name mapping (52 only; ignore twist/end/helper/metacarpal/end bones).
    -   ✅ Extract FBX A‑pose joint heads for mapped bones (armature at identity). Units: use as-is; only convert if numeric checks fail.
    -   ✅ Compute `J_ABSOLUTE` (52×3) and `SMPL_OFFSETS` using the SMPL‑H tree; save `data/reference/smplh_target_reference.npz`.
    -   ✅ Generate `data/reference/smplh_target.glb` armature from these values (no animation), with child cube.
    -   ⏳ Add validation: compare parent‑child distances vs FBX (≤ 2 mm) and hierarchy correctness, plus quick visual check.

    Acceptance Criteria

    -   `smplh_target.glb` has exactly 52 bones with the SMPL‑H parent tree.
    -   Parent‑child distances match FBX (≤ 0.2 cm error).
    -   Armature at identity; units in meters; visible in front; child cube present.

    Testing

    -   Automated: length diff report per bone (GLB vs FBX sample) with pass/fail summary.
    -   Manual: load `A-Pose.FBX` + `smplh_target.glb` in Blender, verify size/orientation match and joint placement.

    Notes

    -   Unit conversion: we will not change units unless numeric length checks indicate a mismatch; visual parity suggests FBX scale is already correct in the project.
    -   **ISSUE**: `smplh_target.glb` is scaled too large compared to the animations. Need to fix scaling to match the data files before proceeding to M3.
    -   Status: ⚠️ Complete but requires scale fix

M2.1 — Fix Reference Scale 

-   Objective: Fix the scaling of `smplh_target.glb` and `smplh_target_reference.npz` to match the scale used in the actual animation data.

    Tasks

    -   Analyze scaling in existing retargeted animations (e.g., `D1 - Urban 1_poses_retargeted.glb`).
    -   Determine correct scale factor to apply to `J_ABSOLUTE` in `smplh_target_reference.npz`.
    -   Regenerate `smplh_target_reference.npz` with correct scaling.
    -   Regenerate `smplh_target.glb` with correct scaling.
    -   Verify scale matches animation data visually in Blender.

    Acceptance Criteria

    -   `smplh_target.glb` and animation GLBs have matching scale when loaded together in Blender.
    -   Bone lengths are proportionally correct relative to animation data.
    -   Visual inspection confirms reference skeleton size matches animation skeletons.

    Testing

    -   Load `smplh_target.glb` + `D1 - Urban 1_poses_retargeted.glb` in Blender side-by-side.
    -   Measure sample bone lengths in both (e.g., spine, femur) and verify they match.
    -   Visual confirmation that both skeletons are same size/scale.

    Status: 🔲 Not Started (blocking M3)

M3 — Standardize Root Position & Orientation

-   Objective: Ensure all animations start with the pelvis (root bone) at the exact position and rotation defined in the reference SMPL-H (`data/reference/smplh_target_reference.npz`).

    Tasks

    -   Load reference pelvis position and rotation from `smplh_target_reference.npz`.
    -   For each input `.npz`, compute the delta between its frame 0 pelvis and the reference pelvis.
    -   Apply inverse transform to entire animation to align pelvis to reference.
    -   Export test GLBs and verify pelvis position/rotation matches reference exactly at frame 0.

    Acceptance Criteria

    -   Frame 0 pelvis position matches reference `J_ABSOLUTE[0]` (Pelvis) within 0.1mm.
    -   Frame 0 pelvis rotation matches reference orientation (identity or reference-defined rotation).
    -   All subsequent frames maintain correct relative motion.

    Testing

    -   Automated: Compare frame 0 pelvis transform vs reference for 5+ test files.
    -   Manual: Load output GLB in Blender, verify pelvis at origin/reference position at frame 0.

    Status: 🔲 Not Started

M4 — Set Frame 0 to Reference A-Pose

-   Objective: Override frame 0 of all animations to exactly match the reference SMPL-H A-pose, while preserving the animation starting from frame 1.

    Tasks

    -   Load reference `J_ABSOLUTE` from `smplh_target_reference.npz` (this is the A-pose).
    -   For frame 0 only, set all bone rotations to match the reference A-pose.
    -   Ensure frame 0 uses reference bone positions while maintaining correct root translation from input.
    -   Keep frames 1+ unchanged (will be retargeted in later milestones).
    -   Export test GLBs and verify frame 0 pose visually matches `smplh_target.glb`.

    Acceptance Criteria

    -   Frame 0 joint positions match reference A-pose (within 1mm per joint).
    -   Frame 0 looks identical to `smplh_target.glb` when loaded in Blender.
    -   Frame 1+ animations remain intact (no unintended changes yet).

    Testing

    -   Automated: Joint position comparison for frame 0 across 5+ files.
    -   Manual: Load output GLB + reference GLB side-by-side in Blender, verify frame 0 pose match.

    Status: 🔲 Not Started

M5 — Retarget Single Bone Pair (L_Hip & R_Hip)

-   Objective: Implement bone length retargeting for just the left and right hip bones, validating that the rest of the skeleton correctly adjusts to the bone length change.

    Tasks

    -   Compute target bone lengths for L_Hip and R_Hip from reference `SMPL_OFFSETS`.
    -   For each frame, calculate the input FK positions for L_Knee (child of L_Hip) and R_Knee (child of R_Hip).
    -   Adjust L_Hip and R_Hip rotations to maintain the target (knee) positions while using reference bone lengths.
    -   Verify that downstream bones (knees, ankles, feet) maintain correct positions.
    -   Export test GLBs and validate bone lengths and joint positions.

    Acceptance Criteria

    -   L_Hip and R_Hip bone lengths match reference (within 0.1mm).
    -   L_Knee and R_Knee positions match input FK positions (within 2mm per frame).
    -   Downstream bones (ankles, feet) preserve relative relationships.
    -   Visual inspection shows natural hip/leg motion without distortion.

    Testing

    -   Automated: Bone length validation for L_Hip/R_Hip across all frames.
    -   Automated: Joint position comparison for L_Knee/R_Knee vs input FK.
    -   Manual: Load output GLB in Blender, play animation, verify hips and legs look natural.

    Status: 🔲 Not Started

M6 — Retarget All Bone Lengths

-   Objective: Extend bone length retargeting to all 52 bones in the SMPL-H skeleton, ensuring consistent bone lengths across all animations while preserving motion characteristics.

    Tasks

    -   Apply the same retargeting approach from M5 to all bones.
    -   Traverse the kinematic tree (parent-to-child order).
    -   For each bone, adjust rotation to maintain child joint target positions while using reference bone length.
    -   Handle special cases: end effectors (hands, feet, head), fingers (15 per hand).
    -   Export test GLBs and validate all bone lengths and overall motion quality.

    Acceptance Criteria

    -   All 52 bones have lengths matching reference (within 0.2mm).
    -   Joint positions for all frames approximate input FK (within 5mm accumulated error per chain).
    -   Animations preserve motion characteristics (no jittering, unnatural bends, or pops).
    -   Visual inspection across 10+ diverse animations shows natural motion.

    Testing

    -   Automated: Full bone length validation report for all bones across 10+ files.
    -   Automated: Joint position error report (per-joint, per-frame) with max/mean error stats.
    -   Manual: Load multiple output GLBs in Blender, play animations, verify motion quality across different subjects/datasets (ACCAD, EKUT, etc.).

    Notes

    -   This is the most complex milestone and may require iteration.
    -   Consider breaking into sub-milestones if issues arise (e.g., spine chain, arms, hands separately).

    Status: 🔲 Not Started

M7 — Validation & Tooling

-   Objective: Create comprehensive validation tools and helper scripts to ensure quality across the entire dataset.

    Tasks

    -   Create `validate_retarget.py` script with subcommands:
        -   `--bone-lengths`: Compare bone lengths vs reference, output per-bone report.
        -   `--frame0-pose`: Verify frame 0 matches reference A-pose.
        -   `--root-alignment`: Check pelvis position/rotation at frame 0.
        -   `--fk-diff`: Compare joint positions vs input FK (per-frame error stats).
        -   `--batch-report`: Process multiple files and generate summary statistics.
    -   Create `quick_view.py`: Export a subset of frames (e.g., 0, 10, 50, 100) for rapid visual inspection.
    -   Run validation on large sample (50-100 files) across all datasets.
    -   Document common failure modes and thresholds.

    Acceptance Criteria

    -   Validation scripts run successfully on 100+ files.
    -   Reports show ≥95% files pass all validation checks.
    -   Failures are categorized (bone length, FK error, pose mismatch) with actionable info.
    -   Quick viewer exports work for spot-checking.

    Testing

    -   Run full validation suite on representative sample from each dataset (ACCAD, EKUT, TotalCapture).
    -   Manual review of flagged failures.
    -   Visual spot-checks on 20+ random files.

    Status: 🔲 Not Started

M8 — Documentation & Packaging

-   Objective: Finalize documentation, clean up code, and prepare for handoff/production use.

    Tasks

    -   Update `src/retarget_usage.md` with all CLI flags and examples.
    -   Create `VALIDATION.md` documenting validation tools, thresholds, and interpretation.
    -   Add inline code comments for complex retargeting logic.
    -   Create minimal `requirements.txt` (numpy, pathlib, etc. - Blender has most built-in).
    -   Update main `README.md` with project summary, quick start, and file structure.
    -   Clean up temporary/debug files.
    -   Final test: Process 10 files end-to-end from raw `.npz` to validated `.glb`.

    Acceptance Criteria

    -   All documentation is concise, accurate, and up-to-date.
    -   A new user can understand and run the pipeline from README alone.
    -   Code is clean with no dead/debug code.
    -   End-to-end test completes successfully.

    Status: 🔲 Not Started

Outputs

-   `reference/fbx_apose_reference.glb` (visual A‑pose reference from original FBX)
-   `data/reference/smplh_target_reference.npz` (52-joint SMPL-H reference: J_ABSOLUTE, SMPL_OFFSETS)
-   `data/reference/smplh_target.glb` (clean SMPL‑H A-pose armature, no animation)
-   `data/output/` (retargeted GLBs per input `.npz`, with `_retargeted` suffix)
-   Validation reports and helper scripts

Success Criteria

-   Hundreds of hours of AMASS data converted to consistent SMPL-H skeleton.
-   All animations start with uniform A-pose at frame 0.
-   Bone lengths match reference across all files.
-   Motion characteristics preserved (validated both numerically and visually).
-   Pipeline is documented and reproducible.
