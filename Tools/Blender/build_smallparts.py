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


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def objects_since(before):
    return [o for o in bpy_objects() if o.name not in before]


def bpy_objects():
    import bpy
    return list(bpy.data.objects)


def drop_stub(build, *args):
    """Runs a build_plugs plug builder and removes the straight cable stub its overmould leaves (the coil's own
    cable continues from the strain relief instead). Returns the builder's result."""
    import bpy
    before = {o.name for o in bpy.data.objects}
    r = build(*args)
    for o in list(bpy.data.objects):
        if o.name not in before and "_cable" in o.name.split("#", 1)[0]:
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


def place_plug(build, origin, cable_dir, up=(0, 1, 0), parent=None):
    """Builds a build_plugs plug head with its contact face at origin and its cable leaving along cable_dir.
    Returns (relief end point, cable direction, info)."""
    fr = P.Frame(origin, cable_dir, up)
    info = drop_stub(build, fr, parent)
    return info


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
    lead_a = bezier(ea, da, p_start, t_start, 12, 0.03, 0.04)
    lead_b = bezier(p_end, t_end, eb, -db, 12, 0.04, 0.03)
    pts = lead_a[:-1] + loops + lead_b[1:]
    for p in pts:
        p.y = max(p.y, r)
    sweep(root, pts, circle_profile(r, 8, math.pi / 8), "rubber", "dp_cable")
    # the white twist tie (a moving piece: the code takes it off)
    tth = coil.tie
    cen, out, hw, hh = coil.bundle_section(tth)
    tan = coil.tangent(tth)
    tie_a = P.anchor("A_TIE_0", P.Frame(cen + V((0, hh, 0)), (0, 1, 0), tuple(tan)), (hw * 2 + 0.006, TIE_W + 0.012, hh * 2 + 0.006),
                     root, meta="tie=twist,colour=white")
    twist_tie(tie_a, cen, tan, (0, 1, 0), hw, hh, pig_dir=tan)
    return dict(note="1.8 m DisplayPort cable (d 5.8 mm), 6 turns, both DP heads inside the coil")


# ====================================================================== registry and driver

MODELS = {
    "coil_dp": (build_coil_dp, dict(fit=("box_cable_dp A_ITEM_PART_0", (0.115, 0.115, 0.020)))),
}


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
    notes = [f"  size: {size.x:.4f} (x) x {size.y:.4f} (y) x {size.z:.4f} (z) m; bounds y {lo.y:.4f}..{hi.y:.4f}"]
    if info.get("note"):
        notes.append("  note: " + info["note"])
    fit = cfg.get("fit")
    if fit:
        w, h, t = fit[1]
        notes.append(f"  fits {fit[0]} (w {w}, h {h}, t {t}): margins w {w - size.x:+.4f}, h {h - size.z:+.4f}, t {t - size.y:+.4f}")
    tris, meshes = P.write_report(root, mid, "\n".join(notes))
    print("\n".join(notes))
    if prev:
        P.preview(root, mid, views=cfg.get("wb", ((30, 40), (-150, 30))), size=(900, 700))
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
