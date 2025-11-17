# find or generate a changelog from source to target

#So I feel like the current version isn't going to be useful. Only having the bpy.types changelogs makes it hard to track deeper changes, as the changed names don't explicitly come up. And those broader changes are going to be the issue.
# I can take my best bet with heuristics - if you mention nodes and sockets I can give recommendations as to the biggest changes, but that wasn't the point of this.
# Maybe this is something I need to come back to later. I'm tired, and let's be honest I don't know what I'm doing. This whole thing is probably a mess.

from operator import index
import os

api={"log_path": r"D:/Git_Repos/blender-API-helper/api_dumps_rst_output", "local_paths": {}} #r"D:\Git_Repos\blender-API-helper\test_scripts\BLENDER_export_nodegroups_recursive.py"}

headers = ["Added", "Renamed", "Removed", "Function Arguments"]
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
    print(f"source_v: {source_v}, target_v: {target_v}")
    link_dict = {}
    local_logs=api["local_paths"]
    root=api["log_path"]
    local_files = get_local_files()
    for version in [source_v, target_v]:
        filepath = get_files(version, local_files)
        if not filepath:
            if link_dict == {}:
                from get_changelogs_raw import get_link_list
                link_dict=get_link_list(root) ## link_dict now includes remote file locations for all versions, not just those requested at the call time. So this should only need to run once.
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
    # Sample entry:
    """Entry:  {'block_starts': 3106, 'block_item': 'bpy.types.WindowManager', 'block_ends': 3130, 'block_contents': ['Added', '* :class:`bpy.types.WindowManager.extension_search`', '* :class:`bpy.types.WindowManager.extension_show_panel_available`', '* :class:`bpy.types.WindowManager.extension_show_panel_installed`', '* :class:`bpy.types.WindowManager.extension_type`', '* :class:`bpy.types.WindowManager.extensions_blocked`', '* :class:`bpy.types.WindowManager.extensions_updates`', 'Renamed', '* **pose_assets** -> :class:`bpy.types.WindowManager.addon_tags`', '* **pose_assets** -> :class:`bpy.types.WindowManager.extension_tags`', 'Function Arguments', '* :class:`bpy.types.WindowManager.invoke_confirm` (operator, event, title, message, confirm_text, icon, text_ctxt, translate), *was (operator, event)*', '* :class:`bpy.types.WindowManager.invoke_props_dialog` (operator, width, title, confirm_text, cancel_default, text_ctxt, translate), *was (operator, width)*']}
    Entry:  {'block_starts': 3131, 'block_item': 'bpy.types.WorkSpace', 'block_ends': 3139, 'block_contents': ['Renamed', '* **active_pose_asset_index** -> :class:`bpy.types.WorkSpace.active_addon`', '* **asset_library_ref** -> :class:`bpy.types.WorkSpace.asset_library_reference`']}"""


    # renamed formatting: 'Renamed': ['* **show_edges** -> :class:bpy.types.View3DOverlay.show_camera_guides'
    # function argument change: 'Function Arguments': ['bpy.types.WindowManager.invoke_confirm (operator, event, title, message, confirm_text, icon, text_ctxt, translate), *was (operator, event)*'
    """
    if block_type == "Renamed":
        bpy_types_id + first half == 'old name'

    So... regex to get **(this text)**

    Or really I could just get the dicts themselves already pre-done, instead of parsing the text at all. I really, really should just do that.
    """

    cleaned_dict = {}
    for entry in blocks.values():
        bpy_types_id = entry["block_item"]
        cleaned_dict[bpy_types_id]={}
        block_type=None
        changed = []
        for i, line in enumerate(entry["block_contents"]):
            if line in headers:
                if cleaned_dict[bpy_types_id].get(block_type):
                    cleaned_dict[bpy_types_id][block_type]=changed # append to the prev block type before changing and finding new changes
                block_type=line
                changed=[] # empty the changed list
                cleaned_dict[bpy_types_id][block_type]=changed # start the new section
            else:
            #    if line.startswith("*"): # why not just do line.replace() all the time? Does it take longer than checking startswith()? does it matter? What's the general pov on this?
            #                                # Given that it only has to check the first char of each line, I guess it's actually better to do the startswith first, so it doesn't check for " :class:" everywhere on every line, and same for "`" later. Mm.
            #        line = line.replace("* :class:", "")
            #    if "`" in line:
            #        line=line.replace("`", "") ## Turned all of these off, because they're all removed at the sphinx changelog gen stage now.
                changed.append(line)
    #print(f"\n cleaned dict: \n \n {cleaned_dict}")
    return cleaned_dict

