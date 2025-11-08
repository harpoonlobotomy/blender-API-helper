#get API json dump links
# This is mostly comments right now, still figuring things out.Does work to diff between versions, but not in a usable way.
# 7/11/25
# https://docs.blender.org/api/

from pathlib import Path
import json
import os
import requests

specify_versions = ["3.1", "4.5"] # for only getting specific versions of the API instead of all
subdir = "\\api_dumps_2"
versionlist = set()

def check_for_raw(localdir):
    print(localdir)
    root = os.path.dirname(os.path.abspath(__file__)) + localdir
    if not os.path.exists(root):
        os.makedirs(root)
        return None
    files = [f for f in Path(root).iterdir() if f.is_file()]
    return files

def cleaned_dumps(version, contents):

    root = os.path.dirname(os.path.abspath(__file__)) + subdir + "\\cleaned_api_dumps\\"
    filepath =  root + version + "_cleaned.json"
    if not os.path.exists(root):
        os.makedirs(root)
        
    with open(filepath, "w+", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)

    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} created.")
    else:
        print("File does not exist.")
    return filepath

def clean_files(files):
    cleaned_filelist = []
    for filename in files:
        with open(filename) as f:
            d = json.load(f) ## d == list, 0==versionname as list "[2, 92]", 1 = contents as dict.
            version = '.'.join(map(str,d[0]))
            file_contents = d[1]
            cleaned_filelist.append(cleaned_dumps(version, file_contents))

    return cleaned_filelist

## Get initial files from the API dump index
def get_json_links():

    fulladdr = {}

    def makeurl(ending):
        html_root = "https://docs.blender.org/api/"
        url = html_root + ending
        return  url

    resp = requests.get("https://docs.blender.org/api/api_dump_index.json")
    dict_data = resp.json()  # requests automatically parses JSON

    for k, v in dict_data.items():
        if specify_versions:
            if k not in specify_versions:
                continue
            
        v = makeurl(v)
        fulladdr[k] = v
    return fulladdr

def write_raw_file_from_web(version, link):

    root = os.path.dirname(os.path.abspath(__file__)) + subdir + "\\" # at start and
    filepath =  root + version + ".json"

    if not os.path.exists(root):
        os.makedirs(root)

    with open(filepath, "w+"):
        dump_file=requests.get(link)
        dump_json = dump_file.json()
        Path(filepath).write_text(json.dumps(dump_json))
    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} created.")
    else:
        print("File does not exist.")

def get_version_name(file):
    filename = os.path.basename(file)
    filename = filename.rsplit(".", 1)[0]
    versionname = filename.split("_")[0]
    #print("versionname: ", versionname)
    return versionname

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

        version = get_version_name((filepath))

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
    verlist = set()
    for file in files:
        verlist.add(get_version_name(file))
    return verlist

def make_files():
    link_dict = get_json_links()
    for version, link in link_dict.items():
        write_raw_file_from_web(version, link)
    files = check_for_raw(subdir)
    return files
## run
def main():

    files = check_for_raw(subdir)
    if specify_versions:
        verlist = make_verlist(files)
        for version in specify_versions:
            if version not in verlist:
                print("File not found. Will create.")
                files = make_files() #makes any/all if >=1 not found. Doesn't make a specific file that was missing. Need to change this.

    if not files:
        print("Raw files are not here.")
        files = make_files()
        if not files: 
            print("Files not found locally and failed to download.")
            return
    
    overwrite_cleaned = False
    cleaned = check_for_raw(subdir + "\\cleaned_api_dumps")
    if overwrite_cleaned or not cleaned:
        print("overwrite or not cleaned, cleaning:")
        cleaned = clean_files(files)
    
    if len(cleaned) == 2:
        print("2 files found.")
        compare_files(cleaned)
    else:
        print(f"{len(cleaned)} files found.")
        

class Nodes: # doesn't do anything yet. Mostly just here because I think it might be useful to implement later.
    def __init__(self, name):
        self.name = name
    
    version = {}
    attr = []

 
#def build_nodes(version, name, data):
#    for property, contents in data.items():

#        print(node.version)
#        break

if __name__ == "__main__":
    main() # no args but theoretically will run as-is. But without args, less useful.

"""
from https://stackoverflow.com/questions/36059194/what-is-the-difference-between-json-dump-and-json-dumps-in-python:

When you call jsonstr = json.dumps(mydata) it first creates a full copy of your data in memory and only then you file.write(jsonstr) it to disk. 
So this is a faster method but can be a problem if you have a big piece of data to save.
When you call json.dump(mydata, file) -- without 's', new memory is not used, as the data is dumped by chunks. But the whole process is about 2 times slower."""
