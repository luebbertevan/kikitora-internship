# Commands to Run Scripts

## Blender Path

**Use the full path** (blender is usually not in PATH):

```bash
/Applications/Blender.app/Contents/MacOS/Blender
```

## create_glb_from_npz.py

**Basic command (use full path):**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/create_glb_from_npz.py -- <input_folder>
```

**If blender is in your PATH:**

```bash
blender --background --python src/originals/create_glb_from_npz.py -- <input_folder>
```

**With options:**

```bash
blender --background --python src/originals/create_glb_from_npz.py -- \
  <input_folder> \
  [--limit N] \
  [--json-pose <path>] \
  [--add-cube] \
  [--cube-size <size>] \
  [--cube-location X Y Z]
```

**Examples:**

```bash
# Process all NPZ files in test_small folder
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/create_glb_from_npz.py -- data/test_small

# Process only first 3 files
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/create_glb_from_npz.py -- data/test_small --limit 3

# Add a cube parented to armature
blender --background --python src/originals/create_glb_from_npz.py -- data/test_small --add-cube --cube-size 0.5 --cube-location 0 0 1
```

**Arguments:**

-   `input_folder`: Path to folder containing NPZ files (searches recursively)
-   `--limit N`: Limit number of files to process (for testing)
-   `--json-pose <path>`: Optional JSON pose file to override frame 0 after baking
-   `--add-cube`: Add a cube mesh parented to the armature
-   `--cube-size <size>`: Size of the cube (default: 1.0)
-   `--cube-location X Y Z`: Location of cube (default: 0 0 0)

---

## retarget.py (Current Pipeline)

**Basic command (use full path):**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/retarget.py -- <input_folder>
```

**If blender is in your PATH:**

```bash
blender --background --python src/retarget.py -- <input_folder>
```

**With options:**

```bash
blender --background --python src/retarget.py -- \
  <input_folder> \
  [--limit N] \
  [--cube-size <size>] \
  [--cube-location X Y Z]
```

**Examples:**

```bash
# Process all NPZ files
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/retarget.py -- data/test

# Process only first 3 files
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/retarget.py -- data/test_small --limit 3

# Add a cube
blender --background --python src/retarget.py -- data/test_small --cube-size 0.5 --cube-location 0 0 1
```

**Arguments:**

-   `input_folder`: Path to folder containing NPZ files (searches recursively)
-   `--limit N`: Limit number of files to process (for testing)
-   `--cube-size <size>`: Size of the cube (default: 1.0)
-   `--cube-location X Y Z`: Location of cube (default: 0 0 0)

---

## original_retarget.py

**Basic command (use full path):**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/original_retarget.py -- <input_folder>
```

**If blender is in your PATH:**

```bash
blender --background --python src/originals/original_retarget.py -- <input_folder>
```

**With options:**

```bash
blender --background --python src/originals/original_retarget.py -- \
  <input_folder> \
  [--limit N]
```

**Examples:**

```bash
# Process all NPZ files
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/original_retarget.py -- data/test_small

# Process only first 3 files
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/original_retarget.py -- data/test_small --limit 3
```

**Arguments:**

-   `input_folder`: Path to folder containing NPZ files (searches recursively)
-   `--limit N`: Limit number of files to process (for testing)

---

**Note:** All examples above use the full path. If `blender` is in your PATH, you can use `blender` instead of the full path.

---

## Fixed Versions (Proper Scene Clearing)

**Fixed versions** that properly clear data blocks between files to prevent corruption:

### create_glb_from_npz_fixed.py

**Basic command:**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/create_glb_from_npz_fixed.py -- data/test
```

**With limit:**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/create_glb_from_npz_fixed.py -- data/test_small --limit 3
```

### original_retarget_fixed.py

**Basic command:**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/original_retarget_fixed.py -- data/test_small
```

**With limit:**

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/originals/original_retarget_fixed.py -- data/test_small --limit 3
```

**What's fixed:**

-   Properly clears all data blocks (armatures, actions, meshes) between files
-   Uses unique names per file to avoid collisions
-   Prevents animation mixing/corruption
-   Each file is processed independently

---

## Output Locations

-   **create_glb_from_npz.py**: Exports to `create_glb_output/` folder (modified for comparison)
-   **retarget.py**: Exports to same folder as input NPZ file (with `.glb` extension)
-   **original_retarget.py**: Exports to `original_retarget_output/` folder (modified for comparison)

---

## Notes

1. **`--background`**: Runs Blender without GUI (required for scripts)
2. **`--`**: Separates Blender arguments from script arguments
3. **Script arguments**: Everything after `--` is passed to the Python script
4. **Recursive search**: All scripts search recursively for `.npz` files in the input folder



/Applications/Blender.app/Contents/MacOS/Blender \
  /Users/evan/Blender/KikiTora-Internship/New-A-Pose.blend \
  --background \
  --python src/utils/reference/export_apose_from_blender.py \
  -- data/reference/apose_from_blender.npz
