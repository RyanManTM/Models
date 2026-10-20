"""
CPU models: cpu_arc5 and cpu_arc7 (Socket V5, a 40 x 40 mm LGA package with an "octopus" heat spreader)
and cpu_tiron5 (Socket L17, a 37.5 x 45 mm LGA package with a notched rectangular heat spreader).

Frame (REALISM.md section 2): origin at the centre of the bottom (contact) face, +z up, the IHS top at
z 0.006. The pin-1 corner is (+x, -y): bottom-left when looking down at the IHS with +y up.

Run: blender -b --factory-startup -P Tools/Blender/build_cpu.py -- [ids...]
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

SPECS = {
    "cpu_arc5": dict(sock="V5", line1="ARC 5 7600", cores="6-CORE", opn="100-000000593", lot="9HA3527U30046",
                     fab="DIFFUSED IN TAIWAN", made="MADE IN MALAYSIA", seed=5),
    "cpu_arc7": dict(sock="V5", line1="ARC 7 7800", cores="8-CORE", opn="100-000000590", lot="2LH9264M20117",
                     fab="DIFFUSED IN TAIWAN", made="MADE IN CHINA", seed=7),
    "cpu_tiron5": dict(sock="L17", line1="TIRON® CORE™ i5-14400", spec="SRN46 2.50GHZ", fpo="X340L978",
                       year="©'23", seed=14),
}

# Package geometry in millimetres.
PKG = {
    "V5": dict(sx=40.0, sy=40.0, t=1.2, top=6.0, pitch=0.95, void=None,
               notches=[("+x", 12.0, 1.0), ("-x", 12.0, 1.0)]),
    "L17": dict(sx=37.5, sy=45.0, t=1.1, top=6.0, pitch=0.9, void=(9.0, 16.0),
                notches=[("+x", 14.0, 1.0), ("-x", 14.0, 1.0)]),
}

SUB_GREEN = {"V5": "#2b5a3c", "L17": "#244f3a"}
NICKEL = "#c4c6c9"
ETCH = "#7d8085"


# ------------------------------------------------------------------ outlines

def fillet_poly(pts, radii, seg=4):
    """Rounds each corner of a polygon by its radius (0 = sharp). Counter-clockwise in, out."""
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = Vector((*pts[i - 1], 0)), Vector((*pts[i], 0)), Vector((*pts[(i + 1) % n], 0))
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        if r <= 0:
            out.append((p1.x, p1.y))
            continue
        a = (p0 - p1).normalized()
        b = (p2 - p1).normalized()
        ang = math.acos(max(-1.0, min(1.0, a.dot(b))))
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append((p1.x, p1.y))
            continue
        d = r / math.tan(ang * 0.5)
        d = min(d, (p0 - p1).length * 0.49, (p2 - p1).length * 0.49)
        rr = d * math.tan(ang * 0.5)
        s = p1 + a * d
        e = p1 + b * d
        bis = (a + b).normalized()
        cen = p1 + bis * (rr / math.sin(ang * 0.5))
        a0 = math.atan2(s.y - cen.y, s.x - cen.x)
        a1 = math.atan2(e.y - cen.y, e.x - cen.x)
        da = a1 - a0
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        for k in range(seg + 1):
            t = a0 + da * k / seg
            out.append((cen.x + math.cos(t) * rr, cen.y + math.sin(t) * rr))
    return out


def substrate_outline(P):
    """Rounded rectangle with semicircular keying notches cut into the side edges (mm)."""
    sx, sy = P["sx"] * 0.5, P["sy"] * 0.5
    rc = 0.6
    pts = []
    # corners with fillets, notches on the +x / -x edges (counter-clockwise)
    def arc(cx, cy, r, a0, a1, n=8):
        return [(cx + math.cos(math.radians(a0 + (a1 - a0) * k / n)) * r, cy + math.sin(math.radians(a0 + (a1 - a0) * k / n)) * r) for k in range(n + 1)]
    pts += arc(-sx + rc, -sy + rc, rc, 180, 270, 3)
    pts += arc(sx - rc, -sy + rc, rc, 270, 360, 3)
    for side, pos, r in P["notches"]:
        if side == "+x":
            pts += [(sx + math.cos(math.radians(a)) * r, pos + math.sin(math.radians(a)) * r) for a in [270 - 180 * k / 8 for k in range(9)]]
    pts += arc(sx - rc, sy - rc, rc, 0, 90, 3)
    pts += arc(-sx + rc, sy - rc, rc, 90, 180, 3)
    for side, pos, r in P["notches"]:
        if side == "-x":
            pts += [(-sx + math.cos(math.radians(a)) * r, pos + math.sin(math.radians(a)) * r) for a in [90 - 180 * k / 8 for k in range(9)]]
    return pts


def ihs_outline_v5():
    """Octopus IHS: a body with four legs on the top and bottom edges, gaps exposing capacitors (mm)."""
    bx, by, ly = 17.6, 15.6, 18.9
    legs = [(-14.6, 4.6), (-4.9, 4.4), (4.9, 4.4), (14.6, 4.6)]  # (centre x, width)
    pts, rad = [], []
    # bottom edge, from left (-x) to right (+x), legs going down to -ly
    pts.append((-bx, -by + 0.0)); rad.append(1.2)
    for cx, w in legs:
        x0, x1 = cx - w / 2, cx + w / 2
        if x0 > -bx + 0.01:
            pts.append((x0, -by)); rad.append(0.5)
        pts.append((max(x0, -bx), -ly)); rad.append(0.9)
        pts.append((min(x1, bx), -ly)); rad.append(0.9)
        if x1 < bx - 0.01:
            pts.append((x1, -by)); rad.append(0.5)
    # right edge up, top edge from right to left
    for cx, w in reversed(legs):
        x0, x1 = cx - w / 2, cx + w / 2
        if x1 < bx - 0.01:
            pts.append((x1, by)); rad.append(0.5)
        pts.append((min(x1, bx), ly)); rad.append(0.9)
        pts.append((max(x0, -bx), ly)); rad.append(0.9)
        if x0 > -bx + 0.01:
            pts.append((x0, by)); rad.append(0.5)
    # dedupe consecutive
    out, orad = [], []
    for p, r in zip(pts, rad):
        if out and abs(out[-1][0] - p[0]) < 1e-6 and abs(out[-1][1] - p[1]) < 1e-6:
            continue
        out.append(p)
        orad.append(r)
    return fillet_poly(out, orad, 3)


def ihs_gaps_v5():
    """The exposed substrate areas between the legs (x0, x1, y0, y1) in mm, top and bottom."""
    xs = [(-12.3, -7.1), (-2.7, 2.7), (7.1, 12.3)]
    out = []
    for s in (-1, 1):
        for x0, x1 in xs:
            out.append((x0, x1, min(s * 15.6, s * 19.4), max(s * 15.6, s * 19.4)))
    return out


def ihs_outline_l17():
    bx, by = 14.6, 18.3
    nd, nl = 1.6, 5.0  # notch depth, length
    ys = [-12.0, 12.0]
    pts = [(-bx, -by), (bx, -by)]
    for y in ys:  # right edge going up
        pts += [(bx, y - nl / 2), (bx - nd, y - nl / 2), (bx - nd, y + nl / 2), (bx, y + nl / 2)]
    pts += [(bx, by), (-bx, by)]
    for y in reversed(ys):  # left edge going down
        pts += [(-bx, y + nl / 2), (-bx + nd, y + nl / 2), (-bx + nd, y - nl / 2), (-bx, y - nl / 2)]
    rad = []
    for p in pts:
        corner = abs(abs(p[0]) - bx) < 1e-6 and abs(abs(p[1]) - by) < 1e-6
        rad.append(1.4 if corner else 0.45)
    return fillet_poly(pts, rad, 3)


def land_positions(P):
    """LGA land centres (mm), hex-staggered rows, excluding the corner key and the central void."""
    sx, sy, pitch = P["sx"], P["sy"], P["pitch"]
    rows = int((sy - 2.6) / (pitch * 0.866)) + 1
    out = []
    for r in range(rows):
        y = -(rows - 1) * pitch * 0.866 * 0.5 + r * pitch * 0.866
        off = (pitch * 0.5) if r % 2 else 0.0
        cols = int((sx - 2.6 - off) / pitch) + 1
        for k in range(cols):
            x = -(cols - 1) * pitch * 0.5 + k * pitch + off * 0.0
            x += (pitch * 0.25 if r % 2 else -pitch * 0.25)
            if abs(x) > sx * 0.5 - 1.3 or abs(y) > sy * 0.5 - 1.3:
                continue
            if P["void"] and abs(x) < P["void"][0] * 0.5 and abs(y) < P["void"][1] * 0.5:
                continue
            # pin-1 corner key: no lands under the big triangle
            if x > sx * 0.5 - 5.0 and y < -sy * 0.5 + 5.0 and (x - (sx * 0.5 - 5.0)) - (y - (-sy * 0.5 + 5.0)) > 0:
                continue
            out.append((x, y))
    return out


# ------------------------------------------------------------------ textures

def datamatrix(art, x, y, size, n, seed, col, bg=None):
    """A Data Matrix-looking 2D code: L finder on two sides, clock track on the others."""
    rnd = random.Random(seed)
    cell = size / n
    if bg is not None:
        art.rect(x - cell, y - cell, x + size + cell, y + size + cell, bg, z=0.3)
    for i in range(n):
        for j in range(n):
            on = False
            if i == 0 or j == 0:
                on = True
            elif i == n - 1:
                on = (j % 2 == 0)
            elif j == n - 1:
                on = (i % 2 == 1)
            else:
                on = rnd.random() < 0.5
            if on:
                art.rect(x + i * cell, y + j * cell, x + (i + 1) * cell, y + (j + 1) * cell, col, z=0.35)


def substrate_texture(cid, sock, P):
    """Top (left half) and land side (right half) of the package substrate."""
    name = f"cpu_{sock.lower()}_pcb"
    path = pp.tex_path(name)
    at = pp.Atlas(2048, 1024, bg=SUB_GREEN[sock])
    ppm = 1000.0 / max(P["sx"], P["sy"])
    sx, sy = P["sx"], P["sy"]
    green = SUB_GREEN[sock]
    darker = pp.shade(green, 0.82)
    lighter = pp.shade(green, 1.18)
    gold = "#c9a34e"
    rnd = random.Random(42 if sock == "V5" else 43)
    regions = {}
    # ---- top side
    r, uv, ctx = at.panel(sx, sy, ppm, bg=green)
    regions["top"] = uv
    with ctx as a:
        # faint routing under the mask
        for k in range(160):
            x0, y0 = rnd.uniform(0.5, sx - 0.5), rnd.uniform(0.5, sy - 0.5)
            pts = [(x0, y0)]
            for s in range(rnd.randint(2, 5)):
                dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1)])
                L = rnd.uniform(0.6, 4.0)
                x0 = min(sx - 0.4, max(0.4, x0 + dx * L))
                y0 = min(sy - 0.4, max(0.4, y0 + dy * L))
                pts.append((x0, y0))
            a.line(pts, 0.09, lighter, z=0.2)
        for k in range(400):
            a.circle(rnd.uniform(0.6, sx - 0.6), rnd.uniform(0.6, sy - 0.6), 0.12, darker, z=0.25, seg=8)
        # capacitor pads in the IHS gaps (art coords: u = sx/2 - x, v = y + sy/2)
        if sock == "V5":
            for x0, x1, y0, y1 in ihs_gaps_v5():
                for (cx, cy) in v5_gap_caps(x0, x1, y0, y1):
                    u, v = sx / 2 - cx, cy + sy / 2
                    for s in (-1, 1):
                        a.rect(u - 0.3, v + s * 0.42 - 0.2, u + 0.3, v + s * 0.42 + 0.2, gold, z=0.4)
        else:
            for (cx, cy, ang) in l17_top_caps():
                u, v = sx / 2 - cx, cy + sy / 2
                if ang == 0:
                    for s in (-1, 1):
                        a.rect(u + s * 0.42 - 0.2, v - 0.3, u + s * 0.42 + 0.2, v + 0.3, gold, z=0.4)
                else:
                    for s in (-1, 1):
                        a.rect(u - 0.3, v + s * 0.42 - 0.2, u + 0.3, v + s * 0.42 + 0.2, gold, z=0.4)
        # pin-1 triangle print (the gold triangle itself is geometry; a white outline frames it)
        tri = [(0.7, 0.7), (4.2, 0.7), (0.7, 4.2)]
        a.poly([(p[0] - 0.25, p[1] - 0.25) for p in [(0.7, 0.7), (4.75, 0.7), (0.7, 4.75)]], "#e8e4d8", z=0.3)
        a.poly(tri, green, z=0.31)
        # small print in the margins
        if sock == "V5":
            a.text("2318PGS  B2", sx - 2.6, sy / 2, 0.75, "#e0ddd0", font="narrowbd", rot=90)
            a.text("○ 37", 1.4, sy - 1.2, 0.7, "#e0ddd0", font="narrowbd")
            datamatrix(a, 1.2, sy / 2 - 2.0, 3.0, 12, 99, "#e8e4d8")
        else:
            a.text("K8-3A 2327", sx / 2, sy - 1.6, 0.8, "#e0ddd0", font="narrowbd")
            a.text("V1309P", sx / 2, 1.6, 0.8, "#e0ddd0", font="narrowbd")
            datamatrix(a, sx - 3.6, sy - 5.4, 2.6, 12, 77, "#e8e4d8")
    # ---- land side (looking up at the bottom: u = x + sx/2)
    r, uv, ctx = at.panel(sx, sy, ppm, bg=green)
    regions["bottom"] = uv
    with ctx as a:
        for (x, y) in land_positions(P):
            u, v = x + sx / 2, y + sy / 2
            a.circle(u, v, 0.43, darker, z=0.2, seg=10)
            a.circle(u, v, 0.33, gold, z=0.3, seg=10)
        # corner triangle (gold) at the pin-1 corner (+x, -y): seen from below +x is on the right
        a.poly([(sx - 0.8, 0.8), (sx - 5.6, 0.8), (sx - 0.8, 5.6)], gold, z=0.4)
        if P["void"]:
            vx, vy = P["void"]
            a.rrect(sx / 2, sy / 2, vx - 0.6, vy - 0.6, 0.6, "#1a1c1c", z=0.2)
            for (x, y) in l17_void_caps():
                u, v = x + sx / 2, y + sy / 2
                for s in (-1, 1):
                    a.rect(u + s * 0.45 - 0.22, v - 0.32, u + s * 0.45 + 0.22, v + 0.32, gold, z=0.4)
        a.text("V5" if sock == "V5" else "L17", 2.6, sy - 2.2, 1.0, "#e0ddd0", font="narrowbd")
    regions["edge"] = at.swatch("#5f6650")
    at.render(path)
    return name, regions


def ihs_texture(cid, S, sock, size_mm, text_up_x):
    """Laser-etched markings on the nickel heat spreader. size_mm = (w, h) in the text's frame."""
    name = f"{cid}_ihs"
    w, h = size_mm
    at = pp.Atlas(1024, 1024, bg=NICKEL)
    ppm = 1000.0 / max(w, h)
    r, uv, ctx = at.panel(w, h, ppm, bg=NICKEL)
    rnd = random.Random(S["seed"])
    with ctx as a:
        # lapping marks: faint concentric arcs and noise
        for k in range(70):
            rr = rnd.uniform(4, 60)
            cx, cy = rnd.uniform(-40, w + 40), rnd.uniform(-40, h + 40)
            col = pp.shade(NICKEL, rnd.uniform(0.98, 1.015))
            seg = 48
            pts = []
            a0 = rnd.uniform(0, 6.28)
            for i in range(seg):
                t = a0 + i * 0.05
                pts.append((cx + math.cos(t) * rr, cy + math.sin(t) * rr))
            a.line(pts, rnd.uniform(0.15, 0.6), col, z=0.1, joins=False)
        cxm, cym = w / 2, h / 2
        if sock == "V5":
            # Arc logo: an arc swoosh plus the wordmark
            ly = cym + 9.4
            pts = [(cxm - 9.6 + 5.0 * math.cos(math.radians(a_)), ly - 2.2 + 5.0 * math.sin(math.radians(a_))) for a_ in range(30, 151, 6)]
            a.line(pts, 0.75, ETCH, z=0.5)
            a.text("ARC", cxm - 9.6, ly - 0.6, 3.6, ETCH, font="agency", ay="CENTER")
            a.text(S["line1"], cxm, cym + 3.4, 3.1, ETCH, font="arialbd", fit=30.0)
            a.text(S["cores"], cxm, cym - 0.4, 2.0, ETCH, font="arialbd")
            a.text(S["opn"], cxm, cym - 4.2, 1.7, ETCH, font="ocr")
            a.text(S["lot"], cxm, cym - 7.0, 1.7, ETCH, font="ocr")
            a.text(S["fab"], cxm, cym - 9.8, 1.25, ETCH, font="arialbd")
            a.text(S["made"], cxm, cym - 11.8, 1.25, ETCH, font="arialbd")
            # pin-1 triangle etched at the IHS corner (+x,-y -> left/bottom in the image)
            a.poly([(1.2, 1.2), (4.0, 1.2), (1.2, 4.0)], ETCH, z=0.5)
            a.text("© 2023", w - 4.0, 1.6, 1.0, ETCH, font="arialbd")
        else:
            datamatrix(a, 2.4, cym - 3.4, 6.8, 16, S["seed"] * 3, ETCH)
            tx = 12.0
            a.text(S["line1"], tx, cym + 6.2, 2.3, ETCH, font="arialbd", ax="LEFT", fit=w - tx - 1.5)
            a.text(S["spec"], tx, cym + 2.2, 2.1, ETCH, font="arialbd", ax="LEFT")
            a.text(S["fpo"], tx, cym - 1.8, 2.1, ETCH, font="ocr", ax="LEFT")
            a.text(S["year"] + "      (e4)", tx, cym - 5.8, 1.6, ETCH, font="arialbd", ax="LEFT")
            a.text("MALAY", tx, cym - 9.2, 1.4, ETCH, font="arialbd", ax="LEFT")
            # pin-1 triangle: the package corner (+x,-y). With text up = +x the corner is at the image's
            # bottom-left... the image's left is -y, its bottom is -x? (right = +y, up = +x) -> corner
            # (+x,-y) is at the image's top-left.
            a.poly([(1.2, h - 1.2), (4.0, h - 1.2), (1.2, h - 4.0)], ETCH, z=0.5)
    regions = {"top": uv, "side": at.swatch(pp.shade(NICKEL, 0.92))}
    at.render(pp.tex_path(name))
    pp.PREVIEW_TEX[name] = (0.85, 0.3)
    return name, regions


