#!/usr/bin/env python3
"""
Inspect what frame 0 looks like before and after A-pose application.
This will help debug why frame 0 still looks like mocap pose.
"""

import bpy
import sys
import math
from pathlib import Path
import numpy as np

# Add src to path for retarget module
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import retarget


def inspect_frame0():
    """Process one NPZ and inspect frame 0 at different stages"""
    npz_path = Path(__file__).parent.parent / "data" / "test" / "D6- CartWheel_poses.npz"
    
    print(f"\n{'='*80}")
    print(f"Inspecting frame 0 processing: {npz_path.name}")
    print('='*80)
    
    # Load NPZ data
    data = np.load(str(npz_path))
    poses = data['poses']
    trans = data['trans']
    
    print(f"\nLoaded {len(poses)} frames")
    print(f"Frame 0 pose (first 10 values): {poses[0][:10]}")
    print(f"Frame 0 trans: {trans[0]}")
    
    # Compute FK for frame 0
    joint_positions_frame0 = retarget.forward_kinematics(poses[0], trans[0])
    print(f"\nFrame 0 FK pelvis position: {joint_positions_frame0[0]}")
    
    # Create armature and animate (same as retarget.py)
    print("\n" + "="*80)
    print("Creating armature and baking animation...")
    print("="*80)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.armatures:
        bpy.data.armatures.remove(block)
    for block in bpy.data.actions:
        bpy.data.actions.remove(block)
    
    # Create armature
    armature = retarget.create_armature_from_j_absolute(retarget.J_ABSOLUTE)
    
    # Create empties and animate
    empties, joint_positions = retarget.create_empties_and_animate(
        npz_path, poses, trans, align_root=True
    )
    
    # Add constraints
    retarget.add_armature_constraints(armature, empties)
    
    # Bake
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone in armature.pose.bones:
        bone.bone.select = True
    
    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=min(10, len(poses) - 1),  # Just bake first 10 frames for speed
        step=1,
        only_selected=True,
        visual_keying=True,
        clear_constraints=True,
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'}
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Inspect frame 0 AFTER baking, BEFORE A-pose application
    print("\n" + "="*80)
    print("Frame 0 AFTER baking (mocap rotations):")
    print("="*80)
    
    bpy.context.scene.frame_set(0)
    
    for bone_name in ["Pelvis", "L_Shoulder", "R_Shoulder", "L_Hip", "Spine1"]:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            quat = pose_bone.rotation_quaternion
            euler = quat.to_euler('XYZ')
            print(f"  {bone_name}: quat={[f'{q:.4f}' for q in quat]}, "
                  f"euler_deg={[f'{math.degrees(a):.2f}' for a in euler]}")
    
    # Now apply A-pose
    print("\n" + "="*80)
    print("Applying A-pose to frame 0...")
    print("="*80)
    
    retarget.apply_apose_to_frame0(armature)
    
    # Inspect frame 0 AFTER A-pose application
    print("\n" + "="*80)
    print("Frame 0 AFTER A-pose application:")
    print("="*80)
    
    bpy.context.scene.frame_set(0)
    
    for bone_name in ["Pelvis", "L_Shoulder", "R_Shoulder", "L_Hip", "Spine1"]:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            quat = pose_bone.rotation_quaternion
            euler = quat.to_euler('XYZ')
            print(f"  {bone_name}: quat={[f'{q:.4f}' for q in quat]}, "
                  f"euler_deg={[f'{math.degrees(a):.2f}' for a in euler]}")
    
    # Check frame 1 for comparison
    print("\n" + "="*80)
    print("Frame 1 (for comparison):")
    print("="*80)
    
    bpy.context.scene.frame_set(1)
    
    for bone_name in ["Pelvis", "L_Shoulder", "R_Shoulder"]:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            quat = pose_bone.rotation_quaternion
            euler = quat.to_euler('XYZ')
            print(f"  {bone_name}: quat={[f'{q:.4f}' for q in quat]}, "
                  f"euler_deg={[f'{math.degrees(a):.2f}' for a in euler]}")


if __name__ == "__main__":
    inspect_frame0()

