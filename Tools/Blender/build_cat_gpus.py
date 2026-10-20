r"""
build_cat_gpus.py - catalogue 11: fifteen graphics cards (13 desktop cards, 2 passive data-centre accelerators).

    blender -b --factory-startup -P Tools/Blender/build_cat_gpus.py -- [ids...] [--nopreview]

Every card is build_gpu.py's card with a new spec (put into build_gpu.SPECS) and its own style hooks, so the frame and
the anchor kinds are gpu_rx66 / rx77 / rx88's: the PCIe edge at the origin, the full-height bracket at x +0.095, the
cooler facing -y, the height along +z, A_PORT_DP_0..2 / A_PORT_HDMI_0 on the bracket, A_SCREW_PH2_0..1 in the case's
slot positions, A_HIT_0..2, A_FAN_n, A_FILM_BACKPLATE_0, A_FILM_SHROUD_0 and the power port(s) on the top edge
(A_PORT_PCIE8_0..1 or A_PORT_12V2X6_0). What varies: length, height, thickness, fans, colours, RGB and the shroud.

The two data-centre cards (gpu_verdia_t100, gpu_voltra_mi210) are passive: no A_FAN_n and no display ports
(build_gpu's "fans": 0 and "outputs": False hooks); see docs/reports/cat_gpus.md for their contract.

Brand art is drawn here (cat_texture: the logo plate, the hub sticker, the serial label, colour swatches), in the cell
layout build_gpu.build() expects. Writes Assets/Resources/Models/<id>.fbx, Textures/<id>.png, previews
Logs/ModelPreviews/<id>_<n>.png and the anchor report Logs/ModelPreviews/cat_gpus_report.txt.
"""
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import build_gpu as G  # noqa: E402

pb = G.pb
PREVIEW = [True]
REPORT = os.path.join(c.PREVIEWS, "cat_gpus_report.txt")

# ====================================================================== artwork

SW = ["sw%d" % i for i in range(8)]  # 64 x 64 colour swatches, s["swatches"][i]


def emblem(cv, kind, x, y, h, col, col2):
    """Brand marks in a box of height h at (x, y) (top-left). Returns the width used."""
    if kind == "voltra":  # a slanted V, the right blade split (as build_gpu)
        w = h * 0.9
        cv.poly([(x, y), (x + w * 0.28, y), (x + w * 0.52, y + h * 0.72), (x + w * 0.4, y + h)], col)
        cv.poly([(x + w * 0.62, y + h * 0.42), (x + w * 0.76, y), (x + w * 1.04, y), (x + w * 0.74, y + h * 0.62)], col2)
        return w * 1.05
    if kind == "verdia":  # a rounded square with an eye-like swirl cut through it
        cv.rect(x, y, h, h, col, r=h * 0.14)
        cx, cy = x + h * 0.56, y + h * 0.52
        lens = [(cx + h * 0.42 * math.cos(a * pb.DEG), cy + h * 0.24 * math.sin(a * pb.DEG)) for a in range(0, 360, 12)]
        cv.poly(lens, col2)
        cv.circle(cx, cy, h * 0.17, col)
        cv.circle(cx, cy, h * 0.07, col2)
        cv.poly([(x, y + h * 0.5), (x + h * 0.16, y + h * 0.5), (x + h * 0.16, y + h * 0.58), (x, y + h * 0.58)], col2)
        return h
    if kind == "tiron":  # an open ring with a bar, a dot on top
        cx, cy = x + h * 0.5, y + h * 0.55
        cv.ring(cx, cy, h * 0.30, h * 0.44, col)
        cv.rect(cx + h * 0.10, y + h * 0.02, h * 0.42, h * 0.22, col2)
        cv.rect(cx - h * 0.06, cy - h * 0.18, h * 0.12, h * 0.36, col)
        cv.circle(cx, y + h * 0.04, h * 0.06, col)
        return h
    if kind == "zenith":  # a peak with a sun over its shoulder
        cv.circle(x + h * 0.66, y + h * 0.30, h * 0.20, col2)
        cv.poly([(x, y + h), (x + h * 0.42, y + h * 0.18), (x + h * 0.62, y + h * 0.56), (x + h * 0.74, y + h * 0.42),
                 (x + h * 1.05, y + h)], col)
        cv.poly([(x + h * 0.30, y + h), (x + h * 0.42, y + h * 0.62), (x + h * 0.54, y + h)], col2)
        return h * 1.08
    if kind == "aegis":  # a shield with a slanted eye slit
        w = h * 0.82
        sh = [(x, y), (x + w, y), (x + w, y + h * 0.52), (x + w * 0.5, y + h), (x, y + h * 0.52)]
        cv.poly(sh, col)
        cv.poly([(x + w * 0.16, y + h * 0.40), (x + w * 0.84, y + h * 0.22), (x + w * 0.80, y + h * 0.36),
                 (x + w * 0.20, y + h * 0.54)], col2)
        return w * 1.05
    if kind == "mako":  # a shark fin
        pts = [(x, y + h)]
        for k in range(11):
            t = k / 10
            pts.append((x + h * (0.18 + 0.62 * t), y + h * (1.0 - math.sin(t * math.pi * 0.5) ** 0.7)))
        pts += [(x + h * 0.86, y + h * 0.04), (x + h * 0.82, y + h * 0.5), (x + h * 1.1, y + h)]
        cv.poly(pts, col)
        cv.poly([(x + h * 0.08, y + h * 0.88), (x + h * 1.0, y + h * 0.88), (x + h * 1.1, y + h), (x, y + h)], col2)
        return h * 1.12
    if kind == "kestrel":  # two swept wings
        for k, cc in ((0, col), (1, col2)):
            o = k * h * 0.28
            cv.poly([(x + o, y + h), (x + o + h * 0.45, y + h * 0.1), (x + o + h * 0.62, y + h * 0.1),
                     (x + o + h * 0.30, y + h * 0.76), (x + o + h * 0.7, y + h * 0.76), (x + o + h * 0.58, y + h)], cc)
        return h * 1.0
    raise KeyError(kind)


EM_W = dict(voltra=0.945, verdia=1.0, tiron=1.0, zenith=1.08, aegis=0.861, mako=1.12, kestrel=1.0)  # width / height


