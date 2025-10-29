"""
Debug: Check actual armature bone positions vs target reference
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


def check_armature_bones(glb_path: Path, reference_path: Path):
    """Check armature bone rest positions"""
    
    # Load reference
    ref_data = np.load(str(reference_path))
    ref_joints = ref_data['J_ABSOLUTE']
    
    # Import GLB
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    armature_obj = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature_obj = obj
            break
    
    if not armature_obj:
        print("No armature found!")
        return
    
    print("Armature bone rest positions (Edit Mode):\n")
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    for i, bone_name in enumerate(JOINT_NAMES):
        if bone_name in armature_obj.data.edit_bones:
            bone = armature_obj.data.edit_bones[bone_name]
            ref_pos = ref_joints[i]
            bone_pos = bone.head
            
            diff = (Vector(bone_pos) - Vector(ref_pos)).length
            
            if diff > 0.1:
                print(f"Joint {i:2d} {bone_name:20s}:")
                print(f"  Bone head: [{bone_pos.x:8.3f}, {bone_pos.y:8.3f}, {bone_pos.z:8.3f}]")
                print(f"  Reference: [{ref_pos[0]:8.3f}, {ref_pos[1]:8.3f}, {ref_pos[2]:8.3f}]")
                print(f"  Diff: {diff*100:.3f} cm\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = sys.argv[1:]
    
    glb_path = Path(argv[0])
    ref_path = Path(argv[1])
    check_armature_bones(glb_path, ref_path)