# ------------------------------------------------------------------ small parts

def v5_gap_caps(x0, x1, y0, y1):
    out = []
    n = max(1, int((x1 - x0 - 0.4) / 0.95))
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        for yy in (y0 + (y1 - y0) * 0.3, y0 + (y1 - y0) * 0.72):
            out.append((x, yy))
    return out


def l17_top_caps():
    out = []
    for i in range(10):
        x = -9.0 + i * 2.0
        out.append((x, -20.6, 0))
        out.append((x, 20.6, 0))
    for y in (-12.0, 12.0):
        for s in (-1, 1):
            out.append((s * 13.6, y - 1.0, 90))
            out.append((s * 13.6, y + 1.0, 90))
    return out


def l17_void_caps():
    out = []
    for i in range(4):
        for j in range(9):
            out.append((-2.7 + i * 1.8, -6.4 + j * 1.6))
    return out


# ------------------------------------------------------------------ build

def build(cid):
    S = SPECS[cid]
    sock = S["sock"]
    P = PKG[sock]
    c.reset()
    sub_name, sub_reg = substrate_texture(cid, sock, P)
    if sock == "V5":
        ihs_pts = ihs_outline_v5()
        ihs_w, ihs_h = 35.0, 38.0
        ihs_name, ihs_reg = ihs_texture(cid, S, sock, (ihs_w, ihs_h), False)
    else:
        ihs_pts = ihs_outline_l17()
        ihs_w, ihs_h = 36.6, 29.2  # text frame: along +y, up = +x
        ihs_name, ihs_reg = ihs_texture(cid, S, sock, (ihs_w, ihs_h), True)
    pp.PREVIEW_TEX[sub_name] = (0.0, 0.42)

    root = c.root(cid)
    k = pp.Kit(cid)
    sx, sy, T, top = P["sx"] * MM, P["sy"] * MM, P["t"] * MM, P["top"] * MM

    # substrate (one prism with keyed notches), top / land side / edge mapped into the atlas
    outline = [(x * MM, y * MM) for x, y in substrate_outline(P)]
    mapper = pp.MultiMap([
        pp.Planar(sub_reg["top"], (0, 0, T), (0, 0, 1), (0, 1, 0), (sx, sy)),
        pp.Planar(sub_reg["bottom"], (0, 0, 0), (0, 0, -1), (0, 1, 0), (sx, sy)),
        sub_reg["edge"]])
    pp.prism(k["tex_" + sub_name], [outline], 0.0, T, uv=mapper)

    # heat spreader
    ihs = [(x * MM, y * MM) for x, y in ihs_pts]
    if sock == "V5":
        up = (0, 1, 0)
        isz = (ihs_w * MM, ihs_h * MM)
    else:
        up = (1, 0, 0)
        isz = (ihs_w * MM, ihs_h * MM)
    imap = pp.MultiMap([pp.Planar(ihs_reg["top"], (0, 0, top), (0, 0, 1), up, isz, thresh=0.5), ihs_reg["side"]])
    pp.prism_bevel(k["tex_" + ihs_name], ihs, T, top, 0.00022, seg=1, uv=imap)
    # the die-attach sealant bead where the IHS meets the substrate
    # (a thin dark line just outside the IHS foot)

    # pin-1 gold triangle on the substrate top (+x, -y corner)
    g = k["gold"]
    cx, cy = sx * 0.5, -sy * 0.5
    tri = [Vector((cx - 0.0007, cy + 0.0007, T + 0.00002)), Vector((cx - 0.0042, cy + 0.0007, T + 0.00002)),
           Vector((cx - 0.0007, cy + 0.0042, T + 0.00002)), Vector((cx - 0.0007, cy + 0.0007, T + 0.00001)),
           Vector((cx - 0.0042, cy + 0.0007, T + 0.00001)), Vector((cx - 0.0007, cy + 0.0042, T + 0.00001))]
    g.add(tri, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])

    # LGA lands (gold octagons facing down, proud of the land side by 0.03 mm)
    zb = -0.00003
    for (x, y) in land_positions(P):
        x, y = x * MM, y * MM
        vs = [Vector((x + math.cos(math.radians(22.5 + 45 * i)) * 0.00033, y + math.sin(math.radians(22.5 + 45 * i)) * 0.00033, zb)) for i in range(8)]
        _flat_down(g, vs)

    # capacitors: in the IHS gaps (V5) / along the edges and in the land-side void (L17)
    if sock == "V5":
        for x0, x1, y0, y1 in ihs_gaps_v5():
            for (px, py) in v5_gap_caps(x0, x1, y0, y1):
                pp.smd_passive(k, px * MM, py * MM, T, 0.0010, 0.0005, 0.00045, ang=90, body="ceramic", term="solder")
    else:
        for (px, py, ang) in l17_top_caps():
            pp.smd_passive(k, px * MM, py * MM, T, 0.0010, 0.0005, 0.00045, ang=ang, body="ceramic", term="solder")
        for (px, py) in l17_void_caps():
            # mounted on the land side, hanging below the contact face
            _cap_down(k, px * MM, py * MM)

    k.finish(root)

    # anchors
    c.anchor("A_MARK_PIN1_0", (sx * 0.5 - 0.0007, -sy * 0.5 + 0.0007, T), (0.006, 0.006, 0.002), root,
             meta="corner=+x-y")
    c.anchor("A_PASTE_0", (0, 0, top), (0.03, 0.03, 0.002), root, meta=f"ihs={ihs_w * MM:.4f}x{ihs_h * MM:.4f}")
    c.anchor("A_HIT_0", (0, 0, top * 0.5), (sx, sy, top + 0.0004), root)

    c.join_by_tag(root, cid)
    c.export(root, cid)
    pp.report(root)
    return root


def _flat_down(g, vs):
    """Adds a flat polygon facing -z (Unity)."""
    bvs = [g.bm.verts.new(c.conv(v) - g.ofs_b) for v in vs]
    f = g.bm.faces.new(bvs)
    f.normal_update()
    if pp.unconv(f.normal).z > 0:
        f.normal_flip()
    g.count += 1


def _cap_down(k, x, y):
    zc = -0.00022
    pp.box(k["ceramic"], (x, y, zc), (0.0006, 0.0005, 0.00044))
    for s in (-1, 1):
        pp.box(k["solder"], (x + s * 0.00042, y, zc), (0.00022, 0.00052, 0.00046))


def previews(cid, root):
    pp.preview(root, cid, views=((25, 40), (-35, 65), (200, -45)), size=(960, 720), dist=0.13, zup=True)
    pp.preview(root, cid, views=((10, 55),), size=(960, 720), dist=0.07, start=3, zup=True)


def main(ids=None):
    ids = ids or list(SPECS)
    for cid in ids:
        root = build(cid)
        previews(cid, root)


if __name__ == "__main__":
    main(c.args() or None)
