"""
extras_caps.py - the part caps, guards and the PSU sticker of UNBOXING.md section 2.5 (agent C).

Convention for every cap / guard (so one Pullable works for all): the model's local +Z is the direction it is
pulled off, and its origin is the seat reference it is placed at. Placement (PLACEMENTS below and the report) is
given as a parent (the part root or an anchor), a local position and forward/up directions in the parent's
axes (Unity: localRotation = Quaternion.LookRotation(forward, up)).

  cap_pcie16        clear PET U-channel over a graphics card's x16 gold fingers (89 mm edge), a key rib in the
                    edge's notch, a pull tab at the far (-x card) end.   On: the GPU root, pull = GPU -Z.
  cap_dp, cap_hdmi  black rubber dust plugs: a sleeve that slides in round the port's tongue, a head on the
                    shell lip and a ribbed pull tab.                    On: A_PORT_DP_n / A_PORT_HDMI_0, identity.
  guard_ram_ddr5, guard_ram_ddr4
                    clear clip over a DIMM's gold fingers, its key-notch gap at the stick's notch, a pull tab at
                    the +y end.                                         On: the RAM root, pull = RAM -Z.
  cap_paste         clear dome over the stock cooler's pre-applied paste, a flange and a pull tab.
                                                                        On: A_PASTE_PRE_0, identity.
  sticker_psu_voltage
                    yellow "CHECK VOLTAGE 115V/230V BEFORE USE" sticker draped over the rocker switch in its
                    shipped (off) pose; tex_sticker_psu.       At A_SWITCH_PSU_0's pose (parent: PSU root).
"""
import math

import dct_common as c
import parts_b as pb
import extras_common as xc
from mathutils import Matrix, Vector as V

DEG = math.pi / 180.0
M_XZ = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))  # 2D (x, z) -> extruded along y
M_YZ = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0)))  # 2D (y, z) -> extruded along x
CLEAR = "clear_plastic"

# parent frame / anchor, local position, forward, up: where each cap sits (Unity, the parent's axes)
PLACEMENTS = {
    "cap_pcie16": [("gpu_rx66", "<root>", (0.0, 0.0, 0.0), (0, 0, -1), (0, 1, 0)),
                   ("gpu_rx88", "<root>", (0.0, 0.0, 0.0), (0, 0, -1), (0, 1, 0))],
    "cap_dp": [(g, f"A_PORT_DP_{i}", (0.0, 0.0, 0.0), (0, 0, 1), (0, 1, 0)) for g in ("gpu_rx66", "gpu_rx88")
               for i in range(3)],
    "cap_hdmi": [(g, "A_PORT_HDMI_0", (0.0, 0.0, 0.0), (0, 0, 1), (0, 1, 0)) for g in ("gpu_rx66", "gpu_rx88")],
    "guard_ram_ddr5": [("ram_ddr5_16", "<root>", (0.0, 0.0, 0.0), (0, 0, -1), (0, 1, 0))],
    "guard_ram_ddr4": [("ram_ddr4_8", "<root>", (0.0, 0.0, 0.0), (0, 0, -1), (0, 1, 0))],
    "cap_paste": [("cooler_stock", "A_PASTE_PRE_0", (0.0, 0.0, 0.0), (0, 0, 1), (0, 1, 0))],
    "sticker_psu_voltage": [("psu_450", "A_SWITCH_PSU_0", (0.0, 0.0, 0.0), (0, 0, 1), (0, 1, 0)),
                            ("psu_750", "A_SWITCH_PSU_0", (0.0, 0.0, 0.0), (0, 0, 1), (0, 1, 0))],
}

