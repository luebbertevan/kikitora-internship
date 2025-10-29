# Viewing Raw AMASS Animations in Blender

Quick guide to export and view raw (pre-retarget) animations from AMASS data.

## Export Raw Animation to GLB

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python src/originals/scripts/create_glb_from_npz.py -- \
  "data/extracted/ACCAD/Female1Gestures_c3d" \
  --limit 1 --add-cube
```

**Options:**

-   `--limit 1` - Process only 1 file (remove to process all)
-   `--add-cube` - Add child cube mesh (required by pipeline)

**Output:** GLB file saved next to the source `.npz` file

## View Animation in Blender

1. **Open Blender** (GUI mode)
2. **Import:** File → Import → glTF 2.0 (.glb/.gltf)
3. **Navigate** to exported GLB file location
4. **Select** the `.glb` file and import

5. **Play animation:**

    - Press **Space** to play/pause
    - Or use timeline controls at bottom
    - Scrub timeline slider to jump to frames

## Note

This exports the **raw, pre-retarget** animation (inconsistent bone lengths, variable frame 0 poses). Useful for comparing before/after retargeting.
