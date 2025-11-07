# Stretch Constraint Bug

## Summary

When we switched the retargeting pipeline to pin frame 0 empties directly to the Blender A‑pose joint positions, the armature constraints—specifically the `STRETCH_TO` constraints used for bones that have children—began scaling the bones. The constraint tries to make the bone’s tail reach its target, and if the empties are farther apart than the original T‑pose offsets, Blender stretches the bone (changes scale). Because Blender bakes those constraints, frame 0 appears distorted (stretched limbs), and fast-moving frames later in the animation also look scaled or rubbery when pose-to-pose distances differ from the original rest lengths.

## Root Cause

-   The armature was built assuming SMPL T‑pose bone lengths (`SMPL_OFFSETS`).
-   Empties now get positioned from two different sources:
    -   Frame 0: absolute Blender A‑pose positions (lengths differ from T-pose).
    -   Frames 1+: FK positions based on T‑pose offsets plus mocap rotations (and previously an extra translation offset).
-   `STRETCH_TO` modifies bone scale to match the distance to the target. When the empties’ separation doesn’t equal the rest offsets, the constraint stretches. This happens especially in frame 0 and during fast motion when the mocap FK momentarily produces very different distances.

## Symptoms

-   Frame 0 appears wildly scaled—limbs elongated or compressed.
-   Subsequent frames show noticeable scaling artifacts, most obvious in fast-moving sections.
-   After baking, these scale changes become permanent in the GLB output.

## Mitigation Ideas

1. **Keep pipeline consistent**: ensure the empties’ spacing matches the rest offsets for every frame. For example, adjust root translation/mocap `trans` so FK produces the A‑pose on frame 0 instead of overriding empties.
2. **Change constraints**: replace `STRETCH_TO` with constraints that only rotate (e.g., `DAMPED_TRACK` + `COPY_LOCATION`, or add drivers) so bone length is preserved.
3. **Bake A‑pose differently**: bake the A‑pose into the armature without using constraints that modify scale, then apply mocap from frame 1 onwards.

At present, option 2 is the safest fix for the scaling bug: switch away from `STRETCH_TO` so bones do not stretch regardless of empty positions.
