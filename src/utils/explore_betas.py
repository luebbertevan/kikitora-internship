"""
Explore betas in NPZ files and understand how to compute bone lengths from them.

This script:
1. Loads betas from NPZ files
2. Explains what betas represent
3. Shows how to compute original bone lengths from betas using SMPL model
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from numpy.typing import NDArray


def explore_npz_betas(npz_path: Path) -> None:
    """Explore betas in an NPZ file"""
    print(f"\n{'='*80}")
    print(f"Exploring betas in: {npz_path}")
    print(f"{'='*80}\n")
    
    data = np.load(str(npz_path))
    
    if 'betas' not in data:
        print("❌ No betas found in this NPZ file")
        return
    
    betas = data['betas']
    
    print(f"Betas shape: {betas.shape}")
    print(f"Betas dtype: {betas.dtype}")
    print(f"\nBetas values:")
    print(betas)
    print(f"\nStatistics:")
    print(f"  Min: {np.min(betas):.6f}")
    print(f"  Max: {np.max(betas):.6f}")
    print(f"  Mean: {np.mean(betas):.6f}")
    print(f"  Std: {np.std(betas):.6f}")
    print(f"  Non-zero count: {np.count_nonzero(betas)}/{len(betas)}")
    
    # Check if betas are near zero (standardized skeleton)
    if np.max(np.abs(betas)) < 1e-3:
        print("\n✅ Betas are near zero - using standardized/default skeleton")
    else:
        print(f"\n⚠️  Betas are non-zero - subject has custom body proportions")
        print(f"   Max absolute beta: {np.max(np.abs(betas)):.6f}")


def compute_j_absolute_from_betas(
    betas: NDArray[np.float64],
    smpl_model_path: Optional[Path] = None
) -> Tuple[NDArray[np.float64], str]:
    """
    Compute J_ABSOLUTE (joint positions) from betas using SMPL model.
    
    This requires:
    1. SMPL model file (usually .npz or .pkl)
    2. Model contains: v_template, shapedirs, J_regressor
    
    Process:
    1. Apply betas to template mesh: v = v_template + shapedirs @ betas
    2. Regress joint positions: J = J_regressor @ v
    3. Return J_ABSOLUTE (52, 3)
    
    Args:
        betas: Shape parameters (16,) or (10,)
        smpl_model_path: Path to SMPL model file
        
    Returns:
        (J_ABSOLUTE, method) tuple
    """
    if smpl_model_path is None:
        # Try to find SMPL model in common locations
        possible_paths = [
            Path("data/models/amass_joints_h36m_60.pkl"),
            Path("data/models/smplh_neutral.npz"),
            Path("data/models/model.npz"),
        ]
        
        for path in possible_paths:
            if path.exists():
                smpl_model_path = path
                break
        
        if smpl_model_path is None:
            raise FileNotFoundError(
                "SMPL model not found. Please provide path to SMPL model file."
            )
    
    print(f"\nLoading SMPL model from: {smpl_model_path}")
    
    # Load model
    if smpl_model_path.suffix == '.pkl':
        import pickle
        with open(smpl_model_path, 'rb') as f:
            model_data = pickle.load(f, encoding='latin1')
    else:
        model_data = np.load(str(smpl_model_path), allow_pickle=True)
        # If it's a numpy array with one item, extract it
        if isinstance(model_data, np.ndarray) and model_data.size == 1:
            model_data = model_data.item()
    
    # Extract required components
    # Handle both dict and numpy array formats
    if isinstance(model_data, dict):
        v_template = model_data.get('v_template')
        shapedirs = model_data.get('shapedirs')
        J_regressor = model_data.get('J_regressor')
    else:
        # Try direct access
        try:
            v_template = model_data['v_template']
            shapedirs = model_data['shapedirs']
            J_regressor = model_data['J_regressor']
        except (KeyError, TypeError):
            # Try item() method if it's a numpy array
            if hasattr(model_data, 'item'):
                model_dict = model_data.item()
                v_template = model_dict.get('v_template')
                shapedirs = model_dict.get('shapedirs')
                J_regressor = model_dict.get('J_regressor')
            else:
                raise KeyError("Cannot extract model components")
    
    if v_template is None:
        raise KeyError("v_template not found in model")
    if shapedirs is None:
        raise KeyError("shapedirs not found in model")
    if J_regressor is None:
        raise KeyError("J_regressor not found in model")
    
    print(f"  v_template shape: {v_template.shape}")
    print(f"  shapedirs shape: {shapedirs.shape}")
    print(f"  J_regressor shape: {J_regressor.shape}")
    
    # Handle betas shape
    if len(betas.shape) > 1:
        betas = betas.flatten()
    
    # Limit betas to available shape components
    num_betas = min(len(betas), shapedirs.shape[-1])
    betas_used = betas[:num_betas]
    
    print(f"\nUsing {num_betas} beta components")
    
    # Step 1: Apply betas to template mesh
    # v = v_template + sum(beta_i * shapedirs[:, :, i])
    if shapedirs.ndim == 3:
        # shapedirs is (num_verts, 3, num_betas)
        v_posed = v_template.copy()
        for i in range(num_betas):
            v_posed += betas_used[i] * shapedirs[:, :, i]
    else:
        # shapedirs might be flattened, need to reshape
        # This is model-specific
        raise NotImplementedError("shapedirs format not recognized")
    
    print(f"  Computed mesh vertices: {v_posed.shape}")
    
    # Step 2: Regress joint positions from mesh
    J_absolute = J_regressor @ v_posed
    
    print(f"  Computed joint positions: {J_absolute.shape}")
    print(f"  Should be (52, 3) for SMPL-H")
    
    return J_absolute, "betas_smpl_model"


def compute_smpl_offsets_from_j_absolute(j_absolute: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Compute SMPL_OFFSETS from J_ABSOLUTE using the SMPL-H parent tree.
    
    Args:
        j_absolute: Joint positions (52, 3)
        
    Returns:
        SMPL_OFFSETS (52, 3)
    """
    from numpy.typing import NDArray
    
    SMPL_H_PARENTS = np.array([
        -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
        7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
        18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
        29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
        21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
        49, 50,
    ], dtype=np.int32)
    
    smpl_offsets = np.zeros((52, 3))
    
    for i in range(52):
        parent_idx = SMPL_H_PARENTS[i]
        if parent_idx == -1:
            # Root joint - offset is just the position
            smpl_offsets[i] = j_absolute[i]
        else:
            # Child joint - offset is relative to parent
            smpl_offsets[i] = j_absolute[i] - j_absolute[parent_idx]
    
    return smpl_offsets


