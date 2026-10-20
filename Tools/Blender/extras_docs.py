"""
extras_docs.py - the paper models of UNBOXING.md section 2.3 (agent C):
  doc_leaflet        a tri-fold quick install guide, folded (0.10 x 0.21), the cover springing up a little
  doc_booklet        a saddle-stitched A5 manual (0.148 x 0.21, about 3 mm), nested folded sheets, a slightly
                     curled cover and two staples on the spine
  doc_card           a warranty / installation card (0.09 x 0.055) with rounded corners
  doc_sticker_sheet  a case-badge backing card (0.08 x 0.06) with two raised badge stickers on A_STICKER_0..1
  doc_slip           a packing slip: an A4 folded in three (0.21 x 0.10)

Frame (all papers): origin at the bottom centre (the lowest point, the middle of the footprint), lying flat,
front face up (+Y), the top of the page towards +Z, reading right = +X. A_HIT_0 covers the paper.
Tags: doc_cover = the visible front face, doc_back = the visible back face, each with 0..1 UVs over that face
(front: u along +X, v along +Z; back: as if the paper were turned over about its vertical (Z) axis, i.e. u along
-X, v along +Z). Everything else (edges, folds, inner pages, the inside of the sheets) is paper_white.
The badge stickers use tex_doc_badges (an atlas of badge artworks, see BADGE_CELLS).
"""
import math
import random

import dct_common as c
import parts_b as pb
import extras_common as xc
from mathutils import Vector as V

DEG = math.pi / 180.0
TAU = 2.0 * math.pi


# ====================================================================== helpers

def _norm2(t):
    """Left normal of a 2D tangent (a, h)."""
    n = V((-t[1], t[0]))
    return n.normalized()


def _polyline_normals(P):
    out = []
    for i in range(len(P)):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, len(P) - 1)]
        out.append(_norm2(b - a))
    return out


