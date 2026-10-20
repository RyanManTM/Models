"""
The bench test monitor: monitor_24, a modern 23.8" IPS monitor (three-sided thin bezel, a chin with the logo),
a height-style neck and a flat base.

Run:  "D:\\New folder\\blender.exe" -b --factory-startup -P Tools/Blender/build_monitor.py

Frame: origin at the bottom centre of the base (it stands on the desk), +y up, +z towards the viewer.
Anchors: A_SCREEN_0 (the screen surface centre, +z towards the viewer, size = active area 0.53 x 0.30; the dark
screen mesh is attached to it so the game can find it), A_PORT_DP_0 and A_PORT_C13_0 on the rear I/O panel
(facing -z, plugs come from behind), A_BUTTON_POWER_0 (front, bottom right of the chin) with A_LED_POWER_0 beside
it, A_HIT_0 (the panel) and A_HIT_1 (stand and base).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ

AW, AH = 0.530, 0.2985        # active area
BS, BT, BB = 0.0062, 0.0062, 0.0185   # bezel: sides, top, bottom chin
W = AW + 2 * BS
H = AH + BT + BB
Y0 = 0.098                     # bottom of the panel
ZF = 0.022                     # front (glass) surface
THIN = 0.0085                  # thickness of the thin outer part
YC = Y0 + BB + AH / 2          # screen centre height


def label_texture():
    art = P.Art(512, 256, bg=(0.92, 0.92, 0.9), name="mon_label")
    ink = (0.08, 0.08, 0.09)
    art.text("LUMEN", 20, 205, 40, ink, "seguibl.ttf")
    art.text("MODEL: LM-24F1   23.8\" IPS 1920x1080", 20, 168, 20, ink, "arialbd.ttf", maxw=470)
    art.text("INPUT: 100-240V~ 50/60Hz 1.0A", 20, 140, 18, ink, "arial.ttf")
    art.code128ish(2401, 20, 70, 330, 56, ink)
    art.text("S/N  LM24F12610190088", 20, 46, 18, ink, "consola.ttf")
    art.text("CE  FC  \u267b", 380, 98, 32, ink, "seguisym.ttf")
    art.text("MADE IN CHINA", 20, 16, 16, ink, "arial.ttf")
    art.render("monitor_24_label")
    art.dispose()


def rear_shell(root):
    """The back: a thin plate behind the panel and the rounded electronics bulge with vents."""
    # the thin back cover (outline follows the front, small radius)
    outline = P.rrect(W, H, 0.004, 0, Y0 + H / 2)
    P.slab("back_cover", outline, THIN - 0.0018, "black_plastic", P.plane((0, 0, ZF - 0.0018 - (THIN - 0.0018) / 2), X, Y), parent=root)
    # the bulge: one smooth lofted dome (rounded rectangles shrinking towards the back)
    yc = Y0 + 0.125
    z0 = ZF - THIN + 0.0005
    depth = 0.0285
    secs = []
    for i in range(9):
        t = i / 8
        k = 1 - (1 - math.cos(t * math.pi / 2)) * 0.22      # shrinks faster near the back: a soft dome
        w, h = 0.330 * k, 0.205 * (1 - (1 - math.cos(t * math.pi / 2)) * 0.26)
        secs.append((P.rrect(w, h, 0.032 * k, 0, yc, 6), z0 - depth * math.sin(t * math.pi / 2)))
    P.loft("bulge", secs, "black_plastic", parent=root, smooth=55)
    z = z0 - depth
    zb = z  # back face of the bulge
    # vent slots across the top of the bulge (cut into a thin cap so they read as openings)
    vents = [P.stadium(0.022, 0.0026, -0.088 + 0.022 * k, yc + 0.055) for k in range(9)]
    P.slab("bulge_vent_plate", P.rrect(0.222, 0.026, 0.006, 0, yc + 0.055), 0.0012, "black_plastic",
           P.plane((0, 0, zb - 0.0006), X, Y), holes=vents, parent=root)
    P.slab("bulge_vent_dark", P.rrect(0.214, 0.018, 0.004, 0, yc + 0.055), 0.0004, "dark_plastic",
           P.plane((0, 0, zb + 0.0012), X, Y), parent=root)
    return zb, yc


def build():
    P.reset()
    label_texture()
    root = c.root("monitor_24")

    # ---------------- front: bezel frame, the dark border under the glass, the screen
    outer = P.rrect(W, H, 0.0035, 0, Y0 + H / 2)
    inner = P.rrect(AW + 0.003, AH + 0.003, 0.0008, 0, YC)
    P.slab("bezel", outer, 0.0018, "black_plastic", P.plane((0, 0, ZF - 0.0009), X, Y), holes=[inner], parent=root)
    P.slab("bezel_lip", P.rrect(W - 0.0012, H - 0.0012, 0.003, 0, Y0 + H / 2), 0.0004, "black_plastic",
           P.plane((0, 0, ZF + 0.0002), X, Y), holes=[P.rrect(AW + 0.0065, AH + 0.0065, 0.001, 0, YC)], parent=root)
    # the chin: slightly thicker band with the logo
    P.slab("chin", P.rrect(W, BB - 0.001, 0.003, 0, Y0 + (BB - 0.001) / 2), 0.0028, "dark_plastic",
           P.plane((0, 0, ZF - 0.0011), X, Y), parent=root)
    P.text3d("logo", "LUMEN", 0.0062, 0.00012, "grey_plastic", P.Frame((0, Y0 + BB * 0.5, ZF + 0.0003), Z, Y), "seguibl.ttf",
             parent=root, width=0.036, spacing=1.2)
    # the black inactive border (under the glass) and the screen itself
    P.slab("panel_border", P.rrect(AW + 0.0035, AH + 0.0035, 0.0008, 0, YC), 0.0006, "black_plastic",
           P.plane((0, 0, ZF - 0.0005), X, Y), parent=root)
    scr = P.anchor("A_SCREEN_0", P.Frame((0, YC, ZF - 0.0001), Z, Y), (AW, AH, 0.002), root,
                   meta="px=1920x1080,ref=1024x576,diag=23.8")
    P.quad("screen", P.Frame((0, YC, ZF - 0.0001), Z, Y), AW, AH, "black_plastic", scr)
    # the panel's side edge (metal frame peeking out between front and back)
    P.slab("panel_edge", P.rrect(W - 0.0004, H - 0.0004, 0.0033, 0, Y0 + H / 2), 0.0012, "alu_dark",
           P.plane((0, 0, ZF - 0.0024), X, Y), holes=[P.rrect(W - 0.004, H - 0.004, 0.002, 0, Y0 + H / 2)], parent=root)

    # ---------------- back
    zb, yc = rear_shell(root)
    # VESA 100 plate with the stand's quick-release bracket
    vesa = [P.circle(0.0024, sx * 0.05, yc + sy * 0.05, 14) for sx in (-1, 1) for sy in (-1, 1)]
    P.slab("vesa_plate", P.rrect(0.125, 0.125, 0.012, 0, yc), 0.0012, "dark_plastic", P.plane((0, 0, zb - 0.0006), X, Y),
           holes=vesa, parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.cylinder("vesa_insert", P.Frame((sx * 0.05, yc + sy * 0.05, zb + 0.0005), NZ, Y), 0.0024, 0.002, "steel", 14, root,
                       z0=-0.001)
    # rear label sticker
    P.quad("label", P.Frame((-0.095, yc - 0.02, zb - 0.0002), NZ, Y), 0.06, 0.03, "tex_monitor_24_label", root)

    # ---------------- rear I/O block: a moulded block on the back of the bulge with the port cavities through it
    io_y = Y0 + 0.068
    depth = 0.0078
    io_z = zb - depth            # the face the plugs go into (facing -z)
    PX = {"c14": -0.085, "dp": 0.060, "hdmi": 0.087, "audio": 0.110}   # power left of the neck, video right (seen from the front)
    ch = 0.0042
    w14, h14 = 0.0246, 0.0164
    c14 = [(-w14 / 2, -h14 / 2), (w14 / 2, -h14 / 2), (w14 / 2, h14 / 2 - ch), (w14 / 2 - ch, h14 / 2), (-w14 / 2 + ch, h14 / 2), (-w14 / 2, h14 / 2 - ch)]
    dpw, dph, dpc = 0.0166, 0.0052, 0.0018
    dp = [(-dpw / 2, -dph / 2), (dpw / 2 - dpc, -dph / 2), (dpw / 2, -dph / 2 + dpc), (dpw / 2, dph / 2), (-dpw / 2, dph / 2)]
    hw, hh, hc = 0.0148, 0.0050, 0.0013
    hd = [(-hw / 2 + hc, -hh / 2), (hw / 2 - hc, -hh / 2), (hw / 2, -hh / 2 + hc), (hw / 2, hh / 2), (-hw / 2, hh / 2), (-hw / 2, -hh / 2 + hc)]
    # the block's local frame: x along -x (seen from behind, +local x is the viewer's right), y up, z out (-z)
    bfr = P.Frame((0, io_y, zb - depth / 2), NZ, Y)
    def at(x, pts):
        return [(-x + px_, py_) for (px_, py_) in pts]   # local x = -case x
    P.slab("io_block", P.rrect(0.036, 0.026, 0.004, -PX["c14"], 0), depth, "black_plastic", bfr, holes=[at(PX["c14"], c14)], parent=root)
    holes = [at(PX["dp"], dp), at(PX["hdmi"], hd), P.circle(0.0032, -PX["audio"], 0, 20)]
    P.slab("io_block", P.rrect(0.072, 0.026, 0.004, -0.085, 0), depth, "black_plastic", bfr, holes=holes, parent=root)
    def port_frame(x, dy=0.0):
        return P.Frame((x, io_y + dy, io_z), NZ, Y)
    # C14 inlet (the C13 plug goes in): dark cavity, three pins
    pf = port_frame(PX["c14"])
    P.slab("c14_floor", c14, 0.0006, "dark_plastic", pf.sub(0, 0, -depth + 0.0006), parent=root)
    for (x, y, ww, hh_) in ((-0.007, -0.002, 0.0008, 0.0040), (0.007, -0.002, 0.0008, 0.0040), (0.0, 0.0045, 0.0040, 0.0008)):
        P.cube("c14_pin", (x, y, -depth + 0.0035), (ww, hh_, 0.005), "nickel", pf, root)
    P.anchor("A_PORT_C13_0", pf.sub(0, 0, 0.0002), (0.028, 0.02, 0.012), root, meta="inlet=c14")
    # DisplayPort and HDMI: a metal shell lining the cavity, the contact tongue, a dark floor
    for name, pts, tw in (("dp", dp, 0.0118), ("hdmi", hd, 0.0106)):
        f = port_frame(PX[name])
        P.slab(name + "_shell", pts, depth - 0.0004, "nickel", f.sub(0, 0, -(depth - 0.0004) / 2),
               holes=[[(px_ * 0.94, py_ * 0.82) for (px_, py_) in pts]], parent=root)
        P.cube(name + "_tongue", (0, -0.0003, -depth * 0.55), (tw, 0.0012, depth * 0.8), "black_plastic", f, root)
        P.slab(name + "_floor", pts, 0.0004, "dark_plastic", f.sub(0, 0, -depth + 0.0005), parent=root)
        if name == "dp":
            P.anchor("A_PORT_DP_0", f.sub(0, 0, 0.0002), (0.02, 0.008, 0.012), root, meta="dp=1.4")
    af = port_frame(PX["audio"])
    P.lathe("audio", [(0.0019, 0.0), (0.0032, 0.0), (0.0032, -depth + 0.001), (0.0019, -depth + 0.001)], "nickel", af, 20, root)
    P.cylinder("audio_hole", af.sub(0, 0, -depth + 0.0008), 0.0019, 0.0005, "dark_plastic", 16, root)
    P.slab("kensington", P.rrect(0.007, 0.003, 0.0006, 0.13, Y0 + 0.03), 0.002, "steel_dark", P.plane((0, 0, ZF - THIN - 0.001), X, Y),
           holes=[P.rrect(0.0055, 0.0018, 0.0003, 0.13, Y0 + 0.03)], parent=root)
    # tiny port legends above the ports (raised print, reads from behind)
    for (x, s_) in ((PX["c14"], "AC IN"), (PX["dp"], "DP"), (PX["hdmi"], "HDMI"), (PX["audio"], "AUDIO")):
        P.text3d("io_print", s_, 0.0022, 0.00006, "grey_plastic", P.Frame((x, io_y + 0.0115, io_z), NZ, Y), "arialbd.ttf",
                 parent=root, width=0.012)

    # ---------------- power button and LED on the chin (front, bottom right as you face the screen)
    bx = -(AW / 2 - 0.012)  # viewer's right is -x
    bf = P.Frame((bx, Y0 + 0.0065, ZF + 0.0004), Z, Y)
    P.lathe("btn_ring", [(0.0024, 0.0001), (0.0032, 0.0001), (0.0032, -0.0008), (0.0024, -0.0008)], "dark_plastic", bf, 24, root)
    ab = P.anchor("A_BUTTON_POWER_0", bf, (0.008, 0.008, 0.006), root, meta="press=-z_local,travel=0.0008")
    P.lathe("btn_cap", [(0, 0.0003), (0.0021, 0.0003), (0.0023, 0.0), (0.0023, -0.002), (0, -0.002)], "black_plastic", bf, 24, ab)
    P.slab("btn_icon", P.arc(0, 0, 0.0011, math.radians(120), math.radians(420), 16) + P.arc(0, 0, 0.0007, math.radians(420), math.radians(120), 16),
           0.00006, "grey_plastic", bf.sub(0, 0, 0.00033), parent=ab)
    lf = P.Frame((bx + 0.0075, Y0 + 0.0065, ZF + 0.0002), Z, Y)
    al = P.anchor("A_LED_POWER_0", lf, (0.003, 0.003, 0.003), root, meta="colour=white")
    P.cube("led", (0, 0, -0.0003), (0.0022, 0.0008, 0.0008), "led_white", lf, al)

    # ---------------- stand: neck and base
    ny0, ny1 = 0.010, yc + 0.02          # neck from the base to the VESA bracket
    nz_bot, nz_top = -0.075, zb - 0.011  # the neck leans forward a little
    # neck: a tapered, rounded column (sections lofted between two outlines)
    def neck_section(t):
        y = ny0 + (ny1 - ny0) * t
        z = nz_bot + (nz_top - nz_bot) * t
        w = 0.058 - 0.010 * t
        return y, z, w
    d = P.vec((0, ny1 - ny0, nz_top - nz_bot))
    nfr = P.Frame((0, ny0, nz_bot), d.normalized(), (0, 0, -1))
    secs = []
    for i in range(7):
        t = i / 6
        _, _, w = neck_section(t)
        secs.append((P.rrect(w, 0.022, 0.0075, 0, 0, 5), d.length * t))
    P.loft("neck", secs, "dark_plastic", nfr, parent=root, smooth=50)
    # the VESA bracket the neck holds
    P.slab("neck_head", P.rrect(0.11, 0.09, 0.012, 0, yc - 0.005), 0.010, "dark_plastic", P.plane((0, 0, zb - 0.0062), X, Y), parent=root)
    # cable management hole in the neck
    P.slab("neck_clip", P.rrect(0.036, 0.024, 0.008, 0, 0.0), 0.0035, "black_plastic",
           P.Frame((0, 0.10, nz_bot + (nz_top - nz_bot) * ((0.10 - ny0) / (ny1 - ny0)) - 0.0125), NZ, Y),
           holes=[P.rrect(0.026, 0.014, 0.006)], parent=root)
    # base: a flat rounded plate with a soft top edge and rubber feet
    bl, bw = 0.245, 0.185
    bc = (0.0, -0.012)
    P.slab("base", P.rrect(bl, bw, 0.06, bc[0], bc[1], 12), 0.0105, "dark_plastic", P.plane((0, 0.0053, 0), X, NZ), parent=root)
    P.slab("base_top", P.rrect(bl - 0.006, bw - 0.006, 0.057, bc[0], bc[1], 12), 0.002, "dark_plastic", P.plane((0, 0.0115, 0), X, NZ), parent=root)
    P.slab("base_collar", P.rrect(0.075, 0.040, 0.012, 0, 0.075), 0.006, "black_plastic", P.plane((0, 0.0145, 0), X, NZ), parent=root)
    for (x, z) in [(-0.095, -0.062), (0.095, -0.062), (-0.095, 0.088), (0.095, 0.088)]:
        P.cylinder("foot", P.Frame((x, 0.0004, z), Y, Z), 0.008, 0.0008, "rubber", 16, root)

    # ---------------- hitboxes
    P.anchor("A_HIT_0", ((0, Y0 + H / 2, ZF - 0.02)), (W, H, 0.045), root)
    P.anchor("A_HIT_1", ((0, 0.09, -0.04)), (0.245, 0.18, 0.19), root)

    P.finalize(root, "monitor_24")
    c.export(root, "monitor_24")
    tris, meshes = P.write_report(root, "monitor_24")
    P.preview(root, "monitor_24", views=((25, 15), (155, 20)), size=(960, 720))
    P.beauty(root, "monitor_24", views=((28, 12), (150, 18), (200, 5)), size=(1280, 960), samples=96)
    P.beauty(root, "monitor_24", views=((160, 5),), size=(1280, 960), samples=96, target=(0.0, Y0 + 0.06, zb), dist=0.42, start_index=5)
    return tris, meshes


def main():
    r = build()
    print("BUILT monitor_24", r)
    return r


if __name__ == "__main__":
    main()
