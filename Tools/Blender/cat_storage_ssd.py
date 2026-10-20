"""
Catalogue storage, part 1: M.2 2280 NVMe drives (the ssd_1tb contract) and 2.5" SATA SSDs (the ssd_sata_500
contract), built from per-model configs (build_cat_storage.py holds the configs and runs them).

Frames and anchors are exactly those of build_ssd.py (its outline, finger and connector constants are imported,
build_ssd.py itself is unchanged):
  M.2:  origin at the PCB centre on its bottom face, PCB z 0..0.0008, connector (M key) at -x, screw notch at +x.
        A_SCREW_PH0_0, A_KEY_M2_0, A_HIT_0 (the hitbox grows to cover a heatsink).
  2.5": origin at the body centre, x = length (connectors at -x), y = thickness (+y = top), z = width.
        A_PORT_SATADATA_0, A_PORT_SATAPWR_0, A_SCREW_PH2_0..3, A_HIT_0.
"""
import math
import os
import random
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_ssd as bs  # noqa: E402

MM = 0.001
L, W, T = bs.L, bs.W, bs.T
GOLD = bs.GOLD


def texname(sid):
    """Texture file of a model: the id without its kind prefix, so '<name>#tex_<file>' stays under Blender's 63 characters."""
    return sid.split("_", 1)[1]


def barcode(a, x0, y0, x1, y1, rnd, ink="#111111", unit=0.2):
    bx = x0
    while bx < x1:
        w = rnd.choice([1, 1, 2, 3]) * unit
        a.rect(bx, y0, min(x1, bx + w), y1, ink, z=0.35)
        bx += w + rnd.choice([1, 2]) * unit


def traces(a, w, h, rnd, col, n=140, dot=None):
    for k in range(n):
        u0, v0 = rnd.uniform(1, w - 1), rnd.uniform(1, h - 1)
        pts = [(u0, v0)]
        for s in range(rnd.randint(2, 4)):
            dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (-1, 1), (-1, 0), (0, -1)])
            Lr = rnd.uniform(1.0, 6.0)
            u0 = min(w - 0.6, max(0.6, u0 + dx * Lr))
            v0 = min(h - 0.6, max(0.6, v0 + dy * Lr))
            pts.append((u0, v0))
        a.line(pts, 0.13, col, z=0.1)
    if dot:
        for k in range(n * 2):
            a.circle(rnd.uniform(1, w - 1), rnd.uniform(1, h - 1), 0.2, dot, z=0.15, seg=8)


# ================================================================== M.2


