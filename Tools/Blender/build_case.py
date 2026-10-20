"""
Mid-tower cases: case_brickhouse (budget, black, solid front, one rear fan) and case_breeze (white, mesh front,
three front fans plus one rear, ARGB).

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_case.py -- [case_brickhouse] [case_breeze]

Other scripts add cases by putting a style into STYLES (build_parts_d.py adds case_aero). Optional style keys, absent
on brickhouse and breeze: front="glass" (a panoramic glass front that meets the side glass without a corner pillar,
black top and base strips), fans_bottom / bottom_fan_d / BOTTOM_FANS (intake fans lying on the PSU shroud, numbered
after the rear fan, their plugs resting where the front fans' plugs rest), code / sn (the rear label).
Optional hooks (build_cat_cases.py uses them; absent on brickhouse, breeze and aero): front_fans = [(y, d), ...] (the
front intake fans' heights and sizes, instead of the three 120 mm fans at FRONT_FANS_Y), and callables that get a
namespace of build()'s locals: front_wall(ns, holes) -> holes (the front wall's cut-outs), face(ns) (draws the front
face's decoration instead of the mesh insert / inlay), feet(ns) (instead of the four feet), extra(ns) (more looks,
called before the hitboxes).

Frame (as PartFactory.BuildCase): origin at the bottom centre, 0.42 (x) x 0.45 (y) x 0.21 (z); -x is the front,
+x the rear, the window faces +z, the motherboard tray faces +z at z ~ -0.095, the PSU bay is bottom rear.
The feet reach 8 mm below the origin, as today.

Real ATX geometry (ATX 2.2 figure 3, board frame = origin at the PCB centre, +x rear, +y top):
  board pose A_SOCKET_MOBO_0 = (0.068, 0.2675, -0.0885) facing +z; standoffs 6.35 mm tall on the tray at
  z = -0.09485; the nine ATX holes A C F G H J K L M; the rear I/O window (158.75 x 44.45 mm, its bottom 3.81 mm
  below the top of the PCB); seven expansion slots at 20.32 mm pitch, aligned so that slot 2 (the third from the
  top) carries the board's x16 slot at board y -0.045 (as today); the slot screws and the bracket tab rail match
  build_gpu.py (tab top 0.1065 above the PCIe contact, screws 0.1015 behind it, slot centres -0.0069 / -0.0272).
"""
import math
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import build_plugs as BP  # noqa: E402

try:
    import parts_fan as PF  # the shared fan (another modeller's module)
except Exception as e:  # pragma: no cover
    PF = None
    print("parts_fan not importable, building case fans locally:", e)

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ
T = 0.0008     # sheet steel
R = 0.0010     # inner bend radius

# chassis planes
XF = -0.2005   # front wall, outer face
XR = 0.1963    # rear wall, outer face (the PSU, I/O shield and slot brackets sit against its inside)
XRI = XR - T
ZG = 0.1000    # +z frame plane the glass rests on
ZBK = -0.1042  # -z frame plane the back panel rests on
YT = 0.45

# motherboard
MB = (0.068, 0.2675, -0.0885)
Z_TRAY = MB[2] - 0.00635       # tray front surface (standoff height 1/4")
ATX_IN = 0.0254
ATX_HOLES = {  # ATX 2.2 figure 3: (h along the 12" edge from datum A, v towards the front edge), inches
    "A": (0.0, 0.0), "C": (4.9, 0.0), "F": (11.1, 0.9), "G": (0.0, 6.1), "H": (4.9, 6.1), "J": (11.1, 6.1),
    "K": (0.0, 8.95), "L": (4.9, 8.95), "M": (11.1, 8.95), "B": (3.1, 0.0)}
ATX_ORDER = ["A", "C", "F", "G", "H", "J", "K", "L", "M"]
PRE = {"A": 1, "C": 1, "F": 1, "H": 1, "K": 1, "M": 1, "G": 0, "J": 0, "L": 0, "B": 0}


def hole_board(letter):
    """An ATX hole in the board frame (metres): x = (4.4 - v)", y = (h - 5.35)"."""
    h, v = ATX_HOLES[letter]
    return ((4.4 - v) * ATX_IN, (h - 5.35) * ATX_IN)


def hole_case(letter):
    bx, by = hole_board(letter)
    return (MB[0] + bx, MB[1] + by)


# expansion slots: slot k (0 = top), 20.32 mm pitch, slot 2 carries the x16 card. The card origin is the board's
# A_SOCKET_PCIE16_0 (build_board.py: board (0.030, -0.0427, 0.0121)); the bracket's slot centres, tab and screws
# come from build_gpu.py (SLOT_Y -0.0069 / -0.0272, Z_TAB 0.1065, X_SCREW 0.1015, bracket plate x 0.0955..0.0965).
SLOT_PITCH = 0.02032
CARD = (0.030, -0.0427, 0.0121)
SLOT_Y = [MB[1] + CARD[1] - 0.0069 - SLOT_PITCH * (k - 2) for k in range(7)]
TAB_Z = MB[2] + CARD[2] + 0.1065     # top of the bracket tabs
SCREW_X = MB[0] + CARD[0] + 0.1015
COVER_X = MB[0] + CARD[0] + 0.0960

# rear I/O window (ATX), trimmed 2.4 mm at the slot end so the top slot cover clears it
IO_Z0 = MB[2] + 0.0016 - 0.00381
IO_Z1 = IO_Z0 + 0.04445
IO_Y0 = MB[1] + (5.196 - 5.35) * ATX_IN
IO_Y1 = MB[1] + (11.446 - 5.35) * ATX_IN
IO_YC = MB[1] + ((5.196 + 11.446) / 2 - 5.35) * ATX_IN   # the ATX window centre (the shield is made for it)

# PSU (build_psu: origin at the box centre, rear face at +x, screws (z, y) on the rear face)
PSU = (0.125, 0.053, 0.0)
PSU_SCREWS = [(-0.069, 0.037), (0.069, 0.037), (-0.069, -0.037), (0.045, -0.027)]

# where the loose front-panel plugs rest on the tray (contact end up, cables towards the bottom grommet)
FP_POS = {"fp_pwrsw": (-0.150, 0.215), "fp_reset": (-0.1385, 0.217), "fp_pled": (-0.127, 0.219), "fp_hddled": (-0.1155, 0.221),
          "usb3hdr": (-0.104, 0.232), "audiohdr": (-0.152, 0.262)}

# fans
REAR_FAN = (XRI - 0.0128, 0.355, 0.030)
FRONT_FANS_Y = [0.352, 0.230, 0.108]
# bottom intake fans (style fans_bottom): (x, z) centres on the PSU shroud top, behind the 2.5" sled on the shroud
BOTTOM_FANS = [(-0.042, 0.004), (0.052, 0.004), (0.146, 0.004)]

STYLES = {
    "case_brickhouse": dict(
        brand="BRICKHOUSE", model="M1", paint="paint_black", trim="dark_plastic", bezel="dark_plastic",
        cover_tag="paint_black", screw_tag="steel_dark", logo_tag="alu", logo_font="ariblk.ttf",
        shroud_logo_tag="alu", front="solid", fans_front=0, fan_tag="fan_black", fan_rgb=False, fan_pins=3,
        hub=("BRICKHOUSE", "#121214", "#e8e8ea", "#d0602a"), thumb_tag="steel_dark", led_power="led_blue",
        label_bg=(0.93, 0.93, 0.9)),
    "case_breeze": dict(
        brand="BREEZE", model="AIR 400 MESH", paint="paint_white", trim="white_plastic", bezel="white_plastic",
        cover_tag="paint_white", screw_tag="steel", logo_tag="grey_plastic", logo_font="seguisb.ttf",
        shroud_logo_tag="paint_black", front="mesh", fans_front=3, fan_tag="white_plastic", fan_rgb=True, fan_pins=4,
        hub=("BREEZE", "#e9e9e7", "#2a2c30", "#8fb7e8"), thumb_tag="steel_dark", led_power="led_white",
        label_bg=(0.96, 0.96, 0.95)),
}


# ---------------------------------------------------------------- helpers

ROOT = [None]   # the model being built (sheets and flanges default to it)


def sheet(name, tag, o, a, b, outline, holes=(), t=T, parent=None, **kw):
    return P.slab(name, outline, t, tag, P.plane(o, a, b), holes=holes, parent=parent or ROOT[0], **kw)


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rr(x0, x1, y0, y1, r=0.0, seg=4):
    return P.rrect(x1 - x0, y1 - y0, r, (x0 + x1) / 2, (y0 + y1) / 2, seg)


