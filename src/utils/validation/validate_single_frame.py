"""
============================================================================
VALIDATE SINGLE FRAME
============================================================================

PURPOSE:
    Validates a specific frame from a GLB file by extracting all joint 
    positions and comparing them to the reference A-pose positions. Provides 
    detailed per-joint error statistics and identifies joints with largest 
    deviations.

RELEVANCE: ✅ ACTIVE - Useful validation tool for debugging specific frames
    Helpful for troubleshooting individual frames that fail other validations 
    or for understanding pose accuracy at different frames.

MILESTONE: M3+ (Frame validation - ACTIVE)

USAGE:
    blender --background --python validate_single_frame.py -- <GLB_FILE> [FRAME_NUMBER]

EXAMPLE:
    blender --background --python validate_single_frame.py -- data/test_small/D6-\ CartWheel_poses_retargeted.glb 0
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


def extract_frame_joint_positions(glb_path: Path, frame_number: int = 0) -> np.ndarray:
    """
    Extract joint positions from a GLB at a specific frame.
    
    Returns:
        (52, 3) array of joint positions in world space
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
    
    # Set to desired frame
    bpy.context.scene.frame_set(frame_number)
    
    # Extract joint positions
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bones = armature_obj.pose.bones
    joint_positions = np.zeros((len(JOINT_NAMES), 3))
    
    for i, joint_name in enumerate(JOINT_NAMES):
        pose_bone = pose_bones.get(joint_name)
        if pose_bone:
            bone = pose_bone.bone
            
            # At frame 0 with identity rotations and zero locations, 
            # the bone should be at rest pose, so bone.head is correct
            # But we still need to apply any pose transform
            # The simplest: use bone.head in rest pose, which should match
            # the reference since armature was created from reference
            
            # Actually, let's compute the pose-space position properly:
            # pose_bone.matrix is the full transform (includes parents)
            # But for validation, we want just the local transform
            
            # Get pose-space head position in armature local space
            # pose_bone.matrix includes full parent chain transform
            # bone.head is rest pose position in bone's local space
            # pose_bone.matrix @ bone.head gives final position in armature local space
            pose_head = pose_bone.matrix @ bone.head
            joint_positions[i] = np.array([pose_head.x, pose_head.y, pose_head.z])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return joint_positions


def load_reference_positions() -> np.ndarray:
    """Load reference A-pose joint positions from NPZ."""
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    ref = np.load(str(ref_path))
    return ref['J_ABSOLUTE']


def compare_frames(glb_positions: np.ndarray, reference_positions: np.ndarray) -> dict:
    """
    Compare joint positions and return detailed statistics.
    
    Returns:
        dict with error statistics
    """
    errors = np.linalg.norm(glb_positions - reference_positions, axis=1)  # Per-joint distance in meters
    errors_mm = errors * 1000.0  # Convert to mm
    
    return {
        'max_error_mm': np.max(errors_mm),
        'mean_error_mm': np.mean(errors_mm),
        'median_error_mm': np.median(errors_mm),
        'errors_per_joint_mm': errors_mm,
        'pelvis_error_mm': errors_mm[0],  # Pelvis is index 0
    }


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    
    if len(argv) < 1:
        print("Usage: blender --background --python validate_single_frame.py -- <GLB_FILE> [FRAME_NUMBER]")
        print("Example: blender --background --python validate_single_frame.py -- 'data/test_small/D6- CartWheel_poses_retargeted.glb' 0")
        return
    
    glb_path = Path(argv[0])
    frame_number = int(argv[1]) if len(argv) > 1 else 0
    
    if not glb_path.exists():
        print(f"Error: GLB file not found: {glb_path}")
        return
    
    print("=" * 80)
    print(f"EXTRACTING FRAME {frame_number} FROM: {glb_path.name}")
    print("=" * 80)
    
    # Extract positions from GLB
    try:
        glb_positions = extract_frame_joint_positions(glb_path, frame_number)
        print(f"\n✓ Successfully extracted {len(glb_positions)} joint positions")
        print(f"  Pelvis position: {glb_positions[0]}")
    except Exception as e:
        print(f"✗ Error extracting positions: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load reference
    try:
        reference_positions = load_reference_positions()
        print(f"\n✓ Loaded reference A-pose positions")
        print(f"  Reference pelvis position: {reference_positions[0]}")
    except Exception as e:
        print(f"✗ Error loading reference: {e}")
        return
    
    # Compare
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    comparison = compare_frames(glb_positions, reference_positions)
    
    print(f"\nMax error: {comparison['max_error_mm']:.3f}mm")
    print(f"Mean error: {comparison['mean_error_mm']:.3f}mm")
    print(f"Median error: {comparison['median_error_mm']:.3f}mm")
    print(f"Pelvis error: {comparison['pelvis_error_mm']:.3f}mm")
    
    # Show joints with largest errors
    sorted_indices = np.argsort(comparison['errors_per_joint_mm'])[::-1]
    print(f"\nTop 10 joints with largest errors:")
    for idx in sorted_indices[:10]:
        joint_name = JOINT_NAMES[idx] if idx < len(JOINT_NAMES) else f"Joint_{idx}"
        error = comparison['errors_per_joint_mm'][idx]
        print(f"  {joint_name}: {error:.3f}mm")
    
    # Show per-axis differences for pelvis
    pelvis_diff = glb_positions[0] - reference_positions[0]
    print(f"\nPelvis difference (GLB - Reference):")
    print(f"  X: {pelvis_diff[0]*1000:.3f}mm")
    print(f"  Y: {pelvis_diff[1]*1000:.3f}mm")
    print(f"  Z: {pelvis_diff[2]*1000:.3f}mm")
    
    # Acceptance criteria check
    threshold_mm = 1.0
    passed = comparison['max_error_mm'] < threshold_mm
    print(f"\n{'=' * 80}")
    print(f"ACCEPTANCE CRITERIA (threshold: {threshold_mm}mm)")
    print(f"{'=' * 80}")
    print(f"Status: {'✅ PASS' if passed else '❌ FAIL'}")
    
    if not passed:
        failing_joints = np.sum(comparison['errors_per_joint_mm'] >= threshold_mm)
        print(f"  Joints failing threshold: {failing_joints}/{len(JOINT_NAMES)}")
        print(f"  Failing joints:")
        for idx in sorted_indices:
            if comparison['errors_per_joint_mm'][idx] >= threshold_mm:
                joint_name = JOINT_NAMES[idx] if idx < len(JOINT_NAMES) else f"Joint_{idx}"
                print(f"    {joint_name}: {comparison['errors_per_joint_mm'][idx]:.3f}mm")


if __name__ == '__main__':
    main()

