"""
cat_cpus_server.py - the server CPUs of catalogue 10, on two new socket contracts (used by build_cat_cpus.py).

  Socket SP-V  (Arc Epoch, the EPYC 9004 analog): a 72 x 75.4 mm LGA package with a large two-tier IHS (a notched
               foot flange and a raised top), capacitor rows on the exposed substrate at both y ends, and a bright
               orange plastic carrier frame that clips over the substrate edge and slides into the socket's rail.
  Socket L46   (Tiron Platinum, the Xeon analog): a 61 x 105 mm LGA package with a long IHS that has four ears,
               wide capacitor fields at both y ends, a capacitor island in the land side, and a black carrier clip.

Frame (as the desktop CPUs): origin at the centre of the bottom (contact) face, +z up, pin 1 at the (+x, -y) corner;
the long side of the package along y. Anchors: A_MARK_PIN1_0, A_PASTE_0, A_HIT_0, and the carrier A_CARRIER_0 (a
moving piece in its installed pose, pivot on the substrate top at the package centre) with A_MARK_CARRIER_0@A_CARRIER_0 (its own pin-1
triangle). The contract is written up in docs/reports/cat_cpus.md.
"""
import math
import random

import dct_common as c
import parts_c as P
import parts_pcb as pp
import build_cpu
from mathutils import Vector

MM = 0.001
NICKEL = build_cpu.NICKEL
ETCH = build_cpu.ETCH

# Package geometry in millimetres. ihs: foot flange half sizes, corner radius, notches/ears; plate: the raised top.
PKG = {
    "SP-V": dict(sx=72.0, sy=75.4, t=1.6, flange=1.0, top=6.4, pitch=0.94, void=None, sub="#2c553b",
                 ihs=dict(bx=31.5, by=33.2, r=2.6, notch=dict(ys=(-21.0, 21.0), depth=1.6, length=6.0)),
                 plate=(58.0, 63.6, 1.8), carrier="#f26b1d", carrier_text="#ffd2b0", label="SP-V", mount="rail=+y"),
    "L46": dict(sx=61.0, sy=105.0, t=1.6, flange=1.1, top=6.6, pitch=0.95, void=(10.0, 34.0), sub="#2f4b36",
                ihs=dict(bx=25.5, by=41.0, r=2.2, ears=dict(ys=(-31.0, 31.0), out=3.0, length=8.0)),
                plate=(48.0, 79.0, 1.6), carrier="#26282b", carrier_text="#c9ccd0", label="L46", mount="mount=heatsink"),
}

SPECS = {
    "cpu_epoch_9124": dict(sock="SP-V", model="9124", cores="16-CORE", opn="100-000000802", lot="2CK8149D10023",
                           made="MADE IN MALAYSIA", copy="© 2022", seed=124),
    "cpu_epoch_9354": dict(sock="SP-V", model="9354", cores="32-CORE", opn="100-000000798", lot="2CN4417F20061",
                           made="MADE IN MALAYSIA", copy="© 2022", seed=354),
    "cpu_epoch_9654": dict(sock="SP-V", model="9654", cores="96-CORE", opn="100-000000789", lot="2CQ7350G40188",
                           made="MADE IN CHINA", copy="© 2022", seed=654),
    "cpu_tiron_plat_8480": dict(sock="L46", line1="TIRON® PLATINUM 8480", spec="SRM7H 2.00GHZ", fpo="X2360A51",
                                year="©'22", cores="56C", seed=848),
}


# ------------------------------------------------------------------ outlines (mm)

