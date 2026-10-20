"""
shipping_bits: small packaging bits and the box cutter for build_shipping.py.

  twist_tie        a white plastic twist tie wrapped round a cable bundle, ends twisted into a pigtail. ORIGIN ON THE
                   BUNDLE AXIS (the loop's centre); the loop goes round the x axis (nominal bundle 30 mm wide (z) x
                   18 mm thick (y)), the pigtail points +y. A_TWIST_0 = the twist (fwd +y), A_HIT_0.
  twist_tie_open   the same tie untwisted and lying flat (kinked), origin bottom centre.
  velcro_strap     a 12 mm hook-and-loop strap wrapped 1.4 turns round a bundle; ORIGIN ON THE BUNDLE AXIS (x), nominal
                   bundle 24 x 18 mm; A_RIP_0 = the free tab (fwd = the pull direction), A_HIT_0.
  hw_bag           a small clear zip bag (60 x 80 mm) with a white write-on strip (A_LABEL_0, the code prints the text)
                   and four screws inside; lying flat, zip at -z.
  cable_pouch      a black zip pouch (0.18 x 0.045 x 0.12) with a woven brand label; zip along the +z edge
                   (A_ZIP_0 = the slider).
  box_cutter       a yellow 18 mm snap-off utility knife, blade out, lying on its side: length along z (blade tip +z),
                   spine towards +x. A_GRIP_0 (hand pose: fwd +z, up = spine), A_BLADE_0 (the tip), A_HIT_0.
"""
import math
import random

import shipping_lib as S
from shipping_lib import V, B, P, c


def ribbon_profile(w, t, n_end=3):
    """A flat ribbon cross-section with rounded edges (CCW), width along x."""
    pts = []
    r = t / 2
    for i in range(n_end + 1):
        a = -math.pi / 2 + math.pi * i / n_end
        pts.append((w / 2 - r + r * math.cos(a), r * math.sin(a)))
    for i in range(n_end + 1):
        a = math.pi / 2 + math.pi * i / n_end
        pts.append((-w / 2 + r + r * math.cos(a), r * math.sin(a)))
    return pts


# ====================================================================== twist ties

TIE_W, TIE_T = 0.0042, 0.0007


def build_twist_tie(kit):
    tag = "white_plastic"
    ry, rz = 0.0098, 0.0158          # tie centre line round a 30 x 18 mm bundle
    rh = 0.0011                      # pigtail helix radius
    yb = ry + 0.0008                 # pigtail base
    turns, hlen = 3.2, 0.0125
    pts = []
    # strand A: from the tip down the helix to the base (+z side)
    tip_a = []
    nh = 40
    for i in range(nh + 1):
        t = 1 - i / nh
        th = turns * 2 * math.pi * t
        y = yb + hlen * t
        tip_a.append(V((rh * math.sin(th), y, rh * math.cos(th))))
    # splayed tip
    pts.append(tip_a[0] + V((0.0012, 0.0035, 0.0012)))
    pts.append(tip_a[0] + V((0.0004, 0.0016, 0.0005)))
    pts += tip_a
    # the loop round the bundle (from the top, +z side, round the bottom, back to the top, -z side)
    nl = 56
    for i in range(1, nl):
        ph = 2 * math.pi * i / nl
        # start/end leaning in to meet the pigtail
        y = ry * math.cos(ph)
        z = rz * math.sin(ph)
        pts.append(V((0.0002 * math.sin(3 * ph), y, z)))
    # strand B: up the helix (opposite phase), -z side
    for i in range(nh + 1):
        t = i / nh
        th = turns * 2 * math.pi * t + math.pi
        y = yb + hlen * t
        pts.append(V((rh * math.sin(th), y, rh * math.cos(th))))
    pts.append(pts[-1] + V((-0.0005, 0.0016, -0.0004)))
    pts.append(pts[-2] + V((-0.0014, 0.0034, -0.0016)))
    n_a = 2 + nh + 1

    def scale(t):
        i = t * (len(pts) - 1)
        in_helix = i < n_a + 2 or i > len(pts) - n_a - 3
        return (1.2, 0.42) if in_helix else (1.0, 1.0)
    # the ribbon's width runs along the bundle axis (the path normal, seeded with +x)
    prof = [(y, -x) for (x, y) in ribbon_profile(TIE_W, TIE_T)]
    geo = S.sweep_profile(pts, prof, up=(1, 0, 0), scale=scale, smooth=True)
    kit.mb(tag).add(geo)
    kit.anchor("A_TWIST_0", (0, yb + hlen / 2, 0), (0.006, hlen + 0.006, 0.006), forward=(0, 1, 0), up=(0, 0, 1),
               meta="turns=2")
    kit.anchor("A_HIT_0", (0, 0.004, 0), (0.012, 2 * ry + hlen + 0.012, 2 * rz + 0.006))
    kit.finish(smooth=50.0)


