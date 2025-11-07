#!/usr/bin/env python3
"""
Diagnose why frame 0 visually looks like mocap pose despite having A-pose rotations.
"""

import bpy
import sys
import math
import numpy as np
from pathlib import Path
from mathutils import Quaternion, Euler, Vector


def diagnose_glb(glb_path: Path):
    """Diagnose frame 0 appearance"""
    print(f"\n{'='*80}")
    print(f"Diagnosing: {glb_path.name}")
    print('='*80)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import GLB
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    # Find armature
    armature = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    
    if not armature:
        print("No armature found")
        return
    
    # Check frame 0
    bpy.context.scene.frame_set(0)
    
    # Get world-space bone positions (what you actually see)
    print("\nFrame 0 - Bone HEAD positions (world space - what you see):")
    
    for bone_name in ["Pelvis", "L_Shoulder", "R_Shoulder", "L_Hip", "R_Hip", "Spine1"]:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            # World position
            world_pos = armature.matrix_world @ pose_bone.head
            print(f"  {bone_name}: [{world_pos.x:.4f}, {world_pos.y:.4f}, {world_pos.z:.4f}]")
    
    # Get ELBOW positions to check if arms are down (A-pose) or out (T-pose/mocap)
    # Shoulder rotation affects where the elbow is, not where the shoulder head is
    l_elbow_pos = armature.matrix_world @ armature.pose.bones["L_Elbow"].head
    r_elbow_pos = armature.matrix_world @ armature.pose.bones["R_Elbow"].head
    l_shoulder_pos = armature.matrix_world @ armature.pose.bones["L_Shoulder"].head
    r_shoulder_pos = armature.matrix_world @ armature.pose.bones["R_Shoulder"].head
    
    print(f"\nArm position analysis (checking if arms are down = A-pose):")
    print(f"  L_Shoulder head: [{l_shoulder_pos.x:.4f}, {l_shoulder_pos.y:.4f}, {l_shoulder_pos.z:.4f}]")
    print(f"  L_Elbow head:    [{l_elbow_pos.x:.4f}, {l_elbow_pos.y:.4f}, {l_elbow_pos.z:.4f}]")
    print(f"  R_Shoulder head: [{r_shoulder_pos.x:.4f}, {r_shoulder_pos.y:.4f}, {r_shoulder_pos.z:.4f}]")
    print(f"  R_Elbow head:    [{r_elbow_pos.x:.4f}, {r_elbow_pos.y:.4f}, {r_elbow_pos.z:.4f}]")
    
    # In T-pose: elbows are roughly same Z as shoulders (arms horizontal)
    # In A-pose: elbows are LOWER Z than shoulders (arms angled down)
    l_arm_z_diff = l_shoulder_pos.z - l_elbow_pos.z
    r_arm_z_diff = r_shoulder_pos.z - r_elbow_pos.z
    
    print(f"\n  L_arm Z difference (shoulder - elbow): {l_arm_z_diff:.4f}")
    print(f"  R_arm Z difference (shoulder - elbow): {r_arm_z_diff:.4f}")
    
    if l_arm_z_diff > 0.1:
        print("  → L_arm angled DOWN (A-pose!)")
    elif abs(l_arm_z_diff) < 0.05:
        print("  → L_arm roughly horizontal (T-pose)")
    else:
        print(f"  → L_arm in custom pose")
    
    if r_arm_z_diff > 0.1:
        print("  → R_arm angled DOWN (A-pose!)")
    elif abs(r_arm_z_diff) < 0.05:
        print("  → R_arm roughly horizontal (T-pose)")
    else:
        print(f"  → R_arm in custom pose")
    
    # Check bone rotations
    print(f"\nFrame 0 - Bone rotations (local quaternions):")
    for bone_name in ["L_Shoulder", "R_Shoulder"]:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            quat = pose_bone.rotation_quaternion
            euler = quat.to_euler('XYZ')
            print(f"  {bone_name}:")
            print(f"    Quaternion: [{quat.w:.4f}, {quat.x:.4f}, {quat.y:.4f}, {quat.z:.4f}]")
            print(f"    Euler (deg): X={math.degrees(euler.x):.2f}, Y={math.degrees(euler.y):.2f}, Z={math.degrees(euler.z):.2f}")
    
    # Compare to frame 1
    print(f"\n{'='*40}")
    print("Frame 1 for comparison (mocap animation):")
    print('='*40)
    
    bpy.context.scene.frame_set(1)
    
    l_elbow_pos_f1 = armature.matrix_world @ armature.pose.bones["L_Elbow"].head
    r_elbow_pos_f1 = armature.matrix_world @ armature.pose.bones["R_Elbow"].head
    l_shoulder_pos_f1 = armature.matrix_world @ armature.pose.bones["L_Shoulder"].head
    r_shoulder_pos_f1 = armature.matrix_world @ armature.pose.bones["R_Shoulder"].head
    
    l_arm_z_diff_f1 = l_shoulder_pos_f1.z - l_elbow_pos_f1.z
    r_arm_z_diff_f1 = r_shoulder_pos_f1.z - r_elbow_pos_f1.z
    
    print(f"  L_arm Z difference: {l_arm_z_diff_f1:.4f}")
    print(f"  R_arm Z difference: {r_arm_z_diff_f1:.4f}")


def main():
    test_dir = Path(__file__).parent.parent / "data" / "test"
    glb_file = test_dir / "D6- CartWheel_poses_retargeted.glb"
    
    if not glb_file.exists():
        print(f"File not found: {glb_file}")
        sys.exit(1)
    
    diagnose_glb(glb_file)


if __name__ == "__main__":
    main()

