"""
server_1u and server_2u: 19" rack servers ("STRATA SR110" 1U and "STRATA SR220" 2U), 0.70 m deep.

Rack device frame (datacenter_common): origin at the centre of the front mounting plane at the bottom of the U space,
+Z out of the front, the chassis towards -Z. The ears (control panels with captive thumbscrews) sit on the rack's
front rails at z 0..0.030; the drive faces are at z = 0.030 and the rear face at z = -0.670. Chassis 0.434 wide
(slide rails take the 8 mm per side up to the rack's 0.450 opening), 43.6 / 87.3 mm high, centred in its U space.

Front: hot-swap drive trays A_BAY_n (pull=+z): 8 x 2.5" (2 rows x 4) on the 1U, 12 x 3.5" (3 x 4) on the 2U, each
with its activity LED A_LED_DRIVE_n@A_BAY_n; the power button A_BUTTON_POWER_0 (with A_LED_POWER_0), the ID
button A_BUTTON_ID_0 (A_LED_ID_0), status LEDs A_LED_HEALTH_0 / A_LED_FAULT_0, a front USB A_PORT_USBA_FRONT_0;
the 2U has the removable bezel A_BEZEL_0 over its drives.
Rear: two hot-swap PSUs A_PSU_0/1 (pull=-z) with a handle, A_LED_PSU_n@A_PSU_n and the C14 inlet
A_PORT_C14_n@A_PSU_n; 4 x RJ45 A_PORT_ETH_0..3 (A_LED_LINK_n / A_LED_ACT_n), the IPMI port A_PORT_IPMI_0, VGA
A_PORT_VGA_0, USB A_PORT_USBA_0..1, PCIe slot covers.
Top cover A_LID_0 (slide=-z) over a believable interior: the board, two CPU heatsinks, 16 DIMMs, the fan wall with
A_FAN_n rotors, the air shroud A_SHROUD_0 (lift=+y), the drive backplane, risers and the PSU cage.
Slide rails A_RAIL_L_0 (-x) and A_RAIL_R_0 (+x), in their installed pose between the rack's front and rear rails.
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

XB = 0.217            # chassis half width (0.434)
ZF = 0.030            # front faces (drive trays, ears)
DEPTH = 0.700
ZR = ZF - DEPTH       # rear face
T = 0.0010            # sheet steel
REAR_RAIL_Z = -0.740  # the rack's rear rails (datacenter_rack): the slide rails span 0 .. -0.740
PAINT = "paint_black"
GREEN = P.PALETTE_TAG

STYLES = {
    "server_1u": dict(units=1, h=0.0436, model="SR110", bays=(2, 4), bay_kind="sff", fans=8, fan=0.040, fan_d=0.028,
                      sink_h=None, psu_layout="side", slots_1u=True, thumb_y=0.022225),
    "server_2u": dict(units=2, h=0.0873, model="SR220", bays=(3, 4), bay_kind="lff", fans=6, fan=0.060, fan_d=0.038,
                      sink_h=None, psu_layout="corners", bezel=True, thumb_y=0.0381),
}

ATLAS = D.Atlas("server_print", 2048, 1024)
ATLAS.add("logo", 0, 896, 512, 128)
ATLAS.add("lid", 0, 0, 768, 512)
ATLAS.add("lff", 768, 0, 512, 160)
ATLAS.add("sff", 768, 160, 512, 160)
ATLAS.add("dimm", 1280, 0, 768, 180)
ATLAS.add("psu", 768, 320, 512, 160)
ATLAS.add("labels", 0, 520, 1024, 256)
ATLAS.add("tag", 1024, 520, 384, 140)
ATLAS.add("bezel", 1280, 200, 768, 120)
ATLAS.add("shroud", 1280, 340, 640, 160)
LABELS = D.Labels(ATLAS, "labels", 128, 32, ["IPMI", "VGA", "USB", "1", "2", "3", "4", "PSU 1", "PSU 2", "ID", "LOM"])


# ====================================================================== layout per style

def layout(sid):
    st = dict(STYLES[sid])
    units = st["units"]
    st["H"] = st["h"]
    st["YB"] = (units * D.U - st["h"]) / 2
    st["YT"] = st["YB"] + st["h"]
    yb, yt = st["YB"], st["YT"]
    rows, cols = st["bays"]
    if st["bay_kind"] == "sff":
        bw, bh, pitch_x, pitch_y = 0.0740, 0.0190, 0.0755, 0.0200
        x_start = -0.2065          # the cage's -x edge
        y_start = yb + 0.0018
    else:
        bw, bh, pitch_x, pitch_y = 0.1052, 0.0268, 0.1066, 0.0278
        x_start = -0.2132
        y_start = yb + 0.0020
    bays = []
    n = 0
    for r in range(rows):          # row 0 at the bottom
        for k in range(cols):      # column 0 at -x (the viewer's right)
            cx = x_start + pitch_x * (k + 0.5)
            cy = y_start + pitch_y * (r + 0.5)
            bays.append((n, cx, cy))
            n += 1
    st["bay_list"] = bays
    st["bay_size"] = (bw, bh)
    st["bay_pitch"] = (pitch_x, pitch_y)
    st["cage"] = (x_start - 0.0008, x_start + pitch_x * cols + 0.0008, y_start - 0.0008, y_start + pitch_y * rows + 0.0008)
    # rear: PSUs and I/O
    pw, ph = 0.0735, 0.0400
    py0 = yb + T + 0.0012
    if st["psu_layout"] == "side":
        st["psus"] = [(0.2140 - pw / 2, py0 + ph / 2), (0.2140 - pw * 1.5 - 0.0012, py0 + ph / 2)]
        io_y = yb + 0.0125
        st["io"] = dict(ipmi=(-0.112, io_y), vga=(-0.085, io_y), usb=[(-0.060, yb + 0.0085), (-0.060, yb + 0.0165)],
                        eth=[(-0.036 + 0.016 * k, io_y) for k in range(4)])
        st["slots"] = [(-0.171, yb + 0.0125, 0.080, 0.0185), (-0.171, yb + 0.0325, 0.080, 0.0185)]
        st["vents"] = (-0.125, 0.058, yb + 0.0225, yt - 0.0035)
        st["rear_id"] = (-0.1265, yt - 0.006)
    else:
        st["psus"] = [(0.2140 - pw / 2, py0 + ph / 2), (-0.2140 + pw / 2, py0 + ph / 2)]
        io_y = yb + 0.0140
        st["io"] = dict(ipmi=(-0.098, io_y), vga=(-0.068, io_y), usb=[(-0.040, yb + 0.0100), (-0.040, yb + 0.0180)],
                        eth=[(-0.014 + 0.016 * k, io_y) for k in range(4)])
        st["slots"] = [(-0.174, yb + 0.0545, 0.076, 0.0185), (-0.174, yb + 0.0748, 0.076, 0.0185),
                       (0.174, yb + 0.0545, 0.076, 0.0185), (0.174, yb + 0.0748, 0.076, 0.0185),
                       (0.0, yb + 0.0545, 0.120, 0.0185), (0.0, yb + 0.0748, 0.120, 0.0185)]
        st["vents"] = (0.058, 0.130, yb + 0.006, yb + 0.040)
        st["rear_id"] = (0.050, yb + 0.030)
    st["psu_size"] = (pw, ph)
    return st


# ====================================================================== artwork

def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=None, name="server_print")
    silver = (0.78, 0.8, 0.83)
    # logo badge
    x, y, w, h = ATLAS.reg["logo"]
    art.rect(x, y, w, h, (0.03, 0.03, 0.035))
    art.text("STRATA", x + w / 2, y + h / 2, 84, silver, "segoeuib.ttf", align="CENTER", valign="CENTER", spacing=1.25, maxw=w - 40)
    # bezel band
    x, y, w, h = ATLAS.reg["bezel"]
    art.rect(x, y, w, h, (0.035, 0.035, 0.04))
    art.grad(x, y, w, h * 0.5, (0.05, 0.05, 0.055), (0.035, 0.035, 0.04))
    art.text("STRATA", x + 40, y + h / 2, 64, silver, "segoeuib.ttf", valign="CENTER", spacing=1.25)
    art.text("SR220", x + w - 40, y + h / 2, 44, (0.25, 0.6, 0.95), "segoeuib.ttf", align="RIGHT", valign="CENTER")
    # lid service label
    x, y, w, h = ATLAS.reg["lid"]
    ink = (0.1, 0.1, 0.12)
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    art.rect(x, y + h - 56, w, 56, (0.08, 0.1, 0.14))
    art.text("STRATA  SERVICE INFORMATION", x + 20, y + h - 38, 28, (0.9, 0.92, 0.95), "segoeuib.ttf", maxw=w - 40)
    # a block diagram: drives, fans, CPUs + DIMMs, PSUs, risers
    bx, by = x + 30, y + 120
    art.rect(bx, by, 300, 300, (0.98, 0.98, 0.97))
    for k in range(4):
        art.rect(bx + 10 + k * 72, by + 255, 64, 34, (0.75, 0.78, 0.82))
    for k in range(6):
        art.circle(bx + 30 + k * 48, by + 228, 16, (0.55, 0.58, 0.62))
    for cx_ in (bx + 80, bx + 220):
        art.rect(cx_ - 30, by + 120, 60, 60, (0.35, 0.38, 0.42))
        for d in (-1, 1):
            for k in range(4):
                art.rect(cx_ + d * (40 + k * 7) - 2, by + 95, 4, 110, (0.2, 0.45, 0.25))
    art.rect(bx + 10, by + 10, 120, 50, (0.85, 0.75, 0.3))
    art.rect(bx + 170, by + 10, 120, 50, (0.85, 0.75, 0.3))
    art.text("PSU 2", bx + 70, by + 35, 20, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("PSU 1", bx + 230, by + 35, 20, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("CPU 2", bx + 80, by + 150, 16, (1, 1, 1), "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("CPU 1", bx + 220, by + 150, 16, (1, 1, 1), "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("FRONT", bx + 150, by + 310, 18, ink, "arialbd.ttf", align="CENTER")
    lines = ["DIMM population: A1 B1 first,", "then A2 B2 ... (see manual)", "Fans are hot-swappable.",
             "Replace a PSU within 60 s.", "Close the cover before power-on:", "the intrusion switch logs it.",
             "", "Service tag:  STR-7Q2K91", "Express code:  41 0937 2215"]
    for k, s in enumerate(lines):
        art.text(s, x + 360, y + h - 100 - k * 34, 22, ink, "arial.ttf", maxw=w - 380)
    for i in range(21):   # a QR-like square
        for j in range(21):
            if (i * 7 + j * 13 + i * j) % 5 < 2 or (i < 7 and j < 7 and (i in (0, 6) or j in (0, 6) or (1 < i < 5 and 1 < j < 5))):
                art.rect(x + 560 + i * 8, y + 30 + j * 8, 8, 8, ink)
    art.text("WARNING: hazardous energy inside.", x + 30, y + 70, 20, (0.7, 0.1, 0.05), "arialbd.ttf")
    art.text("Disconnect both power cords before servicing.", x + 30, y + 44, 18, ink, "arial.ttf", maxw=500)
    # drive labels
    for reg, top, sub in (("lff", "8 TB  SAS 12Gb/s  7.2K", "3.5\" HDD  •  hot-plug"), ("sff", "1.92 TB  SAS SSD", "2.5\" • mixed use • hot-plug")):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.9, 0.9, 0.88))
        art.rect(x, y + h - 40, w, 40, (0.12, 0.14, 0.2))
        art.text("STRATA", x + 14, y + h - 28, 26, (0.9, 0.92, 0.95), "segoeuib.ttf")
        art.text(top, x + 14, y + h - 76, 30, ink, "arialbd.ttf", maxw=w - 28)
        art.text(sub, x + 14, y + h - 110, 22, ink, "arial.ttf", maxw=w - 28)
        art.code128ish(len(reg) * 31, x + 14, y + 8, 300, 22, ink)
    # DIMM face: green PCB, 9 chips, gold fingers, a label
    x, y, w, h = ATLAS.reg["dimm"]
    art.rect(x, y, w, h, (0.06, 0.32, 0.15))
    for k in range(9):
        art.rect(x + 20 + k * 82, y + 50, 64, 90, (0.06, 0.06, 0.07))
        art.rect(x + 26 + k * 82, y + 120, 20, 6, (0.25, 0.25, 0.27))
    for k in range(120):
        art.rect(x + 8 + k * 6.3, y + 2, 4.2, 30, (0.86, 0.68, 0.3))
    art.rect(x + 380, y + 2, 8, 30, (0.06, 0.32, 0.15))
    art.rect(x + 560, y + 146, 180, 28, (0.92, 0.92, 0.9))
    art.text("32GB 2Rx8 RDIMM", x + 650, y + 160, 16, ink, "arialbd.ttf", align="CENTER", valign="CENTER", maxw=170)
    # PSU label
    x, y, w, h = ATLAS.reg["psu"]
    art.rect(x, y, w, h, (0.92, 0.92, 0.9))
    art.text("STRATA  800W", x + 16, y + h - 40, 34, ink, "segoeuib.ttf")
    art.rect(x + w - 150, y + 20, 130, 120, (0.75, 0.75, 0.78))
    art.text("80 PLUS", x + w - 85, y + 110, 22, ink, "arialbd.ttf", align="CENTER")
    art.text("PLATINUM", x + w - 85, y + 60, 20, ink, "arialbd.ttf", align="CENTER", maxw=120)
    art.text("AC IN 100-240V~ 10-5A 50/60Hz", x + 16, y + 72, 18, ink, "arial.ttf", maxw=w - 190)
    art.text("DC OUT 12V 66.7A  12Vsb 3A", x + 16, y + 44, 18, ink, "arial.ttf", maxw=w - 190)
    art.text("HOT-PLUG  •  CRPS", x + 16, y + 16, 18, ink, "arialbd.ttf")
    LABELS.draw(art)
    # pull-out info tag
    x, y, w, h = ATLAS.reg["tag"]
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    art.text("SERVICE TAG", x + 14, y + h - 30, 20, ink, "arialbd.ttf")
    art.text("STR-7Q2K91", x + 14, y + h - 62, 28, ink, "consola.ttf")
    art.code128ish(77, x + 14, y + 12, 250, 40, ink)
    # shroud print: airflow arrows and DIMM map
    x, y, w, h = ATLAS.reg["shroud"]
    art.rect(x, y, w, h, (0.04, 0.04, 0.045))
    for k in range(3):
        ax0 = x + 60 + k * 200
        art.poly([(ax0, y + 70), (ax0 + 90, y + 70), (ax0 + 90, y + 50), (ax0 + 130, y + 80), (ax0 + 90, y + 110), (ax0 + 90, y + 90), (ax0, y + 90)], (0.75, 0.77, 0.8))
    art.text("AIRFLOW", x + w / 2, y + 130, 22, (0.75, 0.77, 0.8), "arialbd.ttf", align="CENTER")
    art.text("Do not operate without the air shroud", x + w / 2, y + 22, 18, (0.6, 0.62, 0.65), "arial.ttf", align="CENTER", maxw=w - 40)
    art.render(ATLAS.file)
    art.dispose()


# ====================================================================== pieces

def thumbscrew(a, fr, tag="steel"):
    """A captive thumbscrew's knurled head on the ear (moving piece of anchor a)."""
    n = 16
    pts = []
    for k in range(n * 2):
        ang = math.pi * k / n
        r = 0.0052 if k % 2 == 0 else 0.0048
        pts.append((r * math.cos(ang), r * math.sin(ang)))
    P.slab("thumb_knurl", pts, 0.0055, tag, fr.sub(0, 0, 0.0012 + 0.00275), parent=a)
    P.lathe("thumb_cap", [(0, 0.0067), (0.0046, 0.0067), (0.0050, 0.0062), (0.0050, 0.0012), (0.0058, 0.0012), (0.0058, 0.0), (0, 0.0)],
            tag, fr, 24, a)


