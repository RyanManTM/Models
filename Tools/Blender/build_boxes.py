"""
Retail packaging rigs: box_<partid> for every catalog item (PartDef.cs) except the AC (box_ac_12k is kept as it is).
Owner: Blender agent B. Contract: Logs/UNBOXING.md 2.2 (rig anchors) and 3 (what is in each box).

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_boxes.py -- [ids...] [--noshots] [--nopreview]
      ids are part ids (cpu_arc5) or box ids (box_cpu_arc5); none = all. --noshots reuses the cached product shots
      (Logs/ModelPreviews/boxshots), --nopreview skips the preview renders.

Every box is a RIG (rig_common.Rig, built in rig_products.py): origin at the bottom centre, the front at +z, the
closed pose, A_HIT_0 = the outer size (PartFactory.BoxSize reads it). The removable pieces are anchors with meta
(order, under, parent, with, hinge/open, lift/slide/dist, label) and their meshes '<piece>@<anchor>#<tag>'; the
content poses (A_ITEM_PART_<n>: the part model's own frame, A_ITEM_ACC/DOC/CORD/HW/POUCH) are anchors only: the game
spawns the parts, papers and bags. Seals and tape are anchors (the game builds the peel strips); 'seallook@A_SEAL_n'
and 'tapelook@A_TAPE_n' meshes only make the closed box look right and are replaced by the game.

Art: tex_box_<partid> (an atlas of the printed faces: product shot, brand, name, specs, category stripe, barcode),
tex_box_<partid>_in (inner boxes, trays, accessory boxes, ribbons: plain colours with a small logo).
Previews: Logs/ModelPreviews/box_<partid>_0..1 (closed), _2 (opened, the part in place), _3 (exploded),
and the anchor report box_<partid>_report.txt.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ
SHOTS = os.path.join(c.PREVIEWS, "boxshots")


def _retrying(fn, what):
    """The Unity editor may hold a texture or model for a moment while it imports it: retry the write."""
    import time

    def wrapped(*a, **kw):
        for attempt in range(10):
            try:
                return fn(*a, **kw)
            except (RuntimeError, OSError) as ex:
                print(what, "RETRY", attempt, ex)
                time.sleep(3.0)
        return fn(*a, **kw)
    return wrapped


P.Art.render = _retrying(P.Art.render, "ART")
P.save_png = _retrying(P.save_png, "PNG")

# PackageBox.CategoryColor
CAT = {"Case": (0.3, 0.3, 0.35), "Motherboard": (0.2, 0.6, 0.3), "CPU": (0.9, 0.4, 0.1), "Cooler": (0.2, 0.6, 0.95),
       "RAM": (0.8, 0.2, 0.6), "GPU": (0.85, 0.15, 0.15), "PSU": (0.95, 0.8, 0.2), "Storage": (0.3, 0.3, 0.9),
       "Other": (0.2, 0.8, 0.85)}


def box_size(pid, cat):
    """PartFactory.BoxSize (the rig's A_HIT_0). The SATA SSD box is the code's Sata25 size (0.14 x 0.03 x 0.10):
    a 2.5" drive in its tray and bag does not fit the M.2 box."""
    if cat == "Case":
        return (0.52, 0.56, 0.30)
    if cat == "Motherboard":
        return (0.32, 0.07, 0.27)
    if cat == "CPU":
        return (0.11, 0.07, 0.11)
    if cat == "Cooler":   # the stock cooler box is 0.15 deep (was 0.12): the model's fan plug sticks out 30 mm
        return (0.16, 0.20, 0.14) if pid == "cooler_tower" else (0.12, 0.09, 0.15)
    if cat == "RAM":
        return (0.16, 0.03, 0.12)
    if cat == "GPU":
        return (0.36, 0.09, 0.17)
    if cat == "PSU":
        return (0.21, 0.12, 0.18)
    if cat == "Storage":
        return (0.14, 0.03, 0.10) if pid == "ssd_sata_500" else (0.11, 0.025, 0.08)
    if pid == "usb_installer":
        return BLISTER
    if pid == "cable_dp":
        return (0.15, 0.03, 0.21)
    if pid == "fan_splitter":
        return (0.09, 0.02, 0.15)
    return (0.68, 0.48, 0.62)


BLISTER = (0.095, 0.024, 0.155)   # usb_installer: a card lying flat with the bubble on top

# ---------------------------------------------------------------- the catalogue (PartDef.cs) and the box styles

ITEMS = {
    "case_brickhouse": dict(cat="Case", brand="BRICKHOUSE", model="M1", name="M1 Mid-Tower", line="ATX MID-TOWER CASE",
                            specs=["Tempered glass side panel", "1 x 120 mm rear fan included", "ATX / Micro-ATX / Mini-ITX",
                                   "Front I/O: 2 x USB 3.0, USB-C, audio", "GPU up to 330 mm", "CPU cooler up to 160 mm"],
                            style="carton", ink=(0.09, 0.075, 0.065), accent=(0.86, 0.36, 0.10), font="ariblk.ttf"),
    "case_breeze": dict(cat="Case", brand="BREEZE", model="AIR 400", name="Air 400 Mesh", line="HIGH-AIRFLOW ATX MID-TOWER",
                        specs=["Fine-mesh front panel", "3 x 120 mm ARGB front + 1 x 120 mm rear", "Tempered glass side panel",
                               "ATX / Micro-ATX / Mini-ITX", "GPU up to 360 mm", "Magnetic dust filters"],
                        style="carton", ink=(0.10, 0.10, 0.11), accent=(0.22, 0.55, 0.88), font="seguisb.ttf", lower=True),
    "mb_ridge_b5": dict(cat="Motherboard", brand="RIDGE", model="B5 GAMING", name="B5 Gaming", line="ATX MOTHERBOARD",
                        specs=["Socket V5", "4 x DDR5 up to 6400 MT/s", "PCIe 4.0 x16", "M.2 NVMe with heatsink", "2.5G LAN",
                               "USB 3.2 Gen 2"], badges=["SOCKET V5", "DDR5", "PCIe 4.0"],
                        style="retail", bg0=(0.035, 0.038, 0.045), bg1=(0.13, 0.14, 0.16), accent=(0.86, 0.16, 0.14),
                        text=(0.96, 0.96, 0.95), font="AGENCYB.TTF", bag="antistatic_silver"),
    "mb_ridge_z4": dict(cat="Motherboard", brand="RIDGE", model="Z4 PRO", name="Z4 Pro", line="ATX MOTHERBOARD",
                        specs=["Socket L17", "4 x DDR4 up to 3200 MT/s", "PCIe 4.0 x16", "M.2 NVMe", "1G LAN", "USB 3.2 Gen 1"],
                        badges=["SOCKET L17", "DDR4", "PCIe 4.0"], style="retail", bg0=(0.04, 0.045, 0.05),
                        bg1=(0.14, 0.15, 0.16), accent=(0.08, 0.68, 0.64), text=(0.96, 0.96, 0.95), font="AGENCYB.TTF",
                        sibling="mb_ridge_b5", bag="antistatic_pink"),
    "cpu_arc5": dict(cat="CPU", brand="ARC", model="5", name="5 7600", line="DESKTOP PROCESSOR",
                     specs=["6 cores / 12 threads", "Up to 5.1 GHz boost", "38 MB total cache", "Socket V5", "65 W TDP",
                            "Unlocked for overclocking"], badges=["6 CORES", "SOCKET V5"], numeral="5", sub="7600",
                     style="retail", bg0=(0.03, 0.03, 0.035), bg1=(0.17, 0.08, 0.03), accent=(1.0, 0.42, 0.08),
                     text=(0.97, 0.97, 0.96), font="seguibl.ttf"),
    "cpu_arc7": dict(cat="CPU", brand="ARC", model="7", name="7 7800", line="DESKTOP PROCESSOR",
                     specs=["8 cores / 16 threads", "Up to 5.4 GHz boost", "40 MB total cache", "Socket V5", "120 W TDP",
                            "Cooler not included"], badges=["8 CORES", "SOCKET V5"], numeral="7", sub="7800",
                     style="retail", bg0=(0.03, 0.03, 0.035), bg1=(0.19, 0.05, 0.03), accent=(1.0, 0.30, 0.10),
                     text=(0.97, 0.97, 0.96), font="seguibl.ttf", sibling="cpu_arc5"),
    "cpu_tiron5": dict(cat="CPU", brand="TIRON", model="i5", name="i5-14400", line="DESKTOP PROCESSOR",
                       specs=["10 cores (6P + 4E) / 16 threads", "Up to 4.7 GHz", "20 MB cache", "Socket L17", "65 W base power",
                              "Cooler not included"], badges=["10 CORES", "SOCKET L17"], numeral="i5", sub="14400",
                       style="retail", bg0=(0.01, 0.08, 0.25), bg1=(0.06, 0.36, 0.78), accent=(0.45, 0.80, 1.0),
                       text=(0.98, 0.98, 1.0), font="segoeuib.ttf", field=(0.97, 0.97, 0.98), field_ink=(0.03, 0.22, 0.55)),
    "cooler_stock": dict(cat="Cooler", brand="SPINNER", model="STOCK", name="Stock Cooler", line="CPU COOLER",
                         specs=["For CPUs up to 95 W", "Pre-applied thermal paste", "80 mm fan, 4-pin PWM", "Socket V5 / L17"],
                         badges=["95 W", "PWM"], style="retail", bg0=(0.93, 0.94, 0.95), bg1=(0.80, 0.82, 0.85),
                         accent=(0.10, 0.62, 0.85), text=(0.07, 0.08, 0.10), font="ERASBD.TTF"),
    "cooler_tower": dict(cat="Cooler", brand="FROSTPEAK", model="TOWER 120", name="Tower 120", line="CPU AIR COOLER",
                         specs=["4 x 6 mm copper heat pipes", "120 mm PWM fan, 600-1800 rpm", "Up to 200 W TDP",
                                "Socket V5 / L17", "Height 155 mm"], badges=["4 HEAT PIPES", "200 W"],
                         style="retail", bg0=(0.90, 0.95, 0.99), bg1=(0.36, 0.62, 0.90), accent=(0.04, 0.18, 0.42),
                         text=(0.04, 0.12, 0.28), font="GILSANUB.TTF"),
    "ram_ddr5_16": dict(cat="RAM", brand="VOLT", model="DDR5-6000", name="32 GB DDR5-6000", line="DESKTOP MEMORY KIT",
                        specs=["2 x 16 GB DDR5", "6000 MT/s CL30", "1.35 V", "ARGB light bar", "Aluminium heat spreader"],
                        badges=["32 GB (2x16)", "DDR5", "RGB"], style="retail", bg0=(0.025, 0.025, 0.03), bg1=(0.13, 0.12, 0.10),
                        accent=(1.0, 0.82, 0.10), text=(0.97, 0.97, 0.95), font="impact.ttf"),
    "ram_ddr4_8": dict(cat="RAM", brand="VOLT", model="DDR4-3200", name="16 GB DDR4-3200", line="DESKTOP MEMORY KIT",
                       specs=["2 x 8 GB DDR4", "3200 MT/s CL16", "1.35 V", "Low-profile heat spreader"],
                       badges=["16 GB (2x8)", "DDR4"], style="retail", bg0=(0.03, 0.025, 0.025), bg1=(0.20, 0.05, 0.05),
                       accent=(0.92, 0.18, 0.14), text=(0.97, 0.97, 0.95), font="impact.ttf"),
    "gpu_rx66": dict(cat="GPU", brand="VOLTRA", model="RX 6600", name="RX 6600 8 GB", line="GRAPHICS CARD",
                     specs=["8 GB GDDR6, 128-bit", "PCIe 4.0 x8", "1 x 8-pin power, 160 W", "3 x DisplayPort 1.4, 1 x HDMI 2.1",
                            "Dual-fan cooler"], badges=["8 GB GDDR6", "PCIe 4.0"], style="retail", bg0=(0.03, 0.03, 0.035),
                     bg1=(0.18, 0.19, 0.21), accent=(0.78, 0.80, 0.84), text=(0.97, 0.97, 0.96), font="AGENCYB.TTF",
                     ribbon=(0.70, 0.72, 0.76)),
    "gpu_rx88": dict(cat="GPU", brand="VOLTRA", model="RX 8800", name="RX 8800 16 GB", line="GRAPHICS CARD",
                     specs=["16 GB GDDR6, 256-bit", "PCIe 4.0 x16", "12V-2x6 power, 300 W", "3 x DisplayPort 2.1, 1 x HDMI 2.1",
                            "Triple-fan cooler, metal backplate"], badges=["16 GB GDDR6", "12V-2x6"], style="retail",
                     bg0=(0.03, 0.025, 0.025), bg1=(0.22, 0.04, 0.05), accent=(0.90, 0.13, 0.13), text=(0.97, 0.97, 0.96),
                     font="AGENCYB.TTF", ribbon=(0.80, 0.08, 0.08)),
    "psu_450": dict(cat="PSU", brand="AMPERE", model="450 W", name="450 W Bronze", line="ATX POWER SUPPLY",
                    specs=["80 PLUS Bronze, 85% efficient", "Non-modular cables", "120 mm fluid-bearing fan", "1 x CPU 8-pin, 1 x PCIe 8-pin",
                           "Active PFC"], badges=["450 W", "80 PLUS BRONZE"], style="retail", bg0=(0.03, 0.03, 0.03),
                    bg1=(0.14, 0.11, 0.08), accent=(0.78, 0.48, 0.24), text=(0.97, 0.97, 0.95), font="FRAMDCN.TTF"),
    "psu_750": dict(cat="PSU", brand="AMPERE", model="750 W", name="750 W Gold", line="ATX 3.1 POWER SUPPLY",
                    specs=["80 PLUS Gold, 90% efficient", "Fully modular", "Native 12V-2x6 cable", "135 mm FDB fan, zero-rpm mode",
                           "2 x PCIe 8-pin, 2 x CPU 8-pin"], badges=["750 W", "80 PLUS GOLD", "ATX 3.1"], style="retail",
                    bg0=(0.03, 0.03, 0.03), bg1=(0.16, 0.13, 0.06), accent=(0.88, 0.70, 0.26), text=(0.97, 0.97, 0.95),
                    font="FRAMDCN.TTF"),
    "ssd_1tb": dict(cat="Storage", brand="QUILL", model="1 TB", name="1 TB NVMe SSD", line="M.2 2280 PCIe 4.0 NVMe",
                    specs=["Up to 7000 MB/s read", "Up to 6000 MB/s write", "M.2 2280, PCIe 4.0 x4", "5-year warranty"],
                    badges=["1 TB", "NVMe"], style="retail", bg0=(0.97, 0.97, 0.96), bg1=(0.86, 0.89, 0.90),
                    accent=(0.0, 0.58, 0.60), text=(0.08, 0.10, 0.12), font="georgiab.ttf"),
    "ssd_sata_500": dict(cat="Storage", brand="QUILL", model="500 GB", name="500 GB SATA SSD", line='2.5" SATA SOLID STATE DRIVE',
                         specs=["Up to 550 MB/s read", "Up to 500 MB/s write", '2.5", 7 mm, SATA 6 Gb/s', "3-year warranty"],
                         badges=["500 GB", "SATA"], style="retail", bg0=(0.97, 0.97, 0.96), bg1=(0.86, 0.89, 0.90),
                         accent=(0.95, 0.45, 0.10), text=(0.08, 0.10, 0.12), font="georgiab.ttf"),
    "usb_installer": dict(cat="Other", brand="BASEMENT OS", model="1.0", name="Basement OS 1.0 installer USB",
                          line="INSTALLER USB DRIVE", specs=["Bootable USB 3.0 drive, 16 GB", "Installs Basement OS 1.0",
                                                             "Boot from USB in the BIOS"], style="blister",
                          bg0=(0.04, 0.05, 0.09), bg1=(0.12, 0.15, 0.26), accent=(0.95, 0.45, 0.10), text=(0.97, 0.97, 0.96),
                          font="seguibl.ttf", model_id="usb_stick"),
    "cable_dp": dict(cat="Other", brand="LINKWIRE", model="DP 1.4", name="DisplayPort Cable 1.8 m", line="DISPLAYPORT 1.4 CABLE",
                     specs=["DisplayPort male to male", "1.8 m (6 ft)", "8K 60 Hz / 4K 144 Hz", "Latching connectors",
                            "Gold-plated contacts"], style="bag", bg0=(0.06, 0.07, 0.09), bg1=(0.10, 0.22, 0.36),
                     accent=(0.20, 0.75, 0.95), text=(0.97, 0.97, 0.98), font="seguibl.ttf"),
    "fan_splitter": dict(cat="Other", brand="LINKWIRE", model="1-TO-2", name="4-pin PWM Fan Splitter", line="FAN SPLITTER CABLE",
                         specs=["1 x 4-pin female to 2 x 4-pin male", "PWM signal from one fan only", "10 cm sleeved cable",
                                "Max 1 A per header"], style="bag", bg0=(0.06, 0.07, 0.09), bg1=(0.10, 0.22, 0.36),
                         accent=(0.20, 0.75, 0.95), text=(0.97, 0.97, 0.98), font="seguibl.ttf"),
    # parts batch D (build_parts_d.py): the same box kinds and sizes as their siblings, built after the 20 above
    "cpu_arc9": dict(cat="CPU", brand="ARC", model="9", name="9 9900X", line="DESKTOP PROCESSOR",
                     specs=["12 cores / 24 threads", "Up to 5.6 GHz boost", "76 MB total cache", "Socket V5", "120 W TDP",
                            "Cooler not included"], badges=["12 CORES", "SOCKET V5"], numeral="9", sub="9900X",
                     style="retail", bg0=(0.03, 0.025, 0.03), bg1=(0.21, 0.02, 0.06), accent=(0.94, 0.12, 0.20),
                     text=(0.97, 0.97, 0.96), font="seguibl.ttf", sibling="cpu_arc5"),
    "gpu_rx77": dict(cat="GPU", brand="VOLTRA", model="RX 7700", name="RX 7700 12 GB", line="GRAPHICS CARD",
                     specs=["12 GB GDDR6, 192-bit", "PCIe 4.0 x16", "2 x PCIe 8-pin power, 245 W", "3 x DisplayPort 1.4, 1 x HDMI 2.1",
                            "Triple-fan cooler, metal backplate"], badges=["12 GB GDDR6", "2 x 8-PIN"], style="retail",
                     bg0=(0.025, 0.03, 0.04), bg1=(0.10, 0.15, 0.21), accent=(0.55, 0.80, 0.96), text=(0.97, 0.97, 0.98),
                     font="AGENCYB.TTF", ribbon=(0.62, 0.66, 0.72), sibling="gpu_rx88"),
    "mb_ridge_x5": dict(cat="Motherboard", brand="RIDGE", model="X5 ELITE", name="X5 Elite", line="PREMIUM ATX MOTHERBOARD",
                        specs=["Socket V5", "4 x DDR5 up to 8000 MT/s", "Armoured PCIe 5.0 x16", "2 x M.2 NVMe with heatsinks",
                               "Wi-Fi 6E + 2.5G LAN", "USB 3.2 Gen 2"], badges=["SOCKET V5", "DDR5", "PCIe 5.0"],
                        style="retail", bg0=(0.94, 0.95, 0.96), bg1=(0.76, 0.79, 0.83), accent=(0.20, 0.48, 0.78),
                        text=(0.07, 0.08, 0.10), font="AGENCYB.TTF", sibling="mb_ridge_b5", bag="antistatic_silver"),
    "case_aero": dict(cat="Case", brand="AERO", model="VIEW 360", name="View 360", line="PANORAMIC ATX MID-TOWER",
                      specs=["Panoramic glass front and side, no corner pillar", "3 x 92 mm ARGB bottom + 1 x 120 mm ARGB rear",
                             "ATX / Micro-ATX / Mini-ITX", "Front I/O: 2 x USB 3.0, USB-C, audio", "GPU up to 360 mm",
                             "Magnetic dust filters"], style="carton", ink=(0.08, 0.08, 0.09), accent=(0.30, 0.66, 0.92),
                      font="seguisb.ttf", sibling="case_breeze"),
}

# Box ids that exist in Assets/Resources/Models but are not rebuilt here (kept as they are).
KEEP = ("ac_12k",)

# How a part is posed for its product shot: (local axis that faces the camera, local axis that points up),
# then the camera (yaw, pitch) in degrees around it (yaw 0 = looking from +z).
POSE = {
    "Case": ((0, 0, 1), (0, 1, 0), (-38, 12)),
    "Motherboard": ((0, 0, 1), (0, 1, 0), (14, 16)),
    "CPU": ((0, 0, 1), (0, 1, 0), (16, 26)),
    "Cooler": ((0, 1, 0), (0, 0, 1), (28, 22)),
    "RAM": ((1, 0, 0), (0, 0, 1), (18, 14)),
    "GPU": ((0, -1, 0), (0, 0, 1), (-24, 16)),
    "PSU": ((0, -1, 0), (0, 0, 1), (26, 20)),
    "Storage": ((0, 0, 1), (0, 1, 0), (14, 24)),
    "Other": ((0, 0, 1), (0, 1, 0), (22, 10)),
}
POSE_ID = {"ssd_sata_500": ((0, 1, 0), (0, 0, 1), (16, 26)), "usb_installer": ((0, 1, 0), (0, 0, -1), (24, 12)),
           "cable_dp": ((0, 0, 1), (0, 1, 0), (12, 58)), "fan_splitter": ((0, 0, 1), (0, 1, 0), (12, 58))}


# ---------------------------------------------------------------- product shots

def conv_matrix():
    return Matrix(((-1, 0, 0), (0, 0, -1), (0, 1, 0)))


def import_model(model_id):
    path = os.path.join(c.MODELS, model_id + ".fbx")
    if not os.path.exists(path):
        return None
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return new


def standin(pid, item):
    """A simple stand-in when no model exists yet (the AC's indoor unit is only ever a stand-in, the cables are coils)."""
    if pid in ("cable_dp", "fan_splitter"):
        return cable_standin(pid)
    root = c.root("standin")
    if item["cat"] == "Other" and pid == "ac_12k":
        L, Hh, D = 0.80, 0.28, 0.20
        P.slab("ac_body", P.rrect(L, Hh, 0.03, 0, Hh / 2), D, "white_plastic", P.plane((0, 0, 0), X, Y), parent=root, smooth=None)
        P.cube("ac_front", (0, Hh * 0.62, D / 2 + 0.002), (L - 0.03, Hh * 0.55, 0.004), "white_plastic", parent=root, bevel=0.002)
        for k in range(3):
            P.cube("ac_louvre", (0, 0.035 + k * 0.012, D / 2 - 0.01), (L - 0.08, 0.004, 0.03), "grey_plastic", parent=root)
        P.cube("ac_display", (0.27, Hh * 0.62, D / 2 + 0.0045), (0.07, 0.025, 0.001), "black_plastic", parent=root)
        P.cube("ac_led", (0.25, Hh * 0.62, D / 2 + 0.0052), (0.004, 0.004, 0.001), "led_blue", parent=root)
        P.text3d("ac_logo", "FROSTLINE", 0.016, 0.0006, "grey_plastic", P.Frame((-0.25, Hh * 0.62, D / 2 + 0.004), Z, Y),
                 "segoeuib.ttf", parent=root, width=0.12)
    else:
        s = box_size(pid, item["cat"])
        P.cube("standin", (0, s[1] * 0.35, 0), (s[0] * 0.7, s[1] * 0.6, s[2] * 0.7), "dark_plastic", parent=root, bevel=0.003)
    return [o for o in c.descendants(root)]


def crop_alpha(path, pad=6):
    import numpy as np
    a = P.load_png(path)
    alpha = a[..., 3]
    ys, xs = np.where(alpha > 0.02)
    if len(xs) == 0:
        return
    y0, y1 = max(0, ys.min() - pad), min(a.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad + 1)
    out = a[y0:y1, x0:x1].copy()
    # Blender saved premultiplied-free sRGB; keep as is
    P.save_png(out, os.path.splitext(os.path.basename(path))[0], os.path.dirname(path))


def render_shot(pid, item, path, size=1024, yaw_off=0.0, pitch_off=0.0):
    P.reset()
    sc = bpy.context.scene
    model_id = item.get("model_id", pid)
    objs = import_model(model_id)
    used = model_id
    if objs is None and item.get("sibling"):
        objs = import_model(item["sibling"])
        used = item["sibling"]
    if objs is None:
        objs = standin(pid, item)
        used = "stand-in"
    meshes = [o for o in objs if o.type == "MESH"]
    # materials: physically based stand-ins by tag (the material name is the tag)
    for o in meshes:
        tag = o.data.materials[0].name if o.data.materials else P._tag_of(o.name)
        if "." in tag and tag.rsplit(".", 1)[1].isdigit():
            tag = tag.rsplit(".", 1)[0]
        o.data.materials.clear()
        o.data.materials.append(P.pbr_material(tag, lit_leds=True))
    # pose: a pivot holding every top-level imported object
    fwd, up, (yaw, pitch) = POSE_ID.get(pid, POSE[item["cat"]])
    pivot = bpy.data.objects.new("shot_pivot", None)
    sc.collection.objects.link(pivot)
    for o in objs:
        if o.parent is None and o is not pivot:
            mw = o.matrix_world.copy()
            o.parent = pivot
            o.matrix_world = mw
    Wl = Vector(fwd).normalized()
    Vl = Vector(up).normalized()
    Ul = Vl.cross(Wl)
    Lm = Matrix((Ul, Vl, Wl)).transposed()       # local axes as columns (Unity)
    R = Lm.transposed()                          # maps the local axes to world x, y, z
    C = conv_matrix()
    Mb = C @ R @ C.inverted()
    pivot.matrix_world = Mb.to_4x4()
    bpy.context.view_layer.update()
    # render settings
    P._gpu_cycles(sc, 128)
    P._setup_world(sc, strength=0.9)
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.view_settings.view_transform = "AgX"
    lo, hi = P._bounds(meshes)
    centre = (lo + hi) * 0.5
    radius = (hi - lo).length * 0.5
    camd = bpy.data.cameras.new("shot_cam")
    camd.lens = 85
    cam = c.link(bpy.data.objects.new("shot_cam", camd))
    sc.camera = cam
    y_, p_ = (yaw + yaw_off) * P.DEG, (pitch + pitch_off) * P.DEG
    u = Vector((math.sin(y_) * math.cos(p_), math.sin(p_), math.cos(y_) * math.cos(p_)))
    fov = 2 * math.atan(18.0 / camd.lens)
    d = radius / math.sin(fov / 2) * 1.02
    cam.location = centre + c.conv(u) * d
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    for nm, energy, loc in (("key", 90.0, (1.0, -1.6, 2.0)), ("fill", 30.0, (-1.8, -0.8, 0.6)), ("rim", 70.0, (-0.6, 1.8, 1.4))):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy = energy * max(0.05, radius) ** 2 * 4
        ld.size = max(0.15, radius * 1.2)
        lo_ = c.link(bpy.data.objects.new(nm, ld))
        lo_.location = centre + Vector(loc) * max(0.3, radius * 2.5)
        lo_.rotation_euler = (centre - lo_.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    crop_alpha(path)
    print("SHOT", pid, "from", used, "->", path)
    return used


def ink_version(src, dst_name, ink, gamma=1.0, halftone=False):
    """A one-colour print of a product shot (for kraft cartons): ink coverage from the shot's darkness."""
    import numpy as np
    a = P.load_png(src)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    cover = np.clip((1.0 - lum) ** gamma * 1.15, 0, 1) * a[..., 3]
    # keep the outline readable: light parts of the part still get a thin wash
    cover = np.maximum(cover, a[..., 3] * 0.10)
    if halftone:
        h, w = cover.shape
        yy, xx = np.mgrid[0:h, 0:w]
        cell = 5.0
        u = (xx + yy) / (cell * 1.414)
        v = (xx - yy) / (cell * 1.414)
        du, dv = u - np.round(u), v - np.round(v)
        r = np.sqrt(du * du + dv * dv)
        dot = np.clip((np.sqrt(cover) * 0.62 - r) * 6 + 0.5, 0, 1)
        cover = np.where(cover > 0.85, cover, dot * (cover > 0.02))
    out = np.zeros_like(a)
    out[..., 0], out[..., 1], out[..., 2] = ink
    out[..., 3] = cover
    return P.save_png(out, dst_name, SHOTS)


def line_art(src, dst_name, ink, tone=0.22):
    """A flexo-style one-colour line drawing of a product shot (real case cartons are printed like this):
    ink on the edges (luminance and silhouette), a light tone fill for the dark areas."""
    import numpy as np
    a = P.load_png(src)
    al = a[..., 3]
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    # local contrast so edges inside a black object still show
    from math import sqrt
    def grad(img):
        gx = np.zeros_like(img)
        gy = np.zeros_like(img)
        gx[:, 1:-1] = img[:, 2:] - img[:, :-2]
        gy[1:-1, :] = img[2:, :] - img[:-2, :]
        return np.sqrt(gx * gx + gy * gy)
    ll = np.log(0.02 + lum) * al
    e = grad(ll) * 0.9 + grad(al) * 2.0
    e = np.clip((e - 0.06) * 3.0, 0, 1)
    # thicken a little
    e2 = e.copy()
    e2[1:, :] = np.maximum(e2[1:, :], e[:-1, :])
    e2[:, 1:] = np.maximum(e2[:, 1:], e[:, :-1])
    cover = np.clip(e2 + tone * al * (1 - np.clip(lum * 3, 0, 1)) + 0.06 * al, 0, 1)
    out = np.zeros_like(a)
    out[..., 0], out[..., 1], out[..., 2] = ink
    out[..., 3] = cover
    return P.save_png(out, dst_name, SHOTS)


def kraft_texture():
    import numpy as np
    path = os.path.join(SHOTS, "kraft.png")
    if os.path.exists(path):
        return path
    rng = np.random.default_rng(7)
    n = 1024
    base = np.array([0.66, 0.50, 0.33])
    noise = rng.normal(0, 1, (n, n)).astype(np.float32)
    # fibres: smear the noise along x, plus a low-frequency mottling
    k = np.ones(25, dtype=np.float32) / 25
    fib = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, noise)
    # isotropic mottling: white noise blurred in the frequency domain (tiles seamlessly)
    wn = rng.normal(0, 1, (n, n)).astype(np.float32)
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    g = np.exp(-(fx * fx + fy * fy) / (2 * (1.0 / 90) ** 2))
    low = np.real(np.fft.ifft2(np.fft.fft2(wn) * g)).astype(np.float32)
    low /= max(1e-6, low.std())
    t = fib * 0.045 + low * 0.011 + noise * 0.010
    img = np.zeros((n, n, 4), dtype=np.float32)
    for i in range(3):
        img[..., i] = np.clip(base[i] * (1 + t), 0, 1)
    img[..., 3] = 1
    return P.save_png(img, "kraft", SHOTS)


# ---------------------------------------------------------------- tape textures

def tape_textures():
    art = P.Art(2048, 128, bg=(0.50, 0.33, 0.14), name="tape")
    art.grad(0, 0, 2048, 128, (0.46, 0.30, 0.12), (0.60, 0.42, 0.20))
    for k in range(40):
        art.rect(0, 4 + k * 3.1, 2048, 1.0, (0.70, 0.52, 0.28), alpha=0.25)
    art.rect(0, 0, 2048, 5, (0.40, 0.26, 0.10))
    art.rect(0, 123, 2048, 5, (0.40, 0.26, 0.10))
    for k in range(6):
        x = k * 345 + 40
        art.text("BRICKHOUSE \u2022 HANDLE WITH CARE", x, 64, 30, (0.42, 0.30, 0.16), "arialbd.ttf", valign="CENTER", alpha=0.0)
    art.render("box_tape")
    art.dispose()
    art = P.Art(2048, 128, bg=(0.90, 0.91, 0.92), name="seal")
    art.grad(0, 0, 2048, 128, (0.80, 0.82, 0.85), (0.96, 0.96, 0.97))
    for k in range(9):
        x = 30 + k * 228
        art.text("SEALED \u2022 DO NOT ACCEPT IF BROKEN", x, 64, 20, (0.25, 0.27, 0.30), "arialbd.ttf", valign="CENTER", maxw=210)
    for k in range(48):
        art.rect(k * 43, 0, 2, 128, (0.70, 0.72, 0.76), alpha=0.5)
    art.render("box_seal")
    art.dispose()


# ---------------------------------------------------------------- atlas layout

def layout(s, fw):
    """Face regions (px) of one atlas: row A = front, back, left, right (height y); row B = top, bottom and the
    two side flaps (height z)."""
    sx, sy, sz = s
    pad = 0.006
    rowA = [("front", sx, sy), ("back", sx, sy), ("left", sz, sy), ("right", sz, sy)]
    rowB = [("top", sx, sz), ("bottom", sx, sz), ("flapL", fw, sz), ("flapR", fw, sz)]
    wm = max(sum(w for _, w, _ in rowA), sum(w for _, w, _ in rowB)) + pad * 5
    hm = sy + sz + pad * 3
    W = 2048
    k = W / wm
    H = 1024 if hm * k <= 1024 else 2048
    k = min(k, H / hm)
    reg = {}
    x = pad
    for n, w, h in rowA:
        reg[n] = (x * k, pad * k, w * k, h * k)
        x += w + pad
    x = pad
    for n, w, h in rowB:
        reg[n] = (x * k, (sy + 2 * pad) * k, w * k, h * k)
        x += w + pad
    return reg, W, H


def uv_of(r, W, H):
    x, y, w, h = r
    return (x / W, y / H, (x + w) / W, (y + h) / H)


# ---------------------------------------------------------------- printed art

def lighten(col, k):
    return tuple(min(1.0, x + (1 - x) * k) for x in col)


def darken(col, k):
    return tuple(x * (1 - k) for x in col)


class Face:
    def __init__(self, art, r):
        self.a = art
        self.x, self.y, self.w, self.h = r
        self.m = min(self.w, self.h)

    def X(self, f):
        return self.x + self.w * f

    def Y(self, f):
        return self.y + self.h * f


def logo(F, it, x, y, size, col, align="LEFT", maxw=None, valign="BASE"):
    txt = it["brand"].lower() if it.get("lower") else it["brand"]
    return F.a.text(txt, x, y, size, col, it.get("font", "arialbd.ttf"), align=align, maxw=maxw, valign=valign,
                    spacing=1.05)


def badge(F, x, y, text, size, fg, bg, outline=None):
    w = F.a.text_width(text, size, "arialbd.ttf") + size * 0.9
    h = size * 1.55
    F.a.poly(P.rrect(w, h, h * 0.22, x + w / 2, y + h / 2, 3), bg)
    F.a.text(text, x + w / 2, y + h / 2, size, fg, "arialbd.ttf", align="CENTER", valign="CENTER")
    return w


def category_stripe(F, it, vertical=True, frac=0.035):
    col = CAT[it["cat"]]
    if vertical:
        F.a.rect(F.x, F.y, F.w * frac, F.h, col)
    else:
        F.a.rect(F.x, F.y, F.w, F.h * frac, col)


def retail_bg(F, it, vertical=True):
    a = F.a
    a.grad(F.x, F.y, F.w, F.h, it["bg0"], it["bg1"], vertical=vertical)
    # slanted accent bands (printed in the brand colour)
    acc = it["accent"]
    x0, y0, w, h = F.x, F.y, F.w, F.h
    a.poly([(x0 + w * 0.55, y0), (x0 + w * 0.80, y0), (x0 + w * 0.35, y0 + h), (x0 + w * 0.10, y0 + h)], acc, alpha=0.10)
    a.poly([(x0 + w * 0.84, y0), (x0 + w * 0.88, y0), (x0 + w * 0.43, y0 + h), (x0 + w * 0.39, y0 + h)], acc, alpha=0.35)


def hero_face(F, it, shot, secondary=False):
    a = F.a
    retail_bg(F, it)
    acc, txt = it["accent"], it["text"]
    m = F.m
    # glow behind the product
    a.radial(F.X(0.58), F.Y(0.52), m * 0.55, lighten(acc, 0.2), it["bg1"], 0.45, 0.0)
    if shot:
        fw, fh = (0.80, 0.62) if F.w >= F.h else (0.86, 0.50)
        a.image(shot, F.X(0.56), F.Y(0.53), fit=(F.w * fw, F.h * fh))
    pad = m * 0.06
    # brand and line at the top left
    lh = m * (0.11 if not secondary else 0.13)
    logo(F, it, F.x + pad + F.w * 0.035, F.y + F.h - pad - lh * 0.8, lh, txt, maxw=F.w * 0.5)
    a.text(it["line"], F.x + pad + F.w * 0.035, F.y + F.h - pad - lh * 1.55, lh * 0.32, lighten(acc, 0.1), "arialbd.ttf",
           maxw=F.w * 0.55, spacing=1.15)
    # the model name (a big numeral for CPUs)
    if it.get("numeral"):
        n = it["numeral"]
        ns = m * 0.34
        a.text(n, F.x + F.w - pad, F.y + F.h - pad - ns * 0.78, ns, acc, it.get("font", "arialbd.ttf"), align="RIGHT")
        a.text(it["sub"], F.x + F.w - pad, F.y + F.h - pad - ns * 1.06, ns * 0.22, txt, "arialbd.ttf", align="RIGHT")
    name = it["model"] if it["cat"] not in ("RAM", "Storage", "PSU", "GPU") else it["name"].upper()
    ns = m * (0.085 if not secondary else 0.1)
    if not it.get("numeral"):
        a.text(name, F.x + pad + F.w * 0.035, F.y + pad + ns * 1.9, ns, txt, it.get("font", "arialbd.ttf"), maxw=F.w * 0.62)
    # badges along the bottom
    bx = F.x + pad + F.w * 0.035
    for b in it.get("badges", [])[: (3 if not secondary else 2)]:
        bx += badge(F, bx, F.y + pad * 0.9, b, ns * 0.42, it["bg0"], acc) + ns * 0.3
    category_stripe(F, it)


def band_face(F, it, shot):
    """A short wide face (the front of a flat box)."""
    a = F.a
    a.grad(F.x, F.y, F.w, F.h, it["bg1"], it["bg0"], vertical=False)
    acc, txt = it["accent"], it["text"]
    h = F.h
    a.rect(F.x, F.y, F.w, h * 0.12, CAT[it["cat"]])
    logo(F, it, F.x + h * 0.25, F.Y(0.56), h * 0.36, txt, maxw=F.w * 0.3, valign="CENTER")
    a.text(it["name"].upper(), F.X(0.36), F.Y(0.62), h * 0.24, txt, "arialbd.ttf", maxw=F.w * 0.38, valign="CENTER")
    a.text(it["line"], F.X(0.36), F.Y(0.33), h * 0.13, lighten(acc, 0.1), "arialbd.ttf", maxw=F.w * 0.38, valign="CENTER")
    if shot:
        a.image(shot, F.X(0.86), F.Y(0.56), fit=(F.w * 0.24, h * 0.78))


def back_face(F, it, shot, seed):
    a = F.a
    light = sum(it["bg0"]) > 1.5
    a.grad(F.x, F.y, F.w, F.h, it["bg0"], darken(it["bg1"], 0.05) if not light else it["bg1"])
    acc, txt = it["accent"], it["text"]
    m = F.m
    pad = m * 0.07
    a.rect(F.x, F.y + F.h - F.h * 0.03, F.w, F.h * 0.03, CAT[it["cat"]])
    ts = m * 0.075
    a.text("KEY FEATURES", F.x + pad, F.y + F.h - pad - ts, ts, acc, "arialbd.ttf", maxw=F.w * 0.5)
    ls = m * 0.048
    n = len(it["specs"])
    room = (F.h - 2 * pad - ts * 1.6 - m * 0.22)
    step = min(ls * 1.75, room / max(1, n))
    ls = min(ls, step / 1.6)
    for i, s_ in enumerate(it["specs"]):
        yy = F.y + F.h - pad - ts * 1.9 - (i + 1) * step
        a.rect(F.x + pad, yy + ls * 0.25, ls * 0.45, ls * 0.45, acc)
        a.text(s_, F.x + pad + ls * 0.9, yy, ls, txt, "arial.ttf", maxw=F.w * (0.52 if shot else 0.85))
    if shot and F.w > F.h * 0.8:
        a.image(shot, F.X(0.78), F.Y(0.62), fit=(F.w * 0.38, F.h * 0.5))
    # barcode in a white box, and the marks
    bw = min(F.w * 0.32, m * 0.62)
    bh = bw * 0.48
    digits = "6" + str(P.shash(it["name"]) % 10 ** 11).zfill(11)
    a.ean13(digits, F.x + F.w - pad - bw, F.y + pad, bw, bh)
    ms = m * 0.06
    mx = F.x + pad
    for t_, f_ in (("CE", "arial.ttf"), ("FC", "arialbd.ttf"), ("\u267b", "seguisym.ttf"), ("RoHS", "arialbd.ttf")):
        w = a.text(t_, mx, F.y + pad + ms * 0.2, ms, txt, f_)[0]
        mx += w + ms * 0.6
    weee(a, mx + ms * 0.4, F.y + pad, ms * 1.2, txt)
    a.text("Designed by " + it["brand"].title() + ".  Made in Taiwan.", F.x + pad, F.y + pad + ms * 1.6, ms * 0.45, txt,
           "arial.ttf", maxw=F.w * 0.5)


def weee(a, x, y, s, col):
    """The crossed-out wheelie bin."""
    a.poly([(x + s * 0.2, y + s * 0.15), (x + s * 0.8, y + s * 0.15), (x + s * 0.88, y + s * 0.85), (x + s * 0.12, y + s * 0.85)], col)
    a.poly([(x + s * 0.28, y + s * 0.22), (x + s * 0.72, y + s * 0.22), (x + s * 0.78, y + s * 0.78), (x + s * 0.22, y + s * 0.78)],
           (1, 1, 1) if sum(col) < 1.5 else (0, 0, 0))
    for (x0, y0, x1, y1) in ((0.05, 0.0, 0.95, 1.0), (0.95, 0.0, 0.05, 1.0)):
        dx, dy = (x1 - x0) * s, (y1 - y0) * s
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * s * 0.05, dx / L * s * 0.05
        a.poly([(x + x0 * s - nx, y + y0 * s - ny), (x + x0 * s + nx, y + y0 * s + ny), (x + x1 * s + nx, y + y1 * s + ny),
                (x + x1 * s - nx, y + y1 * s - ny)], col)


def side_face(F, it, shot, sticker, seed):
    a = F.a
    a.grad(F.x, F.y, F.w, F.h, it["bg0"], it["bg1"])
    acc, txt = it["accent"], it["text"]
    m = F.m
    pad = m * 0.08
    if F.h > F.w * 1.2:
        # tall side: the brand up the side
        a.text(it["brand"].lower() if it.get("lower") else it["brand"], F.X(0.3), F.y + pad, F.w * 0.32, txt,
               it.get("font", "arialbd.ttf"), rot=math.pi / 2, maxw=F.h * 0.8)
    else:
        logo(F, it, F.x + pad, F.Y(0.78), m * 0.16, txt, maxw=F.w * 0.45)
        a.text(it["name"].upper(), F.x + pad, F.Y(0.64), m * 0.075, txt, "arialbd.ttf", maxw=F.w * 0.5)
        a.text(it["line"], F.x + pad, F.Y(0.55), m * 0.045, lighten(acc, 0.1), "arialbd.ttf", maxw=F.w * 0.5)
        ls = m * 0.045
        for i, s_ in enumerate(it["specs"][:4 if not sticker else 2]):
            yy = F.Y(0.42) - i * ls * 1.7
            a.rect(F.x + pad, yy + ls * 0.25, ls * 0.4, ls * 0.4, acc)
            a.text(s_, F.x + pad + ls * 0.8, yy, ls, txt, "arial.ttf", maxw=F.w * 0.48)
        if shot and not sticker:
            a.image(shot, F.X(0.75), F.Y(0.52), fit=(F.w * 0.42, F.h * 0.7))
    a.rect(F.x, F.y, F.w, F.h * 0.05, CAT[it["cat"]])
    if sticker:
        label_sticker(F, it, seed)


def label_sticker(F, it, seed):
    a = F.a
    m = F.m
    lw, lh = min(F.w * 0.62, m * 1.25), min(F.h * 0.3, m * 0.48)
    x0, y0 = F.x + F.w - lw - m * 0.06, F.y + F.h * 0.08
    a.rect(x0, y0, lw, lh, (0.97, 0.97, 0.96))
    ink = (0.06, 0.06, 0.07)
    fs = lh * 0.11
    a.text(it["brand"] + "  " + it["name"], x0 + lh * 0.08, y0 + lh - fs * 1.4, fs, ink, "arialbd.ttf", maxw=lw * 0.9)
    a.text("P/N " + it["brand"][:2] + "-" + str(P.shash(it["name"]) % 100000).zfill(5), x0 + lh * 0.08, y0 + lh - fs * 2.7,
           fs * 0.85, ink, "consola.ttf", maxw=lw * 0.9)
    a.code128ish(seed, x0 + lh * 0.08, y0 + lh * 0.3, lw * 0.8, lh * 0.25, ink)
    a.text("S/N " + str(P.shash(it["name"] + "sn") % 10 ** 12).zfill(12), x0 + lh * 0.08, y0 + lh * 0.1, fs * 0.85, ink,
           "consola.ttf", maxw=lw * 0.9)


def bottom_face(F, it):
    a = F.a
    a.rect(F.x, F.y, F.w, F.h, it["bg0"])
    txt = it["text"]
    m = F.m
    a.text("\u267b", F.X(0.5), F.Y(0.5), m * 0.22, txt, "seguisym.ttf", align="CENTER", valign="CENTER")
    a.text("PLEASE RECYCLE THIS PACKAGING", F.X(0.5), F.Y(0.25), m * 0.05, txt, "arialbd.ttf", align="CENTER", maxw=F.w * 0.8)


def flap_face(F, it):
    a = F.a
    a.rect(F.x, F.y, F.w, F.h, it["bg1"])
    a.rect(F.x, F.y, F.w * 0.08, F.h, CAT[it["cat"]])


# kraft cartons -------------------------------------------------------------

def kraft_bg(F, kraft):
    F.a.image(kraft, F.x, F.y, F.w, F.h)


def carton_hero(F, it, ink_shot, kraft):
    a = F.a
    kraft_bg(F, kraft)
    ink, acc = it["ink"], it["accent"]
    m = F.m
    pad = m * 0.06
    # big brand across the top, the product line under it
    ls = m * 0.13
    logo(F, it, F.x + pad, F.y + F.h - pad - ls * 0.85, ls, ink, maxw=F.w * 0.72)
    a.text(it["line"], F.x + pad, F.y + F.h - pad - ls * 1.5, ls * 0.28, ink, "arialbd.ttf", maxw=F.w * 0.7, spacing=1.2)
    a.rect(F.x + pad, F.y + F.h - pad - ls * 1.75, F.w * 0.5, ls * 0.06, acc)
    if ink_shot:
        a.image(ink_shot, F.X(0.5), F.Y(0.46), fit=(F.w * 0.74, F.h * 0.6))
    # model in the accent colour, bottom right, and the spec line
    a.text(it["model"], F.x + F.w - pad, F.y + pad + ls * 0.4, ls * 0.9, acc, it.get("font", "arialbd.ttf"), align="RIGHT", maxw=F.w * 0.5)
    a.rect(F.x, F.y, F.w, F.h * 0.022, CAT[it["cat"]])


def carton_side(F, it, kraft, sticker, seed):
    a = F.a
    kraft_bg(F, kraft)
    ink, acc = it["ink"], it["accent"]
    m = F.m
    pad = m * 0.07
    top = F.y + F.h - F.h * 0.2      # below the tape that runs down the ends
    logo(F, it, F.x + pad, top - m * 0.09, m * 0.11, ink, maxw=F.w * 0.8)
    a.text(it["name"].upper(), F.x + pad, top - m * 0.17, m * 0.05, ink, "arialbd.ttf", maxw=F.w * 0.8)
    ls = m * 0.042
    for i, s_ in enumerate(it["specs"]):
        yy = top - m * 0.27 - i * ls * 1.8
        a.rect(F.x + pad, yy + ls * 0.25, ls * 0.45, ls * 0.45, acc)
        a.text(s_, F.x + pad + ls * 0.9, yy, ls, ink, "arial.ttf", maxw=F.w * 0.8)
    # handling marks: this way up, fragile, keep dry
    hs = m * 0.12
    hx = F.x + pad
    hy = F.y + pad + (F.h * 0.3 if sticker else 0)
    arrows(a, hx, hy, hs, ink)
    glass(a, hx + hs * 1.4, hy, hs, ink)
    umbrella(a, hx + hs * 2.8, hy, hs, ink)
    if sticker:
        label_sticker(F, dict(it, text=ink), seed)
    a.rect(F.x, F.y, F.w, F.h * 0.022, CAT[it["cat"]])


def carton_top(F, it, kraft):
    a = F.a
    kraft_bg(F, kraft)
    ink = it["ink"]
    m = F.m
    logo(F, it, F.X(0.5), F.Y(0.78), m * 0.12, ink, align="CENTER", maxw=F.w * 0.7, valign="CENTER")
    logo(F, it, F.X(0.5), F.Y(0.22), m * 0.12, ink, align="CENTER", maxw=F.w * 0.7, valign="CENTER")
    hs = m * 0.12
    arrows(a, F.X(0.12), F.Y(0.62), hs, ink)
    arrows(a, F.X(0.80), F.Y(0.62), hs, ink)


def arrows(a, x, y, s, col):
    """'This way up': two arrows over a bar in a box."""
    t = s * 0.06
    for (x0, y0, x1, y1) in ((0, 0, s, t), (0, s - t, s, s), (0, 0, t, s), (s - t, 0, s, s)):
        a.rect(x + x0, y + y0, x1 - x0, y1 - y0, col)
    for cx in (0.33, 0.67):
        a.rect(x + s * cx - s * 0.04, y + s * 0.25, s * 0.08, s * 0.4, col)
        a.poly([(x + s * (cx - 0.13), y + s * 0.62), (x + s * (cx + 0.13), y + s * 0.62), (x + s * cx, y + s * 0.85)], col)
    a.rect(x + s * 0.18, y + s * 0.14, s * 0.64, s * 0.06, col)


def glass(a, x, y, s, col):
    t = s * 0.06
    for (x0, y0, x1, y1) in ((0, 0, s, t), (0, s - t, s, s), (0, 0, t, s), (s - t, 0, s, s)):
        a.rect(x + x0, y + y0, x1 - x0, y1 - y0, col)
    a.poly([(x + s * 0.3, y + s * 0.85), (x + s * 0.7, y + s * 0.85), (x + s * 0.62, y + s * 0.5), (x + s * 0.38, y + s * 0.5)], col)
    a.rect(x + s * 0.47, y + s * 0.2, s * 0.06, s * 0.32, col)
    a.rect(x + s * 0.34, y + s * 0.16, s * 0.32, s * 0.06, col)


def umbrella(a, x, y, s, col):
    t = s * 0.06
    for (x0, y0, x1, y1) in ((0, 0, s, t), (0, s - t, s, s), (0, 0, t, s), (s - t, 0, s, s)):
        a.rect(x + x0, y + y0, x1 - x0, y1 - y0, col)
    a.poly([(x + s * 0.15, y + s * 0.55)] + [(x + s * (0.5 + 0.35 * math.cos(t_)), y + s * (0.55 + 0.25 * math.sin(t_)))
                                             for t_ in [i * math.pi / 12 for i in range(13)]], col)
    a.rect(x + s * 0.48, y + s * 0.2, s * 0.04, s * 0.36, col)
    for k in range(3):
        a.rect(x + s * (0.2 + k * 0.08), y + s * (0.84 + 0.0), s * 0.025, s * 0.08, col)


def compose(pid, it, s, fw, shot, ink_shot, kraft):
    reg, W, H = layout(s, fw)
    art = P.Art(W, H, bg=(0.5, 0.5, 0.5), name="box_" + pid)
    sx, sy, sz = s
    seed = P.shash(pid) & 0xffff
    if it["style"] == "carton":
        carton_hero(Face(art, reg["front"]), it, ink_shot, kraft)
        carton_hero(Face(art, reg["back"]), it, ink_shot, kraft)
        carton_side(Face(art, reg["left"]), it, kraft, False, seed)
        carton_side(Face(art, reg["right"]), it, kraft, True, seed)
        carton_top(Face(art, reg["top"]), it, kraft)
        kraft_bg(Face(art, reg["bottom"]), kraft)
        for n in ("flapL", "flapR"):
            kraft_bg(Face(art, reg[n]), kraft)
    else:
        top_hero = sx * sz >= sx * sy * 1.1
        hero_name, other = ("top", "front") if top_hero else ("front", "top")
        hero_face(Face(art, reg[hero_name]), it, shot)
        o = Face(art, reg[other])
        if o.h / o.w < 0.4:
            band_face(o, it, shot)
        else:
            hero_face(o, it, shot, secondary=True)
        back_face(Face(art, reg["back"]), it, shot, seed)
        side_face(Face(art, reg["left"]), it, shot, False, seed)
        side_face(Face(art, reg["right"]), it, shot, True, seed)
        bottom_face(Face(art, reg["bottom"]), it)
        flap_face(Face(art, reg["flapL"]), it)
        flap_face(Face(art, reg["flapR"]), it)
    art.render("box_" + pid)
    art.dispose()
    return reg, W, H


# ---------------------------------------------------------------- blister card and bag header art

BLISTER_UV = {"front": (8 / 1024, 8 / 1024, 508 / 1024, 1016 / 1024), "back": (516 / 1024, 8 / 1024, 1016 / 1024, 1016 / 1024)}


def compose_blister(pid, it):
    """usb_installer: the card's front and back side by side (tex_box_usb_installer)."""
    W, H = 1024, 1024
    art = P.Art(W, H, bg=(0.1, 0.1, 0.1), name="blister")
    front = (8, 8, 500, 1008)
    back = (516, 8, 500, 1008)
    F_ = Face(art, front)
    art.grad(F_.x, F_.y, F_.w, F_.h, it["bg0"], it["bg1"])
    acc, txt = it["accent"], it["text"]
    art.poly([(F_.X(0), F_.Y(0.08)), (F_.X(1), F_.Y(0.20)), (F_.X(1), F_.Y(0.24)), (F_.X(0), F_.Y(0.12))], acc)
    art.circle(F_.X(0.5), F_.Y(0.47), 150, lighten(it["bg1"], 0.15))
    art.text("BASEMENT OS", F_.X(0.5), F_.Y(0.86), 58, txt, "seguibl.ttf", align="CENTER", maxw=F_.w * 0.86)
    art.text("1.0", F_.X(0.5), F_.Y(0.79), 54, acc, "seguibl.ttf", align="CENTER")
    art.text("INSTALLER USB DRIVE", F_.X(0.5), F_.Y(0.745), 22, lighten(acc, 0.3), "arialbd.ttf", align="CENTER", spacing=1.2)
    art.text("BOOTABLE  •  16 GB  •  USB 3.0", F_.X(0.5), F_.Y(0.06), 20, txt, "arialbd.ttf", align="CENTER", maxw=F_.w * 0.9)
    art.rect(F_.x, F_.y + F_.h * 0.965, F_.w, F_.h * 0.035, CAT["Other"])
    B = Face(art, back)
    art.rect(B.x, B.y, B.w, B.h, (0.95, 0.95, 0.94))
    ink = (0.08, 0.08, 0.1)
    art.text("BASEMENT OS 1.0 INSTALLER", B.X(0.08), B.Y(0.84), 26, ink, "arialbd.ttf", maxw=B.w * 0.84)
    for i, s_ in enumerate(["1. Plug the drive into a rear USB port.", "2. Press DEL at power-on and put USB",
                            "    first in the boot order (Boot tab).", "3. Save with F10 and follow the installer.",
                            "4. Remove the drive when asked."]):
        art.text(s_, B.X(0.08), B.Y(0.76) - i * 34, 20, ink, "arial.ttf", maxw=B.w * 0.86)
    # the peel-open back panel (perforated outline) under the blister
    px, py, pw, ph = B.X(0.22), B.Y(0.25), B.w * 0.56, B.h * 0.30
    for k in range(40):
        t_ = k / 40
        art.rect(px + pw * t_, py, pw / 80, 2, ink)
        art.rect(px + pw * t_, py + ph, pw / 80, 2, ink)
    for k in range(24):
        t_ = k / 24
        art.rect(px, py + ph * t_, 2, ph / 48, ink)
        art.rect(px + pw, py + ph * t_, 2, ph / 48, ink)
    art.text("PEEL HERE", px + pw / 2, py + ph * 0.5, 20, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    art.ean13("590000000150", B.X(0.52), B.Y(0.06), B.w * 0.4, B.w * 0.2)
    art.text("CE  FC  ♻", B.X(0.08), B.Y(0.08), 30, ink, "seguisym.ttf")
    art.rect(B.x, B.y + B.h * 0.965, B.w, B.h * 0.035, CAT["Other"])
    art.render("box_" + pid)
    art.dispose()


HEADER_UV = {"front": (0.0, 0.5, 1.0, 1.0), "back": (0.0, 0.0, 1.0, 0.5)}


def compose_header(pid, it, shot):
    """cable_dp / fan_splitter: the header card of the zip bag, front (top half) and back (bottom half)."""
    W, H = 1024, 1024
    art = P.Art(W, H, bg=(0.5, 0.5, 0.5), name="header")
    F_ = Face(art, (0, 512, 1024, 512))
    acc, txt = it["accent"], it["text"]
    art.grad(F_.x, F_.y, F_.w, F_.h, it["bg0"], it["bg1"], vertical=False)
    art.poly([(F_.X(0.55), F_.y), (F_.X(0.75), F_.y), (F_.X(0.6), F_.y + F_.h), (F_.X(0.4), F_.y + F_.h)], acc, alpha=0.18)
    # euro hang hole is cut in the card at the top centre: keep the top band clear
    art.text(it["brand"], F_.X(0.06), F_.Y(0.60), 92, txt, it["font"], maxw=F_.w * 0.5)
    art.text(it["name"].upper(), F_.X(0.06), F_.Y(0.42), 44, txt, "arialbd.ttf", maxw=F_.w * 0.56)
    art.text(it["line"], F_.X(0.06), F_.Y(0.32), 26, lighten(acc, 0.2), "arialbd.ttf", maxw=F_.w * 0.56, spacing=1.2)
    if shot and os.path.exists(shot):
        art.image(shot, F_.X(0.80), F_.Y(0.45), fit=(F_.w * 0.36, F_.h * 0.80))
    bx = F_.X(0.06)
    for b in it["specs"][:2]:
        bx += badge(F_, bx, F_.Y(0.08), b.upper(), 22, it["bg0"], acc) + 16
    art.rect(F_.x, F_.y, F_.w, F_.h * 0.04, CAT[it["cat"]])
    B = Face(art, (0, 0, 1024, 512))
    art.rect(B.x, B.y, B.w, B.h, (0.95, 0.95, 0.94))
    ink = (0.08, 0.08, 0.1)
    art.text(it["brand"] + "  " + it["name"], B.X(0.05), B.Y(0.70), 40, ink, "arialbd.ttf", maxw=B.w * 0.9)
    for i, s_ in enumerate(it["specs"]):
        art.rect(B.X(0.05), B.Y(0.56) - i * 46 + 8, 12, 12, acc)
        art.text(s_, B.X(0.05) + 24, B.Y(0.56) - i * 46, 26, ink, "arial.ttf", maxw=B.w * 0.55)
    art.ean13("6" + str(P.shash(it["name"]) % 10 ** 11).zfill(11), B.X(0.66), B.Y(0.12), B.w * 0.28, B.h * 0.32)
    art.text("CE  FC  ♻  RoHS", B.X(0.05), B.Y(0.08), 30, ink, "seguisym.ttf")
    art.render("box_" + pid)
    art.dispose()


# ---------------------------------------------------------------- inner prints (tex_box_<pid>_in)

INNER_W = 1024
SWATCHES = ("field", "accent", "white", "black", "ribbon", "grey", "kraft", "bg1")


def inner_colours(it):
    dark = sum(it.get("bg0", (0, 0, 0))) < 1.5
    field = it.get("field") or ((0.035, 0.035, 0.04) if dark else (0.96, 0.96, 0.95))
    ink = it.get("field_ink") or ((0.62, 0.63, 0.66) if sum(field) < 1.5 else (0.12, 0.13, 0.15))
    if it.get("style") == "carton":
        field = (0.95, 0.95, 0.94)
        ink = it["ink"]
    return field, ink


def inner_art(pid, it):
    """tex_box_<pid>_in: the inner box, trays, accessory box and ribbon prints. Returns {'uv': {panel: rect},
    'sw': {swatch: uv point}}. Panels: logo (a field panel with the brand), end (brand + product name on a long
    strip), acc (a white accessory-box face), label (a white kit label)."""
    W = INNER_W
    art = P.Art(W, W, bg=(0.5, 0.5, 0.5), name="in_" + pid)
    field, ink = inner_colours(it)
    acc = it.get("accent", (0.5, 0.5, 0.5))
    font = it.get("font", "arialbd.ttf")
    brand = it["brand"].lower() if it.get("lower") else it["brand"]
    regions = {"logo": (0, 512, 512, 512), "end": (512, 768, 512, 256), "acc": (512, 512, 512, 256),
               "label": (512, 256, 512, 256), "stripe": (0, 256, 512, 256)}
    # logo panel: the field with the brand embossed-looking (a lighter/darker ink), a fine accent rule
    x, y, w, h = regions["logo"]
    art.rect(x, y, w, h, field)
    art.text(brand, x + w / 2, y + h * 0.52, 74, ink, font, align="CENTER", valign="CENTER", maxw=w * 0.7)
    art.rect(x + w * 0.3, y + h * 0.40, w * 0.4, 3, acc)
    art.text(it["name"].upper(), x + w / 2, y + h * 0.33, 22, ink, "arialbd.ttf", align="CENTER", maxw=w * 0.8, spacing=1.2)
    # end panel: brand + product name across a long strip
    x, y, w, h = regions["end"]
    art.rect(x, y, w, h, field)
    art.text(brand, x + 24, y + h * 0.5, 62, ink, font, valign="CENTER", maxw=w * 0.42)
    art.text(it["name"].upper(), x + w - 24, y + h * 0.5, 30, ink, "arialbd.ttf", align="RIGHT", valign="CENTER", maxw=w * 0.5)
    art.rect(x, y, w, 10, acc)
    # accessory box face: white board, black print
    x, y, w, h = regions["acc"]
    art.rect(x, y, w, h, (0.95, 0.95, 0.94))
    blk = (0.08, 0.08, 0.09)
    art.text(brand, x + 26, y + h - 70, 50, blk, font, maxw=w * 0.6)
    art.text("ACCESSORIES", x + 26, y + h - 120, 30, blk, "arialbd.ttf", spacing=1.25)
    art.text("Mounting hardware, cables and documentation inside.", x + 26, y + 40, 18, blk, "arial.ttf", maxw=w * 0.9)
    art.rect(x, y, w, 8, CAT[it["cat"]])
    # kit label: white with a bar code, for screw kits and pouches
    x, y, w, h = regions["label"]
    art.rect(x, y, w, h, (0.97, 0.97, 0.96))
    art.text(brand + "  " + it["name"], x + 20, y + h - 50, 30, blk, "arialbd.ttf", maxw=w * 0.9)
    art.code128ish(P.shash(pid) & 0xffff, x + 20, y + 30, w * 0.6, 70, blk)
    # stripe panel: the field with accent bands (tray decks, ribbons)
    x, y, w, h = regions["stripe"]
    art.rect(x, y, w, h, field)
    for k in range(3):
        art.rect(x, y + 40 + k * 30, w, 8, acc, alpha=0.9 - k * 0.25)
    # swatches
    rib = it.get("ribbon", acc)
    cols = {"field": field, "accent": acc, "white": (0.95, 0.95, 0.94), "black": (0.03, 0.03, 0.035), "ribbon": rib,
            "grey": (0.45, 0.46, 0.48), "kraft": (0.62, 0.47, 0.30), "bg1": it.get("bg1", field)}
    sw = {}
    for i, n in enumerate(SWATCHES):
        art.rect(i * 128, 0, 128, 256, cols[n])
        sw[n] = ((i * 128 + 64) / W, 128 / W)
    art.render("box_" + pid + "_in")
    art.dispose()
    uv = {k: (r[0] / W, r[1] / W, (r[0] + r[2]) / W, (r[1] + r[3]) / W) for k, r in regions.items()}
    return {"uv": uv, "sw": sw, "field": field, "ink": ink}


# ---------------------------------------------------------------- product shots of the cable items (no part model)

def _fbx_at(model_id, frame):
    objs = import_model(model_id)
    if not objs:
        return []
    piv = bpy.data.objects.new("piv", None)
    bpy.context.scene.collection.objects.link(piv)
    for o in objs:
        if o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = piv
            o.matrix_world = mw
    m = Matrix.Translation(c.conv(frame.o)) @ c.basis(frame.fwd, frame.up).to_4x4()
    piv.matrix_world = m
    return objs + [piv]


def cable_standin(pid):
    """A coiled cable for the product shot (cable_dp, fan_splitter have no part model)."""
    root = c.root("standin")
    objs = [root]
    if pid == "cable_dp":
        R0, turns, r = 0.052, 5, 0.0028
        pts = []
        for i in range(turns * 24 + 1):
            a = 2 * math.pi * i / 24
            rr_ = R0 + 0.004 * math.sin(i * 0.7) + 0.0015 * (i / 24)
            pts.append((rr_ * math.cos(a), 0.004 + 0.0035 * math.sin(a * 0.5 + i * 0.05) + 0.0006 * (i / 24), rr_ * math.sin(a)))
        a_end = 2 * math.pi * turns
        e0, e1 = pts[0], pts[-1]
        pts = [(e0[0] + 0.05, e0[1], e0[2] - 0.03)] + pts + [(e1[0] + 0.03, e1[1], e1[2] + 0.06)]
        P.tube("coil", P.smooth_path(pts, 2), r, "rubber", parent=root, verts=10)
        objs += _fbx_at("plug_dp", P.Frame((pts[0][0] + 0.0, pts[0][1], pts[0][2] - 0.0), (-0.85, 0, 0.55), (0, 1, 0)))
        objs += _fbx_at("plug_dp", P.Frame((pts[-1][0], pts[-1][1], pts[-1][2]), (-0.5, 0, -0.86), (0, 1, 0)))
        P.cube("tie", (R0, 0.005, 0.0), (0.012, 0.014, 0.003), "white_plastic", parent=root, bevel=0.001)
    else:
        pts = [(-0.05, 0.004, 0.0), (-0.02, 0.006, 0.01), (0.0, 0.006, 0.0), (0.02, 0.005, -0.02), (0.04, 0.004, -0.03)]
        P.tube("lead", P.smooth_path(pts, 4), 0.0018, "rubber", parent=root, verts=8)
        pts2 = [(0.0, 0.006, 0.0), (0.02, 0.005, 0.02), (0.045, 0.004, 0.03)]
        P.tube("lead2", P.smooth_path(pts2, 4), 0.0018, "rubber", parent=root, verts=8)
        objs += _fbx_at("plug_fan4", P.Frame((-0.05, 0.004, 0.0), (-1, 0, 0), (0, 1, 0)))
        objs += _fbx_at("plug_fan4", P.Frame((0.04, 0.004, -0.03), (0.8, 0, -0.6), (0, 1, 0)))
        objs += _fbx_at("plug_fan4", P.Frame((0.045, 0.004, 0.03), (0.8, 0, 0.6), (0, 1, 0)))
    objs += [o for o in c.descendants(root) if o not in objs]
    return objs


# ---------------------------------------------------------------- driver

def shot_paths(pid):
    return os.path.join(SHOTS, pid + "_hero.png"), pid + "_ink"


class Ctx:
    """Everything a rig builder needs: the item, its size, the art atlas and the inner print."""

    def __init__(self, pid, it, s, reg=None, W=None, H=None, fw=None, inner=None, hero=None):
        self.pid, self.it, self.s = pid, it, s
        self.tex = "tex_box_" + pid
        self.tin = "tex_box_" + pid + "_in"
        self.uv = {k: uv_of(v, W, H) for k, v in reg.items()} if reg else {}
        self.fw = fw
        self.inner = inner or {}
        self.iuv = self.inner.get("uv", {})
        self.sw = self.inner.get("sw", {})
        self.hero = hero
        self.cat = it["cat"]


def build(pid, do_shots=True, do_preview=True):
    import rig_products as RP
    it = ITEMS[pid]
    os.makedirs(SHOTS, exist_ok=True)
    hero, ink_name = shot_paths(pid)
    used = "cached"
    if do_shots or not os.path.exists(hero):
        used = render_shot(pid, it, hero)
    P.reset()
    kraft = kraft_texture()
    ink_shot = None
    if it["style"] == "carton":
        ink_shot = line_art(hero, ink_name, it["ink"])
    s = box_size(pid, it["cat"])
    P.reset()
    kraft_texture()
    inner = inner_art(pid, it)
    if it["style"] == "blister":
        compose_blister(pid, it)
        ctx = Ctx(pid, it, s, inner=inner, hero=hero)
    elif it["style"] == "bag":
        compose_header(pid, it, hero)
        ctx = Ctx(pid, it, s, inner=inner, hero=hero)
    else:
        fw = min(s[0] * 0.3, s[2] * 0.45)
        reg, W, H = compose(pid, it, s, fw, hero, ink_shot, kraft)
        ctx = Ctx(pid, it, s, reg, W, H, fw, inner, hero)
    P.reset()
    rig = RP.BUILDERS[RP.kind_of(pid, it)](ctx)
    bid = "box_" + pid
    rig.finalize()
    bad = rig.check()
    import time
    for attempt in range(6):          # the editor may hold the file for a moment while it imports
        try:
            c.export(rig.root, bid)
            break
        except (RuntimeError, OSError) as ex:
            print("EXPORT RETRY", bid, ex)
            time.sleep(3.0)
    notes = RP.NOTES.get(pid, "")
    tris, meshes = P.write_report(rig.root, bid, f"shot from: {used}\n{notes}" + ("\nCHECK: " + "; ".join(bad) if bad else ""))
    if do_preview:
        RP.previews(rig, ctx)
    return tris, meshes, used


def main(argv=None):
    argv = list(argv or [])
    do_shots = "--noshots" not in argv
    do_prev = "--nopreview" not in argv
    ids = [a[4:] if a.startswith("box_") else a for a in argv if not a.startswith("--")]
    ids = [i for i in ids if i not in KEEP]
    P.reset()
    P.write_palette()
    tape_textures()
    out = {}
    for pid in (ids or list(ITEMS)):
        if pid not in ITEMS:
            print("UNKNOWN id", pid)
            continue
        out[pid] = build(pid, do_shots, do_prev)
    for k, v in out.items():
        print("BUILT box_" + k, v)
    return out


if __name__ == "__main__":
    main(c.args())
