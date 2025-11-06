"""
Inspect RSL (Rokoko Studio Live) operators

The operators are under bpy.ops.rsl.* not bpy.ops.rokoko.*
"""

import bpy

print("="*80)
print("INSPECTING RSL OPERATORS")
print("="*80)

# List all RSL operators
print("\nAll RSL operators:")
rsl_ops = [op for op in dir(bpy.ops.rsl) if not op.startswith('_')]
for op in sorted(rsl_ops):
    print(f"  bpy.ops.rsl.{op}")

# Inspect the retarget operator specifically
print("\n" + "="*80)
print("INSPECTING bpy.ops.rsl.retarget_animation")
print("="*80)

try:
    retarget_op = bpy.ops.rsl.retarget_animation
    
    # Get help
    print("\nHelp:")
    help(retarget_op)
    
    # Get RNA type
    if hasattr(retarget_op, 'get_rna_type'):
        rna = retarget_op.get_rna_type()
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
                        try:
                            if hasattr(prop, 'default'):
                                prop_str += f" [default: {prop.default}]"
                        except:
                            pass
                        if prop.description:
                            prop_str += f" - {prop.description}"
                        print(prop_str)
                else:
                    print("\n(No properties found)")
    
    # Try calling with invalid args to see signature
    print("\n" + "-"*80)
    print("Attempting to infer signature...")
    try:
        retarget_op()  # This will fail but show what's expected
    except TypeError as e:
        print(f"Signature hint: {e}")
    except Exception as e:
        print(f"Error: {e}")
        
except AttributeError:
    print("❌ bpy.ops.rsl.retarget_animation not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Inspect other RSL operators
print("\n" + "="*80)
print("OTHER RSL OPERATORS")
print("="*80)

for op_name in rsl_ops:
    if op_name != 'retarget_animation':
        try:
            op = getattr(bpy.ops.rsl, op_name)
            print(f"\nbpy.ops.rsl.{op_name}:")
            if hasattr(op, 'get_rna_type'):
                rna = op.get_rna_type()
                if rna:
                    print(f"  ID: {rna.identifier}")
                    print(f"  Label: {rna.name}")
        except:
            pass

print("\n" + "="*80)
print("INSPECTION COMPLETE")
print("="*80)
print("\nKey finding: Operators are under bpy.ops.rsl.* not bpy.ops.rokoko.*")
print("Retarget operator: bpy.ops.rsl.retarget_animation")

