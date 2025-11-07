#!/usr/bin/env python3
"""
Generate A-pose rotations programmatically from T-pose.

Creates a simple A-pose by rotating shoulder bones down ~45°.
This gives identity rotations for most bones, with only shoulders modified.
"""

import numpy as np
from pathlib import Path
from mathutils import Quaternion, Euler
import math

# Joint names
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2",
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck",
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder",
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def create_apose_rotations() -> dict:
    """
    Create A-pose bone rotations.
    
    A-pose = T-pose with arms rotated down ~45°
    
    ALL bones get identity rotation (T-pose), then shoulders are modified.
    This ensures frame 0 is completely reset to T-pose before A-pose is applied.
    
    Returns:
        Dictionary mapping bone names to quaternions [w, x, y, z]
        Plus a special 'RESET_ALL_TO_IDENTITY' flag
    """
    rotations = {}
    
    # ALL bones: identity rotation (reset to T-pose)
    identity_quat = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    
    for bone_name in JOINT_NAMES:
        rotations[bone_name] = identity_quat.copy()
    
    # L_Shoulder: rotate down 45° around Y-axis (local rotation)
    # In Blender: R Y -45
    angle = math.radians(-45)
    l_shoulder_quat = Quaternion((0, 1, 0), angle)  # Axis-angle to quaternion
    rotations["L_Shoulder"] = np.array([
        l_shoulder_quat.w, l_shoulder_quat.x, l_shoulder_quat.y, l_shoulder_quat.z
    ], dtype=np.float64)
    
    # R_Shoulder: rotate down 45° around Y-axis (opposite direction)
    # In Blender: R Y 45
    angle = math.radians(45)
    r_shoulder_quat = Quaternion((0, 1, 0), angle)
    rotations["R_Shoulder"] = np.array([
        r_shoulder_quat.w, r_shoulder_quat.x, r_shoulder_quat.y, r_shoulder_quat.z
    ], dtype=np.float64)
    
    return rotations


def main():
    """Generate and save A-pose rotations"""
    print("Generating A-pose rotations...")
    
    rotations = create_apose_rotations()
    
    # Output path
    output_path = Path(__file__).parent.parent.parent / "data" / "reference" / "apose_rotations.npz"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to NPZ
    np.savez(output_path, **rotations)
    
    print(f"✓ Generated {len(rotations)} bone rotations")
    print(f"✓ Saved to: {output_path}")
    print("\nA-pose configuration:")
    print("  - Most bones: Identity rotation (T-pose)")
    print("  - L_Shoulder: Rotated -45° around Y-axis")
    print("  - R_Shoulder: Rotated +45° around Y-axis")
    print("\nYou can now use this in retarget.py for frame 0 A-pose")


if __name__ == "__main__":
    main()

