"""
box_catalog: the catalogue-driven box items. Reads docs/catalog/*.json (one object per part, see
docs/tasks/catalog/README.md) and turns every part into a build_boxes ITEMS entry, so no box is hand-written:

  * kind: the rig builder (rig_products.BUILDERS and the other rig modules), from the part's contract;
  * the printed art: the brand's look (BRANDS, with per-product-line overrides in LINES), the box name, the product
    line, key specs and badges written from the part's own specs;
  * docs: the papers in the box (the part's "docs" list: one A_ITEM_DOC per paper);
  * bounds: measured from the part's FBX (its own frame, Unity axes) at build time, and the box size from them.

Run by build_boxes.py; also  ... -P Tools/Blender/box_catalog.py -- --json [ids]  adds "box" and "box_size" to the
catalogue files for every id whose box model exists (the only two keys it touches).
"""
import glob
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG = os.environ.get("DCT_CATALOG") or os.path.join(REPO, "docs", "catalog")
FAMILIES = ("cpus", "gpus", "boards", "ram", "storage", "psus", "coolers", "cases", "server")


def load():
    """[(family, part), ...] in catalogue order."""
    out = []
    for fam in FAMILIES:
        path = os.path.join(CATALOG, fam + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                out += [(fam, p) for p in json.load(fh)]
    return out


# ---------------------------------------------------------------- kinds (which rig a part's box is)

def kind_of(p):
    """The rig kind of a catalogue part's box, from its contract (and a few product facts)."""
    ct = p["contract"].split(" ")[0]
    pid = p["id"]
    cat = p["category"]
    if ct in ("cpu_arc5", "cpu_tiron5"):
        return "cpu"
    if ct in ("cpu_spv", "cpu_l46"):
        return "oem_cpu"
    if ct == "gpu":
        return "gpu"
    if ct == "gpu_dc":
        return "oem_card"
    if ct.startswith("mb_ridge"):
        return "mb"
    if ct == "mb_server_eeb":
        return "oem_board"
    if ct == "ram":
        return "ram"
    if ct == "rdimm":
        return "oem_rdimm"
    if ct == "ssd_1tb":
        return "ssd_m2"
    if ct == "ssd_sata_500":
        return "ssd_sata"
    if ct == "hdd35":
        # enterprise drives ship in brown bulk boxes, the desktop ones in a retail box
        return "hdd_bulk" if p["specs"].get("helium") or "exos" in pid else "hdd"
    if ct == "u2":
        return "oem_u2"
    if ct == "psu":
        return "psu"
    if ct == "psu_sfx":
        return "psu_sfx"
    if ct == "psu_crps":
        return "oem_psu"
    if ct == "cooler_tower":
        return "cooler_low" if p["specs"].get("height_mm", 150) < 80 else "cooler_tower"
    if ct == "cooler_stock":
        return "cooler_stock"
    if ct == "aio":
        return "aio"
    if ct.startswith("heatsink_"):
        return "oem_heatsink"
    if ct == "case":
        return "case"
    if ct == "case_fan":
        return "fan_pack"
    if ct == "pcie_card":
        return "oem_card"
    if ct == "rack_device":
        return "oem_rack"
    raise KeyError(f"{pid}: no box kind for contract {p['contract']} ({cat})")


# ---------------------------------------------------------------- brand looks (docs/tasks/catalog/README.md brand table)

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


DARK_TEXT = (0.97, 0.97, 0.96)
INK = (0.08, 0.08, 0.09)

# bg0/bg1: the print's gradient, accent: the brand colour, text: the type colour, font: the logo face,
# lower: the logo is set in lower case, ink: the one-colour print on kraft cartons (cases), field: the inner box colour.
BRANDS = {
    # CPUs
    "Arc": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.17, 0.08, 0.03), accent=(1.0, 0.42, 0.08), text=DARK_TEXT, font="seguibl.ttf"),
    "Tiron": dict(bg0=(0.01, 0.08, 0.25), bg1=(0.06, 0.36, 0.78), accent=(0.45, 0.80, 1.0), text=(0.98, 0.98, 1.0),
                  font="segoeuib.ttf", field=(0.97, 0.97, 0.98), field_ink=(0.03, 0.22, 0.55)),
    # GPU chips and board partners
    "Verdia": dict(bg0=(0.025, 0.028, 0.03), bg1=(0.10, 0.12, 0.10), accent=(0.46, 0.73, 0.0), text=DARK_TEXT,
                   font="AGENCYB.TTF", ribbon=(0.46, 0.73, 0.0)),
    "Voltra": dict(bg0=(0.03, 0.025, 0.025), bg1=(0.22, 0.04, 0.05), accent=(0.90, 0.13, 0.13), text=DARK_TEXT,
                   font="AGENCYB.TTF", ribbon=(0.80, 0.08, 0.08)),
    "Zenith": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.16, 0.13, 0.05), accent=(0.98, 0.66, 0.06), text=DARK_TEXT,
                   font="AGENCYB.TTF", ribbon=(0.98, 0.66, 0.06)),
    "Aegis": dict(bg0=(0.035, 0.035, 0.04), bg1=(0.14, 0.13, 0.10), accent=(0.95, 0.70, 0.12), text=DARK_TEXT,
                  font="AGENCYB.TTF", ribbon=(0.95, 0.70, 0.12)),
    "Mako": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.18, 0.05, 0.05), accent=(0.86, 0.10, 0.12), text=DARK_TEXT,
                 font="AGENCYB.TTF", ribbon=(0.86, 0.10, 0.12)),
    "Kestrel": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.17, 0.10, 0.03), accent=(1.0, 0.50, 0.05), text=DARK_TEXT,
                    font="AGENCYB.TTF", ribbon=(1.0, 0.50, 0.05)),
    "Ridge": dict(bg0=(0.035, 0.038, 0.045), bg1=(0.13, 0.14, 0.16), accent=(0.86, 0.16, 0.14), text=DARK_TEXT,
                  font="AGENCYB.TTF"),
    # memory
    "Corvex": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.15, 0.15, 0.15), accent=(0.98, 0.80, 0.0), text=DARK_TEXT,
                   font="FRAMDCN.TTF", ribbon=(0.98, 0.80, 0.0)),
    "G.Stride": dict(bg0=(0.02, 0.02, 0.025), bg1=(0.16, 0.16, 0.18), accent=(0.86, 0.08, 0.10), text=DARK_TEXT,
                     font="impact.ttf"),
    "Kingsland": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.12, 0.02, 0.03), accent=(0.86, 0.06, 0.12), text=DARK_TEXT,
                      font="impact.ttf"),
    "Crux": dict(bg0=(0.02, 0.17, 0.42), bg1=(0.05, 0.42, 0.78), accent=(0.55, 0.85, 1.0), text=(0.98, 0.98, 1.0),
                 font="seguibl.ttf", lower=True, field=(0.97, 0.97, 0.98), field_ink=(0.02, 0.20, 0.48)),
    "TeamForge": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.17, 0.12, 0.04), accent=(0.92, 0.65, 0.18), text=DARK_TEXT,
                      font="impact.ttf"),
    "Volt": dict(bg0=(0.025, 0.025, 0.03), bg1=(0.13, 0.12, 0.10), accent=(1.0, 0.82, 0.10), text=DARK_TEXT, font="impact.ttf"),
    # storage
    "Sorin": dict(bg0=(0.02, 0.02, 0.025), bg1=(0.10, 0.10, 0.12), accent=(0.95, 0.42, 0.10), text=DARK_TEXT,
                  font="seguibl.ttf"),
    "Westline": dict(bg0=(0.02, 0.02, 0.02), bg1=(0.14, 0.14, 0.15), accent=(0.80, 0.82, 0.84), text=DARK_TEXT,
                     font="arialbd.ttf"),
    "Seacrest": dict(bg0=(0.03, 0.18, 0.10), bg1=(0.10, 0.48, 0.28), accent=(0.55, 0.88, 0.40), text=DARK_TEXT,
                     font="seguibl.ttf", lower=True),
    "Quill": dict(bg0=(0.97, 0.97, 0.96), bg1=(0.86, 0.89, 0.90), accent=(0.0, 0.58, 0.60), text=(0.08, 0.10, 0.12),
                  font="georgiab.ttf"),
    # power
    "Ampere": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.14, 0.11, 0.08), accent=(0.78, 0.48, 0.24), text=DARK_TEXT, font="FRAMDCN.TTF"),
    "Seastar": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.12, 0.12, 0.13), accent=(0.86, 0.70, 0.30), text=DARK_TEXT,
                    font="GILSANUB.TTF"),
    "Hush": dict(bg0=(0.03, 0.03, 0.03), bg1=(0.12, 0.12, 0.12), accent=(0.96, 0.52, 0.08), text=DARK_TEXT,
                 font="seguibl.ttf", lower=True, ribbon=(0.96, 0.52, 0.08), ink=(0.08, 0.08, 0.08)),
    # cooling
    "Noctis": dict(bg0=(0.06, 0.04, 0.03), bg1=(0.30, 0.19, 0.13), accent=(0.86, 0.76, 0.60), text=(0.98, 0.96, 0.92),
                   font="GILSANUB.TTF", field=(0.84, 0.76, 0.62), field_ink=(0.36, 0.20, 0.13), ribbon=(0.58, 0.32, 0.22)),
    "Arctiq": dict(bg0=(0.96, 0.97, 0.98), bg1=(0.78, 0.86, 0.93), accent=(0.0, 0.40, 0.74), text=(0.05, 0.10, 0.20),
                   font="seguibl.ttf"),
    "Glacier": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.10, 0.16, 0.17), accent=(0.10, 0.80, 0.72), text=DARK_TEXT,
                    font="seguibl.ttf"),
    "Frostpeak": dict(bg0=(0.90, 0.95, 0.99), bg1=(0.36, 0.62, 0.90), accent=(0.04, 0.18, 0.42), text=(0.04, 0.12, 0.28),
                      font="GILSANUB.TTF"),
    # cases (kraft cartons, one-colour ink) and fans
    "Lumin": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.14, 0.14, 0.16), accent=(0.20, 0.72, 0.95), text=DARK_TEXT,
                  font="seguisb.ttf", ink=(0.07, 0.07, 0.08)),
    "Facet": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.15, 0.15, 0.16), accent=(0.95, 0.95, 0.95), text=DARK_TEXT,
                  font="GILSANUB.TTF", lower=True, ink=(0.06, 0.06, 0.06)),
    "Nexa": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.20, 0.10, 0.30), accent=(0.55, 0.30, 0.85), text=DARK_TEXT,
                 font="seguibl.ttf", ink=(0.30, 0.12, 0.45)),
    "Phanta": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.14, 0.14, 0.15), accent=(0.85, 0.85, 0.86), text=DARK_TEXT,
                   font="AGENCYB.TTF", ink=(0.07, 0.07, 0.08)),
    "Brickhouse": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.14, 0.11, 0.08), accent=(0.86, 0.36, 0.10), text=DARK_TEXT,
                       font="ariblk.ttf", ink=(0.09, 0.075, 0.065)),
    # server
    "Strata": dict(bg0=(0.95, 0.95, 0.94), bg1=(0.86, 0.87, 0.88), accent=(0.0, 0.42, 0.62), text=INK, font="seguibl.ttf"),
    "Arc Epoch": dict(bg0=(0.03, 0.03, 0.035), bg1=(0.20, 0.10, 0.03), accent=(1.0, 0.42, 0.08), text=DARK_TEXT, font="seguibl.ttf"),
    "Linkwave": dict(bg0=(0.95, 0.95, 0.94), bg1=(0.86, 0.87, 0.88), accent=(0.02, 0.45, 0.70), text=INK, font="seguibl.ttf"),
    "Broadline": dict(bg0=(0.95, 0.95, 0.94), bg1=(0.86, 0.87, 0.88), accent=(0.80, 0.0, 0.10), text=INK, font="arialbd.ttf"),
    "Melnet": dict(bg0=(0.95, 0.95, 0.94), bg1=(0.86, 0.87, 0.88), accent=(0.46, 0.73, 0.0), text=INK, font="arialbd.ttf"),
}
DEFAULT_BRAND = dict(bg0=(0.03, 0.03, 0.035), bg1=(0.14, 0.14, 0.15), accent=(0.6, 0.6, 0.62), text=DARK_TEXT, font="arialbd.ttf")