def m2_textures(cfg):
    sid = cfg["id"]
    pcb = cfg.get("pcb", "#121417")
    silk = cfg.get("silk", "#e6e6e0")
    at = pp.Atlas(2048, 2048, bg=pcb)
    rnd = random.Random(zlib.crc32(sid.encode()))
    reg = {}
    ppm = 12.0
    lighter = pp.shade(pcb, 1.6)

    def to_top(x, y):
        return L / 2 - x, y + W / 2

    r, uv, ctx = at.panel(L, W, ppm, bg=pcb)
    reg["top"] = uv
    with ctx as a:
        traces(a, L, W, rnd, lighter, 140, pp.shade(pcb, 2.1))
        for y, side in bs.m2_fingers():
            if side > 0:
                u, v = to_top(-L / 2, y)
                a.rect(u - 2.9, v - 0.18, u, v + 0.18, GOLD, z=0.2)
        u, v = to_top(L / 2, 0)
        a.ring(u, v, bs.NOTCH_R, bs.NOTCH_R + 1.4, GOLD, z=0.2)
        for (x, y, l, w) in cfg["chips_top"]:
            u, v = to_top(x, y)
            a.frame_rect(u - l / 2 - 0.5, v - w / 2 - 0.5, u + l / 2 + 0.5, v + w / 2 + 0.5, 0.15, silk, z=0.3)
        for (x, y, ang, kind) in cfg["passives"]:
            u, v = to_top(x, y)
            for s in (-1, 1):
                if ang == 0:
                    a.rect(u + s * 0.5 - 0.25, v - 0.3, u + s * 0.5 + 0.25, v + 0.3, "#b8b8b0", z=0.25)
                else:
                    a.rect(u - 0.3, v + s * 0.5 - 0.25, u + 0.3, v + s * 0.5 + 0.25, "#b8b8b0", z=0.25)
        a.text("2280", *to_top(37.6, 8.6), 1.0, silk, font="narrowbd")
    # bottom (seen from below: u = x + L/2)
    r, uv, ctx = at.panel(L, W, ppm, bg=pcb)
    reg["bottom"] = uv
    with ctx as a:
        traces(a, L, W, rnd, lighter, 160)
        for y, side in bs.m2_fingers():
            if side < 0:
                v = y + W / 2
                a.rect(0.0, v - 0.18, 2.9, v + 0.18, GOLD, z=0.2)
        a.ring(L, W / 2, bs.NOTCH_R, bs.NOTCH_R + 1.4, GOLD, z=0.2)
        for (x, y, l, w) in cfg.get("chips_bottom", []):
            u, v = x + L / 2, y + W / 2
            a.frame_rect(u - l / 2 - 0.5, v - w / 2 - 0.5, u + l / 2 + 0.5, v + w / 2 + 0.5, 0.15, silk, z=0.3)
    # the bottom regulatory sticker
    sw, sh = cfg.get("sticker_size", (40.0, 16.0))
    r, uv, ctx = at.panel(sw, sh, 20.0, bg=cfg.get("sticker_bg", "#d9dadc"))
    reg["sticker"] = uv
    with ctx as a:
        ink = cfg.get("sticker_ink", "#1a1a1a")
        a.text(cfg["brand"].upper(), 1.5, sh - 2.4, 2.2, ink, font="agency", ax="LEFT")
        for i, s in enumerate(cfg["sticker_lines"]):
            a.text(s, 1.5, sh - 5.2 - i * 1.8, 1.2, ink, font="narrowbd", ax="LEFT", fit=sw * 0.62)
        barcode(a, 1.5, 1.6, sw * 0.6, 4.0, rnd, ink)
        a.text(cfg.get("sn", "S/N 2431X0A71C3"), sw * 0.31, 0.8, 0.8, ink, font="ocr")
        a.ring(sw - 5.0, sh - 5.0, 2.0, 2.35, ink, z=0.35)
        a.text("CE", sw - 5.0, sh - 5.0, 1.6, ink, font="arialbd")
        a.text("MADE IN " + cfg.get("origin", "KOREA"), sw - 5.0, 4.6, 0.9, ink, font="narrowbd")
        a.text("WARRANTY VOID IF REMOVED", sw - 5.0, 2.6, 0.6, ink, font="narrowbd", fit=8.5)
    # the top label (u along -x from the label's +x end, v along +y)
    lx0, lx1 = cfg["label_x"]
    r, uv, ctx = at.panel(lx1 - lx0, cfg.get("label_w", 20.0), 20.0, bg=cfg.get("label_bg", "#141414"))
    reg["label"] = uv
    with ctx as a:
        cfg["label_art"](a, lx1 - lx0, cfg.get("label_w", 20.0), rnd)
    # controller marking
    cs = cfg["ctrl"]["s"]
    r, uv, ctx = at.panel(cs, cs, 30.0, bg=cfg["ctrl"].get("top", "#1b1c1e"))
    reg["ctrl"] = uv
    with ctx as a:
        ink = cfg["ctrl"].get("ink", "#8a8d93")
        lines = cfg["ctrl"]["mark"]
        for i, s in enumerate(lines):
            a.text(s, cs / 2, cs * 0.76 - i * cs * 0.17, cs * (0.13 if i else 0.15), ink,
                   font="agency" if i == 0 else "arialbd", fit=cs * 0.9)
        a.circle(cs * 0.1, cs * 0.1, cs * 0.04, pp.shade(cfg["ctrl"].get("top", "#1b1c1e"), 1.6), z=0.2)
    r, uv, ctx = at.panel(8.0, 8.0, 30.0, bg="#1b1c1e")
    reg["dram"] = uv
    with ctx as a:
        for i, s in enumerate(cfg.get("dram_mark", ["SORIN", "K4F8E3S4HD", "MGCL"])):
            a.text(s, 4.0, 6.0 - i * 1.6, 1.0 if i else 1.2, "#86898f", font="agency" if i == 0 else "arialbd", fit=7.2)
    r, uv, ctx = at.panel(12.0, 12.0, 30.0, bg="#1b1c1e")
    reg["nand"] = uv
    with ctx as a:
        for i, s in enumerate(cfg.get("nand_mark", ["SORIN", "K9DUGB8H1A", "CCK0 2405"])):
            a.text(s, 6.0, 8.6 - i * 2.0, 1.4 if i else 1.7, "#86898f", font="agency" if i == 0 else "arialbd", fit=10.5)
    r, uv, ctx = at.panel(3.0, 3.0, 40.0, bg="#1b1c1e")
    reg["pmic"] = uv
    with ctx as a:
        a.text("S2D", 1.5, 1.8, 0.8, "#8a8d93", font="arialbd")
        a.text("4C1", 1.5, 0.9, 0.7, "#8a8d93", font="arialbd")
    if cfg.get("heatsink"):
        hs = cfg["heatsink"]
        hw, hh = hs["top_size"]
        r, uv, ctx = at.panel(hw, hh, 16.0, bg=hs.get("top_bg", "#16171a"))
        reg["hs_top"] = uv
        with ctx as a:
            hs["art"](a, hw, hh, rnd)
        reg["hs_body"] = at.swatch(hs.get("body", "#141518"))
        if hs.get("side_art"):
            sw2, sh2 = hs["side_size"]
            r, uv, ctx = at.panel(sw2, sh2, 16.0, bg=hs.get("body", "#141518"))
            reg["hs_side"] = uv
            with ctx as a:
                hs["side_art"](a, sw2, sh2, rnd)
    reg["black"] = at.swatch("#141518")
    reg["ctrl_side"] = at.swatch(cfg["ctrl"].get("side", "#141518"))
    reg["edge"] = at.swatch(pp.mix(pcb, "#c9a24c", 0.25))
    reg["label_edge"] = at.swatch(cfg.get("label_bg", "#141414"))
    at.render(pp.tex_path(texname(sid)))
    pp.PREVIEW_TEX[texname(sid)] = (0.0, 0.42)
    return reg


