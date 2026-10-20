"""
extras_common.py - shared helpers for build_extras.py (agent C: papers, part caps, guards and stickers).

Built on dct_common and parts_b (neither is changed). Everything takes UNITY coordinates (metres, +Y up,
left-handed), like dct_common; parts_b.Model / MB do the conversion and the face winding.

What is here:
  * oriented(verts, face, want)  - winds a face so its normal (Unity numbers) points along `want`.
  * Sheet                        - a geometry collector with one builder per tag, for hand-made faces with UVs.
  * import_part(pid)             - imports Assets/Resources/Models/<pid>.fbx into the scene (for fit checks and
                                   previews only; the part is never exported from here).
  * place(root, pos, fwd, up)    - moves a finished model's root (and everything under it) to a pose in the
                                   part's frame, after export, to check the fit.
  * fit_check(root, part_objs)   - BVH triangle-overlap test and the smallest gap between a cap and the part.
  * preview(...)                 - EEVEE renders with the game-like look of every tag (clear plastic is
                                   transparent, tex_ tags show their PNGs, doc_cover/doc_back show test pages).
  * bounds(root), tri_count(root), report(model, extra_lines).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector as V
from mathutils.bvhtree import BVHTree

import dct_common as c
import parts_b as pb

DEG = math.pi / 180.0

# Preview look of the tags (the game uses its own URP materials; these only make the previews honest).
# tag: (sRGB colour, alpha, metallic, roughness)
LOOK = {
    "clear_plastic": ((0.86, 0.91, 0.96), 0.16, 0.0, 0.04),
    "paper_white": ((0.94, 0.94, 0.92), 1.0, 0.0, 0.75),
    "rubber": ((0.035, 0.035, 0.037), 1.0, 0.0, 0.62),
    "steel": ((0.74, 0.75, 0.77), 1.0, 1.0, 0.28),
    "doc_cover": ((1.0, 1.0, 1.0), 1.0, 0.0, 0.55),
    "doc_back": ((1.0, 1.0, 1.0), 1.0, 0.0, 0.6),
}
# preview-only images for doc_cover / doc_back (set by the doc builders; never exported)
DOC_IMAGES = {}


# ====================================================================== geometry

def newell(pts):
    n = V((0.0, 0.0, 0.0))
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def oriented(verts, face, want):
    """Returns the face's index list wound so that its normal (Unity numbers, right-hand rule) points along want."""
    n = newell([verts[i] for i in face])
    if n.dot(V(want)) < 0:
        return list(reversed(face))
    return list(face)


class Sheet:
    """Collects hand-built faces per tag: add(tag, [p0, p1, ...], want_normal, uvs=None). Each face keeps its own
    vertices (flat shading), which suits thin paper, film and stickers. flush(model) adds everything to a
    parts_b.Model (static) or to an anchor's moving piece."""

    def __init__(self):
        self.g = {}

    def add(self, tag, pts, want, uvs=None, smooth=False):
        verts, faces, uvl, flags = self.g.setdefault(tag, ([], [], [], []))
        base = len(verts)
        pts = [V(p) for p in pts]
        verts.extend(pts)
        idx = list(range(base, base + len(pts)))
        f = oriented(verts, idx, want)
        faces.append(f)
        if uvs is not None:
            if f != idx:
                uvs = list(reversed(uvs))
            uvl.append([tuple(u) for u in uvs])
        else:
            uvl.append(None)
        flags.append(smooth)

    def quad(self, tag, a, b, cc, d, want, uvs=None, smooth=False):
        self.add(tag, [a, b, cc, d], want, uvs, smooth)

    def geo(self, tag):
        verts, faces, uvl, flags = self.g[tag]
        uvs = uvl if any(u is not None for u in uvl) else None
        if uvs is not None:
            # faces without UVs get their first corner's UV of (0, 0) - only happens for mixed builders
            uvs = [u if u is not None else [(0.0, 0.0)] * len(faces[i]) for i, u in enumerate(uvl)]
        return verts, faces, uvs, flags

    def flush(self, model, anchor=None, name="piece"):
        for tag in self.g:
            if anchor is None:
                model.mb(tag).add(self.geo(tag))
            else:
                model.piece(anchor, tag, name).add(self.geo(tag))
        self.g = {}


