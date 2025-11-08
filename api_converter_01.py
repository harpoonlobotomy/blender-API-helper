#api_converter_01.py
#harpoonlobotomy 8/11/25

#concept: Take 'API version the code is written in ('source version') and 'API version target ('target version') and convert direct equivalents, and flag others.

# method (theoretical): 
#   * Use API dump cleaner to get references across the source and target versions (eg `get_and_clean_api_dumps_02.py`)
#   * Find instances of bpy in source code.
#   * Compare those instances to the API diff - if renamed, apply the rename. If added/remove, flag with appropriate version.
            # -- Note: Ideally, I'd like to to have a solid reference of all additions/removals, not just those in the source/target versions, so we could then say 'this was removed in 'version x.x', not only 'this was removed sometime between {source} and {target}. For later implementation, potentially.
#   * 


from get_and_clean_api_dumps_02 import get_files

## !! Maybe reference this: https://github.com/nutti/fake-bpy-module/tree/main/src/fake_bpy_module
# it doesn't replace version api, but it does read/recognise blender API in context. Maybe at least some parts of it I can pull.
# don't know how it actually works yet, need to look into it.

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
    #
    # like, how do I find this:
    #    group_out_node = next((n for n in nodegroup.nodes if n.type == 'GROUP_OUTPUT'), None)

# and even this:
#   nodes = mat.node_tree.nodes

#is here:
#    "Space.SpaceNodeEditor": {
#      "node_tree": [
#        "prop_rna",
#        "Node Tree",
#        "pointer",
#        null,
#        0,
#        null,
#        "Base node tree from context",
#        "...",
#        "...",
#        "..."
#      ],
# or potentially somewhere else. 
## I think this is the point where I have to lean hard on fakebpy or similar things. Or blender code itself, for interpreting these things. Text parsing is going to be useless for anything other than 'bpy.types.*', and those are rare examples.

# I think this, maybe: https://github.com/harpoonlobotomy/fake-bpy-module/blob/main/src/fake_bpy_module/transformer/bpy_context_variable_converter.py
    print("Cleaning these up is going to be messy. Had a look at fakebpy earlier but I need to spend some proper time reading.")

def get_API_docs():
    print("Make sure we have the docs for the versions. Redundant to check now but eh.")
    ## So... We check the script first, then look for instances in the API documentation. Or do we process the diffs of the api documentation, and check that diff for instances in the script.
    # Not sure which is the better option. The diffs might be the majority of the API docs, but it would mean not having to check instances against items that haven't changed...
    # Maybe comparing against diffs is best. I'm really not sure though.
    doc_files = ["list of the cleaned files from get_and_clean"]

    print("v Get the source + target docs, run a diff. Then compare that to the instances found later. v")
    return doc_files

def diff_check(source_v, target_v, instances=None):
    # for first run, no instances. Just diff the files.
    print("Even if between=True, this check will save a lot of time later by excluding things that haven't changed between versions.")
    print("Once an instance is confirmed to be unchanged, we don't need to look for it again, ever.")
    diff_dict = {}
    return diff_dict

def find_changepoint(source_v, target_v, instances, between, doc_files): # 'instances' here will be a list of instances that were found to be diffed between s_v and t_v, but without notation of change within those two.
    # note that 'source_v', 'target_v' might not be the originals, but may be the midpoint>target, etc. It's 'the specification of range, only the first one is truly source/target. But that's fine.
    if not between:
        print("Midpoint files do not exist. there should be an option here to create them. Or a setting. Otherwise you just have to run it again with Betweens on. That's silly.")
        # branches here - either make_midpoints to find the change-holding API version (ie if it changed in 3.4, we can use it even if we didn't explicitly list 3.4. It really has to be that way... It doesn't work otherwise.)
            ##... I think I need to make inbetweens just a 'do you want to premake them, or make them on the fly only'. But making them one way or another isn't optional, really. At least not in the current way things function.
        must_make_midpoints = True #placeholder to enable making required docs on the fly.

def compare_diff_against_instances(initial_diff_dict, all_instances):
    print("Make a new dict from the diff dict, where only instances in the script are included.")
    print("")

def run(source_version, target_version, result):
    versions = result[0] # all versions included, whether between or not.
    doc_files = result[1]#get_API_docs()

    initial_diff_dict = diff_check(source_version, target_version, instances=None) # just establishes the baseline of what has/hasn't changed between source and target
    all_instances = get_api_instances() # then we get the instances of api in the script
    #then we find those instances in the diff dict. Really should be using a class here with prop elements as nodes or something. 
    changed_instances = compare_diff_against_instances(initial_diff_dict, all_instances) # return the diff dict, only as it relates to the instances in the script. 
    
    #if element not in the diff, it's unchanged, we leave it. 
    # then depending on what's different about it, we fork off.
    # this is where it starts getting vague.
    # I need to check how the diff data compares to the website changelog. Does it mark all renamings in the same api log or no? And these logs are only the major releases, not every sub-version.
    # I think it'll work though.
    # So 
