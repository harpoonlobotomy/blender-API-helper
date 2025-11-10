#api_converter_01.py
#harpoonlobotomy 8/11/25

#concept: Take 'API version the code is written in ('source version') and 'API version target ('target version') and convert direct equivalents, and flag others.

# method (theoretical):
#   * Use API dump cleaner to get references across the source and target versions (eg `get_and_clean_api_dumps_02.py`)
#   * Find instances of bpy in source code.
#   * Compare those instances to the API diff - if renamed, apply the rename. If added/remove, flag with appropriate version.
            # -- Note: Ideally, I'd like to to have a solid reference of all additions/removals, not just those in the source/target versions, so we could then say 'this was removed in 'version x.x', not only 'this was removed sometime between {source} and {target}. For later implementation, potentially.
#   *


from genericpath import isfile
import api_context
from get_clean_api_dumps import get_files, get_versions
import json
import os
from api_context import api

## !! Maybe reference this: https://github.com/nutti/fake-bpy-module/tree/main/src/fake_bpy_module
# it doesn't replace version api, but it does read/recognise blender API in context. Maybe at least some parts of it I can pull.
# don't know how it actually works yet, need to look into it.

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

def compare_json(file1_path, file2_path):
    # Load JSON files
    #from deepdiff import DeepDiff
    try:
        with open(file1_path, "r") as f1, open(file2_path, "r") as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
    except Exception as e:
        print("There was a problem opening the file(s):", e)


    def build_nodedicts(file, filepath):

        def get_version_label(file):

            filename = os.path.basename(file)
            filename = filename.rsplit(".", 1)[0]
            version_label = filename.split("_")[0]
            return version_label

        version = get_version_label((filepath))
        nodedict = {}
        print(f"Building keys for API version {version}")
        for k in file.keys():
            for innerk, innerv in file[k].items():
                nodedict[innerk] = innerv
        #file_dict = build_nodes(version, file) # just moved it in here for now, the separate function wasn't worth using as-is.
        return nodedict, version

    dict1, version1 = build_nodedicts(json1, file1_path)
    dict2, version2 = build_nodedicts(json2, file2_path)

    from deepdiff import DeepDiff

    diff = DeepDiff(dict1, dict2, ignore_order=True)

    if diff:
        print("Differences found:") # it reports one diff. Cannot be  the case, at all.
    else:
        print("No differences found.")

#  diff keys:
#       dictionary_item_added
#       dictionary_item_removed
#       values_changed
#       iterable_item_added
#       iterable_item_removed

    change_dict ={}
    for k, v in diff.items():
        change_dict[k] = {}
        #print(f"Key is different across API versions: {k}") ### first key: dictionary_item_added = new when comparing 1, 2
        #print(type(v)) # v is type <class 'deepdiff.helper.SetOrdered'>
        #for item in v:
        #    print(item) # okay downside of this method: It doesn't give the header name. Header name has to be inferred from item text.
            # eg these:
                # root['Context']['asset']
                # root['Context']['region_popup']
                # root['Context']['path_resolve']
                #   are three independent changes, only grouped by being near each other. So the HTML parser wins over that.
        #for keys in diff[v].keys():
        #    print(keys)
    print("Currently we don't do anything with the results here. But we need to. We just have a dict.")
    return change_dict

def update_instances(change_type, changed_dict, instances):
    return changed_dict

def get_dicts_for_diff(comp_dict, source_version, source_filepath, target_version, target_filepath):


    def check_for_local(version): # this should just be a premade dict of version:localfile in api_context instead.
        api_context.simple_filecheck(version)

        api_context.check_is_file(filepath, version)



def diff_check(source, target, comp_dict, instances=None):
    # Should I be getting the filepath here, or setting it earlier? I guess here works, just keep it version numbers outside. Works okay I think.


    print(f"Start of diff check. Source: {source}, target: {target} ")
    if type(source) not in (str, os.PathLike):
        print("inside not isfile.")
        print(f"Source_v: {source}, type: {type(source)}")
        source_version, source = get_files(source, clean=True)
    if  type(target) not in (str, os.PathLike):
        print("inside not isfile.")
        target_version, target = get_files(target, clean=True)


    # for first run, no instances. Just diff the files.
    print(f"source: {source}")
    print(f"source type: {type(source)}")
    if instances!=None:
        # HERE goes the logic for checking the diff keys against instances.
        print("Even if between=True, this check will save a lot of time later by excluding things that haven't changed between versions.")
    #print("Once an instance is confirmed to be unchanged, we don't need to look for it again, ever.")
    print("About to compare_json.")

    get_dicts_for_diff(comp_dict, source_version, source[0], target_version, target[0])

    changed_dict = compare_json(source[0], target[0])
    #for item in instances: ## assuming 'item' is already the basename version of the attribute, a la decompose_data_path(data_path) in bl_rna_utils/data_path.py.
    #    if changed_dict[item]:
    #        #well this won't find anything, because the key is the state of the change (added, removed etc), not the item key. Invert this.
    #        break
    for change_type in changed_dict:
        changed_dict = update_instances(change_type, changed_dict, instances) #what form is 'instances' here? Need to  figure that out before I can do much more.

    return changed_dict

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