def main():
    """Main function to explore betas"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python explore_betas.py <npz_file_path> [smpl_model_path]")
        print("\nExample:")
        print("  python explore_betas.py data/test_small/D6- CartWheel_poses.npz")
        sys.exit(1)
    
    npz_path = Path(sys.argv[1])
    smpl_model_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # Explore betas
    explore_npz_betas(npz_path)
    
    # Try to compute bone lengths if model is available
    if smpl_model_path or Path("data/models/amass_joints_h36m_60.pkl").exists():
        print("\n" + "="*80)
        print("ATTEMPTING TO COMPUTE ORIGINAL BONE LENGTHS FROM BETAS")
        print("="*80)
        
        data = np.load(str(npz_path))
        betas = data['betas']
        
        try:
            j_absolute, method = compute_j_absolute_from_betas(betas, smpl_model_path)
            smpl_offsets = compute_smpl_offsets_from_j_absolute(j_absolute)
            
            print(f"\n✅ Successfully computed original bone lengths using: {method}")
            print(f"\nJ_ABSOLUTE (first 5 joints):")
            for i in range(min(5, len(j_absolute))):
                print(f"  Joint {i:2d}: [{j_absolute[i,0]:8.6f}, {j_absolute[i,1]:8.6f}, {j_absolute[i,2]:8.6f}]")
            
            print(f"\nSMPL_OFFSETS statistics:")
            bone_lengths = [np.linalg.norm(smpl_offsets[i]) for i in range(1, 52)]
            print(f"  Average bone length: {np.mean(bone_lengths):.6f} m")
            print(f"  Min bone length: {np.min(bone_lengths):.6f} m")
            print(f"  Max bone length: {np.max(bone_lengths):.6f} m")
            
        except Exception as e:
            print(f"\n❌ Error computing bone lengths: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️  SMPL model not found. Cannot compute bone lengths from betas.")
        print("   To compute original bone lengths, you need:")
        print("   1. SMPL model file (.npz or .pkl)")
        print("   2. Model should contain: v_template, shapedirs, J_regressor")


if __name__ == "__main__":
    main()

