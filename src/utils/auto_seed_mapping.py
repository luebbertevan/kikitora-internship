import csv
import json
import re
from pathlib import Path


SMPL_KEYS = [
    "Pelvis","L_Hip","R_Hip","Spine1","L_Knee","R_Knee","Spine2",
    "L_Ankle","R_Ankle","Spine3","L_Foot","R_Foot","Neck",
    "L_Collar","R_Collar","Head","L_Shoulder","R_Shoulder",
    "L_Elbow","R_Elbow","L_Wrist","R_Wrist",
] + [f"L_Hand_{i}" for i in range(15)] + [f"R_Hand_{i}" for i in range(15)]


def load_bones(csv_path: Path):
    bones = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            bones.append(row['bone_name'])
    return bones


def pick(candidates, names):
    for pat in candidates:
        rx = re.compile(pat, re.I)
        for n in names:
            if rx.search(n):
                return n
    return ""


def auto_map(names):
    m = {}
    # Core body
    m['Pelvis']      = pick([r'pelvis|hips?|root'], names)
    m['L_Hip']       = pick([r'left.*(thigh|hip)|thigh_l|l_?thigh|hip_l|lHip'], names)
    m['R_Hip']       = pick([r'right.*(thigh|hip)|thigh_r|r_?thigh|hip_r|rHip'], names)
    m['Spine1']      = pick([r'spine[_ ]?0?1|spine_low|lowerback'], names)
    m['Spine2']      = pick([r'spine[_ ]?0?2|spine_mid|midback'], names)
    m['Spine3']      = pick([r'spine[_ ]?0?3|spine_high|upperback|chest'], names)
    m['Neck']        = pick([r'neck'], names)
    m['Head']        = pick([r'head(?!_end)|head$'], names)
    # Legs
    m['L_Knee']      = pick([r'left.*knee|calf_l|l_?knee|shin_l'], names)
    m['R_Knee']      = pick([r'right.*knee|calf_r|r_?knee|shin_r'], names)
    m['L_Ankle']     = pick([r'left.*ankle|ankle_l'], names)
    m['R_Ankle']     = pick([r'right.*ankle|ankle_r'], names)
    m['L_Foot']      = pick([r'left.*foot(?!.*end)|foot_l'], names)
    m['R_Foot']      = pick([r'right.*foot(?!.*end)|foot_r'], names)
    # Shoulders/clavicles
    m['L_Collar']    = pick([r'left.*(clav|collar)|clavicle_l|l_?clav'], names)
    m['R_Collar']    = pick([r'right.*(clav|collar)|clavicle_r|r_?clav'], names)
    m['L_Shoulder']  = pick([r'left.*upperarm|upperarm_l|shoulder_l(?!.*end)'], names)
    m['R_Shoulder']  = pick([r'right.*upperarm|upperarm_r|shoulder_r(?!.*end)'], names)
    m['L_Elbow']     = pick([r'left.*elbow|forearm_l|lowerarm_l'], names)
    m['R_Elbow']     = pick([r'right.*elbow|forearm_r|lowerarm_r'], names)
    m['L_Wrist']     = pick([r'left.*wrist|hand_l(?!.*end)'], names)
    m['R_Wrist']     = pick([r'right.*wrist|hand_r(?!.*end)'], names)
    # Fingers (heuristic seeds; user will review)
    for side in ['L','R']:
        prefix = 'left' if side=='L' else 'right'
        for i in range(15):
            key = f"{side}_Hand_{i}"
            m[key] = pick([fr'{prefix}.*(thumb|index|middle|ring|pinky|little).*\b({i%3+1}|{i})\b',
                           fr'{side.lower()}.*(thumb|index|middle|ring|pinky|little).*{i%3+1}'], names)
    return m


def main():
    csv_path = Path("data/apose_bones.csv")
    out_path = Path("config/mapping_fbx_to_smplh.json")
    names = load_bones(csv_path)
    mapping = auto_map(names)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w') as f:
        json.dump(mapping, f, indent=2)
    print(f"✓ Seeded mapping at: {out_path}\nReview and adjust ambiguous entries.")


if __name__ == '__main__':
    main()


