## Project Spec v2 (Current Plan)

Overview

-   Goal: Convert AMASS `.npz` animations to GLB on a consistent SMPL‑H skeleton, frame 0 A‑pose, fixed bone lengths, correct scale/orientation, child cube included.
-   Reference: `A-Pose.FBX` defines desired bone lengths and A‑pose angles, but we remain SMPL‑H (52 joints). Extra FBX bones are ignored.

Guiding Principles

-   Treat FBX as a bone-length/pose reference only. Output skeleton is SMPL‑H.
-   Keep units consistent (m), armature at identity, glTF friendly.
-   Build in tiny, testable steps; each step exports viewable GLBs.

Milestones

M1 — Parity Export (DONE)

-   Implement pass‑through `.npz`→GLB export (matches original pipeline) with child cube and CLI ergonomics.
-   Acceptance: GLBs open in Blender; animation matches input FK; child cube present.
-   Tests: Compare frame positions vs FK (spot check), visual sanity.

M2 — Clean SMPL‑H Reference (NEW)

-   Objective: Build a clean SMPL‑H armature (52 joints) whose bone lengths and rest angles approximate the FBX A‑pose. Ignore FBX extra bones.

    Tasks

    -   Create explicit FBX→SMPL‑H name mapping (52 only; ignore twist/end/helper bones).
    -   Extract FBX A‑pose joint heads for mapped bones (object/world space at identity), convert cm→m.
    -   Compute `J_ABSOLUTE` (52×3) and `SMPL_OFFSETS` using the SMPL‑H tree.
    -   Generate `smplh_target.glb` armature from these values (no animation), with child cube.
    -   Add validation script to compare lengths vs FBX (tolerance ≤ 2 mm) and hierarchy correctness.

    Acceptance Criteria

    -   `smplh_target.glb` has exactly 52 bones with the SMPL‑H parent tree.
    -   Parent‑child distances match FBX (≤ 0.2 cm error).
    -   Armature at identity; units in meters; visible in front; child cube present.

    Testing

    -   Automated: length diff report per bone (GLB vs FBX sample) with pass/fail summary.
    -   Manual: load `A-Pose.FBX` + `smplh_target.glb` in Blender, verify size/orientation match and joint placement.

M3 — Retarget-on-Clean SMPL‑H (Incremental)

-   Objective: Drive the clean SMPL‑H with `.npz` animations while preserving consistent bone lengths and setting frame 0 to A‑pose.

    Tasks (iterative)

    -   Start from parity: reproduce `.npz` FK on clean SMPL‑H (no constraints mismatch).
    -   Add frame‑0 pose override to A‑pose with correct root translation.
    -   Address joint rotation mapping issues (basis/rest‑space alignment), validate on a few takes.

    Acceptance/Tests

    -   Frame 0 equals A‑pose (+ root trans), lengths preserved; visual sanity on 3+ datasets.

M4 — Validation & Tooling

-   CLI subcommands for: length check, frame‑0 check, FK diff, quick viewer export.
-   Compact reports (per‑bone errors, thresholds).

M5 — Documentation & Packaging

-   `retarget_usage.md` concise usage; examples for single file/dir; known constraints.
-   Minimal `requirements.txt` and README pointers.

Outputs

-   `target_reference.glb` (visual A‑pose reference)
-   `smplh_target.glb` (clean SMPL‑H reference)
-   Retargeted GLBs per input `.npz`
