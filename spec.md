# New Approach Specification: T-Pose Bone Lengths with A-Pose Starting Frame

## Overview

**Strategy**: Keep the hardcoded T-pose bone lengths (which look good) and manually create an A-pose in Blender by rotating the T-pose skeleton. Export the A-pose `J_ABSOLUTE` from Blender and use it to set frame 0 of all animations. This gives us:

-   Known-good T-pose bone lengths (hardcoded, already working)
-   A-pose starting frame (manually created in Blender, visually verified)
-   Same bone lengths for both poses (only rotations differ)

**Key Principle**: We keep the T-pose bone lengths we trust, manually create the A-pose visually in Blender, then use that A-pose `J_ABSOLUTE` to align frame 0 of animations. Since bone lengths don't change, `SMPL_OFFSETS` stay the same - only `J_ABSOLUTE` changes.

---

## Milestone M1: Diagnose Current State and Clean Up

**Objective**: Understand what's in `retarget.py` vs `create_glb_from_npz_fixed.py`, decide what to keep, and remove stale code.

### M1.1: Compare Scripts

**Task**: Side-by-side comparison of `retarget.py` and `create_glb_from_npz_fixed.py`

**Sub-tasks**:

1. List all functions in `retarget.py` that are not in `create_glb_from_npz_fixed.py`
2. List all functions in `create_glb_from_npz_fixed.py` that are not in `retarget.py`
3. Identify differences in shared functions (line-by-line comparison)
4. Document what each difference does

**Deliverable**: Markdown document `docs/M1_SCRIPT_COMPARISON.md` with:

-   Function comparison table
-   List of unique features in each script
-   Explanation of what each unique feature does

### M1.2: Identify Stale Code

**Task**: Determine which features in `retarget.py` are no longer needed

**Sub-tasks**:

1. Review `retarget.py` features:
    - Root alignment to reference pelvis (M3 feature)
    - JSON pose override for frame 0
    - `--export-target-apose` flag
    - Hardcoded T-pose `J_ABSOLUTE`
2. For each feature, decide:
    - **Keep**: Still needed for new approach
    - **Remove**: Stale/obsolete
    - **Modify**: Needs changes for new approach
3. Document decisions with rationale

**Deliverable**: Markdown document `docs/M1_STALE_CODE_ANALYSIS.md` with:

-   Feature list with keep/remove/modify decisions
-   Rationale for each decision

### M1.3: Clean Up `retarget.py`

**Task**: Remove or comment out stale code based on M1.2 decisions

**Sub-tasks**:

1. Remove functions marked as "Remove"
2. Comment out code marked as "Modify" (with TODO comments)
3. Add comments explaining what was removed and why
4. Ensure script still runs (even if incomplete)

**Deliverable**: Updated `retarget.py` with stale code removed, comments added

**Acceptance Criteria**:

-   Script runs without errors (may be incomplete)
-   All removed code is documented
-   Clear TODO comments for code to be modified

---

## Milestone M2: Create A-Pose in Blender and Export J_ABSOLUTE

**Objective**: Manually create an A-pose in Blender by rotating the T-pose skeleton, then export the A-pose `J_ABSOLUTE` for use in frame 0 alignment.

### M2.1: Create Script to Export J_ABSOLUTE from Blender Armature

**Task**: Create a script that reads joint positions from a Blender armature and exports them as `J_ABSOLUTE`

**Sub-tasks**:

1. Create script `src/utils/reference/export_apose_from_blender.py`:
    - Load or create armature in Blender (using T-pose `J_ABSOLUTE`)
    - Read bone head positions for all 52 joints
    - Export as `J_ABSOLUTE` array (52, 3)
    - Save to NPZ file: `data/reference/apose_from_blender.npz`
2. Script should:
    - Match joint names to indices
    - Handle armature in rest pose or posed state
    - Export in correct coordinate system (Z-up, meters)
3. Test script on T-pose armature to verify it exports correctly

**Deliverable**: Script that exports `J_ABSOLUTE` from Blender armature

### M2.2: Manually Create A-Pose in Blender

