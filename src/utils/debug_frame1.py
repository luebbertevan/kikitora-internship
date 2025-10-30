"""
Debug frame 1: Analyze what's happening with joint positions and relationships
"""
import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector, Matrix

JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)


def get_bone_head_world(armature_obj, bone_name, frame_idx):
    """Get bone head position in world space at given frame"""
    bpy.context.scene.frame_set(frame_idx)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.view_layer.update()
    
    if bone_name not in armature_obj.pose.bones:
        return None
    
    pose_bone = armature_obj.pose.bones[bone_name]
    rest_bone = armature_obj.data.bones[bone_name]
    
    # Bone head in local space (rest position)
    local_head = rest_bone.head_local.copy()
    
    # For root, add location offset
    if bone_name == "Pelvis":
        local_head += pose_bone.location
    
    # Transform to world via pose bone matrix
    bone_matrix = pose_bone.matrix
    posed_head_local = bone_matrix @ Vector((0, 0, 0, 1))
    world_pos = armature_obj.matrix_world @ posed_head_local
    
    return world_pos


def analyze_frames(glb_path, npz_path):
    """Compare frame 0 vs frame 1"""
    
    # Load input data
    input_data = np.load(str(npz_path))
    poses = input_data['poses']
    trans = input_data['trans']
    
    print(f"Input data:")
    print(f"  trans[0]: {trans[0]}")
    print(f"  trans[1]: {trans[1]}")
    print(f"  poses[0][:9]: {poses[0][:9]} (first 3 joints)")
    print(f"  poses[1][:9]: {poses[1][:9]} (first 3 joints)")
    
    # Import GLB
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    armature = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    
    if not armature:
        print("No armature found!")
        return
    
    print(f"\n{'='*80}")
    print("JOINT POSITIONS: Frame 0 vs Frame 1")
    print(f"{'='*80}\n")
    
    # Analyze first few joints in tree (Pelvis, L_Hip, R_Hip, Spine1)
    key_joints = [0, 1, 2, 3]  # Pelvis, L_Hip, R_Hip, Spine1
    
    for i in key_joints:
        bone_name = JOINT_NAMES[i]
        parent_idx = SMPL_H_PARENTS[i]
        parent_name = JOINT_NAMES[parent_idx] if parent_idx >= 0 else "None"
        
        pos_0 = get_bone_head_world(armature, bone_name, 0)
        pos_1 = get_bone_head_world(armature, bone_name, 1)
        
        if pos_0 and pos_1:
            diff = (pos_1 - pos_0).length * 100  # in cm
            
            print(f"Joint {i} ({bone_name:20s}) - Parent: {parent_name}")
            print(f"  Frame 0: [{pos_0.x:8.3f}, {pos_0.y:8.3f}, {pos_0.z:8.3f}]")
            print(f"  Frame 1: [{pos_1.x:8.3f}, {pos_1.y:8.3f}, {pos_1.z:8.3f}]")
            print(f"  Change:  [{pos_1.x-pos_0.x:8.3f}, {pos_1.y-pos_0.y:8.3f}, {pos_1.z-pos_0.z:8.3f}] ({diff:.3f} cm)")
            
            # If has parent, check relationship
            if parent_idx >= 0:
                parent_pos_0 = get_bone_head_world(armature, parent_name, 0)
                parent_pos_1 = get_bone_head_world(armature, parent_name, 1)
                
                if parent_pos_0 and parent_pos_1:
                    rel_0 = (pos_0 - parent_pos_0).length * 100
                    rel_1 = (pos_1 - parent_pos_1).length * 100
                    print(f"  Distance to {parent_name}: Frame 0 = {rel_0:.3f} cm, Frame 1 = {rel_1:.3f} cm")
                    if abs(rel_1 - rel_0) > 1.0:
                        print(f"  ⚠️  BONE LENGTH CHANGED by {abs(rel_1-rel_0):.3f} cm!")
            
            print()


if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = sys.argv[1:]
    
    glb_path = Path(argv[0])
    npz_path = Path(argv[1]) if len(argv) > 1 else Path(str(glb_path).replace('.glb', '.npz'))
    
    analyze_frames(glb_path, npz_path)
