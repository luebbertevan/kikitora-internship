import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


SMPL_KEYS: List[str] = (
    [
        "Pelvis","L_Hip","R_Hip","Spine1","L_Knee","R_Knee","Spine2",
        "L_Ankle","R_Ankle","Spine3","L_Foot","R_Foot","Neck",
        "L_Collar","R_Collar","Head","L_Shoulder","R_Shoulder",
        "L_Elbow","R_Elbow","L_Wrist","R_Wrist",
    ]
    + [f"L_Hand_{i}" for i in range(15)]
    + [f"R_Hand_{i}" for i in range(15)]
)


def load_inventory(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open() as f:
        return list(csv.DictReader(f))


def side_of(key: str) -> str:
    if key.startswith("L_"): return "L"
    if key.startswith("R_"): return "R"
    return ""


def finger_index(key: str) -> Tuple[str, int]:
    # Map SMPL hand indices to finger order groups (thumb, index, middle, ring, pinky)
    # 0..14 => 5 fingers * 3 segments
    if "_Hand_" not in key: return ("", -1)
    idx = int(key.split("_Hand_")[1])
    group = ["thumb","index","middle","ring","pinky"][idx // 3]
    seg = (idx % 3) + 1
    return (group, seg)


def score_candidate(smpl_key: str, fbx_name: str) -> float:
    s = 0.0
    name = fbx_name.lower()
    # Side match
    sd = side_of(smpl_key)
    if sd == 'L' and re.search(r'\b(l|left)\b', name): s += 5
    if sd == 'R' and re.search(r'\b(r|right)\b', name): s += 5
    # Body part hints
    hints = {
        'Pelvis': [r'pelvis|hip|root'],
        'Hip': [r'thigh|hip'],
        'Knee': [r'knee|calf|shin'],
        'Ankle': [r'ankle'],
        'Foot': [r'foot(?!.*end)'],
        'Spine1': [r'spine.?0?1|lower|low'],
        'Spine2': [r'spine.?0?2|mid'],
        'Spine3': [r'spine.?0?3|upper|chest'],
        'Neck': [r'neck'],
        'Head': [r'head(?!.*end)|head$'],
        'Collar': [r'clav|collar'],
        'Shoulder': [r'upperarm|shoulder(?!.*end)'],
        'Elbow': [r'elbow|forearm|lowerarm'],
        'Wrist': [r'wrist|hand(?!.*end)'],
    }
    for k, pats in hints.items():
        if k in smpl_key:
            if any(re.search(p, name) for p in pats):
                s += 10
    # Hands: finger group/segment
    fg, seg = finger_index(smpl_key)
    if fg:
        if re.search(fg, name): s += 5
        if re.search(fr'(_|\b){seg}(\b|_)', name): s += 1
    # Penalize helpers
    if re.search(r'twist|roll|end|helper|nub|tip', name): s -= 8
    return s


def rank_candidates(smpl_key: str, names: List[str]) -> List[Tuple[str, float]]:
    scored = [(n, score_candidate(smpl_key, n)) for n in names]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:5]


def interactive_map(csv_path: Path, out_path: Path, non_interactive: bool = False):
    inv = load_inventory(csv_path)
    names = [row['bone_name'] for row in inv]
    mapping: Dict[str, str] = {}
    alternatives: Dict[str, List[str]] = {}
    for smpl in SMPL_KEYS:
        ranked = rank_candidates(smpl, names)
        alternatives[smpl] = [r[0] for r in ranked]
        choice = ranked[0][0] if ranked else ""
        if non_interactive:
            mapping[smpl] = choice
            continue
        # Prompt user
        print(f"\nSMPL-H: {smpl}")
        for i, (n, sc) in enumerate(ranked, 1):
            print(f"  {i}. {n} (score {sc:.1f})")
        raw = input(f"Select [1-{len(ranked)}] or type custom name (empty to skip): ").strip()
        if not raw:
            mapping[smpl] = choice
        elif raw.isdigit() and 1 <= int(raw) <= len(ranked):
            mapping[smpl] = ranked[int(raw)-1][0]
        else:
            mapping[smpl] = raw

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w') as f:
        json.dump(mapping, f, indent=2)
    alt_path = out_path.with_suffix('.alternatives.json')
    with alt_path.open('w') as f:
        json.dump(alternatives, f, indent=2)
    print(f"\n✓ Wrote mapping: {out_path}")
    print(f"✓ Wrote alternatives: {alt_path}")


def main():
    argv = sys.argv[1:]
    non_interactive = '--yes' in argv
    csv_path = Path('data/apose_bones.csv')
    out_path = Path('config/mapping_fbx_to_smplh.json')
    interactive_map(csv_path, out_path, non_interactive=non_interactive)


if __name__ == '__main__':
    main()


