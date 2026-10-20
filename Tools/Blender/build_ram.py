"""
RAM models: ram_ddr5_16 (Volt DDR5-6000 16 GB with an RGB diffuser) and ram_ddr4_8 (Volt DDR4-3200 8 GB,
low-profile red heat spreader).

Frame (REALISM.md section 2, as today's game): origin at the bottom-edge centre of the stick, thickness
along x, the 133.35 mm length along y, the height along z. The label sticker is on the +x side.
The key notch offset (along y from the centre) is in A_NOTCH_0's meta; the board slots carry the same value.

Run: blender -b --factory-startup -P Tools/Blender/build_ram.py -- [ids...]
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
LEN, PCB_H, PCB_T = 133.35, 31.25, 1.27

# Key notch centre along y (mm from the stick centre). DDR4 and DDR5 differ, so neither fits the other's slot.
NOTCH = {"DDR5": -3.9, "DDR4": 4.3}

SPECS = {
    "ram_ddr5_16": dict(mem="DDR5", rgb=True, series="FLUX RGB", top=38.0, sp_x=(2.25, 3.45), pcb="#16181b",
                        spread="#30333a", band="#121316", ink="#d9dce2", accent="#8a93a6",
                        label=["VOLT FLUX RGB  DDR5", "16GB  6000MT/s  CL30-38-38-96", "1.35V   VDF5-16G60C30R"],
                        sn="2441A0731655"),
    "ram_ddr4_8": dict(mem="DDR4", rgb=False, series="STRIKE", top=33.6, sp_x=(2.05, 3.2), pcb="#16181b",
                       spread="#a3161c", band="#141414", ink="#e23a3f", accent="#e8e8e8",
                       label=["VOLT STRIKE  DDR4", "8GB  3200MHz  CL16-18-18-36", "1.35V   VDS4-8G32C16"],
                       sn="2338B0219874"),
}


def pcb_outline(notch_y):
    """Side outline of the DIMM PCB in (y, z) mm: chamfered bottom corners, the key notch and the latch
    notches on both ends."""
    h = LEN / 2
    nw, nd = 1.6, 3.6
    pts = []
    pts += [(-h + 1.2, 0.0)]
    # key notch (U shape with a round top)
    pts += [(notch_y - nw / 2, 0.0), (notch_y - nw / 2, nd - nw / 2)]
    for k in range(1, 6):
        a = math.pi - math.pi * k / 6
        pts.append((notch_y + math.cos(a) * nw / 2, nd - nw / 2 + math.sin(a) * nw / 2))
    pts += [(notch_y + nw / 2, nd - nw / 2), (notch_y + nw / 2, 0.0)]
    pts += [(h - 1.2, 0.0), (h, 1.2)]
    # latch notch on the +y end
    zc, r = 12.8, 1.25
    pts += [(h, zc - r)] + [(h - math.sin(math.pi * k / 8) * r, zc - math.cos(math.pi * k / 8) * r) for k in range(1, 8)] + [(h, zc + r)]
    pts += [(h, PCB_H), (-h, PCB_H)]
    pts += [(-h, zc + r)] + [(-h + math.sin(math.pi * k / 8) * r, zc + math.cos(math.pi * k / 8) * r) for k in range(1, 8)] + [(-h, zc - r)]
    pts += [(-h, 1.2)]
    return pts


def finger_positions(notch_y):
    out = []
    y = -LEN / 2 + 3.0
    while y < LEN / 2 - 3.0:
        if abs(y - notch_y) > 1.25:
            out.append(y)
        y += 0.85
    return out


def textures(rid, S, notch_y):
    at = pp.Atlas(2048, 1024, bg=S["spread"])
    rnd = random.Random(hash(rid) & 0xffff)
    reg = {}
    top = S["top"]
    span_y = 129.2
    span_z = top - 7.0
    # ---- heat spreader face (y across, z up); u runs along the face's own right, so draw "as seen"
    r, uv, ctx = at.panel(span_y, span_z, 15.0, bg=S["spread"])
    reg["spread"] = uv
    with ctx as a:
        # brushed streaks
        for k in range(260):
            z = rnd.uniform(0, span_z)
            x0 = rnd.uniform(-20, span_y)
            col = pp.shade(S["spread"], rnd.uniform(0.86, 1.14))
            a.line([(x0, z), (x0 + rnd.uniform(15, 70), z)], rnd.uniform(0.05, 0.16), col, z=0.1, joins=False)
        # the dark band matches the raised relief panel (diagonal edge)
        band = relief_outline(span_y, span_z)
        a.poly(band, S["band"], z=0.2)
        for k in range(120):
            z = rnd.uniform(0, span_z * 0.55)
            x0 = rnd.uniform(-20, span_y)
            a.line([(x0, z), (x0 + rnd.uniform(10, 40), z)], 0.06, pp.shade(S["band"], 1.35), z=0.25, joins=False)
        # accent line along the band edge
        a.line([(0.0, span_z * 0.52), (span_y * 0.40, span_z * 0.52), (span_y * 0.40 + 6.0, span_z * 0.30), (span_y, span_z * 0.30)],
               0.45, S["accent"], z=0.3)
        # logo and series
        a.text("VOLT", 8.0, span_z * 0.26, 8.5, S["ink"], font="agency", ax="LEFT", space=1.05)
        a.text(S["series"], 36.0, span_z * 0.22, 3.2, S["ink"], font="agencyr", ax="LEFT")
        a.text(S["mem"], span_y - 8.0, span_z * 0.14, 3.0, S["ink"], font="agency", ax="RIGHT")
        if not S["rgb"]:
            # LPX-style chevrons near the top
            for i in range(6):
                x = span_y * 0.58 + i * 3.2
                a.line([(x, span_z * 0.66), (x + 1.4, span_z * 0.80), (x, span_z * 0.94)], 0.6, S["band"], z=0.3)
    # ---- PCB side (y across, z up from the bottom edge)
    r, uv, ctx = at.panel(LEN, PCB_H, 7.5, bg=S["pcb"])
    reg["pcb"] = uv
    with ctx as a:
        lighter = pp.shade(S["pcb"], 1.5)
        for k in range(90):
            x0 = rnd.uniform(2, LEN - 2)
            z0 = rnd.uniform(4.0, 7.0)
            pts = [(x0, z0), (x0, z0 + rnd.uniform(1, 4)), (x0 + rnd.choice([-1, 1]) * rnd.uniform(1, 4), PCB_H)]
            a.line(pts, 0.12, lighter, z=0.1)
        for k in range(160):
            a.circle(rnd.uniform(2, LEN - 2), rnd.uniform(4.2, 7.5), 0.18, pp.shade(S["pcb"], 1.9), z=0.15, seg=8)
        for y in finger_positions(notch_y):
            u = y + LEN / 2
            a.rect(u - 0.3, 0.0, u + 0.3, 3.4, "#c9a24c", z=0.2)
        a.text("288P", 4.0, 5.2, 0.9, "#d8d8d0", font="narrowbd", ax="LEFT")
    # ---- product sticker
    r, uv, ctx = at.panel(46.0, 13.0, 20.0, bg="#e9eaec")
    reg["label"] = uv
    with ctx as a:
        a.rect(0, 11.2, 46, 13.0, "#1a1b1e", z=0.1)
        a.text("VOLT", 1.2, 12.1, 1.5, "#f2f2f2", font="agency", ax="LEFT")
        a.text("MEMORY", 7.2, 12.1, 1.1, "#f2f2f2", font="arialbd", ax="LEFT")
        for i, line in enumerate(S["label"]):
            a.text(line, 1.2, 9.8 - i * 1.9, 1.35 if i == 0 else 1.15, "#141414", font="arialbd" if i == 0 else "narrowbd", ax="LEFT", fit=30)
        # barcode
        bx = 1.2
        while bx < 30.0:
            w = rnd.choice([0.12, 0.12, 0.24, 0.36])
            a.rect(bx, 0.9, bx + w, 3.6, "#111111", z=0.2)
            bx += w + rnd.choice([0.12, 0.24])
        a.text(S["sn"], 15.6, 0.45, 0.8, "#141414", font="ocr")
        a.text("MADE IN TAIWAN", 38.0, 2.0, 0.9, "#141414", font="narrowbd")
        # CE / warranty void dot
        a.ring(38.0, 6.0, 1.6, 1.9, "#141414", z=0.2)
        a.text("PASS", 38.0, 6.0, 0.9, "#141414", font="narrowbd")
    reg["edge_spread"] = at.swatch(pp.shade(S["spread"], 0.9))
    reg["edge_pcb"] = at.swatch("#4a4a3c")
    reg["pcb_plain"] = at.swatch(S["pcb"])
    name = rid
    at.render(pp.tex_path(name))
    pp.PREVIEW_TEX[name] = (0.6, 0.38)
    return name, reg


def relief_outline(span_y, span_z):
    """The raised panel on each spreader face, in the face's art coordinates (u across, v up)."""
    return [(0.0, 0.0), (span_y, 0.0), (span_y, span_z * 0.30), (span_y * 0.40 + 6.0, span_z * 0.30),
            (span_y * 0.40, span_z * 0.52), (0.0, span_z * 0.52)]


