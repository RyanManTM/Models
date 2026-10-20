r"""
build_parts_d.py - parts batch D: four new catalog parts that drop into the game exactly like their siblings.

    "D:\New folder\blender.exe" -b --factory-startup -P Tools/Blender/build_parts_d.py -- [ids...] [--nopreview]

  cpu_arc9      ARC 9 9900X, Socket V5. build_cpu.py with a new spec: cpu_arc5/arc7's package, frame and anchors,
                its own heat-spreader markings (cpu_arc9_ihs.png; the substrate art cpu_v5_pcb.png is shared).
  gpu_rx77      VOLTRA RX 7700, 270 mm, 2.5 slots, 3 fans, 2 x PCIe 8-pin. build_gpu.py with a new spec and style
                hooks (the shroud overlay, skirts, logo plate, backplate); the frame and anchor kinds of gpu_rx66/rx88.
  case_aero     AERO View 360 mid-tower. build_case.py with a new style: black, a panoramic glass front, three
                92 mm ARGB bottom fans; case_breeze's anchors except the fans A_FAN_1..3.
  mb_ridge_x5   RIDGE X5 Elite + its I/O shield io_ridge_x5. build_board.Board subclassed for looks only (silver PCB,
                bigger white VRM heatsinks, armoured slots, white I/O cover); mb_ridge_b5's layout and anchors.

With no ids it builds all of them. Each model writes Assets/Resources/Models/<id>.fbx, its textures, previews
Logs/ModelPreviews/<id>_<n>.png and Logs/ModelPreviews/<id>_report.txt (meshes, triangles, every anchor).
Nothing here edits an existing model: the existing builders are reused with new specs.
"""
import os
import sys
import time
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_cpu  # noqa: E402
import build_gpu  # noqa: E402
import build_case  # noqa: E402
import build_board  # noqa: E402

PREVIEW = [True]

# ---------------------------------------------------------------- cpu_arc9

build_cpu.SPECS["cpu_arc9"] = dict(sock="V5", line1="ARC 9 9900X", cores="12-CORE", opn="100-000001277",
                                   lot="9MK4813R50093", fab="DIFFUSED IN TAIWAN", made="MADE IN MALAYSIA", seed=9)


def build_cpu_arc9():
    root = build_cpu.build("cpu_arc9")
    P.write_report(root, "cpu_arc9", "frame: as cpu_arc5/arc7 (V5 40 x 40 mm package, origin at the contact face centre, +z up)")
    if PREVIEW[0]:
        build_cpu.previews("cpu_arc9", root)
    return root


# ---------------------------------------------------------------- gpu_rx77
# build_gpu.py's card with a new spec: 270 mm, 2.5 slots (50 mm), three 78 mm fans, two PCIe 8-pin ports, a dark
# grey shroud with silver rings, edge rails and chevrons, a brushed silver backplate with a hex flow-through window.
# The style hooks get (m, ns): ns holds build_gpu.build()'s local variables (xa, xb, H, yF, fxs, fz, r_hole, ...).

def _rx77_backplate(m, n):
    """Flow-through: a hex-perforated window past the end of the PCB (over the third fan)."""
    return build_gpu.hex_grid(n.xa + 0.010, 0.016, n.pcb_end - 0.006, n.H - 0.016, 0.0034, 0.0012)


