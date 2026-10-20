r"""
build_cat_cases.py - catalogue 17: cases and fans (7 mid-tower cases, 7 case-fan products).

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_cat_cases.py -- [ids...] [--nopreview]

Cases (build_case.py with new styles; case_breeze's frame and anchors, see docs/reports/cat_cases.md):
  case_lumin_216           Lumin Airwave 216 RGB: black, fine-mesh front, two 160 mm ARGB intake fans
  case_phanta_g360a        Phanta Umbra G360A: black, mesh front, three 120 mm ARGB intake fans, ARGB front strip
  case_nexa_h5             Nexa H5 Draft: white, perforated front, two 120 mm intake fans
  case_facet_fjord         Facet Fjord: charcoal, walnut slats over a mesh front, two 140 mm fans, no RGB
  case_hush_500dx          Hush Calm Base 500DX: black, mesh front with an ARGB light strip, two 140 mm fans
  case_facet_fizzair       Facet Fizz Air: budget, white, hex-mesh front with teal accents, three 120 mm fans
  case_brickhouse_beige98  Brickhouse Beige 98: a retro beige throwback, fake 5.25" CD drive, floppy bay, turbo
                           button and a "66" MHz display
Fans (a new contract, case_fan: origin at the frame centre, +Z = the airflow direction, the intake face at -Z):
  fan_arctiq_p12, fan_arctiq_p14, fan_noctis_a12x25, fan_noctis_a12x25_black, fan_lumin_sl120_white,
  fan_corvex_af120_rgb, fan_hush_wing4_140

With no ids it builds all of them. build_case.py's optional hooks (front_fans, front_wall, face, feet, extra) carry
the looks; every case anchor except the front fans is where case_breeze has it. parts_fan.make_fan is wrapped, not
edited: the extra details (corner pads, side light bars, the interlocking link connectors, the hub light ring) are
added here.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import parts_fan as PF  # noqa: E402
import build_plugs as BP  # noqa: E402
import build_case as BC  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ
SAMPLES = 40          # Cycles samples for the beauty previews (build_case asks for 96)
CUR = {}              # the style being built (for the mesh texture patch)

# ---------------------------------------------------------------- own palette (solid colours through one PNG)
PAL_FILE = "cat_cases_palette"
PAL_TAG = "tex_" + PAL_FILE
_PAL = [("teal", (0.0, 0.62, 0.64)), ("noc_brown", (0.36, 0.22, 0.16)), ("noc_beige", (0.84, 0.76, 0.62)),
        ("orange", (0.95, 0.45, 0.08)), ("charcoal", (0.12, 0.12, 0.13)), ("walnut", (0.30, 0.18, 0.10)),
        ("beige_dark", (0.70, 0.65, 0.52)), ("gold_print", (0.80, 0.66, 0.30))]


def pal(name):
    i = [n for n, _ in _PAL].index(name)
    return ((i % 4 + 0.5) / 4, 1.0 - (i // 4 + 0.5) / 2)


def write_palette():
    import numpy as np
    s = 32
    arr = np.zeros((2 * s, 4 * s, 4), dtype=np.float32)
    arr[..., 3] = 1
    for i, (_, col) in enumerate(_PAL):
        cx, row = i % 4, i // 4
        y0 = 2 * s - (row + 1) * s
        arr[y0:y0 + s, cx * s:(cx + 1) * s, 0:3] = col
    P.save_png(arr, PAL_FILE)


def fix_normals(root, only=None):
    """Recalculates outward normals on every closed (manifold) mesh under root, in Blender space. parts_c.slab on
    some planes (e.g. plane(o, Z, Y), the front face) returns inside-out solids, which Unity's back-face culling
    would show as holes; open meshes (quads, decals) are left as they are. only: the object names to look at."""
    import bmesh
    n = 0
    for o in c.descendants(root):
        if o.type != "MESH" or (only is not None and o.name not in only):
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        if bm.edges and all(len(e.link_faces) == 2 for e in bm.edges):
            before = [f.normal.copy() for f in bm.faces]
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.normal_update()
            if any(f.normal.dot(v) < 0 for f, v in zip(bm.faces, before)):
                bm.to_mesh(o.data)
                n += 1
        bm.free()
    print(f"fix_normals: {n} meshes turned outward")


def set_uv_solid(ob, uv):
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new()
    for d in me.uv_layers.active.data:
        d.uv = uv


# ---------------------------------------------------------------- textures

def mesh_tex(file, web=(0.86, 0.86, 0.84), shape="hex", pitch=0.0042, r=0.00175, w=1024, h=2048, panel=(0.176, 0.372),
             solid=None, border=0.0025):
    """A front mesh / perforated panel at real scale: holes alpha 0 (dark), the web in `web` with a soft bevel.
    shape hex | round; solid(X, Y) -> a mask of areas left solid (metres from the bottom-left corner)."""
    import numpy as np
    pw, ph = panel
    ppm = w / pw
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X_ = (xx + 0.5) / ppm
    Y_ = (yy + 0.5) / (h / ph)
    dy = pitch * math.sqrt(3) / 2
    row = np.floor(Y_ / dy + 0.5)
    best = np.full(X_.shape, 1e9, dtype=np.float32)
    for drow in (-1, 0, 1):
        r2 = row + drow
        cy2 = r2 * dy
        off2 = (r2 % 2) * pitch / 2
        cx2 = np.floor((X_ - off2) / pitch + 0.5) * pitch + off2
        ddx, ddy = np.abs(X_ - cx2), np.abs(Y_ - cy2)
        if shape == "round":
            d = np.sqrt(ddx * ddx + ddy * ddy)
        else:
            d = np.maximum(ddy, ddy * 0.5 + ddx * math.sqrt(3) / 2)
        best = np.minimum(best, d)
    hole = best < r
    edge = np.clip((best - r) / 0.00025, 0, 1)
    if solid is not None:
        hole = hole & ~solid(X_, Y_)
        edge = np.where(solid(X_, Y_), 1.0, edge)
    b = int(border * ppm)
    hole[:b, :] = hole[-b:, :] = False
    hole[:, :b] = hole[:, -b:] = False
    arr = np.zeros((h, w, 4), dtype=np.float32)
    shade = 0.82 + 0.18 * edge
    for k in range(3):
        arr[..., k] = np.where(hole, 0.05, web[k] * shade)
    arr[..., 3] = np.where(hole, 0.0, 1.0)
    return P.save_png(arr, file)


def wood_tex(file, w=256, h=1024):
    """Walnut: dark brown with long wavy grain lines and a few darker streaks (the grain runs along v)."""
    import numpy as np
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h
    warp = 0.03 * np.sin(v * 9.0 + 1.3) + 0.012 * np.sin(v * 31.0 + u * 4.0)
    g = u + warp
    lines = 0.5 + 0.5 * np.sin(g * 2 * math.pi * 23.0 + 2.0 * np.sin(g * 17.0))
    fine = 0.5 + 0.5 * np.sin(g * 2 * math.pi * 97.0 + v * 3.0)
    streak = np.exp(-((g % 0.37 - 0.18) / 0.03) ** 2)
    base = np.array([0.36, 0.22, 0.13])
    dark = np.array([0.20, 0.11, 0.06])
    t = np.clip(0.55 * lines ** 3 + 0.2 * fine + 0.45 * streak, 0, 1)[..., None]
    rgb = base * (1 - t) + dark * t
    arr = np.ones((h, w, 4), dtype=np.float32)
    arr[..., :3] = rgb
    return P.save_png(arr, file)


_orig_mesh_texture = BC.mesh_texture


def _mesh_texture(file, *a, **k):
    m = CUR.get("mesh")
    if not m:
        return _orig_mesh_texture(file, *a, **k)
    return mesh_tex(file, **m)


BC.mesh_texture = _mesh_texture
_orig_beauty = P.beauty


def _beauty(*a, **k):
    k["samples"] = min(k.get("samples", SAMPLES), SAMPLES)
    return _orig_beauty(*a, **k)


P.beauty = _beauty


# ---------------------------------------------------------------- case hooks (ns = build_case.build()'s locals)

def front_wall_fans(ns, fh):
    """The mesh front wall cut out for the style's front fans (instead of the three 120 mm fans)."""
    fans = ns.st["front_fans"]
    zmax = max(d for _, d in fans) / 2 - 0.002
    y0 = min(y - d / 2 for y, d in fans) + 0.004
    y1 = max(y + d / 2 for y, d in fans) - 0.004
    new = [BC.rr(-zmax, zmax, max(0.05, y0), min(0.41, y1), 0.010)]
    for y, d in fans:
        q = PF.HOLE_SPACING.get(round(d, 3), d * 0.875) / 2
        new += [P.circle(0.0022, sz * q, y + sy * q, 12) for sz in (-1, 1) for sy in (-1, 1)]
    return new + fh[-7:]       # keep the front I/O cable hole and the six bezel clips


