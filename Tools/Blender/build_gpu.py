"""
build_gpu.py - graphics cards gpu_rx66 (dual fan, 200 mm, one PCIe 8-pin) and gpu_rx88 (triple fan, 300 mm,
12V-2x6). Run: blender -b --factory-startup -P Tools/Blender/build_gpu.py -- [gpu_rx66] [gpu_rx88]

Frame (as PartFactory.BuildGpu): origin at the PCIe contact edge (the top of the slot). The card runs from the
bracket at x = +0.095 towards -x, the cooler faces -y (down in a tower), the height runs along +z away from the
board. PCB: y -0.0018..-0.0002 (centre -0.001); gold fingers z -0.0052..-0.0012; backplate on +y.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import parts_fan as pf  # noqa: E402
from mathutils import Matrix, Vector as V  # noqa: E402

X0 = 0.095  # bracket end
M_XZ = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))  # 2D (x, z), extruded along y
M_YZ = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0)))  # 2D (y, z), extruded along x
M_XY = Matrix.Identity(3)  # 2D (x, y), extruded along z

PCB_Y0, PCB_Y1 = -0.0018, -0.0002
BP_Y0, BP_Y1 = 0.0012, 0.0027  # backplate
BR_X0, BR_X1 = 0.0955, 0.0965  # bracket plate
BR_YT, BR_YB = 0.0030, -0.0362  # bracket width: two slots
Z_TAB = 0.1065  # bracket tab top (same for every card: the case's slot rail)
SLOT_Y = (-0.0069, -0.0272)  # slot centres (screw positions)
X_SCREW = 0.1015
PORT_Y = -0.0046
PORT_Z = (0.018, 0.037, 0.056, 0.075)  # DP, DP, DP, HDMI

SPECS = {
    "gpu_rx66": dict(L=0.200, H=0.110, T=0.045, Hp=0.1035, fans=2, fan_d=0.085, blades=9, tip_ring=False,
                     power="pcie8", px=-0.058, model="RX 6600", mem="8GB GDDR6", pcb_end=-0.078, pipes=4,
                     pipe_tag="copper", xd=0.025, zd=0.055, bracket_tag="steel", back_tag="paint_black",
                     face_tag="black_plastic", over_tag="alu_dark", ring_tag="black_plastic",
                     logo_tag="paint_white", accent="#d8dadf", emblem="#d8dadf", vent="slots"),
    "gpu_rx88": dict(L=0.300, H=0.125, T=0.055, Hp=0.118, fans=3, fan_d=0.086, blades=11, tip_ring=True,
                     power="12v2x6", px=-0.055, model="RX 8800", mem="16GB GDDR6", pcb_end=-0.112, pipes=6,
                     pipe_tag="nickel", xd=0.020, zd=0.062, bracket_tag="paint_black", back_tag="alu_dark",
                     face_tag="alu_dark", over_tag="black_plastic", ring_tag="black_plastic",
                     logo_tag="alu", accent="#c8141e", emblem="#c8141e", vent="hex"),
}


# ====================================================================== artwork

def make_texture(pid, s):
    at = pb.Atlas(2048, 1024)
    at.add("logo", 0, 0, 1024, 128)
    at.add("plate", 0, 128, 1024, 128)
    at.add("hub", 1024, 0, 512, 512)
    at.add("label", 1536, 0, 512, 256)
    at.add("red", 1536, 256, 128, 128)
    at.add("pcb", 0, 512, 512, 512)
    cv = pb.Canvas(2048, 1024, bg="#0c0c0d")
    acc = s["accent"]

    def emblem(x, y, h, col, col2):
        # a stylised "V": two slanted blades, the right one split by a gap
        w = h * 0.9
        cv.poly([(x, y), (x + w * 0.28, y), (x + w * 0.52, y + h * 0.72), (x + w * 0.4, y + h)], col)
        cv.poly([(x + w * 0.62, y + h * 0.42), (x + w * 0.76, y), (x + w * 1.04, y), (x + w * 0.74, y + h * 0.62)], col2)

    # top-edge logo plate (1024 x 128): glossy black, emblem, VOLTRA, divider, model
    cv.rect(0, 0, 1024, 128, "#0a0a0b")
    cv.rect(0, 0, 1024, 3, "#2a2a2e")
    cv.rect(0, 125, 1024, 3, "#2a2a2e")
    emblem(40, 30, 68, acc, "#f0f0f2")
    cv.text("VOLTRA", 140, 64, 52, "#f2f2f4", "agency", "left", "center", spacing=1.35)
    cv.rect(420, 34, 3, 60, "#55565c")
    cv.text(s["model"], 450, 64, 40, "#c9cad0", "eras_md", "left", "center")
    cv.text("GAMING", 990, 64, 22, acc, "agency", "right", "center", spacing=1.5)
    # second plate (1024 x 128): small print for the bottom edge
    cv.rect(0, 128, 1024, 128, "#0a0a0b")
    cv.text("VOLTRA  |  " + s["model"] + "  |  " + s["mem"], 512, 192, 34, "#a8a9ae", "agency", "center", "center",
            spacing=1.3)
    # hub sticker (512 x 512)
    hx, hy = 1024 + 256, 256
    cv.rect(1024, 0, 512, 512, "#0b0b0c")
    cv.circle(hx, hy, 250, "#121214")
    cv.ring(hx, hy, 228, 236, "#6d6f76")
    emblem(hx - 82, hy - 120, 150, acc, "#e9e9ec")
    cv.text("VOLTRA", hx, hy + 120, 46, "#e9e9ec", "agency", "center", "center", spacing=1.4)
    # serial label (512 x 256)
    lx, ly = 1536, 0
    cv.rect(lx, ly, 512, 256, "#f1f1ee")
    cv.rect(lx + 10, ly + 10, 492, 236, "#f1f1ee")
    cv.text("VOLTRA", lx + 24, ly + 40, 30, "#111111", "agency", "left", "center", spacing=1.3)
    cv.text(s["model"] + " " + s["mem"], lx + 24, ly + 82, 20, "#111111", "arialb", "left", "center", maxw=300)
    pn = "VT-" + s["model"].replace(" ", "") + "-" + s["mem"][:2].strip("G") + "G"
    cv.text("P/N " + pn, lx + 24, ly + 116, 15, "#222222", "arial", "left", "center")
    sn = "S/N 2410" + ("66" if "66" in pid else "88") + "A0071942"
    cv.text(sn, lx + 24, ly + 140, 15, "#222222", "arial", "left", "center")
    cv.barcode(lx + 24, ly + 158, 290, 52, seed=sum(map(ord, pid)))
    cv.text("MADE IN TAIWAN", lx + 24, ly + 228, 13, "#333333", "arialb", "left", "center")
    # a QR-like code
    import random
    rng = random.Random(7 if "66" in pid else 9)
    qx, qy, q = lx + 352, ly + 40, 8
    cells = []
    for i in range(17):
        for j in range(17):
            corner = (i < 5 and j < 5) or (i > 11 and j < 5) or (i < 5 and j > 11)
            if corner:
                continue
            if rng.random() < 0.5:
                cells.append((qx + i * q, qy + j * q, q, q))
    cv.rects(cells, "#111111")
    for (ix, iy) in ((0, 0), (12, 0), (0, 12)):
        cv.frame_rect(qx + ix * q, qy + iy * q, 5 * q, 5 * q, q, "#111111")
        cv.rect(qx + ix * q + 2 * q, qy + iy * q + 2 * q, q, q, "#111111")
    cv.text("CE  FC  UKCA", lx + 390, ly + 205, 14, "#333333", "arialb", "center", "center")
    # accent swatch
    cv.rect(1536, 256, 128, 128, "#c8141e")
    # PCB back (512 x 512): dark solder mask, traces, pads, silkscreen
    px0, py0 = 0, 512
    cv.rect(px0, py0, 512, 512, "#101315")
    rng = random.Random(3)
    tr = []
    for k in range(70):
        x = px0 + rng.uniform(10, 500)
        y = py0 + rng.uniform(10, 500)
        if rng.random() < 0.5:
            tr.append((x, y, rng.uniform(30, 160), 2.2))
        else:
            tr.append((x, y, 2.2, rng.uniform(30, 160)))
    cv.rects([(x, y, min(w, px0 + 510 - x), min(h, py0 + 510 - y)) for (x, y, w, h) in tr], "#1b2125")
    vias = [(px0 + rng.uniform(8, 504), py0 + rng.uniform(8, 504), 5, 5) for _ in range(160)]
    cv.rects(vias, "#3a3f42")
    cv.frame_rect(px0 + 116, py0 + 116, 280, 280, 3, "#d9d9d6")
    cv.text("U1", px0 + 128, py0 + 136, 16, "#d9d9d6", "arialb", "left", "center")
    for k in range(12):
        cv.text(f"C{1201 + k}", px0 + 30 + (k % 4) * 120, py0 + 40 + (k // 4) * 200, 11, "#c9c9c6", "arial",
                "left", "center")
    cv.render(pid)
    return at


# ====================================================================== helpers

def slab_xz(m, tag, outline, holes, y0, depth, bevel=0.0, uv=None):
    m.add(tag, pb.g_slab(outline, holes, depth, y0, bevel=bevel, uv_rect=uv), M_XZ)


def slab_yz(m, tag, outline, holes, x0, depth, bevel=0.0):
    m.add(tag, pb.g_slab(outline, holes, depth, x0, bevel=bevel), M_YZ)


def slab_xy(m, tag, outline, holes, z0, depth, bevel=0.0):
    m.add(tag, pb.g_slab(outline, holes, depth, z0, bevel=bevel), M_XY)


def box(m, tag, lo, hi, bevel=0.0):
    lo, hi = V(lo), V(hi)
    m.add(tag, pb.g_box(tuple(hi - lo), bevel), None, (lo + hi) / 2)


def hex_grid(x0, y0, x1, y1, r, gap):
    """Hexagon holes (flat-topped) filling a rectangle, as 2D loops."""
    out = []
    w = math.sqrt(3) * r
    dx = w + gap
    dy = 1.5 * r + gap * 0.87
    j = 0
    y = y0 + r
    while y + r <= y1 + 1e-9:
        x = x0 + w / 2 + (dx / 2 if j % 2 else 0)
        while x + w / 2 <= x1 + 1e-9:
            out.append(pb.hexagon2(x, y, r, math.pi / 6))
            x += dx
        y += dy
        j += 1
    return out


def dp_shape(cy, cz, grow=0.0):
    """DisplayPort outline in (y, z): 16.1 x 4.8 mm with ONE chamfered corner (on the -y side)."""
    w, h = 0.0050 + 2 * grow, 0.0163 + 2 * grow
    return pb.chamfer2(cy, cz, w, h, (0.0003, 0.0003, 0.0003, 0.0019 + grow * 0.5))


def hdmi_shape(cy, cz, grow=0.0):
    """HDMI type A in (y, z): 14 x 4.55 mm, the two corners on the -y side chamfered."""
    w, h = 0.0049 + 2 * grow, 0.0145 + 2 * grow
    return pb.chamfer2(cy, cz, w, h, (0.0016 + grow * 0.5, 0.0002, 0.0002, 0.0016 + grow * 0.5))


def fin_wave(x, amp, period=0.026, phase=0.0):
    return amp * (0.5 + 0.5 * math.sin(2 * math.pi * x / period + phase))


# ====================================================================== the card

def build(pid):
    s = SPECS[pid]
    at = make_texture(pid, s)
    TEX = "tex_" + pid
    m = pb.Model(pid)
    L, H, T, Hp = s["L"], s["H"], s["T"], s["Hp"]
    xa, xb = X0 - L, X0
    yF = -T  # outer surface of the fan-side face plate
    fp = 0.0025
    fan_thk = 0.013
    fin_y0, fin_y1 = yF + fp + fan_thk + 0.0012, -0.0062
    xd, zd = s["xd"], s["zd"]
    pcb_end = s["pcb_end"]

    # ------------------------------------------------------------------ PCB with the PCIe edge
    tab_bot = -0.0055
    outline = [(pcb_end, 0.0), (-0.0482, 0.0), (-0.0482, 0.0025), (-0.0452, 0.0025), (-0.0452, 0.0),
               (-0.0445, 0.0), (-0.0445, tab_bot + 0.0005), (-0.0440, tab_bot), (0.0305, tab_bot),
               (0.0310, tab_bot + 0.0005), (0.0310, -0.0003), (0.0328, -0.0003), (0.0328, tab_bot + 0.0005),
               (0.0333, tab_bot), (0.0440, tab_bot), (0.0445, tab_bot + 0.0005), (0.0445, 0.0),
               (xb - 0.0008, 0.0), (xb - 0.0008, Hp), (pcb_end + 0.004, Hp), (pcb_end, Hp - 0.004)]
    slab_xz(m, "pcb_black", outline, [], PCB_Y0, PCB_Y1 - PCB_Y0)
    # gold fingers on both faces: 11 + 71 contacts at 1.0 mm, a few shorter (presence detect)
    xs = [0.0435 - k * 0.001 for k in range(11)] + [0.0300 - k * 0.001 for k in range(71)]
    for k, x in enumerate(xs):
        short = k in (0, 16, 30, 47, 81)
        z0, z1 = (-0.0052, -0.0024) if short else (-0.0052, -0.0012)
        box(m, "gold", (x - 0.00036, PCB_Y1, z0), (x + 0.00036, PCB_Y1 + 0.00004, z1))
        box(m, "gold", (x - 0.00036, PCB_Y0 - 0.00004, z0), (x + 0.00036, PCB_Y0, z1))
    # a few parts on the PCB near the bracket (seen past the ports) and MLCCs at the edge
    for k in range(6):
        x = xb - 0.012 - k * 0.0026
        box(m, "ceramic", (x, PCB_Y0 - 0.0006, 0.0015), (x + 0.0012, PCB_Y0, 0.0021))
    # ------------------------------------------------------------------ backplate
    holes = []
    if pid == "gpu_rx66":
        # flow-through slots past the end of the PCB, screw holes for the GPU core bracket
        for k in range(3):
            x = xa + 0.0085 + k * 0.0048
            holes.append(pb.rrect2(x, H * 0.5, 0.0026, H - 0.026, 0.0012, 3))
        core = [(xd + sx * 0.0145, zd + sz * 0.0145) for sx in (-1, 1) for sz in (-1, 1)]
        for (x, z) in core:
            holes.append(pb.circle2(x, z, 0.0026, 16))
    else:
        # big flow-through window over the third fan with angled slats, the GPU core window
        x0w, x1w = xa + 0.010, pcb_end - 0.006
        n = 9
        pitch = (x1w - x0w) / n
        for k in range(n):
            xl = x0w + k * pitch
            sl = 0.010
            holes.append([(xl, 0.016), (xl + pitch * 0.62, 0.016), (xl + pitch * 0.62 + sl, H - 0.016),
                          (xl + sl, H - 0.016)])
        holes.append(pb.rrect2(xd, zd, 0.046, 0.046, 0.004, 4))
    bp_out = pb.chamfer2((xa + 0.0015 + xb - 0.003) / 2, (0.0035 + H - 0.0005) / 2, (xb - 0.003) - (xa + 0.0015),
                         H - 0.004, (0.006, 0.0, 0.0, 0.006))
    slab_xz(m, s["back_tag"], bp_out, holes, BP_Y0, BP_Y1 - BP_Y0, bevel=0.0003)
    # folded lip along the top edge (covers the PCB edge from the window side)
    box(m, s["back_tag"], (xa + 0.012, -0.0030, H - 0.0013), (xb - 0.012, BP_Y1, H - 0.0005), bevel=0.0002)
    # brand print / inlay
    lf = pb.label_frame((0, 1, 0), (0, 0, -1))  # reads from the window side (text top towards the board)
    bx = -0.029 if pid == "gpu_rx66" else -0.059
    m.add(s["logo_tag"], pb.g_text("VOLTRA", "agency", 0.0105, 0.075, 0.00012, spacing=1.3), lf,
          (bx - 0.006, BP_Y1, H * 0.60))
    m.add(s["logo_tag"], pb.g_text(s["model"], "eras_md", 0.0045, 0.05, 0.00012), lf, (bx - 0.006, BP_Y1, H * 0.60 - 0.012))
    m.add(s["logo_tag"], pb.g_box((0.055, 0.00012, 0.0006)), None, (bx - 0.006, BP_Y1 + 0.00006, H * 0.60 - 0.0215))
    # serial sticker near the bracket
    m.add(TEX, pb.g_quad(0.034, 0.017, at.uv("label")), lf, (xb - 0.030, BP_Y1 + 0.00005, 0.016))
    # backplate screws
    scr = [(xb - 0.007, 0.007), (xb - 0.007, H - 0.008), (pcb_end + 0.006, 0.008), (pcb_end + 0.006, H - 0.008),
           ((xb + pcb_end) / 2, 0.006), ((xb + pcb_end) / 2 - 0.01, H - 0.006)]
    for (x, z) in scr:
        pb.screw_ph(m.mb("steel_dark"), (x, BP_Y1, z), (0, 1, 0), (0, 0, 1), r=0.0019, h=0.0008)
    if pid == "gpu_rx66":
        for (x, z) in core:
            pb.screw_ph(m.mb("steel"), (x, BP_Y1, z), (0, 1, 0), (0, 0, 1), r=0.0030, h=0.0012)
    else:
        # PCB back and GPU retention bracket seen through the core window
        m.add(TEX, pb.g_quad(0.050, 0.050, at.uv("pcb")), pb.label_frame((0, 1, 0), (0, 0, 1)),
              (xd, PCB_Y1 + 0.00002, zd))
        for i in range(10):
            for j in range(10):
                if 3 <= i <= 6 and 3 <= j <= 6:
                    continue
                x = xd - 0.0099 + i * 0.0022
                z = zd - 0.0099 + j * 0.0022
                box(m, "ceramic", (x - 0.0005, PCB_Y1, z - 0.00025), (x + 0.0005, PCB_Y1 + 0.0005, z + 0.00025))
        xbr = []
        for a in (45, 135, 225, 315):
            ca, sa = math.cos(a * pb.DEG), math.sin(a * pb.DEG)
            xbr.append((xd + ca * 0.0225, zd + sa * 0.0225))
        arm = 0.0042
        poly = []
        for k, a in enumerate((45, 135, 225, 315)):
            ca, sa = math.cos(a * pb.DEG), math.sin(a * pb.DEG)
            px, pz = -sa, ca
            tip = (xd + ca * 0.0205, zd + sa * 0.0205)
            poly += [(tip[0] - px * arm, tip[1] - pz * arm), (tip[0] + px * arm, tip[1] + pz * arm)]
            b = (a + 45) * pb.DEG
            poly.append((xd + math.cos(b) * 0.0085, zd + math.sin(b) * 0.0085))
        slab_xz(m, "nickel", poly, [], PCB_Y1 + 0.0002, 0.0011, bevel=0.0002)
        for k, a in enumerate((45, 135, 225, 315)):
            ca, sa = math.cos(a * pb.DEG), math.sin(a * pb.DEG)
            p = (xd + ca * 0.0175, zd + sa * 0.0175)
            m.add("steel", pb.g_helix(0.0021, 0.00032, 0.0, 0.0017, 3.5, 8, 14), pb.frame((0, 1, 0), (0, 0, 1)),
                  (p[0], PCB_Y1 + 0.0013, p[1]))
            pb.screw_ph(m.mb("steel"), (p[0], PCB_Y1 + 0.0030, p[1]), (0, 1, 0), (0, 0, 1), r=0.0028, h=0.0011,
                        shank=0.0028)
    # ------------------------------------------------------------------ bracket with ports and vents
    br_out = [(BR_YB, -0.0035), (-0.0300, -0.0035), (-0.0300, -0.0120), (-0.0275, -0.0135), (-0.0250, -0.0135),
              (-0.0240, -0.0035), (-0.0100, -0.0035), (-0.0100, -0.0120), (-0.0075, -0.0135),
              (-0.0050, -0.0135), (-0.0040, -0.0035), (BR_YT, -0.0035), (BR_YT, Z_TAB - 0.0006),
              (BR_YB, Z_TAB - 0.0006)]
    br_holes = []
    for i, z in enumerate(PORT_Z):
        br_holes.append(hdmi_shape(PORT_Y, z, 0.0006) if i == 3 else dp_shape(PORT_Y, z, 0.0006))
    if s["vent"] == "slots":
        z = 0.0075
        while z < 0.100:
            br_holes.append(pb.rrect2(-0.0262, z, 0.0150, 0.0024, 0.0012, 3))
            z += 0.0047
        for z in (0.0885, 0.0935, 0.0985):
            br_holes.append(pb.rrect2(-0.0068, z, 0.0105, 0.0024, 0.0012, 3))
    else:
        br_holes += hex_grid(-0.0345, 0.004, -0.0170, 0.101, 0.0024, 0.0011)
        br_holes += hex_grid(-0.0125, 0.0855, -0.0010, 0.101, 0.0024, 0.0011)
    slab_yz(m, s["bracket_tag"], br_out, br_holes, BR_X0, BR_X1 - BR_X0)
    # the folded tab with two U slots for the case's screws
    tab = [(BR_X0, BR_YB), (0.1065, BR_YB)]
    for ys in (SLOT_Y[1], SLOT_Y[0]):
        tab += [(0.1065, ys - 0.0022), (X_SCREW, ys - 0.0022)]
        tab += [(X_SCREW + 0.0022 * math.cos(a * pb.DEG), ys + 0.0022 * math.sin(a * pb.DEG))
                for a in range(255, 100, -15)]
        tab += [(X_SCREW, ys + 0.0022), (0.1065, ys + 0.0022)]
    tab += [(0.1065, BR_YT), (BR_X0, BR_YT)]
    slab_xy(m, s["bracket_tag"], tab, [], Z_TAB - 0.0010, 0.0010)
    # bend between plate and tab
    m.add(s["bracket_tag"], pb.g_cyl(0.0008, BR_YT - BR_YB, 8), pb.frame((0, 1, 0), (1, 0, 0)),
          (BR_X0 + 0.0002, (BR_YT + BR_YB) / 2, Z_TAB - 0.0008))
    # ports: shells with tongues and contacts
    for i, z in enumerate(PORT_Z):
        hdmi = i == 3
        outer = hdmi_shape(PORT_Y, z, 0.0) if hdmi else dp_shape(PORT_Y, z, 0.0)
        inner = hdmi_shape(PORT_Y, z, -0.0003) if hdmi else dp_shape(PORT_Y, z, -0.0003)
        slab_yz(m, "nickel", outer, [inner], 0.0866, BR_X1 + 0.0002 - 0.0866)
        slab_yz(m, "connector_black", inner, [], 0.0866, 0.0012)
        tl = 0.0108 if hdmi else 0.0118
        ty = PORT_Y + (0.0 if hdmi else 0.0006)
        box(m, "connector_black", (0.0875, ty - 0.0006, z - tl / 2), (BR_X1 - 0.0012, ty + 0.0006, z + tl / 2))
        n = 10 if hdmi else 10
        for k in range(n):
            zz = z - tl / 2 + 0.0008 + k * (tl - 0.0016) / (n - 1)
            box(m, "gold", (0.0885, ty - 0.00064, zz - 0.00018), (BR_X1 - 0.0016, ty - 0.0006, zz + 0.00018))
    # ------------------------------------------------------------------ heatsink: cold plate, mid plate, pipes, fins
    cp = 0.024 if s["pipes"] == 4 else 0.028
    box(m, "nickel", (xd - cp, -0.0080, zd - cp), (xd + cp, -0.0040, zd + cp), bevel=0.0007)
    mid_out = [(pcb_end + 0.003, 0.004), (xb - 0.0125, 0.004), (xb - 0.0125, Hp - 0.002),
               (s["px"] + 0.0115, Hp - 0.002), (s["px"] + 0.0115, Hp - 0.0115), (s["px"] - 0.0115, Hp - 0.0115),
               (s["px"] - 0.0115, Hp - 0.002), (pcb_end + 0.003, Hp - 0.002)]
    mid_holes = [pb.rrect2(xd, zd, 2 * cp + 0.002, 2 * cp + 0.002, 0.002, 3)]
    slab_xz(m, "paint_black", mid_out, mid_holes, -0.0054, 0.0012)
    # heat pipes: through the cold plate, up into the fins, a U-turn at each end of the stack
    n = s["pipes"]
    y_base = -0.0076
    if n == 4:
        yA, yB, pr = -0.0145, -0.0235, 0.0030
    else:
        yA, yB, pr = -0.0150, -0.0300, 0.0030
    zb = [zd + (i - (n - 1) / 2) * 0.0068 for i in range(n)]
    zs = [pb.lerp(0.014, H - 0.017, i / (n - 1)) for i in range(n)]
    x_far = xa + 0.0095
    x_near = xb - 0.0090
    for i in range(n):
        pts = [(xd - 0.032, yB, zs[i]), (x_far, yB, zs[i]), (x_far, yA, zs[i]), (xd - 0.048, yA, zs[i]),
               (xd - cp + 0.004, y_base, zb[i]), (xd + cp - 0.004, y_base, zb[i]), (xd + 0.046, yA, zs[i]),
               (x_near, yA, zs[i]), (x_near, yB, zs[i]), (xd + 0.032, yB, zs[i])]
        path = pb.fillet_path(pts, 0.0045, 8)
        m.add(s["pipe_tag"], pb.g_sweep(path, pr, 16))
    # fins: thin aluminium plates across the card, waved edges, notches for the cold plate and the power plug
    pitch = 0.0020
    x = xb - 0.0150
    k = 0
    while x > xa + 0.0160:
        zlo = 0.0045 + fin_wave(x, 0.0016, phase=1.3)
        zhi = H - 0.0040 - fin_wave(x, 0.0018)
        ytop = fin_y1
        pts = [(fin_y0, zlo), (ytop, zlo)]
        if abs(x - xd) < cp + 0.0008:
            pts += [(ytop, zd - cp - 0.0006), (-0.0108, zd - cp - 0.0006), (-0.0108, zd + cp + 0.0006),
                    (ytop, zd + cp + 0.0006)]
        if abs(x - s["px"]) < 0.0125:
            pts += [(ytop, Hp - 0.0110), (-0.0128, Hp - 0.0110), (-0.0128, zhi)]
        else:
            pts += [(ytop, zhi)]
        pts += [(fin_y0, zhi)]
        slab_yz(m, "alu", pts, [], x - 0.0002, 0.0004)
        x -= pitch
        k += 1
    # end plates of the stack (thicker fins)
    # ------------------------------------------------------------------ shroud
    face = pb.chamfer2((xa + xb - 0.0012) / 2, (0.002 + H) / 2, (xb - 0.0012) - xa, H - 0.002,
                       (0.003, 0.002, 0.002, 0.003))
    nf = s["fans"]
    avail = L - 0.0165
    fpitch = avail / nf
    fxs = [xa + 0.008 + fpitch * (i + 0.5) for i in range(nf)]
    fz = H / 2 + 0.001
    r_hole = s["fan_d"] / 2 + 0.0018
    slab_xz(m, s["face_tag"], face, [pb.circle2(x, fz, r_hole, 96) for x in fxs], yF, fp, bevel=0.0004)
    ring_prof = [(r_hole - 0.0002, -0.0022), (r_hole + 0.0035, -0.0022), (r_hole + 0.0035, 0.0018),
                 (r_hole + 0.0027, 0.0026), (r_hole + 0.0010, 0.0026), (r_hole - 0.0002, 0.0016),
                 (r_hole - 0.0002, -0.0022)]
    Mout = pb.frame((0, -1, 0), (0, 0, 1))  # local z = outwards from the fan face
    for x in fxs:
        m.add(s["ring_tag"], pb.g_lathe(ring_prof, 96), Mout, (x, yF, fz))
    if pid == "gpu_rx66":
        xm = (fxs[0] + fxs[1]) / 2
        over = [(xa + 0.006, 0.010), (xa + 0.020, 0.004), (xm - 0.012, 0.004), (xm, 0.0105), (xm + 0.012, 0.004),
                (xb - 0.010, 0.004), (xb - 0.0045, 0.012), (xb - 0.0045, H - 0.012), (xb - 0.010, H - 0.004),
                (xm + 0.012, H - 0.004), (xm, H - 0.0105), (xm - 0.012, H - 0.004), (xa + 0.020, H - 0.004),
                (xa + 0.006, H - 0.010)]
        # outward = -y: build the overlay from yF - 0.0016 to yF
        slab_xz(m, s["over_tag"], over, [pb.circle2(x, fz, r_hole + 0.0015, 96) for x in fxs], yF - 0.0016,
                0.0016, bevel=0.0003)
        # silver accent lines along the overlay edges
        for (x0l, x1l, zl) in ((xa + 0.024, xm - 0.016, 0.0062), (xm + 0.016, xb - 0.014, 0.0062),
                               (xa + 0.024, xm - 0.016, H - 0.0062), (xm + 0.016, xb - 0.014, H - 0.0062)):
            box(m, "alu", (x0l, yF - 0.0019, zl - 0.0004), (x1l, yF - 0.0016, zl + 0.0004))
        for zz in (0.0055, H - 0.0055):
            pb.screw_ph(m.mb("steel_dark"), (xm, yF, zz), (0, -1, 0), (1, 0, 0), r=0.0017, h=0.0008)
        # brushed silver slashes on the far-end corners of the overlay
        for (zz, sgn) in ((0.0, 1), (H, -1)):
            for k in range(3):
                xr = xa + 0.0215 + k * 0.0042
                sl = [(xr, zz + sgn * 0.0045), (xr + 0.0016, zz + sgn * 0.0045),
                      (xr + 0.0016 - 0.006, zz + sgn * 0.0105), (xr - 0.006, zz + sgn * 0.0105)]
                slab_xz(m, "alu", sl, [], yF - 0.0019, 0.0004)
    else:
        # angular black inserts between the fan rings at the top and bottom, red slashes, a centre badge
        for i in range(nf - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for zz, sgn in ((0.0, 1), (H, -1)):
                tri = [(xm - 0.020, zz + sgn * 0.0035), (xm + 0.020, zz + sgn * 0.0035), (xm + 0.007, zz + sgn * 0.016),
                       (xm - 0.007, zz + sgn * 0.016)]
                slab_xz(m, s["over_tag"], tri, [], yF - 0.0014, 0.0014, bevel=0.0003)
                pb.screw_ph(m.mb("steel_dark"), (xm, yF - 0.0014, zz + sgn * 0.0085), (0, -1, 0), (1, 0, 0), r=0.0017,
                            h=0.0008)
        for (x0r, zz, sgn) in ((xa + 0.006, 0.0, 1), (xa + 0.006, H, -1)):
            for k in range(2):
                xr = x0r + 0.004 + k * 0.006
                sl = [(xr, zz + sgn * 0.004), (xr + 0.0028, zz + sgn * 0.004), (xr + 0.0028 + 0.009, zz + sgn * 0.020),
                      (xr + 0.009, zz + sgn * 0.020)]
                m.add(TEX, pb.g_slab(sl, [], 0.0012, yF - 0.0012, uv_rect=at.uv("red")), M_XZ)
        for (zz, sgn) in ((0.0, 1), (H, -1)):
            sl = [(xb - 0.0045, zz + sgn * 0.0040), (xb - 0.0045, zz + sgn * 0.024), (xb - 0.0075, zz + sgn * 0.024),
                  (xb - 0.0075, zz + sgn * 0.0060)]
            m.add(TEX, pb.g_slab(sl, [], 0.0012, yF - 0.0012, uv_rect=at.uv("red")), M_XZ)
    # side skirts: the top edge (faces the window in a tower), the bottom edge and the far end
    if pid == "gpu_rx66":
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.018), (xb - 0.016, yF + 0.018),
               (xb - 0.024, yF + 0.012), (xa + 0.045, yF + 0.012), (xa + 0.030, yF + 0.024), (xa + 0.002, yF + 0.024)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.012), (xa + 0.035, yF + 0.012),
               (xa + 0.020, yF + 0.020), (xa + 0.004, yF + 0.020)]
        end_h = 0.024
    else:
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.024), (xb - 0.020, yF + 0.024),
               (xb - 0.030, yF + 0.016), (xa + 0.120, yF + 0.016), (xa + 0.105, yF + 0.0245), (xa + 0.060, yF + 0.0245),
               (xa + 0.045, yF + 0.016), (xa + 0.022, yF + 0.016), (xa + 0.010, yF + 0.030), (xa + 0.002, yF + 0.030)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.016), (xa + 0.040, yF + 0.016),
               (xa + 0.022, yF + 0.026), (xa + 0.004, yF + 0.026)]
        end_h = 0.030
    slab_xy(m, s["face_tag"], top, [], H - 0.0018, 0.0018, bevel=0.0003)
    slab_xy(m, s["face_tag"], bot, [], 0.0020, 0.0018, bevel=0.0003)
    endc = pb.chamfer2(yF + end_h / 2, (0.002 + H) / 2, end_h, H - 0.002, (0.006, 0.0, 0.0, 0.006))
    slab_yz(m, s["face_tag"], endc, [], xa, 0.0018, bevel=0.0003)
    # the shroud wall at the bracket end, below the bracket (cards thicker than two slots)
    slab_yz(m, s["face_tag"], pb.rect2((yF + 0.0005 + BR_YB + 0.004) / 2, (0.0025 + H - 0.0005) / 2,
                                       BR_YB + 0.004 - yF - 0.0005, H - 0.003), [], xb - 0.0030, 0.0018)
    # logo plate and RGB light bar on the top edge
    lf_top = pb.label_frame((0, 0, 1), (0, 1, 0))  # reads left to right from the window, bracket on the left
    if pid == "gpu_rx66":
        lw, lh, lx = 0.072, 0.009, (xa + 0.045 + xb - 0.024) / 2
        ly = yF + 0.0060
        rgb_x = (xa + 0.010, xb - 0.030)
        rgb_y = yF + 0.0016
    else:
        lw, lh, lx = 0.096, 0.012, (xa + 0.120 + xb - 0.030) / 2
        ly = yF + 0.0080
        rgb_x = (xa + 0.024, xb - 0.032)
        rgb_y = yF + 0.0018
    box(m, "black_plastic", (lx - lw / 2 - 0.0008, ly - lh / 2 - 0.0008, H - 0.0004),
        (lx + lw / 2 + 0.0008, ly + lh / 2 + 0.0008, H + 0.0003), bevel=0.0002)
    m.add(TEX, pb.g_quad(lw, lh, at.uv("logo")), lf_top, (lx, ly, H + 0.00035))
    box(m, "rgb", (rgb_x[0], rgb_y - 0.0009, H - 0.0003), (rgb_x[1], rgb_y + 0.0009, H + 0.0003))
    if pid == "gpu_rx88":
        # a red accent stripe along the top edge and a small print on the bottom edge
        m.add(TEX, pb.solid(pb.g_box((xb - 0.034 - xa - 0.124, 0.0010, 0.0005)), at.uv("red")), None,
              ((xb - 0.030 + xa + 0.120) / 2, yF + 0.0148, H + 0.0001))
        m.add(TEX, pb.solid(pb.g_box((0.040, 0.0010, 0.0005)), at.uv("red")), None, (xa + 0.0825, yF + 0.0225, H + 0.0001))
        m.add(TEX, pb.g_quad(0.08, 0.010, at.uv("plate")), pb.label_frame((0, 0, -1), (0, 1, 0)),
              ((xa + xb) / 2 + 0.02, yF + 0.008, 0.0020 - 0.00005))
    # ------------------------------------------------------------------ fans
    for i, x in enumerate(fxs):
        a = m.anchor(f"A_FAN_{i}", (x, yF + 0.0012 + fan_thk / 2, fz), (s["fan_d"], s["fan_d"], fan_thk),
                     forward=(0, -1, 0), up=(0, 0, 1), meta=pf.fan_meta("ccw", 2200 if nf == 2 else 1900))
        pf.make_fan(a, diameter=s["fan_d"], thickness=fan_thk, blades=s["blades"], frame=False,
                    tip_ring=s["tip_ring"], sticker=pid, sticker_uv=at.uv("hub"), struts=3, name=f"gpufan{i}")
    # ------------------------------------------------------------------ power connector on the top edge
    pxc = s["px"]
    if s["power"] == "pcie8":
        hw, hd = 0.0186, 0.0096
        z_face = Hp + 0.0040
        yc = PCB_Y0 - hd / 2
        cav = []
        for col in range(4):
            for row in range(2):
                cx = pxc + (col - 1.5) * 0.0042
                cy = yc + (row - 0.5) * 0.0042
                d = (col + row) % 2 == 0
                cav.append(pb.chamfer2(cx, cy, 0.0031, 0.0031, (0.0008, 0.0008, 0.0, 0.0) if d else 0.0002))
        pin_pts = [(pxc + (col - 1.5) * 0.0042, yc + (row - 0.5) * 0.0042) for col in range(4) for row in range(2)]
        name, meta = "A_PORT_PCIE8_0", "pins=8,latch=+y"
        pin_w = 0.0011
    else:
        hw, hd = 0.0206, 0.0102
        z_face = Hp + 0.0040
        yc = PCB_Y0 - hd / 2
        cav, pin_pts = [], []
        for col in range(6):
            for row in range(2):
                cx = pxc + (col - 2.5) * 0.0030
                cy = PCB_Y0 - 0.0046 - row * 0.0030
                cav.append(pb.rrect2(cx, cy, 0.0022, 0.0022, 0.0003, 2))
                pin_pts.append((cx, cy))
        for col in range(4):
            cx = pxc + (col - 1.5) * 0.0024
            cav.append(pb.rrect2(cx, PCB_Y0 - 0.0016, 0.0012, 0.0011, 0.0002, 2))
        name, meta = "A_PORT_12V2X6_0", "pins=12+4,latch=+y,sense=+y"
        pin_w = 0.0008
    hout = pb.rrect2(pxc, yc, hw, hd, 0.0006, 2)
    slab_xy(m, "connector_black", hout, cav, z_face - 0.0030, 0.0030)
    box(m, "connector_black", (pxc - hw / 2, yc - hd / 2, z_face - 0.0145), (pxc + hw / 2, yc + hd / 2, z_face - 0.0030))
    for (x, y) in pin_pts:
        box(m, "solder", (x - pin_w / 2, y - pin_w / 2, z_face - 0.0030), (x + pin_w / 2, y + pin_w / 2, z_face - 0.0009))
    # latch ramp above the PCB edge, on the +y face
    box(m, "connector_black", (pxc - 0.0022, PCB_Y0, z_face - 0.0034), (pxc + 0.0022, PCB_Y0 + 0.0011, z_face - 0.0006))
    m.anchor(name, (pxc, yc, z_face), (hw + 0.004, hd + 0.003, 0.012), forward=(0, 0, 1), up=(0, 1, 0), meta=meta)
    # ------------------------------------------------------------------ other anchors
    for i, z in enumerate(PORT_Z[:3]):
        m.anchor(f"A_PORT_DP_{i}", (BR_X1, PORT_Y, z), (0.019, 0.008, 0.012), forward=(1, 0, 0), up=(0, 1, 0),
                 meta="kind=displayport,chamfer=-y")
    m.anchor("A_PORT_HDMI_0", (BR_X1, PORT_Y, PORT_Z[3]), (0.017, 0.008, 0.012), forward=(1, 0, 0), up=(0, 1, 0),
             meta="kind=hdmi,narrow=-y")
    for i, ys in enumerate(SLOT_Y):
        m.anchor(f"A_SCREW_PH2_{i}", (X_SCREW, ys, Z_TAB), (0.008, 0.008, 0.008), forward=(0, 0, 1), up=(1, 0, 0),
                 meta=f"slot={i}")
    m.anchor("A_HIT_0", ((xa + xb) / 2, (yF + BP_Y1) / 2, H / 2), (L, BP_Y1 - yF, H))
    m.anchor("A_HIT_1", ((BR_X0 + 0.1065) / 2, (BR_YT + BR_YB) / 2, (Z_TAB - 0.0135) / 2),
             (0.1065 - BR_X0, BR_YT - BR_YB, Z_TAB + 0.0135))
    m.anchor("A_HIT_2", (0.0, PCB_Y0 / 2 + PCB_Y1 / 2, -0.0028), (0.090, 0.003, 0.0060))
    # protective films (Logs/UNBOXING.md 1.4; anchors only, the game builds the peel meshes): the clear film on the
    # backplate (2 mm inside its outline; its corners at local +x are chamfered 4 mm like the plate's far end; the
    # screw heads stand up to 1.2 mm proud of it) and the one on the top-edge logo plate
    m.anchor("A_FILM_BACKPLATE_0", ((xa + 0.0015 + xb - 0.003) / 2, BP_Y1 + 0.00015, (0.0035 + H - 0.0005) / 2),
             ((xb - 0.003) - (xa + 0.0015) - 0.004, H - 0.004 - 0.004, 0.001), forward=(0, 1, 0), up=(0, 0, 1),
             meta="film=clear,peel_from=+x,chamfer=0.004@+x,screws=proud")
    m.anchor("A_FILM_SHROUD_0", (lx, ly, H + 0.0004), (lw + 0.0016, lh + 0.0016, 0.001), forward=(0, 0, 1),
             up=(0, 1, 0), meta="film=clear,on=logo_plate,peel_from=-x")
    m.finish()
    m.report()
    m.export()
    pb.preview_textures()
    tgt = ((xa + xb) / 2, -T / 2, H / 2)
    pb.shots(m.root, pid, [
        dict(yaw=35, pitch=-35, target=tgt),  # fans side
        dict(yaw=-40, pitch=55, target=tgt),  # backplate side
        dict(yaw=20, pitch=10, target=(0.0, -T / 2, H), dist=0.32),  # top edge (window view)
        dict(yaw=90, pitch=15, target=(X0, -0.017, 0.055), dist=0.19),  # bracket
        dict(yaw=-15, pitch=-20, target=(fxs[-1], yF, fz), dist=0.16),  # a fan close up
        dict(yaw=-120, pitch=20, target=(xa, -T / 2, H / 2), dist=0.22),  # far end
        dict(yaw=10, pitch=20, target=(s["px"], -0.006, Hp), dist=0.09),  # power connector
    ])
    return m


if __name__ == "__main__":
    ids = [a for a in c.args() if a in SPECS] or list(SPECS)
    for pid in ids:
        build(pid)
