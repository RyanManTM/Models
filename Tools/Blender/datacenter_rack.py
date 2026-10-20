"""
rack_42u (an enclosed 19" 42U rack, 600 W x 1070 D x 2000 H, black powder coat) and rack_12u_open (a 12U open-frame
4-post rack on castors for the basement stage).

Frame: origin at the floor, at the centre of the footprint; +Z is the front, +Y up.
Mounting: two front rails whose front face is the front mounting plane (z = ZM) and two rear rails 0.740 behind it,
facing the rear (their rear face at ZM - 0.742). Square cage-nut holes at the EIA-310 spacing (1/4", 7/8" and
1 1/2" above the bottom of each U), centred +-232.55 mm; the U numbers are printed beside them.

A_RACKU_n (n = 0 for U1 at the bottom): the install pose of a rack device (datacenter_common's device frame):
the centre of the front mounting plane at the BOTTOM of that U, +Z out of the front, size 0.4826 x 0.04445 x the
mounting depth 0.740 (the box extends towards -z in the game's terms; meta says so). A device of k U installed at
A_RACKU_n takes U n+1 .. n+k.

rack_42u moving pieces: the perforated front door A_DOOR_FRONT_0 (hinge=y,open=-110, hinged on -x), the split rear
doors A_DOOR_REAR_0 (-x, open=110) and A_DOOR_REAR_1 (+x, open=-110), the side panels A_PANEL_SIDE_0 (-x) and
A_PANEL_SIDE_1 (+x). Zero-U PDU places A_PDU_0 (-x) and A_PDU_1 (+x) in the rear side channels (the pdu_0u frame:
origin at the bottom end of the body, +Y along it, outlets towards +Z, here facing the rear door).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import datacenter_common as D  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ

PAINT = "paint_black"
MOUNT_DEPTH = 0.740

ATLAS = D.Atlas("rack_print", 1024, 512)
ATLAS.add("numbers", 0, 0, 512, 224)
ATLAS.add("badge", 0, 448, 512, 64)
ATLAS.add("rating", 512, 0, 512, 320)
ATLAS.add("earth", 512, 320, 128, 128)
NUMBERS = D.Labels(ATLAS, "numbers", 64, 32, [str(k) for k in range(1, 43)], fg=(0.92, 0.92, 0.9), bg=(0.03, 0.03, 0.033),
                   font="arialbd.ttf", size=0.66)

STYLES = {
    "rack_42u": dict(units=42, W=0.600, Dp=1.070, H=2.000, y0=0.0900, zm=0.410, enclosed=True),
    "rack_12u_open": dict(units=12, W=0.560, Dp=0.800, H=0.690, y0=0.1150, zm=0.371, enclosed=False),
}


def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=(0.5, 0.5, 0.5), name="rack_print")
    NUMBERS.draw(art)
    x, y, w, h = ATLAS.reg["badge"]
    art.rect(x, y, w, h, (0.03, 0.03, 0.035))
    art.text("STRATA", x + w / 2, y + h / 2, 44, (0.8, 0.82, 0.85), "segoeuib.ttf", align="CENTER", valign="CENTER", spacing=1.3)
    x, y, w, h = ATLAS.reg["rating"]
    ink = (0.08, 0.08, 0.09)
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    art.rect(x, y + h - 52, w, 52, (0.08, 0.09, 0.12))
    art.text("STRATA  NETSHELTER-STYLE ENCLOSURE", x + 16, y + h - 34, 22, (0.9, 0.92, 0.95), "segoeuib.ttf", maxw=w - 32)
    lines = [("MODEL", "SRK-4260-107"), ("HEIGHT", "42U  2000 mm"), ("WIDTH x DEPTH", "600 x 1070 mm"),
             ("STATIC LOAD", "1360 kg"), ("ROLLING LOAD", "1020 kg"), ("MOUNTING", "EIA-310-E, square holes")]
    for k, (a, b) in enumerate(lines):
        art.text(a, x + 16, y + h - 84 - k * 32, 20, ink, "arialbd.ttf")
        art.text(b, x + 210, y + h - 84 - k * 32, 20, ink, "arial.ttf", maxw=w - 230)
    art.code128ish(4260, x + 16, y + 14, 260, 40, ink)
    art.text("S/N SRK42A2609-0417", x + 290, y + 30, 16, ink, "consola.ttf", maxw=210)
    x, y, w, h = ATLAS.reg["earth"]
    art.rect(x, y, w, h, (0.95, 0.8, 0.1))
    art.rect(x + 6, y + 6, w - 12, h - 12, (0.98, 0.86, 0.15))
    art.ring(x + w / 2, y + h / 2, 44, 50, ink)
    art.rect(x + w / 2 - 3, y + h / 2 - 4, 6, 40, ink)
    for k, ww in enumerate((60, 42, 24)):
        art.rect(x + w / 2 - ww / 2, y + h / 2 - 8 - k * 12, ww, 6, ink)
    art.render(ATLAS.file)
    art.dispose()
    D.hex_perf_texture("rack_perf", 512, 512, 0.1, 0.1, 0.0056, 0.0021, web=(0.055, 0.055, 0.06))


# ====================================================================== rails

def rail(st, root, x_sign, front, enclosed):
    """A mounting rail: the 19" flange with the square holes (facing +z on the front pair, -z at the rear), a side
    flange running along z, and the printed U numbers beside the holes (front face only)."""
    zm = st["zm"]
    units = st["units"]
    y0 = st["y0"]
    y_lo, y_hi = y0 - 0.008, y0 + units * D.U + 0.008
    t = 0.002
    x_in, x_out = 0.2245, 0.2530
    sx = x_sign
    holes = []
    for n in range(units):
        for hh in D.HOLES_IN_U:
            yy = y0 + n * D.U + hh
            holes.append(D.rect(sx * D.HOLE_X - D.SQ_HOLE / 2, sx * D.HOLE_X + D.SQ_HOLE / 2, yy - D.SQ_HOLE / 2, yy + D.SQ_HOLE / 2))
    xa, xb = sorted((sx * x_in, sx * x_out))
    if front:
        zf0, zf1 = zm - t, zm
    else:
        zf0, zf1 = zm - MOUNT_DEPTH - t, zm - MOUNT_DEPTH
    D.zslab("rail_flange", PAINT, D.rect(xa, xb, y_lo, y_hi), zf0, zf1, holes, root)
    # side flange along z (an L profile; the open frame's posts are deeper C profiles)
    depth = 0.055 if enclosed else 0.045
    xs = sx * x_out
    zs0, zs1 = (zf0 - depth, zf0) if front else (zf1, zf1 + depth)
    D.xslab("rail_side", PAINT, D.rect(zs0, zs1, y_lo, y_hi), xs - sx * t, xs, (), root)
    if not enclosed:   # the return lip of the C profile
        zl = zs0 if front else zs1
        D.box("rail_lip", (min(xs, xs - sx * 0.012), y_lo, min(zl, zl + (0.002 if front else -0.002))),
              (max(xs, xs - sx * 0.012), y_hi, max(zl, zl + (0.002 if front else -0.002))), PAINT, root)
    # cage nuts: none fitted (the devices bring theirs); U numbers on the flange's outer strip, and U boundary ticks
    if front:
        xn = sx * 0.2458
        for n in range(units):
            yc = y0 + (n + 0.5) * D.U
            NUMBERS.quad("u_number", str(n + 1), P.Frame((xn, yc, zm + 0.00005), Z, Y), 0.0060, root)
            D.zslab("u_tick", "paint_white", D.rect(xn - 0.0022, xn + 0.0022, y0 + n * D.U - 0.00025, y0 + n * D.U + 0.00025),
                    zm, zm + 0.00006, (), root)
    else:
        xn = sx * 0.2465
        for n in range(units):
            yc = y0 + (n + 0.5) * D.U
            NUMBERS.quad("u_number", str(n + 1), P.Frame((xn, yc, zm - MOUNT_DEPTH - t - 0.00005), NZ, Y), 0.0060, root)


# ====================================================================== enclosed rack pieces

def perforated_door(name_anchor, x0, x1, y0, y1, z_out, a, hinge_x, handle_x, perf_margin=0.040):
    """A door leaf in its closed pose: a folded steel frame round a perforated sheet (two-sided tiled quads), three
    hinge knuckles on hinge_x, and a swing handle with a key lock at handle_x. All of it is a moving piece of a."""
    t = 0.020
    zi = z_out - t
    w = x1 - x0
    # frame: four box-section members (front face, inner return) with the perforated field inside
    m = perf_margin
    D.zslab("door_face", PAINT, D.rr(x0, x1, y0, y1, 0.004), z_out - 0.0015, z_out,
            [D.rect(x0 + m, x1 - m, y0 + m * 1.6, y1 - m * 1.6)], a)
    for (xa, xb, ya, yb) in ((x0, x0 + 0.003, y0, y1), (x1 - 0.003, x1, y0, y1), (x0, x1, y0, y0 + 0.003), (x0, x1, y1 - 0.003, y1)):
        D.box("door_edge", (xa, ya, zi), (xb, yb, z_out - 0.0015), PAINT, a)
    for (xa, xb, ya, yb) in ((x0 + 0.003, x0 + m, y0 + 0.003, y1 - 0.003), (x1 - m, x1 - 0.003, y0 + 0.003, y1 - 0.003),
                             (x0 + m, x1 - m, y0 + 0.003, y0 + m * 1.6), (x0 + m, x1 - m, y1 - m * 1.6, y1 - 0.003)):
        D.box("door_return", (xa, ya, zi), (xb, yb, zi + 0.0012), PAINT, a)
    pw, ph = w - 2 * m, (y1 - y0) - 3.2 * m
    D.tiled_quads("door_perf", "tex_rack_perf", P.Frame(((x0 + x1) / 2, (y0 + y1) / 2, z_out - 0.0010), Z, Y), pw + 0.002, ph + 0.002,
                  0.1, 0.1, a, back=True)
    # hinge knuckles
    for yy in (y0 + 0.12, (y0 + y1) / 2, y1 - 0.12):
        P.cylinder("door_hinge", P.Frame((hinge_x, yy, z_out - 0.010), Y, Z), 0.0055, 0.060, "steel_dark", 12, a)
    # swing handle: a recessed housing with a key cylinder and the folding lever
    hy = (y0 + y1) / 2 + 0.05
    D.zslab("handle_housing", "black_plastic", D.rr(handle_x - 0.016, handle_x + 0.016, hy - 0.090, hy + 0.035, 0.006), z_out, z_out + 0.006, (), a)
    D.zslab("handle_lever", "black_plastic", D.rr(handle_x - 0.009, handle_x + 0.009, hy - 0.080, hy + 0.010, 0.004), z_out + 0.006, z_out + 0.016, (), a)
    lf = P.Frame((handle_x, hy + 0.022, z_out + 0.006), Z, Y)
    P.lathe("handle_lock", [(0, 0.0015), (0.0055, 0.0015), (0.0060, 0.0005), (0.0060, -0.002), (0, -0.002)], "nickel", lf, 16, a)
    D.box("handle_keyway", (handle_x - 0.0007, hy + 0.019, z_out + 0.0075), (handle_x + 0.0007, hy + 0.025, z_out + 0.0078), "dark_plastic", a)
    return hy


def side_panel(st, k, root):
    """A removable side panel: a flat sheet with folded edges, two latches with keys at the top, a handle recess."""
    W, Dp, H = st["W"], st["Dp"], st["H"]
    sx = -1 if k == 0 else 1
    xo = sx * W / 2
    z0, z1 = -Dp / 2 + 0.030, Dp / 2 - 0.030
    y0, y1 = 0.072, H - 0.040
    a = P.anchor(f"A_PANEL_SIDE_{k}", P.Frame((xo, (y0 + y1) / 2, 0.0), Z, Y), (0.020, y1 - y0, z1 - z0), root,
                 meta=f"remove={'-x' if sx < 0 else '+x'},dist=0.06,lift=+y,latch=2,order=0")
    D.xslab("side_sheet", PAINT, D.rr(z0, z1, y0, y1, 0.004), xo - sx * 0.0015, xo, (), a)
    for (za, zb, ya, yb) in ((z0, z0 + 0.0015, y0, y1), (z1 - 0.0015, z1, y0, y1), (z0, z1, y0, y0 + 0.0015), (z0, z1, y1 - 0.0015, y1)):
        D.box("side_edge", (min(xo - sx * 0.018, xo), ya, za), (max(xo - sx * 0.018, xo), yb, zb), PAINT, a)
    # stiffening ribs inside, so it looks right off the rack
    for zz in (-0.18, 0.18):
        D.box("side_rib", (min(xo - sx * 0.012, xo - sx * 0.0015), y0 + 0.05, zz - 0.010), (max(xo - sx * 0.012, xo - sx * 0.0015), y1 - 0.05, zz + 0.010),
              PAINT, a)
    for zz in (z0 + 0.10, z1 - 0.10):   # latches with key locks, near the top
        lf = P.Frame((xo + sx * 0.0002, y1 - 0.060, zz), (sx, 0, 0), Y)
        P.slab("side_latch", P.rrect(0.024, 0.040, 0.006), 0.004, "black_plastic", lf.sub(0, 0, 0.002), parent=a)
        P.cylinder("side_lock", lf.sub(0, 0.006, 0.004), 0.0045, 0.002, "nickel", 14, a)
    P.slab("side_grip", P.rrect(0.120, 0.030, 0.010), 0.003, "black_plastic", P.Frame((xo + sx * 0.0002, y0 + 0.95 * (y1 - y0) / 2, 0.0), (sx, 0, 0), Y).sub(0, 0, 0.0015),
           parent=a)
    return a


def caster(fr_pos, root, swivel=True, wheel_r=0.025, h=0.065):
    """A plate caster: the mounting plate, the swivel yoke, a black wheel on its axle."""
    x, y, z = fr_pos
    D.box("caster_plate", (x - 0.030, h - 0.004, z - 0.030), (x + 0.030, h, z + 0.030), "steel", root)
    P.cylinder("caster_swivel", P.Frame((x, h - 0.008, z), Y, Z), 0.018, 0.008, "steel", 16, root, z0=-0.004)
    for sx in (-1, 1):
        D.xslab("caster_yoke", "steel", [(z - 0.012, h - 0.012), (z + 0.016, h - 0.012), (z + 0.010, wheel_r), (z - 0.004, wheel_r - 0.010)],
                x + sx * 0.0135, x + sx * 0.0155, (), root)
    P.cylinder("caster_wheel", P.Frame((x, wheel_r, z + 0.003), X, Y), wheel_r, 0.020, "rubber", 18, root)
    P.cylinder("caster_hub", P.Frame((x, wheel_r, z + 0.003), X, Y), wheel_r * 0.45, 0.0215, "grey_plastic", 12, root)
    P.cylinder("caster_axle", P.Frame((x, wheel_r, z + 0.003), X, Y), 0.0035, 0.032, "steel", 8, root)


def leveller(pos, root, top):
    """A levelling foot: a threaded rod from the base frame and a rubber-padded foot, wound down to the floor."""
    x, y, z = pos
    P.cylinder("level_rod", P.Frame((x, 0.0, z), Y, Z), 0.0055, top, "steel", 10, root, z0=0.010)
    P.cylinder("level_nut", P.Frame((x, top - 0.012, z), Y, Z), 0.010, 0.010, "steel", 6, root)
    P.lathe("level_foot", [(0, 0.0), (0.022, 0.0), (0.022, 0.006), (0.016, 0.012), (0.006, 0.014), (0, 0.014)], "steel", P.Frame((x, 0.0, z), Y, Z), 18, root)
    P.cylinder("level_pad", P.Frame((x, 0.0, z), Y, Z), 0.0215, 0.003, "rubber", 18, root, z0=-0.0005)


def brush_strip(x0, x1, z0, z1, y, root, tag="rubber"):
    """A cable-entry brush: a frame round a slot with two rows of bristles meeting in the middle."""
    D.yslab("brush_frame", "black_plastic", D.rr(x0 - 0.010, x1 + 0.010, z0 - 0.010, z1 + 0.010, 0.004), y, y + 0.003,
            [D.rr(x0, x1, z0, z1, 0.003)], root)
    zm = (z0 + z1) / 2
    for (za, zb) in ((z0, zm - 0.0008), (zm + 0.0008, z1)):
        D.yslab("brush_bristles", tag, D.rect(x0, x1, za, zb), y - 0.004, y + 0.0015, (), root)


# ====================================================================== builds

def frame_42(st, root):
    W, Dp, H = st["W"], st["Dp"], st["H"]
    hw, hd = W / 2, Dp / 2
    zf = hd - 0.020      # the frame's front face (the door sits in front of it)
    zb = -hd + 0.020
    p = 0.030
    # corner posts (folded profiles) and the top and bottom frames
    for sx in (-1, 1):
        for zz in (zf, zb):
            za, zbb = sorted((zz, zz - math.copysign(p, zz)))
            D.box("post", (min(sx * hw, sx * (hw - p)), 0.065, za), (max(sx * hw, sx * (hw - p)), H - 0.025, zbb), PAINT, root, bevel=0.002, seg=1)
    for yy in (0.065, H - 0.055):
        for sx in (-1, 1):
            D.box("frame_depth", (min(sx * hw, sx * (hw - p)), yy, zb), (max(sx * hw, sx * (hw - p)), yy + p, zf), PAINT, root)
        for zz in (zf, zb):
            za, zbb = sorted((zz, zz - math.copysign(p, zz)))
            D.box("frame_width", (-hw + p, yy, za), (hw - p, yy + p, zbb), PAINT, root)
    # rail support beams (depth members the rails bolt to), top and bottom
    for yy in (st["y0"] - 0.025, st["y0"] + st["units"] * D.U + 0.010):
        for sx in (-1, 1):
            D.box("rail_beam", (min(sx * 0.253, sx * 0.272), yy, st["zm"] - MOUNT_DEPTH - 0.06), (max(sx * 0.253, sx * 0.272), yy + 0.020, st["zm"] - 0.002),
                  PAINT, root)
    # roof: a shallow tray with two brush cable entries and a fan blanking plate
    D.box("roof", (-hw, H - 0.025, -hd + 0.002), (hw, H - 0.002, hd - 0.002), PAINT, root, bevel=0.003, seg=1)
    brush_strip(-0.20, 0.20, -0.42, -0.36, H - 0.0045, root)
    brush_strip(-0.20, 0.20, 0.30, 0.34, H - 0.0045, root)
    D.yslab("roof_plate", PAINT, D.rr(-0.13, 0.13, -0.15, 0.15, 0.01), H - 0.002, H, [], root)
    for k in range(4):
        P.cylinder("roof_screw", P.Frame((-0.12 + 0.24 * (k % 2), H, -0.14 + 0.28 * (k // 2)), Y, Z), 0.004, 0.0015, "steel", 8, root, z0=0.0)
    # bottom panel with the floor cable entry, base plinth
    D.yslab("floor_panel", PAINT, D.rect(-hw + p, hw - p, zb + p, zf - p), 0.065, 0.067, [D.rr(-0.20, 0.20, -0.42, -0.30, 0.01)], root)
    brush_strip(-0.19, 0.19, -0.41, -0.31, 0.0685, root)
    # casters and levelling feet at the four corners
    for sx in (-1, 1):
        for sz in (-1, 1):
            caster((sx * 0.235, 0, sz * 0.455), root)
            leveller((sx * 0.255, 0, sz * 0.395), root, 0.075)
    # earth stud and the rating label inside the rear frame
    D.decal("rating", ATLAS, "rating", P.Frame((-hw + p + 0.0002, 1.70, -0.10), X, Y), 0.16, 0.10, root)
    D.decal("earth", ATLAS, "earth", P.Frame((-hw + p + 0.0002, 0.20, zb + 0.06), X, Y), 0.025, 0.025, root)
    P.cylinder("earth_stud", P.Frame((-hw + p, 0.17, zb + 0.06), X, Y), 0.004, 0.012, "nickel", 6, root, z0=0.0)


def doors_42(st, root):
    W, Dp, H = st["W"], st["Dp"], st["H"]
    hw, hd = W / 2, Dp / 2
    y0, y1 = 0.070, H - 0.030
    # front door: hinged on -x (a negative turn about +y swings its +x edge out to +z)
    hx = -hw + 0.004
    a = P.anchor("A_DOOR_FRONT_0", P.Frame((hx, (y0 + y1) / 2, hd - 0.010), Z, Y), (W, y1 - y0, 0.020), root,
                 meta="hinge=y,open=-110,lock=1,handle=A_HANDLE_0")
    hy = perforated_door("A_DOOR_FRONT_0", -hw + 0.002, hw - 0.002, y0, y1, hd, a, hx, hw - 0.040)
    P.anchor("A_HANDLE_0", P.Frame((hw - 0.040, hy - 0.035, hd + 0.016), Z, Y), (0.020, 0.100, 0.020), a, meta="turn=90,lock=1")
    D.decal("badge", ATLAS, "badge", P.Frame((0.0, y1 - 0.034, hd + 0.0001), Z, Y), 0.12, 0.015, a)
    # rear doors: two leaves, hinged at the outer edges
    for k, sx in enumerate((-1, 1)):
        hx = sx * (hw - 0.004)
        a = P.anchor(f"A_DOOR_REAR_{k}", P.Frame((hx, (y0 + y1) / 2, -hd + 0.010), Z, Y), (hw, y1 - y0, 0.020), root,
                     meta=f"hinge=y,open={110 if sx < 0 else -110},lock={1 if k == 1 else 0},leaf={k}")
        xa, xb = sorted((sx * (hw - 0.002), sx * 0.002))
        # build the leaf facing -z: mirror by building in a frame turned round y
        _rear_leaf(xa, xb, y0, y1, -hd, a, hx, -sx * 0.035)


def _rear_leaf(x0, x1, y0, y1, z_out, a, hinge_x, handle_dx):
    """A rear door leaf (its outside faces -z)."""
    t = 0.020
    zi = z_out + t
    m = 0.035
    D.zslab("rdoor_face", PAINT, D.rr(x0, x1, y0, y1, 0.004), z_out, z_out + 0.0015, [D.rect(x0 + m, x1 - m, y0 + m * 1.6, y1 - m * 1.6)], a)
    for (xa, xb, ya, yb) in ((x0, x0 + 0.003, y0, y1), (x1 - 0.003, x1, y0, y1), (x0, x1, y0, y0 + 0.003), (x0, x1, y1 - 0.003, y1)):
        D.box("rdoor_edge", (xa, ya, z_out + 0.0015), (xb, yb, zi), PAINT, a)
    for (xa, xb, ya, yb) in ((x0 + 0.003, x0 + m, y0 + 0.003, y1 - 0.003), (x1 - m, x1 - 0.003, y0 + 0.003, y1 - 0.003),
                             (x0 + m, x1 - m, y0 + 0.003, y0 + m * 1.6), (x0 + m, x1 - m, y1 - m * 1.6, y1 - 0.003)):
        D.box("rdoor_return", (xa, ya, zi - 0.0012), (xb, yb, zi), PAINT, a)
    pw, ph = (x1 - x0) - 2 * m, (y1 - y0) - 3.2 * m
    D.tiled_quads("rdoor_perf", "tex_rack_perf", P.Frame(((x0 + x1) / 2, (y0 + y1) / 2, z_out + 0.0010), NZ, Y), pw + 0.002, ph + 0.002,
                  0.1, 0.1, a, back=True)
    for yy in (y0 + 0.12, (y0 + y1) / 2, y1 - 0.12):
        P.cylinder("rdoor_hinge", P.Frame((hinge_x, yy, z_out + 0.010), Y, Z), 0.0055, 0.060, "steel_dark", 12, a)
    hx = (x0 + x1) / 2 + (x1 - x0) / 2 * (1 if handle_dx > 0 else -1) - handle_dx * 0.4
    hy = (y0 + y1) / 2 + 0.05
    D.zslab("rhandle_housing", "black_plastic", D.rr(hx - 0.014, hx + 0.014, hy - 0.070, hy + 0.030, 0.006), z_out - 0.005, z_out, (), a)
    D.zslab("rhandle_lever", "black_plastic", D.rr(hx - 0.008, hx + 0.008, hy - 0.062, hy + 0.008, 0.004), z_out - 0.013, z_out - 0.005, (), a)


def pdu_places(st, root):
    """Zero-U PDU positions in the rear side channels (outlets facing the rear door)."""
    for k, sx in enumerate((-1, 1)):
        P.anchor(f"A_PDU_{k}", P.Frame((sx * 0.270, 0.120, st["zm"] - MOUNT_DEPTH - 0.115), NZ, Y), (0.056, 1.80, 0.044), root,
                 meta=f"zeroU=1,len=1.80,side={'l' if sx < 0 else 'r'},mount=buttons,model=pdu_0u")
        # the mounting brackets (keyhole tabs) on the channel's beam at the PDU's button heights
        for yy in (0.32, 1.72):
            D.box("pdu_bracket", (sx * 0.255 - 0.002, yy - 0.020, st["zm"] - MOUNT_DEPTH - 0.095), (sx * 0.255 + 0.002, yy + 0.020, st["zm"] - MOUNT_DEPTH - 0.060),
                  "steel", root)
        D.box("pdu_channel", (min(sx * 0.255, sx * 0.272), 0.10, st["zm"] - MOUNT_DEPTH - 0.095), (max(sx * 0.255, sx * 0.272), 1.95, st["zm"] - MOUNT_DEPTH - 0.075),
              PAINT, root)


def frame_open(st, root):
    """The open frame: the four posts are the rails (in rail()); top and bottom frames join them, castors under."""
    W, Dp, H = st["W"], st["Dp"], st["H"]
    zf, zr = st["zm"], st["zm"] - MOUNT_DEPTH
    y_lo = st["y0"] - 0.045
    y_hi = st["y0"] + st["units"] * D.U + 0.008
    for (ya, yb) in ((y_lo, y_lo + 0.035), (y_hi, y_hi + 0.035)):
        # side rails along z (box section) and cross members along x
        for sx in (-1, 1):
            D.box("frame_side", (min(sx * 0.253, sx * 0.280), ya, zr - 0.050), (max(sx * 0.253, sx * 0.280), yb, zf - 0.002), PAINT, root, bevel=0.002, seg=1)
        for zz in (zf - 0.028, zr + 0.028):
            D.box("frame_cross", (-0.253, ya + 0.004, zz - 0.012), (0.253, yb - 0.004, zz + 0.012), PAINT, root, bevel=0.002, seg=1)
    # gussets at the post feet and the castors under the bottom frame
    for sx in (-1, 1):
        for zz in (zf - 0.025, zr + 0.025):
            D.box("caster_mount", (sx * 0.2665 - 0.030, y_lo - 0.004, zz - 0.030), (sx * 0.2665 + 0.030, y_lo, zz + 0.030), "steel", root)
            caster((sx * 0.2665, 0, zz), root, h=y_lo - 0.004, wheel_r=0.022)
    # a cable tie bar across the back, the earth stud and the label
    D.box("tie_bar", (-0.252, y_hi - 0.060, zr - 0.0068), (0.252, y_hi - 0.040, zr - 0.0020), "steel", root)
    for k in range(9):
        D.box("tie_slot", (-0.2 + k * 0.05 - 0.004, y_hi - 0.0555, zr - 0.0070), (-0.2 + k * 0.05 + 0.004, y_hi - 0.0445, zr - 0.0066), "dark_plastic", root)
    P.cylinder("earth_stud", P.Frame((-0.2665, y_lo + 0.02, zr - 0.04), X, Y), 0.004, 0.012, "nickel", 6, root, z0=0.0)
    D.decal("earth", ATLAS, "earth", P.Frame((-0.2802, y_lo + 0.018, zr - 0.010), NX, Y), 0.022, 0.022, root)


def build(rid):
    P.reset()
    textures()
    st = STYLES[rid]
    root = c.root(rid)
    D.ROOT[0] = root
    enclosed = st["enclosed"]
    for sx in (-1, 1):
        rail(st, root, sx, True, enclosed)
        rail(st, root, sx, False, enclosed)
    if enclosed:
        frame_42(st, root)
        doors_42(st, root)
        for k in range(2):
            side_panel(st, k, root)
        pdu_places(st, root)
    else:
        frame_open(st, root)
    for n in range(st["units"]):
        P.anchor(f"A_RACKU_{n}", P.Frame((0, st["y0"] + n * D.U, st["zm"]), Z, Y), (D.EAR_W, D.U, MOUNT_DEPTH), root,
                 meta=f"u={n + 1},pitch={D.U},depth={MOUNT_DEPTH},extends=-z,base=bottom,rear={-MOUNT_DEPTH}")
    W, Dp, H = st["W"], st["Dp"], st["H"]
    if enclosed:
        P.anchor("A_HIT_0", (0, H / 2, 0), (W, H, Dp), root)
    else:
        zf, zr = st["zm"], st["zm"] - MOUNT_DEPTH
        for k, sx in enumerate((-1, 1)):
            P.anchor(f"A_HIT_{k}", (sx * 0.262, H / 2, (zf + zr) / 2), (0.040, H, zf - zr + 0.06), root)
        P.anchor("A_HIT_2", (0, 0.07, (zf + zr) / 2), (W, 0.07, zf - zr + 0.06), root)
    extra = (f"frame: floor at y=0, footprint centred; front mounting plane z={st['zm']}, rear rails' rear face z={st['zm'] - MOUNT_DEPTH - 0.002:.3f}; "
             f"U1 bottom y={st['y0']}, top of U{st['units']} y={st['y0'] + st['units'] * D.U:.4f}")
    if enclosed:
        views = dict(preview_views=((30, 15), (150, 20)), beauty_views=((28, 12), (155, 15)), fill=2.5,
                     more_beauty=[(((25, 10),), dict(pose=[("A_DOOR_FRONT_0", "y", -110), ("A_DOOR_REAR_0", "y", 110), ("A_DOOR_REAR_1", "y", -110)],
                                                      hide=("@A_PANEL_SIDE_1",))),
                                  (((-25, 5),), dict(target=(0.20, 1.0, st["zm"]), dist=0.45, hide=("@A_DOOR_FRONT_0",))),
                                  (((160, 12),), dict(pose=[("A_DOOR_REAR_0", "y", 110), ("A_DOOR_REAR_1", "y", -110)]))])
    else:
        views = dict(preview_views=((30, 18), (150, 22)), beauty_views=((30, 15), (150, 18)), fill=2.5,
                     more_beauty=[(((-20, 5),), dict(target=(0.2, 0.35, st["zm"]), dist=0.45))])
    return D.finish(root, rid, size=(900, 1000) if enclosed else (1000, 800), samples=36, extra=extra, **views)
