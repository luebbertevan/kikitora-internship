# Extracting A-Pose Reference Data

This guide explains how to extract the reference skeleton data from `A-Pose.FBX`.

## What This Does

Extracts:

-   Joint positions in A-pose (`J_ABSOLUTE`)
-   Bone offsets relative to parents (`SMPL_OFFSETS`)
-   Bone lengths

These will replace the hardcoded values in `retarget.py`.

## Running the Extraction

### Option 1: Default Paths (Easiest)

If `A-Pose.FBX` is in `src/` directory, run:

```bash
blender --background --python src/utils/extract_apose_reference.py
```

Output will be saved to `config/apose_reference.npz`

### Option 2: Custom Paths

```bash
blender --background --python src/utils/extract_apose_reference.py -- src/A-Pose.FBX config/apose_reference.npz
```

### On macOS

If Blender is installed at `/Applications/Blender.app`:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/utils/extract_apose_reference.py -- src/A-Pose.FBX config/apose_reference.npz
```

## Output

Creates `config/apose_reference.npz` containing:

-   `J_ABSOLUTE`: (52, 3) numpy array - joint positions in A-pose
-   `SMPL_OFFSETS`: (52, 3) numpy array - bone offsets from parent
-   `bone_lengths`: Dictionary of bone name → length

## Verification

You can verify the extracted data:

```python
import numpy as np

data = np.load('config/apose_reference.npz')
print(f"J_ABSOLUTE shape: {data['J_ABSOLUTE'].shape}")
print(f"SMPL_OFFSETS shape: {data['SMPL_OFFSETS'].shape}")
print(f"\nFirst 5 joints:")
for i in range(5):
    print(f"  Joint {i}: {data['J_ABSOLUTE'][i]}")
```

## Troubleshooting

-   **"No armature found"**: FBX doesn't contain an armature, or bone names don't match
-   **"Bone X not found"**: Bone naming in FBX doesn't match expected SMPL-H names
-   Check that `A-Pose.FBX` contains all 52 SMPL+H bones with correct names