def mesh_insert(ns, x_off=0.0016, back=True):
    """The front mesh insert (the style's mesh texture) behind the face opening, as on case_breeze."""
    tag = "tex_" + ns.cid + "_mesh"
    P.quad("front_mesh", P.Frame((ns.xface + x_off, 0.2145, 0.0), NX, Y), 0.180, 0.376, tag, ns.root, uv=(0, 0, 1, 1))
    if back:
        P.quad("front_mesh_back", P.Frame((ns.xface + x_off + 0.0002, 0.2145, 0.0), X, Y), 0.180, 0.376, tag, ns.root)


def face_logo(ns, text, size=0.0105, tag=None, y=0.0145, font=None, width=0.06, spacing=1.15, z=0.0):
    P.text3d("bezel_logo", text, size, 0.0003, tag or ns.st["logo_tag"], P.Frame((ns.xface, y, z), NX, Y),
             font or ns.st["logo_font"], parent=ns.root, width=width, spacing=spacing)


def front_plate(name, tag, ns, z0, z1, y0, y1, d=0.0010, r=0.001, holes=(), out=0.0, **kw):
    """A plate on the front face (world z0..z1, y0..y1), d thick, standing `out` proud of the face."""
    P.slab(name, BC.rr(z0, z1, y0, y1, r), d, tag, P.plane((ns.xface - out + d / 2 - d, 0, 0), Z, Y), holes=holes,
           parent=ns.root, **kw)


def feet_rails(ns, tag="black_plastic"):
    """Two long rail feet (Lancool / H5 style), rubber strips under them; bottoms 8 mm below the origin."""
    for z in (-0.08, 0.08):
        P.slab("foot", P.rrect(0.385, 0.020, 0.008, 0.0, 0.0), 0.0055, tag, P.plane((-0.008, -0.00275, z), X, Z),
               parent=ns.root)
        for x in (-0.17, 0.155):
            P.slab("foot_pad", P.rrect(0.040, 0.016, 0.005), 0.0025, "rubber", P.plane((x, -0.00675, z), X, Z),
                   parent=ns.root)


def feet_round(ns, tag="alu_dark"):
    """Round turned feet with rubber soles (Fjord)."""
    for x in (-0.175, 0.16):
        for z in (-0.075, 0.075):
            P.cylinder("foot", P.Frame((x, -0.00275, z), NY, X), 0.013, 0.0055, tag, 32, ns.root, r2=0.0115, smooth=40)
            P.cylinder("foot_pad", P.Frame((x, -0.00675, z), NY, X), 0.011, 0.0025, "rubber", 32, ns.root, smooth=40)


def feet_square(ns, tag="connector_beige"):
    """Chunky square feet with rubber soles (the retro case)."""
    for x in (-0.18, 0.165):
        for z in (-0.082, 0.082):
            P.cube("foot", (x, -0.00275, z), (0.030, 0.0055, 0.030), tag, parent=ns.root, bevel=0.0012)
            P.cube("foot_pad", (x, -0.00675, z), (0.026, 0.0025, 0.026), "rubber", parent=ns.root, bevel=0.0006)


# ---- per-case faces

def face_lumin(ns):
    mesh_insert(ns)
    # the solid lower band carries the logo; two thin grooves frame the mesh at the sides
    face_logo(ns, "LUMIN", 0.0085, "grey_plastic", y=0.0135, font="arialbd.ttf", width=0.045, spacing=1.4)
    for z in (-0.096, 0.096):
        front_plate("bezel_groove", "black_plastic", ns, z - 0.0006, z + 0.0006, 0.03, 0.40, d=0.0004, out=0.00005)


