"""
Server motherboards for catalogue 12 (built from build_cat_boards.py; new contracts, see docs/reports/cat_boards.md):

  mb_strata_spv   Strata single-socket board for Arc Epoch (socket SP-V): 12 DDR5 RDIMM slots, 3 x PCIe x16, an
                  OCP 3.0 SFF NIC slot, 2 x M.2, a BMC. SSI-EEB.
  mb_strata_l46   Strata dual-socket board for Tiron Platinum (socket L46): 16 DDR5 RDIMM slots, 4 x PCIe x16,
                  2 x M.2, a BMC. SSI-EEB.
Each with its I/O shield io_strata_spv / io_strata_l46 (the ATX I/O aperture, as on the desktop boards).

Frame (as the desktop boards, REALISM.md section 2): origin at the PCB centre, the PCB spans z 0..0.0016, +z is the
component side, +x the rear I/O edge, +y the edge that is the top in a tower. SSI-EEB: 0.3302 (x, 13") by 0.3048
(y, 12"). Airflow runs front (-x) to rear (+x), so the DIMM slots run along x.

The build_board helpers are reused by setting its module geometry (board size, holes, rear I/O face) for the
duration of a server build (Geom); everything is restored afterwards.
"""
import math
import random

import dct_common as c
import parts_c as P
import parts_pcb as pp
import build_board as BB
from mathutils import Vector

MM, PT = BB.MM, BB.PT
SBW, SBH = 330.2, 304.8
SHX, SHY = SBW / 2, SBH / 2
IO_FACE_S = SHX + 4.0           # as the ATX boards: the port faces 4 mm past the rear edge
SHIELD_X_S = SHX + 5.9
SEAT_Z = BB.SEAT_Z
IHS_H = 6.5                     # assumed contact-face-to-IHS-top height of the server CPUs (A_SOCKET_COOLER_n)

# SSI-EEB mounting holes used by these boards (board mm). The three rear holes keep the ATX positions relative to
# the rear edge (A, C, F), so a case or chassis with ATX standoffs at the rear lines up; the rest suit the layout.
HOLES_S = [(155.0, -135.9), (155.0, -11.4), (132.1, 146.05), (60.0, 146.05), (60.0, -11.4),
           (-155.0, -135.9), (-155.0, -11.4), (-155.0, 146.05)]
HOLE_IDS = ["A", "C", "F", "R1", "R2", "R3", "R4", "R5"]
DIMM_LEN = 139.6

BOARDS = {
    "mb_strata_spv": dict(
        sock="SP-V", mem="DDR5", model="SP-V 1S", chipset="", shield="io_strata_spv",
        mask="#0e3b2c", trace="#14523d", pour="#104533", via="#2a6b52", pad="#c4b07c", silk="#f0f0ea",
        deco="#1a5a44", accent="#f0f0ea", heat="alu", heat2="alu", latch="connector_black", shroud="black_plastic",
        plate_bg="#1b1d20", plate_ink="#e8e8e8", plate_acc="#4fa3d8", sockets=1),
    "mb_strata_l46": dict(
        sock="L46", mem="DDR5", model="L46 2S", chipset="", shield="io_strata_l46",
        mask="#0e3b2c", trace="#14523d", pour="#104533", via="#2a6b52", pad="#c4b07c", silk="#f0f0ea",
        deco="#1a5a44", accent="#f0f0ea", heat="alu", heat2="alu", latch="connector_black", shroud="black_plastic",
        plate_bg="#1b1d20", plate_ink="#e8e8e8", plate_acc="#4fa3d8", sockets=2),
}
BB.BOARDS.update(BOARDS)