def cat_texture(pid, s):
    """build_gpu's atlas cells (logo, plate, hub, label, red, pcb) in this card's brand art, plus swatches."""
    a = s["art"]
    at = pb.Atlas(2048, 1024)
    at.add("logo", 0, 0, 1024, 128)
    at.add("plate", 0, 128, 1024, 128)
    at.add("hub", 1024, 0, 512, 512)
    at.add("label", 1536, 0, 512, 256)
    at.add("red", 1536, 256, 128, 128)
    at.add("pcb", 0, 512, 512, 512)
    at.add("badge", 512, 512, 1024, 128)  # a second name plate (series word), on the shroud face or the backplate
    at.add("strip", 512, 640, 1024, 64)  # a thin print strip
    for i in range(8):
        at.add(SW[i], 1536 + 64 * (i % 8), 384, 64, 64)
    cv = pb.Canvas(2048, 1024, bg="#0c0c0d")
    acc = a["accent"]
    bg, fg, dim = a["plate_bg"], a["plate_fg"], a["plate_dim"]
    maker = a.get("partner") or a["chip"]
    mk = maker.lower()
    em2 = a.get("em2", bg)

    # top-edge logo plate (1024 x 128): emblem, MAKER, divider, chip model, series word right
    cv.rect(0, 0, 1024, 128, bg)
    cv.rect(0, 0, 1024, 3, a.get("plate_line", dim))
    cv.rect(0, 125, 1024, 3, a.get("plate_line", dim))
    wem = emblem(cv, mk, 34, 28, 72, a.get("em_col", acc), em2)
    xt = 34 + wem + 24
    cv.text(maker, xt, 64, 50, fg, a.get("font", "agency"), "left", "center", spacing=1.3, maxw=250)
    cv.rect(xt + 265, 34, 3, 60, dim)
    cv.text(a["line"], xt + 290, 64, 40, fg, "eras_md", "left", "center", maxw=330)
    cv.text(a["series"], 994, 64, 26, acc, "agency", "right", "center", spacing=1.5, maxw=230)
    # second plate (1024 x 128): small print for the bottom edge
    cv.rect(0, 128, 1024, 128, bg)
    cv.text(maker + "  |  " + a["line"] + "  |  " + s["mem"], 512, 192, 34, dim if a.get("dark_print") else fg,
            "agency", "center", "center", spacing=1.3, maxw=960)
    # hub sticker (512 x 512)
    hx, hy = 1024 + 256, 256
    hb, hf, hr = a["hub"]
    cv.rect(1024, 0, 512, 512, hb)
    cv.circle(hx, hy, 250, hb)
    cv.ring(hx, hy, 228, 238, hr)
    eh = 150
    ew = EM_W[mk] * eh
    emblem(cv, mk, hx - ew / 2, hy - 126, eh, a.get("hub_em", hf), a.get("hub_em2", hb))
    cv.text(maker, hx, hy + 112, 44, hf, "agency", "center", "center", spacing=1.35, maxw=360)
    # serial label (512 x 256)
    lx, ly = 1536, 0
    cv.rect(lx, ly, 512, 256, "#f1f1ee")
    cv.text(maker, lx + 24, ly + 40, 30, "#111111", "agency", "left", "center", spacing=1.3, maxw=300)
    cv.text(a["chip"] + " " + a["line"] + " " + s["mem"], lx + 24, ly + 82, 20, "#111111", "arialb", "left",
            "center", maxw=310)
    cv.text("P/N " + a["pn"], lx + 24, ly + 116, 15, "#222222", "arial", "left", "center", maxw=310)
    cv.text(a["sn"], lx + 24, ly + 140, 15, "#222222", "arial", "left", "center")
    cv.barcode(lx + 24, ly + 158, 290, 52, seed=sum(map(ord, pid)))
    cv.text(a.get("made", "MADE IN TAIWAN"), lx + 24, ly + 228, 13, "#333333", "arialb", "left", "center")
    rng = random.Random(sum(map(ord, pid)) * 7)
    qx, qy, q = lx + 352, ly + 40, 8
    cells = []
    for i in range(17):
        for j in range(17):
            corner = (i < 5 and j < 5) or (i > 11 and j < 5) or (i < 5 and j > 11)
            if not corner and rng.random() < 0.5:
                cells.append((qx + i * q, qy + j * q, q, q))
    cv.rects(cells, "#111111")
    for (ix, iy) in ((0, 0), (12, 0), (0, 12)):
        cv.frame_rect(qx + ix * q, qy + iy * q, 5 * q, 5 * q, q, "#111111")
        cv.rect(qx + ix * q + 2 * q, qy + iy * q + 2 * q, q, q, "#111111")
    cv.text("CE  FC  UKCA", lx + 390, ly + 205, 14, "#333333", "arialb", "center", "center")
    # accent swatch and colour swatches
    cv.rect(1536, 256, 128, 128, s.get("swatch", acc))
    for i, col in enumerate(s.get("swatches", [])):
        cv.rect(1536 + 64 * i, 384, 64, 64, col)
    # badge (1024 x 128) and strip (1024 x 64)
    bb, bf = a.get("badge_bg", bg), a.get("badge_fg", fg)
    cv.rect(512, 512, 1024, 128, bb)
    cv.text(a.get("badge", a["series"]), 1024, 576, 64, bf, a.get("badge_font", "agency"), "center", "center",
            spacing=1.6, maxw=960)
    cv.rect(512, 640, 1024, 64, a.get("strip_bg", bg))
    cv.text(a.get("strip", maker + "  " + a["line"]), 1024, 672, 30, a.get("strip_fg", dim), "agency", "center",
            "center", spacing=2.0, maxw=980)
    # PCB back (512 x 512)
    px0, py0 = 0, 512
    cv.rect(px0, py0, 512, 512, "#101315")
    rng = random.Random(3)
    tr = []
    for k in range(70):
        x = px0 + rng.uniform(10, 500)
        y = py0 + rng.uniform(10, 500)
        tr.append((x, y, rng.uniform(30, 160), 2.2) if rng.random() < 0.5 else (x, y, 2.2, rng.uniform(30, 160)))
    cv.rects([(x, y, min(w, px0 + 510 - x), min(h, py0 + 510 - y)) for (x, y, w, h) in tr], "#1b2125")
    cv.rects([(px0 + rng.uniform(8, 504), py0 + rng.uniform(8, 504), 5, 5) for _ in range(160)], "#3a3f42")
    cv.frame_rect(px0 + 116, py0 + 116, 280, 280, 3, "#d9d9d6")
    cv.text("U1", px0 + 128, py0 + 136, 16, "#d9d9d6", "arialb", "left", "center")
    cv.render(pid)
    return at


# ====================================================================== geometry helpers (all take (m, n))

def mirror(pts, fz):
    return [(x, 2 * fz - z) for (x, z) in reversed(pts)]


def ov(m, n, tag, pts, d=0.0014, y=None, bevel=0.0003, holes=()):
    """A raised piece on the fan-side face: from the face plate's outer surface yF outwards (-y) by d."""
    y = n.yF if y is None else y
    G.slab_xz(m, tag, pts, list(holes), y - d, d, bevel=bevel)


def ov_sw(m, n, cell, pts, d=0.0012, y=None, holes=()):
    """The same in a solid colour from this card's atlas (a swatch cell)."""
    y = n.yF if y is None else y
    m.add(n.TEX, pb.g_slab(pts, list(holes), d, y - d, uv_rect=n.at.uv(cell)), G.M_XZ)


def face_film(m, n, name, cx, cz, w, h, y, on, peel="-x"):
    """A clear film on a glossy or RGB panel of the fan-side face: its plane in (x, z) at y, +Z (forward) = -y."""
    m.anchor(name, (cx, y - 0.00015, cz), (w, h, 0.001), forward=(0, -1, 0), up=(0, 0, 1),
             meta=f"film=clear,on={on},peel={peel},tab={peel}")


def hub_films(m, n_fans, fan_d, fan_thk=0.013):
    """A_FILM_HUB_<n>: the film disc on every fan hub sticker, an anchor of the rotor (A_FILM_HUB_n@A_FAN_n), on the
    sticker (parts_fan: radius 0.164 x diameter, 0.31 mm behind the rotor's front face)."""
    fans = {a.name: a for a in m.anchors if a.name.startswith("A_FAN_")}
    for i in range(n_fans):
        a = fans[f"A_FAN_{i}"]
        p, f, u = pb.unity_pose(a)
        d = 2 * 0.164 * fan_d
        pos = p + f * (fan_thk / 2 - 0.0002 + 0.00015)
        m.anchor(f"A_FILM_HUB_{i}", tuple(pos), (d, d, 0.001), forward=tuple(f), up=tuple(u), parent=a,
                 meta="film=clear,shape=disc,on=hub_sticker,peel=+y,tab=+y")


def ring_holes(n, grow=0.0040):
    """Holes round the fan rings, kept 1 mm apart (overlapping holes break the tessellation)."""
    if len(n.fxs) > 1:
        grow = min(grow, (n.fxs[1] - n.fxs[0] - 0.001) / 2 - n.r_hole)
    return [pb.circle2(x, n.fz, n.r_hole + grow, 96) for x in n.fxs]


def face_frame(m, n, tag, inset, d=0.0016, grow=0.0040, chamfer=0.004, bevel=0.0003, sw=None):
    """An overlay covering the whole face (minus inset), holed round every fan ring."""
    xa, xb, H = n.xa, n.xb, n.H
    out = pb.chamfer2((xa + xb - 0.0012) / 2, (0.002 + H) / 2, (xb - 0.0012) - xa - 2 * inset, H - 0.002 - 2 * inset,
                      chamfer)
    if sw:
        ov_sw(m, n, sw, out, d, holes=ring_holes(n, grow))
    else:
        ov(m, n, tag, out, d, holes=ring_holes(n, grow), bevel=bevel)


def strip_xz(m, n, tag, p0, p1, w, d=0.0004, y=None, sw=None):
    """A straight strip of width w on the face, from p0 to p1 (x, z)."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dz)
    nx, nz = -dz / ln * w / 2, dx / ln * w / 2
    pts = [(p0[0] + nx, p0[1] + nz), (p1[0] + nx, p1[1] + nz), (p1[0] - nx, p1[1] - nz), (p0[0] - nx, p0[1] - nz)]
    if sw:
        ov_sw(m, n, sw, pts, d, y=y)
    else:
        ov(m, n, tag, pts, d, y=y, bevel=0.0)


def corner_tri(n, x_end, sx, sz, a, b, inset=0.004):
    """A triangle in a face corner: x_end = xa or xb, sx = +1 at xa (pointing in), sz = +1 bottom, -1 top."""
    z0 = 0.002 + inset if sz > 0 else n.H - inset
    x0 = x_end + sx * inset
    return [(x0, z0), (x0 + sx * a, z0), (x0, z0 + sz * b)]


def flow_fins(m, n, x0, x1, tag="alu", z0=0.010, z1=None, pitch=0.0020):
    """Fins behind a backplate flow-through window: the stack's fins grown from y -0.0062 to the backplate."""
    z1 = n.H - 0.010 if z1 is None else z1
    x = x1
    while x > x0:
        G.slab_yz(m, tag, pb.rect2((-0.0062 + G.BP_Y0) / 2 - 0.0002, (z0 + z1) / 2, G.BP_Y0 - (-0.0062) - 0.0004,
                                   z1 - z0), [], x - 0.0002, 0.0004)
        x -= pitch


