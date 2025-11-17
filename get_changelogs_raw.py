#get changelogs from online

import os

def get_link_list(log_path):
    fulladdr={}
    def makeurl(ending):
        html_root = "https://docs.blender.org/api/"
        url = html_root + ending
        print(f"URL: {url}")
        return url

    if not os.path.isfile(log_path + "\\api_dump_index.json"):
        print(f"Not a file: {log_path + "\\api_dump_index.json"}")
        import requests
        raw_index = requests.get("https://docs.blender.org/api/api_dump_index.json") # currently we do this each time we need to get a link. That'll be any midpoint. Going to move this part.
        link_dict = raw_index.json()  # requests automatically parses JSON
        print(f"link_dict after downloading from remote: {link_dict}")
    else:
        import json
        index_path=(log_path + "/api_dump_index.json")
        with open(index_path, "r") as f1:
            link_dict = json.load(f1)
    for k, v in link_dict.items():
        link=makeurl(v)
        fulladdr[k]=link

    return fulladdr

def write_raw_file_from_web(root, version, url):
    filepath =  root + "//" + str(version) + ".json"
    if not os.path.exists(root):
        os.makedirs(root)
    import requests
    from pathlib import Path
    import json
    with open(filepath, "w"):
        print(f"Filepath: {filepath}, url: {url}")
        dump_file=requests.get(url)
        dump_json = dump_file.json()
        Path(filepath).write_text(json.dumps(dump_json))
    if os.path.isfile(filepath):
        print(f"{os.path.abspath(filepath)} -- raw file created.")
        return filepath
    else:
        print("File does not exist.")
