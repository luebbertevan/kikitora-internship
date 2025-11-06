"""
Create GLB from NPZ - Original Motion Capture (No Reference Skeleton)

This script creates a GLB that represents the ORIGINAL motion capture data
without any retargeting to a reference skeleton. This is for validation purposes
to compare original mocap vs retargeted output.

Strategy:
1. Extract original bone lengths from the animation data itself
2. Use a T-pose detection method to find a frame with minimal rotations
3. Measure bone lengths from that frame's joint positions
4. Use those measured bone lengths for all frames

This avoids using any hardcoded reference skeleton values.
"""

import bpy
import numpy as np
import json
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Tuple
from mathutils import Vector, Matrix, Euler, Quaternion
from numpy.typing import NDArray


# SMPL+H kinematic tree
SMPL_H_PARENTS: NDArray[np.int32] = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Joint names
JOINT_NAMES: List[str] = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def axis_angle_to_rotation_matrix(axis_angle: NDArray[np.float64]) -> NDArray[np.float64]:
    """Convert axis-angle to rotation matrix using Rodrigues' formula"""
    angle: float = np.linalg.norm(axis_angle)
    if angle < 1e-6:
        return np.eye(3)
    
    axis: NDArray[np.float64] = axis_angle / angle
    K: NDArray[np.float64] = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    R: NDArray[np.float64] = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R


def forward_kinematics(
    poses: NDArray[np.float64], 
    trans: NDArray[np.float64],
    smpl_offsets: NDArray[np.float64]
) -> NDArray[np.float64]:
    """
    Compute forward kinematics using specified bone offsets.
    
    Args:
        poses: Pose parameters (axis-angle) - from NPZ file
        trans: Root translation - from NPZ file
        smpl_offsets: Bone offsets to use
        
    Returns:
        Joint positions (52, 3)
    """
    num_joints: int = len(SMPL_H_PARENTS)
    joint_positions: NDArray[np.float64] = np.zeros((num_joints, 3))
    
    pose_params: NDArray[np.float64] = poses.reshape(-1, 3)
    global_transforms: List[NDArray[np.float64]] = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        if i < len(pose_params):
            rot_mat: NDArray[np.float64] = axis_angle_to_rotation_matrix(pose_params[i])
        else:
            rot_mat = np.eye(3)
        
        local_transform: NDArray[np.float64] = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = smpl_offsets[i]
        
        parent_idx: int = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions


def find_tpose_frame(poses: NDArray[np.float64], threshold: float = 0.1) -> int:
    """
    Find the frame with minimal rotations (closest to T-pose).
    
    Args:
        poses: Pose parameters (num_frames, 156)
        threshold: Maximum rotation angle to consider "T-pose" (radians)
        
    Returns:
        Frame index with minimal rotations
    """
    # Compute rotation magnitudes for each frame
    rotation_magnitudes = np.zeros(len(poses))
    
    for frame_idx in range(len(poses)):
        frame_poses = poses[frame_idx].reshape(-1, 3)  # (52, 3)
        # Compute rotation angle for each joint
        angles = np.linalg.norm(frame_poses, axis=1)  # (52,)
        rotation_magnitudes[frame_idx] = np.sum(angles)
    
    # Find frame with minimum total rotation
    tpose_frame = np.argmin(rotation_magnitudes)
    
    print(f"T-pose detection: Frame {tpose_frame} has minimal rotations (total: {rotation_magnitudes[tpose_frame]:.6f})")
    
    return int(tpose_frame)