def _rx77_overlay(m, n):
    G, pb = build_gpu, build_gpu.pb
    xa, xb, H, yF, fz = n.xa, n.xb, n.H, n.yF, n.fz
    fxs = n.fxs

    def mirror(pts):
        return [(x, 2 * fz - z) for (x, z) in reversed(pts)]

    # silver rails along both long edges, with slanted ends
    rail = [(xa + 0.014, 0.0058), (xb - 0.017, 0.0058), (xb - 0.0130, 0.0090), (xa + 0.0180, 0.0090)]
    for pts in (rail, mirror(rail)):
        G.slab_xz(m, "alu", pts, [], yF - 0.0012, 0.0012, bevel=0.0002)
    # black wedges between the fan rings (top and bottom) with a silver chevron and a screw
    for i in range(len(fxs) - 1):
        xm = (fxs[i] + fxs[i + 1]) / 2
        wedge = [(xm - 0.019, fz + 0.0445), (xm + 0.019, fz + 0.0445), (xm + 0.0035, fz + 0.0205), (xm - 0.0035, fz + 0.0205)]
        for pts, sgn in ((wedge, 1), (mirror(wedge), -1)):
            G.slab_xz(m, n.s["over_tag"], pts, [], yF - 0.0016, 0.0016, bevel=0.0003)
            for side in (-1, 1):
                strip = [(xm + side * 0.0125, fz + sgn * 0.0415), (xm + side * 0.0100, fz + sgn * 0.0415),
                         (xm + side * 0.0010, fz + sgn * 0.0262), (xm + side * 0.0035, fz + sgn * 0.0262)]
                if side < 0:
                    strip = list(reversed(strip))
                if sgn < 0:
                    strip = list(reversed(strip))
                G.slab_xz(m, "alu", strip, [], yF - 0.0019, 0.0004)
            pb.screw_ph(m.mb("steel_dark"), (xm, yF - 0.0016, fz + sgn * 0.0355), (0, -1, 0), (1, 0, 0), r=0.0016, h=0.0007)
    # silver corner blades at both ends
    for (x0, d) in ((xa + 0.0045, 1), (xb - 0.0045, -1)):
        for sgn in (1, -1):
            zz = fz + sgn * (H / 2 - 0.0035)
            blade = [(x0, zz), (x0 + d * 0.0035, zz), (x0 + d * 0.0035, zz - sgn * 0.030), (x0, zz - sgn * 0.024)]
            if (d > 0) != (sgn > 0):
                blade = list(reversed(blade))
            G.slab_xz(m, "alu", blade, [], yF - 0.0016, 0.0016, bevel=0.0002)


def _rx77_skirts(m, n):
    xa, xb, yF = n.xa, n.xb, n.yF
    top = [(xa + 0.002, yF), (xb - 0.0015, yF), (xb - 0.0015, yF + 0.022), (xb - 0.018, yF + 0.022), (xb - 0.026, yF + 0.0145),
           (xa + 0.092, yF + 0.0145), (xa + 0.080, yF + 0.0265), (xa + 0.002, yF + 0.0265)]
    bot = [(xa + 0.004, yF), (xb - 0.002, yF), (xb - 0.002, yF + 0.0145), (xa + 0.032, yF + 0.0145), (xa + 0.020, yF + 0.0225),
           (xa + 0.004, yF + 0.0225)]
    return top, bot, 0.0265


def _rx77_logo(m, n):
    xa, xb, yF = n.xa, n.xb, n.yF
    lw, lh = 0.092, 0.0105
    lx = (xa + 0.092 + xb - 0.026) / 2
    return lw, lh, lx, yF + 0.0074, (xa + 0.016, xb - 0.030), yF + 0.0017


def _rx77_trim(m, n):
    G, pb = build_gpu, build_gpu.pb
    xa, xb, H, yF = n.xa, n.xb, n.H, n.yF
    # a silver line along the step of the top skirt, and the model print on the bottom edge
    G.box(m, "alu", (xa + 0.094, yF + 0.0136, H - 0.0001), (xb - 0.028, yF + 0.0146, H + 0.0004))
    G.box(m, "alu", (xa + 0.006, yF + 0.0250, H - 0.0001), (xa + 0.078, yF + 0.0260, H + 0.0004))
    m.add(n.TEX, pb.g_quad(0.08, 0.010, n.at.uv("plate")), pb.label_frame((0, 0, -1), (0, 1, 0)),
          ((xa + xb) / 2 + 0.02, yF + 0.0075, 0.0020 - 0.00005))


