# Retargeting Project Spec - Library-Based Approach

## Overview

**Goal**: Retarget SMPL-H motion capture animations from source `.npz` files onto a target A-pose SMPL-H skeleton using external libraries, preserving animation character, ensuring feet stay on ground, and maintaining hand/finger behavior.

**Current Problem**: The existing `create_glb_from_npz_fixed.py` directly applies rotations without accounting for scale/proportion differences, causing:

-   Foot sliding (feet not on ground)
-   Lost hand/finger behavior
-   Lost animation character
-   Arm/leg mismatch due to different bone lengths

**New Strategy**: Leverage proven retargeting libraries instead of implementing retargeting math manually.

---

## Part 1: Research & Validation Phase

### Research Overview

Before implementing, we need to thoroughly research, validate, and test each proposed library/tool to ensure it:

1. Works with SMPL-H format
2. Can be automated (no manual steps)
3. Handles proportion/scale differences correctly
4. Preserves animation character
5. Can be integrated into our pipeline

### R1: Research Rokoko Studio Live Add-on

**Objective**: Understand Rokoko's capabilities, limitations, and automation requirements for SMPL-H retargeting.

**Tasks**:

1. **R1.1 - Documentation Review**

    - Read Rokoko Studio Live documentation
    - Identify exact operator names and parameters
    - Check if SMPL-H is supported natively
    - Document bone mapping requirements
    - **Validation**: Create summary document `docs/RESEARCH/rokoko_research.md` with:
        - Operator signatures
        - Required parameters
        - SMPL-H compatibility notes
        - Known limitations

2. **R1.2 - Installation Testing**

    - Download Rokoko add-on
    - Test installation via `bpy.ops.preferences.addon_install()`
    - Test enabling via `bpy.ops.preferences.addon_enable()`
    - Verify operator availability: `hasattr(bpy.ops, 'rokoko')`
    - **Validation**: Create test script `tests/research/test_rokoko_installation.py` that:
        - Installs add-on programmatically
        - Verifies operator exists
        - Reports success/failure

3. **R1.3 - Basic Functionality Test**

    - Create minimal test: two simple armatures (source + target)
    - Test `bpy.ops.rokoko.retarget()` with minimal parameters
    - Verify it runs without errors
    - Check if output armature has animation
    - **Validation**: Script `tests/research/test_rokoko_basic.py` that:
        - Creates two test armatures (3 bones each)
        - Applies simple animation to source
        - Runs retarget operator
        - Exports GLB and verifies animation exists
        - Reports pass/fail

4. **R1.4 - SMPL-H Compatibility Test**

    - Import our existing `smplh_target.glb` (target A-pose)
    - Import one animation GLB from `create_glb_from_npz_fixed.py` (source)
    - Attempt retargeting with default bone mapping
    - Document any bone mapping issues
    - Test with custom JSON bone mapping if needed
    - **Validation**: Script `tests/research/test_rokoko_smplh.py` that:
        - Loads source animation GLB
        - Loads target A-pose GLB
        - Runs retarget operator
        - Validates bone count (should be 52)
        - Checks for missing/unmapped bones
        - Exports result and visual inspection
        - Reports detailed findings

5. **R1.5 - Proportion/Scale Handling Test**

    - Create test case: source with different bone lengths than target
    - Run retargeting
    - Measure bone lengths in output vs target
    - Check if feet/hands maintain positions
    - **Validation**: Script `tests/research/test_rokoko_proportions.py` that:
        - Creates source with 1.2x scale
        - Creates target with 1.0x scale
        - Retargets
        - Measures output bone lengths (should match target)
        - Checks end effector positions (feet, hands)
        - Reports scale handling quality

6. **R1.6 - Animation Character Preservation Test**
    - Use a known animation (e.g., cartwheel) from our dataset
    - Retarget using Rokoko
    - Compare visually: source vs retargeted
    - Check for:
        - Foot sliding
        - Hand position preservation
        - Motion smoothness
        - Overall character preservation
    - **Validation**: Manual visual inspection + automated checks:
        - Script: `tests/research/test_rokoko_character.py`
            - Loads cartwheel animation
            - Retargets
            - Computes FK positions for key joints (feet, hands) per frame
            - Compares source vs retargeted:
                - Foot height variation (should be minimal)
                - Hand trajectories (should match closely)
            - Reports character preservation metrics

