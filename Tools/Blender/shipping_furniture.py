"""
shipping_furniture: the unboxing table, the wheelie bin, bin bags and the paperwork tray for build_shipping.py.

  unbox_table     a 1.5 x 0.7 m fold-in-half table, top at 0.76 m: blow-moulded white HDPE top with a rounded rim and
                  a recessed underside, grey steel rails, folding leg frames with braces and lock rings, black caps.
                  A_TOP_0 = the top surface centre (+Z up out of the top, +Y towards the back), A_HIT_0..2.
  wheelie_bin     a 240 L two-wheel bin (EN 840 size), dark green, front at +z, handle and wheels at the back (-z).
                  A_LID_0 the hinged lid (moving piece, hinge=x,open=-110), A_MOUTH_0 the trigger volume just below
                  the rim, A_LINER_0 the liner rim pose, A_HANDLE_0, A_WHEEL_0/1 (moving pieces, spin=x), A_HIT_0..1.
  bin_bag_full    a tied black bin bag full of lumpy rubbish, 0.5 x 0.7 x 0.4; A_KNOT_0 at the knot (+Z up).
  bin_bag_roll    a roll of black bin bags with a paper band and a loose end; lying along x.
  paperwork_tray  a black perforated-steel A4 letter tray (front scoop at +z); A_STACK_0 = where papers stack.
"""
import math
import random

import shipping_lib as S
from shipping_lib import V, B, P, c


# ====================================================================== shared shape helpers

def rr_ring(w, d, r, y, cx=0.0, cz=0.0, seg=6, radii=None):
    """A rounded rectangle in the x-z plane at height y, counter-clockwise seen from above (+x first).
    radii = (r_px_pz, r_mx_pz, r_mx_mz, r_px_mz) overrides r per corner."""
    rs = radii or (r, r, r, r)
    out = []
    corners = [((cx + w / 2, cz + d / 2), 0), ((cx - w / 2, cz + d / 2), 1), ((cx - w / 2, cz - d / 2), 2),
               ((cx + w / 2, cz - d / 2), 3)]
    # walking order seen from above with +x right and -z up (Unity, looking down -y): (+x,+z) -> (-x,+z) ...
    for (px, pz), k in corners:
        rr = max(1e-5, min(rs[k], w / 2 - 1e-5, d / 2 - 1e-5))
        sx = 1 if px > cx else -1
        sz = 1 if pz > cz else -1
        ccx, ccz = px - sx * rr, pz - sz * rr
        a0 = {0: 0.0, 1: 90.0, 2: 180.0, 3: 270.0}[k]
        for i in range(seg + 1):
            a = (a0 + 90.0 * i / seg) * S.DEG
            out.append(V((ccx + rr * math.cos(a), y, ccz + rr * math.sin(a))))
    return out


def loft(rings, closed=True, smooth=True, uv_fn=None):
    """Quads between successive rings (same vertex count)."""
    verts, faces, uvs = [], [], []
    n = len(rings[0])
    for r in rings:
        verts += [V(p) for p in r]
    for j in range(len(rings) - 1):
        for i in range(n if closed else n - 1):
            i1 = (i + 1) % n
            f = [j * n + i, j * n + i1, (j + 1) * n + i1, (j + 1) * n + i]
            faces.append(f)
            if uv_fn is not None:
                uvs.append([uv_fn(verts[k]) for k in f])
    return verts, faces, (uvs if uv_fn is not None else None), [smooth] * len(faces)


def cap(ring, uv_fn=None, smooth=False):
    """A fan-triangulated cap over a (convex-ish) ring."""
    ctr = sum((V(p) for p in ring), V()) / len(ring)
    verts = [ctr] + [V(p) for p in ring]
    n = len(ring)
    faces = [[0, 1 + i, 1 + (i + 1) % n] for i in range(n)]
    uvs = [[uv_fn(verts[k]) for k in f] for f in faces] if uv_fn else None
    return verts, faces, uvs, [smooth] * n


def outward_xz(centre=(0, 0, 0)):
    cx, cz = centre[0], centre[2]

    def f(p):
        return V((p.x - cx, 0, p.z - cz))
    return f


def tube_between(a, b, r, segs=12):
    """A capped cylinder from a to b."""
    a, b = V(a), V(b)
    d = b - a
    up = V((0, 1, 0)) if abs(d.normalized().y) < 0.9 else V((1, 0, 0))
    M = B.frame(d.normalized(), up)
    return B.xf(B.g_cyl(r, d.length, segs), M, (a + b) / 2)


# ====================================================================== unbox table

TB_W, TB_D, TB_H = 1.50, 0.70, 0.76