def bracket_extension(m, n, tag):
    """Cards thicker than 2.5 slots: the bracket plate grows over the third (and fourth) slot, vented (looks only;
    the screws and A_HIT_1 stay on the two-slot tab)."""
    y_end = n.yF + 0.0025
    if y_end > G.BR_YB - 0.004:
        return
    holes = G.hex_grid(y_end + 0.003, 0.006, G.BR_YB - 0.002, 0.100, 0.0024, 0.0011)
    G.slab_yz(m, tag, [(y_end, -0.0035), (G.BR_YB + 0.0002, -0.0035), (G.BR_YB + 0.0002, G.Z_TAB - 0.0006),
                       (y_end, G.Z_TAB - 0.0006)], holes, G.BR_X0, G.BR_X1 - G.BR_X0)


def riser(m, n):
    """Low-profile card: a port riser on the PCB, so the bracket's upper ports sit on board."""
    G.box(m, "pcb_black", (0.0830, G.PCB_Y0, n.Hp - 0.004), (G.BR_X0 - 0.0004, G.PCB_Y1, 0.0840))


def end_grille(m, n, tag, depth):
    """A hex-perforated end cap at the far end (passive cards: the intake)."""
    yF = n.yF
    holes = G.hex_grid(yF + 0.003, 0.008, yF + depth - 0.003, n.H - 0.008, 0.0028, 0.0010)
    G.slab_yz(m, tag, pb.chamfer2(yF + depth / 2, (0.002 + n.H) / 2, depth, n.H - 0.002, 0.002), holes, n.xa, 0.0016)


def bottom_print(m, n, dy=0.008):
    m.add(n.TEX, pb.g_quad(0.08, 0.010, n.at.uv("plate")), pb.label_frame((0, 0, -1), (0, 1, 0)),
          ((n.xa + n.xb) / 2 + 0.02, n.yF + dy, 0.0020 - 0.00005))


# ====================================================================== styles
# Each returns the hook dict for the spec: overlay, skirts, logo, trim, backplate.

def logo_at(lw, lh, x_frac, y_off, rgb=None):
    def f(m, n):
        lx = n.xa + (n.xb - n.xa) * x_frac
        rgb_x = None if rgb is None else (n.xa + rgb[0], n.xb - rgb[1])
        return lw, lh, lx, n.yF + y_off, rgb_x, n.yF + (rgb[2] if rgb else 0.0018)
    return f


def window_backplate(frac_holes="slots"):
    """Flow-through window past the PCB end: 'slots' (angled slats), 'hex' or 'none'."""
    def f(m, n):
        x0w, x1w = n.xa + 0.010, n.pcb_end - 0.006
        if frac_holes == "none" or x1w - x0w < 0.02:
            return []
        if frac_holes == "hex":
            return G.hex_grid(x0w, 0.014, x1w, n.H - 0.014, 0.0034, 0.0012)
        if frac_holes == "open":
            return [pb.rrect2((x0w + x1w) / 2, n.H / 2, x1w - x0w, n.H - 0.026, 0.006, 4)]
        k = max(4, int((x1w - x0w) / 0.010))
        pitch = (x1w - x0w) / k
        out = []
        for i in range(k):
            xl = x0w + i * pitch
            out.append([(xl, 0.016), (xl + pitch * 0.6, 0.016), (xl + pitch * 0.6 + 0.008, n.H - 0.016),
                        (xl + 0.008, n.H - 0.016)])
        return out
    return f


def common_trim(extra=None, fins=True, ext_tag=None):
    def f(m, n):
        s = n.s
        if fins and s.get("flow", True) and n.pcb_end - 0.008 > n.xa + 0.024:
            flow_fins(m, n, n.xa + 0.016, n.pcb_end - 0.004)
        bracket_extension(m, n, ext_tag or s["bracket_tag"])
        if extra:
            extra(m, n)
    return f


# ---------------------------------------------------------------- Zenith (Zotac / Sapphire look)

def zenith_duo():
    """Verdia 5060 Zenith Duo: compact, black, grey angular end panels, silver slashes between the fans."""
    def overlay(m, n):
        xa, xb, H, fz = n.xa, n.xb, n.H, n.fz
        for (xe, sx) in ((xa, 1), (xb - 0.0012, -1)):
            for sz in (1, -1):
                ov(m, n, "steel_dark", corner_tri(n, xe, sx, sz, 0.030, 0.034), 0.0016)
        xm = (n.fxs[0] + n.fxs[1]) / 2
        for sz in (1, -1):
            zc = fz + sz * (H / 2 - 0.016)
            for k in (-1, 1):
                strip_xz(m, n, "alu", (xm + k * 0.003 - 0.004, zc - sz * 0.010), (xm + k * 0.003 + 0.004, zc + sz * 0.010),
                         0.0016, 0.0006)
        # grey line along the bottom edge with a kink at the bracket end
        strip_xz(m, n, "steel_dark", (xa + 0.036, 0.0072), (xb - 0.030, 0.0072), 0.0012, 0.0005)
        strip_xz(m, n, "steel_dark", (xb - 0.030, 0.0072), (xb - 0.018, 0.0142), 0.0012, 0.0005)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.018), (xb - 0.022, yF + 0.018),
               (xb - 0.028, yF + 0.012), (xa + 0.040, yF + 0.012), (xa + 0.028, yF + 0.022), (xa + 0.002, yF + 0.022)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.012), (xa + 0.004, yF + 0.012)]
        return top, bot, 0.022

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.072, 0.0095, 0.56, 0.0062),
                trim=common_trim(lambda m, n: bottom_print(m, n, 0.0062)), backplate=window_backplate("slots"))


def zenith_core():
    """Voltra 7600 Zenith Core: plain black, a raised dark band between the fans, no RGB."""
    def overlay(m, n):
        xa, xb, H, fz = n.xa, n.xb, n.H, n.fz
        xm = (n.fxs[0] + n.fxs[1]) / 2
        for sz in (1, -1):
            band = [(xm - 0.024, fz + sz * (H / 2 - 0.004)), (xm + 0.024, fz + sz * (H / 2 - 0.004)),
                    (xm + 0.010, fz + sz * (H / 2 - 0.022)), (xm - 0.010, fz + sz * (H / 2 - 0.022))]
            ov(m, n, "dark_plastic", band, 0.0016)
            pb.screw_ph(m.mb("steel_dark"), (xm, n.yF - 0.0016, fz + sz * (H / 2 - 0.012)), (0, -1, 0), (1, 0, 0),
                        r=0.0016, h=0.0007)
        # a dark grey rim along both long edges with stepped ends
        for sz in (1, -1):
            z0 = 0.002 + 0.003 if sz > 0 else H - 0.003
            rim = [(xa + 0.010, z0), (xb - 0.012, z0), (xb - 0.016, z0 + sz * 0.003), (xa + 0.014, z0 + sz * 0.003)]
            ov(m, n, "dark_plastic", rim, 0.0010)
        for (xe, sx) in ((xa, 1), (xb - 0.0012, -1)):
            for sz in (1, -1):
                ov(m, n, "dark_plastic", corner_tri(n, xe, sx, sz, 0.022, 0.026, 0.006), 0.0012)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.020), (xa + 0.060, yF + 0.020),
               (xa + 0.050, yF + 0.014), (xa + 0.002, yF + 0.014)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.014), (xa + 0.004, yF + 0.014)]
        return top, bot, 0.020

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.074, 0.0095, 0.60, 0.0070),
                trim=common_trim(lambda m, n: bottom_print(m, n, 0.0070)), backplate=window_backplate("hex"))