def face_phanta(ns):
    mesh_insert(ns)
    face_logo(ns, "PHANTA", 0.0080, "alu", y=0.0140, font="arialbd.ttf", width=0.05, spacing=1.5)
    # ARGB light strip down the front's left edge (seen from the front), in a black channel
    front_plate("argb_channel", "black_plastic", ns, 0.0915, 0.0985, 0.03, 0.40, d=0.0012, out=0.0006)
    P.cube("front_argb", (ns.xface - 0.0007, 0.215, 0.0950), (0.0010, 0.366, 0.0034), "rgb", parent=ns.root)


def face_nexa(ns):
    mesh_insert(ns)
    face_logo(ns, "NEXA", 0.0070, "grey_plastic", y=0.0140, font="arialbd.ttf", width=0.03, spacing=1.6)


def face_fjord(ns):
    """Walnut slats over a black mesh: 12 vertical slats in the face opening, the mesh set back behind them."""
    mesh_insert(ns, x_off=0.0068)
    n, sw, gap = 12, 0.0112, 0.0036
    span = n * sw + (n - 1) * gap
    for k in range(n):
        z = -span / 2 + sw / 2 + k * (sw + gap)
        u0 = (k * 0.137) % 0.62
        P.slab("wood_slat", BC.rr(z - sw / 2, z + sw / 2, 0.0300, 0.3990, 0.0016), 0.0060, "tex_" + ns.cid + "_wood",
               P.plane((ns.xface + 0.0030, 0, 0), Z, Y), parent=ns.root, uv=(u0, 0.0, u0 + 0.36, 1.0))
    # cross battens behind the slats (they hold them)
    for y in (0.07, 0.36):
        P.cube("slat_batten", (ns.xface + 0.0066, y, 0.0), (0.0012, 0.012, 0.176), "black_plastic", parent=ns.root)
    face_logo(ns, "FACET", 0.0060, "alu", y=0.0140, font="arialbd.ttf", width=0.03, spacing=1.8)


def face_hush(ns):
    mesh_insert(ns)
    # solid side covers leave a centre mesh band; an ARGB strip runs down the left cover's inner edge
    for z0, z1 in ((-0.0885, -0.050), (0.050, 0.0885)):
        front_plate("front_cover", ns.st["bezel"], ns, z0, z1, 0.028, 0.401, d=0.0020, out=0.0, r=0.0008)
    P.cube("front_argb", (ns.xface + 0.0004, 0.2145, 0.0490), (0.0016, 0.372, 0.0024), "rgb", parent=ns.root)
    P.cube("front_argb_diffuser", (ns.xface + 0.0004, 0.2145, -0.0490), (0.0016, 0.372, 0.0012), "dark_plastic",
           parent=ns.root)
    face_logo(ns, "hush", 0.0110, "alu", y=0.0135, font="seguisb.ttf", width=0.04, spacing=1.1)


def face_fizz(ns):
    mesh_insert(ns)
    # teal accent bars down both outer edges of the face and a teal logo
    for z in (-0.0985, 0.0985):
        P.slab("accent", BC.rr(z - 0.0028, z + 0.0028, 0.028, 0.401, 0.0012), 0.0012, PAL_TAG,
               P.plane((ns.xface - 0.0004, 0, 0), Z, Y), parent=ns.root, uv_solid=pal("teal"))
    o = P.text3d("bezel_logo", "FACET", 0.0068, 0.0003, PAL_TAG, P.Frame((ns.xface, 0.0140, 0.0), NX, Y), "arialbd.ttf",
                 parent=ns.root, width=0.034, spacing=1.8)
    set_uv_solid(o, pal("teal"))