def _arc(cx, ch, r, a0, a1, n):
    return [V((cx + r * math.cos(a0 + (a1 - a0) * k / n), ch + r * math.sin(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def _append(P, pts, tags, tag):
    for p in pts:
        if P and (p - P[-1]).length < 1e-7:
            continue
        P.append(p)
        tags.append(tag)


def ribbon(sheet, P, region, t, map3, L, nb=1, uv=None, lift=None, cap_tag="paper_white"):
    """A sheet of paper whose mid-surface cross-section is the 2D polyline P (a, h), extruded over b in [-L/2, L/2].
    region[i] names the cross-section point i ('cover', 'back' or anything else); a segment whose two ends share
    'cover' gets doc_cover on its OUTSIDE face (the left side of the polyline direction), 'back' gets doc_back.
    map3(a, h, b) -> Unity point. uv(kind, a_param, b) -> (u, v) for 'cover'/'back' faces, where a_param is the
    point's index-based cross-section param. lift(i, b) -> extra height for point i at b (curl)."""
    N = _polyline_normals(P)
    bs = [-L / 2 + L * k / nb for k in range(nb + 1)]

    def pt(i, b, side):
        dh = lift(i, b) if lift is not None else 0.0
        q = P[i] + N[i] * (t / 2 * side)
        return V(map3(q.x, q.y + dh, b))

    def nrm(i, side):
        n = N[i] * side
        return V(map3(n.x, n.y, 0.0)) - V(map3(0.0, 0.0, 0.0))

    for i in range(len(P) - 1):
        kind = region[i] if region[i] == region[i + 1] and region[i] in ("cover", "back") else None
        for k in range(nb):
            b0, b1 = bs[k], bs[k + 1]
            want = (nrm(i, 1) + nrm(i + 1, 1)) * 0.5
            # outside face
            pts = [pt(i, b0, 1), pt(i + 1, b0, 1), pt(i + 1, b1, 1), pt(i, b1, 1)]
            if kind is not None:
                tag = "doc_cover" if kind == "cover" else "doc_back"
                uvs = [uv(kind, i, b0), uv(kind, i + 1, b0), uv(kind, i + 1, b1), uv(kind, i, b1)]
                sheet.add(tag, pts, want, uvs)
            else:
                sheet.add("paper_white", pts, want)
            # inside face
            pts = [pt(i, b0, -1), pt(i + 1, b0, -1), pt(i + 1, b1, -1), pt(i, b1, -1)]
            sheet.add("paper_white", pts, -want)
        # the two cut edges at b = -L/2 and +L/2
        for b, s in ((bs[0], -1.0), (bs[-1], 1.0)):
            pts = [pt(i, b, 1), pt(i + 1, b, 1), pt(i + 1, b, -1), pt(i, b, -1)]
            sheet.add(cap_tag, pts, V(map3(0.0, 0.0, s)) - V(map3(0.0, 0.0, 0.0)))
    # the free edges at both ends of the polyline
    for i, s in ((0, -1.0), (len(P) - 1, 1.0)):
        j = 1 if i == 0 else len(P) - 2
        d = (P[i] - P[j]).normalized()
        want = V(map3(d.x, d.y, 0.0)) - V(map3(0.0, 0.0, 0.0))
        for k in range(nb):
            b0, b1 = bs[k], bs[k + 1]
            pts = [pt(i, b0, 1), pt(i, b1, 1), pt(i, b1, -1), pt(i, b0, -1)]
            sheet.add(cap_tag, pts, want)


def _hit(m, w, h, depth, meta=None):
    """A_HIT_0 covering a paper lying flat: w along x, depth (thickness) along y, h along z."""
    return m.anchor("A_HIT_0", (0.0, depth / 2, 0.0), (w, depth, h), meta=meta)


def _finish(m):
    m.finish()
    xc.triangulate(m.root)
    xc.validate(m.root)
    m.export()


# ====================================================================== tri-fold (leaflet, slip)

def trifold_section(w, t, rho1=0.00075, rho2=0.00025, spring_cover=0.0026, spring_flap=0.0006, n_arc=10,
                    n_cover=18, n_flap=8):
    """Cross-section (a across the folds, h up) of a roll-folded sheet: inner flap P1 (attached at the +a fold
    F2, lying on the back panel), back panel P2 (on the table), front cover P3 (attached at the -a fold F1, on
    top, its free edge springing up). Returns (points, regions, cover_range, back_range)."""
    P, R = [], []
    ac1 = -w / 2 + rho1 + t / 2       # F1 arc centre (outer fold, left)
    ac2 = w / 2 - rho2 - t / 2        # F2 arc centre (inner fold, right)
    # P1: from its free edge (inside the F1 loop) to the top of F2, springing up towards its free edge
    a_free = ac1 + 0.0004
    h1 = t / 2 + 2 * rho2
    pts = []
    for k in range(n_flap + 1):
        s = k / n_flap
        a = a_free + (ac2 - a_free) * s
        pts.append(V((a, h1 + spring_flap * (1.0 - s) ** 2.2)))
    _append(P, pts, R, "flap")
    # F2: from the top over the right side down to the bottom
    _append(P, _arc(ac2, t / 2 + rho2, rho2, 90 * DEG, -90 * DEG, n_arc // 2 + 2), R, "fold")
    # P2: flat on the table, right to left
    _append(P, [V((ac2, t / 2)), V((0.0, t / 2)), V((ac1, t / 2))], R, "back")
    R[-3] = "back"  # the arc's last point (== the panel's first) belongs to both; keep it 'back'
    # F1: from the bottom over the left side to the top
    _append(P, _arc(ac1, t / 2 + rho1, rho1, -90 * DEG, -270 * DEG, n_arc), R, "fold")
    R[-1] = "cover"
    # P3: the cover from the top of F1 to its free edge, springing up
    a_end = w / 2 - 0.0004
    h3 = t / 2 + 2 * rho1
    pts = []
    for k in range(1, n_cover + 1):
        s = k / n_cover
        a = ac1 + (a_end - ac1) * s
        pts.append(V((a, h3 + spring_cover * s ** 1.7)))
    _append(P, pts, R, "cover")
    return P, R, (ac1, a_end), (ac2, ac1)


def build_trifold(pid, w, L, landscape, spring_cover, meta):
    """Leaflet (portrait panels, folds along Z) or slip (landscape panels, folds along X)."""
    m = pb.Model(pid)
    t = 0.0001
    P, R, (c0, c1), (b0, b1) = trifold_section(w, t, spring_cover=spring_cover)
    if landscape:
        # folds along X: the cross-section runs along Z (a), the length along X (b)
        def map3(a, h, b):
            return (b, h, a)
    else:
        def map3(a, h, b):
            return (a, h, b)

    def uv(kind, i, b):
        a = P[i].x
        if kind == "cover":
            s = (a - c0) / (c1 - c0)
            bb = (b + L / 2) / L
            return (bb, s) if landscape else (s, bb)
        s = (b0 - a) / (b0 - b1)      # 0 at the +a fold, 1 at the -a fold
        bb = (b + L / 2) / L
        if landscape:
            # the back seen from below after turning the slip over about Z: u along -X, v along +Z
            return (1.0 - bb, 1.0 - s)
        return (s, bb)

    sh = xc.Sheet()
    ribbon(sh, P, R, t, map3, L, nb=1, uv=uv)
    sh.flush(m)
    depth = max(p.y for p in P) + t / 2
    if landscape:
        _hit(m, L, w, depth, meta)
    else:
        _hit(m, w, L, depth, meta)
    _finish(m)
    return m


# ====================================================================== booklet

def build_booklet(pid="doc_booklet", W=0.148, L=0.21, H=0.003):
    """A saddle-stitched A5 booklet: nested folded sheets (the cover outermost), the spine on the -X edge, two
    staples on the spine, the cover curling up a little towards the fore-edge and the bottom-right corner."""
    m = pb.Model(pid)
    sh = xc.Sheet()
    tc, tp, gap = 0.00025, 0.00023, 0.00001
    layers = [tc] + [tp] * 5
    xs = -W / 2 + H / 2                 # spine arc centre (x)
    yc = H / 2
    rng = random.Random(11)
    acc = 0.0
    curl_fore, curl_corner = 0.0021, 0.0016

    for k, tk in enumerate(layers):
        rho = H / 2 - acc - tk / 2 - k * gap
        acc += tk
        inset = 0.0 if k == 0 else 0.00035 + rng.uniform(0.0, 0.00030)
        x_end = W / 2 - inset
        n_leaf = 12 if k == 0 else 5
        n_arc = 10 if k == 0 else 6
        nb = 8 if k == 0 else 4
        f = 1.0 if k == 0 else max(0.0, 0.55 - 0.12 * k)   # how much this sheet follows the cover's curl
        P, R = [], []
        # bottom leaf: fore-edge -> spine (flat on the table)
        _append(P, [V((x_end - (x_end - xs) * s / 2, yc - rho)) for s in range(3)], R, "back")
        # spine fold
        _append(P, _arc(xs, yc, rho, -90 * DEG, -270 * DEG, n_arc), R, "spine")
        R[-1] = "cover"
        # top leaf: spine -> fore-edge
        _append(P, [V((xs + (x_end - xs) * s / n_leaf, yc + rho)) for s in range(1, n_leaf + 1)], R, "cover")
        if k > 0:
            R = ["page"] * len(R)
        n_top0 = len(P) - n_leaf - 1      # index of the first top-leaf point (the arc's end)

        def lift(i, b, P=P, n_top0=n_top0, f=f, xs=xs, x_end=x_end, k=k):
            if i < n_top0:
                return 0.0
            xn = (P[i].x - xs) / (x_end - xs)
            zn = b / (L / 2)
            v = curl_fore * xn ** 2.6
            corner = max(0.0, (xn - 0.55) / 0.45) ** 2 * max(0.0, (-zn - 0.45) / 0.55) ** 2
            v += curl_corner * corner * (1.0 if k == 0 else 0.35)
            return v * f

        def uv(kind, i, b, P=P, xs=xs, x_end=x_end):
            bb = (b + L / 2) / L
            s = (P[i].x - xs) / (x_end - xs)
            if kind == "cover":
                return (max(0.0, s), bb)
            return (1.0 - s, bb)     # back cover: u along -X (spine on the right when turned over), v along +Z

        ribbon(sh, P, R, tk, lambda a, h, b: (a, h, b), L, nb=nb, uv=uv, lift=lift)
    sh.flush(m)
    # two staples: crowns lying on the spine ridge, the legs bent in through the fold
    x_ridge = xs - H / 2
    for z in (-L / 4, L / 4):
        crown = 0.0122
        g = pb.g_sweep([(x_ridge + 0.00025, yc, z - crown / 2), (x_ridge - 0.00005, yc, z - crown / 2 + 0.0004),
                        (x_ridge - 0.00012, yc, z), (x_ridge - 0.00005, yc, z + crown / 2 - 0.0004),
                        (x_ridge + 0.00025, yc, z + crown / 2)], 0.00026, 8)
        m.add("steel", g)
        # flattened look: a thin strip on top of the wire
        m.add("steel", pb.g_box((0.00012, 0.00062, crown - 0.0012)), None, (x_ridge - 0.00026, yc, z))
    depth = H + curl_fore + curl_corner * 0.6
    _hit(m, W, L, depth, "doc=manual,pages=24,spine=-x,staples=2")
    _finish(m)
    return m


# ====================================================================== flat card and sticker sheet

def flat_card(sh, W, Hh, t, r, y0=0.0, seg=6, tags=("doc_cover", "doc_back", "paper_white")):
    """A flat rounded-rectangle card lying on y0..y0+t: top face (tags[0]) with u along +X, v along +Z; bottom
    face (tags[1]) with u along -X, v along +Z; the rim (tags[2])."""
    outline = pb.rrect2(0.0, 0.0, W, Hh, r, seg)   # (x, z)
    flat, tris = pb._tess([list(outline)])
    top = [V((p[0], y0 + t, p[1])) for p in flat]
    bot = [V((p[0], y0, p[1])) for p in flat]
    for tr in tris:
        sh.add(tags[0], [top[i] for i in tr], (0, 1, 0), [((flat[i][0] + W / 2) / W, (flat[i][1] + Hh / 2) / Hh)
                                                         for i in tr])
        sh.add(tags[1], [bot[i] for i in tr], (0, -1, 0), [((W / 2 - flat[i][0]) / W, (flat[i][1] + Hh / 2) / Hh)
                                                           for i in tr])
    n = len(outline)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        mid = V(((a[0] + b[0]) / 2, 0.0, (a[1] + b[1]) / 2))
        d = V((b[0] - a[0], 0.0, b[1] - a[1]))
        out = V((d.z, 0.0, -d.x))
        if out.dot(mid) < 0:
            out = -out
        sh.add(tags[2], [V((a[0], y0, a[1])), V((b[0], y0, b[1])), V((b[0], y0 + t, b[1])), V((a[0], y0 + t, a[1]))],
               out)


def build_card(pid="doc_card", W=0.09, Hh=0.055):
    m = pb.Model(pid)
    sh = xc.Sheet()
    t = 0.00035
    flat_card(sh, W, Hh, t, 0.0032)
    sh.flush(m)
    _hit(m, W, Hh, t, "doc=card")
    _finish(m)
    return m


# badge atlas (tex_doc_badges.png, 1024 x 1024, 4 x 4 cells of 256 px; row 0 at the top)
BADGE_CELLS = [  # cell index: (col, row, text)
    (0, 0, "ARC 5 (cpu_arc5 main)"), (1, 0, "ARC 7 (cpu_arc7 main)"), (2, 0, "TIRON i5 (cpu_tiron5 main)"),
    (3, 0, "RIDGE GAMING (boards main)"), (0, 1, "VOLTRA RX (gpus main)"), (1, 1, "ARC mark (small)"),
    (2, 1, "TIRON mark (small)"), (3, 1, "RIDGE mark (small)"), (0, 2, "VOLTRA mark (small)"),
]
EDGE_CELL = (1, 2)   # a brushed-silver swatch for the badges' rims


def cell_uv(col, row, inset=3.0):
    """UV rectangle (u0, v0, u1, v1) of an atlas cell (v up)."""
    px = 256.0
    u0 = (col * px + inset) / 1024.0
    u1 = ((col + 1) * px - inset) / 1024.0
    v1 = 1.0 - (row * px + inset) / 1024.0
    v0 = 1.0 - ((row + 1) * px - inset) / 1024.0
    return (u0, v0, u1, v1)


def badge_texture():
    """Renders tex_doc_badges.png: domed metal-look case badges for the fictional brands."""
    cv = pb.Canvas(1024, 1024, bg="#202024")

    def plate(col, row, bg, rim, rim2="#e9eaee"):
        x, y = col * 256, row * 256
        cv.rect(x, y, 256, 256, rim)
        cv.rect(x + 6, y + 6, 244, 244, rim2, r=26)
        cv.rect(x + 14, y + 14, 228, 228, rim, r=20)
        cv.rect(x + 20, y + 20, 216, 216, bg, r=16)
        # a soft highlight band (the dome catching light)
        cv.poly([(x + 22, y + 60), (x + 234, y + 22), (x + 234, y + 70), (x + 22, y + 108)], _mix(bg, "#ffffff", 0.07))
        return x, y

    # ---- ARC 5 / ARC 7: black, an orange arc, ARC, big digit in a box
    for col, digit in ((0, "5"), (1, "7")):
        x, y = plate(col, 0, "#0e0e10", "#9a9ca3")
        cx = x + 128
        cv.ring(cx - 46, y + 96, 32, 42, "#f08a24")
        cv.rect(cx - 92, y + 96, 92, 48, "#0e0e10")     # cut the ring into an arc (open bottom)
        cv.text("ARC", cx - 46, y + 128, 40, "#f2f2f4", "agency", "center", "center", spacing=1.15)
        cv.rect(cx + 14, y + 50, 74, 104, "#f08a24", r=10)
        cv.text(digit, cx + 51, y + 102, 74, "#101012", "black", "center", "center")
        cv.rect(x + 40, y + 172, 176, 3, "#f08a24")
        cv.text("PROCESSOR", cx, y + 200, 17, "#c5c7cd", "arialb", "center", "center", spacing=1.15, maxw=170)
    # ---- TIRON i5: deep blue, a ring, tiron, CORE i5
    x, y = plate(2, 0, "#0a3d7a", "#a9b3c4")
    cx = x + 128
    cv.ring(cx, y + 112, 74, 82, "#5fb4ff")
    cv.rect(cx - 96, y + 104, 40, 22, "#0a3d7a")
    cv.text("tiron", cx, y + 104, 46, "#ffffff", "segoe", "center", "center", maxw=140)
    cv.rect(cx - 52, y + 136, 104, 40, "#ffffff", r=8)
    cv.text("CORE i5", cx, y + 156, 22, "#0a3d7a", "segoe_black", "center", "center", maxw=92)
    cv.text("14TH GEN", cx, y + 212, 15, "#cfe6ff", "arialb", "center", "center", spacing=1.2, maxw=170)
    # ---- RIDGE GAMING: dark steel, mountain-ridge emblem
    x, y = plate(3, 0, "#151619", "#8d96a4")
    cx = x + 128
    cv.poly([(cx - 84, y + 140), (cx - 34, y + 64), (cx - 6, y + 104), (cx + 22, y + 72), (cx + 84, y + 140),
             (cx + 60, y + 140), (cx + 22, y + 98), (cx - 6, y + 128), (cx - 34, y + 92), (cx - 60, y + 140)], "#d9dde4")
    cv.text("RIDGE", cx, y + 172, 38, "#eef0f3", "agency", "center", "center", spacing=1.2, maxw=180)
    cv.text("GAMING", cx, y + 208, 16, "#8d96a4", "arialb", "center", "center", spacing=1.3, maxw=150)
    # ---- VOLTRA RX: black, the V emblem in red and white
    x, y = plate(0, 1, "#0b0b0c", "#8a8c92")
    cx = x + 128

    def vemblem(x0, y0, hgt, c1, c2):
        w = hgt * 0.9
        cv.poly([(x0, y0), (x0 + w * 0.28, y0), (x0 + w * 0.52, y0 + hgt * 0.72), (x0 + w * 0.4, y0 + hgt)], c1)
        cv.poly([(x0 + w * 0.62, y0 + hgt * 0.42), (x0 + w * 0.76, y0), (x0 + w * 1.04, y0),
                 (x0 + w * 0.74, y0 + hgt * 0.62)], c2)

    vemblem(cx - 50, y + 46, 100, "#c8141e", "#f0f0f2")
    cv.text("VOLTRA", cx, y + 176, 34, "#f2f2f4", "agency", "center", "center", spacing=1.15, maxw=180)
    cv.text("RX GRAPHICS", cx, y + 208, 15, "#c8141e", "arialb", "center", "center", spacing=1.2, maxw=160)
    # ---- small marks
    x, y = plate(1, 1, "#0e0e10", "#9a9ca3")
    cv.ring(x + 128, y + 116, 56, 70, "#f08a24")
    cv.rect(x + 50, y + 116, 156, 80, "#0e0e10")
    cv.text("ARC", x + 128, y + 160, 54, "#f2f2f4", "agency", "center", "center", spacing=1.3)
    x, y = plate(2, 1, "#0a3d7a", "#a9b3c4")
    cv.ring(x + 128, y + 128, 80, 88, "#5fb4ff")
    cv.text("tiron", x + 128, y + 128, 58, "#ffffff", "segoe", "center", "center")
    x, y = plate(3, 1, "#151619", "#8d96a4")
    cv.poly([(x + 44, y + 170), (x + 94, y + 86), (x + 122, y + 128), (x + 150, y + 94), (x + 212, y + 170),
             (x + 186, y + 170), (x + 150, y + 122), (x + 122, y + 156), (x + 94, y + 116), (x + 70, y + 170)],
            "#d9dde4")
    x, y = plate(0, 2, "#0b0b0c", "#8a8c92")
    vemblem(x + 70, y + 64, 128, "#c8141e", "#f0f0f2")
    # ---- rim swatches
    cv.rect(256, 512, 256, 256, "#c9ccd2")
    cv.rect(512, 512, 256, 256, "#2a2b2f")
    cv.render("doc_badges")


def _mix(a, b, t):
    ha, hb = a.lstrip("#"), b.lstrip("#")
    ca = [int(ha[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(hb[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(round(x + (y - x) * t)):02x}" for x, y in zip(ca, cb))


def badge(model, anchor, w, h, r, y0, cell, thick=0.00038, dome=0.00014, seg=5):
    """A domed badge sticker (moving piece of its A_STICKER anchor): a rounded-rectangle foil plate whose top
    rises gently to the middle, the artwork (atlas cell) on top, a silver rim."""
    sh = xc.Sheet()
    ax, az = anchor["centre"]
    u0, v0, u1, v1 = cell_uv(*cell)
    eu0, ev0, eu1, ev1 = cell_uv(*EDGE_CELL, inset=40)
    outline = pb.rrect2(0.0, 0.0, w, h, r, seg)
    # top: a grid of rings from the rim inwards (shrinking outlines) so the dome is smooth
    rings = []
    nr = 4
    for k in range(nr + 1):
        s = 1.0 - k / nr * 0.92
        rise = dome * (1.0 - (1.0 - k / nr) ** 2) if k > 0 else 0.0
        yy = y0 + thick - dome + rise + (0.0 if k > 0 else 0.0)
        if k == 0:
            yy = y0 + thick - dome - 0.00006
        rings.append([V((ax + p[0] * s, yy, az + p[1] * s)) for p in outline])
    n = len(outline)

    def uvp(p):
        return (u0 + (p.x - ax + w / 2) / w * (u1 - u0), v0 + (p.z - az + h / 2) / h * (v1 - v0))

    for k in range(nr):
        for i in range(n):
            j = (i + 1) % n
            pts = [rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]]
            sh.add("tex_doc_badges", pts, (0, 1, 0), [uvp(p) for p in pts], smooth=True)
    centre = V((ax, rings[-1][0].y, az))
    for i in range(n):
        j = (i + 1) % n
        pts = [rings[-1][i], rings[-1][j], centre]
        sh.add("tex_doc_badges", pts, (0, 1, 0), [uvp(p) for p in pts], smooth=True)
    # rim (vertical sides) and the underside (the adhesive face: plain, the rim swatch)
    eu = ((eu0 + eu1) / 2, (ev0 + ev1) / 2)
    for i in range(n):
        j = (i + 1) % n
        a, b = outline[i], outline[j]
        pa = V((ax + a[0], y0, az + a[1]))
        pb_ = V((ax + b[0], y0, az + b[1]))
        top_a, top_b = rings[0][i], rings[0][j]
        out = V((b[1] - a[1], 0.0, -(b[0] - a[0])))
        if out.dot(V((a[0] + b[0], 0.0, a[1] + b[1]))) < 0:
            out = -out
        sh.add("tex_doc_badges", [pa, pb_, top_b, top_a], out, [eu] * 4)
    flat, tris = pb._tess([list(outline)])
    for tr in tris:
        sh.add("tex_doc_badges", [V((ax + flat[q][0], y0, az + flat[q][1])) for q in tr], (0, -1, 0), [eu] * 3)
    sh.flush(model, anchor["obj"], anchor["name"])


def build_sticker_sheet(pid="doc_sticker_sheet", W=0.08, Hh=0.06):
    """The case-badge sticker sheet: a glossy backing card (doc_cover / doc_back) with two badges on it."""
    badge_texture()
    m = pb.Model(pid)
    sh = xc.Sheet()
    t = 0.0003
    flat_card(sh, W, Hh, t, 0.0025)
    sh.flush(m)
    specs = [  # name, centre (x, z), w, h, corner r, default cell
        ("badge_0", (-0.0135, 0.0040), 0.022, 0.022, 0.0030, (0, 0)),
        ("badge_1", (0.0190, 0.0040), 0.016, 0.016, 0.0025, (1, 1)),
    ]
    for i, (name, (x, z), w, h, r, cell) in enumerate(specs):
        idx = [k for k, cc in enumerate(BADGE_CELLS) if (cc[0], cc[1]) == cell][0]
        a = m.anchor(f"A_STICKER_{i}", (x, t, z), (w, h, 0.0005), forward=(0, 1, 0), up=(0, 0, 1),
                     meta=f"shape=rrect,w={w:.3f},h={h:.3f},r={r:.4f},cell={idx},peel=+y")
        badge(m, {"obj": a, "name": name, "centre": (x, z)}, w, h, r, t, cell)
    _hit(m, W, Hh, t + 0.0004, "doc=sticker,badges=2")
    _finish(m)
    return m


# ====================================================================== preview pages (scratch only)

def preview_pages(scratch):
    """Test artwork for doc_cover / doc_back in the previews (never exported): a page per paper kind with an
    obvious top, reading direction and page number, so a flipped or mirrored UV shows at once."""
    import os
    import bpy
    old = c.TEXTURES
    c.TEXTURES = scratch
    out = {}
    try:
        for kind, (w, h) in {"leaflet": (480, 1008), "booklet": (592, 840), "card": (720, 440),
                             "sticker": (640, 480), "slip": (1008, 480)}.items():
            for side in ("front", "back"):
                cv = pb.Canvas(w, h, bg="#fbfbf8")
                acc = {"leaflet": "#c8141e", "booklet": "#1d3d6b", "card": "#2b2b2f", "sticker": "#e9e9ec",
                       "slip": "#1f6f43"}[kind]
                hb = int(h * 0.16) if h > w else int(h * 0.22)
                if side == "front":
                    cv.rect(0, 0, w, hb, acc)
                    cv.text({"leaflet": "QUICK INSTALL GUIDE", "booklet": "USER MANUAL", "card": "WARRANTY CARD",
                             "sticker": "CASE BADGES", "slip": "PACKING SLIP"}[kind], w * 0.06, hb * 0.5,
                            hb * 0.28, "#ffffff" if kind != "sticker" else "#202024", "arialb", "left", "center",
                            maxw=w * 0.88)
                    y = hb + h * 0.05
                    if kind in ("leaflet", "booklet"):
                        cv.rect(w * 0.12, y, w * 0.76, h * 0.32, "#d9dadd", r=8)
                        cv.text("1", w * 0.5, y + h * 0.16, h * 0.08, "#9a9ca3", "arialb", "center", "center")
                        y += h * 0.37
                    for k in range(7 if h > w else 3):
                        cv.rect(w * 0.08, y + k * h * 0.045, w * (0.84 - 0.1 * (k % 3)), h * 0.014, "#8c8e94")
                    cv.text("TOP >", w * 0.94, hb * 0.5, hb * 0.18, "#ffffff", "arialb", "right", "center")
                else:
                    cv.rect(0, h - hb * 0.5, w, hb * 0.5, acc)
                    cv.text("BACK", w * 0.06, h * 0.12, h * 0.06, "#303034", "arialb", "left", "center")
                    for k in range(5 if h > w else 2):
                        cv.rect(w * 0.08, h * 0.22 + k * h * 0.05, w * 0.7, h * 0.014, "#a4a6ab")
                    cv.barcode(w * 0.6, h * 0.66, w * 0.3, h * 0.08)
                path = cv.render(f"preview_{kind}_{side}")
                out[(kind, side)] = bpy.data.images.load(path, check_existing=True)
    finally:
        c.TEXTURES = old
    return out
