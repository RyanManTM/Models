"""
shipping_lib: shared helpers for build_shipping.py (Blender agent A: shipping cartons, filler, crumples, small bits,
the unboxing table, the wheelie bin, bin bags and the paperwork tray; see Logs/UNBOXING.md section 2.3).

Built on dct_common (Unity coordinates, anchors, export), parts_b (the per-tag mesh builder MB / build_mesh and its
g_* primitives) and parts_c (2D artwork, PNG I/O, Cycles helpers). It changes none of them.

  * Kit: one model. Static geometry is accumulated per tag (one object per tag, named <id>_<tag>#<tag>); moving
    pieces per (anchor, name, tag) -> '<name>@<anchor>#<tag>' with the pivot on the anchor; named statics (e.g.
    'tapelook#tape_brown') keep their own name.
  * Faces are wound by the right-hand rule in Unity numbers (normal = (b - a) x (c - a) points OUT), as parts_b.
  * Preview materials for the new tags of UNBOXING.md 2.1 (kraft_paper, tape_brown, bag_clear, bubble_wrap, ...).
  * render(): Cycles previews on a light floor (studio HDRI + key and rim lights), so the shapes read.
  * Report blocks in the format of the existing *_report.txt files, merged into one shipping_report.txt.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as B  # noqa: E402
import parts_c as P  # noqa: E402

V = Vector
DEG = math.pi / 180.0
TAU = 2.0 * math.pi
REPORT = os.path.join(c.PREVIEWS, "shipping_report.txt")
ART_TMP = os.path.join(__import__("tempfile").gettempdir(), "dct_shipping_art")   # intermediate artwork layers

# Workbench preview colours of the new tags (the game has its own materials).
NEW_TAGS = {
    "kraft_paper": (0.58, 0.42, 0.26), "tape_brown": (0.55, 0.36, 0.16), "tape_clear": (0.85, 0.86, 0.86),
    "bag_clear": (0.86, 0.89, 0.92), "bubble_wrap": (0.80, 0.87, 0.92), "film_clear": (0.88, 0.90, 0.92),
    "paper_white": (0.92, 0.92, 0.90), "fabric_black": (0.05, 0.05, 0.055), "velcro_black": (0.035, 0.035, 0.04),
    "eps_foam": (0.95, 0.95, 0.94), "clear_plastic": (0.8, 0.85, 0.9), "smoke_plastic": (0.25, 0.26, 0.28),
}


def setup_tags():
    c.TAGS.update(NEW_TAGS)


# ====================================================================== the model kit

class Kit(B.Model):
    """parts_b.Model with named statics and per-tag smoothing, and no join step (one builder per tag already)."""

    def __init__(self, mid):
        super().__init__(mid)
        P._names.clear()
        P._fonts.clear()
        setup_tags()
        self.named = {}

    def named_mb(self, name, tag):
        return self.named.setdefault((name, tag), B.MB())

    def finish(self, smooth=35.0, smooth_by_tag=None):
        sb = smooth_by_tag or {}
        objs = []
        for tag, mb in self.static.items():
            if mb.f:
                objs.append(B.build_mesh(mb, f"{self.id}_{tag}", tag, self.root, sb.get(tag, smooth)))
        for (nm, tag), mb in self.named.items():
            if mb.f:
                objs.append(B.build_mesh(mb, nm, tag, self.root, sb.get(tag, smooth)))
        for (aname, nm, tag), (a, mb) in self.pieces.items():
            if mb.f:
                objs.append(B.build_mesh(mb, nm, tag, a, sb.get(tag, smooth)))
        for o in objs:
            if len(o.name) > 63 or "." in o.name.split("#", 1)[-1]:
                print("WARNING bad object name", o.name)
        return objs


# ====================================================================== geometry helpers (Unity space)

def geo_quad(pts, uvs=None, normal=None, smooth=False):
    """One polygon; reversed if its right-hand normal disagrees with 'normal'."""
    pts = [V(p) for p in pts]
    if normal is not None:
        n = B._newell(pts)
        if n.dot(V(normal)) < 0:
            pts = pts[::-1]
            uvs = uvs[::-1] if uvs is not None else None
    return pts, [list(range(len(pts)))], ([list(uvs)] if uvs is not None else None), [smooth]


def add_quad(mb, pts, uvs=None, normal=None, smooth=False):
    mb.add(geo_quad(pts, uvs, normal, smooth))


def grid_surface(fn, nu, nv, closed_u=False, uv_fn=None, smooth=True, flip=False):
    """A surface from fn(u, v) -> point (u, v in 0..1). Normal = d/du x d/dv (flip reverses).
    uv_fn(u, v) -> (s, t) gives explicit UVs."""
    cols = nu if closed_u else nu + 1
    verts = []
    for j in range(nv + 1):
        for i in range(cols):
            verts.append(V(fn(i / nu, j / nv)))
    faces, uvs = [], []
    for j in range(nv):
        for i in range(nu):
            i1 = (i + 1) % cols if closed_u else i + 1
            f = [j * cols + i, j * cols + i1, (j + 1) * cols + i1, (j + 1) * cols + i]
            if uv_fn is not None:
                uu = [uv_fn(i / nu, j / nv), uv_fn((i + 1) / nu, j / nv), uv_fn((i + 1) / nu, (j + 1) / nv),
                      uv_fn(i / nu, (j + 1) / nv)]
            else:
                uu = None
            if flip:
                f = f[::-1]
                uu = uu[::-1] if uu else None
            faces.append(f)
            uvs.append(uu)
    return verts, faces, (uvs if uv_fn is not None else None), [smooth] * len(faces)


def facing(geo, direction):
    """Flips every face of geo whose normal points against 'direction' (a vector or a function of the face
    centre returning one)."""
    verts, faces = geo[0], geo[1]
    uvs = geo[2]
    nf, nu = [], []
    for i, f in enumerate(faces):
        pts = [V(verts[k]) for k in f]
        n = B._newell(pts)
        ctr = sum(pts, V()) / len(pts)
        d = V(direction(ctr)) if callable(direction) else V(direction)
        if n.dot(d) < 0:
            nf.append(f[::-1])
            nu.append(uvs[i][::-1] if uvs is not None and uvs[i] is not None else None)
        else:
            nf.append(f)
            nu.append(uvs[i] if uvs is not None else None)
    return (verts, nf, nu if uvs is not None else None) + tuple(geo[3:])


def sweep_profile(path, profile, closed_path=False, up=None, caps=True, smooth=True, twist=None, scale=None):
    """Sweeps a closed 2D cross-section (list of (x, y), CCW) along a path of Unity points.
    The section's x follows the path's side vector, y its normal ('up' guides the first normal).
    twist(t) -> extra roll in radians, scale(t) -> (sx, sy) for t in 0..1."""
    Pp = [V(p) for p in path]
    m = len(Pp)
    T = []
    for i in range(m):
        if closed_path:
            a = Pp[(i + 1) % m] - Pp[i - 1]
        else:
            a = Pp[min(i + 1, m - 1)] - Pp[max(i - 1, 0)]
        T.append(a.normalized())
    ref = V(up) if up is not None else (V((0, 1, 0)) if abs(T[0].y) < 0.9 else V((1, 0, 0)))
    N = (ref - T[0] * ref.dot(T[0])).normalized()
    frames = []
    for i in range(m):
        if i > 0:
            q = T[i - 1].rotation_difference(T[i])
            N = q @ N
            N = (N - T[i] * N.dot(T[i])).normalized()
        Bv = T[i].cross(N).normalized()
        frames.append((N.copy(), Bv))
    n = len(profile)
    verts, faces = [], []
    for i in range(m):
        t = i / max(1, m - 1)
        Nn, Bb = frames[i]
        if twist is not None:
            a = twist(t)
            ca, sa = math.cos(a), math.sin(a)
            Nn, Bb = Nn * ca + Bb * sa, Bb * ca - Nn * sa
        sx, sy = scale(t) if scale is not None else (1.0, 1.0)
        for (x, y) in profile:
            verts.append(Pp[i] + Bb * (x * sx) + Nn * (y * sy))
    segs = m if closed_path else m - 1
    for i in range(segs):
        i1 = (i + 1) % m
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, i1 * n + j1, i1 * n + j])
    flags = [smooth] * len(faces)
    if caps and not closed_path:
        faces.append([j for j in reversed(range(n))])
        faces.append([(m - 1) * n + j for j in range(n)])
        flags += [False, False]
    # make the side faces point out of the tube (the profile winding decides): test one face
    if faces:
        f0 = faces[0]
        nrm = B._newell([verts[k] for k in f0])
        ctr = sum((verts[k] for k in f0), V()) / len(f0)
        if nrm.dot(ctr - Pp[0]) < 0:
            faces = [f[::-1] for f in faces]
    return verts, faces, None, flags


def smooth_path(points, n=6):
    return P.smooth_path(points, n)


def displace(geo, fn):
    """New geometry with every vertex moved: fn(p) -> new point."""
    verts = [V(fn(V(p))) for p in geo[0]]
    return (verts,) + tuple(geo[1:])


def vertex_normals(verts, faces):
    acc = [V((0, 0, 0)) for _ in verts]
    for f in faces:
        n = B._newell([verts[k] for k in f])
        for k in f:
            acc[k] += n
    return [a.normalized() if a.length > 1e-12 else V((0, 1, 0)) for a in acc]


def icosphere(subdiv=3):
    """Unit icosphere (verts, faces) with outward winding."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    bm.verts.index_update()
    verts = [V((v.co.x, v.co.y, v.co.z)) for v in bm.verts]
    faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    # Blender's winding is right-handed in its own numbers; the coordinates are used as Unity numbers here (a
    # rotation of a sphere is still a sphere), so keep the winding whose normal points out.
    out = []
    for f in faces:
        n = B._newell([verts[k] for k in f])
        ctr = sum((verts[k] for k in f), V()) / len(f)
        out.append(f if n.dot(ctr) > 0 else f[::-1])
    return verts, out


