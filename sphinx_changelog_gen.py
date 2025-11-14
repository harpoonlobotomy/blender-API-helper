# SPDX-FileCopyrightText: 2011-2022 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# original found here: https://github.com/blender/blender/blob/main/doc/python_api/sphinx_changelog_gen.py
# Original licensed under SPDX-License-Identifier: GPL-2.0-or-later, will add appropriate documentation shortly.

## Any edits to the original made by harpoonlobotomy for the API converter project.

"""
---------------

Dump the Python API into a JSON file, or generate changelogs from those JSON API dumps.

>>  from inside D:\\Git_Repos\\blender-API-helper:
(proper working text, exactly as-is.)
python D:/Git_Repos/blender-API-helper/sphinx_changelog_gen.py -- --indexpath="D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json" changelog --filepath-in-from D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json --filepath-in-to D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json --filepath-out changes.rst

to_basename: 4.5
Found to file: 'D:/Git_Repos/blender-API-helper/api_dumps_rst_output/4.5.json'
Found from file: 'D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.1.json'
Written: 'changes.rst'

# will by default generate changeloig between the last two available versions listed in the index,
# unless input files are provided explicitly:
python doc/python_api/sphinx_changelog_gen.py -- \
        --indexpath="path/to/api/docs/api_dump_index.json" \
        changelog --filepath-in-from api_dump_3_5.json \
                  --filepath-in-to   api_dump_4_5.json \
                  --filepath-out changes.rst

--------------

API dump index format:

{[version_main, version_sub]: "<version>/api_dump.json", ...
}

API dump format:

[
    [version_main, vserion_sub, version_path],
    {"module.name":
        {"parent.class":
            {"basic_type", "member_name":
                ["Name", type, range, length, default, descr, f_args, f_arg_types, f_ret_types]}, ...
        }, ...
    }
]

"""
__all__ = (
    "generate_changelogs",
)

import json
import os

make_dict=True # make it optional in case I don't want it for some reason.
api_names = "basic_type" "name", "type", "range", "length", "default", "descr", "f_args", "f_arg_types", "f_ret_types"
API_BASIC_TYPE = 0
API_F_ARGS = 7

def compare_props(a, b, fuzz=0.75):
    # must be same basic_type, function != property
    if a[0] != b[0]:
        return False

    tot = 0
    totlen = 0
    for i in range(1, len(a)):
        if not (Ellipsis is a[i] is b[i]):
            tot += (a[i] == b[i])
            totlen += 1

    return ((tot / totlen) >= fuzz)


def api_changelog(args):
    indexpath = args.indexpath
    filepath_in_from = args.filepath_in_from
    filepath_in_to = args.filepath_in_to
    filepath_out = args.filepath_out

    rootpath = os.path.dirname(indexpath)
    json_dict_path = rootpath + "changelog.json"
    api_dict={}
    #removed all dump and index mentions - we start this function with source/targets filenames already in play.

    to_basename = float(os.path.basename(str(filepath_in_to)).rsplit(".",1)[0])
    from_basename = float(os.path.basename(str(filepath_in_from)).rsplit(".",1)[0])

    if filepath_in_to is None:
        raise ValueError("Please provide source version API dump filepath.")

    print("Found to file: %r" % filepath_in_to)

    if filepath_in_from is None:
        raise ValueError("Please provide target version API dump filepath.")

    print("Found from file: %r" % filepath_in_from)

    with open(os.path.join(rootpath, filepath_in_from), 'r', encoding='utf-8') as file_handle:
        _, dict_from = json.load(file_handle)

    with open(os.path.join(rootpath, filepath_in_to), 'r', encoding='utf-8') as file_handle:
        _, dict_to = json.load(file_handle)

    api_changes = []

    # first work out what moved
    for mod_id, mod_data in dict_to.items():
        mod_data_other = dict_from[mod_id]
        for class_id, class_data in mod_data.items():
            class_data_other = mod_data_other.get(class_id)
            if class_data_other is None:
                # TODO, document new structs
                continue

            # find the props which are not in either
            set_props_new = set(class_data.keys())
            set_props_other = set(class_data_other.keys())
            set_props_shared = set_props_new & set_props_other

            props_moved = []
            props_new = []
            props_old = []
            func_args = []

            set_props_old = set_props_other - set_props_shared
            set_props_new = set_props_new - set_props_shared

            # first find settings which have been moved old -> new
            for prop_id_old in set_props_old.copy():
                prop_data_other = class_data_other[prop_id_old]
                for prop_id_new in set_props_new.copy():
                    prop_data = class_data[prop_id_new]
                    if compare_props(prop_data_other, prop_data):
                        props_moved.append((prop_id_old, prop_id_new))

                        # remove
                        set_props_old.discard(prop_id_old)
                        set_props_new.remove(prop_id_new)

            # func args
            for prop_id in set_props_shared:
                prop_data = class_data[prop_id]
                prop_data_other = class_data_other[prop_id]
                if prop_data[API_BASIC_TYPE] == prop_data_other[API_BASIC_TYPE]:
                    if prop_data[API_BASIC_TYPE].startswith("func"):
                        args_new = prop_data[API_F_ARGS]
                        args_old = prop_data_other[API_F_ARGS]

                        if args_new != args_old:
                            func_args.append((prop_id, args_old, args_new))

            if props_moved or set_props_new or set_props_old or func_args:
                props_moved.sort()
                props_new[:] = sorted(set_props_new)
                props_old[:] = sorted(set_props_old)
                func_args.sort()

                api_changes.append((mod_id, class_id, props_moved, props_new, props_old, func_args))

    # also document function argument changes
    with open(filepath_out, 'w', encoding='utf-8') as fout:
        fw = fout.write

        # Write header.
        fw(""
           ":tocdepth: 2\n"
           "\n"
           "Change Log\n"
           "**********\n"
           "\n"
           "Changes in Blender's Python API between releases.\n"
           "\n"
           ".. note, this document is auto generated by sphinx_changelog_gen.py\n"
           "\n"
           "\n"
           "%s to %s\n"
           "============\n"
           "\n" % ("v"+str(from_basename), "v"+str(to_basename)))

        def write_title(title, title_char):
            fw("%s\n%s\n\n" % (title_char * len(title), title))

        def init_dictkey(change_type, prop_list):
            entry[change_type]=[prop_id for prop_id in prop_list]


        for mod_id, class_id, props_moved, props_new, props_old, func_args in api_changes:
            class_name = class_id.split(".")[-1]
            title = mod_id + "." + class_name
            write_title(title, "-")
            api_dict[mod_id+"."+class_id]={}
            entry=api_dict[mod_id+"."+class_id]
            if props_new:
                write_title("Added", "^")
                if make_dict:
                    init_dictkey("added", props_new)
                for prop_id in props_new:
                    fw("* :class:`%s.%s.%s`\n" % (mod_id, class_name, prop_id))
                fw("\n")

            if props_old:
                if make_dict:
                    init_dictkey("removed", props_old)
                write_title("Removed", "^")
                for prop_id in props_old:
                    fw("* **%s**\n" % prop_id)  # can't link to removed docs
                fw("\n")

            if props_moved:
                if make_dict:
                    init_dictkey("renamed", props_moved)
                write_title("Renamed", "^")
                for prop_id_old, prop_id in props_moved:
                    fw("* **%s** -> :class:`%s.%s.%s`\n" % (prop_id_old, mod_id, class_name, prop_id))
                fw("\n")

            if func_args:
                write_title("Function Arguments", "^")
                if make_dict:
                    init_dictkey("function arguments", func_args)
                for func_id, args_old, args_new in func_args:
                    args_new = ", ".join(args_new)
                    args_old = ", ".join(args_old)
                    fw("* :class:`%s.%s.%s` (%s), *was (%s)*\n" % (mod_id, class_name, func_id, args_new, args_old))
                fw("\n")
        from pprint import pprint
        pprint(api_dict)

    if make_dict:
        class JSONEncoderAPIDump(json.JSONEncoder):
            def default(self, o):
                if o is ...:
                    return "..."
                if isinstance(o, set):
                    return tuple(o)
                return json.JSONEncoder.default(self, o)
    print("Written: %r" % filepath_out)

    #if save_hardcopy:
    #    json_dict = rootpath + "changelog.json"
    #    with open(json_dict, 'w', encoding='utf-8') as file_handle:
    #        json.dump((to_basename, api_dict), file_handle, cls=JSONEncoderAPIDump)

