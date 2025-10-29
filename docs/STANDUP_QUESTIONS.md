# Standup Questions

## Critical Questions

### 1. Reference Data - Do you have a working example of correctly formatted data?

Do you have a working example of correctly formatted .glb? Need to see what A-pose + consistent skeleton looks like.

### 2. T-pose vs A-pose

**Answer from project:** T-pose is the "ideal template skeleton" (reference), but output frame 0 must be A-pose. **Question:** Should I use T-pose skeleton bone lengths as the consistent reference, then create A-pose from those same bone lengths?

### 3. Files in Drive

**Theory:** These are the "consistent skeleton" reference files mentioned in the project description.

-   `data/models/smplh_tpose.glb` - This is likely the "ideal template skeleton" from the project description. Is this the consistent reference skeleton? Should I extract bone lengths from this GLB programmatically, or use `config/smplh.json` joint positions?

-   `config/smplh.json` - Contains bone hierarchy + rest pose positions for all 52 bones with exact joint positions and bone lengths. **Theory:** This might define the consistent skeleton structure. Should I use this JSON instead of hardcoded `J_ABSOLUTE` in `retarget.py`?

-   `config/SMPL_H_Armature_transforms.json` - Blender export with edit_bones data (head/tail positions, transforms). **Theory:** Serialized Blender armature state. Is this a backup/reference, or should I use it to recreate the armature?

-   `data/models/amass_joints_h36m_60.pkl` - Why is this here? Related to training pipeline?

-   **Original files:** `src/originals/visualize_neutral_smplh.py` loads `model.npz` from SMPL+H and computes `J_ABSOLUTE` using `J_regressor.dot(v_template)`. Should I compute joint positions from the actual SMPL model file instead of hardcoded constants?

-   **Original files:** `src/originals/create_glb_from_npz.py` has `apply_json_pose_to_frame0()` function. What JSON pose format does this expect? Is this related to `config/SMPL_H_Armature_transforms.json`?

### 4. About `retarget.py`

**From project:** `retarget.py` exists but has bone length inconsistency problem. Implementation approach is up to me.

-   `retarget.py` computes bone rotations from joint positions - is this IK approach correct for solving the problem?
-   Should I modify `retarget.py` to create A-pose armature with consistent bone lengths, or build new code?

---

### Design Approach

**Answer from project:** "What the solution space looks like and all the implementation details are entirely up to you" - so flexible. **Question:** Is A-pose the only requirement, or should I design for flexible target poses?

---

## M1 Summary (What I Found)

-   Extracted and analyzed AMASS data
-   Frame 0 is **rest pose** (arms at 0°, not A-pose)
-   No A-pose examples in data
-   Ready for M2 once I have target reference