def decimate_obj(obj, ratio):
    """Applies a collapse decimation to a finished object (keeps its name, tag and UVs)."""
    if ratio >= 0.999:
        return obj
    md = obj.modifiers.new("dec", "DECIMATE")
    md.ratio = ratio
    md.use_collapse_triangulate = True
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = obj.data
    obj.modifiers.remove(md)
    me.name = old.name
    obj.data = me
    bpy.data.meshes.remove(old)
    return obj


# ====================================================================== noise

def fbm(p, octaves=4, lac=2.0, gain=0.5, seed=0.0):
    s, a, f = 0.0, 1.0, 1.0
    o = V((seed * 17.31, seed * 3.7, seed * 11.13))
    for _ in range(octaves):
        s += a * noise.noise(p * f + o)
        a *= gain
        f *= lac
    return s


def ridged(p, octaves=3, seed=0.0):
    """Sharp creases: 1 - |noise| summed."""
    s, a, f = 0.0, 1.0, 1.0
    o = V((seed * 5.1, seed * 9.7, seed * 2.3))
    for _ in range(octaves):
        s += a * (1.0 - abs(noise.noise(p * f + o)))
        a *= 0.5
        f *= 2.1
    return s


def cell_crease(p, seed=0.0):
    """Facet look: distance to the second-nearest Voronoi site minus the nearest (0 on cell borders)."""
    d, _ = noise.voronoi(p + V((seed * 3.3, seed * 1.7, seed * 7.9)), distance_metric="DISTANCE", exponent=2.5)
    return d[1] - d[0]


