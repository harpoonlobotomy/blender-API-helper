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
from api_context import api
import api_context

#specify_versions = ["3.1", "4.5"] # for only getting specific versions of the API instead of all

def check_for_files(root, versions): # keep ROOT because it may be a subdir
    print(f"Start of check_for_files, root: {root}, versions: {versions}")
    complete=False
    found=None
    print(f"directory in check_for_files: {root}")
    if not os.path.exists(root):
        os.makedirs(root)
        print(f"Directory doesn't exist yet: {root}")
        return None, complete

    def check_is_file(filepath, versions):

        print("Start of check_is_file")
        print(f"filepath: {filepath}, versions: {versions}")

        if os.path.isfile(filepath):
            f2 = str(filepath).replace("_cleaned", "")
            #print(f"f2: {f2}")
            basename = float(os.path.basename(f2).rsplit(".",1)[0]) # god this is all messy as hell but it does find both clean and raw files. Except it doesn't, because if they['re floats, the 'in' doesn't work.
            if basename in versions:
                #print(f"Basename found: {basename}")
                return basename
            else:
                print(f"basename {basename} of type {type(basename)} not in versions: {versions}")
                return None
        else:
            return None

    found_all = [str(f) for f in Path(root).iterdir() if f.is_file()] # made this str so they're not winpath obj. Might be a mistake but it keeps the list usable if pre-existing, otherwise they're all windpath objects. idk if it's better to keep them that, but this way it's consistent - whether found or created, 'cleaned' is a list of str filepaths.
    if found_all:
        print(f"found_all: {found_all}")
        found=[]
        found_versions = []
        if not versions:
            print("No versions given.")
            if len(found_all) > 1:
                print(f"Assuming they're all here. {len(versions)} version files found.")
                return found_all, True
        for f in found_all:
            basename=check_is_file(f, versions)
            if basename and basename != None:
                api.localpaths[basename]=f
                found_versions.append(basename)
                found.append(f)
        #print(f"versions: {versions}")
        #print(f"found versions: {found_versions}")
        #exit()
        if len(found_versions)==len(versions):
            print("All files requested in versions are Found.")
            complete=True
        else:
            print("Not all versions found.")
    else:
        print("Apparently didn't find_all - don't know why it failed here...")
        exit()
    print("leaving check_for_files")
    return found, complete

def cleaned_dumps(version, contents): # taking api_dir out of here and getting it from the class each time - better or worse?

    #root = os.path.dirname(os.path.abspath(__file__)) + subdir + "\\cleaned_api_dumps\\"
    root=api.dir + "cleaned_api_dumps\\"
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

def clean_files(files):
    cleaned_filelist = []
    for file in files:
        with open(file) as f:
            d = json.load(f) ## d == list, 0==versionname as list "[2, 92]", 1 = contents as dict.
            version = '.'.join(map(str,d[0]))
            file_contents = d[1]
            cleaned_filelist.append(cleaned_dumps(version, file_contents))

    return cleaned_filelist

## Get initial files from the API dump index
def get_dump_links(versions_requested=None): # version_requested = specify a specific version number(s) to seek, regardless of specify_versions.
                                            # useful for pickups. I think here's the best place, because it just returns a list of 1, no later culling.
    fulladdr = {}

    def makeurl(ending):
        html_root = "https://docs.blender.org/api/"
        url = html_root + ending
        return  url

    try:
        dict_data = dict(api.all_versions)
    except:
        resp = requests.get("https://docs.blender.org/api/api_dump_index.json") # currently we do this each time we need to get a link. That'll be any midpoint. Going to move this part.
        dict_data = resp.json()  # requests automatically parses JSON
    #print(f"dict data: {dict_data}")
    for k, v in dict_data.items():
        if versions_requested:
            if float(k) not in versions_requested: # if a shortlist, exclude anything not on the shortlist.
                continue

        fulladdr[k] = makeurl(v)
    return fulladdr

def write_raw_file_from_web(version, link):

    root = api.dir
    filepath =  root + version + ".json"
    if not os.path.exists(root):
        os.makedirs(root)
    if not api.overwrite: # dangerous to default here? idk feels bad.
        if os.path.isfile(filepath):
            print(f"File {filepath} already exists.")
            return

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
    return version_label

def make_ver_set(files):
    ver_set = set()
    for file in files:
        ver_set.add(get_version_label(file))
    return ver_set

def make_files(api_dir, versions_requested=None):
    print(f"dir: {api_dir}, versions_requested: {versions_requested}")
    link_dict = get_dump_links(versions_requested)
    #print(link_dict)
    for version, link in link_dict.items():
        write_raw_file_from_web(version, link)

    print(f"Raw files created. About to check for files, versions requested: {versions_requested}")
    files, complete = check_for_files(api_dir, versions_requested)
    print(f"Complete: {complete}")
    return files, complete # if complete==true, all files expected were found.

