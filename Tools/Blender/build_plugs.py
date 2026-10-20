"""
Cable plugs and small items: plug_<kind>, screw_ph2, screw_ph0, screw_thumb, standoff_brass, usb_stick.

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_plugs.py -- [kind ...]

Plug frame (REALISM.md section 2): origin at the centre of the contact face, +Z back along the cable,
+Y "up" = the latch / label side. The housing occupies z 0..L, the wire stubs leave the back.
Small items: screws have their origin at the underside of the head (the seating plane), +Z out of the
head (the direction the screwdriver comes from), the thread below (-Z). The standoff has its origin at
its base (the tray contact plane), +Z towards the board. The USB stick is a plug: origin at the tip of
the USB-A shell, +Z back along the stick.

Every model has A_HIT_0 (the body) and, where a cable continues, A_CABLE_0 at the end of the wire stub
(+Z along the cable, meta r=<bundle radius>,n=<wires>). Plugs with a latch have A_LATCH_0 (the press point).

The builders (PLUGS[kind](frame, parent)) are reused by build_case.py for the case's loose plugs.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

LABELS_FILE = "parts_c_plug_labels"
LABELS_TAG = "tex_" + LABELS_FILE
LABELS = ["POWER SW", "RESET SW", "POWER LED", "H.D.D LED", "HD AUDIO", "USB 3.0", "BASEMENT OS 1.0", "INSTALLER"]
STICK_FILE = "usb_stick_label"


def label_uv(i):
    """UV region of label strip i (8 strips stacked, strip 0 at the top)."""
    n = len(LABELS)
    return (0.0, 1.0 - (i + 1) / n, 1.0, 1.0 - i / n)


def write_label_textures():
    art = P.Art(1024, 128 * len(LABELS), bg=(0.02, 0.02, 0.022), name="plug_labels")
    for i, s in enumerate(LABELS):
        y = art.h - (i + 0.5) * 128
        art.text(s, art.w / 2, y, 96, (0.93, 0.93, 0.9), "arialbd.ttf", align="CENTER", maxw=980, valign="CENTER")
    art.render(LABELS_FILE)
    art.dispose()
    # USB stick label: a printed sticker wrapping the top of the stick
    art = P.Art(1024, 384, bg=(0.07, 0.08, 0.1), name="stick_label")
    art.grad(0, 0, 1024, 384, (0.05, 0.06, 0.08), (0.12, 0.14, 0.2))
    art.rect(0, 300, 1024, 12, (0.95, 0.45, 0.1))
    art.text("BASEMENT OS", 60, 205, 92, (0.96, 0.96, 0.94), "seguibl.ttf", maxw=760)
    art.text("1.0", 830, 205, 92, (0.95, 0.45, 0.1), "seguibl.ttf")
    art.text("INSTALLER  \u2022  BOOTABLE USB", 62, 120, 46, (0.75, 0.78, 0.85), "segoeuib.ttf", maxw=900)
    art.text("16 GB  USB 3.0", 62, 50, 40, (0.55, 0.58, 0.65), "segoeui.ttf")
    art.circle(950, 80, 40, (0.95, 0.45, 0.1))
    art.text("B", 950, 80, 52, (0.07, 0.08, 0.1), "seguibl.ttf", align="CENTER", valign="CENTER")
    art.render(STICK_FILE)
    art.dispose()


# ---------------------------------------------------------------- shared parts

def wire_stubs(fr, parent, pts, r, z0, length, tag="rubber", colours=("cable_black",), name="wire", converge=0.0, segs=8):
    """Straight insulated wire stubs from the back face (z0) along +Z. pts are local (x, y) wire centres.
    converge pulls the far ends towards the bundle centre."""
    if colours is None:
        colours = ("cable_black",)   # black insulation through the palette: joins with the tinned terminals
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    for i, (x, y) in enumerate(pts):
        x1 = x + (cx - x) * converge
        y1 = y + (cy - y) * converge
        f = P.Frame(fr.p(x, y, z0), fr.d(x1 - x, y1 - y, length), fr.v if abs(fr.d(x1 - x, y1 - y, length).normalized().dot(fr.v)) < 0.9 else fr.u)
        ln = math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2 + length ** 2)
        if colours is not None:
            P.cylinder(name, f, r, ln, P.PALETTE_TAG, segs, parent, z0=0.0, uv_solid=P.pal(colours[i % len(colours)]), smooth=70)
        else:
            P.cylinder(name, f, r, ln, tag, segs, parent, z0=0.0, smooth=70)
    return fr.p(cx, cy, z0 + length)


def cavity(w, h, cx, cy, kind="S", ch=0.0006):
    """A pin cavity outline: S square (slightly rounded), D polarised (two corners chamfered at the top),
    U polarised at the bottom."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    if kind == "D":
        return [(x0, y0), (x1, y0), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch)]
    if kind == "U":
        return [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1), (x0, y1), (x0, y0 + ch)]
    return P.rrect(w, h, 0.00015, cx, cy, 2)


def latch(fr, parent, x, y_top, z_hook, length, width=0.0034, tag="connector_black", name="latch"):
    """A cantilever latch on the +Y face: hook at the front, pivot block, ridged press pad at the back."""
    lift = 0.0011
    P.cube(name, (x, y_top + lift, z_hook + length / 2), (width, 0.0007, length), tag, fr, parent, bevel=0.0002)
    P.cube(name, (x, y_top + 0.0005, z_hook + 0.0004), (width, 0.0013, 0.0012), tag, fr, parent)          # hook
    P.cube(name, (x, y_top + 0.0005, z_hook + length * 0.55), (width * 0.8, 0.001, 0.0016), tag, fr, parent)  # pivot
    P.cube(name, (x, y_top + lift + 0.0006, z_hook + length - 0.0014), (width + 0.0012, 0.0009, 0.0028), tag, fr, parent,
           bevel=0.0002)
    for k in range(3):
        P.cube(name, (x, y_top + lift + 0.0012, z_hook + length - 0.0024 + k * 0.0009), (width + 0.0010, 0.0003, 0.0003),
               tag, fr, parent)
    return fr.p(x, y_top + lift + 0.001, z_hook + length - 0.0014)