def flange(name, tag, o, a, b, path, length, parent=None):
    """A bent sheet edge: path (centreline, sharp corners) in the (a, b) plane through o, swept along a x b."""
    return P.bent(name, path, T, length, tag, P.plane(o, a, b), r_inner=R, parent=parent or ROOT[0])


def textures(cid, st):
    files = {}
    # rear label sticker
    art = P.Art(512, 320, bg=st["label_bg"], name="case_label")
    ink = (0.08, 0.08, 0.09)
    art.text(st["brand"], 24, 262, 46, ink, st["logo_font"], maxw=330)
    art.text("MODEL: " + st.get("code", "BH-M1" if "brick" in cid else "BZ-A400M"), 24, 214, 26, ink, "arialbd.ttf")
    art.text("ATX MID-TOWER CASE", 24, 182, 22, ink, "arial.ttf")
    art.code128ish(P.shash(cid) & 0xffff, 24, 92, 300, 64, ink)
    art.text("S/N  " + st.get("sn", "BH1" if "brick" in cid else "BZ4") + "2610190427", 24, 64, 22, ink, "consola.ttf")
    art.text("MADE IN CHINA", 24, 26, 20, ink, "arial.ttf")
    art.rect(360, 140, 128, 128, ink)
    art.text("CE", 424, 204, 70, st["label_bg"], "arial.ttf", align="CENTER", valign="CENTER")
    art.text("\u267b", 424, 70, 80, ink, "seguisym.ttf", align="CENTER", valign="CENTER")
    files["label"] = art.render(cid + "_label")
    art.dispose()
    if st["front"] == "mesh":
        files["mesh"] = mesh_texture(cid + "_mesh")
    # fan hub sticker and motor label (shared fan module helpers)
    if PF is not None:
        try:
            b, bg, fg, ac = st["hub"]
            PF.hub_sticker_texture(cid + "_fanhub", b, None, bg, fg, ac)
            PF.motor_label_texture(cid + "_fanmotor", b, "DC 12V 0.18A")
            files["hub"] = cid + "_fanhub"
            files["motor"] = cid + "_fanmotor"
        except Exception as e:
            print("fan textures failed", e)
    return files


def mesh_texture(file, w=1024, h=2048, panel=(0.176, 0.372)):
    """A white hex-perforated front mesh (real scale: 3.6 mm hexes on a 4.2 mm pitch). Holes are alpha 0
    with a dark colour, so it also reads right if drawn opaque."""
    import numpy as np
    pw, ph = panel
    pitch = 0.0042
    rr_ = 0.00175  # hex inradius
    px_per_m = w / pw
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X_ = (xx + 0.5) / px_per_m
    Y_ = (yy + 0.5) / (h / ph)
    dy = pitch * math.sqrt(3) / 2
    row = np.floor(Y_ / dy + 0.5)
    cy = row * dy
    off = (row % 2) * pitch / 2
    cx = np.floor((X_ - off) / pitch + 0.5) * pitch + off
    # also test the neighbour rows (hex tiling)
    best = np.full(X_.shape, 1e9, dtype=np.float32)
    for drow in (-1, 0, 1):
        r2 = row + drow
        cy2 = r2 * dy
        off2 = (r2 % 2) * pitch / 2
        cx2 = np.floor((X_ - off2) / pitch + 0.5) * pitch + off2
        ddx, ddy = np.abs(X_ - cx2), np.abs(Y_ - cy2)
        # hex distance (pointy side along y): max(|x|, |x|/2 + |y|*sqrt3/2)
        d = np.maximum(ddy, ddy * 0.5 + ddx * math.sqrt(3) / 2)
        best = np.minimum(best, d)
    hole = best < rr_
    edge = np.clip((best - rr_) / (0.00025), 0, 1)
    arr = np.zeros((h, w, 4), dtype=np.float32)
    web = np.array([0.86, 0.86, 0.84])
    shade = 0.82 + 0.18 * edge  # a soft bevel towards each hole
    for k in range(3):
        arr[..., k] = np.where(hole, 0.07, web[k] * shade)
    arr[..., 3] = np.where(hole, 0.0, 1.0)
    # a solid border (the frame of the insert)
    b = int(0.0025 * px_per_m)
    arr[:b, :, :3] = web
    arr[-b:, :, :3] = web
    arr[:, :b, :3] = web
    arr[:, -b:, :3] = web
    arr[:b, :, 3] = arr[-b:, :, 3] = 1
    arr[:, :b, 3] = arr[:, -b:, 3] = 1
    return P.save_png(arr, file)


def power_icon(name, fr, r, w, tag, parent, depth=0.00012, z=0.0):
    """The IEC power symbol: a broken ring with a bar through the gap, raised on the frame's XY plane."""
    pts_o = P.arc(0, 0, r, math.radians(120), math.radians(420), 24)
    pts_i = P.arc(0, 0, r - w, math.radians(420), math.radians(120), 24)
    P.slab(name, pts_o + pts_i, depth, tag, fr.sub(0, 0, z + depth / 2), parent=parent)
    P.slab(name, P.rrect(w, r * 1.15, w * 0.45, 0, r * 0.45), depth, tag, fr.sub(0, 0, z + depth / 2), parent=parent)


# ---------------------------------------------------------------- the build

