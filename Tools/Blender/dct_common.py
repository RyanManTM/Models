"""
Shared helpers for the Data Centre Tycoon part models (Blender 5.0, run headless).

Everything here takes UNITY coordinates (metres, Y up, left-handed): the conversion to Blender
happens inside. Verified by probe_axes.py: a Blender point (x, y, z) arrives in Unity as (-x, z, -y).

Contract with the game (see Logs/REALISM.md):
  * Mesh objects are named "<name>#<tag>". The tag picks the game's material (see TAGS below).
    Each mesh object has exactly ONE material.
  * Interaction points are empties named "A_<KIND>_<NAME>_<INDEX>" with custom properties
    "size" ("x,y,z" metres, hitbox in the anchor's own axes) and optional "meta".
    Anchor orientation: local +Z = the direction a part or plug comes FROM (outward), local +Y = "up".
  * Moving pieces (levers, latches, switches, covers) pivot at their anchor. The FBX exporter mis-places
    objects nested under empties, so the exported hierarchy is FLAT: a piece that belongs to an anchor is
    named "<name>@<anchor>#<tag>" (anchors on moving pieces: "A_...@<anchor>"), and the game re-parents it.
  * Textures go to Assets/Resources/Models/Textures as PNG; a tag "tex_<file>" means "use that texture".
"""
import bmesh
import bpy
import math
import os
import sys
from mathutils import Matrix, Vector

# The project root is two folders above this file (Tools/Blender), so the scripts run from any checkout
# (the game, or the models-only repo on a Linux cloud machine). DCT_PROJECT overrides it.
PROJECT = os.environ.get("DCT_PROJECT") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS = os.path.join(PROJECT, "Assets", "Resources", "Models")
TEXTURES = os.path.join(MODELS, "Textures")
PREVIEWS = os.path.join(PROJECT, "Logs", "ModelPreviews")

# ---------------------------------------------------------------- fonts
# The art uses Windows fonts. Where a Windows font isn't installed (Linux), the closest Liberation or DejaVu
# font stands in; on Windows nothing changes. DCT_FONT_DIR and Tools/Blender/fonts are searched first.
WINDOWS_FONTS = r"C:\Windows\Fonts"
_SANS = ["LiberationSans-Regular.ttf", "DejaVuSans.ttf"]
_SANS_BOLD = ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
_NARROW = ["LiberationSansNarrow-Regular.ttf", "DejaVuSansCondensed.ttf"] + _SANS
_NARROW_BOLD = ["LiberationSansNarrow-Bold.ttf", "DejaVuSansCondensed-Bold.ttf"] + _SANS_BOLD
_MONO = ["LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
_MONO_BOLD = ["LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"] + _MONO
_SERIF_BOLD = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"] + _SANS_BOLD
FONT_STANDINS = {
    "arial": _SANS, "arialbd": _SANS_BOLD, "ariblk": _SANS_BOLD, "arialn": _NARROW, "arialnb": _NARROW_BOLD,
    "segoeui": _SANS, "segoeuib": _SANS_BOLD, "seguisb": _SANS_BOLD, "seguibl": _SANS_BOLD,
    "seguisym": ["DejaVuSans.ttf"] + _SANS, "calibri": _SANS, "calibrib": _SANS_BOLD,
    "consola": _MONO, "consolab": _MONO_BOLD, "ocraext": _MONO,
    "impact": _NARROW_BOLD, "agencyb": _NARROW_BOLD, "agencyr": _NARROW, "bahnschrift": _NARROW,
    "georgia": ["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"] + _SANS, "georgiab": _SERIF_BOLD,
}
_font_index = None


def _index_fonts():
    """Lower-case file name -> path for every font in the search folders (built once)."""
    global _font_index
    if _font_index is not None:
        return _font_index
    _font_index = {}
    dirs = [os.environ.get("DCT_FONT_DIR", ""), os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
            "/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts")]
    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith((".ttf", ".otf")):
                    _font_index.setdefault(f.lower(), os.path.join(root, f))
    return _font_index


