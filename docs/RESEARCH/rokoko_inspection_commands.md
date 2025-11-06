# Commands to Inspect Rokoko Operators

## Quick Method: Run in Blender Python Console

1. **Open Blender**
2. **Open Python Console** (Window > Toggle System Console, or use Scripting workspace)
3. **First, check if Rokoko is installed/enabled:**

```python
# Check if Rokoko is enabled
import bpy
any('rokoko' in addon.module.lower() for addon in bpy.context.preferences.addons)
```

If this returns `False`, Rokoko is not installed or not enabled.

4. **If Rokoko is enabled, list operators:**

```python
# List all Rokoko operators
[op for op in dir(bpy.ops) if 'rokoko' in op.lower()]
```

If this returns `[]`, Rokoko operators are not available.

5. **Check for alternative operator names:**

```python
# Check for retarget-related operators
[op for op in dir(bpy.ops) if 'retarget' in op.lower() or 'mocap' in op.lower()]
```

## Method 2: Run Inspection Script

### Option A: Use Full Path

```python
# In Blender Python console, use full path
import os
script_path = os.path.expanduser('~/fractal-bootcamp/kikitora-internship/tests/research/find_rokoko_operators.py')
exec(open(script_path).read())
```

### Option B: Paste Inline Script

Copy the entire contents of `docs/RESEARCH/rokoko_diagnostic_inline.py` and paste directly into Blender Python console.

### Or via Blender Command Line:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python tests/research/inspect_rokoko_operators.py
```

## Method 3: Manual Inspection Commands

### List all Rokoko operators:

```python
import bpy
[op for op in dir(bpy.ops) if 'rokoko' in op.lower()]
```

### Get help for a specific operator:

```python
import bpy
help(bpy.ops.rokoko.retarget)  # Adjust operator name as needed
```

### Get operator properties:

```python
import bpy
op = bpy.ops.rokoko.retarget  # Adjust as needed
rna = op.get_rna_type()
if rna:
    print(f"ID: {rna.identifier}")
    print(f"Name: {rna.name}")
    for prop in rna.properties:
        print(f"  {prop.identifier}: {prop.type}")
```

### Try calling operator to see required parameters:

```python
import bpy
# This will fail but show what parameters are expected
bpy.ops.rokoko.retarget()
```

## Expected Operators

Based on typical Rokoko add-ons, you might find:

## ✅ ACTUAL OPERATORS FOUND

**Operators are under `bpy.ops.rsl.*` not `bpy.ops.rokoko.*`**

-   **`bpy.ops.rsl.retarget_animation`** - Main retargeting operator ✅
-   **`bpy.ops.rsl.build_bone_list`** - Auto-build bone mapping list
-   **`bpy.ops.rsl.add_bone_list_item`** - Add manual bone mapping
-   **`bpy.ops.rsl.clear_bone_list`** - Clear bone mappings
-   **`bpy.ops.rsl.save_custom_bones_retargeting`** - Save custom mappings
-   **`bpy.ops.rsl.info_rokoko`** - Info operator
-   **`bpy.ops.rsl.toggle_rokoko_id`** - Toggle operator

**See `rokoko_retarget_operator_usage.md` for detailed usage instructions.**