def build(cid):
    st = STYLES[cid]
    P.reset()
    root = c.root(cid)
    ROOT[0] = root
    paint = st["paint"]
    tex = textures(cid, st)
    breeze = st["front"] == "mesh"
    glass = st["front"] == "glass"
    n_bottom = st.get("fans_bottom", 0)
    bfd = st.get("bottom_fan_d", 0.092)
    xm = (XF + XR) / 2
    Lx = XR - XF
    ffans = st.get("front_fans")     # [(y, d)] custom front fans (hook), else the 120 mm FRONT_FANS_Y

    # ---------------- bottom panel: PSU intake slots, flanges up both sides
    holes = [P.stadium(0.112, 0.0055, 0.126, -0.052 + 0.013 * k) for k in range(9)]
    holes += [P.circle(0.0021, x, z, 12) for x in (-0.175, 0.16) for z in (-0.08, 0.08)]  # feet screws
    if n_bottom:
        holes += P.hex_grid(lambda a, b, r_: -0.168 < a < 0.046 and -0.060 < b < 0.060, 0.0090, 0.0036, -0.170, 0.048, -0.062, 0.062)
    sheet("bottom", paint, (0, T / 2, 0), X, Z, rect(XF, XR, ZBK + R + T, ZG - R - T), holes)
    for zedge, sgn in ((ZG, 1), (ZBK, -1)):
        zc = zedge - sgn * T / 2
        flange("bottom_fl", paint, (xm, 0, 0), Z, Y, [(zc - sgn * 0.004, T / 2), (zc, T / 2), (zc, 0.014)], Lx - 0.002)

    # ---------------- top panel: big vent under a magnetic dust filter
    vent = rr(-0.165, 0.125, -0.074, 0.074, 0.008)
    sheet("top", paint, (0, YT - T / 2, 0), X, Z, rect(XF, XR, ZBK + R + T, ZG - R - T), [vent])
    for zedge, sgn in ((ZG, 1), (ZBK, -1)):
        zc = zedge - sgn * T / 2
        flange("top_fl", paint, (xm, 0, 0), Z, Y, [(zc - sgn * 0.004, YT - T / 2), (zc, YT - T / 2), (zc, YT - 0.014)], Lx - 0.002)
    # magnetic filter: rubber-magnet frame and the mesh
    fo = rr(-0.169, 0.129, -0.078, 0.078, 0.009)
    sheet("top_filter_frame", "rubber", (0, YT + 0.0006, 0), X, Z, fo, [rr(-0.163, 0.123, -0.072, 0.072, 0.006)], t=0.0012)
    sheet("top_filter_mesh", "mesh_black", (0, YT + 0.0004, 0), X, Z, rr(-0.164, 0.124, -0.073, 0.073, 0.006), t=0.0004)
    P.cube("top_filter_tab", (0.135, YT + 0.0006, 0.0), (0.012, 0.0012, 0.03), "rubber", parent=root, bevel=0.0004)

    # ---------------- front wall
    if glass:
        fh = [rr(-0.086, 0.086, 0.020, 0.406, 0.012)]    # open behind the front glass
    elif breeze:
        fh = [rr(-0.058, 0.058, 0.050, 0.410, 0.010)]
        for yf in FRONT_FANS_Y:
            fh += [P.circle(0.0022, sz * 0.0525, yf + sy * 0.0525, 12) for sz in (-1, 1) for sy in (-1, 1)]
    else:
        fh = []
        for yf in (0.29, 0.165):
            fh += P.hex_grid(lambda a, b, r_, yf=yf: a * a + (b - yf) ** 2 < 0.054 ** 2, 0.0078, 0.0034, -0.06, 0.06, yf - 0.06, yf + 0.06)
            fh += [P.circle(0.0022, sz * 0.0525, yf + sy * 0.0525, 12) for sz in (-1, 1) for sy in (-1, 1)]
    fh += [rr(-0.030, 0.030, 0.416, 0.441, 0.004)]  # front I/O cables
    fh += [rr(z - 0.004, z + 0.004, y - 0.0025, y + 0.0025, 0.001) for z in (-0.092, 0.088) for y in (0.06, 0.225, 0.39)]  # bezel clips
    if st.get("front_wall"):
        fh = st["front_wall"](types.SimpleNamespace(**locals()), fh)
    sheet("front", paint, (XF + T / 2, 0, 0), Z, Y, rect(ZBK + R + T, ZG - R - T, T, YT - T), fh)
    for zedge, sgn in ((ZG, 1), (ZBK, -1)):
        zc = zedge - sgn * T / 2
        flange("front_fl", paint, (0, YT / 2, 0), Z, X, [(zc - sgn * 0.004, XF + T / 2), (zc, XF + T / 2), (zc, XF + 0.016)], YT - 2 * T - 0.002)

    # ---------------- rear wall: I/O window, fan grille, slot openings, PSU opening
    rh = [rr(IO_Z0, IO_Z1, IO_Y0, IO_Y1, 0.0006)]
    fz, fy = REAR_FAN[2], REAR_FAN[1]
    rh += P.hex_grid(lambda a, b, r_: (a - fz) ** 2 + (b - fy) ** 2 < 0.0565 ** 2, 0.0068, 0.0030,
                     fz - 0.06, fz + 0.06, fy - 0.06, fy + 0.06)
    rh += [P.stadium(0.0046, 0.012, fz + sz * 0.0525, fy + sy * 0.0525) for sz in (-1, 1) for sy in (-1, 1)]
    for k, y in enumerate(SLOT_Y):
        top = min(y + 0.0071, IO_Y0 - 0.003)   # the top slot is trimmed where it meets the I/O window
        rh.append(rr(-0.0835, TAB_Z + 0.0006, y - 0.0071, top, 0.001))
    pz0, pz1, py0, py1 = -0.064, 0.064, PSU[1] - 0.0335, PSU[1] + 0.0335
    tz, ty = PSU_SCREWS[3][0], PSU[1] + PSU_SCREWS[3][1]
    psu_open = [(pz0, py0), (tz - 0.008, py0), (tz - 0.008, ty + 0.0075), (tz + 0.008, ty + 0.0075), (tz + 0.008, py0),
                (pz1, py0), (pz1, py1), (pz0, py1)]
    rh.append(psu_open)
    rh += [P.circle(0.0018, PSU[2] + z, PSU[1] + y, 14) for (z, y) in PSU_SCREWS]
    rh += [P.circle(0.0017, -0.1, y, 12) for y in (0.06, 0.39)]  # back panel thumbscrews
    sheet("rear", paint, (XR - T / 2, 0, 0), Z, Y, rect(ZBK + R + T, ZG - R - T, T, YT - T), rh)
    for zedge, sgn in ((ZG, 1), (ZBK, -1)):
        zc = zedge - sgn * T / 2
        flange("rear_fl", paint, (0, YT / 2, 0), Z, X, [(zc - sgn * 0.004, XR - T / 2), (zc, XR - T / 2), (zc, XR - 0.016)], YT - 2 * T - 0.002)
    # PEM nuts on the +z rear flange for the glass thumbscrews
    for y in (0.03, 0.42):
        P.cylinder("pem", P.Frame((0.1885, y, ZG - T - 0.0015), NZ, Y), 0.0034, 0.003, "steel", 6, root, z0=-0.0015, smooth=None)

    # slot rail outside the rear wall: the bracket tabs rest on it, screws go in along -z
    rail_holes = [P.circle(0.0014, SCREW_X, y, 12) for y in SLOT_Y]
    ry0, ry1 = SLOT_Y[6] - 0.012, SLOT_Y[0] + 0.012
    sheet("slot_rail", paint, (0, 0, TAB_Z - 0.001 - T / 2), X, Y, rect(XR - 0.0006, XR + 0.0085, ry0, ry1), rail_holes)
    flange("slot_rail_lip", paint, (0, (ry0 + ry1) / 2, 0), X, Z,
           [(XR + 0.006, TAB_Z - 0.001 - T / 2), (XR + 0.0092, TAB_Z - 0.001 - T / 2), (XR + 0.0092, TAB_Z - 0.0085)], ry1 - ry0)
    for y in (ry0 + 0.002, ry1 - 0.002):
        P.cube("slot_rail_gusset", (XR + 0.0045, y, TAB_Z - 0.006), (0.009, T, 0.009), paint, parent=root)
    # threaded inserts under the rail
    for y in SLOT_Y:
        P.cylinder("rail_nut", P.Frame((SCREW_X, y, TAB_Z - 0.001 - T - 0.0012), Z, X), 0.0028, 0.0024, "steel", 6, root, smooth=None)

    # ---------------- motherboard tray
    th = [rr(0.042, 0.150, 0.274, 0.402, 0.008)]                    # CPU cooler cut-out
    GROM = []
    for y in (0.335, 0.250, 0.165):                                  # front column, beside the board edge
        GROM.append(("tray", (-0.077, y), (0.020, 0.060)))
    GROM.append(("tray", (0.032, 0.4345), (0.064, 0.016)))           # top: EPS
    for (x, y), (w, h) in [(g[1], g[2]) for g in GROM]:
        th.append(rr(x - w / 2, x + w / 2, y - h / 2, y + h / 2, min(w, h) * 0.45))
    for L_ in list(ATX_HOLES):
        hx, hy = hole_case(L_)
        th.append(P.circle(0.0016, hx, hy, 12))
    for (x, y) in [(-0.12, 0.40), (-0.12, 0.30), (-0.12, 0.20), (-0.035, 0.433), (0.12, 0.433), (-0.03, 0.125)]:
        th += [rr(x - 0.0035, x - 0.0010, y - 0.002, y + 0.002, 0.0006), rr(x + 0.0010, x + 0.0035, y - 0.002, y + 0.002, 0.0006)]
    tray_x0 = -0.168
    sheet("tray", paint, (0, 0, Z_TRAY - T / 2), X, Y, rect(tray_x0 + R + T, XRI, 0.1044, YT - T), th)
    flange("tray_fl", paint, (0, (0.1044 + YT - T) / 2, 0), X, Z,
           [(tray_x0 + 0.005, Z_TRAY - T / 2), (tray_x0 + T / 2, Z_TRAY - T / 2), (tray_x0 + T / 2, ZBK + 0.0012)], YT - T - 0.1044)
    # embossed rings round the standoff holes (the extruded threads)
    for L_ in list(ATX_HOLES):
        hx, hy = hole_case(L_)
        P.lathe("emboss", [(0.0016, Z_TRAY - 0.0001), (0.0034, Z_TRAY - 0.0001), (0.0030, Z_TRAY + 0.0005), (0.0016, Z_TRAY + 0.0005)],
                paint, P.Frame((hx, hy, 0), Z, Y), 16, root, smooth=None)
    # tie-down bridges over the slot pairs
    for (x, y) in [(-0.12, 0.40), (-0.12, 0.30), (-0.12, 0.20), (-0.035, 0.433), (0.12, 0.433), (-0.03, 0.125)]:
        P.cube("tie_bridge", (x, y, Z_TRAY + 0.0006), (0.0026, 0.004, 0.0006), paint, parent=root)

    # ---------------- PSU shroud
    sx0 = -0.172
    YS = 0.1036     # shroud top mid-plane
    ZS = 0.0979     # shroud side mid-plane
    sh = []
    GROM.append(("shroud", (-0.100, -0.0835), (0.050, 0.016)))
    GROM.append(("shroud", (0.065, -0.0835), (0.050, 0.016)))
    for g in GROM[-2:]:
        (x, z), (w, h) = g[1], g[2]
        sh.append(rr(x - w / 2, x + w / 2, z - h / 2, z + h / 2, h * 0.45))
    if n_bottom:
        for (fx, fz_) in BOTTOM_FANS[:n_bottom]:
            sh.append(P.circle(bfd / 2 - 0.0015, fx, fz_, 48))
            sh += [P.circle(0.0021, fx + sx_ * (bfd / 2 - 0.0048), fz_ + sz_ * (bfd / 2 - 0.0048), 10) for sx_ in (-1, 1) for sz_ in (-1, 1)]
    else:
        sh += P.hex_grid(lambda a, b, r_: 0.03 < a < 0.172 and -0.06 < b < 0.075, 0.0075, 0.0032, 0.03, 0.175, -0.065, 0.08)
    sh += [P.circle(0.0016, x, z, 10) for x in (-0.148, -0.112) for z in (-0.060, 0.024)]  # SSD bracket screws
    sheet("shroud_top", paint, (0, YS, 0), X, Z, rect(sx0 + 0.0018, XRI, Z_TRAY - T, ZS - 0.0018), sh)
    shf = [P.stadium(0.15, 0.0042, 0.0, 0.025 + 0.011 * k) for k in range(6)] if (breeze or glass) else []
    sheet("shroud_front", paint, (sx0 + T / 2, 0, 0), Z, Y, rect(Z_TRAY - T, ZS - 0.0018, T, YS - 0.0018), shf)
    win = rr(0.088, 0.168, 0.026, 0.082, 0.008)  # shows the PSU's label
    sheet("shroud_side", paint, (0, 0, ZS), X, Y, rect(sx0 + 0.0018, XRI, T, YS - 0.0018), [win])
    flange("shroud_bend", paint, (0.5 * (sx0 + XRI), 0, 0), Z, Y, [(ZS - 0.003, YS), (ZS, YS), (ZS, YS - 0.003)], XRI - sx0 - 0.002)
    flange("shroud_bend", paint, (0, 0, 0.5 * (Z_TRAY + ZS)), X, Y, [(sx0 + 0.003, YS), (sx0 + T / 2, YS), (sx0 + T / 2, YS - 0.003)],
           ZS - Z_TRAY - 0.002)
    flange("shroud_bend", paint, (0, YS / 2, 0), X, Z, [(sx0 + 0.003, ZS), (sx0 + T / 2, ZS), (sx0 + T / 2, ZS - 0.003)], YS - 0.004)
    P.text3d("shroud_logo", st["brand"], 0.016, 0.0004, st["shroud_logo_tag"], P.Frame((-0.065, 0.052, ZS + T / 2), Z, Y),
             st["logo_font"], parent=root, width=0.13)
    # PSU support rails with rubber pads
    for z in (-0.056, 0.056):
        P.cube("psu_rail", (0.125, (T + PSU[1] - 0.043) / 2, z), (0.13, PSU[1] - 0.043 - T - 0.001, 0.012), paint, parent=root)
        P.cube("psu_pad", (0.125, PSU[1] - 0.043 - 0.0005, z), (0.12, 0.001, 0.011), "rubber", parent=root)

    # ---------------- feet and the PSU dust filter
    for x in ((-0.175, 0.16) if not st.get("feet") else ()):
        for z in (-0.08, 0.08):
            P.slab("foot", P.rrect(0.046, 0.022, 0.006), 0.0055, "black_plastic", P.plane((x, -0.00275, z), X, Z), parent=root)
            P.slab("foot_pad", P.rrect(0.040, 0.017, 0.005), 0.0025, "rubber", P.plane((x, -0.00675, z), X, Z), parent=root)
    if st.get("feet"):
        st["feet"](types.SimpleNamespace(**locals()))
    fx0 = -0.179 if n_bottom else 0.040   # the filter reaches under the bottom fans' intake
    ff = rr(fx0, 0.202, -0.068, 0.068, 0.004)
    sheet("filter_frame", "black_plastic", (0, -0.0019, 0), X, Z, ff, [rr(fx0 + 0.006, 0.196, -0.062, 0.062, 0.002)], t=0.0026)
    sheet("filter_mesh", "mesh_black", (0, -0.0012, 0), X, Z, rr(fx0 + 0.005, 0.197, -0.063, 0.063, 0.002), t=0.0004)
    for k in range(round((0.196 - fx0 - 0.006) / 0.025) - 1):  # the frame's ribs
        sheet("filter_rib", "black_plastic", (0, -0.0019, 0), X, Z, rect(fx0 + 0.006 + 0.025 * (k + 1) - 0.001, fx0 + 0.006 + 0.025 * (k + 1) + 0.001, -0.062, 0.062), t=0.0022)
    P.slab("filter_tab", P.rrect(0.010, 0.034, 0.004, 0.207, 0.0), 0.0026, "black_plastic", P.plane((0, -0.0019, 0), X, Z), parent=root)
    for k in range(4):
        P.cube("filter_grip", (0.2095, -0.0003, -0.009 + k * 0.006), (0.004, 0.0008, 0.0014), "black_plastic", parent=root)

    # ---------------- front bezel and front I/O
    bez = st["bezel"]
    bx0, bx1 = -0.2185, XF           # bezel depth
    bz, by0, by1 = 0.1055, -0.0005, YT + 0.0005
    side_slits = []
    if st["front"] == "solid":
        side_slits = [P.stadium(0.0105, 0.0026, -0.2088, 0.030 + 0.0082 * k) for k in range(46)]
    for zs in ((-bz,) if glass else (bz, -bz)):
        sheet("bezel_side", bez, (0, 0, zs - math.copysign(0.0012, zs)), X, Y, rect(bx0 + 0.002, bx1 - 0.0004, by0 + 0.002, by1 - 0.002),
              side_slits, t=0.0024)
        if side_slits:
            sheet("bezel_side_mesh", "mesh_black", (0, 0, zs - math.copysign(0.0030, zs)), X, Y, rect(-0.2150, -0.2025, 0.025, 0.41), t=0.0004)
    for ys in (by0, by1):
        sheet("bezel_cap", bez, (0, ys - math.copysign(0.0012, ys - 0.2), 0), X, Z, rect(bx0 + 0.002, bx1 - 0.0004, -bz + 0.002, bz - 0.002), t=0.0024)
    # the front face: a rounded plate (two steps give the edge a soft chamfer)
    io_y = 0.4268
    face_holes = [P.rrect(0.137, 0.017, 0.004, 0, io_y)]  # open behind the front I/O insert
    if breeze:
        face_holes.append(rr(-0.0885, 0.0885, 0.028, 0.401, 0.006))
    xface = bx0 - 0.0000  # outer face of the bezel
    if glass:
        # panoramic front: a black top strip (front I/O) and base strip (logo, ARGB line) with the front glass between
        # them. The glass runs to the window side's outer glass plane, where the side glass butts against it.
        gzf = ZG + 0.0045                      # the side glass's outer face
        GY0, GY1 = 0.0285, 0.4085              # the front glass between the strips
        for (y0_, y1_, hl) in ((GY1, by1, [P.rrect(0.137, 0.017, 0.004, 0, io_y)]), (by0, GY0, [])):
            sheet("bezel_face", bez, (bx0 + 0.0016, 0, 0), Z, Y, rr(-bz, gzf, y0_, y1_, 0.003), hl, t=0.0026)
            sheet("bezel_face_edge", bez, (bx0 + 0.0002, 0, 0), Z, Y, rr(-bz + 0.0008, gzf - 0.0008, y0_ + 0.0008, y1_ - 0.0008, 0.0025),
                  hl, t=0.0004)
        sheet("front_glass", "glass", (bx0 + 0.0020, 0, 0), Z, Y, rect(-bz, gzf, GY0, GY1), t=0.004)
        # black silkscreen on the inside of the front glass: a band on the solid side, thin lines at the strips
        xs = bx0 + 0.00403
        sheet("front_glass_band", "paint_black", (xs, 0, 0), Z, Y, rect(-bz, -bz + 0.009, GY0, GY1), t=0.00006)
        for (y0_, y1_) in ((GY0, GY0 + 0.003), (GY1 - 0.003, GY1)):
            sheet("front_glass_band", "paint_black", (xs, 0, 0), Z, Y, rect(-bz + 0.009, gzf, y0_, y1_), t=0.00006)
        # ARGB light line along the top of the base strip, and the brand on the base strip
        P.cube("front_argb", (xface + 0.0012, GY0 - 0.0016, (gzf - bz) / 2), (0.0016, 0.0016, bz + gzf - 0.012), "rgb", parent=root)
        P.text3d("bezel_logo", st["brand"], 0.0090, 0.0003, st["logo_tag"], P.Frame((xface, 0.0120, 0.0), NX, Y), st["logo_font"],
                 parent=root, width=0.05, spacing=1.35)
    else:
        sheet("bezel_face", bez, (bx0 + 0.0016, 0, 0), Z, Y, P.rrect(2 * bz, by1 - by0, 0.006, 0, (by0 + by1) / 2), face_holes, t=0.0026)
        sheet("bezel_face_edge", bez, (bx0 + 0.0002, 0, 0), Z, Y, P.rrect(2 * bz - 0.0016, by1 - by0 - 0.0016, 0.0052, 0, (by0 + by1) / 2),
              ([rr(-0.0885 - 0.0008, 0.0885 + 0.0008, 0.028 - 0.0008, 0.401 + 0.0008, 0.0068)] if breeze else []) +
              [P.rrect(0.137, 0.017, 0.004, 0, io_y)], t=0.0004)
    if st.get("face"):
        st["face"](types.SimpleNamespace(**locals()))
    elif glass:
        pass
    elif breeze:
        # the mesh insert (texture with real-scale perforation) just behind the face opening
        mf = P.Frame((xface + 0.0016, 0.2145, 0.0), NX, Y)
        P.quad("front_mesh", mf, 0.180, 0.376, "tex_" + cid + "_mesh", root, uv=(0, 0, 1, 1))
        # back side of the mesh (seen from inside the case)
        P.quad("front_mesh_back", P.Frame((xface + 0.0018, 0.2145, 0.0), X, Y), 0.180, 0.376, "tex_" + cid + "_mesh", root)
        P.text3d("bezel_logo", "breeze", 0.0105, 0.0003, st["logo_tag"], P.Frame((xface, 0.0145, 0.0), NX, Y), "seguisb.ttf",
                 parent=root, width=0.06, spacing=1.15)
    else:
        # brushed aluminium inlay with an orange accent line, and the brand below it
        P.slab("bezel_inlay", P.rrect(0.150, 0.345, 0.004, 0.004, 0.222), 0.0010, "alu_dark", P.plane((xface - 0.0005, 0, 0), Z, Y), parent=root)
        P.slab("bezel_accent", P.rrect(0.0028, 0.345, 0.0012, -0.0755, 0.222), 0.0010, P.PALETTE_TAG, P.plane((xface - 0.0005, 0, 0), Z, Y),
               parent=root, uv_solid=P.pal("accent_orange"))
        for k in range(3):
            P.slab("bezel_groove", P.rrect(0.15, 0.0012, 0.0005, 0.004, 0.035 - k * 0.006), 0.0004, "black_plastic",
                   P.plane((xface - 0.0001, 0, 0), Z, Y), parent=root)
        P.text3d("bezel_logo", st["brand"], 0.0115, 0.0004, st["logo_tag"], P.Frame((xface, 0.0135 + 0.0, 0.0), NX, Y), st["logo_font"],
                 parent=root, width=0.105)
    # front I/O insert (black on both cases)
    iof = P.Frame((xface, io_y, 0.0), NX, Y)    # local x runs towards -z (viewer's right seen from the front)
    io_holes = []
    PB_Z, RS_Z, HDD_Z, USB_Z, AUD_Z = 0.050, 0.031, 0.022, (0.004, -0.0165), -0.036
    # (local x = -z)
    io_holes.append(P.circle(0.0079, -PB_Z, 0, 32))
    io_holes.append(P.circle(0.0030, -RS_Z, 0, 16))
    io_holes.append(P.circle(0.0012, -HDD_Z, 0, 10))
    for uz in USB_Z:
        io_holes.append(P.rrect(0.0132, 0.0058, 0.0005, -uz, 0))
    io_holes.append(P.circle(0.0030, -AUD_Z, 0, 16))
    io_holes.append(P.rrect(0.0090, 0.0034, 0.0016, 0.054, 0))  # USB-C
    P.slab("io_insert", P.rrect(0.142, 0.022, 0.005), 0.0016, "black_plastic", iof.sub(0, 0, -0.0005), holes=io_holes, parent=root)
    # power button: chrome bezel ring, LED ring (A_LED_POWER_0) and the button cap (A_BUTTON_POWER_0)
    pbf = iof.sub(-PB_Z, 0, 0)
    P.lathe("pwr_ring", [(0.0062, 0.0003), (0.0079, 0.0003), (0.0081, -0.0004), (0.0078, -0.0009), (0.0062, -0.0009)], "nickel",
            pbf, 40, root, smooth=50)
    a_led = P.anchor("A_LED_POWER_0", pbf.sub(0, 0, -0.0004), (0.016, 0.016, 0.004), root, meta="colour=" + st["led_power"][4:])
    P.lathe("pwr_led", [(0.0054, -0.0008), (0.0062, -0.0008), (0.0062, -0.0002), (0.0054, -0.0002)], st["led_power"], pbf, 40, a_led)
    a_pb = P.anchor("A_BUTTON_POWER_0", pbf.sub(0, 0, 0.0), (0.016, 0.016, 0.008), root, meta="press=+z_local,travel=0.0015")
    P.lathe("pwr_cap", [(0, 0.0007), (0.0046, 0.0007), (0.0052, 0.0004), (0.0053, -0.004), (0, -0.004)], "black_plastic", pbf, 40, a_pb)
    power_icon("pwr_icon", pbf.sub(0, 0, 0.0007), 0.0025, 0.0006, "grey_plastic", a_pb)
    # reset (recessed) and the HDD LED
    rsf = iof.sub(-RS_Z, 0, 0)
    P.lathe("rst_ring", [(0.0021, 0.0002), (0.0031, 0.0002), (0.0031, -0.0008), (0.0021, -0.0008)], "dark_plastic", rsf, 24, root)
    a_rs = P.anchor("A_BUTTON_RESET_0", rsf, (0.006, 0.006, 0.006), root, meta="press=+z_local,travel=0.001")
    P.lathe("rst_cap", [(0, -0.0006), (0.0019, -0.0006), (0.002, -0.003), (0, -0.003)], "black_plastic", rsf, 24, a_rs)
    hdf = iof.sub(-HDD_Z, 0, 0)
    a_hdd = P.anchor("A_LED_HDD_0", hdf, (0.003, 0.003, 0.003), root, meta="colour=red")
    P.lathe("hdd_led", [(0, 0.0001), (0.0010, 0.0), (0.0011, -0.0015), (0, -0.0015)], "led_red", hdf, 16, a_hdd)
    # USB-A ports (blue USB 3 tongues) with their anchors
    for i, uz in enumerate(USB_Z):
        uf = iof.sub(-uz, 0, 0)
        P.slab("usb_shell", P.rrect(0.0125, 0.0050, 0.0004), 0.0085, "nickel", uf.sub(0, 0, -0.0045),
               holes=[P.rrect(0.0119, 0.0044, 0.0002)], parent=root)
        P.cube("usb_tongue", (0, 0.0009, -0.0050), (0.0105, 0.0016, 0.0075), P.PALETTE_TAG, uf, root, uv_solid=P.pal("usb_blue"))
        P.cube("usb_floor", (0, 0, -0.0088), (0.0118, 0.0044, 0.0004), "black_plastic", uf, root)
        P.anchor(f"A_PORT_USBA_FRONT_{i}", P.Frame(c_add(uf.o, uf.w, 0.0002), uf.w, Y), (0.014, 0.007, 0.012), root, meta="usb=3.0")
    # audio combo jack and USB-C
    af = iof.sub(-AUD_Z, 0, 0)
    P.lathe("audio_jack", [(0.0018, 0.0001), (0.0030, 0.0001), (0.0030, -0.006), (0.0018, -0.006)], "nickel", af, 24, root)
    P.cylinder("audio_hole", af.sub(0, 0, -0.0055), 0.0019, 0.0006, "black_plastic", 16, root)
    cf = iof.sub(0.054, 0, 0)
    P.slab("usbc_shell", P.rrect(0.0088, 0.0032, 0.0015), 0.006, "nickel", cf.sub(0, 0, -0.003), holes=[P.rrect(0.0082, 0.0026, 0.0012)], parent=root)
    P.cube("usbc_tongue", (0, 0, -0.0032), (0.0066, 0.0007, 0.005), "black_plastic", cf, root)
    # tiny icons over the jacks
    P.text3d("io_icon", "SS\u2192", 0.0022, 0.00008, "grey_plastic", iof.sub(-0.0063, -0.0072, 0.00005), "segoeuib.ttf", parent=root, width=0.006)
    P.text3d("io_icon", "\u2299", 0.0028, 0.00008, "grey_plastic", iof.sub(-AUD_Z, -0.0068, 0.00005), "seguisym.ttf", parent=root, width=0.004)

    # ---------------- glass side panel (moving): smoked glass, black silkscreen band, thumbscrews
    a_side = P.anchor("A_PANEL_SIDE_0", P.Frame((0.0, 0.225, ZG), Z, Y), (0.398, 0.448, 0.006), root,
                      meta="remove=+z,lift=0.01,glass=1")
    gx0, gx1, gy0, gy1 = XF + 0.0002, XR - 0.0002, 0.0015, YT - 0.0015
    gz = ZG + 0.0005 + 0.002
    TH = [(0.1885, 0.42), (0.1885, 0.03)]
    ghole = [P.circle(0.0034, x, y, 16) for (x, y) in TH]
    band = 0.021
    if glass:
        # the glass runs on to the front glass (no corner pillar); its bands line up with the front strips
        gxs = bx0 + 0.004
        sheet("glass", "glass", (0, 0, gz), X, Y, rr(gxs, gx1, gy0, gy1, 0.0015), ghole, t=0.004, parent=a_side)
        for r_, hl in ((rect(gxs, gx1, GY1, gy1), [P.circle(0.0036, *TH[0], 16)]), (rect(gxs, gx1 - band, gy0, GY0), []),
                       (rect(gx1 - band, gx1, gy0, GY1), [P.circle(0.0036, *TH[1], 16)])):
            sheet("glass_band", "paint_black", (0, 0, ZG + 0.00048), X, Y, r_, hl, t=0.00006, parent=a_side)
    else:
        sheet("glass", "glass", (0, 0, gz), X, Y, rr(gx0, gx1, gy0, gy1, 0.003), ghole, t=0.004, parent=a_side)
        sheet("glass_band", "paint_black", (0, 0, ZG + 0.00048), X, Y, rr(gx0, gx1, gy0, gy1, 0.003),
              [rr(gx0 + band, gx1 - band, gy0 + band, gy1 - band - 0.004, 0.004)] + [P.circle(0.0036, x, y, 16) for (x, y) in TH],
              t=0.00006, parent=a_side)
    P.text3d("glass_print", "TEMPERED GLASS", 0.0032, 0.00004, "grey_plastic", P.Frame((gx1 - 0.045, gy0 + 0.0105, ZG + 0.00054), Z, Y),
             "arialbd.ttf", parent=a_side, width=0.05)
    P.text3d("glass_print", st["brand"], 0.0045, 0.00004, "grey_plastic", P.Frame((gx0 + 0.045, gy0 + 0.0105, ZG + 0.00054), Z, Y),
             st["logo_font"], parent=a_side, width=0.05)
    for y in (0.08, 0.37):  # hooks along the front edge that drop into the front flange
        P.cube("glass_hook", (gx0 + 0.006, y, ZG - 0.002), (0.008, 0.02, 0.004), "black_plastic", parent=a_side, bevel=0.0006)
    for i, (x, y) in enumerate(TH):
        ta = P.anchor(f"A_SCREW_THUMB_{i}", P.Frame((x, y, ZG + 0.0045 + 0.0008), Z, X), (0.013, 0.013, 0.01), a_side,
                      meta="thread=6-32,captive=1")
        BP.thumbscrew(P.anchor_frame(ta), ta, tag=st["thumb_tag"], name="thumb", washer="rubber")
    # rubber bumpers on the frame where the glass rests
    for (x, y) in [(-0.17, 0.0068), (0.17, 0.0068), (-0.17, YT - 0.0068), (0.17, YT - 0.0068)]:
        P.cube("glass_bumper", (x, y, ZG + 0.00022), (0.02, 0.006, 0.00045), "rubber", parent=root)

    # ---------------- back panel (moving): solid steel, folded edges, rear flange with two thumbscrews
    a_back = P.anchor("A_PANEL_BACK_0", P.Frame((0.0, 0.225, ZBK - T), NZ, Y), (0.398, 0.448, 0.006), root, meta="remove=-z")
    zb = ZBK - T / 2 - 0.0002
    sheet("back_panel", paint, (0, 0, zb), X, Y, rect(XF + 0.003, XR - 0.002, 0.0025, YT - 0.0025), parent=a_back)
    for yedge, sgn in ((0.0, -1), (YT, 1)):
        yc = yedge - sgn * T / 2
        flange("back_fl", paint, (xm, 0, 0), Y, Z, [(yc - sgn * 0.004, zb), (yc, zb), (yc, zb + 0.006)], Lx - 0.006, parent=a_back)
    flange("back_fl", paint, (0, YT / 2, 0), X, Z, [(XR - 0.004, zb), (XR + T / 2 + 0.0001, zb), (XR + T / 2 + 0.0001, ZBK + 0.0105)],
           YT - 0.012, parent=a_back)
    flange("back_fl", paint, (0, YT / 2, 0), X, Z, [(XF + 0.007, zb), (XF + 0.0025, zb), (XF + 0.0025, zb + 0.006)], YT - 0.012, parent=a_back)
    P.cube("back_grip", (XR + 0.0013, 0.225, ZBK + 0.0105 - 0.004), (0.0012, 0.05, 0.004), paint, parent=a_back)
    for i, y in enumerate((0.39, 0.06)):
        ta = P.anchor(f"A_SCREW_THUMB_{2 + i}", P.Frame((XR + T + 0.0003, y, -0.1), X, Y), (0.013, 0.013, 0.01), a_back,
                      meta="thread=6-32")
        BP.thumbscrew(P.anchor_frame(ta), ta, tag=st["thumb_tag"], name="thumb")

    # ---------------- slot covers (moving) with their PH2 screws
    for k, y in enumerate(SLOT_Y):
        a = P.anchor(f"A_SLOTCOVER_{k}", P.Frame((COVER_X, y, -0.03), Z, Y), (0.004, 0.019, 0.125), root,
                     meta=f"slot={k},remove=+z")
        hw = 0.0090
        yt = min(y + hw, IO_Y0 - 0.0012)       # clears the I/O shield next to the top slot
        outl = [(-0.0935, y - 0.004), (-0.0880, y - 0.004), (-0.0870, y - hw), (TAB_Z - 0.0035, y - hw), (TAB_Z - 0.0035, y + hw),
                (IO_Z1 + 0.003, y + hw), (IO_Z1 + 0.001, yt), (-0.0870, yt), (-0.0880, min(y + 0.004, yt)), (-0.0935, min(y + 0.004, yt))]
        vents = [P.stadium(0.013, 0.0026, zc, y + dy) for zc in (-0.066, -0.047, -0.028, -0.009, 0.010) for dy in (-0.0038, 0.0038)
                 if y + dy + 0.0018 < yt or zc - 0.0065 > IO_Z1 + 0.003]
        sheet("cover", st["cover_tag"], (COVER_X, 0, 0), Z, Y, outl, vents, parent=a)
        flange("cover_bend", st["cover_tag"], (0, y, 0), X, Z,
               [(COVER_X, TAB_Z - 0.0040), (COVER_X, TAB_Z - 0.0005), (COVER_X + 0.0035, TAB_Z - 0.0005)], 2 * hw, parent=a)
        tab = [(COVER_X + 0.0030, y - hw), (SCREW_X + 0.0050, y - hw), (SCREW_X + 0.0050, y - 0.0022), (SCREW_X, y - 0.0022)]
        tab += [(SCREW_X - 0.0022 * math.sin(t_ * math.pi / 8), y - 0.0022 * math.cos(t_ * math.pi / 8)) for t_ in range(1, 8)]
        tab += [(SCREW_X, y + 0.0022), (SCREW_X + 0.0050, y + 0.0022), (SCREW_X + 0.0050, y + hw), (COVER_X + 0.0030, y + hw)]
        sheet("cover_tab", st["cover_tag"], (0, 0, TAB_Z - 0.0005), X, Y, tab, parent=a)
        sa = P.anchor(f"A_SCREW_PH2_{k}", P.Frame((SCREW_X, y, TAB_Z), Z, X), (0.008, 0.008, 0.008), root,
                      meta=f"slot={k},thread=6-32,pre=1")
        BP.screw(P.anchor_frame(sa), sa, "ph2", st["screw_tag"], name="slot_screw")

    # ---------------- motherboard socket, standoffs, I/O shield, PSU and SSD sockets
    P.anchor("A_SOCKET_MOBO_0", P.Frame(MB, Z, Y), (0.244, 0.305, 0.012), root, meta="formfactor=atx,standoff=0.00635")
    for i, L_ in enumerate(ATX_ORDER + ["B"]):
        hx, hy = hole_case(L_)
        bx, by = hole_board(L_)
        meta = f"pre={PRE[L_]},hole={L_},board={bx:.5f};{by:.5f}" + (",atx=0" if L_ == "B" else "")
        a = P.anchor(f"A_STANDOFF_{i}", P.Frame((hx, hy, Z_TRAY), Z, Y), (0.008, 0.008, 0.008), root, meta=meta)
        if PRE[L_]:
            BP.standoff(P.anchor_frame(a), a, "gold", name="standoff")
    P.anchor("A_SOCKET_IOSHIELD_0", P.Frame((XR - T / 2, IO_YC, (IO_Z0 + IO_Z1) / 2), Z, Y),
             (0.004, IO_Y1 - IO_Y0, IO_Z1 - IO_Z0), root, meta="frame=board,insert=+x,window=0.15875x0.04445")
    P.anchor("A_SOCKET_PSU_0", P.Frame(PSU, Z, Y), (0.142, 0.088, 0.152), root, meta="insert=+x")
    # 2.5" mounts: a sled on the shroud and a tray behind the motherboard tray (SSD frame: x length, y top, z width)
    ssd0 = P.Frame((-0.130, YS + T / 2 + 0.0010 + 0.0035, -0.018), NX, Y)
    P.anchor("A_SOCKET_SSD25_0", ssd0, (0.1, 0.007, 0.07), root, meta="frame=ssd25,connector=-z")
    ssd_bracket(ssd0, paint, root)
    ssd1 = P.Frame((-0.126, 0.300, Z_TRAY - T - 0.0012 - 0.0035), NX, NZ)
    P.anchor("A_SOCKET_SSD25_1", ssd1, (0.1, 0.007, 0.07), root, meta="frame=ssd25,connector=-y,behind_tray=1")
    ssd_bracket(ssd1, paint, root)

    # ---------------- grommets
    for gi, g in enumerate(GROM):
        where, (u, v), (w, h) = g
        if where == "tray":
            fr = P.Frame((u, v, Z_TRAY - T / 2), Z, Y)
        else:
            fr = P.Frame((u, YS, v), Y, Z)
        grommet(fr, w, h, root, horizontal=(w > h))
        P.anchor(f"A_GROMMET_{gi}", fr, (w, h, 0.004), root, meta=f"on={where}")

    # ---------------- fans
    fans = [("A_FAN_0", REAR_FAN, NX, Y, 0.12)]
    if ffans:
        for i, (y, d_) in enumerate(ffans):
            fans.append((f"A_FAN_{i + 1}", (XF + T + 0.0128, y, 0.0), NX, Y, d_))
    elif st["fans_front"]:
        for i, y in enumerate(FRONT_FANS_Y):
            fans.append((f"A_FAN_{i + 1}", (XF + T + 0.0128, y, 0.0), NX, Y, 0.12))
    yb = YS + T / 2 + 0.0128        # bottom fans: lying on the shroud, air coming up from below (forward -y)
    for i, (fx, fz_) in enumerate(BOTTOM_FANS[:n_bottom]):
        fans.append((f"A_FAN_{i + 1}", (fx, yb, fz_), NY, X, bfd))
    for name, pos, fwd_, up_, d_ in fans:
        fa = P.anchor(name, P.Frame(pos, fwd_, up_), (d_, d_, 0.025), root,
                      meta=(PF.fan_meta("ccw", 1200) if PF else "axis=z,spin=-1,rpm=1200") + (",rgb=1" if st["fan_rgb"] else ""))
        make_case_fan(fa, st, tex, d_)
    # fan screws on the rear grille
    for sz in (-1, 1):
        for sy in (-1, 1):
            BP.screw(P.Frame((XR, REAR_FAN[1] + sy * 0.0525, REAR_FAN[2] + sz * 0.0525), X, Y), root, "ph2", "steel_dark" if not breeze else "steel",
                     name="fan_screw")

    # ---------------- loose plugs: fan cables and the front-panel bundle
    fan_kind = "fan4" if st["fan_pins"] == 4 else "fan3"
    plug_rest = []
    # rear fan: the plug lies on the tray strip above the board, the cable runs from the frame's corner
    plug_rest.append(("A_PLUG_FAN_0", fan_kind, (0.118, 0.4335, Z_TRAY + 0.0026), (1, 0, 0),
                      [(REAR_FAN[0] - 0.006, REAR_FAN[1] + 0.058, REAR_FAN[2] - 0.058), (0.17, 0.43, -0.03), (0.150, 0.4345, Z_TRAY + 0.004)]))
    for i, (y, d_) in enumerate(ffans or [(y_, 0.12) for y_ in FRONT_FANS_Y[:st["fans_front"]]]):
        zp = Z_TRAY + 0.0026
        yp = 0.385 - 0.04 * i
        q = 0.058 if d_ == 0.12 else d_ / 2 - 0.002     # the frame corner the cable leaves from
        plug_rest.append((f"A_PLUG_FAN_{i + 1}", fan_kind, (-0.128, yp, zp), (-1, 0, 0),
                          [(XF + 0.026, y - q, -q), (-0.176, y - 0.045, -0.085), (-0.176, yp, Z_TRAY + 0.006),
                           (-0.170, yp, Z_TRAY + 0.003)]))
    for i, (fx, fz_) in enumerate(BOTTOM_FANS[:n_bottom]):
        zp = Z_TRAY + 0.0026
        yp = 0.385 - 0.04 * i
        yc_ = YS + T / 2 + 0.0035 + 0.0022 * i
        plug_rest.append((f"A_PLUG_FAN_{i + 1}", fan_kind, (-0.128, yp, zp), (-1, 0, 0),
                          [(fx - bfd / 2 + 0.006, yb + 0.004, fz_ - bfd / 2 + 0.006), (fx - bfd / 2 - 0.004, yc_, -0.060),
                           (fx - bfd / 2 - 0.012, yc_, -0.086 + 0.0022 * i), (-0.174 - 0.0025 * i, yc_ + 0.004, -0.089 + 0.0022 * i),
                           (-0.176 - 0.0025 * i, yp, Z_TRAY + 0.006), (-0.170, yp, Z_TRAY + 0.003)]))
    fp_list = [("A_PLUG_PWRSW_0", "fp_pwrsw", FP_POS["fp_pwrsw"]), ("A_PLUG_RESET_0", "fp_reset", FP_POS["fp_reset"]),
               ("A_PLUG_PLED_0", "fp_pled", FP_POS["fp_pled"]), ("A_PLUG_HDDLED_0", "fp_hddled", FP_POS["fp_hddled"]),
               ("A_PLUG_USB3_0", "usb3hdr", FP_POS["usb3hdr"]), ("A_PLUG_AUDIO_0", "audiohdr", FP_POS["audiohdr"])]
    for name, kind, (x, y) in fp_list:
        plug_rest.append((name, kind, (x, y, None), (0, -1, 0), None))
    for name, kind, pos, cable_dir, route in plug_rest:
        build = BP.PLUGS[kind]
        # the plug lies flat on the tray: +z (cable) along cable_dir, its top (+y) facing the glass
        probe = P.Frame((0, 0, 0), cable_dir, Z)
        x, y, zz = pos
        info_h = {"fp_pwrsw": 0.00254, "fp_reset": 0.00254, "fp_pled": 0.00254, "fp_hddled": 0.00254, "usb3hdr": 0.0086,
                  "audiohdr": 0.00508, "fan3": 0.0046, "fan4": 0.0046}.get(kind, 0.005)
        zz = Z_TRAY + info_h / 2 + 0.0003 if zz is None else zz
        fr = P.Frame((x, y, zz), cable_dir, Z)
        meta = f"kind={kind}"
        if name.startswith("A_PLUG_FAN"):
            meta += f",fan={name[-1]}"
        else:
            meta += ",from=A_GROMMET_2"
        a = P.anchor(name, fr, (0.025, 0.012, 0.03), root, meta=meta)
        build(P.anchor_frame(a), a)
        if route:
            P.tube("fan_cable", P.smooth_path(route, 6), 0.0016, "rubber", root, 8)
    # the front-panel bundle: from the I/O board down behind the tray, out at the bottom front grommet
    bundle = [(XF + 0.004, 0.428, -0.03), (XF + 0.012, 0.425, -0.090), (tray_x0 - 0.004, 0.40, -0.100), (tray_x0 - 0.004, 0.20, -0.100),
              (-0.077, 0.1385, -0.098), (-0.077, 0.1385, Z_TRAY + 0.003), (-0.10, 0.126, Z_TRAY + 0.0025)]
    P.tube("fp_bundle", P.smooth_path(bundle, 6), 0.0035, "rubber", root, 10)
    ux, uy = FP_POS["usb3hdr"]
    P.tube("usb3_cable", P.smooth_path([(XF + 0.004, 0.426, 0.006), (XF + 0.014, 0.42, -0.08), (tray_x0 - 0.006, 0.38, -0.099),
                                         (tray_x0 - 0.006, 0.20, -0.099), (-0.079, 0.150, -0.099), (-0.079, 0.150, Z_TRAY + 0.004),
                                         (-0.092, 0.150, Z_TRAY + 0.0045), (ux, uy - 0.0405, Z_TRAY + 0.0045)], 6), 0.0032, "rubber", root, 10)
    # wires from the bundle end to each front-panel plug's tail
    for k_ in ("fp_pwrsw", "fp_reset", "fp_pled", "fp_hddled", "audiohdr"):
        tx, ty = FP_POS[k_]
        ty -= 0.0404 if k_ != "audiohdr" else 0.040
        P.tube("fp_wire", P.smooth_path([(-0.10, 0.126, Z_TRAY + 0.0025), ((tx - 0.10) / 2, (ty + 0.126) / 2 - 0.006, Z_TRAY + 0.0018),
                                         (tx, ty, Z_TRAY + 0.0014)], 5), 0.0012, "rubber", root, 8)

    if st.get("extra"):
        st["extra"](types.SimpleNamespace(**locals()))

    # ---------------- hitboxes (not the glass)
    hits = [((-0.2095, 0.225, 0.0), (0.019, 0.451, 0.211)), ((XR - 0.003, 0.225, 0.0), (0.008, 0.45, 0.21)),
            ((xm, YT - 0.005, 0.0), (0.4, 0.01, 0.21)), ((xm, -0.002, 0.0), (0.4, 0.012, 0.21)),
            ((0.014, 0.277, Z_TRAY - 0.003), (0.364, 0.345, 0.006)), ((0.012, 0.052, 0.0), (0.368, 0.104, 0.194))]
    for i, (pos, size) in enumerate(hits):
        P.anchor(f"A_HIT_{i}", pos, size, root)

    P.finalize(root, cid)
    c.export(root, cid)
    extra = case_numbers()
    tris, meshes = P.write_report(root, cid, extra)
    P.preview(root, cid, views=((35, 30), (-140, 30)), size=(1000, 760))
    P.beauty(root, cid, views=((32, 22), (-35, 22), (150, 20), (95, 60)), size=(1280, 960), samples=96)
    P.beauty(root, cid, views=((40, 28),), size=(1280, 960), samples=96, hide=("A_PANEL_SIDE_0",), start_index=6)
    P.beauty(root, cid, views=((-60, 10),), size=(1280, 960), samples=96, target=(XF - 0.01, 0.42, 0.0), dist=0.32, start_index=7)
    P.beauty(root, cid, views=((90, 8),), size=(1280, 960), samples=96, target=(XR, 0.25, 0.0), dist=0.75, start_index=8)
    return tris, meshes