def build_m2(cfg):
    sid = cfg["id"]
    c.reset()
    reg = m2_textures(cfg)
    TX = "tex_" + texname(sid)
    root = c.root(sid)
    k = pp.Kit("m")
    t = T * MM
    mapper = pp.MultiMap([pp.Planar(reg["top"], (0, 0, t), (0, 0, 1), (0, 1, 0), (L * MM, W * MM)),
                          pp.Planar(reg["bottom"], (0, 0, 0), (0, 0, -1), (0, 1, 0), (L * MM, W * MM)),
                          reg["edge"]])
    pp.prism(k[TX], [[(x * MM, y * MM) for x, y in bs.m2_outline()]], 0.0, t, uv=mapper)
    for y, side in bs.m2_fingers():
        z = t + 0.00002 if side > 0 else -0.00002
        pp.quad(k["gold"], ((-L / 2 + 1.45) * MM, y * MM, z), (0.00036, 0.0029), normal=(0, 0, side), up=(1, 0, 0))
    # controller: a nickel lid (990 Pro style) or a marked moulded package
    ct = cfg["ctrl"]
    if ct.get("nickel"):
        pp.box(k["chip_black"], (ct["x"] * MM, 0, t + 0.35 * MM), ((ct["s"] + 0.6) * MM, (ct["s"] + 0.6) * MM, 0.7 * MM), bevel=0.0001)
        lid = pp.MultiMap([pp.Planar(reg["ctrl"], (ct["x"] * MM, 0, t + ct["h"] * MM), (0, 0, 1), (1, 0, 0), (ct["s"] * MM, ct["s"] * MM)),
                           reg["ctrl_side"]])
        pp.box(k[TX], (ct["x"] * MM, 0, t + (ct["h"] + 0.7) * 0.5 * MM), (ct["s"] * MM, ct["s"] * MM, (ct["h"] - 0.7) * MM), bevel=0.0002, uv=lid)
    else:
        pp.chip_marked(k[TX], ct["x"] * MM, 0, t, ct["s"] * MM, ct["s"] * MM, ct["h"] * MM, reg["ctrl"], reg["ctrl_side"], text_rot=90)
    if cfg.get("dram"):
        dx, dy = cfg["dram"]
        pp.chip_marked(k[TX], dx * MM, dy * MM, t, 8.0 * MM, 8.0 * MM, 0.9 * MM, reg["dram"], reg["black"], text_rot=90)
    for (x, y, l, w) in cfg["nand"]:
        pp.chip_marked(k[TX], x * MM, y * MM, t, l * MM, w * MM, 1.2 * MM, reg["nand"], reg["black"], text_rot=90)
    for (x, y, l, w) in cfg.get("chips_bottom", []):
        bmap = pp.MultiMap([pp.Planar(reg["nand"], (x * MM, y * MM, -1.2 * MM), (0, 0, -1), (-1, 0, 0), (w * MM, l * MM)), reg["black"]])
        pp.box(k[TX], (x * MM, y * MM, -0.6 * MM), (l * MM, w * MM, 1.2 * MM), bevel=0.00015, uv=bmap)
    px, py = cfg.get("pmic", (30.5, 6.5))
    pp.chip_marked(k[TX], px * MM, py * MM, t, 3.0 * MM, 3.0 * MM, 0.8 * MM, reg["pmic"], reg["black"])
    for (ix, iy) in cfg.get("inductors", [(31.0, -4.0)]):
        pp.box(k["dark_plastic"], (ix * MM, iy * MM, t + 0.6 * MM), (2.6 * MM, 2.0 * MM, 1.2 * MM), bevel=0.00015)
    for (x, y, ang, kind) in cfg["passives"]:
        body = "ceramic" if kind == "cap" else "chip_black"
        pp.smd_passive(k, x * MM, y * MM, t, 0.001, 0.0005, 0.0005, ang=ang, body=body)
    # top label: a thin printed sheet resting on the tallest chips
    top_h = max([1.2 if cfg["nand"] else 0.0, ct["h"]] + ([0.9] if cfg.get("dram") else []))
    if not cfg.get("heatsink") or cfg.get("label_under_hs"):
        lz = t + top_h * MM + 0.00006
        lx0, lx1 = cfg["label_x"]
        lw = cfg.get("label_w", 20.0)
        lmap = pp.MultiMap([pp.Planar(reg["label"], ((lx0 + lx1) / 2 * MM, 0, lz), (0, 0, 1), (0, 1, 0), ((lx1 - lx0) * MM, lw * MM)),
                            reg["label_edge"]])
        pp.box(k[TX], ((lx0 + lx1) / 2 * MM, 0, lz), ((lx1 - lx0) * MM, lw * MM, 0.00012), uv=lmap)
    # bottom sticker (between the bottom chips' top and the PCB, or flat on the PCB)
    if cfg.get("sticker_x") is not None:
        sw, sh = cfg.get("sticker_size", (40.0, 16.0))
        bz = -0.00003 - (1.2 * MM if cfg.get("chips_bottom") else 0.0)
        pp.quad(k[TX], (cfg["sticker_x"] * MM, 0, bz), (sw * MM, sh * MM), normal=(0, 0, -1), up=(0, 1, 0), region=reg["sticker"])
    hs_top = 0.0
    if cfg.get("heatsink"):
        hs_top = build_m2_heatsink(k, TX, reg, cfg["heatsink"], t)
    k.finish(root)

    c.anchor("A_SCREW_PH0_0", (L / 2 * MM, 0, t), (0.006, 0.006, 0.004), root, meta="notch=+x")
    if cfg.get("heatsink"):
        z0 = cfg["heatsink"].get("bottom", -1.2) * MM
        c.anchor("A_HIT_0", (0, 0, (z0 + hs_top) / 2), (L * MM, cfg["heatsink"]["w"] * MM, hs_top - z0), root)
    else:
        c.anchor("A_HIT_0", (0, 0, 0.0012), (L * MM, W * MM, 0.0026), root)
    c.anchor("A_KEY_M2_0", (-L / 2 * MM, bs.MKEY_Y * MM, t * 0.5), (0.002, 0.0015, 0.002), root, meta=f"key=M,y={bs.MKEY_Y * MM:.4f}")
    c.join_by_tag(root, "m")
    c.export(root, sid)
    pp.report(root)
    return root