# product-line looks within a brand (the real brands dress each line differently): id substring -> overrides
LINES = [
    ("aegis_b650_bulwark", dict(bg1=(0.17, 0.15, 0.10), accent=(0.86, 0.72, 0.38))),          # the tan "armour" line
    ("aegis_x870e_vanguard", dict(bg1=(0.22, 0.03, 0.05), accent=(0.92, 0.06, 0.14))),        # the red gaming line
    ("aegis_z790_keystone", dict(bg0=(0.94, 0.95, 0.96), bg1=(0.80, 0.84, 0.88), accent=(0.05, 0.45, 0.70),
                                 text=(0.06, 0.08, 0.12))),                                    # the white "everyday" line
    ("aegis_1200p", dict(bg1=(0.22, 0.03, 0.05), accent=(0.92, 0.06, 0.14))),
    ("mako_b650_harpoon", dict(bg1=(0.20, 0.19, 0.14), accent=(0.78, 0.70, 0.46))),
    ("mako_z790_riptide", dict(bg0=(0.92, 0.93, 0.94), bg1=(0.74, 0.77, 0.80), accent=(0.70, 0.08, 0.10), text=(0.06, 0.06, 0.08))),
    ("kestrel_b650_glide", dict(bg0=(0.93, 0.94, 0.95), bg1=(0.70, 0.78, 0.86), accent=(0.0, 0.40, 0.72), text=(0.05, 0.08, 0.14))),
    ("4060_kestrel", dict(bg0=(0.04, 0.06, 0.10), bg1=(0.10, 0.22, 0.38), accent=(0.30, 0.65, 0.95), ribbon=(0.30, 0.65, 0.95))),
    ("westline_sn580", dict(bg0=(0.04, 0.22, 0.50), bg1=(0.16, 0.46, 0.80), accent=(0.70, 0.88, 1.0))),
    ("sorin_980", dict(bg0=(0.96, 0.96, 0.97), bg1=(0.80, 0.86, 0.94), accent=(0.05, 0.30, 0.75), text=(0.05, 0.07, 0.12))),
    ("sorin_870", dict(bg0=(0.96, 0.96, 0.97), bg1=(0.84, 0.85, 0.87), accent=(0.10, 0.10, 0.12), text=(0.05, 0.05, 0.07))),
    ("crux_mx500", dict(bg0=(0.96, 0.96, 0.97), bg1=(0.82, 0.88, 0.95), accent=(0.0, 0.36, 0.72), text=(0.02, 0.12, 0.30))),
    ("crux_t705", dict(bg0=(0.02, 0.02, 0.03), bg1=(0.10, 0.12, 0.16), accent=(0.0, 0.55, 0.95), text=DARK_TEXT)),
    ("crux_ddr", dict(bg0=(0.02, 0.17, 0.42), bg1=(0.05, 0.42, 0.78))),
    ("noctis_d15_black", dict(bg0=(0.02, 0.02, 0.025), bg1=(0.16, 0.16, 0.17), accent=(0.70, 0.70, 0.72), text=DARK_TEXT,
                              field=(0.05, 0.05, 0.055), field_ink=(0.62, 0.62, 0.64))),
    ("noctis_a12x25_black", dict(bg0=(0.02, 0.02, 0.025), bg1=(0.16, 0.16, 0.17), accent=(0.70, 0.70, 0.72), text=DARK_TEXT,
                                 field=(0.05, 0.05, 0.055), field_ink=(0.62, 0.62, 0.64))),
    ("voltra_7900xtx_ref", dict(bg1=(0.24, 0.03, 0.04))),
    ("verdia_5090_ref", dict(bg1=(0.06, 0.07, 0.06), accent=(0.46, 0.73, 0.0))),
    ("tiron_b580", dict(bg0=(0.01, 0.06, 0.20), bg1=(0.04, 0.30, 0.66), accent=(0.45, 0.80, 1.0), ribbon=(0.45, 0.80, 1.0))),
    ("frostpeak_120_rgb", dict(bg0=(0.03, 0.03, 0.05), bg1=(0.14, 0.18, 0.36), accent=(0.45, 0.70, 1.0), text=DARK_TEXT)),
    ("seastar_px1000", dict(bg1=(0.24, 0.22, 0.20), accent=(0.86, 0.86, 0.86))),
]
WHITE = dict(bg0=(0.96, 0.96, 0.95), bg1=(0.82, 0.83, 0.85), text=(0.07, 0.07, 0.09), field=(0.96, 0.96, 0.95),
             field_ink=(0.20, 0.20, 0.22))