def build_table(kit):
    top_tag = "white_plastic"
    steel = "steel_dark"
    W, D, H = TB_W, TB_D, TB_H
    gap = 0.003
    # the top profile: (inset from the outline, height), from the underside panel round the rim to the top surface
    prof = [(0.050, H - 0.024), (0.040, H - 0.047), (0.034, H - 0.050), (0.008, H - 0.050), (0.0022, H - 0.0478),
            (0.0, H - 0.042), (0.0, H - 0.012)]
    for i in range(1, 5):
        a = (90.0 * i / 4) * S.DEG
        prof.append((0.012 - 0.012 * math.cos(a), H - 0.012 + 0.012 * math.sin(a)))
    for side in (1, -1):        # two halves, hinged at x = 0
        x0, x1 = gap / 2, W / 2
        cxh = side * (x0 + x1) / 2
        wh = x1 - x0
        big, small = 0.035, 0.004
        radii = (big, small, small, big) if side > 0 else (small, big, big, small)
        rings = []
        for d_in, y in prof:
            rr = tuple(max(0.0015, r - d_in) for r in radii)
            rings.append(rr_ring(wh - 2 * d_in, D - 2 * d_in, 0, y, cx=cxh, seg=4, radii=rr))
        g = loft(rings, smooth=True)
        g = S.facing(g, lambda p, cxh=cxh: V((p.x - cxh, 0.0, p.z)) * 0.2 + V((0, (p.y - (H - 0.03)) * 4, 0)))
        kit.mb(top_tag).add(g)
        # the top surface and the recessed underside panel
        kit.mb(top_tag).add(S.facing(cap(rings[-1]), (0, 1, 0)))
        kit.mb(top_tag).add(S.facing(cap(rings[0]), (0, -1, 0)))
        # blow-moulding tack-offs (shallow round dimples) on the underside
        for i in range(3):
            for k in range(2):
                px = side * (0.16 + i * 0.2)
                pz = (k - 0.5) * 0.3
                dim = B.g_cyl(0.022, 0.006, 10, r2=0.012)
                kit.mb(top_tag).add(dim, B.frame((0, 1, 0), (0, 0, 1)), (px, H - 0.024 - 0.003, pz))
    # --- steel: side rails (split at the hinge), hinge plates, leg frames, braces, caps
    rail_y = H - 0.050 - 0.011
    for sz in (1, -1):
        zr = sz * (D / 2 - 0.055)
        for sx in (1, -1):
            xa, xb = sx * 0.012, sx * (W / 2 - 0.07)
            kit.mb(steel).add(B.g_box((abs(xb - xa), 0.022, 0.022), bevel=0.002), None, ((xa + xb) / 2, rail_y, zr))
        # the centre hinge: two side plates and a pivot
        for dz in (-0.014, 0.014):
            kit.mb(steel).add(B.g_box((0.09, 0.04, 0.003), bevel=0.001), None, (0, rail_y - 0.006, zr + dz))
        kit.mb("steel").add(tube_between((0, rail_y - 0.012, zr - 0.018), (0, rail_y - 0.012, zr + 0.018), 0.005, 10))
        for rx in (-0.03, 0.03):
            kit.mb("steel").add(tube_between((rx, rail_y - 0.0, zr - 0.017), (rx, rail_y - 0.0, zr + 0.017), 0.0035, 8))
    # end rails across the table near each end
    for sx in (1, -1):
        kit.mb(steel).add(B.g_box((0.022, 0.022, D - 0.11 - 0.022), bevel=0.002), None, (sx * (W / 2 - 0.07), rail_y, 0))
    # leg frames: two legs, a top pivot tube in brackets, a low crossbar, braces with lock rings
    leg_r = 0.0127
    zl = D / 2 - 0.085
    for sx in (1, -1):
        xl = sx * (W / 2 - 0.135)
        ytop = rail_y - 0.004
        for sz in (1, -1):
            kit.mb(steel).add(tube_between((xl, 0.022, sz * zl), (xl, ytop, sz * zl), leg_r, 14))
            # the foot cap
            kit.mb("black_plastic").add(B.g_cyl(leg_r + 0.003, 0.03, 14, bevel=0.003), B.frame((0, 1, 0), (0, 0, 1)),
                                        (xl, 0.015, sz * zl))
            # the pivot bracket under the top
            kit.mb(steel).add(B.g_box((0.05, 0.035, 0.004), bevel=0.001), None, (xl, ytop + 0.006, sz * (zl + 0.018)))
            # a brace from the leg up to the rail, with its lock ring
            pa = V((xl, 0.40, sz * zl))
            pb = V((sx * (W / 2 - 0.45), rail_y - 0.008, sz * (D / 2 - 0.055)))
            kit.mb(steel).add(tube_between(pa, pb, 0.0075, 10))
            mid = pa + (pb - pa) * 0.62
            kit.mb(steel).add(tube_between(mid - (pb - pa).normalized() * 0.025, mid + (pb - pa).normalized() * 0.025,
                                           0.0105, 12))
            kit.mb("steel").add(tube_between(pa + V((sx * -0.004, 0, -sz * 0.0)) - V((0, 0, sz * 0.016)),
                                             pa + V((0, 0, sz * 0.002)), 0.004, 8))
        kit.mb(steel).add(tube_between((xl, ytop - 0.002, -zl - 0.02), (xl, ytop - 0.002, zl + 0.02), leg_r * 0.9, 14))
        kit.mb(steel).add(tube_between((xl, 0.17, -zl), (xl, 0.17, zl), leg_r * 0.85, 12))
    # the carry handle and latch at the middle of the front edge (black plastic, under the rim)
    hz = D / 2 - 0.02
    handle = [V((-0.07, H - 0.05, hz)), V((-0.06, H - 0.085, hz + 0.005)), V((0.06, H - 0.085, hz + 0.005)),
              V((0.07, H - 0.05, hz))]
    handle = S.smooth_path(handle, 5)
    kit.mb("black_plastic").add(S.sweep_profile(handle, [(0.009 * math.cos(t), 0.006 * math.sin(t)) for t in
                                                        [k * 2 * math.pi / 8 for k in range(8)]], up=(0, 0, 1)))
    kit.mb("black_plastic").add(B.g_box((0.05, 0.02, 0.03), bevel=0.004), None, (0.0, H - 0.06, -hz + 0.01))
    kit.anchor("A_TOP_0", (0, H, 0), (W, D, 0.002), forward=(0, 1, 0), up=(0, 0, -1), meta="surface=1")
    kit.anchor("A_HIT_0", (0, H - 0.025, 0), (W, 0.05, D))
    for i, sx in enumerate((1, -1)):
        kit.anchor(f"A_HIT_{1 + i}", (sx * (W / 2 - 0.135), (H - 0.05) / 2, 0), (0.06, H - 0.05, 2 * zl + 0.05))
    kit.finish(smooth=40.0)


# ====================================================================== wheelie bin

BIN_GREEN = (0.13, 0.27, 0.17)     # sRGB
BIN_REG = (0.0, 0.0, 0.62, 1.0)    # the green plastic region of tex_ship_bin (UV)


