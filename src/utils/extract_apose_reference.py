"""
Extract A-pose reference skeleton from A-Pose.FBX file

This script loads the A-Pose.FBX file and extracts:
1. Joint positions in A-pose (J_ABSOLUTE)
2. Bone lengths (SMPL_OFFSETS)
3. Bone structure

Run this in Blender to generate the reference data.
"""

import bpy
import numpy as np
from pathlib import Path
from mathutils import Vector
from typing import Dict, List

# SMPL+H kinematic tree (same as retarget.py)
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

# Mapping from FBX bone names to SMPL-H joint names
FBX_TO_SMPL_MAPPING = {
    # Body core
    'pelvis': 'Pelvis',
    'spine_01': 'Spine1',
    'spine_02': 'Spine2',
    'spine_03': 'Spine3',
    'neck_01': 'Neck',
    'head': 'Head',
    
    # Left side
    'thigh_l': 'L_Hip',
    'calf_l': 'L_Knee',
    'foot_l': 'L_Ankle',
    'ball_l': 'L_Foot',
    'clavicle_l': 'L_Collar',
    'upperarm_l': 'L_Shoulder',
    'lowerarm_l': 'L_Elbow',
    'hand_l': 'L_Wrist',
    
    # Right side
    'thigh_r': 'R_Hip',
    'calf_r': 'R_Knee',
    'foot_r': 'R_Ankle',
    'ball_r': 'R_Foot',
    'clavicle_r': 'R_Collar',
    'upperarm_r': 'R_Shoulder',
    'lowerarm_r': 'R_Elbow',
    'hand_r': 'R_Wrist',
    
    # Left hand - thumb (L_Hand_0-2)
    'thumb_01_l': 'L_Hand_0',
    'thumb_02_l': 'L_Hand_1',
    'thumb_03_l': 'L_Hand_2',
    
    # Left hand - index (L_Hand_3-5)
    'index_01_l': 'L_Hand_3',
    'index_02_l': 'L_Hand_4',
    'index_03_l': 'L_Hand_5',
    
    # Left hand - middle (L_Hand_6-8)
    'middle_01_l': 'L_Hand_6',
    'middle_02_l': 'L_Hand_7',
    'middle_03_l': 'L_Hand_8',
    
    # Left hand - ring (L_Hand_9-11)
    'ring_01_l': 'L_Hand_9',
    'ring_02_l': 'L_Hand_10',
    'ring_03_l': 'L_Hand_11',
    
    # Left hand - pinky (L_Hand_12-14)
    'pinky_01_l': 'L_Hand_12',
    'pinky_02_l': 'L_Hand_13',
    'pinky_03_l': 'L_Hand_14',
    
    # Right hand - thumb (R_Hand_0-2)
    'thumb_01_r': 'R_Hand_0',
    'thumb_02_r': 'R_Hand_1',
    'thumb_03_r': 'R_Hand_2',
    
    # Right hand - index (R_Hand_3-5)
    'index_01_r': 'R_Hand_3',
    'index_02_r': 'R_Hand_4',
    'index_03_r': 'R_Hand_5',
    
    # Right hand - middle (R_Hand_6-8)
    'middle_01_r': 'R_Hand_6',
    'middle_02_r': 'R_Hand_7',
    'middle_03_r': 'R_Hand_8',
    
    # Right hand - ring (R_Hand_9-11)
    'ring_01_r': 'R_Hand_9',
    'ring_02_r': 'R_Hand_10',
    'ring_03_r': 'R_Hand_11',
    
    # Right hand - pinky (R_Hand_12-14)
    'pinky_01_r': 'R_Hand_12',
    'pinky_02_r': 'R_Hand_13',
    'pinky_03_r': 'R_Hand_14',
}


def load_fbx_armature(fbx_path: Path) -> bpy.types.Object:
    """Load FBX file and return the armature object"""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    
    # Find armature
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    
    raise ValueError(f"No armature found in {fbx_path}")


def extract_joint_positions(armature_obj: bpy.types.Object) -> np.ndarray:
    """
    Extract joint positions from armature in its rest pose (A-pose)
    
    Returns:
        J_ABSOLUTE: (52, 3) array of joint positions in A-pose
    """
    armature_data = armature_obj.data
    bpy.context.view_layer.objects.active = armature_obj
    
    # Make sure we're in rest pose
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Extract positions
    joint_positions = np.zeros((52, 3), dtype=np.float64)
    
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_data.edit_bones

    # Map FBX bone names to SMPL-H joint indices
    smpl_joint_to_idx = {name: i for i, name in enumerate(JOINT_NAMES)}
    
    # Create reverse mapping: SMPL name -> FBX bone name
    fbx_bone_names = {b.name for b in edit_bones}
    mapped_count = 0
    
    for fbx_name, smpl_name in FBX_TO_SMPL_MAPPING.items():
        if fbx_name in fbx_bone_names and smpl_name in smpl_joint_to_idx:
            joint_idx = smpl_joint_to_idx[smpl_name]
            bone = edit_bones[fbx_name]
            joint_positions[joint_idx] = np.array(bone.head[:])
            mapped_count += 1
        elif smpl_name in smpl_joint_to_idx:
            print(f"Warning: FBX bone '{fbx_name}' not found (maps to SMPL '{smpl_name}')")
    
    # Report missing joints
    missing_joints = []
    for i, smpl_name in enumerate(JOINT_NAMES):
        if np.allclose(joint_positions[i], 0.0):
            missing_joints.append(smpl_name)
    
    if missing_joints:
        print(f"Warning: {len(missing_joints)} joints not mapped: {missing_joints}")
    else:
        print(f"Successfully mapped {mapped_count} bones to SMPL-H joints")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return joint_positions


