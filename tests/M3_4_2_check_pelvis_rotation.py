"""
M3.4.2: Check Pelvis Rotation Application

This script checks if pelvis rotation in mocap data is causing
the armature to face the ground.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import forward_kinematics, SMPL_H_PARENTS

print("="*80)
print("M3.4.2: Checking Pelvis Rotation in Mocap Data")
print("="*80)

# Find a test NPZ file
test_dir = Path(__file__).parent.parent / 'data' / 'test'
npz_files = list(test_dir.glob('*.npz'))

if not npz_files:
    print("❌ No NPZ files found in data/test_small")
    sys.exit(1)

npz_path = npz_files[0]
print(f"\n📁 Testing with: {npz_path.name}")

# Load mocap data
data = np.load(str(npz_path))
poses = data['poses']  # (num_frames, 156) - 52 joints * 3
trans = data['trans']  # (num_frames, 3)

print(f"\n✓ Loaded mocap data:")
print(f"   Frames: {len(poses)}")
print(f"   Poses shape: {poses.shape}")
print(f"   Trans shape: {trans.shape}")

# Check pelvis rotation (first 3 values of poses)
pelvis_rotations = poses[:, 0:3]  # (num_frames, 3)

print(f"\n📊 Pelvis Rotation Analysis (first 10 frames):")
print(f"   Frame | X rotation | Y rotation | Z rotation | Magnitude")
print(f"   " + "-"*60)

for i in range(min(10, len(poses))):
    rot = pelvis_rotations[i]
    magnitude = np.linalg.norm(rot)
    print(f"   {i:5d} | {rot[0]:11.6f} | {rot[1]:11.6f} | {rot[2]:11.6f} | {magnitude:9.6f}")

# Check if pelvis rotations are non-zero
non_zero_frames = np.sum(np.abs(pelvis_rotations) > 1e-6, axis=0)
max_magnitude = np.max(np.linalg.norm(pelvis_rotations, axis=1))

print(f"\n🔍 Pelvis Rotation Statistics:")
print(f"   Frames with non-zero X rotation: {non_zero_frames[0]}/{len(poses)}")
print(f"   Frames with non-zero Y rotation: {non_zero_frames[1]}/{len(poses)}")
print(f"   Frames with non-zero Z rotation: {non_zero_frames[2]}/{len(poses)}")
print(f"   Maximum rotation magnitude: {max_magnitude:.6f} radians")
print(f"   Maximum rotation magnitude: {np.degrees(max_magnitude):.2f} degrees")

if max_magnitude > 0.1:  # More than ~6 degrees
    print(f"\n   ⚠️  WARNING: Pelvis has significant rotation!")
    print(f"      This could be causing the armature to face the ground.")
    print(f"      Frame 0 rotation: {pelvis_rotations[0]} ({np.linalg.norm(pelvis_rotations[0]):.6f} rad)")
else:
    print(f"\n   ✅ Pelvis rotation is small (likely not the issue)")

# Check pelvis translation
print(f"\n📊 Pelvis Translation (first 10 frames):")
print(f"   Frame | X trans | Y trans | Z trans")
print(f"   " + "-"*40)

for i in range(min(10, len(trans))):
    t = trans[i]
    print(f"   {i:5d} | {t[0]:7.3f} | {t[1]:7.3f} | {t[2]:7.3f}")

# Test: What happens if we set pelvis rotation to zero?
print(f"\n🧪 Testing: What if pelvis rotation is zero?")

# Test frame 0 with zero pelvis rotation
poses_zero_rot = poses.copy()
poses_zero_rot[:, 0:3] = 0.0  # Zero out pelvis rotation

# Compute FK with original and zero rotation
joints_original = forward_kinematics(poses[0], trans[0])
joints_zero_rot = forward_kinematics(poses_zero_rot[0], trans[0])

pelvis_original = joints_original[0]
pelvis_zero_rot = joints_zero_rot[0]

print(f"\n   Frame 0 pelvis position with original rotation: {pelvis_original}")
print(f"   Frame 0 pelvis position with zero rotation:     {pelvis_zero_rot}")
print(f"   Difference: {pelvis_zero_rot - pelvis_original}")

# Check if pelvis rotation affects the overall orientation
# by looking at spine direction
spine1_original = joints_original[3] - joints_original[0]  # Spine1 relative to pelvis
spine1_zero_rot = joints_zero_rot[3] - joints_zero_rot[0]

spine1_original_norm = spine1_original / np.linalg.norm(spine1_original)
spine1_zero_rot_norm = spine1_zero_rot / np.linalg.norm(spine1_zero_rot)

angle_diff = np.arccos(np.clip(np.dot(spine1_original_norm, spine1_zero_rot_norm), -1, 1))
print(f"\n   Spine direction change: {np.degrees(angle_diff):.2f} degrees")

if angle_diff > 0.1:  # More than ~6 degrees
    print(f"   ⚠️  Pelvis rotation significantly affects orientation!")
else:
    print(f"   ✅ Pelvis rotation has minimal effect on orientation")

print("\n" + "="*80)
print("Next steps:")
print("  1. If pelvis rotation is significant, test setting it to zero")
print("  2. Check if coordinate system transformation is needed")
print("  3. Compare to reference GLB orientation")
print("="*80)