def bin_texture():
    """tex_ship_bin: moulded dark green plastic (left part, mapped by position), plus the prints (right part):
    the capacity plaque, a recycling sticker and a painted house number."""
    import numpy as np
    n = 1024

    def draw(a):
        x0 = int(n * 0.64)
        # capacity plaque (moulded, slightly lighter green with raised letters): region A (top right)
        a.rect(x0, int(n * 0.72), n - x0 - 8, int(n * 0.26), (0.10, 0.22, 0.14))
        a.text("240 L", x0 + (n - x0) / 2, n * 0.88, 74, (0.17, 0.33, 0.21), "arialbd.ttf", align="CENTER", valign="CENTER")
        a.text("EN 840-1  •  HDPE  •  MAX 96 kg", x0 + (n - x0) / 2, n * 0.77, 15, (0.17, 0.33, 0.21), "arialbd.ttf",
               align="CENTER", valign="CENTER")
        # recycling sticker: region B (middle right)
        yb = int(n * 0.40)
        a.rect(x0, yb, n - x0 - 8, int(n * 0.28), (0.96, 0.96, 0.92))
        a.rect(x0, yb + int(n * 0.21), n - x0 - 8, int(n * 0.07), (0.15, 0.55, 0.22))
        a.text("GENERAL WASTE", x0 + (n - x0) / 2, yb + n * 0.245, 26, (1, 1, 1), "arialbd.ttf", align="CENTER", valign="CENTER")
        a.text("♻", x0 + (n - x0) * 0.25, yb + n * 0.11, 80, (0.15, 0.55, 0.22), "seguisym.ttf", align="CENTER",
               valign="CENTER")
        for i, s_ in enumerate(["Bags tied, please", "No hot ashes", "Lid closed", "Collection: Tuesday"]):
            a.text(s_, x0 + (n - x0) * 0.45, yb + n * (0.165 - i * 0.04), 15, (0.1, 0.1, 0.1), "arialbd.ttf")
        # painted house number: region C (bottom right): white paint on green
        a.rect(x0, 8, n - x0 - 8, int(n * 0.30), BIN_GREEN)
        a.text("12", x0 + (n - x0) / 2, n * 0.155, 190, (0.93, 0.93, 0.9), "ariblk.ttf", align="CENTER", valign="CENTER")
    arr = S.art_layer(n, n, "bin", draw)
    # the green moulded plastic (left region): a little mottling
    w0 = int(n * BIN_REG[2])
    nz = S.noise_field(n, n, 14.0, 77)
    fine = S.noise_field(n, n, 1.5, 78)
    for k in range(3):
        arr[:, :w0, k] = BIN_GREEN[k] * (1 + 0.018 * nz[:, :w0] + 0.012 * fine[:, :w0])
    # paint brush streaks on the number
    xs = int(n * 0.64)
    reg = arr[8:int(n * 0.31), xs:n - 8]
    streak = S.noise_field(reg.shape[0], reg.shape[1], 0.8, 79, sy=6.0)
    white = reg[..., 0] > 0.5
    reg[..., :3] *= np.where(white, 0.94 + 0.06 * streak, 1.0)[..., None]
    arr[..., 3] = 1.0
    return P.save_png(arr, "ship_bin")


def bin_uv(p):
    """Green plastic: a projection of the position into the green region (subtle mottling only)."""
    u0, v0, u1, v1 = BIN_REG
    a = (p.x + p.z * 0.7 + 0.8) / 1.6
    b = (p.y + 0.05) / 1.15
    return (u0 + (u1 - u0) * min(1.0, max(0.0, a)), v0 + (v1 - v0) * min(1.0, max(0.0, b)))


def with_uv(geo, fn=bin_uv):
    verts, faces = geo[0], geo[1]
    return verts, faces, [[fn(V(verts[k])) for k in f] for f in faces], (geo[3] if len(geo) > 3 else None)


