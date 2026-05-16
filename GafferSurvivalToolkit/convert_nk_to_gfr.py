#!/usr/bin/env python3
"""
Convert Nuke .nk demo/template files to Gaffer .gfr format.

Focuses on creating functional Gaffer equivalents rather than 1:1 node mapping.
For Expression-based procedural patterns, uses GafferImage nodes where possible.

Usage:
    python convert_nk_to_gfr.py <input.nk> <output.gfr>
"""

import re
import sys
from pathlib import Path


def parse_nk_file(content):
    """Parse a Nuke .nk file and extract nodes with properties and connections."""
    nodes = []

    # Remove boilerplate
    lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if (
            stripped.startswith("set cut_paste_input")
            or stripped.startswith("version ")
            or stripped.startswith("push ")
        ):
            continue
        lines.append(line)
    content = "\n".join(lines)

    # Parse nodes: NodeName { ... }
    node_pattern = re.compile(r"^(\w+)\s*\{", re.MULTILINE)
    matches = list(node_pattern.finditer(content))

    for i, match in enumerate(matches):
        node_type = match.group(1)
        start = match.end()

        # Find matching closing brace
        brace_count = 1
        pos = start
        while brace_count > 0 and pos < len(content):
            if content[pos] == "{":
                brace_count += 1
            elif content[pos] == "}":
                brace_count -= 1
            pos += 1

        block_content = content[start : pos - 1]

        # Parse properties
        props = {}
        for prop_line in block_content.split("\n"):
            prop_line = prop_line.strip()
            if not prop_line:
                continue
            prop_match = re.match(r"(\w+)\s+(.+)", prop_line)
            if prop_match:
                key = prop_match.group(1)
                value = prop_match.group(2).strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                props[key] = value

        # Determine input connections by "inputs" count
        try:
            input_count = int(props.get("inputs", "0"))
        except ValueError:
            input_count = 0  # Handle cases like "1+1"

        nodes.append(
            {
                "type": node_type,
                "props": props,
                "input_count": input_count,
                "index": i,
            }
        )

    return nodes


