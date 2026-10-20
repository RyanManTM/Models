"""
parts_b.py - modelling helpers for the graphics cards, power supplies, CPU coolers and fans
(build_gpu.py, build_psu.py, build_cooler.py, parts_fan.py). Built on dct_common; does not change it.

Everything takes UNITY coordinates (metres, +Y up, left-handed), like dct_common.

Geometry is accumulated per material tag in a MeshBuilder (MB) and turned into ONE object per tag at the end
(Model.finish), so a part ends up with one renderer per tag plus its moving pieces, and building thousands of
fins or pins stays fast.

Conventions:
  * Local geometry is a tuple (verts, faces, uvs): verts are Vectors, faces lists of vertex indices wound by the
    right-hand rule so the normal points OUT (in Unity numbers), uvs None or one list of (u, v) per face corner.
  * MB.add(geo, M, t) places local geometry: Unity point = M @ local + t. M is a 3x3 matrix whose columns are
    the local x, y, z axes in Unity space: frame(forward, up) (a rotation, like dct_common's anchors) or
    label_frame(normal, up) (columns: reading-right, up, normal; a mirror, used for text and labels).
  * The Unity->Blender conversion is a mirror, so build_mesh() reverses every face. Unity culls back faces, so
    the previews here render with back-face culling ON: a hole in a preview means a flipped face.
  * Plain-tag meshes get box-projected UVs, 1 UV unit = 0.1 m, so the game can tile brushed metal, powder
    coat and similar detail textures at a real-world scale. tex_ meshes carry their own 0..1 UVs.
"""
import bmesh
import bpy
import math
import os
import random
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

import dct_common as c

V = Vector
DEG = math.pi / 180.0
TAU = 2.0 * math.pi
UV_METRES = 0.1  # box-projected UVs: one UV unit per 0.1 m

FONT_DIR = r"C:\Windows\Fonts"
FONTS = {
    "arial": "arial.ttf", "arialb": "arialbd.ttf", "black": "ariblk.ttf", "narrow": "ARIALN.TTF",
    "narrowb": "ARIALNB.TTF", "agency": "AGENCYB.TTF", "agency_r": "AGENCYR.TTF", "franklin": "FRAHV.TTF",
    "franklin_cn": "FRADMCN.TTF", "franklin_md": "FRAMDCN.TTF", "eras": "ERASBD.TTF", "eras_md": "ERASDEMI.TTF",
    "gothic": "GOTHICB.TTF", "mono": "consolab.ttf", "segoe": "segoeuib.ttf", "segoe_r": "segoeui.ttf",
    "segoe_black": "seguibl.ttf", "segoe_sb": "seguisb.ttf", "tw": "TCCEB.TTF", "copper": "COPRGTB.TTF",
    "ocr": "OCRAEXT.TTF", "impact": "impact.ttf", "tahoma": "tahomabd.ttf", "verdana": "verdanab.ttf",
}


# ====================================================================== math

def frame(forward=(0, 0, 1), up=(0, 1, 0)):
    """Rotation whose local +Z is forward and +Y is up (columns: right, up, forward), like dct_common.basis."""
    f = V(forward).normalized()
    u = V(up).normalized()
    r = u.cross(f)
    if r.length < 1e-9:
        raise ValueError("forward and up are parallel")
    r.normalize()
    u = f.cross(r).normalized()
    return Matrix((r, u, f)).transposed()


def label_frame(normal, up):
    """Columns (reading-right, up, normal) for something you read (text, a label) facing 'normal' with its top
    towards 'up'. A mirror (det -1); MB.add handles the winding."""
    n = V(normal).normalized()
    u = V(up)
    u = (u - n * u.dot(n)).normalized()
    r = n.cross(u).normalized()
    return Matrix((r, u, n)).transposed()


def rot(axis, angle):
    """Rotation about a Unity axis ('x', 'y', 'z' or a vector) by angle radians (right-hand rule in numbers)."""
    if isinstance(axis, str):
        axis = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    return Matrix.Rotation(angle, 3, V(axis))


def lerp(a, b, t):
    return a + (b - a) * t


def to_unity(b):
    """Blender point/direction -> Unity (inverse of c.conv)."""
    return V((-b[0], b[2], -b[1]))


def unity_pose(obj):
    """(position, forward, up) of a Blender object in Unity terms."""
    m = obj.matrix_world
    return to_unity(m.translation), -to_unity(m.col[1].xyz).normalized(), to_unity(m.col[2].xyz).normalized()


def is_anchor(obj):
    return obj is not None and obj.type == "EMPTY" and obj.name.startswith("A_")


def area2(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i][0], poly[i][1]
        x1, y1 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        a += x0 * y1 - x1 * y0
    return a * 0.5


# ====================================================================== 2D shapes (lists of (x, y))

def circle2(cx, cy, r, n=32, a0=0.0):
    return [(cx + r * math.cos(a0 + TAU * i / n), cy + r * math.sin(a0 + TAU * i / n)) for i in range(n)]


