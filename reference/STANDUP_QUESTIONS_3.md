# Standup Questions 3 - Rotation Alignment

## Problem

M3 currently only translates animations to start at the same position. Each animation maintains its **original facing direction** (some face +X, others face +Y).

### Why Rotation Alignment is Difficult

The pelvis rotation alone doesn't tell me which direction is "front" because:

-   The pelvis is roughly spherical - it doesn't have an inherent "front" direction
-   The rotation is relative to an unknown starting orientation

To determine "front," I need to:

1. Look at hip positions → tells me "left" and "right"
2. Look at spine position → tells me "up"
3. Compute "front" as perpendicular to both (cross product)

When I tried to add rotation standardization, outputs were upside down or incorrectly oriented due to coordinate system issues I cannot debug without visual feedback.

## Questions

**Q1**: Do all animations need to face the same direction as the reference? Or is it acceptable for them to keep their original orientations as long as they start at the same position?

**Q2**: If rotation IS required - can you provide visual debugging feedback (screenshots/screen recordings of the incorrect outputs in Blender)?