**Task**: Use Blender to manually adjust T-pose armature to A-pose

**Sub-tasks**:

1. Load T-pose armature in Blender (or create from hardcoded `J_ABSOLUTE`)
2. Manually rotate bones to create A-pose:
    - Arms: Rotate down ~45° from horizontal
    - Legs: Slight outward rotation if needed
    - Spine: Minimal changes
    - Hands: Natural A-pose position
3. Visual verification: A-pose should look correct
4. Save Blender file for future reference

**Deliverable**: A-pose armature in Blender (visually verified)

### M2.3: Export A-Pose J_ABSOLUTE

**Task**: Run export script to save A-pose `J_ABSOLUTE`

**Sub-tasks**:

1. Run export script on A-pose armature:
    ```bash
    /Applications/Blender.app/Contents/MacOS/Blender --background --python src/utils/reference/export_apose_from_blender.py
    ```
2. Verify exported NPZ file:
    - Check shape is (52, 3)
    - Compare a few key joints to T-pose (should differ by rotation only)
    - Verify bone lengths are same (compute `SMPL_OFFSETS` and compare to T-pose)
3. Save to `data/reference/apose_from_blender.npz`

**Deliverable**: Exported A-pose `J_ABSOLUTE` NPZ file

**Acceptance Criteria**:

-   A-pose looks correct visually in Blender
-   Exported `J_ABSOLUTE` has shape (52, 3)
-   Bone lengths match T-pose (same `SMPL_OFFSETS`)
-   Only joint positions differ (rotations applied)

---

## Milestone M3: Load A-Pose J_ABSOLUTE for Frame 0 Alignment

**Objective**: Load the exported A-pose `J_ABSOLUTE` and prepare it for use in frame 0 alignment.

### M3.1: Create Load Function for A-Pose

**Task**: Create function to load A-pose `J_ABSOLUTE` from exported NPZ

**Sub-tasks**:

1. Create function `load_apose_j_absolute() -> NDArray[np.float64]`:
    - Load `data/reference/apose_from_blender.npz`
    - Extract `J_ABSOLUTE` key
    - Validate shape is (52, 3)
    - Return as `NDArray[np.float64]`
2. Add error handling and logging
3. Keep existing `load_reference_j_absolute()` for other uses if needed

**Deliverable**: Function to load A-pose `J_ABSOLUTE`

### M3.2: Verify A-Pose Bone Lengths

**Task**: Confirm that A-pose has same bone lengths as T-pose

**Sub-tasks**:

1. Load both T-pose and A-pose `J_ABSOLUTE`
2. Compute `SMPL_OFFSETS` for both
3. Compare offsets - should be identical (within floating-point precision)
4. If different, investigate why (should only differ by rotations)

**Deliverable**: Confirmation that bone lengths match

**Acceptance Criteria**:

-   A-pose `SMPL_OFFSETS` match T-pose `SMPL_OFFSETS` exactly
-   Only `J_ABSOLUTE` positions differ (due to rotations)

---

## Milestone M3.3: Diagnose Armature Facing Ground Issue

**Objective**: Investigate why the entire armature is facing the ground (pelvis rotation issue).

### M3.3.1: Check Reference NPZ Coordinate System

**Task**: Verify the coordinate system of the reference NPZ J_ABSOLUTE

**Sub-tasks**:

1. Load reference NPZ and inspect J_ABSOLUTE values:
    - Check pelvis position (should be near origin or reasonable)
    - Check if Z is up (Blender standard) or Y is up
    - Compare to what Blender expects (Z-up, meters)
2. Load reference GLB (`data/reference/smplh_target.glb`) and check:
    - What coordinate system it uses
    - How the armature is oriented
    - Compare pelvis position in GLB vs NPZ
3. Document findings in `docs/M3_4_COORDINATE_SYSTEM.md`

**Deliverable**: Analysis document showing coordinate system of reference NPZ

### M3.3.2: Check Pelvis Rotation Application

**Task**: Verify how pelvis rotation is being applied in forward kinematics

