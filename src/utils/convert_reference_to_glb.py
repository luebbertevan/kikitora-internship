"""
Simple script to convert the reference A-pose NPZ to a GLB with multiple frames of the same pose.

Usage:
    blender --background --python convert_reference_to_glb.py -- <NUM_FRAMES> [OUTPUT_PATH]
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector


# SMPL+H kinematic tree
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)

# Joint names
JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def add_cube_and_parent(armature_obj: bpy.types.Object, cube_size: float = 0.05, 
                         cube_location: tuple = (0.0, 0.0, 0.0)) -> bpy.types.Object:
    """Add a small cube parented to the armature (required for pipeline)."""
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=cube_location)
    cube = bpy.context.active_object
    cube.name = "ParentedCube"
    cube.parent = armature_obj
    cube.parent_type = 'ARMATURE'
    return cube


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    
    if len(argv) < 1:
        print("Usage: blender --background --python convert_reference_to_glb.py -- <NUM_FRAMES> [OUTPUT_PATH]")
        print("Example: blender --background --python convert_reference_to_glb.py -- 10 data/reference/reference_apose_10frames.glb")
        return
    
    num_frames = int(argv[0])
    output_path = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent.parent.parent / 'data' / 'reference' / f'reference_apose_{num_frames}frames.glb'
    
    # Load reference A-pose
    ref_path = Path(__file__).parent.parent.parent / 'data' / 'reference' / 'smplh_target_reference.npz'
    if not ref_path.exists():
        print(f"Error: Reference NPZ not found at {ref_path}")
        return
    
    ref_data = np.load(str(ref_path))
    J_ABSOLUTE = ref_data['J_ABSOLUTE']
    
    print(f"Loaded reference A-pose with {len(J_ABSOLUTE)} joints")
    print(f"Creating GLB with {num_frames} frames of the same A-pose")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)
    
    # Create armature
    armature_data = bpy.data.armatures.new("SMPL_H_Armature")
    armature_obj = bpy.data.objects.new("SMPL_H_Armature", armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    
    # Create bones from reference positions
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones
    bone_list = []
    
    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i] if i < len(JOINT_NAMES) else f"Joint_{i}")
        bone.head = Vector(J_ABSOLUTE[i])
        
        # Set tail pointing toward first child
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if children:
            if i == 0:  # Pelvis
                bone.tail = Vector(J_ABSOLUTE[3])  # Spine1
            else:
                bone.tail = Vector(J_ABSOLUTE[children[0]])
        else:
            # End bones - point in Y+ direction
            bone.tail = Vector(J_ABSOLUTE[i]) + Vector((0, 0.05, 0))
        
        bone_list.append(bone)
    
    # Set parent relationships
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set frame range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = num_frames - 1
    
    # Set armature display
    armature_obj.show_in_front = True
    armature_data.display_type = 'WIRE'
    
    # Add cube (required for pipeline)
    cube = add_cube_and_parent(armature_obj, cube_size=0.05)
    print(f"✓ Added cube parented to armature")
    
    # Set all bones to rest pose (identity rotations) for all frames
    print("Setting all frames to A-pose (rest pose = identity rotations)...")
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    
    for frame in range(num_frames):
        bpy.context.scene.frame_set(frame)
        for bone_name in JOINT_NAMES:
            pose_bone = armature_obj.pose.bones.get(bone_name)
            if pose_bone:
                pose_bone.rotation_quaternion = (1, 0, 0, 0)  # Identity
                pose_bone.location = (0, 0, 0)  # No offset
                pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                pose_bone.keyframe_insert(data_path="location", frame=frame)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"✓ Set {num_frames} frames to A-pose")
    
    # Export to GLB
    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    cube.select_set(True)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_skins=True,
    )
    
    print(f"✓ Successfully exported to: {output_path}")


if __name__ == '__main__':
    main()