def ihs_outline(P_):
    """The IHS foot flange: SP-V a rounded rectangle with two notches per x side (the carrier clips sit in them);
    L46 a rounded rectangle with four ears on the x sides (the carrier clip fingers press on them)."""
    I = P_["ihs"]
    bx, by = I["bx"], I["by"]
    pts = [(-bx, -by), (bx, -by)]
    if "notch" in I:
        N = I["notch"]
        d, L = N["depth"], N["length"]
        for y in N["ys"]:
            pts += [(bx, y - L / 2), (bx - d, y - L / 2), (bx - d, y + L / 2), (bx, y + L / 2)]
        pts += [(bx, by), (-bx, by)]
        for y in reversed(N["ys"]):
            pts += [(-bx, y + L / 2), (-bx + d, y + L / 2), (-bx + d, y - L / 2), (-bx, y - L / 2)]
    else:
        E = I["ears"]
        o, L = E["out"], E["length"]
        for y in E["ys"]:
            pts += [(bx, y - L / 2 - 1.2), (bx + o, y - L / 2), (bx + o, y + L / 2), (bx, y + L / 2 + 1.2)]
        pts += [(bx, by), (-bx, by)]
        for y in reversed(E["ys"]):
            pts += [(-bx, y + L / 2 + 1.2), (-bx - o, y + L / 2), (-bx - o, y - L / 2), (-bx, y - L / 2 - 1.2)]
    rad = []
    for p in pts:
        corner = abs(abs(p[0]) - bx) < 1e-6 and abs(abs(p[1]) - by) < 1e-6
        rad.append(I["r"] if corner else 0.5)
    return build_cpu.fillet_poly(pts, rad, 3)


def top_caps(sock, P_):
    """Capacitors on the substrate top (x, y, angle) in mm: rows across both exposed y ends."""
    out = []
    hy = P_["sy"] / 2
    if sock == "SP-V":
        rows, xmax, step = (hy - 3.3, hy - 2.0), 29.0, 1.55
    else:
        rows, xmax, step = (hy - 9.6, hy - 7.6, hy - 5.6, hy - 3.6), 25.0, 1.5
    n = int(2 * xmax / step)
    for yy in rows:
        for s in (-1, 1):
            for i in range(n + 1):
                x = -xmax + i * step
                if s < 0 and x > xmax - 5.5 and yy > hy - 6.0:
                    continue  # keep the pin-1 corner clear
                out.append((x, s * yy, 0))
    if sock == "L46":
        # resistor/cap clusters beside the ears
        for s in (-1, 1):
            for y in (-14.0, -8.0, 8.0, 14.0):
                for k in range(3):
                    out.append((s * 27.4, y + (k - 1) * 1.4, 90))
    return out


def void_caps(P_):
    if not P_["void"]:
        return []
    vx, vy = P_["void"]
    out = []
    nx, ny = int((vx - 1.6) / 1.8), int((vy - 1.6) / 1.6)
    for i in range(nx):
        for j in range(ny):
            out.append((-(nx - 1) * 0.9 + i * 1.8, -(ny - 1) * 0.8 + j * 1.6))
    return out


# ------------------------------------------------------------------ textures

