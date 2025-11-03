"""
============================================================================
EXPLORE AMASS DATA
============================================================================

PURPOSE:
    Data exploration tool for AMASS .npz files. Inspects file structure, 
    displays key data fields, and compares frame 0 poses across multiple 
    files to understand data format and variations.

RELEVANCE: 📚 REFERENCE - Useful for understanding data format
    Helpful when exploring new datasets or debugging data issues.

MILESTONE: M1 (Data exploration - COMPLETED)

USAGE:
    python explore_amass_data.py <npz_file_path>
    python explore_amass_data.py <directory_with_npz_files>

EXAMPLE:
    python explore_amass_data.py data/extracted/ACCAD/Female1Gestures_c3d/D1\ -\ Urban\ 1_poses.npz
============================================================================
"""
import numpy as np
import sys
from pathlib import Path

def load_npz_file(npz_path):
    """Load and display information about an AMASS .npz file"""
    data = np.load(npz_path)
    
    print(f"\n{'='*60}")
    print(f"File: {npz_path.name}")
    print(f"{'='*60}")
    
    print(f"\nKeys in file:")
    for key in data.keys():
        val = data[key]
        if hasattr(val, 'shape'):
            print(f"  {key}: shape {val.shape}, dtype {val.dtype}")
        else:
            print(f"  {key}: {type(val)}")
    
    # Focus on the key data
    if 'poses' in data and 'trans' in data:
        poses = data['poses']
        trans = data['trans']
        print(f"\nPoses: {poses.shape} - {poses.shape[0]} frames")
        print(f"Translations: {trans.shape}")
        print(f"Framerate: {data.get('mocap_framerate', 'unknown')}")
        
        print(f"\nFrame 0 (first frame):")
        print(f"  Pose params shape: {poses[0].shape}")
        print(f"  Translation: {trans[0]}")
        
        # Show joint parameters
        if poses[0].shape[0] == 156:  # SMPL-H: 52 joints * 3 axis-angle
            print(f"  This is SMPL-H format (52 joints × 3)")
            print(f"  First 10 joint params: {poses[0][:10]}")
    
    return data

def find_npz_files(directory):
    """Find all .npz files in directory tree"""
    npz_files = list(Path(directory).rglob("*.npz"))
    return npz_files

def compare_frame_0(npz_files, num_samples=5):
    """Compare frame 0 poses across multiple files"""
    print(f"\n{'='*60}")
    print("COMPARING FRAME 0 POSES")
    print(f"{'='*60}")
    
    if len(npz_files) == 0:
        print("No .npz files found!")
        return
    
    # Sample first N files
    samples = npz_files[:num_samples]
    
    frame_0_data = []
    for npz_file in samples:
        data = np.load(npz_file)
        if 'poses' in data and 'trans' in data:
            frame_0_data.append({
                'file': npz_file.name,
                'pose': data['poses'][0],
                'trans': data['trans'][0]
            })
            print(f"\n{npz_file.name}:")
            print(f"  Translation: {data['trans'][0]}")
            print(f"  Pose params (first 9): {data['poses'][0][:9]}")
    
    # Calculate statistics
    if len(frame_0_data) > 1:
        trans_variations = np.std([f['trans'] for f in frame_0_data], axis=0)
        print(f"\nTranslation variation across files:")
        print(f"  Std dev in X: {trans_variations[0]:.4f}")
        print(f"  Std dev in Y: {trans_variations[1]:.4f}")
        print(f"  Std dev in Z: {trans_variations[2]:.4f}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python explore_amass_data.py <npz_file_path>")
        print("   or: python explore_amass_data.py <directory_with_npz_files>")
        print("\nExample:")
        print("  python explore_amass_data.py data/extracted/ACCAD/.../some_poses.npz")
        print("  python explore_amass_data.py data/extracted/ACCAD/")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if input_path.is_file() and input_path.suffix == '.npz':
        # Single file
        load_npz_file(input_path)
    
    elif input_path.is_dir():
        # Directory - find all .npz files
        npz_files = find_npz_files(input_path)
        print(f"\nFound {len(npz_files)} .npz files")
        
        if len(npz_files) > 0:
            print(f"\nAnalyzing first file as example:")
            load_npz_file(npz_files[0])
            
            print(f"\n\nComparing first 5 frame 0 poses:")
            compare_frame_0(npz_files[:5])
    else:
        print(f"Error: {input_path} is not a .npz file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()

