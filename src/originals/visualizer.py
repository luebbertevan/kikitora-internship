import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation

# SMPL+H kinematic tree from the model
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# ALL 52 joint positions (absolute) from J_regressor * v_template
J_ABSOLUTE = np.array([
    [-0.001795, -0.223333, 0.028219],  # 0
    [0.067725, -0.314740, 0.021404],  # 1
    [-0.069466, -0.313855, 0.023899],  # 2
    [-0.004328, -0.114370, 0.001523],  # 3
    [0.102001, -0.689938, 0.016908],  # 4
    [-0.107756, -0.696424, 0.015049],  # 5
    [0.001159, 0.020810, 0.002615],  # 6
    [0.088406, -1.087899, -0.026785],  # 7
    [-0.091982, -1.094839, -0.027263],  # 8
    [0.002616, 0.073732, 0.028040],  # 9
    [0.114764, -1.143690, 0.092503],  # 10
    [-0.117354, -1.142983, 0.096085],  # 11
    [-0.000162, 0.287603, -0.014817],  # 12
    [0.081461, 0.195482, -0.006050],  # 13
    [-0.079143, 0.192565, -0.010575],  # 14
    [0.004990, 0.352572, 0.036532],  # 15
    [0.172438, 0.225951, -0.014918],  # 16
    [-0.175155, 0.225116, -0.019719],  # 17
    [0.432050, 0.213179, -0.042374],  # 18
    [-0.428897, 0.211787, -0.041119],  # 19
    [0.681284, 0.222165, -0.043545],  # 20 - Right wrist
    [-0.684196, 0.219560, -0.046679],  # 21 - Left wrist
    [0.783767, 0.213183, -0.022054],  # 22
    [0.815568, 0.216115, -0.018788],  # 23
    [0.837963, 0.214387, -0.018140],  # 24
    [0.791063, 0.216050, -0.044867],  # 25
    [0.821578, 0.217270, -0.048936],  # 26
    [0.845128, 0.215785, -0.052425],  # 27
    [0.765890, 0.208316, -0.084165],  # 28
    [0.781693, 0.207917, -0.094992],  # 29
    [0.797572, 0.206667, -0.105123],  # 30
    [0.779095, 0.213415, -0.067855],  # 31
    [0.806930, 0.215059, -0.072228],  # 32
    [0.829592, 0.213672, -0.078705],  # 33
    [0.723217, 0.202218, -0.017008],  # 34
    [0.740918, 0.203986, 0.007192],  # 35
    [0.762150, 0.200379, 0.022060],  # 36
    [-0.783494, 0.210911, -0.022044],  # 37 - Left hand starts
    [-0.815675, 0.213810, -0.019676],  # 38
    [-0.837971, 0.212032, -0.020059],  # 39
    [-0.791352, 0.214082, -0.045896],  # 40
    [-0.821700, 0.215536, -0.050057],  # 41
    [-0.844837, 0.214110, -0.053971],  # 42
    [-0.767226, 0.205917, -0.086044],  # 43
    [-0.782858, 0.205594, -0.097170],  # 44
    [-0.798573, 0.204555, -0.107284],  # 45
    [-0.779985, 0.211294, -0.069581],  # 46
    [-0.807581, 0.213016, -0.074152],  # 47
    [-0.829999, 0.211622, -0.081116],  # 48
    [-0.722013, 0.199415, -0.016553],  # 49
    [-0.739452, 0.200249, 0.007932],  # 50
    [-0.760794, 0.195263, 0.022366],  # 51
])

# Compute RELATIVE offsets from parent to child for ALL joints
SMPL_OFFSETS = np.zeros((52, 3))
for i in range(52):
    parent_idx = SMPL_H_PARENTS[i]
    if parent_idx == -1:
        SMPL_OFFSETS[i] = J_ABSOLUTE[i]  # Root uses absolute position
    else:
        # Relative offset = child position - parent position
        SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]