**Sub-tasks**:

1. Add diagnostic logging to `forward_kinematics()`:
    - Log pelvis rotation (first 3 values of `poses`)
    - Log pelvis translation (`trans`)
    - Log computed pelvis position after FK
2. Test on a single frame:
    - Load a test NPZ
    - Print pelvis rotation values
    - Check if rotation is being applied correctly
    - Verify if pelvis rotation should be zero for A-pose
3. Check if mocap `poses[0]` (pelvis rotation) is non-zero and causing the issue

**Deliverable**: Diagnostic output showing pelvis rotation values and their effect

### M3.3.3: Compare Reference GLB vs Generated GLB

**Task**: Visually compare reference GLB orientation to generated GLB

**Sub-tasks**:

1. Load `data/reference/smplh_target.glb` in Blender:
    - Note armature orientation
    - Check pelvis position and rotation
    - Export frame 0 joint positions
2. Load a generated GLB from retarget.py:
    - Compare frame 0 orientation
    - Check if there's a rotation difference
    - Measure angle between reference and generated
3. Document findings

**Deliverable**: Comparison document with visual notes and measurements

### M3.3.4: Test Zero Pelvis Rotation

**Task**: Test if setting pelvis rotation to zero fixes the orientation issue

**Sub-tasks**:

1. Create test script that:
    - Loads mocap NPZ
    - Sets `poses[0]` (pelvis rotation) to `[0, 0, 0]` for all frames
    - Runs retarget.py with modified poses
2. Check if armature is now upright
3. If yes: pelvis rotation is the issue
4. If no: investigate coordinate system or J_ABSOLUTE loading

**Deliverable**: Test results and conclusion about root cause

**Acceptance Criteria**:

-   Root cause identified (pelvis rotation, coordinate system, or J_ABSOLUTE loading)
-   Clear explanation of why armature faces ground
-   Proposed fix identified

---

## Milestone M3.4: Diagnose Rotation Application Issues

**Objective**: Investigate why rotations are applied strangely (arms at different angles).

### M3.4.1: Compare Frame 0 Pose to A-Pose

**Task**: Check if frame 0 of mocap matches A-pose

**Sub-tasks**:

1. Create diagnostic script:
    - Load mocap NPZ
    - Compute frame 0 joint positions using FK
    - Load reference A-pose J_ABSOLUTE
    - Compare joint positions
2. Measure differences:
    - Which joints differ most?
    - Are arms in different positions?
    - Are rotations relative to wrong rest pose?
3. Document findings

**Deliverable**: Comparison showing frame 0 vs A-pose differences

### M3.4.2: Understand Rotation Space

**Task**: Verify that mocap rotations are relative to original rest pose, not A-pose

**Sub-tasks**:

1. Research: Are `poses` in mocap NPZ relative to:
    - Original mocap subject's rest pose (T-pose)?
    - Some other reference pose?
2. Check if this explains why rotations look wrong:
    - If mocap rotations are relative to T-pose
    - But we're applying them to A-pose bone lengths
    - The rotations will be wrong
3. This is expected - M4 will fix by setting frame 0 to A-pose first

**Deliverable**: Explanation of rotation space issue

### M3.4.3: Visualize Rotation Differences

**Task**: Create visualization showing how rotations differ

**Sub-tasks**:

1. Create script that:
    - Computes what frame 0 should look like with mocap rotations
    - Computes what A-pose looks like
    - Shows difference in bone directions
2. Export both as GLBs for visual comparison
3. Document which bones are most affected

**Deliverable**: Visual comparison GLBs and analysis

**Acceptance Criteria**:

-   Confirmed that rotations are relative to wrong rest pose
-   Understanding that M4 (frame 0 A-pose) will fix this
-   Clear explanation of why arms look wrong

---

## Milestone M4: Set Frame 0 to A-Pose

**Objective**: Override frame 0 of all animations to exactly match the A-pose created in Blender, while preserving animation starting from frame 1.

### M4.1: Load A-Pose Joint Positions

**Task**: Load A-pose joint positions for frame 0 override

