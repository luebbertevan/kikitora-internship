import bpy
import numpy as np
import sys
from pathlib import Path
from mathutils import Vector, Quaternion

# Import our retarget module to reuse constants and FK
import importlib.util
retarget_path = Path("src/scripts/retarget.py")
spec = importlib.util.spec_from_file_location("retarget", retarget_path)
retarget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retarget)

SMPL_H_PARENTS = retarget.SMPL_H_PARENTS
JOINT_NAMES = retarget.JOINT_NAMES
axis_angle_to_rotation_matrix = retarget.axis_angle_to_rotation_matrix
forward_kinematics = retarget.forward_kinematics

# Ensure SMPL offsets are loaded from target_reference.npz like our script
from numpy.typing import NDArray


def create_tpose_armature(name: str = "SMPLH_Armature_Original") -> bpy.types.Object:
    zero_poses = np.zeros((52, 3), dtype=np.float64).flatten()
    zero_trans = np.zeros(3, dtype=np.float64)
    tpose_joints = forward_kinematics(zero_poses, zero_trans)

    armature = bpy.data.armatures.new(name)
    armature_obj = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.edit_bones

    for i in range(52):
        bone = edit_bones.new(JOINT_NAMES[i])
        bone.head = Vector(tpose_joints[i])
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        if children:
            if i == 0:
                bone.tail = Vector(tpose_joints[3])
            else:
                bone.tail = Vector(tpose_joints[children[0]])
        else:
            bone.tail = Vector(tpose_joints[i]) + Vector((0, 0.05, 0))

    bone_list = list(edit_bones)
    for i, parent_idx in enumerate(SMPL_H_PARENTS):
        if parent_idx != -1:
            bone_list[i].parent = bone_list[parent_idx]

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


def retarget_original_style(armature_obj: bpy.types.Object, poses: NDArray[np.float64], trans: NDArray[np.float64]) -> None:
    num_frames = len(poses)
    zero_poses = np.zeros((52, 3), dtype=np.float64).flatten()
    zero_trans = np.zeros(3, dtype=np.float64)
    tpose_joints = forward_kinematics(zero_poses, zero_trans)

    bone_info = []
    for i in range(52):
        children = [j for j in range(52) if SMPL_H_PARENTS[j] == i]
        child_idx = children[0] if children else None
        if i == 0 and children:
            child_idx = 3
        bone_info.append({
            'head': Vector(tpose_joints[i]),
            'tail': Vector(tpose_joints[child_idx]) if child_idx is not None else None,
            'child_idx': child_idx
        })

    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    for frame_idx in range(num_frames):
        bpy.context.scene.frame_set(frame_idx)
        frame_joints = forward_kinematics(poses[frame_idx], trans[frame_idx])

        for i in range(52):
            pose_bone = armature_obj.pose.bones[JOINT_NAMES[i]]
            if i == 0:
                pose_bone.location = Vector(frame_joints[i])
                pose_bone.keyframe_insert(data_path="location", frame=frame_idx)
            else:
                pose_bone.location = Vector((0, 0, 0))

            info = bone_info[i]
            if info['child_idx'] is not None:
                target_pos = Vector(frame_joints[info['child_idx']])
                rest_dir = (info['tail'] - info['head']).normalized()
                target_dir = (target_pos - info['head']).normalized()
                rotation = rest_dir.rotation_difference(target_dir)
                pose_bone.rotation_mode = 'QUATERNION'
                pose_bone.rotation_quaternion = rotation
                pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_idx)

    bpy.ops.object.mode_set(mode='OBJECT')


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    npz_path = Path(argv[0])

    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Load target reference into retarget module globals
    ref = np.load("src/scripts/target_reference.npz")
    retarget.SMPL_OFFSETS = ref['SMPL_OFFSETS']
    retarget.J_ABSOLUTE = ref['J_ABSOLUTE']

    # Load NPZ
    data = np.load(str(npz_path))
    poses = data['poses']
    trans = data['trans']

    # Create T-pose armature and retarget
    arm = create_tpose_armature()
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(poses) - 1
    retarget_original_style(arm, poses, trans)

    # Export as _orig.glb next to npz
    out = npz_path.with_suffix('.glb')
    out_orig = out.with_name(out.stem + '_orig.glb')
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=str(out_orig), export_format='GLB', use_selection=True, export_animations=True)
    print(f"Exported original-style GLB to: {out_orig}")


if __name__ == "__main__":
    main()
