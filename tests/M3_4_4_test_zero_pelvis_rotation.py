"""
M3.4.4: Test Zero Pelvis Rotation

This script tests if setting pelvis rotation to zero fixes
the armature facing ground issue.
"""

import sys
from pathlib import Path
import numpy as np
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("="*80)
print("M3.4.4: Testing Zero Pelvis Rotation")
print("="*80)

# Find a test NPZ file
test_dir = Path(__file__).parent.parent / 'data' / 'test'
npz_files = list(test_dir.glob('*.npz'))

if not npz_files:
    print("❌ No NPZ files found in data/test")
    sys.exit(1)

npz_path = npz_files[0]
print(f"\n📁 Testing with: {npz_path.name}")

# Load mocap data
data = np.load(str(npz_path))
poses = data['poses'].copy()  # Make a copy
trans = data['trans'].copy()

print(f"\n✓ Loaded mocap data:")
print(f"   Frames: {len(poses)}")

# Check original pelvis rotation
original_pelvis_rot = poses[0, 0:3]
original_magnitude = np.linalg.norm(original_pelvis_rot)
print(f"\n📊 Original pelvis rotation (frame 0):")
print(f"   Rotation: {original_pelvis_rot}")
print(f"   Magnitude: {original_magnitude:.6f} rad ({np.degrees(original_magnitude):.2f}°)")

# Create modified version with zero pelvis rotation
poses_zero_rot = poses.copy()
poses_zero_rot[:, 0:3] = 0.0  # Zero out pelvis rotation for all frames

print(f"\n✓ Created modified poses with zero pelvis rotation")

# Save to temporary NPZ file
temp_dir = Path(__file__).parent.parent / 'data' / 'output'
temp_dir.mkdir(exist_ok=True, parents=True)

temp_npz = temp_dir / f"{npz_path.stem}_zero_pelvis_rot.npz"
np.savez(str(temp_npz), 
         poses=poses_zero_rot,
         trans=trans,
         mocap_framerate=data.get('mocap_framerate', 30),
         gender=data.get('gender', 'neutral'),
         betas=data.get('betas'),
         dmpls=data.get('dmpls'))

print(f"✓ Saved modified NPZ to: {temp_npz}")

print(f"\n📝 Instructions:")
print(f"   1. Run retarget.py on the modified NPZ:")
print(f"      /Applications/Blender.app/Contents/MacOS/Blender --background --python src/retarget.py -- {temp_npz}")
print(f"   2. Check if the generated GLB has the armature upright")
print(f"   3. Compare to the original GLB to see the difference")

print(f"\n💡 If the armature is now upright, the pelvis rotation is the issue.")
print(f"   We'll need to either:")
print(f"   - Set pelvis rotation to zero in retarget.py")
print(f"   - Or apply a compensating rotation to align with reference")

print("\n" + "="*80)

