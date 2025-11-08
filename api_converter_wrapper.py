# api_converter_wrapper
# just a script to handle the file-creation, versions, etc.
# harpoonlobotomy 8/11/25

from api_converter_01 import run


if __name__ == "__main__":

    try:
        import argparse
        parser = argparse.ArgumentParser(description="Get Blender API reference files for specific versions.") # if only two versions, give whatever diff you can. Encourage 'get the inbetween version data' at that point if limits were specified.
#        parser.add_argument("input_file", help="Input Python script (e.g., my_script.py)") # currently only runs a single file. Later, a whole folder would be better. # not sure if I want a file here or not. Surely there's a script outside of this one, calling this one. This one shouldn't care about the script.
        parser.add_argument("--source_version", type=float, default=3.1, help="Source version (API version the script was written for, eg 3.1)")
        parser.add_argument("--target_version", type=float, default=4.5, help="Target version (API version to convert to, eg 4.5)")
        parser.add_argument("--api-dir", default=r"D:\Git_Repos\blender-API-helper\temp_pipeline_outputs", help="Folder to store API reference files.")
        parser.add_argument("--betweens", type=bool, default=True, help="If 'False', only downloads/checks for the specified version numbers.") ## add "--disable_patterns True" to disable patterns.
        parser.add_argument("--overwrite", type=bool, default=False, help="Overwrite existing API docs")
        args = parser.parse_args()

        source_version=args.source_version # this feels messy. Why am I using argparse instead of sys.args?
        target_version=args.target_version # if not target version, use source_version and only get the one. Not sure why you'd want to. Maybe for getting midpoints later down the line. That's likely, actually.
        api_dir=args.api_dir
        betweens=args.betweens
        overwrite=args.overwrite
        print("Args received:", vars(args))

    except:
        print("No args recieved, using hardcoded defaults.")
        #input_file="",
        source_version=3.1
        target_version=4.5
        api_dir=r"D:\Git_Repos\blender-API-helper\api_dumps_3"
        betweens=True
        overwrite=False

    from get_and_clean_api_dumps_02 import get_files, get_versions
    forward_convert, versions = get_versions(source_version, target_version, betweens)

    try:
        print("Going to main.")
        result = get_files(api_dir, betweens, versions, overwrite) # could keep source+target here. Might be a reason to.
        print(f"Result: {result}")
    except Exception as e:
        print("Failed to run pipeline: ", e)

    run(source_version, target_version, result) # using it here instead.