def pin_face(fr, parent, cells, W, H, face_t, tag, name="face", term_tag="tin", cav=0.0030, outline=None):
    """The contact face: a plate with one cavity per cell (x, y, kind) and a tinned terminal in each."""
    holes = [cavity(cav, cav, x, y, k) for (x, y, k) in cells if k != "X"]
    P.slab(name, outline or P.rrect(W, H, 0.0004), face_t, tag, fr.sub(0, 0, face_t / 2), holes=holes, parent=parent)
    # cavity floors (dark) and the terminals inside
    P.cube(name + "_floor", (0, 0, face_t + 0.0002), (W - 0.0006, H - 0.0006, 0.0004), tag, fr, parent)
    for (x, y, k) in cells:
        if k == "X":
            continue
        if term_tag == "tin":
            P.cube("term", (x, y, face_t - 0.0004), (cav * 0.42, cav * 0.42, 0.0008), P.PALETTE_TAG, fr, parent, uv_solid=P.pal("tin"))
        else:
            P.cube("term", (x, y, face_t - 0.0004), (cav * 0.42, cav * 0.42, 0.0008), term_tag, fr, parent)


def hit_and_cable(fr, root, centre, size, cable_end=None, r=0.003, n=1, latch_at=None, parent_anchor=None):
    """Anchors for the standalone plug models (not used when the plug is part of a case)."""
    if parent_anchor is not None:
        return
    P.anchor("A_HIT_0", fr.sub(*centre), size, root)
    if cable_end is not None:
        P.anchor("A_CABLE_0", P.Frame(cable_end, fr.w, fr.v), (r * 2, r * 2, 0.01), root, meta=f"r={r:.4f},n={n}")
    if latch_at is not None:
        P.anchor("A_LATCH_0", P.Frame(latch_at, fr.v, fr.w), (0.004, 0.004, 0.003), root, meta="press=-y")


# ---------------------------------------------------------------- Mini-Fit Jr family (4.2 mm pitch)

MF_PITCH = 0.0042


def minifit(fr, parent, cols, rows=2, keys=None, latch_on=True, wire_len=0.028, wire_tag="rubber", name="mf",
            tag="connector_black", x0=0.0, colours=None, wire_r=0.00125):
    """A Mini-Fit Jr plug housing (ATX, EPS, PCIe, modular PSU ends) centred at local x0."""
    p = MF_PITCH
    W = cols * p + 0.0012
    H = rows * p + 0.0010
    L = 0.0128
    face_t = 0.0032
    cells = []
    for j in range(rows):
        for i in range(cols):
            x = x0 + (i - (cols - 1) / 2) * p
            y = (j - (rows - 1) / 2) * p
            k = "S"
            if keys:
                k = keys[j][i]
            cells.append((x, y, k))
    pin_face(fr.sub(x0, 0, 0), parent, [(x - x0, y, k) for (x, y, k) in cells], W, H, face_t, tag, name)
    P.cube(name + "_body", (x0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), tag, fr, parent, bevel=0.0003)
    # the ribs along the sides of real housings
    for sx in (-1, 1):
        P.cube(name + "_rib", (x0 + sx * (W / 2 + 0.0002), 0, L * 0.55), (0.0004, H * 0.6, L * 0.7), tag, fr, parent)
    press = None
    if latch_on:
        press = latch(fr, parent, x0, H / 2, 0.0012, 0.0105, tag=tag, name=name + "_latch")
    wp = [(x, y) for (x, y, k) in cells]
    end = wire_stubs(fr, parent, wp, wire_r, L, wire_len, wire_tag, colours, name + "_wire", converge=0.15)
    return dict(W=W, H=H, L=L, end=end, press=press)


ATX24_KEYS = [list("DSSDDSDSSDDS"), list("SDDSSDSDDSSD")]
EPS4_KEYS = [list("SS"), list("DD")]
PCIE6_KEYS = [list("DSD"), list("SDS")]
PCIE2_KEYS = [list("D"), list("S")]


def plug_atx24(fr, parent, anchors_root=None):
    r = minifit(fr, parent, 12, 2, ATX24_KEYS, name="atx")
    hit_and_cable(fr, anchors_root, (0, 0, r["L"] / 2), (r["W"] + 0.002, r["H"] + 0.004, r["L"]), r["end"], 0.0085, 24,
                  r["press"], parent_anchor=None if anchors_root else 1)
    return r


def plug_eps8(fr, parent, anchors_root=None):
    """CPU 4+4: two 2x2 halves side by side, each with its latch."""
    gap = 0.0003
    w4 = 2 * MF_PITCH + 0.0012
    a = minifit(fr, parent, 2, 2, EPS4_KEYS, name="eps_a", x0=-(w4 + gap) / 2)
    b = minifit(fr, parent, 2, 2, EPS4_KEYS, name="eps_b", x0=(w4 + gap) / 2)
    # the dovetail rail that joins the halves
    P.cube("eps_rail", (0, -a["H"] / 2 - 0.0003, 0.007), (0.0016, 0.0006, 0.009), "connector_black", fr, parent)
    end = (a["end"] + b["end"]) / 2
    W = 2 * w4 + gap
    hit_and_cable(fr, anchors_root, (0, 0, a["L"] / 2), (W + 0.002, a["H"] + 0.004, a["L"]), end, 0.0045, 8,
                  a["press"], parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=a["H"], L=a["L"], end=end)


def plug_pcie8(fr, parent, anchors_root=None):
    """PCIe 6+2: a 2x3 with the latch and a loose 2x1 clipped to its side."""
    gap = 0.0003
    w6 = 3 * MF_PITCH + 0.0012
    w2 = 1 * MF_PITCH + 0.0012
    tot = w6 + gap + w2
    x6 = -tot / 2 + w6 / 2
    x2 = tot / 2 - w2 / 2
    a = minifit(fr, parent, 3, 2, PCIE6_KEYS, name="pcie_6", x0=x6)
    b = minifit(fr, parent, 1, 2, PCIE2_KEYS, latch_on=False, name="pcie_2", x0=x2)
    # the hook of the +2 half riding in the 6-pin's slot
    P.cube("pcie_hook", (x2, a["H"] / 2 + 0.0005, 0.006), (0.0024, 0.001, 0.008), "connector_black", fr, parent)
    end = (a["end"] * 6 + b["end"] * 2) / 8
    hit_and_cable(fr, anchors_root, (0, 0, a["L"] / 2), (tot + 0.002, a["H"] + 0.004, a["L"]), end, 0.0045, 8,
                  a["press"], parent_anchor=None if anchors_root else 1)
    return dict(W=tot, H=a["H"], L=a["L"], end=end)


def plug_mod(fr, parent, anchors_root, cols, keys, wires_n=None, rows=2, flat=False):
    r = minifit(fr, parent, cols, rows, keys, name="mod")
    hit_and_cable(fr, anchors_root, (0, 0, r["L"] / 2), (r["W"] + 0.002, r["H"] + 0.004, r["L"]), r["end"],
                  0.002 * math.sqrt(cols * rows) + 0.002, cols * rows, r["press"], parent_anchor=None if anchors_root else 1)
    return r


def plug_mod_atx(fr, parent, anchors_root=None):
    return plug_mod(fr, parent, anchors_root, 10, [list("DSDSSDSDSD"), list("SDSDDSDSDS")])


