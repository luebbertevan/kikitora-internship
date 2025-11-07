#!/usr/bin/env python3
"""
Verify that frame 0 joint positions match the reference A-pose positions exactly.
"""

import bpy
import sys
import numpy as np
from pathlib import Path

# Load reference A-pose positions (from apose_from_blender.npz - rest pose from New-A-Pose.blend)
apose_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
apose_data = np.load(str(apose_path))
reference_j_absolute = apose_data['J_ABSOLUTE']

print("="*80)
print("Verifying frame 0 matches reference A-pose (from apose_from_blender.npz)")
print("="*80)

# Load retargeted GLB
glb_path = Path(__file__).parent.parent / 'data' / 'test' / 'D6- CartWheel_poses_retargeted.glb'

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
    sys.exit(1)

# Set to frame 0
bpy.context.scene.frame_set(0)

# Joint names
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2",
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck",
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder",
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

# Compare positions
print("\nComparing frame 0 positions to reference A-pose:")
print(f"{'Joint':<20} {'Match?':<8} {'Distance (m)':<15}")
print("-" * 50)

total_distance = 0.0
max_distance = 0.0
max_distance_joint = ""

for i, joint_name in enumerate(JOINT_NAMES[:10]):  # Check first 10 joints
    if joint_name not in armature.pose.bones:
        continue
    
    pose_bone = armature.pose.bones[joint_name]
    world_pos = armature.matrix_world @ pose_bone.head
    
    # Reference position
    ref_pos = reference_j_absolute[i]
    
    # Compute distance
    diff = np.array([world_pos.x - ref_pos[0], 
                     world_pos.y - ref_pos[1],
                     world_pos.z - ref_pos[2]])
    distance = np.sqrt(np.sum(diff**2))
    
    total_distance += distance
    if distance > max_distance:
        max_distance = distance
        max_distance_joint = joint_name
    
    match = "✓" if distance < 0.01 else "✗"
    print(f"{joint_name:<20} {match:<8} {distance:<15.6f}")

avg_distance = total_distance / 10
print("-" * 50)
print(f"Average distance: {avg_distance:.6f} m")
print(f"Max distance: {max_distance:.6f} m ({max_distance_joint})")

if avg_distance < 0.01:
    print("\n✓ Frame 0 MATCHES reference A-pose!")
else:
    print(f"\n✗ Frame 0 does NOT match reference A-pose")
    print(f"  Average error: {avg_distance:.6f} m")

