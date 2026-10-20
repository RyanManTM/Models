"""
Power: ups_2u (an AMPERE 2200 VA rack UPS), ups_tower (an AMPERE 1500 VA tower UPS for the basement), pdu_0u (a
vertical zero-U PDU, 24 x C13 + 4 x C19) and pdu_1u (a 1U horizontal PDU, 8 x C13 with a lit switch).

ups_2u: the rack device frame (datacenter_common). Front: the display module at +x (the viewer's left) with the LCD
A_SCREEN_0, A_BUTTON_POWER_0, the menu buttons A_BUTTON_UP_0 / DOWN_0 / ENTER_0 and the LEDs A_LED_ONLINE_0,
A_LED_BATTERY_0, A_LED_FAULT_0; the removable bezel A_BEZEL_0 over the battery pack A_BATTERY_0 (pull=+z). Rear:
outlets A_PORT_C13_0..7 in two groups, the C20 inlet A_PORT_C20_0, A_PORT_USBB_0, A_PORT_SERIAL_0 (RJ45), the input
breaker A_BUTTON_BREAKER_0, the management card slot, a fan. Ears with A_SCREW_RACK_0..3.
ups_tower: origin at the floor, at the centre of the footprint, +Z the front. The same front controls on a sloped
top panel, the front bezel A_BEZEL_0 over the battery A_BATTERY_0; rear outlets A_PORT_NEMA515_0..7 (US
receptacles, for the PC power cords), the attached input cord A_CORD_0, A_PORT_USBB_0, the breaker, a fan.
pdu_0u: origin at the centre of the bottom end of the body; +Y along the body; +Z is the outlet face (in the rack the
outlets face the rear door, see A_PDU_n). Outlets A_PORT_C13_0..23 and A_PORT_C19_0..3 in three banks, the
breakers A_SWITCH_BREAKER_0..1, the input cord A_CORD_0 from the bottom end, two mounting buttons on the back.
pdu_1u: the rack device frame; 8 x C13 A_PORT_C13_0..7 on the front, the lit rocker A_SWITCH_POWER_0 (with
A_LED_SWITCH_0@A_SWITCH_POWER_0), the input cord A_CORD_0 at the rear, ears.
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

ATLAS = D.Atlas("power_print", 2048, 1024)
ATLAS.add("labels", 0, 512, 1024, 512)
ATLAS.add("bezel_logo", 1024, 896, 512, 128)
ATLAS.add("rating_ups", 1024, 512, 512, 360)
ATLAS.add("rating_pdu", 1536, 512, 512, 360)
ATLAS.add("tower_logo", 1536, 896, 512, 128)
ATLAS.add("pdu_logo", 0, 384, 512, 96)
ATLAS.add("lcd_frame", 512, 384, 256, 96)
LABELS = D.Labels(ATLAS, "labels", 128, 32, [str(k) for k in range(1, 25)] + [
    "C19-1", "C19-2", "C19-3", "C19-4", "BANK A", "BANK B", "BANK C", "INPUT", "OUTPUT", "GROUP 1", "GROUP 2",
    "USB", "SERIAL", "NMC", "BATTERY", "BREAKER", "ONLINE", "ON BATT", "FAULT", "ENTER", "200-240V~", "100-127V~",
    "16A", "OUTLETS", "SURGE ONLY", "BATT + SURGE", "I", "O", "15A", "30A"], size=0.58)


def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=None, name="power_print")
    LABELS.draw(art)
    ink = (0.08, 0.08, 0.09)
    for reg, sub in (("bezel_logo", "SMART 2200 RM"), ("tower_logo", "SMART 1500")):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.09, 0.09, 0.1))
        art.text("AMPERE", x + 22, y + 68, 56, (0.93, 0.93, 0.95), "segoeuib.ttf", spacing=1.15)
        art.text(sub, x + w - 22, y + 24, 26, (0.95, 0.62, 0.12), "arialbd.ttf", align="RIGHT")
    x, y, w, h = ATLAS.reg["pdu_logo"]
    art.rect(x, y, w, h, (0.07, 0.07, 0.08))
    art.text("AMPERE", x + 20, y + 50, 46, (0.93, 0.93, 0.95), "segoeuib.ttf")
    art.text("METERED PDU  30A", x + w - 20, y + 20, 22, (0.95, 0.62, 0.12), "arialbd.ttf", align="RIGHT")
    for reg, title, lines in (("rating_ups", "AMPERE SMART-UPS", ["Model: SR2200RM2U  /  ST1500 (tower)", "Input: 200-240V~ 50/60Hz 10A",
                                                                  "Output: 2200VA / 1980W", "Battery: 4 x 12V 9Ah VRLA",
                                                                  "Replace with AMPERE RBC-43 only", "S/N: AS2200R2610B0071"]),
                              ("rating_pdu", "AMPERE RACK PDU", ["Model: AP-0U2404 / AP-1U08", "Input: 200-240V~ 30A 1~",
                                                                 "Outlets: C13 10A max, C19 16A max", "Bank breakers: 16A",
                                                                 "Max load: 24A total", "S/N: AP0U2610A0453"])):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.94, 0.94, 0.93))
        art.rect(x, y + h - 56, w, 56, (0.1, 0.1, 0.12))
        art.text(title, x + 18, y + h - 38, 28, (0.95, 0.95, 0.96), "segoeuib.ttf", maxw=w - 36)
        for k, s in enumerate(lines):
            art.text(s, x + 18, y + h - 92 - k * 34, 21, ink, "arial.ttf", maxw=w - 36)
        art.code128ish(len(reg) * 101, x + 18, y + 14, 280, 40, ink)
        art.text("CE  UL  ♻", x + 320, y + 30, 26, ink, "seguisym.ttf")
    x, y, w, h = ATLAS.reg["lcd_frame"]
    art.rect(x, y, w, h, (0.12, 0.12, 0.13))
    art.text("STATUS", x + 16, y + 64, 18, (0.7, 0.72, 0.75), "arialbd.ttf")
    art.text("LOAD  BATT  RUNTIME", x + 16, y + 20, 15, (0.55, 0.57, 0.6), "arialbd.ttf", maxw=w - 30)
    art.render(ATLAS.file)
    art.dispose()


# ====================================================================== outlets

def nema515_outlet(fr, parent, tag="black_plastic"):
    """A NEMA 5-15R receptacle: a rounded face with the two flat slots (the neutral taller) and the U ground hole."""
    face = P.rrect(0.0215, 0.0275, 0.0050, 0, 0, 3)
    hot = D.rect(-0.0068, -0.0053, 0.0015, 0.0083)
    neu = D.rect(0.0053, 0.0068, 0.0010, 0.0090)
    gnd = P.arc(0, -0.0060, 0.0024, 0, math.pi, 6) + [(-0.0024, -0.0088), (0.0024, -0.0088)]   # the U ground
    P.slab("nema_face", face, 0.0040, tag, fr.sub(0, 0, -0.0020), holes=[hot, neu, gnd], parent=parent)
    P.slab("nema_back", face, 0.0004, "dark_plastic", fr.sub(0, 0, -0.0042), parent=parent)


# ====================================================================== UPS (2U)

def ups_front_panel(fr, root, w, h, screen_w=0.058, screen_h=0.026, buttons_y=None):
    """The display module: a dark panel with the LCD (A_SCREEN_0), a power button, three menu buttons and the three
    status LEDs, laid out in the frame's local XY (fr at the panel's centre, +Z out)."""
    P.slab("disp_panel", P.rrect(w, h, 0.004), 0.004, "dark_plastic", fr.sub(0, 0, -0.002), parent=root)
    sx, sy = -w * 0.08, h * 0.16
    P.slab("lcd_bezel", P.rrect(screen_w + 0.008, screen_h + 0.008, 0.002, sx, sy), 0.0010, "black_plastic", fr.sub(0, 0, 0.0005),
           holes=[P.rrect(screen_w + 0.001, screen_h + 0.001, 0.001, sx, sy)], parent=root)
    sf = fr.sub(sx, sy, 0.0002)
    scr = P.anchor("A_SCREEN_0", sf, (screen_w, screen_h, 0.003), root, meta="kind=lcd,ref=256x112,colour=blue_white")
    P.quad("screen", sf, screen_w, screen_h, "black_plastic", scr)
    # LEDs above the LCD's right end... (to the viewer's right is -x)
    for k, (nm, tag, lab) in enumerate((("ONLINE", "led_green", "ONLINE"), ("BATTERY", "led_yellow", "ON BATT"), ("FAULT", "led_red", "FAULT"))):
        ly = sy + screen_h / 2 - 0.004 - k * 0.0095
        lf = fr.sub(sx + screen_w / 2 + 0.010, ly, 0.0002)
        D.led(f"A_LED_{nm}_0", lf, 0.0030, 0.0030, tag, root, round_=True, meta=f"colour={tag[4:]},fn={nm.lower()}")
    # buttons along the bottom: power (left of the viewer: +x) then up / down / enter
    by = -h * 0.30 if buttons_y is None else buttons_y
    pf = fr.sub(w * 0.36, by, 0.0006)
    a = D.button("A_BUTTON_POWER_0", pf, 0.0048, 0.0012, "black_plastic", root, ring_tag="grey_plastic",
                 meta="press=-z_local,travel=0.0012,fn=power,hold=2", height=0.0018)
    D.power_icon("pwr_icon", pf.sub(0, 0, 0.0010), 0.0024, 0.0006, "grey_plastic", a)
    for k, (nm, sym) in enumerate((("UP", "up"), ("DOWN", "down"), ("ENTER", "enter"))):
        bf = fr.sub(w * 0.10 - k * 0.016, by, 0.0006)
        a = D.button(f"A_BUTTON_{nm}_0", bf, 0.0040, 0.0010, "grey_plastic", root, ring_tag="black_plastic",
                     meta=f"press=-z_local,travel=0.0010,fn={sym}", height=0.0016, square=(0.010, 0.007))
        if sym in ("up", "down"):
            tri = [(0, 0.0018), (-0.0018, -0.0010), (0.0018, -0.0010)] if sym == "up" else [(0, -0.0018), (0.0018, 0.0010), (-0.0018, 0.0010)]
            P.slab("btn_arrow", tri, 0.0001, "black_plastic", bf.sub(0, 0, 0.0009), parent=a)
        else:
            P.slab("btn_dot", P.circle(0.0012, 0, 0, 10), 0.0001, "black_plastic", bf.sub(0, 0, 0.0009), parent=a)


def battery_pack(a, x0, x1, y0, y1, z_front, depth, root):
    """A battery pack (moving piece of a): a steel tray of 12 V blocks with their terminals and links, the front
    retaining plate with a pull handle, the rear connector."""
    D.box("batt_tray", (x0, y0, z_front - depth), (x1, y0 + 0.0012, z_front), "steel", a)
    for xs in (x0, x1 - 0.0012):
        D.box("batt_tray_side", (xs, y0, z_front - depth), (xs + 0.0012, y0 + (y1 - y0) * 0.55, z_front), "steel", a)
    n = 4
    bw = (x1 - x0 - 0.004) / n
    for k in range(n):
        bx0 = x0 + 0.002 + k * bw
        D.box("batt_block", (bx0 + 0.0005, y0 + 0.0012, z_front - depth + 0.004), (bx0 + bw - 0.0005, y1 - 0.004, z_front - 0.010), "black_plastic", a,
              bevel=0.0015, seg=1)
        for j, col in enumerate(("red", "black")):
            P.cylinder("batt_term", P.Frame((bx0 + bw * (0.3 if j == 0 else 0.7), y1 - 0.004, z_front - 0.020), Y, Z), 0.0030, 0.003, P.PALETTE_TAG, 10, a,
                       z0=0.0, uv_solid=P.pal(col))
    for k in range(n - 1):
        D.box("batt_link", (x0 + 0.002 + (k + 0.7) * bw - 0.002, y1 - 0.0012, z_front - 0.023), (x0 + 0.002 + (k + 1.3) * bw + 0.002, y1 - 0.0004, z_front - 0.017),
              "copper", a)
    # front plate with the handle and a label, rear connector
    D.zslab("batt_plate", "steel", D.rect(x0, x1, y0, y1), z_front - 0.0015, z_front, [], a)
    hx = (x0 + x1) / 2
    hy = (y0 + y1) / 2
    P.tube("batt_handle", [(hx - 0.040, hy, z_front), (hx - 0.040, hy, z_front + 0.016), (hx + 0.040, hy, z_front + 0.016), (hx + 0.040, hy, z_front)],
           0.0030, "black_plastic", a, 8)
    for sx in (-1, 1):
        P.cylinder("batt_screw", P.Frame((hx + sx * ((x1 - x0) / 2 - 0.008), hy, z_front), Z, Y), 0.0035, 0.004, "steel", 12, a, z0=0.0)
    LABELS.quad("batt_label", "BATTERY", P.Frame((hx, hy + (y1 - y0) * 0.30, z_front + 0.00005), Z, Y), 0.006, a)
    D.box("batt_conn", (hx - 0.012, y0 + 0.004, z_front - depth - 0.012), (hx + 0.012, y0 + 0.018, z_front - depth), P.PALETTE_TAG, a,
          uv_solid=P.pal("grey"))


def build_ups_2u():
    P.reset()
    textures()
    root = c.root("ups_2u")
    D.ROOT[0] = root
    H = 0.0873
    yb = (2 * D.U - H) / 2
    yt = yb + H
    BW = 0.432
    ZF = 0.004              # the chassis front plate
    DEPTH = 0.480
    ZR = ZF - DEPTH
    ZB = 0.032              # the bezel's face
    # chassis
    D.box("base", (-BW / 2, yb, ZR), (BW / 2, yb + 0.0012, ZF), "paint_black", root)
    D.box("top", (-BW / 2, yt - 0.0012, ZR), (BW / 2, yt, ZF), "paint_black", root)
    for sx in (-1, 1):
        D.box("side", (min(sx * BW / 2, sx * (BW / 2 - 0.0012)), yb, ZR), (max(sx * BW / 2, sx * (BW / 2 - 0.0012)), yt, ZF), "paint_black", root)
    D.decal("rating", ATLAS, "rating_ups", P.Frame((0.08, yt + 0.00005, ZR + 0.10), Y, NZ), 0.11, 0.077, root)
    # front plate with the battery opening, the display module at +x
    bx0, bx1 = -0.200, 0.100
    D.zslab("front_plate", "paint_black", D.rect(-BW / 2, BW / 2, yb, yt), ZF - 0.0015, ZF, [D.rect(bx0, bx1, yb + 0.006, yt - 0.006)], root)
    D.box("batt_bay", (bx0, yb + 0.0012, ZF - 0.36), (bx1, yb + 0.0030, ZF - 0.0015), "steel", root)
    D.box("batt_bay_back", (bx0, yb, ZF - 0.362), (bx1, yt, ZF - 0.360), "steel", root)
    D.box("batt_socket", (-0.062, yb + 0.004, ZF - 0.360), (-0.038, yb + 0.018, ZF - 0.355), "black_plastic", root)
    dfr = P.Frame((0.165, yb + H / 2, ZB - 0.0005), Z, Y)
    D.box("disp_housing", (0.112, yb + 0.002, ZF), (0.214, yt - 0.002, ZB - 0.004), "black_plastic", root, bevel=0.002, seg=1)
    ups_front_panel(dfr, root, 0.096, H - 0.010)
    D.ears(root, 2, ZF, "paint_black", body_w=BW, depth=0.030)
    # battery pack behind the bezel
    a = P.anchor("A_BATTERY_0", P.Frame(((bx0 + bx1) / 2, yb + H / 2, ZF), Z, Y), (bx1 - bx0, H - 0.012, 0.36), root,
                 meta="pull=+z,dist=0.38,order=1,under=A_BEZEL_0,kind=vrla,cells=4x12v9ah,connector=anderson")
    battery_pack(a, bx0 + 0.003, bx1 - 0.003, yb + 0.0032, yt - 0.007, ZF + 0.0015, 0.35, root)
    # the bezel: a ribbed vent face over the battery, the logo
    b = P.anchor("A_BEZEL_0", P.Frame(((-0.214 + 0.110) / 2, yb + H / 2, ZB), Z, Y), (0.324, H - 0.002, ZB - ZF), root,
                 meta="remove=+z,dist=0.05,order=0,clips=4")
    xb0, xb1 = -0.214, 0.110
    vents = [D.rect(xb0 + 0.020, xb1 - 0.110, yb + 0.010 + k * 0.0080, yb + 0.0135 + k * 0.0080) for k in range(9)]
    D.zslab("bezel_face", "dark_plastic", D.rr(xb0, xb1, yb + 0.0010, yt - 0.0010, 0.004), ZB - 0.0025, ZB, vents, b)
    D.zslab("bezel_vent_back", "black_plastic", D.rect(xb0 + 0.018, xb1 - 0.108, yb + 0.008, yt - 0.008), ZB - 0.009, ZB - 0.008, (), b)
    for (ya, yb_) in ((yb + 0.0010, yb + 0.0030), (yt - 0.0030, yt - 0.0010)):
        D.box("bezel_lip", (xb0, ya, ZF + 0.001), (xb1, yb_, ZB - 0.0025), "dark_plastic", b)
    for xx in (xb0, xb1 - 0.002):
        D.box("bezel_lip", (xx, yb + 0.0010, ZF + 0.001), (xx + 0.002, yt - 0.0010, ZB - 0.0025), "dark_plastic", b)
    D.decal("bezel_logo", ATLAS, "bezel_logo", P.Frame((xb1 - 0.055, yb + H / 2, ZB + 0.00005), Z, Y), 0.088, 0.022, b)
    # rear: outlets, inlet, comms, breaker, fan, card slot
    rp_holes = []
    outlets = []
    for g, gx in enumerate((0.150, 0.060)):
        for k in range(4):
            x = gx + (k % 2 - 0.5) * 0.034
            y = yb + 0.022 + (k // 2) * 0.034
            outlets.append((x, y, g))
            rp_holes.append(D.c14_outline(x, y, 1.24))
    inlet = (-0.170, yb + 0.030)
    rp_holes.append(D.c20_outline(*inlet))
    usb = (-0.040, yb + 0.060)
    ser = (-0.040, yb + 0.030)
    rp_holes.append(D.rect(usb[0] - 0.0062, usb[0] + 0.0062, usb[1] - 0.0055, usb[1] + 0.0055))
    rp_holes.append(D.rect(ser[0] - D.RJ45_W / 2 - 0.001, ser[0] + D.RJ45_W / 2 + 0.001, ser[1] - D.RJ45_H / 2 - 0.0028, ser[1] + D.RJ45_H / 2 + 0.0008))
    fan = (-0.100, yb + 0.045)
    rp_holes += P.hex_grid(lambda a_, b_, r: (a_ - fan[0]) ** 2 + (b_ - fan[1]) ** 2 < 0.026 ** 2, 0.0070, 0.0029, fan[0] - 0.03, fan[0] + 0.03, yb + 0.012, yt - 0.012)
    D.zslab("rear", "paint_black", D.rect(-BW / 2, BW / 2, yb, yt), ZR - 0.0015, ZR, rp_holes, root)
    for k, (x, y, g) in enumerate(outlets):
        of = P.Frame((x, y, ZR - 0.0015), NZ, Y)
        D.c13_outlet(of, root, depth=0.008)
        P.anchor(f"A_PORT_C13_{k}", of, (0.026, 0.018, 0.012), root, meta=f"depth=0.007,plug=c14,outlet=c13,group={g + 1}")
        LABELS.quad("outlet_no", str(k + 1), P.Frame((x, y + 0.0128, ZR - 0.00155), NZ, Y), 0.0030, root)
    for g, gx in enumerate((0.150, 0.060)):
        LABELS.quad("group_label", f"GROUP {g + 1}", P.Frame((gx, yt - 0.0050, ZR - 0.00155), NZ, Y), 0.0040, root)
    inf = P.Frame((inlet[0], inlet[1], ZR - 0.0015), NZ, Y)
    D.c20_inlet(inf, root)
    P.anchor("A_PORT_C20_0", inf, (0.034, 0.025, 0.014), root, meta="depth=0.009,plug=c19,inlet=c20")
    LABELS.quad("inlet_label", "INPUT", P.Frame((inlet[0], inlet[1] + 0.019, ZR - 0.00155), NZ, Y), 0.0040, root)
    LABELS.quad("inlet_volt", "200-240V~", P.Frame((inlet[0], inlet[1] - 0.019, ZR - 0.00155), NZ, Y), 0.0034, root)
    uf = P.Frame((usb[0], usb[1], ZR - 0.0015), NZ, Y)
    D.cavity(uf, P.rrect(0.0090, 0.0080, 0.0012), 0.008, root, wall_tag="black_plastic")
    D.box("usbb_tongue", (usb[0] - 0.0030, usb[1] - 0.0018, ZR + 0.0005), (usb[0] + 0.0030, usb[1] + 0.0022, ZR + 0.0060), "black_plastic", root)
    P.anchor("A_PORT_USBB_0", uf, (0.012, 0.012, 0.012), root, meta="depth=0.008,usb=b")
    LABELS.quad("usb_label", "USB", P.Frame((usb[0] + 0.016, usb[1], ZR - 0.00155), NZ, Y), 0.0034, root)
    sf = P.Frame((ser[0], ser[1], ZR - 0.0015), NZ, Y)
    D.rj45_jack(sf, root, latch_up=False)
    P.anchor("A_PORT_SERIAL_0", sf, (0.0145, 0.012, 0.02), root, meta="depth=0.012,rj45=1,latch=-up,serial=rs232")
    LABELS.quad("ser_label", "SERIAL", P.Frame((ser[0] + 0.018, ser[1], ZR - 0.00155), NZ, Y), 0.0034, root)
    # breaker (a push-to-reset button)
    bf = P.Frame((-0.200, yb + 0.068, ZR - 0.0015), NZ, Y)
    P.lathe("breaker_body", [(0, 0.0), (0.0075, 0.0), (0.0075, 0.0030), (0.0060, 0.0040), (0, 0.0040)], "black_plastic", bf, 18, root)
    a = P.anchor("A_BUTTON_BREAKER_0", bf.sub(0, 0, 0.004), (0.012, 0.012, 0.01), root, meta="press=-z_local,travel=0.003,fn=reset,rating=15a")
    P.cylinder("breaker_cap", bf.sub(0, 0, 0.0055), 0.0045, 0.0030, "white_plastic", 16, a)
    LABELS.quad("brk_label", "BREAKER", P.Frame((-0.200, yb + 0.080, ZR - 0.00155), NZ, Y), 0.0034, root)
    # management card slot cover and the fan behind its grille
    D.zslab("nmc_cover", "steel", D.rect(0.000, 0.024, yb + 0.008, yb + 0.076), ZR - 0.0025, ZR - 0.0015, [], root)
    for y in (yb + 0.013, yb + 0.071):
        P.cylinder("nmc_screw", P.Frame((0.012, y, ZR - 0.0025), NZ, Y), 0.0025, 0.0015, "steel", 10, root, z0=0.0)
    LABELS.quad("nmc_label", "NMC", P.Frame((0.012, yb + 0.042, ZR - 0.00255), NZ, Y), 0.0030, root)
    fa = P.anchor("A_FAN_0", P.Frame((fan[0], fan[1], ZR + 0.014), NZ, Y), (0.06, 0.06, 0.025), root, meta="axis=z,spin=1,rpm=3200")
    D.server_fan(fa, 0.060, 0.025, blades=7, parent=root, segs=18)
    P.cylinder("earth_screw", P.Frame((0.205, yb + 0.075, ZR - 0.0015), NZ, Y), 0.0030, 0.0025, "nickel", 8, root, z0=0.0)
    P.anchor("A_HIT_0", (0, yb + H / 2, (ZB + ZR) / 2), (BW, H, ZB - ZR), root)
    P.anchor("A_HIT_1", (0, yb + H / 2, 0.001), (D.EAR_W, H, 0.004), root)
    return D.finish(root, "ups_2u", preview_views=((25, 15), (155, 20)), beauty_views=((22, 12), (155, 15)), size=(1100, 700), samples=36,
                    extra=f"frame: rack device, 2U, body 0.432 x {H} x 0.480, bezel face z={ZB}, rear z={ZR:.3f}",
                    more_beauty=[(((-15, 8),), dict(target=(0.16, yb + H / 2, ZB), dist=0.24)),
                                 (((25, 25),), dict(hide=("@A_BEZEL_0",))),
                                 (((165, 10),), dict(target=(0.05, yb + H / 2, ZR), dist=0.42))])


# ====================================================================== UPS (tower)

def build_ups_tower():
    P.reset()
    textures()
    root = c.root("ups_tower")
    D.ROOT[0] = root
    W, H, Dp = 0.170, 0.219, 0.439
    zf, zr = Dp / 2, -Dp / 2
    ft = 0.006    # feet
    # body: a rounded shell lofted along z
    secs = [(P.rrect(W, H - ft, 0.010, 0, ft + (H - ft) / 2, 4), zr), (P.rrect(W, H - ft, 0.010, 0, ft + (H - ft) / 2, 4), zf - 0.030)]
    P.loft("body", secs, "black_plastic", parent=root, smooth=35)
    for sx in (-1, 1):
        for sz in (-1, 1):
            D.box("foot", (sx * 0.065 - 0.012, 0.0, sz * 0.18 - 0.012), (sx * 0.065 + 0.012, ft, sz * 0.18 + 0.012), "rubber", root, bevel=0.002, seg=1)
    # front: the bezel (removable) over the battery door, and the sloped control panel at the top
    zb = zf
    b = P.anchor("A_BEZEL_0", P.Frame((0, ft + (H - ft) * 0.36, zb), Z, Y), (W, (H - ft) * 0.70, 0.030), root,
                 meta="remove=+z,dist=0.05,order=0,clips=4")
    by0, by1 = ft + 0.004, ft + (H - ft) * 0.70
    vents = [D.rect(-0.060, 0.060, by0 + 0.018 + k * 0.0095, by0 + 0.0225 + k * 0.0095) for k in range(9)]
    secs = []
    for (z, ins) in ((zf - 0.030, 0.0), (zf - 0.006, 0.0), (zf - 0.002, 0.003), (zf, 0.006)):
        secs.append((P.rrect(W - 2 * ins, by1 - by0 - 2 * ins, max(0.003, 0.010 - ins), 0, (by0 + by1) / 2, 4), z))
    P.loft("bezel_shell", secs, "dark_plastic", parent=b, smooth=40, caps=(True, False))
    D.zslab("bezel_face", "dark_plastic", P.rrect(W - 0.012, by1 - by0 - 0.012, 0.004, 0, (by0 + by1) / 2, 4), zf - 0.0025, zf, vents, b)
    D.zslab("bezel_vent_back", "black_plastic", D.rect(-0.062, 0.062, by0 + 0.014, by0 + 0.106), zf - 0.010, zf - 0.009, (), b)
    D.decal("bezel_logo", ATLAS, "tower_logo", P.Frame((0.0, by1 - 0.022, zf + 0.00005), Z, Y), 0.100, 0.025, b)
    # battery behind the bezel (a door plate and the pack)
    D.zslab("batt_door_frame", "black_plastic", P.rrect(W - 0.010, by1 - by0, 0.006, 0, (by0 + by1) / 2), zf - 0.032, zf - 0.030,
            [D.rect(-0.060, 0.060, by0 + 0.010, by1 - 0.012)], root)
    a = P.anchor("A_BATTERY_0", P.Frame((0, (by0 + by1) / 2, zf - 0.030), Z, Y), (0.12, by1 - by0 - 0.022, 0.18), root,
                 meta="pull=+z,dist=0.20,order=1,under=A_BEZEL_0,kind=vrla,cells=2x12v9ah")
    battery_pack(a, -0.059, 0.059, by0 + 0.011, by1 - 0.013, zf - 0.030, 0.17, root)
    # control panel: the sloped top front
    cy0 = by1 + 0.002
    cfr = P.Frame((0.0, (cy0 + H - 0.004) / 2, zf - 0.012), (0, math.sin(math.radians(25)), math.cos(math.radians(25))),
                  (0, math.cos(math.radians(25)), -math.sin(math.radians(25))))
    D.fbox("ctrl_block", cfr, (-W / 2 + 0.004, -0.031, -0.034), (W / 2 - 0.004, 0.030, 0.0), "black_plastic", root, bevel=0.003, seg=1)
    ups_front_panel(cfr.sub(0, 0.0, 0.0005), root, W - 0.016, 0.056, screen_w=0.050, screen_h=0.020)
    # rear: 8 NEMA 5-15R in two groups, the cord, USB, breaker, fan
    rp = []
    outs = []
    for k in range(8):
        col, row = k % 2, k // 2
        x = 0.020 if col == 0 else -0.020
        y = 0.050 + row * 0.036
        outs.append((x, y))
        rp.append(P.rrect(0.0235, 0.0295, 0.0055, x, y, 3))
    fan = (0.054, 0.186)
    rp += P.hex_grid(lambda a_, b_, r: (a_ - fan[0]) ** 2 + (b_ - fan[1]) ** 2 < 0.019 ** 2, 0.0062, 0.0026, fan[0] - 0.022, fan[0] + 0.022, fan[1] - 0.022, fan[1] + 0.022)
    usb = (-0.060, 0.175)
    rp.append(D.rect(usb[0] - 0.0062, usb[0] + 0.0062, usb[1] - 0.0055, usb[1] + 0.0055))
    D.zslab("rear_plate", "black_plastic", P.rrect(W - 0.004, H - ft - 0.004, 0.008, 0, ft + (H - ft) / 2, 4), zr - 0.0015, zr + 0.0005, rp, root)
    for k, (x, y) in enumerate(outs):
        of = P.Frame((x, y, zr - 0.0015), NZ, Y)
        nema515_outlet(of, root)
        P.anchor(f"A_PORT_NEMA515_{k}", of, (0.024, 0.030, 0.014), root,
                 meta=f"depth=0.010,plug=nema5-15p,outlet=nema5-15r,group={'battery' if k < 6 else 'surge'}")
        LABELS.quad("outlet_no", str(k + 1), P.Frame((x + (0.0155 if x < 0 else -0.0155), y + 0.011, zr - 0.00155), NZ, Y), 0.0030, root)
    LABELS.quad("grp_label", "BATT + SURGE", P.Frame((0.0, 0.0315, zr - 0.00155), NZ, Y), 0.0045, root)
    uf = P.Frame((usb[0], usb[1], zr - 0.0015), NZ, Y)
    D.cavity(uf, P.rrect(0.0090, 0.0080, 0.0012), 0.008, root)
    D.box("usbb_tongue", (usb[0] - 0.0030, usb[1] - 0.0018, zr + 0.0005), (usb[0] + 0.0030, usb[1] + 0.0022, zr + 0.0060), "black_plastic", root)
    P.anchor("A_PORT_USBB_0", uf, (0.012, 0.012, 0.012), root, meta="depth=0.008,usb=b")
    LABELS.quad("usb_label", "USB", P.Frame((usb[0], usb[1] - 0.0105, zr - 0.00155), NZ, Y), 0.0034, root)
    fa = P.anchor("A_FAN_0", P.Frame((fan[0], fan[1], zr + 0.012), NZ, Y), (0.045, 0.045, 0.02), root, meta="axis=z,spin=1,rpm=2800")
    D.server_fan(fa, 0.045, 0.020, blades=7, parent=root, segs=18)
    bf = P.Frame((-0.040, 0.205, zr - 0.0015), NZ, Y)
    P.lathe("breaker_body", [(0, 0.0), (0.0070, 0.0), (0.0070, 0.0030), (0.0055, 0.0040), (0, 0.0040)], "black_plastic", bf, 18, root)
    a = P.anchor("A_BUTTON_BREAKER_0", bf.sub(0, 0, 0.004), (0.012, 0.012, 0.01), root, meta="press=-z_local,travel=0.003,fn=reset,rating=15a")
    P.cylinder("breaker_cap", bf.sub(0, 0, 0.0055), 0.0042, 0.0030, "white_plastic", 16, a)
    # the attached input cord: grommet and strain relief at the lower rear
    cp = (-0.050, 0.022, zr - 0.0015)
    cf = P.Frame(cp, NZ, Y)
    P.lathe("cord_boot", [(0, 0.0), (0.0090, 0.0), (0.0088, 0.006), (0.0060, 0.024), (0.0050, 0.034), (0, 0.034)], "black_plastic", cf, 16, root, smooth=50)
    P.cylinder("cord_stub", cf.sub(0, 0, 0.034), 0.0040, 0.010, "rubber", 12, root, z0=0.0)
    P.anchor("A_CORD_0", cf.sub(0, 0, 0.044), (0.012, 0.012, 0.02), root, meta="r=0.0040,plug=nema5-15p,len=1.8,awg=14")
    D.decal("rating", ATLAS, "rating_ups", P.Frame((-W / 2 - 0.0002, 0.070, -0.10), NX, Y), 0.11, 0.077, root)
    P.anchor("A_HIT_0", (0, H / 2, 0), (W, H, Dp), root)
    return D.finish(root, "ups_tower", preview_views=((30, 15), (150, 20)), beauty_views=((28, 12), (150, 15)), size=(900, 800), samples=36,
                    extra=f"frame: floor at y=0, footprint centred, front +z; body {W} x {H} x {Dp}",
                    more_beauty=[(((-15, 20),), dict(target=(0.0, 0.195, zf - 0.01), dist=0.22)),
                                 (((30, 15),), dict(hide=("@A_BEZEL_0",)))])


# ====================================================================== PDUs

def build_pdu_0u():
    P.reset()
    textures()
    root = c.root("pdu_0u")
    D.ROOT[0] = root
    W, Dz, L = 0.044, 0.056, 1.80
    zf = Dz / 2
    # the extruded aluminium body with end caps; outlets sit in the front face
    D.box("body", (-W / 2, 0.020, -Dz / 2), (W / 2, L - 0.020, zf - 0.0015), "alu_dark", root, bevel=0.002, seg=1)
    for (y0, y1) in ((0.0, 0.020), (L - 0.020, L)):
        D.box("end_cap", (-W / 2 - 0.0005, y0, -Dz / 2 - 0.0005), (W / 2 + 0.0005, y1, zf + 0.0005), "black_plastic", root, bevel=0.003, seg=2)
    # outlet plan (bottom to top): breakers, bank A (C19 + 8 C13), bank B (C19 + 8 C13 + C19), bank C (8 C13 + C19)
    plan = [("brk", 0.120), ("gap", 0.030), ("logo", 0.070), ("c19", 0.050)] + [("c13", 0.038)] * 8 + [("gap", 0.060), ("c19", 0.050)] + \
           [("c13", 0.038)] * 8 + [("c19", 0.050), ("gap", 0.060)] + [("c13", 0.038)] * 8 + [("c19", 0.050), ("gap", 0.040)]
    total = sum(p for _, p in plan)
    y = 0.020 + (L - 0.040 - total) / 2
    face_holes = []
    items = []
    n13 = n19 = 0
    bank = 0
    for kind, pitch in plan:
        yc = y + pitch / 2
        if kind == "c13":
            face_holes.append(D.c14_outline(0, yc, 1.24))
            items.append(("c13", n13, yc, "ABC"[min(2, n13 // 8)]))
            n13 += 1
        elif kind == "c19":
            face_holes.append(P.rrect(0.0335, 0.0250, 0.003, 0, yc))
            items.append(("c19", n19, yc, "ABBC"[n19]))
            n19 += 1
        elif kind in ("brk", "logo"):
            items.append((kind, 0, yc, ""))
        y += pitch
    D.zslab("face", "black_plastic", D.rect(-W / 2 + 0.0015, W / 2 - 0.0015, 0.020, L - 0.020), zf - 0.0015, zf, face_holes, root)
    for kind, n, yc, bk in items:
        if kind == "c13":
            f = P.Frame((0, yc, zf), Z, Y)
            D.c13_outlet(f, root, depth=0.008)
            P.anchor(f"A_PORT_C13_{n}", f, (0.026, 0.018, 0.012), root, meta=f"depth=0.007,plug=c14,outlet=c13,bank={bk},n={n + 1}")
            LABELS.quad("outlet_no", str(n + 1), P.Frame((0.0, yc + 0.0145, zf + 0.00005), Z, Y), 0.0028, root)
        elif kind == "c19":
            f = P.Frame((0, yc, zf), Z, Y)
            D.c19_outlet(f, root, depth=0.009)
            P.anchor(f"A_PORT_C19_{n}", f, (0.032, 0.024, 0.014), root, meta=f"depth=0.008,plug=c20,outlet=c19,bank={bk},n={n + 1}")
            LABELS.quad("c19_no", f"C19-{n + 1}", P.Frame((0.0, yc + 0.0175, zf + 0.00005), Z, Y), 0.0030, root)
        elif kind == "brk":
            # two bank breakers (toggles) and the meter display
            for k, by in enumerate((yc - 0.030, yc + 0.010)):
                f = P.Frame((0, by, zf), Z, Y)
                P.slab("brk_body", P.rrect(0.030, 0.026, 0.002), 0.004, "black_plastic", f.sub(0, 0, 0.002), parent=root)
                a = P.anchor(f"A_SWITCH_BREAKER_{k}", f.sub(0, 0, 0.004), (0.020, 0.016, 0.012), root,
                             meta="hinge=x,on=-25,off=25,on_side=+y,rating=16a,mark_on=I,mark_off=O")
                D.fbox("brk_toggle", f.sub(0, 0, 0.004), (-0.007, -0.0025, 0.0), (0.007, 0.0025, 0.009), "white_plastic", a, bevel=0.0008, seg=1)
                LABELS.quad("brk_label", f"BANK {'AB'[k]}", P.Frame((0.0, by - 0.0175, zf + 0.00005), Z, Y), 0.0030, root)
            mf = P.Frame((0, yc + 0.042, zf), Z, Y)
            P.slab("meter_bezel", P.rrect(0.030, 0.016, 0.002), 0.0020, "black_plastic", mf.sub(0, 0, 0.001),
                   holes=[P.rrect(0.024, 0.010, 0.001)], parent=root)
            scr = P.anchor("A_SCREEN_0", mf.sub(0, 0, 0.0004), (0.024, 0.010, 0.003), root, meta="kind=7seg,digits=3,colour=red,shows=amps")
            P.quad("meter", mf.sub(0, 0, 0.0004), 0.024, 0.010, "black_plastic", scr)
        elif kind == "logo":
            D.decal("logo", ATLAS, "pdu_logo", P.Frame((0, yc, zf + 0.00005), Z, (1, 0, 0)), 0.060, 0.0113, root)
    # the cord out of the bottom end, two mounting buttons on the back, the rating label on the side
    cf = P.Frame((0.0, 0.0, -0.008), NY, Z)
    P.lathe("cord_boot", [(0, 0.0), (0.0110, 0.0), (0.0105, 0.010), (0.0075, 0.040), (0.0065, 0.055), (0, 0.055)], "black_plastic", cf, 16, root, smooth=50)
    P.cylinder("cord_stub", cf.sub(0, 0, 0.055), 0.0062, 0.015, "rubber", 12, root, z0=0.0)
    P.anchor("A_CORD_0", cf.sub(0, 0, 0.070), (0.016, 0.016, 0.02), root, meta="r=0.0062,plug=l6-30p,len=3.0,awg=10")
    for k, by in enumerate((0.20, 1.60)):
        bf = P.Frame((0.0, by, -Dz / 2), NZ, Y)
        P.lathe("mount_button", [(0, 0.0), (0.0045, 0.0), (0.0045, 0.006), (0.0080, 0.007), (0.0080, 0.009), (0, 0.009)], "steel", bf, 16, root)
        P.anchor(f"A_MOUNT_{k}", bf.sub(0, 0, 0.009), (0.02, 0.02, 0.012), root, meta="kind=button,keyhole=1")
    D.decal("rating", ATLAS, "rating_pdu", P.Frame((W / 2 + 0.0002, 1.10, 0.0), X, (0, 1, 0)), 0.050, 0.035, root)
    P.anchor("A_HIT_0", (0, L / 2, 0), (W, L, Dz), root)
    return D.finish(root, "pdu_0u", preview_views=((35, 10), (150, 15)), beauty_views=((30, 10), (160, 10)), size=(700, 1100), samples=36,
                    extra=f"frame: origin at the bottom end of the body (cross-section centre), +Y along it, outlets on +Z; {W} x {L} x {Dz}",
                    more_beauty=[(((20, 8),), dict(target=(0.0, 0.25, zf), dist=0.30)),
                                 (((25, 6),), dict(target=(0.0, 0.62, zf), dist=0.25))])


def build_pdu_1u():
    P.reset()
    textures()
    root = c.root("pdu_1u")
    D.ROOT[0] = root
    H = 0.0436
    yb = (D.U - H) / 2
    yt = yb + H
    BW = 0.440
    ZF = 0.003
    ZR = ZF - 0.180
    D.box("chassis", (-BW / 2, yb, ZR), (BW / 2, yt, ZF - 0.0015), "paint_black", root, bevel=0.001, seg=1)
    # front: 8 C13 outlets, the lit rocker, the logo
    xs = [0.150 - k * 0.036 for k in range(8)]
    yc = yb + H / 2
    holes = [D.c14_outline(x, yc, 1.24) for x in xs]
    sw = (-0.170, yc)
    holes.append(P.rrect(0.0255, 0.0175, 0.0012, sw[0], sw[1]))
    D.zslab("front", "paint_black", D.rect(-BW / 2, BW / 2, yb, yt), ZF - 0.0015, ZF, holes, root)
    for k, x in enumerate(xs):
        f = P.Frame((x, yc, ZF), Z, Y)
        D.c13_outlet(f, root, depth=0.008)
        P.anchor(f"A_PORT_C13_{k}", f, (0.026, 0.018, 0.012), root, meta=f"depth=0.007,plug=c14,outlet=c13,n={k + 1}")
        LABELS.quad("outlet_no", str(k + 1), P.Frame((x, yt - 0.0045, ZF + 0.00005), Z, Y), 0.0030, root)
    # the lit rocker switch: a bezel, the rocker (moving piece) with its red lamp window
    f = P.Frame((sw[0], sw[1], ZF), Z, Y)
    P.slab("rocker_bezel", P.rrect(0.0285, 0.0205, 0.0015), 0.0020, "black_plastic", f.sub(0, 0, 0.0010),
           holes=[P.rrect(0.0240, 0.0160, 0.0010)], parent=root)
    P.slab("rocker_well", P.rrect(0.0240, 0.0160, 0.0010), 0.0010, "dark_plastic", f.sub(0, 0, -0.004), parent=root)
    a = P.anchor("A_SWITCH_POWER_0", f.sub(0, 0, 0.0005), (0.026, 0.018, 0.010), root,
                 meta="hinge=x,on=-9,off=9,on_side=+y,mark_on=I,mark_off=O,lit=1,led=A_LED_SWITCH_0")
    prof = [(-0.0078, -0.0035), (0.0078, -0.0035), (0.0078, 0.0010), (0.0, 0.0028), (-0.0078, 0.0010)]   # (y, z) rocker profile
    D.xslab("rocker", "black_plastic", [(sw[1] * 0 + z + ZF + 0.0005, y + sw[1]) for (y, z) in prof], sw[0] - 0.0115, sw[0] + 0.0115, (), a)
    lf = P.Frame((sw[0], sw[1] + 0.0039, ZF + 0.0005 + 0.0020), (0, 0.225, 0.974), (0, 0.974, -0.225))
    led = P.anchor("A_LED_SWITCH_0", lf, (0.018, 0.004, 0.003), a, meta="colour=red,fn=power_on")
    P.cube("rocker_lamp", (0, 0, 0.0001), (0.018, 0.0040, 0.0006), "led_red", lf, led)
    P.text3d("rocker_o", "O", 0.0030, 0.0001, "white_plastic", P.Frame((sw[0], sw[1] - 0.0039, ZF + 0.0005 + 0.0019), (0, -0.225, 0.974), (0, 0.974, 0.225)),
             "arialbd.ttf", parent=a)
    D.decal("logo", ATLAS, "pdu_logo", P.Frame((0.198, yc, ZF + 0.00005), Z, Y), 0.034, 0.0064, root)
    D.ears(root, 1, ZF, "paint_black", body_w=BW, slots=[D.HOLES_IN_U[0], D.HOLES_IN_U[2]])
    # rear: the input cord through a strain relief, a rating label on top
    cf = P.Frame((0.150, yc, ZR), NZ, Y)
    P.lathe("cord_boot", [(0, 0.0), (0.0090, 0.0), (0.0086, 0.008), (0.0060, 0.028), (0.0052, 0.040), (0, 0.040)], "black_plastic", cf, 16, root, smooth=50)
    P.cylinder("cord_stub", cf.sub(0, 0, 0.040), 0.0045, 0.012, "rubber", 12, root, z0=0.0)
    P.anchor("A_CORD_0", cf.sub(0, 0, 0.052), (0.014, 0.014, 0.02), root, meta="r=0.0045,plug=c20,len=2.5,awg=14")
    D.decal("rating", ATLAS, "rating_pdu", P.Frame((-0.05, yt + 0.00005, ZR + 0.07), Y, NZ), 0.080, 0.056, root)
    P.anchor("A_HIT_0", (0, yc, (ZF + ZR) / 2), (BW, H, ZF - ZR), root)
    P.anchor("A_HIT_1", (0, yc, 0.001), (D.EAR_W, H, 0.004), root)
    return D.finish(root, "pdu_1u", preview_views=((22, 15), (160, 20)), beauty_views=((18, 12), (155, 18)), size=(1100, 600), samples=36,
                    extra=f"frame: rack device, 1U, body 0.440 x {H} x 0.180, front z={ZF}",
                    more_beauty=[(((-15, 8),), dict(target=(-0.12, yc, ZF), dist=0.16))])
