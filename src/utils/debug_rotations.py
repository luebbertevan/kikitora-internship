"""
Debug: Check what compute_bone_rotation is receiving for frame 1
"""
import bpy
import numpy as np
from pathlib import Path
import sys
from mathutils import Vector, Quaternion
import importlib.util

# Load constants and functions from retarget.py
retarget_path = Path("src/scripts/retarget.py")
spec = importlib.util.spec_from_file_location("retarget", retarget_path)
retarget_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retarget_module)

JOINT_NAMES = retarget_module.JOINT_NAMES
SMPL_H_PARENTS = retarget_module.SMPL_H_PARENTS
forward_kinematics = retarget_module.forward_kinematics
compute_bone_rotation = retarget_module.compute_bone_rotation

def analyze_rotation_computation(glb_path, npz_path, ref_path):
    """See what positions are being used to compute rotations"""
    
    # Load data
    input_data = np.load(str(npz_path))
    poses = input_data['poses']
    trans = input_data['trans']
    
    # Load target skeleton (sets global SMPL_OFFSETS)
    ref_data = np.load(str(ref_path))
    retarget_module.SMPL_OFFSETS = ref_data['SMPL_OFFSETS']
    retarget_module.J_ABSOLUTE = ref_data['J_ABSOLUTE']
    
    # Import GLB to get actual armature bone rest positions
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    
    armature = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    
    if not armature:
        print("No armature!")
        return
    
    # Switch to Edit mode to access rest bones
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get actual rest positions from armature
    print("="*80)
    print("REST POSITIONS: FK vs Armature Bones")
    print("="*80)
    
    zero_poses = np.zeros((52, 3)).flatten()
    apose_joints = forward_kinematics(zero_poses, np.zeros(3))
    
    # Analyze frame 1 FK
    frame1_joints = forward_kinematics(poses[1], trans[1])
    
    print(f"\nTrans[1]: {trans[1]}\n")
    
    # Check first few joints
    for i in [0, 1, 2, 3]:
        bone_name = JOINT_NAMES[i]
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        child_idx = children[0] if children else None
        if i == 0 and children:
            child_idx = 3
        
        edit_bone = armature.data.edit_bones[bone_name] if bone_name in armature.data.edit_bones else None
        
        print(f"Joint {i} ({bone_name})")
        
        # FK rest (apose_joints)
        fk_rest_head = apose_joints[i]
        print(f"  FK Rest Head: [{fk_rest_head[0]:8.3f}, {fk_rest_head[1]:8.3f}, {fk_rest_head[2]:8.3f}]")
        
        if edit_bone:
            arm_rest_head = edit_bone.head
            arm_rest_tail = edit_bone.tail
            print(f"  Arm Rest Head: [{arm_rest_head.x:8.3f}, {arm_rest_head.y:8.3f}, {arm_rest_head.z:8.3f}]")
            print(f"  Arm Rest Tail: [{arm_rest_tail.x:8.3f}, {arm_rest_tail.y:8.3f}, {arm_rest_tail.z:8.3f}]")
            print(f"  ⚠️  FK vs Arm: diff = {np.linalg.norm(np.array(arm_rest_head) - fk_rest_head) * 100:.3f} cm")
        
        if child_idx is not None:
            fk_rest_tail = apose_joints[child_idx]
            print(f"  FK Rest Tail: [{fk_rest_tail[0]:8.3f}, {fk_rest_tail[1]:8.3f}, {fk_rest_tail[2]:8.3f}]")
            
            # Frame 1 target
            fk_frame1_child = frame1_joints[child_idx]
            print(f"  FK Frame1 Target: [{fk_frame1_child[0]:8.3f}, {fk_frame1_child[1]:8.3f}, {fk_frame1_child[2]:8.3f}]")
            
            # What rotation would be computed?
            bone_head = Vector(apose_joints[i])
            bone_tail = Vector(apose_joints[child_idx])
            target_pos = Vector(frame1_joints[child_idx])
            
            rotation = compute_bone_rotation(bone_head, bone_tail, target_pos)
            print(f"  Computed Rotation: {rotation}")
            
            # Check: apply rotation to rest direction
            rest_dir = (bone_tail - bone_head).normalized()
            # Rotate rest_dir by rotation
            rotated_dir = rotation @ rest_dir
            target_dir = (target_pos - bone_head).normalized()
            
            print(f"  Rest Dir: [{rest_dir.x:.3f}, {rest_dir.y:.3f}, {rest_dir.z:.3f}]")
            print(f"  Rotated Dir: [{rotated_dir.x:.3f}, {rotated_dir.y:.3f}, {rotated_dir.z:.3f}]")
            print(f"  Target Dir: [{target_dir.x:.3f}, {target_dir.y:.3f}, {target_dir.z:.3f}]")
            print(f"  Match? {np.isclose(rotated_dir, target_dir, atol=0.01).all()}")
        
        print()


if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = sys.argv[1:]
    
    glb_path = Path(argv[0])
    npz_path = Path(argv[1]) if len(argv) > 1 else Path(str(glb_path).replace('.glb', '.npz'))
    ref_path = Path("src/scripts/target_reference.npz")
    
    analyze_rotation_computation(glb_path, npz_path, ref_path)
