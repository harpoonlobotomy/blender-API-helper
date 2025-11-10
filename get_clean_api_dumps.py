#get API json dump links
# This is mostly comments right now, still figuring things out.Does work to diff between versions, but not in a usable way.
# 7/11/25
# https://docs.blender.org/api/

"""
Useful elsewhere perhaps:
all_versions = list(all the versions in the api dump index)
files = set(raw files downloaded) - filenames only, not actual file data.
cleaned = list(cleaned json files for parsing) - filenames only, not actual file data.
"""


from pathlib import Path
import json
import os
import requests

#specify_versions = ["3.1", "4.5"] # for only getting specific versions of the API instead of all
subdir = "\\api_dumps_2"
versionlist = set()

def check_for_files(root, versions):
    complete=False
    found=None
    #print(f"directory in check_for_files: {root}")
    if not os.path.exists(root):
        os.makedirs(root)
        return None, complete
    
    found_all = [str(f) for f in Path(root).iterdir() if f.is_file()] # made this str so they're not winpath obj. Might be a mistake but it keeps the list usable if pre-existing, otherwise they're all windpath objects. idk if it's better to keep them that, but this way it's consistent - whether found or created, 'cleaned' is a list of str filepaths.
    if found_all:

        found=[]
        found_versions = []
        for f in found_all:
            f2 = str(f).replace("_cleaned", "")
            basename = float(os.path.basename(f2).rsplit(".",1)[0]) # god this is all messy as hell but it does find both clean and raw files.
            if basename in versions:
                found_versions.append(basename)
                found.append(f)

        if len(found_versions)==len(versions):
            print("All files requested in versions are Found.")
            complete=True
        else:
            print("Not all versions found.")
# No, it won't.    found = [f for f in Path(root).iterdir() if f.is_file and f in versions()] # will this work? If it's a file and if it's in versions. 
    #for item in found:
        # if one of versions not in item?? `if any(versions) not in item`?
    #    print(item) # really want to potentially output the vers name here directly for use outside the func. Will think about it.
        #well ignore this for now, because none of them exist for me to test against. But later: 'if the file is not a version referenced in versions, don't include it' is the intent.
    return found, complete

def cleaned_dumps(api_dir, version, contents):

    #root = os.path.dirname(os.path.abspath(__file__)) + subdir + "\\cleaned_api_dumps\\"
    root=api_dir + "cleaned_api_dumps\\"
    filepath =  root + version + "_cleaned.json"

    if not os.path.exists(root):
        os.makedirs(root)
        
    with open(filepath, "w+", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)

    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} created.")
    else:
        print(f"File creation failed for {version}; file does not exist.")

    return filepath

def clean_files(api_dir, files):
    cleaned_filelist = []
    for filename in files:
        with open(filename) as f:
            d = json.load(f) ## d == list, 0==versionname as list "[2, 92]", 1 = contents as dict.
            version = '.'.join(map(str,d[0]))
            file_contents = d[1]
            cleaned_filelist.append(cleaned_dumps(api_dir, version, file_contents))

    return cleaned_filelist

## Get initial files from the API dump index
def get_json_links(versions_requested=None): # version_requested = specify a specific version number(s) to seek, regardless of specify_versions. 
                                            # useful for pickups. I think here's the best place, because it just returns a list of 1, no later culling.
    fulladdr = {}

    def makeurl(ending):
        html_root = "https://docs.blender.org/api/"
        url = html_root + ending
        return  url

    resp = requests.get("https://docs.blender.org/api/api_dump_index.json")
    dict_data = resp.json()  # requests automatically parses JSON
    #print(f"dict data: {dict_data}")
    for k, v in dict_data.items():
        if versions_requested:
            if float(k) not in versions_requested: # if a shortlist, exclude anything not on the shortlist.
                continue

        fulladdr[k] = makeurl(v)
    return fulladdr

def write_raw_file_from_web(root, version, link):

    filepath =  root + version + ".json"
    if not os.path.exists(root):
        os.makedirs(root)

    with open(filepath, "w+"):
        dump_file=requests.get(link)
        dump_json = dump_file.json()
        Path(filepath).write_text(json.dumps(dump_json))
    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} -- raw file created.")
    else:
        print("File does not exist.")