# the part anchors used above, in the part frames (from the part reports; checked against the FBX at build time)
PART_ANCHORS = {
    ("gpu_rx66", "A_PORT_DP_0"): ((0.0965, -0.0046, 0.0180), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx66", "A_PORT_DP_1"): ((0.0965, -0.0046, 0.0370), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx66", "A_PORT_DP_2"): ((0.0965, -0.0046, 0.0560), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx66", "A_PORT_HDMI_0"): ((0.0965, -0.0046, 0.0750), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx88", "A_PORT_DP_0"): ((0.0965, -0.0046, 0.0180), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx88", "A_PORT_DP_1"): ((0.0965, -0.0046, 0.0370), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx88", "A_PORT_DP_2"): ((0.0965, -0.0046, 0.0560), (1, 0, 0), (0, 1, 0)),
    ("gpu_rx88", "A_PORT_HDMI_0"): ((0.0965, -0.0046, 0.0750), (1, 0, 0), (0, 1, 0)),
    ("cooler_stock", "A_PASTE_PRE_0"): ((0.0, 0.0, 0.0), (0, 0, -1), (0, 1, 0)),
    ("psu_450", "A_SWITCH_PSU_0"): ((0.0704, 0.0260, 0.0470), (1, 0, 0), (0, 1, 0)),
    ("psu_750", "A_SWITCH_PSU_0"): ((0.0704, 0.0260, 0.0470), (1, 0, 0), (0, 1, 0)),
}


def world_pose(pid, parent, pos, fwd, up):
    """The cap's pose in the PART frame (composes the anchor pose with the local placement)."""
    if parent == "<root>":
        return V(pos), V(fwd), V(up)
    apos, afwd, aup = PART_ANCHORS[(pid, parent)]
    R = pb.frame(afwd, aup)
    return V(apos) + R @ V(pos), R @ V(fwd), R @ V(up)


class Placed:
    """Adds geometry given in a PART's frame to a cap model whose root frame is the placement pose there."""

    def __init__(self, model, pos=(0, 0, 0), forward=(0, 0, 1), up=(0, 1, 0)):
        self.m = model
        self.R = pb.frame(forward, up)
        self.Ri = self.R.transposed()
        self.pos = V(pos)

    def add(self, tag, geo, M=None, t=(0, 0, 0)):
        M = Matrix.Identity(3) if M is None else M
        self.m.add(tag, geo, self.Ri @ M, self.Ri @ (V(t) - self.pos))

    def box(self, tag, lo, hi, bevel=0.0):
        lo, hi = V(lo), V(hi)
        self.add(tag, pb.g_box(tuple(hi - lo), bevel), None, (lo + hi) / 2)

    def pt(self, p):
        return self.Ri @ (V(p) - self.pos)

    def dir(self, d):
        return self.Ri @ V(d)


def _anchors(m, L, hit_lo, hit_hi, grip_c, grip_size, meta):
    """A_HIT_0 (the cap's bounds) and A_GRIP_0 (the pull tab: forward = the pull direction), positions given in
    the part frame through L."""
    lo, hi = L.pt(hit_lo), L.pt(hit_hi)
    cen = (lo + hi) / 2
    size = V((abs(hi.x - lo.x), abs(hi.y - lo.y), abs(hi.z - lo.z)))
    m.anchor("A_HIT_0", tuple(cen), tuple(size), meta=meta)
    m.anchor("A_GRIP_0", tuple(L.pt(grip_c)), grip_size, forward=(0, 0, 1), up=(0, 1, 0), meta="pull=+z")


def _round_corners(pts, r, n=3, which=None):
    """Fillets the listed corners (indices) of a 2D polygon with radius r."""
    out = []
    m = len(pts)
    for i in range(m):
        if which is not None and i not in which:
            out.append(pts[i])
            continue
        a, b, cc = V(pts[i - 1]), V(pts[i]), V(pts[(i + 1) % m])
        d0, d1 = (a - b).normalized(), (cc - b).normalized()
        ang = math.acos(max(-1.0, min(1.0, d0.dot(d1))))
        t = r / math.tan(ang / 2)
        p0, p1 = b + d0 * t, b + d1 * t
        bis = (d0 + d1).normalized()
        ctr = b + bis * math.sqrt(r * r + t * t)
        v0, v1 = p0 - ctr, p1 - ctr
        a0, a1 = math.atan2(v0.y, v0.x), math.atan2(v1.y, v1.x)
        da = a1 - a0
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        for k in range(n + 1):
            aa = a0 + da * k / n
            out.append((ctr.x + r * math.cos(aa), ctr.y + r * math.sin(aa)))
    return out


