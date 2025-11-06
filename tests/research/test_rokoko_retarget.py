"""
Example: Using Rokoko retarget_animation operator in a Python script

This script demonstrates how to use bpy.ops.rsl.retarget_animation
to retarget animation from a source armature to a target armature.
"""

import bpy
import sys
from pathlib import Path


def setup_rokoko_retarget(source_armature_name: str, target_armature_name: str):
    """
    Set up Rokoko retargeting between two armatures.
    
    Args:
        source_armature_name: Name of the source armature (must have animation)
        target_armature_name: Name of the target armature
    """
    # Get armature objects
    source_armature = bpy.data.objects.get(source_armature_name)
    target_armature = bpy.data.objects.get(target_armature_name)
    
    if not source_armature:
        raise ValueError(f"Source armature '{source_armature_name}' not found!")
    if not target_armature:
        raise ValueError(f"Target armature '{target_armature_name}' not found!")
    
    # Check source has animation
    if not source_armature.animation_data or not source_armature.animation_data.action:
        raise ValueError(f"Source armature '{source_armature_name}' must have animation!")
    
    # Set scene properties
    scene = bpy.context.scene
    scene.rsl_retargeting_armature_source = source_armature
    scene.rsl_retargeting_armature_target = target_armature
    
    # Configure settings (optional)
    scene.rsl_retargeting_auto_scaling = True  # Scale source to match target height
    scene.rsl_retargeting_use_pose = 'POSE'     # Use pose mode (or 'REST')
    
    # Clear any existing bone mappings
    scene.rsl_retargeting_bone_list.clear()
    
    print(f"✓ Set source: {source_armature_name}")
    print(f"✓ Set target: {target_armature_name}")
    
    return source_armature, target_armature


def auto_build_bone_list():
    """
    Automatically detect and build bone mapping list.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        result = bpy.ops.rsl.build_bone_list()
        if result == {'FINISHED'}:
            bone_count = len(bpy.context.scene.rsl_retargeting_bone_list)
            print(f"✓ Auto-detected {bone_count} bone mappings")
            return True
        else:
            print(f"⚠️  build_bone_list returned: {result}")
            return False
    except Exception as e:
        print(f"❌ Error building bone list: {e}")
        return False


def manual_bone_mapping(source_bones: list, target_bones: list):
    """
    Manually add bone mappings.
    
    Args:
        source_bones: List of source bone names
        target_bones: List of target bone names (must match source_bones length)
    """
    if len(source_bones) != len(target_bones):
        raise ValueError("source_bones and target_bones must have same length!")
    
    scene = bpy.context.scene
    bone_list = scene.rsl_retargeting_bone_list
    
    for source_bone, target_bone in zip(source_bones, target_bones):
        bone_item = bone_list.add()
        bone_item.bone_name_source = source_bone
        bone_item.bone_name_target = target_bone
        bone_item.bone_name_key = target_bone  # Usually same as target
    
    print(f"✓ Added {len(source_bones)} manual bone mappings")


def execute_retarget():
    """
    Execute the Rokoko retargeting operation.
    
    Returns:
        True if successful, False otherwise
    """
    scene = bpy.context.scene
    
    # Check bone list is not empty
    if not scene.rsl_retargeting_bone_list:
        print("❌ Bone mapping list is empty! Run auto_build_bone_list() or manual_bone_mapping() first.")
        return False
    
    # Check source and target are set
    if not scene.rsl_retargeting_armature_source:
        print("❌ Source armature not set!")
        return False
    if not scene.rsl_retargeting_armature_target:
        print("❌ Target armature not set!")
        return False
    
    try:
        print("🔄 Executing retargeting...")
        result = bpy.ops.rsl.retarget_animation()
        
        if result == {'FINISHED'}:
            print("✅ Retargeting successful!")
            
            # The target armature now has the retargeted animation
            target = scene.rsl_retargeting_armature_target
            if target.animation_data and target.animation_data.action:
                action_name = target.animation_data.action.name
                print(f"✓ Animation action: {action_name}")
            
            return True
        else:
            print(f"⚠️  Retargeting returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error during retargeting: {e}")
        import traceback
        traceback.print_exc()
        return False


def retarget_animation(source_armature_name: str, target_armature_name: str, 
                      use_auto_detect: bool = True):
    """
    Complete retargeting workflow.
    
    Args:
        source_armature_name: Name of source armature with animation
        target_armature_name: Name of target armature
        use_auto_detect: If True, auto-detect bone mappings; if False, use manual mapping
    
    Returns:
        True if successful
    """
    # Step 1: Setup
    setup_rokoko_retarget(source_armature_name, target_armature_name)
    
    # Step 2: Build bone mapping
    if use_auto_detect:
        if not auto_build_bone_list():
            print("⚠️  Auto-detection failed, you may need manual mapping")
            return False
    else:
        # Example manual mapping - adjust to your bone names
        source_bones = ["Pelvis", "L_Hip", "R_Hip", "Spine1"]
        target_bones = ["Pelvis", "L_Hip", "R_Hip", "Spine1"]
        manual_bone_mapping(source_bones, target_bones)
    
    # Step 3: Execute retargeting
    return execute_retarget()


# Example usage
if __name__ == "__main__":
    # Example: Retarget from "SourceArmature" to "TargetArmature"
    # Replace with your actual armature names
    
    source_name = "SourceArmature"  # Change this
    target_name = "TargetArmature"  # Change this
    
    print("="*60)
    print("ROKOKO RETARGET EXAMPLE")
    print("="*60)
    
    success = retarget_animation(source_name, target_name, use_auto_detect=True)
    
    if success:
        print("\n✅ Complete!")
    else:
        print("\n❌ Failed!")
        sys.exit(1)