def get_version_label(file):
    filename = os.path.basename(file)
    filename = filename.rsplit(".", 1)[0]
    version_label = filename.split("_")[0]
    #print("versionname: ", versionname)
    return version_label

def compare_json(file1_path, file2_path):
    # Load JSON files
    #from deepdiff import DeepDiff
    try:
        with open(file1_path, "r") as f1, open(file2_path, "r") as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
    except Exception as e:
        print("There was a problem opening the file(s):", e)

    comb_dict = {}

    def build_nodes(version, file):
        main_dict = {}
        for k in file.keys():
            #print(f"K: {k}, v: {v}") is the whole dict.
            for innerk, innerv in file[k].items():
                #build_nodes(version, node, json1[k])
                #print("innerk, innerv: ", innerk, innerv) # AOV {'is_valid': ['prop_rna', 'Valid', 'boolean', None, 0, False, 'Is the name of the AOV conflicting', '...', '...', '...'], 'name': ['prop_rna', 'Name', 'string', None, 0, '', 'Name of the AOV', '...', '...', '...'], 'type': ['prop_rna', 'Type', 'enum', None, 0, 'COLOR', 'Data type of the AOV', '...', '...', '...']}
                #

                ###      dict from 'version: AOV:contents'##
                #if not main_dict.get(version):
                #    main_dict[version] = {}
                #main_dict[version].update({innerk: innerv}) 
                

                ## if dict is only made per version:
                main_dict[innerk] = innerv ## key is highest level, no version recorded directly. 
                 ## ^^  this version gets actual results ^^



                node = Nodes(innerk)
                node.version.update({version: innerv})
                #print(node.name)
                #print(node.version)
                #print(f"len.versions: {len(node.version)}")        
                #for versions in node.version:
                #    versionlist.add(versions)
                #if len(node.version) > 1:
                    #print(node.version)
                for version, attr in node.version.items():
                    #print(f"Version: {version}, Attr: {attr}")
                    node.attr.append(attr)
                #print(f"Node attributes: {node.attr}")

                    #print(f"node version keys: {node.version.keys()}")
        return main_dict # maindict = version:({k, v})
#
    def build_nodedicts(file, filepath):

        version = get_version_label((filepath))

        print(f"Building names for API version {version}")
        file_dict = build_nodes(version, file)
        return file_dict, version

    dict1, version1 = build_nodedicts(json1, file1_path) 
    dict2, version2 = build_nodedicts(json2, file2_path)  

    #for k, w in dict1.items():
    #    print(k) # 3.1
    #    #print(k, w) # <- version: everything in it
    #    for w in dict1[k]:
    #        print(w)
    #        for y in dict1[k][w]:
    #            print(y) # "is_valid"
    #            exit()
    #        break
    #    for w in dict1.get(k):
    #        w = dict1[k][w]
    #        #print(f"w: {w}")
    #        #print(len(w))
    #        dict1_inner=w#print(type(w))
    #for k in dict2.keys():
    #    for w in dict2.get(k): # this bit is so dumb. 
    #        w = dict2[k][w]
    #        print(len(w))
    #        dict2_inner=w#print(type(w)) ## inner keys inside of 'version'
    #               
    from deepdiff import DeepDiff

    diff = DeepDiff(dict1, dict2, ignore_order=True)

    #if diff:
        #print("Differences found:") # it reports one diff. Cannot be  the case, at all.
        #print(diff)
        #exit()
    #else:
    #    print("No differences found.")

    for k, v in diff.items():
        print(f"Key is different across API versions: {k}") ### first key: dictionary_item_added = new when comparing 1, 2 
        print(type(v)) # v is type <class 'deepdiff.helper.SetOrdered'>
        for item in v:
            print(item) # okay downside of this method: It doesn't give the header name. Header name has to be inferred from item text.
            # eg these:
                # root['Context']['asset']
                # root['Context']['region_popup']
                # root['Context']['path_resolve']
                #   are three independent changes, only grouped by being near each other. So the HTML parser wins over that.
        #for keys in diff[v].keys():
        #    print(keys)
        exit()
