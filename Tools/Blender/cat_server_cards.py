"""
cat_server_cards: the PCIe add-in cards of catalogue 18 (build_cat_server.py) and their low-profile brackets.

Card frame = the GPU frame (docs/MODEL_PIPELINE.md, build_gpu.py): origin at the PCIe contact edge, where the centre
of an x16 edge would be, so a card of any width installs in a slot at the same pose as a graphics card. The card runs
from the bracket at x = +0.095 towards -x, its components face -y, its height runs along +z away from the slot.
PCB y -0.0018..-0.0002; the gold fingers z -0.0052..-0.0012, starting 0.0445 from the origin on the bracket side
(the 11-pin segment, the key, then the long segment: 21 pins for x4, 38 for x8, 71 for x16).

Every card is a single-slot low-profile card (68.9 mm board) that ships with a full-height bracket fitted:
  * the bracket is the moving piece of A_BRACKET_0 (at the bracket's outer face, on the slot-0 centre line, at the
    full-height bracket's mid height z = 0.0465; model axes), meta swap=<id>_lpbracket. The separate model <id>_lpbracket has its origin
    at that same pose, so the game swaps them by removing bracket@A_BRACKET_0 and placing the model at A_BRACKET_0.
  * A_SCREW_PH2_0 is the case-slot screw in the bracket tab (the GPU's slot 0 position: x 0.1015, y -0.0069,
    z 0.1065); A_SCREW_PH1_0..1 are the two small screws that hold the bracket to the port cages.
  * Ports A_PORT_ETH_n / A_PORT_SFP_n / A_PORT_QSFP_n at the bracket's outer face (x 0.0965), +Z out of the bracket
    (+x), +Y away from the board (-y): the cage top / RJ45 latch side. Each has A_LED_LINK_n and A_LED_ACT_n.
    A_PORT_SAS_n are the internal SFF-8654 x8 receptacles on the top edge, +Z up (+z), with A_LED_SAS_n.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import datacenter_common as D  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ

# the GPU contract's numbers (build_gpu.py)
X0 = 0.095
PCB_Y0, PCB_Y1 = -0.0018, -0.0002
BR_X0, BR_X1 = 0.0955, 0.0965
BR_YT = 0.0030
BR_YB = BR_YT - 0.0184           # one slot wide (the GPU bracket is two: -0.0362)
Z_TAB = 0.1065                   # full-height tab (the case's slot rail)
Z_TAB_LP = 0.0657                # low-profile bracket: 79.2 mm long, its tongue 13.5 mm below the slot top
X_SCREW = 0.1015
SLOT_Y0 = -0.0069
TAB_BOT = -0.0055
X_PCB_END = 0.0947               # the board's edge at the bracket
HP = 0.0634                      # low-profile board: 68.9 mm from the bottom of the fingers
BRK = (BR_X1, SLOT_Y0, 0.0465)   # A_BRACKET_0: the full-height bracket's centre
LONG_PINS = {1: 7, 4: 21, 8: 38, 16: 71}

ATLAS = D.Atlas("cat_server_cards", 2048, 1024)
for _k in range(8):
    ATLAS.add(f"lab{_k}", (_k % 4) * 512, (_k // 4) * 192, 512, 192)
ATLAS.add("logo_linkwave", 0, 400, 512, 128)
ATLAS.add("logo_melnet", 512, 400, 512, 128)
ATLAS.add("logo_broadline", 1024, 400, 512, 128)
ATLAS.add("silk", 0, 560, 1536, 256)
ATLAS.add("legends", 1536, 400, 512, 416)
ATLAS.add("supercap", 0, 840, 512, 160)
LEGENDS = D.Labels(ATLAS, "legends", 128, 32, ["1", "2", "P1", "P2", "ACT", "LNK", "0-7", "8-15", "SAS", "25G", "100G",
                   "10G", "1G", "C0", "C1", "ERR", "HB"], fg=(0.92, 0.93, 0.95), size=0.6)

# brand looks: Linkwave = Intel Ethernet (green board, bare alu sink, blue label), Melnet = Mellanox (green board,
# black sink with a white print), Broadline = Broadcom/LSI (green board, black finned sink)
CARDS = {
    "nic_linkwave_350t2": dict(
        brand="Linkwave", model="LW350-T2", lanes=4, L=0.1275, kind="eth", ports=[0.0215, 0.0400], speed="1g",
        sink=dict(x=0.040, z=0.030, w=0.022, l=0.022, h=0.006, tag="alu", fins=7), lab=0, logo="logo_linkwave",
        title="Dual-port 1GbE server adapter", sub="2 x RJ45  -  PCIe 2.1 x4", sn="LW350T2-2611-0044",
        mac="A0:36:9F:4D:21:E8", label_col=(0.05, 0.36, 0.7), magnetics=True),
    "nic_linkwave_710da2": dict(
        brand="Linkwave", model="LW710-DA2", lanes=8, L=0.1676, kind="sfp", ports=[0.0215, 0.0405], speed="10g",
        sink=dict(x=0.000, z=0.031, w=0.036, l=0.036, h=0.010, tag="alu", fins=11), lab=1, logo="logo_linkwave",
        title="Dual-port 10GbE SFP+ adapter", sub="2 x SFP+  -  PCIe 3.0 x8", sn="LW710DA2-2547-1093",
        mac="3C:FD:FE:A1:07:5C", label_col=(0.05, 0.36, 0.7)),
    "nic_melnet_strand6_25g": dict(
        brand="Melnet", model="Strand-6 Lx", lanes=8, L=0.1676, kind="sfp", ports=[0.0215, 0.0405], speed="25g",
        sink=dict(x=-0.004, z=0.031, w=0.040, l=0.040, h=0.011, tag="alu_dark", fins=12), lab=2, logo="logo_melnet",
        title="Strand-6 Lx dual-port 25GbE SFP28", sub="2 x SFP28  -  PCIe 4.0 x8", sn="MT2611X09812",
        mac="B8:CE:F6:2A:91:40", label_col=(0.1, 0.1, 0.11)),
    "nic_melnet_strand6_100g": dict(
        brand="Melnet", model="Strand-6 Dx", lanes=16, L=0.1676, kind="qsfp", ports=[0.0190, 0.0440], speed="100g",
        sink=dict(x=-0.010, z=0.031, w=0.052, l=0.046, h=0.012, tag="alu_dark", fins=14), lab=3, logo="logo_melnet",
        title="Strand-6 Dx dual-port 100GbE QSFP28", sub="2 x QSFP28  -  PCIe 4.0 x16", sn="MT2614X21377",
        mac="0C:42:A1:7E:33:B2", label_col=(0.1, 0.1, 0.11)),
    "hba_broadline_9500_16i": dict(
        brand="Broadline", model="9500-16i", lanes=8, L=0.1556, kind="sas", ports=[-0.0350, -0.0040], speed="12g",
        sink=dict(x=0.030, z=0.029, w=0.056, l=0.048, h=0.014, tag="paint_black", fins=13), lab=4, logo="logo_broadline",
        title="9500-16i tri-mode storage adapter", sub="16 internal ports  -  2 x SFF-8654 x8", sn="SP26101877",
        mac="SAS 500605B0:1C7E4A90", label_col=(0.55, 0.05, 0.08)),
    "hba_broadline_9560_16i": dict(
        brand="Broadline", model="9560-16i", lanes=8, L=0.1556, kind="sas", ports=[-0.0350, -0.0040], speed="12g",
        sink=dict(x=0.033, z=0.029, w=0.050, l=0.046, h=0.014, tag="paint_black", fins=12), lab=5, logo="logo_broadline",
        title="9560-16i RAID controller, 8 GB cache", sub="RAID 0/1/5/6/10/50/60  -  2 x SFF-8654 x8", sn="SP26112406",
        mac="SAS 500605B0:2A11F3C8", label_col=(0.55, 0.05, 0.08), raid=True),
}


# ====================================================================== artwork

def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=None, name="cat_server_cards")
    ink = (0.08, 0.08, 0.09)
    for cid, s in CARDS.items():
        x, y, w, h = ATLAS.reg[f"lab{s['lab']}"]
        art.rect(x + 4, y + 4, w - 8, h - 8, (0.95, 0.95, 0.93))
        art.rect(x + 4, y + h - 46, w - 8, 42, s["label_col"])
        art.text(s["brand"].upper(), x + 18, y + h - 34, 28, (0.97, 0.97, 0.98), "segoeuib.ttf", spacing=1.1)
        art.text(s["model"], x + w - 18, y + h - 34, 26, (0.97, 0.97, 0.98), "arialbd.ttf", align="RIGHT")
        art.text(s["title"], x + 18, y + h - 72, 19, ink, "arialbd.ttf", maxw=w - 36)
        art.text(s["sub"], x + 18, y + h - 96, 16, ink, "arial.ttf", maxw=w - 36)
        art.text("S/N " + s["sn"], x + 18, y + 64, 16, ink, "consola.ttf")
        art.text(("MAC " if ":" in s["mac"][:3] or s["mac"][2] == ":" else "") + s["mac"], x + 18, y + 44, 15, ink, "consola.ttf",
                 maxw=300)
        art.code128ish(P.shash(cid) % 9999, x + 18, y + 12, 290, 26, ink)
        for i in range(13):    # a QR-like square
            for j in range(13):
                if (i * 5 + j * 11 + i * j) % 4 < 2 or (i < 4 and j < 4):
                    art.rect(x + w - 128 + i * 8, y + 14 + j * 8, 8, 8, ink)
    for reg, word, col in (("logo_linkwave", "LINKWAVE", (0.93, 0.94, 0.96)), ("logo_melnet", "MELNET", (0.95, 0.95, 0.96)),
                           ("logo_broadline", "BROADLINE", (0.93, 0.93, 0.95))):
        x, y, w, h = ATLAS.reg[reg]
        art.text(word, x + w / 2, y + h / 2, 70, col, "segoeuib.ttf", align="CENTER", valign="CENTER", spacing=1.15, maxw=w - 30)
    # PCB silkscreen: white print on a transparent cell (part numbers, a few designators)
    x, y, w, h = ATLAS.reg["silk"]
    sk = (0.93, 0.93, 0.9)
    for k, (cid, s) in enumerate(CARDS.items()):
        cx = x + (k % 3) * 512
        cy = y + (1 - k // 3) * 128
        art.text(f"{s['brand'].upper()}  {s['model']}", cx + 12, cy + 80, 26, sk, "arialbd.ttf", maxw=488)
        art.text(f"PBA {P.shash(cid) % 900000 + 100000}-00{k + 1}  REV A2   94V-0  E{P.shash(s['sn']) % 90000 + 10000}", cx + 12, cy + 40, 18, sk,
                 "arial.ttf", maxw=488)
    LEGENDS.draw(art)
    x, y, w, h = ATLAS.reg["supercap"]
    art.rect(x + 2, y + 2, w - 4, h - 4, (0.06, 0.06, 0.07))
    art.text("BROADLINE", x + 20, y + h - 42, 30, (0.92, 0.92, 0.94), "segoeuib.ttf")
    art.text("CacheGuard CVP-05  supercap module", x + 20, y + h - 78, 19, (0.8, 0.8, 0.82), "arial.ttf", maxw=w - 40)
    art.text("6.4 V  -  do not short  -  RoHS", x + 20, y + h - 106, 16, (0.65, 0.65, 0.68), "arial.ttf")
    art.code128ish(4405, x + 20, y + 14, 260, 22, (0.85, 0.85, 0.87))
    art.render(ATLAS.file)
    art.dispose()


# ====================================================================== geometry helpers in the card frame

def xz_sheet(name, tag, outline, y0, y1, holes=(), parent=None):
    """A plate in the card plane (x, z), from y0 to y1."""
    return D.sheet(name, tag, (0, (y0 + y1) / 2, 0), X, Z, outline, holes, abs(y1 - y0), parent)


def edge_x_end(lanes):
    return 0.0300 - (LONG_PINS[lanes] - 1) * 0.001 - 0.0045


def pcb_outline(s):
    lanes = s["lanes"]
    x_far = X0 - s["L"]
    xe = edge_x_end(lanes)
    pts = [(x_far, 0.0)]
    if lanes == 16:   # the retention-hook notch beyond an x16 edge
        pts += [(xe - 0.0037, 0.0), (xe - 0.0037, 0.0025), (xe - 0.0007, 0.0025), (xe - 0.0007, 0.0)]
    pts += [(xe, 0.0), (xe, TAB_BOT + 0.0005), (xe + 0.0005, TAB_BOT), (0.0305, TAB_BOT), (0.0310, TAB_BOT + 0.0005),
            (0.0310, -0.0003), (0.0328, -0.0003), (0.0328, TAB_BOT + 0.0005), (0.0333, TAB_BOT), (0.0440, TAB_BOT),
            (0.0445, TAB_BOT + 0.0005), (0.0445, 0.0), (X_PCB_END, 0.0), (X_PCB_END, HP), (x_far + 0.003, HP), (x_far, HP - 0.003)]
    return pts


def fingers(s, root):
    n = LONG_PINS[s["lanes"]]
    xs = [0.0435 - k * 0.001 for k in range(11)] + [0.0300 - k * 0.001 for k in range(n)]
    short = {0, 16, len(xs) - 1}
    for k, x in enumerate(xs):
        z0, z1 = (-0.0052, -0.0024) if k in short else (-0.0052, -0.0012)
        D.box("finger", (x - 0.00036, PCB_Y1, z0), (x + 0.00036, PCB_Y1 + 0.00004, z1), "gold", root)
        D.box("finger", (x - 0.00036, PCB_Y0 - 0.00004, z0), (x + 0.00036, PCB_Y0, z1), "gold", root)


def chip(name, x, z, w, l, h, tag="chip_black", root=None, y=PCB_Y0):
    """A part on the component side: w along x, l along z, h tall (towards -y)."""
    return D.box(name, (x - w / 2, y - h, z - l / 2), (x + w / 2, y, z + l / 2), tag, root)


def heatsink(sk, root, brand_reg):
    """A finned heatsink on the controller: base plate and fins standing off the board (towards -y), running along
    x (the airflow), push pins in two corners, a brand print on the top of the fins."""
    x, z, w, l, h = sk["x"], sk["z"], sk["w"], sk["l"], sk["h"]
    tag = sk["tag"]
    yb = PCB_Y0 - 0.0016                      # the die and pad under the base
    chip("die", x, z, 0.018, 0.018, 0.0012, "chip_black", root)
    D.box("sink_base", (x - w / 2, yb - 0.0020, z - l / 2), (x + w / 2, yb, z + l / 2), tag, root, bevel=0.0004, seg=1)
    n = sk["fins"]
    comb = D.comb_outline(n, l / n, l / n * 0.42, 0.0, h - 0.002, 0.0006)
    P.slab("sink_fins", comb, w, tag, P.Frame((x, yb - 0.0020, z), X, NY), parent=root)
    # a flat top strip across the fins (where the print sits)
    D.box("sink_cap", (x - w / 2, yb - h - 0.0004, z - l * 0.18), (x + w / 2, yb - h + 0.0002, z + l * 0.18), tag, root)
    D.decal("sink_logo", ATLAS, brand_reg, P.Frame((x, yb - h - 0.00045, z), NY, Z), w * 0.86, w * 0.86 / 4, root)
    for (dx, dz) in ((-1, -1), (1, 1)):
        px, pz = x + dx * (w / 2 - 0.0025), z + dz * (l / 2 - 0.0025)
        P.cylinder("push_pin", P.Frame((px, yb - 0.0020, pz), NY, Z), 0.0016, 0.0016, "white_plastic", 10, root, z0=0.0)
        P.cylinder("push_pin_back", P.Frame((px, PCB_Y1, pz), Y, Z), 0.0019, 0.0011, "white_plastic", 10, root, z0=0.0)


# ====================================================================== ports

QSFP_W, QSFP_H = 0.0184, 0.0090


def qsfp_cage(fr, parent, depth=0.052):
    out = D.rect(-QSFP_W / 2, QSFP_W / 2, -QSFP_H / 2, QSFP_H / 2)
    P.slab("qsfp_cage", P.rrect(QSFP_W + 0.0014, QSFP_H + 0.0014, 0.0003), depth, "nickel", fr.sub(0, 0, -depth / 2),
           holes=[out], parent=parent)
    P.slab("qsfp_gasket", P.rrect(QSFP_W + 0.0036, QSFP_H + 0.0036, 0.0005), 0.0006, "steel", fr.sub(0, 0, 0.0003),
           holes=[P.rrect(QSFP_W + 0.0004, QSFP_H + 0.0004, 0.0002)], parent=parent)
    P.slab("qsfp_back", out, 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=parent)
    P.cube("qsfp_conn", (0, -0.0016, -depth + 0.007), (0.0150, 0.0034, 0.012), "black_plastic", fr, parent)
    # the heat-sink clip on the cage top (riding fins over the module)
    for k in range(5):
        P.cube("qsfp_fin", (-0.0072 + k * 0.0036, QSFP_H / 2 + 0.0019, -depth * 0.55), (0.0008, 0.0024, depth * 0.62), "nickel", fr, parent)


def port_specs(s):
    """[(kind, z, y_centre, opening_w (along z), opening_h (along y))] in card coordinates."""
    out = []
    for z in s["ports"]:
        if s["kind"] == "eth":
            out.append(("eth", z, PCB_Y0 - 0.0066, D.RJ45_W + 0.0024, D.RJ45_H + 0.0042))
        elif s["kind"] == "sfp":
            out.append(("sfp", z, PCB_Y0 - 0.0006 - D.SFP_H / 2 - 0.0006, D.SFP_W + 0.0012, D.SFP_H + 0.0012))
        elif s["kind"] == "qsfp":
            out.append(("qsfp", z, PCB_Y0 - 0.0006 - QSFP_H / 2 - 0.0007, QSFP_W + 0.0014, QSFP_H + 0.0014))
    return out


def port_frame(z, yc):
    """The mouth frame of a bracket port: at x = BR_X1, +Z out (+x), +Y away from the board (-y); local x = +z."""
    return P.Frame((BR_X1, yc, z), X, NY)


def led_z(s, n, ow):
    """SFP / QSFP: the LED column beside port n, on the cage's outer side."""
    return s["ports"][n] + (-1 if n == 0 else 1) * (ow / 2 + 0.0028)