def substrate_texture(sock, P_):
    """Top (one panel) and land side (another) of the substrate, shared by every CPU on the socket."""
    name = f"cpu_{sock.replace('-', '').lower()}_pcb"
    sx, sy = P_["sx"], P_["sy"]
    green = P_["sub"]
    darker, lighter, gold, ink = pp.shade(green, 0.82), pp.shade(green, 1.18), "#c9a34e", "#e0ddd0"
    at = pp.Atlas(2048, 2048, bg=green)
    ppm = 1000.0 / max(sx, sy)
    rnd = random.Random(61 if sock == "SP-V" else 62)
    regions = {}
    r, uv, ctx = at.panel(sx, sy, ppm, bg=green)
    regions["top"] = uv
    with ctx as a:  # looking down: u = sx/2 - x, v = y + sy/2
        for k in range(420):
            x0, y0 = rnd.uniform(0.5, sx - 0.5), rnd.uniform(0.5, sy - 0.5)
            pts = [(x0, y0)]
            for s in range(rnd.randint(2, 5)):
                dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1)])
                L = rnd.uniform(0.8, 6.0)
                x0, y0 = min(sx - 0.4, max(0.4, x0 + dx * L)), min(sy - 0.4, max(0.4, y0 + dy * L))
                pts.append((x0, y0))
            a.line(pts, 0.1, lighter, z=0.2)
        for k in range(900):
            a.circle(rnd.uniform(0.6, sx - 0.6), rnd.uniform(0.6, sy - 0.6), 0.13, darker, z=0.25, seg=8)
        for (cx, cy, ang) in top_caps(sock, P_):
            u, v = sx / 2 - cx, cy + sy / 2
            for s in (-1, 1):
                if ang == 0:
                    a.rect(u + s * 0.42 - 0.2, v - 0.3, u + s * 0.42 + 0.2, v + 0.3, gold, z=0.4)
                else:
                    a.rect(u - 0.3, v + s * 0.42 - 0.2, u + 0.3, v + s * 0.42 + 0.2, gold, z=0.4)
        # pin-1: the gold triangle is geometry, a white outline frames it (corner at u 2.0, v 2.0)
        a.poly([(1.5, 1.5), (6.4, 1.5), (1.5, 6.4)], "#e8e4d8", z=0.3)
        a.poly([(2.0, 2.0), (5.5, 2.0), (2.0, 5.5)], green, z=0.31)
        a.text(P_["label"], sx - 4.0, 4.0, 1.4, ink, font="narrowbd")
        a.text("Y2241P  A1" if sock == "SP-V" else "J3P-2B 2238", sx / 2, sy - 1.9, 0.9, ink, font="narrowbd")
        build_cpu.datamatrix(a, sx - 6.5, sy - 6.3, 3.4, 14, 61 if sock == "SP-V" else 62, "#e8e4d8")
    r, uv, ctx = at.panel(sx, sy, ppm, bg=green)
    regions["bottom"] = uv
    with ctx as a:  # looking up: u = x + sx/2
        for (x, y) in build_cpu.land_positions(P_):
            u, v = x + sx / 2, y + sy / 2
            a.circle(u, v, 0.42, darker, z=0.2, seg=10)
            a.circle(u, v, 0.32, gold, z=0.3, seg=10)
        a.poly([(sx - 0.8, 0.8), (sx - 5.6, 0.8), (sx - 0.8, 5.6)], gold, z=0.4)
        if P_["void"]:
            vx, vy = P_["void"]
            a.rrect(sx / 2, sy / 2, vx - 0.6, vy - 0.6, 0.6, "#1a1c1c", z=0.2)
            for (x, y) in void_caps(P_):
                u, v = x + sx / 2, y + sy / 2
                for s in (-1, 1):
                    a.rect(u + s * 0.45 - 0.22, v - 0.32, u + s * 0.45 + 0.22, v + 0.32, gold, z=0.4)
        a.text(P_["label"], 3.2, sy - 2.4, 1.2, ink, font="narrowbd")
    regions["edge"] = at.swatch("#5f6650")
    at.render(pp.tex_path(name))
    pp.PREVIEW_TEX[name] = (0.0, 0.42)
    return name, regions


