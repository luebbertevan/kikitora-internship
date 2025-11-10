# A-Pose Debugging Plan


## Read the code








Now that `apose_from_blender.npz` stores the Blender armature’s rest-pose coordinates, we need to trace where the mismatch creeps in. Below is a structured approach you can follow to pinpoint and fix the remaining differences.

---

## 1. Verify Exported Data

### 1.1 Inspect Blender UI vs NPZ

1. Open `New-A-Pose.blend`.
2. Select `SMPLH_Armature` → Pose Mode → select each bone head.
3. Ensure the transform orientation is **GLOBAL**.
4. Compare those coordinates with `J_ABSOLUTE` printed by the exporter (or load the NPZ in Python).

```python
import numpy as np
data = np.load('data/reference/apose_from_blender.npz')
J = data['J_ABSOLUTE']
print(J.shape)  # (52, 3)
print(J[0])     # pelvis head
```

### 1.2 Confirm NPZ matches Blender (your numbers)

-   Pelvis head ~ `(-0.001795, -0.028219, 0.920356)`
-   Pelvis tail ~ `(-0.002728, 0.023431, 0.820739)` (good sanity check)
-   Repeat for shoulder/hip joints.

If there are still discrepancies, re-check the armature world matrix or scale (should be identity `Matrix 4x4`). The exporter now prints these values for double-checking.

---

## 2. Instrument `retarget.py`

Use the debug helpers you added (or re-add):

```python
def _log_position_diff(label, positions):
    ...

def _collect_empty_positions(empties):
    ...

def _collect_bone_head_positions(armature):
    ...
```

Call `_log_position_diff` at key stages:

1. **Before armature creation**: `print("Using frame 0 pose (from FK) ...")`.
2. **After armature creation**: compute rest pose from the placed edit bones.
3. **After setting frame-0 empties**: should match `J_ABSOLUTE_APOSE`.
4. **After constraints**: `_collect_bone_head_positions`.
5. **After baking**: final pose bones.

Monitor frame 0 diffs at each step for max and mean errors:

```
_log_position_diff("After constraints (pre-bake)", _collect_bone_head_positions(armature))
```

This confirms exactly where values deviate from `J_ABSOLUTE_APOSE`.

---

## 3. Compare With FK

Run FK manually before constraints/bake:

```python
from retarget import forward_kinematics, J_ABSOLUTE_APOSE
poses = np.zeros((156,))
joints = forward_kinematics(poses, J_ABSOLUTE_APOSE[0])
print(np.max(np.linalg.norm(joints - J_ABSOLUTE_APOSE, axis=1)))
```

This should show how close the FK output is to the NPZ data (makes sure our offsets are consistent).

---

## 4. Inspect Constraints

-   Without `COPY_LOCATION`, the bones never move to new positions; they only rotate.
-   With `COPY_LOCATION`, they double-transform. Ensure the armature rest lengths exactly match `J_ABSOLUTE_APOSE` (i.e. rebuild rest pose if needed).
-   Check if any other constraints (`STRETCH_TO`, etc.) persist. They can still stretch bones.

You may need to disable the frame 0 override temporarily and regenerate the armature from A-pose to confirm the rest geometry matches.

---

## 5. Bake Step Sanity Check

After `bpy.ops.nla.bake` runs, make sure the resulting pose bones on frame 0 still match the empties from earlier. If not, something after the bake (pose overrides, JSON pose, etc.) is touching frame 0.

Set the `limit` flag in `retarget.py` to run just one file (e.g., `--limit 1`) so debugging is quick.

---

## 6. Optional: Visualize Differences

Use a small script to visualize both sets of joint positions (e.g., Matplotlib axes or a small Blender script to drop empties at `J_ABSOLUTE_APOSE` and `forward_kinematics` output).

```python
import numpy as np
import matplotlib.pyplot as plt
...
```

This will show which joints are still off and by how much.

---

## Recap Checklist

1. **Exporter sanity** – Blender UI matches NPZ? ✅
2. **Armature build** – built from the right rest pose? Check offsets.
3. **Constraints** – only rotate (no stretch) and located on the correct target empties.
4. **Baking** – debug logs show frame 0 matching after bake; nothing overrides it later.
5. **FK** – confirm the frame 0 ONE is identity relative to new rest pose if needed.

Once these steps are done, we should be able to reproduce the Blender A-pose at frame 0 and keep the rest of the mocap animation intact. Use this plan as a checklist for your troubleshooting sessions. Good luck!


## Paris Questiosn

1. Why are the little bone circle things different sizes? The knee bones are bigger than the spine bones. What's up with that? Not sure it actually means "scale" in blender tbh
2. The knees are not level and I think that's an issue with the ground truth A pose you made
3. look at way more data points and see what % of animations have clearly bad bone positions/rotations