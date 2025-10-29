## retarget.py usage

Run Blender in background and pass either a single AMASS .npz file or a directory. By default, .glb files are written next to each processed .npz; use `--output DIR` to send them elsewhere. Use `--limit` to cap files when using a directory.

### Requirements

-   Blender installed (command-line accessible)
-   AMASS-format .npz files with keys: poses (N×156), trans (N×3)

### Target skeleton options

1. Default (recommended): no target provided/found

-   Behavior: silently uses built-in A-pose target skeleton.
-   Command:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python src/scripts/retarget.py -- "/path/to/your/input_or_folder"
```

2. Auto-load local target reference

-   Behavior: if `target_reference.npz` exists in the same directory as `retarget.py`, it is loaded. If missing/invalid, falls back to default A-pose.
-   Command: same as (1)

3. Explicit custom target reference

-   Behavior: overrides default/local with your .npz containing J_ABSOLUTE and SMPL_OFFSETS (52×3 each, SMPL-H order).
-   Command:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python src/scripts/retarget.py -- "/path/to/your/input_or_folder" \
  --target "/absolute/path/to/custom_target.npz"
```

-   If the given --target is missing/invalid, the script continues with default A-pose.

### Arguments

-   input_path (positional): a single .npz file or directory (relative or absolute)
-   --limit N (optional): process at most N files (directory input only)
-   --target PATH (optional): custom target .npz with J_ABSOLUTE, SMPL_OFFSETS
-   --output DIR (optional): directory for .glb outputs (defaults to next to each .npz)

### Example

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python src/scripts/retarget.py -- \
  "/Users/evan/fractal-bootcamp/kikitora-internship/data/extracted/ACCAD" \
  --limit 3 \
  --target "/Users/evan/fractal-bootcamp/kikitora-internship/src/scripts/target_reference.npz" \
  --output "/Users/evan/fractal-bootcamp/kikitora-internship/data/output/glb"
```

### Output

-   For file input: a .glb is exported alongside the input .npz
-   For directory input: a .glb is exported alongside each processed .npz
-   All outputs use consistent bone lengths; frame 0 is the target pose (default A-pose)

### Notes

-   Default is production-friendly: no reference files required
-   target_reference.npz lives next to retarget.py when used
-   SMPL-H joint order is assumed; names match JOINT_NAMES in retarget.py