**Acceptance Criteria**:

-   ✅ All 6 research tasks completed with validation scripts
-   ✅ Documentation created with findings
-   ✅ Clear understanding of Rokoko's capabilities/limitations
-   ✅ Decision on whether Rokoko is viable for our use case

**Outputs**:

-   `docs/RESEARCH/rokoko_research.md`
-   `tests/research/test_rokoko_*.py` (6 scripts)
-   Test results and recommendations

---

### R2: Research smplx + human-body-prior Stack

**Objective**: Evaluate pure Python approach using smplx library and human-body-prior for retargeting.

**Tasks**:

1. **R2.1 - Library Installation & Setup**

    - Install `smplx` library
    - Install `human-body-prior` (if available)
    - Install `pytorch3d` or `trimesh` for export
    - Test basic imports and version compatibility
    - **Validation**: Script `tests/research/test_smplx_installation.py`:
        - Imports all required libraries
        - Checks versions
        - Tests basic SMPL-H model loading
        - Reports compatibility

2. **R2.2 - Load Source Animation NPZ**

    - Test loading our animation NPZ files with smplx
    - Parse `poses`, `trans`, `betas` from NPZ
    - Create SMPL-H model instance
    - Generate joint positions for one frame
    - **Validation**: Script `tests/research/test_smplx_load_animation.py`:
        - Loads one of our animation NPZ files
        - Creates SMPL-H model
        - Computes joint positions for frame 0
        - Compares with our FK computation (should match closely)
        - Reports differences

3. **R2.3 - Load Target Reference NPZ**

    - Test loading our `smplh_target_reference.npz`
    - Understand how to apply different `betas` or `J_ABSOLUTE` to model
    - Create target SMPL-H model with reference proportions
    - **Validation**: Script `tests/research/test_smplx_load_target.py`:
        - Loads reference NPZ
        - Creates target model
        - Extracts bone lengths
        - Compares with reference `SMPL_OFFSETS`
        - Reports compatibility

4. **R2.4 - Retargeting Approach Research**

    - Research if `human-body-prior` has retargeting utilities
    - Understand how to transfer poses between different SMPL-H instances
    - Test basic pose transfer (if examples exist)
    - **Validation**: Document findings in `docs/RESEARCH/smplx_retargeting_research.md`:
        - Available retargeting functions
        - Example code snippets
        - Limitations
        - Integration complexity

5. **R2.5 - GLB Export Test**
    - Test exporting animated skeleton to GLB using `trimesh` or `pygltflib`
    - Verify animation keyframes are preserved
    - Check if exported GLB opens in Blender correctly
    - **Validation**: Script `tests/research/test_smplx_export_glb.py`:
        - Creates animated skeleton from NPZ
        - Exports to GLB
        - Imports back into Blender (via script)
        - Verifies animation exists
        - Reports export quality

**Acceptance Criteria**:

-   ✅ All 5 research tasks completed
-   ✅ Understanding of smplx capabilities for our use case
-   ✅ Assessment of retargeting complexity with this stack
-   ✅ Decision on viability

**Outputs**:

-   `docs/RESEARCH/smplx_retargeting_research.md`
-   `tests/research/test_smplx_*.py` (5 scripts)
-   Test results and recommendations

---

### R3: Research mmhuman3d

**Objective**: Evaluate OpenMMLab's mmhuman3d library for SMPL-H retargeting.

**Tasks**:

1. **R3.1 - Installation & Setup**

    - Install `mmhuman3d` (check dependencies)
    - Test imports and basic functionality
    - **Validation**: Script `tests/research/test_mmhuman3d_installation.py`

2. **R3.2 - Documentation Review**

    - Find retargeting/conversion functions
    - Check SMPL-H support
    - Document API for pose conversion
    - **Validation**: Document in `docs/RESEARCH/mmhuman3d_research.md`