def plug_mod_cpu(fr, parent, anchors_root=None):
    return plug_mod(fr, parent, anchors_root, 4, [list("SSDD"), list("DDSS")])


def plug_mod_pcie(fr, parent, anchors_root=None):
    return plug_mod(fr, parent, anchors_root, 4, [list("DSDS"), list("SDSD")])


def plug_mod_sata(fr, parent, anchors_root=None):
    return plug_mod(fr, parent, anchors_root, 3, [list("SDS"), list("DSD")])


# ---------------------------------------------------------------- 12V-2x6 (16-pin, 3.0 mm pitch)

def plug_p12v2x6(fr, parent, anchors_root=None, name="hp"):
    p = 0.003
    W = 6 * p + 0.0016
    Hp = 2 * p + 0.0012
    Hs = 0.0030   # the sideband (sense) row above the power pins
    L = 0.0150
    face_t = 0.0030
    tag = "connector_black"
    yc = -Hs / 2      # power block centre
    ys = Hp / 2 - Hs / 2 + 0.0002  # sense row centre (above, local)
    cells = []
    for j in range(2):
        for i in range(6):
            cells.append(((i - 2.5) * p, yc + (j - 0.5) * p, "D" if (i + j) % 2 else "S"))
    outline = [(-W / 2, -Hp / 2 - Hs / 2), (W / 2, -Hp / 2 - Hs / 2), (W / 2, Hp / 2 - Hs / 2 + 0.0002),
               (W / 2 - 0.0018, Hp / 2 - Hs / 2 + 0.0002), (W / 2 - 0.0018, Hp / 2 + Hs / 2),
               (-W / 2 + 0.0018, Hp / 2 + Hs / 2), (-W / 2 + 0.0018, Hp / 2 - Hs / 2 + 0.0002), (-W / 2, Hp / 2 - Hs / 2 + 0.0002)]
    holes = [cavity(0.0021, 0.0021, x, y, k, 0.0004) for (x, y, k) in cells]
    sense = [(-0.0045 + i * 0.003, yc + Hp / 2 + Hs / 2 - 0.0002) for i in range(4)]
    holes += [P.rrect(0.0012, 0.0012, 0.0002, x, y, 2) for (x, y) in sense]
    P.slab(name + "_face", outline, face_t, tag, fr.sub(0, 0, face_t / 2), holes=holes, parent=parent)
    for (x, y, k) in cells:
        P.cube("term", (x, y, face_t - 0.0004), (0.0009, 0.0009, 0.0008), P.PALETTE_TAG, fr, parent, uv_solid=P.pal("tin"))
    # body follows the outline
    P.slab(name + "_body", outline, L - face_t, tag, fr.sub(0, 0, face_t + (L - face_t) / 2), parent=parent)
    P.cube(name + "_floor", (0, yc, face_t + 0.0002), (W - 0.0006, Hp - 0.0006, 0.0004), tag, fr, parent)
    # latch over the sense row, and the grip ribs on the sides
    press = latch(fr, parent, 0, Hp / 2 + Hs / 2 - Hs / 2, 0.0010, 0.012, width=0.0032, tag=tag, name=name + "_latch")
    for sx in (-1, 1):
        for k in range(4):
            P.cube(name + "_grip", (sx * (W / 2 + 0.0002), yc, 0.008 + k * 0.0014), (0.0004, Hp * 0.8, 0.0006), tag, fr, parent)
    wp = [(x, y) for (x, y, k) in cells]
    end = wire_stubs(fr, parent, wp, 0.0013, L, 0.028, "rubber", None, name + "_wire", converge=0.1)
    wire_stubs(fr, parent, [(x, y) for (x, y) in sense], 0.00055, L, 0.026, "rubber", None, name + "_sense", converge=0.4)
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, Hp + Hs + 0.004, L), end, 0.006, 16, press,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=Hp + Hs, L=L, end=end)


def plug_mod_12v2x6(fr, parent, anchors_root=None):
    return plug_p12v2x6(fr, parent, anchors_root, name="mhp")


# ---------------------------------------------------------------- SATA

def sata_l_hole(w, h, blade_w, cx=0.0, cy=0.0):
    """The L-shaped mouth of a SATA plug: a slot for the contact blade plus the key leg at one end."""
    t = h * 0.42
    x0, x1 = cx - w / 2, cx + w / 2
    y0 = cy - h / 2
    return [(x0, y0), (x1, y0), (x1, y0 + t), (x0 + blade_w, y0 + t), (x0 + blade_w, cy + h / 2), (x0, cy + h / 2)]


def plug_sata_data(fr, parent, anchors_root=None):
    W, H, L = 0.0108, 0.0058, 0.0145
    tag = "connector_black"
    face_t = 0.0016
    hole = sata_l_hole(W - 0.0024, H - 0.0024, 0.0016)
    P.slab("sd_face", P.rrect(W, H, 0.0005), face_t, tag, fr.sub(0, 0, face_t / 2), holes=[hole], parent=parent)
    P.cube("sd_body", (0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), tag, fr, parent, bevel=0.0005)
    # the seven contacts on the floor of the mouth
    for i in range(7):
        P.cube("sd_pin", (-W / 2 + 0.0024 + 0.0004 + i * 0.00105 + 0.0006, -H / 2 + 0.0016, 0.0012),
               (0.0006, 0.0003, 0.0015), "gold", fr, parent)
    # metal latch clip on top
    P.cube("sd_clip", (0, H / 2 + 0.0003, 0.0075), (0.0042, 0.0005, 0.0105), "steel", fr, parent)
    P.cube("sd_clip", (0, H / 2 + 0.0002, 0.0012), (0.0042, 0.0008, 0.0009), "steel", fr, parent)
    P.cube("sd_clip_tab", (0, H / 2 + 0.0009, 0.0122), (0.0046, 0.0009, 0.0025), "steel", fr, parent)
    # flat 7-wire cable
    P.cube("sd_strain", (0, 0, L + 0.002), (0.0082, 0.0024, 0.004), tag, fr, parent, bevel=0.0006)
    P.cube("sd_cable", (0, 0, L + 0.004 + 0.012), (0.0076, 0.0014, 0.024), "rubber", fr, parent, bevel=0.0005)
    end = fr.p(0, 0, L + 0.028)
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, H + 0.003, L), end, 0.004, 7, fr.p(0, H / 2 + 0.001, 0.0122),
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=H, L=L, end=end)


