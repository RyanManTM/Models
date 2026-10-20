"""
Helpers for the electronics part models (boards, CPUs, RAM, SSDs): a batched mesh builder with UVs,
a flat 2D artwork renderer for PCB / label / marking textures, common SMD components, and an EEVEE
preview that shows the textures.

Everything takes UNITY coordinates (metres, +Y up, left-handed) like dct_common; dct_common.conv() does
the Blender conversion. Builds on dct_common and never changes it.

Texture orientation (matches the game's decal quads): a face whose outward normal is n, looked at from
outside with image-up along `up`, has the image's right along cross(up, -n) (component-wise formula, the
same as Unity's camera right). For a board top (+z, up +y) the image runs from +x (left) to -x (right).
"""
import bmesh
import bpy
import math
import os
import random
from contextlib import contextmanager
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

import dct_common as c

FONTS = {
    "arial": r"C:\Windows\Fonts\arial.ttf",
    "arialbd": r"C:\Windows\Fonts\arialbd.ttf",
    "narrow": r"C:\Windows\Fonts\ARIALN.TTF",
    "narrowbd": r"C:\Windows\Fonts\ARIALNB.TTF",
    "agency": r"C:\Windows\Fonts\AGENCYB.TTF",
    "agencyr": r"C:\Windows\Fonts\AGENCYR.TTF",
    "ocr": r"C:\Windows\Fonts\OCRAEXT.TTF",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "monobd": r"C:\Windows\Fonts\consolab.ttf",
    "bahn": r"C:\Windows\Fonts\bahnschrift.ttf",
    "impact": r"C:\Windows\Fonts\impact.ttf",
    "calibri": r"C:\Windows\Fonts\calibrib.ttf",
}

MM = 0.001


# ------------------------------------------------------------------ small maths

def vec(p):
    return Vector((float(p[0]), float(p[1]), float(p[2])))


def cross(a, b):
    return Vector((a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]))


def unconv(b):
    """Blender vector -> Unity."""
    return Vector((-b[0], b[2], -b[1]))


def rot(axis, deg):
    """3x3 rotation in Unity-coordinate numbers about 'x', 'y', 'z' (or a vector), right-hand formula."""
    ax = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}.get(axis, axis)
    return Matrix.Rotation(math.radians(deg), 3, Vector(ax))


def frame(x=(1, 0, 0), y=(0, 1, 0), z=(0, 0, 1)):
    """3x3 matrix whose columns are the local axes (Unity numbers)."""
    return Matrix((vec(x), vec(y), vec(z))).transposed()


def srgb_to_lin(v):
    v = max(0.0, min(1.0, v))
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rgb(h):
    """'#rrggbb' or (r,g,b) 0..255 -> sRGB floats."""
    if isinstance(h, str):
        h = h.lstrip("#")
        return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)
    if max(h) > 1.0:
        return (h[0] / 255.0, h[1] / 255.0, h[2] / 255.0)
    return tuple(h)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def shade(a, k):
    a = rgb(a)
    return tuple(max(0.0, min(1.0, x * k)) for x in a)


# ------------------------------------------------------------------ UV mappers

class Planar:
    """Maps faces whose normal is within `thresh` of `normal` onto `region` (u0,v0,u1,v1), with the
    world rectangle centred at `center`, image-up along `up`, `size`=(w,h) metres."""

    def __init__(self, region, center, normal, up, size, thresh=0.6, mirror=False):
        self.region = region
        self.center = vec(center)
        self.normal = vec(normal).normalized()
        f = -self.normal
        u = vec(up)
        u = (u - f * u.dot(f)).normalized()
        self.U = u
        self.R = cross(u, f).normalized()
        if mirror:
            self.R = -self.R
        self.w, self.h = size
        self.thresh = thresh

    def __call__(self, n, pts):
        if n.dot(self.normal) < self.thresh:
            return None
        u0, v0, u1, v1 = self.region
        out = []
        for p in pts:
            d = p - self.center
            out.append((u0 + (d.dot(self.R) / self.w + 0.5) * (u1 - u0), v0 + (d.dot(self.U) / self.h + 0.5) * (v1 - v0)))
        return out


class Swatch:
    """Every face gets one UV point (a flat-colour patch of the atlas)."""

    def __init__(self, uv):
        self.uv = uv

    def __call__(self, n, pts):
        return [self.uv] * len(pts)


# ------------------------------------------------------------------ mesh builder