## run
def get_files(versions, clean=False): # versions includes source + target.
    #version = 4.1
    #files = make_files(version)
    #, betweens=False, overwrite=False
    ### CURRENTLY: This func requires the non-clean files to be found first. There's no way to say 'here is the cleaned files, don't bother looking for the other ones'.
    # putting in a temporary measure to subvert that.
    api_dir=api.dir
    if type(versions) == str:
        versions = [float(versions)]
    if type(versions) == float:
        versions=[versions]

    print(f"in get_files. Versions: {versions}, clean: {clean}")

    print(f"versions inside get_files: {versions}, type: {type(versions)}")
    if api.betweens == False or len(versions) > 2: # this check is probably outdated by now...
        print("api betweens is False, about to get_source_and_target")
        source, target = api_context.get_source_and_target(versions)
        versions = [source, target]

    clean_dir=api_dir + "cleaned_api_dumps\\" # could set this elsewhere bit it's fine for now.
    print(f"Clean? {clean}")
    if clean:
        if os.path.exists(clean_dir):
            print(f"Clean file dir: {clean_dir}. About to check for files. Versions: {versions}")
            cleaned, complete = check_for_files(clean_dir, versions)
            if complete and len(cleaned) == len(versions):
                return versions, cleaned # return early if all clean versions already exist, else run the func.

    print(f"Not premarked 'clean', about to check for files. versions requested: {versions}")
    files, complete = check_for_files(api_dir, versions)
    #print(f"Files: {files}")

    if not files:
        print(f"No viable files found. Attempting to create. Versions: {versions}")
        files, complete = make_files(api_dir, versions) ## api_dir needs to be set somewhere else. Maybe the wrapper script that doesn't exist yet. Should be an import, not something passed through like this.
    if files and complete:
        print("All files found: all raw files for versions exist..")
    else:
        print(f"Files: {files}")
        print(f"complete: {complete}")
        print("Not all files found. Using the verlist.")
        verlist = make_ver_set(files) # not sure if the verlist makes sense anymore. Might have to redo this section
        to_make=[]
        for version in versions:
            print(f"Version: {version}, type: {type(version)}, versions: {versions}, type: {type(versions)}")
            if version not in verlist:
                to_make.append(version) # could just do this from the start, ignore the 'make all'. I kinda like that though. Why bother iterating, y'know? Idk.
                print("File not found. Will create.")
        if to_make:
            files, complete = make_files(api_dir, to_make) #makes any/all if >=1 not found. Doesn't make a specific file that was missing. Need to change this.
                #this should not return 'files', because it'll overwrite with each one added.

        if not files or not complete:
            print("Files not found locally and failed to download.")
            return versions, None#"Files not found locally and failed to download."

    #print(f"About to check for clean files. Versions: {versions}")
    cleaned, complete = check_for_files(clean_dir, versions)
    #print(f"cleaned, complete after checking for clean files: {cleaned} // complete: {complete}")

    if complete:
        print("All cleaned files requested were found pre-existing.")
    if api.overwrite or not cleaned or not complete:
        print("Overwrite or cleaned not found; cleaning:")
        cleaned = clean_files(files) # doesn't need api because it only run if clean files didn't exist yet.

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

def get_versions(source_version, target_version, betweens=False):

    import sys

    try:
        if api.betweens: # this is so dumb but it allows for that one initial check before api is init. I need to be allowed to set it manually sometimes. Really should remove this one from the class.
            print("betweens is true.")
            betweens = True
            versions=None # so it gets all the potential version numbers, not just the end result versions. Needed for later. But it's broken,
    except:
        pass #this only happens at the first run, it's v silly but it's a workaround. Will fix it properly later.
    if betweens:
        print("betweens is true")
        versions=None
    else:
        print("betweens is not true.")
        versions = [source_version, target_version]

    version_numbers = get_dump_links(versions)
    all_versions = []
    for item in version_numbers:
        item.strip(", ")
        all_versions.append(float(item)) # not sure of a better way to convert them all to floats. Probably is one.

    forward_convert=True # by default, assume going from earlier to more recent API version.

    if source_version not in all_versions:
        print(f"Source version {source_version} not found. Please check - version must be given as a float, and must match one of these API versions: {all_versions}")
        sys.exit()
    if target_version not in all_versions:
        print(f"Target version {target_version} not found. Please check - version must be given as a float, and must match one of these API versions: {all_versions}")
        sys.exit()

    if source_version > target_version:
        forward_convert=False # have to move this elsewhere, so it the class is set correctly the first time. Actually no, as long as this is the only time get_versions is used, it's okay.

    if betweens:
        if forward_convert==False:
            v1=target_version
            v2=source_version
        else:
            v1=source_version
            v2=target_version

        versions = [v for v in all_versions if v1 <= v <= v2]
        print(f"Versions: {versions}")
    else:
        versions=[source_version, target_version] # if no inbetweens, just get the source and target.
        print(f"Versions type: {type(versions)}")
    #versions = {version for version in range(v1, v2)} ## range requires they be in order, so the older API must come first.
    # theoretically the api converter should run just as smoothly going from newer api to older, so force it to arrange them correctly here.

    if not versions:
        print("No versions found: Check --source_version and --target_version are provided. Exiting.")
        exit(0)
    return forward_convert, versions # could output source and target directly here. Thinking about it.

#get_versions(4.1, 4.1, betweens=False) # if only getting one, just repeat the one version in source + target. works fine.

"""
from https://stackoverflow.com/questions/36059194/what-is-the-difference-between-json-dump-and-json-dumps-in-python:

When you call jsonstr = json.dumps(mydata) it first creates a full copy of your data in memory and only then you file.write(jsonstr) it to disk.
So this is a faster method but can be a problem if you have a big piece of data to save.
When you call json.dump(mydata, file) -- without 's', new memory is not used, as the data is dumped by chunks. But the whole process is about 2 times slower."""
