"""
build_cooler.py - CPU coolers cooler_stock (Wraith-style: round-cornered plastic shroud, top fan, aluminium radial
fin core round a copper slug, pre-applied paste, four spring screws) and cooler_tower (120 mm single tower: 45
thin fins, four U-bent nickel-plated heat pipes, nickel base with a protective film, a fan on wire clips, a top
cover with the brand). Run: blender -b --factory-startup -P Tools/Blender/build_cooler.py -- [cooler_stock] [cooler_tower]

Frame (as PartFactory.BuildCooler): origin at the centre of the base contact face, +z away from the board,
x towards the board's rear I/O edge, y towards its top edge. The mounting screws sit on the board's cooler
holes at (+-0.033, +-0.033).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import parts_fan as pf  # noqa: E402
from mathutils import Matrix, Vector as V  # noqa: E402

M_XZ = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))  # 2D (x, z) -> extruded along y
M_YZ = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0)))  # 2D (y, z) -> extruded along x
HOLES = [(sx * 0.033, sy * 0.033) for sx in (1, -1) for sy in (1, -1)]
Z_BOARD = -0.0075  # board surface below the IHS top (CPU + socket)


def box(m, tag, lo, hi, bevel=0.0):
    lo, hi = V(lo), V(hi)
    m.add(tag, pb.g_box(tuple(hi - lo), bevel), None, (lo + hi) / 2)


def spring_screw(m, i, x, y, z_seat, z_head, head_r=0.0035, spring_r=0.0029, tag="steel"):
    """A captive spring screw: the spring (static) from the seat to the head, the screw (head + shank down into the
    backplate) as a moving piece of A_SCREW_PH2_<i>. Returns the anchor."""
    a = m.anchor(f"A_SCREW_PH2_{i}", (x, y, z_head + 0.0018), (0.009, 0.009, 0.012), forward=(0, 0, 1), up=(0, 1, 0),
                 meta="spring=1,thread=M3,turns=8")
    turns = max(3.0, (z_head - z_seat) / 0.0011)
    m.add("steel", pb.g_helix(spring_r, 0.00038, z_seat + 0.0002, z_head - 0.0002, turns, 8, 14), None, (x, y, 0))
    sc = m.piece(a, tag, "screw")
    sc.add(pb.g_screw_head(head_r, 0.0018, "ph", 24), None, (x, y, z_head))
    L = z_head - (Z_BOARD - 0.0025)
    sc.add(pb.g_cyl(0.0015, L, 14), None, (x, y, z_head - L / 2))
    sc.add(pb.g_cyl(0.0013, 0.002, 14, r2=0.0006), None, (x, y, z_head - L - 0.001))
    # washer under the head
    sc.add(pb.g_ring(0.0016, 0.0034, 0.0004, 20), None, (x, y, z_head - 0.0002))
    return a


def fan_plug(m, face, back_dir, up, cable_from, cable_pts, tag="connector_black"):
    """A 4-pin PWM fan plug resting loose at 'face' (contact face centre), its +z (back_dir) pointing back along
    the cable, which runs (static) from cable_from through cable_pts into the plug."""
    a = m.anchor("A_PLUG_FAN_0", face, (0.012, 0.008, 0.016), forward=back_dir, up=up,
                 meta="kind=fan4,frame=plug,target=CPU_FAN")
    M = pb.frame(back_dir, up)
    t = V(face)
    pl = m.piece(a, tag, "plug")
    holes = [pb.rect2((k - 1.5) * 0.00254, -0.0004, 0.0012, 0.0012) for k in range(4)]
    pl.add(pb.g_slab(pb.rrect2(0, 0, 0.0101, 0.0058, 0.0005, 2), holes, 0.0025, 0.0), M, t)
    pl.add(pb.g_box((0.0101, 0.0058, 0.0110), 0.0003), M, t + M @ V((0, 0, 0.0080)))
    pl.add(pb.g_box((0.0050, 0.0012, 0.0045)), M, t + M @ V((0, 0.0034, 0.0035)))  # friction ramp
    for k in (-1, 1):
        pl.add(pb.g_box((0.0007, 0.0010, 0.0115)), M, t + M @ V((k * 0.0042, 0.0033, 0.0075)))  # key ribs
    for k in range(4):
        pl.add(pb.g_box((0.0007, 0.0007, 0.0018)), M, t + M @ V(((k - 1.5) * 0.00254, -0.0004, 0.0012)))
    pts = [V(cable_from)] + [V(p) for p in cable_pts] + [t + M @ V((0, 0, 0.0185)), t + M @ V((0, 0, 0.0120))]
    m.add("black_plastic", pb.g_sweep(pb.fillet_path(pts, 0.006, 6), 0.0013, 10))
    return a


# ====================================================================== stock cooler

def tex_stock():
    at = pb.Atlas(1024, 512)
    at.add("hub", 0, 0, 512, 512)
    at.add("top", 512, 0, 512, 128)
    cv = pb.Canvas(1024, 512, bg="#0d0d0e")
    cx, cy = 256, 256
    cv.circle(cx, cy, 252, "#151517")
    cv.ring(cx, cy, 226, 236, "#d2232a")
    # a spiral swirl emblem
    for k in range(3):
        a0 = k * 120
        pts = []
        for j in range(25):
            a = (a0 + j * 4.8) * pb.DEG
            r = 40 + j * 2.6
            pts.append((cx + math.cos(a) * r, cy - 40 + math.sin(a) * r * 0.55))
        for j in range(24, -1, -1):
            a = (a0 + j * 4.8) * pb.DEG
            r = 40 + j * 2.6 - 10 - j * 0.35
            pts.append((cx + math.cos(a) * r, cy - 40 + math.sin(a) * r * 0.55))
        cv.poly(pts, "#e9e9ea" if k else "#d2232a")
    cv.text("SPINNER", cx, cy + 84, 50, "#ececee", "eras", "center", "center", spacing=1.25)
    cv.text("COOLING", cx, cy + 140, 22, "#9a9ba0", "arialb", "center", "center", spacing=2.0)
    cv.rect(512, 0, 512, 128, "#101012")
    cv.text("SPINNER", 768, 64, 58, "#d8d9dc", "eras", "center", "center", spacing=1.3)
    cv.render("cooler_stock")
    return at


def build_stock():
    pid = "cooler_stock"
    at = tex_stock()
    m = pb.Model(pid)
    TEX = "tex_" + pid
    # copper slug: the contact face and a core up the middle of the extrusion
    m.add("copper", pb.g_lathe([(0.0, 0.0), (0.0175, 0.0), (0.0175, 0.0060), (0.0150, 0.0070), (0.0150, 0.0300),
                                (0.0, 0.0300)], 64))
    # aluminium extrusion: hub and base ring, 44 curved radial fins with a stepped outer bottom
    m.add("alu", pb.g_lathe([(0.0175, 0.0004), (0.0205, 0.0004), (0.0205, 0.0335), (0.0150, 0.0335),
                             (0.0150, 0.0070), (0.0175, 0.0060), (0.0175, 0.0004)], 64))
    n = 44
    prof = [(0.0198, 0.0010), (0.0300, 0.0010), (0.0345, 0.0045), (0.0420, 0.0060), (0.0420, 0.0335),
            (0.0198, 0.0335)]
    for k in range(n):
        th0 = pb.TAU * k / n
        verts, faces, uvs, fl = pb.g_slab(prof, [], 0.0008, -0.0004)
        out = []
        for p in verts:
            rr, zz, w = p.x, p.y, p.z
            th = th0 + 7.0 * (rr - 0.0198)  # swept fins
            out.append(V((rr * math.cos(th) + w * math.sin(th), rr * math.sin(th) - w * math.cos(th), zz)))
        m.add("alu", (out, faces, None, fl))
    # shroud: rounded-square top with the fan opening and screw wells, a skirt, the wells
    S = 0.100
    fan_d = 0.078
    top_holes = [pb.circle2(0, 0, fan_d / 2 + 0.0015, 96)] + [pb.circle2(x, y, 0.0042, 20) for (x, y) in HOLES]
    sh = m.mb("black_plastic")
    sh.add(pb.g_slab(pb.rrect2(0, 0, S, S, 0.020, 6), top_holes, 0.0025, 0.0505, bevel=0.0010))
    sh.add(pb.g_slab(pb.rrect2(0, 0, S, S, 0.020, 6), [pb.rrect2(0, 0, S - 0.003, S - 0.003, 0.0185, 6)], 0.0153,
                     0.0354, bevel=0.0004))
    # moulded ribs round the skirt bottom (stiffening lip) and a groove line
    sh.add(pb.g_slab(pb.rrect2(0, 0, S + 0.0012, S + 0.0012, 0.0206, 6), [pb.rrect2(0, 0, S - 0.003, S - 0.003, 0.0185, 6)],
                     0.0018, 0.0354, bevel=0.0004))
    for (x, y) in HOLES:
        sh.add(pb.g_ring(0.0042, 0.0055, 0.0325, 24), None, (x, y, 0.0185 + 0.0325 / 2))
        sh.add(pb.g_ring(0.0017, 0.0055, 0.0015, 24), None, (x, y, 0.0185 + 0.00075))  # spring seat
        # web from the well to the skirt corner
        d = V((x, y, 0)).normalized()
        sh.add(pb.xf(pb.g_box((0.010, 0.0016, 0.014)), pb.rot("z", math.atan2(y, x)),
                     V((x, y, 0)) + d * 0.0095 + V((0, 0, 0.0435))))
    # a raised ring round the fan opening and a lip on the skirt bottom
    sh.add(pb.g_lathe([(fan_d / 2 + 0.0015, 0.0528), (fan_d / 2 + 0.0045, 0.0528), (fan_d / 2 + 0.0040, 0.0538),
                       (fan_d / 2 + 0.0020, 0.0538), (fan_d / 2 + 0.0015, 0.0528)], 96))
    # embossed brand on the +x side of the skirt
    m.add("grey_plastic", pb.g_text("SPINNER", "eras", 0.0055, 0.060, 0.00015, spacing=1.25),
          pb.label_frame((1, 0, 0), (0, 0, 1)), (S / 2 + 0.00002, 0.0, 0.0440))
    # fan (frameless, 7 blades) sitting in the shroud
    fz = 0.0515 - 0.007
    fa = m.anchor("A_FAN_0", (0, 0, fz), (fan_d, fan_d, 0.014), forward=(0, 0, 1), up=(0, 1, 0),
                  meta=pf.fan_meta("ccw", 2800))
    pf.make_fan(fa, diameter=fan_d, thickness=0.014, blades=7, frame=False, sticker=pid, sticker_uv=at.uv("hub"),
                struts=3, name="stockfan", cov=(0.72, 1.0), sweep=0.45)
    # spring screws
    for i, (x, y) in enumerate(HOLES):
        spring_screw(m, i, x, y, 0.0200, 0.0262)
    # pre-applied paste square (moving piece: it can be wiped)
    pa = m.anchor("A_PASTE_PRE_0", (0, 0, 0), (0.030, 0.030, 0.004), forward=(0, 0, -1), up=(0, 1, 0),
                  meta="kind=preapplied,area=0.028x0.028")
    m.piece(pa, "paste", "paste").add(pb.g_slab(pb.rrect2(0, 0, 0.028, 0.028, 0.0025, 4), [], 0.00018, -0.00018,
                                                bevel=0.00006))
    # fan cable: motor -> along the +y strut -> out through the skirt -> to the plug
    fan_plug(m, (0.010, 0.080, 0.004), (0, -1, 0), (0, 0, 1), (0.0, 0.006, fz - 0.0065),
             [(0.0, 0.041, fz - 0.0065), (0.0, 0.051, fz - 0.009), (0.002, 0.054, 0.024), (0.008, 0.060, 0.008)])
    m.anchor("A_HIT_0", (0, 0, 0.027), (S, S, 0.054))
    m.anchor("A_HIT_1", (0, 0, 0.003), (0.036, 0.036, 0.006))
    m.finish()
    m.report()
    m.export()
    pb.preview_textures()
    pb.shots(m.root, pid, [
        dict(yaw=30, pitch=45), dict(yaw=200, pitch=20), dict(yaw=20, pitch=-60),
        dict(yaw=0, pitch=88, dist=0.25), dict(yaw=60, pitch=25, target=(0.033, 0.033, 0.03), dist=0.09),
        dict(yaw=160, pitch=-15, target=(0.0, 0.0, 0.01), dist=0.16),
    ])
    return m


# ====================================================================== tower cooler

FIN_X = 0.025  # half depth (air goes -x -> +x)
FIN_Y = 0.0625  # half width
FIN_Z0, FIN_PITCH, FIN_N = 0.0400, 0.0025, 45
PIPES = [(-0.0105, 0.050, -0.0105), (-0.0035, 0.024, -0.0105), (0.0035, 0.037, 0.0105), (0.0105, 0.058, 0.0105)]
# (x in the base, leg y, leg x in the fin stack)


def tex_tower():
    at = pb.Atlas(2048, 1024)
    at.add("top", 0, 0, 1024, 256)
    at.add("hub", 1024, 0, 512, 512)
    at.add("film", 1536, 0, 512, 512)
    at.add("tab", 1536, 512, 256, 128)
    at.add("blue", 1792, 512, 64, 64)
    cv = pb.Canvas(2048, 1024, bg="#0d0d0e")
    # top cover insert: brushed-dark plate, mountain emblem, FROSTPEAK
    cv.rect(0, 0, 1024, 256, "#121315")
    cv.poly([(70, 196), (150, 66), (192, 130), (222, 96), (296, 196)], "#dfe6ee")
    cv.poly([(150, 66), (172, 102), (160, 112), (148, 96), (134, 116), (128, 102)], "#7fb6e6")
    cv.text("FROSTPEAK", 330, 120, 74, "#eef1f5", "eras", "left", "center", spacing=1.2, maxw=640)
    cv.text("TOWER 120", 334, 196, 30, "#7fb6e6", "arialb", "left", "center", spacing=1.8)
    # fan hub sticker
    hx, hy = 1024 + 256, 256
    cv.circle(hx, hy, 252, "#141518")
    cv.ring(hx, hy, 226, 236, "#7fb6e6")
    cv.poly([(hx - 120, hy + 50), (hx - 40, hy - 90), (hx + 2, hy - 20), (hx + 34, hy - 60), (hx + 120, hy + 50)],
            "#e6ecf2")
    cv.text("FROSTPEAK", hx, hy + 110, 40, "#e6ecf2", "eras", "center", "center", spacing=1.2)
    # protective film: blue with white print
    fx, fy = 1536, 0
    cv.rect(fx, fy, 512, 512, "#3d8ee6")
    for k in range(9):
        cv.line(fx, fy + 40 + k * 60, fx + 512, fy - 60 + k * 60, 14, "#4a98ec")
    cv.text("REMOVE", fx + 256, fy + 180, 64, "#ffffff", "arialb", "center", "center")
    cv.text("BEFORE USE", fx + 256, fy + 270, 52, "#ffffff", "arialb", "center", "center")
    cv.text("FROSTPEAK", fx + 256, fy + 380, 30, "#e8f2ff", "eras", "center", "center", spacing=1.3)
    cv.rect(1536, 512, 256, 128, "#3d8ee6")
    cv.text("PEEL >", 1536 + 128, 512 + 64, 40, "#ffffff", "arialb", "center", "center")
    cv.rect(1792, 512, 64, 64, "#3d8ee6")
    cv.render("cooler_tower")
    return at


def fin_outline():
    """One fin in (x, y): a sawtooth intake edge (-x), clip notches on the sides near the intake."""
    pts = [(-FIN_X + 0.004, -FIN_Y), (-0.0200, -FIN_Y), (-0.0200, -FIN_Y + 0.0022), (-0.0170, -FIN_Y + 0.0022),
           (-0.0170, -FIN_Y), (FIN_X, -FIN_Y), (FIN_X, FIN_Y), (-0.0170, FIN_Y), (-0.0170, FIN_Y - 0.0022),
           (-0.0200, FIN_Y - 0.0022), (-0.0200, FIN_Y), (-FIN_X + 0.004, FIN_Y)]
    # sawtooth intake edge from +y to -y
    n = 10
    for k in range(1, 2 * n):
        y = FIN_Y - k * (2 * FIN_Y) / (2 * n)
        x = -FIN_X if k % 2 == 1 else -FIN_X + 0.004
        pts.append((x, y))
    return pts


def build_tower():
    pid = "cooler_tower"
    at = tex_tower()
    m = pb.Model(pid)
    TEX = "tex_" + pid
    # ---------------------------------------------------------------- base: nickel plate, pipe channels, cap
    box(m, "nickel", (-0.019, -0.020, 0.0), (0.019, 0.020, 0.0042), bevel=0.0004)
    box(m, "nickel", (-0.0150, -0.0195, 0.0042), (0.0150, 0.0195, 0.0068), bevel=0.0003)
    cap = pb.chamfer2(0, 0, 0.040, 0.034, 0.003)
    m.add("alu", pb.g_slab(cap, [], 0.0058, 0.0068, bevel=0.0004))
    for k in range(5):  # grooves on the cap
        box(m, "alu_dark", (-0.0195, -0.0150 + k * 0.0075, 0.0124), (0.0195, -0.0143 + k * 0.0075, 0.01265))
    # ---------------------------------------------------------------- heat pipes (6 mm, U-bent)
    z_top = FIN_Z0 + (FIN_N - 1) * FIN_PITCH + 0.0030
    yb = 0.0090
    for (xb, w, xl) in PIPES:
        half = [(xl, w, z_top), (xl, w, 0.036), (xb, w, 0.024), (xb, w, yb)]
        pts = [(p[0], -p[1], p[2]) for p in half] + list(reversed(half))
        path = pb.fillet_path(pts, 0.0095, 10)
        m.add("nickel", pb.g_sweep(path, 0.0030, 16))
        for sy in (-1, 1):  # crimped tips under the cover
            m.add("nickel", pb.g_cyl(0.0024, 0.0016, 16, r2=0.0012), None, (xl, sy * w, z_top + 0.0008))
    # ---------------------------------------------------------------- fins
    outline = fin_outline()
    for k in range(FIN_N):
        z = FIN_Z0 + k * FIN_PITCH
        m.add("alu", pb.g_slab(outline, [], 0.0004, z - 0.0002))
    # pipe collars on the top and bottom fins
    for (xb, w, xl) in PIPES:
        for sy in (-1, 1):
            for z in (FIN_Z0 - 0.0004, FIN_Z0 + (FIN_N - 1) * FIN_PITCH + 0.0004):
                m.add("alu", pb.g_ring(0.0030, 0.0036, 0.0008, 16), None, (xl, sy * w, z))
    # ---------------------------------------------------------------- top cover with the brand insert
    zc = FIN_Z0 + (FIN_N - 1) * FIN_PITCH + 0.0018
    cover = pb.chamfer2(0.0005, 0, 2 * FIN_X + 0.002, 2 * FIN_Y + 0.002, 0.006)
    holes = []
    for (xb, w, xl) in PIPES:
        for sy in (-1, 1):
            holes.append(pb.circle2(xl, sy * w, 0.0026, 16))
    m.add("paint_black", pb.g_slab(cover, holes, 0.0030, zc, bevel=0.0005))
    m.add("alu", pb.g_slab(pb.chamfer2(0.0005, 0, 2 * FIN_X - 0.004, 2 * FIN_Y - 0.004, 0.004),
                           [pb.chamfer2(0.0005, 0, 2 * FIN_X - 0.006, 2 * FIN_Y - 0.006, 0.0035)], 0.0004, zc + 0.0030))
    # reads upright in a tower (board +y up, the fan at the front): along -x
    m.add(TEX, pb.g_quad(0.046, 0.0115, at.uv("top")), pb.label_frame((0, 0, 1), (0, 1, 0)), (0.0005, 0.0, zc + 0.00305))
    # ---------------------------------------------------------------- mounting: X bracket with spring screws
    xb_poly = []
    arm = 0.0045
    for k, (hx, hy) in enumerate([(0.033, 0.033), (-0.033, 0.033), (-0.033, -0.033), (0.033, -0.033)]):
        d = V((hx, hy, 0)).normalized()
        p = V((-d.y, d.x, 0))
        tip = V((hx, hy, 0)) + d * 0.004
        xb_poly += [tuple(tip - p * arm)[:2], tuple(tip + p * arm)[:2]]
        nxt = math.atan2(hy, hx) + math.pi / 4
        xb_poly.append((math.cos(nxt) * 0.0120, math.sin(nxt) * 0.0120))
    xbh = [pb.circle2(x, y, 0.0018, 16) for (x, y) in HOLES]
    m.add("steel", pb.g_slab(xb_poly, xbh, 0.0015, 0.0126, bevel=0.0003))
    for i, (x, y) in enumerate(HOLES):
        spring_screw(m, i, x, y, 0.0141, 0.0196, head_r=0.0036, spring_r=0.0030)
    # ---------------------------------------------------------------- the protective film (moving piece)
    fa_ = m.anchor("A_FILM_0", (0, 0, 0), (0.044, 0.044, 0.003), forward=(0, 0, -1), up=(0, 1, 0),
                   meta="peel_from=+x,text=REMOVE BEFORE USE")
    fp = m.piece(fa_, TEX, "film")
    fp.add(pb.solid(pb.g_slab(pb.rect2(0, 0, 0.040, 0.042), [], 0.00012, -0.00013, back=False), at.uv("blue")))
    fp.add(pb.g_quad(0.040, 0.042, at.uv("film")), pb.label_frame((0, 0, -1), (0, 1, 0)), (0, 0, -0.000135))
    tab = [(0.0198, -0.006), (0.0235, -0.006), (0.0305, -0.004), (0.0305, 0.004), (0.0235, 0.006), (0.0198, 0.006)]
    fp.add(pb.solid(pb.g_slab(tab, [], 0.00012, -0.00013, back=False), at.uv("blue")))
    fp.add(pb.g_quad(0.010, 0.010, at.uv("tab")), pb.label_frame((0, 0, -1), (0, 1, 0)), (0.0252, 0, -0.000135))
    # ---------------------------------------------------------------- fan on wire clips
    fan_c = (-FIN_X - 0.0010 - 0.0125, 0.0, FIN_Z0 + (FIN_N - 1) * FIN_PITCH / 2)
    fa = m.anchor("A_FAN_0", fan_c, (0.12, 0.12, 0.025), forward=(-1, 0, 0), up=(0, 1, 0),
                  meta=pf.fan_meta("ccw", 1800))
    pf.make_fan(fa, diameter=0.12, thickness=0.025, blades=7, frame=True, sticker=pid, sticker_uv=at.uv("hub"),
                name="towerfan")
    xback = fan_c[0] + 0.0125
    for sy in (-1, 1):
        pts = [(xback - 0.004, sy * 0.0525, fan_c[2] + 0.0525), (xback + 0.002, sy * 0.0525, fan_c[2] + 0.0525),
               (-0.0185, sy * 0.0612, fan_c[2] + 0.046), (-0.0185, sy * 0.0612, fan_c[2] - 0.046),
               (xback + 0.002, sy * 0.0525, fan_c[2] - 0.0525), (xback - 0.004, sy * 0.0525, fan_c[2] - 0.0525)]
        m.add("steel", pb.g_sweep(pb.fillet_path(pts, 0.003, 6), 0.0006, 8))
    # fan cable: motor -> down the lower +y strut -> frame corner -> down to the plug beside the base
    mc = (xback - 0.0015, 0.0, fan_c[2])
    fan_plug(m, (-0.034, 0.090, 0.006), (0, -1, 0), (0, 0, 1), mc,
             [(xback - 0.0015, 0.040, fan_c[2] - 0.040), (xback - 0.0015, 0.0585, fan_c[2] - 0.0585),
              (xback - 0.004, 0.061, FIN_Z0 - 0.010), (-0.036, 0.064, 0.012)])
    # ---------------------------------------------------------------- hitboxes
    m.anchor("A_HIT_0", (0, 0, (FIN_Z0 + zc + 0.003) / 2), (2 * FIN_X, 2 * FIN_Y, zc + 0.003 - FIN_Z0 + 0.002))
    m.anchor("A_HIT_1", (fan_c[0], 0, fan_c[2]), (0.025, 0.12, 0.12))
    m.anchor("A_HIT_2", (0, 0, 0.012), (0.075, 0.075, 0.024))
    # the clear film over the top cover, inside the aluminium ring, over the brand (Logs/UNBOXING.md 1.4; anchor
    # only, the game builds the peel mesh)
    m.anchor("A_FILM_TOP_0", (0.0005, 0.0, zc + 0.0031), (0.040, 0.115, 0.001), forward=(0, 0, 1), up=(0, 1, 0),
             meta="film=clear,on=top_cover,peel_from=+x")
    m.finish()
    m.report()
    m.export()
    pb.preview_textures()
    pb.shots(m.root, pid, [
        dict(yaw=-50, pitch=20), dict(yaw=130, pitch=25), dict(yaw=90, pitch=10),
        dict(yaw=30, pitch=-40, target=(0, 0, 0.02), dist=0.2), dict(yaw=0, pitch=80, dist=0.4),
        dict(yaw=20, pitch=15, target=(0.0, 0.0, 0.03), dist=0.16),
    ])
    return m


BUILDERS = {"cooler_stock": build_stock, "cooler_tower": build_tower}

if __name__ == "__main__":
    ids = [a for a in c.args() if a in BUILDERS] or list(BUILDERS)
    for pid in ids:
        BUILDERS[pid]()