def look(p):
    """The print colours and fonts of a part's box."""
    st = dict(DEFAULT_BRAND)
    st.update(BRANDS.get(p["brand"], {}))
    if "_white" in p["id"]:
        st.update(WHITE)                 # white products come in white boxes, the brand colour stays as the accent
    for key, ov in LINES:
        if key in p["id"]:
            st.update(ov)
    return st


# ---------------------------------------------------------------- the words on the box

def _num(x):
    return f"{x:g}"


def _strip_brand(name, brand):
    return name[len(brand):].strip() if name.startswith(brand) else name


def texts(p, kind):
    """(model, name, line, specs, badges, extra): the big model name, the full product name, the product line under the
    logo, up to 6 key specs (back and sides), up to 3 badges (front), extra item keys (CPU numerals)."""
    s, g, cat = p["specs"], p["game"], p["category"]
    name = _strip_brand(p["name"], p["brand"])
    extra = {}
    if kind == "cpu":
        m = re.match(r"(i\d|\d)[ -](\S+)", name)
        if m:
            extra = dict(numeral=m.group(1), sub=m.group(2))
        specs = [f"{s['cores']} cores / {s['threads']} threads", f"Up to {_num(s['boost_ghz'])} GHz boost",
                 f"{s['l3_mb']} MB L3 cache", f"Socket {g['socket']}", f"{s['tdp_w']} W TDP",
                 (f"{s['igpu']} graphics" if s.get("igpu") else "Cooler not included")]
        return name.upper(), name, "DESKTOP PROCESSOR", specs, [f"{s['cores']} CORES", f"SOCKET {g['socket']}"], extra
    if kind == "gpu":
        conn = {"PCIe8x1": "1 x PCIe 8-pin power", "PCIe8x2": "2 x PCIe 8-pin power",
                "Power16": "12V-2x6 power connector"}.get(g.get("gpu_connector"), "PCIe power")
        specs = [f"{s['vram_gb']} GB graphics memory", f"Boost clock up to {s['boost_mhz']} MHz", conn,
                 f"{p['power_w']} W board power", f"{s['fans']}-fan cooler, {_num(s['slots'])}-slot",
                 f"Card length {s['length_mm']} mm"]
        chip = "VERDIA VTX" if "verdia" in p["id"] else "VOLTRA RX" if "voltra" in p["id"] else "TIRON LUMEN"
        return name.upper(), name, chip + " GRAPHICS CARD", specs, [f"{s['vram_gb']} GB", conn.split(" power")[0].upper()], extra
    if kind == "mb":
        lan = f"{_num(s['lan_gbe'])}G LAN"
        specs = [f"Socket {g['socket']}, {s['chipset']} chipset", f"{s['dimm_slots']} x {g['mem']}, up to {s['max_ram_gb']} GB",
                 f"{s['m2_slots']} x M.2 NVMe", f"{s['pcie_x16']} x PCIe x16 slots", ("Wi-Fi + " + lan) if s.get("wifi") else lan,
                 f"{s['sata']} x SATA 6 Gb/s"]
        return name.upper(), name, f"{s['form']} MOTHERBOARD", specs, [f"SOCKET {g['socket']}", g["mem"], s["chipset"]], extra
    if kind == "ram":
        n, per = s["kit"].lower().split("x")
        total = int(n) * int(per.rstrip("gb"))
        specs = [f"{n} x {per.upper().rstrip('GB')} GB {g['mem']}", f"{s['speed_mts']} MT/s CL{s['cas']}",
                 f"Timings {s['timings']}", f"{_num(s['voltage'])} V"]
        if p["rgb"]:
            specs.append("RGB light bar")
        specs.append("Aluminium heat spreader" if s.get("spreader") else "Bare module")
        badges = [f"{total} GB ({s['kit'].replace('GB', '')})", g["mem"]] + (["RGB"] if p["rgb"] else [])
        return name.upper(), name, "DESKTOP MEMORY KIT", specs, badges, extra
    if kind in ("ssd_m2", "ssd_sata"):
        cap = g["storage_gb"]
        capt = f"{cap // 1000} TB" if cap >= 1000 and cap % 1000 == 0 else f"{cap / 1000:g} TB" if cap >= 1000 else f"{cap} GB"
        specs = [f"Up to {s['read_mbs']} MB/s read", f"Up to {s['write_mbs']} MB/s write", f"{s['form']}, {s['interface']}",
                 f"{s['tbw']} TBW endurance", f"{s.get('nand', 'TLC')} NAND" + (", DRAM cache" if s.get("dram") else "")]
        if s.get("has_heatsink"):
            specs.append("Integrated heatsink")
        line = (s["form"] + " " + s["interface"]).upper() if kind == "ssd_m2" else '2.5" SATA SOLID STATE DRIVE'
        return name.upper(), name, line, specs, [capt, "NVMe" if kind == "ssd_m2" else "SATA"], extra
    if kind == "psu":
        mod = {"none": "Non-modular cables", "semi": "Semi-modular cables", "full": "Fully modular"}[s["modular"]]
        conns = f"{s['eps8']} x CPU 8-pin, {s['pcie8']} x PCIe 8-pin" + (f", {s['p12v2x6']} x 12V-2x6" if s.get("p12v2x6") else "")
        specs = [s["efficiency"], mod, f"{s['fan_mm']} mm fan", conns, f"ATX {s['atx_version']}",
                 f"{s['depth_mm']} mm deep"]
        eff = s["efficiency"].upper()
        return name.upper(), name, f"ATX {s['atx_version']} POWER SUPPLY".replace("ATX 2.x", "ATX"), specs, \
            [f"{g['psu_watts']} W", eff], extra
    if kind in ("cooler_tower", "cooler_low", "cooler_stock"):
        specs = [f"Up to {g['cooler_max_w']} W TDP", f"{s['fans']} x {s['fan_mm']} mm PWM fan" if s["fans"] == 1
                 else f"{s['fans']} x {s['fan_mm']} mm PWM fans", f"Height {s['height_mm']} mm", "Socket V5 / L17"
                 if kind != "cooler_stock" else f"Socket {g.get('socket', 'L17')}"]
        if s.get("heat_pipes"):
            specs.insert(1, f"{s['heat_pipes']} copper heat pipes")
        if s.get("towers", 0) > 1:
            specs.insert(2, "Dual tower")
        if s.get("argb"):
            specs.append(f"ARGB ({s['argb']})")
        badges = ([f"{s['heat_pipes']} HEAT PIPES"] if s.get("heat_pipes") else []) + [f"{g['cooler_max_w']} W"]
        line = "CPU COOLER" if kind == "cooler_stock" else "LOW-PROFILE CPU COOLER" if kind == "cooler_low" else "CPU AIR COOLER"
        return name.upper(), name, line, specs, badges, extra
    if kind == "case":
        specs = [s["side_panel"].capitalize() + " side panel", s["fans_included"] + " fans", "ATX / Micro-ATX / Mini-ITX",
                 f"GPU up to {s['max_gpu_mm']} mm", f"CPU cooler up to {s['max_cooler_mm']} mm", s["front"].capitalize() + " front"]
        return name.upper(), name, s["form_factor"].upper() + " CASE", specs, [], extra
    # the kinds of the other rig modules: a generic set of words they may override
    specs = [f"{k.replace('_', ' ')}: {v}" for k, v in list(s.items())[:6] if not isinstance(v, (dict, list))]
    return name.upper(), name, cat.upper(), specs, [], extra