def face_beige(ns):
    """The 1998 front: a fake 5.25" CD drive, a 3.5" floppy bay, the turbo panel (TURBO button, LEDs and the
    two-digit MHz display), a key lock, vent grooves and the badge."""
    root, xf = ns.root, ns.xface
    bez = ns.st["bezel"]
    # 5.25" bay: a CD-ROM face 146 x 41.5 mm, standing 1.2 mm proud
    yb = 0.386
    front_plate("cd_face", "connector_beige", ns, -0.073, 0.073, yb - 0.0205, yb + 0.0205, d=0.0012, out=0.0012, r=0.0008)
    front_plate("cd_tray", PAL_TAG, ns, -0.064, 0.050, yb - 0.0035, yb + 0.0110, d=0.0006, out=0.0021, r=0.0006,
                uv_solid=pal("beige_dark"))
    front_plate("cd_line", "black_plastic", ns, -0.064, 0.050, yb - 0.0040, yb - 0.0035, d=0.0002, out=0.0019, r=0.0001)
    P.cube("cd_eject", (xf - 0.0022, yb - 0.0115, -0.058), (0.0016, 0.0042, 0.012), "connector_beige", parent=root, bevel=0.0005)
    P.cylinder("cd_led", P.Frame((xf - 0.0012, yb - 0.0115, -0.040), NX, Y), 0.0011, 0.0010, "led_green", 12, root, z0=0)
    P.cylinder("cd_jack", P.Frame((xf - 0.0012, yb - 0.0115, 0.060), NX, Y), 0.0022, 0.0010, "black_plastic", 16, root, z0=0)
    P.cylinder("cd_volume", P.Frame((xf - 0.0012, yb - 0.0115, 0.047), NX, Y), 0.0030, 0.0018, "grey_plastic", 20, root, z0=0)
    P.text3d("cd_print", "CD-ROM  52X", 0.0030, 0.00008, "dark_plastic", P.Frame((xf - 0.00272, yb + 0.0040, 0.012), NX, Y),
             "arialbd.ttf", parent=root, width=0.03)
    P.text3d("cd_print", "COMPACT DISC", 0.0020, 0.00008, "dark_plastic", P.Frame((xf - 0.0013, yb - 0.0120, 0.010), NX, Y),
             "arialbd.ttf", parent=root, width=0.022)
    # 3.5" floppy bay: 102 x 25.4 mm
    yf = 0.336
    front_plate("fdd_face", "connector_beige", ns, -0.051, 0.051, yf - 0.0127, yf + 0.0127, d=0.0012, out=0.0012, r=0.0008)
    front_plate("fdd_slot", "black_plastic", ns, -0.046, 0.034, yf + 0.0010, yf + 0.0040, d=0.0003, out=0.00125)
    front_plate("fdd_flap", "connector_beige", ns, -0.046, 0.034, yf + 0.0010, yf + 0.0040, d=0.0004, out=0.0016)
    P.cube("fdd_button", (xf - 0.0018, yf - 0.0060, 0.040), (0.0014, 0.0050, 0.010), "connector_beige", parent=root, bevel=0.0004)
    P.cylinder("fdd_led", P.Frame((xf - 0.0012, yf - 0.0060, -0.040), NX, Y), 0.0010, 0.0008, "led_green", 12, root, z0=0)
    # turbo panel: a recessed dark plate with the display, the TURBO button and its LED, power/HDD legends
    yt = 0.285
    front_plate("turbo_panel", "dark_plastic", ns, -0.050, 0.050, yt - 0.016, yt + 0.016, d=0.0008, out=0.0003, r=0.002)
    front_plate("mhz_window", "black_plastic", ns, -0.044, -0.014, yt - 0.010, yt + 0.010, d=0.0004, out=0.0007, r=0.001)
    seven_seg("66", ns, -0.0290, yt, root)
    P.text3d("mhz_print", "MHz", 0.0034, 0.00008, "grey_plastic", P.Frame((xf - 0.0007, yt - 0.0128, -0.0290), NX, Y),
             "arialbd.ttf", parent=root, width=0.012)
    ta = P.anchor("A_BUTTON_TURBO_0", P.Frame((xf - 0.0003, yt + 0.002, 0.012), NX, Y), (0.016, 0.010, 0.008), root,
                  meta="press=+z_local,travel=0.0015,toggle=1,fun=1")
    P.cube("turbo_cap", (0, 0, 0.0010), (0.0150, 0.0085, 0.0034), "connector_beige", P.anchor_frame(ta), ta, bevel=0.0007)
    P.text3d("turbo_print", "TURBO", 0.0026, 0.00008, "dark_plastic", P.anchor_frame(ta).sub(0, -0.0002, 0.00272),
             "arialbd.ttf", parent=ta, width=0.011)
    la = P.anchor("A_LED_TURBO_0", P.Frame((xf - 0.0003, yt + 0.002, 0.030), NX, Y), (0.004, 0.004, 0.003), root,
                  meta="colour=yellow,on_when=A_BUTTON_TURBO_0")
    P.lathe("turbo_led", [(0, 0.0010), (0.0015, 0.0008), (0.0016, -0.001), (0, -0.001)], "led_yellow", P.anchor_frame(la), 16, la)
    P.text3d("turbo_print", "TURBO", 0.0020, 0.00008, "grey_plastic", P.Frame((xf - 0.0007, yt - 0.0090, 0.030), NX, Y),
             "arialbd.ttf", parent=root, width=0.009)
    # key lock
    kf = P.Frame((xf, yt, 0.042), NX, Y)
    P.lathe("keylock", [(0.0, 0.0016), (0.0040, 0.0016), (0.0045, 0.0008), (0.0045, -0.001), (0.0, -0.001)], "nickel", kf, 32, root)
    P.cube("key_slot", (0, 0, 0.00165), (0.0007, 0.0042, 0.0002), "black_plastic", kf, root)
    # vent grooves across the lower front, the badge and a sticker
    for k in range(18):
        y = 0.040 + 0.0105 * k
        front_plate("vent_groove", PAL_TAG, ns, -0.070, 0.070, y, y + 0.0035, d=0.0003, out=-0.0001,
                    uv_solid=pal("beige_dark"))
    front_plate("badge", "alu", ns, -0.052, 0.052, 0.0105, 0.0285, d=0.0008, out=0.0008, r=0.002)
    P.text3d("bezel_logo", "BRICKHOUSE 98", 0.0060, 0.00012, "black_plastic", P.Frame((xf - 0.0008, 0.0195, 0.0), NX, Y),
             "ariblk.ttf", parent=root, width=0.095)
    P.slab("sticker", P.rrect(0.022, 0.016, 0.002), 0.0001, PAL_TAG, P.plane((xf - 0.00006, 0, 0), Z, Y), parent=root,
           uv_solid=pal("gold_print"))
    del bez


SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def seven_seg(txt, ns, z_centre, y_centre, root, h=0.014, w=0.0075, t=0.0013):
    """A two-digit red seven-segment display on the front face (led_red, lit by the game with the power LED)."""
    xf = ns.xface - 0.0008
    for i, ch in enumerate(txt):
        zc = z_centre + (i - (len(txt) - 1) / 2) * (w + 0.0045)   # left to right as seen from the front (-z first)
        zc = -zc + 2 * z_centre                                     # seen from the front, +z is on the left
        segs = {"a": (0, h / 2, w, t), "g": (0, 0, w, t), "d": (0, -h / 2, w, t), "f": (-w / 2, h / 4, t, h / 2),
                "b": (w / 2, h / 4, t, h / 2), "e": (-w / 2, -h / 4, t, h / 2), "c": (w / 2, -h / 4, t, h / 2)}
        for s in SEG[ch]:
            dz, dy, sz, sy = segs[s]
            P.cube("mhz_seg", (xf - 0.0001, y_centre + dy, zc - dz), (0.0003, sy - 0.0003, sz - 0.0003), "led_red", parent=root)


# ---- extras (shroud details, top accents)

def extra_lumin(ns):
    # a perforated plate on the shroud's front end and a light bar along the shroud's top edge
    P.cube("shroud_argb", (0.012, ns.YS - 0.0016, ns.ZS + 0.0007), (0.36, 0.0018, 0.0010), "rgb", parent=ns.root)


def extra_phanta(ns):
    P.cube("shroud_argb", (0.012, ns.YS - 0.0016, ns.ZS + 0.0007), (0.36, 0.0018, 0.0010), "rgb", parent=ns.root)


def extra_fizz(ns):
    # teal: the shroud logo plate and the 2.5" sled's pull tab
    P.slab("shroud_accent", P.rrect(0.15, 0.004, 0.0015, -0.065, 0.034), 0.0006, PAL_TAG,
           P.plane((0, 0, ns.ZS + 0.0007), X, Y), parent=ns.root, uv_solid=pal("teal"))


def extra_beige(ns):
    # a grey "1998" style service label on the shroud and beige plastic grommet-less look is kept; nothing else
    P.slab("shroud_label", P.rrect(0.05, 0.022, 0.001, 0.13, 0.050), 0.0001, "white_plastic",
           P.plane((0, 0, ns.ZS + 0.00045), X, Y), parent=ns.root)


# ---- unboxing films (anchors only)

