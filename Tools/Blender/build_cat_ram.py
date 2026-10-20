"""
The memory catalogue (task catalog/13): 16 desktop kits (10 DDR5, 6 DDR4) and 4 server RDIMMs.

Every desktop stick follows the ram_ddr5_16 / ram_ddr4_8 contract (build_ram.py): origin at the bottom-edge centre,
thickness along x, the 133.35 mm length along y, the height along z; A_NOTCH_0 (meta y=<offset>,mem=<DDR4|DDR5>)
and A_HIT_0. What varies is the look: the heat-spreader height (31.25 mm bare PCB up to 51 mm), the spreader outline
and art, the colour, the RGB diffuser (`rgb` tag) and the printed spec label. One model per stick type: a kit is two
of the same stick (per_box 2 in docs/catalog/ram.json).

The RDIMMs are a new contract ("rdimm", docs/reports/cat_ram.md): the same frame, a bare green PCB with 10 DRAM
packages per side (9 on DDR4), the RCD in the middle, PMIC (DDR5), SPD hub and thermal sensors, and the DDR5 RDIMM
key notch, which differs from the desktop DDR5 notch.

build_ram.py is not changed: this script reuses its constants and finger layout and builds its own spreaders.

Run: blender -b --factory-startup -P Tools/Blender/build_cat_ram.py -- [ids...] [--nopreview]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_ram as br  # noqa: E402

MM = 0.001
LEN, PCB_T = br.LEN, br.PCB_T
ZB = 7.0          # spreader bottom edge above the stick's bottom edge (mm)
SPAN_Y = 129.2    # spreader length (mm)

# Key notch centre along y (mm from the stick centre). Desktop values are build_ram's; the DDR5 RDIMM key sits
# 2.0 mm nearer the centre than the DDR5 UDIMM key, so a server module can't go into a desktop slot (or back).
NOTCH = dict(br.NOTCH)
NOTCH["DDR5_RDIMM"] = -1.9
NOTCH["DDR4_RDIMM"] = br.NOTCH["DDR4"]   # DDR4 RDIMMs share the UDIMM key (electrically incompatible only)

REPORT_TXT = os.path.join(c.PREVIEWS, "cat_ram_report.txt")


def K(**kw):
    return kw


# ---------------------------------------------------------------------------------------------- the catalogue
# kit: sticks per box; gb: one stick. style picks the spreader (see STYLES). top: overall height in mm.
CAT = [
    # ---- desktop DDR5
    K(id="ram_corvex_ddr5_32_black", brand="Corvex", series="VECTOR", name="Corvex Vector DDR5 32 GB (2 x 16 GB) 6000 CL30",
      mem="DDR5", gb=16, kit=2, mts=6000, cl="30-36-36-76", v="1.40V", pn="CVX32GX5M2B6000C30", style="vector",
      top=34.9, rgb=False, spread="#1b1c1f", band="#0e0f11", ink="#e6e7ea", accent="#5d6168", color="#1B1C1F",
      price=105, analog="Corsair Vengeance DDR5 32GB (2x16GB) 6000 CL30 black"),
    K(id="ram_corvex_ddr5_32_white_rgb", brand="Corvex", series="VECTOR RGB", name="Corvex Vector RGB DDR5 32 GB (2 x 16 GB) 6000 CL36 White",
      mem="DDR5", gb=16, kit=2, mts=6000, cl="36-36-36-76", v="1.35V", pn="CVX32GX5M2E6000C36W", style="vector_rgb",
      top=44.0, rgb=True, spread="#e9eaec", band="#d2d4d8", ink="#3a3d44", accent="#9aa0aa", color="#E9EAEC",
      price=119, analog="Corsair Vengeance RGB DDR5 32GB (2x16GB) 6000 CL36 white"),
    K(id="ram_gstride_ddr5_48_rgb", brand="G.Stride", series="TRINE Z5 RGB", name="G.Stride Trine Z5 RGB DDR5 48 GB (2 x 24 GB) 7200 CL36",
      mem="DDR5", gb=24, kit=2, mts=7200, cl="36-46-46-115", v="1.40V", pn="GS5-7200J3646F24GX2-TN5RK", style="trine",
      top=44.0, rgb=True, spread="#c9ccd1", band="#141518", ink="#141518", accent="#e8e9ec", color="#C9CCD1",
      price=189, analog="G.Skill Trident Z5 RGB DDR5-7200 48GB (2x24GB) silver/black"),
    K(id="ram_gstride_ddr5_32_lp", brand="G.Stride", series="FLARE X5", name="G.Stride Flare X5 DDR5 32 GB (2 x 16 GB) 6000 CL30 low profile",
      mem="DDR5", gb=16, kit=2, mts=6000, cl="30-36-36-96", v="1.35V", pn="GS5-6000J3036F16GX2-FL5", style="flare",
      top=33.0, rgb=False, spread="#17181b", band="#2a2c31", ink="#e3e4e7", accent="#6a6e76", color="#17181B",
      price=109, analog="G.Skill Flare X5 DDR5-6000 32GB (2x16GB) CL30 low profile"),
    K(id="ram_kingsland_ddr5_64", brand="Kingsland", series="FEROX", name="Kingsland Ferox DDR5 64 GB (2 x 32 GB) 5600 CL36",
      mem="DDR5", gb=32, kit=2, mts=5600, cl="36-38-38-80", v="1.25V", pn="KLF556C36BBEK2-64", style="ferox",
      top=34.9, rgb=False, spread="#1c1d20", band="#2b2d31", ink="#e5e6e8", accent="#e0262b", color="#1C1D20",
      price=189, analog="Kingston Fury Beast DDR5-5600 64GB (2x32GB) black"),
    K(id="ram_kingsland_ddr5_32_white_rgb", brand="Kingsland", series="FEROX RGB", name="Kingsland Ferox RGB DDR5 32 GB (2 x 16 GB) 6000 CL30 White",
      mem="DDR5", gb=16, kit=2, mts=6000, cl="30-36-36-80", v="1.40V", pn="KLF560C30BWAK2-32", style="ferox_rgb",
      top=42.2, rgb=True, spread="#eceded", band="#d5d7da", ink="#2e3035", accent="#b8bcc3", color="#ECEDED",
      price=125, analog="Kingston Fury Beast RGB DDR5-6000 32GB (2x16GB) white"),
    K(id="ram_crux_ddr5_96", brand="Crux", series="CRUX PRO", name="Crux Pro DDR5 96 GB (2 x 48 GB) 5600 CL46",
      mem="DDR5", gb=48, kit=2, mts=5600, cl="46-45-45", v="1.10V", pn="CXP2K48G56C46U5", style="crux_pro",
      top=35.0, rgb=False, spread="#1a1b1d", band="#26282c", ink="#dfe0e3", accent="#8c9099", color="#1A1B1D",
      price=259, analog="Crucial Pro DDR5-5600 96GB (2x48GB) black"),
    K(id="ram_crux_ddr5_16", brand="Crux", series="", name="Crux DDR5 16 GB (2 x 8 GB) 5600 CL46",
      mem="DDR5", gb=8, kit=2, mts=5600, cl="46-45-45", v="1.10V", pn="CX2K8G56C46U5", style="bare",
      top=31.25, rgb=False, pcb="#1f5a32", spread="#1f5a32", band="#1f5a32", ink="#e8efe8", accent="#e8efe8", color="#1F5A32",
      price=59, analog="Crucial DDR5-5600 16GB (2x8GB) UDIMM, bare green PCB"),
    K(id="ram_teamforge_ddr5_32_white_rgb", brand="TeamForge", series="DELTA RGB", name="TeamForge T-Forge Delta RGB DDR5 32 GB (2 x 16 GB) 6400 CL40 White",
      mem="DDR5", gb=16, kit=2, mts=6400, cl="40-40-40-84", v="1.35V", pn="TFD532G6400HC40BDC01", style="delta",
      top=46.1, rgb=True, spread="#eeeff0", band="#dadcdf", ink="#2b2d31", accent="#a7abb3", color="#EEEFF0",
      price=125, analog="TeamGroup T-Force Delta RGB DDR5-6400 32GB (2x16GB) white"),
    K(id="ram_volt_ddr5_64_rgb", brand="Volt", series="FLUX RGB", name="Volt Flux RGB DDR5 64 GB (2 x 32 GB) 6400 CL32",
      mem="DDR5", gb=32, kit=2, mts=6400, cl="32-39-39-102", v="1.40V", pn="VDF5-32G64C32R", style="flux",
      top=38.0, rgb=True, spread="#30333a", band="#121316", ink="#d9dce2", accent="#8a93a6", color="#30333A",
      price=229, analog="generic DDR5-6400 64GB (2x32GB) RGB kit (Volt house brand)"),
    # ---- desktop DDR4
    K(id="ram_corvex_ddr4_16_lp", brand="Corvex", series="VECTOR LPX", name="Corvex Vector LPX DDR4 16 GB (2 x 8 GB) 3200 CL16",
      mem="DDR4", gb=8, kit=2, mts=3200, cl="16-18-18-36", v="1.35V", pn="CVX16GX4M2B3200C16", style="lpx",
      top=34.0, rgb=False, spread="#1a1b1e", band="#101113", ink="#e6e7ea", accent="#55595f", color="#1A1B1E",
      price=39, analog="Corsair Vengeance LPX DDR4-3200 16GB (2x8GB) CL16 black"),
    K(id="ram_corvex_ddr4_32_rgb", brand="Corvex", series="VECTOR RGB PRO", name="Corvex Vector RGB Pro DDR4 32 GB (2 x 16 GB) 3600 CL18",
      mem="DDR4", gb=16, kit=2, mts=3600, cl="18-22-22-42", v="1.35V", pn="CVW32GX4M2D3600C18", style="rgbpro",
      top=51.0, rgb=True, spread="#1d1e21", band="#101113", ink="#e6e7ea", accent="#5d6168", color="#1D1E21",
      price=79, analog="Corsair Vengeance RGB Pro DDR4-3600 32GB (2x16GB) black"),
    K(id="ram_gstride_ddr4_16_red", brand="G.Stride", series="RIPTIDE V", name="G.Stride Riptide V DDR4 16 GB (2 x 8 GB) 3200 CL16 Red",
      mem="DDR4", gb=8, kit=2, mts=3200, cl="16-18-18-38", v="1.35V", pn="GS4-3200C16D-16GRKB", style="riptide",
      top=42.0, rgb=False, spread="#b3161d", band="#141416", ink="#f2f2f2", accent="#e8e8e8", color="#B3161D",
      price=42, analog="G.Skill Ripjaws V DDR4-3200 16GB (2x8GB) CL16 red"),
    K(id="ram_kingsland_ddr4_32", brand="Kingsland", series="FEROX", name="Kingsland Ferox DDR4 32 GB (2 x 16 GB) 3200 CL16",
      mem="DDR4", gb=16, kit=2, mts=3200, cl="16-18-18", v="1.35V", pn="KLF432C16BBK2/32", style="ferox",
      top=34.1, rgb=False, spread="#1c1d20", band="#2b2d31", ink="#e5e6e8", accent="#e0262b", color="#1C1D20",
      price=69, analog="Kingston Fury Beast DDR4-3200 32GB (2x16GB) black"),
    K(id="ram_crux_ddr4_64", brand="Crux", series="TRACER", name="Crux Tracer DDR4 64 GB (2 x 32 GB) 3200 CL16",
      mem="DDR4", gb=32, kit=2, mts=3200, cl="16-18-18-36", v="1.35V", pn="CXT2K32G32C16U4B", style="tracer",
      top=39.0, rgb=False, spread="#1b1c1f", band="#0f1012", ink="#e8e9eb", accent="#d42a2f", color="#1B1C1F",
      price=139, analog="Crucial Ballistix DDR4-3200 64GB (2x32GB) CL16 black"),
    K(id="ram_teamforge_ddr4_32_red", brand="TeamForge", series="VULCAN Z", name="TeamForge T-Forge Vulcan Z DDR4 32 GB (2 x 16 GB) 3600 CL18 Red",
      mem="DDR4", gb=16, kit=2, mts=3600, cl="18-22-22-42", v="1.35V", pn="TFVZ432G3600HC18JDC01", style="vulcan",
      top=32.0, rgb=False, spread="#b8161c", band="#5a5d63", ink="#f0f0f0", accent="#2a2b2e", color="#B8161C",
      price=65, analog="TeamGroup T-Force Vulcan Z DDR4-3600 32GB (2x16GB) red"),
    # ---- server RDIMMs (new contract)
    K(id="ram_kingsland_rdimm5_32", brand="Kingsland", series="SERVER PREMIER", name="Kingsland Server Premier DDR5-4800 RDIMM 32 GB ECC",
      mem="DDR5", gb=32, kit=1, mts=4800, cl="40-39-39", v="1.10V", pn="KLS48R40BD8KMM-32HMR", style="rdimm",
      top=31.25, rgb=False, ranks="2Rx8", chips_side=10, chip_mark="KINGSLAND", die="D5X8 16Gb", stack=1,
      pcb="#1d5b34", color="#1D5B34", price=179, analog="Kingston Server Premier DDR5-4800 32GB 2Rx8 ECC RDIMM"),
    K(id="ram_sorin_rdimm5_64", brand="Sorin", series="", name="Sorin DDR5-4800 RDIMM 64 GB ECC",
      mem="DDR5", gb=64, kit=1, mts=4800, cl="40-39-39", v="1.10V", pn="S321R8GA0BB0-CQK", style="rdimm",
      top=31.25, rgb=False, ranks="2Rx4", chips_side=10, chip_mark="SORIN", die="S4RAH046VB", stack=1,
      pcb="#1a5530", color="#1A5530", price=329, analog="Samsung M321R8GA0BB0-CQK DDR5-4800 64GB 2Rx4 ECC RDIMM"),
    K(id="ram_crux_rdimm5_128", brand="Crux", series="", name="Crux DDR5-5600 RDIMM 128 GB ECC 3DS",
      mem="DDR5", gb=128, kit=1, mts=5600, cl="46-45-45", v="1.10V", pn="CXR40F2047S1RC56BR", style="rdimm",
      top=38.0, pcb_h=38.0, rgb=False, ranks="2S2Rx4 3DS", chips_side=10, chip_mark="CRUX", die="3DS 2H 32Gb", stack=2,
      pcb="#1e5933", color="#1E5933", price=1199, analog="Micron/Crucial DDR5-5600 128GB 2S2Rx4 3DS ECC RDIMM"),
    K(id="ram_kingsland_rdimm4_32", brand="Kingsland", series="SERVER PREMIER", name="Kingsland Server Premier DDR4-3200 RDIMM 32 GB ECC",
      mem="DDR4", gb=32, kit=1, mts=3200, cl="22-22-22", v="1.20V", pn="KLS32RD4/32MRR", style="rdimm",
      top=31.25, rgb=False, ranks="2Rx4", chips_side=9, chip_mark="KINGSLAND", die="D4X4 8Gb", stack=1,
      pcb="#1d5b34", color="#1D5B34", price=119, analog="Kingston Server Premier DDR4-3200 32GB 2Rx4 ECC RDIMM"),
]
BY_ID = {s["id"]: s for s in CAT}


# ---------------------------------------------------------------------------------------------- PCB
def pcb_outline(notch_y, h):
    """build_ram.pcb_outline with the PCB height as a parameter (31.25 mm JEDEC; taller for the 3DS RDIMM)."""
    hl = LEN / 2
    nw, nd = 1.6, 3.6
    pts = [(-hl + 1.2, 0.0)]
    pts += [(notch_y - nw / 2, 0.0), (notch_y - nw / 2, nd - nw / 2)]
    for k in range(1, 6):
        a = math.pi - math.pi * k / 6
        pts.append((notch_y + math.cos(a) * nw / 2, nd - nw / 2 + math.sin(a) * nw / 2))
    pts += [(notch_y + nw / 2, nd - nw / 2), (notch_y + nw / 2, 0.0)]
    pts += [(hl - 1.2, 0.0), (hl, 1.2)]
    zc, r = 12.8, 1.25
    pts += [(hl, zc - r)] + [(hl - math.sin(math.pi * k / 8) * r, zc - math.cos(math.pi * k / 8) * r) for k in range(1, 8)] + [(hl, zc + r)]
    pts += [(hl, h), (-hl, h)]
    pts += [(-hl, zc + r)] + [(-hl + math.sin(math.pi * k / 8) * r, zc + math.cos(math.pi * k / 8) * r) for k in range(1, 8)] + [(-hl, zc - r)]
    pts += [(-hl, 1.2)]
    return pts


def notch_of(S):
    return NOTCH[S["mem"] + ("_RDIMM" if S["style"] == "rdimm" else "")]


def pcb_h(S):
    return S.get("pcb_h", br.PCB_H)


# ---------------------------------------------------------------------------------------------- spreader styles
# Each style gives, in the face's art coordinates (u across the face as seen, v up from the spreader bottom; the
# same picture on both faces):
#   outline(w, h)   the plate outline (h = plate height above ZB)
#   art(a, S, w, h, rnd)
#   reliefs(w, h)   [(polygon, raise_mm)] raised panels on the face (textured like the face)
#   face_rgb(w, h)  [(polygon, raise_mm)] RGB diffuser windows on the face
#   bar(S, plate_top)  RGB light bar silhouette in (y, z) mm (extruded across the thickness), or None
#   plate_top(S)    the plate's top height (mm above the stick's bottom edge)

def chamfer_rect(w, h, ch):
    return [(0, 0), (w, 0), (w, h - ch), (w - ch, h), (ch, h), (0, h - ch)]


def brushed(a, w, h, col, rnd, n=240, k0=0.88, k1=1.12, wid=(0.05, 0.16), z=0.1, v0=0.0):
    for _ in range(n):
        v = rnd.uniform(v0, h)
        u0 = rnd.uniform(-20, w)
        a.line([(u0, v), (u0 + rnd.uniform(15, 70), v)], rnd.uniform(*wid), pp.shade(col, rnd.uniform(k0, k1)), z=z, joins=False)


def sail(a, x, y, s, col, z=0.6):
    """The Corvex mark: two sails."""
    a.poly([(x, y - s * 0.5), (x + s * 0.55, y - s * 0.5), (x + s * 0.18, y + s * 0.62)], col, z=z)
    a.poly([(x + s * 0.30, y - s * 0.5), (x + s * 0.95, y - s * 0.5), (x + s * 0.45, y + s * 0.42)], col, z=z)


def logo(a, S, x, y, size, col, ax="LEFT"):
    """The brand's word mark at (x, y); returns its right end."""
    b = S["brand"]
    if b == "Corvex":
        sail(a, x, y, size * 1.1, col)
        a.text("CORVEX", x + size * 1.25, y, size, col, font="agency", ax="LEFT", space=1.08)
        return x + size * 1.25 + a.text_width("CORVEX", size, "agency") * 1.08
    if b == "G.Stride":
        a.poly([(x, y - size * 0.45), (x + size * 0.7, y - size * 0.45), (x + size * 1.0, y + size * 0.45), (x + size * 0.3, y + size * 0.45)], col, z=0.6)
        a.text("G.STRIDE", x + size * 1.25, y, size, col, font="impact", ax="LEFT", space=1.02)
        return x + size * 6.0
    if b == "Kingsland":
        a.text("KINGSLAND", x, y, size * 0.75, col, font="arialbd", ax="LEFT", space=1.15)
        return x + size * 4.0
    if b == "Crux":
        a.ring(x + size * 0.45, y, size * 0.30, size * 0.45, col, z=0.6)
        a.circle(x + size * 0.45, y, size * 0.14, col, z=0.6)
        a.text("CRUX", x + size * 1.1, y, size, col, font="arialbd", ax="LEFT", space=1.1)
        return x + size * 4.0
    if b == "TeamForge":
        a.text("T-FORGE", x, y, size, col, font="impact", ax="LEFT", space=1.05)
        return x + size * 4.5
    a.text("VOLT", x, y, size, col, font="agency", ax="LEFT", space=1.05)
    return x + size * 3.0


