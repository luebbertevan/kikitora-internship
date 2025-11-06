# Betas and Bone Lengths - How They Work

## What Are Betas?

**Betas** are shape parameters in the SMPL model that control body shape variations:

-   10 or 16 values (depending on model version)
-   Control things like: height, weight, limb length, body proportions
-   Applied to the template mesh to create personalized body shapes

## What We Know

From exploring the NPZ files:

-   ✅ Each animation has `betas` (shape: 16 values)
-   ✅ Betas are **non-zero** in your test files (subject has custom proportions)
-   ✅ We know the armature structure (SMPL-H with 52 joints)
-   ✅ We know the parent-child relationships

## How to Compute Bone Lengths from Betas

### The Process

1. **Load SMPL Model**:

    - Template mesh vertices (`v_template`)
    - Shape blend shapes (`shapedirs`)
    - Joint regressor (`J_regressor`)

2. **Apply Betas to Template**:

    ```python
    # Modify mesh based on betas
    v_posed = v_template + sum(beta_i * shapedirs[:, :, i])
    ```

3. **Compute Joint Positions**:

    ```python
    # Regress joint positions from mesh
    J_ABSOLUTE = J_regressor @ v_posed
    ```

4. **Compute Bone Lengths**:
    ```python
    # For each joint, compute offset from parent
    for i in range(52):
        parent_idx = SMPL_H_PARENTS[i]
        if parent_idx == -1:
            SMPL_OFFSETS[i] = J_ABSOLUTE[i]  # Root
        else:
            SMPL_OFFSETS[i] = J_ABSOLUTE[i] - J_ABSOLUTE[parent_idx]
    ```

## Why This Works

-   **Betas define body shape** → Different betas = different bone lengths
-   **SMPL model knows** how betas affect mesh vertices
-   **Joint regressor** maps mesh vertices to joint positions
-   **Joint positions** → bone lengths (via parent-child relationships)

## The Challenge

The `amass_joints_h36m_60.pkl` file appears to be in a different format than expected. It might be:

-   A list of pre-computed joint positions (not a full SMPL model)
-   A different model format
-   Missing the required components (v_template, shapedirs, J_regressor)

## Next Steps

1. **Check if we have a full SMPL model file**:

    - Look for `.npz` files with SMPL model
    - Check if model contains: `v_template`, `shapedirs`, `J_regressor`

2. **Alternative: Use SMPL library**:

    - Libraries like `smplx` or `pySMPL` can load models and compute joints from betas
    - These handle the file format differences

3. **If model is not available**:
    - We cannot compute original bone lengths from betas alone
    - Would need to use reference skeleton (not original mocap)

## Summary

**What betas tell us:**

-   Subject has custom body proportions (betas are non-zero)
-   We could compute original bone lengths IF we had the SMPL model

**What we need:**

-   SMPL model file with: `v_template`, `shapedirs`, `J_regressor`
-   OR a library that can load SMPL models

**The key insight:**

-   Betas + SMPL model → Original `J_ABSOLUTE` → Original `SMPL_OFFSETS`
-   This is the ONLY way to get original bone lengths without a reference skeleton