def zenith_white():
    """Voltra 9060 XT Zenith Frost: white shroud, light grey angular inlays, silver lines, white fans."""
    def overlay(m, n):
        xa, xb, H, fz = n.xa, n.xb, n.H, n.fz
        xm = (n.fxs[0] + n.fxs[1]) / 2
        for sz in (1, -1):
            zz = fz + sz * (H / 2)
            ins = [(xm - 0.030, zz - sz * 0.004), (xm + 0.030, zz - sz * 0.004), (xm + 0.012, zz - sz * 0.026),
                   (xm - 0.012, zz - sz * 0.026)]
            ov(m, n, "grey_plastic", ins, 0.0014)
            strip_xz(m, n, "alu", (xm - 0.036, zz - sz * 0.0035), (xm - 0.016, zz - sz * 0.0285), 0.0010, 0.0004)
            strip_xz(m, n, "alu", (xm + 0.036, zz - sz * 0.0035), (xm + 0.016, zz - sz * 0.0285), 0.0010, 0.0004)
        for (xe, sx) in ((xa, 1), (xb - 0.0012, -1)):
            for sz in (1, -1):
                ov(m, n, "grey_plastic", corner_tri(n, xe, sx, sz, 0.026, 0.030), 0.0014)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.020), (xb - 0.024, yF + 0.020),
               (xb - 0.030, yF + 0.013), (xa + 0.030, yF + 0.013), (xa + 0.020, yF + 0.022), (xa + 0.002, yF + 0.022)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.013), (xa + 0.004, yF + 0.013)]
        return top, bot, 0.022

    def extra(m, n):
        bottom_print(m, n, 0.0065)
        G.box(m, "grey_plastic", (n.xa + 0.032, n.yF + 0.0135, n.H - 0.0001), (n.xb - 0.032, n.yF + 0.0145, n.H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.074, 0.0095, 0.55, 0.0068),
                trim=common_trim(extra), backplate=window_backplate("slots"))


def zenith_flare():
    """Voltra 9070 XT Zenith Flare (top line): gunmetal metal shroud, a diagonal ARGB light bar through the middle,
    silver fan rings, a long ARGB bar on the top edge, 3 slots."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        face_frame(m, n, "black_plastic", 0.0035, 0.0012, grow=0.0042)
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.004)
                # an RGB blade between the rings, a silver chevron beside it
                blade = [(xm - 0.005, zz), (xm + 0.005, zz), (xm + 0.0015, zz - sz * 0.030), (xm - 0.0015, zz - sz * 0.030)]
                ov(m, n, "rgb", blade, 0.0016, y=n.yF - 0.0012, bevel=0.0)
                strip_xz(m, n, "alu", (xm - 0.012, zz), (xm - 0.004, zz - sz * 0.024), 0.0014, 0.0006, y=n.yF - 0.0012)
                strip_xz(m, n, "alu", (xm + 0.012, zz), (xm + 0.004, zz - sz * 0.024), 0.0014, 0.0006, y=n.yF - 0.0012)
        # the far end: a slanted ARGB light bar, a gunmetal end block
        x0 = xa + 0.006
        bar = [(x0, 0.010), (x0 + 0.006, 0.010), (x0 + 0.018, H - 0.010), (x0 + 0.012, H - 0.010)]
        ov(m, n, "rgb", bar, 0.0020, y=n.yF - 0.0012, bevel=0.0)
        face_film(m, n, "A_FILM_RGB_0", x0 + 0.009, H / 2, 0.018, H - 0.020, n.yF - 0.0032, "rgb_bar", "+x")

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.034), (xb - 0.020, yF + 0.034),
               (xb - 0.030, yF + 0.026), (xa + 0.120, yF + 0.026), (xa + 0.105, yF + 0.036), (xa + 0.050, yF + 0.036),
               (xa + 0.036, yF + 0.026), (xa + 0.020, yF + 0.026), (xa + 0.010, yF + 0.040), (xa + 0.002, yF + 0.040)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.024), (xa + 0.040, yF + 0.024),
               (xa + 0.022, yF + 0.034), (xa + 0.004, yF + 0.034)]
        return top, bot, 0.040

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.012)
        # a second ARGB bar along the top edge step, silver lines
        G.box(m, "rgb", (xa + 0.122, yF + 0.0275, H - 0.0003), (xb - 0.032, yF + 0.0295, H + 0.0004))
        G.box(m, "alu", (xa + 0.052, yF + 0.0330, H - 0.0001), (xa + 0.103, yF + 0.0342, H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.100, 0.0120, 0.52, 0.0100, rgb=(0.024, 0.032, 0.0020)),
                trim=common_trim(extra), backplate=window_backplate("hex"))


# ---------------------------------------------------------------- Aegis (ASUS look)

def aegis_white():
    """Verdia 5060 Ti Aegis Halo White: white shroud, a grey slash band across each fan pair, silver edge lines,
    a small ARGB strip by the logo."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        xm = (fxs[0] + fxs[1]) / 2
        # the slashed grey band through the middle (the ASUS-style "dual" divider)
        for sz in (1, -1):
            zz = fz + sz * (H / 2 - 0.004)
            band = [(xm - 0.020, zz), (xm - 0.006, zz), (xm + 0.010, zz - sz * 0.024), (xm - 0.004, zz - sz * 0.024)]
            ov(m, n, "grey_plastic", band, 0.0016)
            strip_xz(m, n, "alu", (xm - 0.0035, zz), (xm + 0.0125, zz - sz * 0.024), 0.0010, 0.0004, y=n.yF - 0.0016)
        # silver lines along both long edges, angled at the ends
        for sz in (1, -1):
            z0 = 0.002 + 0.0045 if sz > 0 else H - 0.0045
            strip_xz(m, n, "alu", (xa + 0.022, z0), (xm - 0.028, z0), 0.0009, 0.0005)
            strip_xz(m, n, "alu", (xm + 0.028, z0), (xb - 0.016, z0), 0.0009, 0.0005)
            strip_xz(m, n, "alu", (xa + 0.022, z0), (xa + 0.008, z0 + sz * 0.016), 0.0009, 0.0005)
        for (xe, sx) in ((xa, 1),):
            for sz in (1, -1):
                ov(m, n, "grey_plastic", corner_tri(n, xe, sx, sz, 0.016, 0.040, 0.0035), 0.0012)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.024), (xb - 0.022, yF + 0.024),
               (xb - 0.030, yF + 0.016), (xa + 0.020, yF + 0.016), (xa + 0.012, yF + 0.028), (xa + 0.002, yF + 0.028)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.016), (xa + 0.004, yF + 0.016)]
        return top, bot, 0.028

    def extra(m, n):
        bottom_print(m, n, 0.0075)
        G.box(m, "alu", (n.xa + 0.022, n.yF + 0.0165, n.H - 0.0001), (n.xb - 0.032, n.yF + 0.0175, n.H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.078, 0.0100, 0.55, 0.0080, rgb=(0.030, 0.034, 0.0020)),
                trim=common_trim(extra), backplate=window_backplate("open"))


