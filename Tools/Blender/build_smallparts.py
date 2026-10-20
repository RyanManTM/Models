r"""
Small parts and packaging contents (docs/tasks/02-small-parts.md): the coiled cables and bundles that come in the
retail boxes, the thermal paste syringe, the standoff bag and the female fan connector housings.

Run:  blender -b --factory-startup -P Tools/Blender/build_smallparts.py -- [ids...] [--nopreview]
      none = everything. Ids: coil_dp, coil_c13, coil_sata_pair, bundle_modular, coil_fan_splitter,
      syringe_paste, standoff_bag, fan4_female, fan3_female.

Outputs: Assets/Resources/Models/<id>.fbx, its textures (tex_smallparts_*), Logs/ModelPreviews/<id>_<n>.png
(0-1 Workbench, 2-3 Cycles) and Logs/ModelPreviews/<id>_report.txt.

FLAT ITEMS (coils, bundle, syringe, standoff bag) follow docs/PACKAGING.md: origin at the bottom centre, lying flat
on the y = 0 plane, +Y up, the item's width along x and its height along z with the top edge of its print towards
-z. Placed at identity rotation on a box anchor whose +Z is up and +Y points to -z (every A_ITEM_CORD / POUCH /
PART frame=flat anchor in the box rigs), the model's x, -z, +y are the anchor's w, h, t axes.
The coils are look items (the game draws working cables itself). Their twist tie or velcro straps are moving pieces
on A_TIE_<n> (meta tie=twist|velcro) so the code can take them off.

FAN CONNECTORS fan4_female / fan3_female: the receiving housing on splitter outputs and extension cables (the end a
fan's own plug, plug_fan4 / plug_fan3, slides onto). Frame: origin at the centre of the contact face (where the fan
plug's face seats), +Z back along the wires, +Y the polarising-ramp side. The pins and the ramp wall stand in front
of the face (towards -Z, where the plug comes from); the housing occupies z 0..L and the wire stubs leave the back.

Built on dct_common (frames, anchors, export), parts_c (shapes, finalize, reports, previews), parts_b (mesh
builders), shipping_lib (sweeps, Cycles previews on a floor) and build_plugs (the plug heads). It changes none of them.
"""
import math
import os
import random
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as B  # noqa: E402
import parts_c as P  # noqa: E402
import shipping_lib as S  # noqa: E402
import shipping_bits as SB  # noqa: E402
import build_plugs as PL  # noqa: E402

V = Vector
DEG = math.pi / 180.0
TAU = 2.0 * math.pi
TIE_W, TIE_T = SB.TIE_W, SB.TIE_T


# ====================================================================== small helpers

def new_root(mid):
    P.reset()
    S.setup_tags()
    return c.root(mid)


def geo_obj(parent, geo, name, tag, smooth=50.0):
    """A finished '<name>#<tag>' object from local geometry (verts, faces, uvs, flags) in Unity space."""
    mb = B.MB().add(geo)
    return B.build_mesh(mb, P.uname(name), tag, parent, smooth)


def circle_profile(r, n=8, rot=0.0):
    return [(r * math.cos(rot + TAU * k / n), r * math.sin(rot + TAU * k / n)) for k in range(n)]


def oval_profile(w, h, n=10):
    """A flat cable/sleeve cross-section (w across, h thick): a stadium."""
    pts = []
    r = h / 2
    half = max(0.0, w / 2 - r)
    m = n // 2
    for i in range(m):
        a = -math.pi / 2 + math.pi * i / (m - 1)
        pts.append((half + r * math.cos(a), r * math.sin(a)))
    for i in range(m):
        a = math.pi / 2 + math.pi * i / (m - 1)
        pts.append((-half + r * math.cos(a), r * math.sin(a)))
    return pts


def sweep(parent, pts, profile, tag, name="cable", up=(0, 1, 0), smooth=70.0, caps=True, twist=None):
    geo = S.sweep_profile(pts, profile, up=up, caps=caps, smooth=True, twist=twist)
    return geo_obj(parent, geo, name, tag, smooth)


def ribbon_sweep(path, profile, sides, caps=True):
    """Sweeps a flat cross-section (x across, y thick) along path with its 'across' axis steered by sides[i]: a vector
    the section's x should follow (projected square to the path), or None to keep the ribbon flat (x horizontal).
    Unlike a parallel-transport sweep this never rolls a flat cable over on its edge."""
    Pp = [V(p) for p in path]
    m = len(Pp)
    up = V((0, 1, 0))
    rings = []
    prevN = None
    for i in range(m):
        T = (Pp[min(i + 1, m - 1)] - Pp[max(i - 1, 0)]).normalized()
        g = sides[i]
        sd = (up.cross(T) if g is None else V(g))
        sd = sd - T * sd.dot(T)
        if sd.length < 1e-6:
            sd = rings[-1][1] if rings else V((0, 0, 1))
        sd.normalize()
        N = sd.cross(T).normalized()
        if (prevN is not None and N.dot(prevN) < 0) or (prevN is None and N.dot(up) < 0):
            N, sd = -N, -sd
        prevN = N
        rings.append((N, sd))
    n = len(profile)
    verts, faces = [], []
    for i in range(m):
        N, B = rings[i]
        for (x, y) in profile:
            verts.append(Pp[i] + B * x + N * y)
    for i in range(m - 1):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
    flags = [True] * len(faces)
    if caps:
        faces.append(list(reversed(range(n))))
        faces.append([(m - 1) * n + j for j in range(n)])
        flags += [False, False]
    nrm = B_newell([verts[k] for k in faces[0]])
    ctr = sum((verts[k] for k in faces[0]), V()) / len(faces[0])
    if nrm.dot(ctr - Pp[0]) < 0:
        faces = [f[::-1] for f in faces]
    return verts, faces, None, flags


def B_newell(pts):
    return B._newell(pts)


def bezier(p0, t0, p1, t1, n=10, k0=None, k1=None):
    """Points of a cubic from p0 (leaving along t0) to p1 (arriving along t1); handle lengths k0, k1."""
    p0, p1 = V(p0), V(p1)
    d = (p1 - p0).length
    a = p0 + V(t0).normalized() * (k0 if k0 is not None else d * 0.4)
    b = p1 - V(t1).normalized() * (k1 if k1 is not None else d * 0.4)
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append(p0 * u ** 3 + a * 3 * u * u * t + b * 3 * u * t * t + p1 * t ** 3)
    return out


def lead(p0, t0, p1, t1, n=10, k0=None, k1=None, lift=0.0018):
    """A cable lead between a plug and the coil: a cubic that arches up by 'lift' in the middle, so it crosses over
    the neighbouring turns instead of through them."""
    pts = bezier(p0, t0, p1, t1, n, k0, k1)
    for i, p in enumerate(pts):
        p.y += lift * math.sin(math.pi * i / n)
    return pts


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def drop_stub(build, *args, keys=("_cable",)):
    """Runs a build_plugs plug builder and removes the straight cable stub its overmould leaves (the coil's own
    cable continues from the strain relief instead), or whatever its new objects' names contain one of keys.
    Returns the builder's result."""
    import bpy
    before = {o.name for o in bpy.data.objects}
    r = build(*args)
    for o in list(bpy.data.objects):
        if o.name not in before and any(k in o.name.split("#", 1)[0] for k in keys):
            bpy.data.objects.remove(o)
    return r


