"""
M2.2: Test load_reference_j_absolute() function

This script tests that load_reference_j_absolute() correctly loads
J_ABSOLUTE from the reference NPZ file.
"""

import sys
from pathlib import Path

# Add src to path so we can import retarget
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import after path is set up
import numpy as np
from retarget import load_reference_j_absolute

def main():
    print("="*80)
    print("M2.2: Testing load_reference_j_absolute()")
    print("="*80)
    
    try:
        # Load J_ABSOLUTE
        J_ABSOLUTE = load_reference_j_absolute()
        
        # Verify shape
        print(f"\n✓ Shape: {J_ABSOLUTE.shape}")
        assert J_ABSOLUTE.shape == (52, 3), f"Expected (52, 3), got {J_ABSOLUTE.shape}"
        
        # Verify dtype
        print(f"✓ Dtype: {J_ABSOLUTE.dtype}")
        assert J_ABSOLUTE.dtype == np.float64, f"Expected float64, got {J_ABSOLUTE.dtype}"
        
        # Print first few values
        print(f"\n✓ First 3 joints (Pelvis, L_Hip, R_Hip):")
        for i in range(3):
            print(f"  Joint {i}: {J_ABSOLUTE[i]}")
        
        # Print last joint
        print(f"\n✓ Last joint (R_Hand_14):")
        print(f"  Joint 51: {J_ABSOLUTE[51]}")
        
        # Compare with reference NPZ directly
        print(f"\n✓ Comparing with reference NPZ...")
        ref_path = Path(__file__).parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
        ref_data = np.load(str(ref_path))
        J_ABSOLUTE_ref = ref_data['J_ABSOLUTE']
        
        # Check if values match
        if np.allclose(J_ABSOLUTE, J_ABSOLUTE_ref):
            print("✓ Values match reference NPZ exactly!")
        else:
            max_diff = np.max(np.abs(J_ABSOLUTE - J_ABSOLUTE_ref))
            print(f"⚠️  Values differ from reference NPZ (max diff: {max_diff})")
            if max_diff > 1e-6:
                print("   ERROR: Values should match exactly!")
                return False
        
        print("\n" + "="*80)
        print("✅ All tests passed!")
        print("="*80)
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        return False
    except KeyError as e:
        print(f"\n❌ Key error: {e}")
        return False
    except ValueError as e:
        print(f"\n❌ Value error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

