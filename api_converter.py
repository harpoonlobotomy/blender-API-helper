#api_converter_01.py
#harpoonlobotomy 8/11/25

#concept: Take 'API version the code is written in ('source version') and 'API version target ('target version') and convert direct equivalents, and flag others.

# method (theoretical):
#   * Use API dump cleaner to get references across the source and target versions (eg `get_and_clean_api_dumps_02.py`)
#   * Find instances of bpy in source code.
#   * Compare those instances to the API diff - if renamed, apply the rename. If added/remove, flag with appropriate version.
            # -- Note: Ideally, I'd like to to have a solid reference of all additions/removals, not just those in the source/target versions, so we could then say 'this was removed in 'version x.x', not only 'this was removed sometime between {source} and {target}. For later implementation, potentially.
#   *

import api_context
import json
import os
from api_context import api, get_filepath, simple_filecheck

## !! Maybe reference this: https://github.com/nutti/fake-bpy-module/tree/main/src/fake_bpy_module
# it doesn't replace version api, but it does read/recognise blender API in context. Maybe at least some parts of it I can pull.
# don't know how it actually works yet, need to look into it.

def get_api_instances(input_file):
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

        version = get_version_label(filepath)
        print(f"version label: {version}")
        nodedict = {}
        print(f"Building keys for API version {version}")
        if type(file) is list:
            file=file[0]

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
        print(f"{len(diff)}")
    else:
        print("No differences found.")


#  diff keys:
#       dictionary_item_added
#       dictionary_item_removed
#       values_changed
#       iterable_item_added
#       iterable_item_removed
    import re
    change_dict ={}
    short_dict={}
    for k, v in diff.items(): ######## Now, key to note: 'dictionary_item_added' here just means it wasn't in source dict, not that it was added to the API in this version update.
        temp_list=[]                ### that's obvious, but I'm putting it here for when it's 3am and I forget this simple factor.
        short_temp_list=set()
        short_dict[k]=short_temp_list
        change_dict[k] = temp_list
        for content in diff[k]:
            temp_list.append(content) # let's see if there's anything listed...
            #print(f"item, content(v, using key): {k}, {content}")
            # bad attempt at regexing for "root['XrEventData']...  (?:root\[\')([a-zA-Z]+)
            m = re.search("(?:root\\[\')([a-zA-Z]+)", content)
            label=m.group(1)
            #print(f"label: {label}")
            short_temp_list.add(label)

            #print(f"v: {v}")
        #print(f"temp_list: {temp_list}")
        #print(f"TEST: temp_list contents should be here:  `{change_dict[k]}`")
        print(f"Short dict for {k}: {short_dict[k]}") ## short_dict == just the header, no sub-information.

    print("Currently we don't do anything with the results here. But we need to. We just have a dict.")
    return short_dict

def update_instances(change_type, changed_dict, instances):
    return changed_dict

def diff_check(source_version, target_version, comp_dict, instances=None):
    # Should I be getting the filepath here, or setting it earlier? I guess here works, just keep it version numbers outside. Works okay I think.
    print(f"Start of diff check. Source: {source_version}, target: {target_version} ")

    source_file=get_filepath(source_version)
    target_file=get_filepath(target_version)

    # for first run, no instances. Just diff the files.
    if instances!=None:
        # HERE goes the logic for checking the diff keys against instances.
        print("Even if between=True, this check will save a lot of time later by excluding things that haven't changed between versions.")
        #print("Once an instance is confirmed to be unchanged, we don't need to look for it again, ever.")

    print("About to compare_json.")
    #get_dicts_for_diff(comp_dict, source_version, source_file, target_version, target_file) # taken over by get_filepath and its dict check already.
    print(f"source file: {source_file}, type: {type(source_file)}. Target file: {target_file}, type: {type(target_file)}")
    changed_dict = compare_json(source_file, target_file) # currently returning short_dict
    #for item in instances: ## assuming 'item' is already the basename version of the attribute, a la decompose_data_path(data_path) in bl_rna_utils/data_path.py.
    #    if changed_dict[item]:
    #        #well this won't find anything, because the key is the state of the change (added, removed etc), not the item key. Invert this.
    #        break
    #compare comp_dict to changed_dict. that's where we update the final 'this was added in x'. It's a dict for now, maybe a class made in this script later. Idk. Probably really just avoiding the actual script parsing for the moment.

    for change_type, contents in changed_dict.items():
        changed_dict = update_instances(change_type, changed_dict, instances) #what form is 'instances' here? Need to  figure that out before I can do much more.