def recentre(root, keep_y=True):
    """Moves everything under root so the mesh bounds are centred on x and z (origin at the bottom centre)."""
    lo, hi = bounds(root)
    cx, cz = (lo.x + hi.x) / 2, (lo.z + hi.z) / 2
    shift = c.conv((-cx, 0.0 if keep_y else -lo.y, -cz))
    from mathutils import Matrix
    M = Matrix.Translation(shift)
    for o in root.children:
        o.matrix_world = M @ o.matrix_world
    return cx, cz


def bounds(root):
    """Unity-space bounds of the meshes under root."""
    pts = []
    for o in c.descendants(root):
        if o.type == "MESH":
            mw = o.matrix_world
            for v in o.data.vertices:
                b = mw @ v.co
                pts.append(V((-b.x, b.z, -b.y)))
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


# ====================================================================== coils

class Coil:
    """A cable coiled in loops lying flat: loop centre line an irregular ellipse (rx, rz) round the origin, the turns
    packed in 'lanes' across the bundle (dr outward, dy up, in cable diameters). The cable moves from lane k to lane
    k+1 once per turn (crossing over its neighbour), so the coil reads as a real hand-wound bundle. Near the tie
    angle the bundle is pinched and lifted by the tie's thickness."""

    def __init__(self, d, rx, rz, rows, theta0, tie_theta=None, seed=1, shape=(0.035, 0.025), pinch=0.18):
        self.d, self.rx, self.rz = d, rx, rz
        self.theta0 = theta0
        self.tie = tie_theta
        self.pinch = pinch
        rng = random.Random(seed)
        self.rng = rng
        lanes = []
        for r, (n, off) in enumerate(rows):
            row = [((i - (n - 1) / 2 + off), 0.5 + r * 0.866) for i in range(n)]
            if r % 2:
                row.reverse()
            lanes += row
        self.lanes = lanes
        n = len(lanes)
        # crossing positions (fraction of a turn), descending so no lane is ever used twice at the same angle
        hi, lo = 0.88, 0.22
        self.cross = [hi - (hi - lo) * k / max(1, n - 2) + rng.uniform(-0.03, 0.03) for k in range(n - 1)]
        self.cw = 0.16
        self.ph = [rng.uniform(0, TAU) for _ in range(6)]
        self.shape = shape
        self.cy = sum(l[1] for l in lanes) / n
        self.cr = sum(l[0] for l in lanes) / n

    def lane_at(self, s):
        """(dr, dy, crossing amount 0..1) at turn parameter s."""
        n = len(self.lanes)
        ell = 0.0
        hop = 0.0
        for k in range(n - 1):
            x = (s - (k + self.cross[k])) / self.cw + 0.5
            ell += smoothstep(x)
            if 0 < x < 1:
                hop = max(hop, math.sin(math.pi * x))
        ell = max(0.0, min(n - 1, ell))
        i = min(int(ell), n - 2) if n > 1 else 0
        f = ell - i
        if n == 1:
            return self.lanes[0][0], self.lanes[0][1], 0.0
        a, b = self.lanes[i], self.lanes[i + 1]
        return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, hop

    def radius_scale(self, th):
        a1, a2 = self.shape
        return 1.0 + a1 * math.sin(2 * th + self.ph[0]) + a2 * math.sin(3 * th + self.ph[1])

    def tie_weight(self, th):
        if self.tie is None:
            return 0.0
        dth = (th - self.tie + math.pi) % TAU - math.pi
        return math.exp(-(dth / 0.22) ** 2)

    def point(self, th):
        s = (th - self.theta0) / TAU
        dr, dy, hop = self.lane_at(s)
        g = self.tie_weight(th)
        # pinch the bundle round its centre under the tie, and lift it by the tie's thickness
        dr = self.cr + (dr - self.cr) * (1 - self.pinch * g)
        dy = self.cy + (dy - self.cy) * (1 - self.pinch * g)
        dy += 0.35 * hop                     # crossing over a neighbour
        wob = 0.05 * math.sin(th * 1.7 + s * 2.3 + self.ph[2]) * self.d
        k = self.radius_scale(th)
        r_x = self.rx * k + dr * self.d + wob
        r_z = self.rz * k + dr * self.d + wob
        y = dy * self.d + g * (TIE_T + 0.0002)
        return V((r_x * math.cos(th), y, r_z * math.sin(th)))

    def tangent(self, th):
        e = 1e-3
        return (self.point(th + e) - self.point(th - e)).normalized()

    def path(self, th0, th1, step=10 * DEG):
        n = max(2, int(abs(th1 - th0) / step))
        return [self.point(th0 + (th1 - th0) * i / n) for i in range(n + 1)]

    def bundle_section(self, th):
        """Centre, outward unit, half width and half height of the bundle at angle th (for the tie)."""
        g = self.tie_weight(th)
        drs = [l[0] for l in self.lanes]
        dys = [l[1] for l in self.lanes]
        k = 1 - self.pinch * g
        w = ((max(drs) - min(drs)) * k + 1.0) * self.d / 2
        h = ((max(dys) - min(dys)) * k + 1.0) * self.d / 2
        kk = self.radius_scale(th)
        cr = self.cr * self.d
        cen = V(((self.rx * kk + cr) * math.cos(th), self.cy * self.d + g * (TIE_T + 0.0002), (self.rz * kk + cr) * math.sin(th)))
        out = V((math.cos(th) / max(1e-6, self.rx), 0, math.sin(th) / max(1e-6, self.rz))).normalized()
        return cen, out, w, h