print("Sample relative offsets:")
print(f"Joint 0 (root): {SMPL_OFFSETS[0]}")
print(f"Joint 21 (left wrist, parent 19): {SMPL_OFFSETS[21]}")
print(f"Joint 37 (left hand joint, parent 21): {SMPL_OFFSETS[37]}")

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
    
    # Reshape poses: (156,) -> (52, 3) for 52 joints
    pose_params = poses.reshape(-1, 3)
    
    # Global transformation matrices
    global_transforms = [np.eye(4) for _ in range(num_joints)]
    
    for i in range(num_joints):
        # Local rotation from axis-angle
        if i < len(pose_params):
            rot_mat = axis_angle_to_rotation_matrix(pose_params[i])
        else:
            rot_mat = np.eye(3)
        
        # Local transform
        local_transform = np.eye(4)
        local_transform[:3, :3] = rot_mat
        local_transform[:3, 3] = SMPL_OFFSETS[i]
        
        # Global transform
        parent_idx = SMPL_H_PARENTS[i]
        if parent_idx == -1:
            # Root joint - apply global translation
            global_transforms[i] = local_transform
            global_transforms[i][:3, 3] += trans
        else:
            global_transforms[i] = global_transforms[parent_idx] @ local_transform
        
        joint_positions[i] = global_transforms[i][:3, 3]
    
    return joint_positions

# Load data
file_path = r"C:\Users\Astrid\data\AMASS\raw\EyesJapanDataset\Eyes_Japan_Dataset\aita\accident-04-damage right leg-aita_poses.npz"
data = np.load(file_path)

poses = data['poses']
trans = data['trans']
framerate = float(data['mocap_framerate'])

print(f"\nLoaded animation: {len(poses)} frames at {framerate} fps ({len(poses)/framerate:.2f} seconds)")
print(f"Pose shape: {poses.shape}")
print("Computing joint positions... (this may take a moment)")

# Compute joint positions for all frames
frame_skip = 2  # Process every 2nd frame for speed
frame_indices = range(0, len(poses), frame_skip)
joint_positions_all = []

for idx in frame_indices:
    jp = forward_kinematics(poses[idx], trans[idx])
    joint_positions_all.append(jp)
    if idx % 360 == 0:
        print(f"  Processed frame {idx}/{len(poses)}")

joint_positions_all = np.array(joint_positions_all)
print("Done! Starting visualization...")

# Create figure
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Initialize plot elements
lines = []
for i, parent in enumerate(SMPL_H_PARENTS):
    if parent != -1:
        line, = ax.plot([], [], [], 'b-', linewidth=2)
        lines.append((i, parent, line))

# Joint markers
joints_scatter = ax.scatter([], [], [], c='red', s=20)

# Set axis properties
ax.set_xlabel('X (meters)')
ax.set_ylabel('Y (meters)')
ax.set_zlabel('Z (meters)')
ax.set_title(f'Frame: 0 / {len(joint_positions_all)} | Time: 0.00s / {len(poses)/framerate:.2f}s')

# Set fixed axis limits
all_positions = joint_positions_all.reshape(-1, 3)
margin = 0.5
ax.set_xlim(all_positions[:, 0].min() - margin, all_positions[:, 0].max() + margin)
ax.set_ylim(all_positions[:, 1].min() - margin, all_positions[:, 1].max() + margin)
ax.set_zlim(all_positions[:, 2].min() - margin, all_positions[:, 2].max() + margin)

def update(frame_idx):
    """Update function for animation"""
    joints = joint_positions_all[frame_idx]
    
    # Update skeleton lines
    for i, parent, line in lines:
        line.set_data([joints[parent, 0], joints[i, 0]], 
                      [joints[parent, 1], joints[i, 1]])
        line.set_3d_properties([joints[parent, 2], joints[i, 2]])
    
    # Update joint markers
    joints_scatter._offsets3d = (joints[:, 0], joints[:, 1], joints[:, 2])
    
    # Update title
    actual_frame = frame_idx * frame_skip
    time = actual_frame / framerate
    ax.set_title(f'Frame: {actual_frame} / {len(poses)} | Time: {time:.2f}s / {len(poses)/framerate:.2f}s')
    
    return lines + [joints_scatter]

# Create animation
anim = FuncAnimation(fig, update, frames=len(joint_positions_all), 
                     interval=1000/(framerate/frame_skip), blit=False, repeat=True)

plt.tight_layout()
plt.show()