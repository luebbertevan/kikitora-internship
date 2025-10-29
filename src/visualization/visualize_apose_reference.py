import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from pathlib import Path

# SMPL+H kinematic tree (52 joints)
SMPL_H_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6,
    7, 8, 9, 9, 9, 12, 13, 14, 16, 17,
    18, 19, 20, 22, 23, 20, 25, 26, 20, 28,
    29, 20, 31, 32, 20, 34, 35, 21, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21,
    49, 50,
], dtype=np.int32)


def load_reference(npz_path: Path):
    data = np.load(npz_path)
    J = data["J_ABSOLUTE"]  # (52, 3)
    return J


def plot_skeleton(J: np.ndarray, title: str = "A-Pose Reference"):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title(title)

    # Plot bones
    for i, p in enumerate(SMPL_H_PARENTS):
        if p == -1:
            continue
        xs = [J[p, 0], J[i, 0]]
        ys = [J[p, 1], J[i, 1]]
        zs = [J[p, 2], J[i, 2]]
        ax.plot(xs, ys, zs, "k-", linewidth=1)

    # Plot joints
    ax.scatter(J[:, 0], J[:, 1], J[:, 2], c="r", s=10)

    # Nice equal aspect
    mins = J.min(axis=0)
    maxs = J.max(axis=0)
    center = (mins + maxs) / 2.0
    span = (maxs - mins).max() * 0.55
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.tight_layout()
    plt.show()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Visualize A-Pose reference skeleton")
    parser.add_argument("npz", nargs="?", default="config/apose_reference.npz", help="Path to apose_reference.npz")
    args = parser.parse_args()

    J = load_reference(Path(args.npz))
    plot_skeleton(J, title=f"A-Pose Visualization: {args.npz}")


if __name__ == "__main__":
    main()