def font_file(name):
    """
    The font file to load for a Windows font name or path ("arialbd.ttf", r"C:\\Windows\\Fonts\\arial.ttf"):
    the file itself where it exists (Windows), else a Linux stand-in, else None (Blender's built-in font).
    """
    if not name:
        return None
    if os.path.isfile(name):
        return name
    base = os.path.basename(name.replace("\\", "/"))
    win = os.path.join(WINDOWS_FONTS, base)
    if os.path.isfile(win):
        return win
    index = _index_fonts()
    if base.lower() in index:
        return index[base.lower()]
    stem = os.path.splitext(base)[0].lower()
    bold = stem.endswith(("bd", "b", "bl", "sb")) or "bold" in stem
    for cand in FONT_STANDINS.get(stem, _SANS_BOLD if bold else _SANS):
        if cand.lower() in index:
            return index[cand.lower()]
    return None

# Preview colours for material tags (the game uses its own materials; these only colour the previews
# and make the .fbx readable in Blender). Unknown tags preview mid grey.
TAGS = {
    "gold": (0.85, 0.65, 0.25), "copper": (0.78, 0.45, 0.25), "steel": (0.72, 0.73, 0.75),
    "steel_dark": (0.35, 0.36, 0.38), "alu": (0.8, 0.81, 0.83), "alu_dark": (0.18, 0.18, 0.2),
    "nickel": (0.75, 0.76, 0.77), "black_plastic": (0.04, 0.04, 0.045), "dark_plastic": (0.12, 0.12, 0.13),
    "grey_plastic": (0.4, 0.4, 0.42), "white_plastic": (0.9, 0.9, 0.88), "rubber": (0.06, 0.06, 0.06),
    "fan_black": (0.05, 0.05, 0.055), "paint_black": (0.06, 0.06, 0.065), "paint_white": (0.88, 0.88, 0.86),
    "glass": (0.2, 0.25, 0.28), "mesh_black": (0.08, 0.08, 0.08), "thermal_pad": (0.55, 0.6, 0.65),
    "paste": (0.62, 0.63, 0.65), "film_blue": (0.25, 0.55, 0.95), "cardboard": (0.62, 0.47, 0.3),
    "foam": (0.08, 0.08, 0.09), "connector_black": (0.06, 0.06, 0.06), "connector_white": (0.92, 0.91, 0.86),
    "connector_beige": (0.86, 0.8, 0.66), "pcb_green": (0.05, 0.24, 0.12), "pcb_black": (0.03, 0.035, 0.04),
    "solder": (0.75, 0.75, 0.73), "ceramic": (0.8, 0.75, 0.62), "chip_black": (0.04, 0.04, 0.045),
    "led_red": (1.0, 0.15, 0.1), "led_yellow": (1.0, 0.8, 0.1), "led_white": (1.0, 1.0, 1.0),
    "led_green": (0.2, 1.0, 0.3), "led_blue": (0.3, 0.6, 1.0), "rgb": (0.5, 0.5, 1.0),
}

DEG = math.pi / 180.0


# ---------------------------------------------------------------- coordinates

def conv(v):
    """Unity position or direction -> Blender."""
    return Vector((-v[0], -v[2], v[1]))


def dims(s):
    """Unity axis-aligned size -> Blender size."""
    return Vector((abs(s[0]), abs(s[2]), abs(s[1])))


def basis(forward=(0, 0, 1), up=(0, 1, 0)):
    """Blender 3x3 rotation whose Unity-local axes are: +Z = forward, +Y = up."""
    f = Vector(forward).normalized()
    u = Vector(up).normalized()
    r = u.cross(f)  # Unity right = up x forward (component-wise formula)
    if r.length < 1e-6:
        raise ValueError("forward and up are parallel")
    r.normalize()
    u = f.cross(r).normalized()
    bx = -conv(r)
    by = -conv(f)
    bz = conv(u)
    m = Matrix((bx, by, bz)).transposed()
    return m


# ---------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(TEXTURES, exist_ok=True)
    os.makedirs(PREVIEWS, exist_ok=True)


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def empty(name, pos=(0, 0, 0), parent=None, forward=(0, 0, 1), up=(0, 1, 0)):
    e = link(bpy.data.objects.new(name, None))
    e.empty_display_size = 0.01
    set_xform(e, pos, forward, up)
    if parent is not None:
        set_parent(e, parent)
    return e


def root(name):
    """The model's root: an empty at the origin. Export everything under it."""
    return empty(name)


def set_xform(obj, pos, forward=(0, 0, 1), up=(0, 1, 0)):
    obj.matrix_world = Matrix.Translation(conv(pos)) @ basis(forward, up).to_4x4()


