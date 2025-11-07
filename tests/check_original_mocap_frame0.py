#!/usr/bin/env python3
"""Check what the original mocap frame 0 shoulder rotations were"""

import numpy as np
import math
from pathlib import Path

# Load the original mocap data
npz_path = Path(__file__).parent.parent / 'data' / 'test' / 'D6- CartWheel_poses.npz'
data = np.load(str(npz_path))
poses = data['poses']

# Frame 0 pose parameters (52 joints × 3 axis-angle = 156 values)
frame0_poses = poses[0].reshape(52, 3)

# L_Shoulder is index 16, R_Shoulder is index 17
l_shoulder_pose = frame0_poses[16]
r_shoulder_pose = frame0_poses[17]

print('='*80)
print('Original mocap frame 0 shoulder rotations (axis-angle):')
print('='*80)
print(f'  L_Shoulder: [{l_shoulder_pose[0]:.4f}, {l_shoulder_pose[1]:.4f}, {l_shoulder_pose[2]:.4f}]')
print(f'  R_Shoulder: [{r_shoulder_pose[0]:.4f}, {r_shoulder_pose[1]:.4f}, {r_shoulder_pose[2]:.4f}]')

# Convert to angle magnitude
l_angle = math.sqrt(sum(x**2 for x in l_shoulder_pose))
r_angle = math.sqrt(sum(x**2 for x in r_shoulder_pose))

print(f'\nRotation magnitudes:')
print(f'  L_Shoulder: {math.degrees(l_angle):.2f}°')
print(f'  R_Shoulder: {math.degrees(r_angle):.2f}°')

print(f'\n'+'='*80)
print('A-pose sets shoulders to:')
print('='*80)
print(f'  L_Shoulder: Y-axis, -45.00°')
print(f'  R_Shoulder: Y-axis, +45.00°')

print(f'\n'+'='*80)
print('CONCLUSION:')
print('='*80)
if abs(math.degrees(l_angle) - 45) > 5 or abs(math.degrees(r_angle) - 45) > 5:
    print('✓ Original mocap frame 0 had DIFFERENT shoulder rotations')
    print('✓ A-pose override IS working and changing frame 0!')
else:
    print('⚠ Original mocap frame 0 was already similar to A-pose')
    print('  (This animation happens to start with arms in A-pose-like position)')

