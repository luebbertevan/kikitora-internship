# Single Commands to List Rokoko Operators

## Quick One-Liner (in Blender Python Console)

```python
[op for op in dir(bpy.ops) if 'rokoko' in op.lower()]
```

This will return a list of all Rokoko operator names.

## More Detailed (shows formatted list)

```python
print('\n'.join([f"bpy.ops.{op}" for op in dir(bpy.ops) if 'rokoko' in op.lower()]))
```

## Even More Detailed (with help text)

```python
for op in [o for o in dir(bpy.ops) if 'rokoko' in o.lower()]: print(f"\nbpy.ops.{op}"); help(getattr(bpy.ops, op))
```

## Check if Rokoko is Enabled First

```python
# Check if enabled
any('rokoko' in addon.module.lower() for addon in bpy.context.preferences.addons)
```

## Complete One-Liner (check + list)

```python
import bpy; enabled = any('rokoko' in a.module.lower() for a in bpy.context.preferences.addons); print(f"Rokoko enabled: {enabled}"); print([op for op in dir(bpy.ops) if 'rokoko' in op.lower()] if enabled else "Enable Rokoko first")
```

## Run from Command Line

If you want to run this from terminal (Blender must have Rokoko enabled):

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python-expr "import bpy; print([op for op in dir(bpy.ops) if 'rokoko' in op.lower()])"
```
