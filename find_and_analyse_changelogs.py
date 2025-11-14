# find or generate a changelog from source to target

# taking from the original scripts, they're just so messy though.

from operator import index
import os

api={"log_path": r"D:/Git_Repos/blender-API-helper/api_dumps_rst_output", "local_paths": {}} #r"D:\Git_Repos\blender-API-helper\test_scripts\BLENDER_export_nodegroups_recursive.py"}


# python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst
# also, add '--save_hardcopy=False' to not save a hardcopy of the comparison file

### CHECK FOR FILES (in dict, then in api log path) ###

#  path/to/api/docs == log_path

def check_is_file(filepath, version):
    if isinstance(version, float):
        version=[version] # this is so silly. Why not just compare float to float...?

    if os.path.isfile(filepath):
        try:
            basename = float(os.path.basename(str(filepath)).rsplit(".",1)[0]) # This feels hacky.
            if basename in version:
                return basename
        except Exception as e:
            print(f"Failed to get basename from {filepath}: {e}")
    return None

def get_files(version:float, local_files:list) -> str:

    for f in local_files:
        if "api_dump_index" in f: # skip this file - should be the only other file in the thing. Or potentially, we just skip anything found that can't be made a float, to allow other files to exist but just exclude them if they don't fit the expected patterns. Probably better, really.
            print("skipping, file is log path")
            continue
        basename=check_is_file(f, version)
        if basename and basename != None:
            print(f"Local file {f} exists.")
            return f
    print(f"No local file found for version {version}")
    return None

def make_file(version=float):

    print

def get_local_files():
    root=api["log_path"]
    from pathlib import Path
    if not os.path.exists(root):
        print(f"Log path {root} is not a valid/existing directory.")
        return None

    local_files = [str(f) for f in Path(root).iterdir() if f.is_file()] # made this str so they're not winpath obj. Might be a mistake but it keeps the list usable if pre-existing, otherwise they're all windpath objects. idk if it's better to keep them that, but this way it's consistent - whether found or created, 'cleaned' is a list of str filepaths.
    for f in local_files:
        if "api_dump_index" in f:
            print("index file found.")
    if local_files:
        print(f"Local files found: {local_files}")
        return local_files

#cli call for generating rst files
#  python doc/python_api/sphinx_changelog_gen.py -- --indexpath="path/to/api/docs/api_dump_index.json" changelog --filepath-in-from blender_api_2_63_0.json --filepath-in-to   blender_api_2_64_0.json --filepath-out changes.rst
#actual real-life call:
#  python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst
def get_initial_files(source_v, target_v):
    link_dict = {}
    local_logs=api["local_paths"]
    root=api["log_path"]
    local_files = get_local_files()
    for version in [source_v, target_v]:
        filepath = get_files(version, local_files)
        if not filepath:
            if link_dict == {}:
                from get_changelogs_raw import get_link_list
                link_dict=get_link_list(root) ## link_dict now includes remote file locations for all versions, not just those requested at the call time.
            from get_changelogs_raw import write_raw_file_from_web
            filepath=write_raw_file_from_web(root, version, link_dict[str(version)])
            check=check_is_file(filepath, version)
            if check:
                print(f"File {filepath} attained for version {version}")
            else:
                print(f"Failed to download/save a changelog for {version}")
        local_logs[version]=filepath
    print(f"local logs: {local_logs}")
    return link_dict, local_logs

def breakdown_blocks(blocks):
    pass

