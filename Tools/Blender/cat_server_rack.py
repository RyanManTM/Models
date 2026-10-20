"""
cat_server_rack: the rack gear of catalogue 18 (build_cat_server.py).

Every model here uses the rack device frame of datacenter_common.py (docs/reports/datacentre.md): origin at the
centre of the front mounting plane, at the bottom of the device's U space, +Z out of the front, +Y up, the body
towards -Z, so it installs directly at a rack's A_RACKU_n. Fixed ears carry A_SCREW_RACK_n at their holes (+Z,
meta thread=M6,cage=1); the servers carry the captive thumbscrews A_SCREW_THUMB_n and the slide rails A_RAIL_L/R_0 of
server_1u / server_2u (datacenter_server.py, reused as is). The rack's rear rails are at z = -0.740.

  srv_strata_sg840_4u   4U GPU server: 8 front GPU sleds A_SLED_n, a 10-fan wall, 4 CRPS PSUs A_PSU_n, the lid A_LID_0
  srv_strata_sr224_2u   2U storage server: 24 vertical 2.5" bays A_BAY_n, 2 PSUs, the lid
  srv_linkwave_ls4804x  1U switch: 48 x RJ45 A_PORT_ETH_n + 4 x SFP+ A_PORT_SFP_n
  srv_linkwave_ls1600x  1U aggregation switch: 16 x SFP+ A_PORT_SFP_n, a management RJ45
  srv_strata_shelf_1u   1U cantilever shelf (A_SHELF_0 is its load surface)
  srv_strata_blank_1u / srv_strata_blank_2u   blanking panels
  srv_strata_cma        cable management arm on the +x slide rail's rear ends (A_ARM_0, A_ARM_1@A_ARM_0)
  srv_strata_kvm_1u     1U KVM console drawer: A_DRAWER_0 (pull=+z), the LCD lid A_LID_0@A_DRAWER_0 (hinge=x) with
                        A_SCREEN_0@A_LID_0
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
REAR_RAIL_Z = -0.740
GREEN = P.PALETTE_TAG

ATLAS = D.Atlas("cat_server_rack", 2048, 2048)
ATLAS.add("labels", 0, 1536, 1024, 512)
ATLAS.add("lw48", 1024, 1920, 512, 128)
ATLAS.add("lw16", 1536, 1920, 512, 128)
ATLAS.add("rating48", 1024, 1600, 512, 300)
ATLAS.add("rating16", 1536, 1600, 512, 300)
ATLAS.add("strata", 1024, 1460, 512, 128)
ATLAS.add("sg840", 1536, 1460, 512, 128)
ATLAS.add("sr224", 1024, 1320, 512, 128)
ATLAS.add("kvm_badge", 1536, 1320, 512, 128)
ATLAS.add("kbd", 0, 1000, 1024, 384)
ATLAS.add("shelf_label", 1024, 1180, 512, 128)
ATLAS.add("verdia", 1536, 1180, 512, 128)
ATLAS.add("drive_v", 0, 400, 192, 560)
ATLAS.add("gpu_label", 192, 820, 512, 140)
ATLAS.add("kvm_label", 704, 760, 512, 200)
ATLAS.add("cma_label", 1216, 1020, 384, 140)
ATLAS.add("screen", 1216, 400, 768, 432)
ATLAS.add("touch", 192, 400, 256, 160)
ATLAS.add("blank_logo", 448, 400, 384, 96)
LABELS = D.Labels(ATLAS, "labels", 128, 32, [str(k) for k in range(1, 53)] + [
    "CONSOLE", "MGMT", "USB", "SFP+ 10G", "PWR", "SYS", "FAN", "RESET", "LINK/ACT", "100-240V~ 1A", "PSU 1", "PSU 2",
    "PSU 3", "PSU 4", "IPMI", "VGA", "LOM", "GPU 1", "GPU 2", "GPU 3", "GPU 4", "GPU 5", "GPU 6", "GPU 7", "GPU 8",
    "10G SFP+", "PS1", "PS2", "LCD", "KVM", "USB-B", "100-240V~ 2A", "ID", "STACK", "1G MGMT"], size=0.6)

U = D.U
H1 = 0.0436


def ybt(units, h=None):
    """Bottom and top of a chassis centred in its U space."""
    h = h if h is not None else units * U - 0.0009
    yb = (units * U - h) / 2
    return yb, yb + h


# ====================================================================== artwork

def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=None, name="cat_server_rack")
    LABELS.draw(art)
    silver = (0.80, 0.82, 0.85)
    ink = (0.08, 0.08, 0.09)
    for reg, model, sub in (("lw48", "LS-4804X", "48G + 4 SFP+"), ("lw16", "LS-1600X", "16 x 10G SFP+")):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.10, 0.11, 0.12))
        art.text("LINKWAVE", x + 24, y + 74, 54, (0.92, 0.93, 0.95), "segoeuib.ttf", spacing=1.1)
        art.text(f"{model}  {sub}", x + 26, y + 28, 26, (0.35, 0.75, 0.95), "arialbd.ttf", maxw=w - 40)
    for reg, model, lines in (("rating48", "LS-4804X", ["48 x 10/100/1000BASE-T + 4 x 10G SFP+", "Input: 100-240V~ 50/60Hz 1.0A",
                                                        "MAC: 5C:A1:F0:3E:90:12", "S/N: LW48X2612A0457"]),
                              ("rating16", "LS-1600X", ["16 x 10G SFP+ + 1 x 1G management", "Input: 100-240V~ 50/60Hz 2 x 1.0A",
                                                        "MAC: 5C:A1:F0:51:0C:7A", "S/N: LW16X2612B0088"])):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.94, 0.94, 0.93))
        art.text("LINKWAVE", x + 18, y + h - 44, 34, ink, "segoeuib.ttf")
        art.text("Model: " + model, x + 18, y + h - 84, 22, ink, "arialbd.ttf")
        for k, s in enumerate(lines + ["Class A ITE. Made in Taiwan."]):
            art.text(s, x + 18, y + h - 116 - k * 30, 20, ink, "arial.ttf", maxw=w - 36)
        art.code128ish(len(model) * 77, x + 18, y + 10, 300, 30, ink)
    for reg, word, sub in (("strata", "STRATA", None), ("sg840", "STRATA", "SG840"), ("sr224", "STRATA", "SR224"),
                           ("kvm_badge", "STRATA", "KMM 18.5\"")):
        x, y, w, h = ATLAS.reg[reg]
        art.rect(x, y, w, h, (0.03, 0.03, 0.035))
        if sub:
            art.text(word, x + 30, y + h / 2, 68, silver, "segoeuib.ttf", valign="CENTER", spacing=1.25)
            art.text(sub, x + w - 26, y + h / 2, 44, (0.25, 0.6, 0.95), "segoeuib.ttf", align="RIGHT", valign="CENTER")
        else:
            art.text(word, x + w / 2, y + h / 2, 84, silver, "segoeuib.ttf", align="CENTER", valign="CENTER", spacing=1.25)
    x, y, w, h = ATLAS.reg["verdia"]
    art.rect(x, y, w, h, (0.05, 0.05, 0.05))
    art.text("VERDIA", x + 26, y + h / 2, 70, (0.46, 0.73, 0.0), "segoeuib.ttf", valign="CENTER", spacing=1.2)
    art.text("DC 48", x + w - 24, y + h / 2, 40, (0.85, 0.85, 0.85), "arialbd.ttf", align="RIGHT", valign="CENTER")
    x, y, w, h = ATLAS.reg["gpu_label"]
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    art.text("VERDIA DC 48  48GB GDDR6  passive  350W", x + 16, y + h - 34, 20, ink, "arialbd.ttf", maxw=w - 32)
    art.text("S/N 1652226013455   P/N 900-2G133", x + 16, y + h - 64, 18, ink, "arial.ttf")
    art.code128ish(4813, x + 16, y + 12, 330, 36, ink)
    # vertical 2.5" drive label (reads bottom to top on the tray's side)
    x, y, w, h = ATLAS.reg["drive_v"]
    art.rect(x, y, w, h, (0.9, 0.9, 0.88))
    art.rect(x, y + h - 60, w, 60, (0.12, 0.14, 0.2))
    art.text("STRATA", x + w / 2, y + h - 30, 30, (0.9, 0.92, 0.95), "segoeuib.ttf", align="CENTER", valign="CENTER")
    art.text("3.84TB", x + w / 2, y + h - 110, 36, ink, "arialbd.ttf", align="CENTER")
    art.text("NVMe U.2", x + w / 2, y + h - 150, 26, ink, "arial.ttf", align="CENTER")
    art.text("SSD", x + w / 2, y + h - 184, 26, ink, "arial.ttf", align="CENTER")
    for k in range(18):
        art.rect(x + 30, y + 40 + k * 14, w - 60, 7 if k % 3 else 10, ink)
    # shelf load label
    x, y, w, h = ATLAS.reg["shelf_label"]
    art.rect(x, y, w, h, (0.95, 0.8, 0.1))
    art.rect(x + 6, y + 6, w - 12, h - 12, (0.98, 0.84, 0.12))
    art.text("MAX LOAD 25 kg / 55 lb", x + w / 2, y + 80, 34, ink, "arialbd.ttf", align="CENTER")
    art.text("distribute evenly  -  front mount only", x + w / 2, y + 34, 22, ink, "arial.ttf", align="CENTER")
    x, y, w, h = ATLAS.reg["cma_label"]
    art.rect(x, y, w, h, (0.93, 0.93, 0.92))
    art.text("STRATA  CMA 1U", x + 16, y + h - 36, 24, ink, "arialbd.ttf")
    art.text("Attach to the right-hand rail", x + 16, y + h - 70, 18, ink, "arial.ttf")
    art.text("<- INNER      OUTER ->", x + 16, y + h - 100, 18, ink, "arialbd.ttf")
    art.code128ish(3310, x + 16, y + 10, 240, 20, ink)
    x, y, w, h = ATLAS.reg["kvm_label"]
    art.rect(x, y, w, h, (0.94, 0.94, 0.93))
    art.text("STRATA  KMM 18.5\" LCD CONSOLE", x + 16, y + h - 34, 22, ink, "arialbd.ttf")
    for k, s in enumerate(["1366 x 768  -  US keyboard + touchpad", "Input: 100-240V~ 50/60Hz 0.5A", "S/N: STK1852611C2290"]):
        art.text(s, x + 16, y + h - 70 - k * 30, 18, ink, "arial.ttf")
    art.code128ish(1852, x + 16, y + 10, 300, 30, ink)
    x, y, w, h = ATLAS.reg["blank_logo"]
    art.text("STRATA", x + w / 2, y + h / 2, 58, (0.55, 0.56, 0.58), "segoeuib.ttf", align="CENTER", valign="CENTER", spacing=1.25)
    keyboard_art(art)
    screen_art(art)
    art.render(ATLAS.file)
    art.dispose()


KEY_ROWS = [
    (["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Del"], [1] * 14),
    (["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Bksp"], [1] * 13 + [2]),
    (["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"], [1.5] + [1] * 12 + [1.5]),
    (["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"], [1.75] + [1] * 11 + [2.25]),
    (["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"], [2.25] + [1] * 10 + [2.75]),
    (["Ctrl", "Fn", "Alt", "", "Alt", "Ctrl", "<", "v", ">"], [1.5, 1, 1.5, 6, 1.5, 1.5, 1, 1, 1]),
]
KB_UNITS = 15.0


def keyboard_layout(w, h):
    """[(x0, x1, y0, y1, legend)] for the keys of a w x h keyboard (local x to the user's right, y away from the
    user), in the keyboard's own units."""
    out = []
    u = w / KB_UNITS
    rows = len(KEY_ROWS)
    rh = h / rows
    for r, (keys, widths) in enumerate(KEY_ROWS):
        sc = KB_UNITS / sum(widths)
        x = 0.0
        y1 = h - r * rh
        for k, kw in zip(keys, widths):
            ww = kw * u * sc
            out.append((x, x + ww, y1 - rh, y1, k))
            x += ww
    return out