class Geom:
    """Temporarily gives build_board the server board geometry (size, holes, socket, rear I/O face)."""
    KEYS = ("BW", "BH", "HX", "HY", "HOLES", "S", "IO_FACE", "SHIELD_X")

    def __init__(self, socket_xy):
        self.new = dict(BW=SBW, BH=SBH, HX=SHX, HY=SHY, HOLES=HOLES_S, S=socket_xy, IO_FACE=IO_FACE_S, SHIELD_X=SHIELD_X_S)

    def __enter__(self):
        self.old = {k: getattr(BB, k) for k in self.KEYS}
        for k, v in self.new.items():
            setattr(BB, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(BB, k, v)


class ServerBoard(BB.Board):
    def __init__(self, bid):
        super().__init__(bid)
        self.v5 = False
        self.n = self.cfg["sockets"]
        self.tkey = bid[3:]
        self.MT = "tex_" + self.tkey + "_mk"
        self.PCBT = "tex_" + self.tkey + "_pcb"
        self.rnd = random.Random(31 + self.n)
        if self.n == 1:
            self.sockets = [(-50.0, 10.0)]
            self.banks = [(-50.0, [75.0 + i * 7.6 for i in range(6)]), (-50.0, [-55.0 - i * 7.6 for i in range(6)])]
            self.pcie_ys = [-30.0, -30.0 - 20.32, -30.0 - 40.64]
        else:
            self.sockets = [(-60.0, 76.0), (-60.0, -76.0)]
            b = []
            for sx, sy in self.sockets:
                b.append((sx, [sy + 48.5 + i * 7.2 for i in range(4)]))
                b.append((sx, [sy - 48.5 - i * 7.2 for i in range(4)]))
            self.banks = b
            self.pcie_ys = [-30.0 - 20.32 * i for i in range(4)]

    # ================================================================ build
    def build(self):
        c.reset()
        with Geom(self.sockets[0]):
            self.pcb = pp.Art(SBW, SBH, 2560, 2368, bg=self.cfg["mask"])
            self.marks = pp.Atlas(2048, 4096 if self.n == 2 else 2048, bg="#101010")
            self.root = c.root(self.bid)
            self.pcb_swatches()
            self.s_holes()
            for i, (sx, sy) in enumerate(self.sockets):
                (self.sock_spv if self.n == 1 else self.sock_l46)(i, sx, sy)
            self.s_vrm()
            self.s_dimms()
            self.s_pcie()
            if self.n == 1:
                self.s_ocp()
            self.s_m2()
            self.s_bmc()
            self.rear_io()
            self.s_power()
            self.s_headers()
            self.s_sata()
            self.s_misc()
            self.s_passives()
            self.s_traces()
            self.s_silk()
            self.pcb_mesh()
            self.pcb.render(pp.tex_path(self.tkey + "_pcb"))
            self.marks.render(pp.tex_path(self.tkey + "_mk"))
            pp.PREVIEW_TEX[self.tkey + "_pcb"] = (0.0, 0.5)
            pp.PREVIEW_TEX[self.tkey + "_mk"] = (0.0, 0.42)
            self.k.finish(self.root)
            for g, an, base in self.moving:
                g.obj(base, self.anchors[an])
            self.s_hits()
            c.join_by_tag(self.root, "mb")
            c.export(self.root, self.bid)
            pp.report(self.root)
        return self.root

    # ---------------------------------------------------------------- holes
    def s_holes(self):
        for i, (x, y) in enumerate(HOLES_S):
            self.aring(x, y, BB.HOLE_R, 3.8, self.cfg["pad"], z=0.4)
            for k in range(8):
                a = math.radians(22.5 + 45 * k)
                self.ac(x + math.cos(a) * 3.0, y + math.sin(a) * 3.0, 0.32, self.cfg["mask"], z=0.45, seg=8)
            self.occupy(x - 4.6, y - 4.6, x + 4.6, y + 4.6, 0)
            self.anchor(f"A_HOLE_{i}", (x, y, 0.0), (8.0, 8.0, 3.0), forward=(0, 0, -1), up=(0, 1, 0),
                        meta=f"eeb={HOLE_IDS[i]},d=0.00396")
            self.anchor(f"A_SCREW_PH2_{i}", (x, y, PT), (7.0, 7.0, 6.0), meta=f"hole=A_HOLE_{i},m3=1")

    # ---------------------------------------------------------------- sockets
    def pin_field(self, w, h, pitch, bg="#0d0d0e"):
        uv, ctx = self.mark(w, h, 12.0, bg)
        with ctx as a:
            rows = int((h - 2.0) / (pitch * 0.866))
            for r in range(rows):
                yy = 1.0 + r * pitch * 0.866
                xx = 1.0 + (pitch * 0.5 if r % 2 else 0.0)
                while xx < w - 1.0:
                    a.circle(xx, yy, 0.26, "#c7a148", z=0.2, seg=6)
                    xx += pitch
        return uv

    def housing(self, sx, sy, hw, hh, cw, ch, pitch):
        uv = self.pin_field(cw * 2, ch * 2, pitch)
        black = self.marks.swatch("#101012")
        self.bx(self.MT, sx, sy, PT, hw * 2, hh * 2, 4.0 - PT, uv=self.top_map(uv, sx, sy, 4.0, cw * 2, ch * 2, rest=black))
        out = pp.rounded_rect(sx * MM, sy * MM, hw * 2 * MM, hh * 2 * MM, 0.6 * MM, 2)
        inn = list(reversed(pp.rounded_rect(sx * MM, sy * MM, cw * 2 * MM, ch * 2 * MM, 0.3 * MM, 2)))
        pp.prism(self.k["connector_black"], [out, inn], 4.0 * MM, 5.4 * MM)
        # pin-1 triangle (+x, -y corner) and alignment keys
        tx, ty = sx + (hw + cw) / 2, sy - (hh + ch) / 2
        g = self.k["white_plastic"]
        tri = [Vector((tx * MM, ty * MM, 5.42 * MM)), Vector(((tx - 1.5) * MM, ty * MM, 5.42 * MM)), Vector((tx * MM, (ty + 1.5) * MM, 5.42 * MM)),
               Vector((tx * MM, ty * MM, 5.4 * MM)), Vector(((tx - 1.5) * MM, ty * MM, 5.4 * MM)), Vector((tx * MM, (ty + 1.5) * MM, 5.4 * MM))]
        g.add(tri, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
        for kx in (-1, 1):
            self.bx("connector_black", sx + kx * (cw - 0.5), sy + ch * 0.5, 4.0, 1.0, 2.0, 1.4)
        return (tx + 0.4, ty - 0.4, 5.4)

    def sock_spv(self, i, sx, sy):
        """SP-V (SP5-style): an LGA housing in a steel bolster, a hinged rail frame the CPU's orange carrier slides
        into, a hinged force frame held by three captive Torx screws (tightened 1-2-3), a PnP cap, and four heatsink
        standoffs."""
        k = self.k
        hw, hh, cw, ch = 41.0, 43.0, 37.5, 39.0
        mark = self.housing(sx, sy, hw, hh, cw, ch, 0.94)
        self.occupy(sx - 62, sy - 58, sx + 62, sy + 58)
        # bolster plate
        out = pp.rounded_rect(sx * MM, sy * MM, 104 * MM, 114 * MM, 3.0 * MM, 3)
        win = list(reversed(pp.rounded_rect(sx * MM, sy * MM, (hw * 2 + 1) * MM, (hh * 2 + 1) * MM, 1.0 * MM, 3)))
        pp.prism(k["steel_dark"], [out, win], PT * MM, 2.6 * MM)
        hx = sx - 49.0      # both frames hinge at the -x end
        for hy in (-30.0, 30.0):
            pp.cyl(k["steel"], (hx * MM, (sy + hy) * MM, 4.2 * MM), 2.0 * MM, 10.0 * MM, axis="y", seg=12)
            self.bx("steel_dark", hx, sy + hy, PT, 4.0, 12.0, 1.8)
        # heatsink standoffs (hex posts) and their silkscreen numbers
        for n, (ex, ey) in enumerate(((-56, -40), (56, -40), (56, 40), (-56, 40))):
            pp.cyl(k["steel"], ((sx + ex) * MM, (sy + ey) * MM, (PT + 4.4) * MM), 3.2 * MM, 8.8 * MM, "z", 6)
            pp.cyl(k["steel_dark"], ((sx + ex) * MM, (sy + ey) * MM, (PT + 8.9) * MM), 1.6 * MM, 0.2 * MM, "z", 12)
            self.at(str(n + 1), sx + ex + (5.5 if ex > 0 else -5.5), sy + ey, 2.0, font="arialbd")
            self.occupy(sx + ex - 4, sy + ey - 4, sx + ex + 4, sy + ey + 4)
        # ---- anchors
        sfx = f"_{i}"
        self.anchor("A_SOCKET_CPU" + sfx, (sx, sy, SEAT_Z), (72.0, 75.0, 6.0), meta="socket=SP-V,pin1=+x-y,carrier=A_RAIL_CPU" + sfx)
        self.anchor("A_MARK_SOCKET" + sfx, mark, (3.0, 3.0, 2.0), meta="pin1=+x-y")
        self.anchor("A_SOCKET_COOLER" + sfx, (sx, sy, SEAT_Z + IHS_H), (124.0, 92.0, 60.0),
                    meta="standoffs=0.112x0.080,screws=4,t20=1,order=1-2-3-4")
        self.anchor("A_RAIL_CPU" + sfx, (hx, sy, 4.2), (6.0, 84.0, 8.0),
                    meta="hinge=y,open=-75,carrier_slide=+x,carrier_stop=" + f"{(sx + 36.0) * MM:.4f}")
        self.anchor("A_PLATE_CPU" + sfx, (hx, sy, 4.2), (100.0, 104.0, 6.0),
                    meta="hinge=y,open=-110,screws=A_SCREW_TORX_0..2,after=A_RAIL_CPU" + sfx)
        self.anchor("A_COVER_CPU" + sfx, (sx, sy, 10.6), (72.0, 76.0, 4.0), meta="pnp_cap=1,remove=+z")
        plate = self.anchors["A_PLATE_CPU" + sfx]
        # ---- rail frame (moving piece): two side rails with lips, a front cross bar
        gr = self.piece("steel", "A_RAIL_CPU" + sfx, "rail")
        for s in (-1, 1):
            self.bx(None, sx - 2.0, sy + s * 39.5, 5.0, 92.0, 3.0, 1.2, bevel=0.3, g=gr)
            self.bx(None, sx - 2.0, sy + s * 37.8, 6.2, 88.0, 0.6, 1.4, g=gr)
        self.bx(None, sx + 43.5, sy, 5.0, 3.0, 82.0, 1.2, bevel=0.3, g=gr)
        self.bx(None, hx + 2.5, sy, 4.2, 4.0, 76.0, 1.0, g=gr)
        # ---- force frame (moving piece): a stiff plate with a window, side flanges, the screw tabs
        gp = self.piece("steel", "A_PLATE_CPU" + sfx, "plate")
        z0p, z1p = 7.6, 8.4
        out = pp.rounded_rect((sx + 1.0) * MM, sy * MM, 98 * MM, 100 * MM, 3.0 * MM, 3)
        win = list(reversed(pp.rounded_rect(sx * MM, sy * MM, 70 * MM, 74 * MM, 2.0 * MM, 3)))
        pp.prism(gp, [out, win], z0p * MM, z1p * MM)
        for s in (-1, 1):
            self.bx(None, sx + 1.0, sy + s * 49.6, z0p - 1.6, 88.0, 0.8, 1.6, g=gp)
        BB._slope_x(gp, (hx + 3.0, sy, z0p + 0.4), (hx, sy, 4.2), 60.0, 0.8)
        screws = [(sx + 50.0, sy), (sx - 46.0, sy - 46.0), (sx - 46.0, sy + 46.0)]
        for n, (px, py_) in enumerate(screws):
            self.bx(None, px, py_, z0p, 9.0, 9.0, z1p - z0p, bevel=1.5, g=gp)
            gs = self.piece("steel_dark", "A_PLATE_CPU" + sfx, f"screw{n}")
            pp.cyl(gs, (px * MM, py_ * MM, (z1p + 1.0) * MM), 2.8 * MM, 2.0 * MM, "z", 16, 0.0003)
            self.anchor(f"A_SCREW_TORX_{n}", (px, py_, z1p + 2.0), (6.0, 6.0, 5.0), parent=plate,
                        meta=f"seq={n + 1},t20=1,torque=1.6Nm")
            self.cy("steel", px, py_, PT, 2.6, z0p - PT, 12)
            self.at(str(n + 1), px + (0 if n == 0 else 6.5), py_ + (7.0 if n == 0 else 0), 2.2, font="arialbd")
        # print on the force frame
        uv, ctx = self.mark(30.0, 6.0, 16.0, "#a9adb2")
        with ctx as a:
            a.text("TIGHTEN 1-2-3  T20  1.6 N·m", 15.0, 3.0, 2.0, "#26282b", font="arialbd", fit=28.0)
        self.bx(self.MT, sx + 1.0, sy - 43.5, z1p, 30.0, 6.0, 0.05,
                uv=self.top_map(uv, sx + 1.0, sy - 43.5, z1p + 0.05, 30.0, 6.0, rest=self.marks.swatch("#a9adb2")),
                g=self.piece(self.MT, "A_PLATE_CPU" + sfx, "label"))
        # ---- PnP cap (moving piece)
        gc = self.piece(self.MT, "A_COVER_CPU" + sfx, "cap")
        uv, ctx = self.mark(68.0, 72.0, 8.0, "#151517")
        with ctx as a:
            a.text("SOCKET SP-V", 34.0, 58.0, 4.0, "#9a9a9a", font="arialbd")
            a.text("DO NOT REMOVE", 34.0, 42.0, 5.0, "#e4e4e4", font="arialbd")
            a.text("UNTIL CPU IS INSTALLED", 34.0, 34.0, 3.4, "#e4e4e4", font="arialbd", fit=60.0)
            a.poly([(28.0, 16.0), (40.0, 16.0), (34.0, 24.0)], "#e4e4e4", z=0.3)
        blk = self.marks.swatch("#151517")
        self.bx(self.MT, sx, sy, z1p, 74.0, 78.0, 0.8, bevel=0.3, uv=blk, g=gc)
        self.bx(self.MT, sx, sy, z1p + 0.8, 68.0, 72.0, 1.4, bevel=0.5, uv=self.top_map(uv, sx, sy, z1p + 2.2, 68.0, 72.0, rest=blk), g=gc)

    def sock_l46(self, i, sx, sy):
        """L46 (LGA4677-style): a long LGA housing in a bolster with four threaded studs; the CPU comes clipped to its
        cooler (the processor-heatsink module) and lands on the studs, held by four T30 nuts (tightened 1-2-3-4)."""
        k = self.k
        hw, hh, cw, ch = 57.0, 34.0, 54.0, 31.5
        mark = self.housing(sx, sy, hw, hh, cw, ch, 0.9)
        self.occupy(sx - 68, sy - 44, sx + 68, sy + 44)
        out = pp.rounded_rect(sx * MM, sy * MM, 132 * MM, 86 * MM, 3.0 * MM, 3)
        win = list(reversed(pp.rounded_rect(sx * MM, sy * MM, (hw * 2 + 1) * MM, (hh * 2 + 1) * MM, 1.0 * MM, 3)))
        pp.prism(k["steel_dark"], [out, win], PT * MM, 2.8 * MM)
        # alignment posts for the carrier clip
        for s in (-1, 1):
            self.cy("black_plastic", sx + s * 60.5, sy + s * 10.0, 2.8, 1.4, 3.0, 12)
        studs = [(-58.0, -36.0), (58.0, 36.0), (58.0, -36.0), (-58.0, 36.0)]
        for n, (ex, ey) in enumerate(studs):
            pp.cyl(k["steel"], ((sx + ex) * MM, (sy + ey) * MM, (PT + 6.5) * MM), 2.0 * MM, 13.0 * MM, "z", 12)
            pp.cyl(k["steel_dark"], ((sx + ex) * MM, (sy + ey) * MM, (PT + 1.2) * MM), 3.6 * MM, 2.0 * MM, "z", 6)
        sfx = f"_{i}"
        self.anchor("A_SOCKET_CPU" + sfx, (sx, sy, SEAT_Z), (105.0, 61.0, 6.0), meta="socket=L46,pin1=+x-y,phm=1")
        self.anchor("A_MARK_SOCKET" + sfx, mark, (3.0, 3.0, 2.0), meta="pin1=+x-y")
        self.anchor("A_SOCKET_COOLER" + sfx, (sx, sy, SEAT_Z + IHS_H), (140.0, 90.0, 60.0),
                           meta="studs=0.116x0.072,nuts=4,t30=1,order=1-2-3-4,phm=1")
        for n, (ex, ey) in enumerate(studs):
            self.anchor(f"A_SCREW_TORX_{i * 4 + n}", (sx + ex, sy + ey, PT + 13.0), (8.0, 8.0, 6.0),
                        meta=f"stud=1,seq={n + 1},t30=1,torque=0.9Nm,cooler=A_SOCKET_COOLER{sfx}")
            self.at(str(n + 1), sx + ex + (5.0 if ex > 0 else -5.0), sy + ey + (4.5 if ey > 0 else -4.5), 2.0, font="arialbd")
        self.anchor("A_COVER_CPU" + sfx, (sx, sy, 7.6), (110.0, 66.0, 4.0), meta="dust_cover=1,remove=+z")
        gc = self.piece(self.MT, "A_COVER_CPU" + sfx, "cap")
        uv, ctx = self.mark(108.0, 64.0, 7.0, "#151517")
        with ctx as a:
            a.text("SOCKET L46", 54.0, 50.0, 4.0, "#9a9a9a", font="arialbd")
            a.text("DO NOT REMOVE UNTIL CPU IS INSTALLED", 54.0, 34.0, 4.0, "#e4e4e4", font="arialbd", fit=96.0)
            a.poly([(48.0, 12.0), (60.0, 12.0), (54.0, 20.0)], "#e4e4e4", z=0.3)
        blk = self.marks.swatch("#151517")
        self.bx(self.MT, sx, sy, 5.4, 112.0, 68.0, 0.8, bevel=0.3, uv=blk, g=gc)
        self.bx(self.MT, sx, sy, 6.2, 106.0, 62.0, 1.4, bevel=0.5, uv=self.top_map(uv, sx, sy, 7.6, 108.0, 64.0, rest=blk), g=gc)

    # ---------------------------------------------------------------- VRM (server boards: chokes and power stages
    # in front of and behind each socket, under low aluminium heatsinks in the airflow)
    def s_vrm(self):
        uv, ctx = self.mark(7.6, 7.6, 16.0, "#2e2f33")
        with ctx as a:
            a.text("R15", 3.8, 4.4, 1.6, "#b8b8b8", font="arialbd")
            a.text("2412", 3.8, 2.4, 0.9, "#8a8a8a", font="arialbd")
        side = self.marks.swatch("#2a2b2e")
        for (sx, sy) in self.sockets:
            if self.n == 1:
                cols = [(sx - 62.0, -1), (sx + 62.0, 1)]
                ys = [sy - 40.0 + j * 8.8 for j in range(10)]
            else:
                cols = [(sx - 73.0, -1), (sx + 73.0, 1)]
                ys = [sy - 30.0 + j * 8.6 for j in range(8)]
            for (x, side_) in cols:
                for y in ys:
                    self.bx(self.MT, x, y, PT, 7.6, 7.6, 5.4, bevel=0.35, uv=self.top_map(uv, x, y, PT + 5.4, 7.6, 7.6, rest=side))
                    self.occupy(x - 4.2, y - 4.2, x + 4.2, y + 4.2)
                    mx = x + side_ * 7.2
                    self.mosfet(mx, y, ang=90)
                # low heatsink over the power stages
                hx = x + side_ * 7.2
                y0, y1 = ys[0] - 4.0, ys[-1] + 4.0
                self.bx("alu", hx, (y0 + y1) / 2, PT + 1.2, 6.4, y1 - y0, 2.0, bevel=0.3)
                for f in range(4):
                    self.bx("alu", hx - 2.4 + f * 1.6, (y0 + y1) / 2, PT + 3.2, 0.7, y1 - y0, 8.0)
                self.occupy(hx - 3.4, y0, hx + 3.4, y1)
                for y in (ys[0] - 8.0, ys[-1] + 8.0):
                    self.solid_cap(x, y, 2.5, 6.0)

    # ---------------------------------------------------------------- DIMMs (along x)
    def s_dimm_slot(self, cx, y, body, notch):
        k = self.k
        x0, x1 = cx - DIMM_LEN / 2, cx + DIMM_LEN / 2
        chh, top, floor = 0.85, PT + 7.6, 3.0
        for s in (-1, 1):
            self.bx(body, cx, y + s * (chh + 2.15 / 2), PT, x1 - x0, 2.15, top - PT, bevel=0.25)
            for j in range(11):
                self.bx(body, x0 + 8.0 + j * 12.4, y + s * (chh + 2.15 + 0.15), PT, 1.2, 0.3, top - PT - 1.0)
        self.bx(body, cx, y, PT, x1 - x0, chh * 2, floor - PT)
        for e in (-1, 1):
            self.bx(body, cx + e * (67.0 + 1.4), y, PT, 2.8, chh * 2, top - PT)
        self.bx(body, cx + notch, y, floor, 1.0, chh * 2, 3.3)
        xx = -66.675 + 3.0
        while xx < 66.675 - 3.0:
            if abs(xx - notch) > 1.25:
                for s in (-1, 1):
                    pp.quad(k["gold"], ((cx + xx) * MM, (y + s * (chh - 0.01)) * MM, 4.9 * MM), (0.00038, 0.0032), normal=(0, -s, 0), up=(0, 0, 1))
            xx += 1.7

    def s_latch(self, g, xx, y, sgn):
        z0 = PT + 0.6
        self.bx(None, xx, y, z0, 4.0, 5.8, 7.6, bevel=0.4, g=g)
        self.bx(None, xx - sgn * 0.3, y, z0 + 7.6, 2.6, 4.6, 8.4, bevel=0.3, g=g)
        self.bx(None, xx + sgn * 4.1, y, PT + 14.6, 4.4, 2.4, 2.4, bevel=0.3, g=g)
        BB._slope_x(g, (xx - sgn * 1.4, y, z0 + 15.6), (xx - sgn * 4.4, y, z0 + 17.4), 5.6, 1.3)

    def s_dimms(self):
        notch = BB.NOTCH["DDR5"]
        idx = 0
        letters = "ABCDEFGHIJKL"
        for b, (cx, ys) in enumerate(self.banks):
            cpu = b // 2
            for j, y in enumerate(ys):
                body = "connector_black" if j % 2 == 0 else "grey_plastic"
                self.s_dimm_slot(cx, y, body, notch)
                ch = (b % 2) * len(ys) + j
                name = f"P{cpu}_DIMM{letters[ch]}1"
                self.anchor(f"A_SOCKET_RAM_{idx}", (cx, y, 3.0), (139.6, 7.6, 14.0), up=(1, 0, 0),
                            meta=f"notch={notch * MM:.4f},slot={name},mem=DDR5,rdimm=1,cpu={cpu},latch=both,pref=1")
                x0, x1 = cx - DIMM_LEN / 2, cx + DIMM_LEN / 2
                for e, (xx, sgn) in enumerate(((x0 - 2.1, 1), (x1 + 2.1, -1))):
                    an = f"A_LATCH_RAM_{idx}_{e}"
                    self.anchor(an, (xx + sgn * 1.2, y, PT + 1.2), (6.0, 6.4, 18.0), up=(1, 0, 0),
                                meta=f"hinge=y,open={-35 if e == 0 else 35}")
                    g = self.piece(self.cfg["latch"], an, "latch")
                    self.s_latch(g, xx, y, sgn)
                self.occupy(x0 - 4.5, y - 3.2, x1 + 4.5, y + 3.2)
                self.at(name, x0 - 12.0, y, 1.0, font="narrowbd")
                idx += 1
            yy = ys[-1] + (5.2 if b % 2 == 0 else -5.2)
            self.at(f"CPU{cpu}  DDR5 RDIMM  " + ("A-" if b % 2 == 0 else "") + ("F" if self.n == 1 else "D"), cx + 30.0, yy, 1.6)

    # ---------------------------------------------------------------- PCIe and OCP
    def s_pcie(self):
        x_anchor = SHX - 92.0       # as the ATX boards: the card origin 92 mm in front of the rear edge
        xa, xb = x_anchor - 44.5, x_anchor + 44.5
        for i, y in enumerate(self.pcie_ys):
            self.pcie_slot(xa, xb, y, armour=(i == 0))
            self.anchor(f"A_SOCKET_PCIE16_{i}", (x_anchor, y + 2.3, PT + 10.5), (89.0, 9.0, 14.0),
                        meta=f"lanes=16,card_origin=1,slot=SLOT{i + 1},cpu={0 if self.n == 1 or i < 2 else 1}")
            an = f"A_LATCH_PCIE_{i}"
            self.anchor(an, (xa - 5.0, y, PT + 0.8), (6.0, 7.5, 12.0), meta="hinge=y,open=-25")
            g = self.piece("grey_plastic", an, "latch")
            self.bx(None, xa - 3.1, y, PT + 0.4, 5.6, 7.2, 9.0, bevel=0.4, g=g)
            BB._slope_x(g, (xa - 4.2, y, PT + 9.2), (xa - 7.6, y, PT + 12.0), 7.2, 1.4)
            self.bx(None, xa - 1.0, y, PT + 9.0, 1.4, 4.0, 2.4, bevel=0.2, g=g)
            self.at(f"SLOT{i + 1} PCIE5 X16" + (f" (CPU{0 if self.n == 1 or i < 2 else 1})" if self.n == 2 else ""), xa + 2.0, y - 6.4, 1.5,
                    font="arialbd", ax="LEFT")

    def s_ocp(self):
        """OCP 3.0 SFF (4C+) connector, lying flat with its mouth toward the rear; the NIC slides in from the rear
        over the bay marked on the PCB."""
        cx, cy_, L = 52.0, -112.0, 58.0
        self.bx("connector_black", cx - 3.0, cy_, PT, 8.0, L, 3.0, bevel=0.2)
        self.bx("connector_black", cx - 3.0, cy_, PT + 6.4, 8.0, L, 1.6, bevel=0.2)
        for s in (-1, 1):
            self.bx("connector_black", cx - 3.0, cy_ + s * (L / 2 - 1.0), PT + 3.0, 8.0, 2.0, 3.4)
        self.bx("black_plastic", cx - 3.4, cy_, PT + 3.0, 6.0, L - 4.0, 3.4)
        for j in range(40):
            yy = cy_ - L / 2 + 4.0 + j * (L - 8.0) / 39
            for z in (PT + 3.2, PT + 6.2):
                pp.quad(self.k["gold"], ((cx - 1.0) * MM, yy * MM, z * MM), (0.0016, 0.0005), normal=(0, 0, 1 if z < PT + 4 else -1), up=(1, 0, 0))
        # card guides on the PCB edges of the bay (steel rails) and the bay outline
        for s in (-1, 1):
            self.bx("steel", (cx + SHX) / 2 + 3.0, cy_ + s * 35.0, PT, SHX - cx - 6.0, 2.0, 5.0)
        self.aframe(cx + 1.0, cy_ - 34.0, SHX - 1.0, cy_ + 34.0, 0.3)
        self.at("OCP 3.0 SFF  NIC BAY", (cx + SHX) / 2, cy_ + 6.0, 2.4)
        self.at("KEEP OUT", (cx + SHX) / 2, cy_ - 2.0, 1.8)
        self.occupy(cx - 7.5, cy_ - 37, SHX, cy_ + 37)
        self.anchor("A_SOCKET_OCP_0", (cx + 1.0, cy_, PT + 4.8), (12.0, L + 2.0, 8.0), forward=(1, 0, 0), up=(0, 0, 1),
                    meta="ocp=3.0,form=sff,lanes=16,pins=168,card_origin=1,insert=-x,depth=0.0050")

    # ---------------------------------------------------------------- M.2 (two 2280/22110 slots, no heatsink)
    def s_m2(self):
        for i, yc in enumerate((128.0, 104.0)):
            cx = 44.0
            self.bx("connector_black", cx - 0.6, yc, PT, 5.2, 22.4, BB.M2_Z - PT - 0.1)
            self.bx("connector_black", cx - 0.6, yc, BB.M2_Z + 0.9, 5.2, 22.4, 1.4, bevel=0.2)
            self.bx("connector_black", cx - 2.2, yc, BB.M2_Z - 0.1, 2.0, 22.4, 1.0)
            self.bx("black_plastic", cx + 0.6, yc, BB.M2_Z - 0.1, 2.4, 21.6, 1.0)
            self.bx("connector_black", cx + 0.4, yc + BB.MKEY_Y, BB.M2_Z - 0.1, 2.6, 1.0, 1.0)
            for s in (-1, 1):
                self.bx("steel", cx - 0.4, yc + s * 11.8, PT, 3.6, 1.0, 2.4)
            sxp = cx + 79.6
            pp.cyl(self.k["steel"], (sxp * MM, yc * MM, (PT + (BB.M2_Z - PT) / 2) * MM), 2.6 * MM, (BB.M2_Z - PT) * MM, "z", 6)
            for d, lab in ((cx + 79.6, "2280"), (cx + 59.6, "2260"), (cx + 109.6 - 8.0, "22110")):
                self.aring(d, yc, 1.4, 2.6, self.cfg["pad"], z=0.4)
                self.at(lab, d, yc - 4.4, 1.0, font="narrowbd")
            self.aframe(cx - 3.6, yc - 11.6, cx + 2.2, yc + 11.6, 0.15)
            self.at(f"M2_{i + 1}", cx + 8.0, yc + 8.6, 1.6, font="arialbd")
            self.occupy(cx - 4, yc - 12.5, cx + 3, yc + 12.5)
            self.occupy(sxp - 3, yc - 3, sxp + 3, yc + 3)
            self.anchor(f"A_SOCKET_M2_{i}", (cx + 39.6, yc, BB.M2_Z), (80.0, 22.0, 4.0),
                        meta=f"type=2280,key=M,keyy={BB.MKEY_Y * MM:.4f},insert_angle=20,alt=22110")
            self.anchor(f"A_STANDOFF_M2_{i}", (sxp, yc, BB.M2_Z), (5.0, 5.0, 3.0), meta="screw=ph0")

    # ---------------------------------------------------------------- BMC
    def s_bmc(self):
        x, y = 100.0, 52.0
        self.chip(x, y, 24.0, 24.0, 1.6, ["STR2600-A3", "2419A1B", "TAIWAN"], logo="STRATA BMC", ref="U70")
        self.chip(x, y + 20.0, 12.0, 8.0, 1.0, ["D4 1GB", "MT40A"], ref="U71")
        self.chip(x - 20.0, y, 6.0, 5.0, 1.2, ["25Q512", "BMC"], leads=(4, 1.27, 2), ref="U72")
        self.chip(x + 22.0, y - 4.0, 7.0, 7.0, 0.9, ["EL8211", "PHY"], ref="U73")
        self.at("BMC", x, y - 16.0, 2.0)
        lx, ly = x + 18.0, y + 14.0
        self.anchor("A_LED_BMC_0", (lx, ly, PT + 0.8), (4.0, 3.0, 2.0), meta="colour=green,heartbeat=1")
        g = self.piece("led_green", "A_LED_BMC_0", "led")
        self.bx(None, lx, ly, PT, 2.0, 1.25, 0.8, bevel=0.15, g=g)
        self.at("BMC_HB", lx + 2.0, ly + 2.6, 1.0, font="narrowbd")

    # ---------------------------------------------------------------- rear I/O (server: BMC LAN + 2 USB, VGA,
    # 2 x 10 GbE, UID button with its LED)
    def io_blocks(self):
        return [
            ("uid", 145.0, None, ["A_BUTTON_UID_0"], "UID"),
            ("lan", 124.0, None, ["A_PORT_USBA_0", "A_PORT_USBA_1", "A_PORT_ETH_0"], "BMC"),
            ("vga", 98.0, None, ["A_PORT_VGA_0"], "VGA"),
            ("rj2", 70.0, None, ["A_PORT_ETH_1", "A_PORT_ETH_2"], "10GbE"),
        ]

    def io_uid(self, yc, anchors):
        w, h = 10.0, 12.0
        z0 = PT
        bz = z0 + 6.0
        hole = list(reversed(pp.circle_pts(yc, bz, 3.0, 20)))
        self.port_front("steel", yc, z0, w, h, [hole], 3.0)
        self.io_body("connector_black", yc, z0, w, h, IO_FACE_S - 9.0, IO_FACE_S - 3.0)
        pp.cyl(self.k["led_blue"], ((IO_FACE_S - 0.8) * MM, yc * MM, bz * MM), 2.6 * MM, 2.4 * MM, axis="x", seg=20, bevel=0.0004)
        self.io_anchor(anchors[0], yc, bz, 6.0, 6.0, 1.5, "button=uid,led=blue,press=-x")
        self.shield_cuts.append(("circle", pp.circle_pts(yc, bz, 3.6, 20)))

    def io_vga(self, yc, anchors):
        w, h = 31.0, 12.6
        z0 = PT
        zc = z0 + h / 2
        d = [(yc - 8.3, zc + 3.1), (yc + 8.3, zc + 3.1), (yc + 7.2, zc - 3.1), (yc - 7.2, zc - 3.1)]
        self.port_front("steel", yc, z0, w, h, [d], 6.0)
        self.io_body("connector_black", yc, z0, w - 6, h, IO_FACE_S - 14.0, IO_FACE_S - 6.0)
        self.bx("connector_black", IO_FACE_S - 3.0, yc, zc - 2.6, 5.0, 15.0, 5.2)
        for r, n in ((1.75, 5), (0.0, 5), (-1.75, 5)):
            for j in range(n):
                yy = yc - 4.6 + j * 2.3 + (1.15 if r == 0.0 else 0.0) * 0
                pp.cyl(self.k["gold"], ((IO_FACE_S + 0.05) * MM, yy * MM, (zc + r) * MM), 0.35 * MM, 0.1 * MM, axis="x", seg=6)
        for s in (-1, 1):
            pp.cyl(self.k["steel"], ((IO_FACE_S + 1.5) * MM, (yc + s * 12.5) * MM, zc * MM), 2.4 * MM, 3.0 * MM, axis="x", seg=6)
            self.shield_cuts.append(("circle", pp.circle_pts(yc + s * 12.5, zc, 3.0, 16)))
        self.io_anchor(anchors[0], yc, zc, 17.0, 7.0, 6.0, "vga=1,screws=2")
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, zc, 19.0, 8.6, 1.2, 2)))

    def io_rj2(self, yc, anchors):
        w, h = 16.0, 13.6
        for i in range(2):
            z0 = PT + i * (h + 0.4)
            zc = z0 + h / 2 - 0.4
            op = [(yc - 5.85, zc - 2.0), (yc - 3.0, zc - 2.0), (yc - 3.0, zc - 4.1), (yc + 3.0, zc - 4.1), (yc + 3.0, zc - 2.0),
                  (yc + 5.85, zc - 2.0), (yc + 5.85, zc + 4.4), (yc - 5.85, zc + 4.4)]
            self.port_front("connector_black", yc, z0, w, h, [op], 12.0)
            self.io_body("steel", yc, z0, w + 0.6, h + 0.3, IO_FACE_S - 21.0, IO_FACE_S - 12.0)
            for s in (-1, 1):
                self.bx("steel", IO_FACE_S - 6.5, yc + s * (w / 2 + 0.15), z0, 13.0, 0.3, h)
            for j in range(8):
                yy = yc - 3.57 + j * 1.02
                BB._slope_x(self.k["gold"], (IO_FACE_S - 9.0, yy, zc + 4.2), (IO_FACE_S - 4.0, yy, zc + 2.4), 0.4, 0.25)
            for s, tag in ((-1, "led_green"), (1, "led_yellow")):
                self.bx(tag, IO_FACE_S + 0.05, yc + s * 5.9, z0 + h - 2.4, 0.2, 2.6, 1.6)
            self.io_anchor(anchors[i], yc, zc + 0.6, 11.7, 8.5, 12.0, f"rj45=1,latch=-z,speed=10g,port=LAN{i + 1}")
        self.bx("steel", IO_FACE_S - 6.5, yc, PT + 2 * h + 0.4, 13.0, w + 0.6, 0.3)
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, PT + h + 0.2, w + 1.2, 2 * h + 1.6, 0.8, 2)))

    def io_shroud(self):
        pass

    # ---------------------------------------------------------------- power and headers
    def s_power(self):
        self.minifit(-158.0, 60.0, 12, 2, "y", latch_side=1, name="A_PORT_ATX24_0", meta="atx=24")
        self.at("ATX_PWR", -149.0, 60.0, 1.8, rot=90)
        eps = [(85.0, 146.0, 0), (108.0, 146.0, 0)]
        if self.n == 2:
            eps += [(85.0, -146.0, 1), (108.0, -146.0, 1)]
        for i, (x, y, cpu) in enumerate(eps):
            self.minifit(x, y, 4, 2, "x", latch_side=1 if y > 0 else -1, name=f"A_PORT_EPS8_{i}", meta=f"split=none,cpu={cpu}")
            self.at(f"JPWR{i + 1} CPU{cpu}", x, y - 7.6 if y > 0 else y + 7.6, 1.4)

    def s_headers(self):
        fans = [136.0, 118.0, 100.0, 16.0, 2.0, -28.0]
        for i, y in enumerate(fans):
            self.pin_header(-160.0, y, 4, 1, fan=True, ang=-90, name=f"A_PORT_FANSYS_{i}", meta=f"fan=fan{i + 1},pinout=GND|12V|SENSE|PWM",
                            label=f"FAN{i + 1}", label_pos=(-152.0, y))
        self.pin_header(-140.0, -146.0, 5, 2, missing=(10,), name="A_PORT_FPANEL_0",
                        meta="pinout=1:HDD_LED+,2:PLED+,3:HDD_LED-,4:PLED-,5:RESET_GND,6:PWR_SW,7:RESET,8:PWR_GND,9:NC,10:KEY;"
                             "pwr=6,8;reset=5,7;pled=2,4;hdd=1,3")
        self.at("F_PANEL", -140.0, -139.0, 1.6)
        self.pin_header(-138.0, 128.0, 10, 2, pitch=2.0, missing=(20,), shroud=True, ang=90, name="A_PORT_USB3HDR_0",
                        meta="usb3=19pin,key=+x", label="USB3_FRONT", label_pos=(-130.0, 128.0))
        self.pin_header(-140.0, 104.0, 7, 2, pitch=2.0, missing=(14,), label="TPM", label_pos=(-140.0, 99.0))
        self.pin_header(-140.0, 90.0, 5, 2, missing=(10,), label="COM1", label_pos=(-140.0, 85.6))
        self.pin_header(-140.0, -120.0, 3, 1, label="CLR_CMOS", label_pos=(-140.0, -116.6))
        # two MCIO x8 connectors (NVMe backplane cables), looks plus anchors
        for i, y in enumerate((-36.0, -52.0)):
            self.bx("connector_black", -146.0, y, PT, 9.0, 12.0, 6.4, bevel=0.3)
            self.bx("black_plastic", -150.6, y, PT + 1.2, 0.4, 10.0, 3.6)
            self.bx("steel", -144.0, y, PT + 6.4, 5.0, 12.4, 0.3)
            self.anchor(f"A_PORT_MCIO_{i}", (-150.6, y, PT + 3.0), (4.0, 12.0, 8.0), forward=(-1, 0, 0), up=(0, 0, 1),
                        meta="mcio=x8,depth=0.0040")
            self.at(f"MCIO{i + 1}", -138.0, y, 1.4, ax="LEFT")
            self.occupy(-151, y - 6.5, -141, y + 6.5)

    def s_sata(self):
        x_m = -SHX - 1.0
        for si, yc in enumerate((-66.0, -83.0)):
            w, lvl = 11.6, 6.4
            h = lvl * 2 + 0.6
            M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
            out = [((yc - w / 2) * MM, PT * MM), ((yc + w / 2) * MM, PT * MM), ((yc + w / 2) * MM, (PT + h) * MM), ((yc - w / 2) * MM, (PT + h) * MM)]
            holes = []
            for lv in range(2):
                zc = PT + 0.3 + lvl * lv + lvl / 2
                holes.append(list(reversed([(p[0] * MM, p[1] * MM) for p in pp.rounded_rect(yc, zc, 9.6, 4.6, 0.3, 1)])))
            pp.prism(self.k["connector_black"], [out] + holes, x_m * MM, (x_m + 7.0) * MM, M=M)
            self.bx("connector_black", x_m + 9.5, yc, PT, 5.0, w, h)
            for lv in range(2):
                zc = PT + 0.3 + lvl * lv + lvl / 2
                self.bx("black_plastic", x_m + 7.2, yc, zc - 2.3, 0.4, 9.6, 4.6)
                self.bx("connector_black", x_m + 4.2, yc, zc - 1.2, 5.8, 7.8, 1.1)
                self.bx("connector_black", x_m + 4.2, yc + 3.9, zc - 1.2, 5.8, 1.0, 2.6)
                n = si * 2 + lv
                self.anchor(f"A_PORT_SATA_{n}", (x_m, yc, zc), (11.0, 6.0, 12.0), forward=(-1, 0, 0), up=(0, 0, 1),
                            meta=f"depth=0.0050,sata=SATA{n}")
            self.occupy(x_m, yc - w / 2, x_m + 12, yc + w / 2)
            self.at(f"SATA{si * 2} SATA{si * 2 + 1}", x_m + 14.0, yc, 1.3, ax="LEFT")

    def s_misc(self):
        self.chip(-138.0, -66.0, 10.0, 10.0, 1.2, ["NC6126D", "SIO"], logo="NOVACORE", leads=(20, 0.5, 4), ref="U31")
        self.chip(-138.0, -84.0, 5.3, 5.3, 1.6, ["25Q256", "BIOS"], leads=(4, 1.27, 2), ref="U17")
        self.at("BIOS", -138.0, -90.0, 1.3)
        self.battery(-138.0, 2.0)
        # 2-digit POST code display
        self.bx("black_plastic", -138.0, -100.0, PT, 12.0, 8.0, 3.0, bevel=0.3)
        self.anchor("A_DISPLAY_POST_0", (-138.0, -100.0, PT + 3.0), (12.0, 8.0, 2.0), meta="digits=2,colour=red,looks_only=1")
        g = self.piece("led_red", "A_DISPLAY_POST_0", "digits")
        for dx in (-2.8, 2.8):
            for (ox, oy, sx_, sy_) in ((0, 2.4, 2.4, 0.4), (0, 0, 2.4, 0.4), (0, -2.4, 2.4, 0.4), (-1.3, 1.2, 0.4, 2.0),
                                       (1.3, 1.2, 0.4, 2.0), (-1.3, -1.2, 0.4, 2.0), (1.3, -1.2, 0.4, 2.0)):
                self.bx(None, -138.0 + dx + ox, -100.0 + oy, PT + 3.0, sx_, sy_, 0.05, g=g)
        self.at("POST CODE", -138.0, -106.0, 1.2)
        self.occupy(-145, -105, -131, -95)
        # PCH-style platform hub with a low heatsink (rear of the socket area)
        x, y = 100.0, 14.0
        self.bx("alu", x, y, PT + 1.0, 22.0, 18.0, 2.0, bevel=0.3)
        for f in range(7):
            self.bx("alu", x - 9.0 + f * 3.0, y, PT + 3.0, 1.0, 18.0, 7.0)
        self.occupy(x - 12, y - 10, x + 12, y + 10)
        self.at("PCH", x, y - 12.0, 1.6)

    def s_passives(self):
        rnd = self.rnd
        zones = []
        for (sx, sy) in self.sockets:
            zones += [(sx - 50, sy - 44, sx + 50, sy - 40, 40, 0), (sx - 50, sy + 40, sx + 50, sy + 44, 40, 0)]
        zones += [(60, -10, 140, 40, 60, 0), (110, 80, 160, 100, 30, 90), (-150, -60, -120, 80, 60, 90), (-128, -150, -100, -110, 30, 0),
                  (120, 60, 140, 90, 20, 90), (36, 0, 56, 90, 30, 90)]
        for (x0, y0, x1, y1, n, ang) in zones:
            placed, tries = 0, 0
            while placed < n and tries < n * 12:
                tries += 1
                L, W, H = (1.0, 0.5, 0.5) if rnd.random() < 0.7 else (1.6, 0.8, 0.8)
                body = "ceramic" if rnd.random() < 0.7 else "chip_black"
                count = rnd.randint(3, 8)
                pitch = W + 0.5
                rd = Vector((0, 1, 0)) if ang == 0 else Vector((1, 0, 0))
                sx = round(rnd.uniform(x0, x1) * 2) / 2
                sy = round(rnd.uniform(y0, y1) * 2) / 2
                hw, hh = (L / 2 + 0.25, W / 2 + 0.25) if ang == 0 else (W / 2 + 0.25, L / 2 + 0.25)
                spots = []
                for i in range(count):
                    x, y = sx + rd.x * pitch * i, sy + rd.y * pitch * i
                    if x > x1 or y > y1 or not self.free(x - hw, y - hh, x + hw, y + hh):
                        break
                    spots.append((x, y))
                if len(spots) < 2:
                    continue
                for (x, y) in spots:
                    pp.smd_passive(self.k, x * MM, y * MM, PT * MM, L * MM, W * MM, H * MM, ang=ang, body=body)
                    self.occupy(x - hw, y - hh, x + hw, y + hh, 0.05)
                    placed += 1

    def s_traces(self):
        cfg = self.cfg
        rnd = random.Random(41 + self.n)
        tc = cfg["trace"]
        # DDR byte lanes from each socket into its banks, PCIe lanes to the slots
        for (cx, ys) in self.banks:
            for (sx, sy) in self.sockets:
                if abs(sy - ys[0]) < 80:
                    d = 1 if ys[0] > sy else -1
                    for lane in range(14):
                        x = sx - 42.0 + lane * 6.0
                        for i in range(4):
                            xx = x + i * 0.6
                            self.aline([(xx, sy + d * 44.0), (xx, ys[0] - d * 4.0)], 0.16, tc, z=0.2, joins=False)
        for i, y in enumerate(self.pcie_ys):
            for p in range(10):
                yy = y + 5.0 + p * 0.5
                self.aline([(self.sockets[0][0] + 62.0, yy + 30.0), (20.0, yy + 6.0), (28.0, yy)], 0.16, tc, z=0.2, joins=False)
        for n in range(1300):
            x, y = rnd.uniform(-SHX + 2, SHX - 2), rnd.uniform(-SHY + 2, SHY - 2)
            pts = [(x, y)]
            d = rnd.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
            for s in range(rnd.randint(2, 5)):
                L = rnd.uniform(1.5, 9.0)
                x, y = max(-SHX + 1, min(SHX - 1, x + d[0] * L)), max(-SHY + 1, min(SHY - 1, y + d[1] * L))
                pts.append((x, y))
                d = rnd.choice([(d[1], d[0]), (-d[1], -d[0])])
            self.aline(pts, rnd.choice([0.15, 0.2, 0.3]), tc, z=0.2)
            if rnd.random() < 0.6:
                self.ac(pts[-1][0], pts[-1][1], 0.35, cfg["via"], z=0.25, seg=8)
        for n in range(2600):
            self.ac(rnd.uniform(-SHX, SHX), rnd.uniform(-SHY, SHY), rnd.choice([0.3, 0.35, 0.45]), cfg["via"], z=0.25, seg=8)

    def s_silk(self):
        n = self.n
        self.at("STRATA", 100.0, -14.0, 6.0, font="agency")
        self.at(("SP-V 1S" if n == 1 else "L46 2S") + "  SSI-EEB", 100.0, -21.0, 2.2, font="arialbd")
        self.at("REV 1.10", 100.0, -25.4, 1.2, font="narrowbd")
        for i, (sx, sy) in enumerate(self.sockets):
            if n == 1:
                self.at(f"CPU{i}  SOCKET SP-V", sx + 30.0, sy - 61.0, 1.8, font="arialbd")
            else:
                self.at(f"CPU{i}  SOCKET L46", sx + 40.0, sy + (40.6 if sy > 0 else -40.6), 1.6, font="arialbd")
        self.at("94V-0  E254761  MADE IN TAIWAN", -80.0, -151.0, 1.0, font="narrowbd")

    def s_hits(self):
        boxes = [((0.0, 0.0, 0.8), (SBW, SBH, 1.6))]
        for (sx, sy) in self.sockets:
            boxes.append(((sx, sy, 6.0), (130.0, 100.0, 12.0)))
        for (cx, ys) in self.banks:
            boxes.append(((cx, (ys[0] + ys[-1]) / 2, 5.0), (150.0, abs(ys[-1] - ys[0]) + 8.0, 9.0)))
        boxes.append(((SHX - 92.0, (self.pcie_ys[0] + self.pcie_ys[-1]) / 2, 6.0), (100.0, abs(self.pcie_ys[-1] - self.pcie_ys[0]) + 10.0, 12.0)))
        boxes.append(((SHX - 8.0, 105.0, 15.0), (24.0, 90.0, 30.0)))
        for i, (p, s) in enumerate(boxes):
            self.anchor(f"A_HIT_{i}", p, s)


def build_server(bid, preview=True):
    import build_cat_boards as CB
    b = ServerBoard(bid)
    root = b.build()
    P.write_report(root, bid, "frame: SSI-EEB server board (origin at the PCB centre, +z component side, +x rear I/O, airflow -x to +x)")
    if preview and CB.PREVIEW[0]:
        pp.preview(root, bid, views=((15, 55), (-35, 40), (60, 35)), size=(1280, 960), dist=0.75, zup=True)
        s0 = b.sockets[0]
        pp.preview(root, bid, views=((-25, 50),), size=(1280, 960), dist=0.24, target=(s0[0] * MM, s0[1] * MM, 0.01), start=3, zup=True)
        pp.preview(root, bid, views=((50, 30),), size=(1280, 960), dist=0.22, target=(0.15, 0.06, 0.012), start=4, zup=True)
    with Geom(b.sockets[0]):
        sroot = CB.build_shield(bid, b, True)
    P.write_report(sroot, BOARDS[bid]["shield"], "frame: as the desktop I/O shields (origin at the plate centre, board axes, outer face +x)")
    return root


JOBS = {bid: (lambda b=bid: build_server(b)) for bid in BOARDS}