def build_twist_tie_open(kit):
    tag = "white_plastic"
    rng = random.Random(3)
    L = 0.14
    pts = []
    n = 90
    for i in range(n + 1):
        t = i / n
        s = (t - 0.5) * L
        # the middle keeps a soft bend from the bundle, the ends a spiral kink from the twist
        z = 0.012 * math.cos(math.pi * (t - 0.5) * 1.6)
        end = max(0.0, abs(t - 0.5) * 2 - 0.68) / 0.32
        z += 0.0016 * end * math.sin(t * 95)
        y = 0.0005 + 0.0012 * end * (1 + math.sin(t * 95 + 1.3)) + 0.0006 * math.sin(t * 9)
        pts.append(V((s * 0.97, y, z - 0.006)))
    prof = ribbon_profile(TIE_W, TIE_T)

    def twist(t):
        end = max(0.0, abs(t - 0.5) * 2 - 0.68) / 0.32
        return 0.5 * end * math.sin(t * 95)
    geo = S.sweep_profile(pts, prof, up=(0, 1, 0), twist=twist, smooth=True)
    kit.mb(tag).add(geo)
    ys = [p.y for p in geo[0]]
    y0 = min(ys)
    kit.mb(tag).v = [V((p.x, p.y - y0, p.z)) for p in kit.mb(tag).v]
    kit.anchor("A_HIT_0", (0, 0.003, 0.0), (L, 0.006, 0.03))
    kit.finish(smooth=50.0)


# ====================================================================== velcro strap

def build_velcro(kit):
    tag = "velcro_black"
    w, t = 0.012, 0.0016
    ry, rz = 0.0095, 0.0125
    turns = 1.42
    n = 110
    pts = []
    for i in range(n + 1):
        f = i / n
        ph = -0.35 + turns * 2 * math.pi * f
        grow = t * 1.05 * (ph / (2 * math.pi))
        y = (ry + grow) * math.cos(ph)
        z = (rz + grow) * math.sin(ph)
        pts.append(V((0.0, y, z)))
    # the free tab lifts away a little at the end
    last = pts[-1]
    tan = (pts[-1] - pts[-2]).normalized()
    out = V((0, last.y, last.z)).normalized()
    for k in range(1, 7):
        pts.append(last + tan * 0.0028 * k + out * 0.0007 * k * k / 6)
    prof = [(x, y) for (x, y) in ribbon_profile(w, t, 2)]
    # the profile's width lies across the strap (along the bundle axis x)
    prof = [(-y, x) for (x, y) in prof]
    geo = S.sweep_profile(pts, prof, up=(1, 0, 0), smooth=True)
    kit.mb(tag).add(geo)
    tip = pts[-1]
    pull = (pts[-1] - pts[-4]).normalized()
    up = V((1, 0, 0))
    kit.anchor("A_RIP_0", tuple(tip), (w + 0.004, 0.006, 0.012), forward=tuple(pull), up=tuple(up), meta="rip=1")
    kit.anchor("A_HIT_0", (0, 0, 0), (w + 0.004, 2 * ry + 0.012, 2 * rz + 0.012))
    kit.finish(smooth=45.0)


