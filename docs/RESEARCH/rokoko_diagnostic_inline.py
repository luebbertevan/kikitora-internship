"""
Paste this entire script into Blender Python console to find Rokoko operators
"""

import bpy
import os

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

# List ALL operators and search for Rokoko-related
print("\n" + "="*80)
print("SEARCHING ALL OPERATORS")
print("="*80)

all_ops = [op for op in dir(bpy.ops)]
print(f"Total operators: {len(all_ops)}")

# Check for operators with different naming patterns
keywords = ['rokoko', 'retarget', 'mocap', 'motion', 'studio', 'live', 'transfer', 'bone', 'map']
found_any = False
for keyword in keywords:
    matches = [op for op in dir(bpy.ops) if keyword in op.lower()]
    if matches:
        found_any = True
        print(f"\n✅ Operators containing '{keyword}':")
        for op in sorted(matches):
            print(f"  bpy.ops.{op}")

if not found_any:
    print("\n❌ No operators found with common keywords")

# Check operators starting with 'r'
print("\n" + "="*80)
print("OPERATORS STARTING WITH 'r'")
print("="*80)
r_ops = [op for op in sorted(all_ops) if op.lower().startswith('r')]
print(f"Found {len(r_ops)} operator(s) starting with 'r':")
for op in r_ops:
    print(f"  bpy.ops.{op}")

# Try to access the add-on module directly
print("\n" + "="*80)
print("CHECKING ADD-ON MODULE")
print("="*80)

if addon_name:
    try:
        import importlib
        addon_module = importlib.import_module(addon_name)
        print(f"\n✅ Add-on module loaded: {addon_name}")
        print(f"Module file: {getattr(addon_module, '__file__', 'unknown')}")
        
        # Check for operator classes
        print("\nAttributes in add-on module (first 30):")
        attrs = [attr for attr in dir(addon_module) if not attr.startswith('_')]
        for attr in sorted(attrs)[:30]:
            obj = getattr(addon_module, attr)
            obj_type = type(obj).__name__
            print(f"  {attr} ({obj_type})")
            
        # Check for operator registration
        if hasattr(addon_module, 'register'):
            print("\n✅ Module has register() function")
        if hasattr(addon_module, 'unregister'):
            print("✅ Module has unregister() function")
            
    except Exception as e:
        print(f"❌ Error importing add-on module: {e}")
        import traceback
        traceback.print_exc()

# Check bpy.types for operator classes
print("\n" + "="*80)
print("CHECKING bpy.types FOR OPERATOR CLASSES")
print("="*80)

rokoko_types = []
for attr in dir(bpy.types):
    if 'rokoko' in attr.lower() or 'retarget' in attr.lower():
        rokoko_types.append(attr)

if rokoko_types:
    print(f"✅ Found {len(rokoko_types)} Rokoko-related type(s):")
    for typ in sorted(rokoko_types):
        print(f"  bpy.types.{typ}")
        try:
            cls = getattr(bpy.types, typ)
            if hasattr(cls, 'bl_idname'):
                print(f"    ID: {cls.bl_idname}")
        except:
            pass
else:
    print("❌ No Rokoko-related types found in bpy.types")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)

