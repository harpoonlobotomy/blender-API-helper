# find or generate a changelog from source to target

# taking from the original scripts, they're just so messy though.

import os

api={"log_path": r"D:\Git_Repos\blender-API-helper\api_dumps_rst_output", "local_paths": {}} #r"D:\Git_Repos\blender-API-helper\test_scripts\BLENDER_export_nodegroups_recursive.py"}

### CHECK FOR FILES (in dict, then in api log path) ###

#  path/to/api/docs == log_path


def get_files(local_logs:dict, version:float) -> str:
    root=api["log_path"]
    print(f"root: {root}")
    print(f"version inside get_files: {version}")
    print("Version:", version)
    def check_is_file(filepath, version):
        if isinstance(version, float):
            version=[version] # this is so silly. Why not just compare float to float...?

        if os.path.isfile(filepath):
            try:
                basename = float(os.path.basename(str(filepath)).rsplit(".",1)[0]) # This feels hacky.
                if basename in version:
                    return basename
                else:
                    print(f"basename {basename} of type {type(basename)} not in versions: {version}")
            except Exception as e:
                print(f"Failed to get basename from {filepath}: {e}")
        return None

    def run_check(root):
        from pathlib import Path
        if not os.path.exists(root):
            print(f"Log path {root} is not a valid/existing directory.")
            return None

        found_all = [str(f) for f in Path(root).iterdir() if f.is_file()] # made this str so they're not winpath obj. Might be a mistake but it keeps the list usable if pre-existing, otherwise they're all windpath objects. idk if it's better to keep them that, but this way it's consistent - whether found or created, 'cleaned' is a list of str filepaths.
        if found_all:
            print(f"found_all: {found_all}")
            for f in found_all:
                if f == api["log_path"]: # skip this file - should be the only other file in the thing. Or potentially, we just skip anything found that can't be made a float, to allow other files to exist but just exclude them if they don't fit the expected patterns. Probably better, really.
                    continue
                basename=check_is_file(f, version)
                if basename and basename != None:
                    return f
        print("Not found.")
    file = run_check(root)
    if file:
        print(f"Local file {file} exists.")
    else:
        print(f"No local file found for version {version}")

def make_file(version=float):

    print

def get_local_files(local_logs):
    print

#cli call for generating rst files
#  python doc/python_api/sphinx_changelog_gen.py -- --indexpath="path/to/api/docs/api_dump_index.json" changelog --filepath-in-from blender_api_2_63_0.json --filepath-in-to   blender_api_2_64_0.json --filepath-out changes.rst
#actual real-life call:
#  python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst

def main(source_v=3.5, target_v=4.5):

    local_logs=api["local_paths"]
    print(f"local logs at start: {local_logs}")
    for version in [source_v, target_v]:
        print(f"version: {version}")
        get_local = get_local_files(local_logs)
        filepath = get_files(local_logs, version)
        if not filepath:
            make_file(version=float)
        local_logs[version]=filepath




main()
