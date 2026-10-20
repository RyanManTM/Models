"""
SSD models: ssd_1tb (Quill M.2 2280 NVMe) and ssd_sata_500 (Quill 2.5" 7 mm SATA).

M.2 frame (as today's game): origin at the PCB centre on its bottom face, the PCB spans z 0..0.0008,
the M-key connector end at -x, the half-moon screw notch centred on the +x end (x 0.040).
2.5" frame: origin at the body centre; x = length (100 mm, connectors on the -x end), y = thickness
(7 mm, +y = top cover), z = width (69.85 mm).

Run: blender -b --factory-startup -P Tools/Blender/build_ssd.py -- [ids...]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402
from mathutils import Vector  # noqa: E402

MM = 0.001

# M.2 2280
L, W, T = 80.0, 22.0, 0.8
MKEY_Y = 6.0          # M-key notch centre along y (mm), the board connector uses the same value
NOTCH_R = 1.75

PCB_BLACK = "#121417"
GOLD = "#c9a24c"
SILK = "#e6e6e0"


def m2_outline():
    """M.2 PCB outline (x, y) mm: chamfered connector corners, the M key, and the half-moon screw notch."""
    hx, hy = L / 2, W / 2
    kw, kd = 1.2, 4.2
    pts = [(-hx, -hy + 0.6), (-hx + 0.6, -hy)]
    pts += [(hx, -hy)]
    pts += [(hx, -NOTCH_R)]
    pts += [(hx - math.sin(math.pi * k / 10) * NOTCH_R, -math.cos(math.pi * k / 10) * NOTCH_R) for k in range(1, 10)]
    pts += [(hx, NOTCH_R), (hx, hy), (-hx + 0.6, hy), (-hx, hy - 0.6)]
    # M key slot cut into the connector edge
    pts += [(-hx, MKEY_Y + kw / 2), (-hx + kd, MKEY_Y + kw / 2), (-hx + kd, MKEY_Y - kw / 2), (-hx, MKEY_Y - kw / 2)]
    return pts


def m2_fingers():
    """(y, side) for the edge contacts: top = odd pins, bottom = even pins (staggered by 0.25 mm)."""
    out = []
    for i in range(38):
        y = -9.25 + i * 0.5
        if abs(y - MKEY_Y) > 1.0:
            out.append((y, 1))
    for i in range(37):
        y = -9.0 + i * 0.5
        if abs(y - MKEY_Y) > 1.0:
            out.append((y, -1))
    return out


CTRL = dict(x=-25.5, y=0.0, s=11.0, h=1.15)
NAND = [dict(x=-6.0, y=0.0), dict(x=15.0, y=0.0)]  # 18 (x) by 12 (y) BGA packages
NAND_L, NAND_W, NAND_H = 17.5, 12.0, 1.2


def m2_parts():
    """Passives (x, y, ang, kind) laid out around the chips."""
    out = []
    for i in range(6):
        out.append((-33.0, -8.0 + i * 3.2, 90, "cap"))
    for i in range(4):
        out.append((-18.0, -9.6 + i * 1.3, 0, "res"))
    for i in range(5):
        out.append((4.0, -9.8 + i * 1.0, 0, "cap"))
    for i in range(7):
        out.append((28.5 + (i % 2) * 1.6, -8.0 + i * 1.5, 90, "cap"))
    for i in range(5):
        out.append((33.5, 3.0 + i * 1.3, 0, "res"))
    return out


def m2_textures():
    at = pp.Atlas(2048, 1024, bg=PCB_BLACK)
    rnd = random.Random(11)
    reg = {}
    ppm = 12.0
    lighter = pp.shade(PCB_BLACK, 1.6)

    def to_top(x, y):
        return L / 2 - x, y + W / 2

    # ---- top
    r, uv, ctx = at.panel(L, W, ppm, bg=PCB_BLACK)
    reg["top"] = uv
    with ctx as a:
        for k in range(140):
            u0, v0 = rnd.uniform(1, L - 1), rnd.uniform(1, W - 1)
            pts = [(u0, v0)]
            for s in range(rnd.randint(2, 4)):
                dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (-1, 1), (-1, 0), (0, -1)])
                Lr = rnd.uniform(1.0, 6.0)
                u0 = min(L - 0.6, max(0.6, u0 + dx * Lr))
                v0 = min(W - 0.6, max(0.6, v0 + dy * Lr))
                pts.append((u0, v0))
            a.line(pts, 0.13, lighter, z=0.1)
        for k in range(260):
            a.circle(rnd.uniform(1, L - 1), rnd.uniform(1, W - 1), 0.2, pp.shade(PCB_BLACK, 2.1), z=0.15, seg=8)
        # finger pads (top = odd pins)
        for y, side in m2_fingers():
            if side > 0:
                u, v = to_top(-L / 2, y)
                a.rect(u - 2.9, v - 0.18, u, v + 0.18, GOLD, z=0.2)
        # screw notch ground ring
        u, v = to_top(L / 2, 0)
        a.ring(u, v, NOTCH_R, NOTCH_R + 1.4, GOLD, z=0.2)
        # chip pads / silkscreen outlines
        for n in NAND:
            u, v = to_top(n["x"], n["y"])
            a.frame_rect(u - NAND_L / 2 - 0.5, v - NAND_W / 2 - 0.5, u + NAND_L / 2 + 0.5, v + NAND_W / 2 + 0.5, 0.15, SILK, z=0.3)
        u, v = to_top(CTRL["x"], CTRL["y"])
        a.frame_rect(u - 6.2, v - 6.2, u + 6.2, v + 6.2, 0.15, SILK, z=0.3)
        a.circle(u + 6.6, v + 6.6, 0.3, SILK, z=0.3)
        for (x, y, ang, kind) in m2_parts():
            u, v = to_top(x, y)
            if ang == 0:
                for s in (-1, 1):
                    a.rect(u + s * 0.5 - 0.25, v - 0.3, u + s * 0.5 + 0.25, v + 0.3, "#b8b8b0", z=0.25)
            else:
                for s in (-1, 1):
                    a.rect(u - 0.3, v + s * 0.5 - 0.25, u + 0.3, v + s * 0.5 + 0.25, "#b8b8b0", z=0.25)
        # small silk
        u, v = to_top(-36.0, -9.0)
        a.text("U1", *to_top(-25.5, 7.4), 0.9, SILK, font="narrowbd")
        a.text("U2", *to_top(-6.0, 7.4), 0.9, SILK, font="narrowbd")
        a.text("U3", *to_top(15.0, 7.4), 0.9, SILK, font="narrowbd")
        a.text("2280", *to_top(37.0, 8.4), 1.0, SILK, font="narrowbd")
        a.text("2260", *to_top(17.0, -9.9), 0.8, SILK, font="narrowbd")
        a.text("2242", *to_top(-0.5, -9.9), 0.8, SILK, font="narrowbd")
    # ---- bottom (seen from below: u = x + L/2)
    r, uv, ctx = at.panel(L, W, ppm, bg=PCB_BLACK)
    reg["bottom"] = uv
    with ctx as a:
        for k in range(160):
            u0, v0 = rnd.uniform(1, L - 1), rnd.uniform(1, W - 1)
            pts = [(u0, v0)]
            for s in range(rnd.randint(2, 4)):
                dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (-1, 1), (-1, 0), (0, -1)])
                Lr = rnd.uniform(1.0, 6.0)
                u0 = min(L - 0.6, max(0.6, u0 + dx * Lr))
                v0 = min(W - 0.6, max(0.6, v0 + dy * Lr))
                pts.append((u0, v0))
            a.line(pts, 0.13, lighter, z=0.1)
        for y, side in m2_fingers():
            if side < 0:
                u, v = 0.0, y + W / 2
                a.rect(u, v - 0.18, u + 2.9, v + 0.18, GOLD, z=0.2)
        a.ring(L, W / 2, NOTCH_R, NOTCH_R + 1.4, GOLD, z=0.2)
        # regulatory sticker
        a.rect(20.0, 3.0, 62.0, 19.0, "#d9dadc", z=0.3)
        a.text("QUILL", 22.0, 16.4, 2.2, "#1a1a1a", font="agency", ax="LEFT")
        a.text("NVMe PCIe Gen4 x4  M.2 2280", 22.0, 13.4, 1.2, "#1a1a1a", font="narrowbd", ax="LEFT")
        a.text("Model: QN4-1T00   1TB", 22.0, 11.4, 1.2, "#1a1a1a", font="narrowbd", ax="LEFT")
        a.text("3.3V ⎓ 2.5A", 22.0, 9.4, 1.2, "#1a1a1a", font="narrowbd", ax="LEFT")
        bx = 22.0
        while bx < 48.0:
            w = rnd.choice([0.15, 0.15, 0.3, 0.45])
            a.rect(bx, 4.4, bx + w, 7.6, "#111111", z=0.35)
            bx += w + rnd.choice([0.15, 0.3])
        a.text("SN 2410QN0A71C3", 35.0, 3.7, 0.8, "#111111", font="ocr")
        a.text("MADE IN CHINA", 55.0, 6.0, 1.0, "#1a1a1a", font="narrowbd")
        a.ring(55.0, 12.0, 2.0, 2.35, "#1a1a1a", z=0.35)
        a.text("CE", 55.0, 12.0, 1.6, "#1a1a1a", font="arialbd")
    # ---- top label (over the two NAND packages)
    r, uv, ctx = at.panel(40.0, 20.0, 20.0, bg="#1d1f24")
    reg["label"] = uv
    with ctx as a:
        # copper-foil style label: dark with an orange stripe and a brand block
        a.rect(0.0, 0.0, 3.0, 20.0, "#e2701d", z=0.1)
        a.text("QUILL", 5.0, 14.2, 4.4, "#f2f2f2", font="agency", ax="LEFT")
        a.text("NVMe™ SSD", 5.2, 9.6, 1.9, "#cfd2d8", font="arialbd", ax="LEFT")
        a.text("1TB", 37.5, 14.4, 4.0, "#e2701d", font="agency", ax="RIGHT")
        a.text("PCIe 4.0 x4 • M.2 2280", 5.2, 6.6, 1.3, "#9da3ad", font="narrowbd", ax="LEFT")
        a.text("Q4 SERIES", 37.5, 6.6, 1.3, "#9da3ad", font="narrowbd", ax="RIGHT")
        for i in range(10):
            a.rect(5.2 + i * 3.3, 2.0, 5.2 + i * 3.3 + 2.4, 2.6, pp.mix("#e2701d", "#1d1f24", i / 10.0), z=0.1)
        a.text("WARRANTY VOID IF REMOVED", 21.0, 0.9, 0.8, "#6c717a", font="narrowbd")
    # ---- controller marking
    r, uv, ctx = at.panel(11.0, 11.0, 30.0, bg="#1b1c1e")
    reg["ctrl"] = uv
    with ctx as a:
        a.text("QUILL", 5.5, 8.4, 1.6, "#8a8d93", font="agency")
        a.text("QL5021-E21T", 5.5, 6.0, 1.15, "#8a8d93", font="arialbd")
        a.text("FC3Q1203", 5.5, 4.2, 1.0, "#8a8d93", font="ocr")
        a.text("2409 TAIWAN", 5.5, 2.5, 0.9, "#8a8d93", font="arialbd")
        a.circle(1.2, 1.2, 0.45, "#2d2e31", z=0.2)
    r, uv, ctx = at.panel(3.0, 3.0, 40.0, bg="#1b1c1e")
    reg["pmic"] = uv
    with ctx as a:
        a.text("Q8L", 1.5, 1.8, 0.8, "#8a8d93", font="arialbd")
        a.text("2C1", 1.5, 0.9, 0.7, "#8a8d93", font="arialbd")
    reg["black"] = at.swatch("#141518")
    reg["edge"] = at.swatch("#3c3a30")
    reg["label_edge"] = at.swatch("#1d1f24")
    at.render(pp.tex_path("ssd_1tb"))
    pp.PREVIEW_TEX["ssd_1tb"] = (0.0, 0.45)
    return "ssd_1tb", reg


def build_m2():
    sid = "ssd_1tb"
    c.reset()
    tex, reg = m2_textures()
    TX = "tex_" + tex
    root = c.root(sid)
    k = pp.Kit(sid)
    t = T * MM
    # PCB
    mapper = pp.MultiMap([pp.Planar(reg["top"], (0, 0, t), (0, 0, 1), (0, 1, 0), (L * MM, W * MM)),
                          pp.Planar(reg["bottom"], (0, 0, 0), (0, 0, -1), (0, 1, 0), (L * MM, W * MM)),
                          reg["edge"]])
    pp.prism(k[TX], [[(x * MM, y * MM) for x, y in m2_outline()]], 0.0, t, uv=mapper)
    # edge fingers
    for y, side in m2_fingers():
        z = t + 0.00002 if side > 0 else -0.00002
        pp.quad(k["gold"], ((-L / 2 + 1.45) * MM, y * MM, z), (0.00036, 0.0029), normal=(0, 0, side), up=(1, 0, 0))
    # controller (with marking) and its BGA underfill fillet
    pp.chip_marked(k[TX], CTRL["x"] * MM, CTRL["y"] * MM, t, CTRL["s"] * MM, CTRL["s"] * MM, CTRL["h"] * MM, reg["ctrl"], reg["black"],
                   text_rot=90)
    # NAND packages
    for n in NAND:
        pp.box(k["chip_black"], (n["x"] * MM, n["y"] * MM, t + NAND_H * MM * 0.5), (NAND_L * MM, NAND_W * MM, NAND_H * MM), bevel=0.0001)
    # PMIC, inductor, passives
    pp.chip_marked(k[TX], 30.5 * MM, 6.5 * MM, t, 3.0 * MM, 3.0 * MM, 0.8 * MM, reg["pmic"], reg["black"])
    pp.box(k["dark_plastic"], (31.0 * MM, -4.0 * MM, t + 0.6 * MM), (2.6 * MM, 2.0 * MM, 1.2 * MM), bevel=0.00015)
    for (x, y, ang, kind) in m2_parts():
        body = "ceramic" if kind == "cap" else "chip_black"
        pp.smd_passive(k, x * MM, y * MM, t, 0.001, 0.0005, 0.0005, ang=ang, body=body)
    # label sticker over both NAND packages (a thin printed sheet)
    lz = t + NAND_H * MM + 0.00006
    lx0, lx1 = -15.5 * MM, 24.5 * MM
    lmap = pp.MultiMap([pp.Planar(reg["label"], ((lx0 + lx1) / 2, 0, lz), (0, 0, 1), (0, 1, 0), (lx1 - lx0, 0.020)), reg["label_edge"]])
    pp.box(k[TX], ((lx0 + lx1) / 2, 0, lz), (lx1 - lx0, 0.020, 0.00012), uv=lmap)
    k.finish(root)

    c.anchor("A_SCREW_PH0_0", (L / 2 * MM, 0, t), (0.006, 0.006, 0.004), root, meta="notch=+x")
    c.anchor("A_HIT_0", (0, 0, 0.0012), (L * MM, W * MM, 0.0026), root)
    c.anchor("A_KEY_M2_0", (-L / 2 * MM, MKEY_Y * MM, t * 0.5), (0.002, 0.0015, 0.002), root, meta=f"key=M,y={MKEY_Y * MM:.4f}")
    c.join_by_tag(root, sid)
    c.export(root, sid)
    pp.report(root)
    return root


# ------------------------------------------------------------------ 2.5" SATA

BL, BT, BW = 100.0, 7.0, 69.85
SEAM = 2.3          # y of the seam between the tray and the lid (mm)
HOLE_X = (-50.0 + 14.0, -50.0 + 90.6)
HOLE_Y = -BT / 2 + 3.0
BOTTOM_Z = 61.72 / 2
DATA = dict(z=20.0, w=11.0, pins=7)
PWR = dict(z=-3.4, w=23.4, pins=15)
CONN_Y = -1.0        # connector tongue centre height


def sata_textures():
    at = pp.Atlas(2048, 1024, bg="#202226")
    rnd = random.Random(21)
    reg = {}
    # top cover art (seen from +y with the connector end (-x) at the image's left)
    r, uv, ctx = at.panel(BL, BW, 10.0, bg="#24262b")
    reg["top"] = uv
    with ctx as a:
        for k in range(200):
            y = rnd.uniform(0, BW)
            x0 = rnd.uniform(-20, BL)
            a.line([(x0, y), (x0 + rnd.uniform(20, 70), y)], rnd.uniform(0.05, 0.2), pp.shade("#24262b", rnd.uniform(0.85, 1.2)), z=0.1, joins=False)
        a.poly([(0, 0), (38, 0), (60, BW), (0, BW)], "#191a1d", z=0.2)
        a.line([(38, 0), (60, BW)], 0.5, "#e2701d", z=0.3)
        a.text("QUILL", 8.0, BW * 0.58, 13.0, "#f0f0f0", font="agency", ax="LEFT")
        a.text("SOLID STATE DRIVE", 8.6, BW * 0.40, 3.0, "#c4c8cf", font="arialbd", ax="LEFT", fit=40)
        a.text("500GB", BL - 7.0, BW * 0.30, 8.0, "#e2701d", font="agency", ax="RIGHT")
        a.text("SATA III  6Gb/s", BL - 7.0, BW * 0.18, 2.8, "#c4c8cf", font="arialbd", ax="RIGHT")
        a.text("Q3 SERIES", 8.6, 8.0, 2.4, "#80858e", font="arialbd", ax="LEFT")
    # bottom regulatory sticker (seen from -y)
    r, uv, ctx = at.panel(62.0, 40.0, 12.0, bg="#dedfe1")
    reg["sticker"] = uv
    with ctx as a:
        a.rect(0, 34.0, 62.0, 40.0, "#1d1f24", z=0.1)
        a.text("QUILL", 2.0, 37.0, 3.6, "#f2f2f2", font="agency", ax="LEFT")
        a.text("2.5\" SATA SSD", 60.0, 37.0, 2.2, "#f2f2f2", font="arialbd", ax="RIGHT")
        lines = ["Model: QS3-500G", "Capacity: 500GB", "Rating: 5V ⎓ 1.4A", "FW: Q3FW1.02", "P/N: QS3500G-2.5S"]
        for i, s in enumerate(lines):
            a.text(s, 2.0, 30.5 - i * 3.0, 1.9, "#1a1a1a", font="narrowbd", ax="LEFT")
        bx = 2.0
        while bx < 40.0:
            w = rnd.choice([0.25, 0.25, 0.5, 0.75])
            a.rect(bx, 5.0, bx + w, 12.0, "#111111", z=0.2)
            bx += w + rnd.choice([0.25, 0.5])
        a.text("S/N 2416QS0B33A9", 21.0, 3.2, 1.6, "#111111", font="ocr")
        a.ring(51.0, 24.0, 3.4, 4.0, "#1a1a1a", z=0.2)
        a.text("CE", 51.0, 24.0, 3.0, "#1a1a1a", font="arialbd")
        a.text("MADE IN CHINA", 51.0, 14.0, 1.6, "#1a1a1a", font="narrowbd")
        a.text("WARRANTY VOID IF REMOVED", 51.0, 9.0, 1.1, "#1a1a1a", font="narrowbd", fit=18)
    reg["cover"] = at.swatch("#1f2125")
    reg["edge"] = at.swatch("#3a3c40")
    at.render(pp.tex_path("ssd_sata_500"))
    pp.PREVIEW_TEX["ssd_sata_500"] = (0.0, 0.42)
    return "ssd_sata_500", reg


def build_sata():
    sid = "ssd_sata_500"
    c.reset()
    tex, reg = sata_textures()
    TX = "tex_" + tex
    root = c.root(sid)
    k = pp.Kit(sid)
    hy = BT / 2
    # bottom tray (painted metal) with the connector pocket on the -x end, and the thin top lid with the art
    y0, y1 = -hy, SEAM
    xe = -BL / 2
    pk = dict(x1=xe + 4.6, y0=-hy + 0.5, y1=SEAM - 0.5, z0=PWR["z"] - PWR["w"] / 2 - 1.2, z1=DATA["z"] + DATA["w"] / 2 + 1.2)
    tray = k["paint_black"]
    pp.box(tray, ((pk["x1"] + BL / 2) / 2 * MM, (y0 + y1) / 2 * MM, 0), ((BL / 2 - pk["x1"]) * MM, (y1 - y0) * MM, BW * MM), bevel=0.0005)
    def slab(xa, xb, ya, yb, za, zb):
        pp.box(tray, ((xa + xb) / 2 * MM, (ya + yb) / 2 * MM, (za + zb) / 2 * MM), ((xb - xa) * MM, (yb - ya) * MM, (zb - za) * MM))
    slab(xe, pk["x1"], y0, pk["y0"], -BW / 2 + 0.4, BW / 2 - 0.4)
    slab(xe, pk["x1"], pk["y1"], y1, -BW / 2 + 0.4, BW / 2 - 0.4)
    slab(xe, pk["x1"], pk["y0"], pk["y1"], -BW / 2 + 0.4, pk["z0"])
    slab(xe, pk["x1"], pk["y0"], pk["y1"], pk["z1"], BW / 2 - 0.4)
    # rounded outer corners of the end slabs
    for zz in (-BW / 2 + 0.4, BW / 2 - 0.4):
        pp.cyl(tray, ((xe + pk["x1"]) / 2 * MM, (y0 + y1) / 2 * MM, zz * MM), 0.4 * MM, (y1 - y0) * MM, axis="y", seg=8)
    top_map = pp.MultiMap([pp.Planar(reg["top"], (0, hy * MM, 0), (0, 1, 0), (0, 0, 1), (BL * MM, BW * MM), thresh=0.8), reg["cover"]])
    pp.box(k[TX], (0, (SEAM + 0.12 + hy) / 2 * MM, 0), (BL * MM, (hy - SEAM - 0.12) * MM, BW * MM), bevel=0.0005, uv=top_map)
    # the seam line between lid and tray
    pp.box(k["black_plastic"], (0, (SEAM + 0.06) * MM, 0), ((BL - 0.5) * MM, 0.12 * MM, (BW - 0.5) * MM))
    # connector: the plastic housing at the pocket's back wall and two keyed tongues with gold contacts
    pp.box(k["connector_black"], ((pk["x1"] - 0.4) * MM, (pk["y0"] + pk["y1"]) / 2 * MM, (pk["z0"] + pk["z1"]) / 2 * MM),
           (0.8 * MM, (pk["y1"] - pk["y0"]) * MM, (pk["z1"] - pk["z0"]) * MM))
    for seg in (DATA, PWR):
        zc, w = seg["z"], seg["w"]
        pp.box(k["connector_black"], ((xe + 2.6) * MM, CONN_Y * MM, zc * MM), (3.8 * MM, 1.1 * MM, (w - 1.2) * MM), bevel=0.0001)
        pp.box(k["connector_black"], ((xe + 2.6) * MM, (CONN_Y + 1.15) * MM, (zc + w / 2 - 0.9) * MM), (3.8 * MM, 3.4 * MM, 1.0 * MM))
        n = seg["pins"]
        for i in range(n):
            z = zc - (n - 1) * 1.27 / 2 + i * 1.27
            pp.quad(k["gold"], ((xe + 2.4) * MM, (CONN_Y + 0.56) * MM, z * MM), (0.0007, 0.0030), normal=(0, 1, 0), up=(1, 0, 0))
    # screw holes: 4 side (M3, anchors) + 4 bottom
    for i, x in enumerate(HOLE_X):
        for s in (-1, 1):
            pp.cyl(k["black_plastic"], (x * MM, HOLE_Y * MM, s * (BW / 2 + 0.01) * MM), 1.45 * MM, 0.1 * MM, axis="z", seg=16)
            pp.tube_ring(k["steel"], (x * MM, HOLE_Y * MM, s * (BW / 2 + 0.03) * MM), 1.45 * MM, 1.9 * MM, 0.1 * MM, axis="z", seg=16)
            pp.cyl(k["black_plastic"], (x * MM, (-hy - 0.01) * MM, s * BOTTOM_Z * MM), 1.45 * MM, 0.1 * MM, axis="y", seg=16)
    # bottom sticker
    pp.quad(k[TX], (6.0 * MM, (-hy - 0.03) * MM, 0), (0.062, 0.040), normal=(0, -1, 0), up=(0, 0, 1), region=reg["sticker"])
    k.finish(root)

    # anchors: SATA sockets face -x (plugs come from -x); up = +y (the top cover)
    xa = (xe) * MM
    c.anchor("A_PORT_SATADATA_0", (xa, CONN_Y * MM, DATA["z"] * MM), (0.012, 0.006, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.0045,pins=7")
    c.anchor("A_PORT_SATAPWR_0", (xa, CONN_Y * MM, PWR["z"] * MM), (0.024, 0.006, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.0045,pins=15")
    n = 0
    for x in HOLE_X:
        for s in (-1, 1):
            c.anchor(f"A_SCREW_PH2_{n}", (x * MM, HOLE_Y * MM, s * BW / 2 * MM), (0.006, 0.006, 0.006), root, forward=(0, 0, s), up=(0, 1, 0),
                     meta="m3,side")
            n += 1
    c.anchor("A_HIT_0", (0, 0, 0), (BL * MM, BT * MM, BW * MM), root)
    c.join_by_tag(root, sid)
    c.export(root, sid)
    pp.report(root)
    return root


def previews(sid, root):
    if sid == "ssd_1tb":
        pp.preview(root, sid, views=((20, 50), (-40, 30), (160, -40)), size=(960, 720), dist=0.15, zup=True)
        pp.preview(root, sid, views=((-60, 35),), size=(960, 720), dist=0.07, target=(-0.025, 0, 0.001), start=3, zup=True)
    else:
        pp.preview(root, sid, views=((30, 35), (-120, 25), (160, -45)), size=(960, 720), dist=0.26)
        pp.preview(root, sid, views=((-90, 10),), size=(960, 720), dist=0.09, target=(-0.05, 0, 0.008), start=3)


def main(ids=None):
    for sid in ids or ["ssd_1tb", "ssd_sata_500"]:
        root = build_m2() if sid == "ssd_1tb" else build_sata()
        previews(sid, root)


if __name__ == "__main__":
    main(c.args() or None)
