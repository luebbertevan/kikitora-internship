import bpy
import json
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List
from mathutils import Vector


JOINT_NAMES: List[str] = [
    "Pelvis","L_Hip","R_Hip","Spine1","L_Knee","R_Knee","Spine2",
    "L_Ankle","R_Ankle","Spine3","L_Foot","R_Foot","Neck",
    "L_Collar","R_Collar","Head","L_Shoulder","R_Shoulder",
    "L_Elbow","R_Elbow","L_Wrist","R_Wrist",
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]

SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)


def find_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def load_mapping(mapping_path: Path) -> Dict[str, str]:
    with mapping_path.open() as f:
        m = json.load(f)
    # Basic validation
    missing = [k for k in JOINT_NAMES if k not in m or not m[k]]
    if missing:
        raise ValueError(f"Mapping missing entries for: {missing[:5]}{'...' if len(missing)>5 else ''}")
    return m


def extract_joints_from_fbx(armature_obj, mapping: Dict[str, str]) -> np.ndarray:
    # Ensure edit mode to access edit_bones heads/tails in armature space
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones
    heads = np.zeros((52, 3), dtype=np.float64)
    for i, smpl_name in enumerate(JOINT_NAMES):
        fbx_name = mapping[smpl_name]
        if fbx_name not in edit_bones:
            raise KeyError(f"FBX bone not found for {smpl_name}: '{fbx_name}'")
        head = edit_bones[fbx_name].head
        # Convert to world space then back to object if needed; we keep object space (armature at identity assumed)
        heads[i] = np.array([head.x, head.y, head.z], dtype=np.float64)
    bpy.ops.object.mode_set(mode='OBJECT')
    return heads


def build_offsets(J_abs: np.ndarray) -> np.ndarray:
    offsets = np.zeros_like(J_abs)
    for i in range(52):
        p = int(SMPL_H_PARENTS[i])
        if p == -1:
            offsets[i] = J_abs[i]
        else:
            offsets[i] = J_abs[i] - J_abs[p]
    return offsets


def create_smplh_armature(J_abs: np.ndarray, name: str = "SMPLH_Target"):
    armature = bpy.data.armatures.new(name)
    armature_obj = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.show_in_front = True
    armature.display_type = 'WIRE'
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.edit_bones
    for i, jn in enumerate(JOINT_NAMES):
        b = edit_bones.new(jn)
        b.head = Vector(J_abs[i])
        # Tail toward first child or small stub
        children = [c for c in range(52) if SMPL_H_PARENTS[c] == i]
        if children:
            child = children[0]
            b.tail = Vector(J_abs[child])
        else:
            b.tail = Vector(J_abs[i]) + Vector((0, 0.05, 0))
    # Parents
    bone_list = list(edit_bones)
    for i, p in enumerate(SMPL_H_PARENTS):
        if p != -1:
            bone_list[i].parent = bone_list[int(p)]
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj


def add_cube_and_parent(armature_obj):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    cube = bpy.context.active_object
    cube.name = "ParentedCube"
    bpy.ops.object.select_all(action='DESELECT')
    cube.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    return cube


def main():
    # Args: -- <FBX_PATH> <MAPPING_JSON> <OUT_DIR>
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if len(argv) < 3:
        print("Usage: blender --background --python extract_smplh_from_fbx.py -- <FBX> <MAPPING_JSON> <OUT_DIR>")
        return
    fbx_path = Path(argv[0])
    mapping_path = Path(argv[1])
    out_dir = Path(argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    # Reset scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    arm = find_armature()
    if not arm:
        raise RuntimeError("No armature found in FBX")

    mapping = load_mapping(mapping_path)
    J_abs = extract_joints_from_fbx(arm, mapping)
    SMPL_offsets = build_offsets(J_abs)

    # Save NPZ
    npz_path = out_dir / 'smplh_target_reference.npz'
    np.savez(npz_path, J_ABSOLUTE=J_abs, SMPL_OFFSETS=SMPL_offsets, JOINT_NAMES=np.array(JOINT_NAMES))
    print(f"✓ Wrote {npz_path}")

    # Build armature and export GLB
    # Reset scene for a clean export
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    arm2 = create_smplh_armature(J_abs)
    cube = add_cube_and_parent(arm2)
    bpy.ops.object.select_all(action='DESELECT')
    arm2.select_set(True)
    cube.select_set(True)
    bpy.context.view_layer.objects.active = arm2
    glb_path = out_dir / 'smplh_target.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format='GLB', use_selection=True, export_animations=False)
    print(f"✓ Exported {glb_path}")


if __name__ == '__main__':
    main()


