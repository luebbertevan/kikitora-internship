# Troubleshooting: Rokoko Add-on Enabled But No Operators

## Problem

The add-on `rokoko-studio-live-blender-master` is enabled, but no operators are found when searching for 'rokoko'.

## Possible Causes

1. **Operators use different naming** - Might not be prefixed with 'rokoko'
2. **Add-on needs reload** - Operators might not be registered yet
3. **Different namespace** - Operators might be under a different module
4. **Version differences** - Different versions might use different operator names

## Diagnostic Commands

### 1. Check all operators starting with 'r':

```python
[op for op in sorted(dir(bpy.ops)) if op.lower().startswith('r')]
```

### 2. Search for 'retarget' specifically:

```python
[op for op in dir(bpy.ops) if 'retarget' in op.lower()]
```

### 3. Check add-on module directly:

```python
import importlib
rokoko_module = importlib.import_module('rokoko-studio-live-blender-master')
dir(rokoko_module)
```

### 4. Check bpy.types for operator classes:

```python
[typ for typ in dir(bpy.types) if 'rokoko' in typ.lower() or 'retarget' in typ.lower()]
```

### 5. Reload add-on:

```python
import bpy
bpy.ops.preferences.addon_disable(module='rokoko-studio-live-blender-master')
bpy.ops.preferences.addon_enable(module='rokoko-studio-live-blender-master')
# Then check again
[op for op in dir(bpy.ops) if 'rokoko' in op.lower()]
```

### 6. Check if operators are in a submodule:

```python
import importlib
rokoko = importlib.import_module('rokoko-studio-live-blender-master')
# Check what's in the module
[attr for attr in dir(rokoko) if not attr.startswith('_')]
```

## Next Steps

1. **Run the diagnostic script**: `tests/research/find_rokoko_operators.py`
2. **Check Rokoko documentation** for exact operator names
3. **Try reloading the add-on** in Blender preferences
4. **Check if operators might be in a menu** instead of bpy.ops

## Alternative: Check UI Menus

Rokoko operators might be accessible through menus rather than directly via bpy.ops. Check:

-   Mesh menu
-   Animation menu
-   Object menu
-   Or a custom "Rokoko" menu if the add-on creates one