def build_m2_heatsink(k, TX, reg, hs, t):
    """A clip-on heatsink shell around the drive (it leaves the M.2 fingers and the screw notch free).
    Returns the top height (m)."""
    x0, x1 = hs["x"]
    w = hs["w"]
    zb = hs.get("bottom", -1.2)
    zt = hs["base_top"]
    cx = (x0 + x1) / 2
    body = hs.get("body_tag", TX)
    kind = hs["kind"]
    top_map = pp.MultiMap([pp.Planar(reg["hs_top"], (cx * MM, 0, zt * MM), (0, 0, 1), (0, 1, 0), ((x1 - x0) * MM, w * MM), thresh=0.9),
                           reg["hs_body"]])
    if kind in ("sorin", "westline"):
        # the shell: a lower body around the PCB, a slightly narrower raised top plate with chamfered edges
        pp.box(k[TX], (cx * MM, 0, (zb + 2.6) / 2 * MM), ((x1 - x0) * MM, w * MM, (2.6 - zb) * MM), bevel=0.0004, uv=reg["hs_body"])
        pp.box(k[TX], (cx * MM, 0, (2.4 + zt) / 2 * MM), ((x1 - x0 - 0.6) * MM, (w - 0.8) * MM, (zt - 2.4) * MM), bevel=0.0009, seg=2,
               uv=top_map)
        # the seam where the top meets the bottom half
        pp.box(k["black_plastic"], (cx * MM, 0, 2.5 * MM), ((x1 - x0 - 0.4) * MM, (w + 0.02) * MM, 0.25 * MM))
        if kind == "westline":
            # angular raised fins over the cooler's rear two thirds, cut at an angle like the real thing
            for i in range(5):
                xf = x1 - 28.6 + i * 5.6
                pp.box(k[TX], (xf * MM, 0, (zt + 0.55) * MM), (2.2 * MM, (w - 4.0) * MM, 1.1 * MM), pp.rot("z", 0), bevel=0.0003,
                       uv=reg["hs_body"])
            zt += 1.1
        # RGB light bar on the +x end face (and a strip on top at that end)
        rx = x1 - 2.2
        pp.box(k["rgb"], (rx * MM, 0, (zt + 0.06) * MM), (2.6 * MM, (w - 4.0) * MM, 0.25 * MM), bevel=0.0001)
        pp.box(k["rgb"], ((x1 + 0.06) * MM, 0, (zb + zt) / 2 * MM + 0.0006), (0.25 * MM, (w - 3.0) * MM, (zt - zb - 3.2) * MM))
        return zt * MM + 0.0002
    # "fins": a tall fin stack (Gen5): a base shell and longitudinal fins with a brand bar along the top centre
    fin_top = hs["fin_top"]
    pp.box(k[TX], (cx * MM, 0, (zb + zt) / 2 * MM), ((x1 - x0) * MM, w * MM, (zt - zb) * MM), bevel=0.0004, uv=reg["hs_body"])
    nf = hs.get("fins", 11)
    pitch = (w - 1.0) / (nf - 1)
    for i in range(nf):
        y = -(w - 1.0) / 2 + i * pitch
        if abs(y) < hs.get("bar_w", 7.0) / 2 + 0.3:
            continue
        pp.box(k[TX], (cx * MM, y * MM, (zt + fin_top) / 2 * MM), ((x1 - x0 - 1.0) * MM, 0.75 * MM, (fin_top - zt) * MM), bevel=0.00015,
               uv=reg["hs_body"])
    # centre brand bar (solid), with the printed top
    bw = hs.get("bar_w", 7.0)
    bar_map = pp.MultiMap([pp.Planar(reg["hs_top"], (cx * MM, 0, fin_top * MM), (0, 0, 1), (0, 1, 0), ((x1 - x0) * MM, bw * MM), thresh=0.9),
                           pp.Planar(reg["hs_side"], (cx * MM, -bw / 2 * MM, (zt + fin_top) / 2 * MM), (0, -1, 0), (0, 0, 1),
                                     ((x1 - x0) * MM, (fin_top - zt) * MM), thresh=0.9) if reg.get("hs_side") else reg["hs_body"],
                           reg["hs_body"]])
    pp.box(k[TX], (cx * MM, 0, (zt + fin_top) / 2 * MM), ((x1 - x0 - 0.4) * MM, bw * MM, (fin_top - zt) * MM), bevel=0.0004, uv=bar_map)
    # silver end accents
    for xe in (x0 + 0.7, x1 - 0.7):
        pp.box(k["alu"], (xe * MM, 0, (zt + 1.0) * MM), (1.0 * MM, (w + 0.1) * MM, 1.6 * MM), bevel=0.0002)
    return fin_top * MM


