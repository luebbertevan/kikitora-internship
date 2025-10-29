"""
SMPL+H Animation Retargeting to Consistent Target Skeleton
Computes bone rotations from joint positions to maintain consistent bone lengths.
Default target is A-pose, but can be customized via target_reference.npz
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

# Target skeleton data (loaded from target_reference.npz, defaults to A-pose)
# Can be reloaded via load_target_skeleton() to use a custom target
J_ABSOLUTE: NDArray[np.float64]
SMPL_OFFSETS: NDArray[np.float64]


def load_target_skeleton(target_path: Optional[Path] = None) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Load target skeleton reference from .npz file
    
    Args:
        target_path: Path to target reference .npz file. If None, uses default target_reference.npz 
                     in same directory as this script. The .npz must contain J_ABSOLUTE and SMPL_OFFSETS
                     for 52 SMPL-H joints.
        
    Returns:
        Tuple of (J_ABSOLUTE, SMPL_OFFSETS) defining the target skeleton pose
        
    Raises:
        FileNotFoundError: If target file doesn't exist
        KeyError: If required keys are missing
    """
    if target_path is None:
        # Default to target_reference.npz in same directory as this script
        target_path = Path(__file__).parent / "target_reference.npz"
    
    if not target_path.exists():
        raise FileNotFoundError(
            f"Target reference skeleton not found: {target_path}\n"
            f"Provide a .npz file with J_ABSOLUTE and SMPL_OFFSETS arrays, or use default A-pose values."
        )
    
    data = np.load(target_path)
    
    if 'J_ABSOLUTE' not in data:
        raise KeyError(f"Missing 'J_ABSOLUTE' in {target_path}")
    if 'SMPL_OFFSETS' not in data:
        raise KeyError(f"Missing 'SMPL_OFFSETS' in {target_path}")
    
    J_abs = data['J_ABSOLUTE'].astype(np.float64)
    offsets = data['SMPL_OFFSETS'].astype(np.float64)
    
    if J_abs.shape != (52, 3):
        raise ValueError(f"J_ABSOLUTE shape {J_abs.shape} != (52, 3)")
    if offsets.shape != (52, 3):
        raise ValueError(f"SMPL_OFFSETS shape {offsets.shape} != (52, 3)")
    
    print(f"Loaded target skeleton from: {target_path}")
    return J_abs, offsets


# Load target skeleton on import (default is A-pose)
try:
    J_ABSOLUTE, SMPL_OFFSETS = load_target_skeleton()
