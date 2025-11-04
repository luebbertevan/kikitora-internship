# Rodrigues' Formula & Rotation Representations Explained

## 🔄 The Rotation Conversion Chain

```
Axis-Angle (NPZ) → Rotation Matrix (FK) → Quaternion (GLB)
     ↓                    ↓                      ↓
  3 values           9 values (3×3)           4 values
  Compact            Easy to multiply        Blender's format
```

## 📐 What is Rodrigues' Formula?

**Rodrigues' rotation formula** converts an axis-angle representation to a rotation matrix.

### The Formula:

Given:

-   **Axis**: Unit vector `v = [vx, vy, vz]` (direction to rotate around)
-   **Angle**: `θ` (how much to rotate, in radians)

The rotation matrix `R` is:

```
R = I + sin(θ) × K + (1 - cos(θ)) × K²
```

Where:

-   `I` = 3×3 identity matrix
-   `K` = skew-symmetric matrix (cross-product matrix):
    ```
    K = [  0  -vz   vy ]
        [ vz    0  -vx ]
        [ -vy  vx    0 ]
    ```

### Why This Formula?

-   **Direct conversion**: No intermediate steps
-   **Efficient**: Works directly with axis-angle
-   **Numerically stable**: Handles edge cases well

### Code Implementation:

```python
def axis_angle_to_rotation_matrix(axis_angle: NDArray[np.float64]) -> NDArray[np.float64]:
    angle: float = np.linalg.norm(axis_angle)  # Get angle from magnitude
    if angle < 1e-6:
        return np.eye(3)  # No rotation

    axis: NDArray[np.float64] = axis_angle / angle  # Normalize to get axis

    # Create skew-symmetric matrix K
    K: NDArray[np.float64] = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    # Rodrigues' formula
    R: NDArray[np.float64] = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R
```

---

## 🎯 Why Use Rotation Matrix (Not Quaternion) in Forward Kinematics?

### The Answer: **Matrix Multiplication for Transform Chaining**

In forward kinematics, we need to **chain transforms** through the parent hierarchy:

```
Pelvis → L_Hip → L_Knee → L_Ankle
```

Each bone's global transform = parent's global transform × local transform

**With Matrices:**

```python
global_transform[child] = global_transform[parent] @ local_transform[child]
```

This is **easy** - just matrix multiplication!

**With Quaternions:**

-   Would need to convert quaternion → matrix for each multiplication
-   Or use quaternion multiplication (more complex)
-   Then still need matrix for final position calculation

### Why Matrices Are Better for FK:

1. **Direct Position Calculation**:

    - `position = transform_matrix[:3, 3]` (extract translation)
    - Can't do this with quaternions alone

2. **Combined Transform**:

    - Matrix can store BOTH rotation AND translation in one 4×4 matrix
    - Quaternion only represents rotation (need separate translation)

3. **Hierarchical Chaining**:

    - `parent_matrix @ child_matrix` is straightforward
    - Quaternion multiplication is more complex

4. **Standard Practice**:
    - FK algorithms typically use matrices (industry standard)
    - More intuitive for 3D transformations

### The 4×4 Transform Matrix:

```python
local_transform = [
    [Rxx, Rxy, Rxz, Tx],  # Rotation (3×3) + Translation (X)
    [Ryx, Ryy, Ryz, Ty],  # Rotation (3×3) + Translation (Y)
    [Rzx, Rzy, Rzz, Tz],  # Rotation (3×3) + Translation (Z)
    [  0,   0,   0,  1]   # Homogeneous coordinate
]
```

This combines:

-   **Rotation** (from axis-angle via Rodrigues' formula)
-   **Translation** (from SMPL_OFFSETS)

All in one matrix!

---

## 🎭 But Wait... Don't We Want Quaternions?

**Yes! But at different stages:**

### In Forward Kinematics (FK):

**Use Rotation Matrices** - for efficient computation and chaining

### In Final GLB Output:

**Use Quaternions** - Blender's preferred format for keyframes

### The Conversion Happens During Baking:

```python
# During FK (using matrices):
joint_positions = forward_kinematics(poses, trans)  # Uses rotation matrices

# During baking (constraints → keyframes):
pose_bone.keyframe_insert(data_path="rotation_quaternion")  # Blender converts to quaternion
```

**Blender automatically converts** rotation matrices → quaternions when you keyframe bones!

### Why Quaternions in GLB?

1. **Blender's Native Format**: Bones store rotations as quaternions
2. **Compact**: 4 values vs 9 for matrix (storage efficiency)
3. **No Gimbal Lock**: Quaternions avoid rotation singularities
4. **Smooth Interpolation**: Better for animation blending

---

## 🔄 Complete Flow: Axis-Angle → Matrix → Quaternion

### Step-by-Step:

1. **Input (NPZ)**: Axis-angle `[0.1, 0.2, 0.3]`

    - 3 values, compact representation

2. **FK Computation**: Convert to rotation matrix

    ```python
    rot_matrix = axis_angle_to_rotation_matrix([0.1, 0.2, 0.3])
    # Result: 3×3 rotation matrix
    ```

3. **Build Transform Matrix**:

    ```python
    local_transform = [
        [rot_matrix, offset_translation],
        [0, 0, 0, 1]
    ]
    # 4×4 matrix combining rotation + translation
    ```

4. **Chain Through Parents**:

    ```python
    global_transform = parent_global @ local_transform
    # Matrix multiplication through hierarchy
    ```

5. **Extract Position**:

    ```python
    joint_position = global_transform[:3, 3]
    # Get translation component
    ```

6. **Place Empty**: Empty object at joint position

    ```python
    empty.location = Vector(joint_position)
    ```

7. **Add Constraint**: Bone follows empty

    ```python
    constraint = bone.constraints.new('STRETCH_TO')
    constraint.target = empty
    ```

8. **Bake**: Blender converts to quaternions

    ```python
    bpy.ops.nla.bake(...)  # Blender internally converts rotation → quaternion
    ```

9. **Output (GLB)**: Quaternions stored in keyframes
    - Each bone has quaternion rotation per frame
    - Compact, efficient, no gimbal lock

---

## 📊 Comparison: Why Each Format?

| Format              | Use Case       | Why                                                    |
| ------------------- | -------------- | ------------------------------------------------------ |
| **Axis-Angle**      | NPZ input      | Compact (3 values), common in animation data           |
| **Rotation Matrix** | FK computation | Easy to multiply, combines rotation + translation      |
| **Quaternion**      | GLB output     | Blender's format, smooth interpolation, no gimbal lock |

---

## 🎓 Key Takeaways

1. **Rodrigues' Formula**: Converts axis-angle → rotation matrix

    - Needed for FK computation
    - Standard mathematical formula

2. **Why Matrices in FK**:

    - Easy matrix multiplication for hierarchical chaining
    - Can combine rotation + translation in one 4×4 matrix
    - Direct position extraction

3. **Why Quaternions in GLB**:

    - Blender's native format
    - Better for animation (smooth interpolation)
    - Compact storage

4. **The Conversion Chain**:

    ```
    Axis-Angle (NPZ)
      → Rotation Matrix (FK)
        → Quaternion (Blender/Bake)
          → GLB Keyframes
    ```

5. **You Don't Need to Convert Manually**:
    - FK uses matrices (Rodrigues' formula)
    - Blender automatically converts to quaternions during baking
    - Final GLB has quaternions

---

## 💡 Why Not Skip Matrices and Use Quaternions Directly?

**You could, but it's more complex:**

### If Using Quaternions in FK:

```python
# Would need to:
1. Convert axis-angle → quaternion (more complex formula)
2. Multiply quaternions for hierarchy (quaternion multiplication)
3. Extract position (still need matrix for translation)
4. Convert quaternion → matrix for position calculation anyway
```

### With Matrices:

```python
# Simpler:
1. Convert axis-angle → matrix (Rodrigues' formula)
2. Multiply matrices (standard matrix multiplication)
3. Extract position directly (from matrix)
4. Let Blender convert to quaternion (automatic)
```

**Result**: Matrices are simpler for FK, quaternions are better for storage. Use each where it's best!

---

## 🔍 Visual Example

### Axis-Angle Input:

```
[0.5, 0.0, 0.0]  = Rotate 0.5 radians around X-axis
```

### After Rodrigues' Formula (Rotation Matrix):

```
[1.000  0.000  0.000]  ← X-axis stays same
[0.000  0.878 -0.479]  ← Y-axis rotated
[0.000  0.479  0.878]  ← Z-axis rotated
```

### After FK (4×4 Transform Matrix):

```
[1.000  0.000  0.000  0.1]  ← Rotation + X translation
[0.000  0.878 -0.479  0.0]  ← Rotation + Y translation
[0.000  0.479  0.878  0.95] ← Rotation + Z translation
[0.000  0.000  0.000  1.0]  ← Homogeneous coordinate
```

### After Baking (Blender converts to Quaternion):

```
rotation_quaternion = (0.969, 0.247, 0.000, 0.000)
                      (w,     x,     y,     z)
```

**All three represent the same rotation!** Just different formats for different purposes.