def drive_tray(st, n, cx, cy, root):
    """A hot-swap tray: the front with vents, the lever and release, the LED pipe, the carrier and the drive.
    All of it belongs to A_BAY_n (pull=+z)."""
    bw, bh = st["bay_size"]
    lff = st["bay_kind"] == "lff"
    depth = 0.150 if lff else 0.104
    a = P.anchor(f"A_BAY_{n}", P.Frame((cx, cy, ZF), Z, Y), (bw, bh, depth), root,
                 meta=f"pull=+z,dist={depth + 0.01:.3f},kind={'lff' if lff else 'sff'},slot={n},latch=1")
    w, h = bw - 0.0006, bh - 0.0006
    # front: a vented part and the lever (the lever covers the right-hand 45 %)
    x_split = cx - w / 2 + w * 0.55
    vent = []
    nv = 6
    vx0 = cx - w / 2 + 0.006
    vx1 = x_split - 0.004
    for k in range(nv):
        x0 = vx0 + (vx1 - vx0) * k / nv + 0.0007
        x1 = vx0 + (vx1 - vx0) * (k + 1) / nv - 0.0007
        vent.append(D.rect(x0, x1, cy - h * 0.30, cy + h * 0.30))
    D.zslab("tray_front", "black_plastic", D.rr(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, 0.0012), ZF - 0.0030, ZF, vent, a)
    D.zslab("tray_vent_back", "dark_plastic", D.rect(vx0, vx1, cy - h * 0.32, cy + h * 0.32), ZF - 0.0062, ZF - 0.0054, (), a)
    # the lever: a raised bar with a grip texture of ribs, hinged at its -x end; the release button at its +x end
    lx0, lx1 = x_split, cx + w / 2 - 0.0012
    D.zslab("tray_lever", "dark_plastic", D.rr(lx0, lx1, cy - h * 0.40, cy + h * 0.40, 0.0016), ZF, ZF + 0.0030, (), a)
    for k in range(3):
        xr = lx0 + 0.006 + k * 0.0036
        D.box("tray_lever_rib", (xr, cy - h * 0.30, ZF + 0.0030), (xr + 0.0012, cy + h * 0.30, ZF + 0.0036), "black_plastic", a)
    rb = (lx1 - 0.0045, cy)
    D.box("tray_release", (rb[0] - 0.00225, rb[1] - h * 0.275, ZF + 0.0030), (rb[0] + 0.00225, rb[1] + h * 0.275, ZF + 0.0044), GREEN, a,
          bevel=0.0004, seg=1, uv_solid=P.pal("green"))
    # LED light pipes at the vented end
    D.led(f"A_LED_DRIVE_{n}", P.Frame((cx - w / 2 + 0.0030, cy + h * 0.22, ZF + 0.0003), Z, Y), 0.0016, 0.0030, "led_green", a,
          meta="colour=green,fn=activity")
    D.led(f"A_LED_DRIVEFAULT_{n}", P.Frame((cx - w / 2 + 0.0030, cy - h * 0.22, ZF + 0.0003), Z, Y), 0.0016, 0.0030, "led_yellow", a,
          meta="colour=amber,fn=fault")
    # carrier: two side rails and the drive
    dz0 = ZF - 0.004
    D.box("tray_rail", (cx - w / 2 + 0.0004, cy - h / 2 + 0.0008, dz0 - depth + 0.006), (cx - w / 2 + 0.0016, cy + h / 2 - 0.0028, dz0), "steel_dark", a)
    D.box("tray_rail", (cx + w / 2 - 0.0016, cy - h / 2 + 0.0008, dz0 - depth + 0.006), (cx + w / 2 - 0.0004, cy + h / 2 - 0.0028, dz0), "steel_dark", a)
    if lff:
        dw, dh, dl = 0.1016, 0.0254, 0.1470
    else:
        dw, dh, dl = 0.0699, 0.0150, 0.1000
    dy0 = cy - h / 2 + 0.0010
    D.box("drive_body", (cx - dw / 2, dy0, dz0 - dl), (cx + dw / 2, dy0 + dh * 0.82, dz0), "alu", a, bevel=0.0008, seg=1)
    D.box("drive_lid", (cx - dw / 2 + 0.0015, dy0 + dh * 0.82, dz0 - dl + 0.002), (cx + dw / 2 - 0.0015, dy0 + dh - 0.0004, dz0 - 0.002),
          "alu" if not lff else "steel", a)
    lab = "lff" if lff else "sff"
    D.decal("drive_label", ATLAS, lab, P.Frame((cx, dy0 + dh - 0.0003, dz0 - dl * 0.5), Y, NZ), dw * 0.80, dw * 0.80 * 160 / 512, a)
    D.box("drive_conn", (cx - dw * 0.35, dy0 + 0.0015, dz0 - dl - 0.002), (cx + dw * 0.15, dy0 + 0.006, dz0 - dl), "black_plastic", a)
    return a


