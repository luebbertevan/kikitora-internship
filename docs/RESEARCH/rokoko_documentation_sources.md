# Rokoko Studio Live Documentation Sources

## Primary Documentation Locations

### 1. Official Rokoko Website

**URL**: https://rokoko.com/products/studio-live

**What to look for:**

-   Documentation section
-   User guides
-   API reference (if available)
-   Blender add-on documentation

### 2. Rokoko Documentation Portal

**URL**: https://docs.rokoko.com/

**Key sections to check:**

-   Studio Live documentation
-   Blender integration guides
-   Retargeting/motion transfer documentation
-   API/scripting reference

### 3. GitHub Repository (if open source)

**Search for**: "rokoko studio live blender" on GitHub

**What to find:**

-   Source code repository
-   README files
-   Code examples
-   Operator definitions

### 4. Blender Add-on Documentation

**Location**: Within Blender after installation

**How to access:**

1. Install Rokoko add-on in Blender
2. Check add-on preferences panel
3. Look for "Documentation" or "Help" button
4. Check add-on folder for README files

### 5. Community Resources

-   **Rokoko Community Forum**: https://rokoko.com/community
-   **Discord/Slack channels** (if available)
-   **YouTube tutorials** (search "Rokoko Studio Live retargeting")

## Key Documentation Topics to Find

### For R1.1 Task:

1. **Operator Names**:

    - `bpy.ops.rokoko.*` operators
    - Retargeting operator name
    - Bone mapping operator

2. **Parameters**:

    - Required parameters for retargeting
    - Optional parameters
    - Bone mapping configuration

3. **SMPL-H Support**:

    - Does Rokoko support SMPL-H natively?
    - Bone name requirements
    - Custom bone mapping options

4. **Limitations**:
    - Known issues
    - Unsupported features
    - Workarounds

## How to Access Documentation

### Method 1: Install and Inspect

1. Install Rokoko add-on in Blender
2. Use Python console: `help(bpy.ops.rokoko)` to see available operators
3. Check add-on source code (usually in Blender add-ons folder)

### Method 2: Online Search

Search terms:

-   "Rokoko Studio Live Blender retargeting"
-   "Rokoko Studio Live API documentation"
-   "Rokoko Studio Live bone mapping"
-   "Rokoko Studio Live Python script"

### Method 3: Inspect Add-on Code

If add-on is installed:

-   Location: `~/Library/Application Support/Blender/*/scripts/addons/rokoko_studio_live/`
-   Check for:
    -   `__init__.py` (operator definitions)
    -   README files
    -   Documentation files

## Next Steps for R1.1

1. **Start with official docs**: https://docs.rokoko.com/
2. **Install add-on** (if not already): Check Blender add-ons preferences
3. **Inspect operators**: Use Python console in Blender to list operators
4. **Document findings**: Create `rokoko_research.md` with findings

## Operator Inspection Script

Once you have Blender with Rokoko installed, run this in Blender Python console:

```python
import bpy

# List all Rokoko operators
rokoko_ops = [op for op in dir(bpy.ops) if 'rokoko' in op.lower()]
print("Rokoko operators found:")
for op in rokoko_ops:
    print(f"  {op}")

# Get help for retargeting operator (if exists)
if hasattr(bpy.ops, 'rokoko'):
    try:
        help(bpy.ops.rokoko.retarget)  # Adjust operator name as needed
    except:
        print("Retarget operator help not available")
```