class Geo:
    """Accumulates many primitives into one mesh object (one tag). Coordinates are Unity model space.
    `origin` is the object's pivot (for moving pieces: the anchor position)."""

    def __init__(self, tag, origin=(0, 0, 0)):
        self.tag = tag
        self.bm = bmesh.new()
        self.textured = tag.startswith("tex_")
        self.uvl = self.bm.loops.layers.uv.new("UVMap") if self.textured else None
        self.origin = vec(origin)
        self.ofs_b = c.conv(self.origin)
        self.count = 0

    def add(self, verts, faces, M=None, T=None, uv=None, convex=True):
        """verts: local Unity points; faces: index tuples. M: 3x3 rotation; T: translation (model)."""
        Mt = M if M is not None else None
        Tt = vec(T) if T is not None else Vector((0, 0, 0))
        pts = [((Mt @ vec(v)) if Mt is not None else vec(v)) + Tt for v in verts]
        bvs = [self.bm.verts.new(c.conv(p) - self.ofs_b) for p in pts]
        made = []
        for f in faces:
            if len(set(f)) < 3:
                continue
            try:
                bf = self.bm.faces.new([bvs[i] for i in f])
            except ValueError:
                continue
            made.append((bf, f))
        if not made:
            return []
        if convex:
            cen = c.conv(sum(pts, Vector()) / len(pts)) - self.ofs_b
            for bf, f in made:
                bf.normal_update()
                if bf.normal.dot(bf.calc_center_median() - cen) < 0:
                    bf.normal_flip()
        else:
            bmesh.ops.recalc_face_normals(self.bm, faces=[bf for bf, _ in made])
        if self.uvl is not None:
            mapper = uv
            for bf, f in made:
                bf.normal_update()
                n = unconv(bf.normal)
                fpts = [unconv(l.vert.co + self.ofs_b) for l in bf.loops]
                res = mapper(n, fpts) if mapper else None
                if res is None:
                    res = [(0.0, 0.0)] * len(fpts)
                for l, t in zip(bf.loops, res):
                    l[self.uvl].uv = t
        self.count += len(made)
        return [bf for bf, _ in made]

    def obj(self, name, parent=None, smooth=35):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        ob = c.link(bpy.data.objects.new(name, me))
        # matrix_world (not location): attach() reads matrix_world, which a bare location write leaves stale
        ob.matrix_world = Matrix.Translation(self.ofs_b)
        return c.finish(ob, name, self.tag, parent, smooth_angle=smooth)


class Kit:
    """A bag of Geo builders keyed by tag, all finished into one object per tag at the end."""

    def __init__(self, prefix):
        self.prefix = prefix
        self.geos = {}

    def __getitem__(self, tag):
        g = self.geos.get(tag)
        if g is None:
            g = self.geos[tag] = Geo(tag)
        return g

    def finish(self, parent, smooth=35):
        out = []
        for tag, g in self.geos.items():
            if g.count:
                out.append(g.obj(f"{self.prefix}_{tag}", parent, smooth))
            else:
                g.bm.free()
        self.geos = {}
        return out


# ------------------------------------------------------------------ primitives

_CUBE_V = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
_CUBE_F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def box(g, center, size, M=None, bevel=0.0, seg=1, uv=None):
    """Axis-aligned (in M) box. size in metres. bevel chamfers/rounds all edges."""
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    if bevel <= 0:
        vs = [(x * sx, y * sy, z * sz) for x, y, z in _CUBE_V]
        return g.add(vs, _CUBE_F, M, center, uv)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    b = min(bevel, sx * 0.49, sy * 0.49, sz * 0.49)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    vs = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    fs = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return g.add(vs, fs, M, center, uv)


def edges_bevel_box(g, center, size, M=None, bevel=0.0, which="z", seg=1, uv=None):
    """Box with only the edges parallel to one local axis rounded (e.g. a plate with rounded corners)."""
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    ax = {"x": 0, "y": 1, "z": 2}[which]
    sel = []
    for e in bm.edges:
        d = e.verts[1].co - e.verts[0].co
        if abs(d[ax]) > 1e-9 and abs(d[(ax + 1) % 3]) < 1e-9 and abs(d[(ax + 2) % 3]) < 1e-9:
            sel.append(e)
    lim = [sx, sy, sz]
    lim.pop(ax)
    b = min(bevel, min(lim) * 0.49)
    if b > 0:
        bmesh.ops.bevel(bm, geom=sel, offset=b, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    vs = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    fs = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return g.add(vs, fs, M, center, uv)


def axis_matrix(axis):
    """3x3 that maps local +z onto the given Unity axis ('x','y','z', '-x', ... or a vector)."""
    if isinstance(axis, str):
        s = -1.0 if axis.startswith("-") else 1.0
        a = axis.lstrip("+-")
        d = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}[a] * s
    else:
        d = vec(axis).normalized()
    z = Vector((0, 0, 1))
    if (d - z).length < 1e-9:
        return Matrix.Identity(3)
    if (d + z).length < 1e-9:
        return rot("x", 180)
    return z.rotation_difference(d).to_matrix()


