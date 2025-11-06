"""
Check if Rokoko add-on is installed and enabled in Blender
"""

import bpy

print("\n" + "="*80)
print("CHECKING ROKOKO ADD-ON STATUS")
print("="*80)

# Check all installed add-ons
print("\nChecking installed add-ons...")
all_addons = []
for addon in bpy.context.preferences.addons:
    all_addons.append(addon.module)
    if 'rokoko' in addon.module.lower():
        print(f"✅ Found: {addon.module} (ENABLED)")

# Check available add-ons (not yet enabled)
print("\nChecking available (but disabled) add-ons...")
available_addons = []
for addon_name in bpy.context.preferences.addons.keys():
    if 'rokoko' in addon_name.lower():
        print(f"⚠️  Found: {addon_name} (DISABLED - enable it!)")

# Check add-ons directory for Rokoko files
import os
addon_paths = [
    os.path.expanduser("~/Library/Application Support/Blender"),
]
print("\nChecking add-on directories...")
for base_path in addon_paths:
    if os.path.exists(base_path):
        for version_dir in os.listdir(base_path):
            version_path = os.path.join(base_path, version_dir)
            if os.path.isdir(version_path):
                addons_dir = os.path.join(version_path, "scripts", "addons")
                if os.path.exists(addons_dir):
                    for item in os.listdir(addons_dir):
                        if 'rokoko' in item.lower():
                            print(f"📁 Found add-on folder: {os.path.join(addons_dir, item)}")

# Check for any operators that might be Rokoko-related
print("\n" + "="*80)
print("CHECKING FOR ROKOKO-RELATED OPERATORS")
print("="*80)

# Check for various possible names
possible_names = ['rokoko', 'retarget', 'mocap', 'motion', 'studio', 'live']
found_ops = []
for op in dir(bpy.ops):
    op_lower = op.lower()
    if any(name in op_lower for name in possible_names):
        found_ops.append(op)

if found_ops:
    print(f"\nFound {len(found_ops)} potentially related operator(s):")
    for op in sorted(found_ops):
        print(f"  - bpy.ops.{op}")
else:
    print("\n❌ No Rokoko-related operators found")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

rokoko_found = any('rokoko' in a.module.lower() for a in bpy.context.preferences.addons)
if not rokoko_found:
    print("\n❌ Rokoko add-on is NOT installed or enabled")
    print("\nTo install Rokoko:")
    print("  1. Download from: https://rokoko.com/products/studio-live")
    print("  2. In Blender: Edit > Preferences > Add-ons")
    print("  3. Click 'Install...' and select the downloaded .zip file")
    print("  4. Enable the add-on by checking the checkbox")
    print("  5. Then run the operator check again")
else:
    print("\n✅ Rokoko add-on is installed and enabled")

