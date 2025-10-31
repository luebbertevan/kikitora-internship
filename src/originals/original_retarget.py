"""
SMPL+H Animation Retargeting to Consistent T-Pose Skeleton
Computes bone rotations from joint positions to maintain consistent bone lengths
"""

import bpy
import numpy as np
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from mathutils import Vector, Quaternion
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

# SMPL offsets
J_ABSOLUTE: NDArray[np.float64] = np.array([
    [-0.001795, -0.223333, 0.028219], [0.067725, -0.314740, 0.021404],
    [-0.069466, -0.313855, 0.023899], [-0.004328, -0.114370, 0.001523],
    [0.102001, -0.689938, 0.016908], [-0.107756, -0.696424, 0.015049],
    [0.001159, 0.020810, 0.002615], [0.088406, -1.087899, -0.026785],
    [-0.091982, -1.094839, -0.027263], [0.002616, 0.073732, 0.028040],
    [0.114764, -1.143690, 0.092503], [-0.117354, -1.142983, 0.096085],
    [-0.000162, 0.287603, -0.014817], [0.081461, 0.195482, -0.006050],
    [-0.079143, 0.192565, -0.010575], [0.004990, 0.352572, 0.036532],
    [0.172438, 0.225951, -0.014918], [-0.175155, 0.225116, -0.019719],
    [0.432050, 0.213179, -0.042374], [-0.428897, 0.211787, -0.041119],
    [0.681284, 0.222165, -0.043545], [-0.684196, 0.219560, -0.046679],
    [0.783767, 0.213183, -0.022054], [0.815568, 0.216115, -0.018788],
    [0.837963, 0.214387, -0.018140], [0.791063, 0.216050, -0.044867],
    [0.821578, 0.217270, -0.048936], [0.845128, 0.215785, -0.052425],
    [0.765890, 0.208316, -0.084165], [0.781693, 0.207917, -0.094992],
    [0.797572, 0.206667, -0.105123], [0.779095, 0.213415, -0.067855],
    [0.806930, 0.215059, -0.072228], [0.829592, 0.213672, -0.078705],
    [0.723217, 0.202218, -0.017008], [0.740918, 0.203986, 0.007192],
    [0.762150, 0.200379, 0.022060], [-0.783494, 0.210911, -0.022044],
    [-0.815675, 0.213810, -0.019676], [-0.837971, 0.212032, -0.020059],
    [-0.791352, 0.214082, -0.045896], [-0.821700, 0.215536, -0.050057],
    [-0.844837, 0.214110, -0.053971], [-0.767226, 0.205917, -0.086044],
    [-0.782858, 0.205594, -0.097170], [-0.798573, 0.204555, -0.107284],
    [-0.779985, 0.211294, -0.069581], [-0.807581, 0.213016, -0.074152],
    [-0.829999, 0.211622, -0.081116], [-0.722013, 0.199415, -0.016553],
    [-0.739452, 0.200249, 0.007932], [-0.760794, 0.195263, 0.022366],
])

SMPL_OFFSETS: NDArray[np.float64] = np.zeros((52, 3))
for i in range(52):
    parent_idx = SMPL_H_PARENTS[i]
    if parent_idx == -1:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i]
    else:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]


def axis_angle_to_rotation_matrix(axis_angle: NDArray[np.float64]) -> NDArray[np.float64]:
    """Convert axis-angle to rotation matrix"""
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


def forward_kinematics(poses: NDArray[np.float64], trans: NDArray[np.float64]) -> NDArray[np.float64]:
    """Compute forward kinematics"""
    num_joints: int = len(SMPL_H_PARENTS)
    joint_positions: NDArray[np.float64] = np.zeros((num_joints, 3))
    pose_params: NDArray[np.float64] = poses.reshape(-1, 3)
    global_transforms: List[NDArray[np.float64]] = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        rot_mat = axis_angle_to_rotation_matrix(pose_params[i]) if i < len(pose_params) else np.eye(3)
        local_transform: NDArray[np.float64] = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = SMPL_OFFSETS[i]
        
        parent_idx: int = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions


def create_tpose_armature(name: str = "SMPLH_Armature") -> bpy.types.Object:
    """
    Create T-pose armature with consistent bone lengths
    
    Returns:
        Created armature object with bone length and rest direction info
    """
    # Use T-pose (zero poses)
    zero_poses = np.zeros((52, 3), dtype=np.float64).flatten()
    zero_trans = np.zeros(3, dtype=np.float64)
    tpose_joints = forward_kinematics(zero_poses, zero_trans)
    
    # Create armature
    armature = bpy.data.armatures.new(name)
    armature_obj = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.edit_bones
    
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i])
        bone.head = Vector(tpose_joints[i])
        
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if children:
            if i == 0:
                bone.tail = Vector(tpose_joints[3])  # Spine1
            else:
                bone.tail = Vector(tpose_joints[children[0]])
        else:
            bone.tail = Vector(tpose_joints[i]) + Vector((0, 0.05, 0))
    
    # Set parent relationships
    bone_list = list(edit_bones)
    for i, parent_idx in enumerate(SMPL_H_PARENTS):
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Created T-pose armature with {len(bone_list)} bones")
    return armature_obj


