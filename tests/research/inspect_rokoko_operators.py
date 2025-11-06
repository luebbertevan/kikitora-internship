"""
Inspect Rokoko Studio Live Operators

This script inspects all Rokoko operators available in Blender and documents
their signatures, parameters, and usage.

Run this in Blender Python console or via:
    blender --background --python inspect_rokoko_operators.py
"""

import bpy
import sys
from typing import List, Dict, Any


def inspect_rokoko_operators() -> Dict[str, Any]:
    """
    Inspect all Rokoko operators and collect information about them.
    
    Returns:
        Dictionary with operator information
    """
    results = {
        'operators_found': [],
        'operator_details': {},
        'addon_enabled': False,
        'errors': []
    }
    
    # Check if Rokoko add-on is enabled
    addon_name = None
    for addon in bpy.context.preferences.addons:
        if 'rokoko' in addon.module.lower():
            addon_name = addon.module
            results['addon_enabled'] = True
            results['addon_module'] = addon.module
            break
    
    if not results['addon_enabled']:
        results['errors'].append("Rokoko add-on not found or not enabled")
        return results
    
    # Find all Rokoko operators
    rokoko_ops = []
    for attr in dir(bpy.ops):
        if 'rokoko' in attr.lower():
            rokoko_ops.append(attr)
    
    results['operators_found'] = sorted(rokoko_ops)
    
    # Inspect each operator
    for op_name in rokoko_ops:
        try:
            op_module = getattr(bpy.ops, op_name)
            op_info = {
                'name': op_name,
                'bl_idname': None,
                'bl_label': None,
                'parameters': [],
                'description': None,
            }
            
            # Try to get operator class info
            if hasattr(op_module, '__module__'):
                op_info['module'] = op_module.__module__
            
            # Try to get operator properties
            try:
                # Get operator properties
                if hasattr(op_module, 'get_rna_type'):
                    rna = op_module.get_rna_type()
                    if rna:
                        op_info['bl_idname'] = rna.identifier
                        op_info['bl_label'] = getattr(rna, 'name', None)
                        op_info['description'] = getattr(rna, 'description', None)
                        
                        # Get properties
                        if hasattr(rna, 'properties'):
                            for prop in rna.properties:
                                param_info = {
                                    'name': prop.identifier,
                                    'type': str(prop.type),
                                    'default': getattr(prop, 'default', None),
                                    'description': getattr(prop, 'description', None),
                                }
                                op_info['parameters'].append(param_info)
            except Exception as e:
                op_info['inspection_error'] = str(e)
            
            # Try to get help/docstring
            try:
                help_text = help(op_module)
                op_info['help_text'] = str(help_text)[:500]  # Limit length
            except:
                pass
            
            results['operator_details'][op_name] = op_info
            
        except Exception as e:
            results['errors'].append(f"Error inspecting {op_name}: {e}")
    
    return results


def print_operator_info(results: Dict[str, Any]) -> None:
    """Print operator information in a readable format"""
    print("\n" + "="*80)
    print("ROKOKO OPERATOR INSPECTION RESULTS")
    print("="*80)
    
    if not results['addon_enabled']:
        print("\n❌ Rokoko add-on not found or not enabled")
        print("\nTo enable:")
        print("  1. Edit > Preferences > Add-ons")
        print("  2. Search for 'Rokoko'")
        print("  3. Enable the add-on")
        return
    
    print(f"\n✅ Rokoko add-on enabled: {results.get('addon_module', 'unknown')}")
    print(f"\nFound {len(results['operators_found'])} Rokoko operator(s):")
    
    for op_name in results['operators_found']:
        print(f"\n{'─'*80}")
        print(f"Operator: bpy.ops.{op_name}")
        
        if op_name in results['operator_details']:
            op_info = results['operator_details'][op_name]
            
            if op_info.get('bl_idname'):
                print(f"  ID Name: {op_info['bl_idname']}")
            if op_info.get('bl_label'):
                print(f"  Label: {op_info['bl_label']}")
            if op_info.get('description'):
                print(f"  Description: {op_info['description']}")
            
            if op_info.get('parameters'):
                print(f"  Parameters ({len(op_info['parameters'])}):")
                for param in op_info['parameters']:
                    param_str = f"    - {param['name']} ({param['type']})"
                    if param.get('default') is not None:
                        param_str += f" [default: {param['default']}]"
                    if param.get('description'):
                        param_str += f" - {param['description']}"
                    print(param_str)
            else:
                print("  Parameters: (could not extract)")
            
            if op_info.get('inspection_error'):
                print(f"  ⚠️  Inspection error: {op_info['inspection_error']}")
        else:
            print("  (Could not inspect details)")
    
    if results.get('errors'):
        print(f"\n{'─'*80}")
        print("Errors encountered:")
        for error in results['errors']:
            print(f"  ⚠️  {error}")


def get_operator_signature(op_name: str) -> str:
    """
    Try to get operator signature/call format.
    
    Args:
        op_name: Operator name (e.g., 'rokoko.retarget')
        
    Returns:
        Signature string
    """
    try:
        op_module = getattr(bpy.ops, op_name)
        
        # Try to call with invalid parameters to see error message
        # (This will show us what parameters are expected)
        try:
            op_module()  # Try with no args
        except TypeError as e:
            # Error message often contains parameter info
            return str(e)
        except Exception:
            pass
        
        # Try to get RNA type
        if hasattr(op_module, 'get_rna_type'):
            rna = op_module.get_rna_type()
            if rna and hasattr(rna, 'properties'):
                params = [p.identifier for p in rna.properties]
                return f"bpy.ops.{op_name}({', '.join(params)})"
        
        return f"bpy.ops.{op_name}(...)"
    except:
        return f"bpy.ops.{op_name}(...)" 


def main():
    """Main function"""
    print("Inspecting Rokoko operators...")
    
    results = inspect_rokoko_operators()
    print_operator_info(results)
    
    # Also try to get signatures
    print("\n" + "="*80)
    print("OPERATOR SIGNATURES (attempted)")
    print("="*80)
    
    for op_name in results['operators_found']:
        sig = get_operator_signature(op_name)
        print(f"\n{op_name}:")
        print(f"  {sig}")
    
    # Save results to file
    output_file = "rokoko_operator_inspection.txt"
    with open(output_file, 'w') as f:
        f.write("ROKOKO OPERATOR INSPECTION RESULTS\n")
        f.write("="*80 + "\n\n")
        
        if results['addon_enabled']:
            f.write(f"Add-on enabled: {results.get('addon_module', 'unknown')}\n")
            f.write(f"Operators found: {len(results['operators_found'])}\n\n")
            
            for op_name in results['operators_found']:
                f.write(f"\n{'─'*80}\n")
                f.write(f"Operator: bpy.ops.{op_name}\n")
                
                if op_name in results['operator_details']:
                    op_info = results['operator_details'][op_name]
                    for key, value in op_info.items():
                        if key != 'help_text':  # Skip long help text
                            f.write(f"  {key}: {value}\n")
        else:
            f.write("❌ Rokoko add-on not found or not enabled\n")
        
        if results.get('errors'):
            f.write("\n\nErrors:\n")
            for error in results['errors']:
                f.write(f"  - {error}\n")
    
    print(f"\n✅ Results saved to: {output_file}")


if __name__ == "__main__":
    main()

