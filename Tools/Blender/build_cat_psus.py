r"""
build_cat_psus.py - catalogue 15: power supplies (10 desktop ATX, 1 SFX, 2 server CRPS modules).

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_cat_psus.py -- [ids...] [--nopreview]

With no ids it builds every unit (and the SFX-to-ATX bracket). Each writes Assets/Resources/Models/<id>.fbx, its
texture tex_<id>.png, previews Logs/ModelPreviews/<id>_<n>.png and Logs/ModelPreviews/<id>_report.txt; the run also
writes docs/catalog/psus.json and Logs/ModelPreviews/cat_psus_report.txt (all the reports in one file).

ATX units follow the psu_450 / psu_750 contract (build_psu.py, MODEL_PIPELINE.md section 2): origin at the box centre
of the 140 mm unit, x = depth with the rear face at +0.07, y = height 0.086 with the fan at -y, z = width 0.15.
Longer units keep the rear face at +0.07 and grow towards -x. The rear-face anchors (A_SWITCH_PSU_0, A_PORT_C13_0,
A_SCREW_PH2_0..3) sit exactly where psu_450 has them. The SFX unit and the CRPS modules have new contracts (see
docs/reports/cat_psus.md). build_psu.py itself is not changed: this script imports its rear-face constants and
its socket helper.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import parts_fan as pf  # noqa: E402
import build_psu as BP  # noqa: E402
import cat_psus_art as art  # noqa: E402
from mathutils import Matrix, Vector as V  # noqa: E402

PREVIEW = [True]
SH = BP.SH
M_XZ, M_ZY, M_ZX = BP.M_XZ, BP.M_ZY, BP.M_ZX
box = BP.box

# ---------------------------------------------------------------------------------------------------- form factors
ATX = dict(x1=0.070, w2=0.075, h2=0.043, screws=BP.SCREWS, inlet=BP.INLET, switch=BP.SWITCH,
           honey=(-0.0635, 0.0265, -0.0365, 0.0375), panel=(-0.066, -0.030, 0.066, 0.034), fan_t=0.025)
# SFX 125 (w) x 63.5 (h) x 100 (d): rear face at x +0.05, the 92 mm fan at -y. Screw holes as on the SFX rear panel.
SFX = dict(x1=0.050, w2=0.0625, h2=0.03175, screws=[(-0.0565, 0.0255), (0.0565, 0.0255), (-0.0565, -0.0255),
                                                   (0.0405, -0.0255)],
           inlet=(0.033, -0.0045), switch=(0.033, 0.0185), honey=(-0.052, 0.0155, -0.026, 0.027),
           panel=(-0.056, -0.0255, 0.056, 0.0265), fan_t=0.020)

# ---------------------------------------------------------------------------------------------------- the catalogue
# conns = game data (connectors on the cables): eps8, pcie8, p16 (12V-2x6), sata.
# rows = the modular panel, row by row (top first): atx, cpu, pcie, p16, sata. A socket may feed 2 connectors.
UNITS = [
    dict(id="psu_ampere_550_bronze", brand="Ampere", series="Basic Power", name="Ampere BP-550 550 W Bronze",
         code="BP-550B", watts=550, tier="BRONZE", eff="85%", modular="none", depth=0.140, paint="paint_black",
         style="Ampere", fan=0.12, blades=7, grille="wire", conns=(1, 2, 0, 6), price=49, color="#1A1A1B", rgb=False,
         analog="Corsair CV550 / EVGA 550 BR", amps="8-4A", c335="110W",
         desc="A no-frills 550 W Bronze unit with fixed cables for a first build.",
         side="AMPERE", side_font="eras"),
    dict(id="psu_corvex_cx650m", brand="Corvex", series="CX-M Series", name="Corvex CX650M 650 W Bronze",
         code="CX650M", watts=650, tier="BRONZE", eff="85%", modular="semi", depth=0.140, paint="paint_black",
         style="Corvex", fan=0.12, blades=7, grille="wire", conns=(1, 4, 0, 8), price=75, color="#1A1A1B", rgb=False,
         analog="Corsair CX650M", amps="10-5A", c335="120W",
         rows=[["pcie", "pcie"], ["sata", "sata", "sata"]], feeds={"pcie": 2, "sata": [3, 3, 2]},
         desc="Semi-modular 650 W Bronze: the 24-pin and CPU cables are fixed, the rest plug in.",
         side="CORVEX", side_font="franklin"),
    dict(id="psu_seastar_gx850", brand="Seastar", series="Apex GX", name="Seastar Apex GX-850 850 W Gold",
         code="SSR-850FX", watts=850, tier="GOLD", eff="90%", modular="full", depth=0.140, paint="paint_black",
         style="Seastar", fan=0.12, blades=9, grille="hex", conns=(2, 6, 0, 10), price=130, color="#161617",
         rgb=False, analog="Seasonic Focus GX-850", amps="10-5A", c335="120W",
         rows=[["atx", "sata", "sata"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"], ["sata", "sata", "sata"]],
         feeds={"pcie": [2, 2, 1, 1], "sata": 2},
         desc="Fully modular 850 W Gold with a quiet hybrid fan mode and a ten-year warranty.",
         side="SEASTAR", side_font="segoe_black"),
    dict(id="psu_seastar_px1000_white", brand="Seastar", series="Summit PX", name="Seastar Summit PX-1000 1000 W Platinum White",
         code="SSR-1000PD2", watts=1000, tier="PLATINUM", eff="92%", modular="full", depth=0.160, paint="paint_white",
         style="Seastar_white", fan=0.135, blades=9, grille="slots", conns=(2, 4, 1, 8), price=230, color="#EDEDEB",
         rgb=False, analog="Seasonic Vertex PX-1000 (white)", atx3="3.1", amps="12-6A", c335="125W",
         rows=[["atx", "p16"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"], ["sata", "sata", "sata", "sata"]],
         feeds={"sata": 2},
         desc="White 1000 W Platinum, ATX 3.1 with a native 12V-2x6 cable for the newest graphics cards.",
         side="SEASTAR", side_font="segoe_black", hub_bg="#e8e8e6", hub_ink="#202226", white_fan=True),
    dict(id="psu_corvex_rm850x_white", brand="Corvex", series="RMx Series", name="Corvex RM850x 850 W Gold White",
         code="RM850x", watts=850, tier="GOLD", eff="90%", modular="full", depth=0.160, paint="paint_white",
         style="Corvex_white", fan=0.135, blades=9, grille="hex", conns=(3, 4, 1, 14), price=140, color="#EDEDEB",
         rgb=False, analog="Corsair RM850x (2024) White", atx3="3.1", amps="10-5A", c335="150W",
         rows=[["atx", "p16"], ["cpu", "cpu", "cpu", "pcie", "pcie", "pcie"], ["pcie", "sata", "sata", "sata", "sata"]],
         feeds={"sata": [4, 4, 3, 3]},
         desc="Silent, white, fully modular 850 W Gold with a 12V-2x6 cable; the fan stops at low load.",
         side="CORVEX", side_font="franklin", hub_bg="#e8e8e6", hub_ink="#202226", white_fan=True),
    dict(id="psu_hush_pp12m_750", brand="Hush", series="Clean Power 12 M", name="Hush Clean Power 12 M 750 W Gold",
         code="BN343", watts=750, tier="GOLD", eff="90%", modular="full", depth=0.160, paint="paint_black",
         style="Hush", fan=0.12, blades=7, grille="wire", conns=(2, 2, 1, 6), price=100, color="#141414", rgb=False,
         analog="be quiet! Pure Power 12 M 750W", atx3="3.0", amps="10-5A", c335="110W",
         rows=[["atx", "p16"], ["cpu", "cpu", "pcie", "pcie"], ["sata", "sata"]], feeds={"sata": 3},
         desc="Quiet 750 W Gold with a 12V-2x6 cable, black with brushed silver stripes.",
         side="hush!", side_font="segoe", stripes=True),
    dict(id="psu_hush_dp13_1200", brand="Hush", series="Shadow Power 13", name="Hush Shadow Power 13 1200 W Titanium",
         code="BN335", watts=1200, tier="TITANIUM", eff="94%", modular="full", depth=0.175, paint="paint_black",
         style="Hush", fan=0.135, blades=7, grille="ring", conns=(2, 6, 1, 12), price=330, color="#141414", rgb=False,
         analog="be quiet! Dark Power 13 / Dark Power Pro 13 (Titanium)", atx3="3.0", amps="15-8A", c335="130W",
         rows=[["atx", "p16"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"], ["pcie", "pcie", "sata", "sata", "sata", "sata"]],
         feeds={"sata": 3},
         desc="Flagship 1200 W Titanium, near-silent, with a brushed silver fan ring.",
         side="hush!", side_font="segoe", side_plate=True),
    dict(id="psu_mako_a850g", brand="Mako", series="Forge A-G", name="Mako Forge A850G PCIE5 850 W Gold",
         code="A850G-P5", watts=850, tier="GOLD", eff="90%", modular="full", depth=0.140, paint="paint_black",
         style="Mako", fan=0.135, blades=9, grille="slots", conns=(2, 4, 1, 8), price=120, color="#141414", rgb=False,
         analog="MSI MPG A850G PCIE5", atx3="3.1", amps="12-6A", c335="120W",
         rows=[["atx", "p16"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"], ["sata", "sata", "sata", "sata"]],
         feeds={"sata": 2},
         desc="850 W Gold, ATX 3.1 with a native 12V-2x6 cable, black with a red trim.",
         side="MAKO", side_font="franklin", trim="red"),
    dict(id="psu_aegis_1200p", brand="Aegis", series="Valkyr", name="Aegis Valkyr 1200P 1200 W Platinum",
         code="AV-1200P2", watts=1200, tier="PLATINUM", eff="92%", modular="full", depth=0.190, paint="paint_black",
         style="Aegis", fan=0.135, blades=9, grille="wire", conns=(2, 6, 1, 12), price=330, color="#121214",
         rgb=True, analog="ASUS ROG Thor 1200P2", atx3="3.0", amps="15-7.5A", c335="125W",
         rows=[["atx", "p16"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"], ["pcie", "pcie", "sata", "sata", "sata", "sata"]],
         feeds={"sata": 3},
         desc="1200 W Platinum with an RGB side panel and an OLED power read-out.",
         side="AEGIS", side_font="agency", armour=True, label_side=-1),
    dict(id="psu_corvex_ax1600i", brand="Corvex", series="AXi Series", name="Corvex AX1600i 1600 W Titanium",
         code="AX1600i", watts=1600, tier="TITANIUM", eff="94%", modular="full", depth=0.200, paint="paint_black",
         style="Corvex", fan=0.14, blades=9, grille="hex", conns=(2, 10, 0, 16), price=580, color="#141414",
         rgb=False, analog="Corsair AX1600i", amps="15-10A", c335="150W",
         rows=[["atx", "sata", "sata"], ["cpu", "cpu", "pcie", "pcie", "pcie", "pcie"],
               ["pcie", "pcie", "pcie", "pcie", "pcie", "pcie"], ["sata", "sata", "sata", "sata", "sata"]],
         feeds={"sata": [4, 4, 2, 2, 2, 1, 1]},
         desc="The 1600 W Titanium flagship with digital control, 200 mm deep.",
         side="CORVEX", side_font="franklin", side_plate=True),
    dict(id="psu_corvex_sf750", brand="Corvex", series="SF Series", name="Corvex SF750 750 W Platinum SFX",
         code="SF750", watts=750, tier="PLATINUM", eff="92%", modular="full", depth=0.100, paint="paint_black",
         style="Corvex", fan=0.092, blades=9, grille="perf", conns=(2, 4, 0, 8), price=180, color="#141414",
         rgb=False, analog="Corsair SF750 Platinum", amps="10-5A", c335="120W", form="sfx",
         rows=[["atx"], ["cpu", "cpu", "pcie", "pcie"], ["sata", "sata", "sata"]], feeds={"pcie": 2, "sata": [3, 3, 2]},
         desc="Tiny SFX 750 W Platinum for small-form-factor builds; an ATX bracket comes in the box.",
         side="CORVEX", side_font="franklin"),
]
CRPS = [
    dict(id="psu_strata_crps_800", brand="Strata", name="Strata 800 W Platinum CRPS Hot-Plug PSU", code="SPS-800P",
         watts=800, tier="PLATINUM", eff="94%", ac="100-240V~ 10-5A 50/60Hz", dc="+12V 66.7A, +12Vsb 3A",
         body="alu", latch_col="#e07a1e", price=150, color="#B8BCC2",
         analog="Dell / HPE 800 W Platinum CRPS hot-plug PSU",
         desc="Hot-swap 800 W Platinum server supply; slides into a redundant PSU bay."),
    dict(id="psu_strata_crps_1600", brand="Strata", name="Strata 1600 W Titanium CRPS Hot-Plug PSU", code="SPS-1600T",
         watts=1600, tier="TITANIUM", eff="96%", ac="200-240V~ 10A 50/60Hz", dc="+12V 133A, +12Vsb 3.5A",
         body="steel_dark", latch_col="#2f7bd6", price=320, color="#4A4D52",
         analog="Dell / HPE 1600 W Titanium CRPS hot-plug PSU",
         desc="Hot-swap 1600 W Titanium server supply for GPU and storage servers."),
]
BY_ID = {u["id"]: u for u in UNITS + CRPS}
BRACKET = "psu_bracket_sfx_atx"

KIND = {"atx": "atx24", "cpu": "cpu8", "pcie": "pcie8", "p16": "12v2x6", "sata": "sata6"}
ANAME = {"atx": "A_PORT_MOD_ATX", "cpu": "A_PORT_MOD_CPU", "pcie": "A_PORT_MOD_PCIE", "p16": "A_PORT_MOD_12V2X6",
         "sata": "A_PORT_MOD_SATA"}
TEXT = {"atx": "MB / ATX 24-PIN", "cpu": "CPU", "pcie": "PCIe", "p16": "12V-2x6", "sata": "SATA/PERIF"}


def geo_of(s):
    g = dict(SFX if s.get("form") == "sfx" else ATX)
    g["x0"] = g["x1"] - s["depth"]
    g["xc"] = g["x1"] - s["depth"] / 2
    g["hx"] = s["depth"] / 2
    if s["modular"] == "semi":
        g["panel"] = (-0.016, -0.030, 0.066, 0.034)
        g["exit"] = (0.042, 0.010)  # (z, y) of the fixed bundle
    else:
        g["exit"] = (0.030, 0.024)
    return g


def layout(s, g):
    """The modular panel: [(anchor, key, u, v, text, w, h)] in panel coordinates (u = -z, v = y)."""
    rows = s.get("rows")
    if not rows:
        return []
    u0, v0, u1, v1 = g["panel"]
    n = len(rows)
    top, bot = v1 - 0.0018, v0 + 0.0048  # room for the hint line at the bottom
    pitch = (top - bot) / n
    out, count = [], {}
    for r, row in enumerate(rows):
        sizes = [BP.sock_size(KIND[k]) for k in row]
        gaps = [0.0030 if (i and row[i] == row[i - 1]) else (0.0055 if i else 0.0) for i in range(len(row))]
        width = sum(w for w, h in sizes) + sum(gaps)
        x = (u0 + u1) / 2 - width / 2
        vc = top - pitch * (r + 0.5) + 0.0016
        for i, k in enumerate(row):
            w, h = sizes[i]
            x += gaps[i]
            idx = count.get(k, 0)
            count[k] = idx + 1
            out.append((f"{ANAME[k]}_{idx}", k, x + w / 2, vc, TEXT[k], w, h))
            x += w
    return out


def feeds_of(s, key, count):
    f = s.get("feeds", {}).get(key)
    if f is None:
        return [1] * count
    if isinstance(f, int):
        return [f] * count
    return list(f) + [1] * (count - len(f))


# ---------------------------------------------------------------------------------------------------- geometry bits

def perforation(style, cx, r_out, r_in):
    """Holes (2D, in the pan's (x, z) plane) for a stamped fan grille."""
    holes = []
    if style == "hex":
        hr, pitch = 0.0027, 0.0060
        rowh = pitch * math.sqrt(3) / 2
        j = -int(r_out / rowh) - 1
        while j * rowh <= r_out + rowh:
            z = j * rowh
            off = pitch / 2 if j % 2 else 0.0
            i = -int(r_out / pitch) - 1
            while i * pitch <= r_out + pitch:
                x = i * pitch + off
                d = math.hypot(x, z)
                if r_in + hr < d < r_out - hr:
                    holes.append(pb.hexagon2(cx + x, z, hr, math.pi / 6))
                i += 1
            j += 1
    elif style == "perf":
        hr, pitch = 0.0017, 0.0042
        rowh = pitch * math.sqrt(3) / 2
        j = -int(r_out / rowh) - 1
        while j * rowh <= r_out + rowh:
            z = j * rowh
            off = pitch / 2 if j % 2 else 0.0
            i = -int(r_out / pitch) - 1
            while i * pitch <= r_out + pitch:
                x = i * pitch + off
                d = math.hypot(x, z)
                if r_in + hr < d < r_out - hr:
                    holes.append(pb.circle2(cx + x, z, hr, 12))
                i += 1
            j += 1
    elif style == "slots":
        r = r_in + 0.002
        band, web = 0.0042, 0.0018
        ring = 0
        while r + band < r_out:
            nseg = max(4, int(pb.TAU * r / 0.030))
            br = web / r
            a_off = (ring % 2) * math.pi / nseg
            for k in range(nseg):
                a0 = a_off + pb.TAU * k / nseg + br / 2
                a1 = a_off + pb.TAU * (k + 1) / nseg - br / 2
                m = 10
                pts = [(cx + (r + band) * math.cos(a0 + (a1 - a0) * t / m), (r + band) * math.sin(a0 + (a1 - a0) * t / m))
                       for t in range(m + 1)]
                pts += [(cx + r * math.cos(a1 - (a1 - a0) * t / m), r * math.sin(a1 - (a1 - a0) * t / m))
                        for t in range(m + 1)]
                holes.append(pts)
            r += band + web
            ring += 1
    return holes


def housing(m, s, g, at, TEX):
    P = s["paint"]
    x0, x1, xc, hx, W2, H2 = g["x0"], g["x1"], g["xc"], g["hx"], g["w2"], g["h2"]
    D = s["depth"]
    r = 0.002
    # cover: top and both sides, rounded along the top edges
    box(m, P, (x0 + 0.0002, H2 - SH, -W2 + r), (x1 - 0.0002, H2, W2 - r))
    for sz in (-1, 1):
        box(m, P, (x0 + 0.0002, -H2, sz * W2 - (SH if sz > 0 else 0)), (x1 - 0.0002, H2 - r, sz * W2 + (0 if sz > 0 else SH)))
        a0 = 0.0 if sz > 0 else math.pi / 2
        bend = pb.g_ring(r - SH, r, D - 0.0004, 10, a0, a0 + math.pi / 2)
        m.add(P, bend, Matrix(((0, 0, 1), (0, 1, 0), (1, 0, 0))), (xc, H2 - r, sz * (W2 - r)))
    # pan: the fan-side bottom (open or stamped), bent up into the rear and front walls
    fan_r = s["fan"] / 2 - 0.0025
    style = s["grille"]
    bot_holes = [pb.circle2(xc, 0.0, fan_r + 0.001, 128)]
    m.add(P, pb.g_slab(pb.rect2(xc, 0, D - 2 * r, 2 * (W2 - SH)), bot_holes, SH, -H2), M_XZ)
    if style not in ("wire", "ring"):  # the stamped grille: a perforated disc filling the round opening
        m.add(P, pb.g_slab(pb.circle2(xc, 0.0, fan_r + 0.001, 128), perforation(style, xc, fan_r, 0.0135), SH, -H2), M_XZ)
    for sx, xe in ((1, x1), (-1, x0)):
        a0 = (math.pi * 1.5 if sx > 0 else math.pi)
        bend = pb.g_ring(r - SH, r, 2 * (W2 - SH), 10, a0, a0 + math.pi / 2)
        m.add(P, bend, None, (xe - sx * r, -H2 + r, 0.0))
    # rear wall (+x): honeycomb, screw holes, inlet and switch cut-outs
    hz0, hz1, hy0, hy1 = g["honey"]
    hexes = []
    hr, gap = 0.0028, 0.0010
    w = math.sqrt(3) * hr
    j = 0
    yv = hy0 + hr
    while yv + hr <= hy1:
        zv = hz0 + w / 2 + (w / 2 + gap / 2 if j % 2 else 0)
        while zv + w / 2 <= hz1:
            hexes.append(pb.hexagon2(zv, yv, hr, math.pi / 6))
            zv += w + gap
        yv += 1.5 * hr + gap * 0.87
        j += 1
    zi, yi = g["inlet"]
    zs_, ys_ = g["switch"]
    holes = hexes + [pb.circle2(z, y, 0.0018, 16) for (z, y) in g["screws"]]
    holes.append(pb.chamfer2(zi, yi, 0.0264, 0.0178, (0.0038, 0.0038, 0.0010, 0.0010)))
    holes.append(pb.rrect2(zs_, ys_, 0.0183, 0.0123, 0.0006, 2))
    m.add(P, pb.g_slab(pb.rect2(0, (r - SH) / 2, 2 * (W2 - SH), (H2 - SH) - (-H2 + r)), holes, SH, x1 - SH), M_ZY)
    for (z, y) in g["screws"]:
        m.add("steel_dark", pb.g_ring(0.0017, 0.0034, 0.0024, 6), pb.frame((1, 0, 0), (0, 1, 0)), (x1 - SH - 0.0012, y, z))
    # front wall (-x): the cable grommet (fixed cables) and/or the modular panel cut-out
    f_holes = []
    if s["modular"] in ("full", "semi"):
        u0, v0, u1, v1 = g["panel"]
        f_holes.append(pb.rect2(-(u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) + 0.002, (v1 - v0) + 0.002))
    if s["modular"] in ("none", "semi"):
        ez, ey = g["exit"]
        f_holes.append(pb.circle2(ez, ey, 0.0135, 48))
    if s["modular"] == "none":
        for k in range(8):
            for jj in range(3):
                f_holes.append(pb.circle2(-0.062 + k * 0.0075, -0.020 - jj * 0.0068, 0.0025, 16))
    m.add(P, pb.g_slab(pb.rect2(0, (H2 - SH + -H2 + r) / 2, 2 * (W2 - SH), (H2 - SH) - (-H2 + r)), f_holes, SH, x0), M_ZY)
    # cover screws (2 a side) and the fan screws
    for sz in (-1, 1):
        for x in (xc - hx + 0.020, xc + hx - 0.020):
            pb.screw_ph(m.mb("steel_dark"), (x, -H2 + 0.0045, sz * W2), (0, 0, sz), (0, 1, 0), r=0.0022, h=0.0010)
    fs = {0.092: 0.04125, 0.12: 0.0525, 0.135: 0.059, 0.14: 0.0625}[s["fan"]]
    for (x, z) in ((fs, fs), (-fs, fs), (fs, -fs), (-fs, -fs)):
        pb.screw_ph(m.mb("steel_dark"), (xc + x, -H2, z), (0, -1, 0), (1, 0, 0), r=0.0026, h=0.0011)
    # fan grille
    if style in ("wire", "ring"):
        gm = m.mb(P)
        yr, ys = -H2 - 0.0013, -H2 - 0.0005
        rings = [0.0115, 0.019, 0.027, 0.035, 0.043, 0.051, 0.059, fan_r - 0.004, fan_r + 0.0015]
        rings = [rr for rr in rings if rr <= fan_r - 0.004] + [fan_r + 0.0015]
        for rr in rings:
            nseg = max(32, int(rr * 2000))
            gm.add(pb.g_sweep([(xc + math.cos(pb.TAU * k / nseg) * rr, yr, math.sin(pb.TAU * k / nseg) * rr)
                               for k in range(nseg)], 0.0006, 6, closed=True))
        for k in range(8):
            a = k * math.pi / 4 + math.pi / 8
            r0 = 0.0115 if k % 2 == 0 else 0.027
            gm.add(pb.g_sweep([(xc + math.cos(a) * r0, ys, math.sin(a) * r0),
                               (xc + math.cos(a) * (fan_r + 0.0015), ys, math.sin(a) * (fan_r + 0.0015))], 0.0006, 6))
        if style == "ring":  # brushed aluminium trim ring round the opening, with a chamfered lip
            m.add("alu", pb.g_lathe([(fan_r - 0.0004, 0.0), (fan_r + 0.0075, 0.0), (fan_r + 0.0075, -0.0012),
                                     (fan_r + 0.0062, -0.0024), (fan_r + 0.0012, -0.0024), (fan_r - 0.0004, -0.0012),
                                     (fan_r - 0.0004, 0.0)], 128), pb.frame((0, 1, 0), (1, 0, 0)), (xc, -H2 - 0.0001, 0.0))
        m.add(TEX, pb.g_disc(0.0118, 40, at.uv("badge"), depth=0.0008), pb.label_frame((0, -1, 0), (1, 0, 0)),
              (xc, -H2 - 0.0021, 0.0))
    else:
        m.add(TEX, pb.g_disc(0.0125, 40, at.uv("badge"), depth=0.0003), pb.label_frame((0, -1, 0), (1, 0, 0)),
              (xc, -H2 - 0.0001, 0.0))
    if s.get("trim") == "red":  # red accent strip round the grille plate edge (Mako)
        sw = pb.solid(pb.g_ring(fan_r + 0.0035, fan_r + 0.0052, 0.0004, 128), at.uv("swatch"))
        m.add(TEX, sw, pb.frame((0, 1, 0), (1, 0, 0)), (xc, -H2 - 0.0002, 0.0))
    # the fan behind the grille
    ft = g["fan_t"]
    fa = m.anchor("A_FAN_0", (xc, -H2 + SH + 0.0005 + ft / 2, 0.0), (s["fan"], s["fan"], ft), forward=(0, -1, 0),
                  up=(1, 0, 0), meta=pf.fan_meta("ccw", 1500))
    ftag = "white_plastic" if s.get("white_fan") else "fan_black"
    pf.make_fan(fa, diameter=s["fan"], thickness=ft, blades=s["blades"], frame=True, sticker=s["id"],
                sticker_uv=at.uv("hub"), name="psufan", blade_tag=ftag, frame_tag=ftag)
    return fan_r


def interior(m, s, g):
    """What shows through the honeycomb and the fan: the main PCB, heatsinks, capacitors, transformer, filter."""
    x0, x1, xc, H2 = g["x0"], g["x1"], g["xc"], g["h2"]
    pcb_y = H2 - 0.0085
    fan_top = -H2 + SH + 0.0005 + g["fan_t"]
    yb = max(fan_top + 0.004, pcb_y - 0.0285)
    m.add("pcb_green" if s["paint"] != "paint_white" else "pcb_black", pb.g_box((s["depth"] - 0.022, 0.0016, 2 * g["w2"] - 0.022)),
          None, (xc - 0.002, pcb_y, 0.0))
    under = pcb_y - 0.0008
    for zc in (-0.036 * g["w2"] / 0.075, 0.012 * g["w2"] / 0.075):
        box(m, "alu", (x1 - 0.066, yb, zc - 0.0015), (x1 - 0.008, under, zc + 0.0015))
        for k in range(7):
            box(m, "alu", (x1 - 0.064 + k * 0.0082, yb, zc + 0.0015), (x1 - 0.0628 + k * 0.0082, under - 0.004, zc + 0.012))
    for (x, z, rr, hh) in ((x1 - 0.040, -0.058 * g["w2"] / 0.075, 0.0105, under - yb), (x0 + 0.030, 0.052 * g["w2"] / 0.075, 0.006, 0.020),
                           (x0 + 0.020, 0.035 * g["w2"] / 0.075, 0.005, 0.016)):
        hh = min(hh, under - yb)
        m.add("black_plastic", pb.g_cyl(rr, hh, 24), pb.frame((0, 1, 0), (1, 0, 0)), (x, under - hh / 2, z))
        m.add("alu", pb.g_cyl(rr * 0.92, 0.0004, 24), pb.frame((0, 1, 0), (1, 0, 0)), (x, under - hh - 0.0002, z))
    box(m, "chip_black", (xc - 0.030, yb + 0.006, 0.020 * g["w2"] / 0.075), (xc - 0.008, under, 0.044 * g["w2"] / 0.075))
    box(m, "connector_beige", (xc - 0.027, yb + 0.008, 0.016 * g["w2"] / 0.075), (xc - 0.011, under - 0.003, 0.048 * g["w2"] / 0.075))
    box(m, "connector_beige", (x1 - 0.030, yb + 0.010, 0.040 * g["w2"] / 0.075), (x1 - 0.006, under, 0.060 * g["w2"] / 0.075))


def rear_face(m, s, g):
    """C14 inlet (A_PORT_C13_0) and the I/O rocker (A_SWITCH_PSU_0), exactly as build_psu.py, at the rear face x1."""
    X1 = g["x1"]
    zi, yi = g["inlet"]
    key = pb.chamfer2(zi, yi, 0.0244, 0.0158, (0.0032, 0.0032, 0.0006, 0.0006))
    m.add("black_plastic", pb.g_slab(pb.rrect2(zi, yi, 0.0300, 0.0230, 0.0015, 3), [key], 0.0014, X1), M_ZY)
    key_out = pb.chamfer2(zi, yi, 0.0264, 0.0178, (0.0038, 0.0038, 0.0010, 0.0010))
    m.add("black_plastic", pb.g_slab(key_out, [key], 0.0114, X1 - 0.010), M_ZY)
    m.add("black_plastic", pb.g_slab(key, [], 0.0010, X1 - 0.0095), M_ZY)
    for (z, y, hgt) in ((zi - 0.0070, yi + 0.0025, 0.0040), (zi + 0.0070, yi + 0.0025, 0.0040), (zi, yi - 0.0040, 0.0040)):
        box(m, "nickel", (X1 - 0.0088, y - hgt / 2, z - 0.0006), (X1 - 0.0012, y + hgt / 2, z + 0.0006), 0.0002)
    m.anchor("A_PORT_C13_0", (X1 + 0.0014, yi, zi), (0.030, 0.023, 0.020), forward=(1, 0, 0), up=(0, 1, 0),
             meta="kind=iec_c14_inlet,key=-y")
    zs_, ys_ = g["switch"]
    m.add("black_plastic", pb.g_slab(pb.rrect2(zs_, ys_, 0.0215, 0.0155, 0.0010, 3),
                                     [pb.rrect2(zs_, ys_, 0.0183, 0.0123, 0.0006, 2)], 0.0016, X1), M_ZY)
    m.add("black_plastic", pb.g_slab(pb.rrect2(zs_, ys_, 0.0183, 0.0123, 0.0006, 2), [], 0.001, X1 - 0.004), M_ZY)
    sw = m.anchor("A_SWITCH_PSU_0", (X1 + 0.0004, ys_, zs_), (0.024, 0.018, 0.010), forward=(1, 0, 0), up=(0, 1, 0),
                  meta="hinge=y,on=-9,off=9,on_side=+z,mark_on=I,mark_off=O")
    wr, hr_ = 0.0175, 0.0115
    prof = [(zs_ - wr / 2, X1 - 0.004), (zs_ + wr / 2, X1 - 0.004), (zs_ + wr / 2, X1 + 0.0016), (zs_, X1 + 0.0030),
            (zs_ - wr / 2, X1 + 0.0016)]
    m.piece(sw, "black_plastic", "rocker").add(pb.g_slab(prof, [], hr_, ys_ - hr_ / 2, bevel=0.0003), M_ZX)
    slope = math.atan2(0.0014, wr / 2)
    for side, mark in ((1, "I"), (-1, "O")):
        zc = zs_ + side * 0.0045
        xc = X1 + 0.0030 - 0.0045 * math.tan(slope)
        n = V((math.cos(slope), 0.0, side * math.sin(slope)))
        g_ = pb.g_box((0.0008, 0.0052, 0.0002)) if mark == "I" else pb.g_ring(0.0015, 0.0022, 0.0002, 24)
        m.piece(sw, "paint_white", "mark").add(g_, pb.frame(n, (0, 1, 0)), V((xc, ys_, zc)) + n * 0.00005)
    for i, (z, y) in enumerate(g["screws"]):
        m.anchor(f"A_SCREW_PH2_{i}", (X1, y, z), (0.008, 0.008, 0.008), forward=(1, 0, 0), up=(0, 1, 0), meta="thread=6-32")


def cable_bundle(m, g, ez, ey, n_wires, meta):
    """The fixed sleeved bundle leaving a grommet on the front face, cut short (A_CABLE_EXIT_0)."""
    X0 = g["x0"]
    m.add("rubber", pb.g_lathe([(0.0108, -0.0015), (0.0148, -0.0015), (0.0152, 0.0012), (0.0132, 0.0022),
                                (0.0108, 0.0016), (0.0108, -0.0015)], 48), pb.frame((-1, 0, 0), (0, 1, 0)), (X0, ey, ez))
    rng = random.Random(4 + n_wires)
    offs = [(0.0, 0.0, 0.0042)]
    for k in range(n_wires - 1):
        a = k * pb.TAU / (n_wires - 1)
        offs.append((math.cos(a) * 0.0078, math.sin(a) * 0.0078, 0.0032 if k % 3 else 0.0036))
    for (dy, dz, rr) in offs:
        ln = 0.026 + rng.uniform(-0.002, 0.002)
        pts = [(X0 + 0.004, ey + dy * 0.8, ez + dz * 0.8), (X0 - 0.014, ey + dy * 0.85, ez + dz * 0.85),
               (X0 - ln, ey + dy, ez + dz)]
        m.add("mesh_black", pb.g_sweep(pb.fillet_path(pts, 0.01, 4), rr, 12))
        m.add("black_plastic", pb.g_sweep([(X0 - ln + 0.006, ey + dy, ez + dz), (X0 - ln - 0.0005, ey + dy, ez + dz)],
                                          rr + 0.0003, 12))
    m.add("black_plastic", pb.g_ring(0.0103, 0.0112, 0.0035, 32), pb.frame((-1, 0, 0), (0, 1, 0)), (X0 - 0.014, ey, ez))
    m.anchor("A_CABLE_EXIT_0", (X0 - 0.001, ey, ez), (0.03, 0.03, 0.02), forward=(-1, 0, 0), up=(0, 1, 0), meta=meta)


def modular_panel(m, s, g, at, TEX, socks):
    X0 = g["x0"]
    u0, v0, u1, v1 = g["panel"]
    xp = X0 + 0.0012
    m.add("black_plastic", pb.g_box((0.002, v1 - v0 + 0.002, u1 - u0 + 0.002)), None, (xp + 0.001, (v0 + v1) / 2, -(u0 + u1) / 2))
    m.add(TEX, pb.g_quad(u1 - u0, v1 - v0, at.uv("panel")), pb.label_frame((-1, 0, 0), (0, 1, 0)),
          (xp - 0.00005, (v0 + v1) / 2, -(u0 + u1) / 2))
    counts = {}
    for (name, key, u, v, text, w, h) in socks:
        counts[key] = counts.get(key, 0) + 1
    feeds = {k: feeds_of(s, k, n) for k, n in counts.items()}
    seen = {}
    for (name, key, u, v, text, w, h) in socks:
        kind = KIND[key]
        BP.socket(m, kind, (X0 - 0.0004, v, -u), -1, +1)
        i = seen.get(key, 0)
        seen[key] = i + 1
        meta = {"atx24": "pins=24", "12v2x6": "pins=12+4,sense=+y", "cpu8": "pins=8,key=cpu",
                "pcie8": "pins=8,key=pcie", "sata6": "pins=6,key=sata"}[kind] + ",latch=+y"
        if key in ("pcie", "sata", "cpu"):
            meta += f",feeds={feeds[key][i]}"
        m.anchor(name, (X0 - 0.0004, v, -u), (w + 0.004, h + 0.004, 0.012), forward=(-1, 0, 0), up=(0, 1, 0), meta=meta)


def side_dress(m, s, g, at, TEX):
    """Labels, side logo and per-model trim (stripes, armour plate with RGB and OLED, brushed side plate)."""
    xc, hx, W2, H2 = g["xc"], g["hx"], g["w2"], g["h2"]
    ls = s.get("label_side", 1)
    sfx = s.get("form") == "sfx"
    lw, lh = (0.096, 0.0553) if sfx else (0.118, 0.068)
    m.add(TEX, pb.g_quad(lw, lh, at.uv("label")), pb.label_frame((0, 0, ls), (0, 1, 0)),
          (xc - 0.003 * ls + (0.0 if s["depth"] <= 0.14 else -ls * (hx - 0.070) * 0.6), 0.0, ls * (W2 + 0.00012)))
    os_ = -ls  # the other side: logo, trim
    side = pb.label_frame((0, 0, os_), (0, 1, 0))
    ink = "grey_plastic" if s["paint"] == "paint_black" else "dark_plastic"
    zf = os_ * (W2 + 0.00002)
    if s.get("armour"):
        armour(m, s, g, at, TEX, os_)
    else:
        m.add(ink, pb.g_text(s["side"], s["side_font"], 0.012 if not sfx else 0.009, min(0.09, s["depth"] * 0.65), 0.00008,
                             spacing=1.2), side, (xc, 0.004, zf))
        m.add(ink, pb.g_text(f"{s['watts']}W  80 PLUS {s['tier']}", "arialb", 0.0035, 0.09, 0.00008, spacing=1.3),
              side, (xc, -0.010 if not sfx else -0.008, zf))
    if s.get("stripes"):  # two brushed stripes along each side, top and bottom
        for sz in (-1, 1):
            for y in (H2 - 0.0075, -H2 + 0.0095):
                box(m, "alu", (g["x0"] + 0.006, y - 0.0011, sz * W2 - (0.0002 if sz < 0 else 0)),
                    (g["x1"] - 0.006, y + 0.0011, sz * W2 + (0.0002 if sz > 0 else 0)))
    if s.get("side_plate"):  # brushed aluminium plate inset on the logo side, with the logo engraved dark
        z0 = os_ * W2
        prof = pb.chamfer2(xc, 0.0, 2 * hx - 0.020, 2 * H2 - 0.020, (0.0, 0.010, 0.0, 0.010))
        dz = 0.0007
        m.add("alu_dark", pb.g_slab(prof, [], dz, 0.0), Matrix(((1, 0, 0), (0, 1, 0), (0, 0, os_))), (0, 0, z0))
        side2 = pb.label_frame((0, 0, os_), (0, 1, 0))
        m.add("black_plastic", pb.g_text(s["side"], s["side_font"], 0.012, min(0.09, s["depth"] * 0.6), 0.00008, spacing=1.2),
              side2, (xc, 0.004, os_ * (W2 + dz + 0.00002)))
        m.add("black_plastic", pb.g_text(f"{s['watts']}W  80 PLUS {s['tier']}", "arialb", 0.0035, 0.09, 0.00008,
                                         spacing=1.3), side2, (xc, -0.010, os_ * (W2 + dz + 0.00002)))
    m.add(TEX, pb.g_quad(0.016, 0.008, at.uv("qc")), pb.label_frame((0, 1, 0), (-1, 0, 0)),
          (g["x0"] + 0.020, H2 + 0.0001, 0.058 * W2 / 0.075))


def armour(m, s, g, at, TEX, os_):
    """Aegis: an angular dark aluminium armour plate on the window side, a diagonal RGB light bar and the OLED
    wattage display (A_SCREEN_0)."""
    xc, hx, W2, H2 = g["xc"], g["hx"], g["w2"], g["h2"]
    x0, x1 = g["x0"] + 0.006, g["x1"] - 0.006
    y0, y1 = -H2 + 0.006, H2 - 0.006
    Mz = Matrix(((1, 0, 0), (0, 1, 0), (0, 0, os_)))
    z0 = os_ * W2
    t = 0.0016
    outline = [(x0, y0), (x1 - 0.030, y0), (x1, y0 + 0.022), (x1, y1), (x0 + 0.040, y1), (x0, y1 - 0.026)]
    slot = [(x0 + 0.050, y0 + 0.012), (x0 + 0.058, y0 + 0.012), (x0 + 0.092, y1 - 0.010), (x0 + 0.084, y1 - 0.010)]
    oled = pb.rect2(x1 - 0.040, y1 - 0.016, 0.042, 0.016)
    m.add("alu_dark", pb.g_slab(outline, [slot, oled], t, 0.0, bevel=0.0004), Mz, (0, 0, z0))
    # RGB light bar in the slot and a thin RGB edge line along the lower edge
    m.add("rgb", pb.g_slab(slot, [], t - 0.0003, 0.0), Mz, (0, 0, z0))
    m.add("rgb", pb.g_slab([(x0 + 0.004, y0 - 0.0012), (x1 - 0.034, y0 - 0.0012), (x1 - 0.033, y0 - 0.0002),
                            (x0 + 0.004, y0 - 0.0002)], [], 0.0012, 0.0), Mz, (0, 0, z0))
    # OLED: black glass window over the screen face
    ox, oy = x1 - 0.040, y1 - 0.016
    m.add(TEX, pb.g_quad(0.038, 0.0135, at.uv("oled")), pb.label_frame((0, 0, os_), (0, 1, 0)),
          (ox, oy, os_ * (W2 + t - 0.0004)))
    m.anchor("A_SCREEN_0", (ox, oy, os_ * (W2 + t - 0.0004)), (0.038, 0.0135, 0.004), forward=(0, 0, os_), up=(0, 1, 0),
             meta="kind=oled,res=128x48,shows=watts")
    side = pb.label_frame((0, 0, os_), (0, 1, 0))
    m.add("grey_plastic", pb.g_text(s["side"], s["side_font"], 0.009, 0.05, 0.00008, spacing=1.25), side,
          (x1 - 0.042, -0.004, os_ * (W2 + t + 0.00002)))
    m.add("grey_plastic", pb.g_text(f"{s['watts']}W  PLATINUM", "arialb", 0.0030, 0.05, 0.00008, spacing=1.3), side,
          (x1 - 0.042, -0.014, os_ * (W2 + t + 0.00002)))
    m.anchor("A_RGB_0", (xc, 0.0, os_ * (W2 + t)), (2 * hx - 0.012, 2 * H2 - 0.012, 0.004), forward=(0, 0, os_),
             up=(0, 1, 0), meta="kind=argb,zones=2")


# ---------------------------------------------------------------------------------------------------- ATX / SFX

def build_unit(pid):
    s = BY_ID[pid]
    g = geo_of(s)
    socks = layout(s, g)
    at = art.make_texture(pid, s, socks, g["panel"])
    TEX = "tex_" + pid
    m = pb.Model(pid)
    housing(m, s, g, at, TEX)
    interior(m, s, g)
    rear_face(m, s, g)
    side_dress(m, s, g, at, TEX)
    if s["modular"] in ("full", "semi"):
        modular_panel(m, s, g, at, TEX, socks)
    eps, pcie, p16, sata = s["conns"]
    if s["modular"] == "none":
        ez, ey = g["exit"]
        cable_bundle(m, g, ez, ey, 9, "bundle=atx24," + ",".join(["eps8"] * eps + ["pcie8"] * (pcie // 2)) +
                     f",sata*{sata},molex*2,stub=0.026")
    elif s["modular"] == "semi":
        ez, ey = g["exit"]
        cable_bundle(m, g, ez, ey, 6, "bundle=atx24,eps8,stub=0.026")
    m.anchor("A_HIT_0", (g["xc"], 0, 0), (s["depth"], 2 * g["h2"], 2 * g["w2"]))
    m.finish()
    txt = m.report()
    m.export()
    write_report(pid, txt, contract_line(s))
    if PREVIEW[0]:
        pb.preview_textures()
        X0, X1, H2, W2 = g["x0"], g["x1"], g["h2"], g["w2"]
        ls = s.get("label_side", 1)
        pb.shots(m.root, pid, [
            dict(yaw=-35 if ls > 0 else 215, pitch=25),
            dict(yaw=60 if ls > 0 else 120, pitch=25),
            dict(yaw=90, pitch=5, target=(X1, 0.0, 0.0), dist=0.22),
            dict(yaw=200, pitch=-50),
            dict(yaw=-90, pitch=10, target=(X0, 0.0, 0.0), dist=0.24),
            dict(yaw=0 if ls > 0 else 180, pitch=0, target=(g["xc"], 0, ls * W2), dist=0.2 + max(0, s["depth"] - 0.14)),
            dict(yaw=180 if ls > 0 else 0, pitch=10, target=(g["xc"], 0, -ls * W2), dist=0.24 + max(0, s["depth"] - 0.14)),
        ])
    return m


def contract_line(s):
    if s.get("form") == "sfx":
        return "contract psu_sfx (new): origin at the box centre, x = depth 0.100 (rear face +0.050), y = height 0.0635 (fan -y), z = width 0.125"
    return f"contract psu (as psu_450/psu_750): rear face at x +0.070, depth {s['depth']:.3f} (front face x {0.07 - s['depth']:+.3f})"


# ---------------------------------------------------------------------------------------------------- SFX bracket

def build_bracket():
    """The SFX-to-ATX adapter plate. Its frame IS the ATX PSU frame (drop it on A_SOCKET_PSU_0 like an ATX unit):
    A_SCREW_PH2_0..3 are the ATX case-bay screw holes; A_SOCKET_PSU_SFX_0 is where the SFX unit's origin goes;
    A_SCREW_PH2_4..7 are the four SFX screws through the plate into the unit."""
    pid = BRACKET
    m = pb.Model(pid)
    X1, W2, H2 = 0.070, 0.075, 0.043
    t = 0.0012
    # the SFX unit sits low and towards -z (left as seen from the rear) so its fan clears a bottom intake; offset:
    sy, sz = -0.043 + 0.03175, -0.0075 + 0.0
    sx = X1 + 0.0 - 0.050 - t  # SFX rear face against the plate's inner face
    window = pb.rrect2(sz, sy, 0.1215, 0.0605, 0.002, 3)
    holes = [window] + [pb.circle2(z, y, 0.0018, 16) for (z, y) in ATX["screws"]]
    m.add("paint_black", pb.g_slab(pb.rrect2(0, 0, 0.150, 0.086, 0.002, 3), holes, t, X1 - t), M_ZY)
    # plate flanges: a top lip and a bottom shelf the SFX unit rests on
    box(m, "paint_black", (X1 - 0.022, H2 - t, -W2 + 0.004), (X1 - t, H2, W2 - 0.004))
    box(m, "paint_black", (X1 - 0.030, -H2, -W2 + 0.004), (X1 - t, -H2 + t, W2 - 0.004))
    # SFX screw holes are in the window border: small tabs folded in from the window edge
    for i, (z, y) in enumerate(SFX["screws"]):
        zz, yy = sz + z, sy + y
        m.add("paint_black", pb.g_slab(pb.rrect2(zz, yy, 0.008, 0.008, 0.001, 2), [pb.circle2(zz, yy, 0.0016, 16)], t,
                                       X1 - 2 * t), M_ZY)
        pb.screw_ph(m.mb("steel_dark"), (X1, yy, zz), (1, 0, 0), (0, 1, 0), r=0.0026, h=0.0012)
        m.anchor(f"A_SCREW_PH2_{4 + i}", (X1, yy, zz), (0.008, 0.008, 0.008), forward=(1, 0, 0), up=(0, 1, 0),
                 meta="thread=6-32,into=sfx")
    for i, (z, y) in enumerate(ATX["screws"]):
        m.anchor(f"A_SCREW_PH2_{i}", (X1, y, z), (0.008, 0.008, 0.008), forward=(1, 0, 0), up=(0, 1, 0),
                 meta="thread=6-32,into=case")
    m.anchor("A_SOCKET_PSU_SFX_0", (sx, sy, sz), (0.100, 0.0635, 0.125), forward=(0, 0, 1), up=(0, 1, 0),
             meta="insert=+x,unit=psu_sfx")
    m.anchor("A_HIT_0", (X1 - 0.012, 0, 0), (0.024, 0.086, 0.150))
    m.finish()
    txt = m.report()
    m.export()
    write_report(pid, txt, "contract psu (ATX frame): drops on A_SOCKET_PSU_0; carries an SFX unit at A_SOCKET_PSU_SFX_0")
    if PREVIEW[0]:
        pb.shots(m.root, pid, [dict(yaw=55, pitch=25), dict(yaw=-120, pitch=20), dict(yaw=90, pitch=0, dist=0.3)])
    return m


# ---------------------------------------------------------------------------------------------------- CRPS

CR = dict(x1=0.0925, w2=0.03675, h2=0.020)


def build_crps(pid):
    """A CRPS hot-swap module: 73.5 (w, z) x 40 (h, y) x 185 (d, x). Origin at the body centre, rear (handle, inlet,
    fan, LED) at +x, the card-edge connector at -x."""
    s = BY_ID[pid]
    at = art.make_crps_texture(pid, s)
    TEX = "tex_" + pid
    m = pb.Model(pid)
    X1, W2, H2 = CR["x1"], CR["w2"], CR["h2"]
    X0 = -X1
    B = s["body"]
    t = 0.0008
    # body: a folded sheet tube (top, bottom, both sides) with rounded long edges
    r = 0.0015
    for sy in (-1, 1):
        box(m, B, (X0, sy * H2 - (t if sy > 0 else 0), -W2 + r), (X1 - 0.004, sy * H2 + (0 if sy > 0 else t), W2 - r))
    for sz in (-1, 1):
        box(m, B, (X0, -H2 + r, sz * W2 - (t if sz > 0 else 0)), (X1 - 0.004, H2 - r, sz * W2 + (0 if sz > 0 else t)))
    for sy in (-1, 1):
        for sz in (-1, 1):
            a0 = {(1, 1): 0.0, (1, -1): math.pi / 2, (-1, -1): math.pi, (-1, 1): 1.5 * math.pi}[(sy, sz)]
            # lathe axis local z -> +x; local x -> +z, local y -> +y
            m.add(B, pb.g_ring(r - t, r, X1 - 0.004 - X0, 8, a0, a0 + math.pi / 2), Matrix(((0, 0, 1), (0, 1, 0), (1, 0, 0))),
                  ((X0 + X1 - 0.004) / 2, sy * (H2 - r), sz * (W2 - r)))
    # side vents near the front and the top label
    for k in range(10):
        box(m, "black_plastic", (X0 + 0.012 + k * 0.006, -0.010, W2 + 0.00005), (X0 + 0.015 + k * 0.006, 0.010, W2 + 0.0002))
    m.add(TEX, pb.g_quad(0.120, 0.048, at.uv("label")), pb.label_frame((0, 1, 0), (0, 0, -1)), (-0.010, H2 + 0.0001, 0.0))
    # guide rail along the -z side bottom (keys the module in the cage)
    box(m, "steel", (X0 + 0.010, -H2 + 0.002, -W2 - 0.0012), (X1 - 0.030, -H2 + 0.006, -W2))
    # front (-x): closed end plate with the PCB card edge sticking out
    box(m, B, (X0 - t, -H2, -W2), (X0, H2, W2))
    pcb_t = 0.0016
    ey = -0.008
    ew = 0.046
    box(m, "pcb_green", (X0 - 0.010, ey - pcb_t / 2, -ew / 2), (X0 + 0.004, ey + pcb_t / 2, ew / 2))
    for side in (-1, 1):
        for k in range(26):
            z = -ew / 2 + 0.0022 + k * (ew - 0.0044) / 25
            wz = 0.0009 if k not in (5, 6, 18, 19) else 0.0014  # wide power pads
            yy = ey + side * (pcb_t / 2 + 0.00003)
            box(m, "gold", (X0 - 0.0095, yy - 0.00002, z - wz / 2), (X0 - 0.0015, yy + 0.00002, z + wz / 2))
    box(m, "black_plastic", (X0 - 0.002, ey - 0.004, -ew / 2 - 0.003), (X0, ey + 0.004, ew / 2 + 0.003))
    m.anchor("A_PORT_EDGE_0", (X0 - 0.010, ey, 0.0), (0.012, 0.006, 0.050), forward=(-1, 0, 0), up=(0, 1, 0),
             meta="kind=crps_card_edge,pads=2x26,pcb=1.6mm")
    # rear (+x): end plate with the fan grille, C14 inlet (vertical), LED; handle and latch
    fz, fd = -0.014, 0.033
    iz, iy = 0.019, 0.001
    grille = []
    for j in range(-4, 5):
        for i in range(-4, 5):
            zz, yy = fz + i * 0.0042 + (0.0021 if j % 2 else 0), j * 0.0037
            if math.hypot(zz - fz, yy) < fd / 2 - 0.0025 and math.hypot(zz - fz, yy) > 0.006:
                grille.append(pb.hexagon2(zz, yy, 0.0018, math.pi / 6))
    inlet_cut = pb.chamfer2(iz, iy, 0.0178, 0.0264, (0.0010, 0.0038, 0.0038, 0.0010))
    led_cut = pb.circle2(0.0305, 0.015, 0.0014, 12)
    m.add(B, pb.g_slab(pb.rect2(0, 0, 2 * W2, 2 * H2), grille + [inlet_cut, led_cut], 0.0012, X1 - 0.004), M_ZY)
    # the fan behind the grille (40 mm)
    fa = m.anchor("A_FAN_0", (X1 - 0.004 - 0.0005 - 0.014, 0.0, fz), (0.032, 0.032, 0.028), forward=(1, 0, 0),
                  up=(0, 1, 0), meta=pf.fan_meta("ccw", 12000))
    pf.make_fan(fa, diameter=0.032, thickness=0.028, blades=7, frame=True, sticker=pid, sticker_uv=at.uv("hub"),
                name="crpsfan")
    # vertical C14 inlet
    key = pb.chamfer2(iz, iy, 0.0158, 0.0244, (0.0006, 0.0032, 0.0032, 0.0006))
    m.add("black_plastic", pb.g_slab(pb.rrect2(iz, iy, 0.0230, 0.0300, 0.0015, 3), [key], 0.0014, X1 - 0.0028), M_ZY)
    m.add("black_plastic", pb.g_slab(inlet_cut, [key], 0.0100, X1 - 0.014), M_ZY)
    m.add("black_plastic", pb.g_slab(key, [], 0.0010, X1 - 0.0135), M_ZY)
    for (z, y) in ((iz + 0.0025, iy - 0.0070), (iz + 0.0025, iy + 0.0070), (iz - 0.0040, iy)):
        box(m, "nickel", (X1 - 0.0125, y - 0.0006, z - 0.0020), (X1 - 0.0050, y + 0.0006, z + 0.0020), 0.0002)
    m.anchor("A_PORT_C14_0", (X1 - 0.0014, iy, iz), (0.023, 0.030, 0.020), forward=(1, 0, 0), up=(0, 1, 0),
             meta="kind=iec_c14_inlet,key=+z,vertical=1")
    # status LED (bi-colour; the green die lit by the game)
    led = m.anchor("A_LED_STATUS_0", (X1 - 0.0028, 0.015, 0.0305), (0.004, 0.004, 0.004), forward=(1, 0, 0),
                   up=(0, 1, 0), meta="colors=green,amber,blink=standby")
    m.piece(led, "led_green", "led").add(pb.g_cyl(0.0013, 0.0016, 16), pb.frame((1, 0, 0), (0, 1, 0)), (X1 - 0.0034, 0.015, 0.0305))
    # the handle: a loop standing out of the rear face along the +z edge (fixed, it is the pull grip)
    hz = 0.0315
    ha = m.anchor("A_HANDLE_0", (X1 + 0.026, 0.0, hz), (0.012, 0.036, 0.012), forward=(1, 0, 0), up=(0, 1, 0),
                  meta="grip=pull,dir=+x,fixed=1")
    path = [(X1 - 0.0015, -0.016, hz), (X1 + 0.024, -0.016, hz), (X1 + 0.028, -0.010, hz), (X1 + 0.028, 0.010, hz),
            (X1 + 0.024, 0.016, hz), (X1 - 0.0015, 0.016, hz)]
    m.piece(ha, "black_plastic", "handle").add(pb.g_sweep(pb.fillet_path(path, 0.004, 4), 0.0028, 14))
    m.piece(ha, "rubber", "grip").add(pb.g_sweep([(X1 + 0.028, -0.009, hz), (X1 + 0.028, 0.009, hz)], 0.0034, 14))
    box(m, "black_plastic", (X1 - 0.004, -0.019, hz - 0.005), (X1, 0.019, hz + 0.005))  # handle base
    # the latch: a coloured spring tab on the +z side under the handle; pressed towards -z to release
    la = m.anchor("A_LATCH_0", (X1 + 0.006, -0.0125, W2 - 0.002), (0.012, 0.007, 0.008), forward=(1, 0, 0),
                  up=(0, 1, 0), meta="press=-z,travel=0.002,releases=cage")
    prof = [(X1 - 0.050, -0.0155), (X1 + 0.010, -0.0155), (X1 + 0.012, -0.0125), (X1 + 0.010, -0.0095),
            (X1 - 0.050, -0.0095)]
    m.piece(la, TEX, "latch").add(pb.solid(pb.g_slab(prof, [], 0.0022, W2 - 0.0005, bevel=0.0003), at.uv("swatch")))
    for k in range(4):
        m.piece(la, TEX, "latch").add(pb.solid(pb.g_box((0.0008, 0.005, 0.0006)), at.uv("swatch")), None,
                                      (X1 + 0.002 + k * 0.002, -0.0125, W2 + 0.0019))
    # legend on the rear above the inlet
    m.add(TEX, pb.g_quad(0.0122, 0.007, at.uv("legend")), pb.label_frame((1, 0, 0), (0, 1, 0)),
          (X1 - 0.0027, 0.0155, 0.017))
    m.anchor("A_HIT_0", (0, 0, 0), (2 * X1, 2 * H2, 2 * W2))
    m.finish()
    txt = m.report()
    m.export()
    write_report(pid, txt, "contract psu_crps (new): origin at the body centre, x = depth 0.185 (rear +0.0925, card edge -x), y = height 0.040, z = width 0.0735")
    if PREVIEW[0]:
        pb.preview_textures()
        pb.shots(m.root, pid, [
            dict(yaw=45, pitch=25), dict(yaw=-45, pitch=30), dict(yaw=90, pitch=5, target=(X1, 0, 0), dist=0.16),
            dict(yaw=-90, pitch=15, target=(X0, -0.008, 0), dist=0.12), dict(yaw=60, pitch=20, target=(X1, -0.005, 0.03), dist=0.09),
        ])
    return m


# ---------------------------------------------------------------------------------------------------- reports, json

def write_report(pid, txt, contract):
    path = os.path.join(c.PREVIEWS, f"{pid}_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contract + "\n" + txt + "\n")


def catalogue():
    out = []
    for s in UNITS:
        eps, pcie, p16, sata = s["conns"]
        sfx = s.get("form") == "sfx"
        dims = (125, 63.5, 100) if sfx else (150, 86, round(s["depth"] * 1000))
        specs = {"form_factor": "SFX" if sfx else "ATX", "width_mm": dims[0], "height_mm": dims[1], "depth_mm": dims[2],
                 "fan_mm": round(s["fan"] * 1000), "modular": s["modular"], "efficiency": f"80 PLUS {s['tier'].title()}",
                 "atx_version": s.get("atx3", "2.x"), "eps8": eps, "pcie8": pcie, "p12v2x6": p16, "sata": sata}
        if sfx:
            specs["bracket"] = BRACKET
        out.append(dict(id=s["id"], model=s["id"], brand=s["brand"], name=s["name"], category="PSU", price=s["price"],
                        power_w=0, color=s["color"], rgb=s["rgb"], analog=s["analog"] + " (docs only, never shown in game)",
                        desc=s["desc"], specs=specs,
                        game=dict(psu_watts=s["watts"], psu_efficiency=s["tier"].title(), psu_eps8=eps, psu_pcie8=pcie,
                                  psu_16=p16, psu_sata=sata, psu_modular=s["modular"] == "full", perf=0),
                        contract="psu_sfx" if sfx else "psu", new_contract=sfx))
    for s in CRPS:
        out.append(dict(id=s["id"], model=s["id"], brand=s["brand"], name=s["name"], category="Server",
                        price=s["price"], power_w=0, color=s["color"], rgb=False,
                        analog=s["analog"] + " (docs only, never shown in game)", desc=s["desc"],
                        specs={"form_factor": "CRPS", "width_mm": 73.5, "height_mm": 40, "depth_mm": 185, "fan_mm": 40,
                               "efficiency": f"80 PLUS {s['tier'].title()}", "hot_swap": True},
                        game=dict(psu_watts=s["watts"], psu_efficiency=s["tier"].title(), psu_eps8=0, psu_pcie8=0,
                                  psu_16=0, psu_sata=0, psu_modular=False, perf=0),
                        contract="psu_crps", new_contract=True))
    path = os.path.join(c.PROJECT, "docs", "catalog", "psus.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("CATALOGUE", path, len(out))


def combined_report():
    ids = [s["id"] for s in UNITS] + [BRACKET] + [s["id"] for s in CRPS]
    parts = []
    for pid in ids:
        p = os.path.join(c.PREVIEWS, f"{pid}_report.txt")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                parts.append(f.read())
    with open(os.path.join(c.PREVIEWS, "cat_psus_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")]
    every = [s["id"] for s in UNITS] + [BRACKET] + [s["id"] for s in CRPS]
    for pid in ids or every:
        if pid == BRACKET:
            build_bracket()
        elif pid in BY_ID and pid.startswith("psu_strata_crps"):
            build_crps(pid)
        elif pid in BY_ID:
            build_unit(pid)
        else:
            print("UNKNOWN id", pid)
    catalogue()
    combined_report()


if __name__ == "__main__":
    main(c.args())
