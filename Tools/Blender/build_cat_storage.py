"""
Catalogue 14, storage: 8 M.2 NVMe drives, 3 2.5" SATA SSDs, 4 3.5" hard drives and 2 enterprise U.2 drives.

Run: blender -b --factory-startup -P Tools/Blender/build_cat_storage.py -- [ids...] [--nopreview] [--json]

No ids = all of them. Each id writes Assets/Resources/Models/<id>.fbx, its texture Textures/<id>.png, previews
Logs/ModelPreviews/<id>_0..3.png (EEVEE), and its block in Logs/ModelPreviews/cat_storage_report.txt.
docs/catalog/storage.json is rewritten from the CATALOG below on every run (--json writes only that).

Contracts (frames and anchors, see docs/reports/cat_storage.md):
  M.2 2280  = ssd_1tb       (cat_storage_ssd.build_m2)
  2.5" SATA = ssd_sata_500  (cat_storage_ssd.build_sata)
  3.5" HDD  = new           (cat_storage_hdd.build_hdd)
  U.2       = new           (cat_storage_hdd.build_u2)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402

ROOT = c.PROJECT


# ================================================================== label art (mm, u = 0 at the drive's +x end)

def facets(a, x0, x1, h, rnd, base, n=14, z=0.12):
    """Angular grey facets (a stylised low-poly pattern)."""
    xs = sorted(rnd.uniform(x0, x1) for _ in range(n))
    prev = (x0, rnd.uniform(0, h))
    for x in xs:
        p = (x, rnd.uniform(0, h))
        a.poly([prev, p, (p[0] + rnd.uniform(-3, 3), h if rnd.random() < 0.5 else 0.0)], pp.shade(base, rnd.uniform(1.4, 2.6)), z=z)
        prev = p


def art_990pro(cap):
    def art(a, w, h, rnd):
        for i in range(24):
            a.rect(i * w / 24, 0, (i + 1) * w / 24 + 0.05, h, pp.mix("#191a1c", "#0c0c0d", abs(i - 9) / 15.0), z=0.08)
        a.text("SORIN", 3.0, h - 3.4, 2.0, "#e8e8e8", font="arialbd", ax="LEFT", space=1.25)
        a.text("990 PRO", 3.0, h * 0.47, 6.2, "#f4f4f4", font="arial", ax="LEFT")
        a.text("NVMe™ M.2 SSD", 3.2, 3.6, 1.5, "#a9acb2", font="arialbd", ax="LEFT")
        a.text(cap, w - 3.0, 3.6, 2.4, "#f4f4f4", font="arialbd", ax="RIGHT")
        a.line([(3.0, 6.0), (w - 3.0, 6.0)], 0.08, "#4a4c50", z=0.2, joins=False)
        a.text("PCIe® 4.0 x4", w - 3.0, h - 3.4, 1.3, "#a9acb2", font="arialbd", ax="RIGHT")
    return art


def art_990pro_hs(a, w, h, rnd):
    a.rect(0, 0, w, h, "#121315", z=0.06)
    for i in range(9):
        x = 4.0 + i * 7.5
        a.line([(x, 0.6), (x + 9.0, h - 0.6)], 0.12, "#2c2e32", z=0.1, joins=False)
    a.poly([(w * 0.42, 0), (w * 0.62, 0), (w * 0.70, h), (w * 0.50, h)], "#18191c", z=0.11)
    a.text("990 PRO", 6.0, h * 0.5, 4.8, "#e9e9e9", font="arial", ax="LEFT")
    a.text("SORIN", w - 6.0, h * 0.5, 2.0, "#bfc2c7", font="arialbd", ax="RIGHT", space=1.25)


def art_980(cap):
    def art(a, w, h, rnd):
        a.rect(0, 0, w, h, "#121212", z=0.06)
        a.rect(0, h - 1.2, w, h, "#2a2b2e", z=0.08)
        a.text("SORIN", 3.0, h - 4.2, 2.0, "#e8e8e8", font="arialbd", ax="LEFT", space=1.25)
        a.text("980", 3.0, h * 0.42, 7.0, "#f4f4f4", font="arial", ax="LEFT")
        a.text("NVMe™ M.2 SSD", 17.5, h * 0.42, 1.6, "#a9acb2", font="arialbd", ax="LEFT")
        a.text(cap, w - 3.0, 3.4, 2.2, "#f4f4f4", font="arialbd", ax="RIGHT")
        a.text("PCIe® 3.0 x4", w - 3.0, h - 4.2, 1.3, "#a9acb2", font="arialbd", ax="RIGHT")
    return art


def art_sn850x(cap):
    def art(a, w, h, rnd):
        a.rect(0, 0, w, h, "#0d0d0f", z=0.06)
        facets(a, w * 0.48, w, h, rnd, "#16171a", 16)
        a.text("WESTLINE", 3.0, h - 3.4, 2.4, "#f2f2f2", font="agency", ax="LEFT", space=1.1)
        a.text("ONYX", 3.8 + a.text_width("WESTLINE", 2.4, "agency", 1.1), h - 3.4, 2.4, "#9fa3a9", font="agency", ax="LEFT")
        a.text("SN850X", 3.0, h * 0.42, 5.6, "#f4f4f4", font="agency", ax="LEFT")
        a.text("NVMe™ SSD", 3.2, 3.0, 1.4, "#a9acb2", font="arialbd", ax="LEFT")
        a.rect(w - 13.0, 1.6, w - 2.6, 5.6, "#0d0d0f", z=0.25)
        a.text(cap, w - 3.0, 3.6, 2.6, "#f4f4f4", font="agency", ax="RIGHT", z=0.3)
    return art


def art_sn850x_hs(a, w, h, rnd):
    a.rect(0, 0, w, h, "#111214", z=0.06)
    facets(a, 0.0, w * 0.4, h, rnd, "#141517", 8)
    a.text("SN850X", w * 0.46, h * 0.5, 4.2, "#e9e9e9", font="agency", ax="LEFT")
    a.text("WESTLINE ONYX", w * 0.46 + 0.2, h * 0.5 - 4.0, 1.3, "#a5a8ad", font="agency", ax="LEFT")


def art_sn580(cap):
    def art(a, w, h, rnd):
        for i in range(20):
            a.rect(i * w / 20, 0, (i + 1) * w / 20 + 0.05, h, pp.mix("#2a74c9", "#123d72", i / 19.0), z=0.08)
        a.poly([(w * 0.55, 0), (w, 0), (w, h), (w * 0.72, h)], "#0f3563", z=0.1)
        a.text("WESTLINE", 3.0, h - 3.6, 2.4, "#ffffff", font="agency", ax="LEFT", space=1.1)
        a.text("AZURE", 3.8 + a.text_width("WESTLINE", 2.4, "agency", 1.1), h - 3.6, 2.4, "#bcd7f5", font="agency", ax="LEFT")
        a.text("SN580", 3.0, h * 0.42, 5.8, "#ffffff", font="agency", ax="LEFT")
        a.text("NVMe™ SSD", 3.2, 3.0, 1.4, "#d7e6f7", font="arialbd", ax="LEFT")
        a.text(cap, w - 3.0, 3.6, 2.6, "#ffffff", font="agency", ax="RIGHT")
        a.text("PCIe® Gen4", w - 3.0, h - 3.6, 1.3, "#bcd7f5", font="arialbd", ax="RIGHT")
    return art


def crux_logo(a, x, y, r, col="#3aa0e0", z=0.3):
    a.ring(x, y, r * 0.62, r, col, z=z)
    for k in range(3):
        a.poly([(x - r * 0.62, y - r * 0.18 + k * r * 0.2), (x + r * 0.62, y + r * 0.02 + k * r * 0.2),
                (x + r * 0.62, y + r * 0.14 + k * r * 0.2), (x - r * 0.62, y - r * 0.06 + k * r * 0.2)], col, z=z)


def art_p3plus(cap):
    def art(a, w, h, rnd):
        a.rect(0, 0, w, h, "#101215", z=0.06)
        a.rect(0, 0, w, 1.4, "#1f6fb4", z=0.08)
        a.poly([(w * 0.62, 1.4), (w, 1.4), (w, h * 0.55)], "#16181c", z=0.09)
        crux_logo(a, 5.0, h - 4.6, 2.4)
        a.text("crux", 8.4, h - 4.6, 3.2, "#f2f2f2", font="arialbd", ax="LEFT")
        a.text("P3 Plus", 3.0, h * 0.40, 5.0, "#f4f4f4", font="arialbd", ax="LEFT")
        a.text("PCIe® Gen4 NVMe™ SSD", 3.2, 3.2, 1.3, "#a9acb2", font="arialbd", ax="LEFT")
        a.text(cap, w - 3.0, h - 4.6, 2.8, "#3aa0e0", font="arialbd", ax="RIGHT")
    return art


def art_t705_bar(a, w, h, rnd):
    a.rect(0, 0, w, h, "#1a1b1e", z=0.06)
    a.rect(0, h - 0.5, w, h, "#9ea2a8", z=0.08)
    a.rect(0, 0, w, 0.5, "#9ea2a8", z=0.08)
    a.text("T705", w * 0.5, h * 0.5, 3.6, "#e6e7e9", font="arialbd")
    crux_logo(a, 6.0, h * 0.5, 1.8, "#c7cacf")
    a.text("Gen5", w - 6.0, h * 0.5, 1.6, "#c7cacf", font="arialbd")


# 2.5" tops (u = 0 at the connector end, v across the width)

def art_870(a, w, h, rnd):
    a.rect(0, 0, w, h, "#17181a", z=0.06)
    a.rrect(w * 0.5, h * 0.5, w - 8.0, h - 8.0, 2.0, "#202124", z=0.08)
    a.text("SORIN", 10.0, h * 0.70, 5.0, "#e8e8e8", font="arialbd", ax="LEFT", space=1.25)
    a.text("870 EDGE", 10.0, h * 0.50, 7.0, "#f4f4f4", font="arial", ax="LEFT")
    a.text("SATA III 2.5\" SSD", 10.4, h * 0.34, 2.6, "#a9acb2", font="arialbd", ax="LEFT")
    a.text("1TB", w - 10.0, 9.0, 5.0, "#f4f4f4", font="arialbd", ax="RIGHT")


def art_mx500(a, w, h, rnd):
    for k in range(180):
        y = rnd.uniform(0, h)
        x0 = rnd.uniform(-20, w)
        a.line([(x0, y), (x0 + rnd.uniform(20, 70), y)], rnd.uniform(0.05, 0.2), pp.shade("#55585e", rnd.uniform(0.9, 1.12)), z=0.1, joins=False)
    a.rrect(w * 0.47, h * 0.5, 62.0, 40.0, 1.2, "#111215", z=0.2)
    crux_logo(a, w * 0.47 - 22.0, h * 0.5 + 9.0, 4.2, "#3aa0e0", z=0.3)
    a.text("crux", w * 0.47 - 16.0, h * 0.5 + 9.0, 6.0, "#f2f2f2", font="arialbd", ax="LEFT", z=0.3)
    a.text("MX500", w * 0.47 - 26.0, h * 0.5 - 4.0, 7.0, "#f4f4f4", font="arialbd", ax="LEFT", z=0.3)
    a.text("2TB  SATA  2.5\" 7mm", w * 0.47 - 26.0, h * 0.5 - 13.0, 2.4, "#a9acb2", font="arialbd", ax="LEFT", z=0.3)


def art_a400(a, w, h, rnd):
    a.rect(0, 0, w, h, "#121214", z=0.06)
    a.rrect(w * 0.5, h * 0.5, w - 6.0, h - 6.0, 2.5, "#1b1b1e", z=0.08)
    a.rect(6.0, h * 0.5 + 9.0, 9.5, h * 0.5 + 16.0, "#d3202a", z=0.2)
    a.text("KINGSLAND", 11.0, h * 0.5 + 12.5, 4.6, "#f2f2f2", font="arialbd", ax="LEFT")
    a.text("A400", 6.0, h * 0.5 - 1.0, 11.0, "#f4f4f4", font="arialbd", ax="LEFT")
    a.text("SSD", 41.0, h * 0.5 - 2.6, 4.0, "#d3202a", font="arialbd", ax="LEFT")
    a.text("480GB", w - 7.0, 9.0, 5.4, "#f4f4f4", font="arialbd", ax="RIGHT")
    a.text("SATA 3  2.5\"", 6.4, 9.0, 2.6, "#a9acb2", font="arialbd", ax="LEFT")


# ================================================================== M.2 layouts

def cols(*specs):
    """Passive columns: (x, y0, y1, step, ang, kind) -> list of (x, y, ang, kind)."""
    out = []
    for (x, y0, y1, step, ang, kind) in specs:
        n = int(round((y1 - y0) / step)) + 1
        out += [(x, y0 + i * step, ang, kind) for i in range(n)]
    return out


NAND = (17.5, 12.0)


def m2_cfg(**kw):
    base = dict(pmic=(33.4, 6.0), inductors=[(33.4, -4.6)], label_x=(-36.6, 36.4), label_w=20.0, sticker_x=0.0,
                passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (36.2, -9.0, -1.0, 1.6, 0, "cap"), (30.0, -9.4, 9.4, 2.35, 0, "res")))
    base.update(kw)
    base["chips_top"] = [(base["ctrl"]["x"], 0.0, base["ctrl"]["s"], base["ctrl"]["s"])] + list(base["nand"]) + \
        ([(base["dram"][0], base["dram"][1], 8.0, 8.0)] if base.get("dram") else [])
    return base


SORIN_CTRL = dict(x=-28.0, s=11.0, h=1.15, nickel=True, top="#9a8f80", ink="#3b3732", side="#141518",
                  mark=["SORIN", "S4LV008", "PASCAL", "2338 KOREA"])

M2 = [
    m2_cfg(id="ssd_sorin_990pro_1tb", brand="Sorin", ctrl=SORIN_CTRL, dram=(-15.0, 0.0),
           nand=[(2.0, 0.0) + NAND], label_art=art_990pro("1TB"),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (-15.0, -9.6, -5.2, 1.1, 0, "res"), (13.6, -8.0, 8.0, 2.0, 90, "cap"),
                         (30.0, -9.4, 9.4, 2.35, 0, "res")),
           sticker_lines=["NVMe M.2 SSD  990 PRO", "Model: MZ-V9P1T0", "1TB   3.3V ⎓ 2.8A"], origin="KOREA",
           nand_mark=["SORIN", "K9DVGY8J5B", "CCK0 2338"], sn="S/N S73VNJ0W412718A"),
    m2_cfg(id="ssd_sorin_990pro_2tb_hs", brand="Sorin", ctrl=SORIN_CTRL, dram=(-15.0, 0.0),
           nand=[(0.0, 0.0) + NAND, (19.5, 0.0) + NAND], label_art=art_990pro("2TB"),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (-15.0, -9.6, -5.2, 1.1, 0, "res"), (31.0, -9.4, 9.4, 2.35, 0, "res")),
           pmic=(34.6, 6.0), inductors=[(34.6, -4.6)],
           sticker_lines=["NVMe M.2 SSD  990 PRO w/ Heatsink", "Model: MZ-V9P2T0", "2TB   3.3V ⎓ 2.8A"], origin="KOREA",
           heatsink=dict(kind="sorin", x=(-35.0, 36.6), w=24.2, bottom=-1.2, base_top=7.0, top_size=(71.6, 23.4), art=art_990pro_hs)),
    m2_cfg(id="ssd_sorin_980_500", brand="Sorin",
           ctrl=dict(x=-27.0, s=10.0, h=1.0, top="#1b1c1e", mark=["SORIN", "S4LR033", "PABLO", "2214 KOREA"]),
           nand=[(-6.0, 0.0) + NAND], label_art=art_980("500GB"),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (5.0, -8.0, 8.0, 2.0, 90, "cap"), (20.0, -9.4, 9.4, 2.35, 0, "res"),
                         (26.0, -6.0, 6.0, 2.0, 90, "cap")),
           sticker_lines=["NVMe M.2 SSD  980", "Model: MZ-V8V500", "500GB   3.3V ⎓ 1.8A"], origin="KOREA",
           nand_mark=["SORIN", "K9DKGZ8E5D", "XCK0 2214"]),
    m2_cfg(id="ssd_westline_sn850x_2tb", brand="Westline",
           ctrl=dict(x=-27.5, s=10.5, h=1.1, top="#1b1c1e", mark=["WESTLINE", "20-82-10081", "A2 2251", "TAIWAN"]),
           dram=(-14.5, 0.0), nand=[(1.0, 0.0) + NAND, (20.5, 0.0) + NAND],
           chips_bottom=[(1.0, 0.0) + NAND, (20.5, 0.0) + NAND],
           label_art=art_sn850x("2TB"), sticker_x=10.75, sticker_size=(36.0, 12.0),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (-14.5, -9.6, -5.2, 1.1, 0, "res"), (31.5, -9.4, 9.4, 2.35, 0, "res")),
           pmic=(34.8, 6.0), inductors=[(34.8, -4.6)],
           sticker_lines=["WESTLINE ONYX SN850X", "Model: WLS200T2X0E", "2TB   3.3V ⎓ 2.5A"], origin="MALAYSIA",
           nand_mark=["WESTLINE", "60124 2TB", "BICS5 2302"], dram_mark=["SORIN", "K4AAG165WA", "BCWE"]),
    m2_cfg(id="ssd_westline_sn850x_1tb_hs", brand="Westline",
           ctrl=dict(x=-27.5, s=10.5, h=1.1, top="#1b1c1e", mark=["WESTLINE", "20-82-10081", "A2 2251", "TAIWAN"]),
           dram=(-14.5, 0.0), nand=[(1.0, 0.0) + NAND], label_art=art_sn850x("1TB"),
           sticker_lines=["WESTLINE ONYX SN850X Heatsink", "Model: WLS100T2XHE", "1TB   3.3V ⎓ 2.5A"], origin="MALAYSIA",
           heatsink=dict(kind="westline", x=(-35.0, 36.6), w=24.2, bottom=-1.2, base_top=6.6, top_size=(71.6, 23.4), art=art_sn850x_hs)),
    m2_cfg(id="ssd_westline_sn580_1tb", brand="Westline",
           ctrl=dict(x=-28.0, s=9.0, h=1.0, top="#1b1c1e", mark=["WESTLINE", "A101-000172", "2318 TW"]),
           nand=[(-10.0, 0.0) + NAND], label_art=art_sn580("1TB"),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (1.0, -8.0, 8.0, 2.0, 90, "cap"), (12.0, -9.4, 9.4, 2.35, 0, "res")),
           pmic=(18.0, 6.0), inductors=[(18.0, -4.6)],
           sticker_lines=["WESTLINE AZURE SN580", "Model: WLS100T3B0E", "1TB   3.3V ⎓ 2.0A"], origin="MALAYSIA",
           nand_mark=["WESTLINE", "60130 1TB", "BICS5 2311"]),
    m2_cfg(id="ssd_crux_p3plus_2tb", brand="Crux", pcb="#14301f", silk="#e8ece6",
           ctrl=dict(x=-27.0, s=10.0, h=1.0, top="#1b1c1e", mark=["PHISON", "PS5021-E21T", "2317 TAIWAN"]),
           nand=[(-6.0, 0.0) + NAND, (13.0, 0.0) + NAND], label_art=art_p3plus("2TB"),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (24.5, -8.0, 8.0, 2.0, 90, "cap"), (30.0, -9.4, 9.4, 2.35, 0, "res")),
           sticker_lines=["Crux P3 Plus  CT2000P3PSSD8", "PCIe Gen4 NVMe  M.2 2280", "2TB   3.3V ⎓ 2.5A"], origin="CHINA",
           nand_mark=["CRUX", "NY240 QLC", "2316"]),
    m2_cfg(id="ssd_crux_t705_2tb_hs", brand="Crux",
           ctrl=dict(x=-27.0, s=12.0, h=1.2, top="#1b1c1e", mark=["PHISON", "PS5026-E26", "2402 TAIWAN"]),
           dram=(-13.0, 0.0), nand=[(2.0, 0.0) + NAND, (21.0, 0.0) + NAND], chips_bottom=[(2.0, 0.0) + NAND, (21.0, 0.0) + NAND],
           label_art=art_p3plus("2TB"), sticker_x=11.5, sticker_size=(36.0, 12.0),
           passives=cols((-35.6, -8.0, 8.0, 3.2, 90, "cap"), (32.0, -9.4, 9.4, 2.35, 0, "res")),
           pmic=(35.0, 6.0), inductors=[(35.0, -4.6)],
           sticker_lines=["Crux T705  CT2000T705SSD5", "PCIe Gen5 NVMe  M.2 2280", "2TB   3.3V ⎓ 3.3A"], origin="CHINA",
           heatsink=dict(kind="fins", x=(-35.0, 36.6), w=24.6, bottom=-2.0, base_top=3.4, fin_top=20.6, fins=13, bar_w=7.0,
                         top_size=(71.6, 7.0), top_bg="#1a1b1e", art=art_t705_bar)),
]

SATA = [
    dict(id="ssd_sorin_870_1tb", brand="Sorin", top_art=art_870, top_bg="#17181a", cover="#1a1b1d",
         sticker_lines=["Model: MZ-77E1T0", "Capacity: 1TB", "Rating: 5V ⎓ 1.2A", "FW: SVT02B6Q", "870 EDGE  SATA 6Gb/s"],
         origin="KOREA", sn="S/N S6PUNX0T803211K", lid_bevel=0.9, lid_seg=2),
    dict(id="ssd_crux_mx500_2tb", brand="Crux", top_art=art_mx500, top_bg="#55585e", cover="#4c4f55", tray="steel_dark",
         sticker_lines=["Model: CT2000MX500SSD1", "Capacity: 2TB", "Rating: 5V ⎓ 1.7A", "FW: M3CR046", "MX500  SATA 6Gb/s"],
         origin="CHINA", sn="S/N 2318E6A4F2C1", pbr=(0.55, 0.38), top_screws=[(-44.5, -31.0), (-44.5, 31.0), (44.5, -31.0), (44.5, 31.0)]),
    dict(id="ssd_kingsland_a400_480", brand="Kingsland", top_art=art_a400, top_bg="#121214", cover="#141416", tray="black_plastic",
         seam="dark_plastic", sticker_lines=["Model: SA400S37/480G", "Capacity: 480GB", "Rating: 5V ⎓ 1.1A", "FW: SBFK71F1",
                                             "A400  SATA Rev. 3.0"], origin="TAIWAN", sn="S/N 50026B7784C3A1F2", lid_bevel=1.2, lid_seg=2),
]

# ================================================================== catalogue data

CATALOG = [
    dict(id="ssd_sorin_990pro_1tb", brand="Sorin", name="Sorin 990 Pro 1 TB", price=99, power_w=8, color="#141414", rgb=False,
         analog="Samsung 990 PRO 1TB", desc="Fast PCIe 4.0 NVMe drive with a nickel-coated controller, up to 7450 MB/s.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=7450, write_mbs=6900, tbw=600, dram=True, nand="TLC",
                    sides=1, has_heatsink=False), game=dict(storage_gb=1000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_sorin_990pro_2tb_hs", brand="Sorin", name="Sorin 990 Pro 2 TB Heatsink", price=179, power_w=9, color="#121315", rgb=True,
         analog="Samsung 990 PRO with Heatsink 2TB", desc="The 990 Pro with a black aluminium heatsink and an RGB light bar.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=7450, write_mbs=6900, tbw=1200, dram=True, nand="TLC",
                    sides=1, has_heatsink=True, height_mm=8.2), game=dict(storage_gb=2000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_sorin_980_500", brand="Sorin", name="Sorin 980 500 GB", price=45, power_w=5, color="#121212", rgb=False,
         analog="Samsung 980 500GB", desc="A budget PCIe 3.0 NVMe drive without DRAM, a big step up from SATA.",
         specs=dict(form="M.2 2280", interface="PCIe 3.0 x4 NVMe", read_mbs=3100, write_mbs=2600, tbw=300, dram=False, nand="TLC",
                    sides=1, has_heatsink=False), game=dict(storage_gb=500, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_westline_sn850x_2tb", brand="Westline", name="Westline Onyx SN850X 2 TB", price=139, power_w=9, color="#0d0d0f", rgb=False,
         analog="WD_BLACK SN850X 2TB", desc="A gaming PCIe 4.0 drive with DRAM cache and chips on both sides.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=7300, write_mbs=6600, tbw=1200, dram=True, nand="TLC",
                    sides=2, has_heatsink=False), game=dict(storage_gb=2000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_westline_sn850x_1tb_hs", brand="Westline", name="Westline Onyx SN850X 1 TB Heatsink", price=99, power_w=8, color="#111214",
         rgb=True, analog="WD_BLACK SN850X with Heatsink 1TB", desc="The SN850X with a finned heatsink and an RGB light bar.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=7300, write_mbs=6300, tbw=600, dram=True, nand="TLC",
                    sides=1, has_heatsink=True, height_mm=8.8), game=dict(storage_gb=1000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_westline_sn580_1tb", brand="Westline", name="Westline Azure SN580 1 TB", price=59, power_w=5, color="#2a74c9", rgb=False,
         analog="WD Blue SN580 1TB", desc="A cool-running DRAM-less PCIe 4.0 drive for everyday builds.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=4150, write_mbs=4150, tbw=600, dram=False, nand="TLC",
                    sides=1, has_heatsink=False), game=dict(storage_gb=1000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_crux_p3plus_2tb", brand="Crux", name="Crux P3 Plus 2 TB", price=109, power_w=6, color="#101215", rgb=False,
         analog="Crucial P3 Plus 2TB", desc="Lots of PCIe 4.0 space for little money: QLC flash, no DRAM.",
         specs=dict(form="M.2 2280", interface="PCIe 4.0 x4 NVMe", read_mbs=5000, write_mbs=4200, tbw=440, dram=False, nand="QLC",
                    sides=1, has_heatsink=False), game=dict(storage_gb=2000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_crux_t705_2tb_hs", brand="Crux", name="Crux T705 2 TB Heatsink", price=249, power_w=12, color="#1a1b1e", rgb=False,
         analog="Crucial T705 with heatsink 2TB", desc="A PCIe 5.0 flagship, 14500 MB/s, under a tall finned heatsink.",
         specs=dict(form="M.2 2280", interface="PCIe 5.0 x4 NVMe", read_mbs=14500, write_mbs=12700, tbw=1200, dram=True, nand="TLC",
                    sides=2, has_heatsink=True, height_mm=22.6), game=dict(storage_gb=2000, sata25=False), contract="ssd_1tb"),
    dict(id="ssd_sorin_870_1tb", brand="Sorin", name="Sorin 870 Edge 1 TB", price=89, power_w=4, color="#17181a", rgb=False,
         analog="Samsung 870 EVO 1TB", desc="The reliable 2.5\" SATA classic, 560 MB/s, 7 mm.",
         specs=dict(form="2.5\" 7 mm", interface="SATA 6 Gb/s", read_mbs=560, write_mbs=530, tbw=600, dram=True, nand="TLC"),
         game=dict(storage_gb=1000, sata25=True), contract="ssd_sata_500"),
    dict(id="ssd_crux_mx500_2tb", brand="Crux", name="Crux MX500 2 TB", price=129, power_w=4, color="#55585e", rgb=False,
         analog="Crucial MX500 2TB", desc="Two terabytes of SATA SSD in a grey metal shell.",
         specs=dict(form="2.5\" 7 mm", interface="SATA 6 Gb/s", read_mbs=560, write_mbs=510, tbw=700, dram=True, nand="TLC"),
         game=dict(storage_gb=2000, sata25=True), contract="ssd_sata_500"),
    dict(id="ssd_kingsland_a400_480", brand="Kingsland", name="Kingsland A400 480 GB", price=32, power_w=2, color="#121214", rgb=False,
         analog="Kingston A400 480GB", desc="The cheapest way off a hard drive: a plastic-shell SATA SSD.",
         specs=dict(form="2.5\" 7 mm", interface="SATA 6 Gb/s", read_mbs=500, write_mbs=450, tbw=160, dram=False, nand="TLC"),
         game=dict(storage_gb=480, sata25=True), contract="ssd_sata_500"),
    dict(id="hdd_seacrest_2tb", brand="Seacrest", name="Seacrest Shoreline 2 TB", price=64, power_w=5, color="#c9ccd0", rgb=False,
         analog="Seagate BarraCuda 2TB (ST2000DM008)", desc="A 7200 rpm desktop hard drive for bulk games and files.",
         specs=dict(form="3.5\"", interface="SATA 6 Gb/s", rpm=7200, cache_mb=256, read_mbs=220, recording="SMR", helium=False),
         game=dict(storage_gb=2000, sata25=False), contract="hdd35", new_contract=True),
    dict(id="hdd_westline_4tb", brand="Westline", name="Westline Azure 4 TB", price=84, power_w=5, color="#c9ccd0", rgb=False,
         analog="WD Blue 4TB (WD40EZAZ)", desc="A quiet 5400 rpm-class desktop drive with lots of room.",
         specs=dict(form="3.5\"", interface="SATA 6 Gb/s", rpm=5400, cache_mb=256, read_mbs=180, recording="SMR", helium=False),
         game=dict(storage_gb=4000, sata25=False), contract="hdd35", new_contract=True),
    dict(id="hdd_seacrest_8tb", brand="Seacrest", name="Seacrest Tidewolf 8 TB NAS", price=179, power_w=8, color="#c9ccd0", rgb=False,
         analog="Seagate IronWolf 8TB (ST8000VN004)", desc="A NAS drive built for 24/7 duty in multi-bay boxes.",
         specs=dict(form="3.5\"", interface="SATA 6 Gb/s", rpm=7200, cache_mb=256, read_mbs=210, recording="CMR", helium=True,
                    workload_tby=180), game=dict(storage_gb=8000, sata25=False), contract="hdd35", new_contract=True),
    dict(id="hdd_seacrest_exos_20tb", brand="Seacrest", name="Seacrest Abyss X20 20 TB", price=329, power_w=9, color="#c9ccd0", rgb=False,
         analog="Seagate Exos X20 20TB (ST20000NM007D)", desc="A sealed helium enterprise drive for servers and storage racks.",
         specs=dict(form="3.5\"", interface="SATA 6 Gb/s", rpm=7200, cache_mb=256, read_mbs=272, recording="CMR", helium=True,
                    workload_tby=550), game=dict(storage_gb=20000, sata25=False), contract="hdd35", new_contract=True),
    dict(id="ssd_sorin_pm9a3_3840", brand="Sorin", name="Sorin PM9A3 3.84 TB U.2", price=449, power_w=13, color="#a9adb3", rgb=False,
         analog="Samsung PM9A3 3.84TB U.2 (MZQL23T8HCLS)", desc="An enterprise PCIe 4.0 U.2 drive in a finned aluminium shell.",
         specs=dict(form="2.5\" 15 mm U.2", interface="PCIe 4.0 x4 NVMe (SFF-8639)", read_mbs=6900, write_mbs=4100, dwpd=1, plp=True),
         game=dict(storage_gb=3840, sata25=False), contract="u2", new_contract=True),
    dict(id="ssd_sorin_pm9a3_7680", brand="Sorin", name="Sorin PM9A3 7.68 TB U.2", price=799, power_w=14, color="#a9adb3", rgb=False,
         analog="Samsung PM9A3 7.68TB U.2 (MZQL27T6HBLA)", desc="Double the space of the 3.84 TB, for busy database servers.",
         specs=dict(form="2.5\" 15 mm U.2", interface="PCIe 4.0 x4 NVMe (SFF-8639)", read_mbs=6900, write_mbs=4100, dwpd=1, plp=True),
         game=dict(storage_gb=7680, sata25=False), contract="u2", new_contract=True),
]


def write_json():
    out = []
    for e in CATALOG:
        out.append(dict(id=e["id"], model=e["id"], brand=e["brand"], name=e["name"], category="Storage", price=e["price"],
                        power_w=e["power_w"], color=e["color"], rgb=e["rgb"], analog=e["analog"] + " (docs only, never shown in game)",
                        desc=e["desc"], specs=e["specs"], game=dict(e["game"], perf=0), contract=e["contract"],
                        new_contract=e.get("new_contract", False)))
    path = os.path.join(ROOT, "docs", "catalog", "storage.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("JSON", path)


# ================================================================== report

REPORT = os.path.join(c.PREVIEWS, "cat_storage_report.txt")


def report_block(root, sid):
    import parts_c as P
    tris, meshes = P.stats(root)
    lines = [f"== {sid}: {tris} triangles, {meshes} meshes"]
    for n, p, fw, up, s, m in P.anchor_report(root):
        lines.append(f"  {n} pos={p} fwd={fw} up={up} size={s} meta={m}")
    return lines


def write_report(blocks):
    old = {}
    if os.path.exists(REPORT):
        cur = None
        for ln in open(REPORT, encoding="utf-8").read().splitlines():
            if ln.startswith("== "):
                cur = ln[3:].split(":", 1)[0]
                old[cur] = [ln]
            elif cur and ln.strip():
                old[cur].append(ln)
    old.update(blocks)
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("CATALOGUE 14 STORAGE - anchor report (Unity metres; fwd = local +Z, up = local +Y)\n")
        fh.write("Run: blender -b --factory-startup -P Tools/Blender/build_cat_storage.py -- [ids] [--nopreview]\n\n")
        for e in CATALOG:
            if e["id"] in old:
                fh.write("\n".join(old[e["id"]]) + "\n\n")
    print("REPORT FILE", REPORT)


# ================================================================== runner

def build(sid, preview=True):
    import cat_storage_ssd as S
    m2 = {d["id"]: d for d in M2}
    sata = {d["id"]: d for d in SATA}
    if sid in m2:
        root = S.build_m2(m2[sid])
        if preview:
            S.previews_m2(sid, root, tall=m2[sid].get("heatsink", {}).get("kind") == "fins")
    elif sid in sata:
        root = S.build_sata(sata[sid])
        if preview:
            S.previews_sata(sid, root)
    else:
        import cat_storage_hdd as H
        root = H.build(sid)
        if preview:
            H.previews(sid, root)
    return report_block(root, sid)


def main():
    a = c.args()
    preview = "--nopreview" not in a
    ids = [x for x in a if not x.startswith("--")]
    write_json()
    if "--json" in a:
        return
    blocks = {}
    for sid in ids or [e["id"] for e in CATALOG]:
        blocks[sid] = build(sid, preview)
        write_report(blocks)


if __name__ == "__main__":
    main()