def twist_tie(anchor_parent, cen, axis, up, half_w, half_h, tag="white_plastic", pig_len=0.011, pig_dir=None, seed=2):
    """A twist tie wrapped round a bundle section (centre cen, bundle running along axis, 'up' = where the twist
    is), ends twisted into a short pigtail lying along pig_dir on top of the bundle. Returns the twist point."""
    axis = V(axis).normalized()
    up = (V(up) - axis * V(up).dot(axis)).normalized()
    side = up.cross(axis).normalized()
    a = half_w + TIE_T * 0.6
    b = half_h + TIE_T * 0.6
    pig_dir = V(pig_dir).normalized() if pig_dir is not None else axis
    top = V(cen) + up * b
    base = top + up * 0.0009

    def loop_pt(phi):
        # a squarish superellipse hugging the bundle
        cs, sn = math.cos(phi), math.sin(phi)
        e = 2.0 / 3.5
        x = a * math.copysign(abs(cs) ** e, cs)
        y = b * math.copysign(abs(sn) ** e, sn)
        return V(cen) + side * x + up * y

    # the band round the bundle: a flat ribbon (its width along the bundle), from the twist round and back to it
    nl = 30
    band = [base + side * 0.0008]
    for i in range(1, nl):
        phi = math.pi / 2 - TAU * i / nl
        band.append(loop_pt(phi))
    band.append(base - side * 0.0008)
    prof = [(y, -x) for (x, y) in SB.ribbon_profile(TIE_W, TIE_T, 1)]
    geo_obj(anchor_parent, S.sweep_profile(band, prof, up=tuple(axis), smooth=True), "tie", tag, 50.0)
    # the pigtail: both ends twisted together, folded down flat along the bundle (two interleaved helices)
    lat = up.cross(pig_dir).normalized()
    rh, nh, turns = 0.00075, 18, 3.0
    for ph in (0.0, math.pi):
        pts = [base + side * (0.0008 if ph == 0 else -0.0008)]
        for i in range(nh + 1):
            t = i / nh
            th = turns * TAU * t + ph
            pts.append(base + pig_dir * (pig_len * t) + up * (rh * math.cos(th) * 0.6 + 0.0002) + lat * (rh * math.sin(th)))
        # the cut end splays a little
        pts.append(pts[-1] + pig_dir * 0.0012 + lat * (0.0006 if ph == 0 else -0.0006))
        geo_obj(anchor_parent, S.sweep_profile(pts, circle_profile(0.00058, 6), up=tuple(up), smooth=True), "tie", tag, 50.0)
    return base


def add_tie(root, cen, axis, hw, hh, index=0, colour="white", pig_dir=None):
    """A removable twist tie round a bundle section: the anchor A_TIE_<index> on top of the bundle (+Z up, +Y along
    the bundle) and the tie as its moving piece."""
    axis = V(axis).normalized()
    a = P.anchor(f"A_TIE_{index}", P.Frame(V(cen) + V((0, hh, 0)), (0, 1, 0), tuple(axis)),
                 (hw * 2 + 0.006, TIE_W + 0.012, hh * 2 + 0.006), root, meta=f"tie=twist,colour={colour}")
    twist_tie(a, cen, axis, (0, 1, 0), hw, hh, tag=colour + "_plastic", pig_dir=pig_dir if pig_dir is not None else axis)
    return a


# ====================================================================== coil_dp

def build_coil_dp(root):
    """1.8 m DisplayPort cable, about 0.11 m loops, both plug heads tucked inside the coil, a white twist tie."""
    d = 0.0058                       # the plug model's cable (r 0.0029)
    r = d / 2
    th0 = 200 * DEG
    rows = [(3, 0.0), (3, 0.5)]
    coil = Coil(d, 0.0445, 0.0430, rows, th0, tie_theta=th0 + 32 * DEG, seed=5)
    turns = len(coil.lanes) - 0.12
    th_end = th0 + TAU * turns
    loops = coil.path(th0, th_end, 9 * DEG)
    # plug A: lying flat inside the coil, face towards -x, its cable leaving towards +x then into the coil
    ya = 0.0049
    fa = V((-0.012, ya, 0.010))
    da = V((1, 0, 0.25)).normalized()
    ia = place_plug(PL.plug_dp, fa, da, parent=root)
    ea = V(ia["end"]) - da * 0.03          # the strain relief's end (stub removed)
    # plug B: beside plug A, face towards +x
    fb = V((0.016, ya, -0.013))
    db = V((-1, 0, -0.2)).normalized()
    ib = place_plug(PL.plug_dp, fb, db, parent=root)
    eb = V(ib["end"]) - db * 0.03
    p_start, t_start = loops[0], coil.tangent(th0)
    p_end, t_end = loops[-1], coil.tangent(th_end)
    lead_a = lead(ea, da, p_start, t_start, 12, 0.03, 0.04)
    lead_b = lead(p_end, t_end, eb, -db, 12, 0.04, 0.03)
    pts = lead_a[:-1] + loops + lead_b[1:]
    for p in pts:
        p.y = max(p.y, r)
    sweep(root, pts, circle_profile(r, 8, math.pi / 8), "rubber", "dp_cable")
    cen, out, hw, hh = coil.bundle_section(coil.tie)
    add_tie(root, cen, coil.tangent(coil.tie), hw, hh)
    return dict(note="1.8 m DisplayPort cable (d 5.8 mm), 6 turns, both DP heads inside the coil")


# ====================================================================== coil_c13

def plug_nema515(fr, parent):
    """A US NEMA 5-15P moulded wall plug (the PSU cord's wall end), slim straight style: two flat blades with their
    holes, the round ground pin, a body that tapers into a ribbed strain relief. Frame like build_plugs: origin at
    the face centre, +Z back along the cable, +Y the blade side (ground pin at -Y). Returns the relief end."""
    W, H = 0.0174, 0.0215          # across the blades, blade-to-ground
    tag = "black_plastic"
    by, gy = 0.0056, 0.0056 - 0.0119
    # body: a short lip at the face, then a taper into the relief
    secs = [(P.rrect(W, H, 0.0032, 0, 0, 3), 0.0), (P.rrect(W + 0.0008, H + 0.0008, 0.0035, 0, 0, 3), 0.0012),
            (P.rrect(W + 0.0008, H + 0.0008, 0.0035, 0, 0, 3), 0.0105),
            (P.rrect(W - 0.0005, H - 0.0010, 0.0040, 0, 0, 3), 0.0200),
            (P.rrect(0.0118, 0.0122, 0.0045, 0, -0.0004, 3), 0.0292)]
    P.loft("nema_body", secs, tag, fr, parent, smooth=40)
    # grip ribs on both broad sides (the faces at +-x), on the taper so they stay inside the lip's outline
    for sx in (-1, 1):
        for k in range(5):
            z = 0.0118 + k * 0.0017
            hw = (W + 0.0008) / 2 + ((W - 0.0005) / 2 - (W + 0.0008) / 2) * (z - 0.0105) / (0.0200 - 0.0105)
            P.cube("nema_grip", (sx * (hw + 0.0001), 0, z), (0.0006, H * 0.6, 0.0007), tag, fr, parent)
    # strain relief rings down to the cable
    z = 0.0292
    rr0 = 0.0058
    n = 5
    for k in range(n):
        t = k / (n - 1)
        rr = rr0 * (1 - t) + 0.0034 * t
        P.cylinder("nema_relief", fr.sub(0, -0.0004, z + k * 0.0024), rr, 0.0019, tag, 14, parent, z0=0.0, smooth=70)
        P.cylinder("nema_relief", fr.sub(0, -0.0004, z + k * 0.0024 + 0.0019), rr * 0.86, 0.0005, tag, 14, parent, z0=0.0)
    end = fr.p(0, -0.0004, z + n * 0.0024)
    # the two blades (1.5 mm brass, 6.35 mm wide, 15.9 mm out of the face) with their holes
    L = 0.0159
    for sx in (-1, 1):
        bf = fr.sub(sx * 0.00635, by, -L / 2 + 0.0005, fwd=(1, 0, 0), up=(0, 1, 0))   # local x = plug -z
        a0, a1, h = -L / 2 - 0.0005, L / 2, 0.0032
        out = [(a0, -h), (a1 - 0.0008, -h), (a1, -h + 0.0008), (a1, h - 0.0008), (a1 - 0.0008, h), (a0, h)]
        P.slab("nema_blade", out, 0.0015, "nickel", bf, holes=[P.circle(0.0015, a1 - 0.0045, 0, 12)], parent=parent)
    # the round ground pin (a little longer than the blades)
    gf = fr.sub(0, gy, 0.0, fwd=(0, 0, -1), up=(0, 1, 0))
    Lg = 0.0187
    P.lathe("nema_ground", [(0, -0.0005), (0.0024, -0.0005), (0.0024, Lg - 0.0016), (0.0019, Lg - 0.0004), (0.0011, Lg), (0, Lg)],
            "nickel", gf, 16, parent, smooth=50)
    # moulded marks on the face: a ring round the ground pin
    P.slab("nema_face_ring", P.circle(0.0034, 0, gy, 20), 0.0003, tag, fr.sub(0, 0, -0.00015),
           holes=[P.circle(0.0026, 0, gy, 20)], parent=parent)
    return dict(end=end, W=W, H=H, L=z + n * 0.0024)