def keyboard_art(art):
    x, y, w, h = ATLAS.reg["kbd"]
    for (x0, x1, y0, y1, k) in keyboard_layout(w, h):
        if k:
            art.text(k, x + x0 + 9, y + y1 - 14, 13 if len(k) > 1 else 17, (0.86, 0.87, 0.89), "arialbd.ttf", valign="TOP")
    x, y, w, h = ATLAS.reg["touch"]
    art.rect(x, y, w, h, (0.10, 0.10, 0.11))
    art.rect(x + 10, y + 34, w - 20, h - 44, (0.16, 0.16, 0.17))
    art.rect(x + 10, y + 6, w / 2 - 12, 22, (0.13, 0.13, 0.14))
    art.rect(x + w / 2 + 2, y + 6, w / 2 - 12, 22, (0.13, 0.13, 0.14))


def screen_art(art):
    """The LCD showing a server console (what the preview shows; the game drives A_SCREEN_0 itself)."""
    x, y, w, h = ATLAS.reg["screen"]
    art.rect(x, y, w, h, (0.02, 0.03, 0.06))
    art.rect(x, y + h - 30, w, 30, (0.12, 0.22, 0.45))
    art.text("STRATA KVM  -  [01] SG840-A   [02] SR224-B   [03] SR110-C", x + 12, y + h - 21, 16, (0.9, 0.92, 0.95), "consola.ttf")
    lines = ["strata login: admin", "Password:", "Last login: Tue Oct 20 09:14:02 on tty1",
             "[admin@sg840-a ~]$ verdia-smi --query", "GPU 0  DC 48   41C   P0   212W / 350W   61%",
             "GPU 1  DC 48   43C   P0   224W / 350W   64%", "GPU 2  DC 48   40C   P0   198W / 350W   58%",
             "GPU 3  DC 48   44C   P0   231W / 350W   66%", "[admin@sg840-a ~]$ _"]
    for k, s in enumerate(lines):
        art.text(s, x + 14, y + h - 62 - k * 30, 18, (0.75, 0.9, 0.78), "consola.ttf", maxw=w - 28)


# ====================================================================== common pieces

def ear_plate(root, units, tag, slots=None, t=0.0020, body_w=0.440, h=None, z_face=None, holes_extra=None):
    """Flat 19" ears (D.ears) with the A_SCREW_RACK_n anchors."""
    return D.ears(root, units, z_face if z_face is not None else t, tag, body_w=body_w, t=t, h=h, slots=slots)


def rack_screw_anchors(root, ys, z, start=0):
    n = start
    for sx in (-1, 1):
        for y in ys:
            P.anchor(f"A_SCREW_RACK_{n}", P.Frame((sx * D.HOLE_X, y, z), Z, Y), (0.012, 0.010, 0.006), root,
                     meta=f"thread=M6,cage=1,side={'r' if sx > 0 else 'l'}")
            n += 1
    return n


def cage_nut_screw(fr, root, tag="nickel"):
    """An M6 pan-head rack screw with its plastic cup washer (looks; the blanks ship with them fitted)."""
    P.lathe("cup_washer", [(0.0, 0.0), (0.0062, 0.0), (0.0062, 0.0008), (0.0040, 0.0016), (0.0, 0.0016)], "black_plastic", fr, 20, root)
    P.lathe("rack_screw", [(0.0, 0.0012), (0.0050, 0.0012), (0.0052, 0.0020), (0.0044, 0.0040), (0.0, 0.0044)], tag, fr, 20, root)
    for a in (0, 90):
        P.cube("rack_screw_x", (0, 0, 0.0043), (0.0060, 0.0011, 0.0006), "dark_plastic", fr.sub(0, 0, 0, Z, (math.cos(math.radians(a)), math.sin(math.radians(a)), 0)), root)


# ====================================================================== blanking panels

def build_blank(units):
    mid = f"srv_strata_blank_{units}u"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    yb, yt = ybt(units, units * U - 0.0008)
    t = 0.0012
    ys = D.ear_holes_y(units) if units == 1 else [D.HOLES_IN_U[0], (units - 1) * U + D.HOLES_IN_U[2]]
    if units == 1:
        ys = [D.HOLES_IN_U[0], D.HOLES_IN_U[2]]
    holes = [P.stadium(0.0100, 0.0068, sx * D.HOLE_X, y) for sx in (-1, 1) for y in ys]
    D.zslab("panel", "paint_black", D.rr(-D.EAR_W / 2, D.EAR_W / 2, yb, yt, 0.0012), 0.0, t, holes, root)
    # the top and bottom flanges bent back (stiffness), and the bends
    for (y0, y1) in ((yb, yb + t), (yt - t, yt)):
        D.box("flange", (-0.2180, y0, -0.0120), (0.2180, y1, 0.0), "paint_black", root)
    for y in (yb + t / 2, yt - t / 2):
        P.cylinder("bend", P.Frame((0, y, 0.0), X, Y), 0.0010, 0.436, "paint_black", 6, root)
    # pressed stiffening ribs along the face
    nrib = 2 if units == 1 else 4
    for k in range(nrib):
        y = yb + (yt - yb) * (k + 1) / (nrib + 1)
        P.slab("rib", P.stadium(0.360, 0.0030, 0, 0), 0.0008, "paint_black", P.Frame((0.0, y, t + 0.0002), Z, Y), parent=root)
    D.decal("logo", ATLAS, "blank_logo", P.Frame((0.17, (yb + yt) / 2 + (0.0 if units == 1 else 0.012), t + 0.00005), Z, Y), 0.040, 0.010, root)
    # the screws and cup washers fitted
    n = 0
    for sx in (-1, 1):
        for y in ys:
            fr = P.Frame((sx * D.HOLE_X, y, t), Z, Y)
            a = P.anchor(f"A_SCREW_RACK_{n}", fr, (0.012, 0.010, 0.006), root,
                         meta=f"thread=M6,cage=1,side={'r' if sx > 0 else 'l'},fitted=1")
            cage_nut_screw(fr, a)
            n += 1
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, -0.004), (D.EAR_W, yt - yb, 0.016), root)
    return D.finish(root, mid, preview_views=((25, 12), (150, 20)), beauty_views=((20, 10), (160, 18)), size=(1000, 500 if units == 1 else 600),
                    samples=32, extra=f"frame: rack device, {units}U blanking panel, face z={t}, flanges to z=-0.012")


def build_blank_1u():
    return build_blank(1)


def build_blank_2u():
    return build_blank(2)


# ====================================================================== cantilever shelf

def build_shelf():
    mid = "srv_strata_shelf_1u"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    t = 0.0020
    yb, yt = ybt(1, U - 0.0008)
    depth = 0.400
    xw = 0.2220                  # half width of the tray (inside the rails' 0.450 opening)
    ys = [D.HOLES_IN_U[0], D.HOLES_IN_U[2]]
    # front panel = ears: a full-width plate with a big cut-out above the tray lip
    holes = [P.stadium(0.0100, 0.0068, sx * D.HOLE_X, y) for sx in (-1, 1) for y in ys]
    D.zslab("front", "paint_black", D.rr(-D.EAR_W / 2, D.EAR_W / 2, yb, yt, 0.0012), 0.0, t, holes, root)
    # the tray: a 1.5 mm plate with vent slots, bent up at the sides and the rear
    tf = yb + 0.0015
    slots = []
    for i in range(9):
        for j in range(5):
            x = -0.180 + i * 0.045
            z = -0.060 - j * 0.065
            slots.append(P.stadium(0.032, 0.006, x, z))
    D.yslab("tray", "paint_black", D.rect(-xw, xw, -depth, 0.0), yb, tf, slots, root)
    for sx in (-1, 1):
        D.box("tray_side", (min(sx * xw, sx * (xw - 0.0015)), yb, -depth), (max(sx * xw, sx * (xw - 0.0015)), yb + 0.020, 0.0), "paint_black", root)
        # gusset: a triangle from the front panel down the side lip
        D.xslab("gusset", "paint_black", [(0.0, yb), (0.0, yt - 0.002), (-0.035, yb + 0.020), (-0.035, yb)],
                sx * (xw - 0.0015) - 0.00075, sx * (xw - 0.0015) + 0.00075, (), root)
    D.box("tray_rear", (-xw, yb, -depth), (xw, yb + 0.015, -depth + 0.0015), "paint_black", root)
    # rubber anti-slip strips on the tray
    for x in (-0.150, 0.150):
        D.box("rubber_strip", (x - 0.010, tf, -depth + 0.030), (x + 0.010, tf + 0.0008, -0.030), "rubber", root)
    D.decal("load_label", ATLAS, "shelf_label", P.Frame((0.0, tf + 0.00005, -0.022), Y, NZ), 0.072, 0.018, root)
    D.decal("logo", ATLAS, "strata", P.Frame((0.150, (yb + yt) / 2, t + 0.00005), Z, Y), 0.044, 0.011, root)
    n = 0
    for sx in (-1, 1):
        for y in ys:
            P.anchor(f"A_SCREW_RACK_{n}", P.Frame((sx * D.HOLE_X, y, t), Z, Y), (0.012, 0.010, 0.006), root,
                     meta=f"thread=M6,cage=1,side={'r' if sx > 0 else 'l'}")
            n += 1
    P.anchor("A_SHELF_0", P.Frame((0.0, tf + 0.0008, -depth / 2), Y, NZ), (2 * xw - 0.004, depth - 0.004, 0.004), root,
             meta=f"surface=1,w={2 * xw - 0.004:.3f},d={depth - 0.004:.3f},load_kg=25,front_mount=1")
    P.anchor("A_HIT_0", (0, yb + 0.010, -depth / 2), (2 * xw, 0.020, depth), root)
    P.anchor("A_HIT_1", (0, (yb + yt) / 2, t / 2), (D.EAR_W, yt - yb, t + 0.002), root)
    return D.finish(root, mid, preview_views=((30, 25), (150, 30)), beauty_views=((28, 22), (160, 30)), size=(1000, 700), samples=32,
                    extra=f"frame: rack device, 1U front-mount shelf, panel face z={t}, tray top y={tf:.4f}, depth {depth}")


# ====================================================================== switches

def switch_chassis(root, BW, ZF, ZR, yb, yt, front_holes, vents_x=None):
    D.box("base", (-BW / 2, yb, ZR), (BW / 2, yb + 0.0010, ZF - 0.0015), "steel", root)
    for sx in (-1, 1):
        xo = sx * BW / 2
        slots = [D.rect(-0.180 + k * 0.012, -0.174 + k * 0.012, yb + 0.010, yt - 0.012) for k in range(12)]
        D.xslab("side", "steel", D.rect(ZR, ZF - 0.0015, yb, yt - 0.0010), xo - sx * 0.0010, xo, slots, root)
        D.xslab("side_vent_dark", "dark_plastic", D.rect(-0.182, -0.034, yb + 0.008, yt - 0.010), xo - sx * 0.006, xo - sx * 0.0055, (), root)
    D.box("top", (-BW / 2, yt - 0.0010, ZR), (BW / 2, yt, ZF - 0.0015), "steel", root)
    D.zslab("front", "paint_black", D.rect(-BW / 2, BW / 2, yb + 0.0002, yt - 0.0002), ZF - 0.0015, ZF, front_holes, root)


