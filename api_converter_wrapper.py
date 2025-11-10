# api_converter_wrapper
# just a script to handle the file-creation, versions, etc.
# harpoonlobotomy 8/11/25

## Just found \doc\python_api\rst\change_log.rst.
# It's the best of both worlds. Functionally it's the same format etc as the HTML page, but without the difficulty of having to differentiate between headers etc - the handy dandy dashed line makes all the difference.
# So, looks like I'm re-re-re-starting the parse/diff stage.

#\source\blender\python\intern\bpy_rna_id_collection.cc
#    "   For list of valid set members for key_types & value_types, see: "
#    ":class:`bpy.types.KeyingSetPath.id_type`.\n"

#maybe this:
# PyMethodDef BPY_rna_id_collection_user_map_method_def = {
#     "user_map",
#     (PyCFunction)bpy_user_map,
#     METH_STATIC | METH_VARARGS | METH_KEYWORDS,
#     bpy_user_map_doc,
# };

# print(bpy.data.user_map()) this prints every 'thing' in the blend file. objects, text, workspaces, nodegroups. Heaven.
#       built here I believe: \source\blender\python\intern\bpy_rna_id_collection.cc

# why do texts have a set? Is that just a placeholder because they don't have object data? Guess so.  bpy.data.texts['BLENDER_Mat_Gen.py']: set()

# \tools\utils_api\bpy_introspect_ui.py
# not directly relevant but blender code internal autocomplete: \extern\gflags\src

import api_context


if __name__ == "__main__":

    try:
        import argparse
        parser = argparse.ArgumentParser(description="Get Blender API reference files for specific versions.") # if only two versions, give whatever diff you can. Encourage 'get the inbetween version data' at that point if limits were specified.
        parser.add_argument("input_file", help="Input Python script (e.g., my_script.py)") # currently only runs a single file. Later, a whole folder would be better. # This is the wrapper, so this is the one that needs the subject script.
        parser.add_argument("--source_version", type=float, default=3.1, help="Source version (API version the script was written for, eg 3.1)")
        parser.add_argument("--target_version", type=float, default=4.5, help="Target version (API version to convert to, eg 4.5)")
        parser.add_argument("--api-dir", default=r"D:\Git_Repos\blender-API-helper\temp_pipeline_outputs", help="Folder to store API reference files.")
        parser.add_argument("--betweens", type=bool, default=True, help="If 'False', only downloads/checks for the specified version numbers.")
        parser.add_argument("--overwrite", type=bool, default=False, help="Overwrite existing API docs")
        args = parser.parse_args()

        subject_script=args.input_file
        source_version=args.source_version # this feels messy. Why am I using argparse instead of sys.args?
        target_version=args.target_version # if not target version, use source_version and only get the one. Not sure why you'd want to. Maybe for getting midpoints later down the line. That's likely, actually.
        api_dir=args.api_dir
        betweens=args.betweens
        overwrite=args.overwrite
        print("Args received:", vars(args))

    except:
        print("No args recieved, using hardcoded defaults.")
        input_file=r"D:\Git_Repos\blender-API-helper\test_scripts\BLENDER_export_nodegroups_recursive.py",
        source_version=3.1
        target_version=4.5
        api_dir=r"D:\Git_Repos\blender-API-helper\api_dumps_3"
        betweens=True
        overwrite=False


    # correcting the API here so its right going into the class
    if type(api_dir) != str:
        api_dir=api_dir[0] # because the args often return a tuple
    if not api_dir.endswith("\\"):
        api_dir = api_dir + "\\" # try to make sure it's actually a folder, not generating in the parent folder. Probably a better way. Actually definitely. Will look it up later.

    #get all version numbers now.
    import requests
    resp = requests.get("https://docs.blender.org/api/api_dump_index.json")
    all_versions = resp.json()

    from get_clean_api_dumps import get_files, get_versions
    forward_convert, versions = get_versions(source_version, target_version, betweens)

    api_context.set_context(api_dir, input_file, source_version, target_version, forward_convert, betweens, overwrite, all_versions)

    print(api_dir, input_file, source_version, target_version, forward_convert, betweens, overwrite, all_versions)
    try:
        print("Going to main.")
        result = get_files(versions) # could keep source+target here. Might be a reason to.
        from api_converter_01 import run
        run(result)
        print(f"Run successful: {result}") # using it here instead.
    except Exception as e:
        print("Failed to run pipeline: ", e)