def parse_changelog(filepath_out):
    #doing this with line by line parsing, because docutils has piss-poor documentation and Sphinx is heavy and I'm too tired. Wasted a day on them already.
    line_list=[]
    with open(filepath_out) as file:
        for line in file:
            line_list.append(line.rstrip())
    block_starts=[]
    blocks={}
    counter=0
    active_block=False

    for i, line in enumerate(line_list): ## should I do this while the file is open instead instead of running two separate for loops here? Feels like no but I have no justification for that feeling.
        if block_starts==None:
            continue
        if line.startswith("----") or i+1 == len(line_list): # marks start+end of blocks
            if line.startswith("----"): # separated this out so it only starts a new block at ---, but the blocks are still gathered at the last one.
                blocks[counter]={"block_starts": i+1, "block_item": line_list[i+1]}
            if active_block:
                start=blocks[counter-1]["block_starts"]
                lines_in_block=[]
                for block_i, line in enumerate(line_list): # Should be able to process it all inline here.  But currently can't, so will process the blocks separately.
                    if start<block_i<i: # should this be 'while' instead of 'if'?
                        if line in ('') or line.startswith("^^^^") or line.startswith("----"): # there's a better way of doing this but it works. God I'm braindead today.
                            continue # skip adding blank, ^^ and -- lines.
                        lines_in_block.append(line) #just adding blocks raw for now, later want to do the cleaning inline (change_type subsets etc) but for now, just doing a second pass.
                        blocks[counter-1].update({"block_ends": i, "block_contents": lines_in_block})
                counter+=1 # increase counter while active_block. It wasn't incrementing and I didn't notice...
            if not line.startswith("----"):
                continue
            block_starts.append(i+1)
            active_block=True
            counter+=1

    blocks_dict=breakdown_blocks(blocks)

def make_cli_args(local_logs, source_v, target_v, blender=False, overwrite=True):

    raw_output_filename = str(source_v) + "_" + str(target_v)
    raw_output_filename = raw_output_filename.replace(".", "_")
    outout_filename = "/" + raw_output_filename + "_changes.rst"
    if blender: # is the version in testing for blender direct output. Use a different dir.
        indexpath = api["log_path"] + "/blender_version/api_dump_index.json"
        filepath_out=api["log_path"] + "/blender_version/" + outout_filename
        add_parser="dump"
        ## why not run it in blender via the cli? Why run the script in blender manually? silly. TODO: Fix this part.
        cmd_line = ['--', f'--indexpath={indexpath}', f'{add_parser}', '--filepath-out', f'{filepath_out}'] # this is all so messy...
    else:
        indexpath = api["log_path"] + "/api_dump_index.json"
        filepath_out=api["log_path"] + outout_filename
        add_parser="changelog"
        filepath_from=local_logs[source_v]
        filepath_to=local_logs[target_v]
        cmd_line = ['--', f'--indexpath={indexpath}', f'{add_parser}', '--filepath-in-from', f'{filepath_from}', '--filepath-in-to', f'{filepath_to}', '--filepath-out', f'{filepath_out}'] # Currently it always makes the rst, as the raw dict is too full of extra bits and the rst formatting is ideal.

    print(f"cmd_line:\n {cmd_line}")
    if not os.path.isfile(filepath_out) or overwrite==True:
        print(f"  Filepath out: {filepath_out}\n  Now starting file production.")

        return cmd_line, filepath_out
    return None, filepath_out

def make_changelog(local_logs, source_v, target_v):
    #cmd_line = r'python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst'


    # bool for testing:
    parse_changelogs = False

## API data for the original 'dump' functions:
#    parser_dump = parser_commands.add_parser('dump', help="Dump the current Blender Python API into a JSON file.")
#    parser_dump.add_argument(
#        "--filepath-out", dest="filepath_out", metavar='FILE', required=True,
#        help="Path of the JSON file containing the dump of the API.")
#    parser_dump.set_defaults(func=api_dump)
#
#    parser_changelog = parser_commands.add_parser(
#        'changelog',
#        help="Generate the RST changelog page based on two Blender Python API JSON dumps.",
#    )

    cmd_line, filepath_out =make_cli_args(local_logs, source_v, target_v, blender=True, overwrite=True)
    if cmd_line: ## May need clearer language. '`not cmdline` means the file already existed an overwrite==False
        from sphinx_changelog_gen import generate_changelogs
        generate_changelogs(cmd_line) # creates the rst file
        #print(f"changelog rst: {filepath_out}")

    if parse_changelogs:
        parse_changelog(filepath_out)

def make_blender_json(source_v, target_v):

    return None, None#link_dict, local_logs

def main(source_v=2.92, target_v=4.2):

    make_changelog_on=False
    get_blender_data=True

    link_dict, local_logs = get_initial_files(source_v, target_v)
    make_changelog(local_logs, source_v, target_v) ## Not properly implemented yet, halfway between new version (standalone blender-json-file-creation) and old version.

main()
