# html parser for Blender API changelogs
# for building a database of changes for API tool. Structure: bpy.type > version > change_type > changed_child

# harpoonLobotomy 11/2025

# todo: from this output, build a flexible lookup (to look up 'use_ambient_occlusion' and find when it was last present, what it changed to/from if changed, etc. 
#   That's kinda the whole next step, really. But I'm exhausted so it's not going to be tonight. 

# parse changelogs for 'added', 'removed', 'changed' etc per version. Output to json.

##  link for doc287:  https://docs.blender.org/api/blender_python_api_2_78c_release/change_log.html

from bs4 import BeautifulSoup
from bs4.element import Tag
import json
import os
from pprint import pprint

output_to_file = False
use_existing_file = False
print_result = True

html_doc278 = r"D:\Git_Repos\blender-api-helper\changelogs_html\2_78_0 Blender API Change Log — Blender 3c043732d3f - API documentation.html"
html_doc4 = r"D:\Git_Repos\blender-api-helper\changelogs_html\4_0 Change Log — Blender Python API.html"
# Need to switch from hardcoded html files to webscrapes I think.

filelist = [html_doc278, html_doc4]
version = 0.1

existing_data = None # placeholder def so it doesn't get cranky

def get_version_sections(soup):
    """Find version sections based on h2 headers and return list of (ver_text, section)."""
    sections = []
    seen = set()
    for h2 in soup('h2'): # 'calling a tag is like calling find_all'
        for a in h2("a", class_="headerlink"):
            a.decompose()
        ver_text = h2.get_text(strip=True)
        parent = h2.find_parent(['section', 'div']) or h2.parent
        pid = id(parent)
        if pid in seen:
            continue
        seen.add(pid)
        sections.append((ver_text, parent))
    return sections


def parse_version_section(ver_text, section):
    """Parse a version section container and return a dict of changes.

    This version avoids re-processing the same lists for multiple contexts by
    taking a *block* of nodes after each <h3> (up to the next h2/h3) and parsing
    change headers (h4) and lists only from that block. That prevents duplication
    caused by scanning the entire version container for each h3.
    """
    sectiondict = {}

    h3_tags = section.find_all('h3', recursive=False) or section.find_all('h3')

    change_type = None
    for h3 in h3_tags:
        for a in h3.find_all('a', class_='headerlink'):
            a.decompose()
        context = h3.get_text(strip=True)

        # build the sequence of sibling nodes that belong to this h3's block
        block_nodes = []
        for sib in h3.next_siblings:
            if isinstance(sib, Tag) and sib.name in ('h2', 'h3'):
                break
            # keep tags and strings (strings are ignored later)
            if isinstance(sib, Tag) or (hasattr(sib, 'strip')):
                block_nodes.append(sib)

        change_map = {}  # change_type -> list(items)

        for node in block_nodes:
            if not isinstance(node, Tag):
                continue
            # check for h4 inside the node regardless of change_type status
            inner_h4 = node.find('h4', recursive=False)
            if inner_h4:
                for a in inner_h4.find_all('a', class_='headerlink'):
                    a.decompose()
                change_type = inner_h4.get_text(strip=True)
                change_map.setdefault(change_type, [])

            # collect lists inside node (these are considered part of change_type)
            for lst in node.find_all(['ul', 'ol', 'dl']):
                # extract only list-item-level text to avoid duplicates from nested tags
                items = []
                line = []
                text=None
                if lst.name in ('ul', 'ol'):
                    for li in lst.find_all('li', recursive=False):
                        if "Function Arguments" or "Renamed" in change_type:
                            text = li.get_text(strip=True)
                            line.append(text)
                            items.append(line)
                        else:
                            text = li.get_text(separator=' ', strip=True)
                            if text:
                                items.append(text)
                else:  # dl
                    for dt in lst.find_all('dt', recursive=False):
                        text = dt.get_text(separator=' ', strip=True)
                        if text:
                            items.append(text)
                    for dd in lst.find_all('dd', recursive=False):
                        text = dd.get_text(separator=' ', strip=True)
                        if text:
                            items.append(text)

                # append new items while avoiding exact duplicates
                for it in items:
                    if type(it) == list:
                        change_map[change_type]=it # changed it to prevent needlessly nested lists.
                    else:
                        #print(f"It in items: {it}, type: {type(it)}")
                        if it not in change_map[change_type]:
                            change_map[change_type].append(it)

        # commit non-empty change_map entries to sectiondict
        for change_type, items in change_map.items():
            if items:
                ver_contents = {ver_text: {change_type: items}}
                sectiondict.setdefault(context, ver_contents)
    return sectiondict

def merge_dict(filedict, parsed):

    for k, a in parsed.items():
        test = filedict.get(k)
        if test:
            #print(f"K: {k}, A: {list(a)[0]}, test: {test}")

            if a in list(test.keys()):
                #print("This version already exists in the main dict. Skipping.")
                continue                    

            test.update(a)
            filedict[k]=test
        else:
            #print(f"New category: {k}, contents: {a}")
            filedict[k]=a

# --- Main execution ---
output_path = r"D:\Git_Repos\blender-api-helper\changelogs_output.json"
if use_existing_file:
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                print("[WARN] Existing file is not valid JSON. Starting fresh.")
                existing_data = {}

for filename in filelist:
    with open(filename, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    file = os.path.basename(filename)

    if existing_data:
        filedict = existing_data
    else:
        filedict = {}
    rev_dict = {} # 
    types = set()

    for ver_text, section in get_version_sections(soup):
        parsed = parse_version_section(ver_text, section)
        if parsed:
            filedict_new = merge_dict(filedict, parsed) # works properly. Adds additional version:data without wiping existing.
            if filedict_new:
                filedict.update(filedict_new)

if print_result:
    pprint(filedict)

if output_to_file:
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(filedict, f, indent=2)

