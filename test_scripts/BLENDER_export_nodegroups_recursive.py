# written for Blender 4.3
# harpoonLobotomy, 10/10/25

import bpy
import os
import json
from collections import defaultdict

output_path = "test_ng_recursive_2.json"
overwrite_keys = True
test_print = False
ignore_frames = True
selected_only = True
recursion = True

discovered_nodegroups = []

def nodegroup_to_json(nodegroup_node, discovered_nodegroups):
    new_discovered_nodegroups = []
    data = {}
    node_index = {}
    temp_name = nodegroup_node.name
    nodegroup = nodegroup_node.node_tree
    temp_name = nodegroup.name
    name = temp_name.split(".")[0]
    print(f"Starting node {name} in nodegroup_to_json")
    data["color"] = nodegroup.color_tag

    group_in_node = next((n for n in nodegroup.nodes if n.type == 'GROUP_INPUT'), None)
    group_out_node = next((n for n in nodegroup.nodes if n.type == 'GROUP_OUTPUT'), None)

    sockets = {"inputs": {}, "outputs": {}}
  
    for i, sock in enumerate(nodegroup_node.inputs):
        default_vals = None
        if sock.name == "":
            continue
        else:
            if not sock.is_linked:
                if sock.default_value:
                    print(f"socket default values from the outside: {sock.default_value}")
                if not sockets["inputs"]:
                    sockets["inputs"] = {}
                val = sock.default_value
                if val is not None:
                    print(f"Sockname: `{sock.name}`  Val: `{val}` type: `{type(val)}`")
                if isinstance(val, (int, float)):
                    default_vals = float(val)
                elif hasattr(val, "__iter__") and not isinstance(val, str):
                    default_vals = list(val)
                else:
                    default_vals = val
            idx = {
                "socket_name": sock.name,
                "socket_type": sock.bl_idname,     
            }
            if default_vals:
                print("Default vals: ", default_vals)
                idx.update({"default_values": default_vals})
            sockets["inputs"][i] = idx

    if group_out_node:
        for i, sock in enumerate(group_out_node.inputs):
            if sock.name == "":
                continue
            else:
                if not sockets["outputs"]:
                    sockets["outputs"] = {}
                idx = {
                    "socket_name": sock.name,
                    "socket_type": sock.bl_idname
                }
                sockets["outputs"][i] = idx

    data["sockets"] = sockets
    type_counters = defaultdict(int)  
    
    nodes_data = []
    for node in nodegroup.nodes:
        name = None
        
        if node.bl_idname == "NodeFrame":
            pass
        else:
            node_type = node.bl_idname
            print("Node name, node_type: ", node.name, node_type)
            if node.hide:
                node_entry["autohide"] = node.hide
                
            if node.bl_idname == "NodeReroute":
                node_entry["reroute_type"] = node.socket_idname

            if node.bl_idname == "ShaderNodeGroup":
                temp_name = node.node_tree.name
                short_name = temp_name.split(".")[0]
                if short_name not in discovered_nodegroups:
                    print(f"Internal nodegroup not seen before: {short_name}")
                    new_discovered_nodegroups.append(node)  
            else:
                short_name = node_type.removeprefix("ShaderNode")

            count = type_counters[short_name]
            if count == 0:
                new_name = short_name
            else:
                new_name = f"{short_name}.{count:03d}"

            node_entry = {
                "name": short_name,
                "type": node.bl_idname,
                "location": [round(node.location.x / 10) * 10, round(node.location.y / 10) * 10]
            }

            type_counters[short_name] += 1

            if new_name == "NodeGroupInput":
                new_name = "GroupInput"
            if new_name == "NodeGroupOutput":
                new_name = "GroupOutput"               

            node_entry["name"] = new_name
            node_index[node] = new_name

            if hasattr(node, "operation"):
                node_entry["operation"] = node.operation
            if hasattr(node, "blend_type"):
                node_entry["blend_type"] = node.blend_type
            if hasattr(node, "data_type"):
                node_entry["data_type"] = node.data_type

            # Default values
            default_vals = {}
            for inp in node.inputs:
                if not inp.is_linked and hasattr(inp, "default_value") and not inp.is_unavailable and "Rotation" not in inp.identifier:
                    val = inp.default_value
                    if val:
                        print(f"Val: {val} type: {type(val)}")
                    if isinstance(val, (int, float)):
                        default_vals[inp.identifier] = float(val)
                    elif hasattr(val, "__iter__") and not isinstance(val, str):
                        default_vals[inp.identifier] = list(val)
                    else:
                        default_vals = val

            if default_vals:
                node_entry["default_values"] = default_vals
            nodes_data.append(node_entry)

    data["nodes"] = nodes_data

    # Links
    links_data = []
    for link in nodegroup.links:
        from_node_name = link.from_node.name if link.from_node else "Group Input"
        to_node_name = link.to_node.name if link.to_node else "Group Output"
        from_node_type = link.from_node.bl_idname if link.from_node else "Group Input"
        to_node_type = link.to_node.bl_idname if link.to_node else "Group Output"
        
        if link.from_node.bl_idname == "ShaderNodeGroup":
            from_node_name = node_index[link.from_node]
            from_socket_id = link.from_socket.name    
        elif from_node_name == "Group Input":
            from_socket_id = link.from_socket.name
            from_node_name = "GroupInput"
        else:
            from_socket_id = link.from_socket.identifier
            from_node_name = node_index[link.from_node]
        
        if link.to_node.bl_idname == "ShaderNodeGroup":
            to_node_name = node_index[link.to_node]
            to_socket_id = link.to_socket.name     
        elif to_node_name == "Group Output":
            to_socket_id = link.to_socket.name
            to_node_name = "GroupOutput"
        else:
            to_socket_id = link.to_socket.identifier
            to_node_name = node_index[link.to_node]
        
        from_node_name = from_node_name.replace(" ","")
        to_node_name = to_node_name.replace(" ","")

        links_data.append([
            from_node_name,
            from_socket_id,
            to_node_name,
            to_socket_id
        ])

    data["links"] = links_data

    return data, new_discovered_nodegroups

