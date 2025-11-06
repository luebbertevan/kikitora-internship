# Rokoko Operators Found!

## Key Discovery

**Rokoko operators are under `bpy.ops.rsl.*` not `bpy.ops.rokoko.*`**

Where `rsl` = Rokoko Studio Live

## Found Operators

### Main Retargeting Operator

-   **`bpy.ops.rsl.retarget_animation`**
    -   ID: `rsl.retarget_animation`
    -   Type: `RSL_OT_retarget_animation`

### Other RSL Operators

-   `bpy.ops.rsl.info_rokoko` (ID: `rsl.info_rokoko`)
-   `bpy.ops.rsl.save_custom_bones_retargeting` (ID: `rsl.save_custom_bones_retargeting`)
-   `bpy.ops.rsl.toggle_rokoko_id` (ID: `rsl.toggle_rokoko_id`)

## Commands to Inspect

### List all RSL operators:

```python
[op for op in dir(bpy.ops.rsl) if not op.startswith('_')]
```

### Get help for retarget operator:

```python
help(bpy.ops.rsl.retarget_animation)
```

### Get operator properties:

```python
op = bpy.ops.rsl.retarget_animation
rna = op.get_rna_type()
for prop in rna.properties:
    print(f"{prop.identifier}: {prop.type}")
```

### Try calling to see signature:

```python
bpy.ops.rsl.retarget_animation()  # Will fail but show parameters
```

## Next Steps for R1.1

1. **Inspect `bpy.ops.rsl.retarget_animation` parameters**
2. **Check Rokoko documentation** for this operator
3. **Document the operator signature** in `docs/RESEARCH/rokoko_research.md`