def psu(st, k, root):
    """A CRPS-style hot-swap PSU (moving piece of A_PSU_k): the body, the rear face with the fan grille, the C14
    inlet, the LED, the release latch and the pull handle, the gold edge connector inside."""
    (px, py) = st["psus"][k]
    pw, ph = st["psu_size"]
    L = 0.185
    a = P.anchor(f"A_PSU_{k}", P.Frame((px, py, ZR), Z, Y), (pw, ph, L), root, meta=f"pull=-z,dist={L + 0.01:.3f},watts=800,eff=platinum,slot={k}")
    # body (bare steel) and the rear plate
    D.box("psu_body", (px - pw / 2, py - ph / 2, ZR + 0.004), (px + pw / 2, py + ph / 2, ZR + L), "steel", a)
    D.decal("psu_label", ATLAS, "psu", P.Frame((px, py + ph / 2 + 0.00005, ZR + L * 0.55), Y, NZ), pw * 0.9, pw * 0.9 * 160 / 512, a)
    gx = px + pw / 2 - 0.022    # the fan grille towards +x, the inlet and the handle towards -x
    holes = P.hex_grid(lambda aa, bb, rr_: (aa - gx) ** 2 + (bb - py) ** 2 < 0.0160 ** 2, 0.0072, 0.0030, gx - 0.018, gx + 0.018, py - 0.018, py + 0.018)
    inlet = (px - pw / 2 + 0.0185, py + 0.004)
    holes.append(D.c14_outline(*inlet))
    holes.append(D.rect(px - pw / 2 + 0.0046, px - pw / 2 + 0.0072, py - ph / 2 + 0.003, py - ph / 2 + 0.0115))   # latch slot
    D.zslab("psu_rear", "steel_dark", D.rr(px - pw / 2, px + pw / 2, py - ph / 2, py + ph / 2, 0.001), ZR - 0.0012, ZR + 0.004, holes, a)
    P.cylinder("psu_fan", P.Frame((gx, py, ZR + 0.010), Z, Y), 0.0170, 0.004, "fan_black", 20, a)
    P.cylinder("psu_fan_hub", P.Frame((gx, py, ZR + 0.0075), Z, Y), 0.0060, 0.002, "black_plastic", 16, a)
    # inlet (its anchor sits on the PSU: A_PORT_C14_k@A_PSU_k)
    ifr = P.Frame((inlet[0], inlet[1], ZR - 0.0012), NZ, Y)
    D.c14_inlet(ifr, a, depth=0.009)
    P.anchor(f"A_PORT_C14_{k}", ifr, (0.028, 0.020, 0.012), a, meta="depth=0.008,plug=c13,inlet=c14")
    # status LED above the inlet
    D.led(f"A_LED_PSU_{k}", P.Frame((inlet[0] + 0.012, py + ph / 2 - 0.004, ZR - 0.0012), NZ, Y), 0.0024, 0.0024, "led_green", a,
          meta="colour=green,fn=psu_ok", round_=True)
    # release latch tab (green touch point) and the pull handle (a bent rod along the bottom edge)
    P.slab("psu_latch", P.rrect(0.0022, 0.0080, 0.0006), 0.006, GREEN,
           P.Frame((px - pw / 2 + 0.0059, py - ph / 2 + 0.0072, ZR - 0.002), Z, Y), parent=a, uv_solid=P.pal("green"))
    hy = py - ph / 2 + 0.0055 if st["units"] == 1 else py - ph / 2 + 0.006
    hx0, hx1 = px - pw / 2 + 0.012, px + pw / 2 - 0.006
    P.tube("psu_handle", [(hx0, hy, ZR - 0.0012), (hx0, hy, ZR - 0.016), (hx1, hy, ZR - 0.016), (hx1, hy, ZR - 0.0012)], 0.0019, "black_plastic", a, 8)
    # the gold edge connector at the inner end and its PCB
    D.box("psu_pcb", (px - 0.020, py - 0.0008, ZR + L), (px + 0.020, py + 0.0008, ZR + L + 0.010), "pcb_green", a)
    D.box("psu_fingers", (px - 0.018, py - 0.00085, ZR + L + 0.002), (px + 0.018, py + 0.00085, ZR + L + 0.0095), "gold", a)
    return a


