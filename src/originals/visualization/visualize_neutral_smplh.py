import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider

# SMPL+H kinematic tree (parent indices for each joint)
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Joint names for reference
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

# Load the SMPL+H model
model_path = r"C:\Users\Astrid\Downloads\smplh\neutral\model.npz"
print(f"Loading model from: {model_path}")
model = np.load(model_path, allow_pickle=True)

# Extract joint positions using J_regressor
J_regressor = model['J_regressor']
v_template = model['v_template']

# Compute all 52 joint positions in T-pose
J_ABSOLUTE = J_regressor.dot(v_template)

print(f"Computed {len(J_ABSOLUTE)} joint positions")

# Create figure with subplots for different views
fig = plt.figure(figsize=(18, 6))

# Front view
ax1 = fig.add_subplot(131, projection='3d')
ax1.set_title('Front View', fontweight='bold')

# Side view
ax2 = fig.add_subplot(132, projection='3d')
ax2.set_title('Side View', fontweight='bold')

# Top view
ax3 = fig.add_subplot(133, projection='3d')
ax3.set_title('Top View', fontweight='bold')

axes = [ax1, ax2, ax3]
view_angles = [(0, 90), (0, 0), (90, 0)]  # (elevation, azimuth)

for ax, (elev, azim) in zip(axes, view_angles):
    # Plot skeleton connections
    for i, parent_idx in enumerate(SMPL_H_PARENTS):
        if parent_idx != -1:
            xs = [J_ABSOLUTE[parent_idx, 0], J_ABSOLUTE[i, 0]]
            ys = [J_ABSOLUTE[parent_idx, 1], J_ABSOLUTE[i, 1]]
            zs = [J_ABSOLUTE[parent_idx, 2], J_ABSOLUTE[i, 2]]
            ax.plot(xs, ys, zs, 'b-', linewidth=2, alpha=0.7)
    
    # Plot joint positions
    ax.scatter(J_ABSOLUTE[:, 0], J_ABSOLUTE[:, 1], J_ABSOLUTE[:, 2], 
               c='red', s=25, alpha=0.8, edgecolors='darkred')
    
    # Highlight key joints
    key_joints = [0, 15, 16, 17, 20, 21]  # Pelvis, Head, Shoulders, Wrists
    ax.scatter(J_ABSOLUTE[key_joints, 0], 
               J_ABSOLUTE[key_joints, 1], 
               J_ABSOLUTE[key_joints, 2], 
               c='green', s=60, alpha=0.9, edgecolors='darkgreen', 
               marker='o', linewidths=2)
    
    # Set labels
    ax.set_xlabel('X (m)', fontsize=9)
    ax.set_ylabel('Y (m)', fontsize=9)
    ax.set_zlabel('Z (m)', fontsize=9)
    
    # Set equal aspect ratio
    max_range = np.array([
        J_ABSOLUTE[:, 0].max() - J_ABSOLUTE[:, 0].min(),
        J_ABSOLUTE[:, 1].max() - J_ABSOLUTE[:, 1].min(),
        J_ABSOLUTE[:, 2].max() - J_ABSOLUTE[:, 2].min()
    ]).max() / 2.0
    
    mid_x = (J_ABSOLUTE[:, 0].max() + J_ABSOLUTE[:, 0].min()) * 0.5
    mid_y = (J_ABSOLUTE[:, 1].max() + J_ABSOLUTE[:, 1].min()) * 0.5
    mid_z = (J_ABSOLUTE[:, 2].max() + J_ABSOLUTE[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Set viewing angle
    ax.view_init(elev=elev, azim=azim)
    ax.grid(True, alpha=0.2)

plt.suptitle('SMPL+H T-Pose Visualization - 52 Joints', 
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout()
plt.show()

# Print statistics
print("\n" + "="*60)
print("SMPL+H T-Pose Statistics:")
print("="*60)
print(f"Total joints: {len(J_ABSOLUTE)}")
print(f"X range: [{J_ABSOLUTE[:, 0].min():.3f}, {J_ABSOLUTE[:, 0].max():.3f}] meters")
print(f"Y range: [{J_ABSOLUTE[:, 1].min():.3f}, {J_ABSOLUTE[:, 1].max():.3f}] meters")
print(f"Z range: [{J_ABSOLUTE[:, 2].min():.3f}, {J_ABSOLUTE[:, 2].max():.3f}] meters")
print(f"Total height (Y): {J_ABSOLUTE[:, 1].max() - J_ABSOLUTE[:, 1].min():.3f} meters")
print(f"Arm span (X): {J_ABSOLUTE[:, 0].max() - J_ABSOLUTE[:, 0].min():.3f} meters")