# ---------------------------------------------------------------- items

STYLE = {"case": "carton"}
BAG = {"Aegis": "antistatic_silver", "Kestrel": "antistatic_silver", "Mako": "antistatic_pink", "Ridge": "antistatic_pink"}


def item(fam, p):
    kind = kind_of(p)
    st = look(p)
    model, name, line, specs, badges, extra = texts(p, kind)
    brand = p["brand"].upper()
    it = dict(cat=p["category"], brand=brand, model=model, name=name, line=line, specs=specs, badges=badges,
              style=STYLE.get(kind, "retail"), kind=kind, family=fam, docs=list(p.get("docs", [])),
              model_id=p["model"], part=p, colour=rgb(p.get("color", "#808080")), rgb=bool(p.get("rgb")))
    it.update(st)
    it.update(extra)
    if it["style"] == "carton":
        it.setdefault("ink", INK)
    if kind == "mb":
        it["bag"] = BAG.get(p["brand"], "antistatic_silver")
    io = p["specs"].get("io_shield")
    if io and not p["specs"].get("io_preattached"):
        it["acc_models"] = [io]          # measured with the part: the rig poses them at A_ITEM_ACC
    if p["category"] not in CATS:
        it["cat_colour"] = (0.25, 0.45, 0.55)
    return it


