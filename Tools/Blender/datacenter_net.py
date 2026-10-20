"""
switch_24 (a 1U 24-port gigabit switch with 4 SFP+ uplinks, "LINKWAVE LS-2804X") and patch_panel_24 (a 1U 24-port
Cat6 keystone patch panel with a numbered label strip and a rear cable bar).

Rack device frame (datacenter_common): origin at the centre of the front mounting plane at the bottom of the U, +Z
out of the front; the ears sit on the rack rails (z 0..0.002), A_SCREW_RACK_n at their holes.

switch_24: A_PORT_ETH_0..23 (port n+1; odd numbers on the top row with the latch up, even numbers below with the
latch down: each anchor's +Y points at its latch), each with A_LED_LINK_n (green) and A_LED_ACT_n (amber);
A_PORT_SFP_0..3 (ports 25-28) with A_LED_SFP_n; the console port A_PORT_CONSOLE_0 (RJ45); status LEDs
A_LED_POWER_0, A_LED_SYS_0, A_LED_FAN_0; the rear C14 inlet A_PORT_C14_0.
patch_panel_24: front A_PORT_ETH_0..23 (keystone jacks, latch down), rear A_PUNCH_0..23 (the 110 IDC block on the
back of each keystone, +Z towards the rear where the punch-down tool comes from).
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

ATLAS = D.Atlas("net_print", 2048, 1024)
ATLAS.add("labels", 0, 512, 1024, 512)
ATLAS.add("logo", 1024, 896, 512, 128)
ATLAS.add("rating", 1024, 512, 512, 360)
ATLAS.add("strip", 0, 440, 2048, 48)
ATLAS.add("idc", 1536, 768, 256, 128)
ATLAS.add("panel_logo", 1536, 896, 512, 128)
ATLAS.add("pins", 1792, 768, 256, 128)
LABELS = D.Labels(ATLAS, "labels", 128, 32, [str(k) for k in range(1, 29)] + ["CONSOLE", "SFP+ 10G", "PWR", "SYS", "FAN",
                  "RESET", "LINK/ACT", "100-240V~ 1A", "1G", "MGMT"], size=0.6)

H1 = 0.0436
YB = (D.U - H1) / 2
YT = YB + H1


# ====================================================================== artwork

def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=None, name="net_print")
    LABELS.draw(art)
    x, y, w, h = ATLAS.reg["logo"]
    art.rect(x, y, w, h, (0.10, 0.11, 0.12))
    art.text("LINKWAVE", x + 24, y + 74, 54, (0.92, 0.93, 0.95), "segoeuib.ttf", spacing=1.1)
    art.text("LS-2804X  24G + 4 SFP+", x + 26, y + 28, 26, (0.35, 0.75, 0.95), "arialbd.ttf")
    x, y, w, h = ATLAS.reg["panel_logo"]
    art.rect(x, y, w, h, (0.035, 0.035, 0.04))
    art.text("CAT 6", x + w / 2, y + 82, 50, (0.92, 0.93, 0.95), "ariblk.ttf", align="CENTER")
    art.text("LINKWAVE  24-PORT KEYSTONE", x + w / 2, y + 28, 24, (0.7, 0.72, 0.75), "arialbd.ttf", align="CENTER")
    x, y, w, h = ATLAS.reg["rating"]
    ink = (0.08, 0.08, 0.09)
    art.rect(x, y, w, h, (0.94, 0.94, 0.93))
    art.text("LINKWAVE", x + 18, y + h - 44, 34, ink, "segoeuib.ttf")
    lines = ["Model: LS-2804X", "24 x 10/100/1000BASE-T + 4 x 10G SFP+", "Input: 100-240V~ 50/60Hz 1.0A",
             "MAC: 5C:A1:F0:2B:44:7E", "S/N: LW28X2610C0193", "Class A ITE. Made in Taiwan."]
    for k, s in enumerate(lines):
        art.text(s, x + 18, y + h - 90 - k * 34, 22, ink, "arial.ttf", maxw=w - 36)
    art.code128ish(2804, x + 18, y + 12, 300, 42, ink)
    art.text("CE  FC  ♻", x + 340, y + 30, 28, ink, "seguisym.ttf")
    # patch panel strip: white, numbers 1..24 at the real port positions (filled in by strip_texture)
    x, y, w, h = ATLAS.reg["idc"]
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    cols = [(0.95, 0.5, 0.1), (0.1, 0.55, 0.15), (0.1, 0.3, 0.8), (0.45, 0.25, 0.1)]
    for k in range(8):
        cc = cols[[0, 0, 1, 2, 2, 1, 3, 3][k]]
        art.rect(x + 8 + k * 30, y + 64, 26, 54, cc if k % 2 else (0.96, 0.96, 0.95))
        art.rect(x + 8 + k * 30, y + 64, 26, 10, cc)
        art.rect(x + 8 + k * 30, y + 108, 26, 10, cc)
    for k in range(8):   # the IDC slots under the colour code
        art.rect(x + 19 + k * 30, y + 30, 4, 34, (0.05, 0.05, 0.06))
    art.text("T568B", x + w / 2, y + 12, 18, ink, "arialbd.ttf", align="CENTER")
    x, y, w, h = ATLAS.reg["pins"]   # 8 gold contacts seen inside a jack
    art.rect(x, y, w, h, (0.03, 0.03, 0.035))
    for k in range(8):
        art.rect(x + 16 + k * 29, y + 8, 12, h - 16, (0.88, 0.7, 0.32))
    strip_texture(art)
    art.render(ATLAS.file)
    art.dispose()


PP_PITCH = 0.0165
PP_GAP = 0.0080


def pp_port_x():
    xs = []
    total = 24 * PP_PITCH + 3 * PP_GAP
    x = total / 2 - PP_PITCH / 2
    for k in range(24):     # port 1 at +x (the viewer's left)
        xs.append(x)
        x -= PP_PITCH + (PP_GAP if k % 6 == 5 else 0.0)
    return xs


STRIP_X0, STRIP_X1 = -0.215, 0.215


def strip_texture(art):
    x, y, w, h = ATLAS.reg["strip"]
    art.rect(x, y, w, h, (0.95, 0.95, 0.94))
    for k, px in enumerate(pp_port_x()):
        u = (STRIP_X1 - px) / (STRIP_X1 - STRIP_X0)      # front decal: +x on the viewer's left
        art.text(str(k + 1), x + u * w, y + h / 2, h * 0.62, (0.05, 0.05, 0.06), "arialbd.ttf", align="CENTER", valign="CENTER")
        if k % 6 == 0 and k:
            gx = x + (STRIP_X1 - (px + PP_PITCH / 2 + PP_GAP / 2)) / (STRIP_X1 - STRIP_X0) * w
            art.rect(gx - 1, y + 4, 2, h - 8, (0.6, 0.6, 0.6))


# ====================================================================== switch

def rj45_bank(fr, cols, rows, px, py, parent, latch_by_row):
    """A ganged RJ45 jack block (cols x rows) behind a panel cut-out, its face at fr (mouth plane, +Z out).
    Returns [(col, row, local_x, local_y)]. Row 0 is the bottom row."""
    w, h = D.RJ45_W, D.RJ45_H
    ports = []
    holes = []
    for r in range(rows):
        for k in range(cols):
            lx = (k - (cols - 1) / 2) * px
            ly = (r - (rows - 1) / 2) * py
            holes.append(D.rj45_outline(lx, ly, latch_by_row[r]))
            ports.append((k, r, lx, ly))
    bw, bh = cols * px + 0.0016, rows * py + 0.0010
    depth = 0.016
    P.slab("rj45_bank", P.rrect(bw, bh, 0.0006), depth, "black_plastic", fr.sub(0, 0, -depth / 2 - 0.0002), holes=holes, parent=parent)
    P.slab("rj45_floor", P.rrect(bw - 0.001, bh - 0.001, 0.0004), 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=parent)
    # the metal shield round the block
    P.slab("rj45_shield", P.rrect(bw + 0.0014, bh + 0.0014, 0.0008), 0.0004, "nickel", fr.sub(0, 0, 0.0001),
           holes=[P.rrect(bw - 0.0002, bh - 0.0002, 0.0004)], parent=parent)
    for (k, r, lx, ly) in ports:
        up = latch_by_row[r]
        s = -1 if up else 1
        cf = P.Frame(fr.p(lx, ly + s * (h / 2 - 0.0009), -depth * 0.5), fr.v, fr.w)
        P.slab("rj45_pins", D.comb_outline(8, 0.00102, 0.00042, -0.0045, 0.0050, 0.0012), 0.0003, "gold", cf, parent=parent)
    return ports


def build_switch():
    P.reset()
    textures()
    root = c.root("switch_24")
    D.ROOT[0] = root
    ZF = 0.0045          # the front panel's face
    ZR = ZF - 0.250      # the rear face
    BW = 0.440
    # chassis: a U-shaped base (bottom + sides) and a top cover with its own sides overlapping
    D.box("base", (-BW / 2, YB, ZR), (BW / 2, YB + 0.0010, ZF - 0.0015), "steel", root)
    for sx in (-1, 1):
        xo = sx * BW / 2
        slots = [D.rect(-0.150 + k * 0.012, -0.144 + k * 0.012, YB + 0.010, YT - 0.012) for k in range(10)]
        D.xslab("side", "steel", D.rect(ZR, ZF - 0.0015, YB, YT - 0.0010), xo - sx * 0.0010, xo, slots, root)
        D.xslab("side_vent_dark", "dark_plastic", D.rect(-0.152, -0.030, YB + 0.008, YT - 0.010), xo - sx * 0.006, xo - sx * 0.0055, (), root)
    D.box("top", (-BW / 2, YT - 0.0010, ZR), (BW / 2, YT, ZF - 0.0015), "steel", root)
    D.decal("rating", ATLAS, "rating", P.Frame((0.10, YT + 0.00005, ZR + 0.08), Y, NZ), 0.090, 0.0633, root)
    # front panel with the cut-outs; ears
    pitch_x, pitch_y = 0.0142, 0.0170
    groups = [(0.1045, 6), (0.0145, 6)]     # bank centres (x) and their column counts
    rows_y = (YB + 0.0137, YB + 0.0307)
    yc = (rows_y[0] + rows_y[1]) / 2
    sfp_x = [-0.0680, -0.0845]
    sfp_y = [YB + 0.0137, YB + 0.0307]
    con = (-0.1150, YB + 0.0137)
    holes = []
    for gx, ncol in groups:
        bw, bh = ncol * pitch_x + 0.0016, 2 * pitch_y + 0.0010
        holes.append(D.rect(gx - bw / 2, gx + bw / 2, yc - bh / 2, yc + bh / 2))
    for x in sfp_x:
        for y in sfp_y:
            holes.append(D.rect(x - D.SFP_W / 2 - 0.0006, x + D.SFP_W / 2 + 0.0006, y - D.SFP_H / 2 - 0.0006, y + D.SFP_H / 2 + 0.0006))
    holes.append(D.rect(con[0] - D.RJ45_W / 2 - 0.0012, con[0] + D.RJ45_W / 2 + 0.0012, con[1] - D.RJ45_H / 2 - 0.0020, con[1] + D.RJ45_H / 2 + 0.0020))
    holes.append(P.circle(0.0011, -0.1150, YB + 0.0315, 10))     # reset pinhole
    vents = [D.rect(-0.200 + k * 0.006, -0.197 + k * 0.006, YB + 0.008, YT - 0.008) for k in range(10)]
    D.zslab("front", "paint_black", D.rect(-BW / 2, BW / 2, YB + 0.0002, YT - 0.0002), ZF - 0.0015, ZF, holes + vents, root)
    D.zslab("front_vent_dark", "dark_plastic", D.rect(-0.202, -0.1365, YB + 0.006, YT - 0.006), ZF - 0.010, ZF - 0.009, (), root)
    D.ears(root, 1, ZF, "paint_black", body_w=BW, slots=[D.HOLES_IN_U[0], D.HOLES_IN_U[2]])
    # RJ45 banks: port numbers 1.. from +x; odd on top (latch up), even below (latch down)
    n_port = 0
    for gx, ncol in groups:
        ports = rj45_bank(P.Frame((gx, yc, ZF), Z, Y), ncol, 2, pitch_x, pitch_y, root, latch_by_row=(False, True))
        for k in range(ncol):
            lx = (ncol - 1) / 2 * pitch_x - k * pitch_x          # columns from +x
            for r, top in ((1, True), (0, False)):
                pnum = n_port + 2 * k + (0 if top else 1)        # 0-based: top = odd numbers (1, 3, ...)
                px, py = gx + lx, rows_y[r]
                up = (0, 1, 0) if top else (0, -1, 0)
                P.anchor(f"A_PORT_ETH_{pnum}", P.Frame((px, py, ZF), Z, up), (0.0142, 0.0125, 0.020), root,
                         meta=f"depth=0.012,rj45=1,latch=+up,port={pnum + 1},speed=1g")
                ly = py + (D.RJ45_H / 2 + 0.0012) * (1 if top else -1)
                D.led(f"A_LED_LINK_{pnum}", P.Frame((px + 0.0045, ly, ZF + 0.0003), Z, Y), 0.0020, 0.0011, "led_green", root,
                      meta="colour=green,fn=link")
                D.led(f"A_LED_ACT_{pnum}", P.Frame((px - 0.0045, ly, ZF + 0.0003), Z, Y), 0.0020, 0.0011, "led_yellow", root,
                      meta="colour=amber,fn=activity")
                LABELS.quad("port_no", str(pnum + 1), P.Frame((px, py + (0.0085 if top else -0.0085), ZF + 0.00005), Z, Y), 0.0024, root)
        n_port += 2 * ncol
    # SFP+ cages: ports 25-28 (top first)
    k = 0
    for x in sfp_x:
        for y in reversed(sfp_y):
            fr = P.Frame((x, y, ZF), Z, Y)
            D.sfp_cage(fr, root, depth=0.046)
            P.anchor(f"A_PORT_SFP_{k}", fr, (0.0145, 0.0105, 0.05), root, meta=f"depth=0.042,sfp=sfp+,speed=10g,port={25 + k}")
            ly = y + (D.SFP_H / 2 + 0.0016) * (1 if y > yc else -1)
            D.led(f"A_LED_SFP_{k}", P.Frame((x, ly, ZF + 0.0003), Z, Y), 0.0030, 0.0010, "led_green", root, meta="colour=green,fn=link")
            k += 1
    LABELS.quad("sfp_label", "SFP+ 10G", P.Frame(((sfp_x[0] + sfp_x[1]) / 2, YT - 0.0028, ZF + 0.00005), Z, Y), 0.0024, root)
    # console: an RJ45 with a light-blue surround
    cf = P.Frame((con[0], con[1], ZF), Z, Y)
    D.rj45_jack(cf, root, latch_up=True)
    P.slab("console_ring", P.rrect(D.RJ45_W + 0.0034, D.RJ45_H + 0.0050, 0.0008), 0.0004, P.PALETTE_TAG, cf.sub(0, 0.0005, 0.0001),
           holes=[P.rrect(D.RJ45_W + 0.0018, D.RJ45_H + 0.0040, 0.0004)], parent=root, uv_solid=P.pal("lightblue"))
    P.anchor("A_PORT_CONSOLE_0", cf, (0.0145, 0.012, 0.02), root, meta="depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200")
    LABELS.quad("console_label", "CONSOLE", P.Frame((con[0], YT - 0.0028, ZF + 0.00005), Z, Y), 0.0024, root)
    LABELS.quad("reset_label", "RESET", P.Frame((con[0] - 0.009, YB + 0.0315, ZF + 0.00005), Z, Y), 0.0020, root)
    # logo plate and status LEDs at +x (the viewer's left)
    D.decal("logo", ATLAS, "logo", P.Frame((0.1855, YB + 0.0300, ZF + 0.00005), Z, Y), 0.040, 0.010, root)
    for k, (nm, tag, lab) in enumerate((("POWER", "led_green", "PWR"), ("SYS", "led_green", "SYS"), ("FAN", "led_yellow", "FAN"))):
        lx = 0.1985 - k * 0.0125
        D.led(f"A_LED_{nm}_0", P.Frame((lx, YB + 0.0130, ZF + 0.0003), Z, Y), 0.0026, 0.0026, tag, root, round_=True,
              meta=f"colour={'green' if 'green' in tag else 'amber'},fn={nm.lower()}")
        LABELS.quad("led_label", lab, P.Frame((lx, YB + 0.0085, ZF + 0.00005), Z, Y), 0.0022, root)
    # rear: C14 inlet, two fan grilles, the earth screw
    rf = P.Frame((-0.150, YB + 0.0220, ZR), NZ, Y)
    D.zslab("rear", "steel", D.rect(-BW / 2, BW / 2, YB + 0.0002, YT - 0.0002), ZR - 0.0010, ZR,
            [D.c14_outline(-0.150, YB + 0.0220)] + [hh for fx in (0.040, 0.120) for hh in P.hex_grid(
                lambda a, b, r, fx=fx: (a - fx) ** 2 + (b - (YB + 0.0218)) ** 2 < 0.0175 ** 2, 0.0062, 0.0026, fx - 0.02, fx + 0.02, YB + 0.002, YB + 0.042)],
            root)
    D.c14_inlet(rf, root, depth=0.011)
    P.anchor("A_PORT_C14_0", rf, (0.028, 0.020, 0.012), root, meta="depth=0.008,plug=c13,inlet=c14")
    LABELS.quad("rear_label", "100-240V~ 1A", P.Frame((-0.150, YB + 0.0365, ZR - 0.00005), NZ, Y), 0.0026, root)
    for fx in (0.040, 0.120):
        a = P.anchor(f"A_FAN_{0 if fx < 0.1 else 1}", P.Frame((fx, YB + 0.0218, ZR + 0.016), NZ, Y), (0.04, 0.04, 0.02), root,
                     meta="axis=z,spin=1,rpm=6000")
        D.server_fan(a, 0.040, 0.020, blades=5, parent=root, segs=14)
    P.cylinder("earth_screw", P.Frame((-0.190, YB + 0.0200, ZR - 0.001), NZ, Y), 0.0030, 0.0025, "nickel", 8, root, z0=0.0)
    # the hitbox
    P.anchor("A_HIT_0", (0, (YB + YT) / 2, (ZF + ZR) / 2), (BW, H1, ZF - ZR), root)
    P.anchor("A_HIT_1", (0, (YB + YT) / 2, 0.001), (D.EAR_W, H1, 0.004), root)
    return D.finish(root, "switch_24", preview_views=((22, 15), (160, 20)), beauty_views=((18, 12), (155, 15)), size=(1100, 650), samples=36,
                    extra=f"frame: rack device, 1U, body 0.440 x {H1} x 0.250, front z={ZF}, rear z={ZR:.4f}",
                    more_beauty=[(((-12, 6),), dict(target=(0.05, YB + 0.022, ZF), dist=0.30)),
                                 (((-15, 6),), dict(target=(-0.09, YB + 0.022, ZF), dist=0.20))])


# ====================================================================== patch panel

def keystone(fr, root, a_name, port, punch_name):
    """A Cat6 keystone jack seen from the front (face fr at its mouth plane, +Z out; latch down) with its body and
    the 110 IDC block behind the panel."""
    kw, kh = 0.0145, 0.0192
    mouth = D.rj45_outline(0, 0.0012, latch_up=False)
    P.slab("ks_face", P.rrect(kw, kh, 0.0012, seg=1), 0.0018, "black_plastic", fr.sub(0, 0, -0.0009), holes=[mouth], parent=root)
    P.slab("ks_cavity", P.rrect(D.RJ45_W + 0.0012, D.RJ45_H + 0.0028, 0.0005, 0, 0.0002, seg=1), 0.014, "black_plastic", fr.sub(0, 0, -0.0018 - 0.007),
           holes=[mouth], parent=root)
    P.slab("ks_floor", P.rrect(D.RJ45_W + 0.001, D.RJ45_H + 0.003, 0.0004, 0, 0.0002, seg=1), 0.0006, "dark_plastic", fr.sub(0, 0, -0.0160), parent=root)
    # the 8 contacts: a printed quad on the cavity's upper wall (cheap, and the game has 24 of them)
    cf = P.Frame(fr.p(0, 0.0012 + D.RJ45_H / 2 - 0.00005, -0.0075), fr.v * -1, fr.w * -1)
    P.quad("ks_pins", cf, 0.0090, 0.0090, ATLAS.tag, root, uv=ATLAS.uv("pins"))
    # the body behind the panel, and the IDC block
    D.fbox("ks_body", fr, (-kw / 2 + 0.0005, -kh / 2 + 0.0008, -0.030), (kw / 2 - 0.0005, kh / 2 - 0.0008, -0.0018), "black_plastic", root)
    D.fbox("ks_idc", fr, (-kw / 2 + 0.0005, -0.0075, -0.040), (kw / 2 - 0.0005, 0.0075, -0.030), "white_plastic", root)
    bf = P.Frame(fr.p(0, 0, -0.04005), fr.w * -1, fr.v)
    P.quad("ks_code", bf, kw - 0.0016, (kw - 0.0016) / 2, ATLAS.tag, root, uv=ATLAS.uv("idc"))
    P.anchor(a_name, P.Frame(fr.p(0, 0.0012, 0), fr.w, fr.v * -1), (0.0142, 0.0125, 0.02), root,
             meta=f"depth=0.012,rj45=1,latch=+up,port={port},cat=6")
    P.anchor(punch_name, P.Frame(fr.p(0, 0, -0.040), fr.w * -1, fr.v), (0.014, 0.015, 0.012), root,
             meta=f"idc=110,wires=8,scheme=T568B,port={port}")


def build_patch():
    P.reset()
    textures()
    root = c.root("patch_panel_24")
    D.ROOT[0] = root
    ZF = 0.0020        # the panel's face (it is its own pair of ears)
    xs = pp_port_x()
    py = YB + 0.0190
    kw, kh = 0.0145, 0.0192
    holes = [P.rrect(kw + 0.0004, kh + 0.0004, 0.0013, x, py, seg=1) for x in xs]
    for sx in (-1, 1):
        holes += [P.stadium(0.0100, 0.0068, sx * D.HOLE_X, y) for y in (D.HOLES_IN_U[0], D.HOLES_IN_U[2])]
    D.zslab("panel", "paint_black", D.rr(-D.EAR_W / 2, D.EAR_W / 2, YB + 0.0002, YT - 0.0002, 0.0015), 0.0, ZF, holes, root)
    # top and bottom flanges bent back (stiffness), and the side returns
    for (ya, yb_) in ((YB + 0.0002, YB + 0.0017), (YT - 0.0017, YT - 0.0002)):
        D.box("flange", (-0.216, ya, -0.030), (0.216, yb_, 0.0), "paint_black", root)
    for sx in (-1, 1):
        D.box("return", (min(sx * 0.216, sx * 0.2175), YB + 0.0002, -0.030), (max(sx * 0.216, sx * 0.2175), YT - 0.0002, 0.0), "paint_black", root)
    for k, sx in enumerate((-1, 1)):
        for j, y in enumerate((D.HOLES_IN_U[0], D.HOLES_IN_U[2])):
            P.anchor(f"A_SCREW_RACK_{2 * k + j}", P.Frame((sx * D.HOLE_X, y, ZF), Z, Y), (0.012, 0.010, 0.006),
                     root, meta=f"thread=M6,cage=1,side={'r' if sx > 0 else 'l'}")
    # keystones
    for k, x in enumerate(xs):
        keystone(P.Frame((x, py, ZF + 0.0006), Z, Y), root, f"A_PORT_ETH_{k}", k + 1, f"A_PUNCH_{k}")
    # the numbered label strip above the ports under a clear cover, and the panel print
    sy = YT - 0.0048
    D.zslab("strip_holder", "black_plastic", D.rect(STRIP_X0 - 0.002, STRIP_X1 + 0.002, sy - 0.0040, sy + 0.0040), ZF, ZF + 0.0008, (), root)
    D.decal("strip", ATLAS, "strip", P.Frame((0.0, sy, ZF + 0.00085), Z, Y), STRIP_X1 - STRIP_X0, 0.0060, root)
    D.zslab("strip_cover", "clear_plastic", D.rect(STRIP_X0 - 0.0015, STRIP_X1 + 0.0015, sy - 0.0035, sy + 0.0035), ZF + 0.0009, ZF + 0.0013, (), root)
    D.decal("panel_logo", ATLAS, "panel_logo", P.Frame((0.0, YB + 0.0050, ZF + 0.00005), Z, Y), 0.0240, 0.0060, root)
    # the rear cable management bar on two brackets
    zb = -0.110
    for sx in (-1, 1):
        D.xslab("bar_bracket", "steel", [(-0.0005, YB + 0.0020), (-0.0005, YB + 0.0150), (zb + 0.010, YB + 0.0080), (zb, YB + 0.0080), (zb, YB + 0.0020)],
                sx * 0.2120, sx * 0.2140, (), root)
    P.cylinder("cable_bar", P.Frame((0.0, YB + 0.0050, zb + 0.004), X, Y), 0.0030, 0.428, "steel", 10, root)
    for k in range(13):
        x = -0.198 + k * 0.033
        P.lathe("bar_tie_mount", [(0.0, -0.002), (0.0045, -0.002), (0.0045, 0.002), (0.0, 0.002)], "black_plastic",
                P.Frame((x, YB + 0.0050, zb + 0.004), X, Y), 10, root)
    P.anchor("A_BAR_0", P.Frame((0.0, YB + 0.0050, zb + 0.004), NZ, Y), (0.43, 0.012, 0.012), root, meta="ties=13,pitch=0.033")
    P.anchor("A_HIT_0", (0, (YB + YT) / 2, -0.012), (D.EAR_W, H1, 0.032), root)
    P.anchor("A_HIT_1", (0, YB + 0.006, (zb - 0.010) / 2), (0.43, 0.012, -zb + 0.010), root)
    clear = ("#clear_plastic",)   # the renders have no glass shader for it: leave the cover out so the strip shows
    return D.finish(root, "patch_panel_24", preview_views=((20, 12), (160, 25)), beauty_views=((18, 10), (155, 25)), size=(1100, 650), samples=36,
                    extra=f"frame: rack device, 1U panel (its own ears), face z={ZF}, keystones z={ZF + 0.0006}", beauty_kw=dict(hide=clear),
                    more_beauty=[(((-12, 6),), dict(target=(0.15, YB + 0.022, ZF), dist=0.22, hide=clear)),
                                 (((170, 30),), dict(target=(0.10, YB + 0.02, -0.04), dist=0.30, hide=clear))])
