"""
M3.4.1: Check Reference NPZ Coordinate System

This script investigates the coordinate system of the reference NPZ
to diagnose why the armature is facing the ground.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("="*80)
print("M3.4.1: Checking Reference NPZ Coordinate System")
print("="*80)

# Load reference NPZ
ref_path = Path(__file__).parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
print(f"\nLoading: {ref_path}")

ref_data = np.load(str(ref_path))
J_ABSOLUTE = ref_data['J_ABSOLUTE']

print(f"\n✓ J_ABSOLUTE shape: {J_ABSOLUTE.shape}")
print(f"✓ J_ABSOLUTE dtype: {J_ABSOLUTE.dtype}")

# Check pelvis (joint 0)
pelvis = J_ABSOLUTE[0]
print(f"\n📊 Pelvis (joint 0): {pelvis}")
print(f"   X: {pelvis[0]:.6f}, Y: {pelvis[1]:.6f}, Z: {pelvis[2]:.6f}")

# Check a few key joints
print(f"\n📊 Key Joints:")
print(f"   Pelvis (0):     {J_ABSOLUTE[0]}")
print(f"   L_Hip (1):      {J_ABSOLUTE[1]}")
print(f"   R_Hip (2):      {J_ABSOLUTE[2]}")
print(f"   Spine1 (3):     {J_ABSOLUTE[3]}")
print(f"   L_Shoulder (33): {J_ABSOLUTE[33]}")
print(f"   R_Shoulder (34): {J_ABSOLUTE[34]}")

# Analyze coordinate system
print(f"\n🔍 Coordinate System Analysis:")

# Check if Z is up (Blender standard)
# If Z is up, pelvis Z should be positive and reasonable
# If Y is up, pelvis Y should be positive and reasonable

z_range = [J_ABSOLUTE[:, 2].min(), J_ABSOLUTE[:, 2].max()]
y_range = [J_ABSOLUTE[:, 1].min(), J_ABSOLUTE[:, 1].max()]
x_range = [J_ABSOLUTE[:, 0].min(), J_ABSOLUTE[:, 0].max()]

print(f"   X range: [{x_range[0]:.3f}, {x_range[1]:.3f}]")
print(f"   Y range: [{y_range[0]:.3f}, {y_range[1]:.3f}]")
print(f"   Z range: [{z_range[0]:.3f}, {z_range[1]:.3f}]")

# Check which axis has the largest range (likely up axis)
ranges = {
    'X': abs(x_range[1] - x_range[0]),
    'Y': abs(y_range[1] - y_range[0]),
    'Z': abs(z_range[1] - z_range[0])
}
max_axis = max(ranges, key=ranges.get)
print(f"\n   Largest range: {max_axis} axis ({ranges[max_axis]:.3f})")

# Check pelvis position relative to other joints
# In Z-up: pelvis should be at bottom (lowest Z) or near origin
# In Y-up: pelvis should be at bottom (lowest Y) or near origin

pelvis_z_rank = np.sum(J_ABSOLUTE[:, 2] < pelvis[2])  # How many joints have lower Z
pelvis_y_rank = np.sum(J_ABSOLUTE[:, 1] < pelvis[1])  # How many joints have lower Y

print(f"\n   Pelvis Z rank: {pelvis_z_rank}/52 (lower = closer to ground in Z-up)")
print(f"   Pelvis Y rank: {pelvis_y_rank}/52 (lower = closer to ground in Y-up)")

# Check if pelvis is near origin
pelvis_dist_from_origin = np.linalg.norm(pelvis)
print(f"\n   Pelvis distance from origin: {pelvis_dist_from_origin:.6f}")

# Check if this looks like Z-up or Y-up
if pelvis[2] > 0.5 and pelvis_z_rank < 10:
    print(f"\n   ✅ Likely Z-up: Pelvis Z is positive ({pelvis[2]:.3f}) and near bottom")
elif pelvis[1] > 0.5 and pelvis_y_rank < 10:
    print(f"\n   ⚠️  Likely Y-up: Pelvis Y is positive ({pelvis[1]:.3f}) and near bottom")
else:
    print(f"\n   ⚠️  Unclear: Pelvis position doesn't clearly indicate up axis")

# Check if values are in meters (Blender standard)
# Human height is ~1.7m, so if Z range is ~1-2m, likely meters
if z_range[1] - z_range[0] < 3.0:
    print(f"\n   ✅ Values appear to be in meters (reasonable human scale)")
else:
    print(f"\n   ⚠️  Values might not be in meters (range too large)")

print("\n" + "="*80)
print("Next steps:")
print("  1. Compare this to reference GLB orientation")
print("  2. Check if coordinate system matches Blender's Z-up")
print("  3. Investigate pelvis rotation in mocap data")
print("="*80)