CATS = ("Case", "Motherboard", "CPU", "Cooler", "RAM", "GPU", "PSU", "Storage", "Other")


def items():
    """{part id: item} for the whole catalogue."""
    return {p["id"]: item(fam, p) for fam, p in load()}


# ---------------------------------------------------------------- bounds and sizes

_VERTS = {}      # model id -> (n, 3) array of its vertices in its own frame (Unity axes), kept for slab()


def measure(model_id):
    """The part's bounds in its own frame (Unity axes): ((lo), (hi)) over every mesh vertex, from its FBX.
    Leaves an empty scene behind."""
    import bpy
    import numpy as np
    path = os.path.join(c.MODELS, model_id + ".fbx")
    if not os.path.exists(path):
        return None
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    objs = list(bpy.context.scene.objects)
    roots = [o for o in objs if o.parent is None and o.type == "EMPTY" and not o.name.startswith("A_")]
    inv = roots[0].matrix_world.inverted() if roots else None
    pts = []
    for o in objs:
        if o.type != "MESH" or not len(o.data.vertices):
            continue
        M = (inv @ o.matrix_world) if inv is not None else o.matrix_world
        co = np.empty(len(o.data.vertices) * 3)
        o.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        R = np.array([[M[i][j] for j in range(3)] for i in range(3)])
        T = np.array([M[i][3] for i in range(3)])
        b = co @ R.T + T
        pts.append(np.stack([-b[:, 0], b[:, 1], b[:, 2]], axis=1))   # the root's import rotation undone: x mirrored = Unity
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not pts:
        return None
    v = np.concatenate(pts)
    _VERTS[model_id] = v
    lo, hi = v.min(axis=0), v.max(axis=0)
    return tuple(round(float(x), 5) for x in lo), tuple(round(float(x), 5) for x in hi)