def hub_film(fa, d, th=0.025, hub_ratio=0.172, n=0):
    """A_FILM_HUB_<n>: the clear film disc on a fan's hub sticker, in the A_FAN_<n> frame (it spins with the rotor).
    parts_fan puts the sticker at about +h - 1.4 mm on the anchor's +Z (intake) side, radius 0.82 x the hub."""
    r = d * hub_ratio * 0.82
    P.anchor(f"A_FILM_HUB_{n}", P.anchor_frame(fa).sub(0, 0, th / 2 - 0.0012), (2 * r, 2 * r, 0.0001), fa,
             meta="peel=+x,tab=+x,shape=disc")


def case_films(ns):
    """The front panel film and the hub films of the pre-installed fans (the glass films come from build_case's
    films=True)."""
    st = ns.st
    P.anchor("A_FILM_FRONT_0", P.Frame((ns.xface - 0.00005, (ns.by0 + ns.by1) / 2, 0.0), NX, Y),
             (2 * ns.bz, ns.by1 - ns.by0, 0.0001), ns.root, meta="peel=-y,tab=+y+z,on=front_panel")
    if st.get("badge_film"):
        P.anchor("A_FILM_BADGE_0", P.Frame((ns.xface - 0.0016 - 0.00005, 0.0195, 0.0), NX, Y), (0.104, 0.018, 0.0001),
                 ns.root, meta="peel=-z,tab=+z,on=badge")
    anchors = {o.name.split("@")[0]: o for o in c.descendants(ns.root) if o.type == "EMPTY"}
    for name, pos, fwd_, up_, d_ in ns.fans:
        n = int(name.rsplit("_", 1)[1])
        hub_film(anchors[name], d_, n=n)


def with_films(extra):
    def hook(ns):
        if extra:
            extra(ns)
        case_films(ns)
    return hook


CASES = {
    "case_lumin_216": dict(
        brand="LUMIN", model="AIRWAVE 216", paint="paint_black", trim="black_plastic", bezel="black_plastic",
        cover_tag="paint_black", screw_tag="steel_dark", logo_tag="grey_plastic", logo_font="arialbd.ttf",
        shroud_logo_tag="grey_plastic", front="mesh", fans_front=2, front_fans=[(0.318, 0.16), (0.155, 0.16)],
        fan_tag="fan_black", fan_rgb=True, fan_pins=4, hub=("LUMIN", "#111113", "#e8e8ea", "#9a7cff"),
        thumb_tag="steel_dark", led_power="led_white", label_bg=(0.93, 0.93, 0.9), code="LM-216R", sn="LM2",
        mesh=dict(web=(0.07, 0.07, 0.075), shape="hex", pitch=0.0026, r=0.00105),
        front_wall=front_wall_fans, face=face_lumin, feet=feet_rails, extra=extra_lumin),
    "case_phanta_g360a": dict(
        brand="PHANTA", model="UMBRA G360A", paint="paint_black", trim="black_plastic", bezel="black_plastic",
        cover_tag="paint_black", screw_tag="steel_dark", logo_tag="alu", logo_font="arialbd.ttf",
        shroud_logo_tag="alu", front="mesh", fans_front=3, fan_tag="fan_black", fan_rgb=True, fan_pins=4,
        hub=("PHANTA", "#121214", "#e8e8ea", "#ff3c8c"), thumb_tag="steel_dark", led_power="led_white",
        label_bg=(0.93, 0.93, 0.9), code="PH-G360A", sn="PG3",
        mesh=dict(web=(0.06, 0.06, 0.065), shape="round", pitch=0.0032, r=0.00125),
        face=face_phanta, extra=extra_phanta),
    "case_nexa_h5": dict(
        brand="NEXA", model="H5 DRAFT", paint="paint_white", trim="white_plastic", bezel="white_plastic",
        cover_tag="paint_white", screw_tag="steel", logo_tag="grey_plastic", logo_font="arialbd.ttf",
        shroud_logo_tag="grey_plastic", front="mesh", fans_front=2, front_fans=[(0.300, 0.12), (0.170, 0.12)],
        fan_tag="white_plastic", fan_rgb=False, fan_pins=4, hub=("NEXA", "#ececea", "#2a2c30", "#7a50d8"),
        thumb_tag="steel", led_power="led_white", label_bg=(0.96, 0.96, 0.95), code="NX-H5D", sn="NX5",
        mesh=dict(web=(0.90, 0.90, 0.89), shape="round", pitch=0.0050, r=0.0016),
        front_wall=front_wall_fans, face=face_nexa, feet=feet_rails),
    "case_facet_fjord": dict(
        brand="FACET", model="FJORD", paint="paint_black", trim="dark_plastic", bezel="dark_plastic",
        cover_tag="paint_black", screw_tag="steel_dark", logo_tag="alu", logo_font="arialbd.ttf",
        shroud_logo_tag="alu", front="mesh", fans_front=2, front_fans=[(0.300, 0.14), (0.155, 0.14)],
        fan_tag="fan_black", fan_rgb=False, fan_pins=4, hub=("FACET", "#141415", "#d8d8d4", "#a07850"),
        thumb_tag="steel_dark", led_power="led_white", label_bg=(0.93, 0.93, 0.9), code="FC-FJD", sn="FJ1",
        mesh=dict(web=(0.05, 0.05, 0.055), shape="hex", pitch=0.0030, r=0.0012),
        front_wall=front_wall_fans, face=face_fjord, feet=feet_round),
    "case_hush_500dx": dict(
        brand="HUSH", model="CALM BASE 500DX", paint="paint_black", trim="black_plastic", bezel="black_plastic",
        cover_tag="paint_black", screw_tag="steel_dark", logo_tag="alu", logo_font="seguisb.ttf",
        shroud_logo_tag="alu", front="mesh", fans_front=2, front_fans=[(0.300, 0.14), (0.155, 0.14)],
        fan_tag="fan_black", fan_rgb=False, fan_pins=4, hub=("hush", "#101011", "#e8e8ea", "#e87a1e"),
        thumb_tag="steel_dark", led_power="led_white", label_bg=(0.93, 0.93, 0.9), code="HS-500DX", sn="HB5",
        mesh=dict(web=(0.06, 0.06, 0.065), shape="hex", pitch=0.0036, r=0.0015),
        front_wall=front_wall_fans, face=face_hush),
    "case_facet_fizzair": dict(
        brand="FACET", model="FIZZ AIR", paint="paint_white", trim="white_plastic", bezel="white_plastic",
        cover_tag="paint_white", screw_tag="steel", logo_tag="grey_plastic", logo_font="arialbd.ttf",
        shroud_logo_tag="grey_plastic", front="mesh", fans_front=3, fan_tag="white_plastic", fan_rgb=False, fan_pins=3,
        hub=("FACET", "#ececea", "#2a2c30", "#00a0a4"), thumb_tag="steel", led_power="led_white",
        label_bg=(0.96, 0.96, 0.95), code="FC-FZA", sn="FZ1",
        mesh=dict(web=(0.90, 0.90, 0.89), shape="hex", pitch=0.0062, r=0.0026),
        face=face_fizz, extra=extra_fizz),
    "case_brickhouse_beige98": dict(
        brand="BRICKHOUSE", model="BEIGE 98", paint="connector_beige", trim="connector_beige", bezel="connector_beige",
        cover_tag="connector_beige", screw_tag="steel", logo_tag="dark_plastic", logo_font="ariblk.ttf",
        shroud_logo_tag="dark_plastic", front="solid", fans_front=0, fan_tag="fan_black", fan_rgb=False, fan_pins=3,
        hub=("BRICKHOUSE", "#d8ccb0", "#2a2620", "#7a6a50"), thumb_tag="steel", led_power="led_green",
        label_bg=(0.96, 0.94, 0.88), code="BH-B98", sn="B98",
        face=face_beige, feet=feet_square, extra=extra_beige, badge_film=True),
}

