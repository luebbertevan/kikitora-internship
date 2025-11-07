#!/usr/bin/env python3
"""
Create A-pose rotations by manually posing T-pose armature in Blender.

This script:
1. Creates a T-pose armature (from hardcoded J_ABSOLUTE in retarget.py)
2. Lets you manually rotate bones to A-pose in Pose Mode
3. Exports the rotations as quaternions to NPZ

Usage:
    1. Run this script in Blender to create T-pose armature:
       /Applications/Blender.app/Contents/MacOS/Blender --python src/utils/reference/create_apose_rotations.py
    
    2. In Blender:
       - Switch to Pose Mode (Tab)
       - Manually rotate bones to A-pose:
         * L_Shoulder: Rotate down ~45° (R Y -45)
         * R_Shoulder: Rotate down ~45° (R Y 45)
         * Keep rest in T-pose
       - Go back to Object Mode
    
    3. Run this script again with --export flag:
       /Applications/Blender.app/Contents/MacOS/Blender <your_file>.blend --python src/utils/reference/create_apose_rotations.py -- --export
"""

import bpy
import numpy as np
import sys
import argparse
from pathlib import Path
from typing import Dict
from mathutils import Quaternion, Vector

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


def create_tpose_armature() -> bpy.types.Object:
    """Create T-pose armature from hardcoded J_ABSOLUTE"""
    print("Creating T-pose armature...")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create armature
    armature_data = bpy.data.armatures.new("SMPL_H_Armature")
    armature_obj = bpy.data.objects.new("SMPL_H_Armature", armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    
    # Switch to Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_data.edit_bones
    
    # Create bones
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i])
        bone.head = Vector(J_ABSOLUTE_TPOSE[i])
        
        # Set tail (for visualization)
        parent_idx = SMPL_H_PARENTS[i]
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        
        if len(children) > 0:
            # Point toward first child
            bone.tail = Vector(J_ABSOLUTE_TPOSE[children[0]])
        else:
            # End bone - extend in Y direction
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
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"✓ Created T-pose armature with {len(edit_bones)} bones")
    return armature_obj


def export_apose_rotations(armature_obj: bpy.types.Object, output_path: Path) -> None:
    """Export current pose bone rotations as A-pose"""
    print("Exporting A-pose rotations...")
    
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # Extract quaternion rotations for each bone
    rotations = {}
    for bone_name in JOINT_NAMES:
        if bone_name in armature_obj.pose.bones:
            pose_bone = armature_obj.pose.bones[bone_name]
            quat = pose_bone.rotation_quaternion
            rotations[bone_name] = np.array([quat.w, quat.x, quat.y, quat.z], dtype=np.float64)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Save to NPZ
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, **rotations)
    
    print(f"✓ Exported {len(rotations)} bone rotations to: {output_path}")
    print("\nA-pose rotations saved! You can now use these in retarget.py")


def main():
    # Parse arguments
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Create and export A-pose rotations")
    parser.add_argument("--export", action="store_true", help="Export current pose as A-pose rotations")
    parser.add_argument("--output", type=str, default="data/reference/apose_rotations.npz",
                       help="Output path for A-pose rotations NPZ")
    
    args = parser.parse_args(argv)
    output_path = Path(__file__).parent.parent.parent / args.output
    
    if args.export:
        # Export current pose
        armature_obj = bpy.context.active_object
        if not armature_obj or armature_obj.type != 'ARMATURE':
            print("Error: No armature selected. Please select the armature in Object Mode.")
            sys.exit(1)
        
        export_apose_rotations(armature_obj, output_path)
    else:
        # Create T-pose armature for manual posing
        create_tpose_armature()
        print("\n" + "="*80)
        print("T-POSE ARMATURE CREATED")
        print("="*80)
        print("\nNext steps:")
        print("1. Switch to Pose Mode (Tab key)")
        print("2. Rotate bones to create A-pose:")
        print("   - Select L_Shoulder bone (left arm)")
        print("   - Press R (rotate), Y (Y-axis), -45 (angle)")
        print("   - Select R_Shoulder bone (right arm)")
        print("   - Press R, Y, 45")
        print("3. Save this file as: tpose_to_apose.blend")
        print("4. Run again with --export flag:")
        print(f"   blender tpose_to_apose.blend --python {__file__} -- --export")


if __name__ == "__main__":
    main()