# -- vector: Corvex DDR5, flat plate with a stepped shoulder and a ribbed panel
def vector_outline(w, h):
    return [(0, 0), (w, 0), (w, h - 2.5), (w - 2.5, h), (w * 0.64, h), (w * 0.61, h - 1.8), (w * 0.08, h - 1.8),
            (w * 0.05, h), (2.5, h), (0, h - 2.5)]


def vector_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.9, k1=1.1)
    # the ribbed right-hand panel
    a.poly([(w * 0.66, 0), (w, 0), (w, h - 2.5), (w * 0.70, h - 2.5)], S["band"], z=0.2)
    for i in range(18):
        v = 1.2 + i * (h - 4.5) / 17
        a.line([(w * 0.66 + (v / h) * w * 0.04 + 1.0, v), (w - 1.0, v)], 0.18, pp.shade(S["band"], 1.6), z=0.25, joins=False)
    logo(a, S, 7.0, h * 0.42, 6.0, S["ink"])
    a.text(S["series"], 7.0, h * 0.17, 2.4, S["accent"], font="agencyr", ax="LEFT", space=1.4)
    a.text(S["mem"], w * 0.60, h * 0.17, 2.2, S["accent"], font="agency", ax="RIGHT")


# -- vector_rgb: the same family with a light bar on top
def vector_rgb_outline(w, h):
    return [(0, 0), (w, 0), (w, h - 2.0), (w - 2.0, h), (2.0, h), (0, h - 2.0)]