build_gpu.SPECS["gpu_rx77"] = dict(
    L=0.270, H=0.118, T=0.050, Hp=0.108, fans=3, fan_d=0.078, blades=11, tip_ring=False, power="pcie8",
    px=[-0.1005, -0.0790], model="RX 7700", mem="12GB GDDR6", pcb_end=-0.128, pipes=5, pipe_tag="nickel", xd=0.022,
    zd=0.058, bracket_tag="steel", back_tag="alu", face_tag="steel_dark", over_tag="black_plastic", ring_tag="alu",
    logo_tag="paint_black", accent="#c4c8ce", emblem="#c4c8ce", vent="slots", sn="S/N 241077A0071942", qr_seed=8,
    swatch="#c4c8ce", logo_maxw=262, bp_logo_x=-0.045, core="screws", backplate=_rx77_backplate, overlay=_rx77_overlay,
    skirts=_rx77_skirts, logo=_rx77_logo, trim=_rx77_trim)


def build_gpu_rx77():
    if not PREVIEW[0]:
        build_gpu.pb.shots = lambda *a, **k: None
    mdl = build_gpu.build("gpu_rx77")
    with open(os.path.join(c.PREVIEWS, "gpu_rx77_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(mdl.report() + "\n")
    return mdl


# ---------------------------------------------------------------- case_aero
# build_case.py's mid-tower with a new style: black, a panoramic glass front that meets the side glass without a
# corner pillar, three 92 mm ARGB intake fans lying on the PSU shroud (behind the 2.5" sled), a 120 mm ARGB rear fan.
# Every anchor except the bottom fans' A_FAN_1..3 is where case_breeze has it.

build_case.STYLES["case_aero"] = dict(
    brand="AERO", model="VIEW 360", paint="paint_black", trim="black_plastic", bezel="black_plastic",
    cover_tag="paint_black", screw_tag="steel_dark", logo_tag="alu", logo_font="seguisb.ttf", shroud_logo_tag="alu",
    front="glass", fans_front=0, fans_bottom=3, bottom_fan_d=0.092, fan_tag="fan_black", fan_rgb=True, fan_pins=4,
    hub=("AERO", "#121315", "#e8eaee", "#7cc8ff"), thumb_tag="steel_dark", led_power="led_white",
    label_bg=(0.93, 0.93, 0.9), code="AR-V360", sn="AR3", films=True)   # films: the glass film anchors (unboxing)


def build_case_aero():
    return build_case.build("case_aero")


# ---------------------------------------------------------------- mb_ridge_x5 + io_ridge_x5
# build_board.py's Board with a new config and a subclass that only changes looks (no method that creates an anchor
# is overridden): a silver PCB, white VRM heatsinks that are taller and wider than the B5's, the rear one meeting the
# white I/O cover, armour on both full-length PCIe slots, white DIMM slots and latches, a second M.2 heatsink, and a
# bare-steel I/O shield. The layout (and so every anchor) is mb_ridge_b5's.

BB = build_board
BB.BOARDS["mb_ridge_x5"] = dict(
    sock="V5", mem="DDR5", model="X5 ELITE", chipset="RX670", shield="io_ridge_x5",
    mask="#c4c7cc", trace="#b7bbc1", pour="#bdc1c6", via="#9da2a9", pad="#b6a982", silk="#25282d",
    deco="#aab0b8", accent="#3c7fc4", heat="paint_white", heat2="alu", latch="white_plastic",
    shroud="white_plastic", plate_bg="#eceef0", plate_ink="#1b1e23", plate_acc="#3c7fc4")


class PremiumBoard(BB.Board):
    """mb_ridge_b5's layout with the premium look."""

    def dimm_slot(self, x, body, notch_y):
        super().dimm_slot(x, "white_plastic", notch_y)

    def pcie_slot(self, xa, xb, yc, armour):
        super().pcie_slot(xa, xb, yc, armour or (xb - xa) > 50.0)   # both full-length slots get the steel armour

    def vrm(self):
        cfg, k = self.cfg, self.k
        PT, MM = BB.PT, BB.MM
        # chokes: the B5's positions and markings
        uv, ctx = self.mark(7.6, 7.6, 16.0, "#2e2f33")
        with ctx as a:
            a.text("R22", 3.8, 4.4, 1.6, "#b8b8b8", font="arialbd")
            a.text("2346", 3.8, 2.4, 0.9, "#8a8a8a", font="arialbd")
        choke_side = self.marks.swatch("#2a2b2e")
        chokes = [(-6.0 + i * 9.5, 129.5) for i in range(6)] + [(72.0, 40.0 + i * 9.5) for i in range(9)]
        for n, (x, y) in enumerate(chokes):
            if y > 125.0:
                self.at(f"PL{n + 1}", x, y - 5.3, 0.9, font="narrowbd")
            else:
                self.at(f"PL{n + 1}", x - 5.2, y, 0.9, font="narrowbd", rot=90)
            self.bx(self.MT, x, y, PT, 7.6, 7.6, 5.4, bevel=0.35, uv=self.top_map(uv, x, y, PT + 5.4, 7.6, 7.6, rest=choke_side))
            for s in (-1, 1):
                self.ar(x + s * 2.6 - 1.2, y - 3.2, x + s * 2.6 + 1.2, y + 3.2, cfg["pad"], 0.35)
            self.occupy(x - 4.2, y - 4.2, x + 4.2, y + 4.2)
        heat, heat2 = cfg["heat"], cfg["heat2"]
        # ---- top heatsink: wider and taller than the B5's (x -15..49, up to z 34): a white finned block under a
        # stepped white cover, silver fin edges toward the socket, a silver accent and the logo plate
        t = dict(x0=-15.0, x1=49.0, y0=133.6, y1=150.8, z1=34.0)
        xm, ym = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2
        W, D = t["x1"] - t["x0"], t["y1"] - t["y0"]
        self.bx(heat, xm, ym, 3.6, W, D, 4.6, bevel=0.6)
        nf = int((W - 2) / 2.6)
        for i in range(nf):
            x = t["x0"] + 1.4 + i * (W - 2.8) / (nf - 1)
            self.bx(heat, x, ym + 1.0, 8.2, 1.0, D - 2.0, t["z1"] - 15.0)
            self.bx(heat2, x, t["y0"] + 1.2, 8.2, 1.0, 0.4, t["z1"] - 15.0)          # silver fin edges, socket side
        capz = t["z1"] - 7.0
        self.bx(heat, xm, ym + 1.2, capz, W + 0.4, D - 2.4, 3.6, bevel=0.6)
        BB._slope(k[heat], (xm, t["y0"] + 2.6, capz + 1.8), (xm, t["y0"] - 0.2, capz - 2.0), W + 0.4, 3.2)
        self.bx(heat, xm + 2.0, ym + 2.2, capz + 3.6, W - 6.0, D - 6.4, 3.4, bevel=0.8)  # the upper step
        BB._slope(k[heat2], (xm + 2.0, t["y0"] + 3.4, capz + 6.2), (xm + 2.0, t["y0"] + 1.6, capz + 3.8), W - 6.0, 0.6)
        uv, ctx = self.mark(40.0, 8.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text("RIDGE", 2.0, 4.0, 5.0, cfg["plate_ink"], font="agency", ax="LEFT")
            a.line([(20.0, 2.0), (38.0, 2.0)], 0.5, cfg["plate_acc"])
            a.text(cfg["model"].split()[0] + " ELITE POWER", 38.0, 5.0, 2.0, cfg["plate_acc"], font="agencyr", ax="RIGHT")
        pe = self.marks.swatch(cfg["plate_bg"])
        px, py_ = xm + 2.0, ym + 3.0
        self.bx(self.MT, px, py_, capz + 7.0, 40.0, 8.0, 0.5, bevel=0.15, uv=self.top_map(uv, px, py_, capz + 7.5, 40.0, 8.0, rest=pe))
        self.occupy(t["x0"], t["y0"], t["x1"], t["y1"])
        # ---- rear heatsink: longer and taller (y 26..131, up to z 37), its top level with the I/O cover so the two
        # read as one white block; fins along x under a cover with a chamfer toward the socket
        r = self.rear = dict(x0=77.4, x1=95.4, y0=26.0, y1=131.0, z1=37.0)
        xm, ym = (r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2
        W, D = r["x1"] - r["x0"], r["y1"] - r["y0"]
        self.bx(heat, xm, ym, 3.6, W, D, 4.6, bevel=0.6)
        nf = int((D - 2) / 2.6)
        for i in range(nf):
            y = r["y0"] + 1.4 + i * (D - 2.8) / (nf - 1)
            self.bx(heat, xm + 1.0, y, 8.2, W - 2.0, 1.0, r["z1"] - 15.0)
            self.bx(heat2, r["x0"] + 1.2, y, 8.2, 0.4, 1.0, r["z1"] - 15.0)
        capz = r["z1"] - 7.0
        self.bx(heat, xm + 1.2, ym, capz, W - 2.4, D + 0.4, 3.6, bevel=0.6)
        BB._slope_x(k[heat], (r["x0"] + 2.6, ym, capz + 1.8), (r["x0"] - 0.2, ym, capz - 2.0), D + 0.4, 3.2)
        self.bx(heat, xm + 2.2, ym, capz + 3.6, W - 6.4, D - 6.0, 3.4, bevel=0.8)
        BB._slope_x(k[heat2], (r["x0"] + 3.4, ym, capz + 6.2), (r["x0"] + 1.6, ym, capz + 3.8), D - 6.0, 0.6)
        # brushed silver inlay with grooves on the cover top
        self.bx(heat2, xm + 2.6, ym, capz + 7.0, W - 9.0, D - 14.0, 0.3)
        for j in range(6):
            self.bx("black_plastic", xm + 2.6, r["y0"] + 12.0 + j * 2.0, capz + 7.25, W - 10.0, 0.5, 0.1)
        self.occupy(r["x0"], r["y0"], r["x1"], r["y1"])
        # nickel heat pipe linking both, as on the B5
        pts = [(30.0, 140.0, 3.4), (46.0, 139.5, 3.4), (58.0, 134.6, 3.4), (70.5, 126.5, 3.4), (80.0, 119.0, 3.4), (86.0, 110.0, 3.4)]
        c.tube("heatpipe", [(p[0] * MM, p[1] * MM, p[2] * MM) for p in pts], 1.6 * MM, "nickel", self.root, verts=12)
        # solid polymer capacitors and the memory VRM, as on the B5
        for (x, y, rr, h) in [(74.5, 145.0, 3.15, 8.0), (74.5, 137.4, 3.15, 8.0), (-17.5, 129.0, 2.5, 6.0), (-17.5, 136.0, 2.5, 6.0),
                              (70.0, 33.5, 2.5, 6.0), (63.5, 21.0, 2.5, 6.0), (70.0, 21.0, 2.5, 6.0)]:
            self.solid_cap(x, y, rr, h)
        for y in (133.0, 123.0):
            self.small_choke(-70.0, y)
            self.mosfet(-81.0, y)
        self.solid_cap(-89.0, 132.0, 2.5, 6.0)
        self.solid_cap(-89.0, 124.0, 2.5, 6.0)

    def io_shroud(self):
        super().io_shroud()
        # the white cover gets a silver strip along its slanted wall and a silver end cap at the bottom
        y0, y1 = 22.0, 151.5
        self.bx("alu", 100.3, (y0 + y1) / 2, 30.4, 0.4, y1 - y0 - 8.0, 1.6)
        self.bx("alu", (99.8 + BB.IO_FACE - 1.7) / 2, y0 + 1.0, 4.0, BB.IO_FACE - 1.7 - 99.8, 2.2, 31.0)

    def m2(self):
        super().m2()
        # a second white M.2 heatsink (fixed, looks only) over the M2_2 slot, on posts like the first one
        PT, MM, k = BB.PT, BB.MM, self.k
        yc = BB.M2B_Y
        for px in (-20.0, 78.0):
            pp.cyl(k["steel"], (px * MM, yc * MM, (PT + (7.2 - PT) / 2) * MM), 2.6 * MM, (7.2 - PT) * MM, "z", 6)
        heat = self.cfg["heat"]
        self.bx(heat, 29.0, yc, 7.2, 106.0, 24.0, 2.4, bevel=0.8)
        for i in range(9):
            pp.box(k["alu"], ((-14.0 + i * 6.0) * MM, yc * MM, 9.8 * MM), (1.4 * MM, 22.0 * MM, 0.5 * MM), pp.rot("z", 28), 0.0002)
        for px in (-20.0, 78.0):
            pp.tube_ring(k["steel"], (px * MM, yc * MM, 9.65 * MM), 1.2 * MM, 2.2 * MM, 0.2 * MM, seg=16)
        uv, ctx = self.mark(30.0, 14.0, 20.0, self.cfg["plate_bg"])
        with ctx as a:
            a.text("M.2_2", 15.0, 8.6, 5.0, self.cfg["plate_ink"], font="agency")
            a.line([(3.0, 3.0), (27.0, 3.0)], 0.5, self.cfg["plate_acc"])
        pe = self.marks.swatch(self.cfg["plate_bg"])
        self.bx(self.MT, 62.0, yc, 9.6, 30.0, 14.0, 0.5, bevel=0.2, uv=self.top_map(uv, 62.0, yc, 10.1, 30.0, 14.0, rest=pe))
        self.occupy(-24.0, yc - 12.0, 82.0, yc + 12.0)


def build_mb_ridge_x5():
    bid = "mb_ridge_x5"
    b = PremiumBoard(bid)
    root = b.build()
    P.write_report(root, bid, "frame and layout: as mb_ridge_b5 (origin at the PCB centre, +z component side, +x rear I/O)")
    if PREVIEW[0]:
        pp.preview(root, bid, views=((15, 55), (-35, 40), (60, 35)), size=(1280, 960), dist=0.62, zup=True)
        pp.preview(root, bid, views=((-25, 50),), size=(1280, 960), dist=0.2, target=(0.03, 0.06, 0.01), start=3, zup=True)
        pp.preview(root, bid, views=((50, 30),), size=(1280, 960), dist=0.2, target=(0.1, 0.07, 0.015), start=4, zup=True)
        pp.preview(root, bid, views=((-60, 45),), size=(1280, 960), dist=0.2, target=(-0.08, -0.1, 0.005), start=5, zup=True)
        pp.preview(root, bid, views=((-110, 40),), size=(1280, 960), dist=0.16, target=(-0.07, 0.11, 0.008), start=6, zup=True)
        pp.preview(root, bid, views=((30, 40),), size=(1280, 960), dist=0.16, target=(0.03, -0.03, 0.006), start=7, zup=True)
        pp.preview(root, bid, views=((-20, 35),), size=(1280, 960), dist=0.14, target=(0.0, -0.14, 0.004), start=8, zup=True)
        pp.preview(root, bid, views=((-100, 20),), size=(1280, 960), dist=0.12, target=(-0.115, -0.07, 0.006), start=9, zup=True)
    else:
        pp.preview = lambda *a, **k: []
    # the I/O shield: the board's cut-outs in a bare (unpainted) steel plate, to go with the silver theme
    sroot = BB.build_shield(bid, types.SimpleNamespace(v5=False, shield_cuts=b.shield_cuts, shield_labels=b.shield_labels))
    P.write_report(sroot, "io_ridge_x5", "frame: as io_ridge_b5 (origin at the plate centre, board axes, outer face +x)")
    return root


JOBS = {
    "cpu_arc9": build_cpu_arc9,
    "gpu_rx77": build_gpu_rx77,
    "case_aero": build_case_aero,
    "mb_ridge_x5": build_mb_ridge_x5,
}


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
        P.PREVIEW[0] = False
    ids = [a for a in argv if not a.startswith("--")] or list(JOBS)
    t0 = time.time()
    for pid in ids:
        t = time.time()
        JOBS[pid]()
        print(f"BUILT {pid} in {time.time() - t:.1f}s")
    print(f"BUILD_PARTS_D done: {len(ids)} jobs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(c.args())
