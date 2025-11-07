"""
Explain why using A-pose J_ABSOLUTE for retargeting makes sense.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import SMPL_H_PARENTS, JOINT_NAMES, forward_kinematics

print("="*80)
print("Why Using A-Pose J_ABSOLUTE for Retargeting Makes Sense")
print("="*80)

# Load A-pose
apose_npz_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
if not apose_npz_path.exists():
    print(f"❌ A-pose NPZ not found")
    sys.exit(1)

apose_data = np.load(str(apose_npz_path))
A_POSE_J_ABSOLUTE = apose_data['J_ABSOLUTE']
A_POSE_SMPL_OFFSETS = apose_data.get('SMPL_OFFSETS', None)

if A_POSE_SMPL_OFFSETS is None:
    # Compute if not in NPZ
    A_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i]
        else:
            A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i] - A_POSE_J_ABSOLUTE[parent_idx]

print(f"\n📊 A-Pose Armature Description:")
print(f"   J_ABSOLUTE: Joint positions in A-pose rest pose")
print(f"   SMPL_OFFSETS: Bone lengths/directions computed from A-pose")
print(f"   Shape: {A_POSE_J_ABSOLUTE.shape}")

print(f"\n💡 How Retargeting Works:")
print(f"   1. Forward Kinematics uses SMPL_OFFSETS (bone lengths)")
print(f"   2. Mocap 'poses' (rotations) are applied to these bone lengths")
print(f"   3. Mocap 'trans' (root translation) moves the pelvis")
print(f"   4. Result: Joint positions computed using A-pose bone lengths")

print(f"\n🔍 What This Means:")
print(f"   ✅ You're retargeting onto the A-pose armature")
print(f"   ✅ Bone lengths come from your manually created A-pose")
print(f"   ✅ Rest pose is A-pose (not T-pose)")
print(f"   ✅ Mocap rotations will be applied relative to A-pose rest pose")

print(f"\n⚠️  Important Consideration:")
print(f"   Mocap rotations might be relative to T-pose (original mocap rest pose)")
print(f"   But you're applying them to A-pose bone lengths")
print(f"   This is why M4 (setting frame 0 to A-pose) is important!")
print(f"   Frame 0 override will align the starting pose correctly")

print(f"\n✅ Conclusion:")
print(f"   Using A-pose J_ABSOLUTE makes perfect sense because:")
print(f"   1. It defines the armature you want to retarget onto")
print(f"   2. SMPL_OFFSETS computed from it give you the correct bone lengths")
print(f"   3. FK will use these bone lengths for all frames")
print(f"   4. This is exactly what 'retargeting onto A-pose armature' means!")

print("\n" + "="*80)