def aegis_paladin():
    """Verdia 5080 Aegis Paladin (flagship): black, faceted dark metal panels, a big diagonal ARGB light bar across
    the far end and an ARGB prism along the top edge, 3.5 slots."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        face_frame(m, n, "alu_dark", 0.003, 0.0014, grow=0.0042, chamfer=0.010)
        # faceted wedges between the fans
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.005)
                wedge = [(xm - 0.016, zz), (xm + 0.016, zz), (xm + 0.004, zz - sz * 0.036), (xm - 0.004, zz - sz * 0.036)]
                ov(m, n, "black_plastic", wedge, 0.0016, y=n.yF - 0.0014)
                strip_xz(m, n, "alu", (xm - 0.017, zz), (xm - 0.005, zz - sz * 0.036), 0.0008, 0.0004, y=n.yF - 0.0030)
        # the big light bar: a wide slanted ARGB blade at the far end, with a dark frame
        x0 = xa + 0.008
        frame_pts = [(x0, 0.006), (x0 + 0.020, 0.006), (x0 + 0.046, H - 0.006), (x0 + 0.026, H - 0.006)]
        ov(m, n, "black_plastic", frame_pts, 0.0020, y=n.yF - 0.0014)
        bar = [(x0 + 0.006, 0.010), (x0 + 0.014, 0.010), (x0 + 0.039, H - 0.010), (x0 + 0.031, H - 0.010)]
        ov(m, n, "rgb", bar, 0.0010, y=n.yF - 0.0034, bevel=0.0)
        face_film(m, n, "A_FILM_RGB_0", x0 + 0.0225, H / 2, 0.033, H - 0.020, n.yF - 0.0044, "rgb_bar", "+x")
        # bracket end: a second short light slash
        bar2 = [(xb - 0.016, H * 0.62), (xb - 0.010, H * 0.62), (xb - 0.010, H - 0.012), (xb - 0.022, H - 0.012)]
        ov(m, n, "rgb", bar2, 0.0010, y=n.yF - 0.0014, bevel=0.0)
        face_film(m, n, "A_FILM_RGB_1", xb - 0.016, (H * 0.62 + H - 0.012) / 2, 0.012, H * 0.38 - 0.012, n.yF - 0.0024,
                  "rgb_slash", "-x")

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.040), (xb - 0.024, yF + 0.040),
               (xb - 0.036, yF + 0.030), (xa + 0.150, yF + 0.030), (xa + 0.130, yF + 0.044), (xa + 0.060, yF + 0.044),
               (xa + 0.046, yF + 0.030), (xa + 0.020, yF + 0.030), (xa + 0.008, yF + 0.050), (xa + 0.002, yF + 0.050)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.030), (xa + 0.050, yF + 0.030),
               (xa + 0.030, yF + 0.042), (xa + 0.004, yF + 0.042)]
        return top, bot, 0.050

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.014)
        # the ARGB prism on the top edge: a light bar along the step, and the far-end light block
        G.box(m, "rgb", (xa + 0.062, yF + 0.0405, H - 0.0003), (xa + 0.128, yF + 0.0430, H + 0.0012))
        G.box(m, "rgb", (xa + 0.004, yF + 0.002, H - 0.0003), (xa + 0.018, yF + 0.046, H + 0.0006))
        G.box(m, "alu", (xa + 0.152, yF + 0.0285, H - 0.0001), (xb - 0.038, yF + 0.0297, H + 0.0004))
        # the series badge on the backplate
        m.add(n.TEX, pb.g_quad(0.090, 0.0112, n.at.uv("badge")), pb.label_frame((0, 1, 0), (0, 0, -1)),
              (xa + 0.075, G.BP_Y1 + 0.00006, H * 0.30))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.108, 0.0130, 0.62, 0.0150, rgb=(0.152, 0.040, 0.0022)),
                trim=common_trim(extra), backplate=window_backplate("hex"))


# ---------------------------------------------------------------- Mako (MSI look)

def mako_gale():
    """Verdia 5070 Mako Gale 3X: black with silver claws between the fans, a silver line along the top edge, no RGB."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.0035)
                claw = [(xm - 0.017, zz), (xm + 0.017, zz), (xm + 0.003, zz - sz * 0.021), (xm - 0.003, zz - sz * 0.021)]
                ov(m, n, "black_plastic", claw, 0.0016)
                strip_xz(m, n, "alu", (xm - 0.0135, zz - sz * 0.001), (xm - 0.0025, zz - sz * 0.018), 0.0016, 0.0005,
                         y=n.yF - 0.0016)
                strip_xz(m, n, "alu", (xm + 0.0135, zz - sz * 0.001), (xm + 0.0025, zz - sz * 0.018), 0.0016, 0.0005,
                         y=n.yF - 0.0016)
        # silver end bars with a notch
        for (x0, d) in ((xa + 0.005, 1), (xb - 0.0055, -1)):
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.004)
                bar = [(x0, zz), (x0 + d * 0.004, zz), (x0 + d * 0.004, zz - sz * 0.026), (x0, zz - sz * 0.032)]
                ov(m, n, "alu", bar, 0.0012, bevel=0.0002)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.024), (xb - 0.020, yF + 0.024),
               (xb - 0.028, yF + 0.016), (xa + 0.080, yF + 0.016), (xa + 0.068, yF + 0.026), (xa + 0.002, yF + 0.026)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.016), (xa + 0.004, yF + 0.016)]
        return top, bot, 0.026

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.0080)
        G.box(m, "alu", (xa + 0.006, yF + 0.0040, H - 0.0001), (xb - 0.010, yF + 0.0055, H + 0.0004))
        G.box(m, "alu", (xa + 0.006, yF + 0.0225, H - 0.0001), (xa + 0.066, yF + 0.0237, H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.086, 0.0100, 0.58, 0.0100),
                trim=common_trim(extra), backplate=window_backplate("slots"))


def mako_leviathan():
    """Verdia 5090 Mako Leviathan (top line): a brushed silver frame round a black face, ARGB lines along the frame,
    an ARGB band on the top edge, a 4-slot body with deep skirts."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        face_frame(m, n, "alu", 0.0015, 0.0012, grow=0.0050, chamfer=0.008)
        face_frame(m, n, "black_plastic", 0.0120, 0.0020, grow=0.0042, chamfer=0.006)
        for sz in (1, -1):
            z0 = 0.002 + 0.0085 if sz > 0 else H - 0.0085
            strip_xz(m, n, "rgb", (xa + 0.030, z0), (xb - 0.030, z0), 0.0014, 0.0005, y=n.yF - 0.0018)
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.008)
                v = [(xm - 0.012, zz), (xm + 0.012, zz), (xm, zz - sz * 0.016)]
                ov(m, n, "alu", v, 0.0010, y=n.yF - 0.0028, bevel=0.0002)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.050), (xb - 0.020, yF + 0.050),
               (xb - 0.030, yF + 0.040), (xa + 0.030, yF + 0.040), (xa + 0.018, yF + 0.056), (xa + 0.002, yF + 0.056)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.040), (xa + 0.004, yF + 0.040)]
        return top, bot, 0.056

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.018)
        G.box(m, "alu", (xa + 0.004, yF + 0.0005, H - 0.0001), (xb - 0.004, yF + 0.0040, H + 0.0006))
        G.box(m, "rgb", (xa + 0.032, yF + 0.0405, H - 0.0003), (xb - 0.032, yF + 0.0430, H + 0.0006))
        m.add(n.TEX, pb.g_quad(0.090, 0.0112, n.at.uv("badge")), pb.label_frame((0, 1, 0), (0, 0, -1)),
              (xa + 0.070, G.BP_Y1 + 0.00006, H * 0.30))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.110, 0.0130, 0.60, 0.0200, rgb=None),
                trim=common_trim(extra), backplate=window_backplate("hex"))


# ---------------------------------------------------------------- Kestrel (Gigabyte look)

def kestrel_ice():
    """Verdia 5070 Ti Kestrel Talon Ice: white shroud, silver wedge corners, grey X-cuts between the fans, an ARGB
    logo strip on the top edge."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.0035)
                x_cut = [(xm - 0.014, zz), (xm - 0.008, zz), (xm + 0.002, zz - sz * 0.024), (xm - 0.004, zz - sz * 0.024)]
                ov(m, n, "grey_plastic", x_cut, 0.0014)
                x_cut2 = [(xm + 0.008, zz), (xm + 0.014, zz), (xm + 0.004, zz - sz * 0.024), (xm - 0.002, zz - sz * 0.024)]
                ov(m, n, "alu", x_cut2, 0.0010)
        for (xe, sx) in ((xa, 1), (xb - 0.0012, -1)):
            for sz in (1, -1):
                ov(m, n, "alu", corner_tri(n, xe, sx, sz, 0.020, 0.028, 0.0035), 0.0012)
                ov(m, n, "grey_plastic", corner_tri(n, xe, sx, sz, 0.034, 0.012, 0.0035), 0.0008)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.022), (xb - 0.024, yF + 0.022),
               (xb - 0.034, yF + 0.015), (xa + 0.110, yF + 0.015), (xa + 0.095, yF + 0.025), (xa + 0.050, yF + 0.025),
               (xa + 0.035, yF + 0.015), (xa + 0.020, yF + 0.015), (xa + 0.010, yF + 0.028), (xa + 0.002, yF + 0.028)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.015), (xa + 0.030, yF + 0.015),
               (xa + 0.018, yF + 0.023), (xa + 0.004, yF + 0.023)]
        return top, bot, 0.028

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.0075)
        G.box(m, "grey_plastic", (xa + 0.052, yF + 0.0215, H - 0.0001), (xa + 0.093, yF + 0.0227, H + 0.0004))
        G.box(m, "alu", (xa + 0.112, yF + 0.0138, H - 0.0001), (xb - 0.036, yF + 0.0148, H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.086, 0.0105, 0.62, 0.0078, rgb=(0.112, 0.036, 0.0020)),
                trim=common_trim(extra), backplate=window_backplate("slots"))


def kestrel_lp():
    """Verdia 4060 Kestrel Low Profile: a half-height black card with two small fans and silver slashes."""
    def overlay(m, n):
        xa, xb, H, fz = n.xa, n.xb, n.H, n.fz
        xm = (n.fxs[0] + n.fxs[1]) / 2
        for sz in (1, -1):
            zz = fz + sz * (H / 2 - 0.003)
            ov(m, n, "black_plastic", [(xm - 0.010, zz), (xm + 0.010, zz), (xm + 0.002, zz - sz * 0.012),
                                       (xm - 0.002, zz - sz * 0.012)], 0.0012)
        for (xe, sx) in ((xa, 1), (xb - 0.0012, -1)):
            for sz in (1, -1):
                ov(m, n, "alu", corner_tri(n, xe, sx, sz, 0.010, 0.014, 0.003), 0.0008)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.018), (xa + 0.002, yF + 0.018)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.012), (xa + 0.004, yF + 0.012)]
        return top, bot, 0.018

    def extra(m, n):
        riser(m, n)

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.060, 0.0075, 0.50, 0.0080),
                trim=common_trim(extra, fins=False), backplate=window_backplate("none"))


# ---------------------------------------------------------------- reference designs