# ====================================================================== hardware bag

HB_W, HB_L = 0.060, 0.080


def screw_geo(r_head=0.0032, h_head=0.0022, d=0.0035, length=0.006):
    """A pan-head screw along local +z: head base at z = 0, shank down to -length (simple thread rings)."""
    head = B.g_screw_head(r_head, h_head, "ph", n=12, dome=0.45)
    prof = [(0.0, -length), (d / 2 * 0.8, -length), (d / 2, -length + 0.0006)]
    k = 0
    z = -length + 0.0006
    while z < -0.0004:
        prof.append((d / 2 * (0.86 if k % 2 else 1.0), z))
        z += 0.00045
        k += 1
    prof += [(d / 2, 0.0), (0.0, 0.0)]
    shank = B.g_lathe(prof, 10)
    return B.merge(head, shank)


def build_hw_bag(kit):
    tag = "bag_clear"
    rng = random.Random(8)
    seal = 0.0035
    zip_z = -HB_L / 2 + 0.010
    # the screws inside (lying on the bottom film)
    screws = []
    sg = screw_geo()
    for i, (x, z, rot) in enumerate([(-0.012, 0.012, 30), (0.010, 0.020, 115), (0.006, -0.002, 70), (-0.008, 0.028, 160)]):
        a = rot * S.DEG
        axis = V((math.cos(a), 0, math.sin(a)))
        M = B.frame(axis, (0, 1, 0))
        pos = V((x, 0.0032 + 0.0004, z))
        kit.mb("steel").add(sg, M, pos)
        screws.append((pos, axis))

    def bump(x, z):
        h = 0.0
        p = V((x, 0, z))
        for pos, axis in screws:
            d = p - V((pos.x, 0, pos.z))
            along = d.dot(axis)
            along = max(-0.0065, min(0.0025, along))
            q = d - axis * along
            dist = q.length
            h = max(h, 0.0074 * math.exp(-(dist / 0.0055) ** 2))
        return h

    def env(x, z):
        u = (x / (HB_W / 2 - seal))
        v = (z - (zip_z + 0.002 + HB_L / 2 - seal)) / 2   # unused
        fu = max(0.0, 1 - abs(x) / (HB_W / 2 - seal)) ** 0.35
        z0, z1 = zip_z + 0.003, HB_L / 2 - seal
        fv = max(0.0, min(z - z0, z1 - z) / 0.006)
        return fu * min(1.0, fv) ** 0.5

    def top(i, j):
        x = -HB_W / 2 + seal + (HB_W - 2 * seal) * i
        z = zip_z + 0.003 + (HB_L / 2 - seal - zip_z - 0.003) * j
        h = env(x, z) * (0.0012 + bump(x, z) + 0.0003 * math.sin(x * 400 + z * 230))
        return (x, 0.0004 + h, z)

    def bot(i, j):
        x = -HB_W / 2 + seal + (HB_W - 2 * seal) * i
        z = zip_z + 0.003 + (HB_L / 2 - seal - zip_z - 0.003) * j
        return (x, 0.0002, z)
    mb = kit.mb(tag)
    mb.add(S.facing(S.grid_surface(top, 12, 16, smooth=True), (0, 1, 0)))
    mb.add(S.facing(S.grid_surface(bot, 1, 1, smooth=False), (0, -1, 0)))
    # the flat seals round three sides, and the lip above the zip (two-sided thin slabs)
    for (x0, x1, z0, z1) in ((-HB_W / 2, -HB_W / 2 + seal, zip_z, HB_L / 2), (HB_W / 2 - seal, HB_W / 2, zip_z, HB_L / 2),
                             (-HB_W / 2 + seal, HB_W / 2 - seal, HB_L / 2 - seal, HB_L / 2),
                             (-HB_W / 2, HB_W / 2, -HB_L / 2, zip_z + 0.003)):
        mb.add(B.xf(B.g_box((x1 - x0, 0.0005, z1 - z0)), None, ((x0 + x1) / 2, 0.00045, (z0 + z1) / 2)))
    # the zip: two tracks across
    for dz in (-0.0011, 0.0011):
        mb.add(B.xf(B.g_box((HB_W - 0.001, 0.0011, 0.0013), bevel=0.0004), None, (0, 0.0009, zip_z + dz)))
    # the white write-on strip (printed on the film, following it)
    lw, lh = 0.046, 0.013
    lz = zip_z + 0.0035 + lh / 2 + 0.0015

    def lab(i, j):
        x = -lw / 2 + lw * i
        z = lz - lh / 2 + lh * j
        tx, ty, tz = top((x + HB_W / 2 - seal) / (HB_W - 2 * seal), (z - zip_z - 0.003) / (HB_L / 2 - seal - zip_z - 0.003))
        return (x, ty + 0.0005, z)
    kit.mb("paper_white").add(S.facing(S.grid_surface(lab, 10, 4, smooth=True), (0, 1, 0)))
    ly = lab(0.5, 0.5)[1]
    kit.anchor("A_LABEL_0", (0, ly, lz), (lw, lh, 0.0002), forward=(0, 1, 0), up=(0, 0, -1), meta="print=hw_label")
    kit.anchor("A_HIT_0", (0, 0.004, 0), (HB_W, 0.009, HB_L))
    kit.finish(smooth=45.0)