def switch_rear(root, BW, ZR, yb, yt, inlets, fans, extra_holes=()):
    holes = [D.c14_outline(x, yb + 0.0220) for x in inlets] + list(extra_holes)
    for fx in fans:
        holes += P.hex_grid(lambda a, b, r, fx=fx: (a - fx) ** 2 + (b - (yb + 0.0218)) ** 2 < 0.0175 ** 2, 0.0062, 0.0026,
                            fx - 0.02, fx + 0.02, yb + 0.002, yb + 0.042)
    D.zslab("rear", "steel", D.rect(-BW / 2, BW / 2, yb + 0.0002, yt - 0.0002), ZR - 0.0010, ZR, holes, root)
    for k, x in enumerate(inlets):
        rf = P.Frame((x, yb + 0.0220, ZR), NZ, Y)
        D.c14_inlet(rf, root, depth=0.011)
        P.anchor(f"A_PORT_C14_{k}", rf, (0.028, 0.020, 0.012), root, meta=f"depth=0.008,plug=c13,inlet=c14,psu={k + 1}")
        LABELS.quad("rear_label", "100-240V~ 1A" if len(inlets) == 1 else f"PS{k + 1}", P.Frame((x, yb + 0.0365, ZR - 0.00005), NZ, Y), 0.0026, root)
    for k, fx in enumerate(fans):
        a = P.anchor(f"A_FAN_{k}", P.Frame((fx, yb + 0.0218, ZR + 0.016), NZ, Y), (0.04, 0.04, 0.02), root, meta="axis=z,spin=1,rpm=7000")
        D.server_fan(a, 0.040, 0.020, blades=5, parent=root, segs=14)
    P.cylinder("earth_screw", P.Frame((-0.200, yb + 0.0200, ZR - 0.001), NZ, Y), 0.0030, 0.0025, "nickel", 8, root, z0=0.0)


def status_leds(root, x0, yb, ZF, names, pitch=0.0125):
    for k, (nm, tag, lab) in enumerate(names):
        lx = x0 - k * pitch
        D.led(f"A_LED_{nm}_0", P.Frame((lx, yb + 0.0130, ZF + 0.0003), Z, Y), 0.0026, 0.0026, tag, root, round_=True,
              meta=f"colour={'green' if 'green' in tag else 'amber'},fn={nm.lower()}")
        LABELS.quad("led_label", lab, P.Frame((lx, yb + 0.0085, ZF + 0.00005), Z, Y), 0.0022, root)


def build_switch48():
    import datacenter_net as N
    mid = "srv_linkwave_ls4804x"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    yb, yt = ybt(1, H1)
    ZF = 0.0045
    ZR = ZF - 0.280
    BW = 0.440
    pitch_x, pitch_y = 0.0142, 0.0170
    bank_w = 6 * pitch_x + 0.0016
    banks = [0.1411 - k * (bank_w + 0.0030) for k in range(4)]
    rows_y = (yb + 0.0137, yb + 0.0307)
    yc = (rows_y[0] + rows_y[1]) / 2
    sfp_x = [banks[-1] - bank_w / 2 - 0.0050 - 0.0076, banks[-1] - bank_w / 2 - 0.0050 - 0.0076 - 0.0165]
    sfp_y = [yb + 0.0137, yb + 0.0307]
    holes = []
    for gx in banks:
        bh = 2 * pitch_y + 0.0010
        holes.append(D.rect(gx - bank_w / 2, gx + bank_w / 2, yc - bh / 2, yc + bh / 2))
    for x in sfp_x:
        for y in sfp_y:
            holes.append(D.rect(x - D.SFP_W / 2 - 0.0006, x + D.SFP_W / 2 + 0.0006, y - D.SFP_H / 2 - 0.0006, y + D.SFP_H / 2 + 0.0006))
    holes.append(P.circle(0.0011, 0.2000, yb + 0.0320, 10))     # reset pinhole
    switch_chassis(root, BW, ZF, ZR, yb, yt, holes)
    D.decal("rating", ATLAS, "rating48", P.Frame((0.10, yt + 0.00005, ZR + 0.09), Y, NZ), 0.090, 0.0527, root)
    D.ears(root, 1, ZF, "paint_black", body_w=BW, slots=[D.HOLES_IN_U[0], D.HOLES_IN_U[2]])
    n_port = 0
    for gx in banks:
        N.rj45_bank(P.Frame((gx, yc, ZF), Z, Y), 6, 2, pitch_x, pitch_y, root, latch_by_row=(False, True))
        for k in range(6):
            lx = 2.5 * pitch_x - k * pitch_x
            for r, top in ((1, True), (0, False)):
                pnum = n_port + 2 * k + (0 if top else 1)
                px, py = gx + lx, rows_y[r]
                up = (0, 1, 0) if top else (0, -1, 0)
                P.anchor(f"A_PORT_ETH_{pnum}", P.Frame((px, py, ZF), Z, up), (0.0142, 0.0125, 0.020), root,
                         meta=f"depth=0.012,rj45=1,latch=+up,port={pnum + 1},speed=1g,poe=0")
                ly = py + (D.RJ45_H / 2 + 0.0012) * (1 if top else -1)
                D.led(f"A_LED_LINK_{pnum}", P.Frame((px + 0.0045, ly, ZF + 0.0003), Z, Y), 0.0020, 0.0011, "led_green", root, meta="colour=green,fn=link")
                D.led(f"A_LED_ACT_{pnum}", P.Frame((px - 0.0045, ly, ZF + 0.0003), Z, Y), 0.0020, 0.0011, "led_yellow", root, meta="colour=amber,fn=activity")
                LABELS.quad("port_no", str(pnum + 1), P.Frame((px, py + (0.0085 if top else -0.0085), ZF + 0.00005), Z, Y), 0.0024, root)
        n_port += 12
    k = 0
    for x in sfp_x:
        for y in reversed(sfp_y):
            fr = P.Frame((x, y, ZF), Z, Y)
            D.sfp_cage(fr, root, depth=0.046)
            P.anchor(f"A_PORT_SFP_{k}", fr, (0.0145, 0.0105, 0.05), root, meta=f"depth=0.042,sfp=sfp+,speed=10g,port={49 + k}")
            ly = y + (D.SFP_H / 2 + 0.0016) * (1 if y > yc else -1)
            D.led(f"A_LED_SFP_{k}", P.Frame((x, ly, ZF + 0.0003), Z, Y), 0.0030, 0.0010, "led_green", root, meta="colour=green,fn=link")
            k += 1
    LABELS.quad("sfp_label", "SFP+ 10G", P.Frame(((sfp_x[0] + sfp_x[1]) / 2, yt - 0.0026, ZF + 0.00005), Z, Y), 0.0022, root)
    # logo and status LEDs at +x (the viewer's left)
    D.decal("logo", ATLAS, "lw48", P.Frame((0.2005, yb + 0.0300, ZF + 0.00005), Z, Y), 0.030, 0.0075, root)
    status_leds(root, 0.2110, yb, ZF, (("POWER", "led_green", "PWR"), ("SYS", "led_green", "SYS"), ("FAN", "led_yellow", "FAN")), pitch=0.0100)
    LABELS.quad("reset_label", "RESET", P.Frame((0.2000 - 0.0085, yb + 0.0320, ZF + 0.00005), Z, Y), 0.0020, root)
    # rear: console RJ45, USB, the out-of-band management port, power, fans
    con = (-0.120, yb + 0.0220)
    mg = (-0.100, yb + 0.0220)
    usb = (-0.080, yb + 0.0220)
    extra = [D.rect(con[0] - D.RJ45_W / 2 - 0.0012, con[0] + D.RJ45_W / 2 + 0.0012, con[1] - D.RJ45_H / 2 - 0.0020, con[1] + D.RJ45_H / 2 + 0.0020),
             D.rect(mg[0] - D.RJ45_W / 2 - 0.0012, mg[0] + D.RJ45_W / 2 + 0.0012, mg[1] - D.RJ45_H / 2 - 0.0020, mg[1] + D.RJ45_H / 2 + 0.0020),
             D.usba_outline(*usb)]
    switch_rear(root, BW, ZR, yb, yt, [-0.170], [0.030, 0.090, 0.150], extra)
    for nm, (x, y), lab, meta in (("CONSOLE", con, "CONSOLE", "depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200"),
                                  ("MGMT", mg, "MGMT", "depth=0.012,rj45=1,latch=+up,speed=1g,net=oob")):
        fr = P.Frame((x, y, ZR), NZ, Y)
        D.rj45_jack(fr, root, latch_up=True)
        P.anchor(f"A_PORT_{nm}_0", fr, (0.0145, 0.012, 0.02), root, meta=meta)
        LABELS.quad("rear_label", lab, P.Frame((x, yt - 0.0050, ZR - 0.00005), NZ, Y), 0.0022, root)
    ufr = P.Frame((usb[0], usb[1], ZR), NZ, Y)
    D.usba_port(ufr, root)
    P.anchor("A_PORT_USBA_0", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=2.0,fn=config")
    LABELS.quad("rear_label", "USB", P.Frame((usb[0], yt - 0.0050, ZR - 0.00005), NZ, Y), 0.0022, root)
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZF + ZR) / 2), (BW, H1, ZF - ZR), root)
    P.anchor("A_HIT_1", (0, (yb + yt) / 2, 0.001), (D.EAR_W, H1, 0.004), root)
    return D.finish(root, mid, preview_views=((22, 15), (160, 20)), beauty_views=((18, 12), (155, 15)), size=(1100, 650), samples=36,
                    extra=f"frame: rack device, 1U, body 0.440 x {H1} x {ZF - ZR:.3f}, front z={ZF}, rear z={ZR:.4f}",
                    more_beauty=[(((-12, 6),), dict(target=(0.12, yb + 0.022, ZF), dist=0.26)),
                                 (((-15, 6),), dict(target=(-0.17, yb + 0.022, ZF), dist=0.22))])