def c_add(p, d, s):
    return P.vec(p) + P.vec(d) * s


def ssd_bracket(fr, paint, root):
    """A steel sled under a 2.5" drive (frame: x length, y up out of the mount, z width): a floor and two side
    walls with slotted holes at the standard side-hole positions (x -36 mm and +40.6 mm, 3 mm up from the bottom)."""
    yb = -0.0035 - 0.0006
    P.cube("ssd_sled", (0.002, yb, 0), (0.104, 0.0012 if True else T, 0.074), paint, fr, root)
    for sz in (-1, 1):
        z = sz * (0.03493 + 0.0009)
        holes = [P.stadium(0.007, 0.0034, x, -0.0005) for x in (-0.036, 0.0406)]
        P.slab("ssd_wall", P.rrect(0.100, 0.0085, 0.0015, 0.002, 0.0), T, paint, fr.sub(0, 0, z), holes=holes, parent=root)
    for x in (-0.03, 0.035):
        P.cylinder("ssd_sled_screw", P.Frame(fr.p(x, yb + 0.0006, 0.022), fr.v, fr.w), 0.0025, 0.0012, "steel_dark", 12, root, z0=0)


def grommet(fr, w, h, root, horizontal=True):
    """A rubber grommet lining a cut-out: a rim round the edge and a split membrane across it."""
    rim_o = P.rrect(w + 0.004, h + 0.004, min(w, h) * 0.45 + 0.002)
    rim_i = P.rrect(w - 0.003, h - 0.003, max(0.0005, min(w, h) * 0.45 - 0.0015))
    P.slab("grommet_rim", rim_o, 0.0034, "rubber", fr, holes=[rim_i], parent=root, smooth=None)
    gap = 0.0011
    if horizontal:   # the slit runs along the long (x) side
        for sy in (-1, 1):
            hh = (h - 0.003) / 2 - gap / 2
            P.slab("grommet_lip", P.rrect(w - 0.0028, hh, min(hh, 0.002), 0, sy * (gap / 2 + hh / 2)), 0.0008, "rubber",
                   fr.sub(0, 0, 0.0006), parent=root)
    else:
        for sx in (-1, 1):
            ww = (w - 0.003) / 2 - gap / 2
            P.slab("grommet_lip", P.rrect(ww, h - 0.0028, min(ww, 0.002), sx * (gap / 2 + ww / 2), 0), 0.0008, "rubber",
                   fr.sub(0, 0, 0.0006), parent=root)