def lathe(g, center, profile, seg=16, axis="z", M=None, uv=None, phase=0.0):
    """Revolves a (r, h) profile around a local axis. Profiles should start and end with r=0 for a closed
    solid (poles become triangle fans)."""
    A = axis_matrix(axis)
    if M is not None:
        A = M @ A
    verts, faces, rings = [], [], []
    for r, h in profile:
        if r <= 1e-9:
            rings.append([len(verts)])
            verts.append((0.0, 0.0, h))
        else:
            ring = []
            for i in range(seg):
                a = 2 * math.pi * (i + phase) / seg
                ring.append(len(verts))
                verts.append((math.cos(a) * r, math.sin(a) * r, h))
            rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for i in range(seg):
                faces.append((a[0], b[i], b[(i + 1) % seg]))
        elif len(b) == 1:
            for i in range(seg):
                faces.append((a[i], a[(i + 1) % seg], b[0]))
        else:
            for i in range(seg):
                faces.append((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    return g.add([Vector(v) for v in verts], faces, A, center, uv, convex=False)


def cyl(g, center, r, h, axis="z", seg=16, bevel=0.0, r2=None, M=None, uv=None):
    """Closed cylinder (or cone) centred at center, length h along axis, optional top/bottom chamfer."""
    r2 = r if r2 is None else r2
    hh = h * 0.5
    if bevel > 0:
        b = min(bevel, r * 0.45, hh * 0.9)
        prof = [(0, -hh), (r - b, -hh), (r, -hh + b), (r2, hh - b), (r2 - b, hh), (0, hh)]
    else:
        prof = [(0, -hh), (r, -hh), (r2, hh), (0, hh)]
    return lathe(g, center, prof, seg, axis, M, uv)


def tube_ring(g, center, r0, r1, h, axis="z", seg=24, M=None, uv=None):
    """A hollow ring (washer / pipe section)."""
    hh = h * 0.5
    A = axis_matrix(axis)
    if M is not None:
        A = M @ A
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        verts += [(ca * r0, sa * r0, -hh), (ca * r1, sa * r1, -hh), (ca * r1, sa * r1, hh), (ca * r0, sa * r0, hh)]
    for i in range(seg):
        j = (i + 1) % seg
        a, b = i * 4, j * 4
        faces += [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2), (a + 2, b + 2, b + 3, a + 3), (a + 3, b + 3, b, a)]
    return g.add([Vector(v) for v in verts], faces, A, center, uv, convex=False)


def prism(g, loops, z0, z1, M=None, T=None, uv=None):
    """Extrudes 2D loops (first = outline, rest = holes; local x,y) from local z0 to z1, triangulated caps."""
    loops = [[(float(p[0]), float(p[1])) for p in lp] for lp in loops]
    flat = [p for lp in loops for p in lp]
    tris = tessellate_polygon([[Vector((p[0], p[1], 0.0)) for p in lp] for lp in loops])
    n = len(flat)
    verts = [(p[0], p[1], z0) for p in flat] + [(p[0], p[1], z1) for p in flat]
    faces = []
    for t in tris:
        faces.append((t[0], t[2], t[1]))
        faces.append((t[0] + n, t[1] + n, t[2] + n))
    base = 0
    for lp in loops:
        m = len(lp)
        for i in range(m):
            a, b = base + i, base + (i + 1) % m
            faces.append((a, b, b + n, a + n))
        base += m
    return g.add([Vector(v) for v in verts], faces, M, T, uv, convex=False)


def prism_bevel(g, outline, z0, z1, bevel, seg=1, M=None, T=None, uv=None, bottom_bevel=0.0):
    """Extrudes one 2D outline (local x,y; no holes) from z0 to z1 with the top rim (and optionally the
    bottom rim) rounded, then triangulates the caps."""
    bm = bmesh.new()
    pts = [(float(p[0]), float(p[1])) for p in outline]
    # counter-clockwise for consistent winding
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts.reverse()
    b = [bm.verts.new((p[0], p[1], z0)) for p in pts]
    t = [bm.verts.new((p[0], p[1], z1)) for p in pts]
    fb = bm.faces.new(list(reversed(b)))
    ft = bm.faces.new(t)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bm.normal_update()
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(ft.edges), offset=bevel, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    if bottom_bevel > 0:
        bmesh.ops.bevel(bm, geom=[e for e in bm.edges if all(abs(v.co.z - z0) < 1e-9 for v in e.verts)],
                        offset=bottom_bevel, segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    vs = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    fs = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return g.add(vs, fs, M, T, uv, convex=False)


def quad(g, center, size, normal=(0, 0, 1), up=(0, 1, 0), region=None):
    """A single-sided rectangle facing `normal` (a decal). region maps the full quad."""
    n = vec(normal).normalized()
    u = vec(up)
    u = (u - n * u.dot(n)).normalized()
    r = cross(u, -n).normalized()
    w, h = size[0] * 0.5, size[1] * 0.5
    cen = vec(center)
    vs = [cen - r * w - u * h, cen + r * w - u * h, cen + r * w + u * h, cen - r * w + u * h]
    bvs = [g.bm.verts.new(c.conv(p) - g.ofs_b) for p in vs]
    f = g.bm.faces.new(bvs)
    f.normal_update()
    if f.normal.dot(c.conv(n)) < 0:
        f.normal_flip()
    if g.uvl is not None and region is not None:
        u0, v0, u1, v1 = region
        for l in f.loops:
            p = unconv(l.vert.co + g.ofs_b) - cen
            l[g.uvl].uv = (u0 + (p.dot(r) / (2 * w) + 0.5) * (u1 - u0), v0 + (p.dot(u) / (2 * h) + 0.5) * (v1 - v0))
    g.count += 1
    return f


def rounded_rect(cx, cy, w, h, r, seg=4):
    """Outline (counter-clockwise) of a rounded rectangle, local 2D."""
    r = max(0.0, min(r, w * 0.5 - 1e-6, h * 0.5 - 1e-6))
    pts = []
    corners = [(cx + w / 2 - r, cy - h / 2 + r, -90), (cx + w / 2 - r, cy + h / 2 - r, 0),
               (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180)]
    for x, y, a0 in corners:
        if r <= 0:
            pts.append((x, y))
            continue
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    return pts


def circle_pts(cx, cy, r, seg=16, start=0.0):
    return [(cx + math.cos(start + 2 * math.pi * i / seg) * r, cy + math.sin(start + 2 * math.pi * i / seg) * r) for i in range(seg)]


# ------------------------------------------------------------------ 2D artwork renderer

class Art:
    """A flat-colour 2D artwork rendered by Workbench with an orthographic camera.
    Units are arbitrary (usually millimetres or pixels): W x H units -> px_w x px_h pixels.
    Draw order is by z (higher on top). Colours are sRGB tuples or '#rrggbb'."""

    _n = 0

    def __init__(self, W, H, px_w, px_h, bg=None, aa="16"):
        Art._n += 1
        self.sc = bpy.data.scenes.new(f"art_{Art._n}")
        sc = self.sc
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "FLAT"
        sh.color_type = "OBJECT"
        sh.show_cavity = False
        sh.show_shadows = False
        sh.show_object_outline = False
        sh.show_specular_highlight = False
        sh.show_xray = False
        sc.display.render_aa = aa
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.view_settings.exposure = 0.0
        sc.view_settings.gamma = 1.0
        sc.render.dither_intensity = 0.0
        sc.render.resolution_x, sc.render.resolution_y = px_w, px_h
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGB"
        sc.render.image_settings.color_depth = "8"
        sc.render.image_settings.compression = 90
        self.W, self.H = W, H
        self.px_w, self.px_h = px_w, px_h
        self.layers = {}
        self.texts = []
        self.T = [(0.0, 0.0, 1.0)]
        self.fonts = {}
        cd = bpy.data.cameras.new(f"artcam_{Art._n}")
        cd.type = "ORTHO"
        cd.ortho_scale = max(W, H)
        cd.sensor_fit = "AUTO"
        cd.clip_start = 0.01
        cd.clip_end = 1000.0
        cam = bpy.data.objects.new(f"artcam_{Art._n}", cd)
        sc.collection.objects.link(cam)
        cam.location = (W * 0.5, H * 0.5, 100.0)
        sc.camera = cam
        if bg is not None:
            self.rect(-W * 0.01, -H * 0.01, W * 1.01, H * 1.01, bg, z=-1.0)

    # transform stack: local units -> canvas units (offset + uniform scale)
    def map(self, x, y):
        ox, oy, s = self.T[-1]
        return ox + x * s, oy + y * s

    def scale(self):
        return self.T[-1][2]

    @contextmanager
    def region(self, ox, oy, s=1.0):
        pox, poy, ps = self.T[-1]
        self.T.append((pox + ox * ps, poy + oy * ps, ps * s))
        try:
            yield self
        finally:
            self.T.pop()

    def _bm(self, col, z):
        col = rgb(col)
        key = (round(z, 5), tuple(round(x, 4) for x in col))
        bm = self.layers.get(key)
        if bm is None:
            bm = self.layers[key] = bmesh.new()
        return bm

    def poly(self, pts, col, z=0.0, holes=None):
        bm = self._bm(col, z)
        loops = [[self.map(*p) for p in pts]] + [[self.map(*p) for p in h] for h in (holes or [])]
        flat = [p for lp in loops for p in lp]
        if len(flat) < 3:
            return
        vs = [bm.verts.new((p[0], p[1], 0.0)) for p in flat]
        tris = tessellate_polygon([[Vector((p[0], p[1], 0.0)) for p in lp] for lp in loops])
        for t in tris:
            try:
                bm.faces.new((vs[t[0]], vs[t[1]], vs[t[2]]))
            except ValueError:
                pass

    def rect(self, x0, y0, x1, y1, col, z=0.0):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col, z)

    def rrect(self, cx, cy, w, h, r, col, z=0.0, seg=4):
        self.poly(rounded_rect(cx, cy, w, h, r, seg), col, z)

    def frame_rect(self, x0, y0, x1, y1, t, col, z=0.0):
        """An outline rectangle with line thickness t (centred on the edges)."""
        h = t * 0.5
        self.rect(x0 - h, y0 - h, x1 + h, y0 + h, col, z)
        self.rect(x0 - h, y1 - h, x1 + h, y1 + h, col, z)
        self.rect(x0 - h, y0 + h, x0 + h, y1 - h, col, z)
        self.rect(x1 - h, y0 + h, x1 + h, y1 - h, col, z)

    def circle(self, cx, cy, r, col, z=0.0, seg=None):
        if seg is None:
            px = r * self.scale() * self.px_w / self.W
            seg = int(max(8, min(64, px * 2.5)))
        self.poly(circle_pts(cx, cy, r, seg), col, z)

    def ring(self, cx, cy, r0, r1, col, z=0.0, seg=None):
        if seg is None:
            px = r1 * self.scale() * self.px_w / self.W
            seg = int(max(10, min(64, px * 2.5)))
        bm = self._bm(col, z)
        a = [bm.verts.new((*self.map(*p), 0.0)) for p in circle_pts(cx, cy, r0, seg)]
        b = [bm.verts.new((*self.map(*p), 0.0)) for p in circle_pts(cx, cy, r1, seg)]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((a[i], a[j], b[j], b[i]))

    def line(self, pts, w, col, z=0.0, joins=True):
        """Polyline of width w with round joins/caps (joins=True) or square ends."""
        bm = self._bm(col, z)
        hw = w * 0.5
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            nx, ny = -dy / L * hw, dx / L * hw
            q = [self.map(x0 + nx, y0 + ny), self.map(x0 - nx, y0 - ny), self.map(x1 - nx, y1 - ny), self.map(x1 + nx, y1 + ny)]
            vs = [bm.verts.new((p[0], p[1], 0.0)) for p in q]
            bm.faces.new(vs)
        if joins:
            seg = 8 if w * self.scale() * self.px_w / self.W < 6 else 16
            for (x, y) in pts:
                ring = [bm.verts.new((*self.map(*p), 0.0)) for p in circle_pts(x, y, hw, seg)]
                bm.faces.new(ring)

    def font(self, key):
        f = self.fonts.get(key)
        if f is None:
            path = c.font_file(FONTS.get(key, key))
            try:
                f = bpy.data.fonts.load(path, check_existing=True) if path else None
            except Exception:
                f = None
            self.fonts[key] = f
        return f

    def text(self, s, x, y, size, col, z=0.5, font="arialbd", ax="CENTER", ay="CENTER", rot=0.0,
             space=1.0, fit=None, line=1.0, bold=False):
        """Text with cap+descender box height ~ size. fit=max width (local units): shrinks to fit."""
        if not s:
            return None
        cu = bpy.data.curves.new("txt", "FONT")
        cu.body = s
        f = self.font(font)
        if f is not None:
            cu.font = f
        cu.size = size * self.scale()
        cu.align_x = ax
        cu.align_y = ay
        cu.space_character = space
        cu.space_line = line
        cu.resolution_u = 4
        ob = bpy.data.objects.new("txt", cu)
        self.sc.collection.objects.link(ob)
        px, py = self.map(x, y)
        ob.location = (px, py, z)
        ob.rotation_euler = (0.0, 0.0, math.radians(rot))
        lc = [srgb_to_lin(v) for v in rgb(col)]
        ob.color = (lc[0], lc[1], lc[2], 1.0)
        if fit is not None:
            self.sc.view_layers[0].update()
            wdt = ob.dimensions.x
            lim = fit * self.scale()
            if wdt > lim > 0:
                ob.scale = (lim / wdt, 1.0, 1.0)
        self.texts.append(ob)
        return ob

    def text_width(self, s, size, font="arialbd", space=1.0):
        cu = bpy.data.curves.new("tw", "FONT")
        cu.body = s
        f = self.font(font)
        if f is not None:
            cu.font = f
        cu.size = size
        cu.space_character = space
        ob = bpy.data.objects.new("tw", cu)
        self.sc.collection.objects.link(ob)
        self.sc.view_layers[0].update()
        w = ob.dimensions.x
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        return w

    def render(self, path):
        objs = []
        for (z, col), bm in self.layers.items():
            me = bpy.data.meshes.new("artmesh")
            bm.to_mesh(me)
            bm.free()
            ob = bpy.data.objects.new("artmesh", me)
            self.sc.collection.objects.link(ob)
            ob.location.z = z
            lc = [srgb_to_lin(v) for v in col]
            ob.color = (lc[0], lc[1], lc[2], 1.0)
            objs.append(ob)
        self.layers = {}
        self.sc.render.filepath = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.render.render(write_still=True, scene=self.sc.name)
        # clean up
        for ob in list(self.sc.collection.objects):
            data = ob.data
            bpy.data.objects.remove(ob)
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
        bpy.data.scenes.remove(self.sc)
        print("TEXTURE", path)
        return path


class Atlas:
    """Shelf-packs rectangular regions into an Art canvas measured in pixels.
    alloc(w_px, h_px) -> (x0, y0) canvas pixels; uv(rect) -> (u0,v0,u1,v1)."""

    def __init__(self, px_w, px_h, bg=(0, 0, 0)):
        self.art = Art(px_w, px_h, px_w, px_h, bg=bg)
        self.W, self.H = px_w, px_h
        self.x = 0
        self.y = 0
        self.row_h = 0
        self.pad = 4
        self.swatches = {}

    def alloc(self, w, h):
        """Skyline bottom-left packing (with a small gutter between regions)."""
        w, h = int(math.ceil(w)), int(math.ceil(h))
        ww, hh = w + self.pad, h + self.pad
        if not hasattr(self, "sky"):
            self.sky = [(0, self.W, 0)]  # (x, width, y)
        best = None
        for i in range(len(self.sky)):
            x = self.sky[i][0]
            if x + ww > self.W + self.pad:
                break
            # the height needed over the span [x, x + ww)
            y = 0
            span = 0
            j = i
            while span < ww and j < len(self.sky):
                y = max(y, self.sky[j][2])
                span += self.sky[j][1]
                j += 1
            if span < ww and x + span < self.W:
                continue
            if y + h > self.H:
                continue
            if best is None or y < best[1] or (y == best[1] and x < best[0]):
                best = (x, y)
        if best is None:
            raise RuntimeError(f"atlas full ({w}x{h})")
        x0, y0 = best
        # update the skyline: replace the covered span with one segment at y0 + hh
        new = []
        x1 = x0 + ww
        for (sx, sw, sy) in self.sky:
            ex = sx + sw
            if ex <= x0 or sx >= x1:
                new.append((sx, sw, sy))
                continue
            if sx < x0:
                new.append((sx, x0 - sx, sy))
            if ex > x1:
                new.append((x1, ex - x1, sy))
        new.append((x0, min(ww, self.W - x0), y0 + hh))
        new.sort()
        merged = []
        for seg in new:
            if merged and merged[-1][2] == seg[2] and merged[-1][0] + merged[-1][1] == seg[0]:
                merged[-1] = (merged[-1][0], merged[-1][1] + seg[1], seg[2])
            else:
                merged.append(seg)
        self.sky = merged
        return x0, y0, w, h

    def uv(self, rect, inset=0.5):
        x0, y0, w, h = rect
        return ((x0 + inset) / self.W, (y0 + inset) / self.H, (x0 + w - inset) / self.W, (y0 + h - inset) / self.H)

    def swatch(self, col):
        """A flat-colour patch; returns a Swatch mapper for faces in that colour."""
        key = tuple(round(v, 4) for v in rgb(col))
        s = self.swatches.get(key)
        if s is None:
            r = self.alloc(12, 12)
            self.art.rect(r[0], r[1], r[0] + r[2], r[1] + r[3], col, z=0.1)
            s = self.swatches[key] = Swatch(((r[0] + 6) / self.W, (r[1] + 6) / self.H))
        return s

    def panel(self, w_mm, h_mm, ppm, bg=None):
        """Allocates a region for w_mm x h_mm at ppm px/mm; returns (rect, uv, ctx) where ctx is a context
        manager drawing in local millimetres with (0,0) at the region's bottom-left."""
        r = self.alloc(w_mm * ppm, h_mm * ppm)
        if bg is not None:
            self.art.rect(r[0], r[1], r[0] + r[2], r[1] + r[3], bg, z=0.05)
        sx = r[2] / w_mm
        return r, self.uv(r), self.art.region(r[0], r[1], sx)

    def render(self, path):
        return self.art.render(path)


def tex_path(name):
    return os.path.join(c.TEXTURES, name + ".png")


# ------------------------------------------------------------------ common board-level components

def smd_passive(k, x, y, z0, L, W, H, ang=0.0, body="ceramic", term="solder", up=(0, 0, 1)):
    """Chip capacitor / resistor lying on a surface at height z0 (Unity), rotated ang degrees about z."""
    M = rot("z", ang)
    t = min(L * 0.22, 0.0004)
    box(k[body], (x, y, z0 + H * 0.5), (L - 2 * t, W * 0.98, H * 0.96), M)
    for s in (-1, 1):
        off = M @ Vector((s * (L * 0.5 - t * 0.5), 0, 0))
        box(k[term], (x + off.x, y + off.y, z0 + H * 0.5), (t, W, H), M)


def chip_marked(g, x, y, z0, L, W, H, region, black_swatch, ang=0.0, bevel=0.00015, text_rot=0.0):
    """A moulded IC package (L along its local x, W along y, rotated ang about z) whose top face carries a
    marking region of the atlas; text_rot turns the marking relative to the package (0/90/180/270)."""
    M = rot("z", ang)
    up = M @ (rot("z", text_rot) @ Vector((0, 1, 0)))
    size = (L, W) if abs(math.sin(math.radians(text_rot))) < 0.5 else (W, L)
    mapper = MultiMap([Planar(region, (x, y, z0 + H), (0, 0, 1), up, size), black_swatch])
    box(g, (x, y, z0 + H * 0.5), (L, W, H), M, bevel=bevel, uv=mapper)


class MultiMap:
    def __init__(self, maps):
        self.maps = maps

    def __call__(self, n, pts):
        for m in self.maps:
            r = m(n, pts)
            if r is not None:
                return r
        return None


def gull_leads(g, x, y, z0, L, W, n_side, pitch, sides=2, lead_len=0.0009, lead_w=None, ang=0.0, lead_h=0.00018):
    """Gull-wing leads for a package of size L (local x) by W (local y): sides=2 puts n_side leads on each
    long edge (SOIC/TSOP along the +-y edges), sides=4 on all four edges (QFP)."""
    M = rot("z", ang)
    lw = lead_w or pitch * 0.5
    def put(cx, cy, sx, sy):
        o = M @ Vector((cx, cy, 0))
        box(g, (x + o.x, y + o.y, z0 + lead_h * 0.5), (sx, sy, lead_h), M)
    for i in range(n_side):
        t = (i - (n_side - 1) * 0.5) * pitch
        for s in (-1, 1):
            put(t, s * (W * 0.5 + lead_len * 0.5), lw, lead_len)
            if sides == 4:
                put(s * (L * 0.5 + lead_len * 0.5), t, lead_len, lw)


# ------------------------------------------------------------------ preview (EEVEE, textured)

PREVIEW_PBR = {
    # tag: (metallic, roughness)
    "gold": (1.0, 0.22), "copper": (1.0, 0.3), "steel": (1.0, 0.32), "steel_dark": (1.0, 0.4), "alu": (1.0, 0.35),
    "alu_dark": (0.9, 0.42), "nickel": (1.0, 0.22), "solder": (1.0, 0.3), "black_plastic": (0.0, 0.45),
    "dark_plastic": (0.0, 0.5), "grey_plastic": (0.0, 0.5), "white_plastic": (0.0, 0.45), "rubber": (0.0, 0.8),
    "connector_black": (0.0, 0.55), "connector_white": (0.0, 0.5), "connector_beige": (0.0, 0.55),
    "pcb_green": (0.0, 0.45), "pcb_black": (0.0, 0.5), "ceramic": (0.0, 0.5), "chip_black": (0.0, 0.55),
    "thermal_pad": (0.0, 0.7), "film_blue": (0.0, 0.25), "paint_black": (0.2, 0.45), "paint_white": (0.1, 0.4),
    "glass": (0.0, 0.05), "rgb": (0.0, 0.35), "paste": (0.0, 0.6),
}
PREVIEW_TEX = {}  # tex file -> (metallic, roughness); default (0, 0.45)


def _preview_materials():
    for m in bpy.data.materials:
        nt = m.node_tree
        if nt is None:
            continue
        b = nt.nodes.get("Principled BSDF")
        if b is None:
            continue
        tag = m.name
        if tag.startswith("tex_"):
            path = tex_path(tag[4:])
            met, rough = PREVIEW_TEX.get(tag[4:], (0.0, 0.45))
            if os.path.exists(path):
                img = bpy.data.images.load(path, check_existing=True)
                tn = nt.nodes.new("ShaderNodeTexImage")
                tn.image = img
                tn.interpolation = "Cubic"
                nt.links.new(tn.outputs["Color"], b.inputs["Base Color"])
        else:
            col = c.TAGS.get(tag, (0.5, 0.5, 0.5))
            b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
            met, rough = PREVIEW_PBR.get(tag, (0.0, 0.5))
            if tag.startswith("led_"):
                met, rough = 0.0, 0.2
                b.inputs["Base Color"].default_value = (col[0] * 0.6, col[1] * 0.6, col[2] * 0.6, 1.0)
        b.inputs["Metallic"].default_value = met
        b.inputs["Roughness"].default_value = rough


def _preview_world(sc):
    w = bpy.data.worlds.new("preview_world")
    sc.world = w
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    hdri = os.path.join(os.path.dirname(bpy.app.binary_path), "%d.%d" % bpy.app.version[:2], "datafiles", "studiolights", "world", "interior.exr")
    if os.path.exists(hdri):
        env.image = bpy.data.images.load(hdri, check_existing=True)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    plain = nt.nodes.new("ShaderNodeBackground")
    plain.inputs["Color"].default_value = (0.045, 0.047, 0.05, 1.0)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mixn = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mixn.inputs[0])
    nt.links.new(bg.outputs[0], mixn.inputs[1])
    nt.links.new(plain.outputs[0], mixn.inputs[2])
    nt.links.new(mixn.outputs[0], out.inputs["Surface"])