def build_switch_agg():
    mid = "srv_linkwave_ls1600x"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    yb, yt = ybt(1, H1)
    ZF = 0.0045
    ZR = ZF - 0.300
    BW = 0.440
    px, rows = 0.0175, (yb + 0.0137, yb + 0.0307)
    groups = [0.0950, -0.0250]                     # two blocks of 4 x 2 cages
    yc = (rows[0] + rows[1]) / 2
    cages = []
    n = 0
    for gx in groups:
        for k in range(4):
            x = gx + (1.5 - k) * px
            for top in (True, False):
                cages.append((n, x, rows[1] if top else rows[0], top))
                n += 1
    holes = [D.rect(x - D.SFP_W / 2 - 0.0006, x + D.SFP_W / 2 + 0.0006, y - D.SFP_H / 2 - 0.0006, y + D.SFP_H / 2 + 0.0006) for (_, x, y, _) in cages]
    mg = (-0.120, yb + 0.0137)
    con = (-0.140, yb + 0.0137)
    for (x, y) in (mg, con):
        holes.append(D.rect(x - D.RJ45_W / 2 - 0.0012, x + D.RJ45_W / 2 + 0.0012, y - D.RJ45_H / 2 - 0.0020, y + D.RJ45_H / 2 + 0.0020))
    holes.append(P.circle(0.0011, -0.1300, yb + 0.0320, 10))
    vents = [D.rect(-0.210 + k * 0.006, -0.207 + k * 0.006, yb + 0.008, yt - 0.008) for k in range(9)]
    switch_chassis(root, BW, ZF, ZR, yb, yt, holes + vents)
    D.zslab("front_vent_dark", "dark_plastic", D.rect(-0.212, -0.155, yb + 0.006, yt - 0.006), ZF - 0.010, ZF - 0.009, (), root)
    D.decal("rating", ATLAS, "rating16", P.Frame((0.10, yt + 0.00005, ZR + 0.09), Y, NZ), 0.090, 0.0527, root)
    D.ears(root, 1, ZF, "paint_black", body_w=BW, slots=[D.HOLES_IN_U[0], D.HOLES_IN_U[2]])
    for (k, x, y, top) in cages:
        up = (0, 1, 0) if top else (0, -1, 0)
        fr = P.Frame((x, y, ZF), Z, up)
        D.sfp_cage(fr, root, depth=0.046)
        P.anchor(f"A_PORT_SFP_{k}", fr, (0.0145, 0.0105, 0.05), root, meta=f"depth=0.042,sfp=sfp+,speed=10g,port={k + 1},latch=+up")
        ly = y + (D.SFP_H / 2 + 0.0016) * (1 if top else -1)
        D.led(f"A_LED_LINK_{k}", P.Frame((x + 0.0035, ly, ZF + 0.0003), Z, Y), 0.0030, 0.0010, "led_green", root, meta="colour=green,fn=link")
        D.led(f"A_LED_ACT_{k}", P.Frame((x - 0.0035, ly, ZF + 0.0003), Z, Y), 0.0030, 0.0010, "led_yellow", root, meta="colour=amber,fn=activity")
        LABELS.quad("port_no", str(k + 1), P.Frame((x, y + (0.0092 if top else -0.0092), ZF + 0.00005), Z, Y), 0.0022, root)
    for (nm, (x, y), lab, meta) in (("MGMT", mg, "MGMT", "depth=0.012,rj45=1,latch=+up,speed=1g,net=oob"),
                                    ("CONSOLE", con, "CONSOLE", "depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200")):
        fr = P.Frame((x, y, ZF), Z, Y)
        D.rj45_jack(fr, root, latch_up=True)
        P.anchor(f"A_PORT_{nm}_0", fr, (0.0145, 0.012, 0.02), root, meta=meta)
        LABELS.quad("front_label", lab, P.Frame((x, y + 0.0105, ZF + 0.00005), Z, Y), 0.0022, root)
    D.led("A_LED_MGMT_0", P.Frame((mg[0] + 0.0045, mg[1] + D.RJ45_H / 2 + 0.0012, ZF + 0.0003), Z, Y), 0.0020, 0.0011, "led_green", root,
          meta="colour=green,fn=link")
    LABELS.quad("reset_label", "RESET", P.Frame((-0.1300, yb + 0.0360, ZF + 0.00005), Z, Y), 0.0018, root)
    D.decal("logo", ATLAS, "lw16", P.Frame((0.1870, yb + 0.0300, ZF + 0.00005), Z, Y), 0.040, 0.010, root)
    status_leds(root, 0.2010, yb, ZF, (("POWER", "led_green", "PWR"), ("SYS", "led_green", "SYS"), ("FAN", "led_yellow", "FAN")))
    D.led("A_LED_PSU_0", P.Frame((0.1635, yb + 0.0130, ZF + 0.0003), Z, Y), 0.0026, 0.0026, "led_green", root, round_=True, meta="colour=green,fn=psu1")
    D.led("A_LED_PSU_1", P.Frame((0.1530, yb + 0.0130, ZF + 0.0003), Z, Y), 0.0026, 0.0026, "led_green", root, round_=True, meta="colour=green,fn=psu2")
    LABELS.quad("led_label", "PS1", P.Frame((0.1635, yb + 0.0085, ZF + 0.00005), Z, Y), 0.0022, root)
    LABELS.quad("led_label", "PS2", P.Frame((0.1530, yb + 0.0085, ZF + 0.00005), Z, Y), 0.0022, root)
    switch_rear(root, BW, ZR, yb, yt, [-0.170, -0.120], [0.000, 0.060, 0.120, 0.180])
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZF + ZR) / 2), (BW, H1, ZF - ZR), root)
    P.anchor("A_HIT_1", (0, (yb + yt) / 2, 0.001), (D.EAR_W, H1, 0.004), root)
    return D.finish(root, mid, preview_views=((22, 15), (160, 20)), beauty_views=((18, 12), (155, 15)), size=(1100, 650), samples=36,
                    extra=f"frame: rack device, 1U, body 0.440 x {H1} x {ZF - ZR:.3f}, front z={ZF}, rear z={ZR:.4f}",
                    more_beauty=[(((-12, 6),), dict(target=(0.06, yb + 0.022, ZF), dist=0.26))])


# ====================================================================== KVM console drawer

def outer_slide(root, side, yb, rh, z0, z1, tag="steel"):
    """A fixed outer slide member (C channel, open towards the body) along a side, from z0 to z1."""
    sx = -1 if side == "L" else 1
    xo = sx * 0.2245
    yc = yb + rh / 2
    D.box("slide_web", (min(xo, xo - sx * 0.0010), yb, z1), (max(xo, xo - sx * 0.0010), yb + rh, z0), tag, root)
    for yy in (yb, yb + rh - 0.0010):
        D.box("slide_flange", (min(xo, xo - sx * 0.0055), yy, z1), (max(xo, xo - sx * 0.0055), yy + 0.0010, z0), tag, root)
    return yc


def build_kvm():
    mid = "srv_strata_kvm_1u"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    yb, yt = ybt(1, H1)
    BW = 0.4360
    ZD = 0.0200                   # the drawer's front face (closed)
    DL = 0.520                    # drawer length
    ZB = ZD - DL                  # drawer back
    ZE = -0.600                   # fixed electronics box: ZB .. ZE (ports on its rear face)
    # --- fixed: front ears on the outer slides, the slides, rear brackets to the rear rails, the electronics box
    for side in ("L", "R"):
        sx = -1 if side == "L" else 1
        outer_slide(root, side, yb + 0.0040, 0.0300, -0.0005, REAR_RAIL_Z + 0.0015)
        # front ear: an L bracket from the slide's front to the rack plane
        D.zslab("ear", "paint_black", D.rr(min(sx * 0.2235, sx * D.EAR_W / 2), max(sx * 0.2235, sx * D.EAR_W / 2), yb + 0.0003, yt - 0.0003, 0.0012),
                0.0, 0.0020, [P.stadium(0.0100, 0.0068, sx * D.HOLE_X, y) for y in (D.HOLES_IN_U[0], D.HOLES_IN_U[2])], root)
        # rear bracket: a plate on the rear rail's front face (behind which the cage nuts sit)
        D.zslab("rear_bracket", "steel", D.rect(min(sx * 0.2235, sx * 0.2440), max(sx * 0.2235, sx * 0.2440), yb + 0.0020, yt - 0.0020),
                REAR_RAIL_Z + 0.0015, REAR_RAIL_Z + 0.0035, [P.stadium(0.0100, 0.0068, sx * D.HOLE_X, y) for y in (D.HOLES_IN_U[0], D.HOLES_IN_U[2])], root)
        D.box("rear_bracket_arm", (min(sx * 0.2235, sx * 0.2245), yb + 0.004, REAR_RAIL_Z + 0.0035), (max(sx * 0.2235, sx * 0.2245), yb + 0.034, REAR_RAIL_Z + 0.060),
              "steel", root)
    rack_screw_anchors(root, [D.HOLES_IN_U[0], D.HOLES_IN_U[2]], 0.0020)
    for k, (sx, y) in enumerate([(sx, y) for sx in (-1, 1) for y in (D.HOLES_IN_U[0], D.HOLES_IN_U[2])]):
        P.anchor(f"A_SCREW_RACK_{4 + k}", P.Frame((sx * D.HOLE_X, y, REAR_RAIL_Z + 0.0035), Z, Y), (0.012, 0.010, 0.006), root,
                 meta=f"thread=M6,cage=1,side={'r' if sx > 0 else 'l'},rear=1")
    # electronics box with the rear ports
    D.box("ebox", (-0.200, yb + 0.002, ZE), (0.200, yb + 0.030, ZB - 0.004), "steel", root)
    vga, usb, inlet = (-0.120, yb + 0.016), (-0.085, yb + 0.016), (0.120, yb + 0.016)
    holes = [D.rr(vga[0] - 0.0165, vga[0] + 0.0165, vga[1] - 0.0065, vga[1] + 0.0065, 0.0012), P.rrect(0.0122, 0.0112, 0.001, *usb),
             D.c14_outline(*inlet)]
    D.zslab("ebox_rear", "paint_black", D.rect(-0.200, 0.200, yb + 0.002, yb + 0.030), ZE - 0.0010, ZE, holes, root)
    vfr = P.Frame((vga[0], vga[1], ZE - 0.0004), NZ, Y)
    D.vga_port(vfr, root)
    P.anchor("A_PORT_VGA_0", vfr, (0.032, 0.013, 0.012), root, meta="depth=0.006,vga=1,fn=video_in")
    ufr = P.Frame((usb[0], usb[1], ZE), NZ, Y)
    D.cavity(ufr, P.rrect(0.0085, 0.0075, 0.0012), 0.008, root)
    P.cube("usbb_tongue", (0, -0.0008, -0.004), (0.0050, 0.0030, 0.007), "white_plastic", ufr, root)
    P.anchor("A_PORT_USBB_0", ufr, (0.012, 0.012, 0.012), root, meta="depth=0.008,usb=b,fn=keyboard_mouse")
    ifr = P.Frame((inlet[0], inlet[1], ZE - 0.0010), NZ, Y)
    D.c14_inlet(ifr, root, depth=0.011)
    P.anchor("A_PORT_C14_0", ifr, (0.028, 0.020, 0.012), root, meta="depth=0.008,plug=c13,inlet=c14")
    LABELS.quad("rear_label", "VGA", P.Frame((vga[0], yb + 0.0265, ZE - 0.00105), NZ, Y), 0.0024, root)
    LABELS.quad("rear_label", "USB-B", P.Frame((usb[0], yb + 0.0265, ZE - 0.00105), NZ, Y), 0.0024, root)
    LABELS.quad("rear_label", "100-240V~ 1A", P.Frame((inlet[0], yb + 0.0265, ZE - 0.00105), NZ, Y), 0.0024, root)
    D.decal("kvm_label", ATLAS, "kvm_label", P.Frame((0.0, yb + 0.03005, (ZE + ZB) / 2), Y, NZ), 0.060, 0.0234, root)
    # --- the drawer (moving piece): tray, front panel with the handle, keyboard, touchpad, rear box, inner slides
    dr = P.anchor("A_DRAWER_0", P.Frame((0.0, yb + 0.022, ZD), Z, Y), (BW, yt - yb, DL), root,
                  meta="pull=+z,dist=0.450,latch=front_tabs,stop=1")
    D.box("tray_pan", (-BW / 2 + 0.002, yb + 0.0010, ZB), (BW / 2 - 0.002, yb + 0.0020, ZD - 0.004), "paint_black", dr)
    for sx in (-1, 1):
        x0 = sx * (BW / 2 - 0.002)
        D.box("tray_side", (min(x0, x0 - sx * 0.0012), yb + 0.0010, ZB), (max(x0, x0 - sx * 0.0012), yb + 0.0230, ZD - 0.004), "paint_black", dr)
        xi = sx * 0.2195     # inner slide member on the drawer side
        D.box("inner_slide", (min(xi, xi + sx * 0.0012), yb + 0.0090, ZB + 0.010), (max(xi, xi + sx * 0.0012), yb + 0.0290, ZD - 0.030), "steel", dr)
    # front panel: a 1U plate with the handle, a release tab each side, the badge, LCD power and the LED
    D.zslab("drawer_front", "paint_black", D.rr(-BW / 2, BW / 2, yb + 0.0006, yt - 0.0006, 0.0015), ZD - 0.0040, ZD, [], dr)
    P.tube("handle", P.smooth_path([(-0.150, yb + 0.022, ZD), (-0.150, yb + 0.022, ZD + 0.016), (-0.140, yb + 0.022, ZD + 0.022),
                                    (0.140, yb + 0.022, ZD + 0.022), (0.150, yb + 0.022, ZD + 0.016), (0.150, yb + 0.022, ZD)], 3), 0.0040, "alu", dr, 10)
    for sx in (-1, 1):
        D.box("handle_base", (sx * 0.150 - 0.006, yb + 0.010, ZD), (sx * 0.150 + 0.006, yb + 0.034, ZD + 0.003), "black_plastic", dr, bevel=0.001, seg=1)
        D.box("release_tab", (sx * 0.200 - 0.004, yb + 0.012, ZD), (sx * 0.200 + 0.004, yb + 0.032, ZD + 0.0035), GREEN, dr, bevel=0.0006, seg=1,
              uv_solid=P.pal("green"))
    D.decal("badge", ATLAS, "kvm_badge", P.Frame((-0.050, yb + 0.0290, ZD + 0.00005), Z, Y), 0.050, 0.0125, dr)
    bf = P.Frame((0.090, yb + 0.0300, ZD + 0.0002), Z, Y)
    D.button("A_BUTTON_LCD_0", bf, 0.0030, 0.0010, "black_plastic", dr, ring_tag="grey_plastic", meta="press=-z_local,travel=0.0010,fn=lcd_power")
    D.led("A_LED_POWER_0", P.Frame((0.0820, yb + 0.0300, ZD + 0.0002), Z, Y), 0.0022, 0.0022, "led_green", dr, round_=True, meta="colour=green,fn=power")
    LABELS.quad("lcd_label", "LCD", P.Frame((0.090, yb + 0.0245, ZD + 0.00005), Z, Y), 0.0020, dr)
    # the keyboard: a recessed plate, the key caps and one legend quad over them; the touchpad in front of it
    kw, kh = 0.340, 0.120
    kz1 = ZD - 0.0060 - 0.050          # the keyboard's front edge (the touchpad and palm rest in front of it)
    kcx = 0.0
    ky = yb + 0.0060
    D.box("kb_plate", (-0.212, yb + 0.0020, ZD - 0.262), (0.212, ky, ZD - 0.0045), "dark_plastic", dr)
    for (x0, x1, y0, y1, k) in keyboard_layout(kw, kh):
        X0_ = kcx + kw / 2 - x1 + 0.0007
        X1_ = kcx + kw / 2 - x0 - 0.0007
        Z0_ = kz1 - y1 + 0.0007
        Z1_ = kz1 - y0 - 0.0007
        D.box("key", (X0_, ky, Z0_), (X1_, ky + 0.0042, Z1_), "black_plastic", dr, bevel=0.0006, seg=1)
    P.quad("kb_legends", P.Frame((kcx, ky + 0.00425, kz1 - kh / 2), Y, NZ), kw, kh, ATLAS.tag, dr, uv=ATLAS.uv("kbd"))
    P.quad("touchpad", P.Frame((0.0, ky + 0.00005, ZD - 0.030), Y, NZ), 0.064, 0.040, ATLAS.tag, dr, uv=ATLAS.uv("touch"))
    # the rear part of the drawer: a closed box behind the hinge (LCD electronics), and the hinges
    zh = ZD - 0.266
    D.box("drawer_box", (-BW / 2 + 0.003, yb + 0.002, ZB + 0.002), (BW / 2 - 0.003, yb + 0.0390, zh - 0.004), "paint_black", dr)
    for sx in (-1, 1):
        P.cylinder("hinge", P.Frame((sx * 0.180, yb + 0.0310, zh), X, Y), 0.0040, 0.024, "steel_dark", 12, dr)
    # the LCD lid (moving piece of A_LID_0@A_DRAWER_0): closed over the keyboard, screen down; it opens upwards
    ly0, ly1 = yb + 0.0230, yb + 0.0395
    lid = P.anchor("A_LID_0", P.Frame((0.0, yb + 0.0310, zh), Z, Y), (0.432, ly1 - ly0, 0.262), dr,
                   meta="hinge=x,open=-105,min=-115,max=0,closed=0")
    D.box("lid_back", (-0.216, ly0 + 0.002, zh + 0.002), (0.216, ly1, ZD - 0.006), "paint_black", lid, bevel=0.0015, seg=2)
    D.box("lid_bezel", (-0.216, ly0, zh + 0.002), (0.216, ly0 + 0.0022, ZD - 0.006), "black_plastic", lid)
    for k in range(5):   # stiffening ribs on the back
        D.box("lid_rib", (-0.190 + k * 0.095 - 0.020, ly1, zh + 0.030), (-0.190 + k * 0.095 + 0.020, ly1 + 0.0006, ZD - 0.040), "paint_black", lid)
    D.box("lid_grip", (-0.060, ly0 + 0.003, ZD - 0.0075), (0.060, ly1 - 0.003, ZD - 0.0045), "dark_plastic", lid)
    sc = P.anchor("A_SCREEN_0", P.Frame((0.0, ly0 - 0.0001, (zh + ZD - 0.006) / 2 + 0.004), NY, Z), (0.410, 0.231, 0.003), lid,
                  meta="kind=lcd,ref=1366x768,diag=18.5,colour=rgb")
    P.quad("screen", P.Frame((0.0, ly0 - 0.0001, (zh + ZD - 0.006) / 2 + 0.004), NY, Z), 0.410, 0.231, ATLAS.tag, sc, uv=ATLAS.uv("screen"))
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZD + ZE) / 2), (BW, yt - yb, ZD - ZE), root)
    P.anchor("A_HIT_1", (0, (yb + yt) / 2, 0.001), (D.EAR_W, yt - yb, 0.004), root)
    res = D.finish(root, mid, preview_views=((25, 20), (155, 25)), beauty_views=((22, 16), (160, 22)), size=(1100, 650), samples=36,
                   extra=f"frame: rack device, 1U, drawer front z={ZD}, drawer {DL} long, electronics box to z={ZE}, slides to z={REAR_RAIL_Z}")
    if P.PREVIEW[0]:   # the drawer pulled out and the lid open
        from mathutils import Matrix
        objs = list(c.descendants(root))
        move = [o for o in objs if "@A_DRAWER_0" in o.name or o.name == "A_DRAWER_0"]
        saved = {o.name: o.matrix_world.copy() for o in move}
        T = Matrix.Translation(c.conv((0, 0, 0.40)) - c.conv((0, 0, 0)))
        for o in move:
            o.matrix_world = T @ o.matrix_world
        saved2 = D.pose_pieces(root, [("A_LID_0@A_DRAWER_0", "x", -105)])
        P.beauty(root, mid, views=((25, 22), (-20, 35)), size=(1100, 800), samples=36, start_index=4)
        objs = {o.name: o for o in c.descendants(root)}
        for nm, mw in list(saved2.items()) + list(saved.items()):
            objs[nm].matrix_world = mw
    return res


