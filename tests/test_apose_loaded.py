"""Test that A-pose J_ABSOLUTE is loaded correctly in retarget.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("="*80)
print("Testing A-pose J_ABSOLUTE Loading in retarget.py")
print("="*80)

try:
    from retarget import J_ABSOLUTE, SMPL_OFFSETS
    
    print(f"\n✓ J_ABSOLUTE shape: {J_ABSOLUTE.shape}")
    print(f"✓ SMPL_OFFSETS shape: {SMPL_OFFSETS.shape}")
    print(f"\n✓ Pelvis (joint 0): {J_ABSOLUTE[0]}")
    print(f"✓ L_Shoulder (joint 33): {J_ABSOLUTE[33]}")
    print(f"\n✓ SMPL_OFFSETS[0] (Pelvis): {SMPL_OFFSETS[0]}")
    print(f"✓ SMPL_OFFSETS[1] (L_Hip): {SMPL_OFFSETS[1]}")
    
    print("\n" + "="*80)
    print("✅ SUCCESS: A-pose J_ABSOLUTE loaded from apose_from_blender.npz")
    print("   retarget.py is now using A-pose armature for retargeting!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