CASE_NOTES = {
    "case_lumin_216": "front fans A_FAN_1..2 are 160 mm at y 0.318 / 0.155 (breeze: three 120 mm A_FAN_1..3 at 0.352 / 0.230 / 0.108)",
    "case_phanta_g360a": "fans as case_breeze (three 120 mm front, one 120 mm rear)",
    "case_nexa_h5": "front fans A_FAN_1..2 are 120 mm at y 0.300 / 0.170 (no A_FAN_3)",
    "case_facet_fjord": "front fans A_FAN_1..2 are 140 mm at y 0.300 / 0.155 (no A_FAN_3)",
    "case_hush_500dx": "front fans A_FAN_1..2 are 140 mm at y 0.300 / 0.155 (no A_FAN_3)",
    "case_facet_fizzair": "fans as case_breeze (three 120 mm front, one 120 mm rear); 3-pin fans",
    "case_brickhouse_beige98": "no front fans (as case_brickhouse: A_FAN_0 rear only); 3-pin fan; extra anchors "
                               "A_BUTTON_TURBO_0, A_LED_TURBO_0",
}


def own_geometry(fn):
    """Wraps a build_case hook: the meshes it adds get outward normals (fix_normals), build_case's are untouched."""
    def hook(ns):
        before = {o.name for o in c.descendants(ns.root)}
        fn(ns)
        fix_normals(ns.root, {o.name for o in c.descendants(ns.root)} - before)
    return hook


def build_case_id(cid):
    st = CASES[cid]
    st = dict(st, films=True, extra=with_films(st.get("extra")))
    BC.STYLES[cid] = dict(st, **{k: own_geometry(st[k]) for k in ("face", "feet", "extra") if st.get(k)})
    CUR.clear()
    CUR["mesh"] = st.get("mesh")
    write_palette()
    if cid == "case_facet_fjord":
        wood_tex(cid + "_wood")
    out = BC.build(cid)
    CUR.clear()
    return out


# ---------------------------------------------------------------- fans: the case_fan contract

FANS = {
    "fan_arctiq_p12": dict(d=0.12, blades=5, brand="ARCTIQ", model="P12 PWM", rpm=1800, frame_tag="fan_black",
                           blade_tag="fan_black", hub=("#141416", "#e8e8ea", "#3aa0ff"), cov=(0.85, 1.08), sweep=0.42,
                           hub_ratio=0.2, amps="0.08A"),
    "fan_arctiq_p14": dict(d=0.14, blades=5, brand="ARCTIQ", model="P14 PWM", rpm=1700, frame_tag="fan_black",
                           blade_tag="fan_black", hub=("#141416", "#e8e8ea", "#3aa0ff"), cov=(0.85, 1.08), sweep=0.42,
                           hub_ratio=0.19, amps="0.10A"),
    "fan_noctis_a12x25": dict(d=0.12, blades=9, brand="NOCTIS", model="NF-A12x25 PWM", rpm=2000, frame_tag="connector_beige",
                              blade_pal="noc_brown", hub=("#7a4a34", "#efe6d2", "#d8c8a8"), pads="noc_brown",
                              cov=(0.66, 0.96), sweep=0.38, hub_ratio=0.19, amps="0.14A", tip_ring=False),
    "fan_noctis_a12x25_black": dict(d=0.12, blades=9, brand="NOCTIS", model="NF-A12x25 PWM onyx", rpm=2000,
                                    frame_tag="fan_black", blade_tag="fan_black", hub=("#121213", "#d8d8d8", "#6a6a6e"),
                                    pads="rubber", cov=(0.66, 0.96), sweep=0.38, hub_ratio=0.19, amps="0.14A"),
    "fan_lumin_sl120_white": dict(d=0.12, blades=9, brand="LUMIN", model="LINK FAN SL120", rpm=1900, frame_tag="white_plastic",
                                  blade_tag="white_plastic", hub=("#efefed", "#2a2c30", "#9a7cff"), rgb=True, side_bars=True,
                                  link=True, cov=(0.62, 0.92), hub_ratio=0.2, amps="0.20A"),
    "fan_corvex_af120_rgb": dict(d=0.12, blades=7, brand="CORVEX", model="AF120 RGB PRO", rpm=1500, frame_tag="fan_black",
                                 blade_tag="clear_plastic", hub=("#121213", "#e8e8ea", "#f0c020"), rgb=True, hub_ring=True,
                                 cov=(0.66, 0.96), hub_ratio=0.24, amps="0.18A"),
    "fan_hush_wing4_140": dict(d=0.14, blades=7, brand="hush", model="CALM WING 4 140", rpm=1100, frame_tag="fan_black",
                               blade_tag="fan_black", hub=("#101011", "#e8e8ea", "#e87a1e"), corners="orange",
                               cov=(0.68, 0.98), sweep=0.36, hub_ratio=0.18, amps="0.12A"),
}
TH = 0.025