def build_coil_c13(root):
    """1.5 m PSU power cord (18/3 SVT, 6 mm) coiled in 5 turns with a white twist tie; the C13 end (plug_c13 look)
    and the NEMA 5-15P wall plug lie inside the coil."""
    d = 0.0060
    r = d / 2
    th0 = 168 * DEG
    rows = [(3, 0.0), (2, 0.0)]
    coil = Coil(d, 0.0478, 0.0350, rows, th0, tie_theta=250 * DEG, seed=9, shape=(0.02, 0.012))
    turns = len(coil.lanes) - 0.5
    th_end = th0 + TAU * turns
    loops = coil.path(th0, th_end, 9 * DEG)
    # the C13 end lying flat in the coil (its chamfered top up), face towards +x, cable leaving towards -x
    fa = V((0.021, 0.0091, 0.0128))
    da = V((-1, 0, -0.04)).normalized()
    ia = drop_stub(PL.plug_c13, P.Frame(fa, da, (0, 1, 0)), root)
    ea = V(ia["end"]) - da * 0.03
    # the wall plug lying on its side (blades one above the other), prongs towards -x, cable leaving towards +x
    fb = V((-0.0125, 0.0095, -0.0128))
    db = V((1, 0, 0.03)).normalized()
    ib = plug_nema515(P.Frame(fb, db, (0, 0, 1)), root)
    eb = V(ib["end"])
    p_start, t_start = loops[0], coil.tangent(th0)
    p_end, t_end = loops[-1], coil.tangent(th_end)
    lead_a = lead(ea, da, p_start, t_start, 10, 0.012, 0.015)
    lead_b = lead(p_end, t_end, eb, -db, 10, 0.015, 0.012)
    pts = lead_a[:-1] + loops + lead_b[1:]
    for p in pts:
        p.y = max(p.y, r)
    sweep(root, pts, circle_profile(r, 8, math.pi / 8), "rubber", "c13_cord")
    cen, out, hw, hh = coil.bundle_section(coil.tie)
    add_tie(root, cen, coil.tangent(coil.tie), hw, hh)
    return dict(note="1.5 m power cord (d 6.0 mm), 5 turns; C13 end and NEMA 5-15P wall plug inside the coil")


# ====================================================================== coil_sata_pair

SATA_W, SATA_T = 0.0076, 0.0014     # the flat 7-wire cable (as plug_sata_data's stub)


def sata_right_angle(fr, parent, side=1):
    """A right-angle SATA data plug: the plug_sata_data face and latch clip, a shorter body, and the flat cable leaving
    from a boot on one side (local +x if side > 0). Frame like build_plugs (origin at the face centre, +Z into the
    body, +Y the latch side). Returns (exit point, exit direction)."""
    W, H, Lb = 0.0108, 0.0058, 0.0105
    tag = "connector_black"
    face_t = 0.0016
    hole = PL.sata_l_hole(W - 0.0024, H - 0.0024, 0.0016)
    P.slab("ra_face", P.rrect(W, H, 0.0005), face_t, tag, fr.sub(0, 0, face_t / 2), holes=[hole], parent=parent)
    P.cube("ra_body", (0, 0, face_t + (Lb - face_t) / 2), (W, H, Lb - face_t), tag, fr, parent, bevel=0.0005)
    for i in range(7):
        P.cube("ra_pin", (-W / 2 + 0.0024 + 0.0004 + i * 0.00105 + 0.0006, -H / 2 + 0.0016, 0.0012), (0.0006, 0.0003, 0.0015),
               "gold", fr, parent)
    # the boot the cable leaves from, on the side at the back, and its grip ribs
    bx = side * (W / 2 + 0.0019)
    P.cube("ra_boot", (bx, 0, Lb - 0.0047), (0.0040, 0.0030, 0.0088), tag, fr, parent, bevel=0.0007)
    for k in range(3):
        P.cube("ra_rib", (side * (W / 2 + 0.0006 + k * 0.0011), 0.0016, Lb - 0.0047), (0.0005, 0.0004, 0.0080), tag, fr, parent)
    # the metal latch clip over the top, its press tab towards the back
    P.cube("ra_clip", (0, H / 2 + 0.0003, 0.0058), (0.0042, 0.0005, 0.0088), "steel", fr, parent)
    P.cube("ra_clip", (0, H / 2 + 0.0002, 0.0012), (0.0042, 0.0008, 0.0009), "steel", fr, parent)
    P.cube("ra_clip_tab", (0, H / 2 + 0.0009, 0.0098), (0.0046, 0.0009, 0.0022), "steel", fr, parent)
    return fr.p(side * (W / 2 + 0.0039), 0, Lb - 0.0047), fr.u * side


def accordion(L, n, p_mid, p_end, y0, z, seed, samples=8, lift_at=None):
    """Centre line of a flat cable folded back and forth (an accordion) lying flat: n layers between x = -L/2 and +L/2,
    layer 0 on the floor running towards +x, each fold a loose half turn. The layers spread apart towards the folds
    (p_mid at the middle, where the tie squeezes them, p_end at the folds); lift_at lifts the stack by the tie's
    thickness where the tie passes under it."""
    rng = random.Random(seed)
    zs = [z + rng.uniform(-0.0007, 0.0007) for _ in range(n)]
    ends = [(-L / 2 + rng.uniform(-0.002, 0.002), L / 2 + rng.uniform(-0.002, 0.002)) for _ in range(n)]

    def pitch(x):
        return p_mid + (p_end - p_mid) * min(1.0, (2 * abs(x) / L)) ** 2

    def layer_y(i, x):
        y = y0 + i * pitch(x)
        if lift_at is not None:
            y += (TIE_T + 0.0002) * math.exp(-((x - lift_at) / 0.007) ** 2)
        return y
    pts = []
    for i in range(n):
        xa, xb = ends[i]
        if i % 2:
            xa, xb = xb, xa
        for k in range(samples + 1):
            t = k / samples
            x = xa + (xb - xa) * t
            # a slight sideways drift along each layer
            zz = zs[i] + 0.0005 * math.sin(math.pi * t + i)
            pts.append(V((x, layer_y(i, x), zz)))
        if i < n - 1:
            # the fold up to the next layer: a half turn bulging past the end
            xe = xb
            y1, y2 = layer_y(i, xe), layer_y(i + 1, xe)
            R = (y2 - y1) / 2
            yc = (y1 + y2) / 2
            out = 1 if xb > xa else -1
            for k in range(1, 8):
                ph = -math.pi / 2 + math.pi * k / 8
                pts.append(V((xe + out * R * math.cos(ph) * 1.25, yc + R * math.sin(ph), zs[i] + (zs[i + 1] - zs[i]) * k / 8)))
    return pts, pitch