**Sub-tasks**:

1. Use `load_apose_j_absolute()` from M3.1:
    - Load `J_ABSOLUTE` from `data/reference/apose_from_blender.npz`
    - Return as (52, 3) array
2. This is the target joint positions for frame 0

**Deliverable**: Function that returns reference A-pose joint positions

### M4.2: Compute A-Pose Bone Rotations

**Task**: Compute bone rotations needed to achieve A-pose from current frame 0

**Sub-tasks**:

1. Create function `compute_apose_rotations(joint_positions: NDArray[np.float64]) -> List[Quaternion]`:
    - Input: Current frame 0 joint positions (52, 3)
    - Input: Target A-pose joint positions (52, 3)
    - For each bone, compute rotation needed to align bone direction to A-pose
    - Return list of quaternions (one per bone)
2. Algorithm:
    - For each bone, compute current bone direction (tail - head)
    - Compute target bone direction from A-pose
    - Compute rotation quaternion to align directions
    - Handle special cases (root bone, end bones)
3. Test on single frame to verify rotations are correct

**Deliverable**: Function that computes A-pose rotations from joint positions

### M4.3: Apply A-Pose to Frame 0 (After Baking)

**Task**: Override frame 0 bone rotations after constraint baking

**Sub-tasks**:

1. In `process_npz_file()`, after baking constraints:
    - Get reference A-pose joint positions
    - Compute A-pose rotations for frame 0
    - Set frame 0 to these rotations
    - Insert keyframes at frame 0
2. Ensure frame 1+ are unchanged (preserve animation)
3. Add logging: confirm frame 0 was overridden

**Deliverable**: Updated `retarget.py` that sets frame 0 to A-pose

### M4.4: Validate Frame 0 A-Pose

**Task**: Verify frame 0 matches reference A-pose

**Sub-tasks**:

1. Use existing validation script `src/utils/validation/validate_frame0_apose.py`
2. Run on test GLB files:
    ```bash
    /Applications/Blender.app/Contents/MacOS/Blender --background --python src/utils/validation/validate_frame0_apose.py -- data/output/test_file_retargeted.glb
    ```
3. Verify all joints match reference A-pose within tolerance (1mm per joint)
4. Visual check: Load GLB in Blender, compare frame 0 to `smplh_target.glb`

**Deliverable**: Validation results showing frame 0 matches A-pose

**Acceptance Criteria**:

-   Frame 0 joint positions match reference A-pose (within 1mm per joint)
-   Frame 1+ animations are preserved (unchanged)
-   Visual inspection confirms frame 0 looks identical to reference
-   Validation script reports 100% pass rate

---

## Milestone M5: Convert A-Pose GLB to NPZ

**Objective**: Create script to convert A-pose reference GLB back to NPZ format, enabling visual adjustment of A-pose in Blender and reuse in `retarget.py`.

### M5.1: Check Existing Scripts

**Task**: Determine if we already have a GLB → NPZ converter

**Sub-tasks**:

1. Search for existing scripts:
    - Check `src/utils/reference/convert_reference_to_glb.py` (reverse direction?)
    - Search for any GLB → NPZ conversion scripts
2. If exists: Review and determine if it can be used/adapted
3. If not exists: Mark as "needs creation"

**Deliverable**: Document `docs/M5_EXISTING_SCRIPTS.md` with findings

### M5.2: Create GLB → NPZ Converter

**Task**: Create script to extract `J_ABSOLUTE` and `SMPL_OFFSETS` from A-pose GLB

**Sub-tasks**:

1. Create script `src/utils/reference/convert_glb_to_reference_npz.py`:
    - Load GLB file
    - Extract armature
    - For each bone, get head position (this is `J_ABSOLUTE`)
    - Compute `SMPL_OFFSETS` from `J_ABSOLUTE` using parent tree
    - Save to NPZ with keys: `J_ABSOLUTE`, `SMPL_OFFSETS`, `JOINT_NAMES`
2. Handle edge cases:
    - Missing bones
    - Wrong bone count
    - Invalid hierarchy
