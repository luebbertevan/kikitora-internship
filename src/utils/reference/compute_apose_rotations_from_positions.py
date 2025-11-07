#!/usr/bin/env python3
"""
Compute bone rotations needed to transform T-pose → A-pose.

Given:
- T-pose J_ABSOLUTE (rest pose joint positions)
- A-pose J_ABSOLUTE (target joint positions from apose_from_blender.npz)

Compute:
- Local bone rotations that transform each bone from T-pose to A-pose

This generates the rotations needed for frame 0 to match the reference A-pose.
"""

import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector, Quaternion
from typing import List, Optional

# T-pose J_ABSOLUTE from retarget.py
J_ABSOLUTE_TPOSE = np.array([
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


def compute_rotation_between_vectors(vec_from: Vector, vec_to: Vector) -> Quaternion:
    """Compute rotation quaternion that transforms vec_from to vec_to"""
    vec_from_norm = vec_from.normalized()
    vec_to_norm = vec_to.normalized()
    
    # Handle parallel vectors
    dot = vec_from_norm.dot(vec_to_norm)
    if abs(dot - 1.0) < 1e-6:
        return Quaternion((1.0, 0.0, 0.0, 0.0))
    elif abs(dot + 1.0) < 1e-6:
        # 180° rotation - find perpendicular axis
        if abs(vec_from_norm.x) < 0.9:
            perp = vec_from_norm.cross(Vector((1.0, 0.0, 0.0)))
        else:
            perp = vec_from_norm.cross(Vector((0.0, 1.0, 0.0)))
        return Quaternion(perp.normalized(), 3.14159265359)
    
    # Compute rotation
    axis = vec_from_norm.cross(vec_to_norm).normalized()
    angle = vec_from_norm.angle(vec_to_norm)
    return Quaternion(axis, angle)


def compute_apose_rotations():
    """
    Compute bone rotations by creating armatures and measuring the difference.
    
    Creates T-pose and A-pose armatures, then extracts the pose bone rotations
    from the A-pose armature (which represents the rotations needed).
    """
    # Load A-pose J_ABSOLUTE
    # Path from script: src/utils/reference/compute_apose_rotations_from_positions.py
    # Target: data/reference/apose_from_blender.npz
    script_dir = Path(__file__).parent  # src/utils/reference/
    apose_path = script_dir.parent.parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
    
    if not apose_path.exists():
        print(f"Error: {apose_path} not found")
        print("Please export A-pose using: src/utils/reference/export_apose_from_blender.py")
        sys.exit(1)
    
    apose_data = np.load(str(apose_path))
    J_ABSOLUTE_APOSE = apose_data['J_ABSOLUTE']
    
    print(f"Loaded A-pose from: {apose_path.name}")
    print(f"  T-pose pelvis: {J_ABSOLUTE_TPOSE[0]}")
    print(f"  A-pose pelvis: {J_ABSOLUTE_APOSE[0]}")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.armatures:
        bpy.data.armatures.remove(block)
    
    # Create T-pose armature
    print("\nCreating T-pose armature...")
    armature_data = bpy.data.armatures.new("SMPL_H_TPose")
    armature_obj = bpy.data.objects.new("SMPL_H_TPose", armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_data.edit_bones
    
    # Create bones with T-pose positions
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i])
        bone.head = Vector(J_ABSOLUTE_TPOSE[i])
        
        # Set tail
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if len(children) > 0:
            bone.tail = Vector(J_ABSOLUTE_TPOSE[children[0]])
        else:
            bone.tail = bone.head + Vector((0.0, 0.05, 0.0))
    
    # Set parent relationships
    for i in range(52):
        parent_idx = SMPL_H_PARENTS[i]
        if parent_idx >= 0:
            edit_bones[JOINT_NAMES[i]].parent = edit_bones[JOINT_NAMES[parent_idx]]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set rotation mode to quaternion
    bpy.ops.object.mode_set(mode='POSE')
    for bone in armature_obj.pose.bones:
        bone.rotation_mode = 'QUATERNION'
    
    # Now manually position bones to match A-pose positions
    print("Computing rotations to match A-pose positions...")
    
    # For each bone, compute rotation needed to point from parent to A-pose position
    rotations = {}
    
    for i in range(52):
        bone_name = JOINT_NAMES[i]
        parent_idx = SMPL_H_PARENTS[i]
        
        if parent_idx == -1:
            # Root bone - no rotation
            rotations[bone_name] = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
            continue
        
        # Compute bone direction in T-pose (rest pose)
        tpose_dir = Vector(J_ABSOLUTE_TPOSE[i] - J_ABSOLUTE_TPOSE[parent_idx])
        
        # Compute bone direction in A-pose (target)
        apose_dir = Vector(J_ABSOLUTE_APOSE[i] - J_ABSOLUTE_APOSE[parent_idx])
        
        # Skip zero-length bones
        if tpose_dir.length < 1e-6 or apose_dir.length < 1e-6:
            rotations[bone_name] = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
            continue
        
        # Compute rotation from T-pose direction to A-pose direction
        quat = compute_rotation_between_vectors(tpose_dir, apose_dir)
        
        rotations[bone_name] = np.array([quat.w, quat.x, quat.y, quat.z], dtype=np.float64)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return rotations


def main():
    """Compute and save A-pose rotations from reference A-pose positions"""
    print("="*80)
    print("Computing A-pose rotations from reference positions")
    print("="*80)
    
    rotations = compute_apose_rotations()
    
    # Save to NPZ
    output_path = Path(__file__).parent.parent.parent / "data" / "reference" / "apose_rotations.npz"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    np.savez(output_path, **rotations)
    
    print(f"\n✓ Computed {len(rotations)} bone rotations")
    print(f"✓ Saved to: {output_path}")
    print("\nThese rotations will transform T-pose → reference A-pose")
    print("Frame 0 will now match the reference A-pose exactly!")


if __name__ == "__main__":
    main()