# ====================================================================== cable pouch

PO = (0.18, 0.045, 0.12)


def pouch_label_texture():
    import numpy as np
    w, h = 512, 160

    def draw(a):
        a.rect(0, 0, w, h, (0.05, 0.05, 0.055))
        a.rect(10, 10, w - 20, h - 20, (0.09, 0.09, 0.095))
        a.text("AMPERE", w / 2, h * 0.56, 70, (0.88, 0.88, 0.86), "FRAMDCN.TTF", align="CENTER", valign="CENTER", maxw=w * 0.8)
        a.text("MODULAR CABLES", w / 2, h * 0.2, 22, (0.85, 0.62, 0.22), "arialbd.ttf", align="CENTER", valign="CENTER")
    arr = S.art_layer(w, h, "pouch_label", draw)
    # a woven look: fine horizontal ribs
    yy = np.arange(h)[:, None].astype(np.float32)
    rib = 0.88 + 0.12 * (0.5 + 0.5 * np.sin(yy * 2.2))
    arr[..., :3] *= rib[..., None]
    arr[..., 3] = 1.0
    return P.save_png(arr, "ship_pouch_label")


def build_cable_pouch(kit):
    """A soft pillow-shaped pouch: top and bottom panels sewn round a squircle outline (with piping), a zip along the
    +z side with a slider and pull, and a woven label on top."""
    tag = "fabric_black"
    a, b, cz = PO[0] / 2, PO[1] / 2, PO[2] / 2
    rng = random.Random(4)
    ph = [rng.uniform(0, 6.28) for _ in range(8)]
    ne = 5.0      # outline squareness

    def plan(u, v):
        m = max(abs(u), abs(v))
        if m < 1e-9:
            return 0.0, 0.0
        bu, bv = u / m, v / m
        k = 1.0 / (abs(bu) ** ne + abs(bv) ** ne) ** (1.0 / ne)
        return a * u * k, cz * v * k

    def fill(u, v):
        r = (abs(u) ** 6 + abs(v) ** 6) ** (1 / 6)
        return max(0.0, 1.0 - r ** 6) ** 0.42

    def top(i, j):
        u, v = i * 2 - 1, j * 2 - 1
        x, z = plan(u, v)
        f = fill(u, v)
        wr = (0.0016 * S.fbm(V((x * 30, z * 30, 0.3)), 3, seed=3) * f
              + 0.0011 * (1 - f) * math.sin(math.atan2(v, u) * 22 + ph[0]) * min(1.0, 4 * f))
        return (x, b + b * 0.97 * f + wr, z)

    def bot(i, j):
        u, v = i * 2 - 1, j * 2 - 1
        x, z = plan(u, v)
        f = fill(u, v)
        return (x, max(0.0, b - b * min(1.0, 1.3 * f)), z)
    mb = kit.mb(tag)
    mb.add(S.facing(S.grid_surface(top, 22, 15, smooth=True), (0, 1, 0)))
    mb.add(S.facing(S.grid_surface(bot, 10, 7, smooth=True), (0, -1, 0)))
    # the outline (seam), and the zip span along +z
    ring = []
    n_r = 64
    for k in range(n_r):
        t = 2 * math.pi * k / n_r
        u, v = math.cos(t), math.sin(t)
        x, z = plan(u, v)
        ring.append(V((x, b, z)))
    zip_x = 0.82 * a
    pip = [(0.0017 * math.cos(t), 0.0017 * math.sin(t)) for t in [k * 2 * math.pi / 6 for k in range(6)]]
    # piping: everywhere but the zip span
    run = []
    runs = []
    for p in ring + ring[:1]:
        on_zip = p.z > 0 and abs(p.x) < zip_x - 0.004
        if on_zip:
            if len(run) > 1:
                runs.append(run)
            run = []
        else:
            run.append(p + V((p.x, 0, p.z)).normalized() * 0.0006)
    if len(run) > 1:
        runs.append(run)
    # join the last run onto the first (the ring starts at +x, outside the zip)
    if len(runs) > 1:
        runs[0] = runs[-1] + runs[0]
        runs.pop()
    for r_ in runs:
        mb.add(S.sweep_profile(r_, pip, up=(0, 1, 0), smooth=True))
    # the zip: tape and an interlocking chain of teeth along the +z edge
    zpts = [p for p in ring if p.z > 0 and abs(p.x) < zip_x + 0.002]
    zpts.sort(key=lambda p: p.x)
    zc = max(p.z for p in zpts)
    mb.add(B.xf(B.g_box((2 * zip_x, 0.0085, 0.0012)), None, (0, b, zc - 0.0002)))
    pitch = 0.0021
    x = -zip_x
    k = 0
    while x < zip_x:
        dy = 0.0011 if k % 2 else -0.0011
        kit.mb("black_plastic").add(B.g_box((0.0016, 0.0021, 0.0019)), None, (x, b + dy * 0.5, zc + 0.0009))
        x += pitch * 0.75
        k += 1
    # slider and pull tab (hanging down against the side)
    sx = zip_x * 0.55
    kit.mb("steel_dark").add(B.g_box((0.0085, 0.0062, 0.0042), bevel=0.0013, seg=2), None, (sx, b, zc + 0.0026))
    tab = B.merge(B.xf(B.g_box((0.0062, 0.017, 0.0014), bevel=0.0006, seg=2), None, (0, -0.0085, 0)),
                  B.xf(B.g_cyl(0.0016, 0.0062, 8), B.frame((1, 0, 0), (0, 1, 0)), (0, 0, 0)))
    M = B.rot("x", -12 * S.DEG)
    kit.mb("steel_dark").add(tab, M, (sx, b - 0.0028, zc + 0.0052))
    kit.anchor("A_ZIP_0", (sx, b, zc + 0.004), (0.012, 0.012, 0.01), forward=(0, 0, 1), up=(0, 1, 0), meta="zip=x")
    # the woven brand label on the top, following the panel
    pouch_label_texture()
    lw, lh = 0.052, 0.0165
    lzc = cz * 0.42

    def lab(i, j):
        x = -lw / 2 + lw * i
        z = lzc - lh / 2 + lh * j
        best = None
        # the top panel height at (x, z): invert the plan map approximately (the middle is near-linear)
        u, v = x / a, z / cz
        return (x, top((u + 1) / 2, (v + 1) / 2)[1] + 0.0005, z)
    labg = S.grid_surface(lab, 4, 2, smooth=True, uv_fn=lambda u, v: (1 - u, 1 - v))
    kit.mb("tex_ship_pouch_label").add(S.facing(labg, (0, 1, 0)))
    kit.anchor("A_HIT_0", (0, b, 0), (PO[0], PO[1], PO[2]))
    kit.finish(smooth=50.0)
    return PO