#  diff keys:
#       dictionary_item_added
#       dictionary_item_removed
#       values_changed
#       iterable_item_added
#       iterable_item_removed

        #print(f"Value: {diff[k]}")
    for k in dict1.keys():
        exit()
        testk = dict2.get(k)
        if not testk:
            print(f"'{k}' missing from dict2.")

   # for k in json1.keys():
   #     #print(f"K: {k}, v: {v}") is the whole dict.
   #     for innerk, innerv in json1[k].items():
   #         #build_nodes(version, node, json1[k])
   #         #print("innerk, innerv: ", innerk, innerv) # AOV {'is_valid': ['prop_rna', 'Valid', 'boolean', None, 0, False, 'Is the name of the AOV conflicting', '...', '...', '...'], 'name': ['prop_rna', 'Name', 'string', None, 0, '', 'Name of the AOV', '...', '...', '...'], 'type': ['prop_rna', 'Type', 'enum', None, 0, 'COLOR', 'Data type of the AOV', '...', '...', '...']}
   #         node = Nodes(innerk)
   #         node.version.update({version: {innerk: innerv}})
   #         print(node.name)
   #         print(f"len.versions: {len(versions)}")
            #for versions in node.version:
            #    print(versions)
            #break

    #print(json1)
    # jsons 
    # Compare using DeepDiff
    #diff = None
    #diff = DeepDiff(json1, json2, ignore_order=True)

    #if diff:
    #    print("Differences found:")
    #    print(diff)
    #else:
    #    print("No differences found.")
## compare 2 cleaned json files
def compare_files(files):

    if len(files) == 2:
        file1, file2 = files
        compare_json(file1, file2)

def make_verlist(files):
    ver_set = set()
    for file in files:
        ver_set.add(get_version_label(file))
    return ver_set

def make_files(api_dir, versions_requested=None):
    print(f"dir: {api_dir}, versions_requested: {versions_requested}")
    link_dict = get_json_links(versions_requested)
    #print(link_dict)
    for version, link in link_dict.items():
        write_raw_file_from_web(api_dir, version, link)
    print("Raw files created.")
    files, complete = check_for_files(api_dir, versions_requested)
    print(f"Complete: {complete}")
    return files, complete # if complete==true, all files expected were found.

## run
def get_files(api_dir, betweens, versions, overwrite): # versions includes source + target. keeping source+target here for directionality. Could do it with a bool ('forward_convert' bool maybe)
    #version = 4.1
    #files = make_files(version)

    if type(api_dir) != str:
        api_dir=api_dir[0] # because the args often return a tuple
    if not api_dir.endswith("\\"):
        api_dir = api_dir + "\\" # try to make sure it's actually a folder, not generating in the parent folder. Probably a better way. Actually definitely. Will look it up later.

    print(f"API file dir: {api_dir}")
    files, complete = check_for_files(api_dir, versions)
    #print(f"Files: {files}")
    if not files:
        print("No viable files found. Attempting to create...")
        files, complete = make_files(api_dir, versions) ## api_dir needs to be set somewhere else. Maybe the wrapper script that doesn't exist yet. Should be an import, not something passed through like this.
    if files and complete:
        print("All files found.")
    else:
        print(f"Files: {files}")
        print(f"complete: {complete}")
        print("Not all files found. Using the verlist.")
        verlist = make_verlist(files) # not sure if the verlist makes sense anymore. Might have to redo this section
        to_make=[]
        for version in versions:
            if version not in verlist:
                to_make.append(version) # could just do this from the start, ignore the 'make all'. I kinda like that though. Why bother iterating, y'know? Idk.
                print("File not found. Will create.")
        if to_make:
            files, complete = make_files(api_dir, to_make) #makes any/all if >=1 not found. Doesn't make a specific file that was missing. Need to change this.
                #this should not return 'files', because it'll overwrite with each one added.

        if not files or not complete:
            print("Files not found locally and failed to download.")
            return "Files not found locally and failed to download."
    
    cleaned, complete = check_for_files(api_dir + "cleaned_api_dumps\\", versions)
    if complete:
        print("All cleaned files requested were found pre-existing.")
    if overwrite or not cleaned:
        print("Overwrite or cleaned not found; cleaning:")
        cleaned = clean_files(api_dir, files)
    
    if len(cleaned) == len(versions):
        print("All cleaned files confirmed to exist.")
    else:
        print(f"{len(versions)} versions requested, only {len(cleaned)} final API documents.")
    
    ###
    """And here is where the script has to diverge.
    We send `versions`, `cleaned` and `forward_convert` (if we actually make that here - doubtful but for now.) onward to the actual conversion script. This is the end of the function here. I think that's better.
    """
    return versions, cleaned
