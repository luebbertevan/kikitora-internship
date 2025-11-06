"""
Quick Rokoko Operator Inspection

Run this in Blender Python console for quick inspection:
    exec(open('inspect_rokoko_quick.py').read())
"""

import bpy

print("\n" + "="*80)
print("QUICK ROKOKO OPERATOR INSPECTION")
print("="*80)

# Check if Rokoko is enabled
rokoko_enabled = False
for addon in bpy.context.preferences.addons:
    if 'rokoko' in addon.module.lower():
        print(f"\n✅ Rokoko add-on found: {addon.module}")
        rokoko_enabled = True
        break

if not rokoko_enabled:
    print("\n❌ Rokoko add-on not found or not enabled")
    print("\nTo enable:")
    print("  1. Edit > Preferences > Add-ons")
    print("  2. Search for 'Rokoko'")
    print("  3. Enable the add-on")
    sys.exit(1)

# Find all Rokoko operators
print("\n" + "-"*80)
print("Finding Rokoko operators...")
rokoko_ops = []
for attr in dir(bpy.ops):
    if 'rokoko' in attr.lower():
        rokoko_ops.append(attr)

print(f"\nFound {len(rokoko_ops)} operator(s):")
for op in sorted(rokoko_ops):
    print(f"  - bpy.ops.{op}")

# Inspect each operator
print("\n" + "-"*80)
print("Operator Details:")
print("-"*80)

for op_name in sorted(rokoko_ops):
    print(f"\n{'='*80}")
    print(f"bpy.ops.{op_name}")
    print("="*80)
    
    try:
        op = getattr(bpy.ops, op_name)
        
        # Try to get help
        try:
            print("\nHelp:")
            help(op)
        except:
            print("(Help not available)")
        
        # Try to get RNA type
        try:
            if hasattr(op, 'get_rna_type'):
                rna = op.get_rna_type()
                if rna:
                    print(f"\nID Name: {rna.identifier}")
                    print(f"Label: {rna.name}")
                    if rna.description:
                        print(f"Description: {rna.description}")
                    
                    # Properties
                    if hasattr(rna, 'properties'):
                        props = list(rna.properties)
                        if props:
                            print(f"\nProperties ({len(props)}):")
                            for prop in props:
                                prop_str = f"  - {prop.identifier} ({prop.type})"
                                if hasattr(prop, 'default'):
                                    try:
                                        prop_str += f" [default: {prop.default}]"
                                    except:
                                        pass
                                print(prop_str)
                        else:
                            print("\n(No properties found)")
        except Exception as e:
            print(f"\n(Error getting RNA type: {e})")
        
        # Try calling with invalid args to see signature
        try:
            print("\nAttempting to get signature...")
            op()  # This will fail but show what's expected
        except TypeError as e:
            print(f"Signature hint: {e}")
        except Exception as e:
            print(f"(Could not infer signature: {e})")
            
    except Exception as e:
        print(f"Error inspecting operator: {e}")

print("\n" + "="*80)
print("Inspection complete!")
print("="*80)

