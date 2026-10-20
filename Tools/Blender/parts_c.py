"""
parts_c: helpers for the cases, retail boxes, plugs, small items and the bench monitor.

Builds on dct_common (UNITY coordinates everywhere; conversion happens inside). Adds:
  * Frame: a local frame (origin, forward = local +Z, up = local +Y) like dct_common anchors use.
    Geometry is modelled in a frame's local (a, b, c) = (x, y, z) and mapped to Unity, then to Blender.
  * slab(): extruded 2D outlines WITH HOLES (via a filled 2D curve), for sheet metal, cut-outs, grilles,
    profiles. bent(): a sheet-metal cross-section with real bend radii, swept along a direction.
  * lathe(): surfaces of revolution (screws, knobs, standoffs, LEDs, buttons); cube(), cylinder().
  * text3d(): real 3D lettering from a Windows TTF (logos, embossed prints).
  * Unique object names (Blender would append ".001", which breaks the "#tag" suffix).
  * finalize(): joins static meshes per tag and moving pieces per (anchor, tag), and puts each moving
    piece's pivot on its anchor.
  * beauty(): Cycles renders with physically based stand-ins for the tags (and the tex_ PNGs).
  * Art: a 2D layout renderer (rects, gradients, text, images, barcodes) for printed artwork.
  * palette texture: one PNG of colour swatches, so wires and small prints get real colours while
    keeping one material per object.
"""
import bmesh
import bpy
import math
import os
import sys
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402

DEG = math.pi / 180.0
FONTS = r"C:\Windows\Fonts"
STUDIO_HDRI = None
for _cand in (r"D:\New folder\5.0\datafiles\studiolights\world\studio.exr",
              os.path.join(os.path.dirname(bpy.app.binary_path), "%d.%d" % bpy.app.version[:2], "datafiles",
                           "studiolights", "world", "studio.exr")):
    if STUDIO_HDRI is None and os.path.exists(_cand):
        STUDIO_HDRI = _cand

_names = {}
PREVIEW = [True]   # build_parts_c.py --nopreview turns the preview renders off


def reset():
    """dct_common.reset() plus this module's state."""
    c.reset()
    _names.clear()
    _fonts.clear()


def shash(text):
    """A stable hash (Python's hash() changes every run)."""
    import zlib
    return zlib.crc32(str(text).encode("utf-8")) & 0x7fffffff


def uname(base):
    """A unique object base name (the '#tag' suffix must never get Blender's '.001')."""
    n = _names.get(base, 0)
    _names[base] = n + 1
    return base if n == 0 else f"{base}_{n}"


# ---------------------------------------------------------------- frames

def vec(v):
    return Vector((float(v[0]), float(v[1]), float(v[2])))


class Frame:
    """origin + axes in Unity space. Local +Z = forward, +Y = up, +X = up x forward (as dct_common.basis)."""

    def __init__(self, o=(0, 0, 0), fwd=(0, 0, 1), up=(0, 1, 0)):
        w = vec(fwd).normalized()
        v = vec(up).normalized()
        u = v.cross(w)
        if u.length < 1e-9:
            raise ValueError("forward and up are parallel")
        u.normalize()
        v = w.cross(u).normalized()
        self.o, self.u, self.v, self.w = vec(o), u, v, w

    def p(self, a=0.0, b=0.0, cc=0.0):
        return self.o + self.u * a + self.v * b + self.w * cc

    def d(self, a=0.0, b=0.0, cc=0.0):
        return self.u * a + self.v * b + self.w * cc

    def sub(self, a=0.0, b=0.0, cc=0.0, fwd=(0, 0, 1), up=(0, 1, 0)):
        """A child frame at a local point, with axes given in this frame's local directions."""
        return Frame(self.p(a, b, cc), self.d(*fwd), self.d(*up))

    @property
    def fwd(self):
        return tuple(self.w)

    @property
    def up(self):
        return tuple(self.v)


WORLD = Frame()
X, Y, Z = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
NX, NY, NZ = (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)


def plane(o, a, b):
    """A frame whose local X is Unity direction a, local Y is b and local Z is a x b (the sheet normal).
    With o on an axis plane, 2D outlines can be written in absolute Unity coordinates along a and b."""
    a, b = vec(a).normalized(), vec(b).normalized()
    return Frame(o, a.cross(b), b)


def F(o=(0, 0, 0), fwd=(0, 0, 1), up=(0, 1, 0)):
    return Frame(o, fwd, up)


# ---------------------------------------------------------------- 2D outlines (local a, b)

def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def rrect(w, h, r=0.0, cx=0.0, cy=0.0, seg=4):
    """A rounded rectangle, counter-clockwise."""
    r = max(0.0, min(r, w * 0.5 - 1e-6, h * 0.5 - 1e-6))
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    if r <= 1e-7:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    pts += arc(x1 - r, y0 + r, r, -math.pi / 2, 0, seg)
    pts += arc(x1 - r, y1 - r, r, 0, math.pi / 2, seg)
    pts += arc(x0 + r, y1 - r, r, math.pi / 2, math.pi, seg)
    pts += arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi, seg)
    return pts


def circle(r, cx=0.0, cy=0.0, n=16, rot=0.0):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def stadium(w, h, cx=0.0, cy=0.0, seg=5):
    """A slot with round ends; long along a if w > h."""
    if w >= h:
        r = h / 2
        return arc(cx + w / 2 - r, cy, r, -math.pi / 2, math.pi / 2, seg) + arc(cx - w / 2 + r, cy, r, math.pi / 2, 1.5 * math.pi, seg)
    r = w / 2
    return arc(cx, cy + h / 2 - r, r, 0, math.pi, seg) + arc(cx, cy - h / 2 + r, r, math.pi, 2 * math.pi, seg)


def hexagon(r, cx=0.0, cy=0.0, rot=0.0):
    return circle(r, cx, cy, 6, rot)


def hex_grid(region_pts_test, pitch, r_hole, a0, a1, b0, b1, rot=math.pi / 6):
    """Hexagonal holes on a staggered grid inside [a0,a1]x[b0,b1] where region_pts_test(a, b, rr) is True."""
    holes = []
    dy = pitch * math.sqrt(3) / 2
    row = 0
    b = b0
    while b <= b1 + 1e-9:
        off = (pitch / 2) if row % 2 else 0.0
        a = a0 + off
        while a <= a1 + 1e-9:
            if region_pts_test(a, b, r_hole):
                holes.append(hexagon(r_hole, a, b, rot))
            a += pitch
        b += dy
        row += 1
    return holes


