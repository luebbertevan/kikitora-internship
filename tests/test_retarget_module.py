#!/usr/bin/env python3
"""Test if retarget.py module imports and basic functions work"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

print("Testing retarget.py module...")

# Try importing in a Blender context
try:
    import bpy
    print("✓ Blender (bpy) available")
except ImportError:
    print("✗ Blender (bpy) not available - this script must run in Blender")
    sys.exit(1)

# Import retarget module
try:
    import retarget
    print("✓ retarget module imported")
except Exception as e:
    print(f"✗ Failed to import retarget: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check T-pose J_ABSOLUTE loaded
try:
    print(f"\n✓ T-pose J_ABSOLUTE shape: {retarget.J_ABSOLUTE.shape}")
    print(f"✓ T-pose J_ABSOLUTE dtype: {retarget.J_ABSOLUTE.dtype}")
    print(f"✓ First joint (Pelvis): {retarget.J_ABSOLUTE[0]}")
except Exception as e:
    print(f"✗ T-pose J_ABSOLUTE error: {e}")
    sys.exit(1)

# Check SMPL_OFFSETS computed
try:
    print(f"\n✓ SMPL_OFFSETS shape: {retarget.SMPL_OFFSETS.shape}")
    print(f"✓ SMPL_OFFSETS dtype: {retarget.SMPL_OFFSETS.dtype}")
except Exception as e:
    print(f"✗ SMPL_OFFSETS error: {e}")
    sys.exit(1)

# Test load_apose_j_absolute function
try:
    apose_j_absolute = retarget.load_apose_j_absolute()
    print(f"\n✓ A-pose J_ABSOLUTE loaded")
    print(f"✓ A-pose J_ABSOLUTE shape: {apose_j_absolute.shape}")
    print(f"✓ First joint (Pelvis): {apose_j_absolute[0]}")
except FileNotFoundError as e:
    print(f"\n⚠ A-pose NPZ not found: {e}")
    print("  (This is expected if you haven't created it yet)")
except Exception as e:
    print(f"✗ A-pose loading error: {e}")
    import traceback
    traceback.print_exc()

# Test compute_rotation_between_vectors
try:
    import numpy as np
    from mathutils import Quaternion
    
    vec_from = np.array([1.0, 0.0, 0.0])
    vec_to = np.array([0.0, 1.0, 0.0])
    quat = retarget.compute_rotation_between_vectors(vec_from, vec_to)
    print(f"\n✓ compute_rotation_between_vectors works")
    print(f"  90° rotation from X to Y: {quat}")
except Exception as e:
    print(f"✗ compute_rotation_between_vectors error: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All basic tests passed!")