3. Add validation: verify output NPZ matches input GLB structure

**Deliverable**: Script that converts GLB → NPZ

### M5.3: Test Round-Trip Conversion

**Task**: Verify GLB → NPZ → GLB round-trip works

**Sub-tasks**:

1. Start with `data/reference/smplh_target.glb`
2. Convert to NPZ: `convert_glb_to_reference_npz.py smplh_target.glb output.npz`
3. Load output NPZ in `retarget.py` (M2/M3)
4. Export to GLB
5. Compare original GLB vs. round-trip GLB:
    - Visual inspection in Blender
    - Joint position comparison (should match within 0.1mm)

**Deliverable**: Round-trip test results

**Acceptance Criteria**:

-   GLB → NPZ conversion works without errors
-   NPZ contains correct `J_ABSOLUTE`, `SMPL_OFFSETS`, `JOINT_NAMES`
-   Round-trip GLB matches original (within 0.1mm per joint)
-   Script can be used to update reference A-pose after Blender adjustments

---

## Milestone M6: Fix Joint Scale/Distortion Bug

**Objective**: Fix bug where joints are being scaled/distorted in the retargeted animation. This is likely happening in the empties and constraints section of the code.

### M6.1: Identify Scale/Distortion Source

**Task**: Locate where joint scaling/distortion is occurring

**Sub-tasks**:

1. Review empties and constraints code section in `retarget.py`:
    - Empty creation and positioning (lines ~404-411)
    - Constraint setup (lines ~447-518)
    - Baking process (lines ~523-545)
2. Identify potential scale issues:
    - Empty display size affecting calculations?
    - Constraint settings causing scaling?
    - Bone rest length vs. actual length mismatches?
    - Transform application issues?
3. Compare with `create_glb_from_npz_fixed.py`:
    - Are there differences in how empties/constraints are set up?
    - Does the original script have the same issue?
4. Document findings: list all potential sources of scaling/distortion

**Deliverable**: Analysis document `docs/M6_SCALE_BUG_ANALYSIS.md` with:

-   List of potential bug sources
-   Code sections where scaling might occur
-   Comparison with original script

### M6.2: Reproduce and Measure Distortion

**Task**: Create test case that clearly shows the scale/distortion bug

**Sub-tasks**:

1. Process a test NPZ file with known bone lengths
2. Measure joint positions in output GLB:
    - Compare frame 0 joint positions to expected (from FK)
    - Compare bone lengths to reference A-pose
    - Identify which joints are distorted and by how much
3. Create visualization:
    - Export joint positions to CSV for analysis
    - Create comparison plot (expected vs. actual)
    - Document specific frames/joints where distortion is worst
4. Quantify distortion:
    - Measure scale factor per joint (if uniform scaling)
    - Measure position errors (if non-uniform)
    - Identify pattern (all joints? specific bones? specific frames?)

**Deliverable**: Test results document `docs/M6_DISTORTION_MEASUREMENTS.md` with:

-   Quantified distortion measurements
-   Visualizations/comparisons
-   Pattern identification

### M6.3: Fix Scale Issue in Empties/Constraints

**Task**: Fix the identified scale/distortion bug

**Sub-tasks**:

1. Based on M6.1 and M6.2 findings, implement fix:
    - **If empty display size issue**: Remove or correct empty size scaling
    - **If constraint rest length issue**: Set correct rest lengths or disable rest length constraints
    - **If transform application issue**: Ensure transforms are applied correctly
    - **If bone length mismatch**: Ensure bone rest pose matches FK-computed lengths
2. Test fix on same test case from M6.2
3. Verify distortion is reduced/eliminated:
    - Joint positions match expected (within tolerance)
    - Bone lengths match reference
    - Animation looks correct

**Deliverable**: Updated `retarget.py` with scale/distortion fix

### M6.4: Validate Fix Across Multiple Files

**Task**: Ensure fix works across different animations

**Sub-tasks**:

1. Test fix on multiple NPZ files:
    - Different motion types (walking, jumping, gesturing)
    - Different datasets (ACCAD, EKUT)
    - Different frame counts