def verdia_ref():
    """Verdia VTX 5090 reference: a 2-slot double flow-through card, a silver aluminium frame round dark fin faces,
    the lit VTX logo on the top edge."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        # the dark face is inset in the silver frame: an alu_dark plate holed for the fans, a silver spine between
        face_frame(m, n, "alu_dark", 0.0060, 0.0006, grow=0.0040, chamfer=0.002, bevel=0.0001)
        xm = (fxs[0] + fxs[1]) / 2
        ov(m, n, "alu", pb.rrect2(xm, fz, 0.016, H - 0.012, 0.002, 3), 0.0012, bevel=0.0003)
        for sz in (1, -1):  # the X-shaped shoulders of the frame by the spine
            zz = fz + sz * (H / 2 - 0.006)
            ov(m, n, "alu", [(xm - 0.030, zz), (xm + 0.030, zz), (xm + 0.008, zz - sz * 0.030),
                             (xm - 0.008, zz - sz * 0.030)], 0.0012, bevel=0.0003)
        # the fin field visible round the fans: dark slats
        for x in fxs:
            for k in range(-9, 10):
                xx = x + k * 0.0055
                h = H / 2 - 0.010
                if abs(k) * 0.0055 < n.r_hole + 0.004:
                    continue
                ov(m, n, "black_plastic", pb.rect2(xx, fz, 0.0012, 2 * h), 0.0003, bevel=0.0)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.030), (xa + 0.002, yF + 0.030)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.030), (xa + 0.004, yF + 0.030)]
        return top, bot, 0.030

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        # the lit logo: a white light line in front of the plate
        G.box(m, "led_white", (xa + 0.030, yF + 0.0045, H - 0.0002), (xa + 0.040, yF + 0.0255, H + 0.0004))
        for z in (0.0012, H - 0.0012):
            G.box(m, "alu", (xa + 0.001, yF + 0.0004, z - 0.0008), (xb - 0.0015, yF + 0.0016, z + 0.0008))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.090, 0.0110, 0.55, 0.0150),
                trim=common_trim(extra), backplate=window_backplate("open"))


def voltra_ref():
    """Voltra RX 7900 XTX reference: a dark gunmetal shroud, silver chamfered edges, the three red stripes, silver
    fan rings."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        for sz in (1, -1):
            z0 = 0.002 + 0.0022 if sz > 0 else H - 0.0022
            strip_xz(m, n, "alu", (xa + 0.006, z0), (xb - 0.006, z0), 0.0018, 0.0010)
        for i in range(len(fxs) - 1):
            xm = (fxs[i] + fxs[i + 1]) / 2
            for sz in (1, -1):
                zz = fz + sz * (H / 2 - 0.004)
                ov(m, n, "black_plastic", [(xm - 0.014, zz), (xm + 0.014, zz), (xm + 0.003, zz - sz * 0.022),
                                           (xm - 0.003, zz - sz * 0.022)], 0.0014)
        # three red stripes in the far end corner
        for k in range(3):
            xr = xa + 0.008 + k * 0.0045
            strip_xz(m, n, None, (xr, H - 0.006), (xr + 0.010, H - 0.030), 0.0022, 0.0010, sw="red")

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.026), (xb - 0.018, yF + 0.026),
               (xb - 0.026, yF + 0.018), (xa + 0.060, yF + 0.018), (xa + 0.050, yF + 0.028), (xa + 0.002, yF + 0.028)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.018), (xa + 0.004, yF + 0.018)]
        return top, bot, 0.028

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.009)
        for k in range(3):  # the stripes on the top edge, by the far end
            m.add(n.TEX, pb.solid(pb.g_box((0.003, 0.016, 0.0005)), n.at.uv("red")), None,
                  (xa + 0.012 + k * 0.006, yF + 0.0105, H + 0.0001))
        G.box(m, "alu", (xa + 0.062, yF + 0.0170, H - 0.0001), (xb - 0.028, yF + 0.0180, H + 0.0004))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.084, 0.0100, 0.56, 0.0090, rgb=(0.064, 0.030, 0.0020)),
                trim=common_trim(extra), backplate=window_backplate("none"))


def tiron_ref():
    """Tiron Lumen B580 reference: matte black, a silver frame band along both long edges, two big fans, no RGB."""
    def overlay(m, n):
        xa, xb, H, fz, fxs = n.xa, n.xb, n.H, n.fz, n.fxs
        face_frame(m, n, "alu", 0.0010, 0.0012, grow=0.0040, chamfer=0.003)
        face_frame(m, n, "paint_black", 0.0085, 0.0018, grow=0.0036, chamfer=0.008)
        xm = (fxs[0] + fxs[1]) / 2
        ov(m, n, "paint_black", pb.rrect2(xm, fz, 0.010, H - 0.020, 0.003, 3), 0.0010)

    def skirts(m, n):
        xa, xb, yF = n.xa, n.xb, n.yF
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.028), (xa + 0.002, yF + 0.028)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.028), (xa + 0.004, yF + 0.028)]
        return top, bot, 0.028

    def extra(m, n):
        xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
        bottom_print(m, n, 0.014)
        for z in (0.0012, H - 0.0012):  # the silver frame continues round the edges
            G.box(m, "alu", (xa + 0.002, yF + 0.0002, z - 0.0009), (xb - 0.0015, yF + 0.0060, z + 0.0009))

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.080, 0.0100, 0.55, 0.0150),
                trim=common_trim(extra), backplate=window_backplate("open"))


# ---------------------------------------------------------------- data-centre (passive)

def dc_passive(face_cell, end_tag, accent_cell=None):
    """A passive dual-slot accelerator: a closed shroud (a colour panel over the face), a hex intake grille at the
    far end, the whole bracket vented (the exhaust), a power port at the far end of the top edge."""
    def overlay(m, n):
        xa, xb, H = n.xa, n.xb, n.H
        panel = pb.chamfer2((xa + 0.030 + xb - 0.010) / 2, (0.002 + H) / 2, (xb - 0.010) - (xa + 0.030), H - 0.010,
                            (0.010, 0.0, 0.0, 0.010))
        ov_sw(m, n, face_cell, panel, 0.0012)
        face_film(m, n, "A_FILM_FACE_0", (xa + 0.030 + xb - 0.010) / 2, (0.002 + H) / 2, (xb - 0.010) - (xa + 0.030),
                  H - 0.010, n.yF - 0.0012, "shroud_panel", "-x")
        # a black band at the bracket end, ribs on the panel
        ov(m, n, "paint_black", pb.rect2(xb - 0.0060, (0.002 + H) / 2, 0.0090, H - 0.010), 0.0012)
        for k in range(5):
            z = 0.018 + k * (H - 0.036) / 4
            ov(m, n, end_tag, pb.rect2(xa + 0.018, z, 0.020, 0.0016), 0.0006, y=n.yF, bevel=0.0)
        if accent_cell:
            strip_xz(m, n, None, (xa + 0.032, 0.010), (xb - 0.012, 0.010), 0.0016, 0.0004, y=n.yF - 0.0012,
                     sw=accent_cell)
        m.add(n.TEX, pb.g_quad(0.110, 0.0137, n.at.uv("badge")), pb.label_frame((0, -1, 0), (0, 0, 1)),
              ((xa + xb) / 2 + 0.010, n.yF - 0.00125, H * 0.5))

    def skirts(m, n):
        xa, xb, yF, T = n.xa, n.xb, n.yF, n.T
        pxs = n.pxs
        d = T - 0.0075  # closed to the backplate side, short of the power socket
        top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + d)]
        x0, x1 = min(pxs) - 0.014, max(pxs) + 0.014
        top += [(x1, yF + d), (x1, -0.0140), (x0, -0.0140), (x0, yF + d), (xa + 0.002, yF + d)]
        bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + d), (xa + 0.004, yF + d)]
        return top, bot, 0.0015

    def extra(m, n):
        end_grille(m, n, end_tag, n.T - 0.0045)
        bottom_print(m, n, 0.012)

    return dict(overlay=overlay, skirts=skirts, logo=logo_at(0.090, 0.0110, 0.55, 0.0120),
                trim=common_trim(extra, fins=False), backplate=window_backplate("none"))


# ====================================================================== the catalogue

def card(L, H, T, fans, fan_d, power, px, pcb_end, style, art, **kw):
    s = dict(L=L, H=H, T=T, Hp=kw.pop("Hp", min(H - 0.007, 0.124)), fans=fans, fan_d=fan_d, blades=kw.pop("blades", 11),
             tip_ring=kw.pop("tip_ring", False), power=power, px=px, pcb_end=pcb_end, pipes=kw.pop("pipes", 5),
             pipe_tag=kw.pop("pipe_tag", "nickel"), xd=0.021, zd=kw.pop("zd", None), vent=kw.pop("vent", "slots"),
             core=kw.pop("core", "screws"), texture=cat_texture, art=art, model=art["line"], brand=art.get("partner")
             or art["chip"])
    s["zd"] = s["zd"] or round(s["Hp"] * 0.52, 4)
    s.update(kw)
    s.update(style)
    return s