def poly_offset(pts, d):
    """Offsets a closed CCW polygon outward by d (miter, fine for gentle shapes)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0 = (p1 - p0).normalized()
        e1 = (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x))
        n1 = Vector((e1.y, -e1.x))
        m = (n0 + n1)
        if m.length < 1e-9:
            m = n0
        m.normalize()
        k = max(0.3, m.dot(n0))
        q = p1 + m * (d / k)
        out.append((q.x, q.y))
    return out


def fillet_path(path, rc, seg=5):
    """An open polyline with every interior corner rounded to radius rc (centreline)."""
    if len(path) < 3 or rc <= 0:
        return [tuple(p) for p in path]
    out = [tuple(path[0])]
    for i in range(1, len(path) - 1):
        a, b, cc = Vector(path[i - 1]), Vector(path[i]), Vector(path[i + 1])
        d1 = (b - a).normalized()
        d2 = (cc - b).normalized()
        cosang = max(-1.0, min(1.0, d1.dot(d2)))
        theta = math.acos(cosang)  # turning angle
        if theta < 1e-4:
            out.append((b.x, b.y))
            continue
        t = rc * math.tan(theta / 2)
        t = min(t, (b - a).length * 0.49, (cc - b).length * 0.49)
        r = t / math.tan(theta / 2)
        t1 = b - d1 * t
        cross = d1.x * d2.y - d1.y * d2.x
        nrm = Vector((-d1.y, d1.x)) if cross > 0 else Vector((d1.y, -d1.x))
        cen = t1 + nrm * r
        s0 = math.atan2(t1.y - cen.y, t1.x - cen.x)
        t2 = b + d2 * t
        s1 = math.atan2(t2.y - cen.y, t2.x - cen.x)
        ds = s1 - s0
        while ds > math.pi:
            ds -= 2 * math.pi
        while ds < -math.pi:
            ds += 2 * math.pi
        for k in range(seg + 1):
            s = s0 + ds * k / seg
            out.append((cen.x + r * math.cos(s), cen.y + r * math.sin(s)))
    out.append(tuple(path[-1]))
    return out


def thick_path(path, t, r_inner=0.001, seg=5, side=0.0):
    """Closed outline of a bent sheet whose centreline is path (open polyline, sharp corners).
    Corners get a bend with inner radius r_inner. side shifts the sheet: 0 centred, +1 entirely left
    of the path (left of the walking direction), -1 entirely right."""
    cl = fillet_path(path, r_inner + t / 2, seg)
    n = len(cl)
    left, right = [], []
    for i in range(n):
        p = Vector(cl[i])
        if i == 0:
            d = (Vector(cl[1]) - p).normalized()
        elif i == n - 1:
            d = (p - Vector(cl[i - 1])).normalized()
        else:
            d = (Vector(cl[i + 1]) - Vector(cl[i - 1])).normalized()
        nl = Vector((-d.y, d.x))
        lo = -t / 2 + side * t / 2
        hi = t / 2 + side * t / 2
        left.append(p + nl * hi)
        right.append(p + nl * lo)
    pts = [(q.x, q.y) for q in left] + [(q.x, q.y) for q in reversed(right)]
    return pts


# ---------------------------------------------------------------- bmesh building

def _curve_bm(splines, extrude, kind="CURVE", text=None, size=1.0, font=None, align="CENTER", spacing=1.0,
              resolution=3):
    if kind == "FONT":
        cu = bpy.data.curves.new("tmp_font", "FONT")
        cu.body = text
        cu.size = size
        cu.align_x = align
        cu.align_y = "CENTER"
        cu.space_character = spacing
        cu.resolution_u = resolution
        if font is not None:
            cu.font = font
    else:
        cu = bpy.data.curves.new("tmp_curve", "CURVE")
        cu.dimensions = "2D"
        cu.resolution_u = 1
        for pts in splines:
            sp = cu.splines.new("POLY")
            sp.points.add(len(pts) - 1)
            for i, p in enumerate(pts):
                sp.points[i].co = (p[0], p[1], 0.0, 1.0)
            sp.use_cyclic_u = True
    cu.fill_mode = "BOTH" if kind == "CURVE" else cu.fill_mode
    cu.extrude = extrude
    ob = bpy.data.objects.new("tmp_curve_obj", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    if kind == "FONT":
        bpy.data.curves.remove(cu)
    else:
        bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    return bm


def _uv_planar(bm, region, bounds, flip_u=False, flip_v=False, only_normal=None):
    """UVs from local (a, b): bounds (a0, b0, a1, b1) -> region (u0, v0, u1, v1).
    Faces whose local normal z is opposite to only_normal (+1/-1) get a corner pixel of the region."""
    uvl = bm.loops.layers.uv.verify()
    a0, b0, a1, b1 = bounds
    u0, v0, u1, v1 = region
    for f in bm.faces:
        for lp in f.loops:
            x, y = lp.vert.co.x, lp.vert.co.y
            s = (x - a0) / max(1e-9, a1 - a0)
            t = (y - b0) / max(1e-9, b1 - b0)
            if flip_u:
                s = 1 - s
            if flip_v:
                t = 1 - t
            lp[uvl].uv = (u0 + (u1 - u0) * s, v0 + (v1 - v0) * t)


def _uv_solid(bm, uv):
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = uv


def _place(bm, frame):
    for v in bm.verts:
        v.co = c.conv(frame.p(v.co.x, v.co.y, v.co.z))


def emit(name, bm, frame, tag, parent=None, smooth=None, recalc=True, uv=None, uv_bounds=None, uv_solid=None,
         flip_u=True, flip_v=False, hint=None):
    """Turns a local-space bmesh into a finished '<name>#<tag>' object (Unity frame -> Blender).
    uv: planar UVs from local (x, y). Unity is left-handed: seen from the frame's +Z side, local -X is on
    the viewer's right, so by default (flip_u) u runs toward -X and the image reads correctly from +Z."""
    if uv is not None:
        if uv_bounds is None:
            xs = [v.co.x for v in bm.verts]
            ys = [v.co.y for v in bm.verts]
            uv_bounds = (min(xs), min(ys), max(xs), max(ys))
        _uv_planar(bm, uv, uv_bounds, flip_u, flip_v)
    elif uv_solid is not None:
        _uv_solid(bm, uv_solid)
    _place(bm, frame)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if hint is not None:
        bm.normal_update()
        h = c.conv(hint)
        tot = Vector((0, 0, 0))
        for f in bm.faces:
            tot += f.normal * f.calc_area()
        if tot.dot(h) < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
    nm = uname(name)
    obj = c.mesh_object(nm, bm)
    return c.finish(obj, nm, tag, parent, smooth_angle=smooth)