def rect2(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def rrect2(cx, cy, w, h, r, n=4):
    """Rounded rectangle (corner radius r, n segments per corner)."""
    r = min(r, w * 0.5 - 1e-6, h * 0.5 - 1e-6)
    if r <= 1e-7:
        return rect2(cx, cy, w, h)
    pts = []
    corners = [(cx + w / 2 - r, cy - h / 2 + r, -90), (cx + w / 2 - r, cy + h / 2 - r, 0),
               (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180)]
    for (x, y, a) in corners:
        for k in range(n + 1):
            t = (a + 90.0 * k / n) * DEG
            pts.append((x + r * math.cos(t), y + r * math.sin(t)))
    return pts


def chamfer2(cx, cy, w, h, ch):
    """Rectangle with 45 degree chamfered corners; ch may be one value or (bl, br, tr, tl)."""
    if not isinstance(ch, (tuple, list)):
        ch = (ch, ch, ch, ch)
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    bl, br, tr, tl = ch
    pts = []
    pts += [(x0, y0 + bl), (x0 + bl, y0)] if bl > 0 else [(x0, y0)]
    pts += [(x1 - br, y0), (x1, y0 + br)] if br > 0 else [(x1, y0)]
    pts += [(x1, y1 - tr), (x1 - tr, y1)] if tr > 0 else [(x1, y1)]
    pts += [(x0 + tl, y1), (x0, y1 - tl)] if tl > 0 else [(x0, y1)]
    return pts


def hexagon2(cx, cy, r, a0=0.0):
    return circle2(cx, cy, r, 6, a0)


def fillet_path(pts, radius, segs=6):
    """A 3D polyline with its inner corners rounded (heat pipes, wires). pts: Unity points."""
    P = [V(p) for p in pts]
    if len(P) < 3:
        return P
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, cc = P[i - 1], P[i], P[i + 1]
        d0 = (a - b)
        d1 = (cc - b)
        l0, l1 = d0.length, d1.length
        if l0 < 1e-9 or l1 < 1e-9:
            continue
        d0.normalize()
        d1.normalize()
        cosang = max(-1.0, min(1.0, d0.dot(d1)))
        ang = math.acos(cosang)
        if ang > math.pi - 1e-3:  # straight
            out.append(b)
            continue
        t = radius / math.tan(ang / 2)
        t = min(t, l0 * 0.5 if i > 1 else l0 * 0.95, l1 * 0.5 if i < len(P) - 2 else l1 * 0.95)
        p0 = b + d0 * t
        p1 = b + d1 * t
        # quadratic-ish arc: a circular arc from p0 to p1 tangent to both legs
        bis = (d0 + d1).normalized()
        rr = t * math.tan(ang / 2)
        centre = b + bis * math.sqrt(rr * rr + t * t)
        v0 = (p0 - centre)
        v1 = (p1 - centre)
        axis = v0.cross(v1)
        if axis.length < 1e-12:
            out.append(b)
            continue
        axis.normalize()
        sweep = v0.angle(v1)
        for k in range(segs + 1):
            q = Matrix.Rotation(sweep * k / segs, 3, axis)
            out.append(centre + q @ v0)
    out.append(P[-1])
    return out


def arc_pts(centre, radius, a0, a1, n, u=(1, 0, 0), v=(0, 1, 0)):
    """Points on an arc in the plane spanned by unit Unity vectors u, v."""
    C, U_, W = V(centre), V(u), V(v)
    return [C + (U_ * math.cos(lerp(a0, a1, k / n)) + W * math.sin(lerp(a0, a1, k / n))) * radius for k in range(n + 1)]


# ====================================================================== mesh builder

class MB:
    """Accumulates geometry (Unity space) for one object. Each face is flat or smooth shaded: flat primitives
    (slabs, boxes, labels, text) stay flat, round ones (lathes, sweeps, blades) are smooth with sharp edges
    above the object's smoothing angle."""
    __slots__ = ("v", "f", "uv", "s")

    def __init__(self):
        self.v, self.f, self.uv, self.s = [], [], [], []

    def add(self, geo, M=None, t=(0, 0, 0)):
        verts, faces, uvs = geo[0], geo[1], geo[2]
        flags = geo[3] if len(geo) > 3 and geo[3] is not None else [True] * len(faces)
        self.s.extend(flags)
        base = len(self.v)
        M = Matrix.Identity(3) if M is None else M
        t = V(t)
        flip = M.determinant() < 0
        self.v.extend([M @ V(p) + t for p in verts])
        for i, fc in enumerate(faces):
            idx = [base + k for k in fc]
            uv = uvs[i] if uvs is not None else None
            if flip:
                idx.reverse()
                if uv is not None:
                    uv = list(reversed(uv))
            self.f.append(idx)
            self.uv.append(uv)
        return self

    def tris(self):
        return sum(len(f) - 2 for f in self.f)


def _uvs_of(mb):
    if not any(u is not None for u in mb.uv):
        return None
    return mb.uv


def xf(geo, M=None, t=(0, 0, 0)):
    """Transforms local geometry (keeps the winding right if M mirrors)."""
    mb = MB().add(geo, M, t)
    return mb.v, mb.f, _uvs_of(mb), mb.s


def merge(*geos):
    mb = MB()
    for g in geos:
        mb.add(g)
    return mb.v, mb.f, _uvs_of(mb), mb.s


def flat(geo, smooth=False):
    """Marks every face of a geometry flat (or smooth)."""
    return geo[0], geo[1], geo[2], [smooth] * len(geo[1])


def _newell(pts):
    n = V((0, 0, 0))
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def build_mesh(mb, name, tag, parent=None, smooth=32.0):
    """Creates '<name>#<tag>' from a builder. parent: the model root, or an anchor (then the object is a moving
    piece '<name>@<anchor>#<tag>' whose origin and axes are the anchor's)."""
    local = None
    if is_anchor(parent):
        local = parent.matrix_world.copy()
        inv = local.inverted()
        verts = [inv @ c.conv(p) for p in mb.v]
    else:
        verts = [c.conv(p) for p in mb.v]
    faces = [list(reversed(f)) for f in mb.f]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new(name="UVMap")
    data = uvl.data
    for pi, poly in enumerate(me.polygons):
        uv = mb.uv[pi]
        li = poly.loop_indices
        if uv is not None:
            for k, l in enumerate(reversed(list(li))):
                data[l].uv = uv[k]
        else:
            pts = [mb.v[i] for i in mb.f[pi]]
            n = _newell(pts)
            ax = max(range(3), key=lambda a: abs(n[a]))
            a1, a2 = (ax + 1) % 3, (ax + 2) % 3
            for k, l in enumerate(reversed(list(li))):
                p = pts[k]
                data[l].uv = (p[a1] / UV_METRES, p[a2] / UV_METRES)
    obj = c.link(bpy.data.objects.new(name, me))
    if local is not None:
        obj.matrix_world = local
    c.finish(obj, name, tag, parent, smooth_angle=None)
    me.polygons.foreach_set("use_smooth", [bool(x) for x in mb.s])
    if smooth is not None:
        me.set_sharp_from_angle(angle=smooth * DEG)
    me.validate(clean_customdata=False)
    me.update()
    return obj


# ====================================================================== primitives (local geometry)

def bm_geo(bm):
    bm.verts.index_update()
    verts = [v.co.copy() for v in bm.verts]
    faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return verts, faces, None


def g_box(size, bevel=0.0, seg=1):
    """Box centred on the origin. size = (x, y, z)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=V(size), verts=bm.verts)
    if bevel > 0:
        b = min(bevel, min(size) * 0.49)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=seg, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
    return flat(bm_geo(bm), smooth=(bevel > 0 and seg >= 2))


def g_lathe(prof, n=24, a0=0.0, a1=TAU):
    """Revolves a profile [(r, z), ...] about local Z. Give the profile counter-clockwise in the (r, z) half
    plane (bottom centre -> outside -> top centre) for outward normals. r = 0 points become poles."""
    full = abs((a1 - a0) - TAU) < 1e-9
    cols = n if full else n + 1
    verts, faces, rows = [], [], []
    for (r, z) in prof:
        if r < 1e-9:
            verts.append(V((0.0, 0.0, z)))
            rows.append([len(verts) - 1] * cols)
        else:
            row = []
            for j in range(cols):
                a = a0 + (a1 - a0) * j / n
                verts.append(V((r * math.cos(a), r * math.sin(a), z)))
                row.append(len(verts) - 1)
            rows.append(row)
    for i in range(len(prof) - 1):
        A, B = rows[i], rows[i + 1]
        for j in range(n):
            j1 = (j + 1) % cols if full else j + 1
            q = []
            for k in (A[j], A[j1], B[j1], B[j]):
                if k not in q:
                    q.append(k)
            if len(q) >= 3:
                faces.append(q)
    return verts, faces, None


def g_cyl(r, h, n=24, r2=None, caps=(True, True), bevel=0.0, seg=2):
    """Cylinder (cone if r2) along local Z, centred. bevel rounds the cap rims."""
    r2 = r if r2 is None else r2
    z0, z1 = -h / 2, h / 2
    prof = []
    b = min(bevel, r * 0.45, h * 0.45) if bevel > 0 else 0.0
    if caps[0]:
        prof.append((0.0, z0))
    if b > 0 and caps[0]:
        for k in range(seg + 1):
            a = -90 + 90 * k / seg
            prof.append((r - b + b * math.cos(a * DEG), z0 + b + b * math.sin(a * DEG)))
    else:
        prof.append((r, z0))
    if b > 0 and caps[1]:
        for k in range(seg + 1):
            a = 90 * k / seg
            prof.append((r2 - b + b * math.cos(a * DEG), z1 - b + b * math.sin(a * DEG)))
    else:
        prof.append((r2, z1))
    if caps[1]:
        prof.append((0.0, z1))
    return g_lathe(prof, n)


def g_ring(r_in, r_out, h, n=32, a0=0.0, a1=TAU):
    """A washer/tube along local Z, centred."""
    z0, z1 = -h / 2, h / 2
    prof = [(r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1), (r_in, z0)]
    return g_lathe(prof, n, a0, a1)


def _tess(loops):
    flat = [p for L in loops for p in L]
    tris = tessellate_polygon([[V((p[0], p[1], 0.0)) for p in L] for L in loops])
    out = []
    for t in tris:
        a, b, cc = flat[t[0]], flat[t[1]], flat[t[2]]
        s = (b[0] - a[0]) * (cc[1] - a[1]) - (b[1] - a[1]) * (cc[0] - a[0])
        if abs(s) < 1e-14:
            continue
        out.append((t[0], t[1], t[2]) if s > 0 else (t[0], t[2], t[1]))
    return flat, out


def g_slab(outer, holes=(), depth=0.001, z0=0.0, bevel=0.0, seg=1, uv_rect=None, uv_bounds=None, back=True):
    """Extrudes a 2D outline with holes along local +Z, from z0 to z0 + depth.
    uv_rect=(u0, v0, u1, v1) maps the outline's bounds (or uv_bounds=(x0, y0, x1, y1)) to that UV rectangle."""
    outer = list(outer)
    if area2(outer) < 0:
        outer.reverse()
    hs = []
    for h in holes:
        h = list(h)
        if area2(h) > 0:
            h.reverse()
        hs.append(h)
    loops = [outer] + hs
    flat, tris = _tess(loops)
    n = len(flat)
    z1 = z0 + depth
    verts = [V((p[0], p[1], z0)) for p in flat] + [V((p[0], p[1], z1)) for p in flat]
    faces = []
    for t in tris:
        faces.append([t[0] + n, t[1] + n, t[2] + n])
        if back:
            faces.append([t[0], t[2], t[1]])
    s = 0
    for L in loops:
        m = len(L)
        for i in range(m):
            a, b = s + i, s + (i + 1) % m
            faces.append([a, b, b + n, a + n])
        s += m
    if bevel > 0:
        bm = bmesh.new()
        bv = [bm.verts.new(p) for p in verts]
        for f in faces:
            try:
                bm.faces.new([bv[i] for i in f])
            except ValueError:
                pass
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-9)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.5 * DEG, verts=bm.verts[:], edges=bm.edges[:])
        sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > 40 * DEG]
        bmesh.ops.bevel(bm, geom=sharp, offset=bevel, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
        verts, faces, _ = bm_geo(bm)
    uvs = None
    if uv_rect is not None:
        if uv_bounds is None:
            xs = [p[0] for p in outer]
            ys = [p[1] for p in outer]
            uv_bounds = (min(xs), min(ys), max(xs), max(ys))
        x0, y0, x1, y1 = uv_bounds
        u0, v0, u1, v1 = uv_rect
        def uvof(p):
            return (u0 + (p[0] - x0) / (x1 - x0) * (u1 - u0), v0 + (p[1] - y0) / (y1 - y0) * (v1 - v0))
        uvs = [[uvof(verts[i]) for i in f] for f in faces]
    return verts, faces, uvs, [False] * len(faces)


def g_sweep(pts, radius, n=12, closed=False, caps=True, start_normal=None):
    """A round tube through local points (parallel-transport frames). radius may be a function of 0..1."""
    P = [V(p) for p in pts]
    # drop duplicate points
    Q = [P[0]]
    for p in P[1:]:
        if (p - Q[-1]).length > 1e-7:
            Q.append(p)
    P = Q
    m = len(P)
    T = []
    for i in range(m):
        if closed:
            a = P[(i + 1) % m] - P[i - 1]
        else:
            a = P[min(i + 1, m - 1)] - P[max(i - 1, 0)]
        T.append(a.normalized())
    t0 = T[0]
    ref = V(start_normal) if start_normal is not None else (V((0, 0, 1)) if abs(t0.z) < 0.9 else V((1, 0, 0)))
    N = (ref - t0 * ref.dot(t0)).normalized()
    verts, faces = [], []
    for i in range(m):
        if i > 0:
            q = T[i - 1].rotation_difference(T[i])
            N = q @ N
            N = (N - T[i] * N.dot(T[i])).normalized()
        B = T[i].cross(N)
        r = radius(i / max(1, m - 1)) if callable(radius) else radius
        for j in range(n):
            a = TAU * j / n
            verts.append(P[i] + (N * math.cos(a) + B * math.sin(a)) * r)
    segs = m if closed else m - 1
    for i in range(segs):
        i1 = (i + 1) % m
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, i1 * n + j1, i1 * n + j])
    if caps and not closed:
        faces.append([j for j in reversed(range(n))])
        faces.append([(m - 1) * n + j for j in range(n)])
    return verts, faces, None