2. For each file:
    - Process with fixed code
    - Measure joint positions vs. expected
    - Visual inspection in Blender
3. Document results:
    - List of files tested
    - Any remaining distortion issues
    - Performance impact (if any)

**Deliverable**: Validation results document `docs/M6_FIX_VALIDATION.md`

**Acceptance Criteria**:

-   Joint positions match FK-computed positions (within 1mm per joint)
-   Bone lengths match reference A-pose (within 0.1mm per bone)
-   No visual distortion in animation playback
-   Fix works across 5+ test files
-   No performance degradation

---

## Milestone M7: Preserve Feet Behavior (Ground Contact)

**Objective**: Ensure feet stay on the ground when they should be, prevent sliding, and maintain natural foot placement. This is a subjective adjustment that may involve IK solving or proportional adjustments.

**Status**: **PLANNING PHASE** - Detailed approach to be determined after M1-M6 are complete.

### M7.1: Analyze Current Feet Behavior

**Task**: Understand what's wrong with feet in current output

**Sub-tasks**:

1. Process test animations and identify feet issues:
    - Feet floating above ground
    - Feet sliding on ground
    - Feet penetrating ground
    - Unnatural foot angles
2. Document specific problems with examples (frame numbers, joint names)
3. Measure ground level (relative to pelvis or absolute)

**Deliverable**: Analysis document `docs/M7_FEET_ANALYSIS.md`

### M7.2: Determine Ground Level

**Task**: Define where the ground is for each animation

**Sub-tasks**:

1. Approach options:
    - **Option A**: Ground = lowest foot position across all frames
    - **Option B**: Ground = pelvis Z - constant offset (e.g., 1.0m)
    - **Option C**: Ground = average of foot positions when "on ground"
2. Implement ground detection:
    - Find frames where feet should be on ground (stance phase)
    - Compute ground level for those frames
    - Apply to all frames
3. Test on multiple animations to verify approach

**Deliverable**: Ground detection function and test results

### M7.3: Implement Feet Adjustment (TBD)

**Task**: Adjust feet to maintain ground contact

**Approach Options** (to be selected based on M7.1 analysis):

**Option A: Proportional Adjustment**

-   Scale leg bone lengths proportionally to reach ground
-   Adjust hip/knee/ankle rotations to maintain natural angles
-   Preserve relative foot positions

**Option B: IK-Based Solution**

-   Use inverse kinematics to solve for bone rotations
-   Target: foot position at ground level
-   Constraints: maintain natural joint limits

**Option C: Hybrid Approach**

-   Use IK for major adjustments
-   Use proportional scaling for fine-tuning
-   Blend with original rotations based on confidence

**Sub-tasks** (to be detailed after approach selection):

1. Implement chosen approach
2. Test on sample animations
3. Visual validation
4. Iterate based on results

**Deliverable**: Feet adjustment implementation (approach TBD)

**Acceptance Criteria** (to be refined):

-   Feet stay on ground during stance phases
-   No sliding when feet should be planted
-   Natural foot angles maintained
-   Animation character preserved

---

## Milestone M8: Preserve Hands Behavior

**Objective**: Maintain natural hand positions relative to body parts, objects, or ground. This may involve relative positioning, proportional adjustments, or subjective tweaks.

**Status**: **PLANNING PHASE** - Detailed approach to be determined after M1-M5 are complete. May be out of scope.

### M8.1: Analyze Current Hands Behavior

**Task**: Understand what's wrong with hands in current output

**Sub-tasks**:

1. Process test animations and identify hand issues:
    - Hands too far from body
    - Hands in wrong positions relative to objects
    - Unnatural hand angles
    - Hand-to-hand relationships incorrect
2. Document specific problems with examples
3. Identify what hands should be relative to (body parts, ground, objects)

**Deliverable**: Analysis document `docs/M8_HANDS_ANALYSIS.md`

### M8.2: Determine Adjustment Strategy (TBD)

**Task**: Decide how to adjust hands

**Approach Options** (to be selected based on M8.1 analysis):