def serialize_value(val, indent=0):
    ind = '  ' * indent
    if isinstance(val, dict):
        lines = []
        lines.append("{")
        n = len(val)
        for i, (k, v) in enumerate(val.items()):
            comma = "," if i < n - 1 else ""
            lines.append(f'{ind}    "{k}": {serialize_value(v, indent + 1)}{comma}')
        lines.append(ind + "}")
        return "\n".join(lines)
    elif isinstance(val, (list, tuple)):
        if len(val) <= 4 and all(isinstance(x, (int, float)) for x in val):
            return "[" + ", ".join(str(round(x)) if isinstance(x, float) else str(x) for x in val) + "]"
        lines = ["["]
        n = len(val)
        for i, item in enumerate(val):
            comma = "," if i < n - 1 else ""
            if isinstance(item, (list, tuple)) and len(item) <= 4 and all(isinstance(x, (int, float, str)) for x in item):
                item_str = "[" + ", ".join(f'"{x}"' if isinstance(x, str) else str(x) for x in item) + "]"
                lines.append(f'{ind}    {item_str}{comma}')
            else:
                lines.append(f'{ind}    {serialize_value(item, indent + 1)}{comma}')
        lines.append(ind + "]")
        return "\n".join(lines)

    elif isinstance(val, str):
        return f'"{val}"'
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif val is None:
        return "null"
    else:
        return str(val)

def export_frame_groups_custom(discovered_nodegroups):
    obj = bpy.context.object
    mat = obj.active_material
    if not mat:
        print("No active object or material found.")
        return

    nodes = mat.node_tree.nodes

    none_selected = True
    for node in nodes:
        if node.select == True:
            none_selected = False
            break

    if selected_only == True and not none_selected == True:
            nodegroups = [n for n in nodes if n.type == 'GROUP' and n.select == True]
            print("Processing selected nodegroups")
    else:
        nodegroups = [n for n in nodes if n.type == 'GROUP']
        print("Processing all nodegroups in active material.")
        
    new_output = {}
    existing_data = {}
        
    if test_print:
        pass
    else:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("[WARN] Existing file is not valid JSON. Starting fresh.")
                    
 # Step 2: Build new entries
    for nodegroup in nodegroups:
        temp_name = nodegroup.name
        discovered_nodegroups.append(temp_name.split(".", 1)[0])

    for nodegroup in nodegroups:
        print()
        nodegroup_name = nodegroup.name
        temp_name = nodegroup.name
        group_name = temp_name.split(".", 1)[0]
        print("Key nodegroup: ", nodegroup_name)
        print()
        group_data, new_discovered_nodegroups = nodegroup_to_json(nodegroup, discovered_nodegroups)
        
        group_data["nodes"] = [
            node for node in group_data["nodes"]
            if node["name"] not in ("GROUP_INPUT", "GROUP_OUTPUT", "GroupInput", "GroupOutput")
        ]

        new_output[group_name] = group_data

        counter = 0
        while new_discovered_nodegroups and counter <= 50:
            for nodegroup in new_discovered_nodegroups:
                temp_name = nodegroup.name
                group_name = temp_name.split(".", 1)[0]
                discovered_nodegroups.append(group_name)
                print("nodegroup in new_discovered_nodegroups: ", nodegroup)
                counter += 1
                group_data, new_discovered_nodegroups = nodegroup_to_json(nodegroup, discovered_nodegroups)
                group_data["nodes"] = [
                        node for node in group_data["nodes"]
                        if node["name"] not in ("GROUP_INPUT", "GROUP_OUTPUT", "GroupInput", "GroupOutput")
                    ]
                new_output[group_name] = group_data
                print(counter)

    existing_data.update(new_output)

    full_serialized = "{\n"
    items = list(existing_data.items())
    for i, (key, val) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        full_serialized += f'  "{key}": {serialize_value(val, 1)}{comma}\n'
    full_serialized += "}\n"

    if test_print:
        print(full_serialized)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_serialized)

        print(f"[Info] Wrote {len(new_output)} new group(s) to JSON at '{output_path}'")

export_frame_groups_custom(discovered_nodegroups)