def g_quad(w, h, uv_rect=(0, 0, 1, 1)):
    """A rectangle in the local XY plane facing +Z (put it on a surface with label_frame)."""
    u0, v0, u1, v1 = uv_rect
    verts = [V((-w / 2, -h / 2, 0)), V((w / 2, -h / 2, 0)), V((w / 2, h / 2, 0)), V((-w / 2, h / 2, 0))]
    return verts, [[0, 1, 2, 3]], [[(u0, v0), (u1, v0), (u1, v1), (u0, v1)]], [False]


def g_disc(r, n=32, uv_rect=(0, 0, 1, 1), depth=0.0):
    """A round sticker in the local XY plane facing +Z, its UVs a circle inscribed in uv_rect.
    depth > 0 makes it a thin coin (same UVs on the rim) from z = -depth to 0."""
    u0, v0, u1, v1 = uv_rect
    uc, vc, ur, vr = (u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) / 2, (v1 - v0) / 2
    ring = [V((r * math.cos(TAU * i / n), r * math.sin(TAU * i / n), 0)) for i in range(n)]
    ruv = [(uc + ur * math.cos(TAU * i / n), vc + vr * math.sin(TAU * i / n)) for i in range(n)]
    verts = [V((0, 0, 0))] + ring
    faces, uvs = [], []
    for i in range(n):
        faces.append([0, 1 + i, 1 + (i + 1) % n])
        uvs.append([(uc, vc), ruv[i], ruv[(i + 1) % n]])
    if depth > 0:
        base = len(verts)
        verts += [p - V((0, 0, depth)) for p in ring]
        for i in range(n):
            a, b = 1 + i, 1 + (i + 1) % n
            faces.append([base + i, base + (i + 1) % n, b, a])
            uvs.append([ruv[i], ruv[(i + 1) % n], ruv[(i + 1) % n], ruv[i]])
    return verts, faces, uvs, [False] * len(faces)


