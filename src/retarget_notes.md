# retarget.md notes


## Frame 0 (A-pose) → Frame 1 (Original Animation)
Current pipeline:
1. Compute FK for frame N → get joint positions.
2. Place empties at those positions.
3. Constraints align bones to the empties → rotations result implicitly.
For M4:
- Frame 0: Override joint positions to reference A-pose positions.
- Frame 1: Use FK from poses[1] → joint positions naturally transition from A-pose to frame 1.
- The constraints smoothly interpolate bone orientations between frames.


What’s inside the .npz files?

.npz (or .npy) are NumPy array files — basically raw data containers.
In your case (AMASS dataset), they store joint positions and sometimes orientations per frame.

A simplified view might look like this:

Data key	Shape	Meaning
poses	(n_frames, 156)	SMPL joint angles (rotations for each joint)
trans	(n_frames, 3)	Global translation of the body
betas	(10,)	Body shape parameters
gender	string	male/female
(optional) joint_positions	(n_frames, n_joints, 3)	World-space XYZ joint coordinates

1. Empties (a.k.a. Nulls or Helpers)

Think of an Empty as an invisible reference point in 3D space.

It has location, rotation, and scale, but no mesh — you can’t see it when rendering.

It’s often used as a marker or target.

In your project:

Each Empty represents a joint position from the motion-capture data (the .npz files).

For example, the "LeftHand" empty might move around in space following the mocap coordinates for that joint.

So, empties = motion data markers.
They don’t deform the model; they just show where something should be.

🟨 2. Reference Positions

“Reference positions” just means the positions your bones or joints should match.

Example:

You have a skeleton (SMPL-H armature).

You have mocap data giving you joint coordinates for each frame.

The empties show those coordinates.

At any given frame, you can look at all the empties and say:

“Okay, this is where each joint should be at this moment.”

That’s your reference — your ground truth motion.

🟩 3. Constraints (the “rules” that link things)

Constraints are Blender’s way of telling one object how to behave based on another object.

Here are a few common ones you’ll see:

Constraint	What it does	Example
Copy Location	Moves one object to the position of another	Bone moves wherever its corresponding empty goes
Track To	Rotates one object to face another	A bone always points toward its empty
Copy Rotation	Makes one object copy another’s orientation	A bone’s rotation matches the empty’s
IK (Inverse Kinematics)	Moves an entire chain of bones to reach a target	A hand bone moves and the arm adjusts automatically

In your pipeline, constraints are used to make bones follow empties — so the skeleton moves like the mocap data describes.

🟥 4. Baking (making motion permanent)

“Baking” means converting indirect motion (from constraints) into direct keyframes.

Before baking:

The bone’s position is determined by a constraint.

If you delete the constraint, the motion disappears.

After baking:

Blender calculates what the bone’s position would have been at every frame, and saves that as actual keyframes (rotation, location, etc.).

Then you can safely delete the constraints — the motion stays!

So you:

Set up constraints (bones follow empties).

Bake the animation.

Remove constraints — animation is now “real.”

🧭 Putting It Together in Your Project

Your pipeline roughly looks like this:

Step	Action	Why
1	Load .npz joint data → create empties	Each empty shows where a joint is in each frame
2	Add constraints to bones (point toward / move with empties)	Makes the SMPL-H skeleton follow the empties
3	Bake the animation	Turns the constraint-based movement into real keyframes
4	Remove constraints	The skeleton keeps the animation
5	(Frame 0 special case) Manually set bones to A-pose	Ensures consistent rest pose
💡 Quick Analogy

Imagine a dance rehearsal:

The empties are markers on the floor showing where dancers should go.

The constraints are the choreographer’s instructions saying “follow the marker.”

The baking is like recording the final performance so the choreographer can leave — the moves are now permanent.

The reference positions are just the correct stage spots (where each dancer should stand).