**Option A: Relative Positioning**

-   Maintain hand positions relative to specific body parts (shoulders, chest, etc.)
-   Adjust based on body part movement
-   Preserve hand-to-hand relationships

**Option B: Proportional Scaling**

-   Scale arm bone lengths to reach target positions
-   Adjust shoulder/elbow/wrist rotations proportionally
-   Preserve relative hand positions

**Option C: Subjective Manual Tweaks**

-   Identify key frames where hands are critical
-   Manually adjust those frames
-   Interpolate between key frames

**Sub-tasks** (to be detailed after approach selection):

1. Implement chosen approach
2. Test on sample animations
3. Visual validation
4. Iterate based on results

**Deliverable**: Hands adjustment implementation (approach TBD)

**Acceptance Criteria** (to be refined):

-   Hands maintain natural positions relative to body
-   Hand-to-hand relationships preserved
-   Natural hand angles maintained
-   Animation character preserved

**Note**: This milestone may be out of scope depending on project priorities and complexity.

---

## Testing Strategy

### Unit Tests

-   Each milestone should include unit tests for new functions
-   Test scripts in `tests/` directory
-   Run in Blender: `/Applications/Blender.app/Contents/MacOS/Blender --background --python tests/test_name.py`

### Integration Tests

-   After each milestone, test full pipeline:
    1. Process test NPZ file
    2. Export to GLB
    3. Validate output
    4. Visual inspection

### Validation Scripts

-   Use existing validation scripts:
    -   `src/utils/validation/validate_frame0_apose.py` (M4)
    -   `src/utils/validation/validate_root_alignment.py` (if needed)
-   Create new validation scripts as needed

### Test Data

-   Use `data/test_small/` for quick tests
-   Use `data/extracted/` for comprehensive tests
-   Test on multiple datasets (ACCAD, EKUT) when possible

---

## File Structure

```
src/
  retarget.py                    # Main retargeting script (updated in M1-M4)
  utils/
    reference/
      convert_glb_to_reference_npz.py  # M5: GLB → NPZ converter
    validation/
      validate_frame0_apose.py          # M4: Frame 0 validation
tests/
  M2_test_load_j_absolute.py          # M2: Test load function
  M3_validate_apose_offsets.py        # M3: Validate offsets
docs/
  M1_SCRIPT_COMPARISON.md             # M1: Script comparison
  M1_STALE_CODE_ANALYSIS.md           # M1: Stale code analysis
  M3_TEST_RESULTS.md                  # M3: Test results
  M6_SCALE_BUG_ANALYSIS.md            # M6: Scale/distortion bug analysis
  M6_DISTORTION_MEASUREMENTS.md       # M6: Distortion measurements
  M6_FIX_VALIDATION.md                # M6: Fix validation results
  M7_FEET_ANALYSIS.md                 # M7: Feet analysis (TBD)
  M8_HANDS_ANALYSIS.md                # M8: Hands analysis (TBD)
data/
  reference/
    smplh_target_reference.npz         # A-pose reference (input for M2)
    smplh_target.glb                   # A-pose reference GLB (input for M5)
```

---

## Dependencies

-   **Blender 4.5+** (with Python 3.x)
-   **NumPy** (for array operations)
-   **Pathlib** (for file paths)
-   **Mathutils** (Blender's math library)

---

## Notes

1. **Simplest Approach First**: We use NPZ for loading `J_ABSOLUTE` (M2) even though GLB might be simpler later. This is because we already have the NPZ and it's the most straightforward path.

2. **Subjective Adjustments**: M7 and M8 involve subjective visual tweaks. The exact approach will be determined based on analysis of what's wrong with current output.

3. **Out of Scope**: M8 (hands) may be out of scope depending on project priorities. Focus on M1-M6 first, then evaluate if M7/M8 are needed.

4. **Iterative Development**: Each milestone builds on the previous one. Complete M1 before M2, M2 before M3, etc.

5. **Validation at Each Step**: Every milestone includes validation to ensure correctness before moving to the next milestone.