def plug_sata_power(fr, parent, anchors_root=None):
    W, H, L = 0.0228, 0.0062, 0.0125
    tag = "connector_black"
    face_t = 0.0016
    hole = sata_l_hole(W - 0.003, H - 0.0026, 0.0018)
    P.slab("sp_face", P.rrect(W, H, 0.0006), face_t, tag, fr.sub(0, 0, face_t / 2), holes=[hole], parent=parent)
    P.cube("sp_body", (0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), tag, fr, parent, bevel=0.0005)
    for i in range(15):
        P.cube("sp_pin", (-W / 2 + 0.0015 + 0.0024 + i * 0.00122, -H / 2 + 0.0017, 0.0012), (0.0006, 0.0003, 0.0015),
               "gold", fr, parent)
    # 5 wires out of the back (yellow 12 V, black, red 5 V, black, orange 3.3 V) - modern cables: all black
    pts = [(-0.0076 + i * 0.0038, 0.0) for i in range(5)]
    end = wire_stubs(fr, parent, pts, 0.0011, L, 0.026, "rubber", None, "sp_wire", converge=0.1)
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, H + 0.003, L), end, 0.006, 5, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=H, L=L, end=end)


# ---------------------------------------------------------------- fan plugs (2.54 mm KK)

def fan_plug(fr, parent, anchors_root, pins, tag, colours):
    p = 0.00254
    W = 4 * p + 0.0006 if pins == 4 else 3 * p + 0.0006
    H, L = 0.0046, 0.0130
    face_t = 0.0016
    cells = [((i - (pins - 1) / 2) * p, -0.0002, "S") for i in range(pins)]
    holes = [P.rrect(0.0013, 0.0013, 0.0001, x, y, 2) for (x, y, k) in cells]
    P.slab("fan_face", P.rrect(W, H, 0.0003), face_t, tag, fr.sub(0, 0, face_t / 2), holes=holes, parent=parent)
    P.cube("fan_body", (0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), tag, fr, parent, bevel=0.0002)
    P.cube("fan_floor", (0, 0, face_t + 0.0001), (W - 0.0005, H - 0.0005, 0.0003), tag, fr, parent)
    for (x, y, k) in cells:
        P.cube("term", (x, y, face_t - 0.0003), (0.0006, 0.0006, 0.0006), P.PALETTE_TAG, fr, parent, uv_solid=P.pal("tin"))
    # the two polarising ribs on the back (-Y) side that slide along the header's ramp
    for sx in (-1, 1):
        x = sx * (p * (1.0 if pins == 4 else 0.5))
        P.cube("fan_rib", (x, -H / 2 - 0.0005, L * 0.5), (0.0008, 0.001, L * 0.92), tag, fr, parent)
    # the grip ramp on top
    P.cube("fan_grip", (0, H / 2 + 0.0002, L * 0.75), (W * 0.7, 0.0004, L * 0.35), tag, fr, parent)
    pts = [(x, y) for (x, y, k) in cells]
    end = wire_stubs(fr, parent, pts, 0.0007, L, 0.026, "rubber", colours, "fan_wire", converge=0.25)
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, H + 0.003, L), end, 0.0025, pins, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=H, L=L, end=end)


def plug_fan4(fr, parent, anchors_root=None):
    """4-pin PWM: black housing, black wires (modern PWM fans)."""
    return fan_plug(fr, parent, anchors_root, 4, "connector_black", ["cable_black"] * 4)


def plug_fan3(fr, parent, anchors_root=None):
    """3-pin DC: the classic white housing with black (GND), red (+12 V) and yellow (tach) wires."""
    return fan_plug(fr, parent, anchors_root, 3, "connector_white", ["black", "red", "yellow"])


# ---------------------------------------------------------------- front-panel Dupont plugs (2.54 mm)

def dupont(fr, parent, anchors_root, cols, rows, label, colours, blocked=(), pair=True, signs=None, cable="pair",
           tag="connector_black"):
    p = 0.00254
    W, H = cols * p, rows * p
    L = 0.0140
    face_t = 0.0012
    cells = []
    for j in range(rows):
        for i in range(cols):
            k = "X" if (j * cols + i) in blocked else "S"
            cells.append(((i - (cols - 1) / 2) * p, (j - (rows - 1) / 2) * p, k))
    holes = [P.rrect(0.0011, 0.0011, 0.0001, x, y, 2) for (x, y, k) in cells if k != "X"]
    P.slab("dp_face", P.rrect(W, H, 0.0002), face_t, tag, fr.sub(0, 0, face_t / 2), holes=holes, parent=parent)
    P.cube("dp_body", (0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), tag, fr, parent, bevel=0.00015)
    P.cube("dp_floor", (0, 0, face_t + 0.0001), (W - 0.0004, H - 0.0004, 0.0003), tag, fr, parent)
    # crimp windows (the little openings on the side of each Dupont shell)
    for (x, y, k) in cells:
        if k == "X":
            continue
        P.cube("term", (x, y, face_t - 0.0002), (0.0005, 0.0005, 0.0004), P.PALETTE_TAG, fr, parent, uv_solid=P.pal("tin"))
    if label is not None:
        # printed label along the top (+Y) face, reading from the wires towards the pins
        lf = P.Frame(fr.p(0, H / 2 + 0.00003, L * 0.55), fr.v, fr.u)
        P.quad("dp_label", lf, L * 0.82, W * 0.82, LABELS_TAG, parent, uv=label_uv(LABELS.index(label)))
    if signs:
        # '+' / '-' moulded marks at the pin end on the top face
        for (x, y, k), s in zip(cells, signs):
            if s == "+":
                P.cube("dp_sign", (x, H / 2 + 0.00008, 0.0021), (0.0011, 0.00012, 0.0003), "connector_white", fr, parent)
                P.cube("dp_sign", (x, H / 2 + 0.00008, 0.0021), (0.0003, 0.00012, 0.0011), "connector_white", fr, parent)
            elif s == "-":
                P.cube("dp_sign", (x, H / 2 + 0.00008, 0.0021), (0.0011, 0.00012, 0.0003), "connector_white", fr, parent)
    pts = [(x, y) for (x, y, k) in cells if k != "X"]
    n = len(pts)
    if cable == "pair":
        # a twisted pair leaving the back
        r = 0.00062
        lines = []
        for idx, (x, y) in enumerate(pts):
            ph = idx * math.pi
            pts3 = []
            for k in range(13):
                z = L + k * 0.0022
                tw = math.cos(ph + k * 0.9) * min(1.0, k / 3) * (abs(x) * 0.9)
                tw2 = math.sin(ph + k * 0.9) * min(1.0, k / 3) * 0.0006
                pts3.append(fr.p(x * (1 - min(1.0, k / 3)) + tw, y + tw2, z))
            lines.append(pts3)
            P.tube("dp_wire", pts3, r, P.PALETTE_TAG, parent, 8, uv_solid=P.pal(colours[idx % len(colours)]))
        end = fr.p(0, 0, L + 12 * 0.0022)
        rad = 0.0013
    else:
        # a round jacketed cable (audio, USB)
        P.cube("dp_strain", (0, 0, L + 0.002), (W * 0.7, H * 0.8, 0.004), tag, fr, parent, bevel=0.0005)
        P.cylinder("dp_cable", fr.sub(0, 0, L + 0.004), 0.0022, 0.022, "rubber", 10, parent, z0=0.0)
        end = fr.p(0, 0, L + 0.026)
        rad = 0.0022
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, H + 0.002, L), end, rad, n, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=H, L=L, end=end)