def art(chip, line, series, pn, sn, accent, partner=None, light=False, **kw):
    a = dict(chip=chip, line=line, series=series, pn=pn, sn=sn, accent=accent, partner=partner)
    if light:  # a white card: a white plate with dark print
        a.update(plate_bg="#ecedea", plate_fg="#1a1b1e", plate_dim="#8c8f96", hub=("#e8e9e6", "#1c1d20", "#a9acb2"))
    else:
        a.update(plate_bg="#0a0a0b", plate_fg="#f0f0f2", plate_dim="#55565c", hub=("#0b0b0c", "#e9e9ec", "#6d6f76"))
    a.update(kw)
    return a


WHITE_FAN = dict(blade_tag="white_plastic", hub_tag="white_plastic")

CARDS = {}

# 1. Verdia VTX 5060 8 GB, Zenith Duo (Zotac Twin Edge): 220 x 116 x 42 mm, 2 slots, 2 fans, 1 x 8-pin
CARDS["gpu_verdia_5060_zenith"] = card(
    0.220, 0.116, 0.042, 2, 0.086, "pcie8", -0.080, -0.104, zenith_duo(),
    art("VERDIA", "VTX 5060", "DUO", "ZN-V5060-8GD7-D", "S/N 2511Z50600731", "#9aa0a8", partner="ZENITH",
        em_col="#e8e9ec", em2="#8c9097"),
    mem="8GB GDDR7", pipes=4, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black", face_tag="black_plastic",
    over_tag="black_plastic", ring_tag="black_plastic", logo_tag="paint_white", vent="slots", blades=9, fan_rpm=2400)

# 2. Verdia VTX 5060 Ti 16 GB, Aegis Halo White (ASUS Dual White): 230 x 123 x 50 mm, 2.5 slots, 2 fans, 1 x 8-pin
CARDS["gpu_verdia_5060ti_aegis_white"] = card(
    0.230, 0.123, 0.050, 2, 0.090, "pcie8", -0.072, -0.098, aegis_white(),
    art("VERDIA", "VTX 5060 Ti", "HALO", "AG-V5060TI-16G-W", "S/N 2512A5060T0412", "#8c8f96", partner="AEGIS",
        light=True, em_col="#1a1b1e", em2="#ecedea", hub_em="#1c1d20", hub_em2="#e8e9e6"),
    mem="16GB GDDR7", pipes=4, pipe_tag="nickel", bracket_tag="steel", back_tag="paint_white", face_tag="white_plastic",
    over_tag="grey_plastic", ring_tag="white_plastic", logo_tag="grey_plastic", vent="hex", fan_kw=WHITE_FAN,
    swatch="#c9ccd1")

# 3. Verdia VTX 5070 12 GB, Mako Gale 3X (MSI Ventus 3X): 288 x 115 x 50 mm, 2.5 slots, 3 fans, 1 x 8-pin
CARDS["gpu_verdia_5070_mako"] = card(
    0.288, 0.115, 0.050, 3, 0.080, "pcie8", -0.090, -0.122, mako_gale(),
    art("VERDIA", "VTX 5070", "GALE 3X", "MK-V5070-12G-G3X", "S/N 2601M50700219", "#c8cbd0", partner="MAKO",
        em_col="#d6d8dc", em2="#0a0a0b"),
    mem="12GB GDDR7", pipes=5, pipe_tag="nickel", bracket_tag="steel", back_tag="alu", face_tag="black_plastic",
    over_tag="black_plastic", ring_tag="black_plastic", logo_tag="paint_black", vent="slots", blades=9)

# 4. Verdia VTX 5070 Ti 16 GB, Kestrel Talon Ice (Gigabyte Eagle Ice): 304 x 126 x 50 mm, 2.5 slots, 3 fans,
#    12V-2x6, ARGB
CARDS["gpu_verdia_5070ti_kestrel_white"] = card(
    0.304, 0.126, 0.050, 3, 0.084, "12v2x6", -0.092, -0.124, kestrel_ice(),
    art("VERDIA", "VTX 5070 Ti", "TALON ICE", "KS-V5070TI-16G-TI", "S/N 2601K5070T0864", "#7aa7d8", partner="KESTREL",
        light=True, em_col="#1a1b1e", em2="#7aa7d8", hub_em="#2a2c30", hub_em2="#7aa7d8"),
    mem="16GB GDDR7", pipes=5, pipe_tag="nickel", bracket_tag="steel", back_tag="paint_white", face_tag="white_plastic",
    over_tag="grey_plastic", ring_tag="white_plastic", logo_tag="grey_plastic", vent="hex", fan_kw=WHITE_FAN,
    swatch="#7aa7d8")

# 5. Verdia VTX 5080 16 GB, Aegis Paladin (ROG Astral): 348 x 149 x 70 mm, 3.5 slots, 3 fans, 12V-2x6, big ARGB bar
CARDS["gpu_verdia_5080_aegis"] = card(
    0.348, 0.149, 0.070, 3, 0.096, "12v2x6", -0.098, -0.134, aegis_paladin(),
    art("VERDIA", "VTX 5080", "PALADIN", "AG-V5080-16G-PAL", "S/N 2601A50800077", "#e0233a", partner="AEGIS",
        em_col="#e0233a", em2="#0a0a0b", hub_em="#e0233a", hub_em2="#0b0b0c", badge="PALADIN",
        badge_bg="#0a0a0b", badge_fg="#c9cad0"),
    mem="16GB GDDR7", pipes=6, pipe_tag="nickel", bracket_tag="paint_black", back_tag="alu_dark",
    face_tag="black_plastic", over_tag="black_plastic", ring_tag="alu_dark", logo_tag="alu", vent="hex",
    tip_ring=True, blades=11, fan_rpm=1800, bp_logo_x=-0.090)

# 6. Verdia VTX 5090 32 GB reference: 304 x 137 x 40 mm, 2 slots, 2 fans (double flow-through), 12V-2x6
CARDS["gpu_verdia_5090_ref"] = card(
    0.304, 0.137, 0.040, 2, 0.110, "12v2x6", -0.062, -0.090, verdia_ref(),
    art("VERDIA", "VTX 5090", "REFERENCE", "VD-5090-32G-REF", "S/N 2501V50900003", "#76b62a", partner=None,
        em_col="#76b62a", em2="#0a0a0b", hub=("#141518", "#c9cad0", "#3a3c42"), hub_em="#c9cad0", hub_em2="#141518",
        plate_bg="#16171a", plate_dim="#3a3c42"),
    mem="32GB GDDR7", pipes=4, pipe_tag="copper", bracket_tag="paint_black", back_tag="alu", face_tag="alu",
    over_tag="alu_dark", ring_tag="alu_dark", logo_tag="paint_black", vent="hex", blades=7, fan_rpm=1600,
    core="window", bp_logo_x=-0.040)

# 7. Verdia VTX 5090 32 GB, Mako Leviathan (MSI Suprim): 359 x 150 x 80 mm, 4 slots, 3 fans, 12V-2x6, ARGB
CARDS["gpu_verdia_5090_mako"] = card(
    0.359, 0.150, 0.080, 3, 0.100, "12v2x6", -0.104, -0.140, mako_leviathan(),
    art("VERDIA", "VTX 5090", "LEVIATHAN", "MK-V5090-32G-LVT", "S/N 2502M50900141", "#c8cbd0", partner="MAKO",
        em_col="#d6d8dc", em2="#0a0a0b", badge="LEVIATHAN", badge_bg="#c9cbd0", badge_fg="#16171a"),
    mem="32GB GDDR7", pipes=6, pipe_tag="nickel", bracket_tag="steel", back_tag="alu", face_tag="black_plastic",
    over_tag="black_plastic", ring_tag="alu", logo_tag="paint_black", vent="hex", tip_ring=True, blades=11,
    fan_rpm=1700, bp_logo_x=-0.095)

# 8. Verdia VTX 4060 8 GB, Kestrel Low Profile: 182 x 69 x 40 mm, 2 slots, 2 small fans, 1 x 8-pin
CARDS["gpu_verdia_4060_kestrel_lp"] = card(
    0.182, 0.069, 0.040, 2, 0.056, "pcie8", -0.052, -0.080, kestrel_lp(),
    art("VERDIA", "VTX 4060", "LOW PROFILE", "KS-V4060-8G-LP", "S/N 2405K40600392", "#ff7a1a", partner="KESTREL",
        em_col="#ff7a1a", em2="#e9e9ec"),
    Hp=0.064, zd=0.034, mem="8GB GDDR6", pipes=4, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black",
    face_tag="black_plastic", over_tag="black_plastic", ring_tag="black_plastic", logo_tag="paint_white",
    vent="slots", blades=9, fan_rpm=3200, bp_logo_x=-0.020)

