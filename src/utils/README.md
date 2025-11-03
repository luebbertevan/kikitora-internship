# Utility Scripts

This directory contains utility scripts organized by purpose:

## 📁 Folder Structure

### `validation/` - Validation Tools (ACTIVE)

Scripts for validating retargeted animations against reference standards.

-   **`validate_frame0_apose.py`** - Validates frame 0 A-pose alignment (M4)
-   **`validate_frame0_apose_validated.py`** - Validated/correct version
-   **`validate_root_alignment.py`** - Validates root (pelvis) alignment (M3)
-   **`validate_single_frame.py`** - Validates specific frames with detailed stats

### `reference/` - Reference Generation Tools

Scripts for creating and managing reference files.

-   **`convert_reference_to_glb.py`** - Converts reference NPZ to GLB (M2+)
-   **`convert_reference_to_glb_validated.py`** - Validated version
-   **`extract_smplh_from_fbx.py`** - Extracts SMPL-H from FBX (M2 - ARCHIVE)
-   **`inventory_fbx_armature.py`** - Analyzes FBX armature structure (M2 - ARCHIVE)

### `archive/` - Historical/Archive Scripts

Scripts from completed milestones, kept for reference.

-   **`diagnose_scale.py`** - Scale diagnosis tool (M2.1 - COMPLETED)
-   **`explore_amass_data.py`** - AMASS data exploration (M1 - COMPLETED)
-   **`scale_reference.py`** - Reference scaling utility (M2.1 - COMPLETED)

### `debug/` - Debugging Tools

Scripts for debugging and troubleshooting.

-   **`debug_armature_rest_pose.py`** - Debug armature rest pose positions

## Usage Notes

-   **Active scripts** are regularly used in the current workflow
-   **Validated versions** are verified correct implementations (use when discrepancies exist)
-   **Archive scripts** are historical but may be useful for reference or troubleshooting
-   All scripts include detailed headers explaining their purpose and relevance