def argb_plug(fr, parent, name="argb"):
    """A 3-pin 5 V ARGB plug (1 x 4 at 2.54 mm, position 3 blocked as the key): contact face at z=0, the body
    and three wires running back along +z. Black housing, a white arrow at pin 1."""
    w, hgt, L = 0.0104, 0.0030, 0.0120
    holes = [P.rrect(0.0011, 0.0011, 0.0001, (1.5 - i) * 0.00254, 0) for i in (0, 1, 3)]
    P.slab(name + "_face", P.rrect(w, hgt, 0.0004), 0.0006, "connector_black", fr.sub(0, 0, 0.0003), holes=holes, parent=parent)
    P.cube(name + "_body", (0, 0, 0.0006 + (L - 0.0006) / 2), (w, hgt, L - 0.0006), "connector_black", fr, parent, bevel=0.0003)
    P.cube(name + "_key", (-0.5 * 0.00254, 0, 0.00005), (0.0011, 0.0011, 0.0001), "connector_black", fr, parent)
    P.slab(name + "_arrow", [(-0.0002, 0), (0.0002, 0), (0, 0.0007)], 0.00006, "white_plastic",
           fr.sub(1.5 * 0.00254, hgt / 2 + 0.00003, 0.004, (0, 1, 0), (0, 0, -1)), parent=parent)
    for i, tag in ((0, "led_red"), (1, "led_green"), (3, "white_plastic")):
        x = (1.5 - i) * 0.00254
        P.cylinder(name + "_wire", P.Frame(fr.p(x, 0, L), fr.w, fr.v), 0.0006, 0.010, "rubber" if tag != "white_plastic" else "white_plastic",
                   8, parent, z0=0)
    return L + 0.006


def fan_texts(fid, sp):
    b = sp["brand"]
    bg, fg, ac = sp["hub"]
    PF.hub_sticker_texture(fid + "_hub", b, sp["model"].split()[0], bg, fg, ac)
    PF.motor_label_texture(fid + "_motor", b, sp["model"] + "  12V " + sp["amps"])
    return fid + "_hub", fid + "_motor"