def vector_rgb_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.95, k1=1.04)
    a.poly([(0, h * 0.62), (w * 0.30, h * 0.62), (w * 0.34, h * 0.86), (w, h * 0.86), (w, h), (0, h)], S["band"], z=0.2)
    a.line([(0, h * 0.62), (w * 0.30, h * 0.62), (w * 0.34, h * 0.86), (w, h * 0.86)], 0.35, S["accent"], z=0.3)
    logo(a, S, 7.0, h * 0.36, 6.0, S["ink"])
    a.text(S["series"], w - 7.0, h * 0.70, 2.4, S["ink"], font="agencyr", ax="RIGHT", space=1.4)
    a.text(S["mem"], w - 7.0, h * 0.14, 2.2, S["accent"], font="agency", ax="RIGHT")


def bar_flat(S, z0, z1, chamfer=2.0, inset=1.0):
    hl = SPAN_Y / 2 - inset
    return [(-hl, z0), (hl, z0), (hl, z1 - chamfer), (hl - chamfer, z1), (-hl + chamfer, z1), (-hl, z1 - chamfer)]


# -- trine: G.Stride Trident-style, silver top fin over a black lower plate, winged light bar
def trine_outline(w, h):
    pts = [(0, 0), (w, 0), (w, h)]
    # the upper edge dips in the middle (the bar's wings stand above both ends)
    pts += [(w * 0.80, h), (w * 0.72, h - 2.0), (w * 0.28, h - 2.0), (w * 0.20, h), (0, h)]
    return pts


def trine_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=320, k0=0.82, k1=1.15)
    # the black lower body with a raked split line
    body = [(0, 0), (w, 0), (w, h * 0.40), (w * 0.62, h * 0.40), (w * 0.55, h * 0.58), (0, h * 0.58)]
    a.poly(body, S["band"], z=0.2)
    brushed(a, w, h * 0.55, pp.shade(S["band"], 1.2), rnd, n=90, k0=0.9, k1=1.4, wid=(0.04, 0.08), z=0.22)
    a.line([(0, h * 0.58), (w * 0.55, h * 0.58), (w * 0.62, h * 0.40), (w, h * 0.40)], 0.5, "#8d9198", z=0.3)
    logo(a, S, 6.0, h * 0.30, 4.6, "#e6e7ea")
    a.text("TRINE Z5", w * 0.52, h * 0.16, 2.8, "#b9bcc2", font="agency", ax="RIGHT", space=1.3)
    a.text("RGB", w * 0.56, h * 0.16, 2.0, "#b9bcc2", font="agencyr", ax="LEFT")
    a.text(S["mem"], w - 6.0, h * 0.70, 2.4, S["band"], font="agency", ax="RIGHT")


def trine_bar(S, z0):
    hl = SPAN_Y / 2 - 0.6
    top = S["top"]
    pts = [(-hl, z0), (hl, z0), (hl, top - 1.2), (hl - 2.0, top), (hl * 0.62, top), (hl * 0.48, top - 1.6),
           (-hl * 0.48, top - 1.6), (-hl * 0.62, top), (-hl + 2.0, top), (-hl, top - 1.2)]
    return pts


# -- flare: G.Stride low profile, flat with raked stripes
def flare_outline(w, h):
    return chamfer_rect(w, h, 1.2)


def flare_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.9, k1=1.15)
    for g in range(3):
        u0 = w * 0.58 + g * 9.0
        for i in range(3):
            x = u0 + i * 1.9
            a.poly([(x, 0), (x + 1.0, 0), (x + 1.0 + h * 0.45, h), (x + h * 0.45, h)], S["band"], z=0.2)
    a.rect(0, h - 1.4, w, h, S["band"], z=0.2)
    logo(a, S, 6.0, h * 0.58, 3.6, S["ink"])
    a.text("FLARE X5", 6.0, h * 0.26, 3.0, S["accent"], font="agency", ax="LEFT", space=1.3)
    a.text(S["mem"], w - 4.0, h * 0.20, 2.2, S["accent"], font="agency", ax="RIGHT")


