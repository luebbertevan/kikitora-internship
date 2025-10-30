"""
Debug: Compare FK computation for frame 1 vs what's actually in the GLB
"""
import numpy as np
from pathlib import Path
import sys

# Load FK logic
from numpy.typing import NDArray

SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

def axis_angle_to_rotation_matrix(axis_angle: NDArray) -> NDArray:
    angle: float = np.linalg.norm(axis_angle)
    if angle < 1e-6:
        return np.eye(3)
    axis: NDArray = axis_angle / angle
    K: NDArray = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    R: NDArray = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R

def forward_kinematics(poses: NDArray, trans: NDArray, smpl_offsets: NDArray) -> NDArray:
    num_joints = len(SMPL_H_PARENTS)
    joint_positions = np.zeros((num_joints, 3))
    pose_params = poses.reshape(-1, 3)
    global_transforms = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        rot_mat = axis_angle_to_rotation_matrix(pose_params[i]) if i < len(pose_params) else np.eye(3)
        local_transform = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = smpl_offsets[i]
        
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions

# Load data
npz_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/extracted/ACCAD/Female1Gestures_c3d/D1 - Urban 1_poses.npz")
ref_path = Path("src/scripts/target_reference.npz")

input_data = np.load(npz_path)
poses = input_data['poses']
trans = input_data['trans']

ref_data = np.load(ref_path)
SMPL_OFFSETS = ref_data['SMPL_OFFSETS']

print("="*80)
print("FK COMPUTATION: Frame 0 vs Frame 1")
print("="*80)

# Frame 0 (should be A-pose)
zero_poses = np.zeros((52, 3)).flatten()
fk_frame0 = forward_kinematics(zero_poses, trans[0], SMPL_OFFSETS)

# Frame 1
fk_frame1 = forward_kinematics(poses[1], trans[1], SMPL_OFFSETS)

print(f"\nInput trans[0]: {trans[0]}")
print(f"Input trans[1]: {trans[1]}")
print(f"Input poses[1] (first 9 values, 3 joints): {poses[1][:9]}\n")

# Analyze first few joints
for i in [0, 1, 2, 3]:
    parent_idx = SMPL_H_PARENTS[i]
    parent_name = JOINT_NAMES[parent_idx] if parent_idx >= 0 else "None"
    
    print(f"Joint {i} ({JOINT_NAMES[i]:20s}) - Parent: {parent_name}")
    print(f"  FK Frame 0: [{fk_frame0[i][0]:8.3f}, {fk_frame0[i][1]:8.3f}, {fk_frame0[i][2]:8.3f}]")
    print(f"  FK Frame 1: [{fk_frame1[i][0]:8.3f}, {fk_frame1[i][1]:8.3f}, {fk_frame1[i][2]:8.3f}]")
    
    change = fk_frame1[i] - fk_frame0[i]
    change_cm = np.linalg.norm(change) * 100
    print(f"  FK Change:  [{change[0]:8.3f}, {change[1]:8.3f}, {change[2]:8.3f}] ({change_cm:.3f} cm)")
    
    if parent_idx >= 0:
        rel_0 = np.linalg.norm(fk_frame0[i] - fk_frame0[parent_idx]) * 100
        rel_1 = np.linalg.norm(fk_frame1[i] - fk_frame1[parent_idx]) * 100
        print(f"  FK Distance to parent: F0={rel_0:.3f}cm, F1={rel_1:.3f}cm")
    
    print()