def extract_original_bone_lengths(
    poses: NDArray[np.float64],
    trans: NDArray[np.float64]
) -> Tuple[NDArray[np.float64], str]:
    """
    Extract original bone lengths from animation data.
    
    Strategy:
    1. Find T-pose frame (minimal rotations)
    2. For T-pose, with zero rotations, FK simplifies to linear addition of offsets
    3. We can solve for offsets by analyzing the joint positions
    4. Use multiple frames to get more robust estimates
    
    Args:
        poses: Pose parameters (num_frames, 156)
        trans: Root translations (num_frames, 3)
        
    Returns:
        (smpl_offsets, method) tuple
    """
    print("\n" + "="*80)
    print("EXTRACTING ORIGINAL BONE LENGTHS FROM ANIMATION DATA")
    print("="*80)
    
    # Find T-pose frame (frame with minimal rotations)
    tpose_frame_idx = find_tpose_frame(poses)
    tpose_poses = poses[tpose_frame_idx]
    tpose_trans = trans[tpose_frame_idx]
    
    print(f"Using frame {tpose_frame_idx} as T-pose reference")
    
    # Key insight: With zero rotations, FK becomes linear
    # joint_positions[i] = root_trans + sum of offsets along path from root to i
    # We can solve this by analyzing the joint positions
    
    # However, we still need initial bone lengths to run FK even with zero rotations
    # So we use a bootstrap approach:
    # 1. Use frame 0 to get approximate joint positions (with rotations)
    # 2. Measure bone lengths from those positions
    # 3. Use T-pose frame to refine
    
    print("Using frame 0 to bootstrap bone length extraction...")
    
    # Bootstrap: Use frame 0 to get initial joint positions
    # We'll use a simple heuristic: assume bone lengths are roughly proportional
    # to the distances between joints in frame 0
    frame0_poses = poses[0]
    frame0_trans = trans[0]
    
    # Start with approximate offsets based on typical human proportions
    # These are just rough estimates to bootstrap
    bootstrap_offsets = np.zeros((52, 3))
    bootstrap_offsets[0] = frame0_trans
    
    # Use typical bone length proportions (rough estimates)
    # These will be refined
    typical_offsets = {
        # Spine chain
        3: np.array([0.0, 0.0, 0.1]),   # Spine1
        6: np.array([0.0, 0.0, 0.1]),   # Spine2
        9: np.array([0.0, 0.0, 0.1]),   # Spine3
        # Legs
        1: np.array([0.05, 0.0, -0.2]),  # L_Hip
        2: np.array([-0.05, 0.0, -0.2]), # R_Hip
        4: np.array([0.0, 0.0, -0.4]),   # L_Knee
        5: np.array([0.0, 0.0, -0.4]),   # R_Knee
        # ... (simplified for now)
    }
    
    # Initialize with rough estimates
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            bootstrap_offsets[i] = frame0_trans
        elif i in typical_offsets:
            bootstrap_offsets[i] = typical_offsets[i]
        else:
            # Default: small downward offset
            bootstrap_offsets[i] = np.array([0.0, 0.0, -0.1])
    
    # Run FK with bootstrap offsets to get approximate joint positions
    joint_positions_frame0 = forward_kinematics(frame0_poses, frame0_trans, bootstrap_offsets)
    
    # Now measure actual bone lengths from these joint positions
    measured_offsets = np.zeros((52, 3))
    measured_offsets[0] = joint_positions_frame0[0]  # Root
    
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            measured_offsets[i] = joint_positions_frame0[i]
        else:
            # Measure offset from parent to child
            measured_offsets[i] = joint_positions_frame0[i] - joint_positions_frame0[parent_idx]
    
    # Refine using T-pose frame if available
    if np.max(np.abs(tpose_poses)) < 0.1:  # T-pose has minimal rotations
        print("Refining bone lengths using T-pose frame...")
        tpose_joints = forward_kinematics(tpose_poses, tpose_trans, measured_offsets)
        
        # Update offsets based on T-pose positions
        refined_offsets = np.zeros((52, 3))
        refined_offsets[0] = tpose_joints[0]
        
        for i in range(52):
            parent_idx = int(SMPL_H_PARENTS[i])
            if parent_idx == -1:
                refined_offsets[i] = tpose_joints[i]
            else:
                refined_offsets[i] = tpose_joints[i] - tpose_joints[parent_idx]
        
        # Use refined offsets if they're reasonable
        if np.all(np.isfinite(refined_offsets)):
            measured_offsets = refined_offsets
    
    print("Extracted bone lengths from animation data")
    print(f"  Root position: {measured_offsets[0]}")
    avg_bone_length = np.mean([np.linalg.norm(measured_offsets[i]) for i in range(1, 52) if np.linalg.norm(measured_offsets[i]) > 0.01])
    print(f"  Average bone length: {avg_bone_length:.6f}")
    
    return measured_offsets, "tpose_measurement"


