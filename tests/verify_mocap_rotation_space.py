"""
Verify what rest pose the mocap rotations are relative to.
Test: Apply zero rotations - what pose do we get?
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from retarget import forward_kinematics, J_ABSOLUTE as CURRENT_J_ABSOLUTE, SMPL_OFFSETS

print("="*80)
print("Verifying Mocap Rotation Space")
print("="*80)

# Load a test mocap file
test_dir = Path(__file__).parent.parent / 'data' / 'test'
npz_files = list(test_dir.glob('*.npz'))

if not npz_files:
    print("❌ No NPZ files found")
    sys.exit(1)

npz_path = npz_files[0]
print(f"\n📁 Testing with: {npz_path.name}")

data = np.load(str(npz_path))
poses = data['poses']
trans = data['trans']

print(f"✓ Loaded mocap: {len(poses)} frames")

# Test 1: What happens with zero rotations?
print(f"\n🧪 Test 1: Zero Rotations (should give rest pose)")
zero_poses = np.zeros_like(poses[0])  # All rotations zero
zero_trans = np.array([0.0, 0.0, 0.0])  # No translation

fk_zero = forward_kinematics(zero_poses, zero_trans)
print(f"   FK output with zero rotations:")
print(f"   Pelvis: {fk_zero[0]}")
print(f"   L_Shoulder: {fk_zero[33]}")
print(f"   R_Shoulder: {fk_zero[34]}")

print(f"\n   Current J_ABSOLUTE (A-pose):")
print(f"   Pelvis: {CURRENT_J_ABSOLUTE[0]}")
print(f"   L_Shoulder: {CURRENT_J_ABSOLUTE[33]}")
print(f"   R_Shoulder: {CURRENT_J_ABSOLUTE[34]}")

# Check if zero rotations give us the current rest pose
pelvis_diff = np.linalg.norm(fk_zero[0] - CURRENT_J_ABSOLUTE[0])
l_shoulder_diff = np.linalg.norm(fk_zero[33] - CURRENT_J_ABSOLUTE[33])

print(f"\n   Difference from current J_ABSOLUTE:")
print(f"   Pelvis: {pelvis_diff:.6f}m")
print(f"   L_Shoulder: {l_shoulder_diff:.6f}m")

if pelvis_diff < 0.001 and l_shoulder_diff < 0.001:
    print(f"\n   ✅ Zero rotations give current rest pose (A-pose)")
    print(f"      This means: Mocap rotations are relative to A-pose!")
else:
    print(f"\n   ⚠️  Zero rotations do NOT give current rest pose")
    print(f"      This means: Mocap rotations might be relative to different pose")

# Test 2: What does frame 0 actually look like?
print(f"\n🧪 Test 2: Frame 0 of Mocap")
fk_frame0 = forward_kinematics(poses[0], trans[0])
print(f"   FK output for frame 0:")
print(f"   Pelvis: {fk_frame0[0]}")
print(f"   L_Shoulder: {fk_frame0[33]}")

print(f"\n   Frame 0 vs Zero rotations:")
pelvis_diff_f0 = np.linalg.norm(fk_frame0[0] - fk_zero[0])
l_shoulder_diff_f0 = np.linalg.norm(fk_frame0[33] - fk_zero[33])

print(f"   Pelvis difference: {pelvis_diff_f0:.6f}m")
print(f"   L_Shoulder difference: {l_shoulder_diff_f0:.6f}m")

if pelvis_diff_f0 < 0.01 and l_shoulder_diff_f0 < 0.01:
    print(f"   → Frame 0 is very close to rest pose (minimal rotation)")
else:
    print(f"   → Frame 0 differs from rest pose (has rotation)")

# Test 3: Compare to hardcoded T-pose
print(f"\n🧪 Test 3: Compare to Hardcoded T-pose")
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

pelvis_diff_tpose = np.linalg.norm(fk_zero[0] - T_POSE_J_ABSOLUTE[0])
l_shoulder_diff_tpose = np.linalg.norm(fk_zero[33] - T_POSE_J_ABSOLUTE[33])

print(f"   Zero rotations vs T-pose:")
print(f"   Pelvis difference: {pelvis_diff_tpose:.6f}m")
print(f"   L_Shoulder difference: {l_shoulder_diff_tpose:.6f}m")

if pelvis_diff_tpose < 0.001 and l_shoulder_diff_tpose < 0.001:
    print(f"   ✅ Zero rotations give T-pose")
    print(f"      This means: Mocap rotations are relative to T-pose!")
else:
    print(f"   ⚠️  Zero rotations do NOT give T-pose")

print("\n" + "="*80)
print("Conclusion:")
print("   If zero rotations give current J_ABSOLUTE (A-pose):")
print("      → Rotations are relative to A-pose (current rest pose)")
print("   If zero rotations give T-pose:")
print("      → Rotations are relative to T-pose (original rest pose)")
print("="*80)