def bracket_screws(s):
    ps = port_specs(s)
    if not ps:
        return [(-0.0057, 0.0100), (-0.0057, 0.0480)]
    gap = 0.0068 if s["kind"] in ("sfp", "qsfp") else 0.0042
    z0 = min(p[1] for p in ps) - max(p[3] for p in ps) / 2 - gap
    z1 = max(p[1] for p in ps) + max(p[3] for p in ps) / 2 + gap
    yc = ps[0][2]
    return [(yc, z0), (yc, z1)]


def build_ports(s, root):
    """The cages / jacks / receptacles on the board, their anchors and LEDs."""
    n = 0
    for kind, z, yc, ow, oh in port_specs(s):
        fr = port_frame(z, yc)
        if kind == "eth":
            D.rj45_jack(fr, root, latch_up=True, depth=0.0150)
            D.fbox("rj45_rear", fr, (-ow / 2, -oh / 2 + 0.0004, -0.0215), (ow / 2, oh / 2, -0.0150), "black_plastic", root)
            P.anchor(f"A_PORT_ETH_{n}", fr, (0.0145, 0.012, 0.020), root, meta=f"depth=0.012,rj45=1,latch=+up,speed={s['speed']},port={n + 1}")
            # the two LEDs in the jack face, on the board side corners
            D.led(f"A_LED_LINK_{n}", fr.sub(0.0044, -oh / 2 + 0.0016, 0.0003), 0.0024, 0.0016, "led_green", root, meta="colour=green,fn=link")
            D.led(f"A_LED_ACT_{n}", fr.sub(-0.0044, -oh / 2 + 0.0016, 0.0003), 0.0024, 0.0016, "led_yellow", root, meta="colour=amber,fn=activity")
        else:
            if kind == "sfp":
                D.sfp_cage(fr, root, depth=0.046)
                P.anchor(f"A_PORT_SFP_{n}", fr, (0.0145, 0.0105, 0.050), root,
                         meta=f"depth=0.042,sfp={'sfp28' if s['speed'] == '25g' else 'sfp+'},speed={s['speed']},port={n + 1}")
            else:
                qsfp_cage(fr, root)
                P.anchor(f"A_PORT_QSFP_{n}", fr, (0.0190, 0.0095, 0.056), root, meta=f"depth=0.048,qsfp=qsfp28,speed={s['speed']},port={n + 1}")
            # light pipes in the bracket beside the cage, on its outer side: link nearer the board, activity below
            zl = led_z(s, n, ow)
            for k, (nm, tag, col, fn) in enumerate((("LINK", "led_green", "green", "link"), ("ACT", "led_yellow", "amber", "activity"))):
                lf = P.Frame((BR_X1, yc + (k - 0.5) * 0.0050, zl), X, NY)
                D.led(f"A_LED_{nm}_{n}", lf.sub(0, 0, 0.0003), 0.0018, 0.0022, tag, root, meta=f"colour={col},fn={fn}")
        n += 1
    if s["kind"] == "sas":
        for k, x in enumerate(s["ports"]):
            sas_receptacle(s, k, x, root)


