"""
============================================================================
VISUALIZE NPZ FILE CONTENTS
============================================================================

PURPOSE:
    Creates detailed text files showing the contents of NPZ files.
    Useful for understanding data structure, values, and formats.

USAGE:
    python visualize_npz.py <npz_file_path> [output_file_path]

EXAMPLE:
    python visualize_npz.py data/reference/smplh_target_reference.npz data/reference/smplh_target_reference_visualization.txt
    python visualize_npz.py data/test_small/D6-\ CartWheel_poses.npz data/test_small/cartwheel_visualization.txt
============================================================================

# Reference file
python src/utils/visualize_npz.py data/reference/smplh_target_reference.npz

# Animation file
python src/utils/visualize_npz.py "data/test_small/D6- CartWheel_poses.npz"

# Or specify output path
python src/utils/visualize_npz.py <input.npz> <output.txt>

"""
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Any


# SMPL-H joint names for reference
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)


def format_array_summary(arr: np.ndarray, name: str, max_rows: int = 20) -> str:
    """Format array summary with statistics."""
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"{name}")
    lines.append(f"{'='*80}")
    lines.append(f"Shape: {arr.shape}")
    lines.append(f"Dtype: {arr.dtype}")
    lines.append(f"Size: {arr.size:,} elements")
    lines.append(f"Memory: {arr.nbytes / 1024:.2f} KB")
    
    # Only compute statistics for numeric arrays
    is_numeric = np.issubdtype(arr.dtype, np.number)
    
    if arr.size > 0 and is_numeric:
        lines.append(f"\nStatistics:")
        lines.append(f"  Min: {np.min(arr):.6f}")
        lines.append(f"  Max: {np.max(arr):.6f}")
        lines.append(f"  Mean: {np.mean(arr):.6f}")
        lines.append(f"  Std:  {np.std(arr):.6f}")
        
        if arr.ndim == 1:
            lines.append(f"\nFirst {min(max_rows, len(arr))} values:")
            for i in range(min(max_rows, len(arr))):
                lines.append(f"  [{i:3d}]: {arr[i]:12.6f}")
            if len(arr) > max_rows:
                lines.append(f"  ... ({len(arr) - max_rows} more values)")
        
        elif arr.ndim == 2:
            lines.append(f"\nFirst {min(max_rows, arr.shape[0])} rows:")
            for i in range(min(max_rows, arr.shape[0])):
                row_str = " ".join([f"{val:10.6f}" for val in arr[i]])
                lines.append(f"  [{i:3d}]: {row_str}")
            if arr.shape[0] > max_rows:
                lines.append(f"  ... ({arr.shape[0] - max_rows} more rows)")
    
    return "\n".join(lines)