def grid_strip(sheet, tag, rows, want_fn, uv_fn=None, smooth=False):
    """rows: list of point lists (same length): quads between consecutive rows and columns.
    want_fn(i, j) -> wanted normal for the quad (i = row, j = column); uv_fn(i, j) -> uv of the corner."""
    for i in range(len(rows) - 1):
        for j in range(len(rows[i]) - 1):
            pts = [rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]]
            uvs = None
            if uv_fn is not None:
                uvs = [uv_fn(i, j), uv_fn(i, j + 1), uv_fn(i + 1, j + 1), uv_fn(i + 1, j)]
            sheet.add(tag, pts, want_fn(i, j), uvs, smooth)


# ====================================================================== scene helpers

def bounds(root):
    """Unity-space bounds (lo, hi) of every mesh under root."""
    pts = []
    for o in c.descendants(root):
        if o.type == "MESH":
            mw = o.matrix_world
            pts += [pb.to_unity(mw @ v.co) for v in o.data.vertices]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def tri_count(root):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in c.descendants(root) if o.type == "MESH")


def import_part(pid):
    """Imports a part FBX (Assets/Resources/Models/<pid>.fbx) into the scene; returns its objects.
    Only for previews and fit checks: nothing imported here is ever exported."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(c.MODELS, pid + ".fbx"), use_custom_props=True)
    objs = [o for o in bpy.data.objects if o not in before]
    for o in objs:
        o["dct_imported"] = 1
    return objs


def place(root, pos, forward, up):
    """Moves a model root (children follow) to a pose given in Unity terms."""
    c.set_xform(root, pos, forward, up)
    bpy.context.view_layer.update()


def _bvh(obj):
    """BVH of a mesh in world space, from Blender's own triangulation (concave n-gons with holes stay right)."""
    me = obj.data
    me.calc_loop_triangles()
    mw = obj.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    tris = [tuple(t.vertices) for t in me.loop_triangles]
    return BVHTree.FromPolygons(verts, tris, epsilon=0.0), verts


def _samples(obj, step=0.0015):
    """Points spread over a mesh's faces (world space): every vertex plus a barycentric grid on each triangle."""
    me = obj.data
    me.calc_loop_triangles()
    mw = obj.matrix_world
    vs = [mw @ v.co for v in me.vertices]
    pts = list(vs)
    for t in me.loop_triangles:
        a, b, cc = (vs[i] for i in t.vertices)
        n = max(1, min(24, int(max((b - a).length, (cc - b).length, (a - cc).length) / step)))
        for i in range(n + 1):
            for j in range(n + 1 - i):
                if (i, j) in ((0, 0), (n, 0), (0, n)):
                    continue
                pts.append(a + (b - a) * (i / n) + (cc - a) * (j / n))
    return pts


def _near_bounds(obj, lo, hi, pad):
    mw = obj.matrix_world
    pts = [mw @ V(cc) for cc in obj.bound_box]
    for k in range(3):
        if max(p[k] for p in pts) < lo[k] - pad or min(p[k] for p in pts) > hi[k] + pad:
            return False
    return True


def fit_check(root, part_objs, near=0.004):
    """Checks a placed cap against the part: triangle overlaps per part mesh and the smallest gap between the
    cap's surfaces (sampled every 1.5 mm) and the part's surfaces (within `near` metres).
    Returns (overlaps, min_gap, nearest_mesh)."""
    caps = [o for o in c.descendants(root) if o.type == "MESH"]
    cpts = []
    for o in caps:
        cpts += [o.matrix_world @ v.co for v in o.data.vertices]
    lo = V((min(p.x for p in cpts), min(p.y for p in cpts), min(p.z for p in cpts)))
    hi = V((max(p.x for p in cpts), max(p.y for p in cpts), max(p.z for p in cpts)))
    parts = [o for o in part_objs if o.type == "MESH" and _near_bounds(o, lo, hi, near)]
    trees = [(o, _bvh(o)[0]) for o in parts]
    overlaps = {}
    gap, gap_mesh = 1e9, None
    for cobj in caps:
        ct, _ = _bvh(cobj)
        samples = _samples(cobj)
        for (pobj, pt) in trees:
            pairs = ct.overlap(pt)
            if pairs:
                overlaps[(cobj.name, pobj.name)] = len(pairs)
            for v in samples:
                hit = pt.find_nearest(v, near)
                if hit[0] is not None and hit[3] < gap:
                    gap, gap_mesh = hit[3], pobj.name
    return overlaps, gap, gap_mesh


