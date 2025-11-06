"""
Find Rokoko operators - they might use different naming
"""

import bpy

print("="*80)
print("FINDING ROKOKO OPERATORS")
print("="*80)

# Check if add-on is enabled
addon_name = None
for addon in bpy.context.preferences.addons:
    if 'rokoko' in addon.module.lower():
        addon_name = addon.module
        print(f"\n✅ Rokoko add-on found: {addon_name}")
        break

# List ALL operators (to see what's available)
print("\n" + "="*80)
print("ALL OPERATORS (first 50)")
print("="*80)
all_ops = [op for op in dir(bpy.ops)]
print(f"Total operators: {len(all_ops)}")
print("\nFirst 50 operators:")
for op in sorted(all_ops)[:50]:
    print(f"  {op}")

# Check for operators with different naming patterns
print("\n" + "="*80)
print("CHECKING FOR ROKOKO-RELATED OPERATORS")
print("="*80)

keywords = ['rokoko', 'retarget', 'mocap', 'motion', 'studio', 'live', 'transfer', 'bone', 'map']
for keyword in keywords:
    matches = [op for op in dir(bpy.ops) if keyword in op.lower()]
    if matches:
        print(f"\nOperators containing '{keyword}':")
        for op in sorted(matches):
            print(f"  bpy.ops.{op}")

# Try to access the add-on module directly
print("\n" + "="*80)
print("CHECKING ADD-ON MODULE")
print("="*80)

if addon_name:
    try:
        import importlib
        addon_module = importlib.import_module(addon_name)
        print(f"\nAdd-on module: {addon_module}")
        print(f"Module file: {getattr(addon_module, '__file__', 'unknown')}")
        
        # Check for operator classes
        print("\nAttributes in add-on module:")
        attrs = [attr for attr in dir(addon_module) if not attr.startswith('_')]
        for attr in sorted(attrs)[:20]:
            print(f"  {attr}")
            
        # Check for operator registration
        if hasattr(addon_module, 'register'):
            print("\n✅ Module has register() function")
        if hasattr(addon_module, 'unregister'):
            print("✅ Module has unregister() function")
            
    except Exception as e:
        print(f"Error importing add-on module: {e}")

# Check bpy.types for operator classes
print("\n" + "="*80)
print("CHECKING bpy.types FOR OPERATOR CLASSES")
print("="*80)

rokoko_types = []
for attr in dir(bpy.types):
    if 'rokoko' in attr.lower() or 'retarget' in attr.lower():
        rokoko_types.append(attr)

if rokoko_types:
    print(f"Found {len(rokoko_types)} Rokoko-related type(s):")
    for typ in sorted(rokoko_types):
        print(f"  bpy.types.{typ}")
        try:
            cls = getattr(bpy.types, typ)
            if hasattr(cls, 'bl_idname'):
                print(f"    ID: {cls.bl_idname}")
        except:
            pass
else:
    print("No Rokoko-related types found")

# List all operators alphabetically to manually search
print("\n" + "="*80)
print("ALL OPERATORS (alphabetical, search for 'r' section)")
print("="*80)
r_ops = [op for op in sorted(all_ops) if op.lower().startswith('r')]
print(f"Operators starting with 'r' ({len(r_ops)}):")
for op in r_ops[:30]:  # Show first 30
    print(f"  {op}")
if len(r_ops) > 30:
    print(f"  ... and {len(r_ops) - 30} more")