def build(rid):
    S = SPECS[rid]
    notch_y = NOTCH[S["mem"]]
    c.reset()
    tex, reg = textures(rid, S, notch_y)
    T = "tex_" + tex
    root = c.root(rid)
    k = pp.Kit(rid)
    # local (a, b, c) -> model (y, z, x) for side profiles extruded through the thickness
    M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))

    # ---- PCB
    hz = PCB_H * MM * 0.5
    pmap = pp.MultiMap([
        pp.Planar(reg["pcb"], (0, 0, hz), (1, 0, 0), (0, 0, 1), (LEN * MM, PCB_H * MM)),
        pp.Planar(reg["pcb"], (0, 0, hz), (-1, 0, 0), (0, 0, 1), (LEN * MM, PCB_H * MM)),
        reg["edge_pcb"]])
    outline = [(y * MM, z * MM) for y, z in pcb_outline(notch_y)]
    pp.prism(k[T], [outline], -PCB_T * MM * 0.5, PCB_T * MM * 0.5, M=M, uv=pmap)

    # ---- gold fingers on both faces
    g = k["gold"]
    for y in finger_positions(notch_y):
        for s in (-1, 1):
            pp.quad(g, (s * (PCB_T * MM * 0.5 + 0.00002), y * MM, 0.0018), (0.00058, 0.0034), normal=(s, 0, 0), up=(0, 0, 1))

    # ---- SMD resistors / caps in the exposed band above the fingers
    rnd = random.Random(3)
    for s in (-1, 1):
        y = -LEN / 2 + 5.0
        while y < LEN / 2 - 5.0:
            if abs(y - notch_y) > 2.0:
                z = rnd.choice([4.6, 5.6])
                body = "chip_black" if rnd.random() < 0.55 else "ceramic"
                _smd_side(k, s * (PCB_T * 0.5) * MM, y * MM, z * MM, s, body)
            y += rnd.uniform(1.6, 3.2)
    # DRAM packages on the +x side under the spreader (visible from the stick ends), with thermal pads
    n_chips = 8
    for i in range(n_chips):
        y = (-LEN / 2 + 9.5 + i * (LEN - 19.0) / (n_chips - 1)) * MM
        if abs(y / MM - notch_y) < 7.0 and False:
            continue
        pp.box(k["chip_black"], ((PCB_T * 0.5 + 0.5) * MM, y, 16.5 * MM), (1.0 * MM, 10.0 * MM, 11.5 * MM), bevel=0.0001)
    pp.box(k["thermal_pad"], ((PCB_T * 0.5 + 1.0 + (x0_sp(S) - PCB_T * 0.5 - 1.0) / 2) * MM, 0, 16.5 * MM),
           ((x0_sp(S) - PCB_T * 0.5 - 1.0) * MM, (LEN - 12.0) * MM, 12.0 * MM))
    pp.box(k["thermal_pad"], (-(PCB_T * 0.5 + (x0_sp(S) - PCB_T * 0.5) / 2) * MM, 0, 16.5 * MM),
           ((x0_sp(S) - PCB_T * 0.5) * MM, (LEN - 12.0) * MM, 12.0 * MM))
    # PMIC (DDR5) / SPD hub, visible below the spreader edge
    if S["mem"] == "DDR5":
        _chip_side(k, 1, 0.0, 0.0050, 0.0040, 0.0030)
    # ---- heat spreaders
    top = S["top"]
    x0, x1 = S["sp_x"]
    span_y, span_z = 129.2, top - 7.0
    zc = (7.0 + top) * 0.5 * MM
    for s in (-1, 1):
        smap = pp.MultiMap([pp.Planar(reg["spread"], (0, 0, zc), (s, 0, 0), (0, 0, 1), (span_y * MM, span_z * MM)),
                            reg["edge_spread"]])
        prof = spreader_profile(S, span_y)
        pts = [(y * MM, z * MM) for y, z in prof]
        if s > 0:
            pp.prism(k[T], [pts], x0 * MM, x1 * MM, M=M, uv=smap)
        else:
            pp.prism(k[T], [pts], -x1 * MM, -x0 * MM, M=M, uv=smap)
        # raised relief panel (0.35 mm) with the diagonal edge; art coords -> (y, z)
        rel = relief_outline(span_y, span_z)
        # the face's art u runs along -y on +x and along +y on -x
        rpts = []
        for u, v in rel:
            y = (u - span_y / 2) * (-1 if s > 0 else 1)
            rpts.append((y * MM, (v + 7.0) * MM))
        if s < 0:
            rpts.reverse()
        if s > 0:
            pp.prism(k[T], [list(reversed(rpts))], x1 * MM, (x1 + 0.35) * MM, M=M, uv=smap)
        else:
            pp.prism(k[T], [rpts], -(x1 + 0.35) * MM, -x1 * MM, M=M, uv=smap)
    # top bridge joining both plates
    if S["rgb"]:
        pp.box(k["alu_dark"], (0, 0, (top - 1.0) * MM), (2 * x1 * MM, (span_y - 6.0) * MM, 2.0 * MM), bevel=0.0003)
        # RGB diffuser bar
        dprof = [(-2.7, top - 0.2), (2.7, top - 0.2), (2.7, top + 3.0), (1.5, top + 4.6), (-1.5, top + 4.6), (-2.7, top + 3.0)]
        Mx = pp.frame(x=(1, 0, 0), y=(0, 0, 1), z=(0, 1, 0))
        pp.prism(k["rgb"], [[(x * MM, z * MM) for x, z in dprof]], -61.5 * MM, 61.5 * MM, M=Mx)
        # end caps of the diffuser
        for e in (-1, 1):
            pp.box(k["alu_dark"], (0, e * 62.6 * MM, (top + 1.9) * MM), (5.8 * MM, 2.2 * MM, 4.6 * MM), bevel=0.0004)
    else:
        pp.box(k[T], (0, 0, (top - 0.6) * MM), (2 * x1 * MM, span_y * MM, 1.2 * MM), bevel=0.0003, uv=reg["edge_spread"])

    # ---- product sticker on the +x spreader (over the relief panel)
    lx = (x1 + 0.35 + 0.03) * MM
    pp.quad(k[T], (lx, -0.022, 0.0135), (0.046, 0.013), normal=(1, 0, 0), up=(0, 0, 1), region=reg["label"])

    k.finish(root)

    # anchors
    c.anchor("A_NOTCH_0", (0, notch_y * MM, 0.0), (0.004, 0.0025, 0.004), root, meta=f"y={notch_y * MM:.4f},mem={S['mem']}")
    h = (top + (4.6 if S["rgb"] else 0.0)) * MM
    c.anchor("A_HIT_0", (0, 0, h * 0.5), ((x1 + 0.4) * 2 * MM, LEN * MM, h), root)

    c.join_by_tag(root, rid)
    c.export(root, rid)
    pp.report(root)
    return root


