"""
Check what coordinate system retarget.py expects and uses.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import J_ABSOLUTE, SMPL_OFFSETS, forward_kinematics

print("="*80)
print("Checking retarget.py Coordinate System")
print("="*80)

# Check hardcoded T-pose J_ABSOLUTE
print(f"\n📊 Hardcoded T-pose J_ABSOLUTE (from retarget.py):")
print(f"   Pelvis: {J_ABSOLUTE[0]}")
print(f"   X range: [{J_ABSOLUTE[:, 0].min():.3f}, {J_ABSOLUTE[:, 0].max():.3f}]")
print(f"   Y range: [{J_ABSOLUTE[:, 1].min():.3f}, {J_ABSOLUTE[:, 1].max():.3f}]")
print(f"   Z range: [{J_ABSOLUTE[:, 2].min():.3f}, {J_ABSOLUTE[:, 2].max():.3f}]")

# Check which axis is up
ranges = {
    'X': abs(J_ABSOLUTE[:, 0].max() - J_ABSOLUTE[:, 0].min()),
    'Y': abs(J_ABSOLUTE[:, 1].max() - J_ABSOLUTE[:, 1].min()),
    'Z': abs(J_ABSOLUTE[:, 2].max() - J_ABSOLUTE[:, 2].min())
}
max_axis = max(ranges, key=ranges.get)
print(f"   Largest range: {max_axis} axis ({ranges[max_axis]:.3f}m)")

# Check pelvis position
pelvis_z_rank = np.sum(J_ABSOLUTE[:, 2] < J_ABSOLUTE[0, 2])
pelvis_y_rank = np.sum(J_ABSOLUTE[:, 1] < J_ABSOLUTE[0, 1])
print(f"   Pelvis Z rank: {pelvis_z_rank}/52")
print(f"   Pelvis Y rank: {pelvis_y_rank}/52")

# Test FK with zero rotations (should give T-pose positions)
print(f"\n🧪 Testing Forward Kinematics:")
zero_poses = np.zeros((52 * 3,), dtype=np.float64)  # All rotations zero
zero_trans = np.array([0.0, 0.0, 0.0], dtype=np.float64)  # No translation

fk_output = forward_kinematics(zero_poses, zero_trans)
print(f"   FK output (zero rotations, zero trans) Pelvis: {fk_output[0]}")
print(f"   Hardcoded J_ABSOLUTE Pelvis: {J_ABSOLUTE[0]}")
print(f"   Difference: {np.linalg.norm(fk_output[0] - J_ABSOLUTE[0]):.6f}m")

if np.allclose(fk_output, J_ABSOLUTE, atol=1e-6):
    print(f"   ✅ FK output matches J_ABSOLUTE (as expected)")
else:
    print(f"   ⚠️  FK output differs from J_ABSOLUTE")

# Check what happens when we use FK output in Blender
print(f"\n💡 How retarget.py uses coordinates:")
print(f"   1. FK computes joint positions from poses + trans")
print(f"   2. Joint positions are assigned directly to Blender Vectors:")
print(f"      bone.head = Vector(joint_positions[i])")
print(f"      empty.location = Vector(joint_positions[i])")
print(f"   3. Blender Vectors expect Z-up coordinate system")
print(f"   4. So FK output must be in Z-up for Blender to work correctly")

# Check if current T-pose is compatible with Blender
print(f"\n🔍 Compatibility Check:")
if max_axis == 'Z':
    print(f"   ✅ T-pose uses Z-up (compatible with Blender)")
elif max_axis == 'Y':
    print(f"   ⚠️  T-pose uses Y-up (NOT compatible with Blender Z-up)")
    print(f"      This would cause issues when assigning to Blender Vectors")
else:
    print(f"   ⚠️  T-pose uses {max_axis}-up (unusual)")

print("\n" + "="*80)
print("Conclusion:")
print("   retarget.py expects FK output to be in Z-up (Blender standard)")
print("   The A-pose export must also be in Z-up to be compatible")
print("="*80)