except Exception:
    # Missing/invalid target reference is expected in production; silently use defaults
    print("Using default target (A-pose) values")
    # Default fallback: A-pose reference values
    J_ABSOLUTE = np.array([
        [-0.000000, -0.000000, 95.636375],
        [9.724527, 0.660794, 93.460052],
        [-9.724524, 0.660784, 93.460037],
        [0.000126, -0.956927, 103.547203],
        [13.950833, -0.007977, 52.078457],
        [-13.944020, -0.008468, 52.077759],
        [0.000127, -2.365802, 107.423111],
        [18.257202, 4.773808, 7.635051],
        [-18.260323, 4.769928, 7.635861],
        [0.000123, -1.277968, 120.297935],
        [20.961849, -9.616167, 3.404962],
        [-20.956547, -9.623543, 3.413755],
        [0.000234, 3.741064, 151.219604],
        [6.068380, 2.859792, 143.648727],
        [-6.068113, 2.859793, 143.648758],
        [0.000434, 2.432668, 159.778992],
        [17.985998, 6.678337, 142.715332],
        [-17.988436, 6.679042, 142.733200],
        [35.942127, 8.611701, 121.508385],
        [-35.972816, 8.599963, 121.549110],
        [53.440182, -1.038988, 108.006729],
        [-53.496372, -1.064539, 108.092247],
        [54.241528, -4.178918, 106.884377],
        [55.032654, -9.581092, 103.894287],
        [55.313934, -11.209120, 101.510323],
        [59.889046, -7.512047, 103.089867],
        [61.269665, -8.790076, 99.314255],
        [61.713825, -9.295045, 96.733658],
        [60.585987, -5.284940, 102.643631],
        [62.577339, -6.474179, 98.564201],
        [63.113697, -7.000604, 95.845779],
        [60.393665, -3.197578, 102.040756],
        [62.391304, -3.999388, 98.390793],
        [62.802330, -4.344587, 96.006828],
        [60.068771, -1.140531, 101.079140],
        [61.835476, -1.399195, 98.379326],
        [62.499237, -1.609506, 96.577065],
        [-54.298100, -4.205809, 106.974464],
        [-55.091496, -9.612849, 103.993752],
        [-55.377033, -11.243772, 101.611938],
        [-59.952194, -7.547348, 103.197510],
        [-61.345390, -8.830379, 99.428230],
        [-61.798855, -9.340141, 96.850243],
        [-60.652172, -5.321231, 102.751076],
        [-62.656696, -6.515790, 98.679680],
        [-63.202854, -7.048355, 95.964432],
        [-60.463154, -3.234254, 102.145844],
        [-62.469059, -4.039888, 98.501869],
        [-62.886223, -4.387187, 96.119324],
        [-60.143600, -1.177774, 101.182289],
        [-61.915257, -1.442941, 98.486671],
        [-62.583908, -1.657710, 96.686638],
    ], dtype=np.float64)
    
    # Pre-computed SMPL_OFFSETS (default A-pose reference)
    SMPL_OFFSETS = np.array([
        [-0.000000, -0.000000, 95.636375],
        [9.724527, 0.660794, -2.176323],
        [-9.724524, 0.660784, -2.176338],
        [0.000126, -0.956926, 7.910828],
        [4.226306, -0.668771, -41.381596],
        [-4.219496, -0.669252, -41.382278],
        [0.000001, -1.408875, 3.875908],
        [4.306369, 4.781785, -44.443406],
        [-4.316302, 4.778397, -44.441897],
        [-0.000003, 1.087834, 12.874825],
        [2.704647, -14.389975, -4.230089],
        [-2.696224, -14.393471, -4.222107],
        [0.000111, 5.019032, 30.921669],
        [6.068256, 4.137760, 23.350792],
        [-6.068237, 4.137761, 23.350822],
        [0.000200, -1.308395, 8.559387],
        [11.917618, 3.818545, -0.933395],
        [-11.920322, 3.819248, -0.915558],
        [17.956129, 1.933364, -21.206947],
        [-17.984381, 1.920921, -21.184090],
        [17.498055, -9.650689, -13.501656],
        [-17.523556, -9.664503, -13.456863],
        [0.801346, -3.139930, -1.122353],
        [0.791126, -5.402174, -2.990089],
        [0.281281, -1.628028, -2.383965],
        [6.448864, -6.473060, -4.916862],
        [1.380619, -1.278029, -3.775612],
        [0.444160, -0.504969, -2.580597],
        [7.145805, -4.245953, -5.363098],
        [1.991352, -1.189239, -4.079430],
        [0.536358, -0.526425, -2.718422],
        [6.953484, -2.158590, -5.965973],
        [1.997639, -0.801810, -3.649963],
        [0.411026, -0.345200, -2.383965],
        [6.628590, -0.101543, -6.927589],
        [1.766705, -0.258664, -2.699814],
        [0.663761, -0.210311, -1.802261],
        [-0.801727, -3.141270, -1.117783],
        [-0.793396, -5.407040, -2.980713],
        [-0.285538, -1.630922, -2.381813],
        [-6.455822, -6.482808, -4.894737],
        [-1.393196, -1.283032, -3.769279],
        [-0.453465, -0.509762, -2.577988],
        [-7.155800, -4.256691, -5.341171],
        [-2.004524, -1.194559, -4.071396],
        [-0.546158, -0.532565, -2.715248],
        [-6.966782, -2.169715, -5.946404],
        [-2.005905, -0.805634, -3.643974],
        [-0.417164, -0.347299, -2.382545],
        [-6.647228, -0.113235, -6.909958],
        [-1.771656, -0.265167, -2.695618],
        [-0.668652, -0.214769, -1.800034],
    ], dtype=np.float64)


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