#output result:
#   Result: ([3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5], ['D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.1_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.2_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.3_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.4_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.5_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\3.6_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.0_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.1_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.2_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.3_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.4_cleaned.json', 'D:\\Git_Repos\\blender-API-helper\\temp_pipeline_outputs\\\\cleaned_api_dumps\\4.5_cleaned.json'], True)

    # none of the rest of this gets used. This script: Only for getting + preparing the required files. Will delete once I've gotten everything useful from it.
    if betweens:
        if len(cleaned) == len(versions):
            compare_files(cleaned)    
    elif len(versions) == 2:
        compare_files(cleaned) 
    else:
        print(f"{len(cleaned)} files found. But betweens was False, so why are there more than 2?")


class Nodes: # doesn't do anything yet. Mostly just here because I think it might be useful to implement later. 
    def __init__(self, name):
        self.name = name
    
    version = {}
    attr = []

#def build_nodes(version, name, data):
#    for property, contents in data.items():

#        print(node.version)
#        break
def get_versions(source_version, target_version, betweens):
    import sys
    import get_json_dumps
    version_numbers = get_json_dumps.get_json_links(get_v_only=True)
    all_versions = []
    for item in version_numbers:
        item.strip(", ")
        all_versions.append(float(item)) # not sure of a better way to convert them all to floats. Probably is one.
    #int_versions = list of all api versions as floats.

    forward_convert=True # by default, assume going from earlier to more recent API version.

    if source_version not in all_versions:
        print(f"Source version {source_version} not found. Please check - version must be given as a float, and must match one of these API versions: {all_versions}")
        sys.exit()
    if target_version not in all_versions:
        print(f"Target version {target_version} not found. Please check - version must be given as a float, and must match one of these API versions: {all_versions}")
        sys.exit()

    #maybe a little helper function for this. Could be neater; just 'get_versions()' all on its own. Keeping it for now though.
    if source_version > target_version:
        forward_convert=False # I don't know if this script needs this either. Again it's only getting the raw data, it doesn't care about directionality.
                                # keeping it for now, but might move it to the outer layer script later. This should really be a subprocess.
    if betweens:
        if forward_convert==False:
            v1=target_version
            v2=source_version
        else:
            v1=source_version
            v2=target_version

        versions = [v for v in all_versions if v1 <= v <= v2]
        #print(f"Versions: {versions}")
    else:
        versions=[source_version, target_version] # if no inbetweens, just get the source and target.
        print(type(versions))
    #versions = {version for version in range(v1, v2)} ## range requires they be in order, so the older API must come first.
    # theoretically the api converter should run just as smoothly going from newer api to older, so force it to arrange them correctly here.

    if not versions:
        print("No versions found: Check --source_version and --target_version are provided. Exiting.")
        exit(0)
    return forward_convert, versions # could output source and target directly here. Thinking about it.


"""
from https://stackoverflow.com/questions/36059194/what-is-the-difference-between-json-dump-and-json-dumps-in-python:

When you call jsonstr = json.dumps(mydata) it first creates a full copy of your data in memory and only then you file.write(jsonstr) it to disk. 
So this is a faster method but can be a problem if you have a big piece of data to save.
When you call json.dump(mydata, file) -- without 's', new memory is not used, as the data is dumped by chunks. But the whole process is about 2 times slower."""