def build_bin(kit):
    bin_texture()
    tex = "tex_ship_bin"
    T = 0.005
    yb, yt = 0.045, 0.955                     # body bottom, top of the body walls (under the rim)
    # outer body: a tapered rounded box, wider at the top (front +z, back -z)
    def body_ring(t, inset=0.0):
        w = 0.468 + (0.552 - 0.468) * t
        d = 0.535 + (0.640 - 0.535) * t
        cz = 0.012 - 0.022 * t
        r = 0.055 + 0.01 * t
        return rr_ring(w - 2 * inset, d - 2 * inset, max(0.01, r - inset), yb + (yt - yb) * t, cz=cz, seg=5)
    ts = [0.0, 0.04, 0.12, 0.3, 0.5, 0.7, 0.88, 1.0]
    outer = [body_ring(t) for t in ts]
    # bottom edge rounding: pull the first ring in and down
    outer.insert(0, [V((p.x * 0.94, yb - 0.018, p.z * 0.95 + 0.0006)) for p in outer[0]])
    g = with_uv(S.facing(loft(outer), outward_xz((0, 0, 0))))
    kit.mb(tex).add(g)
    kit.mb(tex).add(with_uv(S.facing(cap(outer[0]), (0, -1, 0))))
    inner = [body_ring(t, T) for t in ts]
    gi = with_uv(S.facing(loft(inner), lambda p: -outward_xz((0, 0, 0))(p)))
    kit.mb(tex).add(gi)
    floor = [V((p.x, yb + T + 0.004, p.z)) for p in body_ring(0.0, T + 0.006)]
    kit.mb(tex).add(with_uv(S.facing(cap(floor), (0, 1, 0))))
    kit.mb(tex).add(with_uv(S.facing(loft([inner[0], floor]), (0, 1, 0))))
    # the rim: a rolled lip flaring out over the top of the walls (open underneath like the real moulding)
    top_in = inner[-1]
    top_out = outer[-1]

    def off(ring, d, y):
        ctr = V((0, 0, -0.01))
        out = []
        for p in ring:
            v = V((p.x - ctr.x, 0, p.z - ctr.z))
            out.append(V((p.x, y, p.z)) + v.normalized() * d)
        return out
    rim = [top_in, off(top_in, 0.0, yt + 0.022), off(top_out, 0.006, yt + 0.030), off(top_out, 0.022, yt + 0.026),
           off(top_out, 0.026, yt + 0.010), off(top_out, 0.026, yt - 0.018), off(top_out, 0.021, yt - 0.020),
           off(top_out, 0.020, yt - 0.004), off(top_out, 0.0, yt - 0.004)]
    rg = loft(rim)
    # orient each face by its position along the rim profile (the loft runs inside -> over -> outside -> under)
    kit.mb(tex).add(with_uv(rim_faces(rg, len(top_in))))
    rim_top = yt + 0.030
    # back: the handle bar and hinge knuckles, the lifting comb below it
    zb = -0.34
    hb_y = rim_top + 0.012
    hb_z = zb - 0.072
    kit.mb(tex).add(with_uv(tube_between((-0.22, hb_y, hb_z), (0.22, hb_y, hb_z), 0.016, 14)))
    for sx in (1, -1):
        # the arms joining the handle to the body
        arm = [V((sx * 0.225, hb_y, hb_z)), V((sx * 0.235, hb_y - 0.01, hb_z + 0.03)), V((sx * 0.245, yt - 0.02, zb - 0.01))]
        kit.mb(tex).add(with_uv(S.sweep_profile(S.smooth_path(arm, 4), [(0.016 * math.cos(t), 0.022 * math.sin(t)) for t in
                                                                         [k * 2 * math.pi / 8 for k in range(8)]],
                                                up=(1, 0, 0))))
    # lifting comb: a horizontal bar with teeth under the rim at the back
    kit.mb(tex).add(with_uv(B.xf(B.g_box((0.44, 0.03, 0.03), bevel=0.006, seg=2), None, (0, yt - 0.075, zb - 0.032))))
    for k in range(9):
        kit.mb(tex).add(with_uv(B.xf(B.g_box((0.018, 0.05, 0.022), bevel=0.004), None, (-0.2 + k * 0.05, yt - 0.11, zb - 0.026))))
    # axle housing and the wheels' axle at the back bottom; front feet
    ax_y, ax_z = 0.100, -0.300
    kit.mb(tex).add(with_uv(B.xf(B.g_box((0.50, 0.11, 0.10), bevel=0.012, seg=2), None, (0, 0.105, -0.262))))
    kit.mb("steel").add(tube_between((-0.30, ax_y, ax_z), (0.30, ax_y, ax_z), 0.010, 12))
    for sx in (1, -1):
        kit.mb(tex).add(with_uv(B.xf(B.g_box((0.09, 0.05, 0.07), bevel=0.01, seg=2), None, (sx * 0.15, 0.025, 0.23))))
    # wheels: tyre + hub with spokes, on anchors (spin about local x)
    for i, sx in enumerate((1, -1)):
        wx = sx * 0.272
        a = kit.anchor(f"A_WHEEL_{i}", (wx, ax_y, ax_z), (0.05, 0.2, 0.2), meta="spin=x,r=0.100")
        prof = [(0.062, -0.024), (0.088, -0.025), (0.097, -0.02), (0.100, -0.012), (0.100, 0.012), (0.097, 0.02),
                (0.088, 0.025), (0.062, 0.024)]
        tyre = B.g_lathe(prof, 28)
        Mw = B.frame((1, 0, 0), (0, 1, 0))
        kit.piece(a, "rubber", "wheel").add(tyre, Mw, (wx, ax_y, ax_z))
        # tread grooves
        hub = B.merge(B.g_lathe([(0.0, -0.02), (0.063, -0.02), (0.063, 0.02), (0.0, 0.02)], 20),
                      B.g_lathe([(0.0, 0.021), (0.02, 0.021), (0.02, 0.026), (0.0, 0.026)], 12))
        kit.piece(a, "grey_plastic", "wheel").add(hub, Mw, (wx, ax_y, ax_z))
        for k in range(6):
            ang = k * math.pi / 3
            sp = B.xf(B.g_box((0.008, 0.088, 0.006)), B.rot("z", ang), (0, 0, 0.0215))
            kit.piece(a, "grey_plastic", "wheel").add(sp, Mw, (wx, ax_y, ax_z))
        cap_g = B.g_cyl(0.012, 0.008, 12, bevel=0.002)
        kit.piece(a, "steel", "wheel").add(cap_g, Mw, (wx + sx * 0.028, ax_y, ax_z))
    # front prints: capacity plaque and the recycling sticker (decals a hair off the surface)
    def decal(name, region, centre, w, h, normal, up):
        nrm, upv = V(normal).normalized(), V(up).normalized()
        right = nrm.cross(upv).normalized()      # reading right seen from the front of the decal
        u0, v0, u1, v1 = region
        pts = [centre - right * (w / 2) - upv * (h / 2), centre + right * (w / 2) - upv * (h / 2),
               centre + right * (w / 2) + upv * (h / 2), centre - right * (w / 2) + upv * (h / 2)]
        S.add_quad(kit.mb(tex), pts, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], nrm)
    # the front wall's outer surface at height y (front z on the ring)
    def front_at(y):
        t = (y - yb) / (yt - yb)
        d = 0.535 + (0.640 - 0.535) * t
        cz = 0.012 - 0.022 * t
        return cz + d / 2
    slope = V((0, (0.640 - 0.535) / 2, (yt - yb)))       # the front wall leans out going up
    fn = V((0, -slope.z, slope.y)).normalized()           # unit normal of the front wall (points +z, a little down)
    fn = -fn if fn.z < 0 else fn
    fup = V((0, slope.z, slope.y * 0)).normalized()
    fup = V((0, 1, (0.640 - 0.535) / 2 / (yt - yb))).normalized()
    yp = 0.76
    decal("plaque", (0.648, 0.72, 0.992, 0.98), V((0, yp, front_at(yp) + 0.0012)), 0.20, 0.15, fn, fup)
    ys = 0.52
    decal("sticker", (0.648, 0.40, 0.992, 0.68), V((0.0, ys, front_at(ys) + 0.0012)), 0.17, 0.14, fn, fup)
    # the lid (hinged at the back over the handle bar)
    hinge = V((0, hb_y, hb_z))
    lid = kit.anchor("A_LID_0", tuple(hinge), (0.6, 0.06, 0.72), meta="hinge=x,open=-110,order=0")
    build_lid(kit, lid, tex, rim_top, hinge)
    # the house number painted on the lid's front half
    lid_top = rim_top + 0.008 + 0.018
    nz_c = 0.17
    decal_lid = [V((-0.09, lid_top + lid_dome(0, nz_c) + 0.0012, nz_c - 0.07)), V((0.09, lid_top + lid_dome(0, nz_c) + 0.0012, nz_c - 0.07)),
                 V((0.09, lid_top + lid_dome(0, nz_c) + 0.0012, nz_c + 0.07)), V((-0.09, lid_top + lid_dome(0, nz_c) + 0.0012, nz_c + 0.07))]
    # read from the front: right = -x, up = -z
    S.add_quad(kit.piece(lid, tex, "lid"), decal_lid, [(0.992, 0.31), (0.648, 0.31), (0.648, 0.008), (0.992, 0.008)], (0, 1, 0))
    # anchors
    kit.anchor("A_MOUTH_0", (0, yt - 0.08, -0.01), (0.50, 0.16, 0.58), meta="volume=240")
    kit.anchor("A_LINER_0", (0, rim_top, -0.01), (0.552, 0.004, 0.640), meta="fold=0.06")
    kit.anchor("A_HANDLE_0", (0, hb_y, hb_z), (0.44, 0.04, 0.04), forward=(0, 0, -1), up=(0, 1, 0), meta="grip=1")
    kit.anchor("A_HIT_0", (0, (rim_top + 0.02) / 2, -0.01), (0.60, rim_top + 0.02, 0.70))
    kit.anchor("A_HIT_1", (0, 0.10, -0.29), (0.60, 0.20, 0.12))
    kit.finish(smooth=40.0)