def sas_receptacle(s, k, x, root):
    """An SFF-8654 x8 (SlimSAS 8i) receptacle standing on the board at the top edge, mouth up (+z)."""
    w, d = 0.0265, 0.0088
    zf = HP + 0.0010
    yc = PCB_Y0 - 0.0006 - d / 2
    fr = P.Frame((x, yc, zf), Z, NY)        # local x = ... mouth plane, +Z up
    mouth = P.rrect(w - 0.0030, d - 0.0030, 0.0005)
    P.slab("sas_shell", P.rrect(w, d, 0.0008), 0.0120, "black_plastic", fr.sub(0, 0, -0.0060), holes=[mouth], parent=root)
    P.slab("sas_floor", mouth, 0.0006, "dark_plastic", fr.sub(0, 0, -0.0090), parent=root)
    P.cube("sas_tongue", (0, 0, -0.0055), (w - 0.0060, 0.0011, 0.0060), "black_plastic", fr, root)
    for j in range(17):   # contact rows on the tongue (a gold strip each side)
        xx = -(w - 0.0080) / 2 + j * (w - 0.0080) / 16
        for sy in (-1, 1):
            P.cube("sas_pin", (xx, sy * 0.00062, -0.0058), (0.0003, 0.00012, 0.0045), "gold", fr, root)
    # latch window on the outer face
    P.cube("sas_latch", (0, d / 2 + 0.0002, -0.0040), (0.0060, 0.0006, 0.0030), "dark_plastic", fr, root)
    for sx in (-1, 1):   # board locks
        P.cube("sas_post", (sx * (w / 2 - 0.0012), 0, -0.0130), (0.0016, 0.0050, 0.0030), "nickel", fr, root)
    P.anchor(f"A_PORT_SAS_{k}", fr, (w + 0.003, d + 0.003, 0.014), root,
             meta=f"depth=0.008,conn=sff8654,lanes=8,phys={8 * k}-{8 * k + 7},latch=+up")
    # below the receptacle (its shell reaches 12 mm down from the top edge): the activity LED and the port legend
    D.led(f"A_LED_SAS_{k}", P.Frame((x + 0.0080, PCB_Y0 - 0.0004, HP - 0.0150), NY, Z), 0.0016, 0.0010, "led_green", root,
          meta="colour=green,fn=activity")
    LEGENDS.quad("sas_label", "0-7" if k == 0 else "8-15", P.Frame((x - 0.0030, PCB_Y0 - 0.00005, HP - 0.0150), NY, Z), 0.0026, root)