def visualize_reference_npz(npz_path: Path, output_path: Path) -> None:
    """Visualize reference NPZ file (smplh_target_reference.npz)."""
    data = np.load(str(npz_path))
    
    lines = []
    lines.append("="*80)
    lines.append("REFERENCE NPZ FILE DATA STRUCTURES")
    lines.append("="*80)
    lines.append(f"File: {npz_path}")
    lines.append(f"Keys in NPZ: {list(data.keys())}")
    
    lines.append(f"\n{'='*80}")
    lines.append("DATA STRUCTURE OVERVIEW")
    lines.append(f"{'='*80}")
    lines.append("This NPZ file contains 3 arrays:")
    lines.append("")
    lines.append("1. J_ABSOLUTE - Absolute joint positions in A-pose")
    lines.append("2. SMPL_OFFSETS - Relative offsets for forward kinematics")
    lines.append("3. JOINT_NAMES - Joint name strings")
    
    if 'J_ABSOLUTE' in data:
        J_ABS = data['J_ABSOLUTE']
        lines.append(f"\n{'='*80}")
        lines.append("1. J_ABSOLUTE")
        lines.append(f"{'='*80}")
        lines.append(f"Shape: {J_ABS.shape}  (52 joints × 3 coordinates)")
        lines.append(f"Dtype: {J_ABS.dtype}")
        lines.append(f"Units: meters")
        lines.append(f"Meaning: Absolute 3D positions of each joint in A-pose")
        lines.append(f"\nAll 52 joint positions:")
        lines.append(f"{'Idx':<4} {'Joint Name':<20} {'X (m)':<12} {'Y (m)':<12} {'Z (m)':<12}")
        lines.append("-"*80)
        for i in range(52):
            joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
            lines.append(f"{i:<4} {joint_name:<20} {J_ABS[i][0]:<12.6f} {J_ABS[i][1]:<12.6f} {J_ABS[i][2]:<12.6f}")
    
    if 'SMPL_OFFSETS' in data:
        SMPL_OFF = data['SMPL_OFFSETS']
        lines.append(f"\n{'='*80}")
        lines.append("2. SMPL_OFFSETS")
        lines.append(f"{'='*80}")
        lines.append(f"Shape: {SMPL_OFF.shape}  (52 joints × 3 coordinates)")
        lines.append(f"Dtype: {SMPL_OFF.dtype}")
        lines.append(f"Units: meters")
        lines.append(f"Meaning: Relative offset from parent joint (or absolute for root)")
        lines.append(f"\nFor root (Pelvis): SMPL_OFFSETS[0] = J_ABSOLUTE[0]")
        lines.append(f"For children: SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent]")
        lines.append(f"\nAll 52 offsets:")
        lines.append(f"{'Idx':<4} {'Joint Name':<20} {'X (m)':<12} {'Y (m)':<12} {'Z (m)':<12}")
        lines.append("-"*80)
        for i in range(52):
            joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
            lines.append(f"{i:<4} {joint_name:<20} {SMPL_OFF[i][0]:<12.6f} {SMPL_OFF[i][1]:<12.6f} {SMPL_OFF[i][2]:<12.6f}")
    
    if 'JOINT_NAMES' in data:
        joint_names = data['JOINT_NAMES']
        lines.append(f"\n{'='*80}")
        lines.append("3. JOINT_NAMES")
        lines.append(f"{'='*80}")
        lines.append(f"Shape: {joint_names.shape}  (52 strings)")
        lines.append(f"Dtype: {joint_names.dtype}")
        lines.append(f"Meaning: Joint name for each index")
        lines.append(f"\nAll 52 joint names:")
        for i, name in enumerate(joint_names):
            lines.append(f"  [{i:2d}]: {name}")
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"✓ Visualization saved to: {output_path}")


