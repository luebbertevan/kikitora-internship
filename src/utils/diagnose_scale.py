"""Diagnose the scale mismatch between FBX reference and animation data."""
import numpy as np
from pathlib import Path

# Animation data hardcoded J_ABSOLUTE (from create_glb_from_npz.py - the working animations)
J_ANIM = np.array([
    [-0.001795, -0.223333, 0.028219], [0.067725, -0.314740, 0.021404],
    [-0.069466, -0.313855, 0.023899], [-0.004328, -0.114370, 0.001523],
    [0.102001, -0.689938, 0.016908], [-0.107756, -0.696424, 0.015049],
], dtype=np.float64)

def main():
    # Load FBX-extracted reference
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    ref = np.load(str(ref_path))
    J_FBX = ref['J_ABSOLUTE']
    
    print("=" * 60)
    print("SCALE DIAGNOSIS")
    print("=" * 60)
    
    print("\n### Animation Data (create_glb_from_npz.py) ###")
    print(f"Pelvis position: {J_ANIM[0]}")
    print(f"L_Hip position:  {J_ANIM[1]}")
    print(f"Pelvis Y: {J_ANIM[0][1]:.6f} m")
    print(f"Distance Pelvis->L_Hip: {np.linalg.norm(J_ANIM[1] - J_ANIM[0]):.6f} m")
    
    print("\n### FBX-Extracted Reference (smplh_target_reference.npz) ###")
    print(f"Pelvis position: {J_FBX[0]}")
    print(f"L_Hip position:  {J_FBX[1]}")
    print(f"Pelvis Y: {J_FBX[0][1]:.6f}")
    print(f"Distance Pelvis->L_Hip: {np.linalg.norm(J_FBX[1] - J_FBX[0]):.6f}")
    
    print("\n### Scale Comparison ###")
    # Compare a few key distances
    pelvis_y_ratio = J_FBX[0][1] / J_ANIM[0][1]
    hip_dist_anim = np.linalg.norm(J_ANIM[1] - J_ANIM[0])
    hip_dist_fbx = np.linalg.norm(J_FBX[1] - J_FBX[0])
    hip_ratio = hip_dist_fbx / hip_dist_anim
    
    print(f"FBX Pelvis Y / Animation Pelvis Y: {pelvis_y_ratio:.2f}x")
    print(f"FBX Hip Distance / Animation Hip Distance: {hip_ratio:.2f}x")
    
    print("\n### Diagnosis ###")
    if abs(pelvis_y_ratio - 100) < 10:
        print("⚠️  FBX is ~100x larger than animation data!")
        print("    Likely cause: FBX is in CENTIMETERS, animation is in METERS")
        print(f"    Recommended fix: Multiply J_ABSOLUTE by 0.01 (cm -> m)")
    elif abs(pelvis_y_ratio - 1) < 0.1:
        print("✓ Scales match!")
    else:
        print(f"⚠️  Unexpected scale ratio: {pelvis_y_ratio:.2f}x")
    
    print("\n### Corrected Values (if applying 0.01 scale) ###")
    J_corrected = J_FBX * 0.01
    print(f"Corrected Pelvis position: {J_corrected[0]}")
    print(f"Corrected Pelvis Y: {J_corrected[0][1]:.6f} m")
    print(f"Corrected Distance Pelvis->L_Hip: {np.linalg.norm(J_corrected[1] - J_corrected[0]):.6f} m")
    print(f"Match with animation: {abs(J_corrected[0][1] - J_ANIM[0][1]) < 0.01}")

if __name__ == '__main__':
    main()

