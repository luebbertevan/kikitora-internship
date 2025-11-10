import bpy
import numpy as np
import sys
import argparse
from pathlib import Path
from typing import Optional, List
from mathutils import Vector
from numpy.typing import NDArray


# SMPL+H joint hierarchy (parent indices)
SMPL_H_PARENTS: NDArray[np.int32] = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Joint names (52 entries)
JOINT_NAMES: List[str] = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

# T-pose joint positions from the original SMPL-H template
# Mocap rotations are relative to T-pose, so we need T-pose bone directions for FK
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

# Compute RELATIVE offsets from T-pose J_ABSOLUTE
# These are used in forward kinematics - mocap rotations are relative to T-pose
SMPL_OFFSETS: NDArray[np.float64] = np.zeros((52, 3))
for i in range(52):
    parent_idx = SMPL_H_PARENTS[i]
    if parent_idx == -1:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i]
    else:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]


# Reference A-pose joint positions (loaded at runtime)
APOSE_PATH_DEFAULT = Path(__file__).parent / 'A-Pose.npz'


def axis_angle_to_rotation_matrix(axis_angle: NDArray[np.float64]) -> NDArray[np.float64]:
    """Convert an axis-angle vector to a rotation matrix via Rodrigues' formula."""
    angle: float = np.linalg.norm(axis_angle)
    if angle < 1e-6:
        return np.eye(3)
    
    # Normalize axis
    axis: NDArray[np.float64] = axis_angle / angle
    
    # Rodrigues' rotation formula
    K: NDArray[np.float64] = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    R: NDArray[np.float64] = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R

def load_reference_pelvis(j_absolute_apose: NDArray[np.float64]) -> Optional[NDArray[np.float64]]:
    """Return the pelvis position from the A-pose array."""
    return j_absolute_apose[0].copy()


