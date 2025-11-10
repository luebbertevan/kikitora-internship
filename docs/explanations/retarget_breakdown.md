# retarget.py Breakdown

## Imports

-   numpy, bpy, argparse, mathutils.Vector, pathlib.Path, typing.Optional/List, numpy.typing.NDArray

## Core Data

-   SMPL_H_PARENTS (kinematic tree)
-   JOINT_NAMES (52 joint labels)
-   J_ABSOLUTE (T-pose joint positions)
-   SMPL_OFFSETS (relative offsets from J_ABSOLUTE)
-   J_ABSOLUTE_APOSE (A-pose joint positions from A-Pose.npz)

## Functions

-   axis_angle_to_rotation_matrix(axis_angle)
-   load_reference_pelvis()
-   align_root_to_reference(joint_positions, reference_pelvis)
		why does this Handle both single frame and multi-frame inputs?
-   forward_kinematics(poses, trans)
-   add_cube_and_parent(armature, cube_size, cube_location)
-   process_npz_file(npz_path, cube_size, cube_location, frame_limit)
-   find_npz_files(folder_path)
-   main()

## CLI Flags

-   --frame-limit, --cube-size, --cube-location, --limit, --output, --export-target-apose, --apose-path



blendre scene clean up bug
file batchig bug
bone scaling bug
added flags
use a pose j_absolutes for frame 0
use a pose for the empties
change constraint solver to use copy location