# -- ferox: Kingsland, an asymmetric top edge and angular shards
def ferox_outline(w, h):
    return [(0, 0), (w, 0), (w, h - 3.2), (w * 0.66, h - 3.2), (w * 0.62, h), (1.5, h), (0, h - 1.5)]


def ferox_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=120, k0=0.95, k1=1.06)
    a.poly([(w * 0.40, 0), (w * 0.62, 0), (w * 0.80, h), (w * 0.58, h)], S["band"], z=0.2)
    a.poly([(w * 0.66, 0), (w * 0.71, 0), (w * 0.89, h), (w * 0.84, h)], S["band"], z=0.2)
    a.line([(w * 0.62, 0), (w * 0.80, h)], 0.35, pp.shade(S["band"], 1.5), z=0.25)
    a.text("FEROX", 7.0, h * 0.50, 7.0, S["ink"], font="impact", ax="LEFT", space=1.06)
    logo(a, S, 7.5, h * 0.20, 3.4, S["ink"])
    a.rect(w * 0.93, h * 0.10, w * 0.93 + 1.2, h * 0.32, S["accent"], z=0.3)
    a.text(S["mem"], w * 0.92, h * 0.20, 2.2, S["ink"], font="agency", ax="RIGHT")


def ferox_rgb_outline(w, h):
    return chamfer_rect(w, h, 1.5)


def ferox_rgb_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=140, k0=0.96, k1=1.03)
    a.poly([(w * 0.45, 0), (w * 0.64, 0), (w * 0.78, h), (w * 0.59, h)], S["band"], z=0.2)
    a.poly([(w * 0.68, 0), (w * 0.72, 0), (w * 0.86, h), (w * 0.82, h)], S["band"], z=0.2)
    a.text("FEROX", 7.0, h * 0.52, 6.6, S["ink"], font="impact", ax="LEFT", space=1.06)
    logo(a, S, 7.5, h * 0.22, 3.3, S["ink"])
    a.text("RGB", w * 0.94, h * 0.70, 2.4, S["ink"], font="agency", ax="RIGHT")
    a.text(S["mem"], w * 0.94, h * 0.20, 2.2, S["ink"], font="agency", ax="RIGHT")


def ferox_rgb_bar(S, z0):
    hl = SPAN_Y / 2 - 1.0
    top = S["top"]
    # two shallow V dips: the Fury Beast RGB wave
    pts = [(-hl, z0), (hl, z0), (hl, top - 1.0), (hl - 1.5, top)]
    for f in (0.62, 0.30, -0.02, -0.34, -0.66):
        pts.append((hl * f + 6.0, top - (1.4 if f in (0.30, -0.34) else 0.0)))
    pts += [(-hl + 1.5, top), (-hl, top - 1.0)]
    # keep it a simple polygon: sort the upper run from +y to -y
    upper = sorted(pts[2:], key=lambda p: -p[0])
    return pts[:2] + upper


# -- crux_pro: plain black plate, engraved lines
def crux_pro_outline(w, h):
    return chamfer_rect(w, h, 2.0)


def crux_pro_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=100, k0=0.96, k1=1.05)
    for i in range(5):
        v = h * 0.70 + i * 1.1
        a.line([(w * 0.55, v), (w - 4.0, v)], 0.18, pp.shade(S["spread"], 1.6), z=0.2, joins=False)
    a.line([(4.0, h * 0.12), (w - 4.0, h * 0.12)], 0.2, pp.shade(S["spread"], 1.7), z=0.2, joins=False)
    logo(a, S, 7.0, h * 0.50, 6.0, S["ink"])
    a.text("PRO", 37.0, h * 0.50, 6.0, S["accent"], font="arial", ax="LEFT", space=1.2)
    a.text("OVERCLOCKING", w - 5.0, h * 0.26, 2.0, S["accent"], font="arialbd", ax="RIGHT", space=1.25)
    a.text(S["mem"], w - 5.0, h * 0.48, 2.4, S["ink"], font="arialbd", ax="RIGHT")


# -- delta: TeamForge, a white frame with a wide triangular diffuser on the face
def delta_outline(w, h):
    return chamfer_rect(w, h, 1.6)


def delta_face(w, h):
    return [([(w * 0.10, h * 0.48), (w * 0.90, h * 0.48), (w * 0.97, h - 1.6), (w * 0.03, h - 1.6)], 0.5),
            ([(w * 0.36, h * 0.48), (w * 0.64, h * 0.48), (w * 0.50, h * 0.30)], 0.5)]


def delta_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=120, k0=0.97, k1=1.02)
    a.poly([(0, 0), (w * 0.34, 0), (w * 0.30, h * 0.40), (0, h * 0.40)], S["band"], z=0.2)
    logo(a, S, 5.0, h * 0.20, 4.4, S["ink"])
    a.text("DELTA", w * 0.70, h * 0.22, 4.0, S["ink"], font="impact", ax="LEFT", space=1.2)
    a.text(S["mem"], w - 4.0, h * 0.10, 2.0, S["accent"], font="agency", ax="RIGHT")


# -- flux: the Volt house style (as ram_ddr5_16): dark plate, raked relief panel, diffuser bar on a bridge
def flux_outline(w, h):
    return chamfer_rect(w, h, 4.0)


def flux_relief(w, h):
    return [([(0.0, 0.0), (w, 0.0), (w, h * 0.30), (w * 0.40 + 6.0, h * 0.30), (w * 0.40, h * 0.52), (0.0, h * 0.52)], 0.35)]


def flux_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=260, k0=0.86, k1=1.14)
    a.poly(flux_relief(w, h)[0][0], S["band"], z=0.2)
    brushed(a, w, h * 0.55, pp.shade(S["band"], 1.35), rnd, n=120, k0=0.95, k1=1.05, wid=(0.05, 0.07), z=0.25)
    a.line([(0.0, h * 0.52), (w * 0.40, h * 0.52), (w * 0.40 + 6.0, h * 0.30), (w, h * 0.30)], 0.45, S["accent"], z=0.3)
    a.text("VOLT", 8.0, h * 0.70, 8.5, S["ink"], font="agency", ax="LEFT", space=1.05)
    a.text(S["series"], 40.0, h * 0.68, 3.2, S["ink"], font="agencyr", ax="LEFT")
    a.text(S["mem"], w - 8.0, h * 0.70, 3.0, S["ink"], font="agency", ax="RIGHT")


def flux_bar(S, z0):
    top = S["top"]
    return [(-61.5, z0), (61.5, z0), (61.5, top + 3.0), (60.0, top + 4.6), (-60.0, top + 4.6), (-61.5, top + 3.0)]


# -- lpx: Corvex DDR4 low profile, the stepped fin top edge
def lpx_outline(w, h):
    pts = [(0, 0), (w, 0), (w, h - 3.0)]
    n = 14
    for i in range(n):
        u1 = w - (i + 0.5) * w / n
        u2 = w - (i + 1.0) * w / n
        pts += [(u1 + 1.0, h), (u1 - 1.0, h), (u2 + 0.3, h - 1.6)]
    pts[-1] = (0, h - 3.0)
    return pts


def lpx_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.9, k1=1.12)
    a.rect(0, h - 4.0, w, h, S["band"], z=0.2)
    for i in range(14):
        u = w - (i + 0.5) * w / 14
        a.line([(u, h - 3.6), (u, h)], 0.25, pp.shade(S["band"], 1.8), z=0.25, joins=False)
    a.poly([(w * 0.62, 0), (w, 0), (w, h * 0.46), (w * 0.66, h * 0.46)], S["band"], z=0.2)
    logo(a, S, 7.0, h * 0.44, 6.0, S["ink"])
    a.text("VECTOR", 7.0, h * 0.16, 2.6, S["accent"], font="agency", ax="LEFT", space=1.5)
    a.text("LPX", 28.0, h * 0.16, 2.6, S["ink"], font="agency", ax="LEFT", space=1.3)
    a.text(S["mem"], w - 5.0, h * 0.22, 2.4, S["ink"], font="agency", ax="RIGHT")


# -- rgbpro: Corvex DDR4 RGB Pro, shouldered plate and a tall light bar
def rgbpro_outline(w, h):
    return [(0, 0), (w, 0), (w, h), (w * 0.88, h), (w * 0.86, h - 1.6), (w * 0.14, h - 1.6), (w * 0.12, h), (0, h)]


