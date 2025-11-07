"""
Verify that A-pose export is compatible with retarget.py coordinate system.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import SMPL_H_PARENTS, JOINT_NAMES

print("="*80)
print("Verifying A-Pose Compatibility with retarget.py")
print("="*80)

# Load A-pose
apose_npz_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
if not apose_npz_path.exists():
    print(f"❌ A-pose NPZ not found")
    sys.exit(1)

apose_data = np.load(str(apose_npz_path))
A_POSE_J_ABSOLUTE = apose_data['J_ABSOLUTE']

print(f"\n📊 A-Pose Coordinate System:")
print(f"   Pelvis: {A_POSE_J_ABSOLUTE[0]}")
print(f"   X range: [{A_POSE_J_ABSOLUTE[:, 0].min():.3f}, {A_POSE_J_ABSOLUTE[:, 0].max():.3f}]")
print(f"   Y range: [{A_POSE_J_ABSOLUTE[:, 1].min():.3f}, {A_POSE_J_ABSOLUTE[:, 1].max():.3f}]")
print(f"   Z range: [{A_POSE_J_ABSOLUTE[:, 2].min():.3f}, {A_POSE_J_ABSOLUTE[:, 2].max():.3f}]")

# Check which axis is up
ranges = {
    'X': abs(A_POSE_J_ABSOLUTE[:, 0].max() - A_POSE_J_ABSOLUTE[:, 0].min()),
    'Y': abs(A_POSE_J_ABSOLUTE[:, 1].max() - A_POSE_J_ABSOLUTE[:, 1].min()),
    'Z': abs(A_POSE_J_ABSOLUTE[:, 2].max() - A_POSE_J_ABSOLUTE[:, 2].min())
}
max_axis = max(ranges, key=ranges.get)
print(f"   Largest range: {max_axis} axis ({ranges[max_axis]:.3f}m)")

# Check pelvis position
pelvis_z_rank = np.sum(A_POSE_J_ABSOLUTE[:, 2] < A_POSE_J_ABSOLUTE[0, 2])
pelvis_y_rank = np.sum(A_POSE_J_ABSOLUTE[:, 1] < A_POSE_J_ABSOLUTE[0, 1])
print(f"   Pelvis Z rank: {pelvis_z_rank}/52 (lower = closer to ground in Z-up)")
print(f"   Pelvis Y rank: {pelvis_y_rank}/52 (lower = closer to ground in Y-up)")

# Compute SMPL_OFFSETS from A-pose (as retarget.py will do)
A_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
for i in range(52):
    parent_idx = int(SMPL_H_PARENTS[i])
    if parent_idx == -1:
        A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i]
    else:
        A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i] - A_POSE_J_ABSOLUTE[parent_idx]

print(f"\n✅ Computed SMPL_OFFSETS from A-pose (as retarget.py will do)")
print(f"   Shape: {A_POSE_SMPL_OFFSETS.shape}")

# Check if coordinate system is Z-up (Blender standard)
print(f"\n🔍 Compatibility Check:")
if max_axis == 'Z' and pelvis_z_rank < 20:
    print(f"   ✅ A-pose is in Z-up coordinate system")
    print(f"   ✅ Compatible with Blender (which expects Z-up)")
    print(f"   ✅ Compatible with retarget.py (which assigns to Blender Vectors)")
    print(f"\n   The A-pose can be used directly in retarget.py!")
elif max_axis == 'Y':
    print(f"   ⚠️  A-pose is in Y-up coordinate system")
    print(f"   ❌ NOT compatible with Blender (which expects Z-up)")
    print(f"   ❌ Need to transform Y-up → Z-up")
else:
    print(f"   ⚠️  A-pose uses {max_axis}-up (unusual)")
    print(f"   Need to verify compatibility")

# Check if values are reasonable (in meters, human scale)
if ranges[max_axis] < 3.0:
    print(f"\n✅ Values are in reasonable human scale (meters)")
else:
    print(f"\n⚠️  Values might not be in meters (range too large)")

print("\n" + "="*80)
print("Summary:")
print("   retarget.py will:")
print("   1. Load A-pose J_ABSOLUTE")
print("   2. Compute SMPL_OFFSETS from it")
print("   3. Use SMPL_OFFSETS in forward_kinematics()")
print("   4. Assign FK output directly to Blender Vectors")
print("   5. Blender Vectors expect Z-up coordinates")
print("\n   Therefore: A-pose must be in Z-up for compatibility")
print("="*80)