def align_root_to_reference(
    joint_positions: NDArray[np.float64],
    reference_pelvis: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Translate joints so the pelvis matches the reference position."""
    # Handle both single-frame and multi-frame inputs
    if joint_positions.ndim == 2:
        # Single frame: (52, 3)
        frame0_pelvis = joint_positions[0, :]  # Pelvis is index 0
        translation_offset = reference_pelvis - frame0_pelvis
        return joint_positions + translation_offset[np.newaxis, :]
    else:
        # Multi-frame: (num_frames, 52, 3)
        frame0_pelvis = joint_positions[0, 0, :]  # Frame 0, Pelvis is index 0
        translation_offset = reference_pelvis - frame0_pelvis
        return joint_positions + translation_offset[np.newaxis, np.newaxis, :]


def forward_kinematics(poses: NDArray[np.float64], trans: NDArray[np.float64]) -> NDArray[np.float64]:
    """Reconstruct joint positions from axis-angle rotations and T-pose offsets."""
    num_joints: int = len(SMPL_H_PARENTS)
    joint_positions: NDArray[np.float64] = np.zeros((num_joints, 3))
    
    # Reshape poses: (156,) -> (52, 3) for 52 joints
    pose_params: NDArray[np.float64] = poses.reshape(-1, 3)
    
    # Global transformation matrices
    global_transforms: List[NDArray[np.float64]] = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        # Local rotation from axis-angle
        if i < len(pose_params):
            rot_mat: NDArray[np.float64] = axis_angle_to_rotation_matrix(pose_params[i])
        else:
            rot_mat = np.eye(3)
        
        # Local transform
        local_transform: NDArray[np.float64] = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = SMPL_OFFSETS[i]
        
        # Global transform
        parent_idx: int = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            # Root joint - apply global translation
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions


def add_cube_and_parent(
    armature: bpy.types.Object,
    cube_size: float = 0.05,
    cube_location: tuple[float, float, float] = (0, 0, 0)
) -> bpy.types.Object:
    """Create a cube, parent it to the armature, and return the cube."""
    bpy.ops.mesh.primitive_cube_add(
        size=cube_size,
        location=cube_location
    )
    
    cube: bpy.types.Object = bpy.context.active_object
    cube.name = "ParentedCube"
    
    bpy.ops.object.select_all(action='DESELECT')
    
    cube.select_set(True)
    armature.select_set(True)
    
    bpy.context.view_layer.objects.active = armature
    
    # Parent cube to armature
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    
    print(f"Cube '{cube.name}' (size: {cube_size}) parented to armature '{armature.name}' at location {cube_location}")
    
    return cube


def process_npz_file(
    npz_path: Path,
    cube_size: float = 0.05,
    cube_location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    frame_limit: Optional[int] = None,
    j_absolute_apose: Optional[NDArray[np.float64]] = None
) -> None:
    """Retarget one NPZ file and export the resulting GLB."""
    print(f"\n{'='*80}")
    print(f"Processing: {npz_path}")
    print(f"{'='*80}")
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all animation data to prevent cross-contamination between files
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)
    
    # Load NPZ file
    data = np.load(str(npz_path))
    poses: NDArray[np.float64] = data['poses']
    trans: NDArray[np.float64] = data['trans']

    total_frames: int = len(poses)

    if frame_limit is not None:
        if frame_limit <= 0:
            raise ValueError(f"frame_limit must be a positive integer, got {frame_limit}")

        frames_to_use = min(frame_limit, total_frames)
        if frames_to_use < total_frames:
            print(f"Frame limit applied: using first {frames_to_use} of {total_frames} frames")
            poses = poses[:frames_to_use]
            trans = trans[:frames_to_use]
        else:
            print(f"Frame limit ({frame_limit}) exceeds available frames; using all {total_frames}")

    if len(poses) == 0:
        raise ValueError(f"No frames available after applying frame limit for {npz_path}")
    
    # Get framerate (default to 60 if not present)
    framerate: float = float(data.get('mocap_framerate', 60))
    
    print(f"Loaded {len(poses)} frames at {framerate} fps")
    print(f"Poses shape: {poses.shape}")
    print(f"Trans shape: {trans.shape}")
    
    if j_absolute_apose is None:
        raise ValueError("A-pose joint positions were not provided to process_npz_file")

    joint_positions_frame0: NDArray[np.float64] = j_absolute_apose  # forward_kinematics(poses[0], trans[0])
    print("Using frame 0 pose (from FK) for armature creation")
    
    # Align root to reference pelvis position
    reference_pelvis = load_reference_pelvis(j_absolute_apose)
    if reference_pelvis is not None:
        joint_positions_frame0 = align_root_to_reference(joint_positions_frame0, reference_pelvis)
        print(f"✓ Aligned root to reference pelvis: {reference_pelvis}")
    else:
        print("⚠️  Skipping root alignment (reference not found)")
    
    # Create armature
    armature_data = bpy.data.armatures.new("SMPL_H_Armature")
    armature: bpy.types.Object = bpy.data.objects.new("SMPL_H_Armature", armature_data)
    bpy.context.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    
    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.data.edit_bones
    bone_list: List[bpy.types.EditBone] = []
    
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}")
        bone.head = Vector(joint_positions_frame0[i])

        # Set tail pointing toward first child or slightly offset
        child_indices: List[int] = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if child_indices:
            target_idx = 3 if i == 0 else child_indices[0]
            bone.tail = Vector(joint_positions_frame0[target_idx])
        else:
            bone.tail = Vector(joint_positions_frame0[i]) + Vector((0, 0.05, 0))
        
        bone_list.append(bone)
    
    # Set parent relationships
    for i in range(52):
        parent_idx: int = int(SMPL_H_PARENTS[i])
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(poses) - 1
    bpy.context.scene.render.fps = int(framerate)
    
    print("Creating empties and animation...")
    
    # Create empties for each joint to hold the computed positions
    empties: List[bpy.types.Object] = []
    for i in range(52):
        joint_name: str = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
        empty = bpy.data.objects.new(f"Empty_{joint_name}", None)
        bpy.context.collection.objects.link(empty)
        empty.empty_display_size = 0.02
        empties.append(empty)
    
    # Frame 0: keyframe Blender A-pose world positions directly
    bpy.context.scene.frame_set(0)
    for i, empty in enumerate(empties):
        empty.location = Vector(j_absolute_apose[i])
        empty.keyframe_insert(data_path="location", frame=0)

    # Animate empties using computed forward kinematics for remaining frames
    keyframe_step: int = 1  # Keyframe every frame
    print("Processing frames 1..N with forward kinematics (frame 0 uses Blender A-pose)...")
    for frame_idx in range(1, len(poses), keyframe_step):
        bpy.context.scene.frame_set(frame_idx)
        
        # Compute joint positions using EXACT SAME forward kinematics
        joint_positions: NDArray[np.float64] = forward_kinematics(poses[frame_idx], trans[frame_idx])
        
        # Set empty positions
        for i in range(52):
            empties[i].location = Vector(joint_positions[i])
            empties[i].keyframe_insert(data_path="location", frame=frame_idx)
        
        if frame_idx % 100 == 0:
            print(f"  Processed frame {frame_idx}/{len(poses)}")
    
    print("Empties animation complete!")
    
    print("Adding constraints to armature...")
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = armature.pose.bones
    
    # Add constraints to each bone to track its empty
    for i in range(52):
        joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
        pose_bone = pose_bones.get(joint_name)
        
        if pose_bone:
            child_indices = [j for j in range(52) if SMPL_H_PARENTS[j] == i]

            # Root bone (Pelvis) - special handling
            if i == 0:
                constraint = pose_bone.constraints.new('COPY_LOCATION')
                constraint.target = empties[i]
                constraint.name = "Track_Root_Location"
                
                track_constraint = pose_bone.constraints.new('DAMPED_TRACK')
                track_constraint.target = empties[3]  # Spine1
                track_constraint.name = "Track_To_Spine1"
                track_constraint.track_axis = 'TRACK_Y'
            
            elif len(child_indices) == 0:
                track_constraint = pose_bone.constraints.new('COPY_LOCATION')
                track_constraint.target = empties[i]
                track_constraint.name = "Track_End_Location"
            
            else:
                child_idx: int = child_indices[0]
                track_constraint = pose_bone.constraints.new('COPY_LOCATION')
                track_constraint.target = empties[i]
                track_constraint.name = f"Track_To_Child_{i}"
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("Armature constraints added!")
    
    print("Baking constraints to keyframes on armature bones...")
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone in armature.pose.bones:
        bone.bone.select = True
    

    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=len(poses) - 1,
        step=1,
        only_selected=True,
        visual_keying=True,
        clear_constraints=True,  # Clear constraints after baking
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'}
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("Baking complete! All bones now have keyframes on every frame.")
    
    print("Removing empties...")
    for empty in empties:
        bpy.data.objects.remove(empty, do_unlink=True)
    
    print("Empties removed. Ready for export.")
    
    cube: bpy.types.Object = add_cube_and_parent(armature, cube_size, cube_location)
    
    # Export to GLB with "retargeted" in filename
    output_path: Path = npz_path.with_stem(npz_path.stem + '_retargeted').with_suffix('.glb')
    
    # Select armature and cube for export
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    cube.select_set(True)
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
    
    print(f"Successfully exported to: {output_path}")


def find_npz_files(folder_path: Path) -> List[Path]:
    """
    Recursively find all .npz files in a folder
    
    Args:
        folder_path: Path to the folder to search
        
    Returns:
        List of paths to .npz files
    """
    return sorted(folder_path.rglob("*.npz"))


def main() -> None:
    """Main entry point for batch processing"""
    # Parse command-line arguments
    # Blender passes arguments after "--" to the script
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(
        description="Batch process NPZ files to GLB format with SMPL+H armature"
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
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Limit the number of frames processed from each NPZ (must be > 0)"
    )
    parser.add_argument(
        "--export-target-apose",
        action="store_true",
        help="Export the target A-pose armature to GLB and exit"
    )
    parser.add_argument(
        "--apose-path",
        type=str,
        default=None,
        help="Path to A-pose NPZ (defaults to A-Pose.npz next to retarget.py)"
    )
    parser.add_argument(
        "--cube-size",
        type=float,
        default=0.05,
        help="Size of the cube to add (default: 0.05)"
    )
    parser.add_argument(
        "--cube-location",
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0],
        metavar=("X", "Y", "Z"),
        help="Location of the cube as X Y Z coordinates (default: 0 0 0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output directory (used with --export-target-apose)"
    )
    
    args = parser.parse_args(argv)
    
    # Determine A-pose NPZ path and load data once
    if args.apose_path:
        apose_path = Path(args.apose_path)
    else:
        apose_path = APOSE_PATH_DEFAULT

    if not apose_path.exists():
        print(f"Error: A-pose NPZ not found at {apose_path}")
        print("Place A-Pose.npz next to retarget.py or specify --apose-path <file>")
        sys.exit(1)

    apose_data = np.load(str(apose_path))
    if 'J_ABSOLUTE' not in apose_data:
        print(f"Error: {apose_path} missing 'J_ABSOLUTE'")
        sys.exit(1)
    J_absolute_apose = apose_data['J_ABSOLUTE']
    print(f"Loaded A-pose from {apose_path}")

    # Handle A-pose export mode early
    if args.export_target_apose:
        out_dir = Path(args.output) if args.output else None
        try:
            # Define helpers inline
            def _load_target_reference(npz_path: Optional[Path] = None) -> NDArray[np.float64]:
                if npz_path is None:
                    npz_path = Path(__file__).parent / "target_reference.npz"
                data = np.load(str(npz_path))
                if 'J_ABSOLUTE' not in data:
                    raise KeyError("target_reference.npz missing 'J_ABSOLUTE'")
                J = data['J_ABSOLUTE']
                if J.shape != (52, 3):
                    raise ValueError(f"J_ABSOLUTE shape {J.shape} != (52, 3)")
                return J

            def _create_armature_from_target(J: NDArray[np.float64], name: str = "SMPLH_TargetArmature") -> bpy.types.Object:
                armature = bpy.data.armatures.new(name)
                armature_obj = bpy.data.objects.new(name, armature)
                bpy.context.collection.objects.link(armature_obj)
                bpy.context.view_layer.objects.active = armature_obj
                armature_obj.location = (0, 0, 0)
                armature_obj.rotation_euler = (0, 0, 0)
                armature_obj.scale = (1, 1, 1)
                armature_obj.show_in_front = True
                armature.display_type = 'WIRE'
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature.edit_bones
                for i in range(52):
                    bone = edit_bones.new(JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}")
                    bone.head = Vector(J[i])
                    children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
                    if children:
                        if i == 0:
                            bone.tail = Vector(J[3])
                        else:
                            bone.tail = Vector(J[children[0]])
                    else:
                        bone.tail = Vector(J[i]) + Vector((0, 0.05, 0))
                # Parents
                bone_list = list(edit_bones)
                for i, parent_idx in enumerate(SMPL_H_PARENTS):
                    if parent_idx != -1:
                        bone_list[i].parent = bone_list[parent_idx]
                bpy.ops.object.mode_set(mode='OBJECT')
                return armature_obj

            # Clear scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            J = _load_target_reference()
            # Convert centimeters -> meters to match Blender/glTF units
            J = (J * 0.01).astype(np.float64)
            armature = _create_armature_from_target(J)
            cube = add_cube_and_parent(armature, cube_size=0.05, cube_location=(0.0, 0.0, 0.0))
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = 0
            if out_dir is not None:
                out_dir.mkdir(parents=True, exist_ok=True)
                output_path = (out_dir / "target_reference").with_suffix('.glb')
            else:
                output_path = (Path(__file__).parent / "target_reference").with_suffix('.glb')
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            if cube:
                cube.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.export_scene.gltf(
                filepath=str(output_path),
                export_format='GLB',
                use_selection=True,
                export_animations=True,
            )
            print(f"✓ Exported target A-pose to: {output_path}")
        except Exception as e:
            print(f"Error exporting target A-pose: {e}")
            import traceback
            traceback.print_exc()
        return

    # Convert to Path object
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
    
    # Process each file
    for idx, npz_file in enumerate(npz_files, 1):
        print(f"\n[{idx}/{len(npz_files)}] Processing: {npz_file.name}")
        try:
            process_npz_file(
                npz_file,
                args.cube_size,
                tuple(args.cube_location),
                args.frame_limit,
                J_absolute_apose
            )
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