def parse_changelog(filepath_out):
    #doing this with line by line parsing, because docutils has piss-poor documentation and Sphinx is heavy and I'm too tired. Wasted a day on them already.
    print("Pretend I'm parsing things.")
    line_list=[]
    with open(filepath_out) as file:
        for line in file:
            line_list.append(line.rstrip())
    block_starts=[] #better way of doing this, this was from a previous trial and now just functions as a test bool for the first run.
    blocks={}
    blocks_detailed={}
    counter=0
    active_block=False
    block_type=None
    for i, line in enumerate(line_list):
        if block_starts==None:
            continue
        if line.startswith("----") or i+1 == len(line_list): # marks start+end of blocks
            if active_block:
                start=blocks[counter-1]["block_starts"]
                lines_in_block=[]
                detailed_lines_in_block=[]
                for block_i, line in enumerate(line_list):  #### !! this only appends the first and last entry. Changing how I do it.
                    if start<block_i<i: # should this be 'while' instead of 'if'?
                        if line == '':
                            continue
                        if not (line.startswith("----") or i+1 == len(line_list)): # makes sure it appends the last entry
                            continue
                        if line.startswith("^^^"):
                            if line_list[block_i+1] in ("Added", "Renamed", "Replaced", "Removed", "Function Arguments"):
                                blocks_detailed[counter-1].update({block_type: {"block_contents": detailed_lines_in_block}})
                                detailed_lines_in_block=[]
                            continue
                            # here, we should get the next line, and append the old block_type and block so far to a dict.
                        if line.strip() in ("Added", "Renamed", "Replaced", "Function Arguments", "Removed"):
                            block_type=line.strip()
                            continue
                        #lines_in_block == all lines, inc headers, ^^^, etc.
                        detailed_lines_in_block.append(line)
                        lines_in_block.append(line) # not sure if I want to do this and then finesse the results separately or just do it directly. Really should do it directly if there's no benefit to double handling.
                        #while line.startswith("*"): <- something like this?
                        #if lines.startswith("^^^^"):
                        #    blocks[counter-1].update({"block_ends": i-1, block_type: {"block_contents": lines_in_block}})
                        #    block_type=line_list[block_i+1]
                        #    print(f"block type: {block_type}")
                        #    #blocks[counter-1].update({"block_type": {line_list[block_i+1]:None}})
                        #    continue
                        blocks[counter-1].update({"block_ends": i, "block_contents": lines_in_block})
                        blocks_detailed[counter-1].update({"block_ends": i})
            if not line.startswith("----"):
                continue
            blocks[counter]={"block_starts": i+1, "block_item": line_list[i+1]}
            blocks_detailed[counter]={"block_item": line_list[i+1]}
            block_starts.append(i+1)
        #    affected=[]
            active_block=True
            counter+=1
        #if line.startswith("^^^^"):
        #    change_type=line_list[i+1]
        #    blocks[counter].update({"change_type": {change_type:affected}})
        #if line.startswith("*"):
        #    affected.append(line) # needs characters stripped, and :class:.
        #    print(f"counter: {counter}")
        #    blocks[counter]["change_type"].get(change_type).update(affected)#blocks[counter].update({"affected"})
    #print(f"blocks: {blocks_detailed}")
    breakdown_blocks(blocks)

def make_changelog(local_logs, source_v, target_v):
    #cmd_line = r'python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst'
    raw_output_filename = str(source_v) + "_" + str(target_v)
    raw_output_filename = raw_output_filename.replace(".", "_")
    outout_filename = "/" + raw_output_filename + "_changes.rst"
    filepath_out=api["log_path"] + outout_filename

    if not os.path.isfile(filepath_out):
        from sphinx_changelog_gen import generate_changelogs
        indexpath = api["log_path"] + "/api_dump_index.json"
        filepath_from=local_logs[source_v]
        filepath_to=local_logs[target_v]
        cmd_line = ['--', f'--indexpath={indexpath}', 'changelog', '--filepath-in-from', f'{filepath_from}', '--filepath-in-to', f'{filepath_to}', '--filepath-out', f'{filepath_out}'] # Currently it always makes the rst, as the raw dict is too full of extra bits and the rst formatting is ideal.
        generate_changelogs(cmd_line) # creates the rst file
        print(f"changelog rst: {filepath_out}")
    parse_changelog(filepath_out)

def main(source_v=3.5, target_v=4.5):

    link_dict, local_logs = get_initial_files(source_v, target_v)
    make_changelog(local_logs, source_v, target_v)

main()
