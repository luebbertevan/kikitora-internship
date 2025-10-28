# Standup Questions

## Critical Questions

### 1. Reference Data - Do you have a working example of correctly formatted data?

Do you have a working example of correctly formatted .glb? Need to see what A-pose + consistent skeleton looks like.

### 2. T-pose vs A-pose

Project says "ideal template skeleton" and shows T-pose. Is T-pose just for armature limb length reference, and A-pose for actual output?

### 3. Files in Drive

-   `data/models/amass_joints_h36m_60.pkl` - Why is this here? Related to training pipeline?
-   `config/smplh.json` - Should I use this for bone structure or ignore?
-   `data/models/smplh_tpose.glb` - Is this the consistent skeleton reference?

---

### Design Approach

Should the system accept ANY target skeleton/pose (flexible retargeting), or just focus on A-pose requirement?

---

## M1 Summary (What I Found)

-   Extracted and analyzed AMASS data
-   Frame 0 is **rest pose** (arms at 0°, not A-pose)
-   No A-pose examples in data
-   Ready for M2 once I have target reference