# ====================================================================== cable management arm

def arm_channel(name, parent, x0, x1, yc, h, z0, z1, tag="paint_black"):
    """A U-channel arm segment along x (the web at z0, open towards z1), with wire cable hoops over the open side
    and two hook-and-loop straps."""
    s = 1 if z1 > z0 else -1
    D.box(name + "_web", (min(x0, x1), yc - h / 2, min(z0, z0 - s * 0.0012)), (max(x0, x1), yc + h / 2, max(z0, z0 - s * 0.0012)), tag, parent)
    for yy in (yc - h / 2, yc + h / 2 - 0.0012):
        D.box(name + "_flange", (min(x0, x1), yy, min(z0, z1)), (max(x0, x1), yy + 0.0012, max(z0, z1)), tag, parent)
        D.box(name + "_lip", (min(x0, x1), yy + (0.0012 if yy < yc else -0.0028), min(z1 - s * 0.0012, z1)),
              (max(x0, x1), yy + (0.0040 if yy < yc else 0.0), max(z1 - s * 0.0012, z1)), tag, parent)
    n = int(abs(x1 - x0) / 0.060)
    for k in range(n):
        x = min(x0, x1) + 0.030 + k * 0.060
        # a wire hoop: from the top flange out past the open side and back to the bottom flange
        zt = z1 + s * 0.012
        P.tube(name + "_hoop", P.smooth_path([(x, yc + h / 2 - 0.002, z1), (x, yc + h / 2 + 0.002, zt - s * 0.004), (x, yc + 0.010, zt),
                                              (x, yc - 0.010, zt), (x, yc - h / 2 - 0.002, zt - s * 0.004), (x, yc - h / 2 + 0.002, z1)], 3),
               0.0011, "steel", parent, 6)
    for k in (1, 3):
        x = min(x0, x1) + abs(x1 - x0) * k / 4
        D.box(name + "_strap", (x - 0.009, yc - h / 2 - 0.0010, min(z0, z1) - 0.0008), (x + 0.009, yc + h / 2 + 0.0010, max(z0, z1) + 0.0008),
              "black_plastic", parent)


def build_cma():
    mid = "srv_strata_cma"
    P.reset()
    textures()
    root = c.root(mid)
    D.ROOT[0] = root
    yb = 0.0004
    h = 0.032
    yc = yb + 0.0040 + 0.015            # the 1U slide rail's centre line (server_1u: A_RAIL_x_0 y)
    zo = REAR_RAIL_Z + 0.0015          # the outer slide's rear end (server_1u/2u rails)
    zi = -0.660                         # the inner member's rear end on the chassis (ZR + 0.010)
    # fixed: the outer connector slides into the +x outer rail's channel behind the rail's intermediate member and
    # carries the arm's hinge behind the rear post; the support bracket does the same in the -x rail
    for sx in (-1, 1):
        nm = "outer_conn" if sx > 0 else "support"
        D.box(nm, (min(sx * 0.2195, sx * 0.2234), yc - 0.0125, zo + 0.0005), (max(sx * 0.2195, sx * 0.2234), yc + 0.0125, -0.7200), "steel", root)
        D.box(nm + "_link", (min(sx * 0.2060, sx * 0.2234), yc - h / 2, zo - 0.0085), (max(sx * 0.2060, sx * 0.2234), yc + h / 2, zo + 0.0005), "steel", root)
        D.box(nm + "_clip", (min(sx * 0.2215, sx * 0.2234), yc - 0.005, -0.7200), (max(sx * 0.2215, sx * 0.2234), yc + 0.005, -0.7170), GREEN, root,
              uv_solid=P.pal("green"))
    D.box("support_shelf", (-0.2234, yc - h / 2 - 0.0012, zo - 0.060), (-0.1700, yc - h / 2, zo - 0.008), "steel", root)
    P.anchor("A_MOUNT_OUTER_0", P.Frame((0.2215, yc, -0.7200), Z, Y), (0.006, 0.026, 0.020), root,
             meta="clip=outer_rail,side=r,insert=+z,release=green_tab")
    P.anchor("A_MOUNT_SUPPORT_0", P.Frame((-0.2215, yc, -0.7200), Z, Y), (0.006, 0.026, 0.020), root,
             meta="clip=outer_rail,side=l,insert=+z,release=green_tab")
    # arm 0 (outer): hinged at the outer connector, runs to the elbow at -x; z -0.745 .. -0.763
    za0, za1 = zo - 0.0090, zo - 0.0270
    a0 = P.anchor("A_ARM_0", P.Frame((0.2140, yc, (za0 + za1) / 2), Z, Y), (0.420, h, 0.020), root,
                  meta="hinge=y,closed=0,open=80,follows=A_RAIL_R_0,travel=0.62")
    arm_channel("arm0", a0, 0.2100, -0.2000, yc, h, za0, za1)
    for k in range(3):
        P.cylinder("hinge_knuckle", P.Frame((0.2140, yc - h / 2 + 0.004 + k * 0.012, (za0 + za1) / 2), Y, Z), 0.0042, 0.0080, "nickel", 12, a0)
    D.decal("cma_label", ATLAS, "cma_label", P.Frame((0.020, yc, za1 - 0.00005), NZ, Y), 0.060, 0.0219, a0)
    # arm 1 (inner): hinged at the elbow, runs back to the inner connector on the server's inner rail
    zb0, zb1 = zi - 0.034, zi - 0.052
    zel = (za0 + zb1) / 2
    a1 = P.anchor("A_ARM_1", P.Frame((-0.2060, yc, zel), Z, Y), (0.420, h, 0.020), a0,
                  meta="hinge=y,closed=0,open=-160,follows=A_ARM_0")
    D.box("elbow", (-0.2140, yc - h / 2, za1 + 0.002), (-0.1980, yc + h / 2, zb0 + 0.002), "steel_dark", a1)
    P.cylinder("elbow_pin", P.Frame((-0.2060, yc, zel), Y, Z), 0.0030, h + 0.004, "nickel", 12, a1)
    arm_channel("arm1", a1, -0.2000, 0.2080, yc, h, zb0, zb1)
    # the inner connector: a link from the arm's end to a plate that clips on the inner rail member's rear end
    # (outside the member, between it and the intermediate member)
    D.box("inner_link", (0.2080, yc - h / 2, zb1), (0.2203, yc + h / 2, zb0 + 0.002), "steel", a1)
    D.box("inner_conn", (0.2188, yc - 0.0080, zb0 + 0.002), (0.2203, yc + 0.0080, zi + 0.008), "steel", a1)
    D.box("inner_conn_clip", (0.2188, yc - 0.004, zi + 0.002), (0.2203, yc + 0.004, zi + 0.008), GREEN, a1, uv_solid=P.pal("green"))
    P.anchor("A_MOUNT_INNER_0", P.Frame((0.2195, yc, zi), Z, Y), (0.004, 0.016, 0.020), a1, meta="clip=inner_rail,side=r,insert=+z,release=green_tab")
    P.anchor("A_HIT_0", (0.0, yc, (zb0 + za1) / 2), (0.448, h + 0.004, zb0 - za1), root)
    return D.finish(root, mid, preview_views=((150, 30), (210, 25)), beauty_views=((155, 25), (200, 35)), size=(1100, 600), samples=32,
                    extra=f"frame: rack device (the frame of the server it serves, installed at the same A_RACKU_n); outer rail rear end z={zo}, "
                          f"inner rail rear end z={zi}, rail centre y={yc:.4f}")


