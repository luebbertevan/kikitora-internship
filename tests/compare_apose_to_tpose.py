"""
Compare exported A-pose NPZ to hardcoded T-pose J_ABSOLUTE
Verify that bone lengths (SMPL_OFFSETS) are the same.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import J_ABSOLUTE as T_POSE_J_ABSOLUTE, SMPL_H_PARENTS, JOINT_NAMES

print("="*80)
print("Comparing A-pose from Blender to Hardcoded T-pose")
print("="*80)

# Load exported A-pose NPZ
apose_npz_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'

if not apose_npz_path.exists():
    print(f"\n❌ Error: A-pose NPZ not found at {apose_npz_path}")
    print("   Please export the A-pose first using export_apose_from_blender.py")
    sys.exit(1)

print(f"\n📁 Loading A-pose from: {apose_npz_path.name}")
apose_data = np.load(str(apose_npz_path))
A_POSE_J_ABSOLUTE = apose_data['J_ABSOLUTE']
A_POSE_SMPL_OFFSETS = apose_data.get('SMPL_OFFSETS', None)

print(f"✓ Loaded A-pose J_ABSOLUTE: shape {A_POSE_J_ABSOLUTE.shape}")

# Compute T-pose SMPL_OFFSETS
T_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
for i in range(52):
    parent_idx = int(SMPL_H_PARENTS[i])
    if parent_idx == -1:
        T_POSE_SMPL_OFFSETS[i] = T_POSE_J_ABSOLUTE[i]
    else:
        T_POSE_SMPL_OFFSETS[i] = T_POSE_J_ABSOLUTE[i] - T_POSE_J_ABSOLUTE[parent_idx]

# Compute A-pose SMPL_OFFSETS if not in NPZ
if A_POSE_SMPL_OFFSETS is None:
    print("   Computing A-pose SMPL_OFFSETS from J_ABSOLUTE...")
    A_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i]
        else:
            A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i] - A_POSE_J_ABSOLUTE[parent_idx]

print(f"✓ T-pose SMPL_OFFSETS: shape {T_POSE_SMPL_OFFSETS.shape}")
print(f"✓ A-pose SMPL_OFFSETS: shape {A_POSE_SMPL_OFFSETS.shape}")

# Compare SMPL_OFFSETS (bone lengths)
print(f"\n🔍 Comparing Bone Lengths (SMPL_OFFSETS):")
print(f"   {'Joint':<20} {'T-pose Offset':<30} {'A-pose Offset':<30} {'Difference':<20} {'Match'}")
print("   " + "-"*110)

max_diff = 0.0
max_diff_joint = None
all_match = True

for i in range(52):
    joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
    t_offset = T_POSE_SMPL_OFFSETS[i]
    a_offset = A_POSE_SMPL_OFFSETS[i]
    diff = np.linalg.norm(t_offset - a_offset)
    
    # Check if they match (within 1mm tolerance)
    matches = diff < 0.001
    if not matches:
        all_match = False
    
    if diff > max_diff:
        max_diff = diff
        max_diff_joint = joint_name
    
    # Only print joints with differences or first 10 joints
    if not matches or i < 10:
        match_str = "✓" if matches else "✗"
        print(f"   {joint_name:<20} {str(t_offset):<30} {str(a_offset):<30} {diff:<20.6f} {match_str}")

print(f"\n📊 Summary:")
print(f"   Maximum difference: {max_diff:.6f} meters ({max_diff*1000:.3f} mm)")
print(f"   Joint with max difference: {max_diff_joint}")
print(f"   All bone lengths match: {'✅ YES' if all_match else '❌ NO'}")

if not all_match:
    print(f"\n⚠️  WARNING: Bone lengths differ!")
    print(f"   This suggests the A-pose has different bone lengths than T-pose.")
    print(f"   If you modified bone lengths in Blender, this is expected.")
    print(f"   If you didn't modify bone lengths, there may be an issue.")
else:
    print(f"\n✅ SUCCESS: All bone lengths match!")
    print(f"   The A-pose has the same bone lengths as T-pose (as expected).")
    print(f"   Only the joint positions differ (due to rotations).")

# Compare J_ABSOLUTE positions (should differ due to rotations)
print(f"\n🔍 Comparing Joint Positions (J_ABSOLUTE):")
print(f"   These should differ due to rotations from T-pose to A-pose")

pelvis_diff = np.linalg.norm(T_POSE_J_ABSOLUTE[0] - A_POSE_J_ABSOLUTE[0])
l_shoulder_diff = np.linalg.norm(T_POSE_J_ABSOLUTE[33] - A_POSE_J_ABSOLUTE[33])
r_shoulder_diff = np.linalg.norm(T_POSE_J_ABSOLUTE[34] - A_POSE_J_ABSOLUTE[34])

print(f"\n   Pelvis position difference: {pelvis_diff:.6f} m ({pelvis_diff*1000:.3f} mm)")
print(f"   L_Shoulder position difference: {l_shoulder_diff:.6f} m ({l_shoulder_diff*1000:.3f} mm)")
print(f"   R_Shoulder position difference: {r_shoulder_diff:.6f} m ({r_shoulder_diff*1000:.3f} mm)")

print(f"\n   T-pose Pelvis: {T_POSE_J_ABSOLUTE[0]}")
print(f"   A-pose Pelvis: {A_POSE_J_ABSOLUTE[0]}")

print(f"\n   T-pose L_Shoulder: {T_POSE_J_ABSOLUTE[33]}")
print(f"   A-pose L_Shoulder: {A_POSE_J_ABSOLUTE[33]}")

# Check if there's a coordinate system issue
print(f"\n🔍 Coordinate System Analysis:")
print(f"   T-pose Pelvis Y: {T_POSE_J_ABSOLUTE[0][1]:.6f}, Z: {T_POSE_J_ABSOLUTE[0][2]:.6f}")
print(f"   A-pose Pelvis Y: {A_POSE_J_ABSOLUTE[0][1]:.6f}, Z: {A_POSE_J_ABSOLUTE[0][2]:.6f}")
print(f"   Difference suggests Y/Z might be swapped or coordinate system transformed")

# Check bone length magnitudes (should be same regardless of coordinate system)
print(f"\n🔍 Bone Length Magnitudes (should match):")
print(f"   {'Joint':<20} {'T-pose Length':<20} {'A-pose Length':<20} {'Difference':<20}")
print("   " + "-"*80)

for i in range(min(10, 52)):  # First 10 joints
    joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
    t_len = np.linalg.norm(T_POSE_SMPL_OFFSETS[i])
    a_len = np.linalg.norm(A_POSE_SMPL_OFFSETS[i])
    diff = abs(t_len - a_len)
    print(f"   {joint_name:<20} {t_len:<20.6f} {a_len:<20.6f} {diff:<20.6f}")

print("\n" + "="*80)
print("⚠️  ISSUE DETECTED:")
print("   Bone lengths (SMPL_OFFSETS) should be the same between T-pose and A-pose.")
print("   The large differences suggest:")
print("   1. The armature in Blender was created from a different source")
print("   2. There's a coordinate system transformation issue")
print("   3. The armature has different bone lengths than the hardcoded T-pose")
print("\n   Questions:")
print("   - How was the armature in your .blend file created?")
print("   - Was it created from the hardcoded T-pose J_ABSOLUTE?")
print("   - Or was it imported from another source (FBX, GLB, etc.)?")
print("="*80)