3. **R3.3 - Pose Conversion Test**

    - Test `convert_smpl_pose()` function (if exists)
    - Try converting between two SMPL-H instances
    - **Validation**: Script `tests/research/test_mmhuman3d_conversion.py`

4. **R3.4 - GLB Export Test**
    - Test visualization/export functions
    - Verify compatibility with our pipeline
    - **Validation**: Script `tests/research/test_mmhuman3d_export.py`

**Acceptance Criteria**:

-   ✅ Library evaluation complete
-   ✅ Viability assessment
-   ✅ Integration complexity understood

**Outputs**:

-   `docs/RESEARCH/mmhuman3d_research.md`
-   Test scripts and results

---

### R4: Research motion-capture-transfer

**Objective**: Evaluate ISL's MotionCaptureTransfer tool for retargeting.

**Tasks**:

1. **R4.1 - Repository Review**

    - Clone/download repository
    - Review README and documentation
    - Understand input/output formats
    - **Validation**: Document in `docs/RESEARCH/motion_capture_transfer_research.md`

2. **R4.2 - Integration Test**

    - Test if it can be called from Python
    - Check if it accepts NPZ input
    - Test with our data format
    - **Validation**: Script `tests/research/test_motion_capture_transfer.py`

3. **R4.3 - Output Format Test**
    - Check output format (NPZ, GLB, etc.)
    - Test if output can be imported into our pipeline
    - **Validation**: Verify output compatibility

**Acceptance Criteria**:

-   ✅ Tool evaluated
-   ✅ Integration path understood
-   ✅ Viability determined

**Outputs**:

-   Research documentation
-   Test results

---

### R5: Decision Matrix & Tool Selection

**Objective**: Synthesize all research and select the best approach.

**Tasks**:

1. **R5.1 - Create Comparison Matrix**

    - Compare all researched tools on:
        - SMPL-H compatibility
        - Automation capability
        - Proportion/scale handling
        - Foot/hand preservation
        - Integration complexity
        - Documentation quality
        - Maintenance/community support
    - **Validation**: Document in `docs/RESEARCH/tool_comparison.md`

2. **R5.2 - Select Primary Approach**

    - Based on research, select primary tool
    - Document rationale
    - Identify fallback options
    - **Validation**: Decision document with justification

3. **R5.3 - Create Implementation Plan**
    - Break down selected approach into implementation steps
    - Identify integration points with existing code
    - Plan testing strategy
    - **Validation**: Implementation roadmap document

**Acceptance Criteria**:

-   ✅ Clear tool selection with justification
-   ✅ Implementation plan created
-   ✅ Ready to proceed to implementation

**Outputs**:

-   `docs/RESEARCH/tool_comparison.md`
-   `docs/RESEARCH/selected_approach.md`
-   Implementation roadmap

---

## Part 2: Implementation Phase

_Note: Implementation milestones will be created after research phase completes and tool is selected. The following are example milestones assuming Rokoko is selected (most likely based on conversation)._

### M1: Setup Development Environment

**Objective**: Set up infrastructure for library-based retargeting.

**Tasks**:

1. **M1.1 - Install Selected Library**

    - Install primary tool (e.g., Rokoko add-on)
    - Create installation script
    - Test installation in headless Blender
    - **Validation**: Script verifies installation success

2. **M1.2 - Create Project Structure**

    - Create `src/retargeting/` directory
    - Set up module structure
    - Create utility functions for library interaction
    - **Validation**: Module imports successfully

3. **M1.3 - Create Base Retargeting Class**
    - Create abstract base class or interface
    - Define common methods (load_source, load_target, retarget, export)
    - **Validation**: Base class can be instantiated (even if not functional)

**Acceptance Criteria**:

-   ✅ Selected library installed and verified
-   ✅ Project structure in place
-   ✅ Base architecture defined

---

### M2: Implement Source NPZ → GLB Conversion

**Objective**: Convert source animation NPZ to GLB using existing code (or improve it).

**Tasks**:

1. **M2.1 - Extract/Refactor NPZ → GLB Function**

    - Extract core functionality from `create_glb_from_npz_fixed.py`
    - Create reusable function `convert_npz_to_glb()`
    - Test with single file
    - **Validation**: Script `tests/test_npz_to_glb.py` verifies conversion

2. **M2.2 - Batch Processing Support**

    - Add batch processing capability
    - Handle errors gracefully
    - Progress reporting
    - **Validation**: Processes 10+ files successfully

3. **M2.3 - Output Validation**
    - Verify GLB has correct structure
    - Check animation exists
    - Verify bone count (52)
    - **Validation**: Automated checks pass

**Acceptance Criteria**:

-   ✅ NPZ → GLB conversion working
-   ✅ Batch processing supported
-   ✅ Output validated

---

### M3: Implement Target Reference Loading

**Objective**: Load target A-pose skeleton for retargeting.

**Tasks**:

1. **M3.1 - Load Target Reference NPZ**

    - Create function to load `smplh_target_reference.npz`
    - Extract bone structure
    - Validate data format
    - **Validation**: Script loads and validates reference

2. **M3.2 - Convert Target to GLB**

    - Create target GLB from reference NPZ (if not exists)
    - Ensure correct bone naming
    - Verify A-pose structure
    - **Validation**: Target GLB matches reference

3. **M3.3 - Validate Target Compatibility**
    - Check bone count (52)
    - Verify bone names match expected SMPL-H names
    - **Validation**: Automated validation script

**Acceptance Criteria**:

-   ✅ Target reference loads correctly
-   ✅ Target GLB available
-   ✅ Compatibility verified

---

### M4: Implement Library Integration (Rokoko Example)

**Objective**: Integrate selected retargeting library into pipeline.

**Tasks**:

1. **M4.1 - Create Library Wrapper**

    - Create wrapper class for library (e.g., `RokokoRetargeter`)
    - Implement basic retargeting call
    - Handle errors and edge cases
    - **Validation**: Wrapper can retarget simple test case

2. **M4.2 - Bone Mapping Configuration**

    - Create SMPL-H bone mapping JSON (if needed)
    - Test mapping with our bone names
    - Handle any unmapped bones
    - **Validation**: All 52 bones mapped correctly

3. **M4.3 - Retargeting Parameters**

    - Test and tune retargeting parameters:
        - Auto-scale
        - IK foot correction
        - Hand preservation
    - Document optimal settings
    - **Validation**: Test script verifies parameter effects

4. **M4.4 - Single File Retargeting Test**
    - Retarget one animation file end-to-end
    - Verify output quality
    - Check for common issues
    - **Validation**: Output GLB passes quality checks

**Acceptance Criteria**:

-   ✅ Library integrated
-   ✅ Retargeting works for single file
-   ✅ Parameters tuned
-   ✅ Output quality acceptable

---

### M5: Implement Validation & Quality Checks

**Objective**: Create comprehensive validation for retargeted animations.

**Tasks**:

1. **M5.1 - Bone Length Validation**

    - Check all bone lengths match target reference
    - Report any mismatches
    - **Validation**: Script reports bone length accuracy

2. **M5.2 - Foot Ground Contact Validation**

    - Measure foot height per frame
    - Detect foot sliding
    - Report frames with issues
    - **Validation**: Script identifies foot sliding issues

3. **M5.3 - Hand Position Validation**

    - Compare hand trajectories (source vs retargeted)
    - Measure position differences
    - **Validation**: Script reports hand preservation quality

4. **M5.4 - Animation Character Validation**
    - Visual inspection guidelines
    - Automated motion smoothness checks
    - Character preservation metrics
    - **Validation**: Comprehensive validation report

**Acceptance Criteria**:

-   ✅ All validation checks implemented
-   ✅ Reports generated successfully
-   ✅ Quality thresholds defined

---

### M6: Batch Processing & Pipeline Integration

**Objective**: Process entire dataset automatically.

**Tasks**:

1. **M6.1 - Create Batch Processing Script**

    - Process multiple NPZ files
    - Handle errors gracefully
    - Progress tracking
    - **Validation**: Processes 10+ files without crashes

2. **M6.2 - Error Handling & Recovery**

    - Catch and log errors
    - Continue processing on failures
    - Generate error report
    - **Validation**: Error handling works correctly

3. **M6.3 - Performance Optimization**

    - Optimize for large batches
    - Reduce Blender startup overhead (if applicable)
    - Parallel processing (if feasible)
    - **Validation**: Processing time acceptable

4. **M6.4 - End-to-End Test**
    - Process representative sample (50+ files)
    - Validate all outputs
    - Generate summary report
    - **Validation**: ≥95% success rate

**Acceptance Criteria**:

-   ✅ Batch processing working
-   ✅ Error handling robust
-   ✅ Performance acceptable
-   ✅ High success rate

---

### M7: Quality Assurance & Refinement

**Objective**: Improve retargeting quality based on validation results.

**Tasks**:

1. **M7.1 - Analyze Validation Results**

    - Review validation reports from M6
    - Identify common issues
    - Categorize failure modes
    - **Validation**: Issue analysis document

2. **M7.2 - Tune Retargeting Parameters**

    - Adjust parameters to fix common issues
    - Test on problematic files
    - **Validation**: Improved quality metrics

3. **M7.3 - Handle Edge Cases**

    - Identify edge cases (extreme poses, etc.)
    - Implement special handling
    - **Validation**: Edge cases handled correctly

4. **M7.4 - Final Quality Check**
    - Re-run validation on full dataset sample
    - Verify improvements
    - **Validation**: Quality metrics meet targets

**Acceptance Criteria**:

-   ✅ Quality improved
-   ✅ Edge cases handled
-   ✅ Quality targets met

---

### M8: Documentation & Finalization

**Objective**: Document the solution and prepare for production use.

**Tasks**:

1. **M8.1 - Code Documentation**

    - Document all functions
    - Add inline comments
    - Create API documentation
    - **Validation**: Documentation complete

2. **M8.2 - User Guide**

    - Create usage guide
    - Document CLI options
    - Provide examples
    - **Validation**: User can follow guide successfully

3. **M8.3 - Testing Documentation**

    - Document test procedures
    - Explain validation metrics
    - Provide troubleshooting guide
    - **Validation**: Testing docs are clear

4. **M8.4 - Final Integration Test**
    - Run full pipeline on 100+ files
    - Generate final report
    - **Validation**: Pipeline works end-to-end

**Acceptance Criteria**:

-   ✅ All documentation complete
-   ✅ Final tests pass
-   ✅ Ready for production use

---

## Success Criteria

**Overall Project Success**:

-   ✅ Retargeted animations preserve motion character
-   ✅ Feet stay on ground (minimal sliding)
-   ✅ Hand/finger behavior preserved
-   ✅ All bone lengths match target reference
-   ✅ Pipeline is fully automated (no manual steps)
-   ✅ Processes large datasets reliably (100+ files)
-   ✅ Quality validation reports show ≥95% pass rate

**Quality Metrics**:

-   Bone length accuracy: ≤0.2mm error
-   Foot height variation: ≤5mm per frame
-   Hand position error: ≤10mm per frame
-   Animation smoothness: No visible pops/jitter

---

## Notes

-   **Research Phase is Critical**: Spend adequate time (1-2 weeks) on research to avoid implementing the wrong solution
-   **Incremental Validation**: Each task should have validation to catch issues early
-   **Fallback Plans**: If primary tool doesn't work, have fallback options ready
-   **Preserve Existing Code**: Keep `create_glb_from_npz_fixed.py` as reference/fallback
-   **Visual Inspection**: Always combine automated checks with visual inspection
-   **Iterative Refinement**: Expect to iterate on parameters and approaches based on results

---

## Timeline Estimate

-   **Research Phase (R1-R5)**: 1-2 weeks
-   **Implementation Phase (M1-M8)**: 3-4 weeks
-   **Total**: 4-6 weeks

_Note: Timeline depends on research findings and selected approach complexity._