def rim_faces(geo, n):
    """Orients the rim loft: each band faces away from the centre line of its profile (inside up, outside out...)."""
    verts, faces = geo[0], geo[1]
    out = []
    for f in faces:
        pts = [verts[k] for k in f]
        nrm = B._newell(pts)
        ctr = sum(pts, V()) / 4
        band = f[0] // n
        radial = V((ctr.x, 0, ctr.z + 0.01)).normalized()
        exp = {0: -radial, 1: V((0, 1, 0)), 2: V((0, 1, 0)) + radial, 3: radial, 4: radial, 5: V((0, -1, 0)),
               6: -radial, 7: V((0, -1, 0))}.get(band, radial)
        out.append(f if nrm.dot(exp) >= 0 else f[::-1])
    return verts, out, None, geo[3]


def lid_dome(x, z):
    return 0.016 * max(0.0, 1 - (x / 0.3) ** 2) * max(0.0, 1 - ((z + 0.01) / 0.36) ** 2)


def build_lid(kit, lid, tex, rim_top, hinge):
    """The lid: a domed top over the rim with a skirt all round, a front grip lip and hinge knuckles at the back."""
    mb = kit.piece(lid, tex, "lid")
    w, d = 0.596, 0.700
    cz = -0.008
    y0 = rim_top + 0.008               # underside of the lid's top sheet
    yt = y0 + 0.018                    # top surface at the edge (then domed)
    # the rounded edge and the skirt: rings from the top grid's border outwards and down
    rings = []
    for (dx, y) in ((0.025, yt), (0.012, yt - 0.002), (0.004, yt - 0.008), (0.0, yt - 0.016), (0.0, yt - 0.045),
                    (0.004, yt - 0.047), (0.004, yt - 0.020)):
        rings.append(rr_ring(w - 2 * dx, d - 2 * dx, max(0.004, 0.05 - dx), y, cz=cz, seg=5))
    # match ring 0 to the grid border height (domed): lift by the dome there
    rings[0] = [V((p.x, p.y + lid_dome(p.x, p.z), p.z)) for p in rings[0]]
    sk = loft(rings)
    nb = len(rings[0])
    verts, faces = sk[0], sk[1]
    of = []
    for f in faces:
        pts = [verts[k] for k in f]
        nrm = B._newell(pts)
        ctr = sum(pts, V()) / 4
        band = f[0] // nb
        radial = V((ctr.x, 0, ctr.z - cz)).normalized()
        exp = {0: V((0, 1, 0)), 1: V((0, 1, 0)) + radial, 2: radial, 3: radial, 4: V((0, -1, 0)), 5: -radial}.get(band, radial)
        of.append(f if nrm.dot(exp) >= 0 else f[::-1])
    mb.add(with_uv((verts, of, None, sk[3])))
    # the domed top: concentric rings inwards from ring 0 (same vertex count), then a small cap
    tops = [rings[0]]
    for dx in (0.045, 0.08, 0.12, 0.165, 0.21, 0.25):
        rr = rr_ring(w - 2 * dx, d - 2 * dx, max(0.004, 0.05 - dx * 0.2), yt, cz=cz, seg=5)
        tops.append([V((p.x, p.y + lid_dome(p.x, p.z), p.z)) for p in rr])
    mb.add(with_uv(S.facing(loft(tops), (0, 1, 0))))
    mb.add(with_uv(S.facing(cap(tops[-1]), (0, 1, 0))))
    # underside of the top sheet (seen when the lid is open)
    under = rr_ring(w - 0.012, d - 0.012, 0.045, yt - 0.020, cz=cz, seg=5)
    mb.add(with_uv(S.facing(cap(under), (0, -1, 0))))
    mb.add(with_uv(S.facing(loft([rings[-1], under]), (0, -1, 0))))
    # front grip lip
    mb.add(with_uv(B.xf(B.g_box((0.26, 0.012, 0.03), bevel=0.005, seg=2), None, (0, yt - 0.04, cz + d / 2 + 0.008))))
    # hinge knuckles round the handle bar
    for sx in (-0.17, -0.06, 0.06, 0.17):
        mb.add(with_uv(tube_between((sx - 0.035, hinge.y, hinge.z), (sx + 0.035, hinge.y, hinge.z), 0.021, 12)))
        mb.add(with_uv(B.xf(B.g_box((0.07, 0.016, 0.05), bevel=0.004), None, (sx, hinge.y + 0.012, hinge.z + 0.03))))


def fill_lid_gap(kit):
    pass


# ====================================================================== bin bags