# ====================================================================== the bracket (card and _lpbracket share it)

def bracket(s, fr, parent, z_tab):
    """A single-slot bracket built in fr = the A_BRACKET_0 pose (x 0.0965, y -0.0069, z 0 of the card; model axes):
    the plate with the port openings and vents, the folded tab with the screw slot, the screws on the cages."""
    fr = fr.sub(0, 0, -BRK[2])     # work in card heights (z = 0 at the slot)

    def q(x, y):           # card (x, y) -> bracket local
        return (x - BRK[0], y - BRK[1])
    yb, yt = BR_YB - BRK[1], BR_YT - BRK[1]
    ytg = (-0.0100 - BRK[1], -0.0040 - BRK[1])
    out = [(yb, -0.0035), (ytg[0], -0.0035), (ytg[0], -0.0120), (ytg[0] + 0.0025, -0.0135), (ytg[1] - 0.0010, -0.0135),
           (ytg[1], -0.0035), (yt, -0.0035), (yt, z_tab - 0.0006), (yb, z_tab - 0.0006)]
    holes = []
    top = 0.006
    for kind, z, yc, ow, oh in port_specs(s):
        cy = yc - BRK[1]
        holes.append(D.rr(cy - oh / 2 - 0.0003, cy + oh / 2 + 0.0003, z - ow / 2 - 0.0003, z + ow / 2 + 0.0003, 0.0005))
        top = max(top, z + ow / 2 + 0.003)
    # LED windows of SFP / QSFP cards
    if s["kind"] in ("sfp", "qsfp"):
        for n, (kind, z, yc, ow, oh) in enumerate(port_specs(s)):
            for k in range(2):
                holes.append(P.rrect(0.0026, 0.0022, 0.0004, yc + (k - 0.5) * 0.0050 - BRK[1], led_z(s, n, ow)))
    sc = bracket_screws(s)
    for (y, z) in sc:
        holes.append(P.circle(0.0012, y - BRK[1], z, 10))
        if s["kind"] != "sas":
            top = max(top, z + 0.0030)
    # vents: two rows of slots above the ports, up to below the tab
    z = top + 0.002
    while z < z_tab - 0.012:
        for yy in (-0.0102, -0.0012):
            if all(abs(z - sz) > 0.0050 for (sy, sz) in sc):
                holes.append(P.rrect(0.0068, 0.0022, 0.0011, yy - BRK[1], z, 3))
        z += 0.0045
    pf = fr.sub(-0.0005, 0, 0, X, Z)          # local x = card y, local y = card z, normal x
    P.slab("bracket", out, 0.0010, "steel", pf, holes=holes, parent=parent)
    # the folded tab with its U slot (open towards +x) and the bend
    tab = [(BR_X0, BR_YB), (0.1065, BR_YB), (0.1065, SLOT_Y0 - 0.0022), (X_SCREW, SLOT_Y0 - 0.0022)]
    tab += [(X_SCREW + 0.0022 * math.cos(math.radians(a)), SLOT_Y0 + 0.0022 * math.sin(math.radians(a))) for a in range(255, 100, -15)]
    tab += [(X_SCREW, SLOT_Y0 + 0.0022), (0.1065, SLOT_Y0 + 0.0022), (0.1065, BR_YT), (BR_X0, BR_YT)]
    tab = [q(x, y) for (x, y) in tab]
    P.slab("bracket_tab", tab, 0.0010, "steel", fr.sub(0, 0, z_tab - 0.0005, Z, Y), parent=parent)
    P.cylinder("bracket_bend", fr.sub(BR_X0 + 0.0002 - BRK[0], (BR_YT + BR_YB) / 2 - BRK[1], z_tab - 0.0008, Y, X), 0.0008,
               BR_YT - BR_YB, "steel", 8, parent)
    # the bracket screws (small pan heads on the outer face)
    for (y, z) in sc:
        P.lathe("bracket_screw", [(0, 0.0011), (0.0014, 0.0010), (0.0019, 0.0004), (0.0019, 0.0), (0, 0.0)], "nickel",
                fr.sub(0.0001, y - BRK[1], z, X, Z), 12, parent)
        P.cube("bracket_screw_slot", (0, 0, 0.0011), (0.0024, 0.0005, 0.0002), "dark_plastic", fr.sub(0.0001, y - BRK[1], z, X, Z), parent)
    # port numbers printed beside the openings
    if s["kind"] in ("eth", "sfp", "qsfp"):
        for k, (kind, z, yc, ow, oh) in enumerate(port_specs(s)):
            LEGENDS.quad("bracket_no", f"P{k + 1}", fr.sub(0.00005, BR_YT - 0.0026 - BRK[1], z, X, Y), 0.0020, parent)
    return sc