# ====================================================================== previews

def _lin(col):
    return tuple(pb.srgb_to_lin(x) for x in col)


def _setup_material(m):
    tag = m.name.split(".")[0] if m.name[-4:-3] == "." and m.name[-3:].isdigit() else m.name
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    if nt is None:
        return
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None) or nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(b.outputs[0], out.inputs["Surface"])
    for l in list(b.inputs["Base Color"].links):
        nt.links.remove(l)
    img = None
    met, rough, alpha = 0.0, 0.5, 1.0
    if tag in DOC_IMAGES:
        img = DOC_IMAGES[tag]
        col, alpha, met, rough = LOOK[tag]
    elif tag.startswith("tex_"):
        path = os.path.join(c.TEXTURES, tag[4:] + ".png")
        if os.path.exists(path):
            img = bpy.data.images.load(path, check_existing=True)
        try:
            import parts_pcb as pp
            met, rough = pp.PREVIEW_TEX.get(tag[4:], (0.0, 0.45))
        except Exception:
            met, rough = 0.0, 0.45
    elif tag in LOOK:
        col, alpha, met, rough = LOOK[tag]
        b.inputs["Base Color"].default_value = _lin(col) + (1.0,)
    else:
        col = c.TAGS.get(tag, (0.5, 0.5, 0.5))
        b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
        try:
            import parts_pcb as pp
            met, rough = pp.PREVIEW_PBR.get(tag, (0.8, 0.3) if tag in ("gold", "copper", "steel", "alu", "nickel",
                                                                         "solder") else (0.0, 0.5))
        except Exception:
            pass
        if tag.startswith("led_"):
            met, rough = 0.0, 0.2
    if img is not None:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = img
        tn.interpolation = "Cubic"
        nt.links.new(tn.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = met
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        try:
            b.inputs["Specular IOR Level"].default_value = 0.8
            b.inputs["Coat Weight"].default_value = 0.4
        except Exception:
            pass
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
        try:
            m.use_transparency_overlap = True
        except Exception:
            pass
    m.diffuse_color = (m.diffuse_color[0], m.diffuse_color[1], m.diffuse_color[2], alpha)


def _world(sc):
    w = bpy.data.worlds.get("extras_world") or bpy.data.worlds.new("extras_world")
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    hdri = os.path.join(os.path.dirname(bpy.app.binary_path), "%d.%d" % bpy.app.version[:2], "datafiles",
                        "studiolights", "world", "interior.exr")
    if os.path.exists(hdri):
        env.image = bpy.data.images.load(hdri, check_existing=True)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    plain = nt.nodes.new("ShaderNodeBackground")
    plain.inputs["Color"].default_value = (0.05, 0.052, 0.056, 1.0)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(plain.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def table(size=0.6, y=0.0, tag="extras_table", col=(0.33, 0.27, 0.21)):
    """A matte table top under the model (preview only), its top at Unity height y."""
    me = bpy.data.meshes.new(tag)
    s = size / 2
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    o = c.link(bpy.data.objects.new(tag, me))
    o.location = c.conv((0, y, 0))
    m = bpy.data.materials.new(tag)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = 0.8
    me.materials.append(m)
    o["dct_preview_only"] = 1
    return o


def preview(name, views, size=(1200, 900)):
    """EEVEE renders to Logs/ModelPreviews/<name>_<i>.png. views: dicts with target (Unity point), yaw, pitch
    (degrees: yaw about +Y from +Z, pitch up), dist (m), optional lens (mm), up ('y' or a Unity vector) and
    index (the <i>); or dir (a Unity vector from the target to the camera) instead of yaw/pitch. Every material in the scene gets its preview look first."""
    sc = bpy.context.scene
    for m in bpy.data.materials:
        if m.name not in ("extras_table",):
            _setup_material(m)
    _world(sc)
    sc.render.engine = "BLENDER_EEVEE"
    for attr, val in (("use_raytracing", True), ("taa_render_samples", 48), ("use_shadows", True)):
        try:
            setattr(sc.eevee, attr, val)
        except Exception:
            pass
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sun_d = bpy.data.lights.new("extras_sun", "SUN")
    sun_d.energy = 2.2
    sun_d.angle = 10 * DEG
    sun = c.link(bpy.data.objects.new("extras_sun", sun_d))
    sun.rotation_euler = (38 * DEG, 12 * DEG, 30 * DEG)
    cd = bpy.data.cameras.new("extras_cam")
    cd.clip_start = 0.0005
    cd.clip_end = 50
    cam = c.link(bpy.data.objects.new("extras_cam", cd))
    sc.camera = cam
    out = []
    for k, v in enumerate(views):
        cd.lens = v.get("lens", 50)
        tgt = c.conv(v["target"])
        if "dir" in v:
            u = V(v["dir"]).normalized()
        else:
            y, p = v.get("yaw", 30) * DEG, v.get("pitch", 30) * DEG
            u = V((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        upv = c.conv(v.get("up", (0, 1, 0)))
        loc = tgt + c.conv(u) * v.get("dist", 0.3)
        fwd = (tgt - loc).normalized()
        right = fwd.cross(upv)
        if right.length < 1e-6:
            right = fwd.cross(c.conv((0, 0, 1)))
        right.normalize()
        upc = right.cross(fwd).normalized()
        m4 = Matrix((right, upc, -fwd)).transposed().to_4x4()
        m4.translation = loc
        cam.matrix_world = m4
        if "roll" in v:
            cam.rotation_euler.rotate_axis("Z", v["roll"] * DEG)
        path = os.path.join(c.PREVIEWS, f"{name}_{v.get('index', k)}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)
    return out


# ====================================================================== report

def anchor_lines(root):
    lines = []
    for e in sorted([o for o in c.descendants(root) if o.type == "EMPTY" and o.name.startswith("A_")],
                    key=lambda o: o.name):
        p, f, u = pb.unity_pose(e)
        lines.append(f"   {e.name}: pos=({p.x:.4f},{p.y:.4f},{p.z:.4f}) fwd=({f.x:.2f},{f.y:.2f},{f.z:.2f}) "
                     f"up=({u.x:.2f},{u.y:.2f},{u.z:.2f}) size={e.get('size')} meta={e.get('meta', '')}")
    return lines


def report(model, extra=()):
    """The parts_b report block (meshes, triangles, anchors) plus the bounds and any extra lines."""
    root = model.root
    lines = [f"== {model.id}"]
    total = 0
    objs = [o for o in c.descendants(root) if o.type == "MESH"]
    for o in sorted(objs, key=lambda o: o.name):
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        total += t
        lines.append(f"   mesh {o.name}: {t} tris")
    lines.append(f"   TOTAL {total} tris in {len(objs)} meshes")
    lo, hi = bounds(root)
    lines.append(f"   bounds lo=({lo.x:.4f},{lo.y:.4f},{lo.z:.4f}) hi=({hi.x:.4f},{hi.y:.4f},{hi.z:.4f}) "
                 f"size=({hi.x - lo.x:.4f},{hi.y - lo.y:.4f},{hi.z - lo.z:.4f})")
    lines += anchor_lines(root)
    lines += ["   " + x for x in extra]
    return "\n".join(lines)


def triangulate(root):
    """Triangulates every mesh under root in place (beauty; UVs and flat/smooth flags kept), so the export carries
    exactly the triangles the fit checks saw (bevelled slabs with holes are concave n-gons otherwise)."""
    import bmesh
    for o in c.descendants(root):
        if o.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()


def validate(root):
    """Names under Blender's 63-character limit with '#<tag>' intact and exactly one material."""
    bad = []
    for o in c.descendants(root):
        if o.type == "MESH":
            tag = o.name.split("#", 1)[1] if "#" in o.name else None
            if tag is None or len(o.name) >= 63 or len(o.data.materials) != 1 or o.data.materials[0].name != tag:
                bad.append(o.name)
        elif o.type == "EMPTY" and len(o.name) >= 63:
            bad.append(o.name)
    if bad:
        raise RuntimeError(f"{root.name}: bad object names/materials {bad}")
    return True