# ================================================================== 2.5" SATA

BL, BT, BW = bs.BL, bs.BT, bs.BW
SEAM = bs.SEAM
DATA, PWR, CONN_Y = bs.DATA, bs.PWR, bs.CONN_Y


def sata_textures(cfg):
    sid = cfg["id"]
    at = pp.Atlas(2048, 1024, bg="#202226")
    rnd = random.Random(zlib.crc32(sid.encode()))
    reg = {}
    r, uv, ctx = at.panel(BL, BW, 10.0, bg=cfg.get("top_bg", "#24262b"))
    reg["top"] = uv
    with ctx as a:
        cfg["top_art"](a, BL, BW, rnd)
    sw, sh = 62.0, 40.0
    r, uv, ctx = at.panel(sw, sh, 12.0, bg=cfg.get("sticker_bg", "#dedfe1"))
    reg["sticker"] = uv
    with ctx as a:
        a.rect(0, 34.0, sw, sh, cfg.get("sticker_band", "#1d1f24"), z=0.1)
        a.text(cfg["brand"].upper(), 2.0, 37.0, 3.6, "#f2f2f2", font="agency", ax="LEFT")
        a.text("2.5\" SATA SSD", 60.0, 37.0, 2.2, "#f2f2f2", font="arialbd", ax="RIGHT")
        for i, s in enumerate(cfg["sticker_lines"]):
            a.text(s, 2.0, 30.5 - i * 3.0, 1.9, "#1a1a1a", font="narrowbd", ax="LEFT", fit=40)
        barcode(a, 2.0, 5.0, 40.0, 12.0, rnd, unit=0.25)
        a.text(cfg.get("sn", "S/N 2416QS0B33A9"), 21.0, 3.2, 1.6, "#111111", font="ocr")
        a.ring(51.0, 24.0, 3.4, 4.0, "#1a1a1a", z=0.2)
        a.text("CE", 51.0, 24.0, 3.0, "#1a1a1a", font="arialbd")
        a.text("MADE IN " + cfg.get("origin", "CHINA"), 51.0, 14.0, 1.6, "#1a1a1a", font="narrowbd", fit=18)
        a.text("WARRANTY VOID IF REMOVED", 51.0, 9.0, 1.1, "#1a1a1a", font="narrowbd", fit=18)
    reg["cover"] = at.swatch(cfg.get("cover", "#1f2125"))
    at.render(pp.tex_path(texname(sid)))
    pp.PREVIEW_TEX[texname(sid)] = cfg.get("pbr", (0.0, 0.42))
    return reg