# ====================================================================== preview materials (Cycles stand-ins)

def _film_material(name, tint=(0.95, 0.96, 0.98), haze=0.06, rough=0.12, facing=0.55, base=0.06):
    """A thin clear film: transparent + glossy by a Schlick-like facing ratio (back faces get the base value),
    a little milky haze."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (*tint, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = rough
    gl.inputs["Color"].default_value = (1, 1, 1, 1)
    df = nt.nodes.new("ShaderNodeBsdfDiffuse")
    df.inputs["Color"].default_value = (*tint, 1)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 4.0
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    mt = nt.nodes.new("ShaderNodeMath")
    mt.operation = "MULTIPLY_ADD"
    mt.inputs[1].default_value = facing
    mt.inputs[2].default_value = base
    mt.use_clamp = True
    nt.links.new(pw.outputs[0], mt.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sel = nt.nodes.new("ShaderNodeMix")
    sel.data_type = "FLOAT"
    nt.links.new(geo.outputs["Backfacing"], sel.inputs["Factor"])
    nt.links.new(mt.outputs[0], sel.inputs["A"])
    sel.inputs["B"].default_value = base
    mx0 = nt.nodes.new("ShaderNodeMixShader")
    mx0.inputs["Fac"].default_value = haze
    nt.links.new(tr.outputs[0], mx0.inputs[1])
    nt.links.new(df.outputs[0], mx0.inputs[2])
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(sel.outputs["Result"], mx.inputs["Fac"])
    nt.links.new(mx0.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def _principled(name, col, rough, metal=0.0, bump=0.0, bump_scale=600.0, alpha=1.0, coat=0.0, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*col, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        bs.inputs["Alpha"].default_value = alpha
    if coat > 0:
        try:
            bs.inputs["Coat Weight"].default_value = coat
            bs.inputs["Coat Roughness"].default_value = 0.08
        except KeyError:
            pass
    if sss > 0:
        try:
            bs.inputs["Subsurface Weight"].default_value = sss
            bs.inputs["Subsurface Radius"].default_value = (0.004, 0.003, 0.002)
        except KeyError:
            pass
    if bump > 0:
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = bump_scale
        nz.inputs["Detail"].default_value = 6.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
    return m


def preview_materials():
    """Creates 'pbr_<tag>' for the new tags (parts_c.pbr_material returns an existing one by name)."""
    defs = {
        "kraft_paper": lambda n: _principled(n, (0.30, 0.185, 0.085), 0.8, bump=0.25, bump_scale=900.0),
        "tape_brown": lambda n: _principled(n, (0.42, 0.20, 0.06), 0.18, alpha=0.9, coat=0.4),
        "tape_clear": lambda n: _film_material(n, (0.97, 0.96, 0.92), 0.05),
        "bag_clear": lambda n: _film_material(n, (0.96, 0.97, 0.98), 0.06, 0.10, 0.6, 0.05),
        "bubble_wrap": lambda n: _film_material(n, (0.93, 0.96, 0.99), 0.08, 0.06, 0.6, 0.06),
        "film_clear": lambda n: _film_material(n, (0.96, 0.97, 0.98), 0.07, 0.08, 0.6, 0.05),
        "paper_white": lambda n: _principled(n, (0.80, 0.80, 0.78), 0.75, bump=0.1, bump_scale=1500.0, sss=0.1),
        "fabric_black": lambda n: _principled(n, (0.022, 0.022, 0.025), 0.92, bump=0.35, bump_scale=2500.0),
        "velcro_black": lambda n: _principled(n, (0.018, 0.018, 0.02), 0.97, bump=0.5, bump_scale=3000.0),
        "eps_foam": lambda n: _principled(n, (0.85, 0.85, 0.84), 0.9, bump=0.2, bump_scale=400.0),
        "black_plastic": lambda n: _principled(n, (0.016, 0.016, 0.018), 0.35, coat=0.0),
        "white_plastic": lambda n: _principled(n, (0.78, 0.78, 0.76), 0.45, bump=0.04, bump_scale=800.0),
    }
    for tag, fn in defs.items():
        nm = "pbr_" + tag
        if bpy.data.materials.get(nm) is None:
            fn(nm)


# ====================================================================== previews

def culled(m):
    """A copy of a preview material whose back faces are fully transparent (Unity culls back faces), so a flipped
    face shows up as a hole in the preview, as it would in the game."""
    name = "cull_" + m.name
    cm = bpy.data.materials.get(name)
    if cm is not None:
        return cm
    cm = m.copy()
    cm.name = name
    nt = cm.node_tree
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    if not out.inputs["Surface"].links:
        return cm
    src = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mx.inputs["Fac"])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return cm


def _bounds_of(objs):
    pts = []
    for o in objs:
        if o.type == "MESH" and not o.hide_render:
            pts += [o.matrix_world @ V(cc) for cc in o.bound_box]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def render(root, mid, views, size=(1100, 850), samples=48, lens=50, start=0, floor=True, target=None, dist=None,
           fill=1.0, hide=(), floor_col=(0.42, 0.42, 0.41), key=1.0, below=False):
    """Cycles previews with PBR stand-ins on a floor. views: (yaw, pitch) degrees (Unity terms, yaw 0 = from +z)
    or dicts {yaw, pitch, dist, target, lens}. Writes Logs/ModelPreviews/<mid>_<start + i>.png."""
    if not P.PREVIEW[0]:
        return []
    sc = bpy.context.scene
    preview_materials()
    P._gpu_cycles(sc, samples)
    sc.cycles.samples = samples
    sc.cycles.transparent_max_bounces = 128   # culled back faces are transparent: no bounce limit, like a rasteriser
    P._setup_world(sc, strength=0.75, bg=(0.23, 0.23, 0.235))
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    objs = [o for o in c.descendants(root) if o.type == "MESH"]
    mine = set(objs)
    hidden = []
    for o in sc.objects:
        if o.type in ("MESH", "CURVE", "FONT") and o not in mine and not o.hide_render:
            o.hide_render = True
            hidden.append(o)
    for o in objs:
        tag = P._tag_of(o.name)
        o.data.materials.clear()
        o.data.materials.append(culled(P.pbr_material(tag, False)))
        if any(h in o.name for h in hide):
            o.hide_render = True
            hidden.append(o)
    lo, hi = _bounds_of(objs)
    centre = (lo + hi) * 0.5 if target is None else c.conv(target)
    radius = max(0.02, (hi - lo).length * 0.5)
    tmp = []
    if floor:
        fm = bpy.data.meshes.new("pv_floor")
        s = max(40.0, radius * 200)
        z0 = lo.z - 0.0002
        fm.from_pydata([(-s, -s, z0), (s, -s, z0), (s, s, z0), (-s, s, z0)], [], [(0, 1, 2, 3)])
        fo = c.link(bpy.data.objects.new("pv_floor", fm))
        mat = bpy.data.materials.new("pv_floor_mat")
        mat.use_nodes = True
        bs = mat.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value = (*floor_col, 1)
        bs.inputs["Roughness"].default_value = 0.65
        fm.materials.append(mat)
        tmp.append(fo)
    camd = bpy.data.cameras.new("pv_cam")
    camd.clip_start = 0.002
    camd.clip_end = 100
    cam = c.link(bpy.data.objects.new("pv_cam", camd))
    sc.camera = cam
    tmp.append(cam)
    for nm, energy, loc, sz in (("key", 70.0 * key, (1.3, -1.2, 2.2), 1.0), ("rim", 45.0, (-1.6, 1.4, 1.3), 0.8),
                                ("fill", 14.0, (-1.5, -1.6, 0.6), 1.4)):
        ld = bpy.data.lights.new("pv_" + nm, "AREA")
        ld.energy = energy * max(0.05, radius) ** 2 * 4
        ld.size = max(0.15, radius * sz)
        lo_ = c.link(bpy.data.objects.new("pv_" + nm, ld))
        lv = V(loc)
        if below:
            lv.z = -lv.z
        lo_.location = centre + lv * max(0.3, radius * 2.5)
        lo_.rotation_euler = (centre - lo_.location).to_track_quat("-Z", "Y").to_euler()
        tmp.append(lo_)
    out = []
    for i, v in enumerate(views):
        if not isinstance(v, dict):
            v = {"yaw": v[0], "pitch": v[1]}
        camd.lens = v.get("lens", lens)
        fov = 2 * math.atan(18.0 / camd.lens)
        tgt = c.conv(v["target"]) if "target" in v else centre
        d = v.get("dist", dist) or (radius / math.sin(fov / 2)) * 1.08 / v.get("fill", fill)
        y, p = v["yaw"] * DEG, v["pitch"] * DEG
        u = V((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        cam.location = tgt + c.conv(u) * d
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(c.PREVIEWS, f"{mid}_{start + i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    for o in tmp:
        data = o.data
        bpy.data.objects.remove(o)
    for o in hidden:
        o.hide_render = False
    return out


def pose_pieces(root, poses):
    """Rotates moving pieces (and the anchors linked to them) about their anchor's local axis, for previews only.
    poses: {anchor_name: (axis 'x'|'y'|'z', degrees)} (Unity rotation, as the game's localRotation)."""
    anchors = {o.name: o for o in c.descendants(root) if o.type == "EMPTY" and o.name.startswith("A_")}
    C = Matrix(((-1, 0, 0), (0, 0, -1), (0, 1, 0)))
    for aname, (axis, deg) in poses.items():
        a = anchors.get(aname)
        if a is None:
            continue
        fr = P.anchor_frame(a)
        ax = {"x": fr.u, "y": fr.v, "z": fr.w}[axis]
        Ru = Matrix.Rotation(deg * DEG, 3, ax)
        Mb = (C @ Ru @ C.inverted()).to_4x4()
        pb = c.conv(fr.o)
        M = Matrix.Translation(pb) @ Mb @ Matrix.Translation(-pb)
        for o in c.descendants(root):
            if o is a:
                continue
            nm = o.name.split("#", 1)[0]
            if "@" in nm and nm.split("@", 1)[1].split("@", 1)[0] == aname:
                o.matrix_world = M @ o.matrix_world


def workbench(root, mid, views, size=(900, 700), start=0, folder=None):
    """Quick Workbench views with the textures shown (for checking UVs)."""
    B.preview_textures()
    out = B.shots(root, mid, [dict(yaw=v[0], pitch=v[1]) if not isinstance(v, dict) else v for v in views],
                  size=size, first=start)
    if folder:
        moved = []
        os.makedirs(folder, exist_ok=True)
        for pth in out:
            dst = os.path.join(folder, os.path.basename(pth))
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(pth, dst)
            moved.append(dst)
        return moved
    return out


# ====================================================================== report

def report_block(root, mid, notes=None):
    """The text of parts_c.write_report (same format as the other *_report.txt files)."""
    tris, meshes = P.stats(root)
    lines = [f"{mid}: {tris} triangles, {meshes} meshes"]
    for o in sorted(c.descendants(root), key=lambda x: x.name):
        if o.type == "MESH":
            lines.append(f"  mesh {o.name}  tris={sum(len(p.vertices) - 2 for p in o.data.polygons)}")
    for n, p, fw, up, s, m in P.anchor_report(root):
        lines.append(f"  {n} pos={p} fwd={fw} up={up} size={s} meta={m}")
    if notes:
        for ln in notes if isinstance(notes, (list, tuple)) else [notes]:
            lines.append(ln)
    return tris, meshes, "\n".join(lines)


def merge_report(blocks, order):
    """Writes shipping_report.txt: rebuilt blocks replace their old ones, other models' blocks are kept."""
    old = {}
    if os.path.exists(REPORT):
        cur, buf = None, []
        with open(REPORT, encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                if ln and not ln.startswith(" ") and ": " in ln and "triangles" in ln:
                    if cur:
                        old[cur] = "\n".join(buf).rstrip()
                    cur = ln.split(":", 1)[0]
                    buf = [ln]
                elif cur:
                    buf.append(ln)
            if cur:
                old[cur] = "\n".join(buf).rstrip()
    old.update(blocks)
    keys = [k for k in order if k in old] + sorted(k for k in old if k not in order)
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n\n".join(old[k] for k in keys) + "\n")
    print("REPORT", REPORT, len(keys), "models")


# ====================================================================== artwork helpers

def art_layer(w, h, name, draw):
    """Renders a transparent artwork layer with parts_c.Art (draw(art) adds the elements) and returns it as a
    float RGBA numpy array (rows bottom to top)."""
    os.makedirs(ART_TMP, exist_ok=True)
    art = P.Art(w, h, bg=None, name=name)
    draw(art)
    path = art.render(name, ART_TMP)
    art.dispose()
    return P.load_png(path)


def blur_fft(a, sx, sy=None):
    """Gaussian blur of a 2D array (wraps around), sigma in pixels along x (columns) and y (rows)."""
    import numpy as np
    sy = sx if sy is None else sy
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (math.pi ** 2) * ((fx * sx) ** 2 + (fy * sy) ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def noise_field(h, w, sigma, seed, sy=None):
    import numpy as np
    rng = np.random.default_rng(seed)
    a = blur_fft(rng.normal(0, 1, (h, w)).astype(np.float32), sigma, sy)
    a /= max(1e-6, a.std())
    return a.astype(np.float32)


def text_on_arc(art, s, cx, cy, r, size, col, font, start_deg, clockwise=True, inward=False, spacing=1.05):
    """Characters along a circle: clockwise from start_deg with the glyphs' tops outward (inward=False), or
    counter-clockwise with the tops inward (text along the bottom of a seal)."""
    widths = [max(art.text_width(ch, size, font), size * 0.32) * spacing for ch in s]
    total = sum(widths)
    ang = start_deg * DEG
    sign = -1.0 if clockwise else 1.0
    # centre the text on start_deg
    ang -= sign * (total / r) / 2
    for ch, wd in zip(s, widths):
        a = ang + sign * (wd / 2) / r
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        rot = a - math.pi / 2 if not inward else a + math.pi / 2
        if ch.strip():
            art.text(ch, x, y, size, col, font, align="CENTER", rot=rot)
        ang += sign * wd / r


def seeded(seed):
    return random.Random(P.shash(seed))


def finish_model(kit, mid, notes=None):
    """Exports <mid>.fbx and returns its report block."""
    c.export(kit.root, mid)
    tris, meshes, block = report_block(kit.root, mid, notes)
    print(f"BUILT {mid}: {tris} tris, {meshes} meshes")
    return block
