import numpy as np

model_path = r"C:\Users\Astrid\Downloads\smplh\neutral\model.npz"
model = np.load(model_path, allow_pickle=True)

print("All keys in model:")
for key in sorted(model.keys()):
    val = model[key]
    if hasattr(val, 'shape'):
        print(f"  {key}: shape {val.shape}, dtype {val.dtype}")
    else:
        print(f"  {key}: {type(val)}")

# Check if there are hand-specific parameters
print("\n" + "="*50)
print("Looking for hand-related data...")

# Check for any keys with 'hand' in the name
hand_keys = [k for k in model.keys() if 'hand' in k.lower()]
print(f"Keys with 'hand': {hand_keys}")

# The J_regressor maps vertices to joints - check if it has all 52 joints
if 'J_regressor' in model:
    J_reg = model['J_regressor']
    print(f"\nJ_regressor shape: {J_reg.shape}")
    print("This should be (52, 6890) for 52 joints")
    
    # We can compute J for all 52 joints from the template mesh
    if 'v_template' in model:
        v_template = model['v_template']
        J_full = J_reg.dot(v_template)
        print(f"\nComputed J for all joints: {J_full.shape}")
        print("\nAll 52 joint positions:")
        for i in range(len(J_full)):
            print(f"  Joint {i:2d}: [{J_full[i,0]:8.6f}, {J_full[i,1]:8.6f}, {J_full[i,2]:8.6f}]")