def nk_to_gaffer_node(nk_node, node_index):
    """Convert a single Nuke node to Gaffer .gfr node definition."""
    nk_type = nk_node["type"]
    props = nk_node["props"]
    node_name = props.get("name", f"{nk_type}{node_index}")

    # Skip non-functional nodes
    if nk_type in ("BackdropNode", "StickyNote", "Dot", "NoOp", "Viewer", "Output"):
        return None

    # Map node types
    gaffer_type_map = {
        "Constant": "GafferImage.Constant",
        "Grade": "GafferImage.Grade",
        "Merge2": "GafferImage.Merge",
        "Merge3": "GafferImage.Merge",
        "Blur": "GafferImage.Blur",
        "Dilate": "GafferImage.Dilate",
        "Erode": "GafferImage.Erode",
        "Median": "GafferImage.Median",
        "Clamp": "GafferImage.Clamp",
        "Crop": "GafferImage.Crop",
        "Reformat": "GafferImage.Resize",
        "Resize": "GafferImage.Resize",
        "Shuffle": "GafferImage.Shuffle",
        "CopyChannels": "GafferImage.CopyChannels",
        "DeleteChannels": "GafferImage.DeleteChannels",
        "ColorSpace": "GafferImage.ColorSpace",
        "DisplayTransform": "GafferImage.DisplayTransform",
        "VectorWarp": "GafferImage.VectorWarp",
        "ImageTransform": "GafferImage.ImageTransform",
        "Offset": "GafferImage.Offset",
        "Mirror": "GafferImage.Mirror",
        "Mix": "GafferImage.Mix",
        "ContactSheet": "GafferImage.ContactSheet",
        "DeepMerge": "GafferImage.DeepMerge",
        "DeepHoldout": "GafferImage.DeepHoldout",
        "DeepRecolor": "GafferImage.DeepRecolor",
        "DeepState": "GafferImage.DeepState",
        "DeepSlice": "GafferImage.DeepSlice",
        "DeepTidy": "GafferImage.DeepTidy",
        "DeepToFlat": "GafferImage.DeepToFlat",
        "FlatToDeep": "GafferImage.FlatToDeep",
        "ImageStats": "GafferImage.ImageStats",
        "ImageSampler": "GafferImage.ImageSampler",
        "Read": "GafferImage.ImageReader",
        "ReadGeo": "GafferScene.SceneReader",
        "ReadGeo2": "GafferScene.SceneReader",
        "Camera2": "GafferScene.Camera",
        "Camera3": "GafferScene.Camera",
        "Axis2": "GafferScene.Group",
        "Scene": "GafferScene.Group",
        "TimeWarp": "Gaffer.TimeWarp",
        "Expression": "Gaffer.Expression",
        "Multiply": "GafferImage.Grade",  # Multiply is a simplified Grade
        "Add": "GafferImage.Grade",  # Add is a simplified Grade
        "Gamma": "GafferImage.Grade",  # Gamma is a simplified Grade
        "ColorWheel": "GafferImage.Ramp",  # ColorWheel → Ramp (closest)
        "STMap": "GafferImage.VectorWarp",  # STMap → VectorWarp
        "DeepExpression": None,  # No Gaffer equivalent
    }

    gaffer_type = gaffer_type_map.get(nk_type)
    if gaffer_type is None:
        return None

    # Convert properties to Gaffer plugs
    gaffer_props = {}

    # Common property mappings
    prop_mappings = {
        # Grade
        "blackpoint": ("blackPoint", lambda v: float(v)),
        "whitepoint": ("whitePoint", lambda v: float(v)),
        "multiply": ("multiply", lambda v: parse_color4f(v)),
        "offset": ("offset", lambda v: parse_color4f(v)),
        "gamma": ("gamma", lambda v: parse_color4f(v)),
        "gain": ("gain", lambda v: parse_color4f(v)),
        "lift": ("lift", lambda v: parse_color4f(v)),
        "contrast": ("contrast", lambda v: float(v)),
        "saturation": ("saturation", lambda v: float(v)),
        # Constant
        "color": ("color", lambda v: parse_color4f(v)),
        # Blur
        "size": ("radius", lambda v: float(v)),
        # Merge
        "operation": ("operation", lambda v: merge_op_map(v)),
        "mix": ("mix", lambda v: float(v)),
        # Read/ImageReader
        "file": ("fileName", lambda v: sanitize_path(v)),
        "first": ("startFrame", lambda v: int(float(v))),
        "last": ("endFrame", lambda v: int(float(v))),
        # Clamp
        "min": ("minimum", lambda v: parse_color4f(v)),
        "max": ("maximum", lambda v: parse_color4f(v)),
        # Dilate/Erode
        "channels": ("channels", lambda v: v),
        # ColorSpace
        "colorspace": ("colorSpace", lambda v: v),
        # Reformat/Resize
        "format": ("format", lambda v: parse_format(v)),
        # Crop
        "box": ("area", lambda v: parse_box2i(v)),
        # Multiply (Nuke) → Grade (Gaffer)
        "value": ("multiply", lambda v: parse_color4f_single(v)),
    }

    for nk_prop, nk_value in props.items():
        if nk_prop in (
            "name",
            "xpos",
            "ypos",
            "selected",
            "inputs",
            "tile_color",
            "note_font_size",
            "bdwidth",
            "bdheight",
            "label",
            "disabled",
        ):
            continue

        if nk_prop in prop_mappings:
            gaffer_prop, converter = prop_mappings[nk_prop]
            try:
                gaffer_props[gaffer_prop] = converter(nk_value)
            except (ValueError, TypeError):
                pass

    # Handle Expression nodes specially
    if nk_type == "Expression":
        # Collect temp vars and expressions
        temp_vars = {}
        exprs = {}
        for i in range(10):
            tn = props.get(f"temp_name{i}")
            te = props.get(f"temp_expr{i}")
            if tn and te:
                temp_vars[tn] = te

            e = props.get(f"expr{i}")
            if e:
                exprs[i] = e

        # For Gaffer.Expression, we can only work with scalar values
        # Per-pixel expressions (using x, y, r, g, b) can't be converted
        # Store as a note for manual conversion
        if exprs:
            gaffer_props["_note"] = (
                f"Nuke Expression with per-pixel math: {list(exprs.values())}"
            )

    # Handle Multiply node (Nuke) → Grade (Gaffer)
    if nk_type == "Multiply":
        if "value" in props:
            gaffer_props["multiply"] = parse_color4f_single(props["value"])

    return {
        "type": gaffer_type,
        "name": node_name,
        "props": gaffer_props,
        "input_count": nk_node["input_count"],
        "nk_type": nk_type,
    }


def parse_color4f(value):
    """Parse Nuke color value to Gaffer Color4f."""
    value = value.strip("{}")
    parts = value.split()
    if len(parts) >= 3:
        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return f"Imath.Color4f({r}, {g}, {b}, {a})"
    elif len(parts) == 1:
        # Single value means all channels are the same
        try:
            v = float(parts[0])
            return f"Imath.Color4f({v}, {v}, {v}, {v})"
        except ValueError:
            return None
    return None


def parse_color4f_single(value):
    """Parse single float to Color4f (for Multiply node)."""
    try:
        v = float(value)
        return f"Imath.Color4f({v}, {v}, {v}, {v})"
    except ValueError:
        return None


def parse_format(value):
    """Parse Nuke format string."""
    # Format: "1920 1080 0 0 1920 1080 1 HD_1080"
    parts = value.split()
    if len(parts) >= 6:
        w, h = int(float(parts[0])), int(float(parts[1]))
        return f'Gaffer.Format({w}, {h}, 1, "{parts[-1] if len(parts) > 6 else ""}")'
    return None