# ====================================================================== cap_pcie16

def build_cap_pcie16():
    """GPU frame: PCB y -0.0018..-0.0002, fingers on both faces (0.04 mm) z -0.0052..-0.0012, the edge tab
    x -0.0445..0.0445 down to z -0.0055 (0.5 mm corner chamfers), the key notch x 0.0310..0.0328 up to z -0.0003.
    The channel: 0.45 mm walls, inside 1.84 mm wide (0.08 mm clearance), floor 0.1 mm under the edge, walls up to
    z -0.0004, closed ends 0.5 mm past the tab, a key rib in the notch, a pull tab at the -x end."""
    m = pb.Model("cap_pcie16")
    L = Placed(m, (0, 0, 0), (0, 0, -1), (0, 1, 0))
    yi0, yi1 = -0.00192, -0.00008
    yo0, yo1 = -0.00237, 0.00037
    zf, zb, zt = -0.0056, -0.0061, -0.0004
    sec = [(yo0, zt), (yo0, zb), (yo1, zb), (yo1, zt), (yi1, zt), (yi1, zf), (yi0, zf), (yi0, zt)]
    sec = _round_corners(sec, 0.00035, 3, which=(1, 2))
    L.add(CLEAR, pb.g_slab(sec, [], 0.0900, -0.0450, bevel=0.00008), M_YZ)
    endc = _round_corners([(yo0, zt), (yo0, zb), (yo1, zb), (yo1, zt)], 0.00035, 3, which=(1, 2))
    for x0 in (-0.0455, 0.0450):
        L.add(CLEAR, pb.g_slab(endc, [], 0.0005, x0, bevel=0.00008), M_YZ)
    # key rib (sits in the edge's key notch, x 0.0310..0.0328)
    L.box(CLEAR, (0.0313, yi0 - 0.00005, zf - 0.00005), (0.0325, yi1 + 0.00005, -0.0042))
    # pull tab: a flat tongue off the far end, with a finger hole
    tab = pb.rrect2(-0.0489, -0.0041, 0.0072, 0.0040, 0.0012, 4)
    hole = pb.circle2(-0.0499, -0.0041, 0.0011, 16)
    L.add(CLEAR, pb.g_slab(tab, [hole], 0.0007, -0.00135, bevel=0.00008), M_XZ)
    # moulded ribs along the channel's outer bottom (stiffening, and they catch the light)
    for y in (yo0 + 0.0004, yo1 - 0.0004):
        L.box(CLEAR, (-0.0440, y - 0.00012, zb - 0.00012), (0.0440, y + 0.00012, zb + 0.00005))
    _anchors(m, L, (-0.0525, yo0, zb - 0.00012), (0.0455, yo1, zt), (-0.0489, -0.001, -0.0041), (0.0072, 0.0015, 0.0040),
             "remove=+z,travel=0.0015,part=gpu,blocks=install,edge=0.089")
    return m


# ====================================================================== port dust caps

PORT_CAPS = {
    # insert outline (snug in the shell), slot round the tongue (centre y, w, h), head outline
    "cap_dp": dict(ins=(0.01558, 0.00428, (0.00172, 0.00025, 0.00025, 0.00025)), slot=(0.0006, 0.0124, 0.0016),
                   head=(0.0175, 0.0062, (0.0022, 0.0006, 0.0006, 0.0006)), label="DP"),
    "cap_hdmi": dict(ins=(0.01378, 0.00418, (0.00142, 0.00142, 0.00017, 0.00017)), slot=(0.0, 0.0114, 0.0016),
                     head=(0.0157, 0.0061, (0.0019, 0.0019, 0.0005, 0.0005)), label="HDMI"),
}


