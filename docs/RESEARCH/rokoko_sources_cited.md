# Rokoko Studio Live - Source Citations

## Primary Sources

### 1. Official GitHub Repository

-   **URL**: https://github.com/Rokoko/rokoko-studio-live-blender
-   **README**: https://github.com/Rokoko/rokoko-studio-live-blender#readme
-   **License**: MIT (see `LICENSE.md` in repository)
-   **Content**: Main repository with source code, README, and documentation

### 2. Official Documentation

-   **Support Documentation**: https://support.rokoko.com/hc/en-us/categories/4410420388113-Rokoko-Plugins
-   **Support Portal**: https://support.rokoko.com/
-   **Content**: Official user guides, tutorials, and API documentation

### 3. Source Code (Local Installation)

-   **Location**: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/`
-   **Key Files**:
    -   `operators/retargeting.py` - Retarget operator implementation (lines 76-537)
    -   `core/retargeting.py` - Helper functions (`get_source_armature()`, `get_target_armature()`)
    -   `properties.py` - Scene properties (`rsl_retargeting_armature_source`, `rsl_retargeting_bone_list`, etc.)
    -   `panels/retargeting.py` - UI panel implementation
    -   `__init__.py` - Add-on metadata (bl_info)

### 4. Video Tutorial

-   **URL**: https://youtu.be/Od8Ecr70A4Q
-   **Title**: Rokoko Studio Live Retargeting Tutorial
-   **Content**: Step-by-step visual guide for retargeting

### 5. Add-on Metadata

From `__init__.py`:

```python
bl_info = {
    'name': 'Rokoko Studio Live for Blender',
    'author': 'Rokoko Electronics ApS',
    'category': 'Animation',
    'location': 'View 3D > Tool Shelf > Rokoko',
    'description': 'Stream your Rokoko Studio animations directly into Blender',
    'version': (1, 4, 3),
    'blender': (2, 80, 0),
    'wiki_url': 'https://github.com/Rokoko/rokoko-studio-live-blender#readme',
}
```

## Code References

### Operator Definition

**Source**: `operators/retargeting.py` (lines 76-80)

```python
class RetargetAnimation(bpy.types.Operator):
    bl_idname = "rsl.retarget_animation"
    bl_label = "Retarget Animation"
    bl_description = "Retargets the animation from the source armature to the target armature"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
```

### Scene Properties

**Source**: `properties.py`

-   `Scene.rsl_retargeting_armature_source` (PointerProperty)
-   `Scene.rsl_retargeting_armature_target` (PointerProperty)
-   `Scene.rsl_retargeting_auto_scaling` (BoolProperty)
-   `Scene.rsl_retargeting_use_pose` (EnumProperty)
-   `Scene.rsl_retargeting_bone_list` (CollectionProperty)

### Helper Functions

**Source**: `core/retargeting.py`

```python
def get_source_armature():
    return bpy.context.scene.rsl_retargeting_armature_source

def get_target_armature():
    return bpy.context.scene.rsl_retargeting_armature_target
```

## README Retargeting Section

**Source**: GitHub README (lines 197-241)

Key information:

1. **Process**: Open Retargeting panel → Set source/target → Build Bone List → Verify mapping → Configure options → Execute
2. **Auto Scale**: Enable for different-sized armatures
3. **Use Pose**: Select appropriate pose (POSE or REST)
4. **Important**: Both armatures must be in the same pose

## How Information Was Gathered

1. **Direct Source Code Inspection**: Read actual implementation files
2. **Python Console Inspection**: Used `help()` and `get_rna_type()` to inspect operators
3. **README Analysis**: Extracted retargeting workflow from GitHub README
4. **UI Panel Inspection**: Analyzed `panels/retargeting.py` to understand user workflow
5. **Operator Execution**: Tested operator calls to understand behavior

## Verification

All information in the documentation files has been verified against:

-   ✅ Actual source code files
-   ✅ Python console operator inspection
-   ✅ GitHub README
-   ✅ Official documentation links

## License

The Rokoko Studio Live add-on is licensed under MIT License (see repository `LICENSE.md`).