def build_sata(cfg):
    """build_ssd.build_sata with the look from cfg: same tray, pocket, connectors, holes and anchors."""
    sid = cfg["id"]
    c.reset()
    reg = sata_textures(cfg)
    TX = "tex_" + texname(sid)
    root = c.root(sid)
    k = pp.Kit("m")
    hy = BT / 2
    y0, y1 = -hy, SEAM
    xe = -BL / 2
    pk = dict(x1=xe + 4.6, y0=-hy + 0.5, y1=SEAM - 0.5, z0=PWR["z"] - PWR["w"] / 2 - 1.2, z1=DATA["z"] + DATA["w"] / 2 + 1.2)
    tray = k[cfg.get("tray", "paint_black")]
    pp.box(tray, ((pk["x1"] + BL / 2) / 2 * MM, (y0 + y1) / 2 * MM, 0), ((BL / 2 - pk["x1"]) * MM, (y1 - y0) * MM, BW * MM), bevel=0.0005)

    def slab(xa, xb, ya, yb, za, zb):
        pp.box(tray, ((xa + xb) / 2 * MM, (ya + yb) / 2 * MM, (za + zb) / 2 * MM), ((xb - xa) * MM, (yb - ya) * MM, (zb - za) * MM))
    slab(xe, pk["x1"], y0, pk["y0"], -BW / 2 + 0.4, BW / 2 - 0.4)
    slab(xe, pk["x1"], pk["y1"], y1, -BW / 2 + 0.4, BW / 2 - 0.4)
    slab(xe, pk["x1"], pk["y0"], pk["y1"], -BW / 2 + 0.4, pk["z0"])
    slab(xe, pk["x1"], pk["y0"], pk["y1"], pk["z1"], BW / 2 - 0.4)
    for zz in (-BW / 2 + 0.4, BW / 2 - 0.4):
        pp.cyl(tray, ((xe + pk["x1"]) / 2 * MM, (y0 + y1) / 2 * MM, zz * MM), 0.4 * MM, (y1 - y0) * MM, axis="y", seg=8)
    top_map = pp.MultiMap([pp.Planar(reg["top"], (0, hy * MM, 0), (0, 1, 0), (0, 0, 1), (BL * MM, BW * MM), thresh=0.8), reg["cover"]])
    lid_bevel = cfg.get("lid_bevel", 0.5)
    pp.box(k[TX], (0, (SEAM + 0.12 + hy) / 2 * MM, 0), (BL * MM, (hy - SEAM - 0.12) * MM, BW * MM), bevel=lid_bevel * MM,
           seg=cfg.get("lid_seg", 1), uv=top_map)
    pp.box(k[cfg.get("seam", "black_plastic")], (0, (SEAM + 0.06) * MM, 0), ((BL - 0.5) * MM, 0.12 * MM, (BW - 0.5) * MM))
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
    for i, x in enumerate(bs.HOLE_X):
        for s in (-1, 1):
            pp.cyl(k["black_plastic"], (x * MM, bs.HOLE_Y * MM, s * (BW / 2 + 0.01) * MM), 1.45 * MM, 0.1 * MM, axis="z", seg=16)
            pp.tube_ring(k["steel"], (x * MM, bs.HOLE_Y * MM, s * (BW / 2 + 0.03) * MM), 1.45 * MM, 1.9 * MM, 0.1 * MM, axis="z", seg=16)
            pp.cyl(k["black_plastic"], (x * MM, (-hy - 0.01) * MM, s * bs.BOTTOM_Z * MM), 1.45 * MM, 0.1 * MM, axis="y", seg=16)
    pp.quad(k[TX], (6.0 * MM, (-hy - 0.03) * MM, 0), (0.062, 0.040), normal=(0, -1, 0), up=(0, 0, 1), region=reg["sticker"])
    # optional extras on the top: lid screws (plastic shells have none), a recessed panel
    for (sx, sz) in cfg.get("top_screws", []):
        pp.cyl(k["steel_dark"], (sx * MM, (hy + 0.02) * MM, sz * MM), 1.1 * MM, 0.08 * MM, axis="y", seg=12)
    k.finish(root)

    xa = xe * MM
    c.anchor("A_PORT_SATADATA_0", (xa, CONN_Y * MM, DATA["z"] * MM), (0.012, 0.006, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.0045,pins=7")
    c.anchor("A_PORT_SATAPWR_0", (xa, CONN_Y * MM, PWR["z"] * MM), (0.024, 0.006, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.0045,pins=15")
    n = 0
    for x in bs.HOLE_X:
        for s in (-1, 1):
            c.anchor(f"A_SCREW_PH2_{n}", (x * MM, bs.HOLE_Y * MM, s * BW / 2 * MM), (0.006, 0.006, 0.006), root, forward=(0, 0, s), up=(0, 1, 0),
                     meta="m3,side")
            n += 1
    c.anchor("A_HIT_0", (0, 0, 0), (BL * MM, BT * MM, BW * MM), root)
    c.join_by_tag(root, "m")
    c.export(root, sid)
    pp.report(root)
    return root


def previews_m2(sid, root, tall=False):
    pp.preview(root, sid, views=((20, 50), (-40, 30), (160, -40)), size=(960, 720), dist=0.16 if tall else 0.15, zup=True)
    pp.preview(root, sid, views=((-60, 35),), size=(960, 720), dist=0.08, target=(-0.025, 0, 0.004 if tall else 0.001), start=3, zup=True)


def previews_sata(sid, root):
    pp.preview(root, sid, views=((30, 35), (-120, 25), (160, -45)), size=(960, 720), dist=0.26)
    pp.preview(root, sid, views=((-90, 10),), size=(960, 720), dist=0.09, target=(-0.05, 0, 0.008), start=3)