def rgbpro_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.9, k1=1.1)
    for i in range(22):
        v = 1.0 + i * (h - 2.0) / 21
        a.line([(w * 0.70, v), (w - 1.0, v)], 0.16, pp.shade(S["spread"], 1.7), z=0.2, joins=False)
    logo(a, S, 7.0, h * 0.50, 6.0, S["ink"])
    a.text("VECTOR", 7.0, h * 0.22, 2.6, S["accent"], font="agency", ax="LEFT", space=1.5)
    a.text("RGB PRO", 30.0, h * 0.22, 2.6, S["ink"], font="agency", ax="LEFT", space=1.3)
    a.text(S["mem"], w * 0.66, h * 0.22, 2.2, S["accent"], font="agency", ax="RIGHT")


def rgbpro_bar(S, z0):
    hl = SPAN_Y / 2 - 3.0
    top = S["top"]
    return [(-hl, z0), (hl, z0), (hl, top - 2.0), (hl - 2.0, top), (-hl + 2.0, top), (-hl, top - 2.0)]


# -- riptide: G.Stride DDR4, red claw teeth along the top
def riptide_outline(w, h):
    pts = [(0, 0), (w, 0), (w, h - 7.0)]
    # five claws rising towards the left end, then a flat shoulder
    base = h - 7.0
    for i in range(5):
        u0 = w - 4.0 - i * 13.0
        pts += [(u0, base + i * 0.6), (u0 - 9.0, h - (4 - i) * 0.6), (u0 - 9.0, base + i * 0.6 + 1.2)]
    pts += [(w * 0.42, h), (2.0, h), (0, h - 2.0)]
    return pts


def riptide_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=280, k0=0.82, k1=1.15)
    a.poly([(0, 0), (w, 0), (w, h * 0.34), (w * 0.45, h * 0.34), (w * 0.40, h * 0.18), (0, h * 0.18)], S["band"], z=0.2)
    logo(a, S, 6.0, h * 0.62, 4.6, S["ink"])
    a.text("RIPTIDE V", 6.0, h * 0.38, 3.4, S["ink"], font="agency", ax="LEFT", space=1.3)
    a.text(S["mem"], w - 5.0, h * 0.17, 2.4, "#bfbfbf", font="agency", ax="RIGHT")


# -- tracer: Crux DDR4, a black plate with a raised badge and a red rake
def tracer_outline(w, h):
    return [(0, 0), (w, 0), (w, h - 3.0), (w - 3.0, h), (w * 0.60, h), (w * 0.56, h - 1.2), (3.0, h - 1.2), (0, h - 4.2)]


def tracer_relief(w, h):
    return [([(w * 0.04, h * 0.40), (w * 0.44, h * 0.40), (w * 0.48, h * 0.80), (w * 0.08, h * 0.80)], 0.4)]


def tracer_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, k0=0.9, k1=1.12)
    a.poly(tracer_relief(w, h)[0][0], S["band"], z=0.2)
    a.poly([(w * 0.62, 0), (w * 0.66, 0), (w * 0.74, h), (w * 0.70, h)], S["accent"], z=0.2)
    a.poly([(w * 0.68, 0), (w * 0.69, 0), (w * 0.77, h), (w * 0.76, h)], S["accent"], z=0.2)
    logo(a, S, w * 0.07, h * 0.60, 5.0, S["ink"])
    a.text("TRACER", w * 0.30, h * 0.60, 3.0, S["accent"], font="agency", ax="LEFT", space=1.4)
    a.text(S["mem"], w - 5.0, h * 0.20, 2.4, S["ink"], font="agency", ax="RIGHT")


# -- vulcan: TeamForge DDR4 low profile, red with grey angular blades
def vulcan_outline(w, h):
    return [(0, 0), (w, 0), (w, h - 2.0), (w * 0.78, h - 2.0), (w * 0.74, h), (w * 0.30, h), (w * 0.26, h - 2.0), (0, h - 2.0)]


def vulcan_art(a, S, w, h, rnd):
    brushed(a, w, h, S["spread"], rnd, n=220, k0=0.85, k1=1.12)
    a.poly([(w * 0.70, 0), (w, 0), (w, h - 2.0), (w * 0.78, h - 2.0)], S["band"], z=0.2)
    a.poly([(0, 0), (w * 0.08, 0), (w * 0.02, h - 2.0), (0, h - 2.0)], S["band"], z=0.2)
    a.line([(w * 0.70, 0), (w * 0.78, h - 2.0)], 0.4, S["accent"], z=0.3)
    logo(a, S, 9.0, h * 0.52, 4.6, S["ink"])
    a.text("VULCAN Z", 9.0, h * 0.24, 2.8, S["ink"], font="agency", ax="LEFT", space=1.4)
    a.text(S["mem"], w - 4.0, h * 0.22, 2.2, S["ink"], font="agency", ax="RIGHT")


def _none(*_):
    return []


STYLES = {
    "vector": dict(outline=vector_outline, art=vector_art, plate=lambda S: S["top"]),
    "vector_rgb": dict(outline=vector_rgb_outline, art=vector_rgb_art, plate=lambda S: S["top"] - 6.5,
                       bar=lambda S, z0: bar_flat(S, z0, S["top"], 2.0, 1.0)),
    "trine": dict(outline=trine_outline, art=trine_art, plate=lambda S: S["top"] - 7.0, bar=trine_bar),
    "flare": dict(outline=flare_outline, art=flare_art, plate=lambda S: S["top"]),
    "ferox": dict(outline=ferox_outline, art=ferox_art, plate=lambda S: S["top"]),
    "ferox_rgb": dict(outline=ferox_rgb_outline, art=ferox_rgb_art, plate=lambda S: S["top"] - 5.4, bar=ferox_rgb_bar),
    "crux_pro": dict(outline=crux_pro_outline, art=crux_pro_art, plate=lambda S: S["top"]),
    "delta": dict(outline=delta_outline, art=delta_art, plate=lambda S: S["top"] - 1.6, face_rgb=delta_face, label_y=-34.0,
                  bar=lambda S, z0: bar_flat(S, z0, S["top"], 0.8, 1.6)),
    "flux": dict(outline=flux_outline, art=flux_art, plate=lambda S: S["top"], reliefs=flux_relief, bar=flux_bar),
    "lpx": dict(outline=lpx_outline, art=lpx_art, plate=lambda S: S["top"]),
    "rgbpro": dict(outline=rgbpro_outline, art=rgbpro_art, plate=lambda S: S["top"] - 12.0, bar=rgbpro_bar),
    "riptide": dict(outline=riptide_outline, art=riptide_art, plate=lambda S: S["top"]),
    "tracer": dict(outline=tracer_outline, art=tracer_art, plate=lambda S: S["top"], reliefs=tracer_relief),
    "vulcan": dict(outline=vulcan_outline, art=vulcan_art, plate=lambda S: S["top"]),
}
SP_X = (2.15, 3.35)   # spreader plate from x0 to x1 (mm) on each side


# ---------------------------------------------------------------------------------------------- textures
def label_art(a, S, rnd, w=46.0, h=13.0):
    """The printed spec sticker: brand bar, capacity / speed / timings / voltage / part number, barcode."""
    dark = "#1a1b1e"
    a.rect(0, h - 1.8, w, h, dark, z=0.1)
    a.text(S["brand"].upper(), 1.2, h - 0.9, 1.25, "#f2f2f2", font="arialbd", ax="LEFT", space=1.1)
    kind = "ECC REGISTERED" if S["style"] == "rdimm" else "MEMORY"
    a.text(kind, w - 1.2, h - 0.9, 1.0, "#f2f2f2", font="arialbd", ax="RIGHT")
    unit = "MT/s"
    if S["style"] == "rdimm":
        l1 = f"{S['mem']}-{S['mts']}  RDIMM  {S['ranks']}"
    else:
        l1 = f"{(S['series'] + '  ') if S['series'] else ''}{S['mem']}"
    lines = [l1, f"{S['gb']}GB  {S['mts']}{unit}  CL{S['cl']}", f"{S['v']}   {S['pn']}"]
    for i, line in enumerate(lines):
        a.text(line, 1.2, h - 3.2 - i * 1.9, 1.35 if i == 0 else 1.15, "#141414",
               font="arialbd" if i == 0 else "narrowbd", ax="LEFT", fit=32)
    bx = 1.2
    while bx < 30.0:
        bw = rnd.choice([0.12, 0.12, 0.24, 0.36])
        a.rect(bx, 0.9, bx + bw, 3.6, "#111111", z=0.2)
        bx += bw + rnd.choice([0.12, 0.24])
    a.text("".join(str(rnd.randint(0, 9)) for _ in range(12)), 15.6, 0.45, 0.8, "#141414", font="ocr")
    a.text("MADE IN TAIWAN", 38.0, 2.0, 0.9, "#141414", font="narrowbd")
    a.ring(38.0, 6.0, 1.6, 1.9, "#141414", z=0.2)
    a.text("PASS", 38.0, 6.0, 0.9, "#141414", font="narrowbd")


