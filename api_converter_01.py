#api_converter_01.py
#harpoonlobotomy 8/11/25

#concept: Take 'API version the code is written in ('source version') and 'API version target ('target version') and convert direct equivalents, and flag others.

# method (theoretical): 
#   * Use API dump cleaner to get references across the source and target versions (eg `get_and_clean_api_dumps_02.py`)
#   * Find instances of bpy in source code.
#   * Compare those instances to the API diff - if renamed, apply the rename. If added/remove, flag with appropriate version.
            # -- Note: Ideally, I'd like to to have a solid reference of all additions/removals, not just those in the source/target versions, so we could then say 'this was removed in 'version x.x', not only 'this was removed sometime between {source} and {target}. For later implementation, potentially.
#   * 


## !! Maybe reference this: https://github.com/nutti/fake-bpy-module/tree/main/src/fake_bpy_module
# it doesn't replace version api, but it does read/recognise blender API in context. Maybe at least some parts of it I can pull.

source = 3.1 # source API version. Could infer from version data in-script, but for now it has to be provided explicitly.
target = 4.5 # target api version.

sourcefile = r"D:\Scripts\Testing\My_Script_3_1.py" # Note: This script does not exist. Placeholder.


def get_api_instances():
    # Here is where we find the API instances. Somehow.
    #Obvious first step is we look for any key strings. 'NodeTree', 'bpy.*', 'Node.', etc. Maybe build a list of these from the first components of API dumps, the most common?
    # Really it needs to be code analysis, because we make variables and then apply more code to them, so being able to track the code is kind of important. Beyond what I think I can actually do though. For now just stick to raw code.
    #   So if you renamed 'bpy.*.' to something else, it won't find it. But it'll be able to mark the first instance at least.

    #from here, look up the instance in the 'target' version. 
    # if is not present in the target version, really need to look at the versions inbetween to find it. Maybe it was renamed in 4.1 - would not be listed as 'renamed' in 4.5, would just seem to be missing.

    # So the next step is...
    #       Make a big list of all the elements of sourcecode used
    #       Look them up in the target.
    #           - for the ones not found, look them up in the inbetweens. Maybe pick the midpoint, check there, then check either side depending.
    #           - will take a while to process but I think that's just going to be the way it is.

    # So, I have a list, a, b, c, d, of api terms missing from target.
    # I check the 4.1(midpoint) dict for a, b, c, d.
        # for each instance, if found and not marked as 'renamed', {!! mark and then once everything's been checked}, check the new midpoint between original_midpoint and target. Repeat until you find the last known version. 

    # need to look at fakebpy and/or yapf to see if they're what I need here. I'm ambitious, but recreating a python code analyser feels a little beyond me. Just slightly.
    print("Get instances from sourcecode.")