def build_coil_sata_pair(root):
    """Two flat 0.5 m SATA data cables (black, latching plugs; one with a right-angle end), each folded in five layers,
    lying side by side and held by a white twist tie round the middle. Each cable's first plug lies past the -x end,
    its last plug (the right-angle one on cable 2) beside the bundle, its lead curling back from the top layer."""
    L = 0.083
    n = 5
    y0 = SATA_T / 2 + 0.0001
    H = 0.0058
    xt = -0.008
    p_mid, p_end = SATA_T + 0.00012, 0.0021
    zc = (0.0047, -0.0047)
    for ci, z in enumerate(zc):
        pts, pitch = accordion(L, n, p_mid, p_end, y0, z, seed=11 + ci, lift_at=xt)
        # plug A past the -x end, on the floor, face towards -x
        fa = V((-L / 2 - 0.0035 - 0.0185, H / 2, 0.0056 if ci == 0 else -0.0056))
        drop_stub(PL.plug_sata_data, P.Frame(fa, (1, 0, 0), (0, 1, 0)), root)
        ea = fa + V((0.0185, 0, 0))
        start = lead(ea, (1, 0, 0), pts[0], (1, 0, 0), 6, 0.002, 0.002, lift=0.0)
        top = pts[-1]
        if ci == 0:
            # plug B beside the bundle (+z side), face towards -x, its cable curling back from the top layer
            fb = V((0.0225, H / 2, 0.0175))
            drop_stub(PL.plug_sata_data, P.Frame(fb, (1, 0, 0), (0, 1, 0)), root)
            eb, tb = fb + V((0.0185, 0, 0)), V((1, 0, 0))
        else:
            # the right-angle plug beside the bundle (-z side), face towards -z, the cable entering its +x side
            fb = V((0.0300, H / 2, -0.0200))
            eb, tb = sata_right_angle(P.Frame(fb, (0, 0, 1), (0, 1, 0)), root, side=1)
        end = lead(top, (1, 0, 0), eb, -tb, 16, 0.018, 0.012, lift=0.0)
        for k, p in enumerate(end):
            p.y = max(p.y, SATA_W / 2 * math.sin(math.pi * k / 16) ** 0.7 + 0.0002)
        path = start[:-1] + pts + end[1:]
        # flat on the first lead, across = z through the folds; on the last lead the cable rolls up on its edge to
        # make the U-turn (a flat cable only bends the easy way) and lies flat again at the plug
        ne = len(end) - 1
        roll = []
        for k in range(1, len(end)):
            T = (end[min(k + 1, ne)] - end[k - 1]).normalized()
            flat_side = V((0, 1, 0)).cross(T)
            a = (math.pi / 2) * math.sin(math.pi * k / ne) ** 0.7
            roll.append(flat_side.normalized() * math.cos(a) + V((0, 1, 0)) * math.sin(a))
        sides = [None] * (len(start) - 1) + [V((0, 0, 1))] * len(pts) + roll
        geo_obj(root, ribbon_sweep(path, oval_profile(SATA_W, SATA_T, 10), sides), "sata_cable", "rubber", 60.0)
    # the tie round both stacks, a little off centre
    pm = pitch(xt)
    hh = (n - 1) * pm / 2 + SATA_T / 2 + 0.0003
    cen = V((xt, y0 + (n - 1) * pm / 2 + TIE_T + 0.0003, 0.0))
    add_tie(root, cen, (1, 0, 0), 0.0047 + SATA_W / 2 + 0.0009, hh)
    return dict(note="two 0.5 m flat SATA data cables folded in 5 layers; cable 2 ends in a right-angle plug")


# ====================================================================== syringe_paste

SYR_LABEL = "smallparts_syringe_label"