#        if not comp_dict.get(change_type):
#            comp_dict[change_type]=contents
#        else:
#            comp_dict[change_type].update(contents) ## will overwrite. Not a viable solution at all.

    return changed_dict

#def find_changepoint(source_v, target_v, instances, doc_files): # 'instances' here will be a list of instances that were found to be diffed between s_v and t_v, but without notation of change within those two.
#    # note that 'source_v', 'target_v' might not be the originals, but may be the midpoint>target, etc. It's 'the specification of range, only the first one is truly source/target. But that's fine.


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
        
    print(f"versions in after get_versions get_midpoint: {versions}, len: {len(versions)}")
    midpoint_var = versions[int(len(versions)*.5)]
    print(f"Midpoint var: {midpoint_var}")
    return midpoint_var

def run(result):
    # how about we build the source dict, get all the base keys (the keys used for short_dict) and use those as the reference to check from? Wouldn't be perfect but a starting point. Need a starting point...
    # though I guess that's literally what the rst files are for. Okay yeah, ignore this. Getting too tired.
    comp_dict = {} # dict of all dicts. Currently full, should be a simpler version but will do this for testing temporarily.
    versions = result[0] # all versions included, whether between or not.
    doc_files = result[1]#get_API_docs()
    source, target = get_source_and_target(versions)
    print(f"versions at start of run: {versions}")
    source_target_list = [float(source), float(target)]

    print(f"source, target: {source}, {target}")
    print(doc_files[0])

    initial_diff_dict = diff_check(source, target, comp_dict, instances=None) # just establishes the baseline of what has/hasn't changed between source and target
    exit() # after this does nothing useful, so stopping here.
    all_instances = get_api_instances(api.input_file) # then we get the instances of api in the script
    #then we find those instances in the diff dict. Really should be using a class here with prop elements as nodes or something.
    changed_instances = compare_diff_against_instances(initial_diff_dict, all_instances) # return the diff dict, only as it relates to the instances in the script.
    # ^ Need to use this somehow to limit the size of all future pre-diff dicts. If k not in instances, ignore it immediately. And only diff with the things we're looking for. Maybe? Think yes. ?

    print(f"versions before midpoint: {versions}. \n s_t: {source_target_list}")
    # the next three should be a function. The repeated 'diff, get midpoint
    midpoint_var = get_midpoint(source_target_list) # not actually needed here, just wanted to write it while I thought of it.
    # Now. Am I comparing the source to midpoint? Yes, right? Because I need to follow it from there, incase it was renamed etc.
    # But I also need to compare it to the target. Hmmmmm.
    # once we hae the midpoint, compare source and midpoint. Need a dict or class or something to record 'this instance changed in v x.xx'.

    # source > midpoint check
    diff_dict = diff_check(source, midpoint_var, comp_dict, instances=changed_instances) # keeping in mind source and target (or midpoint var, as here) are always floats.
    # and need a ready record of 'did not change in first half' to check at the later midpoint, and 'changed before first half' to check the early midpoint. Separate from the main dict, a malleable temporary space for 'these ones we're actively looking for now'.
    # if still in changed_instances and not in diff_dict, check midpoint between midpoint_var and target - means it changes eventually but hasn't changed yet.
    # if removed, check midpoint between midpoint_var and source.
    #but realy should be using the rst-like output for this. It specified 'removed' per version. I need to do some proper analysis and see what's best, really. Hard to intuit at this shallow level.
    # it does work though, for the basic diffs. Can compare x and y api versions and be told what's new, changed, removed. But not when it was, or what to, at the current manner of doing things.
    # this is all with the api dump jsons. Need to test with the rst-like.