def pcb_art(a, S, notch_y, h, rnd, bare):
    col = S.get("pcb", "#16181b")
    lighter = pp.shade(col, 1.35 if bare else 1.5)
    n_tr = 260 if bare else 90
    for _ in range(n_tr):
        x0 = rnd.uniform(2, LEN - 2)
        z0 = rnd.uniform(4.0, 7.0)
        z1 = rnd.uniform(8.0, h - 1.5) if bare else h
        pts = [(x0, z0), (x0, z0 + rnd.uniform(1, 3)), (x0 + rnd.choice([-1, 1]) * rnd.uniform(1, 4), z1)]
        a.line(pts, 0.12, lighter, z=0.1)
    for _ in range(200 if bare else 160):
        a.circle(rnd.uniform(2, LEN - 2), rnd.uniform(4.2, h - 1.0 if bare else 7.5), 0.18, pp.shade(col, 1.9), z=0.15, seg=8)
    for y in br.finger_positions(notch_y):
        u = y + LEN / 2
        a.rect(u - 0.3, 0.0, u + 0.3, 3.4, "#c9a24c", z=0.2)
    a.text("288P", 4.0, 5.2, 0.9, "#d8d8d0", font="narrowbd", ax="LEFT")
    if bare:
        silk = "#e9eee9"
        a.text(S["pn"][:14], LEN - 4.0, h - 2.0, 1.0, silk, font="narrowbd", ax="RIGHT")
        a.text("PCB 4B0A  E254845  94V-0", 4.0, h - 2.0, 0.85, silk, font="narrowbd", ax="LEFT")
        # chip outlines (silkscreen) behind the packages
        cw, chh = chip_size(S)
        zc = chip_zc(S)
        for y in chip_rows(S):
            a.frame_rect(y + LEN / 2 - cw / 2 - 0.6, zc - chh / 2 - 0.6, y + LEN / 2 + cw / 2 + 0.6, zc + chh / 2 + 0.6, 0.12, silk, z=0.18)


def chip_mark_art(a, S, w, h, rnd):
    ink = "#8e9096"
    a.text(S.get("chip_mark", S["brand"].upper()), 0.8, h - 1.4, 1.05, ink, font="arialbd", ax="LEFT")
    a.text(S.get("die", "D5 16Gb"), 0.8, h - 3.0, 0.85, ink, font="narrowbd", ax="LEFT")
    a.text("".join(rnd.choice("ABCDEFGHJKLMNPRSTUVWXYZ0123456789") for _ in range(8)), 0.8, h - 4.4, 0.8, ink, font="narrowbd", ax="LEFT")
    a.text("2438", 0.8, 1.2, 0.8, ink, font="narrowbd", ax="LEFT")
    a.circle(w - 1.2, 1.2, 0.45, pp.shade("#151517", 1.6), z=0.2)


SHORT = [("ram_", "cr_"), ("corvex", "cvx"), ("gstride", "gs"), ("kingsland", "kl"), ("teamforge", "tf"),
         ("crux", "cx"), ("volt", "vt"), ("white_rgb", "wrgb")]


def tex_name(rid):
    """The texture file (and tag) name, short enough that '<id>_<tag>#<tag>' fits Blender's 63 characters."""
    for a, b in SHORT:
        rid = rid.replace(a, b)
    return rid


def textures(S, notch_y):
    rid = tex_name(S["id"])
    bare = S["style"] in ("bare", "rdimm")
    h_pcb = pcb_h(S)
    at = pp.Atlas(2048, 1024, bg=S.get("spread", S.get("pcb")))
    rnd = random.Random(sum(map(ord, rid)))
    reg = {}
    if not bare:
        st = STYLES[S["style"]]
        span_z = st["plate"](S) - ZB
        r, uv, ctx = at.panel(SPAN_Y, span_z, 15.0, bg=S["spread"])
        reg["spread"] = uv
        with ctx as a:
            st["art"](a, S, SPAN_Y, span_z, rnd)
    ppm = 11.0 if bare else 7.5
    r, uv, ctx = at.panel(LEN, h_pcb, ppm, bg=S.get("pcb", "#16181b"))
    reg["pcb"] = uv
    with ctx as a:
        pcb_art(a, S, notch_y, h_pcb, rnd, bare)
    r, uv, ctx = at.panel(46.0, 13.0, 18.0, bg="#e9eaec")
    reg["label"] = uv
    with ctx as a:
        label_art(a, S, rnd)
    if bare:
        cw, chh = chip_size(S)
        r, uv, ctx = at.panel(cw, chh, 20.0, bg="#151517")
        reg["chip"] = uv
        with ctx as a:
            chip_mark_art(a, S, cw, chh, rnd)
        if S["style"] == "rdimm":
            r, uv, ctx = at.panel(12.0, 9.0, 20.0, bg="#151517")
            reg["rcd"] = uv
            with ctx as a:
                ink = "#8e9096"
                a.text("RCD", 0.8, 7.6, 1.1, ink, font="arialbd", ax="LEFT")
                a.text("D5RCD02" if S["mem"] == "DDR5" else "4RCD0229K", 0.8, 5.8, 0.9, ink, font="narrowbd", ax="LEFT")
                a.text("A1 2432", 0.8, 4.2, 0.85, ink, font="narrowbd", ax="LEFT")
                a.circle(1.2, 1.2, 0.45, "#2a2a2e", z=0.2)
    reg["edge_spread"] = at.swatch(pp.shade(S.get("spread", "#333333"), 0.9))
    reg["edge_pcb"] = at.swatch("#4a4a3c" if not bare else pp.shade(S["pcb"], 0.8))
    reg["chip_black"] = at.swatch("#151517")
    at.render(pp.tex_path(rid))
    pp.PREVIEW_TEX[rid] = (0.6, 0.38) if not bare else (0.0, 0.45)
    return rid, reg


# ---------------------------------------------------------------------------------------------- geometry
M_SIDE = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))    # local (a, b, c) -> model (y, z, x)
M_BAR = M_SIDE


def chip_size(S):
    if S["style"] == "rdimm":
        return (8.6, 11.0)
    return (10.0, 11.5)


def chip_zc(S):
    """Height (mm) of the DRAM packages' centre."""
    if S["style"] == "rdimm":
        return pcb_h(S) - 2.0 - chip_size(S)[1] * 0.5
    return 19.0


def chip_rows(S):
    """y centres (mm) of the DRAM packages on one face."""
    if S["style"] == "bare":
        return [-46.0, -26.0, 26.0, 46.0]
    n = S["chips_side"]
    pitch = 10.0 if n == 10 else 11.0
    gap = 16.0 if n == 10 else 15.0     # the RCD sits in the middle gap
    half = n // 2
    left = [-(gap / 2 + pitch * 0.5 + i * pitch) for i in range(half)]
    right = [-y for y in left]
    out = sorted(left + right)
    if n % 2:
        out.append(0.0)
    return out


def art_to_y(u, s):
    return (u - SPAN_Y / 2) * (-1 if s > 0 else 1)


def side_pts(poly, s, z_off):
    return [(art_to_y(u, s) * MM, (v + z_off) * MM) for u, v in poly]


def point_in(poly, p):
    x, y = p
    inside = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            inside = not inside
    return inside


