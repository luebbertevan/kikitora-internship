import numpy as np

# Load the NPZ file
file_path = r"C:\Users\Astrid\data\AMASS\raw\EyesJapanDataset\Eyes_Japan_Dataset\aita\accident-02-dodge fast-aita_poses.npz"
data = np.load(file_path)

print("=== NPZ File Structure ===\n")

# List all arrays in the file
print("Arrays in file:")
for key in data.files:
    print(f"  - {key}")

print("\n=== Detailed Information ===\n")

# Examine each array
for key in data.files:
    arr = data[key]
    print(f"Array: '{key}'")
    print(f"  Shape: {arr.shape}")
    print(f"  Dtype: {arr.dtype}")
    
    # Handle different data types
    if arr.dtype.kind in ['f', 'i']:  # float or integer
        print(f"  Min: {arr.min():.4f}, Max: {arr.max():.4f}")
        print(f"  First few values: {arr.flat[:10]}")
    elif arr.dtype.kind in ['U', 'S']:  # string
        print(f"  Value: {arr}")
    else:
        print(f"  Value: {arr}")
    
    # If it looks like frames (first dimension might be time)
    if len(arr.shape) >= 2:
        print(f"  Likely interpretation: {arr.shape[0]} frames x {arr.shape[1:]} data per frame")
    elif len(arr.shape) == 1 and arr.shape[0] > 1:
        print(f"  1D array with {arr.shape[0]} elements")
    elif len(arr.shape) == 0:
        print(f"  Scalar value")
    print()

print("\n=== Summary ===")
print(f"Total arrays: {len(data.files)}")
if 'poses' in data.files:
    poses_shape = data['poses'].shape
    print(f"Animation length: {poses_shape[0]} frames")
    print(f"Pose parameters per frame: {poses_shape[1]}")
    
    # SMPL model info
    if poses_shape[1] == 156:
        print("  → Full SMPL+H (body + hands): 3 global + 63 body + 90 hands")
    elif poses_shape[1] == 72:
        print("  → SMPL body only: 3 global + 69 body joints")
    elif poses_shape[1] == 135:
        print("  → SMPL body + one hand: 3 global + 63 body + 69 hand")

if 'trans' in data.files:
    print(f"Global translation: {data['trans'].shape}")

if 'mocap_framerate' in data.files:
    print(f"Framerate: {data['mocap_framerate']} fps")
    if 'poses' in data.files:
        duration = data['poses'].shape[0] / float(data['mocap_framerate'])
        print(f"Duration: {duration:.2f} seconds")

if 'betas' in data.files:
    print(f"Body shape parameters (betas): {data['betas'].shape}")

if 'gender' in data.files:
    print(f"Gender: {data['gender']}")