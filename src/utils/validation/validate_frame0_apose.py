"""
============================================================================
VALIDATE FRAME 0 A-POSE
============================================================================

PURPOSE:
    Validates that frame 0 of retargeted GLB files matches the reference 
    A-pose. Compares all 52 joint positions against the reference and reports 
    per-joint errors. Can process single files or entire directories.

RELEVANCE: ✅ ACTIVE - Primary validation tool for M4+
    Core validation script ensuring animations start with correct A-pose. 
    Part of the standard validation suite.

MILESTONE: M4 (A-pose standardization - ACTIVE)

USAGE:
    blender --background --python validate_frame0_apose.py -- <GLB_FILE_OR_DIR> [--limit N]

EXAMPLE:
    blender --background --python validate_frame0_apose.py -- data/test_small --limit 3
============================================================================
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector


# SMPL+H Joint Names
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def extract_frame0_joint_positions(glb_path: Path) -> np.ndarray:
    """
    Extract joint positions from frame 0 of a GLB.
    
    Returns:
        (52, 3) array of joint positions in armature local space
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)
    
    # Import GLB
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    # Find armature
    armature_obj = next((obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'), None)
    if not armature_obj:
        raise RuntimeError(f"No armature found in {glb_path}")
    
    # Set to frame 0
    bpy.context.scene.frame_set(0)
    
    # Extract joint positions
    # First, get rest pose positions from edit bones (armature local space)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones
    rest_positions = {}
    for joint_name in JOINT_NAMES:
        edit_bone = edit_bones.get(joint_name)
        if edit_bone:
            rest_positions[joint_name] = np.array([edit_bone.head.x, edit_bone.head.y, edit_bone.head.z])
    
    # Now check pose bones to see if we're at rest pose or need to use pose transform
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = armature_obj.pose.bones
    joint_positions = np.zeros((len(JOINT_NAMES), 3))
    
    # Check if all bones are at identity (rest pose)
    all_identity = True
    for pose_bone in pose_bones:
        quat = pose_bone.rotation_quaternion
        is_identity = abs(quat.w - 1.0) < 1e-6 and abs(quat.x) < 1e-6 and abs(quat.y) < 1e-6 and abs(quat.z) < 1e-6
        is_no_offset = np.allclose(pose_bone.location, [0, 0, 0], atol=1e-6)
        if not (is_identity and is_no_offset):
            all_identity = False
            break
    
    if all_identity:
        # All bones at rest pose, use edit bone positions (already in armature local space)
        for i, joint_name in enumerate(JOINT_NAMES):
            if joint_name in rest_positions:
                joint_positions[i] = rest_positions[joint_name]
    else:
        # Need to use pose transforms
        for i, joint_name in enumerate(JOINT_NAMES):
            pose_bone = pose_bones.get(joint_name)
            if pose_bone:
                bone = pose_bone.bone
                # pose_bone.matrix gives transform in armature local space
                pose_head = pose_bone.matrix @ bone.head
                joint_positions[i] = np.array([pose_head.x, pose_head.y, pose_head.z])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return joint_positions


def load_reference_positions() -> np.ndarray:
    """Load reference A-pose joint positions from NPZ."""
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference NPZ not found at {ref_path}")
    ref = np.load(str(ref_path))
    return ref['J_ABSOLUTE']


def compare_to_reference(glb_positions: np.ndarray, reference_positions: np.ndarray, 
                          threshold_mm: float = 1.0) -> dict:
    """
    Compare joint positions and return detailed statistics.
    
    Returns:
        dict with error statistics and pass/fail status
    """
    errors = np.linalg.norm(glb_positions - reference_positions, axis=1)  # Per-joint distance in meters
    errors_mm = errors * 1000.0  # Convert to mm
    
    max_error = np.max(errors_mm)
    mean_error = np.mean(errors_mm)
    median_error = np.median(errors_mm)
    
    passed = max_error < threshold_mm
    
    return {
        'passed': passed,
        'max_error_mm': max_error,
        'mean_error_mm': mean_error,
        'median_error_mm': median_error,
        'errors_per_joint_mm': errors_mm,
        'pelvis_error_mm': errors_mm[0],  # Pelvis is index 0
        'threshold_mm': threshold_mm,
        'failing_joints': [(JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}", errors_mm[i]) 
                           for i in range(len(errors_mm)) if errors_mm[i] >= threshold_mm],
    }


def validate_single_glb(glb_path: Path, reference_positions: np.ndarray, 
                        threshold_mm: float = 1.0) -> dict:
    """Validate a single GLB file."""
    try:
        glb_positions = extract_frame0_joint_positions(glb_path)
        comparison = compare_to_reference(glb_positions, reference_positions, threshold_mm)
        
        # Add file info
        comparison['file'] = glb_path.name
        comparison['file_path'] = str(glb_path)
        
        return comparison
    except Exception as e:
        return {
            'file': glb_path.name,
            'file_path': str(glb_path),
            'error': str(e),
            'passed': False,
        }


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    
    if len(argv) < 1:
        print("Usage: blender --background --python validate_frame0_apose.py -- <GLB_FILE_OR_DIR> [--limit N]")
        print("\nExample:")
        print("  blender --background --python validate_frame0_apose.py -- data/reference/reference_apose_10frames.glb")
        print("  blender --background --python validate_frame0_apose.py -- data/test_small --limit 3")
        return
    
    input_path = Path(argv[0])
    limit = None
    if "--limit" in argv:
        limit_idx = argv.index("--limit")
        if limit_idx + 1 < len(argv):
            limit = int(argv[limit_idx + 1])
    
    # Load reference positions
    print("=" * 80)
    print("FRAME 0 A-POSE VALIDATION")
    print("=" * 80)
    
    try:
        reference_positions = load_reference_positions()
        print(f"✓ Loaded reference A-pose from smplh_target_reference.npz")
        print(f"  Reference pelvis position: {reference_positions[0]}")
    except Exception as e:
        print(f"✗ Error loading reference: {e}")
        return
    
    # Find GLB files
    glb_files = []
    if input_path.is_dir():
        for glb_file in sorted(input_path.rglob('*.glb')):
            glb_files.append(glb_file)
    elif input_path.suffix == '.glb':
        glb_files.append(input_path)
    else:
        print(f"Error: Input path must be a directory or .glb file")
        return
    
    if not glb_files:
        print("No GLB files found to validate.")
        return
    
    if limit:
        glb_files = glb_files[:limit]
    
    print(f"\nValidating {len(glb_files)} file(s) with threshold: 1.0mm")
    print("=" * 80)
    
    results = []
    passed_count = 0
    
    for glb_file in glb_files:
        result = validate_single_glb(glb_file, reference_positions, threshold_mm=1.0)
        results.append(result)
        
        if 'error' in result:
            print(f"\n✗ {result['file']}: ERROR - {result['error']}")
        else:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{status} {result['file']}")
            print(f"  Max error: {result['max_error_mm']:.3f}mm")
            print(f"  Mean error: {result['mean_error_mm']:.3f}mm")
            print(f"  Median error: {result['median_error_mm']:.3f}mm")
            print(f"  Pelvis error: {result['pelvis_error_mm']:.3f}mm")
            
            if not result['passed']:
                print(f"  Failing joints: {len(result['failing_joints'])}/{len(JOINT_NAMES)}")
                # Show top 5 worst joints
                sorted_failures = sorted(result['failing_joints'], key=lambda x: x[1], reverse=True)[:5]
                for joint_name, error in sorted_failures:
                    print(f"    - {joint_name}: {error:.3f}mm")
            else:
                passed_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed_count}/{len(results)} ({passed_count/len(results)*100:.1f}%)")
    
    if passed_count != len(results):
        print("\nFailed files:")
        for result in results:
            if not result.get('passed', False):
                if 'error' in result:
                    print(f"  - {result['file']}: {result['error']}")
                else:
                    print(f"  - {result['file']}: max error {result['max_error_mm']:.3f}mm")
    
    # Expected behavior check
    print("\n" + "=" * 80)
    print("EXPECTED BEHAVIOR")
    print("=" * 80)
    
    # Check if reference_apose_10frames.glb was tested
    ref_glb = next((r for r in results if 'reference_apose_10frames' in r['file']), None)
    if ref_glb:
        if ref_glb.get('passed', False):
            print("✅ reference_apose_10frames.glb PASSED (as expected)")
        else:
            print(f"❌ reference_apose_10frames.glb FAILED (unexpected! max error: {ref_glb['max_error_mm']:.3f}mm)")
    
    # Check test_small files
    test_files = [r for r in results if 'test_small' in r.get('file_path', '') and '_retargeted' in r['file']]
    if test_files:
        all_failed = all(not r.get('passed', False) for r in test_files)
        if all_failed:
            print("✅ All retargeted GLBs in test_small FAILED (as expected - frame 0 is incorrect)")
        else:
            passed_test = [r for r in test_files if r.get('passed', False)]
            print(f"⚠️  {len(passed_test)} retargeted GLB(s) in test_small PASSED (unexpected! frame 0 should be incorrect)")


if __name__ == '__main__':
    main()

# Validate a single GLB
#blender --background --python src/utils/validation/validate_frame0_apose.py -- data/reference/reference_apose_10frames.glb

# Validate all GLBs in a directory
#blender --background --python src/utils/validation/validate_frame0_apose.py -- data/test_small --limit 3