def build_pcb(k, T, reg, S, notch_y):
    h = pcb_h(S)
    hz = h * MM * 0.5
    pmap = pp.MultiMap([
        pp.Planar(reg["pcb"], (0, 0, hz), (1, 0, 0), (0, 0, 1), (LEN * MM, h * MM)),
        pp.Planar(reg["pcb"], (0, 0, hz), (-1, 0, 0), (0, 0, 1), (LEN * MM, h * MM)),
        reg["edge_pcb"]])
    outline = [(y * MM, z * MM) for y, z in pcb_outline(notch_y, h)]
    pp.prism(k[T], [outline], -PCB_T * MM * 0.5, PCB_T * MM * 0.5, M=M_SIDE, uv=pmap)
    for y in br.finger_positions(notch_y):
        for s in (-1, 1):
            pp.quad(k["gold"], (s * (PCB_T * MM * 0.5 + 0.00002), y * MM, 0.0018), (0.00058, 0.0034), normal=(s, 0, 0), up=(0, 0, 1))
    # SMD resistors and caps in the band above the fingers
    rnd = random.Random(3)
    for s in (-1, 1):
        y = -LEN / 2 + 5.0
        while y < LEN / 2 - 5.0:
            if abs(y - notch_y) > 2.0:
                z = rnd.choice([4.6, 5.6])
                br._smd_side(k, s * (PCB_T * 0.5) * MM, y * MM, z * MM, s, "chip_black" if rnd.random() < 0.55 else "ceramic")
            y += rnd.uniform(1.6, 3.2)


def marked_box(k, T, region, swatch, s, y, z, w, hh, t, x_base):
    """A package on a DIMM face (normal s*x) whose outer face carries `region`."""
    xc = s * (x_base + t * 0.5)
    m = pp.MultiMap([pp.Planar(region, (s * (x_base + t), y, z), (s, 0, 0), (0, 0, 1), (w, hh)), swatch])
    pp.box(k[T], (xc, y, z), (t, w, hh), bevel=0.00012, uv=m)


def build_spreader(k, T, reg, S):
    st = STYLES[S["style"]]
    plate_top = st["plate"](S)
    span_z = plate_top - ZB
    x0, x1 = SP_X
    zc = (ZB + plate_top) * 0.5 * MM
    outline = st["outline"](SPAN_Y, span_z)
    reliefs = st.get("reliefs", _none)(SPAN_Y, span_z)
    face_rgb = st.get("face_rgb", _none)(SPAN_Y, span_z)
    for s in (-1, 1):
        smap = pp.MultiMap([pp.Planar(reg["spread"], (0, 0, zc), (s, 0, 0), (0, 0, 1), (SPAN_Y * MM, span_z * MM)),
                            reg["edge_spread"]])
        za, zb = (x0, x1) if s > 0 else (-x1, -x0)
        pp.prism(k[T], [side_pts(outline, s, ZB)], za * MM, zb * MM, M=M_SIDE, uv=smap)
        for poly, hgt in reliefs:
            za, zb = (x1, x1 + hgt) if s > 0 else (-x1 - hgt, -x1)
            pp.prism(k[T], [side_pts(poly, s, ZB)], za * MM, zb * MM, M=M_SIDE, uv=smap)
        for poly, hgt in face_rgb:
            za, zb = (x1 - 0.2, x1 + hgt) if s > 0 else (-x1 - hgt, -x1 + 0.2)
            pp.prism(k["rgb"], [side_pts(poly, s, ZB)], za * MM, zb * MM, M=M_SIDE)
    # chips and thermal pads under the plates (seen from the ends)
    for i in range(8):
        y = (-LEN / 2 + 9.5 + i * (LEN - 19.0) / 7) * MM
        pp.box(k["chip_black"], ((PCB_T * 0.5 + 0.5) * MM, y, 16.5 * MM), (1.0 * MM, 10.0 * MM, 11.5 * MM), bevel=0.0001)
    pp.box(k["thermal_pad"], ((PCB_T * 0.5 + 1.0 + (x0 - PCB_T * 0.5 - 1.0) / 2) * MM, 0, 16.5 * MM),
           ((x0 - PCB_T * 0.5 - 1.0) * MM, (LEN - 12.0) * MM, 12.0 * MM))
    pp.box(k["thermal_pad"], (-(PCB_T * 0.5 + (x0 - PCB_T * 0.5) / 2) * MM, 0, 16.5 * MM),
           ((x0 - PCB_T * 0.5) * MM, (LEN - 12.0) * MM, 12.0 * MM))
    if S["mem"] == "DDR5":
        br._chip_side(k, 1, 0.0, 0.0050, 0.0040, 0.0030)   # the PMIC peeks out under the plate
    # the bridge joining both plates, just under the lowest point of the top edge
    low = min(v for u, v in outline if 0.5 < v) + ZB
    white = pp.rgb(S["spread"])[0] > 0.7
    pp.box(k[T], (0, 0, (low - 0.7) * MM), (2 * x0 * MM, (SPAN_Y - 1.0) * MM, 1.4 * MM), uv=reg["edge_spread"])
    top = plate_top
    bar = st.get("bar")
    if bar:
        sil = bar(S, plate_top - 0.6)
        bw = 2 * x1 - 0.5
        pp.prism(k["rgb"], [[(y * MM, z * MM) for y, z in sil]], -bw * 0.5 * MM, bw * 0.5 * MM, M=M_BAR)
        top = max(z for _, z in sil)
        cap = "white_plastic" if white else "alu_dark"
        ymax = max(abs(y) for y, _ in sil)
        if S["style"] in ("flux", "rgbpro", "vector_rgb"):
            for e in (-1, 1):
                pp.box(k[cap], (0, e * (ymax + 1.0) * MM, (plate_top + (top - plate_top) * 0.5 - 0.3) * MM),
                       ((2 * x1 + 0.4) * MM, 2.0 * MM, (top - plate_top + 0.6) * MM), bevel=0.0004)
        if S["style"] == "rgbpro":
            # the dark rim around the diffuser's top
            pp.box(k[cap], (0, 0, (top - 0.4) * MM), ((bw + 0.6) * MM, (2 * ymax - 3.0) * MM, 0.8 * MM), bevel=0.0002)
    # the spec sticker on the +x plate (over a relief panel if one sits under it)
    lc = (st.get("label_y", -22.0), 13.5)
    lift = 0.0
    lu = (-lc[0] + SPAN_Y / 2, lc[1] - ZB)   # its centre in the +x face's art coordinates
    for poly, hgt in reliefs:
        if point_in(poly, lu):
            lift = max(lift, hgt)
    if span_z < 15.0:
        lc = (-22.0, ZB + span_z * 0.5)
    return top, lc, (x1 + lift + 0.03) * MM


def build_bare(k, T, reg, S, notch_y):
    """Bare desktop stick (Crux 8 GB): 4 DRAM packages on +x, PMIC and SPD hub; the sticker on the -x face."""
    cw, chh = chip_size(S)
    t = 1.0
    x_base = PCB_T * 0.5
    for y in chip_rows(S):
        marked_box(k, T, reg["chip"], reg["chip_black"], 1, y * MM, chip_zc(S) * MM, cw * MM, chh * MM, t * MM, x_base * MM)
    # PMIC with its inductors and caps, SPD hub
    br._chip_side(k, 1, 0.0, 0.0105, 0.0045, 0.0045)
    for e in (-1, 1):
        pp.box(k["chip_black"], ((x_base + 0.6) * MM, e * 5.2 * MM, 10.5 * MM), (1.2 * MM, 2.5 * MM, 2.0 * MM), bevel=0.0002)
        pp.box(k["ceramic"], ((x_base + 0.4) * MM, e * 7.8 * MM, 10.0 * MM), (0.8 * MM, 1.6 * MM, 0.8 * MM))
    br._chip_side(k, 1, 12.0 * MM, 0.0095, 0.0022, 0.0018)
    rnd = random.Random(7)
    for y0 in chip_rows(S):
        for j in range(6):
            pp.box(k["ceramic"], ((x_base + 0.25) * MM, (y0 + rnd.uniform(-4, 4)) * MM, rnd.uniform(9.0, 12.0) * MM), (0.5 * MM, 1.0 * MM, 0.5 * MM))
    return pcb_h(S), (0.0, 19.0), -(x_base + 0.03) * MM