# 9. Voltra RX 7600 8 GB, Zenith Core (Sapphire Pulse): 240 x 120 x 43 mm, 2 slots, 2 fans, 1 x 8-pin, no RGB
CARDS["gpu_voltra_7600_zenith"] = card(
    0.240, 0.120, 0.043, 2, 0.092, "pcie8", -0.088, -0.114, zenith_core(),
    art("VOLTRA", "RX 7600", "CORE", "ZN-R7600-8GD6-C", "S/N 2306Z76000588", "#7e8189", partner="ZENITH",
        em_col="#c9cbd0", em2="#5c5f66"),
    mem="8GB GDDR6", pipes=4, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black", face_tag="black_plastic",
    over_tag="dark_plastic", ring_tag="black_plastic", logo_tag="paint_white", vent="slots", blades=9)

# 10. Voltra RX 9060 XT 16 GB, Zenith Frost White (Sapphire Pure): 245 x 120 x 45 mm, 2 slots, 2 fans, 1 x 8-pin
CARDS["gpu_voltra_9060xt_zenith_white"] = card(
    0.245, 0.120, 0.045, 2, 0.094, "pcie8", -0.084, -0.110, zenith_white(),
    art("VOLTRA", "RX 9060 XT", "FROST", "ZN-R9060XT-16G-W", "S/N 2506Z90600316", "#8c8f96", partner="ZENITH",
        light=True, em_col="#1a1b1e", em2="#a9acb2", hub_em="#1c1d20", hub_em2="#c4c7cc"),
    mem="16GB GDDR6", pipes=4, pipe_tag="nickel", bracket_tag="steel", back_tag="paint_white", face_tag="white_plastic",
    over_tag="grey_plastic", ring_tag="white_plastic", logo_tag="grey_plastic", vent="slots", fan_kw=WHITE_FAN,
    swatch="#c9ccd1")

# 11. Voltra RX 9070 XT 16 GB, Zenith Flare (Sapphire Nitro+): 320 x 128 x 62 mm, 3 slots, 3 fans, 12V-2x6, ARGB
CARDS["gpu_voltra_9070xt_zenith"] = card(
    0.320, 0.128, 0.062, 3, 0.090, "12v2x6", -0.106, -0.140, zenith_flare(),
    art("VOLTRA", "RX 9070 XT", "FLARE+", "ZN-R9070XT-16G-F", "S/N 2503Z90700052", "#2fa8ff", partner="ZENITH",
        em_col="#2fa8ff", em2="#e9e9ec", hub_em="#2fa8ff", hub_em2="#e9e9ec"),
    mem="16GB GDDR6", pipes=6, pipe_tag="nickel", bracket_tag="paint_black", back_tag="alu_dark", face_tag="alu_dark",
    over_tag="black_plastic", ring_tag="alu", logo_tag="alu", vent="hex", tip_ring=True, blades=11, fan_rpm=1900,
    bp_logo_x=-0.075)

# 12. Voltra RX 7900 XTX 24 GB reference: 287 x 123 x 51 mm, 2.5 slots, 3 fans, 2 x 8-pin
CARDS["gpu_voltra_7900xtx_ref"] = card(
    0.287, 0.123, 0.051, 3, 0.080, "pcie8", [-0.122, -0.100], -0.168, voltra_ref(),
    art("VOLTRA", "RX 7900 XTX", "REFERENCE", "VT-RX7900XTX-24G", "S/N 2212V79000951", "#c8141e", partner=None,
        em_col="#c8141e", em2="#f0f0f2", hub_em="#c8141e", hub_em2="#e9e9ec"),
    mem="24GB GDDR6", pipes=6, pipe_tag="copper", bracket_tag="paint_black", back_tag="alu_dark", face_tag="alu_dark",
    over_tag="black_plastic", ring_tag="alu", logo_tag="alu", vent="hex", blades=11, swatch="#c8141e",
    core="window", bp_logo_x=-0.060)

# 13. Tiron Lumen B580 12 GB reference: 272 x 115 x 45 mm, 2 slots, 2 fans, 1 x 8-pin, matte black and silver
CARDS["gpu_tiron_b580_ref"] = card(
    0.272, 0.115, 0.045, 2, 0.096, "pcie8", -0.090, -0.122, tiron_ref(),
    art("TIRON", "LUMEN B580", "REFERENCE", "TL-B580-12G-REF", "S/N 2412T05800467", "#3b8ee8", partner=None,
        em_col="#3b8ee8", em2="#0a0a0b", hub=("#0d0d0e", "#d6d8dc", "#3a3c42"), hub_em="#d6d8dc", hub_em2="#0d0d0e",
        made="MADE IN VIETNAM"),
    mem="12GB GDDR6", pipes=4, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black", face_tag="paint_black",
    over_tag="paint_black", ring_tag="paint_black", logo_tag="alu", vent="hex", blades=9, fan_rpm=2000,
    bp_logo_x=-0.045)

# 14. Verdia T100 80 GB PCIe (H100 PCIe): 268 x 111 x 40 mm, passive dual slot, 12V-2x6 at the far end
CARDS["gpu_verdia_t100"] = card(
    0.268, 0.111, 0.040, 0, 0.080, "12v2x6", -0.148, -0.167, dc_passive("sw0", "paint_black", accent_cell="sw1"),
    art("VERDIA", "T100 PCIe", "TENSOR CORE", "VD-T100-80G-PCIE", "S/N 1323V01000845", "#c9a24a", partner=None,
        em_col="#76b62a", em2="#0a0a0b", badge="VERDIA  T100", badge_bg="#c7a75d", badge_fg="#16171a",
        made="MADE IN TAIWAN"),
    mem="80GB HBM2e", pipes=6, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black", face_tag="paint_black",
    over_tag="paint_black", ring_tag="paint_black", logo_tag="paint_white", vent="full", outputs=False,
    swatches=["#c7a75d", "#76b62a"], bp_logo_x=-0.050, Hp=0.104)

# 15. Voltra Vector MI210 64 GB (AMD Instinct MI210): 267 x 111 x 40 mm, passive dual slot, 8-pin at the far end
CARDS["gpu_voltra_mi210"] = card(
    0.267, 0.111, 0.040, 0, 0.080, "pcie8", -0.147, -0.166, dc_passive("sw0", "paint_black", accent_cell="sw1"),
    art("VOLTRA", "VECTOR MI210", "ACCELERATOR", "VT-MI210-64G-PCIE", "S/N 2203V02100377", "#c8141e", partner=None,
        em_col="#c8141e", em2="#f0f0f2", badge="VOLTRA  VECTOR", badge_bg="#b9bcc2", badge_fg="#16171a"),
    mem="64GB HBM2e", pipes=6, pipe_tag="copper", bracket_tag="steel", back_tag="paint_black", face_tag="paint_black",
    over_tag="paint_black", ring_tag="paint_black", logo_tag="paint_white", vent="full", outputs=False,
    swatches=["#b9bcc2", "#c8141e"], bp_logo_x=-0.050, Hp=0.104)

for _pid, _s in CARDS.items():
    G.SPECS[_pid] = _s


_finish = pb.Model.finish


def _finish_with_unbox(self, *a, **k):
    """Adds the hub films once build_gpu has made the fans (anchors only; nothing else changes)."""
    s = CARDS.get(self.id)
    if s and s["fans"]:
        hub_films(self, s["fans"], s["fan_d"])
    return _finish(self, *a, **k)


pb.Model.finish = _finish_with_unbox


def build(pid):
    mdl = G.build(pid)
    return mdl.report()


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
        pb.shots = lambda *a, **k: []
    ids = [a for a in argv if not a.startswith("--") and a in CARDS] or list(CARDS)
    t0 = time.time()
    texts = {}
    if os.path.exists(REPORT):  # keep the other cards' sections when rebuilding a few
        cur = None
        for line in open(REPORT, encoding="utf-8").read().splitlines():
            if line.startswith("== "):
                cur = line[3:].strip()
                texts[cur] = []
            if cur:
                texts[cur].append(line)
        texts = {k: "\n".join(v) for k, v in texts.items()}
    for pid in ids:
        t = time.time()
        texts[pid] = build(pid)
        print(f"BUILT {pid} in {time.time() - t:.1f}s")
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(texts[k] for k in CARDS if k in texts) + "\n")
    print(f"BUILD_CAT_GPUS done: {len(ids)} cards in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(c.args())