def slide_rail(st, side, root):
    """A ball-bearing slide rail set in its installed pose: the outer member with its front and rear brackets (pins
    through the rack's square holes), the intermediate and inner members along the chassis side."""
    sx = -1 if side == "L" else 1
    yb = st["YB"]
    rh = 0.0300 if st["units"] == 1 else 0.0400
    yc = yb + 0.0040 + rh / 2
    xo = sx * 0.2245   # outer face
    a = P.anchor(f"A_RAIL_{side}_0", P.Frame((sx * 0.2210, yc, -0.002), Z, Y), (0.008, rh, 0.738), root,
                 meta=f"kind=slide,side={side.lower()},front=0,rear={REAR_RAIL_Z},len=0.738,extend=+z,travel=0.62")
    z0, z1 = REAR_RAIL_Z + 0.0015, -0.0022
    # outer member: a C channel (web + flanges)
    D.box("rail_web", (min(xo, xo - sx * 0.0009), yc - rh / 2, z0), (max(xo, xo - sx * 0.0009), yc + rh / 2, z1), "steel", a)
    for yy in (yc - rh / 2, yc + rh / 2 - 0.0009):
        D.box("rail_flange", (min(xo, xo - sx * 0.0060), yy, z0), (max(xo, xo - sx * 0.0060), yy + 0.0009, z1), "steel", a)
    # intermediate and inner members (the inner one fixed on the chassis side)
    xi = xo - sx * 0.0018
    D.box("rail_mid", (min(xi, xi - sx * 0.0018), yc - rh / 2 + 0.0030, z0 + 0.02), (max(xi, xi - sx * 0.0018), yc + rh / 2 - 0.0030, z1 - 0.01), "steel_dark", a)
    xc = sx * (XB + 0.0004)
    D.box("rail_inner", (min(xc, xc + sx * 0.0012), yc - rh / 2 + 0.0055, ZR + 0.01), (max(xc, xc + sx * 0.0012), yc + rh / 2 - 0.0055, ZF - 0.04), "steel", a)
    # brackets: vertical plates behind the front rail flange and in front of the rear one, with pins
    for zb, dz in ((-0.0022, -0.0015), (REAR_RAIL_Z + 0.0015, 0.0015)):
        bx0, bx1 = sorted((xo, sx * (D.HOLE_X + 0.009)))
        D.box("rail_bracket", (bx0, yb + 0.002, min(zb, zb + dz)), (bx1, yb + st["units"] * D.U - 0.002, max(zb, zb + dz)), "steel", a)
        for yy in D.ear_holes_y(st["units"]):
            P.cylinder("rail_pin", P.Frame((sx * D.HOLE_X, yb - st["YB"] + yy, zb), (0, 0, 1 if dz < 0 else -1), Y), 0.0035, 0.004, "steel_dark", 10,
                       a, z0=0.0)
    return a


# ====================================================================== chassis and insides