def build_rdimm(k, T, reg, S, notch_y):
    """Registered ECC: DRAM packages on both faces, the RCD in the middle of +x, PMIC (DDR5), SPD hub, thermal
    sensors, and the sticker on -x over the middle packages."""
    h = pcb_h(S)
    cw, chh = chip_size(S)
    t = 1.0 + 0.45 * (S["stack"] - 1)
    x_base = PCB_T * 0.5
    zc = chip_zc(S)
    for s in (-1, 1):
        for y in chip_rows(S):
            marked_box(k, T, reg["chip"], reg["chip_black"], s, y * MM, zc * MM, cw * MM, chh * MM, t * MM, x_base * MM)
    # RCD: the register clock driver in the middle gap of the front
    marked_box(k, T, reg["rcd"], reg["chip_black"], 1, 0.0, (zc - 0.5) * MM, 12.0 * MM * 0.85, 9.0 * MM * 0.85, 1.0 * MM, x_base * MM)
    # data buffers / decoupling caps around the RCD
    rnd = random.Random(11)
    for s in (-1, 1):
        for y0 in chip_rows(S) + [0.0]:
            for j in range(3):
                pp.box(k["ceramic"], (s * (x_base + 0.25) * MM, (y0 + rnd.uniform(-4, 4)) * MM, (zc - chh * 0.5 - rnd.uniform(1.0, 2.6)) * MM),
                       (0.5 * MM, 1.0 * MM, 0.5 * MM))
    if S["mem"] == "DDR5":
        # PMIC (QFN) at the +y end with its inductors
        py = 52.0
        pp.box(k["chip_black"], ((x_base + 0.45) * MM, py * MM, 9.5 * MM), (0.9 * MM, 4.5 * MM, 4.5 * MM), bevel=0.00015)
        for j, (dy, dz) in enumerate(((-5.0, 9.0), (5.0, 9.0), (-5.0, 12.2), (5.0, 12.2))):
            pp.box(k["chip_black"], ((x_base + 0.7) * MM, (py + dy) * MM, dz * MM), (1.4 * MM, 3.0 * MM, 2.6 * MM), bevel=0.0002)
        # SPD hub with integrated sensor in the middle, two thermal sensors near the ends
        br._chip_side(k, 1, 0.0, 0.0090, 0.0030, 0.0025)
        for e in (-1, 1):
            br._chip_side(k, 1, e * 40.0 * MM, (zc - chh * 0.5 - 1.6) * MM, 0.0020, 0.0016)
    else:
        br._chip_side(k, 1, 30.0 * MM, 0.0090, 0.0030, 0.0040)   # SPD EEPROM with thermal sensor
    return h, (0.0, zc), -(x_base + t + 0.03) * MM


def build(rid):
    S = BY_ID[rid]
    notch_y = notch_of(S)
    c.reset()
    tex, reg = textures(S, notch_y)
    T = "tex_" + tex
    root = c.root(rid)
    k = pp.Kit("ram")
    build_pcb(k, T, reg, S, notch_y)
    if S["style"] == "bare":
        top, lc, lx = build_bare(k, T, reg, S, notch_y)
    elif S["style"] == "rdimm":
        top, lc, lx = build_rdimm(k, T, reg, S, notch_y)
    else:
        top, lc, lx = build_spreader(k, T, reg, S)
    # the spec sticker (+x normal on spreaders, -x on bare and server sticks)
    nx = 1 if lx > 0 else -1
    pp.quad(k[T], (lx, lc[0] * MM * nx, lc[1] * MM), (0.046, 0.013), normal=(nx, 0, 0), up=(0, 0, 1), region=reg["label"])
    k.finish(root)

    meta = f"y={notch_y * MM:.4f},mem={S['mem']}"
    if S["style"] == "rdimm":
        meta += ",type=RDIMM,ecc=1"
    c.anchor("A_NOTCH_0", (0, notch_y * MM, 0.0), (0.004, 0.0025, 0.004), root, meta=meta)
    if S["style"] in ("bare", "rdimm"):
        t = 1.0 + 0.45 * (S.get("stack", 1) - 1)
        wx = (PCB_T * 0.5 + t + 0.4) * 2
    else:
        wx = (SP_X[1] + 0.4) * 2
    c.anchor("A_HIT_0", (0, 0, top * MM * 0.5), (wx * MM, LEN * MM, top * MM), root)
    c.join_by_tag(root, "ram")
    c.export(root, rid)
    pp.report(root)
    return root


def previews(rid, root):
    pp.preview(root, rid, views=((70, 25), (-60, 30), (95, 60)), size=(960, 720), dist=0.24, zup=True)
    pp.preview(root, rid, views=((80, 12),), size=(960, 720), dist=0.085, target=(0, -0.035, 0.012), start=3, zup=True)


def report_lines(root):
    lines = [f"REPORT {root.name} tris={pp.tri_count(root)} objects={sum(1 for o in c.descendants(root) if o.type == 'MESH')}"]
    for o in sorted(c.descendants(root), key=lambda o: o.name):
        if o.type == "MESH":
            n = sum(len(p.vertices) - 2 for p in o.data.polygons)
            lines.append(f"MESH {root.name} {o.name} tris={n}")
    for o in sorted(c.descendants(root), key=lambda o: o.name):
        if o.type == "EMPTY" and o.name.startswith("A_"):
            p = pp.unconv(o.matrix_world.translation)
            lines.append(f"ANCHOR {root.name} {o.name} pos=({p.x:.5f},{p.y:.5f},{p.z:.5f}) size={o.get('size')} meta={o.get('meta', '')}")
    return lines


def write_report(blocks):
    """Merges the rebuilt ids' blocks into Logs/ModelPreviews/cat_ram_report.txt (catalogue order)."""
    old = {}
    if os.path.isfile(REPORT_TXT):
        for line in open(REPORT_TXT, encoding="utf-8"):
            parts = line.split()
            if len(parts) > 1:
                old.setdefault(parts[1], []).append(line.rstrip("\n"))
    old.update(blocks)
    with open(REPORT_TXT, "w", encoding="utf-8", newline="\n") as f:
        for S in CAT:
            for line in old.get(S["id"], []):
                f.write(line + "\n")


LOOKS = {
    "vector": "black aluminium spreader with a ribbed panel",
    "vector_rgb": "white spreader with a full-length RGB light bar",
    "trine": "brushed-silver and black spreader with a winged RGB light bar",
    "flare": "low-profile black spreader that clears any tower cooler",
    "ferox": "black angular spreader",
    "ferox_rgb": "white angular spreader with a wave RGB light bar",
    "crux_pro": "plain black aluminium spreader",
    "bare": "bare green PCB, no heat spreader",
    "delta": "white spreader with a wide triangular RGB diffuser",
    "flux": "dark spreader with a raked relief panel and RGB diffuser",
    "lpx": "low-profile black spreader with the stepped fin top",
    "rgbpro": "black spreader with a tall ten-zone RGB light bar",
    "riptide": "red spreader with the claw-tooth top",
    "tracer": "black spreader with a red rake",
    "vulcan": "low-profile red spreader",
    "rdimm": "registered ECC server module: RCD, SPD hub and thermal sensors on a bare PCB",
}
POWER_W = {"DDR5": 5, "DDR4": 3}


def catalog_entry(S):
    rd = S["style"] == "rdimm"
    kit = S["kit"]
    cap = f"{S['gb']} GB" if kit == 1 else f"{kit} x {S['gb']} GB"
    cl = S["cl"].split("-")[0]
    desc = f"{cap} {S['mem']}-{S['mts']} CL{cl}: {LOOKS[S['style']]}."
    specs = dict(kit=f"{kit}x{S['gb']}GB", speed_mts=S["mts"], cas=int(cl), timings=S["cl"], voltage=float(S["v"].rstrip("V")),
                 height_mm=S["top"], spreader=S["style"] not in ("bare", "rdimm"))
    if rd:
        specs.update(ecc=True, registered=True, ranks=S["ranks"])
    power = (13 if S["gb"] >= 128 else 10 if S["mem"] == "DDR5" else 6) if rd else POWER_W[S["mem"]]
    return dict(id=S["id"], model=S["id"], brand=S["brand"], name=S["name"], category="RAM",
                price=S["price"], power_w=power, color=S["color"], rgb=S["rgb"],
                analog=S["analog"] + " (docs only, never shown in game)", desc=desc, specs=specs,
                game=dict(mem=S["mem"], ram_gb=S["gb"], per_box=kit, perf=0),
                contract="rdimm" if rd else "ram", new_contract=rd)


def write_catalog():
    import json
    path = os.path.join(c.PROJECT, "docs", "catalog", "ram.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump([catalog_entry(S) for S in CAT], f, indent=2)
        f.write("\n")


def main():
    argv = c.args()
    nopreview = "--nopreview" in argv
    ids = [a for a in argv if not a.startswith("--")] or [s["id"] for s in CAT]
    blocks = {}
    for rid in ids:
        root = build(rid)
        blocks[rid] = report_lines(root)
        if not nopreview:
            previews(rid, root)
    os.makedirs(c.PREVIEWS, exist_ok=True)
    write_report(blocks)
    write_catalog()


if __name__ == "__main__":
    main()
