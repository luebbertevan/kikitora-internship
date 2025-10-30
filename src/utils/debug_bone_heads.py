"""Check what bone.head values actually are in the armature"""
import bpy
import sys
import numpy as np
from pathlib import Path

glb_path = Path(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1])
ref_path = Path(sys.argv[sys.argv.index("--") + 2] if "--" in sys.argv else sys.argv[2])

JOINT_NAMES = [
    "Pelvis", "L_Hip", "R_Hip", "Spine1", "L_Knee", "R_Knee", "Spine2", 
    "L_Ankle", "R_Ankle", "Spine3", "L_Foot", "R_Foot", "Neck", 
    "L_Collar", "R_Collar", "Head", "L_Shoulder", "R_Shoulder", 
    "L_Elbow", "R_Elbow", "L_Wrist", "R_Wrist"
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.import_scene.gltf(filepath=str(glb_path))

armature = None
for obj in bpy.context.scene.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature:
    ref = np.load(str(ref_path))
    ref_joints = ref['J_ABSOLUTE']
    
    print("Bone rest positions (Edit Mode) vs Reference:\n")
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    for i, name in enumerate(JOINT_NAMES):
        if name in armature.data.edit_bones:
            bone = armature.data.edit_bones[name]
            ref_pos = ref_joints[i]
            bone_pos = bone.head
            
            print(f"{i:2d} {name:20s}:")
            print(f"    bone.head:    [{bone_pos.x:8.3f}, {bone_pos.y:8.3f}, {bone_pos.z:8.3f}]")
            print(f"    Reference:    [{ref_pos[0]:8.3f}, {ref_pos[1]:8.3f}, {ref_pos[2]:8.3f}]")
            diff = (Vector(bone_pos) - Vector(ref_pos)).length * 100
            if diff > 0.1:
                print(f"    DIFF: {diff:.3f} cm")
            print()