def preview(root_obj, filename, views=((35, 30), (-40, 55)), size=(960, 720), dist=None, target=None, lens=50,
            start=0, zup=False):
    """EEVEE previews with the textures applied, to Logs/ModelPreviews/<filename>_<i>.png.
    views: (yaw, pitch) degrees in Unity terms around `target` (Unity point) or the bounds centre."""
    sc = bpy.context.scene
    _preview_materials()
    _preview_world(sc)
    sc.render.engine = "BLENDER_EEVEE"
    try:
        sc.eevee.use_raytracing = True
        sc.eevee.taa_render_samples = 32
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    pts = []
    for o in c.descendants(root_obj):
        if o.type == "MESH":
            pts += [o.matrix_world @ Vector(cc) for cc in o.bound_box]
    if not pts:
        return []
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = c.conv(target) if target is not None else (lo + hi) * 0.5
    radius = (hi - lo).length * 0.5
    sun_d = bpy.data.lights.new("preview_sun", "SUN")
    sun_d.energy = 2.5
    sun_d.angle = math.radians(8)
    sun = c.link(bpy.data.objects.new("preview_sun", sun_d))
    sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(35))
    cam_data = bpy.data.cameras.new("preview_cam")
    cam_data.lens = lens
    cam_data.clip_start = 0.001
    cam_data.clip_end = 100
    cam = c.link(bpy.data.objects.new("preview_cam", cam_data))
    sc.camera = cam
    out = []
    for i, (yaw, pitch) in enumerate(views):
        d = dist or radius * 3.2 * 50.0 / lens
        y, p = yaw * c.DEG, pitch * c.DEG
        if zup:
            # parts whose 'up' is Unity +z (boards, CPUs): yaw 0 looks from -y, pitch lifts toward +z
            u = Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))
            upv = c.conv((0, 0, 1))
        else:
            u = Vector((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
            upv = c.conv((0, 1, 0))
        cam.location = centre + c.conv(u) * d
        fwd = (centre - cam.location).normalized()
        right = fwd.cross(upv)
        if right.length < 1e-6:
            right = fwd.cross(c.conv((0, 1, 0)) if zup else c.conv((0, 0, 1)))
        right.normalize()
        upc = right.cross(fwd).normalized()
        cam.matrix_world = Matrix((right, upc, -fwd)).transposed().to_4x4()
        cam.location = centre + c.conv(u) * d
        path = os.path.join(c.PREVIEWS, f"{filename}_{start + i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)
    return out


def tri_count(root_obj):
    n = 0
    for o in c.descendants(root_obj):
        if o.type == "MESH":
            for p in o.data.polygons:
                n += len(p.vertices) - 2
    return n


def validate(root_obj):
    """Checks the export contract: every mesh named '<name>#<tag>' within Blender's 63-character limit (a
    longer name is silently truncated, which breaks the tag), one material per mesh, the tag known."""
    bad = []
    for o in c.descendants(root_obj):
        if o.type != "MESH":
            continue
        tag = o.name.split("#", 1)[1] if "#" in o.name else None
        if tag is None or len(o.name) >= 63 or "." in tag or len(o.data.materials) != 1 or o.data.materials[0].name != tag:
            bad.append(o.name)
        elif not (tag in c.TAGS or tag.startswith("tex_")):
            bad.append(o.name + " (unknown tag)")
    for o in c.descendants(root_obj):
        if o.type == "EMPTY" and o.name.startswith("A_") and len(o.name) >= 63:
            bad.append(o.name)
    if bad:
        print("VALIDATION FAILED", root_obj.name, bad)
    else:
        print("VALIDATION OK", root_obj.name)
    return not bad


def report(root_obj):
    """Prints the triangle count and every anchor (name, Unity position, size, meta) for the final report."""
    validate(root_obj)
    print(f"REPORT {root_obj.name} tris={tri_count(root_obj)} objects={sum(1 for o in c.descendants(root_obj) if o.type == 'MESH')}")
    for o in sorted(c.descendants(root_obj), key=lambda o: o.name):
        if o.type == "EMPTY" and o.name.startswith("A_"):
            p = unconv(o.matrix_world.translation)
            print(f"ANCHOR {root_obj.name} {o.name} pos=({p.x:.5f},{p.y:.5f},{p.z:.5f}) size={o.get('size')} meta={o.get('meta', '')}")