def build_port_cap(pid):
    """Anchor frame (A_PORT_DP_n / A_PORT_HDMI_0): x along the port's width, y = the card's +y (the chamfered
    side is -y), +z out of the bracket. The shell's lip is at z +0.0002, the tongue's front at z -0.0012."""
    s = PORT_CAPS[pid]
    m = pb.Model(pid)
    w, h, ch = s["ins"]
    ins = pb.chamfer2(0.0, 0.0, w, h, ch)
    sy, sw, shh = s["slot"]
    slot = pb.rrect2(0.0, sy, sw, shh, 0.0003, 2)
    m.add("rubber", pb.g_slab(ins, [slot], 0.0057, -0.0055, bevel=0.0001))
    hw, hh, hch = s["head"]
    m.add("rubber", pb.g_slab(pb.chamfer2(0.0, 0.0, hw, hh, hch), [], 0.00115, 0.00025, bevel=0.00028))
    # the pull tab: a fin standing out of the head (x-z plane), rounded end, three grip ridges a side
    tab = [(-0.0036, 0.0012), (0.0036, 0.0012), (0.0028, 0.0058)] + \
          [(0.0028 * math.cos(a * DEG), 0.0058 + 0.0014 * math.sin(a * DEG)) for a in range(20, 180, 20)] + \
          [(-0.0028, 0.0058)]
    m.add("rubber", pb.g_slab(tab, [], 0.0009, -0.00045, bevel=0.00022), M_XZ)
    for z in (0.0034, 0.0043, 0.0052):
        for sgn in (-1, 1):
            m.add("rubber", pb.g_box((0.0046, 0.00022, 0.00035), 0.00006), None, (0.0, sgn * 0.00052, z))
    m.anchor("A_HIT_0", (0.0, 0.0, (-0.0055 + 0.0072) / 2), (hw, hh, 0.0127),
             meta=f"remove=+z,travel=0.0015,port={s['label'].lower()},blocks=plug")
    m.anchor("A_GRIP_0", (0.0, 0.0, 0.0045), (0.0072, 0.002, 0.006), meta="pull=+z")
    return m


# ====================================================================== RAM guards

def build_guard_ram(pid, notch_y):
    """RAM frame: PCB x +-0.000635 (fingers +-0.000655), y +-0.066675, bottom z 0, fingers to z 0.0035; the key
    notch 1.6 mm wide, 3.6 mm deep at y = notch_y; DDR5's PMIC starts at z 0.0035 on +x. The clip: inside 1.47 mm
    wide, 0.45 mm walls up to z 0.0034, a 0.5 mm floor, closed ends, a 2 mm gap at the notch (floor and walls up
    to z 0.0022; the walls bridge above), a pull tab at +y."""
    m = pb.Model(pid)
    L = Placed(m, (0, 0, 0), (0, 0, -1), (0, 1, 0))
    xi, xo = 0.000735, 0.001185
    zf, zb, zt = -0.0001, -0.0006, 0.0034
    sec = [(-xo, zt), (-xo, zb), (xo, zb), (xo, zt), (xi, zt), (xi, zf), (-xi, zf), (-xi, zt)]
    sec = _round_corners(sec, 0.0003, 3, which=(1, 2))
    y0, y1 = -0.0668, 0.0668
    g0, g1 = notch_y - 0.0010, notch_y + 0.0010
    for (ya, yb) in ((y0, g0), (g1, y1)):
        L.add(CLEAR, pb.g_slab(sec, [], yb - ya, ya, bevel=0.00006), M_XZ_y())
    endc = _round_corners([(-xo, zt), (-xo, zb), (xo, zb), (xo, zt)], 0.0003, 3, which=(1, 2))
    for ya in (-0.0673, 0.0668):
        L.add(CLEAR, pb.g_slab(endc, [], 0.0005, ya, bevel=0.00006), M_XZ_y())
    zg = 0.0022
    for sgn in (-1, 1):
        L.box(CLEAR, (min(sgn * xi, sgn * xo), g0 - 0.0001, zg), (max(sgn * xi, sgn * xo), g1 + 0.0001, zt))
    # pull tab off the +y end (y-z plane), with a finger hole
    tab = pb.rrect2(0.0692, 0.0010, 0.0042, 0.0032, 0.0010, 4)
    hole = pb.circle2(0.0697, 0.0010, 0.0008, 14)
    L.add(CLEAR, pb.g_slab(tab, [hole], 0.0007, -0.00035, bevel=0.00006), M_YZ)
    _anchors(m, L, (-xo, -0.0673, zb), (xo, 0.0713, zt), (0.0, 0.0692, 0.0010), (0.0015, 0.0042, 0.0032),
             f"remove=+z,travel=0.0015,part=ram,blocks=install,notch={notch_y:.4f}")
    return m