def build_fan(fid):
    sp = FANS[fid]
    P.reset()
    write_palette()
    root = c.root(fid)
    D = sp["d"]
    h = TH / 2
    rgb = sp.get("rgb", False)
    sticker, label = fan_texts(fid, sp)
    # A_FAN_0: the rotor, as a case's A_FAN_<n>: local +Z = the intake side (= -Z of the model), +Y up
    fa = P.anchor("A_FAN_0", P.Frame((0, 0, 0), NZ, Y), (D, D, TH), root,
                  meta=PF.fan_meta("ccw", sp["rpm"]) + (",rgb=1" if rgb else ""))
    blade_tag = PAL_TAG if sp.get("blade_pal") else sp["blade_tag"]
    res = PF.make_fan(fa, diameter=D, thickness=TH, blades=sp["blades"], frame=True, rgb=rgb, spin="ccw", name="fan",
                      blade_tag=blade_tag, frame_tag=sp["frame_tag"], sticker=sticker, label=label,
                      cov=sp.get("cov"), sweep=sp.get("sweep"), hub_ratio=sp.get("hub_ratio"), return_all=True)
    if sp.get("blade_pal"):
        set_uv_solid(res["rotor"], pal(sp["blade_pal"]))
    made = {o.name for o in c.descendants(root)}     # parts_fan's meshes (left as they are)
    hs = PF.HOLE_SPACING[D]
    corners = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
    # ---- per-product details
    if sp.get("pads"):           # anti-vibration pads on both faces of each corner (Noctis)
        ptag = PAL_TAG if sp["pads"] != "rubber" else "rubber"
        for sx, sy in corners:
            cx, cy = sx * hs / 2, sy * hs / 2
            for zf in (-1, 1):
                outl = P.rrect(0.0125, 0.0125, 0.0030, cx + sx * 0.0012, cy + sy * 0.0012)
                o = P.slab("pad", outl, 0.0012, ptag, P.Frame((0, 0, zf * (h + 0.0006)), Z, Y), holes=[P.circle(0.0024, cx, cy, 16)],
                           parent=root, **({"uv_solid": pal(sp["pads"])} if ptag == PAL_TAG else {}))
    if sp.get("corners"):        # coloured corner inserts on the intake face (Hush)
        for sx, sy in corners:
            cx, cy = sx * (D / 2 - 0.0035), sy * (D / 2 - 0.0035)
            tri = [(cx, cy), (cx - sx * 0.016, cy), (cx, cy - sy * 0.016)]
            if sx * sy < 0:
                tri.reverse()
            hole = [P.circle(0.0026, sx * hs / 2, sy * hs / 2, 16)]      # the screw goes through the insert
            for zf in (-1, 1):
                P.slab("corner", tri, 0.0008, PAL_TAG, P.Frame((0, 0, zf * (h + 0.0004)), Z, Y), holes=hole, parent=root,
                       uv_solid=pal(sp["corners"]))
    if sp.get("side_bars"):      # light bars along both sides of the frame, on the intake face and the side walls
        for sx in (-1, 1):
            P.cube("side_bar", (sx * (D / 2 - 0.0028), 0, -h - 0.0003), (0.0030, D - 0.030, 0.0008), "rgb", parent=root)
            P.cube("side_bar", (sx * (D / 2 + 0.0002), 0, -0.004), (0.0006, D - 0.030, 0.008), "rgb", parent=root)
    if sp.get("hub_ring"):       # the LED ring round the hub (spins with the rotor)
        r_hub = D * sp["hub_ratio"]
        P.lathe("hub_ring", [(r_hub - 0.0012, -h + 0.0068), (r_hub + 0.0004, -h + 0.0068), (r_hub + 0.0004, h - 0.004),
                             (r_hub - 0.0012, h - 0.004)], "rgb", P.Frame((0, 0, 0), NZ, Y), 48, fa)
    link = sp.get("link")
    if link:                     # interlocking side connectors: a socket on the -x side wall, a plug tongue on +x
        # (model x; the fan's -x side faces the neighbour's +x side when two are slid together)
        P.cube("link_housing", (-D / 2 - 0.0012, -0.030, 0.0035), (0.0024, 0.024, 0.0110), "white_plastic", parent=root, bevel=0.0004)
        P.cube("link_socket", (-D / 2 - 0.0024, -0.030, 0.0035), (0.0004, 0.018, 0.0060), "connector_black", parent=root)
        for k in range(6):
            P.cube("link_pin_slot", (-D / 2 - 0.00245, -0.030 - 0.0075 + 0.003 * k, 0.0035), (0.0002, 0.0012, 0.0030), "gold", parent=root)
        P.cube("link_tongue_base", (D / 2 + 0.0008, -0.030, 0.0035), (0.0016, 0.024, 0.0110), "white_plastic", parent=root, bevel=0.0004)
        P.cube("link_tongue", (D / 2 + 0.0026, -0.030, 0.0035), (0.0022, 0.0175, 0.0055), "connector_black", parent=root, bevel=0.0003)
        for k in range(6):
            P.cube("link_pin", (D / 2 + 0.0037, -0.030 - 0.0075 + 0.003 * k, 0.0035), (0.0002, 0.0012, 0.0030), "gold", parent=root)
        P.anchor("A_PORT_LINK_0", P.Frame((-D / 2 - 0.0024, -0.030, 0.0035), NX, Y), (0.004, 0.024, 0.011), root,
                 meta=f"chain=link,mate=A_PLUG_LINK_0,pitch={D + 0.0005:.4f},carries=pwm+argb")
        P.anchor("A_PLUG_LINK_0", P.Frame((D / 2 + 0.0037, -0.030, 0.0035), X, Y), (0.004, 0.024, 0.011), root,
                 meta=f"chain=link,mate=A_PORT_LINK_0,pitch={D + 0.0005:.4f},carries=pwm+argb")
    # ---- screw holes (through the frame; screws come from either face, local +Z = the intake side)
    for i, (sx, sy) in enumerate(corners):
        P.anchor(f"A_HOLE_{i}", P.Frame((sx * hs / 2, sy * hs / 2, -h), NZ, Y), (0.008, 0.008, TH), root,
                 meta=f"d=0.0043,spacing={hs:.4f},through=1,screw=fan")
    # ---- cables and the loose plugs: they leave the frame's lower corner and rest below the fan
    ex = res["exit"]
    ex = (ex.x, ex.y, ex.z)
    sgn = -1 if ex[0] < 0 else 1
    plugs = [("A_PLUG_FAN_0", "fan4", 0.0, "kind=fan4,pinout=GND|12V|TACH|PWM,fan=0")]
    if rgb:
        plugs.append(("A_PLUG_ARGB_0", "argb", 0.010, "kind=argb3,pinout=5V|D|KEY|GND,v=5,fan=0"))
    if link:
        ex = (-D / 2 - 0.002, -0.030, 0.0035)       # the controller lead leaves from the link socket's housing
    for k, (name, kind, dz, meta) in enumerate(plugs):
        px = -sgn * (0.020 + 0.018 * k)
        py = -D / 2 - 0.0055
        pz = h - 0.004 - dz
        cable_dir = (sgn, 0, 0)                     # back along the cable, towards the corner it left from
        fr = P.Frame((px, py, pz), cable_dir, (0, 1, 0))
        a = P.anchor(name, fr, (0.025, 0.012, 0.03), root, meta=meta)
        if kind == "argb":
            tail = argb_plug(P.anchor_frame(a), a)
        else:
            BP.PLUGS[kind](P.anchor_frame(a), a)
            tail = 0.020
        end = (px + sgn * tail, py, pz)
        mid = (ex[0] + sgn * 0.004, py - 0.0002, pz) if not link else (ex[0] - 0.006, ex[1] - 0.010, ex[2] - dz)
        route = [ex, (ex[0], min(ex[1], -D / 2 + 0.004), ex[2] - 0.001 - dz), mid, end] if not link else [ex, mid, (ex[0] - 0.004, py, pz), end]
        P.tube("cable_" + kind, P.smooth_path(route, 6), 0.0013 if kind == "argb" else 0.0017,
               "white_plastic" if sp["frame_tag"] == "white_plastic" else "rubber", root, 8)
    # ---- unboxing films: the hub sticker disc, and the glossy light ring on RGB frames
    hub_film(fa, D, TH, sp.get("hub_ratio") or 0.172)
    if rgb:
        P.anchor("A_FILM_RING_0", P.Frame((0, 0, -h - 0.00005), NZ, Y), (D, D, 0.0001), root,
                 meta=f"peel=+x,tab=+x+y,shape=ring,r_in={(D / 2 - D * 0.0105) * 0.92:.4f}")
    P.anchor("A_HIT_0", (0, 0, 0), (D, D, TH), root)
    fix_normals(root, {o.name for o in c.descendants(root)} - made)
    P.finalize(root, fid)
    c.export(root, fid)
    extra = (f"frame: case_fan contract - origin at the frame centre, +Z = airflow (the intake face at z={-h:.4f}), "
             f"{D * 1000:.0f} mm frame, {TH * 1000:.0f} mm deep, holes {hs * 1000:.1f} mm apart")
    tris, meshes = P.write_report(root, fid, extra)
    P.preview(root, fid, views=((200, 25), (25, 25)), size=(900, 760))
    P.beauty(root, fid, views=((205, 22), (30, 25), (150, 60)), size=(1100, 960), samples=SAMPLES)
    return tris, meshes


# ---------------------------------------------------------------- main

ORDER = ["case_lumin_216", "case_phanta_g360a", "case_nexa_h5", "case_facet_fjord", "case_hush_500dx",
         "case_facet_fizzair", "case_brickhouse_beige98",
         "fan_arctiq_p12", "fan_noctis_a12x25", "fan_noctis_a12x25_black", "fan_lumin_sl120_white",
         "fan_corvex_af120_rgb", "fan_arctiq_p14", "fan_hush_wing4_140"]


def main(argv):
    if "--nopreview" in argv:
        P.PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")] or ORDER
    t0 = time.time()
    for i in ids:
        t = time.time()
        out = build_case_id(i) if i in CASES else build_fan(i)
        print(f"BUILT {i} {out} in {time.time() - t:.1f}s")
    write_family_report()
    print(f"BUILD_CAT_CASES done: {len(ids)} in {time.time() - t0:.1f}s")


def write_family_report():
    """Logs/ModelPreviews/cat_cases_report.txt: every built id's report (meshes, triangles, anchors), in order."""
    parts = []
    for i in ORDER:
        path = os.path.join(c.PREVIEWS, f"{i}_report.txt")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                parts.append(fh.read().rstrip() + "\n")
    with open(os.path.join(c.PREVIEWS, "cat_cases_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("Catalogue 17: cases and fans (build_cat_cases.py)\n\n" + "\n".join(parts))


if __name__ == "__main__":
    main(c.args())
