"""Check armature transform in GLB"""
import bpy
import sys
from pathlib import Path

glb_path = Path(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1])

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.import_scene.gltf(filepath=str(glb_path))

armature = None
for obj in bpy.context.scene.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature:
    print(f"Armature: {armature.name}")
    print(f"Location: {armature.location}")
    print(f"Rotation: {armature.rotation_euler}")
    print(f"Scale: {armature.scale}")
    print(f"Matrix World:")
    for row in armature.matrix_world:
        print(f"  {row}")
    
    # Get root bone at frame 0
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    root_bone = armature.pose.bones.get("Pelvis")
    if root_bone:
        print(f"\nRoot bone (Pelvis) at frame 0:")
        print(f"  Location: {root_bone.location}")
        print(f"  Matrix:")
        for row in root_bone.matrix:
            print(f"    {row}")
        world_mat = armature.matrix_world @ root_bone.matrix
        print(f"  World position: [{world_mat[0][3]}, {world_mat[1][3]}, {world_mat[2][3]}]")