def M_XZ_y():
    """2D (x, z) extruded along +y (the RAM's length)."""
    return M_XZ


# ====================================================================== paste cap

def build_cap_paste():
    """A_PASTE_PRE_0 frame: +z = out of the cooler base (the cooler's -z), x = the cooler's -x. The copper face is
    at z 0 (r 17.5 mm); the paste square 28 x 28 mm (corners reach r 18.8 mm) stands 0.18 mm proud; the aluminium
    ring round the copper is recessed 0.4 mm (z -0.0004, r 17.5..20.5 mm) and the fins' bottoms are at z -0.001.
    The cap: a squircle dome (inside 2.7 mm high, 40.8 mm across), a flange r 20.4..23.4 mm at z -0.0003..+0.0002,
    a pull tab towards the cooler's +x."""
    m = pb.Model("cap_paste")
    p = 4.0
    n = 9
    inner, outer = [], []
    for k in range(n + 1):
        t = (90.0 - 90.0 * k / n) * DEG  # from the top (90) down to the rim (0)
        cs, sn = max(0.0, math.cos(t)), max(0.0, math.sin(t))
        inner.append((0.0204 * cs ** (2 / p), -0.0003 + 0.0030 * sn ** (2 / p)))
        outer.append((0.0212 * cs ** (2 / p), 0.0002 + 0.0029 * sn ** (2 / p)))
    prof = inner + [(0.0234, -0.0003), (0.0234, 0.0002)] + list(reversed(outer))
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    m.add(CLEAR, pb.g_lathe(prof, 40))
    tab = pb.rrect2(-0.0264, 0.0, 0.0076, 0.0080, 0.0016, 4)
    hole = pb.circle2(-0.0272, 0.0, 0.0012, 16)
    m.add(CLEAR, pb.g_slab(tab, [hole], 0.0005, -0.0003, bevel=0.00008))
    m.anchor("A_HIT_0", (0.0, 0.0, 0.0014), (0.047, 0.047, 0.0034), meta="remove=+z,travel=0.0015,blocks=install")
    m.anchor("A_GRIP_0", (-0.0264, 0.0, 0.0), (0.0076, 0.008, 0.0015), meta="pull=+z")
    return m


# ====================================================================== PSU voltage sticker

