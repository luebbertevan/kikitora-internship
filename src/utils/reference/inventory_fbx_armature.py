"""
============================================================================
INVENTORY FBX ARMATURE
============================================================================

PURPOSE:
    Analyzes an FBX armature and exports bone information to CSV, including 
    bone names, parent relationships, bone lengths, number of children, and 
    whether each bone is an end bone. Used for understanding FBX structure 
    and creating mappings.

RELEVANCE: 📚 ARCHIVE - Historical (M2 DONE, inventory already created)
    Kept for reference. Useful if examining new FBX files or debugging 
    bone structure issues.

MILESTONE: M2 (FBX analysis - COMPLETED)

USAGE:
    blender --background --python inventory_fbx_armature.py -- <FBX_PATH> <OUT_CSV>

EXAMPLE:
    blender --background --python inventory_fbx_armature.py -- docs/standup/A-Pose.FBX docs/standup/apose_bones.csv
============================================================================
"""
import bpy
import csv
import sys
from pathlib import Path


def find_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def export_bones_csv(armature_obj, out_csv: Path):
    bones = armature_obj.data.bones
    rows = [["bone_name", "parent", "length", "num_children", "is_end"]]

    name_to_children = {b.name: [] for b in bones}
    for b in bones:
        if b.parent:
            name_to_children[b.parent.name].append(b.name)

    for b in bones:
        parent = b.parent.name if b.parent else ""
        length = (b.tail_local - b.head_local).length
        num_children = len(name_to_children[b.name])
        is_end = 1 if num_children == 0 else 0
        rows.append([b.name, parent, f"{length:.6f}", num_children, is_end])

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) < 2:
        print("Usage: blender --background --python inventory_fbx_armature.py -- <FBX_PATH> <OUT_CSV>")
        return

    fbx_path = Path(argv[0])
    out_csv = Path(argv[1])

    # Reset scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))

    arm = find_armature()
    if not arm:
        raise RuntimeError("No armature found after FBX import")

    export_bones_csv(arm, out_csv)
    print(f"✓ Exported bones CSV to: {out_csv}")


if __name__ == "__main__":
    main()