def ihs_texture(cid, S, sock, w, h):
    """Laser markings on the raised IHS top, a w x h mm panel. SP-V: image up = +y (left = +x);
    L46: image up = +x (right = +y), so the text runs along the long side."""
    name = "cpu_ihs_" + cid.split("_")[-1]
    at = pp.Atlas(1024, 1024, bg=NICKEL)
    ppm = 1000.0 / max(w, h)
    r, uv, ctx = at.panel(w, h, ppm, bg=NICKEL)
    rnd = random.Random(S["seed"])
    with ctx as a:
        for k in range(110):  # lapping marks
            rr = rnd.uniform(8, 110)
            cx, cy = rnd.uniform(-60, w + 60), rnd.uniform(-60, h + 60)
            col = pp.shade(NICKEL, rnd.uniform(0.98, 1.015))
            a0 = rnd.uniform(0, 6.28)
            a.line([(cx + math.cos(a0 + i * 0.04) * rr, cy + math.sin(a0 + i * 0.04) * rr) for i in range(48)],
                   rnd.uniform(0.2, 0.8), col, z=0.1, joins=False)
        cxm, cym = w / 2, h / 2
        if sock == "SP-V":
            # the ARC EPOCH logo top left: an arc over "ARC", then "EPOCH" with a wide letter spacing
            lx, ly = 13.0, h - 9.0
            a.line([(lx + 7.5 * math.cos(math.radians(t)), ly - 2.8 + 7.5 * math.sin(math.radians(t)))
                    for t in range(28, 153, 5)], 1.0, ETCH, z=0.5)
            a.text("ARC", lx, ly - 1.0, 5.2, ETCH, font="agency")
            a.text("EPOCH", lx + 11.0, ly - 1.0, 5.2, ETCH, font="agency", ax="LEFT", space=1.25)
            a.text(S["model"], cxm, cym + 6.0, 9.0, ETCH, font="arialbd")
            a.text(S["cores"], cxm, cym - 1.2, 2.8, ETCH, font="arialbd")
            a.text(S["opn"], cxm, cym - 7.6, 2.5, ETCH, font="ocr")
            a.text(S["lot"], cxm, cym - 11.6, 2.5, ETCH, font="ocr")
            a.text("DIFFUSED IN TAIWAN", cxm, cym - 15.8, 1.9, ETCH, font="arialbd")
            a.text(S["made"], cxm, cym - 18.8, 1.9, ETCH, font="arialbd")
            build_cpu.datamatrix(a, w - 13.5, 3.0, 9.0, 18, S["seed"] * 5 + 3, ETCH)
            a.poly([(1.6, 1.6), (6.0, 1.6), (1.6, 6.0)], ETCH, z=0.5)  # pin 1: image bottom-left = (+x, -y)
            a.text(S["copy"], 12.0, 2.6, 1.4, ETCH, font="arialbd")
        else:
            # long panel, image right = +y, up = +x: pin 1 (+x, -y) is at the image's top-left
            build_cpu.datamatrix(a, 5.0, cym - 12.5, 16.0, 20, S["seed"] * 5 + 3, ETCH)
            tx = 27.0
            a.text("tiron", tx, cym + 14.5, 8.0, ETCH, font="arialbd", ax="LEFT")
            a.text(S["line1"], tx, cym + 5.8, 4.4, ETCH, font="arialbd", ax="LEFT", fit=w - tx - 4.0)
            a.text(S["spec"], tx, cym - 0.2, 3.9, ETCH, font="arialbd", ax="LEFT")
            a.text(S["fpo"], tx, cym - 6.0, 3.9, ETCH, font="ocr", ax="LEFT")
            a.text(S["year"] + "   " + S["cores"] + "   (e4)", tx, cym - 11.6, 2.9, ETCH, font="arialbd", ax="LEFT")
            a.text("MALAY", tx, cym - 16.4, 2.5, ETCH, font="arialbd", ax="LEFT")
            a.poly([(1.6, h - 1.6), (6.0, h - 1.6), (1.6, h - 6.0)], ETCH, z=0.5)
    regions = {"top": uv, "side": at.swatch(pp.shade(NICKEL, 0.92))}
    at.render(pp.tex_path(name))
    pp.PREVIEW_TEX[name] = (0.85, 0.3)
    return name, regions


