"""
Catalogue storage, part 2: 3.5" hard drives and 2.5" 15 mm U.2 enterprise SSDs (two new contracts).

3.5" HDD frame: origin at the body centre; x = length (147 mm, the SATA connectors on the -x end), y = height
(26.1 mm, +y = the top cover with the label), z = width (101.6 mm). The PCB is on the bottom (-y).
  A_PORT_SATA_0, A_PORT_SATAPWR_0   the data and power sockets, facing -x (plugs come from -x), up +y
  A_HOLE_0..3                       side screw holes (6-32 UNC), facing out of the +-z sides
  A_HOLE_4..9                       bottom screw holes (6-32 UNC), facing -y
  A_HIT_0                           the body
U.2 frame: the ssd_sata_500 frame made 15 mm thick: origin at the body centre, x = length (connector at -x),
y = thickness (+y = the finned top), z = width.
  A_PORT_U2_0                       the SFF-8639 plug socket, facing -x, up +y
  A_SCREW_PH2_0..3                  the four side holes (M3), at the ssd_sata_500 positions
  A_HOLE_0..3                       the four bottom holes (M3), facing -y
  A_HIT_0                           the body
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
from cat_storage_ssd import barcode, texname, traces  # noqa: E402

MM = 0.001

# ------------------------------------------------------------------ 3.5" dimensions (SFF-8301), mm
HL, HH, HW = 147.0, 26.1, 101.6
YB, YT = -HH / 2, HH / 2
BODY_Y0 = -10.6            # casting bottom face (the PCB sits under it)
BODY_Y1 = 11.6             # casting top face (the cover sits on it)
PCB_Y0 = BODY_Y0 - 1.2
RAIL = 3.0                 # bottom rail width along the sides
X_FRONT = HL / 2
SIDE_HOLES = [X_FRONT - 28.5, X_FRONT - 28.5 - 101.6]
SIDE_HOLE_Y = YB + 6.35
BOTTOM_HOLES = [X_FRONT - 41.6, X_FRONT - 41.6 - 44.45, X_FRONT - 41.6 - 76.2]
BOTTOM_HOLE_Z = 95.25 / 2
HDATA = dict(z=30.0, w=11.0, pins=7)
HPWR = dict(z=11.6, w=23.4, pins=15)
HCONN_Y = YB + 3.9         # connector tongue centre
POCKET_X = -HL / 2 + 7.5   # the casting overhang over the connectors ends here
POCKET_Y = -4.6
SPINDLE = (22.0, 0.0)
PIVOT = (-46.0, -31.0)


def lab_uv(x, z, lx, lz, w, h):
    """Model (x, z) -> portrait label coordinates (u right = -z, v up = +x)."""
    return w / 2 - (z - lz), h / 2 + (x - lx)


def reg_icons(a, x, y, s, ink):
    a.ring(x, y, s * 0.42, s * 0.5, ink, z=0.35)
    a.text("CE", x, y, s * 0.42, ink, font="arialbd", z=0.36)
    a.frame_rect(x + s * 0.8, y - s * 0.45, x + s * 1.7, y + s * 0.45, s * 0.07, ink, z=0.35)
    a.text("RoHS", x + s * 1.25, y, s * 0.24, ink, font="arialbd", z=0.36)
    for k in range(3):
        ang = math.radians(90 + k * 120)
        a.poly([(x + s * 2.4 + math.cos(ang) * s * 0.45, y + math.sin(ang) * s * 0.45),
                (x + s * 2.4 + math.cos(ang + 1.6) * s * 0.45, y + math.sin(ang + 1.6) * s * 0.45),
                (x + s * 2.4, y)], ink, z=0.35)


def hdd_label_common(a, cfg, w, h, rnd, ink, lx, lz):
    """Spec block, barcodes, icons and the screw / breather openings drawn on a portrait label."""
    y = cfg.get("spec_y", 50.0)
    for i, s in enumerate(cfg["spec_lines"]):
        a.text(s, 5.0, y - i * 3.4, 2.2, ink, font="narrowbd", ax="LEFT", fit=w * 0.55)
    barcode(a, 5.0, 8.0, w * 0.5, 15.0, rnd, ink, unit=0.28)
    a.text(cfg["sn"], 5.0 + w * 0.225, 6.0, 1.8, ink, font="ocr")
    barcode(a, w * 0.58, 8.0, w - 5.0, 13.0, rnd, ink, unit=0.22)
    a.text(cfg["pn"], w * 0.58 + (w * 0.42 - 5.0) / 2, 6.0, 1.6, ink, font="ocr")
    reg_icons(a, w * 0.62, 20.0, 5.0, ink)
    a.text("MADE IN " + cfg.get("origin", "THAILAND"), w - 5.0, 26.0, 1.8, ink, font="narrowbd", ax="RIGHT")
    if not cfg.get("helium"):
        u, v = lab_uv(*SPINDLE, lx, lz, w, h)
        a.circle(u, v, 4.4, "#8d9196", z=0.4)
        u, v = lab_uv(*PIVOT, lx, lz, w, h)
        a.circle(u, v, 3.6, "#8d9196", z=0.4)
        u, v = lab_uv(-62.0, 40.0, lx, lz, w, h)
        a.ring(u, v, 1.6, 2.2, ink, z=0.4)
        a.text("DO NOT COVER THIS HOLE", u + 3.4, v, 1.3, ink, font="narrowbd", ax="LEFT", z=0.4)


def art_shoreline(cfg):
    def art(a, w, h, rnd, lx, lz):
        ink = "#1c1d1f"
        a.rect(0, 0, w, h, "#e9eaec", z=0.06)
        a.rect(0, h - 24.0, w, h, "#25272a", z=0.08)
        a.circle(9.5, h - 12.0, 4.2, "#4bb38a", z=0.1)
        a.line([(6.2, h - 12.6), (8.0, h - 10.8), (9.8, h - 12.6), (11.6, h - 10.8), (13.0, h - 12.2)], 0.7, "#e9eaec", z=0.2)
        a.text("SEACREST", 16.0, h - 12.0, 6.0, "#f2f2f2", font="arialbd", ax="LEFT", space=1.1)
        a.text("SHORELINE", 5.0, h - 33.0, 8.4, ink, font="arialbd", ax="LEFT", fit=w * 0.62)
        a.text(cfg["cap"], w - 5.0, h - 33.0, 9.0, "#2c8d68", font="arialbd", ax="RIGHT")
        a.rect(5.0, h - 40.0, w - 5.0, h - 39.4, "#4bb38a", z=0.1)
        a.text("DESKTOP HDD  7200 RPM  SATA 6Gb/s  256MB CACHE", 5.0, h - 44.0, 2.0, ink, font="narrowbd", ax="LEFT", fit=w - 10)
        hdd_label_common(a, cfg, w, h, rnd, ink, lx, lz)
    return art


def art_azure(cfg):
    def art(a, w, h, rnd, lx, lz):
        ink = "#1c1d1f"
        a.rect(0, 0, w, h, "#f4f5f6", z=0.06)
        a.rect(0, h - 30.0, w, h, "#1f63b6", z=0.08)
        a.poly([(w * 0.55, h - 30.0), (w, h - 30.0), (w, h - 12.0)], "#2a74c9", z=0.09)
        a.text("WESTLINE", 5.0, h - 10.0, 6.4, "#ffffff", font="agency", ax="LEFT", space=1.1)
        a.text("AZURE", 5.0, h - 21.0, 8.0, "#d6e6f8", font="agency", ax="LEFT")
        a.text(cfg["cap"], w - 5.0, h - 21.0, 9.0, "#ffffff", font="agency", ax="RIGHT")
        a.text("Desktop Hard Drive  ·  SATA 6 Gb/s  ·  256MB Cache", 5.0, h - 35.0, 2.0, ink, font="narrowbd", ax="LEFT", fit=w - 10)
        a.rect(5.0, h - 38.6, w - 5.0, h - 38.0, "#1f63b6", z=0.1)
        hdd_label_common(a, cfg, w, h, rnd, ink, lx, lz)
    return art


def art_tidewolf(cfg):
    def art(a, w, h, rnd, lx, lz):
        ink = "#e6e7e9"
        a.rect(0, 0, w, h, "#2a2b2e", z=0.06)
        a.poly([(0, h - 20.0), (w * 0.62, h - 20.0), (w * 0.5, h - 23.0), (0, h - 23.0)], "#e0582a", z=0.1)
        a.poly([(w * 0.66, h), (w, h), (w, h - 44.0)], "#1f2023", z=0.09)
        # an abstract wolf-head emblem
        ex, ey = w - 15.0, h - 13.0
        a.poly([(ex - 6, ey - 5), (ex - 5, ey + 6), (ex - 2, ey + 2), (ex + 2, ey + 2), (ex + 5, ey + 6), (ex + 6, ey - 5), (ex, ey - 9)],
               "#e0582a", z=0.12)
        a.poly([(ex - 3, ey - 1), (ex - 1, ey - 1), (ex - 1.5, ey - 2.4)], "#2a2b2e", z=0.13)
        a.poly([(ex + 3, ey - 1), (ex + 1, ey - 1), (ex + 1.5, ey - 2.4)], "#2a2b2e", z=0.13)
        a.text("SEACREST", 5.0, h - 9.0, 4.6, "#f2f2f2", font="arialbd", ax="LEFT", space=1.1)
        a.text("TIDEWOLF", 5.0, h - 31.0, 8.6, "#ffffff", font="arialbd", ax="LEFT", fit=w * 0.62)
        a.rrect(w - 14.0, h - 31.0, 15.0, 7.0, 1.2, "#e0582a", z=0.1)
        a.text("NAS", w - 14.0, h - 31.0, 4.6, "#ffffff", font="arialbd", z=0.2)
        a.text(cfg["cap"], 5.0, h - 42.0, 7.0, "#e0582a", font="arialbd", ax="LEFT")
        a.text("NAS HARD DRIVE  ·  1-8 BAYS  ·  7200 RPM  ·  CMR", 30.0, h - 42.0, 2.0, ink, font="narrowbd", ax="LEFT", fit=w - 35)
        hdd_label_common(a, cfg, w, h, rnd, ink, lx, lz)
    return art


def art_abyss(cfg):
    def art(a, w, h, rnd, lx, lz):
        ink = "#1c1d1f"
        a.rect(0, 0, w, h, "#eceef0", z=0.06)
        a.rect(0, h - 34.0, w, h, "#14284a", z=0.08)
        a.rect(0, h - 35.2, w, h - 34.0, "#4bb38a", z=0.09)
        a.text("SEACREST", 5.0, h - 9.0, 4.6, "#f2f2f2", font="arialbd", ax="LEFT", space=1.1)
        a.text("ABYSS X20", 5.0, h - 22.0, 9.0, "#ffffff", font="arialbd", ax="LEFT", fit=w * 0.66)
        a.text(cfg["cap"], w - 5.0, h - 22.0, 8.0, "#ffffff", font="arialbd", ax="RIGHT")
        a.text("ENTERPRISE CAPACITY  ·  HELIUM SEALED", 5.0, h - 30.0, 2.2, "#c3cbd8", font="narrowbd", ax="LEFT", fit=w - 10)
        a.rrect(w - 16.0, h - 44.0, 22.0, 6.0, 1.0, "#14284a", z=0.1)
        a.text("He", w - 22.5, h - 44.0, 3.6, "#ffffff", font="arialbd", z=0.2)
        a.text("SEALED", w - 13.0, h - 44.0, 2.0, "#ffffff", font="arialbd", z=0.2)
        a.text("7200 RPM  ·  SATA 6Gb/s  ·  512e/4Kn", 5.0, h - 44.0, 2.0, ink, font="narrowbd", ax="LEFT", fit=w * 0.6)
        hdd_label_common(a, cfg, w, h, rnd, ink, lx, lz)
    return art


HDD = {
    "hdd_seacrest_2tb": dict(cap="2TB", art=art_shoreline, pcb="#1d5a35", helium=False, sn="SN: ZFL4QW2K", pn="ST2000DM008",
                             spec_lines=["MODEL: ST2000DM008-2UB102", "P/N: 2UB102-500  FW: 0001", "DATE: 24315  SITE: KOR",
                                         "+5V ⎓ 0.55A   +12V ⎓ 0.45A"], origin="THAILAND", platters=1),
    "hdd_westline_4tb": dict(cap="4TB", art=art_azure, pcb="#12301f", helium=False, sn="S/N: WX12D93HJ7A1", pn="WD40EZAZ-00SF3B0",
                             spec_lines=["MODEL: WL40EZAZ", "DCM: HANNNTJAAB  R/N: 771824", "DATE: 21 MAY 2024",
                                         "5VDC 0.55A   12VDC 0.40A"], origin="MALAYSIA"),
    "hdd_seacrest_8tb": dict(cap="8TB", art=art_tidewolf, pcb="#1d5a35", helium=False, sn="SN: WKD1H6TQ", pn="ST8000VN004",
                             spec_lines=["MODEL: ST8000VN004-3CP101", "P/N: 3CP101-500  FW: SC60", "DATE: 24192  SITE: TK",
                                         "+5V ⎓ 0.70A   +12V ⎓ 0.72A"], origin="THAILAND"),
    "hdd_seacrest_exos_20tb": dict(cap="20TB", art=art_abyss, pcb="#1d5a35", helium=True, sn="SN: ZVT4A1R2", pn="ST20000NM007D",
                                   spec_lines=["MODEL: ST20000NM007D-3DJ103", "P/N: 3DJ103-500  FW: SN04", "DATE: 24210  SITE: WU",
                                               "+5V ⎓ 0.85A   +12V ⎓ 0.75A"], origin="CHINA"),
}


def hdd_textures(sid, cfg):
    at = pp.Atlas(2048, 2048, bg="#202226")
    rnd = random.Random(zlib.crc32(sid.encode()))
    reg = {}
    hel = cfg["helium"]
    lw, lh = (92.0, 134.0) if hel else (90.0, 128.0)
    lx, lz = (0.0, 0.0) if hel else (1.0, 0.0)
    cfg["label"] = (lx, lz, lw, lh)
    r, uv, ctx = at.panel(lw, lh, 11.0, bg="#e9eaec")
    reg["label"] = uv
    with ctx as a:
        cfg["art"](cfg)(a, lw, lh, rnd, lx, lz)
    # PCB, seen from below: u along +z, v along +x (u right = +z)
    pw, ph = 2 * 47.3, 78.5
    pcb = cfg["pcb"]
    r, uv, ctx = at.panel(pw, ph, 10.0, bg=pcb)
    reg["pcb"] = uv
    with ctx as a:
        traces(a, pw, ph, rnd, pp.shade(pcb, 1.5), 260, pp.shade(pcb, 1.9))
        for i in range(12):
            for j in range(3):
                a.circle(60.0 + i * 2.2, 60.0 + j * 2.2, 0.55, "#c9b06a", z=0.2)
        for k in range(30):
            a.circle(rnd.uniform(4, pw - 4), rnd.uniform(4, ph - 4), 0.7, "#c9b06a", z=0.2)
        a.text("100" + str(zlib.crc32(sid.encode()) % 900000 + 100000) + " REV A", 10.0, 6.0, 2.0, "#e8ece6", font="narrowbd", ax="LEFT")
        a.text("SATA", pw - 30.0, 3.0, 1.8, "#e8ece6", font="narrowbd")
        a.text("PWR", pw - 50.0, 3.0, 1.8, "#e8ece6", font="narrowbd")
    for name, mark in (("soc", ["SEACREST" if "seacrest" in sid else "WESTLINE", "SOC 2T8A", "2419 TW"]),
                       ("dram", ["SORIN", "K4B4G1646", "BCMA"]), ("motor", ["SMOOTH", "MC9171", "2422"])):
        r, uv, ctx = at.panel(10.0, 10.0, 30.0, bg="#1b1c1e")
        reg[name] = uv
        with ctx as a:
            for i, s in enumerate(mark):
                a.text(s, 5.0, 7.0 - i * 2.0, 1.4 if i else 1.6, "#8a8d93", font="agency" if i == 0 else "arialbd", fit=9.0)
    r, uv, ctx = at.panel(20.0, 20.0, 20.0, bg="#d7d8da")
    reg["motor_label"] = uv
    with ctx as a:
        a.ring(10.0, 10.0, 8.0, 8.4, "#2a2b2e", z=0.2)
        a.text("NIDEC-STYLE", 10.0, 13.0, 1.6, "#2a2b2e", font="narrowbd")
        a.text("SPM 7200", 10.0, 10.0, 1.8, "#2a2b2e", font="arialbd")
        a.text("2418", 10.0, 7.0, 1.6, "#2a2b2e", font="narrowbd")
    reg["chip"] = at.swatch("#141518")
    reg["pcb_edge"] = at.swatch(pp.mix(pcb, "#c9a24c", 0.3))
    at.render(pp.tex_path(texname(sid)))
    pp.PREVIEW_TEX[texname(sid)] = (0.0, 0.45)
    return reg


def sata_socket(k, x_mouth, y, seg, depth=7.0):
    """A right-angle SATA socket on a PCB edge: an open shroud facing -x with the keyed tongue and contacts."""
    zc, w = seg["z"], seg["w"]
    hz = w / 2 + 0.8
    hy0, hy1 = y - 2.6, y + 3.6
    g = k["connector_black"]
    xb = x_mouth + depth
    pp.box(g, ((xb - 0.6) * MM, (hy0 + hy1) / 2 * MM, zc * MM), (1.2 * MM, (hy1 - hy0) * MM, 2 * hz * MM))
    pp.box(g, ((x_mouth + xb) / 2 * MM, (hy0 + 0.35) * MM, zc * MM), (depth * MM, 0.7 * MM, 2 * hz * MM))
    pp.box(g, ((x_mouth + xb) / 2 * MM, (hy1 - 0.35) * MM, zc * MM), (depth * MM, 0.7 * MM, 2 * hz * MM))
    for s in (-1, 1):
        pp.box(g, ((x_mouth + xb) / 2 * MM, (hy0 + hy1) / 2 * MM, (zc + s * (hz - 0.35)) * MM), (depth * MM, (hy1 - hy0) * MM, 0.7 * MM))
    # the L-shaped key and the contact tongue
    pp.box(g, ((x_mouth + xb) / 2 * MM + 0.0005, (y - 0.3) * MM, zc * MM), ((depth - 1.0) * MM, 1.1 * MM, (w - 1.2) * MM))
    pp.box(g, ((x_mouth + xb) / 2 * MM + 0.0005, (y + 1.2) * MM, (zc + w / 2 - 0.9) * MM), ((depth - 1.0) * MM, 3.0 * MM, 1.0 * MM))
    n = seg["pins"]
    for i in range(n):
        z = zc - (n - 1) * 1.27 / 2 + i * 1.27
        pp.quad(k["gold"], ((x_mouth + 2.6) * MM, (y + 0.26) * MM, z * MM), (0.0007, 0.0034), normal=(0, 1, 0), up=(1, 0, 0))


def build_hdd(sid):
    cfg = HDD[sid]
    c.reset()
    reg = hdd_textures(sid, cfg)
    TX = "tex_" + texname(sid)
    root = c.root(sid)
    k = pp.Kit("m")
    base = k["alu"]
    hx, hz = HL / 2, HW / 2
    # the casting: main block, the overhang over the connectors, the bottom rails and the pocket fill
    pp.box(base, ((POCKET_X + hx) / 2 * MM, (BODY_Y0 + BODY_Y1) / 2 * MM, 0), ((hx - POCKET_X) * MM, (BODY_Y1 - BODY_Y0) * MM, HW * MM),
           bevel=0.0008)
    pp.box(base, ((-hx + POCKET_X) / 2 * MM, (POCKET_Y + BODY_Y1) / 2 * MM, 0), ((POCKET_X + hx) * MM, (BODY_Y1 - POCKET_Y) * MM, HW * MM),
           bevel=0.0006)
    z_lo, z_hi = HPWR["z"] - HPWR["w"] / 2 - 1.2, HDATA["z"] + HDATA["w"] / 2 + 1.2
    for (za, zb) in ((-hz + RAIL, z_lo), (z_hi, hz - RAIL)):
        pp.box(base, ((-hx + POCKET_X) / 2 * MM, (BODY_Y0 + POCKET_Y) / 2 * MM, (za + zb) / 2 * MM),
               ((POCKET_X + hx) * MM, (POCKET_Y - BODY_Y0) * MM, (zb - za) * MM))
    for s in (-1, 1):
        pp.box(base, (0, (YB + BODY_Y0) / 2 * MM + 0.0001, s * (hz - RAIL / 2) * MM), (HL * MM, (BODY_Y0 - YB + 0.2) * MM, RAIL * MM), bevel=0.0004)
    pp.box(base, ((hx - RAIL / 2) * MM, (YB + BODY_Y0) / 2 * MM + 0.0001, 0), (RAIL * MM, (BODY_Y0 - YB + 0.2) * MM, (HW - 1.0) * MM), bevel=0.0004)
    # ribs on the exposed front part of the bottom casting, and the spindle motor
    for xr in (12.0, 40.0, 58.0):
        pp.box(k["alu_dark"], (xr * MM, (BODY_Y0 - 0.4) * MM, 0), (1.6 * MM, 0.8 * MM, (HW - 2 * RAIL - 4.0) * MM))
    sx, sz = SPINDLE
    pp.cyl(k["alu_dark"], (sx * MM, (BODY_Y0 - 0.35) * MM, sz * MM), 14.0 * MM, 0.7 * MM, axis="y", seg=40, bevel=0.0002)
    pp.quad(k[TX], (sx * MM, (BODY_Y0 - 0.72) * MM, sz * MM), (0.020, 0.020), normal=(0, -1, 0), up=(1, 0, 0), region=reg["motor_label"])
    # side grooves (the drive's recessed side band) as dark inlays
    for s in (-1, 1):
        pp.quad(k["alu_dark"], (0, 4.0 * MM, s * (hz + 0.02) * MM), ((HL - 8.0) * MM, 3.0 * MM), normal=(0, 0, s), up=(0, 1, 0))
    # the PCB under the casting: board, outward-facing chips, the SATA sockets on its rear edge
    px0, px1 = -hx + 0.8, -hx + 0.8 + 78.5
    pcb_map = pp.MultiMap([pp.Planar(reg["pcb"], ((px0 + px1) / 2 * MM, PCB_Y0 * MM, 0), (0, -1, 0), (1, 0, 0),
                                     (2 * 47.3 * MM, (px1 - px0) * MM)), reg["pcb_edge"]])
    pp.box(k[TX], ((px0 + px1) / 2 * MM, (PCB_Y0 + BODY_Y0) / 2 * MM, 0), ((px1 - px0) * MM, (BODY_Y0 - PCB_Y0) * MM, 2 * 47.3 * MM), uv=pcb_map)
    for (name, x, z, s, h) in (("soc", -36.0, -8.0, 13.0, 1.0), ("dram", -16.0, -24.0, 9.0, 0.9), ("motor", -12.0, 18.0, 8.0, 0.8)):
        M = pp.rot("x", 180)
        mp = pp.MultiMap([pp.Planar(reg[name], (x * MM, (PCB_Y0 - h) * MM, z * MM), (0, -1, 0), (1, 0, 0), (s * MM, s * MM)), reg["chip"]])
        pp.box(k[TX], (x * MM, (PCB_Y0 - h / 2) * MM, z * MM), (s * MM, h * MM, s * MM), M, bevel=0.00012, uv=mp)
    rnd = random.Random(zlib.crc32((sid + "p").encode()))
    for i in range(36):
        x, z = rnd.uniform(-70, -2), rnd.uniform(-44, 44)
        if abs(x + 36) < 9 and abs(z + 8) < 9 or abs(x + 16) < 6 and abs(z + 24) < 6 or abs(x + 12) < 6 and abs(z - 18) < 6 or x < -62:
            continue
        pp.box(k["ceramic"], (x * MM, (PCB_Y0 - 0.3) * MM, z * MM), (1.6 * MM, 0.6 * MM, 0.8 * MM), pp.rot("y", rnd.choice([0, 90])))
    for seg in (HDATA, HPWR):
        sata_socket(k, -hx, HCONN_Y, seg)
    # the top cover
    if cfg["helium"]:
        pp.box(k["steel"], (0, (BODY_Y1 + 12.9) / 2 * MM, 0), ((HL - 0.6) * MM, (12.9 - BODY_Y1) * MM, (HW - 0.6) * MM), bevel=0.0005)
        for (cx, cz, w, d) in ((0, hz - 1.6, HL - 3.2, 0.5), (0, -hz + 1.6, HL - 3.2, 0.5)):
            pp.box(k["steel_dark"], (cx * MM, 12.91 * MM, cz * MM), (w * MM, 0.02 * MM, d * MM))
        for xx in (hx - 1.6, -hx + 1.6):
            pp.box(k["steel_dark"], (xx * MM, 12.91 * MM, 0), (0.5 * MM, 0.02 * MM, (HW - 3.2) * MM))
        top = 12.9
    else:
        pp.box(k["steel"], (0, (BODY_Y1 + 12.4) / 2 * MM, 0), ((HL - 2.4) * MM, (12.4 - BODY_Y1) * MM, (HW - 2.4) * MM), bevel=0.0004)
        top = 12.4
        screws = [(hx - 3.4, hz - 3.4), (hx - 3.4, -hz + 3.4), (-hx + 3.4, hz - 3.4), (-hx + 3.4, -hz + 3.4), (6.0, hz - 3.2), (6.0, -hz + 3.2),
                  SPINDLE, PIVOT]
        for (x, z) in screws:
            r = 2.6 if (x, z) in (SPINDLE, PIVOT) else 2.2
            pp.cyl(k["steel_dark"], (x * MM, (top + 0.25) * MM, z * MM), r * MM, 0.5 * MM, axis="y", seg=16, bevel=0.0002)
            for a in range(3):
                pp.box(k["black_plastic"], (x * MM, (top + 0.51) * MM, z * MM), (r * 0.8 * MM, 0.02 * MM, 0.35 * MM), pp.rot("y", a * 60))
        pp.cyl(k["black_plastic"], (-62.0 * MM, (top + 0.01) * MM, 40.0 * MM), 0.7 * MM, 0.04 * MM, axis="y", seg=10)
    lx, lz, lw, lh = cfg["label"]
    pp.quad(k[TX], (lx * MM, (top + 0.03) * MM, lz * MM), (lw * MM, lh * MM), normal=(0, 1, 0), up=(1, 0, 0), region=reg["label"])
    # screw holes: dark discs on the sides and the bottom rails
    for x in SIDE_HOLES:
        for s in (-1, 1):
            pp.cyl(k["black_plastic"], (x * MM, SIDE_HOLE_Y * MM, s * (hz + 0.02) * MM), 1.8 * MM, 0.05 * MM, axis="z", seg=16)
    for x in BOTTOM_HOLES:
        for s in (-1, 1):
            pp.cyl(k["black_plastic"], (x * MM, (YB - 0.02) * MM, s * BOTTOM_HOLE_Z * MM), 1.8 * MM, 0.05 * MM, axis="y", seg=16)
    k.finish(root)

    xa = -hx * MM
    c.anchor("A_PORT_SATA_0", (xa, HCONN_Y * MM, HDATA["z"] * MM), (0.012, 0.007, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.006,pins=7")
    c.anchor("A_PORT_SATAPWR_0", (xa, HCONN_Y * MM, HPWR["z"] * MM), (0.024, 0.007, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="depth=0.006,pins=15")
    n = 0
    for x in SIDE_HOLES:
        for s in (-1, 1):
            c.anchor(f"A_HOLE_{n}", (x * MM, SIDE_HOLE_Y * MM, s * hz * MM), (0.006, 0.006, 0.006), root, forward=(0, 0, s), up=(0, 1, 0),
                     meta="6-32,side")
            n += 1
    for x in BOTTOM_HOLES:
        for s in (-1, 1):
            c.anchor(f"A_HOLE_{n}", (x * MM, YB * MM, s * BOTTOM_HOLE_Z * MM), (0.006, 0.006, 0.006), root, forward=(0, -1, 0), up=(1, 0, 0),
                     meta="6-32,bottom")
            n += 1
    c.anchor("A_HIT_0", (0, 0, 0), (HL * MM, HH * MM, HW * MM), root)
    c.join_by_tag(root, "m")
    c.export(root, sid)
    pp.report(root)
    return root


# ------------------------------------------------------------------ U.2 (2.5" 15 mm, SFF-8639)
UL, UT, UW = 100.45, 15.0, 69.85
U_HOLE_X = bs.HOLE_X
U_HOLE_Y = -UT / 2 + 3.0
U_CONN_Y = -UT / 2 + 2.5
U_BOTTOM_Z = bs.BOTTOM_Z
U_FIN_Y = 2.5              # top of the solid shell; the fins rise to +UT/2
U_CONN = dict(z0=bs.PWR["z"] - bs.PWR["w"] / 2, z1=bs.DATA["z"] + bs.DATA["w"] / 2)

U2 = {
    "ssd_sorin_pm9a3_3840": dict(cap="3.84TB", model="MZQL23T8HCLS-00A07", sn="S/N S64HNE0T401523"),
    "ssd_sorin_pm9a3_7680": dict(cap="7.68TB", model="MZQL27T6HBLA-00A07", sn="S/N S6CKNA0W100842"),
}


def u2_textures(sid, cfg):
    at = pp.Atlas(2048, 1024, bg="#202226")
    rnd = random.Random(zlib.crc32(sid.encode()))
    reg = {}
    # top logo band (between the fins and the connector end): u along +x, v along +z
    r, uv, ctx = at.panel(18.0, UW - 2.0, 16.0, bg="#a9adb3")
    reg["band"] = uv
    with ctx as a:
        a.text("SORIN", 9.0, (UW - 2.0) / 2, 4.0, "#5b5f66", font="arialbd", rot=90, space=1.2)
    sw, sh = 88.0, 60.0
    r, uv, ctx = at.panel(sw, sh, 11.0, bg="#eceef0")
    reg["sticker"] = uv
    with ctx as a:
        ink = "#1a1a1a"
        a.rect(0, sh - 9.0, sw, sh, "#121417", z=0.1)
        a.text("SORIN", 3.0, sh - 4.5, 4.4, "#f2f2f2", font="arialbd", ax="LEFT", space=1.2)
        a.text("PM9A3  NVMe™ U.2 SSD", sw - 3.0, sh - 4.5, 2.6, "#f2f2f2", font="arialbd", ax="RIGHT")
        a.text(cfg["cap"], 3.0, sh - 16.0, 7.0, ink, font="arialbd", ax="LEFT")
        lines = [f"Model: {cfg['model']}", "PCIe Gen4 x4  ·  2.5\" 15mm  ·  SFF-8639", "Rating: 12V ⎓ 1.75A   3.3V ⎓ 25mA",
                 "Power-loss protection  ·  1 DWPD"]
        for i, s in enumerate(lines):
            a.text(s, 3.0, sh - 25.0 - i * 3.6, 2.3, ink, font="narrowbd", ax="LEFT", fit=sw * 0.62)
        barcode(a, 3.0, 4.5, 50.0, 13.0, rnd, ink, unit=0.28)
        a.text(cfg["sn"], 26.5, 2.6, 1.8, ink, font="ocr")
        reg_icons(a, 62.0, 22.0, 6.0, ink)
        a.text("MADE IN KOREA", sw - 3.0, 9.0, 2.0, ink, font="narrowbd", ax="RIGHT")
        a.text("DO NOT REMOVE THIS LABEL", sw - 3.0, 5.0, 1.6, ink, font="narrowbd", ax="RIGHT")
    at.render(pp.tex_path(texname(sid)))
    pp.PREVIEW_TEX[texname(sid)] = (0.5, 0.4)
    return reg


def build_u2(sid):
    cfg = U2[sid]
    c.reset()
    reg = u2_textures(sid, cfg)
    TX = "tex_" + texname(sid)
    root = c.root(sid)
    k = pp.Kit("m")
    al = k["alu"]
    hx, hy, hz = UL / 2, UT / 2, UW / 2
    xe = -hx
    pk = dict(x1=xe + 4.6, y0=-hy + 0.6, y1=U_CONN_Y + 3.4, z0=U_CONN["z0"] - 1.2, z1=U_CONN["z1"] + 1.2)
    # the shell: a solid lower body with the connector pocket at -x
    pp.box(al, ((pk["x1"] + hx) / 2 * MM, (-hy + U_FIN_Y) / 2 * MM, 0), ((hx - pk["x1"]) * MM, (U_FIN_Y + hy) * MM, UW * MM), bevel=0.0006)

    def slab(xa, xb, ya, yb, za, zb):
        pp.box(al, ((xa + xb) / 2 * MM, (ya + yb) / 2 * MM, (za + zb) / 2 * MM), ((xb - xa) * MM, (yb - ya) * MM, (zb - za) * MM))
    slab(xe, pk["x1"], -hy, pk["y0"], -hz + 0.5, hz - 0.5)
    slab(xe, pk["x1"], pk["y1"], U_FIN_Y, -hz + 0.5, hz - 0.5)
    slab(xe, pk["x1"], pk["y0"], pk["y1"], -hz + 0.5, pk["z0"])
    slab(xe, pk["x1"], pk["y0"], pk["y1"], pk["z1"], hz - 0.5)
    # the connector back wall and the SFF-8639 tongue: the SATA-style key, contacts on both faces
    g = k["connector_black"]
    pp.box(g, ((pk["x1"] - 0.4) * MM, (pk["y0"] + pk["y1"]) / 2 * MM, (pk["z0"] + pk["z1"]) / 2 * MM),
           (0.8 * MM, (pk["y1"] - pk["y0"]) * MM, (pk["z1"] - pk["z0"]) * MM))
    zc = (U_CONN["z0"] + U_CONN["z1"]) / 2
    zw = U_CONN["z1"] - U_CONN["z0"]
    pp.box(g, ((xe + 2.6) * MM, U_CONN_Y * MM, zc * MM), (3.8 * MM, 1.1 * MM, (zw - 1.2) * MM), bevel=0.0001)
    pp.box(g, ((xe + 2.6) * MM, (U_CONN_Y + 1.15) * MM, (U_CONN["z1"] - 0.9) * MM), (3.8 * MM, 3.4 * MM, 1.0 * MM))
    n = int((zw - 2.4) / 0.8)
    for i in range(n):
        z = U_CONN["z0"] + 1.2 + i * 0.8
        pp.quad(k["gold"], ((xe + 2.4) * MM, (U_CONN_Y + 0.56) * MM, z * MM), (0.00045, 0.0030), normal=(0, 1, 0), up=(1, 0, 0))
        if i % 2 == 0:
            pp.quad(k["gold"], ((xe + 2.4) * MM, (U_CONN_Y - 0.56) * MM, z * MM), (0.00045, 0.0030), normal=(0, -1, 0), up=(1, 0, 0))
    # top: a flat logo band at the connector end, then longitudinal fins over the rest
    bx0, bx1 = xe, xe + 18.0
    pp.box(al, ((bx0 + bx1) / 2 * MM, (U_FIN_Y + hy) / 2 * MM, 0), ((bx1 - bx0) * MM, (hy - U_FIN_Y) * MM, UW * MM), bevel=0.0006)
    pp.quad(k[TX], ((bx0 + bx1) / 2 * MM, (hy + 0.02) * MM, 0), ((bx1 - bx0 - 1.0) * MM, (UW - 2.0) * MM), normal=(0, 1, 0), up=(0, 0, 1),
            region=reg["band"])
    nf = 15
    pitch = (UW - 2.0) / (nf - 1)
    for i in range(nf):
        z = -(UW - 2.0) / 2 + i * pitch
        pp.box(al, ((bx1 + hx) / 2 * MM, (U_FIN_Y + hy) / 2 * MM, z * MM), ((hx - bx1 - 0.6) * MM, (hy - U_FIN_Y) * MM, 1.6 * MM), bevel=0.0003)
    pp.box(al, ((hx - 0.5) * MM, (U_FIN_Y + hy) / 2 * MM, 0), (1.0 * MM, (hy - U_FIN_Y) * MM, UW * MM), bevel=0.0003)
    # the seam between the top shell and the bottom cover, the bottom cover screws and the big label
    pp.box(k["alu_dark"], (0, (-hy + 2.0) * MM, 0), ((UL + 0.02) * MM, 0.25 * MM, (UW + 0.02) * MM))
    for (sx, sz) in ((-40.0, -30.5), (-40.0, 30.5), (44.0, -30.5), (44.0, 30.5)):
        pp.cyl(k["steel"], (sx * MM, (-hy - 0.15) * MM, sz * MM), 1.6 * MM, 0.3 * MM, axis="y", seg=14, bevel=0.0001)
    pp.quad(k[TX], (2.0 * MM, (-hy - 0.03) * MM, 0), (0.088, 0.060), normal=(0, -1, 0), up=(0, 0, 1), region=reg["sticker"])
    for x in U_HOLE_X:
        for s in (-1, 1):
            pp.cyl(k["black_plastic"], (x * MM, U_HOLE_Y * MM, s * (hz + 0.02) * MM), 1.45 * MM, 0.05 * MM, axis="z", seg=16)
            pp.cyl(k["black_plastic"], (x * MM, (-hy - 0.02) * MM, s * U_BOTTOM_Z * MM), 1.45 * MM, 0.05 * MM, axis="y", seg=16)
    k.finish(root)

    c.anchor("A_PORT_U2_0", (xe * MM, U_CONN_Y * MM, zc * MM), (0.040, 0.007, 0.008), root, forward=(-1, 0, 0), up=(0, 1, 0),
             meta="sff8639,pcie=4x4,depth=0.0045")
    n = 0
    for x in U_HOLE_X:
        for s in (-1, 1):
            c.anchor(f"A_SCREW_PH2_{n}", (x * MM, U_HOLE_Y * MM, s * hz * MM), (0.006, 0.006, 0.006), root, forward=(0, 0, s), up=(0, 1, 0),
                     meta="m3,side")
            n += 1
    n = 0
    for x in U_HOLE_X:
        for s in (-1, 1):
            c.anchor(f"A_HOLE_{n}", (x * MM, -hy * MM, s * U_BOTTOM_Z * MM), (0.006, 0.006, 0.006), root, forward=(0, -1, 0), up=(1, 0, 0),
                     meta="m3,bottom")
            n += 1
    c.anchor("A_HIT_0", (0, 0, 0), (UL * MM, UT * MM, UW * MM), root)
    c.join_by_tag(root, "m")
    c.export(root, sid)
    pp.report(root)
    return root


def build(sid):
    return build_hdd(sid) if sid in HDD else build_u2(sid)


def previews(sid, root):
    if sid in HDD:
        pp.preview(root, sid, views=((30, 35), (-130, 25), (160, -50)), size=(960, 720), dist=0.42)
        pp.preview(root, sid, views=((-90, 12),), size=(960, 720), dist=0.13, target=(-0.07, -0.005, 0.02), start=3)
    else:
        pp.preview(root, sid, views=((30, 35), (-120, 25), (160, -45)), size=(960, 720), dist=0.28)
        pp.preview(root, sid, views=((-90, 10),), size=(960, 720), dist=0.10, target=(-0.05, -0.004, 0.008), start=3)