def compute_bone_rotation(bone_head: Vector, bone_tail: Vector, target_pos: Vector) -> Quaternion:
    """
    Compute rotation needed to make bone point from head toward target
    
    Args:
        bone_head: Bone head position in rest pose
        bone_tail: Bone tail position in rest pose  
        target_pos: Target position to point toward
        
    Returns:
        Quaternion rotation
    """
    # Rest direction (bone's default orientation)
    rest_dir = (bone_tail - bone_head).normalized()
    
    # Target direction
    target_dir = (target_pos - bone_head).normalized()
    
    # Compute rotation from rest to target
    rotation = rest_dir.rotation_difference(target_dir)
    
    return rotation


def retarget_animation(
    armature_obj: bpy.types.Object,
    poses: NDArray[np.float64],
    trans: NDArray[np.float64]
) -> None:
    """
    Retarget animation by computing bone rotations from joint positions
    
    Args:
        armature_obj: T-pose armature
        poses: Animation poses (num_frames, 156)
        trans: Animation translations (num_frames, 3)
    """
    num_frames = len(poses)
    
    # Get T-pose joint positions for reference
    zero_poses = np.zeros((52, 3), dtype=np.float64).flatten()
    zero_trans = np.zeros(3, dtype=np.float64)
    tpose_joints = forward_kinematics(zero_poses, zero_trans)
    
    # Store bone rest info
    bone_info = []
    for i in range(52):
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        child_idx = children[0] if children else None
        if i == 0 and children:
            child_idx = 3  # Pelvis points to Spine1
        
        bone_info.append({
            'head': Vector(tpose_joints[i]),
            'tail': Vector(tpose_joints[child_idx]) if child_idx is not None else None,
            'child_idx': child_idx
        })
    
    # Animate
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    print(f"Retargeting {num_frames} frames...")
    
    for frame_idx in range(num_frames):
        if frame_idx % 100 == 0:
            print(f"  Frame {frame_idx}/{num_frames}")
        
        bpy.context.scene.frame_set(frame_idx)
        
        # Compute FK positions for this frame
        frame_joints = forward_kinematics(poses[frame_idx], trans[frame_idx])
        
        # Apply rotations to each bone
        for i in range(52):
            pose_bone = armature_obj.pose.bones[JOINT_NAMES[i]]
            
            # Root gets translation
            if i == 0:
                pose_bone.location = Vector(frame_joints[i])
                pose_bone.keyframe_insert(data_path="location", frame=frame_idx)
            else:
                pose_bone.location = Vector((0, 0, 0))
            
            # Compute rotation
            info = bone_info[i]
            if info['child_idx'] is not None:
                target_pos = Vector(frame_joints[info['child_idx']])
                rotation = compute_bone_rotation(info['head'], info['tail'], target_pos)
                
                pose_bone.rotation_mode = 'QUATERNION'
                pose_bone.rotation_quaternion = rotation
                pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_idx)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Retargeting complete!")


def process_npz_file(npz_path: Path) -> None:
    """Process NPZ file with retargeting"""
    print(f"\n{'='*80}")
    print(f"Processing: {npz_path.name}")
    print(f"{'='*80}")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Load NPZ
    data = np.load(str(npz_path))
    poses: NDArray[np.float64] = data['poses']
    trans: NDArray[np.float64] = data['trans']
    
    print(f"Loaded {len(poses)} frames")
    
    # Create T-pose armature
    armature = create_tpose_armature()
    
    # Set frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(poses) - 1
    
    # Retarget animation
    retarget_animation(armature, poses, trans)
    
    # Export
    output_path = npz_path.with_suffix('.glb')
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_animations=True
    )
    
    print(f"✓ Exported to: {output_path}")


def main() -> None:
    """Main entry point"""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Retarget SMPL+H animations to consistent T-pose skeleton")
    parser.add_argument("input_folder", type=str, help="Folder containing NPZ files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files")
    
    args = parser.parse_args(argv)
    
    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        print(f"Error: Folder not found: {input_folder}")
        sys.exit(1)
    
    npz_files = sorted(input_folder.rglob("*.npz"))
    if args.limit:
        npz_files = npz_files[:args.limit]
    
    print(f"Found {len(npz_files)} NPZ file(s)")
    
    for idx, npz_file in enumerate(npz_files, 1):
        print(f"\n[{idx}/{len(npz_files)}]")
        try:
            process_npz_file(npz_file)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()