def build_bag_full(kit):
    tag = "black_plastic"
    rng = random.Random(21)
    ph = [rng.uniform(0, 6.28) for _ in range(12)]
    pokes = []
    for _ in range(13):    # corners and ends of boxes and bottles inside pushing the film out
        th = rng.uniform(0, 2 * math.pi)
        t = rng.uniform(0.12, 0.7)
        pokes.append((th, t, rng.uniform(0.015, 0.045), rng.uniform(0.18, 0.4), rng.random() < 0.5))
    creases = []
    for _ in range(46):    # the film folds where it is slack
        n = V((rng.gauss(0, 1), rng.gauss(0, 0.6), rng.gauss(0, 1))).normalized()
        creases.append((n, rng.uniform(-0.2, 0.2), rng.uniform(0.012, 0.05), rng.uniform(0.002, 0.007) *
                        (1 if rng.random() < 0.4 else -1)))
    Hb = 0.60
    rx, rz = 0.245, 0.195

    def radius(t):
        if t < 0.05:
            return 0.86 + 0.14 * math.sin(t / 0.05 * math.pi / 2)
        if t < 0.55:
            return 1.0 - 0.06 * ((t - 0.3) / 0.25) ** 2
        k = (t - 0.55) / 0.45
        return max(0.07, (1 - k ** 1.35) * 0.94 + 0.07 * k)

    def fn(i, j):
        th = 2 * math.pi * i
        t = j
        r = radius(t)
        lump = (0.09 * S.fbm(V((math.cos(th) * 1.5, t * 2.4, math.sin(th) * 1.5)), 4, seed=4)) * (1 - t ** 3)
        r *= 1 + lump
        for (pt, pt_t, amp, wdt, sharp) in pokes:
            dth = math.atan2(math.sin(th - pt), math.cos(th - pt))
            dd = math.sqrt((dth / wdt) ** 2 + ((t - pt_t) / (wdt * 0.55)) ** 2)
            if dd < 1:
                r += (amp / rx) * (1 - dd) ** (2.2 if sharp else 1.2)
        x = rx * r * math.cos(th)
        z = rz * r * math.sin(th)
        y = Hb * t if t >= 0.06 else Hb * t * 0.35
        p = V((x, y, z))
        nrm = V((math.cos(th) / rx, 0.0, math.sin(th) / rz)).normalized()
        # gathered pleats running up into the neck
        g = max(0.0, min(1.0, (t - 0.42) / 0.4))
        pleat = 0.011 * g * (1 - g * 0.6) * math.sin(th * 11 + ph[0] + t * 4) * (r / 0.9)
        # slack folds (tents), fine crinkles
        dsp = 0.0
        for (n, d, w, a) in creases:
            q = abs(n.dot(p - V((0, 0.3, 0))) - d)
            if q < w:
                dsp += a * (1 - q / w)
        dsp *= (1 - t ** 4)
        dsp += 0.0016 * math.sin(th * 29 + t * 47 + ph[2]) * math.sin(t * 31 + ph[3]) * (1 - t)
        p = p + nrm * (pleat + dsp)
        return (p.x, max(0.0, p.y), p.z)
    g = S.grid_surface(fn, 64, 32, closed_u=True, smooth=True)
    g = S.facing(g, lambda p: V((p.x, 0, p.z)) + V((0, -0.3 if p.y < 0.02 else 0.0, 0)))
    kit.mb(tag).add(g)
    kit.mb(tag).add(S.facing(cap([V(fn(i / 64, 0.0)) for i in range(64)]), (0, -1, 0)))
    # the knot: a lumpy twisted ball on the neck, and the two tied ears drooping over
    ky = Hb + 0.025
    knot_v, knot_f = S.icosphere(3)
    kv = []
    for p in knot_v:
        q = V((p.x * 0.042, p.y * 0.032, p.z * 0.036))
        q *= 1 + 0.3 * S.fbm(p * 2.2, 2, seed=9) + 0.12 * math.sin(p.x * 9 + p.y * 7)
        kv.append(q + V((0, ky, 0)))
    kit.mb(tag).add((kv, knot_f, None, [True] * len(knot_f)))
    for side, lean, twist in ((1, 0.9, 0.4), (-1, 0.6, -0.3)):
        def ear(i, j, side=side, lean=lean, twist=twist):
            w = 0.095 * (1 - 0.35 * j) * (0.75 + 0.25 * math.sin(i * math.pi))
            s_ = (i - 0.5) * w
            h = j * 0.12
            ang = lean * j * 1.3
            x = side * (0.012 + math.sin(ang) * h * 0.9)
            y = ky + 0.012 + math.cos(ang) * h * 0.75 - 0.03 * j * j
            z = s_ * math.cos(twist * j) + 0.012 * math.sin(j * 5 + side)
            x += 0.006 * math.sin(i * 11 + j * 6) + s_ * math.sin(twist * j) * side
            y += 0.007 * math.sin(i * 7 + j * 9 + side)
            return (x, y, z)
        e1 = S.grid_surface(ear, 8, 8, smooth=True)
        e2 = S.grid_surface(ear, 8, 8, smooth=True, flip=True)
        kit.mb(tag).add(B.merge(e1, e2))
    kit.anchor("A_KNOT_0", (0, ky + 0.01, 0), (0.09, 0.09, 0.09), forward=(0, 1, 0), up=(0, 0, 1), meta="grab=1")
    kit.anchor("A_HIT_0", (0, 0.35, 0), (0.50, 0.70, 0.40))
    kit.finish(smooth=60.0)


def roll_label_texture():
    w, h = 1024, 416

    def draw(a):
        a.rect(0, 0, w, h, (0.95, 0.95, 0.92))
        a.rect(0, h * 0.70, w, h * 0.30, (0.12, 0.45, 0.20))
        a.text("HEAVY DUTY BIN LINERS", w / 2, h * 0.85, 46, (1, 1, 1), "arialbd.ttf", align="CENTER", valign="CENTER")
        a.text("40 x 240 L", w * 0.3, h * 0.42, 84, (0.08, 0.08, 0.08), "ariblk.ttf", align="CENTER", valign="CENTER")
        a.text("EXTRA STRONG  •  TIE TOP", w * 0.72, h * 0.48, 26, (0.12, 0.45, 0.20), "arialbd.ttf", align="CENTER",
               valign="CENTER")
        a.text("Tear along the perforation", w * 0.72, h * 0.28, 20, (0.2, 0.2, 0.2), "arial.ttf", align="CENTER",
               valign="CENTER")
        a.text("♻", w * 0.93, h * 0.30, 60, (0.12, 0.45, 0.20), "seguisym.ttf", align="CENTER", valign="CENTER")
    arr = S.art_layer(w, h, "binroll", draw)
    arr[..., 3] = 1.0
    return P.save_png(arr, "ship_binroll")