def sticker_texture():
    W, H = 768, 486
    cv = pb.Canvas(W, H, bg="#ffd21f")
    cv.frame_rect(10, 10, W - 20, H - 20, 12, "#141414", r=26)
    # warning triangle
    tx, ty, ts = 150, 205, 210
    cv.poly([(tx, ty - ts * 0.55), (tx + ts * 0.55, ty + ts * 0.42), (tx - ts * 0.55, ty + ts * 0.42)], "#141414")
    cv.poly([(tx, ty - ts * 0.38), (tx + ts * 0.40, ty + ts * 0.33), (tx - ts * 0.40, ty + ts * 0.33)], "#ffd21f")
    cv.rect(tx - 10, ty - 30, 20, 80, "#141414", r=6)
    cv.circle(tx, ty + 72, 12, "#141414")
    cv.text("CHECK VOLTAGE", 290, 112, 44, "#141414", "arialb", "left", "center", maxw=440)
    cv.text("115V / 230V", 290, 215, 74, "#141414", "black", "left", "center", maxw=440)
    cv.text("BEFORE USE", 290, 316, 44, "#141414", "arialb", "left", "center", maxw=440)
    cv.rect(40, 368, W - 80, 6, "#141414")
    cv.text("Set the correct mains voltage before switching on.  Remove this label after checking.",
            W / 2, 410, 17, "#141414", "arial", "center", "center", maxw=W - 90)
    cv.text("VERIFIER LA TENSION  -  SPANNUNG PRUFEN  -  COMPROBAR TENSION", W / 2, 444, 15, "#141414", "arialb",
            "center", "center", maxw=W - 90)
    cv.render("sticker_psu")


def _rrect_inside(x, y, w, h, r):
    dx, dy = abs(x) - (w / 2 - r), abs(y) - (h / 2 - r)
    if dx <= 0 or dy <= 0:
        return abs(x) <= w / 2 and abs(y) <= h / 2
    return dx * dx + dy * dy <= r * r


_ROCKER = {}


def _rocker_profile(off_deg, marks):
    """The rocker's top line in the anchor frame after tilting it off_deg about +y: ([x], [z]) sorted by x.
    marks: include the raised I / O marks (0.2 mm, on both halves at x = -+4.5 mm)."""
    key = (off_deg, marks)
    if key not in _ROCKER:
        th = off_deg * DEG
        pts = []
        for k in range(161):
            x0 = -0.00875 + 0.0175 * k / 160
            z0 = 0.0026 - 0.0014 * abs(x0) / 0.00875
            if marks and abs(abs(x0) - 0.0045) <= 0.0023:
                z0 += 0.00025
            pts.append((x0 * math.cos(th) + z0 * math.sin(th), -x0 * math.sin(th) + z0 * math.cos(th)))
        pts.sort()
        _ROCKER[key] = ([p[0] for p in pts], [p[1] for p in pts])
    return _ROCKER[key]


def psu_rear_height(x, y, off_deg=9.0):
    """Height (anchor-local z) of the PSU's rear surface under the sticker, in A_SWITCH_PSU_0's frame
    (x = the PSU's -z, y = up, z = out of the rear face, origin 0.4 mm out of the face): the face plate (z -0.0004),
    the switch bezel ring (21.5 x 15.5, top z +0.0012), the rocker with its I/O marks in its OFF pose (rotated
    off_deg about +y, the game's PsuSwitch offAngle), the hollow round the rocker (deep)."""
    import bisect
    hz = -0.0004
    if _rrect_inside(x, y, 0.0215, 0.0155, 0.0010):
        hz = 0.0012
        if _rrect_inside(x, y, 0.0183, 0.0123, 0.0006):
            hz = -0.0034
            if abs(y) <= 0.00575:
                xs_, zs_ = _rocker_profile(off_deg, abs(y) <= 0.0028)
                if xs_[0] <= x <= xs_[-1]:
                    k = max(1, min(len(xs_) - 1, bisect.bisect_left(xs_, x)))
                    xa, xb, za, zb = xs_[k - 1], xs_[k], zs_[k - 1], zs_[k]
                    t = 0.0 if xb - xa < 1e-12 else (x - xa) / (xb - xa)
                    hz = max(hz, za + (zb - za) * t, za, zb)
    return hz


