"""
============================================================================
SCALE REFERENCE
============================================================================

PURPOSE:
    Scales the smplh_target_reference.npz file by a given factor to match 
    animation data scale. Used during M2.1 to fix scale mismatches between 
    FBX-extracted reference and actual animation data.

RELEVANCE: 📚 ARCHIVE - Historical (M2.1 DONE, scale issue fixed)
    Kept for reference. The reference has already been scaled correctly. 
    Useful if scale adjustments are needed in the future.

MILESTONE: M2.1 (Scale fix - COMPLETED)

USAGE:
    python scale_reference.py [SCALE_FACTOR]

EXAMPLE:
    python scale_reference.py 0.9
============================================================================
"""
import numpy as np
from pathlib import Path
import sys

def main():
    # Allow scale factor as command line argument
    scale_factor = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    
    # Load current reference
    ref = np.load(str(ref_path))
    J_ABSOLUTE = ref['J_ABSOLUTE']
    SMPL_OFFSETS = ref['SMPL_OFFSETS']
    JOINT_NAMES = ref['JOINT_NAMES']
    
    print("Current scale:")
    print(f"  Pelvis Y: {J_ABSOLUTE[0][1]:.6f}")
    print(f"  Hip distance: {np.linalg.norm(J_ABSOLUTE[1] - J_ABSOLUTE[0]):.6f}")
    
    # Scale to match animation data
    J_ABSOLUTE_scaled = J_ABSOLUTE * scale_factor
    SMPL_OFFSETS_scaled = SMPL_OFFSETS * scale_factor
    
    print(f"\nScaled by {scale_factor}x:")
    print(f"  Pelvis Y: {J_ABSOLUTE_scaled[0][1]:.6f}")
    print(f"  Hip distance: {np.linalg.norm(J_ABSOLUTE_scaled[1] - J_ABSOLUTE_scaled[0]):.6f}")
    
    # Save scaled version
    np.savez(str(ref_path), 
             J_ABSOLUTE=J_ABSOLUTE_scaled, 
             SMPL_OFFSETS=SMPL_OFFSETS_scaled, 
             JOINT_NAMES=JOINT_NAMES)
    
    print(f"\n✓ Saved scaled reference to {ref_path}")

if __name__ == '__main__':
    main()