def build_bag_roll(kit):
    roll_label_texture()
    tag = "black_plastic"
    L, R = 0.26, 0.038
    r_core = 0.0125
    cy = R
    Mx = B.frame((1, 0, 0), (0, 1, 0))     # lathe axis (local z) -> +x
    # the outer surface with soft ridges where the folded bag edges are, and the ends with spiral rings
    prof = [(r_core + 0.001, -L / 2 + 0.002)]
    for k in range(9):
        r = r_core + 0.003 + (R - r_core - 0.006) * k / 8
        prof.append((r, -L / 2 + (0.0006 if k % 2 else 0.0)))
    prof += [(R - 0.002, -L / 2), (R, -L / 2 + 0.004)]
    for k in range(1, 12):
        z = -L / 2 + 0.004 + (L - 0.008) * k / 12
        prof.append((R + 0.0006 * math.sin(k * 2.1), z))
    prof += [(R, L / 2 - 0.004), (R - 0.002, L / 2)]
    for k in range(8, -1, -1):
        r = r_core + 0.003 + (R - r_core - 0.006) * k / 8
        prof.append((r, L / 2 - (0.0006 if k % 2 else 0.0)))
    prof.append((r_core + 0.001, L / 2 - 0.002))
    body = B.g_lathe(prof, 32)
    kit.mb(tag).add(S.facing(B.xf(body, Mx, (0, cy, 0)),
                             lambda p: V((p.x * 4 if abs(p.x) > L / 2 - 0.003 else 0, p.y - cy, p.z))))
    # cardboard core
    core = B.g_lathe([(r_core - 0.0018, L / 2 - 0.001), (r_core - 0.0018, -L / 2 + 0.001), (r_core + 0.0012, -L / 2 + 0.001),
                      (r_core + 0.0012, L / 2 - 0.001), (r_core - 0.0018, L / 2 - 0.001)], 20)
    kit.mb("cardboard").add(S.facing(B.xf(core, Mx, (0, cy, 0)),
                                     lambda p: V((p.x if abs(p.x) > L / 2 - 0.0015 else 0, p.y - cy, p.z)) *
                                     (1 if math.hypot(p.y - cy, p.z) > r_core - 0.0003 else -1)))
    # the paper band round the middle
    bw = 0.10
    band = S.grid_surface(lambda i, j: (-bw / 2 + bw * j, cy + (R + 0.0009) * math.cos(2 * math.pi * i),
                                        (R + 0.0009) * math.sin(2 * math.pi * i)), 32, 1, closed_u=True, smooth=True,
                          uv_fn=lambda u, v: (u, v))
    kit.mb("tex_ship_binroll").add(S.facing(band, lambda p: V((0, p.y - cy, p.z))))
    # the outer layer's end: a slight step along the roll (outside the band) and a lifted corner at +x
    ae = 0.30 * math.pi
    for (x0, x1) in ((-L / 2 + 0.004, -bw / 2 - 0.002), (bw / 2 + 0.002, L / 2 - 0.004)):
        def step(i, j, x0=x0, x1=x1):
            x = x0 + (x1 - x0) * i
            a = ae - 0.10 * j
            r = R + 0.0004 * (1 - j)
            return (x, cy + r * math.cos(a), r * math.sin(a))
        kit.mb(tag).add(S.facing(S.grid_surface(step, 6, 1, smooth=True), lambda p: V((0, p.y - cy, p.z))))

    def corner(i, j):
        x = L / 2 - 0.004 - 0.045 * i * (1 - 0.6 * j)
        a = ae - 0.35 * j
        lift = 0.012 * j * j * (1 - i) + 0.0012
        r = R + lift
        return (x, cy + r * math.cos(a), r * math.sin(a))
    kit.mb(tag).add(B.merge(S.grid_surface(corner, 4, 4, smooth=True), S.grid_surface(corner, 4, 4, smooth=True, flip=True)))
    kit.anchor("A_HIT_0", (0, cy, 0.005), (L, 2 * R, 2 * R + 0.02))
    kit.anchor("A_TEAR_0", tuple(V(corner(0.3, 1.0))), (0.03, 0.02, 0.02), forward=(0, 0, 1), up=(0, 1, 0), meta="tear=1")
    kit.finish(smooth=50.0)


# ====================================================================== paperwork tray

TR_W, TR_D, TR_H = 0.270, 0.345, 0.066
TR_PX = 3.6 / 0.001 / 1000.0 * 1000.0   # 3.6 px per mm (as px per metre / 1000) -> 3600 px/m
TR_SCOOP = (0.085, 0.034)              # front scoop half width and depth below the rim


def tray_regions():
    k = 3600.0
    fw, fd = TR_W * k, TR_D * k
    hh = TR_H * k
    return {"floor": (8, 8, fw, fd), "back": (8, fd + 24, fw, hh), "front": (8, fd + hh + 40, fw, hh),
            "left": (fw + 24, 8, hh, fd), "right": (fw + hh + 40, 8, hh, fd)}, k


def scoop_y(x):
    """Height of the front wall's top edge at x (a smooth U dip)."""
    hw, dep = TR_SCOOP
    if abs(x) >= hw + 0.02:
        return TR_H
    t = min(1.0, abs(x) / hw)
    yy = TR_H - dep * (math.cos(t * math.pi / 2) ** 1.2)
    if abs(x) > hw:
        k = (abs(x) - hw) / 0.02
        yy = yy + (TR_H - yy) * k
    return yy


def tray_texture():
    """tex_ship_tray_mesh: black powder-coated steel, perforated (round 3 mm holes, 4.5 mm staggered) with solid
    margins at every fold and edge; holes are alpha 0 (the game's 'mesh' textures are alpha-cutout)."""
    import numpy as np
    n = 2048
    regs, k = tray_regions()
    arr = np.zeros((n, n, 4), dtype=np.float32)
    col = np.array([0.05, 0.05, 0.055], dtype=np.float32)
    arr[..., :3] = col
    arr[..., 3] = 1.0
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    pitch, rh, margin = 0.0045 * k, 0.0015 * k, 0.0055 * k
    for name, (x0, y0, w, h) in regs.items():
        sl = (slice(int(y0), int(y0 + h)), slice(int(x0), int(x0 + w)))
        X = xx[sl] - x0
        Y = yy[sl] - y0
        dy = pitch * math.sqrt(3) / 2
        row = np.floor(Y / dy + 0.5)
        off = (row % 2) * pitch / 2
        cx = np.floor((X - off) / pitch + 0.5) * pitch + off
        cy = row * dy
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        # the solid margins (and the front scoop's edge)
        edge = np.minimum(np.minimum(X, w - X), np.minimum(Y, h - Y))
        if name == "front":
            xm = (X / k) - TR_W / 2                              # x in metres (reading from the front: see uv)
            top = np.vectorize(scoop_y)(-xm)
            edge = np.minimum(edge, (top - Y / k) * k)
        hole = (d < rh) & (edge > margin)
        aa = np.clip((d - rh) / 1.2 + 0.5, 0, 1)
        alpha = np.where(edge > margin, aa, 1.0)
        a = arr[sl]
        a[..., 3] = alpha
        # a soft bevel darkening round each hole
        a[..., :3] = col * (0.8 + 0.2 * np.clip((d - rh) / (pitch * 0.3), 0, 1))[..., None]
    return P.save_png(arr, "ship_tray_mesh")