def build_sticker_psu_voltage(W=0.030, H=0.019, yc=0.0005, gx=41, gy=26):
    """A 30 x 19 mm label in A_SWITCH_PSU_0's frame, draped like a sticky membrane: it lies on the face plate,
    climbs the bezel and bridges over the rocker (pressed in on the O side, as shipped)."""
    sticker_texture()
    m = pb.Model("sticker_psu_voltage")
    xs = [W / 2 - W * i / (gx - 1) for i in range(gx)]          # +x .. -x (reading right = -x)
    ys = [yc - H / 2 + H * j / (gy - 1) for j in range(gy)]
    # obstacle field: the max height within each vertex's cell (sampled finely), then a membrane relaxation
    dx, dy = W / (gx - 1), H / (gy - 1)
    Hf = [[-1.0] * gx for _ in range(gy)]
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            best = -1.0
            for a in (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0):
                for b in (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0):
                    best = max(best, psu_rear_height(x + a * dx, y + b * dy))
            Hf[j][i] = best
    # dilate by one cell, then blur with a 3x3 binomial kernel: still >= the obstacles, but without stair steps
    Hd = [[max(Hf[b][a] for b in range(max(0, j - 1), min(gy, j + 2)) for a in range(max(0, i - 1), min(gx, i + 2)))
           for i in range(gx)] for j in range(gy)]
    wk = (1.0, 2.0, 1.0)
    Hf = [[sum(wk[b - j + 1] * wk[a - i + 1] * Hd[b][a] for b in range(max(0, j - 1), min(gy, j + 2))
               for a in range(max(0, i - 1), min(gx, i + 2))) /
           sum(wk[b - j + 1] * wk[a - i + 1] for b in range(max(0, j - 1), min(gy, j + 2))
               for a in range(max(0, i - 1), min(gx, i + 2)))
           for i in range(gx)] for j in range(gy)]
    h = [row[:] for row in Hf]
    kappa = 0.00030 * (dx / 0.001) ** 2
    for it in range(400):
        nh = [row[:] for row in h]
        for j in range(gy):
            for i in range(gx):
                nb = []
                for (a, b) in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                    if 0 <= a < gx and 0 <= b < gy:
                        nb.append(h[b][a])
                avg = sum(nb) / len(nb)
                nh[j][i] = max(Hf[j][i], avg - kappa)
        h = nh
    off = 0.00008
    sh = xc.Sheet()
    P = [[V((xs[i], ys[j], h[j][i] + off)) for i in range(gx)] for j in range(gy)]

    def uv(i, j):
        return ((W / 2 - xs[i]) / W, (ys[j] - (yc - H / 2)) / H)

    xc.grid_strip(sh, "tex_sticker_psu", P, lambda i, j: (0, 0, 1), lambda i, j: uv(j, i), smooth=True)
    # the thin edges (0.08 mm label stock), mapped to the yellow border colour
    t = 0.00006
    yel = (0.5, 0.012)
    for j in (0, gy - 1):
        for i in range(gx - 1):
            a, b = P[j][i], P[j][i + 1]
            sh.add("tex_sticker_psu", [a, b, b - V((0, 0, t)), a - V((0, 0, t))], (0, -1 if j == 0 else 1, 0),
                   [yel] * 4)
    for i in (0, gx - 1):
        for j in range(gy - 1):
            a, b = P[j][i], P[j + 1][i]
            sh.add("tex_sticker_psu", [a, b, b - V((0, 0, t)), a - V((0, 0, t))], (1 if i == 0 else -1, 0, 0),
                   [yel] * 4)
    sh.flush(m)
    zmax = max(max(r) for r in h) + off
    m.anchor("A_HIT_0", (0.0, yc, (zmax - 0.0004) / 2), (W, H, zmax + 0.0004),
             meta=f"peel=film,label=check_voltage,w={W:.3f},h={H:.3f},pose=off")
    m.anchor("A_GRIP_0", (W / 2 - 0.002, yc - H / 2 + 0.002, 0.0), (0.004, 0.004, 0.001), forward=(0, 0, 1),
             up=(0, 1, 0), meta="peel_from=+x-y")
    return m
