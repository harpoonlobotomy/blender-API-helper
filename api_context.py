#external context for the api scripts
import os

class api:

    def __init__(self):

        self.dir=None
        self.input_file=None
        self.source=None
        self.target=None
        self.forward=None
        self.betweens=None
        self.overwrite=None
        self.localpaths=None
        self.all_versions=None

def set_context(api_dir, input_file, source_version, target_version, forward_convert, betweens, overwrite, all_versions, localpaths):

    api.dir=api_dir
    api.input_file=input_file
    api.source=source_version
    api.target=target_version
    api.forward=forward_convert
    api.betweens=betweens
    api.overwrite=overwrite
    api.localpaths=localpaths
    api.all_versions=all_versions


def get_source_and_target(versions):

    source, *_, target = versions # should maybe rename so it's clearer for the times this is used for not-actually-source and/or not-actually-target. Also source/target might be flipped if we're going from more current to older api.
    return source, target

def check_is_file(filepath, version):
    if type(version) == float:
        version=[version]
    print(f"filepath: {filepath}, versions: {version}")
    print("at start of check_is_file in simple_filecheck")

    if os.path.isfile(filepath):
        f2 = str(filepath).replace("_cleaned", "")
        #print(f"f2: {f2}")
        basename = float(os.path.basename(f2).rsplit(".",1)[0]) # god this is all messy as hell but it does find both clean and raw files. Except it doesn't, because if they['re floats, the 'in' doesn't work.
        if basename in version:
            #print(f"Basename found: {basename}")
            return f2
        else:
            print(f"basename {basename} of type {type(basename)} not in versions: {version}")
            return None
    else:
        return None


def simple_filecheck(version): # only to be used after cleaning/to check for pre-cleaned files. Can be multiple version numbers, though usually it'll only be 1.

    root=api.dir + "\\cleaned_api_dumps\\"

    def run_check(root):
        from pathlib import Path
        if not os.path.exists(root):
            return None #should warn about the path not existing but I'm getting so tired.

        found_all = [str(f) for f in Path(root).iterdir() if f.is_file()] # made this str so they're not winpath obj. Might be a mistake but it keeps the list usable if pre-existing, otherwise they're all windpath objects. idk if it's better to keep them that, but this way it's consistent - whether found or created, 'cleaned' is a list of str filepaths.
        if found_all:
            print(f"found_all: {found_all}")
            for f in found_all:
                basename=check_is_file(f, version)
                if basename and basename != None:
                    api.localpaths[version]=f
                    return f

    file = run_check(root)
    return file


def get_filepath(version):


    version_file = api.localpaths.get(version)

    if not version_file:
        if  type(version) not in (str, os.PathLike):
            version_file = simple_filecheck(version)
            print(f"Target_v: {version}, type: {type(version)}")
    if not version_file:
        from get_clean_api_dumps import get_files
        version, version_file = get_files(version, clean=True) # then go through the wider process to make it. This is bad though. NEed to streamline this, a lot. Just one func for looking. Then one func for making.

    if type(version_file) == list:
        version_file=version_file[0] # apparently this still happens. Good to catch it here.
    return version_file

def get_between_vers(source_version, target_version):

    all_versions = api.all_versions

    if not api.forward:
        source_version, target_version = [target_version, source_version] # no idea if this'll work. Just need to reorder them to get the right order.

    new_versions = [v for v in all_versions if float(source_version) <= float(v) <= float(target_version)]
    print(f"New versions: {new_versions}")
    return new_versions