# ====================================================================== servers (shared with datacenter_server.py)

def server_ears(st, root, thumb_y):
    """The ear blocks of the STRATA servers (as datacenter_server.front): control-panel blocks on the rails with the
    captive thumbscrews A_SCREW_THUMB_0/1, the power button and LED on -x, the ID button and status LEDs on +x."""
    import datacenter_server as DS
    XB, ZF = DS.XB, DS.ZF
    yb, yt = st["YB"], st["YT"]
    for sx in (-1, 1):
        ex0, ex1 = sorted((sx * XB, sx * (D.EAR_W / 2 - 0.0003)))
        D.box("ear", (ex0, yb + 0.0003, 0.0), (ex1, yt - 0.0003, ZF - 0.0016), "steel_dark", root, bevel=0.0006, seg=1)
        D.box("ear_cover", (ex0 + 0.0004, yb + 0.0006, ZF - 0.0022), (ex1 - 0.0004, yt - 0.0006, ZF), "black_plastic", root, bevel=0.0012, seg=2)
        k = 0 if sx < 0 else 1
        tf = P.Frame((sx * D.HOLE_X, thumb_y, ZF), Z, Y)
        a = P.anchor(f"A_SCREW_THUMB_{k}", tf, (0.012, 0.012, 0.012), root, meta="thread=M6,captive=1,len=0.032,turns=4")
        P.cylinder("thumb_well", tf.sub(0, 0, 0.0001), 0.0064, 0.0004, "dark_plastic", 20, root)
        DS.thumbscrew(a, tf)
    exm = -(XB + D.EAR_W / 2) / 2
    exp = -exm
    pwr_y = yt - 0.010
    pf = P.Frame((exm, pwr_y, ZF + 0.0002), Z, Y)
    a = D.button("A_BUTTON_POWER_0", pf, 0.0034, 0.0012, "black_plastic", root, ring_tag="grey_plastic",
                 meta="press=-z_local,travel=0.0012,fn=power,hold=4", height=0.0018)
    D.power_icon("pwr_icon", pf.sub(0, 0, 0.0010), 0.0018, 0.0005, "grey_plastic", a)
    a = P.anchor("A_LED_POWER_0", pf.sub(0, 0, 0.0004), (0.010, 0.010, 0.003), root, meta="colour=green,fn=power,ring=1")
    P.lathe("led_power", [(0.0046, -0.0004), (0.0050, -0.0004), (0.0050, 0.0003), (0.0046, 0.0003), (0.0046, -0.0004)], "led_green", pf, 20, a)
    idf = P.Frame((exp, pwr_y, ZF + 0.0002), Z, Y)
    a = D.button("A_BUTTON_ID_0", idf, 0.0030, 0.0010, "grey_plastic", root, ring_tag="dark_plastic",
                 meta="press=-z_local,travel=0.0010,fn=identify", height=0.0016)
    P.text3d("id_i", "i", 0.0034, 0.0001, "black_plastic", idf.sub(0, 0, 0.0008), "arialbd.ttf", parent=a)
    D.led("A_LED_ID_0", P.Frame((exp - 0.0052, pwr_y, ZF + 0.0002), Z, Y), 0.0020, 0.0020, "led_blue", root, round_=True,
          meta="colour=blue,fn=identify")
    for k, (nm, tag, col) in enumerate((("HEALTH", "led_green", "green"), ("FAULT", "led_yellow", "amber"), ("NET", "led_green", "green"))):
        D.led(f"A_LED_{nm}_0", P.Frame((exp, yt - 0.026 - k * 0.008, ZF + 0.0002), Z, Y), 0.0026, 0.0020, tag, root,
              meta=f"colour={col},fn={nm.lower() if nm != 'NET' else 'network'}")


def vertical_tray(n, cx, y0, y1, w, root, ZF, depth=0.104):
    """A hot-swap 2.5" tray standing on edge (24-bay front): the face with a vented top and two light pipes, the
    lever with its green release at the bottom, the carrier and the drive. Moving piece of A_BAY_n (pull=+z)."""
    cy = (y0 + y1) / 2
    h = y1 - y0
    a = P.anchor(f"A_BAY_{n}", P.Frame((cx, cy, ZF), Z, Y), (w, h, depth), root,
                 meta=f"pull=+z,dist={depth + 0.01:.3f},kind=sff,slot={n},latch=1,orient=vertical")
    ww = w - 0.0006
    vents = [D.rect(cx - ww / 2 + 0.0030, cx + ww / 2 - 0.0030, y1 - 0.016 - k * 0.0036, y1 - 0.0144 - k * 0.0036) for k in range(3)]
    D.zslab("tray_front", "black_plastic", D.rect(cx - ww / 2, cx + ww / 2, y0 + 0.0003, y1 - 0.0003), ZF - 0.0030, ZF, vents, a)
    D.zslab("tray_vent_back", "dark_plastic", D.rect(cx - ww / 2 + 0.002, cx + ww / 2 - 0.002, y1 - 0.026, y1 - 0.012), ZF - 0.0062, ZF - 0.0054, (), a)
    # the lever: a raised bar over the lower 60 % with ribs, the green release at its foot
    ly0, ly1 = y0 + 0.0040, y0 + h * 0.62
    D.zslab("tray_lever", "dark_plastic", D.rr(cx - ww / 2 + 0.0012, cx + ww / 2 - 0.0012, ly0, ly1, 0.0014, seg=2), ZF, ZF + 0.0030, (), a)
    for k in range(3):
        yr = ly1 - 0.007 - k * 0.0040
        D.box("tray_lever_rib", (cx - ww * 0.30, yr, ZF + 0.0030), (cx + ww * 0.30, yr + 0.0012, ZF + 0.0036), "black_plastic", a)
    D.box("tray_release", (cx - ww * 0.28, y0 + 0.0012, ZF + 0.0010), (cx + ww * 0.28, y0 + 0.0040, ZF + 0.0044), GREEN, a,
          uv_solid=P.pal("green"))
    D.led(f"A_LED_DRIVE_{n}", P.Frame((cx - 0.0035, y1 - 0.0050, ZF + 0.0003), Z, Y), 0.0024, 0.0016, "led_green", a, meta="colour=green,fn=activity")
    D.led(f"A_LED_DRIVEFAULT_{n}", P.Frame((cx + 0.0035, y1 - 0.0050, ZF + 0.0003), Z, Y), 0.0024, 0.0016, "led_yellow", a, meta="colour=amber,fn=fault")
    # the drive in its carrier (seen when the tray is out): body, label, the connector end
    dz0 = ZF - 0.004
    dw, dh, dl = 0.0150, 0.0699, 0.1000
    D.box("drive_body", (cx - dw / 2, y0 + 0.002, dz0 - dl), (cx + dw / 2, y0 + 0.002 + dh, dz0), "alu", a)
    D.decal("drive_label", ATLAS, "drive_v", P.Frame((cx + dw / 2 + 0.00005, y0 + 0.002 + dh / 2, dz0 - dl * 0.5), X, Y), 0.028 * 192 / 560 * 2.5,
            0.028 * 2.5, a)
    D.box("drive_conn", (cx - dw / 2 + 0.002, y0 + 0.004, dz0 - dl - 0.002), (cx + dw / 2 - 0.004, y0 + 0.040, dz0 - dl), "black_plastic", a)
    return a


