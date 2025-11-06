# Rokoko Studio Live Research Summary

## Sources and References

-   **GitHub Repository**: https://github.com/Rokoko/rokoko-studio-live-blender
-   **README**: https://github.com/Rokoko/rokoko-studio-live-blender#readme
-   **Official Documentation**: https://support.rokoko.com/hc/en-us/categories/4410420388113-Rokoko-Plugins
-   **Support Portal**: https://support.rokoko.com/
-   **Video Tutorial**: https://youtu.be/Od8Ecr70A4Q
-   **Source Code**: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/`

## ✅ R1.1 Complete: Operator Discovery

### Key Finding

**Rokoko operators are under `bpy.ops.rsl.*` not `bpy.ops.rokoko.*`**

Where `rsl` = Rokoko Studio Live

### Main Operator

-   **`bpy.ops.rsl.retarget_animation`**
    -   ID: `rsl.retarget_animation`
    -   Type: `RSL_OT_retarget_animation`
    -   Description: "Retargets the animation from the source armature to the target armature"

### How It Works

The operator uses **scene properties** (not direct parameters):

1. **Source Armature**: `context.scene.rsl_retargeting_armature_source`
2. **Target Armature**: `context.scene.rsl_retargeting_armature_target`
3. **Bone Mapping**: `context.scene.rsl_retargeting_bone_list`
4. **Settings**: Auto-scaling, pose mode

### Process

1. Validates source has animation
2. Builds bone mapping (auto or manual)
3. Auto-scales source to match target (if enabled)
4. Creates constraints on target (COPY_ROTATION, COPY_LOCATION for roots)
5. Bakes animation to keyframes
6. Cleans up temporary objects

### Documentation Created

-   ✅ `rokoko_operator_found.md` - Initial discovery
-   ✅ `rokoko_retarget_operator_usage.md` - Complete usage guide
-   ✅ `inspect_rsl_operators.py` - Inspection script

## Next Steps (R1.2-R1.5)

### R1.2: Test with Sample Data

-   [ ] Load source armature with animation from NPZ → GLB
-   [ ] Load target armature (reference SMPL-H)
-   [ ] Set up bone mapping
-   [ ] Execute retargeting
-   [ ] Validate output

### R1.3: Bone Name Mapping

-   [ ] Document SMPL-H bone names
-   [ ] Test auto-detection accuracy
-   [ ] Create manual mapping if needed
-   [ ] Test with different bone naming conventions

### R1.4: Integration Testing

-   [ ] Test with actual AMASS NPZ files
-   [ ] Verify frame 0 A-pose handling
-   [ ] Test root alignment
-   [ ] Validate bone lengths

### R1.5: Limitations & Compatibility

-   [ ] Document any limitations
-   [ ] Test edge cases
-   [ ] Compare with manual retargeting approach
-   [ ] Assess if Rokoko can fully solve the project

## Files Reference

-   **Operator Source**: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/operators/retargeting.py`
-   **Helper Functions**: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/core/retargeting.py`
-   **Properties**: `/Users/evan/Library/Application Support/Blender/4.5/scripts/addons/rokoko-studio-live-blender-master/properties.py`
