"""
shipping_filler: packing filler and crumpled trash looks for build_shipping.py.

  filler_paper_0..2   crumpled kraft paper (a round wad, a twisted paper cushion, a loose flattened pad)
  air_pillow_strip    4 inflated air pillows in a row, perforated between them; each pillow is a piece on
                      A_PILLOW_<n> (anchor = the centre of its seal plane, +Y up; the strip's bottom is y = 0)
  air_pillow_flat     one popped pillow; ITS ORIGIN IS THE CENTRE OF THE SEAL PLANE, the same frame as an
                      A_PILLOW_<n> anchor, so the code can swap it in at the anchor's pose
  bubble_wrap_sheet   0.40 x 0.30 sheet of 25 mm bubbles on a staggered grid (meta on A_HIT_0)
  bubble_wrap_wrapped a sleeve wrapped loosely round a nominal 0.22 x 0.08 x 0.14 box (scale by box / nominal)
  crumple_tape, crumple_film, crumple_paper, crumple_bag   small crumpled balls (the code tints them)
"""
import math
import random

import shipping_lib as S
from shipping_lib import V, B, P, c


# ====================================================================== crumpled solids

def crumple_geo(radii, seed, subdiv=5, creases=150, amp=0.045, width=(0.05, 0.22), folds=6, fold_amp=0.16,
                fold_w=(0.18, 0.4), lumps=0.12, lump_freq=1.6, twist=0.0, pinch=None, flat_bottom=0.0):
    """A crumpled wad: an ellipsoid (radii x, y, z) with smooth lumps, a few deep folds and many tent-shaped creases
    (sharp ridges and valleys along random planes; sizes relative to the largest radius), soft-clamped so crossings
    don't spike. Smooth-shaded with sharp creases and decimated, it reads as folded paper or film.
    subdiv is Blender's (5 = 5120 triangles before decimation)."""
    rng = random.Random(seed)
    verts, faces = S.icosphere(subdiv)
    R = max(radii)
    planes = []
    for _ in range(creases):
        n = V((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        d = rng.uniform(-0.9, 0.9) * R
        w = rng.uniform(*width) * R
        a = amp * R * rng.uniform(0.3, 1.0) * (1 if rng.random() < 0.5 else -1)
        planes.append((n, d, w, a))
    big = []
    for _ in range(folds):
        n = V((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        d = rng.uniform(-0.5, 0.5) * R
        w = rng.uniform(*fold_w) * R
        a = -fold_amp * R * rng.uniform(0.6, 1.0)
        big.append((n, d, w, a))
    A = 2.2 * amp * R
    out = []
    for v in verts:
        u = V(v)
        p = V((u.x * radii[0], u.y * radii[1], u.z * radii[2]))
        k = 1.0 + lumps * S.fbm(u * lump_freq, 3, seed=seed % 97)
        if pinch is not None:      # a paper cushion: squeezed at the ends along x
            k *= 1.0 - pinch * math.exp(-((abs(u.x) - 0.85) / 0.25) ** 2)
        p = V((p.x, p.y * k, p.z * k)) if pinch is not None else p * k
        if twist:
            a = twist * u.x
            ca, sa = math.cos(a), math.sin(a)
            p = V((p.x, p.y * ca - p.z * sa, p.y * sa + p.z * ca))
        nrm = V((u.x / radii[0], u.y / radii[1], u.z / radii[2])).normalized()
        dsp = 0.0
        for (n, d, w, a) in planes:
            x = abs(n.dot(p) - d)
            if x < w:
                dsp += a * (1.0 - x / w)
        dsp = A * math.tanh(dsp / A)
        for (n, d, w, a) in big:
            x = abs(n.dot(p) - d)
            if x < w:
                dsp += a * (1.0 - x / w) ** 1.5
        p = p + nrm * dsp
        if flat_bottom > 0 and p.y < -radii[1] * (1 - flat_bottom):
            p.y = -radii[1] * (1 - flat_bottom) + (p.y + radii[1] * (1 - flat_bottom)) * 0.25
        out.append(p)
    return out, faces


def to_bottom(verts, lift=0.0):
    y0 = min(p.y for p in verts)
    return [V((p.x, p.y - y0 + lift, p.z)) for p in verts]


def fin_geo(origin, normal, along, size, seed, amp=0.004, nu=5, nv=4, tilt=0.5):
    """A thin crumpled flap of the sheet sticking out of a wad (two-sided)."""
    rng = random.Random(seed)
    n = V(normal).normalized()
    a = V(along)
    a = (a - n * a.dot(n)).normalized()
    b = n.cross(a).normalized()
    w, h = size
    o = V(origin)

    def fn(u, v):
        # rooted inside the wad (v = 0), leaning out along n as v grows
        s = (u - 0.5) * w * (1 - 0.35 * v)
        t = v * h
        lift = t * tilt + amp * math.sin(u * 7.0 + seed) * v + rng.uniform(-amp, amp) * 0.3 * v
        return o + a * s + b * (t * (1 - tilt * 0.5)) + n * (lift - h * 0.25)
    g1 = S.grid_surface(fn, nu, nv, smooth=False)
    g2 = S.grid_surface(fn, nu, nv, smooth=False, flip=True)
    return B.merge(g1, g2)


def add_wad(kit, tag, verts, faces, name=None):
    geo = (verts, faces, None, [False] * len(faces))
    if name:
        kit.named_mb(name, tag).add(geo)
    else:
        kit.mb(tag).add(geo)


def double_inverted(obj, ctr, radii, margin=2.0):
    """Paper and film are thin sheets seen from both sides: faces of the wad that face inwards by more than
    'margin' (the default, 2, means every face) get a reversed twin, so folds that turn the sheet over never show a
    hole with back-face culling."""
    import bmesh
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    dup = []
    for f in bm.faces:
        cb = f.calc_center_median()
        cu = V((-cb.x, cb.z, -cb.y))            # Blender -> Unity
        nb = f.normal
        nu = V((-nb.x, nb.z, -nb.y))
        d = cu - V(ctr)
        out = V((d.x / radii[0] ** 2, d.y / radii[1] ** 2, d.z / radii[2] ** 2))
        if out.length < 1e-9 or nu.dot(out.normalized()) < margin:
            dup.append(f)
    if dup:
        res = bmesh.ops.duplicate(bm, geom=dup)
        newf = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.reverse_faces(bm, faces=newf)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return len(dup)


def finish_crumple(kit, target_tris, tag, sharp=32.0, ctr=(0, 0, 0), radii=(1, 1, 1)):
    """Decimates the wad, doubles its folded-over faces, then joins the (already two-sided) fins into it."""
    import bpy
    objs = kit.finish(smooth=None)
    wad = None
    fins = None
    for o in objs:
        if o.name == f"{kit.id}_{tag}#{tag}":
            wad = o
        elif o.name.startswith("fins#"):
            fins = o
    tris = sum(len(p.vertices) - 2 for p in wad.data.polygons)
    if tris > target_tris:
        S.decimate_obj(wad, target_tris / tris)
    n = double_inverted(wad, ctr, radii)
    print(f"  {kit.id}: two-sided ({n} faces twinned)")
    if fins is not None:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        wad.select_set(True)
        fins.select_set(True)
        bpy.context.view_layer.objects.active = wad
        bpy.ops.object.join()
    wad.data.shade_smooth()
    wad.data.set_sharp_from_angle(angle=sharp * S.DEG)
    return [o for o in objs if o is not fins]


# ---------------------------------------------------------------------- filler paper

def build_filler_paper(kit, idx):
    tag = "kraft_paper"
    rng = random.Random(500 + idx)
    if idx == 0:      # a round wad
        radii = (0.074, 0.060, 0.068)
        v, f = crumple_geo(radii, 101, creases=170, amp=0.05, width=(0.05, 0.2), folds=7, fold_amp=0.2,
                           lumps=0.1, flat_bottom=0.25)
        n_fins = 0
    elif idx == 1:    # a twisted paper cushion
        radii = (0.105, 0.040, 0.046)
        v, f = crumple_geo(radii, 202, creases=150, amp=0.045, width=(0.04, 0.16), folds=5, fold_amp=0.12,
                           lumps=0.08, twist=1.6, pinch=0.45, flat_bottom=0.2)
        n_fins = 0
    else:             # a loose flattened pad
        radii = (0.092, 0.034, 0.072)
        v, f = crumple_geo(radii, 303, creases=150, amp=0.06, width=(0.06, 0.25), folds=6, fold_amp=0.17,
                           fold_w=(0.25, 0.5), lumps=0.15, lump_freq=1.2, flat_bottom=0.35)
        n_fins = 0
    y0 = min(p.y for p in v)
    v = [V((p.x, p.y - y0, p.z)) for p in v]
    add_wad(kit, tag, v, f)
    # sheet edges and loose flaps sticking out (what makes a wad read as paper rather than a lump)
    ctr = sum(v, V()) / len(v)

    def reach(q):
        d = q - ctr
        return (d.x / radii[0]) ** 2 + (d.y / radii[1]) ** 2 + (d.z / radii[2]) ** 2
    ranked = sorted(range(len(v)), key=lambda k: -reach(v[k]))
    cands = [k for k in ranked[:len(v) * 3 // 10] if v[k].y > 0.35 * max(p.y for p in v)]
    for i in range(n_fins):
        k = cands[rng.randrange(len(cands))]
        p = v[k]
        d = (p - ctr)
        d.y *= 0.6
        n = d.normalized()
        along = n.cross(V((rng.uniform(-1, 1), 1, rng.uniform(-1, 1)))).normalized()
        sz = (radii[0] * rng.uniform(0.45, 0.8), radii[0] * rng.uniform(0.28, 0.5))
        g = fin_geo(p - n * sz[1] * 0.35, n, along, sz, 7 * idx + i, amp=0.0045, tilt=rng.uniform(0.25, 0.7))
        kit.named_mb("fins", tag).add(g)
    xs = [p.x for p in v]
    ys = [p.y for p in v]
    zs = [p.z for p in v]
    size = (max(xs) - min(xs), max(ys), max(zs) - min(zs))
    kit.anchor("A_HIT_0", ((max(xs) + min(xs)) / 2, size[1] / 2, (max(zs) + min(zs)) / 2), size)
    finish_crumple(kit, 1450, tag, sharp=30.0, ctr=(0, -y0, 0), radii=radii)
    return size


# ---------------------------------------------------------------------- crumpled trash looks

def build_crumple(kit, kind):
    if kind == "tape":
        tag = "tape_brown"
        v, f = crumple_geo((0.022, 0.017, 0.019), 11, subdiv=4, creases=60, amp=0.09, width=(0.1, 0.35), folds=4,
                           fold_amp=0.2, lumps=0.15, flat_bottom=0.2)
        y0 = min(p.y for p in v)
        v = [V((p.x, p.y - y0, p.z)) for p in v]
        add_wad(kit, tag, v, f)
        # a tail of tape that didn't stick to the ball (a twisted ribbon)
        path = [V((0.012, 0.02, 0.006)), V((0.022, 0.024, 0.01)), V((0.032, 0.022, 0.016)), V((0.040, 0.015, 0.02))]
        path = S.smooth_path(path, 4)
        prof = [(-0.009, -0.0002), (0.009, -0.0002), (0.009, 0.0002), (-0.009, 0.0002)]
        tail = S.sweep_profile(path, prof, up=(0, 1, 0.3), twist=lambda t: 1.2 * t, smooth=False)
        kit.named_mb("fins", tag).add(tail)
        kit.named_mb("fins", tag).add((tail[0], [f[::-1] for f in tail[1]], None, tail[3]))
        target, radii = 330, (0.022, 0.017, 0.019)
    elif kind == "film":
        tag = "film_clear"
        v, f = crumple_geo((0.040, 0.026, 0.034), 22, creases=140, amp=0.06, width=(0.06, 0.25), folds=6,
                           fold_amp=0.22, lumps=0.2, flat_bottom=0.3)
        y0 = min(p.y for p in v)
        v = [V((p.x, p.y - y0, p.z)) for p in v]
        add_wad(kit, tag, v, f)
        for i, (o, n, a, sz) in enumerate([((0.03, 0.03, 0.01), (0.7, 0.6, 0.2), (0, 0, 1), (0.04, 0.025)),
                                           ((-0.03, 0.025, -0.02), (-0.6, 0.6, -0.5), (1, 0, 0), (0.035, 0.022)),
                                           ((0.0, 0.045, 0.02), (0.1, 1, 0.3), (1, 0, 0.2), (0.03, 0.02))]):
            kit.named_mb("fins", tag).add(fin_geo(V(o), n, a, sz, 40 + i, amp=0.003))
        target, radii = 620, (0.040, 0.026, 0.034)
    elif kind == "paper":
        tag = "paper_white"
        v, f = crumple_geo((0.031, 0.027, 0.029), 33, creases=160, amp=0.055, width=(0.05, 0.22), folds=6,
                           fold_amp=0.18, lumps=0.1, flat_bottom=0.2)
        y0 = min(p.y for p in v)
        v = [V((p.x, p.y - y0, p.z)) for p in v]
        add_wad(kit, tag, v, f)
        target, radii = 650, (0.031, 0.027, 0.029)
    else:  # bag
        tag = "bag_clear"
        v, f = crumple_geo((0.040, 0.018, 0.028), 44, creases=120, amp=0.06, width=(0.06, 0.25), folds=5,
                           fold_amp=0.22, lumps=0.22, lump_freq=1.3, flat_bottom=0.4)
        y0 = min(p.y for p in v)
        v = [V((p.x, p.y - y0, p.z)) for p in v]
        add_wad(kit, tag, v, f)
        # the bag's sealed bottom edge sticking out as a flat crumpled strip
        kit.named_mb("fins", tag).add(fin_geo((0.03, 0.012, 0.0), (1, 0.25, 0.1), (0, 0.2, 1), (0.045, 0.02), 51,
                                              amp=0.002, tilt=0.2))
        kit.named_mb("fins", tag).add(fin_geo((-0.025, 0.02, 0.015), (-0.5, 0.7, 0.4), (1, 0, 0), (0.03, 0.02), 52,
                                              amp=0.002))
        target, radii = 620, (0.040, 0.018, 0.028)
    allv = []
    for mb in list(kit.static.values()) + list(kit.named.values()):
        allv += mb.v
    xs, ys, zs = [p.x for p in allv], [p.y for p in allv], [p.z for p in allv]
    size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    kit.anchor("A_HIT_0", ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2), size)
    finish_crumple(kit, target, tag, sharp=30.0, ctr=(0, -y0, 0), radii=radii)
    return size


# ====================================================================== air pillows

PIL_X = 0.100      # pitch along the strip
PIL_Z = 0.200      # across the strip (with the inflation channel)
PIL_H = 0.021      # half thickness inflated
SEAL = 0.0045      # seal half-width at the perforation and the outer edge
CHAN = 0.016       # the flat inflation channel along +z


def pillow_height(u, v, wr=0.0):
    """Normalised -1..1 coordinates over the chamber -> height 0..1 (a cushion: steep at the seal)."""
    fu = max(0.0, 1.0 - abs(u) ** 2.4) ** 0.55
    fv = max(0.0, 1.0 - abs(v) ** 2.8) ** 0.5
    return fu * fv


def pillow_geo(seed, inflated=True, nu=10, nv=12):
    """One pillow in its own frame: the seal plane at y = 0, x across the pitch, z across the strip.
    Returns a list of geometries (top, bottom, flange)."""
    rng = random.Random(seed)
    a = PIL_X / 2 - SEAL                      # chamber half size along x
    z0, z1 = -PIL_Z / 2 + SEAL, PIL_Z / 2 - CHAN - 0.004
    zc, b = (z0 + z1) / 2, (z1 - z0) / 2
    ph = [rng.uniform(0, 6.28) for _ in range(6)]

    def surf(sign):
        def fn(i, j):
            u, v = i * 2 - 1, j * 2 - 1
            x, z = u * a, zc + v * b
            if inflated:
                h = PIL_H * pillow_height(u, v)
                # puckers where the film is pulled into the seal
                edge = max(abs(u) ** 4, abs(v) ** 6) * min(1.0, 5.0 * (1.0 - max(abs(u), abs(v))))
                h += 0.0022 * edge * (math.sin(v * 9.0 + ph[0]) + 0.6 * math.sin(u * 7.0 + ph[1]))
                h *= 1.0 + 0.04 * math.sin(u * 3.1 + ph[2]) * math.sin(v * 2.3 + ph[3])
            else:
                env = (1 - abs(u) ** 6) * (1 - abs(v) ** 6)
                h = env * (0.0012 + 0.0016 * math.sin(u * 11 + v * 5 + ph[0]) * math.sin(v * 13 - u * 4 + ph[1])
                           + 0.0012 * math.sin(u * 23 + ph[2]) * math.cos(v * 19 + ph[3]))
                h = abs(h) + 0.0002
                # the deflated film sags and curls a little
                h += 0.0
            y = sign * h
            if not inflated:
                y += 0.0025 * math.sin(u * 1.7 + ph[4]) * math.sin(v * 1.3 + ph[5]) * (1 - abs(u) ** 4) * (1 - abs(v) ** 4)
            return (x, y, z)
        return fn
    top = S.facing(S.grid_surface(surf(1), nu, nv, smooth=True), (0, 1, 0))
    bot = S.facing(S.grid_surface(surf(-1), nu, nv, smooth=True), (0, -1, 0))
    # the flange: the flat sealed film round the chamber, out to the pillow's cell (and the channel along +z)
    t = 0.00012
    ring_in = []
    # chamber outline (same samples as the grid border)
    for i in range(nu):
        ring_in.append((-a + 2 * a * i / nu, z0))
    for j in range(nv):
        ring_in.append((a, z0 + 2 * b * j / nv))
    for i in range(nu):
        ring_in.append((a - 2 * a * i / nu, z1))
    for j in range(nv):
        ring_in.append((-a, z1 - 2 * b * j / nv))
    X0, X1, Z0, Z1 = -PIL_X / 2, PIL_X / 2, -PIL_Z / 2, PIL_Z / 2

    def outer_of(px, pz):
        # project the chamber border point onto the cell border (straight out)
        if abs(pz - z0) < 1e-9:
            return (px * PIL_X / 2 / a, Z0)
        if abs(pz - z1) < 1e-9:
            return (px * PIL_X / 2 / a, Z1)
        return ((X1 if px > 0 else X0), pz)
    fl_top, fl_bot = [], []
    n = len(ring_in)
    verts, faces = [], []
    for k in range(n):
        p0, p1 = ring_in[k], ring_in[(k + 1) % n]
        q0, q1 = outer_of(*p0), outer_of(*p1)
        for sgn in (1, -1):
            yy = sgn * t
            quad = [V((p0[0], yy, p0[1])), V((p1[0], yy, p1[1])), V((q1[0], yy, q1[1])), V((q0[0], yy, q0[1]))]
            g = S.geo_quad(quad, None, (0, sgn, 0))
            base = len(verts)
            verts += g[0]
            faces += [[base + i for i in g[1][0]]]
    flange = (verts, faces, None, [False] * len(faces))
    parts = [top, bot, flange]
    # the inflation channel: a slightly open flat tube along x at the +z edge
    zc_ch = PIL_Z / 2 - CHAN / 2 - 0.001
    rch = 0.0024 if inflated else 0.0008

    def chan(sign):
        def fn(i, j):
            x = -PIL_X / 2 + PIL_X * i
            zz = zc_ch + (j * 2 - 1) * CHAN * 0.32
            h = rch * max(0.0, 1 - ((j * 2 - 1)) ** 2) ** 0.5
            return (x, sign * (h + t * 1.5), zz)
        return fn
    parts.append(S.facing(S.grid_surface(chan(1), 4, 4, smooth=True), (0, 1, 0)))
    parts.append(S.facing(S.grid_surface(chan(-1), 4, 4, smooth=True), (0, -1, 0)))
    return parts


def build_pillow_strip(kit):
    tag = "bag_clear"
    for i in range(4):
        x = (i - 1.5) * PIL_X
        a = kit.anchor(f"A_PILLOW_{i}", (x, PIL_H, 0), (PIL_X, 2 * PIL_H, PIL_Z), meta=f"index={i},pop=air_pillow_flat")
        mb = kit.piece(a, tag, "pillow")
        for g in pillow_geo(100 + i):
            mb.add(g, None, (x, PIL_H, 0))
    kit.anchor("A_HIT_0", (0, PIL_H, 0), (4 * PIL_X, 2 * PIL_H, PIL_Z))
    kit.finish(smooth=50.0)


def build_pillow_flat(kit):
    tag = "bag_clear"
    for g in pillow_geo(7, inflated=False, nu=12, nv=16):
        kit.mb(tag).add(g)
    kit.anchor("A_HIT_0", (0, 0, 0), (PIL_X, 0.006, PIL_Z))
    kit.finish(smooth=50.0)


# ====================================================================== bubble wrap

BW_COLS, BW_ROWS, BW_PITCH = 14, 12, 0.027
BW_R, BW_H = 0.0105, 0.0062
BW_FILM = 0.0003


def bubble_geo(r, h, segs=8):
    prof = [(0.0, 0.0), (r, 0.0), (r * 0.84, h * 0.74), (0.0, h)]
    v, f, uv = B.g_lathe(prof, segs)
    # drop the bottom cap (it sits on the film)
    keep = [fc for fc in f if not all(abs(v[k].z) < 1e-12 for k in fc)]
    return v, keep, None, [True] * len(keep)


def bubble_grid():
    step = BW_PITCH * math.sqrt(3) / 2
    x0 = -((BW_COLS - 1) * BW_PITCH + BW_PITCH / 2) / 2
    z0 = -((BW_ROWS - 1) * step) / 2
    pts = []
    for j in range(BW_ROWS):
        for i in range(BW_COLS):
            pts.append((x0 + i * BW_PITCH + (BW_PITCH / 2 if j % 2 else 0.0), z0 + j * step))
    return pts, x0, z0, step


def build_bubble_sheet(kit):
    tag = "bubble_wrap"
    W, D = 0.40, 0.30
    rng = random.Random(5)
    ph = [rng.uniform(0, 6.28) for _ in range(4)]

    def wave(x, z):
        return 0.0025 * (1 + math.sin(x * 9 + ph[0]) * math.sin(z * 7 + ph[1])) + 0.0015 * math.sin(x * 21 + z * 5 + ph[2])
    top = S.grid_surface(lambda i, j: (-W / 2 + W * i, wave(-W / 2 + W * i, -D / 2 + D * j) + BW_FILM, -D / 2 + D * j),
                         12, 9, smooth=True)
    top = S.facing(top, (0, 1, 0))
    bot = S.facing(S.grid_surface(lambda i, j: (-W / 2 + W * i, wave(-W / 2 + W * i, -D / 2 + D * j), -D / 2 + D * j),
                                  12, 9, smooth=True), (0, -1, 0))
    mb = kit.mb(tag)
    mb.add(top)
    mb.add(bot)
    # the film's cut edges (thin)
    pts, x0, z0, step = bubble_grid()
    bub = bubble_geo(BW_R, BW_H)
    M = B.frame((0, 1, 0), (0, 0, 1))   # lathe axis (local z) -> Unity +y
    for (x, z) in pts:
        mb.add(bub, M, (x, wave(x, z) + BW_FILM - 0.0002, z))
    meta = (f"grid={BW_COLS}x{BW_ROWS}x{BW_PITCH:.4f},cols={BW_COLS},rows={BW_ROWS},pitch={BW_PITCH:.4f},"
            f"row={step:.5f},stagger=0.5,x0={x0:.5f},z0={z0:.5f},r={BW_R:.4f},h={BW_H:.4f},y={BW_FILM:.4f}")
    kit.anchor("A_HIT_0", (0, 0.005, 0), (W, 0.012, D), meta=meta)
    kit.finish(smooth=60.0)
    return len(pts)


NOMINAL = (0.22, 0.08, 0.14)


def build_bubble_wrapped(kit):
    """A sheet wrapped once round a box (about the x axis) with a 4 cm overlap on top, held by a piece of clear
    tape; the ends stay open and flare a little. Bubbles face out."""
    tag = "bubble_wrap"
    bx, by, bz = NOMINAL
    rng = random.Random(9)
    ph = [rng.uniform(0, 6.28) for _ in range(6)]
    over = 0.045
    ext = 0.035          # past each end of the box
    rc = 0.016

    # the wrap's cross-section path (y-z), around the box with a varying clearance; s = arc length
    def section(cl):
        hz, hy = bz / 2 + cl, by / 2 + cl
        cy = by / 2
        pts = []
        # start on the top near +z, go round: top -> -z side -> bottom -> +z side -> top again past the start
        segs = [((hz - rc, cy + hy), (-hz + rc, cy + hy)), "c1", ((-hz, cy + hy - rc), (-hz, cy - hy + rc)), "c2",
                ((-hz + rc, cy - hy), (hz - rc, cy - hy)), "c3", ((hz, cy - hy + rc), (hz, cy + hy - rc)), "c4"]
        corners = {"c1": ((-hz + rc, cy + hy - rc), 90, 180), "c2": ((-hz + rc, cy - hy + rc), 180, 270),
                   "c3": ((hz - rc, cy - hy + rc), 270, 360), "c4": ((hz - rc, cy + hy - rc), 0, 90)}
        for sgm in segs:
            if isinstance(sgm, str):
                (ccz, ccy), a0, a1 = corners[sgm]
                for kk in range(1, 6):
                    a = (a0 + (a1 - a0) * kk / 6) * S.DEG
                    pts.append(V((0, ccy + rc * math.sin(a), ccz + rc * math.cos(a))))
            else:
                (z0_, y0_), (z1_, y1_) = sgm
                for kk in range(7):
                    t = kk / 7
                    pts.append(V((0, y0_ + (y1_ - y0_) * t, z0_ + (z1_ - z0_) * t)))
        # overlap: continue along the top past the start
        nz = int(over / 0.012) + 1
        for kk in range(nz + 1):
            pts.append(V((0, cy + hy + BW_H + 0.002, hz - rc - over * kk / nz)))
        return pts

    base = section(0.004)
    # arc length
    sl = [0.0]
    for i in range(1, len(base)):
        sl.append(sl[-1] + (base[i] - base[i - 1]).length)
    Ls = sl[-1]
    Lx = bx + 2 * ext
    nx = 8
    ctr = V((0, by / 2, 0))

    def point(si, tx):
        """si: index along the section, tx: 0..1 along x."""
        p = base[si]
        x = -Lx / 2 + Lx * tx
        endk = max(0.0, abs(tx * 2 - 1) - bx / Lx) / (ext / Lx)        # 0 over the box, 1 at the very end
        d = p - ctr
        d.x = 0
        dn = d.normalized()
        loose = 0.004 + 0.004 * (1 + math.sin(sl[si] * 17 + ph[0]) * math.sin(tx * 7 + ph[1]))
        flare = 0.012 * endk ** 1.5
        sag = -0.004 * endk * max(0.0, dn.y)
        q = ctr + d + dn * (loose + flare) + V((0, sag, 0))
        q.x = x
        return q
    ns = len(base) - 1
    outer = S.grid_surface(lambda i, j: point(int(round(i * ns)), j), ns, nx, smooth=True)
    # make sure it faces out (test against the centre line)
    v0 = outer[0][outer[1][len(outer[1]) // 2][0]]
    nrm = B._newell([outer[0][k] for k in outer[1][len(outer[1]) // 2]])
    flip = nrm.dot(v0 - V((v0.x, ctr.y, ctr.z))) < 0
    if flip:
        outer = (outer[0], [f[::-1] for f in outer[1]], None, outer[3])
    inner = (outer[0], [f[::-1] for f in outer[1]], None, outer[3])
    # offset the inner skin a hair inwards
    vin = []
    for p in outer[0]:
        d = p - V((p.x, ctr.y, ctr.z))
        vin.append(p - d.normalized() * BW_FILM)
    inner = (vin, inner[1], None, inner[3])
    mb = kit.mb(tag)
    mb.add(outer)
    mb.add(inner)
    # bubbles on a staggered grid over (arc length, x), facing out
    bub = bubble_geo(BW_R * 0.95, BW_H * 0.95, segs=7)
    pitch = BW_PITCH * 1.12
    step = pitch * math.sqrt(3) / 2
    count = 0
    row = 0
    s = 0.012
    while s < Ls - 0.012:
        si_f = 0
        while si_f < len(sl) - 1 and sl[si_f + 1] < s:
            si_f += 1
        x = -Lx / 2 + 0.012 + (pitch / 2 if row % 2 else 0)
        while x < Lx / 2 - 0.010:
            tx = (x + Lx / 2) / Lx
            # interpolate the surface point and its frame
            f = (s - sl[si_f]) / max(1e-9, sl[si_f + 1] - sl[si_f])
            pa, pb = point(si_f, tx), point(si_f + 1, tx)
            p = pa + (pb - pa) * f
            tan_s = (pb - pa).normalized()
            px1 = point(si_f, min(1.0, tx + 0.02))
            px0 = point(si_f, max(0.0, tx - 0.02))
            tan_x = (px1 - px0).normalized()
            nrm = tan_x.cross(tan_s).normalized()
            if nrm.dot(p - V((p.x, ctr.y, ctr.z))) < 0:
                nrm = -nrm
            M = B.frame(nrm, tan_s)
            # lathe axis is local z -> along the normal
            mb.add(bub, M, p - nrm * 0.0002)
            count += 1
            x += pitch
        s += step
        row += 1
    # a strip of clear tape over the overlap's free edge, in the middle, lying on the bubbles
    n_top = 7                                # the first path segment (the base layer's top)
    over_idx = list(range(len(base) - (int(over / 0.012) + 2), len(base)))
    edge_z = point(len(base) - 1, 0.5).z

    def top_y(zz, idxs):
        best = min(idxs, key=lambda k: abs(point(k, 0.5).z - zz))
        return point(best, 0.5).y + BW_H + 0.0006
    tw = 0.048
    zs = [edge_z - 0.03 + 0.06 * kk / 10 for kk in range(11)]
    ys = []
    for zz in zs:
        if zz > edge_z + 0.002:
            ys.append(top_y(zz, over_idx))
        else:
            ys.append(top_y(zz, range(0, n_top)))
    tape = S.grid_surface(lambda i, j: (-tw / 2 + tw * i, ys[int(round(j * 10))], zs[int(round(j * 10))]), 1, 10,
                          smooth=True)
    nrm = B._newell([tape[0][k] for k in tape[1][0]])
    if nrm.y < 0:
        tape = (tape[0], [f[::-1] for f in tape[1]], None, tape[3])
    kit.mb("tape_clear").add(tape)
    kit.anchor("A_HIT_0", (0, by / 2, 0), (Lx, by + 0.03, bz + 0.03),
               meta=f"nominal={bx:.3f}x{by:.3f}x{bz:.3f}")
    kit.finish(smooth=60.0)
    return count


# ====================================================================== registry for build_shipping.py

def _mk(fn, notes=None, views=((30, 28), (-120, 22)), extra=None):
    def build(mid, prev):
        kit = S.Kit(mid)
        info = fn(kit)
        nts = list(notes or [])
        if isinstance(info, tuple) and len(info) == 3:
            nts.append(f"  note: size {info[0]:.3f} x {info[1]:.3f} x {info[2]:.3f} m (x, y, z), origin bottom centre.")
        out = S.finish_model(kit, mid, nts)
        if prev:
            S.render(kit.root, mid, list(views), samples=48)
            if extra:
                extra(kit, mid)
        return out
    return build


def _pillow_preview(kit, mid):
    S.render(kit.root, mid, [(10, 70)], samples=48, start=2)


MODELS = [
    ("filler", "filler_paper_0", _mk(lambda k: build_filler_paper(k, 0))),
    ("filler", "filler_paper_1", _mk(lambda k: build_filler_paper(k, 1))),
    ("filler", "filler_paper_2", _mk(lambda k: build_filler_paper(k, 2))),
    ("filler", "air_pillow_strip", _mk(build_pillow_strip, [
        "  note: each pillow is a piece on A_PILLOW_<n> (anchor = centre of its seal plane); swap in air_pillow_flat "
        "at the anchor's pose when popped."], views=((30, 30), (-60, 12)), extra=_pillow_preview)),
    ("filler", "air_pillow_flat", _mk(build_pillow_flat, [
        "  note: origin = centre of the seal plane (the same frame as an A_PILLOW_<n> anchor), not the bottom."],
        views=((30, 35), (-80, 15)))),
    ("filler", "bubble_wrap_sheet", _mk(build_bubble_sheet, [
        "  note: bubble k = row * cols + col; centre x = x0 + col * pitch (+ pitch / 2 on odd rows), z = z0 + row * "
        "row, base at y ~ y; r = radius, h = dome height. Meta values are separate keys (grid=CxRxP repeats them)."],
        views=((25, 40), (-60, 18)))),
    ("filler", "bubble_wrap_wrapped", _mk(build_bubble_wrapped, [
        "  note: wrapped round a nominal box 0.22 x 0.08 x 0.14 (x, y, z) standing on y = 0 at the origin; scale by "
        "(box size / nominal). The sleeve runs round the x axis, open at both x ends; overlap and tape on top."],
        views=((35, 28), (-140, 20)))),
    ("crumples", "crumple_tape", _mk(lambda k: build_crumple(k, "tape"), views=((30, 25), (-120, 30)))),
    ("crumples", "crumple_film", _mk(lambda k: build_crumple(k, "film"), views=((30, 25), (-120, 30)))),
    ("crumples", "crumple_paper", _mk(lambda k: build_crumple(k, "paper"), views=((30, 25), (-120, 30)))),
    ("crumples", "crumple_bag", _mk(lambda k: build_crumple(k, "bag"), views=((30, 25), (-120, 30)))),
]