def plug_fp_pwrsw(fr, parent, anchors_root=None):
    return dupont(fr, parent, anchors_root, 2, 1, "POWER SW", ["white", "red"])


def plug_fp_reset(fr, parent, anchors_root=None):
    return dupont(fr, parent, anchors_root, 2, 1, "RESET SW", ["white", "blue"])


def plug_fp_pled(fr, parent, anchors_root=None):
    return dupont(fr, parent, anchors_root, 2, 1, "POWER LED", ["green", "white"], signs="+-")


def plug_fp_hddled(fr, parent, anchors_root=None):
    return dupont(fr, parent, anchors_root, 2, 1, "H.D.D LED", ["orange", "white"], signs="+-")


def plug_audiohdr(fr, parent, anchors_root=None):
    """HD audio: 2x5 with pin 8 blocked (the key)."""
    return dupont(fr, parent, anchors_root, 5, 2, "HD AUDIO", None, blocked=(8,), cable="round")


def plug_usb3hdr(fr, parent, anchors_root=None):
    """USB 3.0 19-pin header plug: 2x10 at 2.0 mm with one pin blocked, a key rib, a blue housing and a fat cable."""
    p = 0.002
    W, H, L = 10 * p + 0.0028, 2 * p + 0.0046, 0.0125
    face_t = 0.0014
    blue = P.pal("usb_blue")
    cells = []
    for j in range(2):
        for i in range(10):
            k = "X" if (j == 1 and i == 9) else "S"
            cells.append(((i - 4.5) * p, (j - 0.5) * p - 0.0003, k))
    holes = [P.rrect(0.0010, 0.0010, 0.0001, x, y, 2) for (x, y, k) in cells if k != "X"]
    P.slab("u3_face", P.rrect(W, H, 0.0005), face_t, P.PALETTE_TAG, fr.sub(0, 0, face_t / 2), holes=holes, parent=parent,
           uv=None, uv_solid=blue)
    P.cube("u3_body", (0, 0, face_t + (L - face_t) / 2), (W, H, L - face_t), P.PALETTE_TAG, fr, parent, bevel=0.0005,
           uv_solid=blue)
    P.cube("u3_floor", (0, -0.0003, face_t + 0.0001), (W - 0.0012, 2 * p + 0.0004, 0.0003), "connector_black", fr, parent)
    for (x, y, k) in cells:
        if k != "X":
            P.cube("term", (x, y, face_t - 0.0003), (0.0005, 0.0005, 0.0004), P.PALETTE_TAG, fr, parent, uv_solid=P.pal("tin"))
    # the key rib on the +Y side and the pull tab
    P.cube("u3_key", (0, H / 2 + 0.0006, L * 0.5), (0.004, 0.0012, L * 0.9), P.PALETTE_TAG, fr, parent, uv_solid=blue)
    P.cube("u3_tab", (0, 0, L + 0.003), (W * 0.6, H * 0.6, 0.006), P.PALETTE_TAG, fr, parent, bevel=0.0008, uv_solid=blue)
    lf = P.Frame(fr.p(W * 0.27, H / 2 + 0.00003, L * 0.5), fr.v, fr.u)
    P.quad("u3_label", lf, L * 0.75, 0.003, LABELS_TAG, parent, uv=label_uv(LABELS.index("USB 3.0")))
    P.cylinder("u3_cable", fr.sub(0, 0, L + 0.006), 0.0032, 0.022, "rubber", 12, parent, z0=0.0)
    end = fr.p(0, 0, L + 0.028)
    hit_and_cable(fr, anchors_root, (0, 0, L / 2), (W + 0.002, H + 0.003, L), end, 0.0032, 1, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=W, H=H, L=L, end=end)


# ---------------------------------------------------------------- external plugs

def overmold(fr, parent, w, h, z0, length, r_cable, cable_len=0.03, tag="black_plastic", taper=0.7, name="om",
             segs=16):
    """An overmoulded plug body (rounded box) with a ribbed strain relief and a cable stub."""
    P.cube(name + "_body", (0, 0, z0 + length / 2), (w, h, length), tag, fr, parent, bevel=min(w, h) * 0.22, seg=3)
    # strain relief: stacked rings shrinking to the cable
    zr = z0 + length
    n = 5
    for k in range(n):
        t = k / (n - 1)
        rr = (min(w, h) * 0.42) * (1 - t) + r_cable * 1.25 * t
        P.cylinder(name + "_relief", fr.sub(0, 0, zr + k * 0.0026), rr, 0.0021, tag, segs, parent, z0=0.0, smooth=70)
        P.cylinder(name + "_relief", fr.sub(0, 0, zr + k * 0.0026 + 0.0021), rr * 0.85, 0.0005, tag, segs, parent, z0=0.0)
    zc = zr + n * 0.0026
    P.cylinder(name + "_cable", fr.sub(0, 0, zc), r_cable, cable_len, "rubber", 16, parent, z0=0.0, smooth=70)
    return fr.p(0, 0, zc + cable_len)