def visualize_animation_npz(npz_path: Path, output_path: Path) -> None:
    """Visualize animation NPZ file (AMASS data)."""
    data = np.load(str(npz_path))
    
    lines = []
    lines.append("="*80)
    lines.append("ANIMATION NPZ FILE DATA STRUCTURES")
    lines.append("="*80)
    lines.append(f"File: {npz_path.name}")
    lines.append(f"Path: {npz_path}")
    lines.append(f"Keys in NPZ: {list(data.keys())}")
    
    lines.append(f"\n{'='*80}")
    lines.append("DATA STRUCTURE OVERVIEW")
    lines.append(f"{'='*80}")
    lines.append("This NPZ file contains animation data with the following keys:")
    for key in data.keys():
        value = data[key]
        if hasattr(value, 'shape'):
            lines.append(f"  - {key}: shape {value.shape}, dtype {value.dtype}")
        else:
            lines.append(f"  - {key}: {type(value).__name__}")
    
    if 'poses' in data:
        poses = data['poses']
        lines.append(f"\n{'='*80}")
        lines.append("1. poses - Axis-Angle Rotations")
        lines.append(f"{'='*80}")
        lines.append(f"Shape: {poses.shape}  (num_frames × 156)")
        lines.append(f"  156 = 52 joints × 3 axis-angle values per joint")
        lines.append(f"Dtype: {poses.dtype}")
        lines.append(f"Units: radians (angle = magnitude of axis-angle vector)")
        lines.append(f"Meaning: Joint rotations for all frames")
        lines.append(f"Layout: Each row is one frame, values are: [joint0_x, joint0_y, joint0_z, joint1_x, ...]")
        lines.append(f"\nExample - Frame 0, first 5 joints:")
        lines.append(f"{'Joint':<20} {'Axis-Angle [X, Y, Z]':<50}")
        lines.append("-"*80)
        for i in range(min(5, 52)):
            joint_name = JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}"
            axis_angle = poses[0][i*3:(i+1)*3]
            lines.append(f"{joint_name:<20} [{axis_angle[0]:8.4f}, {axis_angle[1]:8.4f}, {axis_angle[2]:8.4f}]")
    
    if 'trans' in data:
        trans = data['trans']
        lines.append(f"\n{'='*80}")
        lines.append("2. trans - Root Translation")
        lines.append(f"{'='*80}")
        lines.append(f"Shape: {trans.shape}  (num_frames × 3)")
        lines.append(f"Dtype: {trans.dtype}")
        lines.append(f"Units: meters")
        lines.append(f"Meaning: Pelvis (root bone) position in world space for each frame")
        lines.append(f"Layout: Each row is one frame: [X, Y, Z]")
        lines.append(f"\nFirst 10 frames:")
        lines.append(f"{'Frame':<8} {'X (m)':<12} {'Y (m)':<12} {'Z (m)':<12}")
        lines.append("-"*50)
        for i in range(min(10, len(trans))):
            lines.append(f"{i:<8} {trans[i][0]:<12.6f} {trans[i][1]:<12.6f} {trans[i][2]:<12.6f}")
    
    if 'mocap_framerate' in data:
        framerate = data['mocap_framerate']
        lines.append(f"\n{'='*80}")
        lines.append("3. mocap_framerate")
        lines.append(f"{'='*80}")
        lines.append(f"Value: {framerate} fps")
        lines.append(f"Dtype: {type(framerate)}")
        lines.append(f"Meaning: Frame rate of the motion capture data")
        if 'poses' in data:
            num_frames = len(data['poses'])
            duration = num_frames / framerate
            lines.append(f"\nDerived info:")
            lines.append(f"  Number of frames: {num_frames}")
            lines.append(f"  Duration: {duration:.2f} seconds")
    
    # Other keys (not used in retargeting but present in file)
    other_keys = [k for k in data.keys() if k not in ['poses', 'trans', 'mocap_framerate']]
    if other_keys:
        lines.append(f"\n{'='*80}")
        lines.append("OTHER KEYS (not used in retargeting pipeline)")
        lines.append(f"{'='*80}")
        for key in other_keys:
            value = data[key]
            if hasattr(value, 'shape'):
                lines.append(f"\n{key}:")
                lines.append(f"  Shape: {value.shape}")
                lines.append(f"  Dtype: {value.dtype}")
                if value.size < 20:
                    lines.append(f"  Values: {value}")
                else:
                    lines.append(f"  First few values: {value.flat[:5]} ...")
            else:
                lines.append(f"\n{key}: {value} (type: {type(value).__name__})")
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"✓ Visualization saved to: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_npz.py <npz_file_path> [output_file_path]")
        print("\nExamples:")
        print("  python visualize_npz.py data/reference/smplh_target_reference.npz")
        print("  python visualize_npz.py data/test_small/D6-\\ CartWheel_poses.npz")
        sys.exit(1)
    
    npz_path = Path(sys.argv[1])
    
    if not npz_path.exists():
        print(f"Error: File not found: {npz_path}")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        # Default: same directory, add _visualization.txt suffix
        output_path = npz_path.parent / f"{npz_path.stem}_visualization.txt"
    
    # Check if it's a reference file or animation file
    data = np.load(str(npz_path))
    
    if 'J_ABSOLUTE' in data and 'SMPL_OFFSETS' in data:
        # Reference file
        print(f"Detected reference NPZ file")
        visualize_reference_npz(npz_path, output_path)
    elif 'poses' in data and 'trans' in data:
        # Animation file
        print(f"Detected animation NPZ file")
        visualize_animation_npz(npz_path, output_path)
    else:
        # Unknown format - try to visualize anyway
        print(f"Unknown NPZ format, attempting to visualize...")
        visualize_animation_npz(npz_path, output_path)


if __name__ == '__main__':
    main()