# ====================================================================== box cutter

BC_L = 0.160          # body length (z)
BC_H = 0.026          # body height (spine to belly, along x)
BC_T = 0.0155         # thickness (y, lying on its side)
BLADE_OUT = 0.030


def cutter_texture():
    """tex_ship_cutter: yellow moulded plastic with the brand print. The body's side faces map onto it with u from the
    butt (0) to the nose (1) and v from the spine (0) to the belly (1), so the print reads on the +y face."""
    w, h = 1024, 256

    def draw(a):
        a.rect(0, 0, w, h, (0.97, 0.77, 0.06))
        ink = (0.05, 0.05, 0.05)
        a.text("SNAPLINE", w * 0.735, h * 0.56, 46, ink, "impact.ttf", align="CENTER", valign="CENTER")
        a.text("18 mm  •  AUTO-LOCK", w * 0.735, h * 0.34, 17, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
        a.poly([(w * 0.585, h * 0.17), (w * 0.635, h * 0.17), (w * 0.635, h * 0.11), (w * 0.665, h * 0.20),
                (w * 0.635, h * 0.29), (w * 0.635, h * 0.23), (w * 0.585, h * 0.23)], ink)
        a.text("CAUTION: SHARP BLADE", w * 0.735, h * 0.80, 12, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    arr = S.art_layer(w, h, "cutter", draw)
    nz = S.noise_field(h, w, 10.0, 31)
    arr[..., :3] *= (0.985 + 0.015 * nz)[..., None]
    arr[..., 3] = 1.0
    return P.save_png(arr, "ship_cutter")


def cutter_outline():
    """Side view (u along z from the butt -L/2 to the nose, v from the belly -H/2 to the spine +H/2)."""
    L, H = BC_L, BC_H
    pts = []
    for i in range(9):          # butt: a round end
        a = math.pi / 2 + math.pi * i / 8
        pts.append((-L / 2 + H / 2 + (H / 2) * math.cos(a), (H / 2) * math.sin(a)))
    for i in range(1, 13):      # belly with a finger dip, rising to the nose
        t = i / 12
        u = -L / 2 + H / 2 + (L - H / 2 - 0.012) * t
        v = -H / 2 + 0.0025 * math.sin(math.pi * min(1.0, t / 0.55)) * (1 if t < 0.55 else 0)
        v += 0.007 * max(0.0, t - 0.75) / 0.25
        pts.append((u, v))
    pts.append((L / 2, -H / 2 + 0.008))   # nose: the blade guide, squared off
    pts.append((L / 2, H / 2 - 0.0035))
    for i in range(1, 8):       # spine back to the butt
        t = i / 8
        u = L / 2 - 0.004 - (L - H / 2 - 0.004) * t
        v = H / 2 - 0.0012 * math.sin(math.pi * t)
        pts.append((u, v))
    return pts


def belly_v(u):
    """The belly's v at u (from the outline)."""
    L, H = BC_L, BC_H
    t = (u - (-L / 2 + H / 2)) / (L - H / 2 - 0.012)
    t = max(0.0, min(1.0, t))
    v = -H / 2 + 0.0025 * math.sin(math.pi * min(1.0, t / 0.55)) * (1 if t < 0.55 else 0)
    return v + 0.007 * max(0.0, t - 0.75) / 0.25


def build_box_cutter(kit):
    cutter_texture()
    L, H, T = BC_L, BC_H, BC_T
    tex = "tex_ship_cutter"
    # side-view geometry (u, v, w) -> world (x = v, y = w, z = u): lying on its side, spine towards +x
    Mm = S.Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    outline = cutter_outline()
    us = [p[0] for p in outline]
    vs = [p[1] for p in outline]
    body = B.g_slab(outline, depth=T, z0=0.0, bevel=0.0022, seg=2, uv_rect=(0.01, 0.97, 0.99, 0.03),
                    uv_bounds=(min(us), min(vs), max(us), max(vs)))
    kit.mb(tex).add(body, Mm, (0, 0, 0))
    # the black end cap over the round butt
    cx, r = -L / 2 + H / 2, H / 2 + 0.0005
    ucap = -L / 2 + 0.012
    vc = math.sqrt(max(0.0, r * r - (ucap - cx) ** 2))
    a0 = math.atan2(vc, ucap - cx)
    cap = [(ucap, -vc), (ucap, vc)]
    for i in range(1, 12):
        a = a0 + (2 * math.pi - 2 * a0) * i / 12
        cap.append((cx + r * math.cos(a), r * math.sin(a)))
    kit.mb("black_plastic").add(B.g_slab(cap, depth=T + 0.0008, z0=-0.0004, bevel=0.0018, seg=2), Mm, (0, 0, 0))
    # the black rubber grip overmould on both faces (rear half, belly side) with ribs
    u0, u1 = ucap + 0.003, 0.004
    lower = [(u0 + (u1 - u0) * k / 10, belly_v(u0 + (u1 - u0) * k / 10) + 0.0019) for k in range(11)]
    upper = []
    for k in range(11):
        t = 1 - k / 10
        u = u0 + (u1 - u0) * t
        v = 0.0065 - (0.0065 - belly_v(u1) - 0.0026) * t ** 1.7
        upper.append((u, v))
    grip = lower + upper
    for side in (1, -1):
        y0 = T - 0.0005 if side > 0 else -0.0009 + 0.0005
        g = B.g_slab(grip, depth=0.0009, z0=0.0, bevel=0.00035)
        kit.mb("rubber").add(g, Mm, (0, y0 if side > 0 else -0.0004, 0))
        for k in range(8):
            u = u0 + 0.008 + k * 0.0075
            vb = belly_v(u) + 0.0035
            vt = min(0.0045, 0.0065 - (0.0065 - belly_v(u1) - 0.0026) * ((u - u0) / (u1 - u0)) ** 1.7) - 0.0015
            if vt - vb < 0.003:
                continue
            rib = B.g_box((vt - vb, 0.0006, 0.0014), bevel=0.0002)
            yy = (T + 0.0004 + 0.0003) if side > 0 else (-0.0004 - 0.0003)
            kit.mb("rubber").add(rib, None, ((vb + vt) / 2, yy, u))
    # the steel blade channel lining the nose, and the slider on the spine
    kit.mb("steel").add(B.g_box((0.0018, T * 0.62, 0.050), bevel=0.0004), None, (H / 2 - 0.0042, T / 2, L / 2 - 0.025))
    kit.mb("black_plastic").add(B.g_box((0.006, T * 0.55, 0.026), bevel=0.0018, seg=2), None, (H / 2 + 0.0008, T / 2, 0.012))
    for k in range(6):
        kit.mb("black_plastic").add(B.g_box((0.0015, T * 0.5, 0.0016), bevel=0.0005), None,
                                    (H / 2 + 0.0038, T / 2, 0.002 + k * 0.004))
    # the blade: 18 mm snap-off, 0.5 mm thick, angled segments, the point at the cutting edge (belly side)
    bw, bt = 0.018, 0.0005
    z0 = L / 2 - 0.006
    zt = L / 2 + BLADE_OUT
    sk = bw * math.tan(32 * S.DEG)
    vcb = -0.0025
    bl = [(z0, -bw / 2 + vcb), (zt, -bw / 2 + vcb), (zt - sk, bw / 2 + vcb), (z0, bw / 2 + vcb)]
    kit.mb("steel").add(B.g_slab(bl, depth=bt, z0=0.0), Mm, (0, T / 2 - bt / 2, 0))
    for k in range(1, 4):       # snap lines on both faces
        uz = zt - k * 0.009
        ln = [(uz - 0.0003, -bw / 2 + vcb), (uz + 0.0003, -bw / 2 + vcb), (uz + 0.0003 - sk, bw / 2 + vcb - 0.0012),
              (uz - 0.0003 - sk, bw / 2 + vcb - 0.0012)]
        for y in (T / 2 + bt / 2 + 0.00003, T / 2 - bt / 2 - 0.00006):
            kit.mb("steel_dark").add(B.g_slab(ln, depth=0.00003, z0=0.0), Mm, (0, y, 0))
    edge = [(z0 + 0.002, -bw / 2 + vcb), (zt - 0.0006, -bw / 2 + vcb),
            (zt - 0.0006 - 0.0025 * math.tan(32 * S.DEG), -bw / 2 + vcb + 0.0025), (z0 + 0.002, -bw / 2 + vcb + 0.0025)]
    for y in (T / 2 + bt / 2 + 0.00002, T / 2 - bt / 2 - 0.00005):
        kit.mb("alu").add(B.g_slab(edge, depth=0.00003, z0=0.0), Mm, (0, y, 0))
    tip = (-bw / 2 + vcb, T / 2, zt)
    kit.anchor("A_GRIP_0", (-0.002, T / 2, -0.035), (H, T, 0.09), forward=(0, 0, 1), up=(1, 0, 0), meta="hold=1")
    kit.anchor("A_BLADE_0", tip, (bt * 4, bw, BLADE_OUT), forward=(0, 0, 1), up=(1, 0, 0), meta=f"out={BLADE_OUT:.3f}")
    kit.anchor("A_HIT_0", (0, T / 2, BLADE_OUT / 2), (H + 0.008, T + 0.002, L + BLADE_OUT))
    kit.finish(smooth=40.0)


# ====================================================================== registry

def _mk(fn, notes=None, views=((30, 30), (-120, 25)), extra=None):
    def build(mid, prev):
        kit = S.Kit(mid)
        fn(kit)
        out = S.finish_model(kit, mid, notes)
        if prev:
            S.render(kit.root, mid, list(views), samples=48)
            if extra:
                extra(kit, mid)
        return out
    return build


MODELS = [
    ("bits", "twist_tie", _mk(build_twist_tie, [
        "  note: origin on the bundle axis; the loop wraps round the x axis (bundle ~30 mm wide in z, 18 mm in y); the "
        "twisted pigtail points +y; A_TWIST_0 = the twist."], views=((70, 20), (10, 35)))),
    ("bits", "twist_tie_open", _mk(build_twist_tie_open, ["  note: lying flat, origin bottom centre."],
                                   views=((20, 50), (80, 20)))),
    ("bits", "velcro_strap", _mk(build_velcro, [
        "  note: origin on the bundle axis (x); wraps 1.4 turns round a ~24 x 18 mm bundle; A_RIP_0 = the free tab, "
        "fwd = the pull direction."], views=((70, 20), (0, 30)))),
    ("bits", "hw_bag", _mk(build_hw_bag, [
        "  note: lying flat, origin bottom centre, zip at -z; A_LABEL_0 = the white write-on strip (+Z out, +Y towards the "
        "zip) for the printed label text."], views=((15, 55), (-60, 25)))),
    ("bits", "cable_pouch", _mk(build_cable_pouch, ["  note: origin bottom centre; zip along the +z edge."],
                                views=((25, 30), (-150, 25)))),
    ("bits", "box_cutter", _mk(build_box_cutter, [
        "  note: lying on its side (origin bottom centre); length along z with the blade tip at +z, spine (slider) "
        "towards +x, cutting edge towards -x. A_GRIP_0: hold pose (fwd +z, up = spine). A_BLADE_0: the tip."],
        views=((60, 50), (-110, 30)))),
]
