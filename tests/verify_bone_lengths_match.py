"""
Verify that SMPL_OFFSETS (bone lengths) are identical between T-pose and A-pose.
They should match exactly since it's the same armature, just different poses.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("="*80)
print("Verifying Bone Lengths Match Between T-pose and A-pose")
print("="*80)

# Hardcoded T-pose J_ABSOLUTE (from original retarget.py)
T_POSE_J_ABSOLUTE = np.array([
    [-0.001795, -0.223333, 0.028219], [0.067725, -0.314740, 0.021404],
    [-0.069466, -0.313855, 0.023899], [-0.004328, -0.114370, 0.001523],
    [0.102001, -0.689938, 0.016908], [-0.107756, -0.696424, 0.015049],
    [0.001159, 0.020810, 0.002615], [0.088406, -1.087899, -0.026785],
    [-0.091982, -1.094839, -0.027263], [0.002616, 0.073732, 0.028040],
    [0.114764, -1.143690, 0.092503], [-0.117354, -1.142983, 0.096085],
    [-0.000162, 0.287603, -0.014817], [0.081461, 0.195482, -0.006050],
    [-0.079143, 0.192565, -0.010575], [0.004990, 0.352572, 0.036532],
    [0.172438, 0.225951, -0.014918], [-0.175155, 0.225116, -0.019719],
    [0.432050, 0.213179, -0.042374], [-0.428897, 0.211787, -0.041119],
    [0.681284, 0.222165, -0.043545], [-0.684196, 0.219560, -0.046679],
    [0.783767, 0.213183, -0.022054], [0.815568, 0.216115, -0.018788],
    [0.837963, 0.214387, -0.018140], [0.791063, 0.216050, -0.044867],
    [0.821578, 0.217270, -0.048936], [0.845128, 0.215785, -0.052425],
    [0.765890, 0.208316, -0.084165], [0.781693, 0.207917, -0.094992],
    [0.797572, 0.206667, -0.105123], [0.779095, 0.213415, -0.067855],
    [0.806930, 0.215059, -0.072228], [0.829592, 0.213672, -0.078705],
    [0.723217, 0.202218, -0.017008], [0.740918, 0.203986, 0.007192],
    [0.762150, 0.200379, 0.022060], [-0.783494, 0.210911, -0.022044],
    [-0.815675, 0.213810, -0.019676], [-0.837971, 0.212032, -0.020059],
    [-0.791352, 0.214082, -0.045896], [-0.821700, 0.215536, -0.050057],
    [-0.844837, 0.214110, -0.053971], [-0.767226, 0.205917, -0.086044],
    [-0.782858, 0.205594, -0.097170], [-0.798573, 0.204555, -0.107284],
    [-0.779985, 0.211294, -0.069581], [-0.807581, 0.213016, -0.074152],
    [-0.829999, 0.211622, -0.081116], [-0.722013, 0.199415, -0.016553],
    [-0.739452, 0.200249, 0.007932], [-0.760794, 0.195263, 0.022366],
], dtype=np.float64)

# Load A-pose
apose_npz_path = Path(__file__).parent.parent / 'data' / 'reference' / 'apose_from_blender.npz'
if not apose_npz_path.exists():
    print(f"❌ A-pose NPZ not found at {apose_npz_path}")
    sys.exit(1)

apose_data = np.load(str(apose_npz_path))
A_POSE_J_ABSOLUTE = apose_data['J_ABSOLUTE']

print(f"\n📊 Loaded A-pose from: {apose_npz_path.name}")

# SMPL_H_PARENTS (needed to compute offsets)
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Compute SMPL_OFFSETS for both
T_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
A_POSE_SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)

for i in range(52):
    parent_idx = int(SMPL_H_PARENTS[i])
    if parent_idx == -1:
        T_POSE_SMPL_OFFSETS[i] = T_POSE_J_ABSOLUTE[i]
        A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i]
    else:
        T_POSE_SMPL_OFFSETS[i] = T_POSE_J_ABSOLUTE[i] - T_POSE_J_ABSOLUTE[parent_idx]
        A_POSE_SMPL_OFFSETS[i] = A_POSE_J_ABSOLUTE[i] - A_POSE_J_ABSOLUTE[parent_idx]

print(f"\n🔍 Comparing SMPL_OFFSETS (Bone Lengths):")
print(f"   {'Joint':<20} {'T-pose Offset':<40} {'A-pose Offset':<40} {'Match'}")
print("   " + "-"*110)

from retarget import JOINT_NAMES

all_match = True
max_diff = 0.0
max_diff_joint = None

for i in range(52):
    joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
    t_offset = T_POSE_SMPL_OFFSETS[i]
    a_offset = A_POSE_SMPL_OFFSETS[i]
    
    # For root (Pelvis), compare magnitudes (position can differ)
    if i == 0:
        t_mag = np.linalg.norm(t_offset)
        a_mag = np.linalg.norm(a_offset)
        diff = abs(t_mag - a_mag)
        matches = diff < 1e-6
    else:
        # For non-root bones, compare the offset vectors directly
        diff = np.linalg.norm(t_offset - a_offset)
        matches = diff < 1e-6
    
    if not matches:
        all_match = False
        if diff > max_diff:
            max_diff = diff
            max_diff_joint = joint_name
    
    # Print first 10 and any mismatches
    if i < 10 or not matches:
        match_str = "✓" if matches else "✗"
        print(f"   {joint_name:<20} {str(t_offset):<40} {str(a_offset):<40} {match_str} {diff:.6e}")

print(f"\n📊 Summary:")
print(f"   All bone lengths match: {'✅ YES' if all_match else '❌ NO'}")
if not all_match:
    print(f"   Maximum difference: {max_diff:.6e} meters ({max_diff*1000:.3f} mm)")
    print(f"   Joint with max difference: {max_diff_joint}")
    print(f"\n   ⚠️  WARNING: Bone lengths differ!")
    print(f"      This suggests the A-pose armature has different bone lengths")
    print(f"      than the T-pose armature. They should be identical.")
else:
    print(f"   ✅ All bone lengths match exactly (as expected)")

# Also check bone length magnitudes (should match for all non-root bones)
print(f"\n🔍 Bone Length Magnitudes (should match for non-root bones):")
print(f"   {'Joint':<20} {'T-pose Length':<20} {'A-pose Length':<20} {'Difference':<20}")
print("   " + "-"*80)

for i in range(52):
    joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
    t_len = np.linalg.norm(T_POSE_SMPL_OFFSETS[i])
    a_len = np.linalg.norm(A_POSE_SMPL_OFFSETS[i])
    diff = abs(t_len - a_len)
    
    if i < 10 or diff > 1e-6:
        print(f"   {joint_name:<20} {t_len:<20.6f} {a_len:<20.6f} {diff:<20.6e}")

print("\n" + "="*80)