def parse_box2i(value):
    """Parse Nuke box value to Imath.Box2i."""
    value = value.strip("{}")
    parts = value.split()
    if len(parts) >= 4:
        x0, y0, x1, y1 = (
            int(float(parts[0])),
            int(float(parts[1])),
            int(float(parts[2])),
            int(float(parts[3])),
        )
        return f"Imath.Box2i( Imath.V2i({x0}, {y0}), Imath.V2i({x1}, {y1}) )"
    return None


def merge_op_map(value):
    """Map Nuke merge operation to Gaffer."""
    op_map = {
        "0": "GafferImage.Merge.Operation.Over",
        "1": "GafferImage.Merge.Operation.Over",
        "2": "GafferImage.Merge.Operation.Over",
        "3": "GafferImage.Merge.Operation.Over",
        "4": "GafferImage.Merge.Operation.Over",
        "5": "GafferImage.Merge.Operation.Over",
        "6": "GafferImage.Merge.Operation.Over",
        "7": "GafferImage.Merge.Operation.Over",
        "8": "GafferImage.Merge.Operation.Over",
        "9": "GafferImage.Merge.Operation.Over",
        "10": "GafferImage.Merge.Operation.Over",
        "11": "GafferImage.Merge.Operation.Over",
    }
    return op_map.get(value, "GafferImage.Merge.Operation.Over")


def sanitize_path(value):
    """Sanitize file path, replacing with <<<replace>>> if needed."""
    if "images/" in value or "images\\" in value:
        filename = Path(value).name
        return f"<<<replace>>>/images/{filename}"
    return value


def generate_gfr(gaffer_nodes, output_name):
    """Generate .gfr file content from converted nodes."""
    if not gaffer_nodes:
        return None

    lines = []
    lines.append(f"// Converted from Nuke .nk file: {output_name}")
    lines.append(
        f"// Note: Expression-based procedural patterns may need manual conversion"
    )
    lines.append(f"// since Gaffer.Expression works on scalars, not per-pixel data.")
    lines.append("")
    lines.append("Gaffer.ScriptNode {")
    lines.append("    children : [")

    for i, node in enumerate(gaffer_nodes):
        if node is None:
            continue

        lines.append(f'        {node["type"]} "{node["name"]}" {{')
        lines.append('            "enabled" : true,')

        for prop_name, prop_value in node["props"].items():
            if prop_name.startswith("_"):
                # Add as comment
                lines.append(f"            // {prop_name}: {prop_value}")
            elif isinstance(prop_value, str) and prop_value.startswith(
                ("Imath.", "Gaffer.")
            ):
                lines.append(f'            "{prop_name}" : {prop_value},')
            elif isinstance(prop_value, bool):
                lines.append(
                    f'            "{prop_name}" : {"true" if prop_value else "false"},'
                )
            elif isinstance(prop_value, (int, float)):
                lines.append(f'            "{prop_name}" : {prop_value},')
            else:
                lines.append(f'            "{prop_name}" : "{prop_value}",')

        lines.append("        },")

    lines.append("    ],")
    lines.append("}")

    return "\n".join(lines)


def convert_nk_to_gfr(nk_content, output_name):
    """Convert Nuke .nk content to Gaffer .gfr format."""
    nodes = parse_nk_file(nk_content)
    gaffer_nodes = []

    for i, node in enumerate(nodes):
        gaffer_node = nk_to_gaffer_node(node, i)
        gaffer_nodes.append(gaffer_node)

    return generate_gfr(gaffer_nodes, output_name)


def main():
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

        with open(input_file, "r") as f:
            content = f.read()

        output_name = Path(output_file).stem
        gfr_content = convert_nk_to_gfr(content, output_name)

        if gfr_content:
            with open(output_file, "w") as f:
                f.write(gfr_content)
            print(f"Converted {Path(input_file).name} → {Path(output_file).name}")
        else:
            print(f"No convertible nodes found in {Path(input_file).name}")

    elif len(sys.argv) == 4 and sys.argv[1] == "--batch":
        nk_dir = Path(sys.argv[2])
        demo_dir = Path(sys.argv[3])
        demo_dir.mkdir(exist_ok=True)

        for nk_file in sorted(nk_dir.glob("*.nk")):
            output_file = demo_dir / f"{nk_file.stem}.gfr"

            with open(nk_file, "r") as f:
                content = f.read()

            output_name = nk_file.stem
            gfr_content = convert_nk_to_gfr(content, output_name)

            if gfr_content:
                with open(output_file, "w") as f:
                    f.write(gfr_content)
                print(f"Converted {nk_file.name} → {output_file.name}")
            else:
                print(f"Skipped {nk_file.name} (no convertible nodes)")

    else:
        print("Usage:")
        print("  python convert_nk_to_gfr.py <input.nk> <output.gfr>")
        print("  python convert_nk_to_gfr.py --batch <nk_dir> <demo_dir>")


if __name__ == "__main__":
    main()