def region(model_id, lo, hi):
    """Bounds ((lo), (hi)) of a measured model's vertices inside the box lo..hi (its own frame), None if none."""
    import numpy as np
    v = _VERTS.get(model_id)
    if v is None:
        return None
    sel = v[np.all((v >= np.array(lo)) & (v <= np.array(hi)), axis=1)]
    if not len(sel):
        return None
    return (tuple(round(float(x), 5) for x in sel.min(axis=0)), tuple(round(float(x), 5) for x in sel.max(axis=0)))


def slab(model_id, axis, a, b):
    """Bounds ((lo), (hi)) of a measured model's vertices with a <= v[axis] <= b (its own frame), None if none."""
    v = _VERTS.get(model_id)
    if v is None:
        return None
    sel = v[(v[:, axis] >= a) & (v[:, axis] <= b)]
    if not len(sel):
        return None
    return (tuple(round(float(x), 5) for x in sel.min(axis=0)), tuple(round(float(x), 5) for x in sel.max(axis=0)))


def up5(x, step=0.005):
    """Rounds a size up to the next 5 mm (box makers' steps)."""
    return round(math.ceil(x / step - 1e-6) * step, 3)


def size(kind, it):
    """The box size of a catalogue item of one of the rig_products kinds, from its measured bounds (None: not mine)."""
    lo, hi = it["bounds"]
    d = [hi[i] - lo[i] for i in range(3)]
    s = it["part"]["specs"]
    if kind == "cpu":
        return (0.11, 0.07, 0.11)
    if kind == "gpu":           # x: card length, y: thickness (fans up), z: height (bracket edge to top edge)
        return (up5(d[0] + 0.05), max(0.075, up5(d[1] + 0.030)), up5(max(d[2] + 0.035, 0.155)))
    if kind == "mb":
        return (0.32, max(0.07, up5(hi[2] + 0.027)), 0.27)
    if kind == "ram":          # two sticks side by side: the depth grows with the stick height
        return (0.16, 0.03, max(0.12, up5(2 * (d[2] + 0.003) + 0.0134)))
    if kind == "ssd_m2":       # heatsink drives need a deeper blister
        return (0.11, max(0.025, up5(d[2] + 0.0165)), 0.08)
    if kind == "ssd_sata":
        return (0.14, 0.03, 0.10)
    if kind == "psu":          # the body is specs depth long; the box adds the end caps (and a pouch layer: semi-modular)
        return (up5(s["depth_mm"] / 1000.0 + 0.067), 0.135 if s.get("modular") == "semi" else 0.12, 0.18)
    if kind == "cooler_stock":
        return (0.12, 0.09, 0.15)
    if kind == "cooler_tower":  # upright: x = the fan's width (local y), y = height, z = depth plus the accessory box
        return (max(0.16, up5(d[1] + 0.012)), max(0.20, up5(d[2] + 0.034)), max(0.14, up5(d[0] + 0.050)))
    if kind == "cooler_low":   # x: the cooler (its local y, with the plug) and the accessory box beside it
        return (up5(d[1] + 0.055), up5(d[2] + 0.028), up5(d[0] + 0.024))
    if kind == "case":
        return (0.52, 0.56, 0.30)
    return None