def g_grid(fn, nu, nv, closed_u=False):
    """A surface from fn(u, v) -> local point, u, v in 0..1. Normal = d/du x d/dv."""
    cols = nu if closed_u else nu + 1
    verts = []
    for j in range(nv + 1):
        for i in range(cols):
            verts.append(V(fn(i / nu, j / nv)))
    faces = []
    for j in range(nv):
        for i in range(nu):
            i1 = (i + 1) % cols if closed_u else i + 1
            faces.append([j * cols + i, j * cols + i1, (j + 1) * cols + i1, (j + 1) * cols + i])
    return verts, faces, None


def g_helix(r, wire, z0, z1, turns, n=10, per_turn=16):
    """A coil spring along local Z (wire = wire radius)."""
    steps = max(4, int(turns * per_turn))
    pts = [(r * math.cos(TAU * turns * k / steps), r * math.sin(TAU * turns * k / steps), lerp(z0, z1, k / steps))
           for k in range(steps + 1)]
    return g_sweep(pts, wire, n)


def g_screw_head(r, h, recess="ph", n=20, dome=0.35):
    """A pan/cheese head screw head: base on z = 0, top at z = h, with a Phillips (ph) or slot recess.
    Returns geometry for the head only (the shank is a separate cylinder)."""
    prof = [(0.0, 0.0), (r, 0.0), (r, h * (1 - dome))]
    for k in range(1, 5):
        a = 90 * k / 4
        prof.append((r - (r * 0.35) * (1 - math.cos(a * DEG)), h * (1 - dome) + h * dome * math.sin(a * DEG)))
    prof.append((0.0, h))
    head = g_lathe(prof, n)
    parts = [head]
    if recess == "ph":
        w = r * 0.22
        L = r * 1.15
        for a in (0.0, 90.0):
            parts.append(xf(g_box((L, w, h * 0.5)), rot("z", a * DEG), (0, 0, h * 0.8)))
    elif recess == "slot":
        parts.append(xf(g_box((r * 1.9, r * 0.25, h * 0.5)), None, (0, 0, h * 0.8)))
    return merge(*parts)


