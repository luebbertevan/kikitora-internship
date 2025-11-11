# AMASS Armature Retargeting Project

## Project Objective

-   Deliver a retargeting script that maps AMASS motion-capture animations from NPZ files onto an SMPL-H skeleton with standardized bone lengths, and produces clean GLB animations with a consistent frame-0 A-pose.

## Technical Constraints

-   AMASS NPZ files store each pose as 52 axis-angle rotations. For each frame we first convert these to rotation matrices, propagate them through the SMPL-H hierarchy via forward kinematics, and only then can we feed Blender the resulting joint transforms. The extra FK step is unavoidable because the data never contains ready-to-use joint matrices.
-   AMASS data omits bone lengths because the research targets dynamic body meshes/blend shapes. Without bone lengths there is no quantitative method to confirm the retargeted animation is faithful to the original animations and verification is limited to visual inspection.
-   Conventional retargeting libraries expect both source and target armatures. AMASS provides no bones to reconstruct a source armature, so tools like Rokoko Studio Live cannot be used.

## Solution Overview

-   Start from a user-authored A-pose exported from Blender (`A-Pose.npz`), align frame 0 empties to those positions, then run forward kinematics with custom SMPL-H T-pose offsets to produce per-frame joint transforms.
-   Apply lightweight constraints (copy-location/damped-track) so the armature follows the FK-driven empties, bake the result, and export each animation as a clean GLB with a consistent A-pose first frame.

## Retargeting Features

### Consistent Skeleton Retargeting

-   Forward kinematics always uses custom T-pose offsets embedded in `retarget.py`. This ensures every animation is mapped onto the same SMPL-H-style joint orientations and bone lengths regardless of the source armature. AMASS mocap data expects this orientation, so we preserve the intended joint rotations without needing to reconstruct the source armature.

### Frame-0 Preparation from A-pose NPZ

-   `A-Pose.npz` supplies world-space joint positions, which are loaded at startup, aligned at frame 0, and baked into the empties before FK is run on the subsequent frames. This guarantees every exported animation begins with the same A-pose on frame 0. Users can override the default by passing `--apose-path` to point at another NPZ file if a different frame 0 pose is desired.

### Blender → NPZ A-pose Export

-   `export_apose_from_blender.py` reads the active Blender armature in Edit Mode (rest pose), gathers each bone’s world-space head position, and writes the 52 × 3 array to an NPZ as `J_ABSOLUTE`. The script produces a custom `A-Pose.npz` that can be used in `retarget.py` using `--apose-path` for instant iteration without hand-editing numeric arrays.

### Scene Isolation & Batching

-   Clears Blender meshes, actions, and armatures before each file. This prevents scene cross-contamination.

### Constraint Strategy

-   Replaced the previous `STRETCH_TO` setup with `COPY_LOCATION` (and damped-track where orientation is needed) so bones follow the FK-driven empties without changing their length. This keeps motion faithful while eliminating the joint scaling and distortion.

### Parameterization & CLI Enhancements

-   Added flags for frame limiting, cube sizing/location, custom A-pose paths, and a mode to export the target A-pose GLB.

## Potential Enhancements

-   Investigate estimating bone lengths from AMASS betas via the original scripts. Success would enable comparison against mocap proportions and unlock conventional retarget libraries.
-   Revisit broader options such as reconstructing a source skeleton from mocap or integrating third-party retarget frameworks once reliable bone lengths are available.
-   Introduce optional IK passes (feet, hands) to improve contact fidelity.

## Usage

### Running `retarget.py`

-   Input: a directory containing AMASS-format NPZ files. The script processes files recursively, clearing Blender’s scene per file and writing the outputs where you specify.
-   Flags:
    -   `--limit N` limits how many NPZs are processed from the directory.
    -   `--frame-limit F` trims each clip to the first `F` frames.
    -   `--apose-path path/to/A-Pose.npz` loads a custom A-pose (defaults to the `A-Pose.npz` in the same directory as `retarget.py`).
    -   `--cube-size`, `--cube-location` adjust the helper cube; `--output DIR` redirects GLBs.
-   Example 1 (basic): `blender --background --python retarget.py -- data/amass_subset`
-   Example 2 (with flags): `blender --background --python retarget.py -- data/amass_subset --limit 2 --frame-limit 300 --apose-path data/reference/custom_apose.npz --output data/exports`

### Running `export_apose_from_blender.py`

-   Input: a `.blend` file whose armature pose has been applied to the rest pose.
-   The script samples each bone’s world-space head position and saves them under `J_ABSOLUTE` in the output NPZ; use that file with `retarget.py --apose-path`.
-   Example 1: `blender AposeRig.blend --background --python export_apose_from_blender.py -- data/reference/A-Pose.npz`

## Outputs

-   Each processed NPZ produces a GLB with the suffix `_retargeted.glb`. When `--output` is provided, GLBs are written to that directory using the same naming convention.
-   All exports use the SMPL-H-style bone lengths defined in `retarget.py`, and frame 0 is guaranteed to match the supplied A-pose reference.