def carrier_texture(sock, P_):
    """The carrier plastic: a flat colour swatch, a darker one for the rails, and the moulded legend on the grip."""
    name = f"cpu_{sock.replace('-', '').lower()}_carrier"
    col, ink = P_["carrier"], P_["carrier_text"]
    at = pp.Atlas(512, 512, bg=col)
    regs = {"body": at.swatch(col), "rail": at.swatch(pp.shade(col, 0.85))}
    gw, gh = grip_size(P_)
    r, uv, ctx = at.panel(gw, gh, 480.0 / gw, bg=col)
    regs["grip"] = uv
    with ctx as a:  # the grip top, image up = +y (read from the -y end that is held), left = +x
        a.text(P_["label"], gw * 0.30, gh * 0.55, gh * 0.38, ink, font="arialbd")
        if sock == "SP-V":
            ax0 = gw * 0.62  # an arrow pointing into the rail (+y = the image's top)
            a.poly([(ax0, gh * 0.66), (ax0 + gh * 0.24, gh * 0.66), (ax0 + gh * 0.12, gh * 0.86)], ink, z=0.5)
            a.rect(ax0 + gh * 0.08, gh * 0.22, ax0 + gh * 0.16, gh * 0.67, ink, z=0.5)
            a.text("PUSH", gw * 0.86, gh * 0.55, gh * 0.22, ink, font="narrowbd")
        else:
            a.text("HEATSINK SIDE UP", gw * 0.74, gh * 0.55, gh * 0.18, ink, font="narrowbd")
        a.text("CARRIER A1" if sock == "SP-V" else "CLIP E1A", gw * 0.30, gh * 0.18, gh * 0.14, ink, font="narrowbd")
    r, uv, ctx = at.panel(8.0, 8.0, 12.0, bg=col)
    regs["tri"] = uv
    with ctx as a:
        a.poly([(1.0, 1.0), (7.0, 1.0), (1.0, 7.0)], ink, z=0.5)
    at.render(pp.tex_path(name))
    pp.PREVIEW_TEX[name] = (0.0, 0.55)
    return name, regs


def grip_size(P_):
    return (34.0, 8.0) if P_["label"] == "SP-V" else (30.0, 7.0)


# ------------------------------------------------------------------ build

def lands(g, P_):
    """LGA lands: gold hexagons facing down, 0.03 mm proud of the land side."""
    zb = -0.00003
    for (x, y) in build_cpu.land_positions(P_):
        x, y = x * MM, y * MM
        build_cpu._flat_down(g, [Vector((x + math.cos(math.radians(60 * i)) * 0.00032,
                                         y + math.sin(math.radians(60 * i)) * 0.00032, zb)) for i in range(6)])