def syringe_label_texture():
    """tex_smallparts_syringe_label: the wrap-round label. u runs along the barrel (0 = the plunger end, 1 = towards
    the tip), v round it (0.5 = the top of the barrel as it lies)."""
    w, h = 1024, 1024
    art = P.Art(w, h, bg=(0.96, 0.98, 1.0), name="syr_label")
    navy, ice, ink = (0.05, 0.13, 0.30), (0.55, 0.80, 0.97), (0.10, 0.12, 0.16)
    art.grad(0, 0, w, h, (0.86, 0.93, 0.99), (0.98, 0.99, 1.0))
    # navy bands along both long edges of the visible face, an ice stripe inside them
    for y in (230, 760):
        art.rect(0, y, w, 34, navy)
        art.rect(0, y + (34 if y < 500 else -10), w, 10, ice)
    # the mountain-peak logo at the plunger end, then the brand along the barrel
    cx, cy = 120, 512
    art.poly([(cx - 85, cy - 70), (cx - 10, cy + 85), (cx + 30, cy + 20), (cx + 55, cy + 55), (cx + 95, cy - 70)], navy)
    art.poly([(cx - 34, cy + 32), (cx - 10, cy + 85), (cx + 13, cy + 40), (cx - 2, cy + 50)], (1, 1, 1))
    art.poly([(cx + 42, cy + 34), (cx + 55, cy + 55), (cx + 68, cy + 34)], (1, 1, 1))
    art.text("FROSTPEAK", 590, 520, 150, navy, "seguibl.ttf", align="CENTER", valign="CENTER", maxw=760)
    art.text("THERMAL COMPOUND", 560, 400, 64, ink, "arialbd.ttf", align="CENTER", valign="CENTER", maxw=640)
    art.rect(800, 600, 190, 92, navy)
    art.text("1.5 g", 895, 646, 64, (1, 1, 1), "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("8.5 W/mK", 520, 646, 54, (0.18, 0.45, 0.75), "arialbd.ttf", align="CENTER", valign="CENTER")
    # the sides and underneath: small print
    art.text("NON-CONDUCTIVE \u2022 NON-CURING \u2022 -50 TO 150 \u00b0C", 512, 150, 34, ink, "arialbd.ttf", align="CENTER",
             valign="CENTER", maxw=960)
    art.text("Apply a pea-sized dot to the centre of the CPU.", 512, 870, 32, ink, "arial.ttf", align="CENTER",
             valign="CENTER", maxw=960)
    art.text("LOT FP2611  EXP 10/2029", 512, 60, 28, (0.35, 0.38, 0.45), "consola.ttf", align="CENTER", valign="CENTER")
    art.text("FROSTPEAK.COM", 512, 960, 30, navy, "arialbd.ttf", align="CENTER", valign="CENTER")
    art.render(SYR_LABEL)
    art.dispose()


def build_syringe_paste(root):
    """A 1.5 g thermal paste syringe lying flat: a clear barrel with the grey paste showing in its front part, the nozzle
    under a ribbed grey cap, the black rubber stopper, a white X-ribbed plunger with its thumb pad, the finger flange,
    and the wrap-round FROSTPEAK label on the back part of the barrel. The tip points -z (the top edge of the print
    as a flat item; standing in a box, tip up)."""
    syringe_label_texture()
    Ro, Ri = 0.0036, 0.0029
    fs = P.Frame((0, Ro, 0), (0, 0, -1), (0, 1, 0))     # local +Z = towards the tip (a), local x = -x
    a_back, a_front, a_stop = -0.023, 0.025, 0.003
    # the barrel: one closed tube profile (outside forward to the nozzle tip, back along the inside)
    prof = [(Ri, a_back), (Ro, a_back), (Ro, a_front), (0.0024, a_front + 0.002), (0.0016, a_front + 0.006),
            (0.0011, 0.041), (0.00055, 0.041), (0.00055, a_front + 0.006), (0.0012, a_front + 0.0022),
            (Ri, a_front - 0.0002), (Ri, a_back)]
    P.lathe("barrel", prof, "clear_plastic", fs, 24, root, smooth=40)
    # the paste, from the stopper into the nozzle
    P.lathe("paste", [(0, a_stop), (Ri - 0.00006, a_stop), (Ri - 0.00006, a_front - 0.0003), (0.00115, a_front + 0.0021),
                      (0.0005, 0.0405), (0, 0.0405)], "paste", fs, 20, root, smooth=40)
    # the plunger (a moving piece: it slides in towards the tip): the rubber stopper with its two sealing ribs, an
    # X-ribbed rod, a disc behind the stopper, the thumb pad
    a_pad = -0.0400
    pl = P.anchor("A_PLUNGER_0", fs.sub(0, 0, a_pad - 0.0013, fwd=(0, 0, -1), up=(0, 1, 0)), (0.010, 0.009, 0.006), root,
                  meta=f"slide=-z,dist={a_front - a_stop - 0.001:.3f}")
    P.lathe("stopper", [(0, a_stop - 0.0001), (Ri - 0.0002, a_stop - 0.0001), (Ri - 0.00002, a_stop - 0.0008),
                        (Ri - 0.0003, a_stop - 0.0022), (Ri - 0.00002, a_stop - 0.0036), (Ri - 0.0002, a_stop - 0.0048),
                        (0.0012, a_stop - 0.0050), (0, a_stop - 0.0050)], "rubber", fs, 20, pl, smooth=40)
    for ang in (45, 135):
        rf = fs.sub(0, 0, (a_stop - 0.005 + a_pad) / 2, fwd=(0, 0, 1),
                    up=(math.cos(ang * DEG), math.sin(ang * DEG), 0))
        P.cube("plunger_rib", (0, 0, 0), (0.0007, 2 * Ri - 0.0007, (a_stop - 0.005) - a_pad), "white_plastic", rf, pl)
    P.cylinder("plunger_disc", fs.sub(0, 0, a_stop - 0.0058), Ri - 0.0003, 0.0008, "white_plastic", 20, pl)
    pad = [(0.0045 * math.cos(TAU * k / 24), Ro * 0.98 * math.sin(TAU * k / 24)) for k in range(24)]
    P.slab("plunger_pad", pad, 0.0013, "white_plastic", fs.sub(0, 0, a_pad - 0.00065), parent=pl)
    # the finger flange at the back of the barrel
    P.slab("flange", P.rrect(0.0120, 2 * Ro * 0.98, 0.0032, 0, 0, 4), 0.0014, "clear_plastic", fs.sub(0, 0, a_back + 0.0007),
           holes=[P.circle(Ri, 0, 0, 20)], parent=root)
    # the cap over the nozzle (a moving piece: it pulls off towards the tip): a ribbed grey sleeve with a rounded end
    cap = P.anchor("A_CAP_0", fs.sub(0, 0, 0.0315), (0.0075, 0.0075, 0.0145), root, meta="pull=-z,dist=0.015")
    P.lathe("cap", [(0.0016, 0.0315), (0.0029, 0.0315), (0.0030, 0.0420), (0.0024, 0.0440), (0.0010, 0.0447), (0, 0.0447),
                    (0, 0.0330), (0.0016, 0.0330), (0.0016, 0.0315)], "grey_plastic", fs, 20, cap, smooth=45)
    for k in range(8):
        ang = k * 45 * DEG + 22.5 * DEG
        rf = fs.sub(0.00305 * math.cos(ang), 0.00305 * math.sin(ang), 0.0368, fwd=(0, 0, 1),
                    up=(math.cos(ang), math.sin(ang), 0))
        P.cube("cap_rib", (0, 0, 0), (0.0005, 0.0005, 0.0090), "grey_plastic", rf, cap)
    P.anchor("A_TIP_0", fs.sub(0, 0, 0.041), (0.003, 0.003, 0.003), root, meta="paste=1.5g")
    # the label wrapped round the back part of the barrel (over the plunger), u along the barrel, v round it
    a0, a1, rl = -0.0215, 0.0045, Ro + 0.00007
    ctr = V(fs.o)

    def lab(u, v):
        th = TAU * v - math.pi / 2          # v = 0.5 on top
        a = a0 + (a1 - a0) * u
        return ctr + V((0, 0, -a)) + V((rl * math.cos(th), rl * math.sin(th), 0))
    geo = S.grid_surface(lab, 10, 28, uv_fn=lambda u, v: (u, 1 - v))
    geo = S.facing(geo, lambda pc: V((pc.x, pc.y - ctr.y, 0)))
    geo_obj(root, geo, "label", "tex_" + SYR_LABEL, 40.0)
    return dict(note="1.5 g FROSTPEAK paste syringe, 7.2 mm barrel; tip at -z", label=SYR_LABEL)


# ====================================================================== fan connector housings (female)

FAN_PITCH = 0.00254
FAN_PIN_LEN = 0.0058      # the pins stand this far in front of the contact face (as a board header's)


def fan_female(fr, parent, pins, tag, colours, anchors_root=None, wires=True, missing=()):
    """The receiving end of a fan splitter output or extension cable: a housing with the pins standing in front of its
    contact face and the polarising wall with its friction ramp along the +Y side (over pins 1-3), the shape a fan's own
    plug slides onto. Frame: origin at the contact face centre, +Z back along the wires, +Y the ramp side. Pin 1 (GND)
    is at +x, the 4-pin's PWM pin at -x (outside the wall, so a 3-pin plug fits too). missing: pin indices (0-based)
    left out (a splitter's second output has no tach pin); wires=False leaves the wire stubs off."""
    p = FAN_PITCH
    W = pins * p + 0.0004 if pins == 4 else pins * p + 0.0003
    L = 0.0075
    yb0, yb1 = -0.0025, 0.0021           # body
    py = -0.0002                         # pin row
    xs = [(1.5 - k) * p if pins == 4 else (1.0 - k) * p for k in range(pins)]   # pin k+1 at xs[k]
    # the housing, its crimp windows (two shallow pockets per terminal on the -Y side) and a pin-1 nick
    P.cube("ff_body", (0, (yb0 + yb1) / 2, L / 2), (W, yb1 - yb0, L), tag, fr, parent, bevel=0.00025)
    for x in xs:
        P.cube("ff_window", (x, yb0 - 0.00005, L * 0.55), (0.0011, 0.0002, 0.0022), "connector_black", fr, parent)
    P.cube("ff_pin1", (xs[0], yb1 + 0.00005, 0.0006), (0.0008, 0.0002, 0.0008), "connector_black", fr, parent)
    # the polarising wall over pins 1-3, flush with the top and standing as tall as the pins, with its ramp
    x0, x1 = xs[2] - p * 0.5 - 0.0002, xs[0] + p * 0.5 + 0.0002
    wy0, wy1 = py + 0.0023, py + 0.0032
    P.cube("ff_wall", ((x0 + x1) / 2, (wy0 + wy1) / 2, (-FAN_PIN_LEN + L * 0.5) / 2), (x1 - x0, wy1 - wy0, FAN_PIN_LEN + L * 0.5),
           tag, fr, parent, bevel=0.0002)
    xm = (x0 + x1) / 2
    ramp = [(0.0, 0.0), (0.0, -0.0028), (0.00045, -0.0018), (0.00045, -0.0004)]   # (into the gap, along -z)
    rf = fr.sub(xm, wy0, -0.0008, fwd=(1, 0, 0), up=(0, -1, 0))     # local x = -z, local y = -Y (into the gap)
    P.slab("ff_ramp", [(-a, b) for (b, a) in ramp], 0.0026, tag, rf, parent=parent)
    # side ribs that guide the plug
    for sx in (-1, 1):
        P.cube("ff_guide", (sx * (W / 2 - 0.0002), py, -0.0012), (0.0004, 0.0012, 0.0024), tag, fr, parent)
    # the pins: square posts with chamfered tips, gold plated, running into the housing
    for k, x in enumerate(xs):
        if k in missing:
            continue
        P.cube("ff_pin", (x, py, (-FAN_PIN_LEN + 0.0035) / 2), (0.00064, 0.00064, FAN_PIN_LEN + 0.0035), "gold", fr, parent)
        P.cube("ff_pin_tip", (x, py, -FAN_PIN_LEN - 0.00012), (0.0004, 0.0004, 0.00024), "gold", fr, parent)
    # wire stubs out of the back (like the plug models)
    if wires:
        end = PL.wire_stubs(fr, parent, [(x, py) for x in xs], 0.0007, L, 0.026, "rubber", colours, "ff_wire", converge=0.25)
    else:
        end = fr.p(0, py, L)
    if anchors_root is not None:
        H = wy1 - yb0
        P.anchor("A_HIT_0", fr.sub(0, (yb0 + wy1) / 2, (L - FAN_PIN_LEN) / 2), (W + 0.002, H + 0.002, L + FAN_PIN_LEN + 0.001),
                 anchors_root)
        P.anchor("A_CABLE_0", P.Frame(end, fr.w, fr.v), (0.005, 0.005, 0.01), anchors_root, meta=f"r=0.0025,n={pins}")
        pin1 = -xs[0]    # in the port anchor's axes (its x = -x here: it faces -Z)
        pinout = "GND|12V|SENSE|PWM" if pins == 4 else "GND|12V|SENSE"
        P.anchor("A_PORT_FAN_0", fr.sub(0, py, -FAN_PIN_LEN, fwd=(0, 0, -1), up=(0, 1, 0)), (W + 0.002, 0.0065, 0.008),
                 anchors_root, meta=f"depth={FAN_PIN_LEN:.4f},pins={pins};pin1={pin1:.5f},0.00000;colstep=0.00254,0.00000;"
                                    f"pinout={pinout}")
    return dict(W=W, H=wy1 - yb0, L=L, end=end, xs=xs, py=py)


def build_fan4_female(root):
    r = fan_female(P.F((0, 0, 0)), root, 4, "connector_black", ["cable_black"] * 4, anchors_root=root)
    return dict(hit=1, note=f"4-pin PWM receiving housing W {r['W']:.4f} H {r['H']:.4f} L {r['L']:.4f}, pins "
                            f"{FAN_PIN_LEN:.4f} in front of the face")


def build_fan3_female(root):
    r = fan_female(P.F((0, 0, 0)), root, 3, "connector_white", ["black", "red", "yellow"], anchors_root=root)
    return dict(hit=1, note=f"3-pin receiving housing W {r['W']:.4f} H {r['H']:.4f} L {r['L']:.4f}, pins "
                            f"{FAN_PIN_LEN:.4f} in front of the face")


# ====================================================================== coil_fan_splitter

SLEEVE_R = 0.0018          # the braided sleeve over the four wires


def shrink_tube(parent, a, b, w, h, y=None, name="shrink"):
    """A flattened heat-shrink sleeve from point a to point b (w across, h high)."""
    a, b = V(a), V(b)
    pts = [a + (b - a) * (k / 3) for k in range(4)]
    geo = ribbon_sweep(pts, oval_profile(w, h, 12), [None] * 4)
    return geo_obj(parent, geo, name, "black_plastic", 45.0)


def build_coil_fan_splitter(root):
    """A 4-pin PWM 1-to-2 fan splitter (about 0.1 m from the input to each output) in black braided sleeving, folded
    for its bag: the input plug (the plug_fan4 look, onto the board header) and the two receiving outputs (fan4_female;
    the second has no tach pin) lie side by side at the +z end, the two branches loop back over the top from the
    heat-shrunk junction, and a white twist tie holds the three sleeves together."""
    zf = 0.034                      # the connectors' contact faces (all pointing +z)
    yp = 0.0034                     # plug_fan4 lying flat: its ribs touch the floor
    ff = fan_female(P.Frame((-0.0125, 0.0028, zf - 0.006), (0, 0, -1), (0, 1, 0)), root, 4, "connector_black", None,
                    wires=False)
    fan_female(P.Frame((0.0125, 0.0028, zf - 0.006), (0, 0, -1), (0, 1, 0)), root, 4, "connector_black", None, wires=False,
               missing=(2,))
    drop_stub(PL.plug_fan4, P.Frame((0.0, yp, zf), (0, 0, -1), (0, 1, 0)), root, keys=("fan_wire",))
    tie_z = 0.0
    lift = TIE_T + 0.0002

    def bump(p):
        p = V(p)
        p.y += lift * math.exp(-((p.z - tie_z) / 0.006) ** 2)
        return p
    # heat shrink on each connector's back, and on the junction
    zb_f = zf - 0.006 - ff["L"]          # the outputs' backs
    zb_p = zf - 0.013                    # the input plug's back
    for x, yc, zb in ((-0.0125, 0.0026, zb_f), (0.0125, 0.0026, zb_f), (0.0, yp - 0.0002, zb_p)):
        shrink_tube(root, (x, yc, zb + 0.001), (x, yc - 0.0003, zb - 0.008), 0.0058, 0.0030)
    zj0, zj1 = -0.012, -0.026
    shrink_tube(root, (0, 0.0023, zj0 + 0.001), (0, 0.0023, zj1), 0.0082, 0.0044, name="junction")
    # the input lead: plug -> junction
    pin = [V((0.0, yp - 0.0003, zb_p - 0.007)), V((0.0, 0.0024, zb_p - 0.016)), V((0.0, SLEEVE_R + 0.0001, 0.004)),
           V((0.0, SLEEVE_R + 0.0001, -0.004)), V((0.0, 0.0022, zj0 + 0.002))]
    pts = [bump(p) for p in P.smooth_path(pin, 5)]
    sweep(root, pts, circle_profile(SLEEVE_R, 8), "fabric_black", "sleeve", smooth=60.0)
    # the branches: out of the junction's far end, a loose loop back over the top, beside the junction, together under
    # the tie, then apart to their outputs
    for sx in (-1, 1):
        ctrl = [(sx * 0.0019, 0.0022, zj1 - 0.001), (sx * 0.0024, 0.0020, zj1 - 0.004)]
        cxu, czu, ru = sx * 0.0074, zj1 - 0.0045, 0.0050
        for k in range(1, 8):
            ph = math.pi - math.pi * k / 8
            ctrl.append((cxu + sx * ru * math.cos(ph), SLEEVE_R + 0.0001, czu - ru * math.sin(ph)))
        ctrl += [(sx * 0.0124, SLEEVE_R + 0.0001, zj1 + 0.002), (sx * 0.0072, SLEEVE_R + 0.0001, zj0 + 0.004),
                 (sx * (SLEEVE_R * 2 + 0.0004), SLEEVE_R + 0.0001, tie_z), (sx * 0.0055, SLEEVE_R + 0.0001, 0.008),
                 (sx * 0.0118, 0.0021, zb_f - 0.010), (sx * 0.0125, 0.0024, zb_f - 0.007)]
        pts = [bump(p) for p in P.smooth_path(ctrl, 4)]
        sweep(root, pts, circle_profile(SLEEVE_R, 8), "fabric_black", "sleeve", smooth=60.0)
    # the twist tie round the three sleeves
    hw = SLEEVE_R * 3 + 0.0006
    cen = V((0.0, SLEEVE_R + 0.0001 + lift, tie_z))
    add_tie(root, cen, (0, 0, 1), hw, SLEEVE_R + 0.0002, pig_dir=(0, 0, -1))
    return dict(note="4-pin PWM 1-to-2 splitter, braided black sleeves, folded; output 2 without the tach pin")


# ====================================================================== registry and driver

MODELS = {
    "coil_dp": (build_coil_dp, dict(fit=("box_cable_dp A_ITEM_PART_0", (0.115, 0.115, 0.020)))),
    "coil_c13": (build_coil_c13, dict(fit=("box_psu_750 A_ITEM_CORD_0", (0.120, 0.090, 0.016)),
                                      fit2=("box_psu_450 A_ITEM_CORD_0", (0.090, 0.075, 0.014)))),
    "coil_sata_pair": (build_coil_sata_pair, dict(fit=("box_mb_ridge_b5/z4 A_ITEM_CORD_0", (0.120, 0.075, 0.012)))),
    "coil_fan_splitter": (build_coil_fan_splitter, dict(fit=("box_fan_splitter A_ITEM_PART_0", (0.070, 0.080, 0.012)),
                                                        wb=((90, 75), (-150, 30)))),
    "syringe_paste": (build_syringe_paste, dict(fit=("box_cooler_tower A_ITEM_HW_1 (kind=syringe; length along h)",
                                                     (0.012, 0.075, 0.009)), wb=((90, 70), (-150, 30)),
                                                views=[(60, 40), (-130, 25)], samples=48)),
    "fan4_female": (build_fan4_female, dict(frame_fixed=True, wb=((35, 25), (-145, 30)), views=[(40, 25), (-150, 30)])),
    "fan3_female": (build_fan3_female, dict(frame_fixed=True, wb=((35, 25), (-145, 30)), views=[(40, 25), (-150, 30)])),
}


def preview_materials():
    """Cycles stand-ins for tags the shared previews don't define (renders only)."""
    import bpy
    if bpy.data.materials.get("pbr_clear_plastic") is None:
        S._film_material("pbr_clear_plastic", (0.93, 0.96, 1.0), 0.05, 0.08, 0.7, 0.08)


def build(mid, prev):
    fn, cfg = MODELS[mid]
    root = new_root(mid)
    info = fn(root) or {}
    if cfg.get("flat", True) and not cfg.get("frame_fixed"):
        recentre(root)
    lo, hi = bounds(root)
    size = hi - lo
    if "hit" not in info:
        P.anchor("A_HIT_0", P.Frame(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2)), tuple(size), root)
    P.finalize(root, mid)
    c.export(root, mid)
    notes = [f"  size: {size.x:.4f} (x) x {size.y:.4f} (y) x {size.z:.4f} (z) m; bounds x {lo.x:.4f}..{hi.x:.4f}, "
             f"y {lo.y:.4f}..{hi.y:.4f}, z {lo.z:.4f}..{hi.z:.4f}"]
    if info.get("note"):
        notes.append("  note: " + info["note"])
    for key in ("fit", "fit2", "fit3"):
        fit = cfg.get(key)
        if fit:
            w, h, t = fit[1]
            notes.append(f"  space {fit[0]} (w {w}, h {h}, t {t}): margins w {w - size.x:+.4f}, h {h - size.z:+.4f}, "
                         f"t {t - size.y:+.4f}")
    tris, meshes = P.write_report(root, mid, "\n".join(notes))
    print("\n".join(notes))
    if prev:
        preview_materials()
        P.preview(root, mid, views=cfg.get("wb", ((0, 78), (-150, 30))), size=(900, 700))
        S.render(root, mid, cfg.get("views", [(25, 45), (-120, 30)]), size=(1000, 760), samples=cfg.get("samples", 40), start=2)
    return tris, meshes, tuple(round(x, 4) for x in size)


def main(argv):
    prev = "--nopreview" not in argv
    P.PREVIEW[0] = prev
    ids = [a for a in argv if not a.startswith("--")] or list(MODELS)
    out = {}
    for mid in ids:
        if mid not in MODELS:
            print("UNKNOWN id", mid)
            continue
        out[mid] = build(mid, prev)
    for k, v in out.items():
        print("BUILT", k, v)
    return out


if __name__ == "__main__":
    main(c.args())