# ---------------------------------------------------------------- catalogue update: "box" and "box_size"

def write_json(sizes):
    """sizes: {part id: (x, y, z)}. Adds or updates "box" and "box_size" on those parts, touching nothing else
    (a text edit at the end of each object, so the files' formatting stays as it is)."""
    for fam in FAMILIES:
        path = os.path.join(CATALOG, fam + ".json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        lines = text.split("\n")
        out, cur, changed = [], None, False
        for i, ln in enumerate(lines):
            m = re.match(r'^    "id": "([^"]+)"', ln)
            if m:
                cur = m.group(1)
            if cur in sizes and re.match(r'^    "box(_size)?": ', ln):
                changed = True
                continue                                  # replaced below
            if cur in sizes and re.match(r"^  \}", ln):
                x, y, z = sizes[cur]
                out[-1] = out[-1].rstrip(",") + ","
                out.append(f'    "box": "box_{cur}",')
                out.append(f'    "box_size": [{x:g}, {y:g}, {z:g}]')
                cur, changed = None, True
            out.append(ln)
        if changed:
            new = "\n".join(out)
            json.loads(new)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            print("JSON updated", path)


if __name__ == "__main__":
    args = c.args()
    if "--json" in args:
        import build_boxes as BB
        ids = [a for a in args if not a.startswith("--")]
        sizes = {}
        for pid, it in items().items():
            if ids and pid not in ids:
                continue
            if not os.path.exists(os.path.join(c.MODELS, "box_" + pid + ".fbx")):
                continue
            sizes[pid] = BB.resolve_size(pid, it)
        write_json(sizes)