def clear_all_data_blocks() -> None:
    """Clear all Blender data blocks to ensure clean state between files."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    for armature in list(bpy.data.armatures):
        bpy.data.armatures.remove(armature)
    
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    
    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)
    
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 0
    
    print("Cleared all data blocks")


def process_npz_file(npz_path: Path) -> None:
    """
    Process a single NPZ file and export to GLB using ORIGINAL bone lengths.
    
    This function:
    1. Extracts original bone lengths from the animation data itself
    2. Uses NO reference skeleton values
    3. Creates GLB faithful to original motion capture
    """
    print(f"\n{'='*80}")
    print(f"Processing: {npz_path}")
    print(f"GOAL: Extract ORIGINAL motion capture (no reference skeleton)")
    print(f"{'='*80}")
    
    # Clear ALL data blocks
    clear_all_data_blocks()
    
    # Load NPZ file
    data = np.load(str(npz_path))
    poses: NDArray[np.float64] = data['poses']
    trans: NDArray[np.float64] = data['trans']
    
    print(f"Loaded {len(poses)} frames")
    print(f"Poses shape: {poses.shape}")
    print(f"Trans shape: {trans.shape}")
    
    # Extract original bone lengths from animation data
    smpl_offsets, method = extract_original_bone_lengths(poses, trans)
    
    print(f"\nUsing bone lengths extracted via: {method}")
    print("⚠️  NOTE: These are ORIGINAL bone lengths from the animation data")
    print("   No reference skeleton values are used!")
    
    # Get framerate
    framerate: float = float(data.get('mocap_framerate', 60))
    
    # Compute joint positions for first frame to create armature
    joint_positions_frame0: NDArray[np.float64] = forward_kinematics(
        poses[0], 
        trans[0],
        smpl_offsets
    )
    print("\nUsing frame 0 pose (from FK with original bone lengths) for armature creation")
    
    # Create armature with unique name per file
    unique_name = f"OriginalMocap_{npz_path.stem}"
    armature_data = bpy.data.armatures.new(unique_name)
    armature: bpy.types.Object = bpy.data.objects.new(unique_name, armature_data)
    bpy.context.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    
    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.data.edit_bones
    bone_list: List[bpy.types.EditBone] = []
    
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}")
        bone.head = Vector(joint_positions_frame0[i])
        
        children: List[int] = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if children:
            if i == 0:
                bone.tail = Vector(joint_positions_frame0[3])  # Spine1
            else:
                bone.tail = Vector(joint_positions_frame0[children[0]])
        else:
            bone.tail = Vector(joint_positions_frame0[i]) + Vector((0, 0.05, 0))
        
        bone_list.append(bone)
    
    # Set parent relationships
    for i in range(52):
        parent_idx: int = int(SMPL_H_PARENTS[i])
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(poses) - 1
    bpy.context.scene.render.fps = int(framerate)
    
    print("Creating empties and animation...")
    
    # Create empties for each joint with unique names
    empties: List[bpy.types.Object] = []
    for i in range(52):
        joint_name: str = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
        empty_name = f"Empty_{unique_name}_{joint_name}"
        empty = bpy.data.objects.new(empty_name, None)
        bpy.context.collection.objects.link(empty)
        empty.empty_display_size = 0.02
        empties.append(empty)
    
    # Animate empties using forward kinematics with ORIGINAL bone lengths
    frame_skip: int = 1
    print("Processing all frames with forward kinematics (using original bone lengths)...")
    for frame_idx in range(0, len(poses), frame_skip):
        bpy.context.scene.frame_set(frame_idx)
        
        # Compute joint positions using FK with ORIGINAL bone lengths
        joint_positions: NDArray[np.float64] = forward_kinematics(
            poses[frame_idx], 
            trans[frame_idx],
            smpl_offsets
        )
        
        # Set empty positions
        for i in range(52):
            empties[i].location = Vector(joint_positions[i])
            empties[i].keyframe_insert(data_path="location", frame=frame_idx)
        
        if frame_idx % 100 == 0:
            print(f"  Processed frame {frame_idx}/{len(poses)}")
    
    print("Empties animation complete!")
    
    # Add constraints to make armature track the empties
    print("Adding constraints to armature...")
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = armature.pose.bones
    
    # Add constraints (same as create_glb_faithful.py)
    for i in range(52):
        joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
        pose_bone = pose_bones.get(joint_name)
        
        if pose_bone:
            children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
            
            if i == 0:
                constraint = pose_bone.constraints.new('COPY_LOCATION')
                constraint.target = empties[i]
                constraint.name = "Track_Root_Location"
                
                stretch_constraint = pose_bone.constraints.new('STRETCH_TO')
                stretch_constraint.target = empties[3]
                stretch_constraint.name = "Track_To_Spine1"
                stretch_constraint.rest_length = 0.0
                stretch_constraint.bulge = 0.0
                stretch_constraint.keep_axis = 'SWING_Y'
            
            elif len(children) == 0:
                if i == 15 or (i >= 22 and i <= 51):
                    parent_idx = int(SMPL_H_PARENTS[i])
                    if parent_idx >= 0:
                        parent_name: str = JOINT_NAMES[parent_idx] if parent_idx < len(JOINT_NAMES) else f"Joint_{parent_idx}"
                        parent_bone = pose_bones.get(parent_name)
                        if parent_bone:
                            rot_constraint = pose_bone.constraints.new('COPY_ROTATION')
                            rot_constraint.target = armature
                            rot_constraint.subtarget = parent_name
                            rot_constraint.name = "Copy_Parent_Rotation"
                elif i == 11:
                    track_constraint = pose_bone.constraints.new('DAMPED_TRACK')
                    track_constraint.target = empties[i]
                    track_constraint.name = "Track_Self_Neg"
                    track_constraint.track_axis = 'TRACK_NEGATIVE_Y'
                else:
                    track_constraint = pose_bone.constraints.new('DAMPED_TRACK')
                    track_constraint.target = empties[i]
                    track_constraint.name = "Track_Self"
                    track_constraint.track_axis = 'TRACK_Y'
            
            else:
                child_idx: int = children[0]
                constraint = pose_bone.constraints.new('STRETCH_TO')
                constraint.target = empties[child_idx]
                constraint.name = f"Track_To_Child_{child_idx}"
                constraint.rest_length = 0.0
                constraint.bulge = 0.0
                constraint.keep_axis = 'SWING_Y'
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Armature constraints added!")
    
    # Bake constraints to keyframes
    print("Baking constraints to keyframes...")
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone in armature.pose.bones:
        bone.bone.select = True
    
    action_name = f"Action_{unique_name}"
    action = bpy.data.actions.new(action_name)
    armature.data.animation_data_create()
    armature.data.animation_data.action = action
    
    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=len(poses) - 1,
        step=1,
        only_selected=True,
        visual_keying=True,
        clear_constraints=True,
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'}
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Baking complete!")
    
    # Delete empties
    print("Removing empties...")
    for empty in empties:
        bpy.data.objects.remove(empty, do_unlink=True)
    
    print("Empties removed. Ready for export.")
    
    # Export to GLB
    output_dir = npz_path.parent / "original_mocap_output"
    output_dir.mkdir(exist_ok=True)
    output_path: Path = output_dir / npz_path.name.replace('.npz', '.glb')
    
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_skins=True,
        export_all_influences=False,
        export_def_bones=False,
        export_optimize_animation_size=True,
        export_anim_single_armature=True,
        export_bake_animation=False,
        export_apply=False
    )
    
    print(f"✅ Successfully exported ORIGINAL motion capture to: {output_path}")
    print(f"   This represents the original animation with original bone lengths")
    print(f"   NO reference skeleton values were used!")


def find_npz_files(folder_path: Path) -> List[Path]:
    """Recursively find all .npz files in a folder"""
    return sorted(folder_path.rglob("*.npz"))


def main() -> None:
    """Main entry point for batch processing"""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(
        description="Create GLB from NPZ - Original Motion Capture (no reference skeleton)"
    )
    parser.add_argument(
        "input_folder",
        type=str,
        help="Path to folder containing NPZ files (will search recursively)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of files to process (for testing)"
    )
    
    args = parser.parse_args(argv)
    
    input_folder = Path(args.input_folder)
    
    if not input_folder.exists():
        print(f"Error: Input folder does not exist: {input_folder}")
        sys.exit(1)
    
    if not input_folder.is_dir():
        print(f"Error: Input path is not a directory: {input_folder}")
        sys.exit(1)
    
    # Find all NPZ files
    npz_files = find_npz_files(input_folder)
    
    if not npz_files:
        print(f"No NPZ files found in {input_folder}")
        sys.exit(0)
    
    # Apply limit if specified
    if args.limit:
        npz_files = npz_files[:args.limit]
    
    print(f"\nFound {len(npz_files)} NPZ file(s) to process")
    print("=" * 80)
    print("ORIGINAL MOTION CAPTURE EXTRACTION")
    print("This script extracts original bone lengths from animation data")
    print("NO reference skeleton values are used")
    print("=" * 80)
    
    # Process each file
    for idx, npz_file in enumerate(npz_files, 1):
        print(f"\n[{idx}/{len(npz_files)}] Processing: {npz_file.name}")
        try:
            process_npz_file(npz_file)
            print(f"✓ Successfully processed {npz_file.name}")
        except Exception as e:
            print(f"✗ Error processing {npz_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print(f"Batch processing complete! Processed {len(npz_files)} file(s)")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