def create_target_armature(name: str = "SMPLH_Armature") -> bpy.types.Object:
    """
    Create armature with consistent bone lengths from target skeleton reference
    
    Returns:
        Created armature object with bone length and rest direction info matching target pose
    """
    # Use target joint positions directly from reference (J_ABSOLUTE defines target pose)
    target_joints = J_ABSOLUTE.copy()
    
    # Create armature
    armature = bpy.data.armatures.new(name)
    armature_obj = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.edit_bones
    
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i])
        bone.head = Vector(target_joints[i])
        
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if children:
            if i == 0:
                bone.tail = Vector(target_joints[3])  # Spine1
            else:
                bone.tail = Vector(target_joints[children[0]])
        else:
            # For end bones, use offset direction
            bone.tail = Vector(target_joints[i]) + Vector(SMPL_OFFSETS[i] if np.linalg.norm(SMPL_OFFSETS[i]) > 0.01 else (0, 0.05, 0))
    
    # Set parent relationships
    bone_list = list(edit_bones)
    for i, parent_idx in enumerate(SMPL_H_PARENTS):
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Created target armature with {len(bone_list)} bones")
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
        armature_obj: Target armature (with consistent bone lengths)
        poses: Animation poses (num_frames, 156)
        trans: Animation translations (num_frames, 3)
    """
    num_frames = len(poses)
    
    # Get target joint positions for reference (directly from loaded target skeleton)
    target_joints = J_ABSOLUTE.copy()
    
    # Store bone rest info
    bone_info = []
    for i in range(52):
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        child_idx = children[0] if children else None
        if i == 0 and children:
            child_idx = 3  # Pelvis points to Spine1
        
        bone_info.append({
            'head': Vector(target_joints[i]),
            'tail': Vector(target_joints[child_idx]) if child_idx is not None else None,
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


def process_npz_file(npz_path: Path, output_dir: Optional[Path] = None) -> None:
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
    
    # Create target armature
    armature = create_target_armature()
    
    # Set frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(poses) - 1
    
    # Retarget animation
    retarget_animation(armature, poses, trans)
    
    # Export
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (output_dir / npz_path.stem).with_suffix('.glb')
    else:
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
    
    parser = argparse.ArgumentParser(description="Retarget SMPL+H animations to consistent target skeleton (default: A-pose)")
    parser.add_argument("input_path", type=str, help="Path to a single .npz file or a directory containing .npz files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files")
    parser.add_argument("--output", type=str, default=None, help="Output directory for .glb files (default: next to each .npz)")
    parser.add_argument("--target", type=str, default=None, help="Path to custom target reference .npz file (must contain J_ABSOLUTE and SMPL_OFFSETS)")
    
    args = parser.parse_args(argv)
    
    # Load custom target if provided; if missing/invalid, continue with defaults
    if args.target:
        target_path = Path(args.target)
        if not target_path.exists():
            print(f"Target reference not found, using default target (A-pose): {target_path}")
        else:
            try:
                global J_ABSOLUTE, SMPL_OFFSETS
                J_ABSOLUTE, SMPL_OFFSETS = load_target_skeleton(target_path)
                print(f"Using custom target reference: {target_path}")
            except Exception:
                print("Failed to load custom target; using default target (A-pose)")
    
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"Error: Path not found: {input_path}")
        sys.exit(1)

    # Support single file or directory
    if input_path.is_file():
        if input_path.suffix.lower() != ".npz":
            print(f"Error: File is not an .npz: {input_path}")
            sys.exit(1)
        npz_files = [input_path]
    else:
        npz_files = sorted(input_path.rglob("*.npz"))
        if args.limit:
            npz_files = npz_files[:args.limit]
    if args.limit:
        npz_files = npz_files[:args.limit]
    
    print(f"Found {len(npz_files)} NPZ file(s)")

    # Resolve output directory if provided
    output_dir: Optional[Path] = None
    if args.output:
        output_dir = Path(args.output)

    for idx, npz_file in enumerate(npz_files, 1):
        print(f"\n[{idx}/{len(npz_files)}]")
        try:
            process_npz_file(npz_file, output_dir)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()