def compute_offsets(joint_positions: np.ndarray) -> np.ndarray:
    """
    Compute relative offsets from parent to child
    
    Returns:
        SMPL_OFFSETS: (52, 3) array of bone offsets
    """
    offsets = np.zeros((52, 3), dtype=np.float64)
    
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            offsets[i] = joint_positions[i]  # Root uses absolute position
        else:
            offsets[i] = joint_positions[i] - joint_positions[parent_idx]
    
    return offsets


def extract_apose_reference(fbx_path: Path) -> Dict:
    """
    Extract A-pose reference data from FBX file
    
    Returns:
        Dictionary with:
        - J_ABSOLUTE: (52, 3) joint positions
        - SMPL_OFFSETS: (52, 3) bone offsets
        - bone_lengths: dictionary of bone name -> length
    """
    print(f"Loading FBX: {fbx_path}")
    armature_obj = load_fbx_armature(fbx_path)
    
    print("Extracting joint positions...")
    J_ABSOLUTE = extract_joint_positions(armature_obj)
    
    print("Computing bone offsets...")
    SMPL_OFFSETS = compute_offsets(J_ABSOLUTE)
    
    # Extract bone lengths using FBX mapping
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones
    
    bone_lengths = {}
    for fbx_name, smpl_name in FBX_TO_SMPL_MAPPING.items():
        if fbx_name in edit_bones:
            bone = edit_bones[fbx_name]
            bone_lengths[smpl_name] = (Vector(bone.tail) - Vector(bone.head)).length
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {
        'J_ABSOLUTE': J_ABSOLUTE,
        'SMPL_OFFSETS': SMPL_OFFSETS,
        'bone_lengths': bone_lengths
    }


def save_reference_data(reference_data: Dict, output_path: Path):
    """Save extracted reference data to .npz file"""
    np.savez(
        output_path,
        J_ABSOLUTE=reference_data['J_ABSOLUTE'],
        SMPL_OFFSETS=reference_data['SMPL_OFFSETS'],
        bone_lengths=reference_data.get('bone_lengths', {})
    )
    print(f"Saved reference data to: {output_path}")


def main():
    """Main entry point - run in Blender"""
    import sys
    from pathlib import Path
    
    # Parse arguments (Blender strips '--' and everything before)
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        # For testing without blender command line
        if len(sys.argv) >= 3:
            argv = sys.argv[1:3]
        else:
            # Default paths for testing
            script_dir = Path(__file__).parent.parent
            fbx_path = script_dir / "A-Pose.FBX"
            output_path = script_dir.parent / "config" / "apose_reference.npz"
            
            if fbx_path.exists():
                print(f"Using default paths:")
                print(f"  FBX: {fbx_path}")
                print(f"  Output: {output_path}")
                reference_data = extract_apose_reference(fbx_path)
                save_reference_data(reference_data, output_path)
                
                print("\n=== Reference Data Summary ===")
                print(f"J_ABSOLUTE shape: {reference_data['J_ABSOLUTE'].shape}")
                print(f"SMPL_OFFSETS shape: {reference_data['SMPL_OFFSETS'].shape}")
                print(f"Number of bones: {len(reference_data['bone_lengths'])}")
                print("\nFirst 5 joint positions:")
                for i in range(min(5, len(JOINT_NAMES))):
                    pos = reference_data['J_ABSOLUTE'][i]
                    print(f"  {JOINT_NAMES[i]}: [{pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}]")
                return
            else:
                print("Usage: blender --background --python extract_apose_reference.py -- <fbx_path> <output_path>")
                print(f"Or place A-Pose.FBX in src/ directory")
                sys.exit(1)
    
    if len(argv) < 2:
        print("Usage: blender --background --python extract_apose_reference.py -- <fbx_path> <output_path>")
        sys.exit(1)
    
    fbx_path = Path(argv[0])
    output_path = Path(argv[1])
    
    if not fbx_path.exists():
        print(f"Error: FBX file not found: {fbx_path}")
        sys.exit(1)
    
    reference_data = extract_apose_reference(fbx_path)
    save_reference_data(reference_data, output_path)
    
    print("\n=== Reference Data Summary ===")
    print(f"J_ABSOLUTE shape: {reference_data['J_ABSOLUTE'].shape}")
    print(f"SMPL_OFFSETS shape: {reference_data['SMPL_OFFSETS'].shape}")
    print(f"Number of bones: {len(reference_data['bone_lengths'])}")
    print("\nFirst 5 joint positions:")
    for i in range(min(5, len(JOINT_NAMES))):
        pos = reference_data['J_ABSOLUTE'][i]
        print(f"  {JOINT_NAMES[i]}: [{pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}]")


if __name__ == "__main__":
    main()