def carrier(root, sock, P_, T):
    """The carrier frame, a moving piece on A_CARRIER_0 (pivot on the substrate top centre, installed pose)."""
    name, R = carrier_texture(sock, P_)
    sx, sy = P_["sx"], P_["sy"]
    hx, hy = sx / 2, sy / 2
    wall, lip = 2.6, 1.3
    t_mm = T / MM
    top = t_mm + 1.0
    gw, gh = grip_size(P_)
    ox, oy = hx + wall, hy + wall
    size = ((ox + 2.2) * 2 * MM, (oy + gh) * 2 * MM, (top + 0.7 - 0.25) * MM)
    # the anchor (and pivot) sits on the substrate top at the package centre, where the lip seats
    an = c.anchor("A_CARRIER_0", (0, 0, T), size, root, meta=f"socket={sock},pose=installed,clip=+z,{P_['mount']},"
                                                             f"color={P_['carrier']}")
    g = pp.Geo("tex_" + name, origin=(0, 0, T))
    m = lambda pts: [(x * MM, y * MM) for x, y in pts]  # noqa: E731
    outer = pp.rounded_rect(0, 0, ox * 2, oy * 2, 1.6, 4)
    # the wall around the substrate edge, then the lip over the substrate top
    pp.prism(g, [m(outer), m(pp.rounded_rect(0, 0, sx + 0.3, sy + 0.3, 0.7, 2))], 0.25 * MM, T, uv=R["body"])
    pp.prism(g, [m(outer), m(pp.rounded_rect(0, 0, sx - 2 * lip, sy - 2 * lip, 0.9, 3))], T, top * MM, uv=R["body"])
    # rails on both x sides: SP-V slides them into the socket's rail frame; on L46 they are the heatsink latches
    for s in (-1, 1):
        pp.box(g, (s * (ox + 1.1) * MM, 0, (t_mm + 0.25) * MM), (2.2 * MM, (sy - 14.0) * MM, 0.9 * MM),
               bevel=0.15 * MM, uv=R["rail"])
    # clip fingers: SP-V into the IHS flange notches, L46 over the IHS ears
    I = P_["ihs"]
    if "notch" in I:
        N = I["notch"]
        x0, x1, ys, zt = I["bx"] - N["depth"] + 0.3, hx - lip + 0.2, N["ys"], t_mm + P_["flange"] + 0.5
        fl = N["length"] - 0.8
    else:
        E = I["ears"]
        x0, x1, ys, zt = I["bx"] + 0.4, hx - lip + 0.2, E["ys"], t_mm + P_["flange"] + 0.6
        fl = E["length"] - 1.6
    for s in (-1, 1):
        for y in ys:
            xa, xb = s * x0, s * x1
            pp.box(g, ((xa + xb) / 2 * MM, y * MM, (t_mm + zt) / 2 * MM), (abs(xb - xa) * MM, fl * MM, (zt - t_mm) * MM),
                   bevel=0.2 * MM, uv=R["body"])
            pp.box(g, ((xa + xb) / 2 * MM, y * MM, (zt - 0.3) * MM), ((abs(xb - xa) + 0.6) * MM, (fl + 1.0) * MM, 0.6 * MM),
                   bevel=0.2 * MM, uv=R["body"])
    # the grip tab at -y (the end held while sliding the carrier in), with a finger slot and the moulded legend
    gy0, gy1 = -oy - gh, -oy + 0.6
    tab = pp.rounded_rect(0, (gy0 + gy1) / 2, gw, gy1 - gy0, 1.6, 4)
    slot = pp.rounded_rect(0, gy0 + 2.4, gw * 0.55, 1.8, 0.85, 3)
    gm = pp.MultiMap([pp.Planar(R["grip"], (0, (gy0 + gh / 2) * MM, top * MM), (0, 0, 1), (0, 1, 0),
                                (gw * MM, gh * MM), thresh=0.9), R["body"]])
    pp.prism(g, [m(tab), m(list(reversed(slot)))], 0.25 * MM, top * MM, uv=gm)
    # hooks at the +y end (SP-V: they catch the rail frame's stop)
    for s in (-1, 1):
        pp.box(g, (s * 20.0 * MM, (oy + 1.0) * MM, (t_mm + 0.2) * MM), (6.0 * MM, 2.0 * MM, 1.6 * MM), bevel=0.2 * MM,
               uv=R["rail"])
    # the carrier's own pin-1 triangle at the (+x, -y) corner of the lip
    cx, cy = (hx + wall * 0.15), -(hy + wall * 0.15)
    pp.quad(g, ((cx - 2.4) * MM, (cy + 2.4) * MM, top * MM + 0.00002), (4.2 * MM, 4.2 * MM), (0, 0, 1), (0, 1, 0),
            region=R["tri"])
    g.obj("carrier", an, smooth=30)
    c.anchor("A_MARK_CARRIER_0", ((cx - 0.6) * MM, (cy + 0.6) * MM, top * MM), (0.005, 0.005, 0.002), an,
             meta="corner=+x-y")
    return an