def plug_c13(fr, parent, anchors_root=None):
    """IEC C13 (the wall cable's PSU end): the keyed face with three sockets, a tapered body, a thick cable."""
    w, h = 0.0236, 0.0150
    ch = 0.0045
    outline = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - ch), (w / 2 - ch, h / 2), (-w / 2 + ch, h / 2), (-w / 2, h / 2 - ch)]
    holes = [P.rrect(0.0022, 0.0042, 0.0003, -0.007, -0.002), P.rrect(0.0022, 0.0042, 0.0003, 0.007, -0.002),
             P.rrect(0.0042, 0.0022, 0.0003, 0.0, 0.0045)]
    P.slab("c13_face", outline, 0.003, "black_plastic", fr.sub(0, 0, 0.0015), holes=holes, parent=parent)
    P.cube("c13_floor", (0, 0, 0.0028), (w - 0.002, h - 0.002, 0.0004), "black_plastic", fr, parent)
    for (x, y, ww, hh) in ((-0.007, -0.002, 0.0008, 0.0030), (0.007, -0.002, 0.0008, 0.0030), (0, 0.0045, 0.0030, 0.0008)):
        P.cube("c13_contact", (x, y, 0.0024), (ww, hh, 0.0008), "nickel", fr, parent)
    # the moulded body grows a little, then tapers into the strain relief
    body = [(-w / 2 - 0.0012, -h / 2 - 0.001), (w / 2 + 0.0012, -h / 2 - 0.001), (w / 2 + 0.0012, h / 2 - ch + 0.0004),
            (w / 2 - ch + 0.0004, h / 2 + 0.001), (-w / 2 + ch - 0.0004, h / 2 + 0.001), (-w / 2 - 0.0012, h / 2 - ch + 0.0004)]
    P.slab("c13_body", body, 0.020, "black_plastic", fr.sub(0, 0, 0.003 + 0.010), parent=parent)
    for k in range(6):
        P.cube("c13_grip", (0, -h / 2 - 0.0012, 0.008 + k * 0.0022), (w * 0.8, 0.0006, 0.0008), "black_plastic", fr, parent)
        P.cube("c13_grip", (0, h / 2 + 0.0012, 0.008 + k * 0.0022), (w * 0.5, 0.0006, 0.0008), "black_plastic", fr, parent)
    end = overmold(fr, parent, 0.016, 0.012, 0.023, 0.006, 0.0036, 0.03, name="c13_om")
    hit_and_cable(fr, anchors_root, (0, 0, 0.015), (w + 0.004, h + 0.004, 0.03), end, 0.0036, 1, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=w, H=h, L=0.03, end=end)


def shell_plug(fr, parent, outline, inner, depth, tongue=None, shell_tag="nickel", name="sh"):
    """A metal plug shell (outline) open at the front, with a dark insert inside."""
    P.slab(name + "_shell", outline, depth, shell_tag, fr.sub(0, 0, depth / 2), holes=[inner], parent=parent)
    P.slab(name + "_back", inner, 0.0006, "black_plastic", fr.sub(0, 0, depth - 0.0003), parent=parent)
    if tongue is not None:
        P.slab(name + "_tongue", tongue, depth - 0.0012, "black_plastic", fr.sub(0, 0, 0.0006 + (depth - 0.0012) / 2), parent=parent)


def plug_dp(fr, parent, anchors_root=None):
    """DisplayPort: the asymmetric shell (one corner cut), the contact tongue, and the overmould with the
    latch button on top and the two latch hooks."""
    w, h = 0.0161, 0.0048
    ch = 0.0018
    outer = [(-w / 2, -h / 2), (w / 2 - ch, -h / 2), (w / 2, -h / 2 + ch), (w / 2, h / 2), (-w / 2, h / 2)]
    t = 0.00035
    inner = [(-w / 2 + t, -h / 2 + t), (w / 2 - ch - t * 0.4, -h / 2 + t), (w / 2 - t, -h / 2 + ch + t * 0.4),
             (w / 2 - t, h / 2 - t), (-w / 2 + t, h / 2 - t)]
    tongue = P.rrect(0.0118, 0.0011, 0.0002, -0.0004, -0.0006)
    shell_plug(fr, parent, outer, inner, 0.0085, tongue, name="dp")
    for i in range(10):
        P.cube("dp_contact", (-0.0055 + i * 0.0011, 0.00006, 0.004), (0.0005, 0.0001, 0.006), "gold", fr, parent)
    # latch hooks poking through the top of the shell
    for sx in (-1, 1):
        P.cube("dp_hook", (sx * 0.005, h / 2 + 0.0002, 0.0025), (0.0016, 0.0006, 0.0024), "steel", fr, parent)
    end = overmold(fr, parent, 0.0215, 0.0098, 0.0085, 0.022, 0.0029, 0.03, name="dp_om")
    # the latch release button
    P.cube("dp_button", (0, 0.0049 + 0.0004, 0.0085 + 0.013), (0.0085, 0.0010, 0.0075), "dark_plastic", fr, parent, bevel=0.0004)
    for k in range(4):
        P.cube("dp_button_rib", (0, 0.0049 + 0.0010, 0.0085 + 0.010 + k * 0.0018), (0.007, 0.0003, 0.0004), "dark_plastic", fr, parent)
    hit_and_cable(fr, anchors_root, (0, 0, 0.018), (0.024, 0.012, 0.036), end, 0.0029, 1, fr.p(0, 0.0059, 0.0215),
                  parent_anchor=None if anchors_root else 1)
    return dict(W=w, H=h, L=0.0305, end=end)


def plug_hdmi(fr, parent, anchors_root=None):
    w, h = 0.0139, 0.0045
    ch = 0.0013
    outer = [(-w / 2 + ch, -h / 2), (w / 2 - ch, -h / 2), (w / 2, -h / 2 + ch), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2 + ch)]
    t = 0.00035
    inner = [(-w / 2 + ch + t * 0.4, -h / 2 + t), (w / 2 - ch - t * 0.4, -h / 2 + t), (w / 2 - t, -h / 2 + ch + t * 0.4),
             (w / 2 - t, h / 2 - t), (-w / 2 + t, h / 2 - t), (-w / 2 + t, -h / 2 + ch + t * 0.4)]
    tongue = P.rrect(0.0105, 0.0012, 0.0002, 0, -0.0004)
    shell_plug(fr, parent, outer, inner, 0.0095, tongue, name="hdmi")
    for i in range(10):
        P.cube("hdmi_contact", (-0.0045 + i * 0.001, 0.00025, 0.0045), (0.0004, 0.0001, 0.006), "gold", fr, parent)
    # the dimples that grip the receptacle
    for sx in (-1, 1):
        P.cube("hdmi_dimple", (sx * 0.004, h / 2 + 0.0001, 0.004), (0.0015, 0.0003, 0.002), "nickel", fr, parent)
    end = overmold(fr, parent, 0.0205, 0.0105, 0.0095, 0.02, 0.0031, 0.03, name="hdmi_om")
    hit_and_cable(fr, anchors_root, (0, 0, 0.017), (0.023, 0.013, 0.034), end, 0.0031, 1, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=w, H=h, L=0.0295, end=end)