def make_case_fan(fa, st, tex, diameter=0.12):
    if PF is not None:
        try:
            PF.make_fan(fa, diameter=diameter, thickness=0.025, blades=7, frame=True, rgb=st["fan_rgb"], spin="ccw",
                        blade_tag=st["fan_tag"], frame_tag=st["fan_tag"], sticker=tex.get("hub"), label=tex.get("motor"),
                        name=fa.name.lower())
            return
        except Exception as e:
            print("make_fan failed, local fan:", e)
    local_fan(fa, st)


def local_fan(fa, st):
    """Fallback 120 mm fan (only if parts_fan is missing): frame, struts, motor and a rotor of swept blades."""
    fr = P.anchor_frame(fa)
    tag = st["fan_tag"]
    P.slab("fan_frame", P.rrect(0.12, 0.12, 0.0045), 0.025, tag, fr, holes=[P.circle(0.058, 0, 0, 64)], parent=c.top_of(fa))
    P.cylinder("fan_motor", fr.sub(0, 0, -0.009), 0.019, 0.006, tag, 32, c.top_of(fa))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        P.cube("fan_strut", (math.cos(a) * 0.039, math.sin(a) * 0.039, -0.011), (0.04, 0.003, 0.003), tag, fr.sub(0, 0, 0, (0, 0, 1), (0, 1, 0)),
               c.top_of(fa))
    P.cylinder("fan_hub", fr, 0.020, 0.017, tag, 32, fa)
    for k in range(7):
        a = 2 * math.pi * k / 7
        bf = P.Frame(fr.p(math.cos(a) * 0.038, math.sin(a) * 0.038, 0), fr.d(-math.sin(a), math.cos(a), 0.6), fr.d(math.cos(a), math.sin(a), 0))
        P.cube("fan_blade", (0, 0, 0), (0.036, 0.0012, 0.03), tag, bf, fa)


def case_numbers():
    lines = ["ATX holes (case coords x, y on the tray at z=%.5f; board frame bx, by):" % Z_TRAY]
    for L_ in ATX_ORDER + ["B"]:
        hx, hy = hole_case(L_)
        bx, by = hole_board(L_)
        lines.append(f"  {L_}: case=({hx:.5f}, {hy:.5f})  board=({bx:.5f}, {by:.5f})  pre={PRE[L_]}")
    lines.append("slot centres y: " + ", ".join(f"{y:.5f}" for y in SLOT_Y))
    lines.append(f"slot screw x={SCREW_X:.5f} z={TAB_Z:.5f}; bracket plate x={COVER_X:.5f}")
    lines.append(f"IO window z {IO_Z0:.5f}..{IO_Z1:.5f}  y {IO_Y0:.5f}..{IO_Y1:.5f}")
    return "\n".join(lines)


def main(ids=None):
    out = {}
    for cid in (ids or list(STYLES)):
        out[cid] = build(cid)
    for k, v in out.items():
        print("BUILT", k, v)
    return out


if __name__ == "__main__":
    a = c.args()
    main(a if a else None)
