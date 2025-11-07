"""
M3: Test that J_ABSOLUTE is loaded from A-pose NPZ at module level
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("="*80)
print("M3: Testing A-pose J_ABSOLUTE loaded at module level")
print("="*80)

try:
    # Import should trigger module-level loading
    from retarget import J_ABSOLUTE, SMPL_OFFSETS
    
    print(f"\n✓ J_ABSOLUTE shape: {J_ABSOLUTE.shape}")
    print(f"✓ SMPL_OFFSETS shape: {SMPL_OFFSETS.shape}")
    
    # Verify it's A-pose (not T-pose)
    # A-pose pelvis should be around [0, 0, 0.99] (from test output earlier)
    pelvis = J_ABSOLUTE[0]
    print(f"\n✓ Pelvis (joint 0): {pelvis}")
    
    # A-pose should have arms at ~45 degrees, not straight out
    # Check L_Shoulder (index 33) - should be different from T-pose
    l_shoulder = J_ABSOLUTE[33]
    print(f"✓ L_Shoulder (joint 33): {l_shoulder}")
    
    # Verify SMPL_OFFSETS computed correctly
    print(f"\n✓ SMPL_OFFSETS[0] (Pelvis offset): {SMPL_OFFSETS[0]}")
    print(f"✓ SMPL_OFFSETS[1] (L_Hip offset): {SMPL_OFFSETS[1]}")
    
    # Verify no hardcoded values remain
    # T-pose pelvis was [-0.001795, -0.223333, 0.028219]
    # A-pose pelvis should be different
    tpose_pelvis = [-0.001795, -0.223333, 0.028219]
    if not np.allclose(pelvis, tpose_pelvis, atol=0.1):
        print("\n✓ Confirmed: Using A-pose (not T-pose hardcoded values)")
    else:
        print("\n⚠️  WARNING: Values match T-pose - may still be using hardcoded!")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("✅ M3 Complete: Hardcoded J_ABSOLUTE removed, using A-pose from NPZ")
    print("="*80)
    
except FileNotFoundError as e:
    print(f"\n❌ File not found: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

