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


Total frames: Now len(poses) + 1 (572 → 573 for CartWheel)




Voxel captureing on a motion capture stage. TRanslating the mo cap to unreal and training the model in unreal. to understand oclusion we know exactly where the limbs are in the space and so you can score the model acuratly and have precisiion control and motion capture is time consumeing and expencive. then we can train the model on video later against motion capture to refine to video. 



why do we need to weight paint the mesh if you always use the standared a pose? is this becuase the smpl-h is going to be precedurlay modified for training on? 



what is the difference with the create_glb_from_npz and the original retarget.py.
create: uses empties and contraints 

there is a important step bwtwe
retarget creates armature from the old t-pose using joint absolute positions.

What was wrong with the original retargeter/create_glb_from_npz? 
(besides the scene clearing problem)

feet on ground
interacting with something(holding something)
least complex ju
feet on ground
hands also on ground
common approach (oppisite of fk)

positions of the hands!! in space 
preserver the character of the animtation
feet on ground


Do we need the betas (bone length presets) from the mo cap npz? probably not

My mental model is to just sub in the bone lengths of the reference skeleton do fk and bake into glb and it seems that is the approach in the original retargeter. what is my mental model missing? where is the problem? create_glb seems to do this but just with frame_0

what is your recomendation for the first step? frame 0 a pose? or retargeting bones?

Also conceptul clarification. if a differently preportioned person is doing an animation wont the standardizatino warp the skeleton animation? A shorter person looks different doing a cartwheel then a taller person different weight shift and physics

what is the anticipated problem that you mentioned.



Why glb? 


can 





create_glb_from_npz.py:
Creates armature from frame 0 pose (actual animation frame)
is this using the betas? NO where in the code is this happening?
# Line 62-68 - Hardcoded reference skeleton
SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]



more questions



is using the rokoko plugin a valid strategy?

How do we find a faithful representation of the original motion capture?
Is there enough information in the original npz to recreate the original motion capture and preportions.
 What does 'faithful' even mean? surely the original bone lengths are encoded somewhere in the npz. 
Ai is struggling with this. thinks that we cannot find the bone lengths. 
If the original animation uses a different coordinate system (e.g., Y-up) or different bone directions, the skeleton is wrong, leading to incorrect orientation and movement.
do we do this already in create glb from npz? i think not


from my research it seems incredibly important for retargeting the the original and the target skeleton be in as similiar as pose as possible with as similair as skeleton as possible
problems: no way to get the original animation skeleton
also my a pose was based on the fbx and is preportionally quite different

no sdk for rokoko. everything happens in blender.
The retargeting features are oriented toward the UI/apps (Studio/Blender/other 3D tools) rather than headless automation.
Is the ai halucinating bpy.ops.rokoko.retarget()

help(bpy.ops.rsl.retarget_animation)
Help on _BPyOpsSubModOp in module bpy.ops:

bpy.ops.rsl.retarget_animation()
    bpy.ops.rsl.retarget_animation()
    Retargets the animation from the source armature to the target armature

no docs. how do I learn how to use this?

what is going on with the glb shape distortion? it is stretching and distorting with movement