def get_source_and_target(versions):

    source, *_, target = versions # should maybe rename so it's clearer for the times this is used for not-actually-source and/or not-actually-target. Also source/target might be flipped if we're going from more current to older api.
    return source, target

def get_midpoint(versions):

    print(f"versions in get_midpoint: {versions}, len: {len(versions)}")
    if len(versions) == 2:
        [source_version, target_version] = versions
        print(f"source version, target version from versions: {source_version}, {target_version}, versions: {versions}")
        versions = api_context.get_between_vers(source_version, target_version)
    # The following only works if 'versions' is all inclusive.
    print(f"versions in after get_versions get_midpoint: {versions}, len: {len(versions)}")
    total_len = len(versions) # doesn't work, eg what if it's 4? With this, it'll end up making it say the answer is 1, because it makes it three, then halves it and removes one.
    print(f"total len: {total_len}")
    midpoint_val = int(total_len*.5) # -1 is always right here, no? It won't always be even numbers but even with odds is it still right? Think so. It just defaults to the lower of the middle when odd.
    print(f"Midpoint value: {midpoint_val}")
    midpoint_var = versions[midpoint_val]
    print(f"Midpoint var: {midpoint_var}")
    return midpoint_var

def run(result):
    comp_dict = {} # dict of all dicts. Currently full, should be a simpler version but will do this for testing temporarily.
    versions = result[0] # all versions included, whether between or not.
    doc_files = result[1]#get_API_docs()
    source, target = get_source_and_target(versions)
    print(f"versions at start of run: {versions}")
    s_t = [float(source), float(target)]
    #try:
    #    result = get_files(api.dir, s_t)
    #except Exception as e:
    #    print(f"Failed to get results: {e}")
    print(f"source, target: {source}, {target}")
    print(doc_files[0])
    #exit()
    initial_diff_dict = diff_check(source, target, comp_dict, instances=None) # just establishes the baseline of what has/hasn't changed between source and target
    all_instances = get_api_instances() # then we get the instances of api in the script
    #then we find those instances in the diff dict. Really should be using a class here with prop elements as nodes or something.
    changed_instances = compare_diff_against_instances(initial_diff_dict, all_instances) # return the diff dict, only as it relates to the instances in the script.
    # ^ Need to use this somehow to limit the size of all future pre-diff dicts. If k not in instances, ignore it immediately. And only diff with the things we're looking for. Maybe? Think yes. ?

    print(f"versions before midpoint: {versions}. /n s_t: {s_t}")
    # the next three should be a function. The repeated 'diff, get midpoint
    midpoint_var = get_midpoint(s_t) # not actually needed here, just wanted to write it while I thought of it.
    mid_version_no, mid_cleaned = get_files(float(midpoint_var), clean=True)
    # Now. Am I comparing the source to midpoint? Yes, right? Because I need to follow it from there, incase it was renamed etc.
    # But I also need to compare it to the target. Hmmmmm.

    # source > midpoint check
    diff_dict = diff_check(source, midpoint_var, comp_dict, instances=all_instances) # keeping in mind source and target (or midpoint var, as here) are always floats.
    # once we hae the midpoint, compare source and midpoint. Need a dict or class or something to record 'this instance changed in v x.xx'.


    #if element not in the diff, it's unchanged, we leave it.
    # then depending on what's different about it, we fork off.
    # this is where it starts getting vague.
    # I need to check how the diff data compares to the website changelog. Does it mark all renamings in the same api log or no? And these logs are only the major releases, not every sub-version.
    # I think it'll work though.
    # So


#  bpy-ops-text-run-script
# https://github.com/blender/blender/blob/main/source/blender/python/intern/bpy_interface_run.cc#L127 <-- blender running a script
#       static bool python_script_exec(
#           bContext *C, const char *filepath, Text *text, ReportList *reports, const bool do_jump)
#       or
#       bool BPY_run_filepath(bContext *C, const char *filepath, ReportList *reports)
#       {
#         return python_script_exec(C, filepath, nullptr, reports, false);
#       }


#https://github.com/blender/blender/blob/main/source/blender/python/BPY_extern_run.hh#L60
