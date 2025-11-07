"""
Analyze coordinate system differences between T-pose and A-pose exports.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import J_ABSOLUTE as T_POSE_J_ABSOLUTE, SMPL_H_PARENTS, JOINT_NAMES

print("="*80)
print("Coordinate System Analysis")
print("="*80)

# Load A-pose
apose_npz_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
if not apose_npz_path.exists():
    print(f"❌ A-pose NPZ not found")
    sys.exit(1)

apose_data = np.load(str(apose_npz_path))
A_POSE_J_ABSOLUTE = apose_data['J_ABSOLUTE']

print(f"\n📊 T-Pose (Hardcoded) Coordinate System:")
print(f"   Expected: Z-up (Blender standard)")
print(f"   Pelvis: {T_POSE_J_ABSOLUTE[0]}")
print(f"   X range: [{T_POSE_J_ABSOLUTE[:, 0].min():.3f}, {T_POSE_J_ABSOLUTE[:, 0].max():.3f}]")
print(f"   Y range: [{T_POSE_J_ABSOLUTE[:, 1].min():.3f}, {T_POSE_J_ABSOLUTE[:, 1].max():.3f}]")
print(f"   Z range: [{T_POSE_J_ABSOLUTE[:, 2].min():.3f}, {T_POSE_J_ABSOLUTE[:, 2].max():.3f}]")

# Check which axis has largest range (likely up axis)
t_ranges = {
    'X': abs(T_POSE_J_ABSOLUTE[:, 0].max() - T_POSE_J_ABSOLUTE[:, 0].min()),
    'Y': abs(T_POSE_J_ABSOLUTE[:, 1].max() - T_POSE_J_ABSOLUTE[:, 1].min()),
    'Z': abs(T_POSE_J_ABSOLUTE[:, 2].max() - T_POSE_J_ABSOLUTE[:, 2].min())
}
t_max_axis = max(t_ranges, key=t_ranges.get)
print(f"   Largest range: {t_max_axis} axis ({t_ranges[t_max_axis]:.3f}m)")

# Check pelvis position relative to other joints
t_pelvis_z_rank = np.sum(T_POSE_J_ABSOLUTE[:, 2] < T_POSE_J_ABSOLUTE[0, 2])
t_pelvis_y_rank = np.sum(T_POSE_J_ABSOLUTE[:, 1] < T_POSE_J_ABSOLUTE[0, 1])
print(f"   Pelvis Z rank: {t_pelvis_z_rank}/52 (lower = closer to ground in Z-up)")
print(f"   Pelvis Y rank: {t_pelvis_y_rank}/52 (lower = closer to ground in Y-up)")

print(f"\n📊 A-Pose (Exported from Blender) Coordinate System:")
print(f"   Pelvis: {A_POSE_J_ABSOLUTE[0]}")
print(f"   X range: [{A_POSE_J_ABSOLUTE[:, 0].min():.3f}, {A_POSE_J_ABSOLUTE[:, 0].max():.3f}]")
print(f"   Y range: [{A_POSE_J_ABSOLUTE[:, 1].min():.3f}, {A_POSE_J_ABSOLUTE[:, 1].max():.3f}]")
print(f"   Z range: [{A_POSE_J_ABSOLUTE[:, 2].min():.3f}, {A_POSE_J_ABSOLUTE[:, 2].max():.3f}]")

a_ranges = {
    'X': abs(A_POSE_J_ABSOLUTE[:, 0].max() - A_POSE_J_ABSOLUTE[:, 0].min()),
    'Y': abs(A_POSE_J_ABSOLUTE[:, 1].max() - A_POSE_J_ABSOLUTE[:, 1].min()),
    'Z': abs(A_POSE_J_ABSOLUTE[:, 2].max() - A_POSE_J_ABSOLUTE[:, 2].min())
}
a_max_axis = max(a_ranges, key=a_ranges.get)
print(f"   Largest range: {a_max_axis} axis ({a_ranges[a_max_axis]:.3f}m)")

a_pelvis_z_rank = np.sum(A_POSE_J_ABSOLUTE[:, 2] < A_POSE_J_ABSOLUTE[0, 2])
a_pelvis_y_rank = np.sum(A_POSE_J_ABSOLUTE[:, 1] < A_POSE_J_ABSOLUTE[0, 1])
print(f"   Pelvis Z rank: {a_pelvis_z_rank}/52")
print(f"   Pelvis Y rank: {a_pelvis_y_rank}/52")

print(f"\n🔍 Coordinate System Comparison:")
print(f"   T-pose up axis: {t_max_axis} (range: {t_ranges[t_max_axis]:.3f}m)")
print(f"   A-pose up axis: {a_max_axis} (range: {a_ranges[a_max_axis]:.3f}m)")

if t_max_axis != a_max_axis:
    print(f"\n   ⚠️  WARNING: Different up axes detected!")
    print(f"      T-pose uses {t_max_axis}-up, A-pose uses {a_max_axis}-up")
    print(f"      This suggests a coordinate system mismatch!")

# Check if Y and Z are swapped
print(f"\n🔍 Checking for Y/Z Swap:")
t_pelvis_yz = T_POSE_J_ABSOLUTE[0, [1, 2]]
a_pelvis_yz = A_POSE_J_ABSOLUTE[0, [1, 2]]
a_pelvis_yz_swapped = A_POSE_J_ABSOLUTE[0, [2, 1]]  # Swap Y and Z

print(f"   T-pose Pelvis [Y, Z]: {t_pelvis_yz}")
print(f"   A-pose Pelvis [Y, Z]: {a_pelvis_yz}")
print(f"   A-pose Pelvis [Z, Y] (swapped): {a_pelvis_yz_swapped}")

# Check if swapping Y/Z makes them closer
diff_original = np.linalg.norm(t_pelvis_yz - a_pelvis_yz)
diff_swapped = np.linalg.norm(t_pelvis_yz - a_pelvis_yz_swapped)

print(f"   Difference (original): {diff_original:.6f}m")
print(f"   Difference (Y/Z swapped): {diff_swapped:.6f}m")

if diff_swapped < diff_original:
    print(f"   ⚠️  Y/Z might be swapped in A-pose export!")

# Check a few more joints
print(f"\n🔍 Checking Multiple Joints for Pattern:")
for i in [0, 1, 3, 33]:  # Pelvis, L_Hip, Spine1, L_Shoulder
    joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
    t_pos = T_POSE_J_ABSOLUTE[i]
    a_pos = A_POSE_J_ABSOLUTE[i]
    a_pos_swapped = np.array([a_pos[0], a_pos[2], a_pos[1]])  # Swap Y and Z
    
    diff_orig = np.linalg.norm(t_pos - a_pos)
    diff_swap = np.linalg.norm(t_pos - a_pos_swapped)
    
    print(f"\n   {joint_name}:")
    print(f"      T-pose: {t_pos}")
    print(f"      A-pose: {a_pos}")
    print(f"      A-pose (Y/Z swapped): {a_pos_swapped}")
    print(f"      Diff (original): {diff_orig:.6f}m")
    print(f"      Diff (Y/Z swapped): {diff_swap:.6f}m")
    if diff_swap < diff_orig:
        print(f"      → Y/Z swap makes it closer!")

print("\n" + "="*80)
print("💡 Analysis:")
print("   If Y/Z are swapped, the export script might be reading")
print("   coordinates in the wrong order (Y, Z instead of X, Y, Z).")
print("   Or Blender's edit_bones.head might be in a different space.")
print("="*80)