# ---------------------------------------------------------------- fonts and text

_font_cache = {}
_cap_cache = {}


def load_font(key):
    path = os.path.join(FONT_DIR, FONTS.get(key, key))
    f = _font_cache.get(path)
    try:
        if f is not None:
            f.name  # still valid?
            return f
    except ReferenceError:
        pass
    found = c.font_file(path)
    if found:
        f = bpy.data.fonts.load(found, check_existing=True)
    else:
        f = bpy.data.fonts.load("<builtin>", check_existing=True)
    _font_cache[path] = f
    return f


def _text_mesh(s, font, extrude=0.0, res=3, spacing=1.0, line=1.0, align="CENTER"):
    """Text at size 1 as Blender mesh data -> (verts, faces) in text space (x right, y up, z out)."""
    cu = bpy.data.curves.new("dct_txt", "FONT")
    cu.body = s
    cu.font = load_font(font)
    cu.size = 1.0
    cu.extrude = extrude
    cu.resolution_u = res
    cu.space_character = spacing
    cu.space_line = line
    cu.align_x = align
    cu.align_y = "TOP_BASELINE"
    ob = bpy.data.objects.new("dct_txt", cu)
    sc = bpy.context.scene
    sc.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    verts = [v.co.copy() for v in me.vertices]
    faces = [list(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    sc.collection.objects.unlink(ob)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return verts, faces


def cap_height(font):
    """Cap height of a font at size 1 (measured on 'H')."""
    if font not in _cap_cache:
        v, _ = _text_mesh("H", font)
        _cap_cache[font] = max(p.y for p in v) - min(p.y for p in v) if v else 0.7
    return _cap_cache[font]


def g_text(s, font="arialb", height=0.005, width=None, depth=0.0003, align="CENTER", valign="CENTER", res=3,
           spacing=1.0, line=1.25, italic=0.0):
    """Extruded text in label space: x = reading right, y = up, z = towards the reader (0..depth).
    height = cap height in metres; width = maximum width (shrinks to fit). valign: CENTER (caps centred on 0),
    BASELINE (first baseline on 0) or TOP (cap top on 0). italic = shear (0.2 looks like an oblique)."""
    cap = cap_height(font)
    e = 0.05
    verts, faces = _text_mesh(s, font, e if depth > 0 else 0.0, res, spacing, line, align)
    if not verts:
        return [], [], None
    k = height / cap
    xs = [p.x for p in verts]
    w = (max(xs) - min(xs)) * k
    if width is not None and w > width:
        k *= width / w
    cap_k = cap * k
    dy = {"CENTER": -cap_k / 2, "BASELINE": 0.0, "TOP": -cap_k}[valign]
    out = []
    for p in verts:
        x, y = p.x * k, p.y * k + dy
        x += italic * (y - dy)
        z = ((p.z + e) / (2 * e)) * depth if depth > 0 else 0.0
        out.append(V((x, y, z)))
    if depth <= 0:
        # flat text: make sure every face points +z
        fixed = []
        for f in faces:
            n = _newell([out[i] for i in f])
            fixed.append(f if n.z >= 0 else list(reversed(f)))
        faces = fixed
    return out, faces, None, [False] * len(faces)


def text_width(s, font, height, spacing=1.0):
    v, _ = _text_mesh(s, font, 0.0, 2, spacing)
    if not v:
        return 0.0
    xs = [p.x for p in v]
    return (max(xs) - min(xs)) * height / cap_height(font)


# ====================================================================== the model

class Model:
    """One part: the root, per-tag builders for static geometry and per-anchor builders for moving pieces."""

    def __init__(self, pid):
        c.reset()
        _font_cache.clear()
        self.id = pid
        self.root = c.root(pid)
        self.static = {}
        self.pieces = {}
        self.anchors = []

    def mb(self, tag):
        return self.static.setdefault(tag, MB())

    def add(self, tag, geo, M=None, t=(0, 0, 0)):
        return self.mb(tag).add(geo, M, t)

    def piece(self, anchor, tag, name="piece"):
        key = (anchor.name, name, tag)
        if key not in self.pieces:
            self.pieces[key] = (anchor, MB())
        return self.pieces[key][1]

    def anchor(self, name, pos, size=(0.01, 0.01, 0.01), forward=(0, 0, 1), up=(0, 1, 0), meta=None, parent=None):
        a = c.anchor(name, pos, size, parent if parent is not None else self.root, forward, up, meta)
        self.anchors.append(a)
        return a

    def finish(self, smooth=32.0):
        for tag, mb in self.static.items():
            if mb.f:
                build_mesh(mb, f"{self.id}_{tag}", tag, self.root, smooth)
        for (aname, nm, tag), (a, mb) in self.pieces.items():
            if mb.f:
                build_mesh(mb, nm, tag, a, smooth)
        c.join_by_tag(self.root, self.id)

    # ---------------------------------------------------------- output
    def export(self):
        return c.export(self.root, self.id)

    def report(self):
        lines = [f"== {self.id}"]
        total = 0
        objs = [o for o in c.descendants(self.root) if o.type == "MESH"]
        for o in sorted(objs, key=lambda o: o.name):
            t = sum(len(p.vertices) - 2 for p in o.data.polygons)
            total += t
            lines.append(f"   mesh {o.name}: {t} tris")
        lines.append(f"   TOTAL {total} tris in {len(objs)} meshes")
        for e in sorted([o for o in c.descendants(self.root) if o.type == "EMPTY" and o.name.startswith("A_")],
                        key=lambda o: o.name):
            p, f, u = unity_pose(e)
            lines.append(f"   {e.name}: pos=({p.x:.4f},{p.y:.4f},{p.z:.4f}) fwd=({f.x:.2f},{f.y:.2f},{f.z:.2f}) "
                         f"up=({u.x:.2f},{u.y:.2f},{u.z:.2f}) size={e.get('size')} meta={e.get('meta', '')}")
        txt = "\n".join(lines)
        print(txt)
        return txt


# ====================================================================== previews

def preview_textures():
    """Hooks tex_ materials up to their PNGs so the Workbench previews show the artwork (call AFTER export)."""
    for m in bpy.data.materials:
        if not m.name.startswith("tex_"):
            continue
        path = os.path.join(c.TEXTURES, m.name[4:] + ".png")
        if not os.path.exists(path):
            continue
        try:
            m.use_nodes = True
        except Exception:
            pass
        nt = m.node_tree
        img = bpy.data.images.load(path, check_existing=True)
        img.reload()
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = img
        bs = [x for x in nt.nodes if x.type == "BSDF_PRINCIPLED"]
        if bs:
            nt.links.new(n.outputs["Color"], bs[0].inputs["Base Color"])
        nt.nodes.active = n


def shots(root, name, views, size=(1200, 900), first=0):
    """Workbench previews with textures and back-face culling. views: dicts with yaw, pitch (deg, Unity terms as
    in c.preview), optional dist (m), target (Unity point), lens (mm). Writes Logs/ModelPreviews/<name>_<i>.png."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "TEXTURE"
    sh.show_cavity = True
    sh.show_shadows = True
    sh.shadow_intensity = 0.3
    sh.show_backface_culling = True
    sh.show_specular_highlight = True
    try:
        sh.cavity_type = "BOTH"
        sh.cavity_ridge_factor = 0.6
        sh.cavity_valley_factor = 1.0
    except Exception:
        pass
    sc.display.render_aa = "16"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("w")
    pts = []
    for o in c.descendants(root):
        if o.type == "MESH":
            pts += [o.matrix_world @ V(cc) for cc in o.bound_box]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) * 0.5
    radius = (hi - lo).length * 0.5
    cd = bpy.data.cameras.new("dct_shot")
    cd.clip_start = 0.002
    cd.clip_end = 50
    cam = c.link(bpy.data.objects.new("dct_shot", cd))
    sc.camera = cam
    out = []
    for i, v in enumerate(views):
        cd.lens = v.get("lens", 50)
        tgt = c.conv(v["target"]) if "target" in v else centre
        d = v.get("dist", radius * 3.2)
        y, p = v.get("yaw", 35) * DEG, v.get("pitch", 30) * DEG
        u = V((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        cam.location = tgt + c.conv(u) * d
        dirn = tgt - cam.location
        cam.rotation_euler = dirn.to_track_quat("-Z", "Y").to_euler()
        if "roll" in v:
            cam.rotation_euler.rotate_axis("Z", v["roll"] * DEG)
        path = os.path.join(c.PREVIEWS, f"{name}_{first + i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    bpy.data.objects.remove(cam)
    return out


# ====================================================================== 2D artwork (textures)

def srgb_to_lin(x):
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def colour(col):
    """'#rrggbb' or (r, g, b) in sRGB 0..1 -> linear RGBA for Blender."""
    if isinstance(col, str):
        h = col.lstrip("#")
        col = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb_to_lin(col[0]), srgb_to_lin(col[1]), srgb_to_lin(col[2]), 1.0)


class Atlas:
    """Named pixel rectangles (x, y from the top-left, w, h) in a W x H texture, and their UVs."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.r = {}

    def add(self, name, x, y, w, h):
        self.r[name] = (x, y, w, h)
        return self.uv(name)

    def uv(self, name, inset=0.5):
        x, y, w, h = self.r[name]
        return ((x + inset) / self.w, 1.0 - (y + h - inset) / self.h, (x + w - inset) / self.w, 1.0 - (y + inset) / self.h)

    def px(self, name):
        return self.r[name]


class Canvas:
    """Flat 2D artwork rendered orthographically by Workbench into a PNG (Assets/Resources/Models/Textures).
    Pixel coordinates, origin top-left, y down. Colours are sRGB ('#rrggbb' or tuples)."""

    def __init__(self, w, h, bg="#ffffff"):
        self.w, self.h = w, h
        self.sc = bpy.data.scenes.new("dct_canvas")
        self.z = 0.0
        self.objs = []
        self.mats = {}
        if bg is not None:
            self.rect(0, 0, w, h, bg)

    def _mat(self, col):
        key = str(col)
        m = self.mats.get(key)
        if m is None:
            m = bpy.data.materials.new("cv_" + key)
            m.diffuse_color = colour(col)
            self.mats[key] = m
        return m

    def _obj(self, data, col):
        self.z += 0.01
        ob = bpy.data.objects.new("cv", data)
        ob.location.z = self.z
        if hasattr(data, "materials"):
            data.materials.append(self._mat(col))
        self.sc.collection.objects.link(ob)
        self.objs.append(ob)
        return ob

    def polys(self, polys, col):
        """Several filled polygons (each: outer [, holes...]) in one colour. polys: list of lists of loops."""
        verts, faces = [], []
        for loops in polys:
            flat, tris = _tess(loops)
            base = len(verts)
            verts += [(p[0], -p[1], 0.0) for p in flat]
            faces += [(base + t[0], base + t[2], base + t[1]) for t in tris]
        me = bpy.data.meshes.new("cv")
        me.from_pydata(verts, [], faces)
        return self._obj(me, col)

    def poly(self, pts, col, holes=()):
        return self.polys([[list(pts)] + [list(h) for h in holes]], col)

    def rect(self, x, y, w, h, col, r=0.0):
        return self.poly(rrect2(x + w / 2, y + h / 2, w, h, r, 6) if r > 0 else rect2(x + w / 2, y + h / 2, w, h), col)

    def frame_rect(self, x, y, w, h, t, col, r=0.0):
        outer = rrect2(x + w / 2, y + h / 2, w, h, r, 6) if r > 0 else rect2(x + w / 2, y + h / 2, w, h)
        inner = rrect2(x + w / 2, y + h / 2, w - 2 * t, h - 2 * t, max(0, r - t), 6) if r > t else \
            rect2(x + w / 2, y + h / 2, w - 2 * t, h - 2 * t)
        return self.poly(outer, col, [inner])

    def rects(self, rs, col):
        return self.polys([[rect2(x + w / 2, y + h / 2, w, h)] for (x, y, w, h) in rs], col)

    def circle(self, cx, cy, r, col, n=96):
        return self.poly(circle2(cx, cy, r, n), col)

    def ring(self, cx, cy, r0, r1, col, n=96):
        return self.poly(circle2(cx, cy, r1, n), col, [circle2(cx, cy, r0, n)])

    def line(self, x0, y0, x1, y1, w, col):
        d = V((x1 - x0, y1 - y0))
        if d.length < 1e-9:
            return None
        n = V((-d.y, d.x)).normalized() * (w / 2)
        return self.poly([(x0 + n.x, y0 + n.y), (x1 + n.x, y1 + n.y), (x1 - n.x, y1 - n.y), (x0 - n.x, y0 - n.y)], col)

    def text(self, s, x, y, size, col, font="arialb", align="left", valign="center", maxw=None, rot=0.0,
             spacing=1.0, line=1.2, italic=0.0):
        """size = cap height in pixels. (x, y) is the anchor point: align left/center/right, valign
        center (caps centred on y), baseline or top."""
        cap = cap_height(font)
        k = size / cap
        if maxw is not None:
            w = text_width(s, font, size, spacing)
            if w > maxw:
                k *= maxw / w
        cu = bpy.data.curves.new("cvt", "FONT")
        cu.body = s
        cu.font = load_font(font)
        cu.size = k
        cu.resolution_u = 8
        cu.space_character = spacing
        cu.space_line = line
        cu.shear = italic
        cu.align_x = {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}[align]
        cu.align_y = "TOP_BASELINE"
        ob = self._obj(cu, col)
        capk = cap * k
        dy = {"center": capk / 2, "baseline": 0.0, "top": capk}[valign]
        # rotate about the anchor point
        ob.rotation_euler.z = -rot * DEG
        off = V((0.0, -dy, 0.0))
        off.rotate(ob.rotation_euler)
        ob.location.x = x + off.x
        ob.location.y = -y + off.y
        return ob

    def barcode(self, x, y, w, h, seed=1, col="#111111"):
        rng = random.Random(seed)
        bars = []
        px = x
        unit = w / 95.0
        while px < x + w - 2 * unit:
            bw = unit * rng.choice((1, 1, 2, 3))
            bars.append((px, y, bw, h))
            px += bw + unit * rng.choice((1, 1, 2, 3))
        return self.rects(bars, col)

    def render(self, filename, size_scale=1.0):
        sc = self.sc
        cd = bpy.data.cameras.new("cvcam")
        cd.type = "ORTHO"
        cd.ortho_scale = max(self.w, self.h)
        cd.clip_start = 0.1
        cd.clip_end = 10000
        cam = bpy.data.objects.new("cvcam", cd)
        cam.location = (self.w / 2, -self.h / 2, 1000.0)
        sc.collection.objects.link(cam)
        sc.camera = cam
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.display.shading.light = "FLAT"
        sc.display.shading.color_type = "MATERIAL"
        sc.display.shading.show_cavity = False
        sc.display.shading.show_shadows = False
        sc.display.shading.show_specular_highlight = False
        sc.display.render_aa = "16"
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.render.dither_intensity = 0.0
        sc.render.resolution_x = int(self.w * size_scale)
        sc.render.resolution_y = int(self.h * size_scale)
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGB"
        path = os.path.join(c.TEXTURES, filename + ".png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True, scene=sc.name)
        # clean up
        for ob in self.objs + [cam]:
            data = ob.data
            bpy.data.objects.remove(ob)
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
        for m in self.mats.values():
            bpy.data.materials.remove(m)
        bpy.data.scenes.remove(sc)
        print("TEXTURE", path)
        return path


# ====================================================================== common hardware bits

def screw_ph(model_or_mb, pos, normal, up=(0, 1, 0), r=0.0028, h=0.0016, tag="steel", recess="ph", shank=0.0):
    """A Phillips pan-head screw head sitting on a surface at pos, facing 'normal'. Returns the geometry added."""
    M = frame(normal, up if abs(V(up).normalized().dot(V(normal).normalized())) < 0.99 else (1, 0, 0))
    geo = g_screw_head(r, h, recess)
    if shank > 0:
        geo = merge(geo, xf(g_cyl(r * 0.55, shank, 10), None, (0, 0, -shank / 2)))
    mb = model_or_mb if isinstance(model_or_mb, MB) else model_or_mb.mb(tag)
    mb.add(geo, M, pos)
    return geo


def solid(geo, uv_rect):
    """Gives every face corner the centre of uv_rect: a solid colour swatch from a tex_ atlas."""
    u = (uv_rect[0] + uv_rect[2]) / 2
    v = (uv_rect[1] + uv_rect[3]) / 2
    verts, faces = geo[0], geo[1]
    return verts, faces, [[(u, v)] * len(f) for f in faces], (geo[3] if len(geo) > 3 else None)