def build_tray(kit):
    tray_texture()
    tex = "tex_ship_tray_mesh"
    paint = "paint_black"
    regs, k = tray_regions()
    W, Dp, Hh = TR_W, TR_D, TR_H
    yf = 0.006            # floor height (on four feet)
    t = 0.0007            # sheet thickness

    def ruv(name, a, b):
        x0, y0, w, h = regs[name]
        return ((x0 + a * k) / 2048.0, (y0 + b * k) / 2048.0)
    mb = kit.mb(tex)
    # floor (both sides)
    for sgn in (1, -1):
        pts = [V((-W / 2, yf + sgn * t / 2, -Dp / 2)), V((W / 2, yf + sgn * t / 2, -Dp / 2)),
               V((W / 2, yf + sgn * t / 2, Dp / 2)), V((-W / 2, yf + sgn * t / 2, Dp / 2))]
        uvs = [ruv("floor", p.x + W / 2, p.z + Dp / 2) for p in pts]
        S.add_quad(mb, pts, uvs, (0, sgn, 0))
    # back and side walls (both sides): plain rectangles
    for sgn in (1, -1):
        zb = -Dp / 2 + sgn * t / 2
        pts = [V((-W / 2, yf, zb)), V((W / 2, yf, zb)), V((W / 2, Hh, zb)), V((-W / 2, Hh, zb))]
        S.add_quad(mb, pts, [ruv("back", p.x + W / 2, p.y - yf) for p in pts], (0, 0, sgn))
        for side, nm in ((-1, "left"), (1, "right")):
            xw = side * W / 2 - side * sgn * t / 2
            pts = [V((xw, yf, -Dp / 2)), V((xw, yf, Dp / 2)), V((xw, Hh, Dp / 2)), V((xw, Hh, -Dp / 2))]
            S.add_quad(mb, pts, [ruv(nm, p.y - yf, p.z + Dp / 2) for p in pts], (-side * sgn, 0, 0))
    # the front wall with the scoop: strips between x samples
    xs = [-W / 2 + W * i / 40 for i in range(41)]
    for sgn in (1, -1):
        zf = Dp / 2 - sgn * t / 2
        for i in range(40):
            xa, xb = xs[i], xs[i + 1]
            pts = [V((xa, yf, zf)), V((xb, yf, zf)), V((xb, scoop_y(xb), zf)), V((xa, scoop_y(xa), zf))]
            # read from the front: u runs from +x to -x
            S.add_quad(mb, pts, [ruv("front", W / 2 - p.x, p.y - yf) for p in pts], (0, 0, -sgn))
    # rolled rims along every top edge (solid paint), corner posts, feet
    prof = [(0.0024 * math.cos(a), 0.0024 * math.sin(a)) for a in [i * 2 * math.pi / 8 for i in range(8)]]
    rim_back = [V((-W / 2, Hh, -Dp / 2)), V((W / 2, Hh, -Dp / 2))]
    kit.mb(paint).add(S.sweep_profile(rim_back, prof, up=(0, 1, 0)))
    for side in (-1, 1):
        kit.mb(paint).add(S.sweep_profile([V((side * W / 2, Hh, -Dp / 2)), V((side * W / 2, Hh, Dp / 2))], prof, up=(0, 1, 0)))
    front = [V((x, scoop_y(x), Dp / 2)) for x in xs]
    kit.mb(paint).add(S.sweep_profile(front, prof, up=(0, 0, 1)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            kit.mb(paint).add(tube_between((sx * W / 2, yf - 0.001, sz * Dp / 2), (sx * W / 2, Hh, sz * Dp / 2), 0.0035, 10))
            kit.mb("rubber").add(B.g_cyl(0.006, yf, 10), B.frame((0, 1, 0), (0, 0, 1)),
                                 (sx * (W / 2 - 0.012), yf / 2, sz * (Dp / 2 - 0.012)))
    # the folds along the floor edges (solid)
    for (a, b_) in (((-W / 2, -Dp / 2), (W / 2, -Dp / 2)), ((-W / 2, Dp / 2), (W / 2, Dp / 2)),
                    ((-W / 2, -Dp / 2), (-W / 2, Dp / 2)), ((W / 2, -Dp / 2), (W / 2, Dp / 2))):
        kit.mb(paint).add(S.sweep_profile([V((a[0], yf, a[1])), V((b_[0], yf, b_[1]))],
                                          [(0.0018 * math.cos(q), 0.0018 * math.sin(q)) for q in
                                           [i * 2 * math.pi / 6 for i in range(6)]], up=(0, 1, 0)))
    kit.anchor("A_STACK_0", (0, yf + t, 0.0), (0.215, 0.300, 0.055), forward=(0, 1, 0), up=(0, 0, -1),
               meta="paper=A4,portrait=1")
    kit.anchor("A_HIT_0", (0, Hh / 2, 0), (W + 0.006, Hh + 0.004, Dp + 0.006))
    kit.finish(smooth=40.0)


# ====================================================================== registry

def _mk(fn, notes=None, views=((30, 30), (-120, 25)), extra=None, samples=48):
    def build(mid, prev):
        kit = S.Kit(mid)
        fn(kit)
        out = S.finish_model(kit, mid, notes)
        if prev:
            S.render(kit.root, mid, list(views), samples=samples)
            if extra:
                extra(kit, mid)
        return out
    return build


def _bin_extra(kit, mid):
    S.pose_pieces(kit.root, {"A_LID_0": ("x", -110)})
    S.render(kit.root, mid, [(25, 40)], samples=48, start=2)


def _table_extra(kit, mid):
    S.render(kit.root, mid, [(20, -28)], samples=48, start=2, floor=False, below=True)


MODELS = [
    ("furniture", "unbox_table", _mk(build_table, [
        "  note: 1.5 x 0.7 m, top surface at y = 0.76; origin on the floor at the centre; fold-in-half (hinge across "
        "x = 0). A_TOP_0: local X = +x (1.5 m), local Y = -z (0.7 m), +Z = up out of the top."],
        views=((30, 28), (-150, 22)), extra=_table_extra)),
    ("furniture", "wheelie_bin", _mk(build_bin, [
        "  note: 240 L, ~0.60 x 1.03 x 0.74 m with the handle; front +z, handle, hinge and wheels at -z. The lid opens "
        "by turning about A_LID_0's x axis (open=-110 lifts the front). Wheels spin about their anchor's local x."],
        views=((30, 18), (-140, 15)), extra=_bin_extra)),
    ("furniture", "bin_bag_full", _mk(build_bag_full, [
        "  note: origin bottom centre; A_KNOT_0 at the knot (+Z up) is the grab point."], views=((30, 20), (-130, 25)))),
    ("furniture", "bin_bag_roll", _mk(build_bag_roll, [
        "  note: lying along x, origin bottom centre; A_TEAR_0 = the lifted corner of the outer bag."], views=((35, 30), (-60, 20)))),
    ("furniture", "paperwork_tray", _mk(build_tray, [
        "  note: A4 letter tray, origin bottom centre, front scoop at +z; tex_ship_tray_mesh is an alpha-cutout "
        "perforation (holes alpha 0); A_STACK_0 = the top of the floor where papers stack (local X = +x, local Y = -z "
        "(the page's top towards the back), +Z up)."], views=((25, 38), (-150, 30)))),
]
