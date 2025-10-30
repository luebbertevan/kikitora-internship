"""
Debug script to compare frame 0 of output GLB with target reference
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector, Matrix
from numpy.typing import NDArray


# SMPL+H kinematic tree
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def get_world_joint_positions(armature_obj, frame_idx: int) -> NDArray:
    """Get world-space joint positions from armature at given frame"""
    bpy.context.view_layer.objects.active = armature_obj
    bpy.context.scene.frame_set(frame_idx)
    
    # Switch to pose mode to apply animations
    bpy.ops.object.mode_set(mode='POSE')
    
    # Update dependencies to ensure transforms are current
    bpy.context.view_layer.update()
    
    joint_positions = np.zeros((52, 3))
    
    # Use bone head positions - simplest approach
    for i, bone_name in enumerate(JOINT_NAMES):
        if bone_name in armature_obj.pose.bones:
            pose_bone = armature_obj.pose.bones[bone_name]
            
            # Get bone head in armature-local space (rest position + location offset)
            rest_bone = armature_obj.data.bones[bone_name]
            local_head = Vector(rest_bone.head_local)
            
            # Apply root location offset
            if i == 0:
                local_head += pose_bone.location
            
            # Transform to world space using armature transform
            # The bone's head position after pose = rest_head transformed by pose_bone.matrix
            # But since head is at bone origin, we use the translation from matrix
            bone_matrix = pose_bone.matrix
            posed_head_local = bone_matrix @ Vector((0, 0, 0, 1))  # Head is at bone origin
            world_pos = armature_obj.matrix_world @ posed_head_local
            
            joint_positions[i] = [world_pos.x, world_pos.y, world_pos.z]
        else:
            print(f"Warning: Bone {bone_name} not found in armature")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return joint_positions


def compare_frame0_to_reference(glb_path: Path, reference_path: Path) -> None:
    """Compare frame 0 of GLB with target reference"""
    
    # Load target reference
    print(f"Loading target reference: {reference_path}")
    ref_data = np.load(str(reference_path))
    ref_joints_base = ref_data['J_ABSOLUTE']  # A-pose at origin
    
    # Load input data to get trans[0]
    npz_path = Path(str(glb_path).replace('.glb', '.npz'))
    if npz_path.exists():
        input_data = np.load(str(npz_path))
        trans_0 = input_data['trans'][0]
        print(f"Input trans[0]: {trans_0}")
        # Frame 0 should be at J_ABSOLUTE + trans[0]
        ref_joints = ref_joints_base + trans_0
        print(f"Expected frame 0 root: {ref_joints[0]}")
    else:
        print("Warning: Could not find input .npz, comparing to base reference")
        ref_joints = ref_joints_base
    
    print(f"Reference joints shape: {ref_joints.shape}")
    print(f"Reference joint 0 (Pelvis): {ref_joints[0]}")
    print(f"Reference joint 3 (Spine1): {ref_joints[3]}")
    
    # Clear scene and import GLB
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    print(f"\nImporting GLB: {glb_path}")
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    # Find armature
    armature_obj = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature_obj = obj
            break
    
    if not armature_obj:
        print("ERROR: No armature found in GLB!")
        return
    
    print(f"Found armature: {armature_obj.name}")
    
    # Get frame 0 joint positions
    print("\nExtracting frame 0 joint positions...")
    frame0_joints = get_world_joint_positions(armature_obj, 0)
    
    # Compare
    print("\n" + "="*80)
    print("COMPARISON: Frame 0 vs Target Reference")
    print("="*80)
    
    max_diff = 0.0
    max_diff_idx = -1
    differences = []
    
    for i in range(52):
        diff = np.linalg.norm(frame0_joints[i] - ref_joints[i])
        differences.append(diff)
        if diff > max_diff:
            max_diff = diff
            max_diff_idx = i
        
        if diff > 1.0:  # Show joints with >1cm difference
            print(f"Joint {i:2d} ({JOINT_NAMES[i]:20s}): diff = {diff:8.3f} cm")
            print(f"    Frame 0:  [{frame0_joints[i][0]:8.3f}, {frame0_joints[i][1]:8.3f}, {frame0_joints[i][2]:8.3f}]")
            print(f"    Reference: [{ref_joints[i][0]:8.3f}, {ref_joints[i][1]:8.3f}, {ref_joints[i][2]:8.3f}]")
    
    print("\n" + "="*80)
    print(f"Summary:")
    print(f"  Max difference: {max_diff:.3f} cm at joint {max_diff_idx} ({JOINT_NAMES[max_diff_idx]})")
    print(f"  Average difference: {np.mean(differences):.3f} cm")
    print(f"  Mean squared error: {np.mean(np.array(differences)**2):.3f} cm²")
    
    # Check if frame 0 should match exactly
    tolerance = 0.1  # 1mm tolerance
    matching = sum(1 for d in differences if d < tolerance)
    print(f"\n  Joints within {tolerance}cm: {matching}/52 ({100*matching/52:.1f}%)")
    
    if max_diff < tolerance:
        print("✓ Frame 0 matches target reference!")
    else:
        print(f"✗ Frame 0 does NOT match (max diff: {max_diff:.3f} cm)")


def main():
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = sys.argv[1:]
    
    if len(argv) < 2:
        print("Usage: blender --background --python debug_frame0.py -- <glb_path> <reference_path>")
        sys.exit(1)
    
    glb_path = Path(argv[0])
    reference_path = Path(argv[1])
    
    if not glb_path.exists():
        print(f"Error: GLB not found: {glb_path}")
        sys.exit(1)
    
    if not reference_path.exists():
        print(f"Error: Reference not found: {reference_path}")
        sys.exit(1)
    
    compare_frame0_to_reference(glb_path, reference_path)


if __name__ == "__main__":
    main()