def build_storage_server():
    import datacenter_server as DS
    mid = "srv_strata_sr224_2u"
    P.reset()
    textures()
    st = DS.layout("server_2u")
    st["sid"] = mid
    st["bay_kind"] = "sff"          # the interior's cage depth (0.115) and fan wall position
    root = c.root(mid)
    D.ROOT[0] = root
    XB, ZF, ZR = DS.XB, DS.ZF, DS.ZR
    yb, yt = st["YB"], st["YT"]
    DS.chassis(st, root)
    # the front: 24 vertical bays from the viewer's left (+x), a band with the badge above them
    n = 24
    pitch = 0.01775
    x_left = pitch * n / 2
    ty0, ty1 = yb + 0.0018, yb + 0.0018 + 0.0760
    holes = [D.rect(x_left - pitch * (k + 1) + 0.0002, x_left - pitch * k - 0.0002, ty0, ty1) for k in range(n)]
    cd = 0.115
    D.zslab("cage", "steel_dark", D.rect(-XB + 0.0008, XB - 0.0008, yb + 0.0002, yt - 0.0009), ZF - 0.012, ZF - 0.0005, holes, root)
    for k in range(n + 1):
        x = x_left - pitch * k
        D.box("cage_wall", (x - 0.0003, ty0, ZF - cd), (x + 0.0003, ty1, ZF - 0.012), "steel_dark", root)
    D.box("cage_floor", (-x_left, ty0 - 0.0006, ZF - cd), (x_left, ty0, ZF - 0.012), "steel_dark", root)
    D.box("cage_roof", (-x_left, ty1, ZF - cd), (x_left, ty1 + 0.0006, ZF - 0.012), "steel_dark", root)
    D.box("backplane", (-x_left, ty0, ZF - cd - 0.0016), (x_left, ty1, ZF - cd), "pcb_green", root)
    for k in range(n):
        cx = x_left - pitch * (k + 0.5)
        D.box("bp_conn", (cx - 0.006, ty0 + 0.004, ZF - cd), (cx + 0.004, ty0 + 0.040, ZF - cd + 0.004), "black_plastic", root)
        vertical_tray(k, cx, ty0, ty1, pitch - 0.0004, root, ZF)
    D.decal("badge", ATLAS, "sr224", P.Frame((0.150, (ty1 + yt) / 2, ZF - 0.00045), Z, Y), 0.028, 0.007, root)
    D.decal("badge2", ATLAS, "strata", P.Frame((-0.150, (ty1 + yt) / 2, ZF - 0.00045), Z, Y), 0.024, 0.006, root)
    server_ears(st, root, D.HOLES_IN_U[2])
    DS.interior(st, root)
    DS.lid(st, root)
    for k in range(2):
        DS.psu(st, k, root)
    DS.slide_rail(st, "L", root)
    DS.slide_rail(st, "R", root)
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZF + ZR) / 2), (2 * XB, yt - yb, DS.DEPTH), root)
    P.anchor("A_HIT_1", (-(XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    P.anchor("A_HIT_2", ((XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    extra = (f"frame: rack device, 2U, chassis 0.434 x {st['h']} x 0.700, front z={ZF}, rear z={ZR:.3f}, bottom y={yb:.5f}, top y={yt:.5f}; "
             f"24 vertical 2.5\" bays numbered from +x")
    return D.finish(root, mid, preview_views=((25, 18), (155, 25)), beauty_views=((22, 14), (160, 18)), size=(1100, 700), samples=36, extra=extra,
                    more_beauty=[(((-25, 10),), dict(target=(0.10, yb + 0.04, ZF), dist=0.30)),
                                 (((25, 55),), dict(hide=("@A_LID_0",)))])


# ====================================================================== 4U GPU server

def gpu_sled(n, cx, y0, y1, w, root, ZF, L=0.300):
    """A front-loading GPU sled (moving piece of A_SLED_n, pull=+z): a perforated face with its handle, release and
    status LED, the steel carrier and a passive double-width data-centre GPU standing on edge in it, with the blind-mate
    connector at the back."""
    cy = (y0 + y1) / 2
    h = y1 - y0
    a = P.anchor(f"A_SLED_{n}", P.Frame((cx, cy, ZF), Z, Y), (w, h, L), root,
                 meta=f"pull=+z,dist={L + 0.01:.3f},slot={n},gpu=double_width,latch=1,blind_mate=1")
    ww = w - 0.0006
    opening = D.rr(cx - ww / 2 + 0.0030, cx + ww / 2 - 0.0030, y0 + 0.040, y1 - 0.012, 0.002)
    D.zslab("sled_face", "black_plastic", D.rr(cx - ww / 2, cx + ww / 2, y0 + 0.0003, y1 - 0.0003, 0.0015), ZF - 0.0030, ZF, [opening], a)
    D.tiled_quads("sled_mesh", "tex_cat_server_sled_mesh", P.Frame((cx, (y0 + 0.040 + y1 - 0.012) / 2, ZF - 0.0012), Z, Y),
                  ww - 0.0060, y1 - 0.012 - y0 - 0.040, 0.05, 0.05, a, back=True)
    # the handle: a vertical pull bar on the lower part, the green release above it, the LED and number
    hx = cx
    P.tube("sled_handle", [(hx, y0 + 0.006, ZF), (hx, y0 + 0.008, ZF + 0.012), (hx, y0 + 0.030, ZF + 0.012), (hx, y0 + 0.032, ZF)],
           0.0028, "alu", a, 8)
    for yy in (y0 + 0.006, y0 + 0.032):
        D.box("sled_handle_foot", (hx - 0.004, yy - 0.003, ZF), (hx + 0.004, yy + 0.003, ZF + 0.002), "black_plastic", a)
    D.box("sled_release", (cx - 0.006, y0 + 0.0345, ZF), (cx + 0.006, y0 + 0.0390, ZF + 0.0035), GREEN, a, bevel=0.0005, seg=1, uv_solid=P.pal("green"))
    D.led(f"A_LED_SLED_{n}", P.Frame((cx + ww / 2 - 0.0060, y1 - 0.0060, ZF + 0.0003), Z, Y), 0.0024, 0.0024, "led_green", a, round_=True,
          meta="colour=green,fn=gpu_ok")
    D.led(f"A_LED_SLEDFAULT_{n}", P.Frame((cx - ww / 2 + 0.0060, y1 - 0.0060, ZF + 0.0003), Z, Y), 0.0024, 0.0024, "led_yellow", a, round_=True,
          meta="colour=amber,fn=fault")
    LABELS.quad("sled_no", f"GPU {n + 1}", P.Frame((cx, y1 - 0.0060, ZF + 0.00005), Z, Y), 0.0024, a)
    # carrier: a floor and one side wall (the GPU's back side), a rear crossbar with the blind-mate connector
    zb = ZF - L
    D.box("sled_floor", (cx - ww / 2, y0 + 0.0005, zb), (cx + ww / 2, y0 + 0.0015, ZF - 0.003), "steel", a)
    D.box("sled_wall", (cx + ww / 2 - 0.0010, y0 + 0.0005, zb), (cx + ww / 2, y1 - 0.004, ZF - 0.003), "steel", a)
    D.box("sled_rear", (cx - ww / 2, y0 + 0.0005, zb), (cx + ww / 2, y1 - 0.004, zb + 0.0012), "steel", a)
    D.box("sled_conn", (cx - 0.012, y0 + 0.010, zb - 0.010), (cx + 0.012, y0 + 0.040, zb), "black_plastic", a)
    D.box("sled_conn_pins", (cx - 0.010, y0 + 0.012, zb - 0.0104), (cx + 0.010, y0 + 0.038, zb - 0.0100), "gold", a)
    # the GPU: a passive card standing on edge (height along y, 2 slots thick along x), its fin stack at the front
    gx0, gx1 = cx - ww / 2 + 0.0020, cx + ww / 2 - 0.0030
    gy0, gy1 = y0 + 0.0030, y0 + 0.0030 + 0.1110
    gz0, gz1 = zb + 0.0040, zb + 0.0040 + 0.2670
    D.box("gpu_shroud", (gx0, gy0, gz0), (gx1, gy1, gz1), "paint_black", a, bevel=0.0012, seg=1)
    D.box("gpu_trim", (gx0 - 0.0002, gy1 - 0.008, gz0 + 0.010), (gx1 + 0.0002, gy1 - 0.006, gz1 - 0.010), "alu", a)
    D.decal("gpu_logo", ATLAS, "verdia", P.Frame(((gx0 + gx1) / 2, gy1 + 0.00005, (gz0 + gz1) / 2), Y, Z), 0.034, 0.0085, a)
    D.decal("gpu_label", ATLAS, "gpu_label", P.Frame((gx0 - 0.00005, (gy0 + gy1) / 2, (gz0 + gz1) / 2), NX, Y), 0.060, 0.0164, a)
    comb = D.comb_outline(11, (gx1 - gx0 - 0.002) / 11, 0.0008, 0.0, 0.006, 0.0005)
    P.slab("gpu_fins", comb, gy1 - gy0 - 0.012, "alu", P.Frame(((gx0 + gx1) / 2, (gy0 + gy1) / 2, gz1), Y, Z), parent=a)
    D.box("gpu_power", (gx0 + 0.006, gy1 - 0.020, gz0 - 0.003), (gx1 - 0.006, gy1 - 0.004, gz0), "black_plastic", a)
    return a


def build_gpu_server():
    import datacenter_server as DS
    mid = "srv_strata_sg840_4u"
    P.reset()
    textures()
    D.hex_perf_texture("cat_server_sled_mesh", 512, 512, 0.05, 0.05, 0.0036, 0.0014, web=(0.06, 0.06, 0.065))
    XB, ZF, ZR, T = DS.XB, DS.ZF, DS.ZR, DS.T
    units = 4
    h = units * U - 0.0009
    yb = (units * U - h) / 2
    yt = yb + h
    st = dict(units=units, h=h, H=h, YB=yb, YT=yt, sid=mid, psu_size=(0.0735, 0.0400))
    pw, ph = st["psu_size"]
    py = yb + T + 0.0012 + ph / 2
    st["psus"] = [(0.2140 - pw / 2 - k * (pw + 0.0012), py) for k in range(4)]
    root = c.root(mid)
    D.ROOT[0] = root
    # --- chassis: pan, side walls, the rear wall with its openings
    D.box("pan", (-XB + 0.0008, yb, ZR + 0.001), (XB - 0.0008, yb + T, ZF - 0.0045), "steel", root)
    for sx in (-1, 1):
        x0 = sx * (XB - 0.0008)
        D.box("side", (min(x0, x0 - sx * T), yb, ZR + 0.001), (max(x0, x0 - sx * T), yt - 0.0009, ZF - 0.0045), "steel", root)
    io_y = yb + 0.0150
    io = dict(ipmi=(-0.105, io_y), eth=[(-0.128, io_y), (-0.144, io_y)], vga=(-0.172, io_y), usb=[(-0.200, yb + 0.0110), (-0.200, yb + 0.0190)])
    slots = [(-0.200 + k * 0.0215, yb + 0.105) for k in range(8)]
    sw, sh = 0.0184, 0.0790
    holes = [D.rect(px - pw / 2 - 0.0006, px + pw / 2 + 0.0006, py - ph / 2 - 0.0006, py + ph / 2 + 0.0006) for (px, py) in st["psus"]]
    holes.append(D.rr(io["ipmi"][0] - 0.0072, io["ipmi"][0] + 0.0072, io_y - 0.0062, io_y + 0.0062, 0.0006))
    holes.append(D.rr(io["eth"][1][0] - 0.0072, io["eth"][0][0] + 0.0072, io_y - 0.0062, io_y + 0.0062, 0.0006))
    holes.append(D.rr(io["vga"][0] - 0.0165, io["vga"][0] + 0.0165, io_y - 0.0065, io_y + 0.0065, 0.0012))
    holes.append(D.rr(-0.200 - 0.0072, -0.200 + 0.0072, yb + 0.0072, yb + 0.0228, 0.0006))
    for (sx_, sy_) in slots:
        holes.append(D.rect(sx_ - sw / 2, sx_ + sw / 2, sy_ - sh / 2, sy_ + sh / 2))
    vx0, vx1, vy0, vy1 = -0.010, 0.205, yb + 0.055, yt - 0.010
    holes += [D.rr(vx0 + 0.004 + k * 0.0070, vx0 + 0.0075 + k * 0.0070, vy0 + 0.004, vy1 - 0.004, 0.0015) for k in range(int((vx1 - vx0 - 0.008) / 0.0070))]
    D.zslab("rear_wall", "paint_black", D.rect(-XB + 0.0008, XB - 0.0008, yb + 0.0002, yt - 0.0009), ZR, ZR + T, holes, root)
    D.zslab("rear_vent_dark", "dark_plastic", D.rect(vx0, vx1, vy0, vy1), ZR + 0.012, ZR + 0.013, (), root)
    for (sx_, sy_) in slots:   # vertical low-profile slot covers (one NIC per GPU), screwed at the top
        sl = [D.rect(sx_ - 0.0035, sx_ + 0.0035, sy_ - sh / 2 + 0.010 + k * 0.0085, sy_ - sh / 2 + 0.0135 + k * 0.0085) for k in range(7)]
        D.zslab("slot_cover", "steel", D.rect(sx_ - sw / 2 + 0.0004, sx_ + sw / 2 - 0.0004, sy_ - sh / 2 + 0.0004, sy_ + sh / 2 - 0.0004),
                ZR - 0.0008, ZR + 0.0002, sl, root)
        P.cylinder("slot_screw", P.Frame((sx_, sy_ + sh / 2 + 0.0045, ZR - 0.0004), NZ, Y), 0.0022, 0.0016, "nickel", 10, root, z0=0.0)
    ipmi = P.Frame((io["ipmi"][0], io_y, ZR), NZ, Y)
    D.rj45_jack(ipmi, root, True)
    P.anchor("A_PORT_IPMI_0", ipmi, (0.016, 0.014, 0.02), root, meta="depth=0.012,rj45=1,latch=+up,net=bmc")
    D.led("A_LED_IPMI_0", P.Frame((io["ipmi"][0] - 0.0045, io_y - 0.0052, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_green", root)
    for k, (ex_, ey_) in enumerate(io["eth"]):
        efr = P.Frame((ex_, ey_, ZR), NZ, Y)
        D.rj45_jack(efr, root, True)
        P.anchor(f"A_PORT_ETH_{k}", efr, (0.0145, 0.012, 0.02), root, meta=f"depth=0.012,rj45=1,latch=+up,speed=10g,lom={k + 1}")
        D.led(f"A_LED_LINK_{k}", P.Frame((ex_ + 0.0042, ey_ - 0.0050, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_green", root, meta="colour=green,fn=link")
        D.led(f"A_LED_ACT_{k}", P.Frame((ex_ - 0.0042, ey_ - 0.0050, ZR - 0.0001), NZ, Y), 0.0022, 0.0012, "led_yellow", root, meta="colour=amber,fn=activity")
    vfr = P.Frame((io["vga"][0], io_y, ZR - 0.0004), NZ, Y)
    D.vga_port(vfr, root)
    P.anchor("A_PORT_VGA_0", vfr, (0.032, 0.013, 0.012), root, meta="depth=0.006,vga=1")
    for k, (ux_, uy_) in enumerate(io["usb"]):
        ufr = P.Frame((ux_, uy_, ZR), NZ, Y)
        D.usba_port(ufr, root)
        P.anchor(f"A_PORT_USBA_{k}", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=3.0")
    D.led("A_LED_ID_1", P.Frame((-0.090, yb + 0.030, ZR - 0.0001), NZ, Y), 0.0030, 0.0030, "led_blue", root, meta="colour=blue,fn=identify", round_=True)
    for txt, lx, ly in (("IPMI", io["ipmi"][0], io_y + 0.0080), ("VGA", io["vga"][0], io_y + 0.0083), ("USB", -0.200, yb + 0.0262),
                        ("1", io["eth"][0][0], io_y + 0.0080), ("2", io["eth"][1][0], io_y + 0.0080)):
        LABELS.quad("legend", txt, P.Frame((lx, ly, ZR - 0.00005), NZ, Y), 0.0026, root)
    for k, (px, _) in enumerate(st["psus"]):
        LABELS.quad("legend", f"PSU {k + 1}", P.Frame((px, py + ph / 2 + 0.0040, ZR - 0.00005), NZ, Y), 0.0026, root)
    # --- front: 8 GPU sleds over a strip with 4 NVMe bays, the badge and a front USB
    sled_w = 0.0505
    x_left = sled_w * 4
    sy0, sy1 = yb + 0.0225, yt - 0.0020
    fh = [D.rect(x_left - sled_w * (k + 1) + 0.0002, x_left - sled_w * k - 0.0002, sy0, sy1) for k in range(8)]
    st["bay_size"], st["bay_kind"] = (0.0740, 0.0190), "sff"
    bays = [(k, -0.2065 + 0.0755 * (k + 0.5), yb + 0.0018 + 0.0100) for k in range(4)]
    fh += [D.rect(cx - 0.0370, cx + 0.0370, cy - 0.0095, cy + 0.0095) for (_, cx, cy) in bays]
    usb = (0.200, yb + 0.0110)
    fvents = [D.rect(0.104 + k * 0.0046, 0.1066 + k * 0.0046, yb + 0.0040, yb + 0.0190) for k in range(9)]
    D.zslab("front_frame", "steel_dark", D.rect(-XB + 0.0008, XB - 0.0008, yb + 0.0002, yt - 0.0009), ZF - 0.0030, ZF - 0.0005,
            fh + fvents + [D.usba_outline(*usb)], root)
    D.zslab("front_vent_dark", "dark_plastic", D.rect(0.100, 0.150, yb + 0.003, yb + 0.020), ZF - 0.010, ZF - 0.009, (), root)
    for k in range(9):    # the sled guides between the bays
        x = x_left - sled_w * k
        D.box("sled_guide", (x - 0.0004, sy0, ZF - 0.305), (x + 0.0004, sy0 + 0.006, ZF - 0.003), "steel_dark", root)
        D.box("sled_guide", (x - 0.0004, sy1 - 0.006, ZF - 0.305), (x + 0.0004, sy1, ZF - 0.003), "steel_dark", root)
    D.box("sled_shelf", (-x_left, sy0 - 0.0010, ZF - 0.305), (x_left, sy0, ZF - 0.003), "steel_dark", root)
    for k in range(8):
        gpu_sled(k, x_left - sled_w * (k + 0.5), sy0, sy1, sled_w - 0.0004, root, ZF)
    D.box("nvme_cage", (-0.2065, yb + 0.0010, ZF - 0.115), (0.0955, yb + 0.0215, ZF - 0.012), "steel_dark", root)
    for (n, cx, cy) in bays:
        DS.drive_tray(st, n, cx, cy, root)
    ufr = P.Frame((usb[0], usb[1], ZF - 0.0005), Z, Y)
    D.usba_port(ufr, root)
    P.anchor("A_PORT_USBA_FRONT_0", ufr, (0.0145, 0.0072, 0.02), root, meta="depth=0.009,usb=3.0")
    D.decal("badge", ATLAS, "sg840", P.Frame((0.170, yb + 0.0175, ZF - 0.00045), Z, Y), 0.034, 0.0085, root)
    server_ears(st, root, 2 * U + D.HOLES_IN_U[1])
    # --- inside: the midplane, the fan wall, the board with two CPUs, DIMMs and PCIe switches, risers to the rear slots
    zm = ZF - 0.318
    D.box("midplane", (-XB + 0.004, yb + T, zm - 0.0016), (XB - 0.004, yt - 0.004, zm), "pcb_green", root)
    for k in range(8):
        cx = x_left - sled_w * (k + 0.5)
        D.box("mid_conn", (cx - 0.013, sy0 + 0.009, zm), (cx + 0.013, sy0 + 0.041, zm + 0.008), "black_plastic", root)
    zfan = zm - 0.032
    fs, fd = 0.080, 0.038
    D.box("fan_cage", (-XB + 0.002, yb + T, zfan - fd / 2 - 0.004), (XB - 0.002, yb + T + 0.002, zfan + fd / 2 + 0.004), "steel_dark", root)
    k = 0
    for r in range(2):
        fy = yb + T + 0.0060 + fs / 2 + r * (fs + 0.0040)
        for j in range(5):
            fx = (j - 2) * 0.0860
            a = P.anchor(f"A_FAN_{k}", P.Frame((fx, fy, zfan), Z, Y), (fs, fs, fd), root, meta="axis=z,spin=1,rpm=11000,hotswap=1,pull=+y")
            D.server_fan(a, fs, fd, blades=7, parent=root, segs=14)
            if r == 1:
                D.box("fan_handle", (fx - fs * 0.30, fy + fs / 2, zfan - 0.004), (fx + fs * 0.30, min(fy + fs / 2 + 0.004, yt - 0.0012), zfan + 0.004),
                      "black_plastic", root)
            k += 1
    btop = yb + T + 0.0030 + 0.0016
    D.yslab("board", "pcb_green", D.rect(-XB + 0.004, XB - 0.004, ZR + 0.200, zfan - fd / 2 - 0.010), yb + T + 0.0030, btop, (), root)
    zc = (ZR + 0.200 + zfan - fd / 2 - 0.010) / 2 + 0.010
    for gx in (-0.090, 0.090):
        D.box("socket", (gx - 0.040, btop, zc - 0.048), (gx + 0.040, btop + 0.0045, zc + 0.048), "steel_dark", root)
        D.box("sink_base", (gx - 0.042, btop + 0.0045, zc - 0.054), (gx + 0.042, btop + 0.0070, zc + 0.054), "copper", root)
        comb = D.comb_outline(32, 0.084 / 32, 0.0005, 0.0, 0.085, 0.0012)
        P.slab("sink_fins", comb, 0.108, "alu", P.Frame((gx, btop + 0.0070, zc), Z, Y), parent=root)
        for side in (-1, 1):
            for j in range(4):
                dx = gx + side * (0.052 + j * 0.0078)
                D.box("dimm_slot", (dx - 0.0030, btop, zc - 0.0735), (dx + 0.0030, btop + 0.0048, zc + 0.0735), "black_plastic", root)
                D.box("dimm", (dx - 0.00065, btop + 0.0030, zc - 0.0667), (dx + 0.00065, btop + 0.0342, zc + 0.0667), "pcb_green", root)
                for s2 in (-1, 1):
                    P.quad("dimm_face", P.Frame((dx + s2 * 0.00075, btop + 0.0186, zc), (s2, 0, 0), Y), 0.1335, 0.0312, "tex_server_print", root,
                           uv=DS.ATLAS.uv("dimm"))
    for gx in (-0.150, 0.0, 0.150):    # PCIe switch heatsinks between the fans and the CPUs
        D.box("plx_sink", (gx - 0.022, btop, zfan - fd / 2 - 0.060), (gx + 0.022, btop + 0.022, zfan - fd / 2 - 0.016), "alu", root)
    for (sx_, sy_) in slots[::2]:     # risers carrying the rear slots
        D.box("riser", (sx_ - 0.0010, btop, ZR + 0.012), (sx_ + 0.0010, sy_ + sh / 2, ZR + 0.140), "pcb_green", root)
    # PSU cage and power distribution
    for (px, py_) in st["psus"]:
        D.box("psu_cage", (px - pw / 2 - 0.0012, yb + T, ZR + 0.001), (px - pw / 2 - 0.0006, py_ + ph / 2 + 0.001, ZR + 0.190), "steel", root)
    D.box("pdb", (st["psus"][-1][0] - pw / 2, yb + T, ZR + 0.196), (st["psus"][0][0] + pw / 2, py + ph / 2, ZR + 0.198), "pcb_green", root)
    D.box("psu_shelf", (st["psus"][-1][0] - pw / 2 - 0.002, py + ph / 2 + 0.001, ZR + 0.001), (st["psus"][0][0] + pw / 2 + 0.002, py + ph / 2 + 0.002, ZR + 0.200),
          "steel", root)
    DS.lid(st, root)
    for k in range(4):
        a = DS.psu(st, k, root)
        a["meta"] = f"pull=-z,dist=0.195,watts=3000,eff=titanium,slot={k},redundancy=3+1"
    DS.slide_rail(st, "L", root)
    DS.slide_rail(st, "R", root)
    P.anchor("A_HIT_0", (0, (yb + yt) / 2, (ZF + ZR) / 2), (2 * XB, yt - yb, DS.DEPTH), root)
    P.anchor("A_HIT_1", (-(XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    P.anchor("A_HIT_2", ((XB + D.EAR_W / 2) / 2, (yb + yt) / 2, ZF / 2), (D.EAR_W / 2 - XB, yt - yb, ZF), root)
    extra = (f"frame: rack device, 4U, chassis 0.434 x {h:.4f} x 0.700, front z={ZF}, rear z={ZR:.3f}, bottom y={yb:.5f}, top y={yt:.5f}; "
             f"8 GPU sleds from +x, midplane z={zm:.3f}, fan wall z={zfan:.3f}")
    return D.finish(root, mid, preview_views=((25, 18), (155, 25)), beauty_views=((24, 14), (160, 18)), size=(1100, 800), samples=36, extra=extra,
                    more_beauty=[(((-25, 8),), dict(target=(0.08, yb + 0.09, ZF), dist=0.45)),
                                 (((25, 55),), dict(hide=("@A_LID_0",))),
                                 (((200, 15),), dict(target=(0.0, yb + 0.09, ZR), dist=0.65))])