def x0_sp(S):
    return S["sp_x"][0]


def spreader_profile(S, span_y):
    h = span_y / 2
    top = S["top"]
    if S["rgb"]:
        return [(-h, 7.0), (h, 7.0), (h, top - 4.0), (h - 4.0, top), (-h + 4.0, top), (-h, top - 4.0)]
    # LPX-like: a stepped fin along the top edge
    pts = [(-h, 7.0), (h, 7.0), (h, top - 3.0)]
    n = 14
    for i in range(n):
        y1 = h - (i + 0.5) * span_y / n
        y2 = h - (i + 1.0) * span_y / n
        pts += [(y1 + 1.0, top), (y1 - 1.0, top), (y2 + 0.3, top - 1.6)]
    pts[-1] = (-h, top - 3.0)
    return pts


def _smd_side(k, x, y, z, s, body):
    """A 0402 part lying on a DIMM face (normal s*x)."""
    t = 0.00045
    xc = x + s * t * 0.5
    pp.box(k[body], (xc, y, z), (t * 0.96, 0.0006, 0.0005))
    for e in (-1, 1):
        pp.box(k["solder"], (xc, y + e * 0.00042, z), (t, 0.00022, 0.00052))


def _chip_side(k, s, y, z, w, h):
    pp.box(k["chip_black"], (s * (PCB_T * 0.5 * MM + 0.00045), y, z), (0.0009, w, h), bevel=0.00012)


def previews(rid, root):
    pp.preview(root, rid, views=((70, 25), (-60, 30), (95, 60)), size=(960, 720), dist=0.24, zup=True)
    pp.preview(root, rid, views=((80, 12),), size=(960, 720), dist=0.085, target=(0, -0.035, 0.012), start=3, zup=True)


def main(ids=None):
    for rid in ids or list(SPECS):
        root = build(rid)
        previews(rid, root)


if __name__ == "__main__":
    main(c.args() or None)
