import bpy
import numpy as np
import sys
import argparse
from pathlib import Path
from mathutils import Vector, Matrix
from typing import Optional

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


def find_armature() -> Optional[bpy.types.Object]:
    """Find the first armature object in the scene."""
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def extract_j_absolute_from_rest_pose(armature_obj: bpy.types.Object) -> np.ndarray:
    """
    Extract J_ABSOLUTE from armature rest pose (edit_bones).
    This gives the rest pose positions, not the posed positions.
    """
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    edit_bones = armature_obj.data.edit_bones
    J_ABSOLUTE = np.zeros((52, 3), dtype=np.float64)
    
    for i, joint_name in enumerate(JOINT_NAMES):
        if joint_name not in edit_bones:
            raise KeyError(f"Bone '{joint_name}' not found in armature")
        
        bone = edit_bones[joint_name]
        head_local = bone.head.to_4d()
        head_world = armature_obj.matrix_world @ head_local
        J_ABSOLUTE[i] = np.array([head_world.x, head_world.y, head_world.z], dtype=np.float64)
        if joint_name == "Pelvis":
            tail_world = armature_obj.matrix_world @ bone.tail.to_4d()
            print(f"[REST] Pelvis head: {J_ABSOLUTE[i]}, tail: {[tail_world.x, tail_world.y, tail_world.z]}")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return J_ABSOLUTE


def compute_smpl_offsets(J_ABSOLUTE: np.ndarray) -> np.ndarray:
    """Compute SMPL_OFFSETS from J_ABSOLUTE using parent tree."""
    SMPL_OFFSETS = np.zeros((52, 3), dtype=np.float64)
    
    for i in range(52):
        parent_idx = int(SMPL_H_PARENTS[i])
        if parent_idx == -1:
            # Root joint - offset is just its position
            SMPL_OFFSETS[i] = J_ABSOLUTE[i]
        else:
            # Child joint - offset is relative to parent
            SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]
    
    return SMPL_OFFSETS


def main():
    parser = argparse.ArgumentParser(
        description="Export A-pose J_ABSOLUTE (world space) from Blender armature to NPZ."
    )
    parser.add_argument(
        "output_npz",
        nargs="?",
        type=Path,
        default=None,
        help="Optional output NPZ path (defaults to A-Pose.npz next to this script).",
    )
    cli_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parsed_args = parser.parse_args(cli_args)
    if parsed_args.output_npz is None:
        output_path = Path(__file__).parent / "A-Pose.npz"
        print(f"No output path supplied; defaulting to {output_path}")
    else:
        output_path = parsed_args.output_npz
    
    print("="*80)
    print("Export A-Pose from Blender Armature")
    print("="*80)
    
    # Find armature
    armature_obj = find_armature()
    if armature_obj is None:
        print("❌ Error: No armature found in scene")
        print("   Please ensure an armature object exists in the Blender scene")
        sys.exit(1)
    
    print(f"\n✓ Found armature: {armature_obj.name} (scale={armature_obj.scale})")
    print(f"Matrix world:\n{armature_obj.matrix_world}")
    
    print("\n📊 Extracting from REST POSE (edit_bones)...")
    J_ABSOLUTE = extract_j_absolute_from_rest_pose(armature_obj)
    SMPL_OFFSETS = compute_smpl_offsets(J_ABSOLUTE)
    
    print(f"✓ Extracted J_ABSOLUTE: shape {J_ABSOLUTE.shape}")
    print("=== J_ABSOLUTE (world space) ===")
    for idx, name in enumerate(JOINT_NAMES):
        print(f"{idx:02d} {name:15s}: {J_ABSOLUTE[idx]}")
    print(f"✓ Computed SMPL_OFFSETS: shape {SMPL_OFFSETS.shape}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        str(output_path),
        J_ABSOLUTE=J_ABSOLUTE,
        SMPL_OFFSETS=SMPL_OFFSETS,
        JOINT_NAMES=np.array(JOINT_NAMES)
    )
    
    print(f"\n✅ Saved to: {output_path}")
    print(f"   Keys: J_ABSOLUTE, SMPL_OFFSETS, JOINT_NAMES")
    print("="*80)


if __name__ == "__main__":
    main()

