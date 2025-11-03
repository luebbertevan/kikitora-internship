"""
Debug script to check armature rest pose bone positions from a GLB.
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector


JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def check_armature_rest_pose(glb_path: Path):
    """Check rest pose bone.head positions in armature local space."""
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
        print(f"No armature found in {glb_path}")
        return
    
    print("=" * 80)
    print(f"ARMATURE REST POSE BONE POSITIONS")
    print("=" * 80)
    print(f"Armature object location: {armature_obj.location}")
    print(f"Armature object rotation: {armature_obj.rotation_euler}")
    print(f"Armature object scale: {armature_obj.scale}")
    print()
    
    # Get rest pose bone positions
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    edit_bones = armature_obj.data.edit_bones
    rest_positions = np.zeros((len(JOINT_NAMES), 3))
    
    for i, joint_name in enumerate(JOINT_NAMES):
        edit_bone = edit_bones.get(joint_name)
        if edit_bone:
            rest_positions[i] = np.array([edit_bone.head.x, edit_bone.head.y, edit_bone.head.z])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("Rest pose bone.head positions (armature local space):")
    print(f"Pelvis (index 0): {rest_positions[0]}")
    print(f"L_Hip (index 1): {rest_positions[1]}")
    print(f"R_Hip (index 2): {rest_positions[2]}")
    print(f"Spine1 (index 3): {rest_positions[3]}")
    
    # Load reference
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    ref = np.load(str(ref_path))
    J_ref = ref['J_ABSOLUTE']
    
    print("\nReference positions (from NPZ):")
    print(f"Pelvis (index 0): {J_ref[0]}")
    print(f"L_Hip (index 1): {J_ref[1]}")
    print(f"R_Hip (index 2): {J_ref[2]}")
    print(f"Spine1 (index 3): {J_ref[3]}")
    
    print("\nDifferences:")
    for i in range(4):
        diff = rest_positions[i] - J_ref[i]
        print(f"{JOINT_NAMES[i]}: {diff} ({np.linalg.norm(diff)*1000:.3f}mm)")


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if len(argv) < 1:
        print("Usage: blender --background --python debug_armature_rest_pose.py -- <GLB_FILE>")
        sys.exit(1)
    
    check_armature_rest_pose(Path(argv[0]))

