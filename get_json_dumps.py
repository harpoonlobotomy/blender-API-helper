#get API json dump links
# no analysis, just bulk download of the api dumps.
# ! Not used in the actual script process. Just for bulk download of the api dumps.

# 7/11/25
# https://docs.blender.org/api/

from pathlib import Path
import requests
import json

def makeurl(ending):
    html_root = "https://docs.blender.org/api/"
    url = html_root + ending
    return  url

def get_json_links(get_v_only=False):
    fulladdr = {}
    resp = requests.get("https://docs.blender.org/api/api_dump_index.json")
    dict_data = resp.json()  # requests automatically parses JSON
    if get_v_only:
        version_list=list(dict_data)
        return version_list # version numbers only. Includes 5.1 which might be incomplete.
    for k, v in dict_data.items():
        v = makeurl(v)
        fulladdr[k] = v
        #print(f"{k}:  {v}")
    return fulladdr

def writefile(version, link):
    import os
    root = os.path.dirname(os.path.abspath(__file__)) + "\\api_dumps"
    outputfile = version + ".json"
    filepath = root + "\\" + outputfile
    if not os.path.exists(root):
        os.makedirs(root)

    with open(outputfile, "w+"):
        dump_file=requests.get(link)
        dump_json = dump_file.json()
        Path(filepath).write_text(json.dumps(dump_json))
    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} created.")
    else:
        print("File does not exist.")

def main():
    link_dict = get_json_links()
    for version, link in link_dict.items():
        writefile(version, link)

if __name__ == "__main__":
    main()


"""
from https://stackoverflow.com/questions/36059194/what-is-the-difference-between-json-dump-and-json-dumps-in-python:

When you call jsonstr = json.dumps(mydata) it first creates a full copy of your data in memory and only then you file.write(jsonstr) it to disk.
So this is a faster method but can be a problem if you have a big piece of data to save.
When you call json.dump(mydata, file) -- without 's', new memory is not used, as the data is dumped by chunks. But the whole process is about 2 times slower."""
