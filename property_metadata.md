# RNA data construction:
# (I'm sure there's a resource for this explicitly but I couldn't find it in a quick search.)

[for reference]

#sample from .\api_dumps\cleaned_api_dumps\5.1_cleaned.json

{
  "bpy.types": {
    "AOV": {
      "is_valid": [ ## potentially 'bpy.props.PointerProperty'? Right number of signature elements...
        "prop_rna",
        "Valid",
        "boolean",
        null,
        0,
        false,
        "Is the name of the AOV conflicting",
        "...",
        "...",
        "..."
      ],
      "name": [
        "prop_rna",   ### contents here are https://docs.blender.org/api/current/bpy.types.PropertyGroup.html#bpy.types.PropertyGroup
        "Name",       ### these are 'bl_rna_get_subclass', 'name' and 'bl_rna_get_subclass_py' in that order.
        "string",     ## or maybe not. Possibly wrong. 
        null,
        0,
        "",
        "Name of the AOV",
        "...",
        "...",
        "..."
      ],
      "type": [
        "prop_rna",
        "Type",
        "enum",
        null,
        0,
        "COLOR", # blender datatype
        "Data type of the AOV", # description
        "...",
        "...",
        "..."
      ]
}}}

#AOV → StructRNA

# "is_valid" → property RNA entry of the AOV struct

# property metadata slots:

# Slot	prop_rna	                              func_rna / func_py
# 0	type tag ("prop_rna")	                      "func_rna" / "func_py"
# 1	property name	function name or              placeholder
# 2	data type ("boolean", "collection", etc.)	  placeholder / return type
# 3	default value	                              placeholder
# 4	flags	                                      placeholder
# 5	internal bool / metadata	                  placeholder
# 6	description / doc	                          docstring or description
# 7	argument names (empty for prop)	            list of argument names
# 8	argument types / placeholders	              argument types
# 9	return info / placeholders	                return type(s)