def plug_eth(fr, parent, anchors_root=None):
    """RJ45: a clear body with eight gold contacts, the latch tab on top, a moulded boot."""
    w, h, L = 0.0117, 0.0080, 0.0215
    P.cube("rj_body", (0, 0, L / 2), (w, h - 0.0016, L), "glass", fr, parent, bevel=0.0004)
    P.cube("rj_body", (0, -0.0008, L * 0.62), (w, h, L * 0.76), "glass", fr, parent, bevel=0.0004)
    for i in range(8):
        P.cube("rj_contact", (-0.00357 + i * 0.00102, -h / 2 + 0.0018, 0.002), (0.0005, 0.0018, 0.0035), "gold", fr, parent)
    # coloured wires inside (568B order), visible through the clear body
    cols = ["orange", "white", "green", "blue", "white", "lightblue", "brown", "white"]
    for i, cn in enumerate(cols):
        P.cylinder("rj_core", P.Frame(fr.p(-0.00357 + i * 0.00102, -0.0012, 0.006), fr.w, fr.v), 0.00042, 0.012,
                   P.PALETTE_TAG, 6, parent, z0=0.0, uv_solid=P.pal(cn))
    # latch tab: a sprung tongue angled up from the front
    P.cube("rj_latch", (0, h / 2 + 0.0006, 0.010), (0.0055, 0.0008, 0.012), "glass", fr, parent)
    P.cube("rj_latch", (0, h / 2 + 0.0002, 0.0045), (0.0055, 0.0012, 0.0015), "glass", fr, parent)
    end = overmold(fr, parent, 0.0128, 0.0096, L, 0.010, 0.0029, 0.03, tag="grey_plastic", name="rj_boot")
    P.cube("rj_boot_guard", (0, h / 2 + 0.0012, L + 0.003), (0.008, 0.0016, 0.008), "grey_plastic", fr, parent, bevel=0.0005)
    hit_and_cable(fr, anchors_root, (0, 0, 0.016), (0.015, 0.012, 0.032), end, 0.0029, 1, fr.p(0, h / 2 + 0.001, 0.014),
                  parent_anchor=None if anchors_root else 1)
    return dict(W=w, H=h, L=L, end=end)


def usba_male(fr, parent, name="ua", tongue_col="usb_blue"):
    """A USB-A male end: steel shell 12 x 4.5 mm with the spring windows and the blue USB 3 tongue."""
    w, h, d = 0.0120, 0.0045, 0.0120
    t = 0.0003
    outer = P.rrect(w, h, 0.0004)
    inner = P.rrect(w - 2 * t, h - 2 * t, 0.0002)
    P.slab(name + "_shell", outer, d, "nickel", fr.sub(0, 0, d / 2), holes=[inner], parent=parent)
    P.cube(name + "_tongue", (0, -0.0009, d / 2 + 0.0004), (w - 0.0018, 0.0019, d - 0.0008), P.PALETTE_TAG, fr, parent,
           uv_solid=P.pal(tongue_col))
    for i in range(4):
        P.cube(name + "_contact", (-0.0035 + i * 0.0023, 0.0001, 0.0035), (0.001, 0.0001, 0.005), "gold", fr, parent)
    for sx in (-1, 1):
        P.cube(name + "_window", (sx * 0.003, h / 2 + 0.00002, 0.0045), (0.0018, 0.00005, 0.0018), "black_plastic", fr, parent)
        P.cube(name + "_window", (sx * 0.003, -h / 2 - 0.00002, 0.0045), (0.0018, 0.00005, 0.0018), "black_plastic", fr, parent)
    return d


def plug_usba(fr, parent, anchors_root=None):
    d = usba_male(fr, parent)
    end = overmold(fr, parent, 0.0160, 0.0080, d, 0.020, 0.0021, 0.03, name="ua_om")
    hit_and_cable(fr, anchors_root, (0, 0, 0.016), (0.018, 0.010, 0.032), end, 0.0021, 1, None,
                  parent_anchor=None if anchors_root else 1)
    return dict(W=0.012, H=0.0045, L=0.032, end=end)


PLUGS = {
    "atx24": plug_atx24, "eps8": plug_eps8, "pcie8": plug_pcie8, "p12v2x6": plug_p12v2x6,
    "sata_data": plug_sata_data, "sata_power": plug_sata_power, "fan4": plug_fan4, "fan3": plug_fan3,
    "fp_pwrsw": plug_fp_pwrsw, "fp_reset": plug_fp_reset, "fp_pled": plug_fp_pled, "fp_hddled": plug_fp_hddled,
    "usb3hdr": plug_usb3hdr, "audiohdr": plug_audiohdr, "c13": plug_c13, "dp": plug_dp, "hdmi": plug_hdmi,
    "eth": plug_eth, "usba": plug_usba, "mod_atx": plug_mod_atx, "mod_cpu": plug_mod_cpu, "mod_pcie": plug_mod_pcie,
    "mod_12v2x6": plug_mod_12v2x6, "mod_sata": plug_mod_sata,
}


# ---------------------------------------------------------------- screws, standoff, USB stick

def cross(w, a):
    """A Phillips cross outline: arms of width w reaching a from the centre."""
    h = w / 2
    return [(a, h), (h, h), (h, a), (-h, a), (-h, h), (-a, h), (-a, -h), (-h, -h), (-h, -a), (h, -a), (h, -h), (a, -h)]


def screw(fr, parent, kind="ph2", tag="steel", name="screw"):
    """A screw in frame fr: head above z=0 (the seating plane), thread below. The Phillips recess is cut into
    the head (real geometry, same material)."""
    if kind == "ph2":      # #6-32 x 1/4" pan head with a washer face (motherboard / case screw)
        rh, hh, rt, lt, pitch = 0.0033, 0.0024, 0.00176, 0.0060, 0.000794
        rc, rec, w, a = 0.0019, 0.0012, 0.0009, 0.0016
        prof = [(0, 0), (rh, 0), (rh, 0.0005), (rh * 0.97, 0.0011), (rh * 0.86, hh * 0.82), (rc, hh), (rc, hh - rec), (0, hh - rec)]
    elif kind == "ph0":    # M2 x 3 wafer head (M.2 screw)
        rh, hh, rt, lt, pitch = 0.0019, 0.0010, 0.001, 0.0030, 0.0004
        rc, rec, w, a = 0.0013, 0.0006, 0.00055, 0.00105
        prof = [(0, 0), (rh, 0), (rh, 0.0004), (rc, hh), (rc, hh - rec), (0, hh - rec)]
    else:
        raise ValueError(kind)
    P.lathe(name + "_head", prof, tag, fr, 28, parent, smooth=40)
    P.slab(name + "_recess", P.circle(rc, 0, 0, 28), rec, tag, fr.sub(0, 0, hh - rec / 2), holes=[cross(w, a)], parent=parent)
    # thread: a stack of V ridges
    tp = [(0, -lt), (rt * 0.75, -lt)]
    z = -lt + pitch * 0.5
    while z < -pitch * 0.25:
        tp += [(rt, z - pitch * 0.25), (rt * 0.82, z + pitch * 0.25)]
        z += pitch
    tp += [(rt * 0.82, 0.0), (0, 0.0)]
    P.lathe(name + "_thread", tp, tag, fr, 14, parent, smooth=60)
    return hh


