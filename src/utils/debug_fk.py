"""
Debug: Check what forward_kinematics computes vs reference
"""
import numpy as np
from pathlib import Path
from numpy.typing import NDArray

# Load the FK function logic
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Load reference and offsets
ref_data = np.load("src/scripts/target_reference.npz")
J_ABSOLUTE = ref_data['J_ABSOLUTE']
SMPL_OFFSETS = ref_data['SMPL_OFFSETS']

def axis_angle_to_rotation_matrix(axis_angle: NDArray) -> NDArray:
    """Convert axis-angle to rotation matrix"""
    angle: float = np.linalg.norm(axis_angle)
    if angle < 1e-6:
        return np.eye(3)
    
    axis: NDArray = axis_angle / angle
    K: NDArray = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    R: NDArray = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R

def forward_kinematics(poses: NDArray, trans: NDArray) -> NDArray:
    """Compute forward kinematics"""
    num_joints = len(SMPL_H_PARENTS)
    joint_positions = np.zeros((num_joints, 3))
    pose_params = poses.reshape(-1, 3)
    global_transforms = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        rot_mat = axis_angle_to_rotation_matrix(pose_params[i]) if i < len(pose_params) else np.eye(3)
        local_transform = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = SMPL_OFFSETS[i]
        
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions

# Test: zero poses should give us A-pose
zero_poses = np.zeros((52, 3)).flatten()
zero_trans = np.zeros(3)

fk_joints = forward_kinematics(zero_poses, zero_trans)

print("Comparison: FK(zero_poses, zero_trans) vs J_ABSOLUTE (A-pose reference)\n")
print(f"FK Pelvis:    [{fk_joints[0][0]:8.3f}, {fk_joints[0][1]:8.3f}, {fk_joints[0][2]:8.3f}]")
print(f"Ref Pelvis:   [{J_ABSOLUTE[0][0]:8.3f}, {J_ABSOLUTE[0][1]:8.3f}, {J_ABSOLUTE[0][2]:8.3f}]")
print(f"Diff Pelvis:  {np.linalg.norm(fk_joints[0] - J_ABSOLUTE[0])*100:.3f} cm\n")

print(f"FK Spine1:    [{fk_joints[3][0]:8.3f}, {fk_joints[3][1]:8.3f}, {fk_joints[3][2]:8.3f}]")
print(f"Ref Spine1:   [{J_ABSOLUTE[3][0]:8.3f}, {J_ABSOLUTE[3][1]:8.3f}, {J_ABSOLUTE[3][2]:8.3f}]")
print(f"Diff Spine1:  {np.linalg.norm(fk_joints[3] - J_ABSOLUTE[3])*100:.3f} cm\n")

max_diff = 0
for i in range(52):
    diff = np.linalg.norm(fk_joints[i] - J_ABSOLUTE[i])
    if diff > max_diff:
        max_diff = diff
        if diff > 0.1:
            print(f"Joint {i} diff: {diff*100:.3f} cm")

print(f"\nMax difference: {max_diff*100:.3f} cm")