def build(cid):
    S = SPECS[cid]
    sock = S["sock"]
    P_ = PKG[sock]
    c.reset()
    sub_name, sub_reg = substrate_texture(sock, P_)
    pw, ph, prr = P_["plate"]
    if sock == "SP-V":
        tw, th, up = pw, ph, (0, 1, 0)
    else:
        tw, th, up = ph, pw, (1, 0, 0)
    ihs_name, ihs_reg = ihs_texture(cid, S, sock, tw, th)

    root = c.root(cid)
    k = pp.Kit(cid)
    sx, sy, T, top = P_["sx"] * MM, P_["sy"] * MM, P_["t"] * MM, P_["top"] * MM
    zf = T + P_["flange"] * MM

    # substrate: a prism with planar maps for the top and the land side
    outline = [(x * MM, y * MM) for x, y in pp.rounded_rect(0, 0, P_["sx"], P_["sy"], 0.8, 3)]
    mapper = pp.MultiMap([
        pp.Planar(sub_reg["top"], (0, 0, T), (0, 0, 1), (0, 1, 0), (sx, sy)),
        pp.Planar(sub_reg["bottom"], (0, 0, 0), (0, 0, -1), (0, 1, 0), (sx, sy)),
        sub_reg["edge"]])
    pp.prism(k["tex_" + sub_name], [outline], 0.0, T, uv=mapper)

    # IHS: the foot flange (with notches or ears), then the raised top with the markings
    side = ihs_reg["side"]
    pp.prism_bevel(k["tex_" + ihs_name], [(x * MM, y * MM) for x, y in ihs_outline(P_)], T, zf, 0.0002, seg=1, uv=side)
    plate = [(x * MM, y * MM) for x, y in pp.rounded_rect(0, 0, pw, ph, prr, 4)]
    imap = pp.MultiMap([pp.Planar(ihs_reg["top"], (0, 0, top), (0, 0, 1), up, (tw * MM, th * MM), thresh=0.5), side])
    pp.prism_bevel(k["tex_" + ihs_name], plate, zf - 0.0001, top, 0.00035, seg=2, uv=imap)

    # pin-1 gold triangle on the substrate top (+x, -y), inset clear of the carrier lip
    g = k["gold"]
    cx, cy = sx * 0.5 - 0.0020, -sy * 0.5 + 0.0020
    zt = T + 0.00002
    tri = [Vector((cx, cy, zt)), Vector((cx - 0.0035, cy, zt)), Vector((cx, cy + 0.0035, zt)),
           Vector((cx, cy, T + 0.00001)), Vector((cx - 0.0035, cy, T + 0.00001)), Vector((cx, cy + 0.0035, T + 0.00001))]
    g.add(tri, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
    lands(g, P_)

    for (px, py, ang) in top_caps(sock, P_):
        pp.smd_passive(k, px * MM, py * MM, T, 0.0010, 0.0005, 0.00045, ang=ang, body="ceramic", term="solder")
    for (px, py) in void_caps(P_):
        build_cpu._cap_down(k, px * MM, py * MM)
    k.finish(root)

    c.anchor("A_MARK_PIN1_0", (cx, cy, T), (0.006, 0.006, 0.002), root, meta="corner=+x-y")
    c.anchor("A_PASTE_0", (0, 0, top), (pw * MM * 0.8, ph * MM * 0.8, 0.002), root,
             meta=f"ihs={pw * MM:.4f}x{ph * MM:.4f}")
    c.anchor("A_HIT_0", (0, 0, top * 0.5), (sx, sy, top + 0.0004), root)
    cap_anchor(root, sock)
    carrier(root, sock, P_, T)

    c.join_by_tag(root, cid)
    c.export(root, cid)
    pp.report(root)
    return root


# ------------------------------------------------------------------ the contact cover (unboxing)
# A clear plastic cover over the land side, a separate cap model (cap_cpu_spv / cap_cpu_l46) that sits on the
# package's A_CAP_PADS_0. The anchor is on the contact face (just below the 0.03 mm proud lands) facing -z, so the
# cap's local +Z is the pull-off direction; the anchor's local +x is the package's -x (a 180 degree turn about y).

CAPS = {"SP-V": "cap_cpu_spv", "L46": "cap_cpu_l46"}
CAP_Z = -0.00004   # the cover's contact face in the package frame
CAP_GROW = 1.0     # mm the cover plate overhangs the substrate on each side (below the carrier wall)
CAP_TAB = 6.0      # mm the pull tab sticks out at the -y end


def cap_size(sock):
    P_ = PKG[sock]
    return (P_["sx"] + 2 * CAP_GROW) * MM, (P_["sy"] + 2 * CAP_GROW) * MM, 0.0016


def cap_anchor(root, sock):
    """A_CAP_PADS_0 on the package (also used by cat_cpus_unbox.py to retrofit the committed FBXs)."""
    w, h, t = cap_size(sock)
    return c.anchor("A_CAP_PADS_0", (0, 0, CAP_Z), (w, h, t), root, forward=(0, 0, -1), up=(0, 1, 0),
                    meta=f"model={CAPS[sock]},remove=-z,blocks=install")


def build_cap(cap_id):
    """The cover in its own frame: origin at the contact face centre, +z = pull-off (away from the lands)."""
    sock = [k for k, v in CAPS.items() if v == cap_id][0]
    c.reset()
    root = c.root(cap_id)
    k = pp.Kit(cap_id)
    g = k["glass"]
    w, h, t = cap_size(sock)
    wm, hm = w / MM, h / MM
    m = lambda pts: [(x * MM, y * MM) for x, y in pts]  # noqa: E731
    # the plate (0.7 mm) with a 1.2 mm rim standing 0.9 mm further out, and two stiffening ribs along y
    pp.prism_bevel(g, m(pp.rounded_rect(0, 0, wm, hm, 1.6, 4)), 0.0, 0.0007, 0.0002, seg=1)
    outer = pp.rounded_rect(0, 0, wm, hm, 1.6, 4)
    inner = pp.rounded_rect(0, 0, wm - 2.4, hm - 2.4, 0.9, 4)
    pp.prism(g, [m(outer), m(list(reversed(inner)))], 0.0007, t)
    for xr in (-wm / 6, wm / 6):
        pp.box(g, (xr * MM, 0, 0.00105), (0.0012, (hm - 3.0) * MM, 0.0007), bevel=0.0002)
    # the pull tab at -y, with a grip ridge
    ty0, ty1 = -hm / 2 - CAP_TAB, -hm / 2 + 1.0
    pp.prism_bevel(g, m(pp.rounded_rect(0, (ty0 + ty1) / 2, 16.0, ty1 - ty0, 2.0, 4)), 0.0, 0.0007, 0.0002, seg=1)
    pp.box(g, (0, (ty0 + 1.6) * MM, 0.001), (0.012, 0.0008, 0.0006), bevel=0.0002)
    # a moulded pin-1 triangle on the rim at the package's (+x, -y) corner = this frame's (-x, -y)
    cx, cy = -wm / 2 + 0.6, -hm / 2 + 0.6
    tri = [(cx, cy), (cx + 4.0, cy), (cx, cy + 4.0)]
    pp.prism(g, [m(tri)], t, t + 0.0003)
    k.finish(root)
    c.anchor("A_HIT_0", (0, 0, t / 2), (w, h, t), root,
             meta="remove=+z,travel=0.030,blocks=install")
    c.join_by_tag(root, cap_id)
    c.export(root, cap_id)
    pp.report(root)
    return root


def build_cap_and_preview(cap_id, preview=True):
    root = build_cap(cap_id)
    sock = [k for k, v in CAPS.items() if v == cap_id][0]
    P.write_report(root, cap_id, f"frame: origin at the contact face centre (on the {sock} package's A_CAP_PADS_0), "
                                 "+z = pull-off direction; local +x = the package's -x")
    if preview:
        pp.preview(root, cap_id, views=((25, 40), (200, -45)), size=(960, 720), dist=0.22, zup=True)
    return root


def previews(cid, root):
    d = 0.24 if PKG[SPECS[cid]["sock"]]["sy"] < 90 else 0.30
    pp.preview(root, cid, views=((25, 40), (-35, 65), (200, -45)), size=(960, 720), dist=d, zup=True)
    pp.preview(root, cid, views=((10, 55),), size=(960, 720), dist=d * 0.5, start=3, zup=True)


def build_and_preview(cid, preview=True):
    root = build(cid)
    sock = SPECS[cid]["sock"]
    P.write_report(root, cid, f"frame: Socket {sock} (new contract): origin at the contact face centre, +z up, "
                              "pin 1 at (+x, -y); the carrier is a moving piece on A_CARRIER_0")
    if preview:
        previews(cid, root)
    return root
