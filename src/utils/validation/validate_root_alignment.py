"""
============================================================================
VALIDATE ROOT ALIGNMENT
============================================================================

PURPOSE:
    Validates that frame 0 pelvis (root bone) position matches the reference 
    A-pose pelvis position from smplh_target_reference.npz. Checks alignment 
    accuracy across multiple GLB files and reports pass/fail statistics.

RELEVANCE: ✅ ACTIVE - Current validation tool for M3+
    Critical validation script for ensuring root alignment in retargeted 
    animations. Part of the validation suite.

MILESTONE: M3 (Root alignment - ACTIVE)

USAGE:
    blender --background --python validate_root_alignment.py -- <glb_file_or_dir> [--limit N]

EXAMPLE:
    blender --background --python validate_root_alignment.py -- data/output/ --limit 5
============================================================================
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector
from typing import Tuple, Optional


def load_reference_pelvis() -> np.ndarray:
    """Load reference pelvis position from smplh_target_reference.npz."""
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    ref = np.load(str(ref_path))
    J_ABSOLUTE = ref['J_ABSOLUTE']
    return J_ABSOLUTE[0]  # Pelvis is index 0


def get_pelvis_position_from_glb(glb_path: Path) -> Optional[np.ndarray]:
    """
    Load GLB and extract pelvis bone head position at frame 0.
    
    Returns:
        Pelvis position as (3,) array, or None if not found
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import GLB
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    # Find armature
    armature_obj = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature_obj = obj
            break
    
    if not armature_obj:
        print(f"⚠️  No armature found in {glb_path.name}")
        return None
    
    # Set to frame 0
    bpy.context.scene.frame_set(0)
    
    # Get pelvis bone in pose mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    pelvis_bone = armature_obj.pose.bones.get('Pelvis')
    if not pelvis_bone:
        print(f"⚠️  Pelvis bone not found in {glb_path.name}")
        bpy.ops.object.mode_set(mode='OBJECT')
        return None
    
    # Get world-space head position
    pelvis_world_pos = armature_obj.matrix_world @ pelvis_bone.head
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return np.array([pelvis_world_pos.x, pelvis_world_pos.y, pelvis_world_pos.z])


def validate_single_file(glb_path: Path, reference_pelvis: np.ndarray, verbose: bool = True) -> Tuple[bool, float]:
    """
    Validate a single GLB file's root alignment.
    
    Returns:
        (pass: bool, error_mm: float)
    """
    pelvis_pos = get_pelvis_position_from_glb(glb_path)
    
    if pelvis_pos is None:
        return False, float('inf')
    
    # Calculate distance error
    error = np.linalg.norm(pelvis_pos - reference_pelvis)
    error_mm = error * 1000  # Convert to mm
    
    # Pass if error < 0.1mm
    passed = error_mm < 0.1
    
    if verbose:
        status = "✓" if passed else "✗"
        print(f"{status} {glb_path.name}: {error_mm:.3f}mm error {'(PASS)' if passed else '(FAIL)'}")
        if not passed and error_mm < 1.0:
            print(f"  Note: Close but not quite - reference: {reference_pelvis}, actual: {pelvis_pos}")
    
    return passed, error_mm


def main():
    """Main entry point for validation script."""
    # Parse arguments
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    
    if len(argv) < 1:
        print("Usage: blender --background --python validate_root_alignment.py -- <glb_file_or_dir> [--limit N]")
        print("Example: blender --background --python validate_root_alignment.py -- data/output/ --limit 5")
        return
    
    input_path = Path(argv[0])
    limit = None
    if '--limit' in argv:
        limit = int(argv[argv.index('--limit') + 1])
    
    # Load reference
    print("=" * 60)
    print("ROOT ALIGNMENT VALIDATION")
    print("=" * 60)
    reference_pelvis = load_reference_pelvis()
    print(f"\nReference pelvis position: {reference_pelvis}")
    print(f"Acceptance threshold: 0.1mm\n")
    
    # Find GLB files
    if input_path.is_file():
        glb_files = [input_path]
    else:
        glb_files = sorted(input_path.rglob('*_retargeted.glb'))
        if limit:
            glb_files = glb_files[:limit]
    
    if not glb_files:
        print(f"⚠️  No GLB files found in {input_path}")
        return
    
    print(f"Validating {len(glb_files)} file(s)...\n")
    
    # Validate each file
    results = []
    for glb_path in glb_files:
        passed, error_mm = validate_single_file(glb_path, reference_pelvis)
        results.append((glb_path.name, passed, error_mm))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed_count = sum(1 for _, p, _ in results if p)
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"Passed: {passed_count}/{total_count} ({pass_rate:.1f}%)")
    
    if passed_count < total_count:
        print("\nFailed files:")
        for name, passed, error_mm in results:
            if not passed:
                print(f"  - {name}: {error_mm:.3f}mm")
    
    # Exit code based on pass rate
    sys.exit(0 if pass_rate == 100 else 1)


if __name__ == '__main__':
    main()

