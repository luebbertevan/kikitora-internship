"""
M1 Tool: Visualize Frame 0 of AMASS animations
Shows the starting pose to help define A-pose requirements
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation

# Copy the constants and functions we need (instead of importing)
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

J_ABSOLUTE = np.array([
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
])

SMPL_OFFSETS = np.zeros((52, 3))
for i in range(52):
    parent_idx = SMPL_H_PARENTS[i]
    if parent_idx == -1:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i]
    else:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]

def axis_angle_to_rotation_matrix(axis_angle):
    """Convert axis-angle to rotation matrix"""
    angle = np.linalg.norm(axis_angle)
    if angle < 1e-6:
        return np.eye(3)
    axis = axis_angle / angle
    return Rotation.from_rotvec(axis_angle).as_matrix()

def forward_kinematics(poses, trans):
    """Compute joint positions from poses using forward kinematics"""
    num_joints = len(SMPL_H_PARENTS)
    joint_positions = np.zeros((num_joints, 3))
    pose_params = poses.reshape(-1, 3)
    global_transforms = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        if i < len(pose_params):
            rot_mat = axis_angle_to_rotation_matrix(pose_params[i])
        else:
            rot_mat = np.eye(3)
        
        local_transform = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = SMPL_OFFSETS[i]
        
        parent_idx = SMPL_H_PARENTS[i]
        if parent_idx == -1:
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions

def visualize_frame0(npz_path, save_path=None):
    """
    Visualize frame 0 pose from an AMASS .npz file
    
    Args:
        npz_path: Path to .npz file
        save_path: Optional path to save visualization
    """
    # Load data
    data = np.load(npz_path)
    poses = data['poses']
    trans = data['trans']
    
    # Get frame 0
    frame_0_poses = poses[0]
    frame_0_trans = trans[0]
    
    print(f"Visualizing: {Path(npz_path).name}")
    print(f"Frame 0 translation: {frame_0_trans}")
    
    # Compute joint positions using FK
    joint_positions = forward_kinematics(frame_0_poses, frame_0_trans)
    
    # Create visualization
    fig = plt.figure(figsize=(15, 10))
    
    # 4 views: front, side, top, 3D interactive
    views = [
        (0, 90, "Front View"),
        (0, 0, "Side View"),
        (90, 0, "Top View"),
        (20, 45, "Perspective View")
    ]
    
    for idx, (elev, azim, title) in enumerate(views):
        ax = fig.add_subplot(2, 2, idx + 1, projection='3d')
        
        # Plot skeleton connections
        for i, parent_idx in enumerate(SMPL_H_PARENTS):
            if parent_idx != -1:
                xs = [joint_positions[parent_idx, 0], joint_positions[i, 0]]
                ys = [joint_positions[parent_idx, 1], joint_positions[i, 1]]
                zs = [joint_positions[parent_idx, 2], joint_positions[i, 2]]
                ax.plot(xs, ys, zs, 'b-', linewidth=2, alpha=0.6)
        
        # Plot joints
        ax.scatter(joint_positions[:, 0], joint_positions[:, 1], joint_positions[:, 2],
                  c='red', s=30, alpha=0.8)
        
        # Highlight key joints
        key_joints = [0, 15, 16, 17, 20, 21]  # Pelvis, Head, Shoulders, Wrists
        ax.scatter(joint_positions[key_joints, 0],
                   joint_positions[key_joints, 1],
                   joint_positions[key_joints, 2],
                   c='green', s=80, alpha=0.9, marker='o')
        
        # Set view
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Set equal aspect
        all_positions = joint_positions
        max_range = np.array([all_positions[:, 0].max() - all_positions[:, 0].min(),
                            all_positions[:, 1].max() - all_positions[:, 1].min(),
                            all_positions[:, 2].max() - all_positions[:, 2].min()]).max() / 2.0
        mid_x = (all_positions[:, 0].max() + all_positions[:, 0].min()) * 0.5
        mid_y = (all_positions[:, 1].max() + all_positions[:, 1].min()) * 0.5
        mid_z = (all_positions[:, 2].max() + all_positions[:, 2].min()) * 0.5
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(f'Frame 0 Pose: {Path(npz_path).name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved to: {save_path}")
    
    plt.show()

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python visualize_frame0.py <npz_file_path> [save_image_path]")
        print("\nExample:")
        print("  python visualize_frame0.py data/extracted/ACCAD/.../some_poses.npz")
        print("  python visualize_frame0.py data.extracted/file.npz output/frame0.png")
        sys.exit(1)
    
    npz_path = Path(sys.argv[1])
    save_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not npz_path.exists():
        print(f"Error: File not found: {npz_path}")
        sys.exit(1)
    
    visualize_frame0(npz_path, save_path)

if __name__ == "__main__":
    main()