def generate_changelogs(argv=None):
    import sys
    import argparse
    #argv = ['--', '--indexpath=D:/Git_Repos/blender-API-helper/api_dumps_rst_output/api_dump_index.json', 'changelog', ' --filepath-in-from D:\\Git_Repos\\blender-API-helper\\api_dumps_rst_output\\3.5.json', ' --filepath-in-to D:\\Git_Repos\\blender-API-helper\\api_dumps_rst_output\\4.5.json', ' --filepath-out D:/Git_Repos/blender-API-helper/api_dumps_rst_output/3.5_4.5_changes.rst']
    for i, a in enumerate(argv):
        print(i, repr(a))
    if argv is None:
        argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"
        print(f"argv recieved: {argv}")
    # When --help or no args are given, print this help
    usage_text = f"For building changelogs between specified versions of bpy API. python sphinx_changelog_gen.py -- --indexpath='api_dumps_index.json' changelog --filepath-in-from 3.1.json --filepath-in-to 4.5.json --filepath-out changes.rst"

    parser = argparse.ArgumentParser(description=usage_text,
                                     epilog=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--indexpath", dest="indexpath", metavar='FILE', required=True,
        help="Path of the JSON file containing the index of all available API dumps.")

    parser_commands = parser.add_subparsers(required=True)

    parser_dump = parser_commands.add_parser('dump', help="Dump the current Blender Python API into a JSON file.")
    parser_dump.add_argument(
        "--filepath-out", dest="filepath_out", metavar='FILE', required=True,
        help="Path of the JSON file containing the dump of the API.")

    parser_changelog = parser_commands.add_parser(
        'changelog',
        help="Generate the RST changelog page based on two Blender Python API JSON dumps.",
    )
    parser_changelog.add_argument(
        "--filepath-in-from", dest="filepath_in_from", metavar='FILE', default=None,
        help="JSON dump file to compare from (typically, previous version). "
             "If not given, will be automatically determined from current Blender version and index file.")
    parser_changelog.add_argument(
        "--filepath-in-to", dest="filepath_in_to", metavar='FILE', default=None,
        help="JSON dump file to compare to (typically, current version). "
             "If not given, will be automatically determined from current Blender version and index file.")
    parser_changelog.add_argument(
        "--filepath-out", dest="filepath_out", metavar='FILE', required=True,
        help="Output sphinx changelog RST file.")

    parser_changelog.set_defaults(func=api_changelog)

    args = parser.parse_args(argv)

    args.func(args)

if __name__ == "__main__":
    generate_changelogs()