def set_parent(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


# ---------------------------------------------------------------- materials

def mat(tag):
    m = bpy.data.materials.get(tag)
    if m is None:
        m = bpy.data.materials.new(tag)
        base = tag
        if tag.startswith("tex_"):
            col = (0.7, 0.7, 0.7)
        else:
            col = TAGS.get(base, (0.5, 0.5, 0.5))
        m.diffuse_color = (col[0], col[1], col[2], 1.0)
        m.metallic = 0.8 if tag in ("gold", "copper", "steel", "alu", "nickel", "solder") else 0.0
        m.roughness = 0.35
    return m


def finish(obj, name, tag, parent=None, smooth_angle=None):
    obj.name = f"{name}#{tag}"
    obj.data.name = obj.name
    obj.data.materials.clear()
    obj.data.materials.append(mat(tag))
    if smooth_angle is not None:
        obj.data.shade_smooth()
        obj.data.set_sharp_from_angle(angle=smooth_angle * DEG)
    else:
        obj.data.shade_flat()
    if parent is not None:
        attach(obj, parent, name, tag)
    return obj


def top_of(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj


def attach(obj, parent, name=None, tag=None):
    """Parents obj. The FBX exporter mis-places objects nested under empties, so the exported hierarchy
    stays flat: anything 'under' an anchor is parented to the model root and named '<name>@<anchor>',
    and the game re-parents it to that anchor on load (keeping its world pose)."""
    if parent.type == "EMPTY" and parent.name.startswith("A_"):
        base = name if name is not None else obj.name.split("#", 1)[0].split("@", 1)[0]
        suffix = ("#" + tag) if tag is not None else ("#" + obj.name.split("#", 1)[1] if "#" in obj.name else "")
        obj.name = f"{base}@{parent.name}{suffix}"
        if obj.data is not None:
            obj.data.name = obj.name
        set_parent(obj, top_of(parent))
    else:
        set_parent(obj, parent)


def mesh_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


# ---------------------------------------------------------------- primitives (Unity coordinates)

def box(name, center, size, tag, parent=None, bevel=0.0, segments=2, forward=(0, 0, 1), up=(0, 1, 0)):
    """An axis-aligned (in its own frame) box. size is in the box's own Unity axes. bevel in metres."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    d = dims(size)
    bmesh.ops.scale(bm, vec=d, verts=bm.verts)
    if bevel > 0:
        b = min(bevel, min(d) * 0.49)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=segments, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
    obj = mesh_object(name, bm)
    set_xform(obj, center, forward, up)
    return finish(obj, name, tag, parent, smooth_angle=35 if bevel > 0 else None)


def cyl(name, center, radius, height, tag, axis="y", parent=None, verts=32, bevel=0.0, segments=2,
        radius2=None, cap=True):
    """A cylinder (or cone if radius2) centred at center, its length along a Unity axis ('x', 'y', 'z')."""
    bm = bmesh.new()
    r2 = radius if radius2 is None else radius2
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts, radius1=radius, radius2=r2,
                          depth=height)
    if bevel > 0 and cap:
        rim = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6 and abs(e.verts[0].co.z) > height * 0.49]
        bmesh.ops.bevel(bm, geom=rim, offset=min(bevel, radius * 0.4, height * 0.45), segments=segments,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    obj = mesh_object(name, bm)
    fwd, up = {"y": ((0, 0, 1), (0, 1, 0)), "x": ((0, 0, 1), (1, 0, 0)), "z": ((0, 1, 0), (0, 0, 1))}[axis]
    # Blender cone axis is local Z; our frame maps Unity +Y (up) to Blender local Z.
    set_xform(obj, center, fwd, up)
    return finish(obj, name, tag, parent, smooth_angle=40)


def from_profile(name, points2d, depth, tag, center=(0, 0, 0), parent=None, forward=(0, 0, 1), up=(0, 1, 0),
                 bevel=0.0):
    """Extrudes a 2D outline (list of (x, y) in the frame's Unity x/y) by depth along the frame's Unity z."""
    bm = bmesh.new()
    vs = [bm.verts.new((-p[0], 0.0, p[1])) for p in points2d]  # Unity x->-Bx, Unity y->Bz, depth along -By
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, -depth, 0)), verts=moved)
    bmesh.ops.translate(bm, vec=Vector((0, depth * 0.5, 0)), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
    obj = mesh_object(name, bm)
    set_xform(obj, center, forward, up)
    return finish(obj, name, tag, parent, smooth_angle=35 if bevel > 0 else None)


def tube(name, points, radius, tag, parent=None, verts=12):
    """A round tube through Unity-space points (heat pipes, cables)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = max(1, verts // 4)
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        c = conv(p)
        sp.points[i].co = (c.x, c.y, c.z, 1.0)
    obj = link(bpy.data.objects.new(name, cu))
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    return finish(obj, name, tag, parent, smooth_angle=60)


# ---------------------------------------------------------------- anchors

def anchor(name, pos, size=(0.01, 0.01, 0.01), parent=None, forward=(0, 0, 1), up=(0, 1, 0), meta=None):
    """An interaction point: A_<KIND>_<NAME>_<INDEX>. size = hitbox in the anchor's own Unity axes."""
    if not name.startswith("A_"):
        raise ValueError("anchor names start with A_: " + name)
    e = empty(name, pos, None, forward, up)
    e["size"] = f"{abs(size[0]):.5f},{abs(size[1]):.5f},{abs(size[2]):.5f}"
    if meta:
        e["meta"] = meta
    if parent is not None:
        if parent.type == "EMPTY" and parent.name.startswith("A_"):
            # An anchor on a moving piece (a thumbscrew on the side panel): flat export, linked by name.
            e.name = f"{name}@{parent.name}"
            set_parent(e, top_of(parent))
        else:
            set_parent(e, parent)
    return e


# ---------------------------------------------------------------- tidy up

def join_by_tag(parent, prefix, keep=()):
    """Joins every direct mesh child of parent that shares a tag into one object per tag.
    Objects listed in keep (or with children) stay separate (moving pieces)."""
    groups = {}
    for ob in list(parent.children):
        if ob.type != "MESH" or ob in keep or ob.children or "@" in ob.name:
            continue  # moving pieces (linked to an anchor with '@') stay separate
        tag = ob.name.split("#", 1)[1] if "#" in ob.name else "untagged"
        groups.setdefault(tag, []).append(ob)
    for tag, obs in groups.items():
        if len(obs) == 1:
            obs[0].name = f"{prefix}_{tag}#{tag}"
            continue
        for o in bpy.context.selected_objects:
            o.select_set(False)
        for o in obs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.object.join()
        j = bpy.context.active_object
        j.name = f"{prefix}_{tag}#{tag}"
        j.data.name = j.name


def descendants(obj):
    out = [obj]
    for c in obj.children:
        out.extend(descendants(c))
    return out


def export(root_obj, filename):
    """Exports root_obj and everything under it to Assets/Resources/Models/<filename>.fbx."""
    path = os.path.join(MODELS, filename + ".fbx")
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in descendants(root_obj):
        o.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"EMPTY", "MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
        bake_space_transform=True, use_custom_props=True, mesh_smooth_type="FACE", add_leaf_bones=False,
        use_mesh_modifiers=True, use_tspace=False)
    print("EXPORTED", path)
    return path


# ---------------------------------------------------------------- previews and artwork

def preview(root_obj, filename, views=((35, 30), (-40, 55)), size=(960, 720), dist=None):
    """Renders preview PNGs (Workbench, material colours) to Logs/ModelPreviews/<filename>_<i>.png.
    views are (yaw, pitch) in degrees around the model's bounds centre, in Unity terms."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_cavity = True
    sc.display.shading.show_shadows = True
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("w")
    pts = []
    for o in descendants(root_obj):
        if o.type == "MESH":
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return []
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) * 0.5
    radius = (hi - lo).length * 0.5
    cam_data = bpy.data.cameras.new("preview_cam")
    cam_data.lens = 50
    cam_data.clip_start = 0.001
    cam_data.clip_end = 100
    cam = link(bpy.data.objects.new("preview_cam", cam_data))
    sc.camera = cam
    out = []
    for i, (yaw, pitch) in enumerate(views):
        d = (dist or radius * 3.2)
        y, p = yaw * DEG, pitch * DEG
        # Unity-space direction from the centre to the camera (yaw around Y from +Z, pitch up)
        u = Vector((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        cam.location = centre + conv(u) * d
        direction = centre - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(PREVIEWS, f"{filename}_{i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    bpy.data.objects.remove(cam)
    return out


def args():
    """Command-line arguments after '--'."""
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