def chassis(st, root):
    yb, yt = st["YB"], st["YT"]
    # bottom pan and the two side walls (inset by the lid's lip)
    D.box("pan", (-XB + 0.0008, yb, ZR + 0.001), (XB - 0.0008, yb + T, ZF - 0.0045), "steel", root)
    for sx in (-1, 1):
        x0 = sx * (XB - 0.0008)
        D.box("side", (min(x0, x0 - sx * T), yb, ZR + 0.001), (max(x0, x0 - sx * T), yt - 0.0009, ZF - 0.0045), "steel", root)
    # rear wall with its openings
    io = st["io"]
    pw, ph = st["psu_size"]
    holes = [D.rect(px - pw / 2 - 0.0006, px + pw / 2 + 0.0006, py - ph / 2 - 0.0006, py + ph / 2 + 0.0006) for (px, py) in st["psus"]]
    holes.append(D.rr(io["ipmi"][0] - 0.0072, io["ipmi"][0] + 0.0072, io["ipmi"][1] - 0.0062, io["ipmi"][1] + 0.0062, 0.0006))
    holes.append(D.rr(io["vga"][0] - 0.0165, io["vga"][0] + 0.0165, io["vga"][1] - 0.0065, io["vga"][1] + 0.0065, 0.0012))
    ux = io["usb"][0][0]
    holes.append(D.rr(ux - 0.0072, ux + 0.0072, io["usb"][0][1] - 0.0038, io["usb"][1][1] + 0.0038, 0.0006))
    ex = [e[0] for e in io["eth"]]
    holes.append(D.rr(min(ex) - 0.0072, max(ex) + 0.0072, io["eth"][0][1] - 0.0062, io["eth"][0][1] + 0.0062, 0.0006))
    for (sx_, sy_, sw, sh) in st["slots"]:
        holes.append(D.rect(sx_ - sw / 2, sx_ + sw / 2, sy_ - sh / 2, sy_ + sh / 2))
    vx0, vx1, vy0, vy1 = st["vents"]
    nv = int((vx1 - vx0) / 0.0062)
    for k in range(nv):
        x = vx0 + (k + 0.5) * (vx1 - vx0) / nv
        holes.append(D.rect(x - 0.0015, x + 0.0015, vy0, vy1))
    D.zslab("rear_wall", PAINT, D.rect(-XB + 0.0008, XB - 0.0008, yb + 0.0002, yt - 0.0009), ZR, ZR + T, holes, root)
    # printed legends above the rear ports and PSUs
    lh = 0.0026
    legends = [("IPMI", io["ipmi"][0], io["ipmi"][1] + 0.0080), ("VGA", io["vga"][0], io["vga"][1] + 0.0083),
               ("USB", io["usb"][0][0] - 0.0098, io["usb"][0][1] + 0.0037)]
    legends += [(str(k + 1), ex_, ey_ + 0.0080) for k, (ex_, ey_) in enumerate(io["eth"])]
    for k, (px, py) in enumerate(st["psus"]):
        legends.append((f"PSU {k + 1}", px, py + ph / 2 + 0.0030 if st["units"] == 2 else py - ph / 2 - 0.0002))
    for txt, lx, ly in legends:
        if txt.startswith("PSU") and st["units"] == 1:
            continue   # the 1U PSUs fill the rear height: their numbers are on their labels
        LABELS.quad("legend", txt, P.Frame((lx, ly, ZR - 0.00005), NZ, Y), lh, root)
    D.zslab("vent_dark", "dark_plastic", D.rect(vx0, vx1, vy0, vy1), ZR + 0.004, ZR + 0.005, (), root)
    # slot covers (vented brackets, screwed from inside: the screw heads show)
    for (sx_, sy_, sw, sh) in st["slots"]:
        sl = [D.rect(sx_ - sw / 2 + 0.010 + k * 0.0085, sx_ - sw / 2 + 0.0135 + k * 0.0085, sy_ - sh * 0.30, sy_ + sh * 0.30)
              for k in range(int((sw - 0.020) / 0.0085))]
        D.zslab("slot_cover", "steel", D.rect(sx_ - sw / 2 + 0.0004, sx_ + sw / 2 - 0.0004, sy_ - sh / 2 + 0.0004, sy_ + sh / 2 - 0.0004),
                ZR - 0.0008, ZR + 0.0002, sl, root)
        D.zslab("slot_cover_dark", "dark_plastic", D.rect(sx_ - sw / 2 + 0.006, sx_ + sw / 2 - 0.006, sy_ - sh * 0.35, sy_ + sh * 0.35), ZR + 0.004, ZR + 0.0048, (), root)
    # rear I/O: IPMI, VGA, USB, LOM (on the board, through the rear wall)
    ipmi = P.Frame((io["ipmi"][0], io["ipmi"][1], ZR), NZ, Y)
    D.rj45_jack(ipmi, root, True)
    P.anchor("A_PORT_IPMI_0", ipmi, (0.016, 0.014, 0.02), root, meta="depth=0.012,rj45=1,latch=+up,net=bmc")
    D.led("A_LED_IPMI_0", P.Frame((io["ipmi"][0] - 0.0045, io["ipmi"][1] - 0.0052, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_green", root)
    vfr = P.Frame((io["vga"][0], io["vga"][1], ZR - 0.0004), NZ, Y)
    D.vga_port(vfr, root)
    P.anchor("A_PORT_VGA_0", vfr, (0.032, 0.013, 0.012), root, meta="depth=0.006,vga=1")
    for k, (ux_, uy_) in enumerate(io["usb"]):
        ufr = P.Frame((ux_, uy_, ZR), NZ, Y)
        D.usba_port(ufr, root)
        P.anchor(f"A_PORT_USBA_{k}", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=3.0")
    for k, (ex_, ey_) in enumerate(io["eth"]):
        efr = P.Frame((ex_, ey_, ZR), NZ, Y)
        D.rj45_jack(efr, root, True)
        P.anchor(f"A_PORT_ETH_{k}", efr, (0.0145, 0.012, 0.02), root, meta=f"depth=0.012,rj45=1,latch=+up,speed=10g,lom={k + 1}")
        D.led(f"A_LED_LINK_{k}", P.Frame((ex_ + 0.0042, ey_ - 0.0050, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_green", root,
              meta="colour=green,fn=link")
        D.led(f"A_LED_ACT_{k}", P.Frame((ex_ - 0.0042, ey_ - 0.0050, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_yellow", root,
              meta="colour=amber,fn=activity")
    # the rear ID LED (blue, matches the front)
    D.led("A_LED_ID_1", P.Frame((st["rear_id"][0], st["rear_id"][1], ZR - 0.0001), NZ, Y), 0.0030, 0.0030, "led_blue", root,
          meta="colour=blue,fn=identify", round_=True)


def front(st, root):
    """Ears with controls and thumbscrews, the drive cage face, the front panel (1U) and the trays."""
    sid = st["sid"]
    yb, yt = st["YB"], st["YT"]
    x0, x1, y0, y1 = st["cage"]
    bw, bh = st["bay_size"]
    holes = [D.rect(cx - bw / 2, cx + bw / 2, cy - bh / 2, cy + bh / 2) for (_, cx, cy) in st["bay_list"]]
    # the cage: one block with a tunnel per bay (dark steel), the backplane behind it
    D.zslab("cage", "steel_dark", D.rect(x0, x1, y0, y1), ZF - 0.012, ZF - 0.0005, holes, root)
    cd = 0.160 if st["bay_kind"] == "lff" else 0.115
    for (sx_) in (x0, x1):
        D.box("cage_wall", (sx_ - 0.0005, y0, ZF - cd), (sx_ + 0.0005, y1, ZF - 0.012), "steel_dark", root)
    for (_, cx, cy) in st["bay_list"]:
        D.box("bay_floor", (cx - bw / 2, cy - bh / 2 - 0.0005, ZF - cd), (cx + bw / 2, cy - bh / 2, ZF - 0.012), "steel_dark", root)
    D.box("backplane", (x0, y0, ZF - cd - 0.0016), (x1, y1, ZF - cd), "pcb_green", root)
    for (_, cx, cy) in st["bay_list"]:
        D.box("bp_conn", (cx - 0.012, cy - bh / 2 + 0.0012, ZF - cd), (cx + 0.004, cy - bh / 2 + 0.0058, ZF - cd + 0.004), "black_plastic", root)
    # the cage top (the front frame above the trays up to the lid)
    if y1 < yt - 0.0009:
        D.box("cage_top", (x0, y1, ZF - 0.012), (x1, yt - 0.0009, ZF - 0.0005), "steel_dark", root)
    if y0 > yb + 0.0002:
        D.box("cage_bot", (x0, yb + 0.0002, ZF - 0.012), (x1, y0, ZF - 0.0005), "steel_dark", root)
    for (n, cx, cy) in st["bay_list"]:
        drive_tray(st, n, cx, cy, root)
    # 1U: the front panel between the cage and the +x ear: logo, vents, VGA? (no: USB + pull tag + vents)
    if x1 < XB - 0.020:
        px0, px1 = x1, XB
        usb = (px1 - 0.012, yb + 0.0125)
        vents = [D.rect(px0 + 0.006 + k * 0.0046, px0 + 0.0086 + k * 0.0046, yb + 0.0215, yt - 0.0045) for k in range(int((px1 - px0 - 0.032) / 0.0046))]
        tag_slot = D.rect(px0 + 0.006, px0 + 0.060, yb + 0.0035, yb + 0.0075)
        D.zslab("front_panel", PAINT, D.rect(px0, px1, yb + 0.0002, yt - 0.0009), ZF - 0.0020, ZF, vents + [tag_slot, D.usba_outline(*usb)], root)
        D.zslab("front_vent_dark", "dark_plastic", D.rect(px0 + 0.004, px1 - 0.026, yb + 0.020, yt - 0.003), ZF - 0.008, ZF - 0.007, (), root)
        ufr = P.Frame((usb[0], usb[1], ZF), Z, Y)
        D.usba_port(ufr, root)
        P.anchor("A_PORT_USBA_FRONT_0", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=2.0")
        # pull-out service tag (luggage tag), pushed in: its edge with a finger notch shows in the slot
        D.box("tag_card", (px0 + 0.0065, yb + 0.0048, ZF - 0.060), (px0 + 0.0595, yb + 0.0062, ZF - 0.0002), "white_plastic", root)
        D.decal("tag_print", ATLAS, "tag", P.Frame((px0 + 0.033, yb + 0.0062 + 0.00005, ZF - 0.030), Y, NZ), 0.052, 0.019, root)
        D.decal("logo", ATLAS, "logo", P.Frame((px0 + 0.032, yb + 0.0145, ZF + 0.00005), Z, Y), 0.044, 0.011, root)
    # ears: control-panel blocks on the rack rails, thumbscrews at the rail holes
    for sx in (-1, 1):
        ex0, ex1 = sorted((sx * XB, sx * (D.EAR_W / 2 - 0.0003)))
        D.box("ear", (ex0, yb + 0.0003, 0.0), (ex1, yt - 0.0003, ZF - 0.0016), "steel_dark", root, bevel=0.0006, seg=1)
        D.box("ear_cover", (ex0 + 0.0004, yb + 0.0006, ZF - 0.0022), (ex1 - 0.0004, yt - 0.0006, ZF), "black_plastic", root, bevel=0.0012, seg=2)
        k = 0 if sx < 0 else 1
        tf = P.Frame((sx * D.HOLE_X, yb - st["YB"] + st["thumb_y"], ZF), Z, Y)
        a = P.anchor(f"A_SCREW_THUMB_{k}", tf, (0.012, 0.012, 0.012), root, meta="thread=M6,captive=1,len=0.032,turns=4")
        P.cylinder("thumb_well", tf.sub(0, 0, 0.0001), 0.0064, 0.0004, "dark_plastic", 20, root)
        thumbscrew(a, tf)
    # controls: -x ear (the viewer's right) power + USB on the 2U; +x ear ID button and status LEDs
    exm = -(XB + D.EAR_W / 2) / 2     # -x ear centre line (the thumbscrew sits at another height)
    exp = -exm
    ty = st["thumb_y"] + yb - st["YB"]
    if st["units"] == 1:
        pwr_y, id_y, led_ys = yt - 0.0075, yt - 0.0075, (yb + 0.0080, yb + 0.0040)
    else:
        pwr_y, id_y, led_ys = yt - 0.010, yt - 0.010, (yt - 0.026, yt - 0.034)
    pf = P.Frame((exm, pwr_y, ZF + 0.0002), Z, Y)
    a = D.button("A_BUTTON_POWER_0", pf, 0.0034, 0.0012, "black_plastic", root, ring_tag="grey_plastic",
                 meta="press=-z_local,travel=0.0012,fn=power,hold=4", height=0.0018)
    D.power_icon("pwr_icon", pf.sub(0, 0, 0.0010), 0.0018, 0.0005, "grey_plastic", a)
    a = P.anchor("A_LED_POWER_0", pf.sub(0, 0, 0.0004), (0.010, 0.010, 0.003), root, meta="colour=green,fn=power,ring=1")
    P.lathe("led_power", [(0.0046, -0.0004), (0.0050, -0.0004), (0.0050, 0.0003), (0.0046, 0.0003), (0.0046, -0.0004)], "led_green", pf, 20, a)
    idf = P.Frame((exp, id_y, ZF + 0.0002), Z, Y)
    a = D.button("A_BUTTON_ID_0", idf, 0.0030, 0.0010, "grey_plastic", root, ring_tag="dark_plastic",
                 meta="press=-z_local,travel=0.0010,fn=identify", height=0.0016)
    P.text3d("id_i", "i", 0.0034, 0.0001, "black_plastic", idf.sub(0, 0, 0.0008), "arialbd.ttf", parent=a)
    D.led("A_LED_ID_0", P.Frame((exp - 0.0052, id_y, ZF + 0.0002), Z, Y), 0.0020, 0.0020, "led_blue", root, round_=True,
          meta="colour=blue,fn=identify")
    D.led("A_LED_HEALTH_0", P.Frame((exp, led_ys[0], ZF + 0.0002), Z, Y), 0.0026, 0.0020, "led_green", root, meta="colour=green,fn=health")
    D.led("A_LED_FAULT_0", P.Frame((exp, led_ys[1], ZF + 0.0002), Z, Y), 0.0026, 0.0020, "led_yellow", root, meta="colour=amber,fn=fault")
    if st["units"] == 2:
        ufr = P.Frame((exm + 0.0008, yb + 0.016, ZF), Z, (1, 0, 0))   # vertical USB in the ear
        D.zslab("ear_usb_bezel", "dark_plastic", P.rrect(0.0082, 0.0160, 0.001, exm + 0.0008, yb + 0.016), ZF, ZF + 0.0004,
                [P.rrect(0.0058, 0.0131, 0.0005, exm + 0.0008, yb + 0.016)], root)
        D.usba_port(ufr, root)
        P.anchor("A_PORT_USBA_FRONT_0", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=2.0")
        D.led("A_LED_NET_0", P.Frame((exp, led_ys[1] - 0.008, ZF + 0.0002), Z, Y), 0.0026, 0.0020, "led_green", root, meta="colour=green,fn=network")


def bezel(st, root):
    """2U: the removable front bezel over the drives: a perforated face (alpha-cut hex tex), a top and bottom
    band with the logo, a lock at one end. Moving piece of A_BEZEL_0."""
    yb, yt = st["YB"], st["YT"]
    x0, x1 = -XB + 0.001, XB - 0.001
    zb0, zb1 = ZF + 0.0035, ZF + 0.022
    a = P.anchor("A_BEZEL_0", P.Frame((0, (yb + yt) / 2, zb1), Z, Y), (x1 - x0, yt - yb, zb1 - zb0), root,
                 meta="remove=+z,dist=0.06,lock=1,key=A_LOCK_0")
    # frame: a shallow tray with a big opening, the perforated sheet in it
    opening = D.rr(x0 + 0.012, x1 - 0.030, yb + 0.010, yt - 0.016, 0.004)
    D.zslab("bezel_face", "black_plastic", D.rr(x0, x1, yb + 0.0008, yt - 0.0008, 0.004), zb1 - 0.0025, zb1, [opening], a)
    for (yy0, yy1) in ((yb + 0.0008, yb + 0.0028), (yt - 0.0028, yt - 0.0008)):
        D.box("bezel_lip", (x0, yy0, zb0), (x1, yy1, zb1 - 0.0025), "black_plastic", a)
    for xx in (x0, x1 - 0.002):
        D.box("bezel_lip", (xx, yb + 0.0008, zb0), (xx + 0.002, yt - 0.0008, zb1 - 0.0025), "black_plastic", a)
    ox0, ox1, oy0, oy1 = x0 + 0.012, x1 - 0.030, yb + 0.010, yt - 0.016
    D.tiled_quads("bezel_mesh", "tex_server_bezel_mesh", P.Frame(((ox0 + ox1) / 2, (oy0 + oy1) / 2, zb1 - 0.0016), Z, Y), ox1 - ox0, oy1 - oy0,
                  0.07, 0.07, a, back=True)
    # logo band along the top
    D.decal("bezel_band", ATLAS, "bezel", P.Frame((0.0, yt - 0.0085, zb1 + 0.00005), Z, Y), 0.090, 0.090 * 120 / 768, a)
    # the lock at the +x end (the viewer's left), a key cylinder
    lf = P.Frame((x1 - 0.016, (yb + yt) / 2, zb1), Z, Y)
    P.lathe("bezel_lock", [(0, 0.0012), (0.0042, 0.0012), (0.0046, 0.0004), (0.0046, -0.002), (0, -0.002)], "nickel", lf, 20, a)
    D.box("bezel_keyway", (x1 - 0.0168, (yb + yt) / 2 - 0.0020, zb1 + 0.0012), (x1 - 0.0152, (yb + yt) / 2 + 0.0020, zb1 + 0.0014), "dark_plastic", a)
    P.anchor("A_LOCK_0", lf.sub(0, 0, 0.0012), (0.010, 0.010, 0.006), a, meta="key=1,turn=90")
    # the bezel's own light bar (status) at the bottom
    D.led("A_LED_BEZEL_0", P.Frame((0.0, yb + 0.0055, zb1 + 0.0001), Z, Y), 0.120, 0.0012, "led_blue", a, meta="colour=blue,fn=status")
    return a


def interior(st, root):
    """Under the lid: the board, CPUs with heatsinks, 16 DIMMs, the fan wall, the air shroud, risers, PSU cage."""
    yb, yt = st["YB"], st["YT"]
    sid = st["sid"]
    one_u = st["units"] == 1
    cd = 0.160 if st["bay_kind"] == "lff" else 0.115
    # fan wall (just behind the backplane)
    fs, fd = st["fan"], st["fan_d"]
    zfan = ZF - cd - 0.030 - fd / 2
    n = st["fans"]
    pitch = (2 * XB - 0.030) / n
    fy = yb + T + 0.0004 + fs / 2
    D.box("fan_bracket", (-XB + 0.002, yb + T, zfan - fd / 2 - 0.004), (XB - 0.002, yb + T + 0.004, zfan + fd / 2 + 0.004), "steel_dark", root)
    for k in range(n):
        fx = -XB + 0.015 + pitch * (k + 0.5)
        a = P.anchor(f"A_FAN_{k}", P.Frame((fx, fy, zfan), Z, Y), (fs, fs, fd), root,
                     meta=f"axis=z,spin=1,rpm={9000 if one_u else 6500},hotswap=1,pull=+y")
        D.server_fan(a, fs, fd, blades=5 if one_u else 7, parent=root, segs=14 if one_u else 16)
        # the hot-swap holder's handle on top of each fan
        D.box("fan_handle", (fx - fs * 0.30, fy + fs / 2, zfan - 0.003), (fx + fs * 0.30, min(fy + fs / 2 + 0.003, yt - 0.0012), zfan + 0.003),
              "black_plastic", root)
    # the board
    zb0, zb1 = zfan - fd / 2 - 0.012, ZR + 0.004
    by = yb + T + 0.0030
    pw, ph = st["psu_size"]
    outline = [(-XB + 0.004, zb1), (XB - 0.004, zb1), (XB - 0.004, zb0), (-XB + 0.004, zb0)]
    if one_u:   # the PSU cage takes the rear +x corner
        cx_ = st["psus"][1][0] - pw / 2 - 0.003
        outline = [(-XB + 0.004, zb1), (cx_, zb1), (cx_, ZR + 0.200), (XB - 0.004, ZR + 0.200), (XB - 0.004, zb0), (-XB + 0.004, zb0)]
    D.yslab("board", "pcb_green", outline, by, by + 0.0016, (), root)
    btop = by + 0.0016
    # CPU groups: [4 DIMMs][socket + heatsink][4 DIMMs] x 2
    zc = (zb0 + ZR + 0.25) / 2 if one_u else (zb0 + ZR + 0.22) / 2
    zc = min(zc, zb0 - 0.085)
    sink_h = (yt - 0.0045) - (btop + 0.0065) if one_u else 0.058
    sh_y = yt - 0.0024 if one_u else btop + sink_h + 0.0095
    for g, gx in enumerate((-0.088, 0.088)):
        # socket and retention frame
        D.box("socket", (gx - 0.038, btop, zc - 0.045), (gx + 0.038, btop + 0.0045, zc + 0.045), "steel_dark", root)
        # heatsink: copper base and a fin stack along z (airflow)
        D.box("sink_base", (gx - 0.040, btop + 0.0045, zc - 0.052), (gx + 0.040, btop + 0.0065, zc + 0.052), "copper", root)
        nfin = 26 if one_u else 30
        comb = D.comb_outline(nfin, 0.080 / nfin, 0.0005, 0.0, sink_h, 0.0012)
        P.slab("sink_fins", comb, 0.104, "alu", P.Frame((gx, btop + 0.0065, zc), Z, Y), parent=root)
        for (dx, dz) in ((-0.034, -0.046), (0.034, -0.046), (-0.034, 0.046), (0.034, 0.046)):
            P.cylinder("sink_screw", P.Frame((gx + dx, btop + 0.0065 + sink_h + 0.0005, zc + dz), Y, Z), 0.0028, 0.002, "steel", 10, root)
        # DIMMs: 4 each side, slots along z
        for side in (-1, 1):
            for k in range(4):
                dx = gx + side * (0.050 + k * 0.0078)
                D.box("dimm_slot", (dx - 0.0030, btop, zc - 0.0735), (dx + 0.0030, btop + 0.0048, zc + 0.0735), "black_plastic", root)
                for zz in (zc - 0.074, zc + 0.074):
                    D.box("dimm_latch", (dx - 0.0028, btop + 0.0048, zz - 0.0022), (dx + 0.0028, btop + 0.0115, zz + 0.0022), "white_plastic", root)
                d_y0 = btop + 0.0030
                d_h = min(0.0312, sh_y - 0.0009 - d_y0)
                D.box("dimm", (dx - 0.00065, d_y0, zc - 0.0667), (dx + 0.00065, d_y0 + d_h, zc + 0.0667), "pcb_green", root)
                for s2 in (-1, 1):
                    P.quad("dimm_face", P.Frame((dx + s2 * 0.00075, d_y0 + d_h / 2, zc), (s2, 0, 0), Y), 0.1335, d_h,
                           ATLAS.tag, root, uv=ATLAS.uv("dimm"))
    # air shroud: the moving piece over the CPUs and DIMMs
    sh_z0, sh_z1 = zc - 0.080, zc + 0.080
    a = P.anchor("A_SHROUD_0", P.Frame((0, sh_y, zc), Z, Y), (0.40, 0.006, sh_z1 - sh_z0), root, meta="lift=+y,dist=0.06,order=1")
    D.yslab("shroud_top", "black_plastic", D.rr(-0.200, 0.200, sh_z0, sh_z1, 0.004), sh_y - 0.0007, sh_y + 0.0007, (), a)
    for xs in (-0.200, -0.006, 0.006, 0.200):
        D.box("shroud_wall", (xs - 0.0006, btop + 0.012, sh_z0), (xs + 0.0006, sh_y - 0.0007, sh_z1), "black_plastic", a)
    D.decal("shroud_print", ATLAS, "shroud", P.Frame((0.0, sh_y + 0.0008, zc), Y, NZ), 0.12, 0.03, a)
    # PSU cage and the power distribution board
    for (px, py) in st["psus"]:
        D.box("psu_cage", (px - pw / 2 - 0.0016, yb + T, ZR + 0.001), (px - pw / 2 - 0.0008, py + ph / 2 + 0.001, ZR + 0.190), "steel", root)
        D.box("psu_cage", (px + pw / 2 + 0.0008, yb + T, ZR + 0.001), (px + pw / 2 + 0.0016, py + ph / 2 + 0.001, ZR + 0.190), "steel", root)
        D.box("pdb", (px - pw / 2, yb + T, ZR + 0.196), (px + pw / 2, py + ph / 2, ZR + 0.198), "pcb_green", root)
        D.box("pdb_slot", (px - 0.020, py - 0.003, ZR + 0.194), (px + 0.020, py + 0.003, ZR + 0.196), "black_plastic", root)
    # PCIe risers: a riser card standing up with a horizontal card on it, at each slot group
    groups = {}
    for (sx_, sy_, sw, sh) in st["slots"]:
        groups.setdefault(round(sx_, 3), []).append((sy_, sw))
    for gx, items in groups.items():
        sw = items[0][1]
        ys = [s[0] for s in items]
        D.box("riser", (gx - sw / 2 + 0.004, max(btop, min(ys) - 0.010), ZR + 0.012), (gx - sw / 2 + 0.006, max(ys) + 0.010, ZR + 0.120), "pcb_green", root)
        for yy in ys[:1]:
            D.box("pcie_card", (gx - sw / 2 + 0.006, yy - 0.0008, ZR + 0.006), (gx + sw / 2 - 0.004, yy + 0.0008, ZR + 0.160), "pcb_green", root)
            D.box("pcie_chip", (gx - 0.012, yy + 0.0008, ZR + 0.06), (gx + 0.012, yy + 0.0028, ZR + 0.09), "alu_dark", root)
    # a few cables: SAS from the backplane to the board, and the fan board ribbon
    for sx in (-1, 1):
        P.tube("sas_cable", P.smooth_path([(sx * 0.196, yb + 0.012, ZF - cd - 0.002), (sx * 0.2085, yb + 0.010, ZF - cd - 0.020),
                                           (sx * 0.2085, yb + 0.008, zfan - fd / 2 - 0.008), (sx * 0.185, btop + 0.003, zfan - fd / 2 - 0.040)], 4),
               0.0028, "black_plastic", root, 6)
    # the BMC chip, the chipset heatsink, the CMOS battery, LOM controller
    D.box("pch_sink", (-0.030, btop, zc - 0.180), (0.010, btop + 0.010 if one_u else btop + 0.020, zc - 0.140), "alu", root)
    D.box("bmc", (-0.110, btop, ZR + 0.060), (-0.095, btop + 0.0015, ZR + 0.075), "chip_black", root)
    P.cylinder("cmos", P.Frame((-0.070, btop + 0.0016, ZR + 0.090), Y, Z), 0.010, 0.0032, "nickel", 20, root, z0=0.0)


def lid(st, root):
    """The top cover (moving piece of A_LID_0, slide=-z): a sheet with side lips, a release latch, the service
    label. It covers the chassis from just behind the front frame to the rear."""
    yt = st["YT"]
    z0, z1 = ZR, ZF - 0.014
    a = P.anchor("A_LID_0", P.Frame((0, yt, (z0 + z1) / 2), Z, Y), (2 * XB, 0.004, z1 - z0), root,
                 meta="slide=-z,dist=0.020,lift=+y,latch=1")
    lx, lz = 0.0, z1 - 0.080
    latch = D.rr(lx - 0.035, lx + 0.035, lz - 0.014, lz + 0.014, 0.004)
    D.yslab("lid_top", "steel", D.rect(-XB, XB, z0, z1), yt - 0.0008, yt, [latch], a)
    for sx in (-1, 1):
        x0 = sx * XB
        D.box("lid_lip", (min(x0, x0 - sx * 0.0007), yt - 0.0070, z0 + 0.010), (max(x0, x0 - sx * 0.0007), yt - 0.0008, z1 - 0.004), "steel", a)
    D.box("lid_lip_front", (-XB + 0.001, yt - 0.0050, z1 - 0.0008), (XB - 0.001, yt - 0.0008, z1), "steel", a)
    # the release latch: a black handle flush in its pocket, with a grip and a lock slot
    D.yslab("lid_latch", "black_plastic", D.rr(lx - 0.0345, lx + 0.0345, lz - 0.0135, lz + 0.0135, 0.0035), yt - 0.0012, yt - 0.0001, (), a)
    for k in range(5):
        D.box("lid_latch_rib", (lx - 0.020 + k * 0.009, yt - 0.0002, lz - 0.008), (lx - 0.018 + k * 0.009, yt, lz + 0.008), "dark_plastic", a)
    P.cylinder("lid_lock", P.Frame((lx + 0.026, yt - 0.0001, lz), Y, Z), 0.0035, 0.0002, "nickel", 16, a)
    D.decal("lid_label", ATLAS, "lid", P.Frame((0.040, yt + 0.00005, (z0 + z1) / 2 + 0.02), Y, NZ), 0.24, 0.16, a)


def build(sid):
    P.reset()
    textures()
    D.hex_perf_texture("server_bezel_mesh", 512, 512, 0.07, 0.07, 0.0042, 0.0016, web=(0.07, 0.07, 0.075))
    st = layout(sid)
    st["sid"] = sid
    root = c.root(sid)
    D.ROOT[0] = root
    chassis(st, root)
    front(st, root)
    interior(st, root)
    lid(st, root)
    for k in range(2):
        psu(st, k, root)
    if st.get("bezel"):
        bezel(st, root)
    slide_rail(st, "L", root)
    slide_rail(st, "R", root)
    yb, yt = st["YB"], st["YT"]
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZF + ZR) / 2), (2 * XB, yt - yb, DEPTH), root)
    P.anchor("A_HIT_1", (-(XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    P.anchor("A_HIT_2", ((XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    extra = (f"frame: rack device, {st['units']}U, chassis 0.434 x {st['h']} x 0.700, front z={ZF}, rear z={ZR:.3f}, "
             f"bottom y={yb:.5f}, top y={yt:.5f}")
    return D.finish(root, sid, preview_views=((25, 18), (155, 25)), beauty_views=((22, 14), (160, 18)), size=(1100, 700),
                    samples=36, extra=extra,
                    more_beauty=[(((-28, 10),), dict(target=(-0.12, yb + 0.02, ZF), dist=0.40)),
                                 (((200, 12),), dict(target=(0.0, yb + 0.02, ZR), dist=0.50)),
                                 (((25, 55),), dict(hide=("@A_LID_0",))),
                                 (((-20, 60),), dict(hide=("@A_LID_0", "@A_SHROUD_0")))])
