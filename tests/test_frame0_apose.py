#!/usr/bin/env python3
"""
Test that frame 0 has A-pose rotations applied correctly.

Loads a retargeted GLB and checks:
1. Frame 0 shoulder rotations match A-pose (~45° rotation)
2. Frame 1+ has different rotations (mocap animation)
"""

import bpy
import sys
import math
from pathlib import Path
from mathutils import Quaternion, Euler


def test_frame0_apose(glb_path: Path) -> None:
    """Test that frame 0 has A-pose"""
    print(f"\n{'='*80}")
    print(f"Testing frame 0 A-pose: {glb_path.name}")
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
        print("✗ No armature found in GLB")
        return
    
    print(f"✓ Found armature: {armature.name}")
    
    # Check if animation exists
    if not armature.animation_data or not armature.animation_data.action:
        print("✗ No animation data found")
        return
    
    action = armature.animation_data.action
    num_frames = int(action.frame_range[1] - action.frame_range[0]) + 1
    print(f"✓ Animation has {num_frames} frames")
    
    # Test shoulder rotations at frame 0 and frame 1
    bpy.context.scene.frame_set(0)
    
    l_shoulder = armature.pose.bones.get("L_Shoulder")
    r_shoulder = armature.pose.bones.get("R_Shoulder")
    
    if not l_shoulder or not r_shoulder:
        print("✗ Shoulder bones not found")
        return
    
    # Get frame 0 rotations
    frame0_l_quat = l_shoulder.rotation_quaternion.copy()
    frame0_r_quat = r_shoulder.rotation_quaternion.copy()
    
    # Convert to Euler for readability
    frame0_l_euler = frame0_l_quat.to_euler('XYZ')
    frame0_r_euler = frame0_r_quat.to_euler('XYZ')
    
    print(f"\nFrame 0 (A-pose):")
    print(f"  L_Shoulder rotation: {[math.degrees(a) for a in frame0_l_euler]}")
    print(f"  R_Shoulder rotation: {[math.degrees(a) for a in frame0_r_euler]}")
    
    # Check if L_Shoulder has ~-45° Y rotation (A-pose)
    l_y_deg = math.degrees(frame0_l_euler.y)
    r_y_deg = math.degrees(frame0_r_euler.y)
    
    # A-pose should have shoulders rotated down (negative Y for left, positive Y for right)
    if -50 < l_y_deg < -40 and 40 < r_y_deg < 50:
        print("  ✓ Frame 0 has A-pose shoulder rotations!")
    elif abs(l_y_deg) < 5 and abs(r_y_deg) < 5:
        print("  ⚠ Frame 0 has T-pose (identity) rotations")
    else:
        print(f"  ? Frame 0 has custom rotations (L: {l_y_deg:.1f}°, R: {r_y_deg:.1f}°)")
    
    # Check frame 1 (should be different - mocap animation)
    if num_frames > 1:
        bpy.context.scene.frame_set(1)
        
        frame1_l_quat = l_shoulder.rotation_quaternion.copy()
        frame1_r_quat = r_shoulder.rotation_quaternion.copy()
        
        frame1_l_euler = frame1_l_quat.to_euler('XYZ')
        frame1_r_euler = frame1_r_quat.to_euler('XYZ')
        
        print(f"\nFrame 1 (mocap animation):")
        print(f"  L_Shoulder rotation: {[math.degrees(a) for a in frame1_l_euler]}")
        print(f"  R_Shoulder rotation: {[math.degrees(a) for a in frame1_r_euler]}")
        
        # Check if frame 1 is different from frame 0
        if not frame0_l_quat.rotation_difference(frame1_l_quat).angle < 0.01:
            print("  ✓ Frame 1 has different rotations (mocap working)")
        else:
            print("  ⚠ Frame 1 same as frame 0 (animation may not be working)")
    
    # Check pelvis position (should be aligned to reference)
    pelvis = armature.pose.bones.get("Pelvis")
    if pelvis:
        bpy.context.scene.frame_set(0)
        pelvis_pos = armature.matrix_world @ pelvis.head
        print(f"\nFrame 0 Pelvis position: {[f'{x:.6f}' for x in pelvis_pos]}")
        
        # Expected reference position (from apose_from_blender.npz)
        expected = [-0.00179506, -0.02821913, 0.92035609]
        print(f"Expected (reference): {[f'{x:.6f}' for x in expected]}")
        
        diff = [(pelvis_pos[i] - expected[i]) for i in range(3)]
        distance = sum(d**2 for d in diff) ** 0.5
        print(f"Distance from reference: {distance:.6f} meters")
        
        if distance < 0.01:
            print("  ✓ Pelvis aligned to reference!")
        else:
            print("  ⚠ Pelvis not aligned to reference")


def main():
    """Test all retargeted GLB files in data/test"""
    test_dir = Path(__file__).parent.parent / "data" / "test"
    glb_files = sorted(test_dir.glob("*_retargeted.glb"))
    
    if not glb_files:
        print("No retargeted GLB files found in data/test")
        sys.exit(1)
    
    print(f"Found {len(glb_files)} retargeted GLB file(s) to test")
    
    for glb_path in glb_files:
        test_frame0_apose(glb_path)
    
    print(f"\n{'='*80}")
    print("Frame 0 testing complete!")
    print('='*80)


if __name__ == "__main__":
    main()