def bracket_anchors(s, fr, parent, z_tab, sc):
    fr = fr.sub(0, 0, -BRK[2])
    P.anchor("A_SCREW_PH2_0", fr.sub(X_SCREW - BRK[0], 0, z_tab, Z, X), (0.008, 0.008, 0.008), parent, meta="slot=0")
    for k, (y, z) in enumerate(sc):
        P.anchor(f"A_SCREW_PH1_{k}", fr.sub(0.0011, y - BRK[1], z, X, Y), (0.005, 0.005, 0.004), parent,
                 meta="thread=4-40,holds=bracket")


# ====================================================================== cards

def build_card(cid):
    s = CARDS[cid]
    P.reset()
    textures()
    root = c.root(cid)
    D.ROOT[0] = root
    x_far = X0 - s["L"]
    # board
    xz_sheet("pcb", "pcb_green", pcb_outline(s), PCB_Y0, PCB_Y1, (), root)
    fingers(s, root)
    # silkscreen print on the component side, near the far end / under the heatsink area
    k = list(CARDS).index(cid)
    sx0, sy0, sw, sh = ATLAS.reg["silk"]
    ATLAS.add(f"silk{k}", sx0 + (k % 3) * 512, sy0 + (1 - k // 3) * 128, 512, 128)
    D.decal("silk", ATLAS, f"silk{k}", P.Frame((x_far + 0.040, PCB_Y0 - 0.00005, HP - 0.0090), NY, Z), 0.060, 0.015, root)
    # the label on the back (+y)
    D.decal("label", ATLAS, f"lab{s['lab']}", P.Frame((x_far + 0.045 if s["L"] > 0.14 else x_far + 0.040, PCB_Y1 + 0.00005, 0.032), Y, Z),
            0.048, 0.048 * 192 / 512, root)
    # the controller and its heatsink
    heatsink(s["sink"], root, s["logo"])
    sk = s["sink"]
    # parts: flash, EEPROM, regulators, inductors, crystals, MLCC arrays
    rng = P.shash(cid)
    parts = [(sk["x"] - sk["w"] / 2 - 0.010, 0.050, 0.006, 0.008, 0.0012), (sk["x"] - sk["w"] / 2 - 0.009, 0.014, 0.005, 0.005, 0.0011),
             (x_far + 0.012, 0.048, 0.008, 0.008, 0.0010)]
    for (x, z, w, l, h) in parts:
        chip("ic", x, z, w, l, h, "chip_black", root)
    for j in range(4):   # power stage: inductors
        chip("inductor", x_far + 0.012 + j * 0.008, 0.016, 0.0065, 0.0065, 0.0040, "dark_plastic" if j % 2 else "chip_black", root)
    for j in range(14):
        x = x_far + 0.006 + (j % 7) * 0.0042
        z = 0.030 + (j // 7) * 0.004
        chip("mlcc", x, z, 0.0016, 0.0008, 0.0008, "ceramic", root)
    for j in range(10):
        x = sk["x"] - sk["w"] / 2 + 0.002 + j * (sk["w"] - 0.004) / 9
        chip("mlcc", x, sk["z"] - sk["l"] / 2 - 0.0030, 0.0008, 0.0016, 0.0008, "ceramic", root)
    P.cylinder("crystal", P.Frame((sk["x"] + sk["w"] / 2 + 0.006, PCB_Y0, 0.012), NY, Z), 0.0016, 0.0016, "nickel", 12, root, z0=0.0)
    if s.get("magnetics"):   # 1GbE: a magnetics module behind each jack
        for z in s["ports"]:
            chip("magnetics", 0.067, z, 0.010, 0.012, 0.0045, "black_plastic", root)
    if s["kind"] in ("sfp", "qsfp"):     # the retimers / PHYs behind the cages
        for z in s["ports"]:
            chip("phy", 0.040, z, 0.006, 0.006, 0.0010, "chip_black", root)
    # a few through-hole pins of the cages / jacks on the back side
    for kind, z, yc, ow, oh in port_specs(s):
        for j in range(6):
            D.box("pin_back", (0.060 + j * 0.005, PCB_Y1, z - 0.004), (0.0612 + j * 0.005, PCB_Y1 + 0.0008, z + 0.004), "solder", root)
    build_ports(s, root)
    if s.get("raid"):
        raid_extras(s, root)
    # the full-height bracket: the moving piece of A_BRACKET_0
    bf = P.Frame(BRK, Z, Y)
    a = P.anchor("A_BRACKET_0", bf, (0.011, BR_YT - BR_YB, Z_TAB + 0.0135), root,
                 meta=f"remove=-z,swap={cid}_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full")
    sc = bracket(s, bf, a, Z_TAB)
    bracket_anchors(s, bf, root, Z_TAB, sc)
    # hit boxes as on the GPU: the body, the bracket, the edge
    xe = edge_x_end(s["lanes"])
    yl = min(PCB_Y0 - 0.020, PCB_Y0 - sk["h"] - 0.004)
    P.anchor("A_HIT_0", ((x_far + X_PCB_END) / 2, (yl + PCB_Y1 + 0.0008) / 2, HP / 2), (X_PCB_END - x_far, PCB_Y1 + 0.0008 - yl, HP), root)
    P.anchor("A_HIT_1", ((BR_X0 + 0.1065) / 2, (BR_YT + BR_YB) / 2, (Z_TAB - 0.0135) / 2), (0.1065 - BR_X0, BR_YT - BR_YB, Z_TAB + 0.0135), root)
    P.anchor("A_HIT_2", ((0.0445 + xe) / 2, (PCB_Y0 + PCB_Y1) / 2, -0.0028), (0.0445 - xe, 0.003, 0.0060), root)
    extra = (f"frame: card (GPU frame), PCIe x{s['lanes']} edge {0.0445 - xe:.4f} m (x {xe:.4f}..0.0445), board {s['L']:.4f} x {HP + 0.0055:.4f}, "
             f"low-profile board with a full-height bracket")
    return D.finish(root, cid, preview_views=((35, -40), (-40, 50)), beauty_views=((30, -35), (-35, 45)), size=(1000, 700), samples=40,
                    extra=extra, more_beauty=[(((75, 10),), dict(target=(0.09, -0.008, 0.035), dist=0.16))])


def raid_extras(s, root):
    """The 9560's cache module (a daughter board on two stacking connectors), the supercap connector and the pack
    on its cable (the moving piece of A_SUPERCAP_0)."""
    x_far = X0 - s["L"]
    # cache module: a small green board with 4 DRAM chips, standing 5 mm off the main board
    mx, mz = x_far + 0.030, 0.027
    for dz in (-0.010, 0.010):
        chip("cache_conn", mx, mz + dz, 0.026, 0.005, 0.0050, "black_plastic", root)
    D.box("cache_pcb", (mx - 0.022, PCB_Y0 - 0.0066, mz - 0.019), (mx + 0.022, PCB_Y0 - 0.0050, mz + 0.019), "pcb_green", root)
    for j in range(4):
        chip("dram", mx - 0.015 + j * 0.010, mz + 0.004, 0.008, 0.012, 0.0010, "chip_black", root, y=PCB_Y0 - 0.0066)
    chip("cache_ctrl", mx, mz - 0.012, 0.010, 0.006, 0.0010, "chip_black", root, y=PCB_Y0 - 0.0066)
    # the supercap connector at the top edge
    cx = x_far + 0.012
    chip("cap_header", cx, HP - 0.0045, 0.0080, 0.0050, 0.0055, "white_plastic", root)
    fr = P.Frame((cx, PCB_Y0 - 0.0028, HP - 0.0020), Z, NY)
    P.anchor("A_PORT_SUPERCAP_0", fr, (0.009, 0.006, 0.006), root, meta="depth=0.004,pins=6,plug=supercap")
    # the pack lies off the card's far end, its cable runs from the header
    a = P.anchor("A_SUPERCAP_0", P.Frame((x_far - 0.050, -0.0060, 0.026), Z, Y), (0.046, 0.010, 0.046), root,
                 meta="kind=supercap,cable=A_PORT_SUPERCAP_0,len=0.45,mount=chassis_clip,free=1")
    px, pz = x_far - 0.050, 0.026
    D.box("cap_case", (px - 0.0230, -0.0100, pz - 0.0225), (px + 0.0230, -0.0020, pz + 0.0225), "black_plastic", a, bevel=0.0012, seg=2)
    D.decal("cap_label", ATLAS, "supercap", P.Frame((px, -0.00195, pz), Y, Z), 0.040, 0.0125, a)
    D.box("cap_clip", (px - 0.020, -0.0110, pz - 0.0030), (px + 0.020, -0.0100, pz + 0.0030), "dark_plastic", a)
    path = P.smooth_path([(cx, PCB_Y0 - 0.0030, HP + 0.0020), (cx - 0.004, PCB_Y0 - 0.0040, HP + 0.0090), (x_far - 0.010, -0.0070, HP + 0.006),
                          (px + 0.010, -0.0062, pz + 0.035), (px + 0.004, -0.0060, pz + 0.0225)], 5)
    P.tube("cap_cable", path, 0.0012, "black_plastic", a, 6)
    P.tube("cap_cable", [(v[0] + 0.0012, v[1], v[2]) for v in path], 0.0012, "black_plastic", a, 6)


def build_lpbracket(cid):
    """<id>_lpbracket: the low-profile bracket of a card, loose. Frame = the card's A_BRACKET_0 pose."""
    s = CARDS[cid]
    P.reset()
    textures()
    mid = cid + "_lpbracket"
    root = c.root(mid)
    D.ROOT[0] = root
    fr = P.Frame((0, 0, 0), Z, Y)
    sc = bracket(s, fr, root, Z_TAB_LP)
    bracket_anchors(s, fr, root, Z_TAB_LP, sc)
    P.anchor("A_HIT_0", ((BR_X0 - 0.0005 + 0.1065) / 2 - BRK[0], (BR_YT + BR_YB) / 2 - BRK[1], (Z_TAB_LP - 0.0135) / 2 - BRK[2]),
             (0.1065 - BR_X0, BR_YT - BR_YB, Z_TAB_LP + 0.0135), root)
    extra = (f"frame: {cid}'s A_BRACKET_0 pose (card x {BRK[0]}, y {BRK[1]}, z {BRK[2]}); tab z={Z_TAB_LP}, "
             f"screw slot at card (x {X_SCREW}, y {SLOT_Y0})")
    return D.finish(root, mid, preview_views=((70, 15), (-110, 20)), beauty_views=((60, 12),), size=(1000, 560), samples=32, extra=extra)