def slab(name, outline, depth, tag, frame=WORLD, holes=(), parent=None, smooth=None, **kw):
    """A 2D outline with holes in the frame's local XY plane, extruded by depth along local Z (centred)."""
    bm = _curve_bm([outline] + list(holes), depth / 2)
    return emit(name, bm, frame, tag, parent, smooth, **kw)


def bent(name, path, t, length, tag, frame=WORLD, r_inner=0.001, side=0.0, parent=None, seg=5, **kw):
    """Sheet metal with bends: the cross-section path (local XY, open polyline) gets thickness t and
    bend radii, then is swept along local Z by length (centred)."""
    outline = thick_path(path, t, r_inner, seg, side)
    bm = _curve_bm([outline], length / 2)
    return emit(name, bm, frame, tag, parent, smooth=40, **kw)


def cube(name, center, size, tag, frame=WORLD, parent=None, bevel=0.0, seg=2, **kw):
    """A box in a frame's local axes; center is local."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        b = min(bevel, min(size) * 0.49)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    return emit(name, bm, frame, tag, parent, smooth=35 if bevel > 0 else None, **kw)


def lathe_bm(profile, segs=24, rot=0.0):
    """Surface of revolution around local Z. profile: [(radius, z), ...] from one end to the other;
    radius 0 makes a pole (closed end)."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-9:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(rot + 2 * math.pi * k / segs), r * math.sin(rot + 2 * math.pi * k / segs), z))
                          for k in range(segs)])
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(segs):
            k2 = (k + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[k], B[k2]))
            elif len(B) == 1:
                bm.faces.new((A[k], B[0], A[k2]))
            else:
                bm.faces.new((A[k], B[k], B[k2], A[k2]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-8)
    return bm


def lathe(name, profile, tag, frame=WORLD, segs=24, parent=None, smooth=40, rot=0.0, **kw):
    return emit(name, lathe_bm(profile, segs, rot), frame, tag, parent, smooth, **kw)


def loft(name, sections, tag, frame=WORLD, parent=None, smooth=50, caps=(True, True), **kw):
    """A smooth skin through outlines: sections = [(outline, z), ...] in the frame's local XY at local z,
    every outline with the same vertex count (CCW). Caps close the first and last section."""
    bm = bmesh.new()
    rings = [[bm.verts.new((p[0], p[1], z)) for p in pts] for pts, z in sections]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if caps[0]:
        f = bm.faces.new(list(reversed(rings[0])))
        bmesh.ops.triangulate(bm, faces=[f])
    if caps[1]:
        f = bm.faces.new(rings[-1])
        bmesh.ops.triangulate(bm, faces=[f])
    return emit(name, bm, frame, tag, parent, smooth, **kw)


def cylinder(name, frame, r, h, tag, segs=24, parent=None, z0=None, r2=None, smooth=40, **kw):
    """A closed cylinder along the frame's local Z, from z0 (default -h/2) to z0 + h."""
    z0 = -h / 2 if z0 is None else z0
    r2 = r if r2 is None else r2
    prof = [(0, z0), (r, z0), (r2, z0 + h), (0, z0 + h)]
    return lathe(name, prof, tag, frame, segs, parent, smooth, **kw)


def ring_bm(r_out, r_in, h, segs=24, z0=0.0):
    return lathe_bm([(r_in, z0), (r_out, z0), (r_out, z0 + h), (r_in, z0 + h), (r_in, z0)], segs)


def quad(name, frame, w, h, tag, parent=None, uv=(0, 0, 1, 1), flip_u=True):
    """A single quad in the frame's local XY plane, facing local +Z, UV 0..1; reads correctly from +Z."""
    bm = bmesh.new()
    vs = [bm.verts.new((-w / 2, -h / 2, 0)), bm.verts.new((w / 2, -h / 2, 0)), bm.verts.new((w / 2, h / 2, 0)),
          bm.verts.new((-w / 2, h / 2, 0))]
    bm.faces.new(vs)
    return emit(name, bm, frame, tag, parent, None, recalc=False, uv=uv, uv_bounds=(-w / 2, -h / 2, w / 2, h / 2),
                flip_u=flip_u, hint=frame.w)


_fonts = {}


def font(file="arialbd.ttf"):
    if file in _fonts and _fonts[file] is not None:
        try:
            _fonts[file].name
            return _fonts[file]
        except ReferenceError:
            pass
    path = c.font_file(os.path.join(FONTS, file))
    f = bpy.data.fonts.load(path, check_existing=True) if path else None
    _fonts[file] = f
    return f


def text_bm(text, size, depth, fontfile="arialbd.ttf", align="CENTER", spacing=1.0, resolution=3, width=None):
    bm = _curve_bm(None, depth / 2, kind="FONT", text=text, size=size, font=font(fontfile), align=align,
                   spacing=spacing, resolution=resolution)
    # Unity is left-handed: seen from +Z, -X is on the viewer's right, so mirror the glyphs to read correctly.
    bmesh.ops.scale(bm, vec=Vector((-1.0, 1.0, 1.0)), verts=bm.verts)
    if width is not None and len(bm.verts):
        xs = [v.co.x for v in bm.verts]
        w = max(xs) - min(xs)
        if w > width:
            k = width / w
            bmesh.ops.scale(bm, vec=Vector((k, k, 1.0)), verts=bm.verts)
    # centre vertically on the glyph box
    if len(bm.verts):
        ys = [v.co.y for v in bm.verts]
        cy = (max(ys) + min(ys)) / 2
        bmesh.ops.translate(bm, vec=Vector((0, -cy, 0)), verts=bm.verts)
    return bm


def text3d(name, text, size, depth, tag, frame, fontfile="arialbd.ttf", align="CENTER", parent=None, width=None,
           spacing=1.0, resolution=3, z=0.0):
    """Raised lettering in the frame's XY plane, standing out along +Z from z; reads correctly (left to right,
    +Y up) when seen from the frame's +Z side."""
    bm = text_bm(text, size, depth, fontfile, align, spacing, resolution, width)
    bmesh.ops.translate(bm, vec=Vector((0, 0, z + depth / 2)), verts=bm.verts)
    return emit(name, bm, frame, tag, parent, None)


def tube(name, points, radius, tag, parent=None, verts=8, uv_solid=None):
    """dct_common.tube with unique names and an optional solid UV (palette colour)."""
    nm = uname(name)
    obj = c.tube(nm, points, radius, tag, parent, verts)
    if uv_solid is not None:
        me = obj.data
        if not me.uv_layers:
            me.uv_layers.new(name="UVMap")
        for d in me.uv_layers.active.data:
            d.uv = uv_solid
    return obj


def smooth_path(points, n=6):
    """Catmull-Rom through Unity points (cables)."""
    P = [vec(p) for p in points]
    if len(P) < 3:
        return P
    out = []
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i > 0 else P[i] * 2 - P[i + 1]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else P[i + 1] * 2 - P[i]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return out


# ---------------------------------------------------------------- anchors, pieces, joining

def anchor(name, frame_or_pos, size=(0.01, 0.01, 0.01), parent=None, meta=None, fwd=None, up=None):
    if isinstance(frame_or_pos, Frame):
        pos, f, u = tuple(frame_or_pos.o), frame_or_pos.fwd, frame_or_pos.up
    else:
        pos, f, u = frame_or_pos, (0, 0, 1), (0, 1, 0)
    if fwd is not None:
        f = fwd
    if up is not None:
        u = up
    return c.anchor(name, pos, size, parent, f, u, meta)


def anchor_frame(a):
    """The Unity frame of an anchor empty."""
    m = a.matrix_world
    o = Vector((-m.translation.x, m.translation.z, -m.translation.y))
    bz = m.to_3x3().col[2]
    by = m.to_3x3().col[1]
    up = Vector((-bz.x, bz.z, -bz.y))   # Blender local Z = Unity up
    fwd = Vector((by.x, -by.z, by.y))   # Blender local Y = -Unity forward
    return Frame(o, fwd, up)


def _tag_of(name):
    t = name.split("#", 1)[1] if "#" in name else "untagged"
    if "." in t and t.rsplit(".", 1)[1].isdigit():
        t = t.rsplit(".", 1)[0]
    return t


def _join(obs):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


UV_METRES = 0.1  # plain-tag meshes: box-projected UVs, one UV unit per 0.1 m (same as parts_b)


def box_uv(ob):
    """World-space box projection in Unity axes, 1 UV unit = 0.1 m (detail textures tile at real scale)."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uvl = me.uv_layers.active.data
    mw = ob.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    for poly in me.polygons:
        n = nm @ poly.normal
        nu = Vector((-n.x, n.z, -n.y))
        ax = max(range(3), key=lambda i: abs(nu[i]))
        for li in poly.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            u3 = (-co.x, co.z, -co.y)
            if ax == 0:
                uv = (u3[2] * (-1 if nu.x > 0 else 1), u3[1])
            elif ax == 1:
                uv = (u3[0], u3[2])
            else:
                uv = (u3[0] * (1 if nu.z > 0 else -1), u3[1])
            uvl[li].uv = (uv[0] / UV_METRES, uv[1] / UV_METRES)


def finalize(root, prefix):
    """Joins statics per tag and moving pieces per (anchor, tag); pivots moving pieces on their anchor.
    Plain-tag meshes get box-projected UVs first (tex_ meshes keep their own 0..1 UVs)."""
    anchors = {o.name: o for o in c.descendants(root) if o.type == "EMPTY" and o.name.startswith("A_")}
    for ob in c.descendants(root):
        if ob.type == "MESH" and not _tag_of(ob.name).startswith("tex_"):
            box_uv(ob)
    statics, pieces = {}, {}
    for ob in list(root.children):
        if ob.type != "MESH":
            continue
        tag = _tag_of(ob.name)
        if "@" in ob.name:
            anc = ob.name.split("#", 1)[0].split("@", 1)[1]
            pieces.setdefault((anc, tag), []).append(ob)
        else:
            statics.setdefault(tag, []).append(ob)
    for tag, obs in statics.items():
        j = _join(obs)
        nm = f"{prefix}_{tag}#{tag}"
        if len(nm) > 63:   # keep names inside Blender's classic limit (its FBX importer hashes longer ones)
            nm = f"s_{tag}#{tag}"
        j.name = nm
        j.data.name = j.name
    for (anc, tag), obs in pieces.items():
        j = _join(obs)
        nm = anc.split("@", 1)[0][2:].lower()
        if len(f"{nm}@{anc}#{tag}") > 63:
            nm = "p"
        j.name = f"{nm}@{anc}#{tag}"
        j.data.name = j.name
        a = anchors.get(anc)
        if a is not None:
            mw = j.matrix_world.copy()
            am = a.matrix_world.copy()
            j.data.transform(am.inverted() @ mw)
            j.matrix_world = am
    # every object must carry exactly one material
    for ob in c.descendants(root):
        if ob.type == "MESH" and len(ob.data.materials) != 1:
            print("WARNING material count", ob.name, len(ob.data.materials))


def stats(root):
    tris = 0
    meshes = 0
    for o in c.descendants(root):
        if o.type == "MESH":
            meshes += 1
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return tris, meshes


def anchor_report(root):
    out = []
    for o in sorted(c.descendants(root), key=lambda x: x.name):
        if o.type == "EMPTY" and o.name.startswith("A_"):
            f = anchor_frame(o)
            out.append((o.name, tuple(round(x, 5) for x in f.o), tuple(round(x, 3) for x in f.w),
                        tuple(round(x, 3) for x in f.v), o.get("size", ""), o.get("meta", "")))
    return out


def write_report(root, model_id, extra=None):
    tris, meshes = stats(root)
    path = os.path.join(c.PREVIEWS, f"{model_id}_report.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"{model_id}: {tris} triangles, {meshes} meshes\n")
        for o in sorted(c.descendants(root), key=lambda x: x.name):
            if o.type == "MESH":
                fh.write(f"  mesh {o.name}  tris={sum(len(p.vertices) - 2 for p in o.data.polygons)}\n")
        for n, p, fw, up, s, m in anchor_report(root):
            fh.write(f"  {n} pos={p} fwd={fw} up={up} size={s} meta={m}\n")
        if extra:
            fh.write(extra + "\n")
    print(f"REPORT {model_id}: {tris} tris, {meshes} meshes -> {path}")
    return tris, meshes


def preview(root, filename, views=((35, 30), (-40, 55)), size=(960, 720), dist=None):
    """dct_common.preview with back-face culling on (Unity culls back faces: a hole means a flipped face)."""
    if not PREVIEW[0]:
        return []
    sc = bpy.context.scene
    sc.display.shading.show_backface_culling = True
    mine = set(c.descendants(root))
    hidden = [o for o in sc.objects if o.type in ("MESH", "CURVE", "FONT") and o not in mine and not o.hide_render]
    for o in hidden:
        o.hide_render = True
        print("WARNING not under the model root (hidden):", o.name)
    out = c.preview(root, filename, views, size, dist)
    for o in hidden:
        o.hide_render = False
    return out


# ---------------------------------------------------------------- palette (solid colours through one PNG)

PALETTE_FILE = "parts_c_palette"
PALETTE_TAG = "tex_" + PALETTE_FILE
_PAL = [
    ("black", (0.03, 0.03, 0.03)), ("red", (0.75, 0.05, 0.04)), ("yellow", (0.95, 0.78, 0.08)),
    ("orange", (0.95, 0.42, 0.05)), ("green", (0.1, 0.55, 0.15)), ("blue", (0.1, 0.25, 0.8)),
    ("white", (0.92, 0.92, 0.9)), ("grey", (0.45, 0.45, 0.47)), ("brown", (0.4, 0.22, 0.1)),
    ("purple", (0.45, 0.15, 0.6)), ("lightblue", (0.35, 0.65, 0.95)), ("usb_blue", (0.05, 0.3, 0.85)),
    ("accent_orange", (0.92, 0.35, 0.08)), ("tape_brown", (0.62, 0.45, 0.24)), ("silver_print", (0.75, 0.76, 0.78)),
    ("dark_grey", (0.16, 0.16, 0.17)), ("cable_black", (0.025, 0.025, 0.028)), ("sata_red", (0.7, 0.05, 0.05)),
    ("copper_wire", (0.8, 0.45, 0.25)), ("tin", (0.78, 0.78, 0.76)), ("pink", (0.9, 0.4, 0.6)),
    ("mid_grey", (0.3, 0.3, 0.31)), ("beige", (0.86, 0.8, 0.66)), ("cream", (0.95, 0.93, 0.86)),
]
PAL_N = 8  # swatches per row; 4 rows


def pal(name):
    """UV of a palette swatch's centre."""
    for i, (n, _) in enumerate(_PAL):
        if n == name:
            col, row = i % PAL_N, i // PAL_N
            return ((col + 0.5) / PAL_N, 1.0 - (row + 0.5) / 4.0)
    raise KeyError(name)


def write_palette():
    import numpy as np
    s = 32
    w, h = PAL_N * s, 4 * s
    arr = np.zeros((h, w, 4), dtype=np.float32)
    arr[..., 3] = 1
    for i, (_, col) in enumerate(_PAL):
        cx, row = i % PAL_N, i // PAL_N
        y0 = h - (row + 1) * s  # numpy row 0 = image bottom in Blender pixel order
        arr[y0:y0 + s, cx * s:(cx + 1) * s, 0:3] = col
    save_png(arr, PALETTE_FILE)


def save_png(arr, file, folder=None):
    """Saves a float RGBA numpy array (rows bottom-to-top, sRGB values) as a PNG texture."""
    h, w = arr.shape[0], arr.shape[1]
    img = bpy.data.images.new("tmp_" + file, w, h, alpha=True)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(arr.astype("float32").ravel())
    path = os.path.join(folder or c.TEXTURES, file + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    return path


def load_png(path):
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    bpy.data.images.remove(img)
    return arr.reshape(h, w, 4)


# ---------------------------------------------------------------- physically based stand-in materials (renders only)

PBR = {
    "gold": ((1.0, 0.77, 0.34), 1, 0.22), "copper": ((0.95, 0.6, 0.45), 1, 0.3), "steel": ((0.76, 0.76, 0.78), 1, 0.28),
    "steel_dark": ((0.32, 0.32, 0.34), 1, 0.38), "alu": ((0.9, 0.91, 0.92), 1, 0.32), "alu_dark": ((0.12, 0.12, 0.13), 0.9, 0.38),
    "nickel": ((0.8, 0.79, 0.76), 1, 0.18), "black_plastic": ((0.018, 0.018, 0.02), 0, 0.42),
    "dark_plastic": ((0.05, 0.05, 0.055), 0, 0.5), "grey_plastic": ((0.22, 0.22, 0.23), 0, 0.5),
    "white_plastic": ((0.8, 0.8, 0.78), 0, 0.42), "rubber": ((0.025, 0.025, 0.025), 0, 0.85),
    "fan_black": ((0.022, 0.022, 0.025), 0, 0.5), "paint_black": ((0.018, 0.018, 0.02), 0.15, 0.55),
    "paint_white": ((0.82, 0.82, 0.8), 0.05, 0.5), "glass": ((0.3, 0.32, 0.33), 0, 0.02),
    "mesh_black": ((0.02, 0.02, 0.022), 0.2, 0.6), "thermal_pad": ((0.5, 0.55, 0.6), 0, 0.85),
    "paste": ((0.55, 0.56, 0.58), 0.3, 0.5), "film_blue": ((0.2, 0.5, 0.9), 0, 0.15),
    "cardboard": ((0.5, 0.36, 0.22), 0, 0.85), "foam": ((0.025, 0.025, 0.03), 0, 1.0),
    "connector_black": ((0.025, 0.025, 0.025), 0, 0.45), "connector_white": ((0.82, 0.81, 0.76), 0, 0.45),
    "connector_beige": ((0.78, 0.7, 0.56), 0, 0.5), "pcb_green": ((0.03, 0.2, 0.08), 0, 0.4),
    "pcb_black": ((0.02, 0.022, 0.025), 0, 0.4), "solder": ((0.75, 0.75, 0.73), 1, 0.25),
    "ceramic": ((0.75, 0.68, 0.52), 0, 0.5), "chip_black": ((0.025, 0.025, 0.028), 0, 0.45),
    "rgb": ((0.85, 0.85, 0.9), 0, 0.35),
}
LEDS = {"led_red": (1, 0.1, 0.05), "led_yellow": (1, 0.75, 0.1), "led_white": (1, 1, 1), "led_green": (0.2, 1, 0.3),
        "led_blue": (0.25, 0.5, 1)}


def pbr_material(tag, lit_leds=False):
    name = "pbr_" + tag
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if tag.startswith("tex_"):
        path = os.path.join(c.TEXTURES, tag[4:] + ".png")
        if os.path.exists(path):
            img = bpy.data.images.load(path, check_existing=True)
            tn = nt.nodes.new("ShaderNodeTexImage")
            tn.image = img
            tn.interpolation = "Cubic"
            nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
            nt.links.new(tn.outputs["Alpha"], bsdf.inputs["Alpha"])
        bsdf.inputs["Roughness"].default_value = 0.45
        return m
    if tag in LEDS:
        col = LEDS[tag]
        bsdf.inputs["Base Color"].default_value = (col[0] * 0.5, col[1] * 0.5, col[2] * 0.5, 1)
        bsdf.inputs["Roughness"].default_value = 0.2
        if lit_leds:
            bsdf.inputs["Emission Color"].default_value = (*col, 1)
            bsdf.inputs["Emission Strength"].default_value = 6.0
        return m
    col, met, rough = PBR.get(tag, ((0.5, 0.5, 0.5), 0, 0.5))
    bsdf.inputs["Base Color"].default_value = (*col, 1)
    bsdf.inputs["Metallic"].default_value = met
    bsdf.inputs["Roughness"].default_value = rough
    if tag == "glass":
        bsdf.inputs["Transmission Weight"].default_value = 1.0
        bsdf.inputs["IOR"].default_value = 1.02   # thin sheets: no refraction (the game's glass is alpha-blended)
        bsdf.inputs["Base Color"].default_value = (0.62, 0.65, 0.67, 1)
    if tag in ("paint_black", "paint_white"):
        # powder coat: a fine bump
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 4000.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.08
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    if tag == "cardboard":
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 300.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.42, 0.29, 0.17, 1)
        ramp.color_ramp.elements[1].color = (0.56, 0.41, 0.26, 1)
        nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    if tag == "rgb":
        bsdf.inputs["Transmission Weight"].default_value = 0.3
    return m


def _setup_world(sc, strength=0.8, bg=(0.18, 0.18, 0.19)):
    w = bpy.data.worlds.new("beauty_world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bgn = nt.nodes.get("Background")
    out = nt.nodes.get("World Output")
    if STUDIO_HDRI:
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(STUDIO_HDRI, check_existing=True)
        nt.links.new(env.outputs["Color"], bgn.inputs["Color"])
        bgn.inputs["Strength"].default_value = strength
        # camera sees a plain backdrop; lighting comes from the HDRI
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        plain = nt.nodes.new("ShaderNodeBackground")
        plain.inputs["Color"].default_value = (*bg, 1)
        plain.inputs["Strength"].default_value = 1.0
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(bgn.outputs["Background"], mix.inputs[1])
        nt.links.new(plain.outputs["Background"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    else:
        bgn.inputs["Color"].default_value = (*bg, 1)


def _gpu_cycles(sc, samples=96):
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for t in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = t
                prefs.get_devices()
                ok = False
                for d in prefs.devices:
                    d.use = d.type == t
                    ok = ok or d.use
                if ok:
                    sc.cycles.device = "GPU"
                    break
            except Exception:
                continue
    except Exception:
        pass
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.cycles.max_bounces = 8
    sc.cycles.transmission_bounces = 8
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def _bounds(objs):
    pts = []
    for o in objs:
        if o.type == "MESH":
            pts += [o.matrix_world @ Vector(cc) for cc in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def beauty(root, filename, views=((35, 25),), size=(1280, 960), samples=96, lens=60, dist=None, lit_leds=False,
           target=None, start_index=2, hide=(), fill=1.0):
    """Cycles renders with PBR stand-ins (after export only: materials are swapped).
    views: (yaw, pitch) in degrees around the bounds centre in Unity terms (yaw 0 looks from +Z)."""
    if not PREVIEW[0]:
        return []
    sc = bpy.context.scene
    _gpu_cycles(sc, samples)
    _setup_world(sc)
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = False
    objs = [o for o in c.descendants(root) if o.type == "MESH"]
    mine = set(objs)
    hidden = []
    for o in bpy.context.scene.objects:   # render the model only (strays would hide modelling mistakes)
        if o.type in ("MESH", "CURVE", "FONT") and o not in mine and not o.hide_render:
            o.hide_render = True
            hidden.append(o)
            print("WARNING not under the model root (hidden):", o.name)
    for o in objs:
        tag = _tag_of(o.name)
        o.data.materials.clear()
        o.data.materials.append(pbr_material(tag, lit_leds))
        if any(h in o.name for h in hide):
            o.hide_render = True
            hidden.append(o)
    lo, hi = _bounds([o for o in objs if not o.hide_render])
    centre = (lo + hi) * 0.5 if target is None else c.conv(target)
    radius = (hi - lo).length * 0.5
    camd = bpy.data.cameras.new("beauty_cam")
    camd.lens = lens
    camd.clip_start = 0.002
    camd.clip_end = 50
    cam = c.link(bpy.data.objects.new("beauty_cam", camd))
    sc.camera = cam
    # a key light and a rim light, on top of the HDRI
    lights = []
    for nm, energy, loc in (("key", 60.0, (1.2, -1.5, 2.0)), ("rim", 40.0, (-1.5, 1.2, 1.2))):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy = energy * max(0.05, radius) ** 2 * 4
        ld.size = max(0.2, radius)
        lo_ = c.link(bpy.data.objects.new(nm, ld))
        lo_.location = centre + Vector(loc) * max(0.3, radius * 2.5)
        lo_.rotation_euler = (centre - lo_.location).to_track_quat("-Z", "Y").to_euler()
        lights.append(lo_)
    out = []
    fov = 2 * math.atan(18.0 / lens)
    for i, (yaw, pitch) in enumerate(views):
        d = dist or (radius / math.sin(fov / 2)) * 1.05 / fill
        y, p = yaw * DEG, pitch * DEG
        u = Vector((math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)))
        cam.location = centre + c.conv(u) * d
        cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(c.PREVIEWS, f"{filename}_{start_index + i}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    bpy.data.objects.remove(cam)
    for lo_ in lights:
        bpy.data.objects.remove(lo_)
    for o in hidden:
        o.hide_render = False
    return out


# ---------------------------------------------------------------- 2D artwork renderer

def srgb_to_lin(cv):
    def f(x):
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return tuple(f(x) for x in cv[:3])


class Art:
    """A flat 2D layout rendered orthographically to a PNG. Units are pixels, origin bottom-left.
    Colours are sRGB triples (as in an image editor). Later items draw on top (z order by call order)."""

    def __init__(self, w, h, bg=(1, 1, 1), name="art"):
        self.w, self.h = int(w), int(h)
        self.scene = bpy.data.scenes.new(name)
        sc = self.scene
        sc.render.engine = "BLENDER_EEVEE"
        sc.render.resolution_x, sc.render.resolution_y = self.w, self.h
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = True
        sc.render.filter_size = 0.9
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"
        try:
            sc.eevee.taa_render_samples = 16
        except Exception:
            pass
        world = bpy.data.worlds.new(name + "_w")
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
        sc.world = world
        camd = bpy.data.cameras.new(name + "_cam")
        camd.type = "ORTHO"
        camd.ortho_scale = max(self.w, self.h)
        camd.clip_start = 0.1
        camd.clip_end = 10000
        cam = bpy.data.objects.new(name + "_cam", camd)
        sc.collection.objects.link(cam)
        cam.location = (self.w / 2, self.h / 2, 1000)
        sc.camera = cam
        self.z = 0.0
        self.mats = {}
        self.objs = [cam]
        if bg is not None:
            self.rect(0, 0, self.w, self.h, bg)

    def _z(self):
        self.z += 0.01
        return self.z

    def _emit_mat(self, col, alpha=1.0, image=None, vcol=False):
        key = (tuple(round(x, 4) for x in col) if col else None, round(alpha, 3), image.name if image else None, vcol)
        if key in self.mats:
            return self.mats[key]
        m = bpy.data.materials.new("artmat")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.0
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        if image is not None:
            tn = nt.nodes.new("ShaderNodeTexImage")
            tn.image = image
            tn.interpolation = "Cubic"
            tn.extension = "CLIP"
            nt.links.new(tn.outputs["Color"], em.inputs["Color"])
            if alpha < 1.0:
                mm = nt.nodes.new("ShaderNodeMath")
                mm.operation = "MULTIPLY"
                mm.inputs[1].default_value = alpha
                nt.links.new(tn.outputs["Alpha"], mm.inputs[0])
                nt.links.new(mm.outputs[0], mix.inputs["Fac"])
            else:
                nt.links.new(tn.outputs["Alpha"], mix.inputs["Fac"])
        elif vcol:
            ca = nt.nodes.new("ShaderNodeVertexColor")
            ca.layer_name = "Col"
            nt.links.new(ca.outputs["Color"], em.inputs["Color"])
            nt.links.new(ca.outputs["Alpha"], mix.inputs["Fac"])
        else:
            em.inputs["Color"].default_value = (*srgb_to_lin(col), 1)
            mix.inputs["Fac"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
        self.mats[key] = m
        return m

    def _mesh(self, verts, faces, mat, cols=None):
        me = bpy.data.meshes.new("artmesh")
        z = self._z()
        me.from_pydata([(x, y, z) for x, y in verts], [], faces)
        if cols is not None:
            ca = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
            for i, col in enumerate(cols):
                lin = srgb_to_lin(col)
                ca.data[i].color = (*lin, col[3] if len(col) > 3 else 1.0)
        uv = me.uv_layers.new(name="UVMap")
        me.materials.append(mat)
        ob = bpy.data.objects.new("artobj", me)
        self.scene.collection.objects.link(ob)
        self.objs.append(ob)
        return ob, me, uv

    def rect(self, x, y, w, h, col, alpha=1.0):
        self._mesh([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], [(0, 1, 2, 3)], self._emit_mat(col, alpha))

    def poly(self, pts, col, alpha=1.0):
        bm = bmesh.new()
        vs = [bm.verts.new((p[0], p[1], 0)) for p in pts]
        f = bm.faces.new(vs)
        bmesh.ops.triangulate(bm, faces=[f])
        verts = [(v.co.x, v.co.y) for v in bm.verts]
        bm.verts.index_update()
        faces = [tuple(v.index for v in f.verts) for f in bm.faces]
        bm.free()
        self._mesh(verts, faces, self._emit_mat(col, alpha))

    def circle(self, cx, cy, r, col, n=48, alpha=1.0):
        self.poly(circle(r, cx, cy, n), col, alpha)

    def ring(self, cx, cy, r0, r1, col, n=48, alpha=1.0):
        verts, faces = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a)))
            verts.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a)))
        for i in range(n):
            j = (i + 1) % n
            faces.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
        self._mesh(verts, faces, self._emit_mat(col, alpha))

    def grad(self, x, y, w, h, c0, c1, vertical=True, a0=1.0, a1=1.0):
        """A linear gradient: c0 at the bottom (or left), c1 at the top (or right)."""
        if vertical:
            cols = [(*c0, a0), (*c0, a0), (*c1, a1), (*c1, a1)]
        else:
            cols = [(*c0, a0), (*c1, a1), (*c1, a1), (*c0, a0)]
        self._mesh([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], [(0, 1, 2, 3)], self._emit_mat(None, 1.0, vcol=True), cols)

    def radial(self, cx, cy, r, c0, c1, a0=1.0, a1=0.0, n=48):
        """A radial glow: c0 at the centre, c1 at radius r."""
        verts = [(cx, cy)] + [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
        cols = [(*c0, a0)] + [(*c1, a1)] * n
        self._mesh(verts, faces, self._emit_mat(None, 1.0, vcol=True), cols)

    def image(self, path, x, y, w=None, h=None, alpha=1.0, fit=None):
        """Draws an image file; give w or h (keeps aspect) or both. fit=(w,h) fits inside a box, centred at x,y."""
        img = bpy.data.images.load(path, check_existing=False)
        iw, ih = img.size
        if fit is not None:
            k = min(fit[0] / iw, fit[1] / ih)
            w, h = iw * k, ih * k
            x, y = x - w / 2, y - h / 2
        elif w is None:
            w = h * iw / ih
        elif h is None:
            h = w * ih / iw
        ob, me, uv = self._mesh([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], [(0, 1, 2, 3)], self._emit_mat(None, alpha, image=img))
        for i, lp in enumerate(me.loops):
            vi = lp.vertex_index
            uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][vi]
        return (x, y, w, h)

    def text(self, s, x, y, size, col, fontfile="arialbd.ttf", align="LEFT", maxw=None, alpha=1.0, spacing=1.0,
             rot=0.0, valign="BASE"):
        """Text with its baseline at y (valign 'BASE'), or centred on y ('CENTER'), or top at y ('TOP').
        size is the font size in pixels (em height). Returns (width, height) drawn."""
        cu = bpy.data.curves.new("arttext", "FONT")
        cu.body = s
        cu.size = size
        cu.align_x = align
        cu.space_character = spacing
        cu.resolution_u = 6
        f = font(fontfile)
        if f is not None:
            cu.font = f
        ob = bpy.data.objects.new("arttext", cu)
        self.scene.collection.objects.link(ob)
        ob.data.materials.append(self._emit_mat(col, alpha))
        dg = bpy.context.evaluated_depsgraph_get()
        ob.location = (0, 0, 0)
        dg.update()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        if len(me.vertices) == 0:
            bpy.data.meshes.remove(me)
            bpy.data.objects.remove(ob)
            return (0, 0)
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        bpy.data.meshes.remove(me)
        w = max(xs) - min(xs)
        k = 1.0
        if maxw is not None and w > maxw:
            k = maxw / w
        ob.scale = (k, k, 1)
        dy = 0.0
        if valign == "CENTER":
            dy = -(max(ys) + min(ys)) / 2 * k
        elif valign == "TOP":
            dy = -max(ys) * k
        ob.location = (x, y + dy, self._z())
        ob.rotation_euler = (0, 0, rot)
        self.objs.append(ob)
        return (w * k, (max(ys) - min(ys)) * k)

    def text_width(self, s, size, fontfile="arialbd.ttf", spacing=1.0):
        cu = bpy.data.curves.new("measure", "FONT")
        cu.body = s
        cu.size = size
        cu.space_character = spacing
        f = font(fontfile)
        if f is not None:
            cu.font = f
        ob = bpy.data.objects.new("measure", cu)
        self.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        w = 0.0
        if len(me.vertices):
            xs = [v.co.x for v in me.vertices]
            w = max(xs) - min(xs)
        bpy.data.meshes.remove(me)
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        return w

    def ean13(self, digits12, x, y, w, h, col=(0.05, 0.05, 0.05), bg=(1, 1, 1), text=True):
        """A real EAN-13 barcode (with check digit) in a white box at x, y of size w x h."""
        d = [int(ch) for ch in digits12[:12]]
        s = sum(d[i] * (3 if i % 2 else 1) for i in range(12))
        d.append((10 - s % 10) % 10)
        L = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
        G = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
        R = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
        P = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]
        bits = "101"
        par = P[d[0]]
        for i in range(6):
            bits += (L if par[i] == "L" else G)[d[1 + i]][:]
        bits += "01010"
        for i in range(6):
            bits += R[d[7 + i]]
        bits += "101"
        self.rect(x, y, w, h, bg)
        mod = w / (len(bits) + 18)
        x0 = x + mod * 11
        th = h * 0.22 if text else 0
        guard = set(list(range(0, 3)) + list(range(45, 50)) + list(range(92, 95)))
        i = 0
        while i < len(bits):
            if bits[i] == "1":
                j = i
                while j < len(bits) and bits[j] == "1":
                    j += 1
                long_bar = i in guard
                by = y + h * 0.08 + (0 if long_bar or not text else th * 0.55)
                self.rect(x0 + i * mod, by, (j - i) * mod, y + h * 0.92 - by, col)
                i = j
            else:
                i += 1
        if text:
            fs = th * 1.0
            ty = y + h * 0.08 + fs * 0.1
            self.text(str(d[0]), x + mod * 4, ty, fs, col, "consola.ttf")
            self.text("".join(map(str, d[1:7])), x0 + mod * 24, ty, fs, col, "consola.ttf", align="CENTER", maxw=mod * 40)
            self.text("".join(map(str, d[7:13])), x0 + mod * 70, ty, fs, col, "consola.ttf", align="CENTER", maxw=mod * 40)
        return "".join(map(str, d))

    def code128ish(self, seed, x, y, w, h, col=(0.05, 0.05, 0.05)):
        """A dense serial-number style barcode (not decodable; looks right)."""
        import random
        rnd = random.Random(seed)
        bits = []
        while len(bits) < 160:
            bits += [1] * rnd.randint(1, 4) + [0] * rnd.randint(1, 3)
        mod = w / len(bits)
        for i, b in enumerate(bits):
            if b:
                self.rect(x + i * mod, y, mod * 1.02, h, col)

    def render(self, file, folder=None):
        path = os.path.join(folder or c.TEXTURES, file + ".png")
        self.scene.render.filepath = path
        bpy.ops.render.render(write_still=True, scene=self.scene.name)
        return path

    def dispose(self):
        for o in self.objs:
            try:
                data = o.data
                bpy.data.objects.remove(o)
                if data is not None and data.users == 0:
                    if isinstance(data, bpy.types.Mesh):
                        bpy.data.meshes.remove(data)
                    elif isinstance(data, bpy.types.Curve):
                        bpy.data.curves.remove(data)
                    elif isinstance(data, bpy.types.Camera):
                        bpy.data.cameras.remove(data)
            except ReferenceError:
                pass
        for m in self.mats.values():
            try:
                bpy.data.materials.remove(m)
            except ReferenceError:
                pass
        bpy.data.scenes.remove(self.scene)