def thumbscrew(fr, parent, tag="steel_dark", name="thumb", washer=None):
    """A knurled case thumbscrew (#6-32): flanged knurled head, a shoulder, the thread."""
    rh, hh = 0.0055, 0.0068
    knurl = []
    n = 30
    for k in range(n * 2):
        a = math.pi * k / n
        r = rh if k % 2 == 0 else rh - 0.00045
        knurl.append((r * math.cos(a), r * math.sin(a)))
    P.slab(name + "_knurl", knurl, hh - 0.0018, tag, fr.sub(0, 0, 0.0012 + (hh - 0.0018) / 2), parent=parent, smooth=None)
    P.lathe(name + "_flange", [(0, 0), (rh + 0.0006, 0), (rh + 0.0006, 0.0010), (rh - 0.0004, 0.0012), (0, 0.0012)], tag, fr, 32, parent)
    P.lathe(name + "_top", [(0, hh - 0.0007), (rh - 0.0002, hh - 0.0007), (rh - 0.0007, hh), (0, hh)], tag, fr, 32, parent)
    if washer:
        P.lathe(name + "_washer", [(0.0019, -0.0008), (0.0048, -0.0008), (0.0048, 0.0), (0.0019, 0.0)], washer, fr, 24, parent)
    tp = [(0, -0.0065), (0.0013, -0.0065)]
    z = -0.0062
    while z < -0.0024:
        tp += [(0.00176, z), (0.00145, z + 0.0004)]
        z += 0.000794
    tp += [(0.0016, -0.0022), (0.0022, -0.0022), (0.0022, 0.0), (0, 0.0)]
    P.lathe(name + "_thread", tp, tag, fr, 14, parent, smooth=60)
    return hh


def standoff(fr, parent, tag="gold", name="standoff", height=0.00635):
    """A #6-32 brass hex standoff: 5 mm hex body, the threaded stud below, the threaded hole on top."""
    hexo = P.hexagon(0.0029, 0, 0, 0)
    hole = P.circle(0.0014, 0, 0, 12)
    P.slab(name + "_hex", hexo, height - 0.0003, tag, fr.sub(0, 0, (height - 0.0003) / 2), holes=[hole], parent=parent)
    P.lathe(name + "_chamfer", [(0.0014, height - 0.0003), (0.0025, height - 0.0003), (0.0023, height), (0.0014, height)], tag, fr, 6,
            parent, rot=0.0)
    tp = [(0, -0.0045), (0.0013, -0.0045)]
    z = -0.0042
    while z < -0.0004:
        tp += [(0.00172, z), (0.0014, z + 0.0004)]
        z += 0.000794
    tp += [(0.0015, 0.0), (0, 0.0)]
    P.lathe(name + "_stud", tp, tag, fr, 12, parent, smooth=60)


def usb_stick(fr, parent):
    d = usba_male(fr, parent, "stick", tongue_col="usb_blue")
    L = 0.042
    w, h = 0.0185, 0.0082
    z0 = d - 0.001
    # body: black plastic shell with a rounded back and a lanyard loop
    body = P.rrect(w, L, 0.004, 0, 0)
    P.slab("stick_body", body, h, "black_plastic", P.Frame(fr.p(0, 0, z0 + L / 2), fr.v, fr.w), parent=parent)
    # the neck where the shell enters the body
    P.cube("stick_neck", (0, 0, z0 - 0.0004), (0.0135, 0.0056, 0.0018), "black_plastic", fr, parent, bevel=0.0004)
    # lanyard hole at the back
    P.slab("stick_loop", P.rrect(0.0105, 0.006, 0.0025), 0.0034, "black_plastic",
           P.Frame(fr.p(0, 0, z0 + L + 0.0012), fr.v, fr.w), holes=[P.rrect(0.0065, 0.0028, 0.0013)], parent=parent)
    # the printed label on top and the activity LED
    lf = P.Frame(fr.p(0, h / 2 + 0.00004, z0 + L * 0.52), fr.v, fr.u * -1)
    P.quad("stick_label", lf, L * 0.78, w * 0.8, "tex_" + STICK_FILE, parent, flip_u=True)
    P.cylinder("stick_led", P.Frame(fr.p(0.0062, h / 2 - 0.0002, z0 + 0.0035), fr.v, fr.w), 0.0008, 0.0006, "led_blue", 12, parent, z0=0.0)
    return z0 + L + 0.004


# ---------------------------------------------------------------- export

def build_one(kind):
    P.reset()
    root = c.root(kind)
    fr = P.F((0, 0, 0))
    info = ""
    if kind.startswith("plug_"):
        k = kind[5:]
        r = PLUGS[k](fr, root, anchors_root=root)
        info = f"W={r['W']:.4f} H={r['H']:.4f} L={r['L']:.4f}"
    elif kind in ("screw_ph2", "screw_ph0"):
        hh = screw(fr, root, kind[6:], "steel")
        rh = 0.0033 if kind == "screw_ph2" else 0.0019
        P.anchor("A_HIT_0", P.F((0, 0, hh / 2)), (rh * 2.4, rh * 2.4, hh + 0.002), root)
    elif kind == "screw_thumb":
        hh = thumbscrew(fr, root)
        P.anchor("A_HIT_0", P.F((0, 0, hh / 2)), (0.013, 0.013, hh + 0.002), root)
    elif kind == "standoff_brass":
        standoff(fr, root)
        P.anchor("A_HIT_0", P.F((0, 0, 0.003)), (0.007, 0.007, 0.007), root)
        P.anchor("A_SCREW_PH2_0", P.F((0, 0, 0.00635)), (0.007, 0.007, 0.004), root, meta="thread=6-32")
    elif kind == "usb_stick":
        zl = usb_stick(fr, root)
        P.anchor("A_HIT_0", P.F((0, 0, zl / 2)), (0.02, 0.01, zl), root)
        P.anchor("A_LED_ACT_0", P.F((0.0062, 0.0041, 0.0145), (0, 1, 0), (0, 0, 1)), (0.002, 0.002, 0.002), root)
    P.finalize(root, kind)
    c.export(root, kind)
    tris, meshes = P.write_report(root, kind, info)
    P.preview(root, kind, views=((30, 25), (150, 35)), size=(800, 600))
    P.beauty(root, kind, views=((32, 22), (155, 30)), size=(1000, 750), samples=64)
    return tris, meshes


ALL = [f"plug_{k}" for k in PLUGS] + ["screw_ph2", "screw_ph0", "screw_thumb", "standoff_brass", "usb_stick"]


def main(kinds=None):
    P.reset()
    P.write_palette()
    write_label_textures()
    out = {}
    for k in (kinds or ALL):
        out[k] = build_one(k)
    for k, v in out.items():
        print("BUILT", k, v)
    return out


if __name__ == "__main__":
    a = c.args()
    main(a if a else None)
