import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from retarget import (  # type: ignore  # pylint: disable=wrong-import-position
    compute_apose_axis_angles,
    forward_kinematics,
    J_ABSOLUTE_APOSE,
)


def main() -> None:
    axis_angles = compute_apose_axis_angles()
    print("Axis-angle rotation (L_Shoulder):", axis_angles[16])
    print("Axis-angle rotation (R_Shoulder):", axis_angles[17])

    poses = np.zeros((156,), dtype=np.float64)
    poses[:] = axis_angles.reshape(-1)

    joints = forward_kinematics(poses, J_ABSOLUTE_APOSE[0])

    diffs = np.linalg.norm(joints - J_ABSOLUTE_APOSE, axis=1)
    print("Max diff:", np.max(diffs))
    print("Avg diff:", np.mean(diffs))
    for idx in [0, 1, 2, 7, 8, 16, 17]:
        print(f"Joint {idx} diff: {diffs[idx]:.6f}")

    print("\nJoint positions (ours vs target) for L_Shoulder and L_Elbow:")
    for idx in [16, 18]:
        print(
            idx,
            "ours", joints[idx],
            "target", J_ABSOLUTE_APOSE[idx],
        )


if __name__ == "__main__":
    main()

