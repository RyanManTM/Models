"""
Motherboards mb_ridge_b5 (Socket V5, DDR5) and mb_ridge_z4 (Socket L17, DDR4), plus their I/O shields
io_ridge_b5 and io_ridge_z4.

Board frame (REALISM.md section 2): origin at the PCB centre, the PCB spans z 0..0.0016, +z = component
side, +x = rear I/O edge, +y = top edge, 0.244 x 0.305 m. Mounting holes are the nine ATX 2.2 positions
(A, C, F, G, H, J, K, L, M; Figure 3 of the spec), the rear I/O window is the ATX aperture (6.25" x 1.75",
0.088" below the PCB bottom, 5.196" above datum hole A).

I/O shield frame: origin at the plate centre, axes as the board's (the outer face looks along +x); in board
coordinates the plate centre sits at (0.1279, 0.07546, 0.0200) (the case's A_SOCKET_IOSHIELD_0).

Everything below is in millimetres (board coordinates) unless a name says otherwise.

Run: blender -b --factory-startup -P Tools/Blender/build_board.py -- [ids...]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_pcb as pp  # noqa: E402
from mathutils import Vector  # noqa: E402

MM = 0.001
PT = 1.6                 # PCB top
BW, BH = 244.0, 305.0
HX, HY = BW / 2, BH / 2


def inch_hole(d, h):
    """ATX hole from (distance from the rear edge, height above the bottom edge) in inches."""
    return ((4.8 - d) * 25.4, (h - 6.0) * 25.4)


HOLES = [inch_hole(0.4, 0.65), inch_hole(0.4, 5.55), inch_hole(1.3, 11.75), inch_hole(6.5, 0.65), inch_hole(6.5, 5.55),
         inch_hole(6.5, 11.75), inch_hole(9.35, 0.65), inch_hole(9.35, 5.55), inch_hole(9.35, 11.75)]
HOLE_NAMES = "ACFGHJKLM"
HOLE_R = 3.96 / 2

# rear I/O window (ATX): y from 5.196" above datum A, 6.25" long; z from -0.088" to +1.662"
IO_Y0 = (0.65 + 5.196 - 6.0) * 25.4
IO_Y1 = IO_Y0 + 6.25 * 25.4
IO_Z0, IO_Z1 = -0.088 * 25.4, (1.75 - 0.088) * 25.4
# Rear I/O x positions are set by the case: its rear wall (and A_SOCKET_IOSHIELD_0) sits at case x 0.1959,
# i.e. board x 0.1279 with the board at A_SOCKET_MOBO_0 (case x 0.068). The connector faces sit 1.9 mm
# behind the shield plate, poking 4 mm past the PCB edge.
IO_FACE = 126.0       # the faces of the rear connectors
SHIELD_X = 127.9      # I/O shield plate centre (board x)

S = (30.0, 75.0)       # CPU socket centre
SEAT_Z = 4.6           # CPU contact face when seated
DIMM_X = [-30.4, -38.0, -45.6, -53.2]
DIMM_Y = 67.3
DIMM_NAMES = ["A1", "A2", "B1", "B2"]
PCIE16_Y = -45.0
SLOT_PITCH = 20.32
M2_Y = -15.0
M2_Z = 4.1             # SSD PCB bottom when installed
M2B_Y = -65.3
NOTCH = {"DDR5": -3.9, "DDR4": 4.3}
MKEY_Y = 6.0

BOARDS = {
    "mb_ridge_b5": dict(sock="V5", mem="DDR5", model="B5 GAMING", chipset="RB650", shield="io_ridge_b5",
                        mask="#16181c", trace="#20242a", pour="#1b1e22", via="#2b2f36", pad="#b6a982", silk="#e8e8e3",
                        deco="#363c46", accent="#a8b0bc", heat="alu_dark", heat2="alu", latch="grey_plastic",
                        shroud="dark_plastic", plate_bg="#121316", plate_ink="#e6e8ec", plate_acc="#8d96a4"),
    "mb_ridge_z4": dict(sock="L17", mem="DDR4", model="Z4 PRO", chipset="RZ790", shield="io_ridge_z4",
                        mask="#1c1616", trace="#291f1f", pour="#211919", via="#332727", pad="#bcab83", silk="#ecece9",
                        deco="#8a1a1f", accent="#c7262c", heat="paint_black", heat2="steel_dark", latch="connector_black",
                        shroud="black_plastic", plate_bg="#121010", plate_ink="#f0f0f0", plate_acc="#cf2a30"),
}


class Board:
    def __init__(self, bid):
        self.bid = bid
        self.cfg = BOARDS[bid]
        self.v5 = self.cfg["sock"] == "V5"
        self.k = pp.Kit(bid)
        self.rnd = random.Random(1 if self.v5 else 2)
        self.occ = []
        self.anchors = {}
        self.moving = []
        self.MT = "tex_" + bid + "_marks"
        self.PCBT = "tex_" + bid + "_pcb"

    # ---------------------------------------------------------------- geometry helpers (mm)
    def bx(self, tag, cx, cy, z0, sx, sy, h, bevel=0.0, uv=None, ang=0.0, g=None):
        g = g or self.k[tag]
        M = pp.rot("z", ang) if ang else None
        return pp.box(g, (cx * MM, cy * MM, (z0 + h / 2) * MM), (sx * MM, sy * MM, h * MM), M, bevel * MM, uv=uv)

    def cy(self, tag, cx, cy_, z0, r, h, seg=16, bevel=0.0, g=None, r2=None):
        g = g or self.k[tag]
        return pp.cyl(g, (cx * MM, cy_ * MM, (z0 + h / 2) * MM), r * MM, h * MM, "z", seg, bevel * MM, None if r2 is None else r2 * MM)

    def occupy(self, x0, y0, x1, y1, pad=0.4):
        self.occ.append((min(x0, x1) - pad, min(y0, y1) - pad, max(x0, x1) + pad, max(y0, y1) + pad))

    def free(self, x0, y0, x1, y1):
        for a in self.occ:
            if x0 < a[2] and x1 > a[0] and y0 < a[3] and y1 > a[1]:
                return False
        return True

    def top_map(self, region, cx, cy_, ztop, w, h, up=(0, 1, 0), rest=None):
        maps = [pp.Planar(region, (cx * MM, cy_ * MM, ztop * MM), (0, 0, 1), up, (w * MM, h * MM))]
        if rest is not None:
            maps.append(rest)
        return pp.MultiMap(maps)

    def anchor(self, name, pos, size, forward=(0, 0, 1), up=(0, 1, 0), meta=None, parent=None):
        e = c.anchor(name, (pos[0] * MM, pos[1] * MM, pos[2] * MM), (size[0] * MM, size[1] * MM, size[2] * MM),
                     parent or self.root, forward, up, meta)
        self.anchors[name] = e
        return e

    def piece(self, tag, anchor_name, base="part"):
        """A Geo for a moving piece (or anything owned by an anchor), pivoting at the anchor."""
        a = self.anchors[anchor_name]
        g = pp.Geo(tag, origin=pp.unconv(a.matrix_world.translation))
        self.moving.append((g, anchor_name, base))
        return g

    # ---------------------------------------------------------------- PCB art helpers (board mm)
    @staticmethod
    def P(x, y):
        return HX - x, y + HY

    def ar(self, x0, y0, x1, y1, col, z=0.3):
        u0, v0 = self.P(max(x0, x1), min(y0, y1))
        u1, v1 = self.P(min(x0, x1), max(y0, y1))
        self.pcb.rect(u0, v0, u1, v1, col, z)

    def ac(self, x, y, r, col, z=0.3, seg=None):
        self.pcb.circle(*self.P(x, y), r, col, z, seg)

    def aring(self, x, y, r0, r1, col, z=0.3):
        self.pcb.ring(*self.P(x, y), r0, r1, col, z)

    def aline(self, pts, w, col, z=0.2, joins=True):
        self.pcb.line([self.P(x, y) for x, y in pts], w, col, z, joins)

    def apoly(self, pts, col, z=0.3):
        self.pcb.poly([self.P(x, y) for x, y in pts], col, z)

    def at(self, s, x, y, size, col=None, rot=0.0, font="arialbd", ax="CENTER", ay="CENTER", z=0.6, fit=None):
        u, v = self.P(x, y)
        return self.pcb.text(s, u, v, size, col or self.cfg["silk"], z=z, font=font, ax=ax, ay=ay, rot=rot, fit=fit)

    def aframe(self, x0, y0, x1, y1, t=0.15, col=None, z=0.5):
        u0, v0 = self.P(max(x0, x1), min(y0, y1))
        u1, v1 = self.P(min(x0, x1), max(y0, y1))
        self.pcb.frame_rect(u0, v0, u1, v1, t, col or self.cfg["silk"], z)

    def silk_box(self, cx, cy_, w, h, ref=None, pin1=True, ang=0.0, ref_side="top"):
        """Silkscreen outline around a footprint (w x h), a pin-1 dot and a reference designator."""
        if abs(math.sin(math.radians(ang))) > 0.5:
            w, h = h, w
        self.aframe(cx - w / 2 - 0.5, cy_ - h / 2 - 0.5, cx + w / 2 + 0.5, cy_ + h / 2 + 0.5, 0.15)
        if pin1:
            self.ac(cx + w / 2 + 0.9, cy_ + h / 2 + 0.9, 0.3, self.cfg["silk"], z=0.5, seg=10)
        if ref:
            if ref_side == "top":
                self.at(ref, cx, cy_ + h / 2 + 1.6, 1.0, font="narrowbd")
            else:
                self.at(ref, cx, cy_ - h / 2 - 1.6, 1.0, font="narrowbd")

    def pads(self, cx, cy_, L, W, n_side, pitch, sides=2, lead=0.9, ang=0.0):
        col = self.cfg["pad"]
        M = pp.rot("z", ang)
        for i in range(n_side):
            t = (i - (n_side - 1) * 0.5) * pitch
            for s in (-1, 1):
                o = M @ Vector((t, s * (W / 2 + lead * 0.5), 0))
                hw = pitch * 0.3
                if abs(math.sin(math.radians(ang))) > 0.5:
                    self.ar(cx + o.x - lead * 0.6, cy_ + o.y - hw, cx + o.x + lead * 0.6, cy_ + o.y + hw, col, 0.35)
                else:
                    self.ar(cx + o.x - hw, cy_ + o.y - lead * 0.6, cx + o.x + hw, cy_ + o.y + lead * 0.6, col, 0.35)
                if sides == 4:
                    o = M @ Vector((s * (L / 2 + lead * 0.5), t, 0))
                    self.ar(cx + o.x - lead * 0.6, cy_ + o.y - hw, cx + o.x + lead * 0.6, cy_ + o.y + hw, col, 0.35)

    # ---------------------------------------------------------------- marks atlas helpers
    def mark(self, w, h, ppm, bg):
        r, uv, ctx = self.marks.panel(w, h, ppm, bg=bg)
        return uv, ctx

    def chip(self, cx, cy_, L, W, H, lines, ang=0.0, bg="#18191b", ink="#8e9198", logo=None, text_rot=0.0, leads=None,
             ref=None, pad=True):
        """A marked IC: geometry + laser marking in the atlas + footprint pads and silkscreen on the PCB."""
        ppm = max(18.0, min(40.0, 260.0 / max(L, W)))
        tw, th = (L, W) if abs(math.sin(math.radians(text_rot))) < 0.5 else (W, L)
        uv, ctx = self.mark(tw, th, ppm, bg)
        with ctx as a:
            n = len(lines) + (1 if logo else 0)
            step = th / (n + 1.2)
            yy = th - step * 0.9
            if logo:
                a.text(logo, tw / 2, yy, step * 0.9, ink, font="agency")
                yy -= step
            for s in lines:
                a.text(s, tw / 2, yy, step * 0.62, ink, font="arialbd", fit=tw * 0.9)
                yy -= step
            a.circle(min(tw, th) * 0.12, min(tw, th) * 0.12, min(tw, th) * 0.05, pp.shade(bg, 1.6), z=0.4)
        black = self.marks.swatch(bg)
        pp.chip_marked(self.k[self.MT], cx * MM, cy_ * MM, PT * MM, L * MM, W * MM, H * MM, uv, black, ang=ang,
                       bevel=0.00012, text_rot=text_rot)
        ww, hh = (L, W) if abs(math.sin(math.radians(ang))) < 0.5 else (W, L)
        self.occupy(cx - ww / 2 - 1.2, cy_ - hh / 2 - 1.2, cx + ww / 2 + 1.2, cy_ + hh / 2 + 1.2)
        if leads:
            n, pitch, sides = leads
            pp.gull_leads(self.k["solder"], cx * MM, cy_ * MM, PT * MM, L * MM, W * MM, n, pitch * MM, sides=sides,
                          lead_len=0.0009, ang=ang)
            if pad:
                self.pads(cx, cy_, L, W, n, pitch, sides, 1.2, ang)
            self.silk_box(cx, cy_, ww + 2.4, hh + 2.4, ref, True, 0.0)
        else:
            if pad:
                # exposed QFN pads around the edge
                col = self.cfg["pad"]
                self.ar(cx - ww / 2 - 0.35, cy_ - hh / 2 - 0.35, cx + ww / 2 + 0.35, cy_ + hh / 2 + 0.35, col, 0.34)
            self.silk_box(cx, cy_, ww + 0.6, hh + 0.6, ref, True, 0.0)

    # ================================================================ build
    def build(self):
        c.reset()
        # Art and atlases are created after the reset (they live in their own scenes)
        self.pcb = pp.Art(BW, BH, 2048, 2560, bg=self.cfg["mask"])
        self.marks = pp.Atlas(2048, 2048, bg="#101010")
        self.root = c.root(self.bid)
        self.pcb_swatches()
        self.mount_holes()
        self.socket()
        self.vrm()
        self.dimms()
        self.pcie()
        self.m2()
        self.chipset()
        self.rear_io()
        self.power_connectors()
        self.headers()
        self.sata()
        self.debug_leds()
        self.misc()
        self.passives()
        self.traces()
        self.silkscreen()
        self.pcb_mesh()
        # render textures
        self.pcb.render(pp.tex_path(self.bid + "_pcb"))
        self.marks.render(pp.tex_path(self.bid + "_marks"))
        pp.PREVIEW_TEX[self.bid + "_pcb"] = (0.0, 0.5)
        pp.PREVIEW_TEX[self.bid + "_marks"] = (0.0, 0.42)
        self.k.finish(self.root)
        for g, an, base in self.moving:
            # keep "<base>@<anchor>#<tag>" under Blender's 63-character name limit
            g.obj(base, self.anchors[an])
        self.hit_boxes()
        self.films()
        c.join_by_tag(self.root, self.bid)
        c.export(self.root, self.bid)
        pp.report(self.root)
        return self.root

    # ---------------------------------------------------------------- PCB
    def pcb_swatches(self):
        """Flat colour patches hidden under the socket housing, for the PCB edge, bottom and hole walls."""
        sx, sy = S
        cols = {"edge": "#3d3f33", "bottom": self.cfg["mask"], "plating": "#b8ad8a"}
        self.pcb_sw = {}
        for i, (k_, col) in enumerate(cols.items()):
            x, y = sx - 10 + i * 8, sy
            self.ar(x - 2, y - 2, x + 2, y + 2, col, z=0.95)
            u, v = self.P(x, y)
            self.pcb_sw[k_] = pp.Swatch((u / BW, v / BH))

    def pcb_mesh(self):
        rc = 0.8
        outline = pp.rounded_rect(0, 0, BW, BH, rc, 3)
        holes = [list(reversed(pp.circle_pts(x, y, HOLE_R, 20))) for x, y in HOLES]
        loops = [[(p[0] * MM, p[1] * MM) for p in outline]] + [[(p[0] * MM, p[1] * MM) for p in h] for h in holes]
        reg = (0.0, 0.0, 1.0, 1.0)
        maps = [pp.Planar(reg, (0, 0, PT * MM), (0, 0, 1), (0, 1, 0), (BW * MM, BH * MM)),
                _NormalSwatch((0, 0, -1), self.pcb_sw["bottom"]),
                _HoleSwatch(self.pcb_sw["plating"]),
                self.pcb_sw["edge"]]
        pp.prism(self.k[self.PCBT], loops, 0.0, PT * MM, uv=pp.MultiMap(maps))

    def mount_holes(self):
        for i, (x, y) in enumerate(HOLES):
            self.aring(x, y, HOLE_R, 3.8, self.cfg["pad"], z=0.4)
            for k in range(8):
                a = math.radians(22.5 + 45 * k)
                self.ac(x + math.cos(a) * 3.0, y + math.sin(a) * 3.0, 0.32, self.cfg["mask"], z=0.45, seg=8)
            self.occupy(x - 4.6, y - 4.6, x + 4.6, y + 4.6, 0)
            # the standoff meets the PCB bottom (comes from -z); the case screw seats on the PCB top
            self.anchor(f"A_HOLE_{i}", (x, y, 0.0), (8.0, 8.0, 3.0), forward=(0, 0, -1), up=(0, 1, 0),
                        meta=f"atx={HOLE_NAMES[i]},d=0.00396")
            self.anchor(f"A_SCREW_PH2_{i}", (x, y, PT), (7.0, 7.0, 6.0), meta=f"hole=A_HOLE_{i},m3=1")

    # ---------------------------------------------------------------- CPU socket
    def socket(self):
        sx, sy = S
        v5 = self.v5
        k = self.k
        if v5:
            hw, hh = 23.0, 23.0          # housing half sizes
            cw, ch = 20.3, 20.3          # cavity half sizes
            fx, fy0, fy1 = 28.0, -33.0, 33.0
            hinge_y = 31.0
            lever_x = 28.6
            keys = [(19.85, 12.0), (-19.85, 12.0)]
            plate = (22.6, -25.0, 25.0, 18.3, 19.6)    # half w, y0, y1, window half w, window half h
        else:
            hw, hh = 22.0, 26.0
            cw, ch = 19.0, 22.7
            fx, fy0, fy1 = 26.0, -35.5, 35.5
            hinge_y = 34.0
            lever_x = 26.8
            keys = [(18.55, 14.0), (-18.55, 14.0)]
            plate = (21.2, -27.5, 28.0, 15.4, 19.0)
        self.occupy(sx - fx - 1, sy + fy0 - 1, sx + fx + 4, sy + fy1 + 1)
        # ---- pin field texture (gold contact tips on the dark housing floor)
        uv, ctx = self.mark(cw * 2, ch * 2, 20.0, "#0d0d0e")
        with ctx as a:
            pitch = 0.95 if v5 else 0.9
            rows = int((ch * 2 - 2.0) / (pitch * 0.866))
            for r in range(rows):
                yy = 1.0 + r * pitch * 0.866
                off = pitch * 0.5 if r % 2 else 0.0
                xx = 1.0 + off
                while xx < cw * 2 - 1.0:
                    if not (not v5 and abs(xx - cw) < 4.5 and abs(yy - ch) < 8.0):
                        a.circle(xx, yy, 0.22, "#c7a148", z=0.2, seg=6)
                    xx += pitch
            if not v5:
                a.rrect(cw, ch, 8.6, 15.6, 0.5, "#18191b", z=0.25)
        black = self.marks.swatch("#101012")
        floor_map = self.top_map(uv, sx, sy, 4.0, cw * 2, ch * 2, rest=black)
        self.bx(self.MT, sx, sy, PT, hw * 2, hh * 2, 4.0 - PT, uv=floor_map)
        ring_out = pp.rounded_rect(sx * MM, sy * MM, hw * 2 * MM, hh * 2 * MM, 0.6 * MM, 2)
        ring_in = list(reversed(pp.rounded_rect(sx * MM, sy * MM, cw * 2 * MM, ch * 2 * MM, 0.3 * MM, 2)))
        pp.prism(k["connector_black"], [ring_out, ring_in], 4.0 * MM, 5.6 * MM)
        for kx, ky in keys:
            self.bx("connector_black", sx + kx, sy + ky, 4.0, 1.0, 1.8, 1.6)
        # pin-1 triangle on the housing (+x, -y corner)
        tx, ty = sx + (hw + cw) / 2, sy - (hh + ch) / 2
        g = k["white_plastic"]
        tri = [Vector((tx * MM, ty * MM, 5.62 * MM)), Vector(((tx - 1.3) * MM, ty * MM, 5.62 * MM)), Vector((tx * MM, (ty + 1.3) * MM, 5.62 * MM)),
               Vector((tx * MM, ty * MM, 5.6 * MM)), Vector(((tx - 1.3) * MM, ty * MM, 5.6 * MM)), Vector((tx * MM, (ty + 1.3) * MM, 5.6 * MM))]
        g.add(tri, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
        self.mark_socket = (tx + 0.4, ty - 0.4, 5.6)
        # ---- ILM stiffener frame (stainless) with side rails, hinge knuckles, hook and shoulder screw
        out = pp.rounded_rect(sx * MM, (sy + (fy0 + fy1) / 2) * MM, fx * 2 * MM, (fy1 - fy0) * MM, 1.5 * MM, 3)
        win = list(reversed(pp.rounded_rect(sx * MM, sy * MM, (hw * 2 + 0.8) * MM, (hh * 2 + 0.8) * MM, 1.0 * MM, 3)))
        pp.prism(k["steel"], [out, win], PT * MM, 2.4 * MM)
        for s in (-1, 1):
            self.bx("steel", sx + s * (fx - 2.6), sy + (fy0 + fy1) / 2 + (1.0 if s > 0 else 0), 2.4, 1.6, (fy1 - fy0) - 9.0, 1.4, bevel=0.3)
        for hx in (-12.0, 12.0):
            pp.cyl(k["steel"], ((sx + hx) * MM, (sy + hinge_y) * MM, 3.0 * MM), 1.7 * MM, 6.0 * MM, axis="x", seg=12)
            self.bx("steel", sx + hx, sy + hinge_y - 1.0, PT, 6.0, 3.0, 1.2)
        # lever retention hook (bottom, +x side)
        hkx, hky = sx + lever_x + 0.6, sy + fy0 + 5.0
        self.bx("steel", hkx, hky, PT, 2.4, 4.0, 4.8, bevel=0.3)
        self.bx("steel", hkx - 1.4, hky, 5.6, 3.0, 4.0, 0.8, bevel=0.2)
        # shoulder screw holding the load plate tongue
        scy = sy + fy0 + 1.6
        self.cy("steel_dark", sx, scy, 2.4, 1.6, 1.4, 12)
        self.cy("steel", sx, scy, 3.8, 3.0, 1.2, 16, bevel=0.3)
        self.bx("black_plastic", sx, scy, 4.95, 0.5, 3.6, 0.12)
        self.bx("black_plastic", sx, scy, 4.95, 3.6, 0.5, 0.12)
        # ILM screws (Torx heads) at the frame corners
        for ex in (-1, 1):
            for ey in (fy0 + 4.0, fy1 - 4.5):
                self.cy("steel_dark", sx + ex * (fx - 4.5), sy + ey, 2.4, 2.2, 1.6, 12, bevel=0.3)
        # ---- anchors
        size = (40.0, 40.0, 6.0) if v5 else (37.5, 45.0, 6.0)
        self.anchor("A_SOCKET_CPU_0", (sx, sy, SEAT_Z), size, meta=f"socket={self.cfg['sock']},pin1=+x-y")
        self.anchor("A_MARK_SOCKET_0", self.mark_socket, (3.0, 3.0, 2.0), meta="pin1=+x-y")
        keep = (95.0, 125.0, 40.0) if v5 else (95.0, 95.0, 40.0)
        self.anchor("A_SOCKET_COOLER_0", (sx, sy, SEAT_Z + 6.0), keep,
                    meta=("holes=0.054x0.090,brackets=1" if v5 else "holes=0.078x0.078,backplate=1"))
        self.anchor("A_LEVER_CPU_0", (sx + lever_x, sy + hinge_y, 3.0), (5.0, 60.0, 8.0),
                    meta="hinge=x,open=-115,plate=A_PLATE_CPU_0")
        self.anchor("A_PLATE_CPU_0", (sx, sy + hinge_y, 3.0), (plate[0] * 2, 55.0, 4.0), meta="hinge=x,open=-125")
        self.anchor("A_COVER_CPU_0", (sx, sy, 8.2), (40.0, 40.0, 3.0), meta="pnp_cap=1,remove=+z")
        # ---- lever arm (rod) and handle
        L = self.anchors["A_LEVER_CPU_0"]
        lx = sx + lever_x
        pts = [(sx - 17.0, sy + hinge_y, 3.0), (lx - 1.0, sy + hinge_y, 3.0), (lx, sy + hinge_y - 1.0, 3.1),
               (lx, sy + fy0 + 7.5, 3.6), (lx + 1.2, sy + fy0 + 5.2, 3.7), (lx + 3.4, sy + fy0 + 3.6, 3.8)]
        c.tube("lever", [(p[0] * MM, p[1] * MM, p[2] * MM) for p in pts], 0.9 * MM, "steel", L, verts=12)
        gl = self.piece("black_plastic", "A_LEVER_CPU_0", "handle")
        self.bx("black_plastic", lx + 4.6, sy + fy0 + 2.9, 3.0, 3.6, 2.4, 1.6, bevel=0.5, g=gl)
        # ---- load plate (flat over the CPU substrate edges, sloped tabs to the hinge and the tongue)
        gp = self.piece("steel", "A_PLATE_CPU_0", "plate")
        phw, py0, py1, wx, wy = plate
        z0p, z1p = SEAT_Z + 1.2, SEAT_Z + 1.8
        out = pp.rounded_rect(sx * MM, (sy + (py0 + py1) / 2) * MM, phw * 2 * MM, (py1 - py0) * MM, 1.6 * MM, 3)
        win = list(reversed(pp.rounded_rect(sx * MM, sy * MM, wx * 2 * MM, wy * 2 * MM, 1.2 * MM, 3)))
        pp.prism(gp, [out, win], z0p * MM, z1p * MM)
        # side flanges (bent down) for stiffness
        for s in (-1, 1):
            self.bx("steel", sx + s * (phw - 0.3), sy + (py0 + py1) / 2, z0p - 1.0, 0.6, (py1 - py0) - 6.0, 1.0, g=gp)
        # hinge tabs (sloping down to the knuckles) and the front tongue
        for hx in (-12.0, 12.0):
            _slope(gp, (sx + hx, sy + py1 - 0.5, z0p + 0.3), (sx + hx, sy + hinge_y, 3.0), 4.0, 0.6)
        _slope(gp, (sx, sy + py0 + 0.5, z0p + 0.3), (sx, scy + 1.4, 5.2), 8.0, 0.6)
        # ---- PnP protective cap (black, clipped into the plate window)
        gc = self.piece(self.MT, "A_COVER_CPU_0", "cap")
        uv, ctx = self.mark(wx * 2 + 3, wy * 2 + 3, 10.0, "#151517")
        with ctx as a:
            W2, H2 = wx * 2 + 3, wy * 2 + 3
            a.text("DO NOT REMOVE", W2 / 2, H2 * 0.62, 2.0, "#e4e4e4", font="arialbd")
            a.text("UNTIL CPU IS INSTALLED", W2 / 2, H2 * 0.52, 1.5, "#e4e4e4", font="arialbd", fit=W2 * 0.8)
            a.text("PnP CAP", W2 / 2, H2 * 0.36, 1.6, "#9a9a9a", font="arialbd")
            a.poly([(W2 * 0.5 - 3, H2 * 0.18), (W2 * 0.5 + 3, H2 * 0.18), (W2 * 0.5, H2 * 0.26)], "#e4e4e4", z=0.3)
            a.text("SOCKET " + self.cfg["sock"], W2 / 2, H2 * 0.82, 1.6, "#9a9a9a", font="arialbd")
        capblk = self.marks.swatch("#151517")
        self.bx(self.MT, sx, sy, z1p, wx * 2 + 3.0, wy * 2 + 3.0, 0.7, bevel=0.3, uv=capblk, g=gc)
        self.bx(self.MT, sx, sy, z1p + 0.7, wx * 2 - 1.0, wy * 2 - 1.0, 1.1, bevel=0.5,
                uv=self.top_map(uv, sx, sy, z1p + 1.8, wx * 2 + 3, wy * 2 + 3, rest=capblk), g=gc)
        self.bx(self.MT, sx, sy + py0 - 1.8, z1p - 0.2, 10.0, 4.0, 0.8, bevel=0.3, uv=capblk, g=gc)
        # ---- AM-style plastic cooler brackets (V5) or bare cooler holes (L17)
        if v5:
            for s in (-1, 1):
                by_ = sy + s * 45.0
                self.bx("black_plastic", sx, by_, PT, 72.0, 9.0, 6.0, bevel=0.8)
                self.bx("black_plastic", sx, by_ + s * 3.8, PT, 14.0, 3.0, 10.5, bevel=0.6)
                self.bx("black_plastic", sx, by_ + s * 3.2, PT + 8.6, 14.0, 4.6, 1.9, bevel=0.4)
                for ex in (-27.0, 27.0):
                    self.cy("black_plastic", sx + ex, by_, PT + 6.0, 3.4, 0.6, 16)
                    self.cy("steel_dark", sx + ex, by_, PT + 6.6, 2.9, 1.4, 16, bevel=0.4)
                    self.bx("black_plastic", sx + ex, by_, PT + 7.95, 0.5, 3.2, 0.1)
                    self.bx("black_plastic", sx + ex, by_, PT + 7.95, 3.2, 0.5, 0.1)
                self.occupy(sx - 37, by_ - 5, sx + 37, by_ + 5)
        else:
            for ex in (-39.0, 39.0):
                for ey in (-39.0, 39.0):
                    self.aring(sx + ex, sy + ey, 2.0, 3.6, self.cfg["pad"], z=0.4)
                    self.ac(sx + ex, sy + ey, 2.0, "#050505", z=0.42)
                    self.occupy(sx + ex - 4, sy + ey - 4, sx + ex + 4, sy + ey + 4)

    # ---------------------------------------------------------------- VRM
    def vrm(self):
        v5 = self.v5
        cfg = self.cfg
        k = self.k
        # choke marking
        uv, ctx = self.mark(7.6, 7.6, 16.0, "#2e2f33")
        with ctx as a:
            a.text("R22", 3.8, 4.4, 1.6, "#b8b8b8", font="arialbd")
            a.text("2346", 3.8, 2.4, 0.9, "#8a8a8a", font="arialbd")
        choke_side = self.marks.swatch("#2a2b2e")
        top_row = [-6.0 + i * 9.5 for i in range(6)] if v5 else [-2.0 + i * 9.5 for i in range(5)]
        rear_x = 72.0 if v5 else 78.0
        rear_col = [40.0 + i * 9.5 for i in range(9)] if v5 else [46.0 + i * 9.5 for i in range(7)]
        chokes = [(x, 129.5) for x in top_row] + [(rear_x, y) for y in rear_col]
        for n, (x, y) in enumerate(chokes):
            if y > 125.0:
                self.at(f"PL{n + 1}", x, y - 5.3, 0.9, font="narrowbd")
            else:
                self.at(f"PL{n + 1}", x - 5.2, y, 0.9, font="narrowbd", rot=90)
            m = self.top_map(uv, x, y, PT + 5.4, 7.6, 7.6, rest=choke_side)
            self.bx(self.MT, x, y, PT, 7.6, 7.6, 5.4, bevel=0.35, uv=m)
            for s in (-1, 1):
                self.ar(x + s * 2.6 - 1.2, y - 3.2, x + s * 2.6 + 1.2, y + 3.2, cfg["pad"], 0.35)
            self.occupy(x - 4.2, y - 4.2, x + 4.2, y + 4.2)
        # heatsinks
        heat, heat2 = cfg["heat"], cfg["heat2"]
        if v5:
            top = dict(x0=-12.0, x1=46.5, y0=133.6, y1=148.4, z1=29.0)
            rear = dict(x0=77.4, x1=95.2, y0=33.0, y1=127.0, z1=33.0)
        else:
            top = dict(x0=-8.0, x1=44.0, y0=133.6, y1=148.4, z1=24.0)
            rear = dict(x0=82.6, x1=95.2, y0=40.0, y1=121.0, z1=28.0)
        # top: base + fins running along y + an angled cap with an accent strip and a logo plate
        t = top
        self.bx(heat, (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2, 3.6, t["x1"] - t["x0"], t["y1"] - t["y0"], 4.4, bevel=0.6)
        nf = int((t["x1"] - t["x0"] - 2) / 2.9)
        for i in range(nf):
            x = t["x0"] + 1.6 + i * (t["x1"] - t["x0"] - 3.2) / (nf - 1)
            self.bx(heat, x, (t["y0"] + t["y1"]) / 2 + 0.6, 8.0, 1.1, t["y1"] - t["y0"] - 1.2, t["z1"] - 11.0)
        capz = t["z1"] - 3.0
        cap_pts = [(t["x0"], t["y0"] + 4.0), (t["x1"], t["y0"] + 4.0), (t["x1"], t["y1"]), (t["x0"], t["y1"])]
        self.bx(heat, (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2 + 2.0, capz, t["x1"] - t["x0"] + 0.4, t["y1"] - t["y0"] - 4.0, 3.0, bevel=0.6)
        # chamfered front lip toward the socket
        _slope(k[heat], ((t["x0"] + t["x1"]) / 2, t["y0"] + 4.0, capz + 1.5), ((t["x0"] + t["x1"]) / 2, t["y0"] + 0.4, capz - 2.5), t["x1"] - t["x0"] + 0.4, 3.0)
        self.bx(heat2, (t["x0"] + t["x1"]) / 2 + 4, t["y0"] + 5.5, capz + 3.0, t["x1"] - t["x0"] - 14, 1.2, 0.4)
        uv, ctx = self.mark(36.0, 8.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text("RIDGE", 2.0, 4.0, 5.0, cfg["plate_ink"], font="agency", ax="LEFT")
            a.line([(19.0, 2.0), (34.0, 2.0)], 0.5, cfg["plate_acc"])
            a.text(cfg["model"].split()[0] + " POWER", 34.0, 5.0, 2.0, cfg["plate_acc"], font="agencyr", ax="RIGHT")
        plate_edge = self.marks.swatch(cfg["plate_bg"])
        px, py_ = (t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2 + 3.0
        self.bx(self.MT, px, py_, capz + 3.0, 36.0, 8.0, 0.5, bevel=0.15, uv=self.top_map(uv, px, py_, capz + 3.5, 36.0, 8.0, rest=plate_edge))
        self.occupy(t["x0"], t["y0"], t["x1"], t["y1"])
        # rear: base + fins running along x + cap with chamfer toward the socket
        r = self.rear = rear
        self.bx(heat, (r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2, 3.6, r["x1"] - r["x0"], r["y1"] - r["y0"], 4.4, bevel=0.6)
        nf = int((r["y1"] - r["y0"] - 2) / 2.9)
        for i in range(nf):
            y = r["y0"] + 1.6 + i * (r["y1"] - r["y0"] - 3.2) / (nf - 1)
            self.bx(heat, (r["x0"] + r["x1"]) / 2 + 0.6, y, 8.0, r["x1"] - r["x0"] - 1.2, 1.1, r["z1"] - 11.0)
        capz = r["z1"] - 3.0
        self.bx(heat, (r["x0"] + r["x1"]) / 2 + 2.0, (r["y0"] + r["y1"]) / 2, capz, r["x1"] - r["x0"] - 4.0, r["y1"] - r["y0"] + 0.4, 3.0, bevel=0.6)
        _slope_x(k[heat], (r["x0"] + 4.0, (r["y0"] + r["y1"]) / 2, capz + 1.5), (r["x0"] + 0.4, (r["y0"] + r["y1"]) / 2, capz - 2.5), r["y1"] - r["y0"] + 0.4, 3.0)
        self.bx(heat2, r["x0"] + 5.5, (r["y0"] + r["y1"]) / 2 - 4, capz + 3.0, 1.2, r["y1"] - r["y0"] - 16, 0.4)
        self.occupy(r["x0"], r["y0"], r["x1"], r["y1"])
        # a nickel heat pipe linking both (B5)
        if v5:
            pts = [(30.0, 140.0, 3.4), (46.0, 139.5, 3.4), (58.0, 134.6, 3.4), (70.5, 126.5, 3.4), (80.0, 119.0, 3.4), (86.0, 110.0, 3.4)]
            c.tube("heatpipe", [(p[0] * MM, p[1] * MM, p[2] * MM) for p in pts], 1.6 * MM, "nickel", self.root, verts=12)
        # solid polymer capacitors (aluminium cans) near the EPS and around the VRM
        caps = [(74.5, 145.0, 3.15, 8.0), (74.5, 137.4, 3.15, 8.0), (-17.5, 129.0, 2.5, 6.0), (-17.5, 136.0, 2.5, 6.0)]
        if v5:
            caps += [(70.0, 33.5, 2.5, 6.0), (63.5, 21.0, 2.5, 6.0), (70.0, 21.0, 2.5, 6.0)]
        else:
            caps += [(75.0, 36.0, 2.5, 6.0), (76.0, 26.0, 2.5, 6.0), (69.0, 26.0, 2.5, 6.0), (2.0, 120.0, 2.5, 6.0), (10.0, 120.0, 2.5, 6.0)]
        for (x, y, rr, h) in caps:
            self.solid_cap(x, y, rr, h)
        # memory VRM (top front, beside the DIMMs)
        for i, y in enumerate((133.0, 123.0)):
            self.small_choke(-70.0, y)
            self.mosfet(-81.0, y)
        self.solid_cap(-89.0, 132.0, 2.5, 6.0)
        self.solid_cap(-89.0, 124.0, 2.5, 6.0)

    def solid_cap(self, x, y, r, h):
        k = self.k
        prof = [(0, PT), (r * 0.9, PT), (r * 0.9, PT + 0.5), (r, PT + 0.8), (r, PT + h - 0.5), (r * 0.94, PT + h), (0, PT + h)]
        pp.lathe(k["alu"], (x * MM, y * MM, 0), [(a * MM, b * MM) for a, b in prof], seg=20)
        # top marking stripe (dark print) and the base plate
        self.bx("black_plastic", x, y, PT, r * 2.2, r * 2.2, 0.5)
        self.bx("dark_plastic", x + r * 0.45, y, PT + h, r * 0.5, r * 1.1, 0.03)
        self.ac(x, y, r + 0.6, self.cfg["silk"], z=0.5)
        self.ac(x, y, r + 0.45, self.cfg["mask"], z=0.51)
        self.occupy(x - r - 0.6, y - r - 0.6, x + r + 0.6, y + r + 0.6)

    def small_choke(self, x, y):
        self.bx("steel_dark", x, y, PT, 6.0, 6.0, 3.0, bevel=0.3)
        self.occupy(x - 3.4, y - 3.4, x + 3.4, y + 3.4)

    def mosfet(self, x, y, ang=0.0):
        self.chip(x, y, 5.0, 6.0, 1.0, ["4C029", "N7A3"], ang=ang, pad=True)
        self.bx("solder", x + 2.9, y, PT, 0.8, 4.0, 0.25)

    # ---------------------------------------------------------------- DIMM slots
    def dimms(self):
        mem = self.cfg["mem"]
        notch = NOTCH[mem]
        y0, y1 = DIMM_Y - 69.8, DIMM_Y + 69.8
        for i, x in enumerate(DIMM_X):
            body = "connector_black" if (self.v5 or i % 2 == 0) else "grey_plastic"
            self.dimm_slot(x, body, notch)
            # anchors: the stick's bottom-edge centre when fully seated
            self.anchor(f"A_SOCKET_RAM_{i}", (x, DIMM_Y, 3.0), (7.6, 139.6, 14.0),
                        meta=f"notch={notch * MM:.4f},slot={DIMM_NAMES[i]},mem={mem},latch=both,pref={'1' if i in (1, 3) else '0'}")
            for e, (yy, sgn) in enumerate(((y0 - 2.1, 1), (y1 + 2.1, -1))):
                name = f"A_LATCH_RAM_{i}_{e}"
                self.anchor(name, (x, yy + sgn * 1.2, PT + 1.2), (6.4, 6.0, 18.0), forward=(0, 0, 1), up=(0, 1, 0),
                            meta=f"hinge=x,open={35 if e == 0 else -35}")
                g = self.piece(self.cfg["latch"], name, "latch")
                self.latch(g, x, yy, sgn)
            self.occupy(x - 3.2, y0 - 4.5, x + 3.2, y1 + 4.5)

    def dimm_slot(self, x, body, notch_y):
        k = self.k
        y0, y1 = DIMM_Y - 69.8, DIMM_Y + 69.8
        ch = 0.85
        top = PT + 7.6
        floor = 3.0
        for s in (-1, 1):
            self.bx(body, x + s * (ch + 2.15 / 2), DIMM_Y, PT, 2.15, y1 - y0, top - PT, bevel=0.25)
            # outer ribs
            for j in range(11):
                yy = y0 + 8.0 + j * 12.4
                self.bx(body, x + s * (ch + 2.15 + 0.15), yy, PT, 0.3, 1.2, top - PT - 1.0)
        self.bx(body, x, DIMM_Y, PT, ch * 2, y1 - y0, floor - PT)
        for e in (-1, 1):
            self.bx(body, x, DIMM_Y + e * (67.0 + 1.4), PT, ch * 2, 2.8, top - PT)
        self.bx(body, x, DIMM_Y + notch_y, floor, ch * 2, 1.0, 3.3)
        # contacts on both inner walls
        y = -66.675 + 3.0
        while y < 66.675 - 3.0:
            if abs(y - notch_y) > 1.25:
                for s in (-1, 1):
                    pp.quad(k["gold"], ((x + s * (ch - 0.01)) * MM, (DIMM_Y + y) * MM, 4.9 * MM), (0.00038, 0.0032), normal=(-s, 0, 0), up=(0, 0, 1))
            y += 0.85
        # silkscreen corner marks at the slot ends
        for yy, d in ((y0 - 4.6, 1), (y1 + 4.6, -1)):
            self.aline([(x - 3.3, yy + d * 2.0), (x - 3.3, yy), (x + 3.3, yy), (x + 3.3, yy + d * 2.0)], 0.15, self.cfg["silk"], z=0.5)

    def latch(self, g, x, yy, sgn):
        """DIMM latch in the closed pose: an upright lever at the slot end with a hook over the stick and a
        finger tab. sgn = +1 at the -y end (hook points toward +y), -1 at the +y end."""
        z0 = PT + 0.6
        self.bx(None, x, yy, z0, 5.8, 4.0, 7.6, bevel=0.4, g=g)                         # base in the slot end
        self.bx(None, x, yy - sgn * 0.3, z0 + 7.6, 4.6, 2.6, 8.4, bevel=0.3, g=g)       # upright arm
        self.bx(None, x, yy + sgn * 4.1, PT + 14.6, 2.4, 4.4, 2.4, bevel=0.3, g=g)      # hook into the stick's side notch
        _slope(g, (x, yy - sgn * 1.4, z0 + 15.6), (x, yy - sgn * 4.4, z0 + 17.4), 5.6, 1.3)  # finger tab

    # ---------------------------------------------------------------- PCIe
    def pcie(self):
        y16 = PCIE16_Y
        # x16 with steel armour + latch
        self.pcie_slot(-14.5, 74.5, y16, armour=True)
        self.anchor("A_SOCKET_PCIE16_0", (30.0, y16 + 2.3, PT + 10.5), (89.0, 9.0, 14.0), meta="lanes=16,card_origin=1")
        self.anchor("A_LATCH_PCIE_0", (-19.5, y16, PT + 0.8), (6.0, 7.5, 12.0), meta="hinge=y,open=-25")
        g = self.piece("connector_black" if not self.v5 else "grey_plastic", "A_LATCH_PCIE_0", "latch")
        self.pcie_latch(g, y16)
        # other slots: x1 / x16-length (x4) / x1
        ys = [y16 - SLOT_PITCH * 2, y16 - SLOT_PITCH * 3, y16 - SLOT_PITCH * 4]
        self.pcie_slot(49.5, 74.5, ys[0], armour=False)
        self.anchor("A_SOCKET_PCIE1_0", (62.0, ys[0] + 2.3, PT + 10.5), (25.0, 9.0, 14.0), meta="lanes=1,looks_only=1")
        self.pcie_slot(-14.5, 74.5, ys[1], armour=False)
        g2 = self.k["connector_black"]
        self.pcie_latch(g2, ys[1])
        self.pcie_slot(49.5, 74.5, ys[2], armour=False)
        self.anchor("A_SOCKET_PCIE1_1", (62.0, ys[2] + 2.3, PT + 10.5), (25.0, 9.0, 14.0), meta="lanes=1,looks_only=1")
        self.slot_ys = [y16] + ys

    def pcie_slot(self, xa, xb, yc, armour):
        k = self.k
        ch = 0.9
        top = PT + 10.5
        floor = 6.6
        L = xb - xa
        xm = (xa + xb) / 2
        body = "connector_black"
        for s in (-1, 1):
            self.bx(body, xm, yc + s * (ch + (3.75 - ch) / 2), PT, L, 3.75 - ch, top - PT, bevel=0.2)
        self.bx(body, xm, yc, PT, L, ch * 2, floor - PT)
        for e, xx in ((-1, xa), (1, xb)):
            self.bx(body, xx - e * 0.8, yc, PT, 1.6, ch * 2, top - PT)
        key_x = xb - 1.6 - 11.65
        self.bx(body, key_x, yc, floor, 1.6, ch * 2, top - floor - 0.6)
        x = xb - 2.2
        while x > xa + 1.8:
            if abs(x - key_x) > 1.3:
                for s in (-1, 1):
                    pp.quad(k["gold"], (x * MM, (yc + s * (ch - 0.01)) * MM, 8.4 * MM), (0.0005, 0.0026), normal=(0, -s, 0), up=(0, 0, 1))
            x -= 1.0
        if armour:
            st = "steel"
            for s in (-1, 1):
                self.bx(st, xm + 0.5, yc + s * 3.95, PT + 0.6, L + 1.0, 0.4, top - PT - 0.3)
                self.bx(st, xm + 0.5, yc + s * (ch + 3.15) / 2 + s * 0.2, top - 0.1, L + 1.0, 3.25 - ch + 0.6, 0.35)
                for j in range(4):
                    self.bx(st, xa + 6 + j * 26.0, yc + s * 4.1, PT - 0.6, 2.0, 0.3, 1.4)
            self.bx(st, xb + 1.2, yc, PT + 0.6, 0.4, 8.3, top - PT - 0.3)
            self.bx(st, xa - 0.4, yc, top - 0.1, 0.8, 8.3, 0.35)
        self.aframe(xa - 0.6, yc - 4.6, xb + 0.6, yc + 4.6, 0.15)
        self.occupy(xa - 7, yc - 4.6, xb + 1.0, yc + 4.6)

    def pcie_latch(self, g, yc):
        x0 = -14.5
        self.bx(None, x0 - 3.1, yc, PT + 0.4, 5.6, 7.2, 9.0, bevel=0.4, g=g)
        _slope_x(g, (x0 - 4.2, yc, PT + 9.2), (x0 - 7.6, yc, PT + 12.0), 7.2, 1.4)
        self.bx(None, x0 - 1.0, yc, PT + 9.0, 1.4, 4.0, 2.4, bevel=0.2, g=g)

    # ---------------------------------------------------------------- M.2
    def m2(self):
        k = self.k
        cfg = self.cfg
        for (yc, main) in ((M2_Y, True), (M2B_Y, False)):
            # connector at the -x end, mouth facing +x (at x -7.6: the SSD's fingers go 2.4 mm in); PCB plane z M2_Z..M2_Z+0.8
            cx = -9.6
            self.bx("connector_black", cx - 0.6, yc, PT, 5.2, 22.4, M2_Z - PT - 0.1)
            self.bx("connector_black", cx - 0.6, yc, M2_Z + 0.9, 5.2, 22.4, 1.4, bevel=0.2)
            self.bx("connector_black", cx - 2.2, yc, M2_Z - 0.1, 2.0, 22.4, 1.0)
            self.bx("black_plastic", cx + 0.6, yc, M2_Z - 0.1, 2.4, 21.6, 1.0)
            self.bx("connector_black", cx + 0.4, yc + MKEY_Y, M2_Z - 0.1, 2.6, 1.0, 1.0)
            for s in (-1, 1):
                self.bx("steel", cx - 0.4, yc + s * 11.8, PT, 3.6, 1.0, 2.4)
            # standoff (2280) and the alternate positions printed on the PCB
            sxp = 70.0
            pp.cyl(k["steel"], (sxp * MM, yc * MM, (PT + (M2_Z - PT) / 2) * MM), 2.6 * MM, (M2_Z - PT) * MM, "z", 6)
            self.cy("black_plastic", sxp, yc, M2_Z, 1.1, 0.05, 12)
            for d, lab in ((70.0, "2280"), (50.0, "2260"), (32.0, "2242")):
                self.aring(d, yc, 1.4, 2.6, cfg["pad"], z=0.4)
                self.at(lab, d, yc - 4.6 if main else yc + 4.6, 1.0, font="narrowbd")
            self.aframe(cx - 3.6, yc - 11.6, cx + 2.2, yc + 11.6, 0.15)
            self.occupy(cx - 4, yc - 12.5, cx + 3, yc + 12.5)
            self.occupy(sxp - 3, yc - 3, sxp + 3, yc + 3)
        self.at("M2_1", -3.0, M2_Y - 16.2, 1.8, font="arialbd")
        self.at("M2_2", -3.0, M2B_Y + 13.0, 1.6, font="arialbd")
        # heatsink posts
        for px in (-20.0, 78.0):
            pp.cyl(k["steel"], (px * MM, M2_Y * MM, (PT + (7.2 - PT) / 2) * MM), 2.6 * MM, (7.2 - PT) * MM, "z", 6)
            self.occupy(px - 3, M2_Y - 3, px + 3, M2_Y + 3)
        # anchors
        self.anchor("A_SOCKET_M2_0", (30.0, M2_Y, M2_Z), (80.0, 22.0, 4.0), meta=f"type=2280,key=M,keyy={MKEY_Y * MM:.4f},insert_angle=20")
        self.anchor("A_STANDOFF_M2_0", (70.0, M2_Y, M2_Z), (5.0, 5.0, 3.0), meta="screw=ph0")
        self.anchor("A_COVER_M2_0", (29.0, M2_Y, 10.7), (106.0, 25.0, 5.0), meta="remove=+z,screws=2")
        cov = self.anchors["A_COVER_M2_0"]
        self.anchor("A_SCREW_PH0_0", (-20.0, M2_Y, 9.8), (5.0, 5.0, 4.0), parent=cov)
        self.anchor("A_SCREW_PH0_1", (78.0, M2_Y, 9.8), (5.0, 5.0, 4.0), parent=cov)
        self.anchor("A_FILM_M2_0", (32.5, M2_Y, 6.2), (80.0, 23.0, 1.0), forward=(0, 0, -1), up=(0, 1, 0),
                    meta="peel=+x", parent=cov)
        # heatsink body (moves with the cover anchor)
        heat = cfg["heat"]
        g = self.piece(heat, "A_COVER_M2_0", "heatsink")
        x0, x1, y0, y1 = -24.0, 82.0, M2_Y - 12.5, M2_Y + 12.5
        self.bx(None, (x0 + x1) / 2, M2_Y, 7.2, x1 - x0, y1 - y0, 2.6, bevel=0.8, g=g)
        # angled ridges on top
        for i in range(7):
            xx = -12.0 + i * 7.0
            pp.box(g, (xx * MM, M2_Y * MM, 10.25 * MM), (2.2 * MM, 23.0 * MM, 0.9 * MM), pp.rot("z", 28), 0.0003)
        # screw counterbores
        for px in (-20.0, 78.0):
            pp.tube_ring(g, (px * MM, M2_Y * MM, 9.85 * MM), 2.2 * MM, 3.4 * MM, 0.1 * MM, seg=20)
        g2 = self.piece(self.MT, "A_COVER_M2_0", "logo")
        uv, ctx = self.mark(30.0, 18.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text("M.2", 15.0, 12.6, 6.0, cfg["plate_ink"], font="agency")
            a.text("SHIELD", 15.0, 6.6, 3.6, cfg["plate_acc"], font="agency")
            a.line([(3.0, 3.0), (27.0, 3.0)], 0.5, cfg["plate_acc"])
        pe = self.marks.swatch(cfg["plate_bg"])
        self.bx(self.MT, 62.0, M2_Y, 9.8, 30.0, 18.0, 0.6, bevel=0.2, uv=self.top_map(uv, 62.0, M2_Y, 10.4, 30.0, 18.0, rest=pe), g=g2)
        gt = self.piece("thermal_pad", "A_COVER_M2_0", "pad")
        self.bx(None, 32.5, M2_Y, 6.2, 79.0, 22.0, 1.0, g=gt)
        gf = self.piece("film_blue", "A_FILM_M2_0", "film")
        self.bx(None, 32.5, M2_Y, 6.13, 80.0, 22.6, 0.06, g=gf)
        self.bx(None, 77.0, M2_Y, 6.13, 9.0, 8.0, 0.06, g=gf)
        self.bx(None, 82.5, M2_Y, 6.6, 2.0, 8.0, 0.06, g=gf)

    # ---------------------------------------------------------------- chipset
    def chipset(self):
        cfg = self.cfg
        heat, heat2 = cfg["heat"], cfg["heat2"]
        x0, x1, y0, y1 = -102.0, -50.0, -112.0, -62.0
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        self.bx(heat, xm, ym, PT + 1.0, x1 - x0, y1 - y0, 4.2, bevel=0.8)
        pts = [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x1 - 3, y1 - 12), (x1 - 13, y1 - 3), (x0 + 3, y1 - 3)]
        pp.prism_bevel(self.k[heat], [(p[0] * MM, p[1] * MM) for p in pts], (PT + 5.2) * MM, (PT + 8.9) * MM, 0.8 * MM, seg=1)
        # grooves and accent
        for i in range(5):
            self.bx("black_plastic", x0 + 6 + i * 2.2, ym - 4, PT + 8.85, 0.8, (y1 - y0) - 18, 0.1)
        _strip(self.k[heat2], (x1 - 4.0, y1 - 13.5), (x1 - 14.0, y1 - 3.5), PT + 8.9, 1.6, 0.5)
        uv, ctx = self.mark(30.0, 26.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text("RIDGE", 15.0, 17.5, 7.0, cfg["plate_ink"], font="agency")
            a.line([(4.0, 12.6), (26.0, 12.6)], 0.4, cfg["plate_acc"])
            a.text(cfg["model"], 15.0, 8.6, 3.4, cfg["plate_acc"], font="agency")
            a.text("SERIES", 15.0, 4.6, 1.8, cfg["plate_ink"], font="arialbd")
        pe = self.marks.swatch(cfg["plate_bg"])
        px, py_ = xm - 4.0, ym - 1.0
        self.bx(self.MT, px, py_, PT + 8.9, 30.0, 26.0, 0.6, bevel=0.3, uv=self.top_map(uv, px, py_, PT + 9.5, 30.0, 26.0, rest=pe))
        for (ex, ey) in ((x0 + 4, y0 + 4), (x1 - 4, y1 - 4)):
            self.cy("steel", ex, ey, PT + 5.2, 1.6, 0.8, 12, bevel=0.2)
        self.occupy(x0, y0, x1, y1)
        self.aframe(x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.15)

    # ---------------------------------------------------------------- rear I/O
    def io_blocks(self):
        """(kind, y centre, z list, anchors list, label) from the top of the I/O window down."""
        if self.v5:
            return [
                ("buttons", 145.0, None, ["A_BUTTON_FLASHBACK_0", None], "BIOS"),
                ("usb2", 130.5, None, ["A_PORT_USBA_0", "A_PORT_USBA_1"], "USB 2.0"),
                ("video", 111.0, None, ["A_PORT_HDMI_0", "A_PORT_DP_0"], "DP HDMI"),
                ("usb5", 92.5, None, ["A_PORT_USBA_2", "A_PORT_USBA_3"], "5Gbps"),
                ("lan", 72.5, None, ["A_PORT_USBA_4", "A_PORT_USBA_5", "A_PORT_ETH_0"], "10Gbps"),
                ("usbc", 54.0, None, [None, None], "USB-C"),
                ("wifi", 33.0, None, [], "Wi-Fi"),
                ("audio3", 12.0, None, ["A_PORT_AUDIOJACK_0"], "AUDIO"),
            ]
        return [
            ("ps2", 145.0, None, ["A_BUTTON_FLASHBACK_0"], "PS/2"),
            ("usb2", 128.0, None, ["A_PORT_USBA_0", "A_PORT_USBA_1"], "USB 2.0"),
            ("video", 109.5, None, ["A_PORT_HDMI_0", "A_PORT_DP_0"], "DP HDMI"),
            ("usb5", 91.0, None, ["A_PORT_USBA_2", "A_PORT_USBA_3"], "5Gbps"),
            ("lan", 71.5, None, ["A_PORT_USBA_4", "A_PORT_USBA_5", "A_PORT_ETH_0"], "5Gbps"),
            ("usbc1", 53.0, None, [None], "USB-C"),
            ("audio5", 18.0, None, ["A_PORT_AUDIOJACK_0"], "AUDIO"),
        ]

    def rear_io(self):
        self.shield_cuts = []     # (kind, outline (y,z) list in mm) for the I/O shield
        self.shield_labels = []
        sw = {
            "blue": self.marks.swatch("#1f5fd0"), "red": self.marks.swatch("#d12a2a"), "teal": self.marks.swatch("#1aa59a"),
            "black": self.marks.swatch("#141414"), "green": self.marks.swatch("#3fa63c"), "pink": self.marks.swatch("#e07aa6"),
            "lblue": self.marks.swatch("#4d8fd6"), "orange": self.marks.swatch("#e08a2c"), "grey": self.marks.swatch("#8d8f93"),
            "purple": self.marks.swatch("#7a4fb0"), "ps2green": self.marks.swatch("#4f9a52"), "dkgrey": self.marks.swatch("#3a3b3e"),
        }
        self.io_sw = sw
        for kind, yc, _, anchors, label in self.io_blocks():
            n0 = len(self.shield_cuts)
            getattr(self, "io_" + kind)(yc, anchors)
            if label:
                ztop = max(p[1] for cut in self.shield_cuts[n0:] for p in cut[1]) if len(self.shield_cuts) > n0 else 20.0
                self.shield_labels.append((yc, label, ztop))
        self.io_shroud()

    # port primitives -------------------------------------------------
    def port_front(self, tag, yc, z0, w, h, holes, depth, back_tag="black_plastic"):
        """A connector block whose front face (at IO_FACE) has openings `holes` (lists of (y, z) mm, absolute),
        extruded `depth` mm back, a dark floor behind the openings, and the block's body behind that."""
        k = self.k
        out = [((yc - w / 2) * MM, z0 * MM), ((yc + w / 2) * MM, z0 * MM), ((yc + w / 2) * MM, (z0 + h) * MM), ((yc - w / 2) * MM, (z0 + h) * MM)]
        loops = [out] + [[(p[0] * MM, p[1] * MM) for p in hole] for hole in holes]
        M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
        pp.prism(k[tag], loops, (IO_FACE - depth) * MM, IO_FACE * MM, M=M)
        for hole in holes:
            ys = [p[0] for p in hole]
            zs = [p[1] for p in hole]
            self.bx(back_tag, IO_FACE - depth + 0.35, (min(ys) + max(ys)) / 2, min(zs) - 0.2, 0.6, max(ys) - min(ys) + 0.4, max(zs) - min(zs) + 0.4)

    def io_body(self, tag, yc, z0, w, h, x_back, x_front):
        self.bx(tag, (x_back + x_front) / 2, yc, z0, x_front - x_back, w, h)
        self.occupy(x_back, yc - w / 2, IO_FACE, yc + w / 2, 0.2)

    def io_anchor(self, name, yc, zc, w, h, depth, meta=""):
        if name:
            self.anchor(name, (IO_FACE, yc, zc), (w + 2.0, h + 2.0, depth * 2 + 2.0), forward=(1, 0, 0), up=(0, 0, 1),
                        meta=(f"depth={depth * MM:.4f}" + ("," + meta if meta else "")))

    def usb_a_stack(self, yc, anchors, tongue, n=2, z0=PT, meta="", cut=True):
        w, lvl = 14.6, 7.8
        h = lvl * n
        holes = []
        for i in range(n):
            zc = z0 + lvl * i + lvl / 2
            holes.append(pp.rounded_rect(yc, zc, 12.5, 5.2, 0.4, 1))
        self.port_front("steel", yc, z0, w, h, holes, 9.0)
        self.io_body("steel", yc, z0, w, h, IO_FACE - 17.0, IO_FACE - 9.0)
        for i in range(n):
            zc = z0 + lvl * i + lvl / 2
            # tongue (coloured plastic) in the upper half of the opening, with 4 contacts underneath
            self.bx(self.MT, IO_FACE - 5.0, yc, zc + 0.35, 8.6, 11.0, 1.9, uv=self.io_sw[tongue])
            for j in range(4):
                pp.quad(self.k["gold"], ((IO_FACE - 2.4) * MM, (yc - 3.0 + j * 2.0) * MM, (zc + 0.34) * MM), (0.0010, 0.0034),
                        normal=(0, 0, -1), up=(1, 0, 0))
            # spring tabs on the shell top
            if i == n - 1:
                for s in (-1, 1):
                    _slope_x(self.k["steel"], (IO_FACE - 3.5, yc + s * 3.5, z0 + h + 0.05), (IO_FACE - 1.0, yc + s * 3.5, z0 + h + 0.45), 1.6, 0.25)
            if i < len(anchors):
                self.io_anchor(anchors[i], yc, zc, 12.5, 5.2, 9.0, meta)
        if cut:
            self.shield_cuts.append(("rect", pp.rounded_rect(yc, z0 + h / 2, w + 1.2, h + 1.2, 0.8, 2)))
        return z0 + h

    def io_usb2(self, yc, anchors):
        self.usb_a_stack(yc, anchors, "black", meta="usb=2.0")

    def io_usb5(self, yc, anchors):
        self.usb_a_stack(yc, anchors, "blue", meta="usb=5g")

    def io_lan(self, yc, anchors):
        top = self.usb_a_stack(yc, anchors[:2], "red" if self.v5 else "blue", meta="usb=10g" if self.v5 else "usb=5g", cut=False)
        # RJ45 on top of the USB pair
        w, h = 16.0, 13.6
        z0 = top + 0.2
        zc = z0 + h / 2 - 0.4
        opening = [(yc - 5.85, zc - 2.0), (yc - 3.0, zc - 2.0), (yc - 3.0, zc - 4.1), (yc + 3.0, zc - 4.1), (yc + 3.0, zc - 2.0),
                   (yc + 5.85, zc - 2.0), (yc + 5.85, zc + 4.4), (yc - 5.85, zc + 4.4)]
        self.port_front("connector_black", yc, z0, w, h, [opening], 12.0)
        self.io_body("steel", yc, z0, w + 0.6, h + 0.3, IO_FACE - 21.0, IO_FACE - 12.0)
        # shield wrap (steel) on the sides/top
        for s in (-1, 1):
            self.bx("steel", IO_FACE - 6.5, yc + s * (w / 2 + 0.15), z0, 13.0, 0.3, h)
        self.bx("steel", IO_FACE - 6.5, yc, z0 + h, 13.0, w + 0.6, 0.3)
        # 8 contact wires at the top of the jack
        for j in range(8):
            yy = yc - 3.57 + j * 1.02
            _slope_x(self.k["gold"], (IO_FACE - 9.0, yy, zc + 4.2), (IO_FACE - 4.0, yy, zc + 2.4), 0.4, 0.25)
        # link / activity LEDs on the face
        for s, tag in ((-1, "led_green"), (1, "led_yellow")):
            self.bx(tag, IO_FACE + 0.05, yc + s * 5.9, z0 + h - 2.4, 0.2, 2.6, 1.6)
        self.io_anchor(anchors[2], yc, zc + 0.6, 11.7, 8.5, 12.0, "rj45=1,latch=-z")
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, (PT + z0 + h) / 2, w + 1.2, z0 + h - PT + 1.2, 0.8, 2)))

    def io_video(self, yc, anchors):
        w, h = 17.2, 13.8
        z0 = PT
        zh = z0 + 3.6     # HDMI centre
        zd = z0 + 10.3    # DP centre
        hdmi = [(yc - 7.0, zh + 2.25), (yc - 7.0, zh - 0.55), (yc - 5.6, zh - 2.25), (yc + 5.6, zh - 2.25), (yc + 7.0, zh - 0.55), (yc + 7.0, zh + 2.25)]
        dp = [(yc - 8.0, zd + 2.35), (yc - 8.0, zd - 2.35), (yc + 6.4, zd - 2.35), (yc + 8.0, zd - 0.75), (yc + 8.0, zd + 2.35)]
        self.port_front("steel", yc, z0, w, h, [list(reversed(hdmi)), list(reversed(dp))], 8.0)
        self.io_body("steel", yc, z0, w, h, IO_FACE - 13.0, IO_FACE - 8.0)
        self.bx("connector_black", IO_FACE - 4.5, yc, zh - 0.1, 7.0, 10.0, 1.6)
        self.bx("connector_black", IO_FACE - 4.5, yc - 0.6, zd - 0.6, 7.0, 11.6, 1.4)
        for j in range(10):
            pp.quad(self.k["gold"], ((IO_FACE - 2.6) * MM, (yc - 4.5 + j * 1.0) * MM, (zh + 0.71) * MM), (0.0005, 0.0024), normal=(0, 0, 1), up=(1, 0, 0))
            pp.quad(self.k["gold"], ((IO_FACE - 2.6) * MM, (yc - 5.1 + j * 1.0) * MM, (zd + 0.11) * MM), (0.0005, 0.0024), normal=(0, 0, 1), up=(1, 0, 0))
        self.io_anchor(anchors[0], yc, zh, 14.0, 4.5, 8.0, "hdmi=1")
        self.io_anchor(anchors[1], yc, zd, 16.0, 4.7, 8.0, "dp=1,latch=1")
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, z0 + h / 2, w + 1.0, h + 1.0, 0.8, 2)))

    def io_usbc(self, yc, anchors, n=2, cut=True):
        w, lvl = 10.0, 6.2
        z0 = PT
        holes = []
        for i in range(n):
            zc = z0 + 1.0 + lvl * i + lvl / 2 - 1.0
            holes.append(list(reversed(_stadium(yc, zc, 8.4, 2.6))))
        self.port_front("steel", yc, z0, w, lvl * n, holes, 7.0)
        self.io_body("steel", yc, z0, w, lvl * n, IO_FACE - 12.0, IO_FACE - 7.0)
        for i in range(n):
            zc = z0 + 1.0 + lvl * i + lvl / 2 - 1.0
            self.bx("connector_black", IO_FACE - 3.8, yc, zc - 0.35, 6.0, 6.6, 0.7)
        if cut:
            self.shield_cuts.append(("rect", pp.rounded_rect(yc, z0 + lvl * n / 2, w + 1.0, lvl * n + 1.0, 0.8, 2)))

    def io_usbc1(self, yc, anchors):
        # Z4: one USB-C below one USB-A (10Gbps teal)
        self.io_usbc(yc, anchors, n=1, cut=False)
        top = PT + 6.2
        t2 = self.usb_a_stack(yc, [], "teal", n=1, z0=top + 0.4, cut=False)
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, (PT + t2) / 2, 14.6 + 1.2, t2 - PT + 1.2, 0.8, 2)))

    def io_wifi(self, yc, anchors):
        k = self.k
        for i, zc in enumerate((PT + 9.0, PT + 21.0)):
            # threaded gold post with a hex nut against the shield
            pp.cyl(k["gold"], ((IO_FACE + 3.0) * MM, yc * MM, zc * MM), 3.15 * MM, 9.0 * MM, axis="x", seg=16)
            pp.cyl(k["gold"], ((IO_FACE - 0.3) * MM, yc * MM, zc * MM), 4.4 * MM, 1.8 * MM, axis="x", seg=6)
            pp.cyl(k["white_plastic"], ((IO_FACE + 7.55) * MM, yc * MM, zc * MM), 2.0 * MM, 0.1 * MM, axis="x", seg=12)
            pp.cyl(k["gold"], ((IO_FACE + 7.6) * MM, yc * MM, zc * MM), 0.45 * MM, 0.2 * MM, axis="x", seg=8)
            self.bx("steel", IO_FACE - 6.0, yc, zc - 4.0, 10.0, 6.5, 8.0)
            self.shield_cuts.append(("circle", pp.circle_pts(yc, zc, 3.6, 20)))
        self.occupy(IO_FACE - 11, yc - 4, IO_FACE, yc + 4)

    def jack_stack(self, yc, rows, z0=PT, anchor_name=None, anchor_row=None):
        """A column of 3.5 mm jacks: rows = [(colour, label)] from the bottom up."""
        w, lvl = 11.0, 10.6
        h = lvl * len(rows) + 1.0
        holes = [list(reversed(pp.circle_pts(yc, z0 + 1.0 + lvl * i + lvl / 2, 1.8, 16))) for i in range(len(rows))]
        self.port_front("connector_black", yc, z0, w, h, holes, 6.0)
        self.io_body("connector_black", yc, z0, w, h, IO_FACE - 17.0, IO_FACE - 6.0)
        for i, (col, lab) in enumerate(rows):
            zc = z0 + 1.0 + lvl * i + lvl / 2
            pp.tube_ring(self.k[self.MT], ((IO_FACE + 0.15) * MM, yc * MM, zc * MM), 1.8 * MM, 3.4 * MM, 0.3 * MM, axis="x", seg=20, uv=self.io_sw[col])
            self.shield_cuts.append(("circle", pp.circle_pts(yc, zc, 3.7, 20)))
            if anchor_name and i == anchor_row:
                self.io_anchor(anchor_name, yc, zc, 3.6, 3.6, 14.0, "jack=line_out,colour=green")
        return z0 + h

    def io_audio3(self, yc, anchors):
        self.jack_stack(yc, [("pink", "MIC"), ("green", "OUT"), ("lblue", "IN")], anchor_name=anchors[0], anchor_row=1)

    def io_audio5(self, yc, anchors):
        self.jack_stack(yc - 6.2, [("pink", "MIC"), ("green", "OUT"), ("lblue", "IN")], anchor_name=anchors[0], anchor_row=1)
        top = self.jack_stack(yc + 6.2, [("grey", "SIDE"), ("black", "REAR"), ("orange", "C/SUB")])
        # optical S/PDIF out above the right column
        w, h = 9.0, 8.0
        z0 = top + 0.6
        hole = list(reversed(pp.rounded_rect(yc + 6.2, z0 + h / 2, 5.4, 4.2, 0.6, 2)))
        self.port_front("connector_black", yc + 6.2, z0, w, h, [hole], 4.0)
        self.io_body("connector_black", yc + 6.2, z0, w, h, IO_FACE - 12.0, IO_FACE - 4.0)
        self.bx("dark_plastic", IO_FACE - 1.0, yc + 6.2, z0 + h / 2 - 2.0, 0.4, 5.2, 4.0)
        self.shield_cuts.append(("rect", pp.rounded_rect(yc + 6.2, z0 + h / 2, w + 1.0, h + 1.0, 0.6, 2)))

    def io_buttons(self, yc, anchors):
        # BIOS flashback (square, lower) and clear CMOS (round, upper) push buttons in a small housing
        w, h = 10.0, 21.0
        z0 = PT
        b1z, b2z = z0 + 5.5, z0 + 15.0
        holes = [list(reversed(pp.rounded_rect(yc, b1z, 6.4, 6.4, 0.6, 2))), list(reversed(pp.circle_pts(yc, b2z, 3.0, 20)))]
        self.port_front("steel", yc, z0, w, h, holes, 3.0)
        self.io_body("connector_black", yc, z0, w, h, IO_FACE - 9.0, IO_FACE - 3.0)
        self.bx("black_plastic", IO_FACE - 1.8, yc, b1z - 2.8, 2.4, 5.6, 5.6, bevel=0.5)
        pp.cyl(self.k["dark_plastic"], ((IO_FACE - 0.8) * MM, yc * MM, b2z * MM), 2.6 * MM, 2.4 * MM, axis="x", seg=20, bevel=0.0004)
        self.io_anchor(anchors[0], yc, b1z, 6.4, 6.4, 1.5, "button=flashback,usb=A_PORT_USBA_0,press=-x")
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, b1z, 7.4, 7.4, 0.6, 2)))
        self.shield_cuts.append(("circle", pp.circle_pts(yc, b2z, 3.6, 20)))

    def io_ps2(self, yc, anchors):
        # Z4: a PS/2 combo port (lower) and the BIOS flashback button (upper)
        w, h = 13.2, 13.0
        z0 = PT
        zc = z0 + 6.5
        hole = list(reversed(pp.circle_pts(yc, zc, 4.6, 24)))
        self.port_front("connector_black", yc, z0, w, h, [hole], 6.0)
        self.io_body("steel", yc, z0, w, h, IO_FACE - 13.0, IO_FACE - 6.0)
        self.bx(self.MT, IO_FACE - 3.0, yc - 3.3, zc - 3.4, 4.0, 0.6, 6.8, uv=self.io_sw["purple"])
        self.bx(self.MT, IO_FACE - 3.0, yc + 3.3, zc - 3.4, 4.0, 0.6, 6.8, uv=self.io_sw["ps2green"])
        pp.cyl(self.k["connector_black"], ((IO_FACE - 4.5) * MM, yc * MM, zc * MM), 3.0 * MM, 3.0 * MM, axis="x", seg=16)
        for j in range(6):
            a = math.radians(30 + 60 * j)
            pp.cyl(self.k["solder"], ((IO_FACE - 2.9) * MM, (yc + math.cos(a) * 1.9) * MM, (zc + math.sin(a) * 1.9) * MM), 0.35 * MM, 0.2 * MM, axis="x", seg=6)
        self.shield_cuts.append(("circle", pp.circle_pts(yc, zc, 5.4, 24)))
        bz = z0 + h + 5.0
        hole = list(reversed(pp.rounded_rect(yc, bz, 6.4, 6.4, 0.6, 2)))
        self.port_front("steel", yc, z0 + h + 0.5, 10.0, 9.0, [hole], 3.0)
        self.io_body("connector_black", yc, z0 + h + 0.5, 10.0, 9.0, IO_FACE - 9.0, IO_FACE - 3.0)
        self.bx("black_plastic", IO_FACE - 1.8, yc, bz - 2.8, 2.4, 5.6, 5.6, bevel=0.5)
        self.io_anchor(anchors[0], yc, bz, 6.4, 6.4, 1.5, "button=flashback,usb=A_PORT_USBA_0,press=-x")
        self.shield_cuts.append(("rect", pp.rounded_rect(yc, bz, 7.4, 7.4, 0.6, 2)))

    def io_shroud(self):
        cfg = self.cfg
        tag = cfg["shroud"]
        y0, y1 = (22.0, 151.5) if self.v5 else (30.0, 151.5)
        # a hollow cover: slanted inner wall + top plate + end caps, open toward the rear and the board
        M = pp.frame(x=(1, 0, 0), y=(0, 0, 1), z=(0, 1, 0))
        wall = [(95.8, PT), (98.0, PT), (98.0, 26.2), (101.4, 34.4), (99.4, 36.6), (95.8, 27.0)]
        pp.prism_bevel(self.k[tag], [(p[0] * MM, p[1] * MM) for p in wall], y0 * MM, y1 * MM, 0.5 * MM, seg=1, M=M)
        xr = IO_FACE - 1.7     # rear edge of the shroud, just inside the port faces
        self.bx(tag, (99.8 + xr) / 2, (y0 + y1) / 2, 34.4, xr - 99.8, y1 - y0, 2.2, bevel=0.5)
        cap = [(95.8, PT), (xr, PT), (xr, 36.6), (99.4, 36.6), (95.8, 27.0)]
        for ya, yb in ((y0, y0 + 2.0), (y1 - 2.0, y1)):
            pp.prism_bevel(self.k[tag], [(p[0] * MM, p[1] * MM) for p in cap], ya * MM, yb * MM, 0.4 * MM, seg=1, M=M)
        # ribs under the top plate between the port blocks keep the inside from looking empty
        self.bx("black_plastic", 103.0, (y0 + y1) / 2, 30.0, 6.0, y1 - y0 - 4.0, 4.4)
        # RGB light bar along the inner top edge
        pp.box(self.k["rgb"], (100.4 * MM, ((y0 + y1) / 2 + 2) * MM, 36.9 * MM), (1.4 * MM, (y1 - y0 - 10) * MM, 0.7 * MM), bevel=0.0002)
        # logo plate on the top, reading along +y
        uv, ctx = self.mark(76.0, 17.0, 14.0, cfg["plate_bg"])
        with ctx as a:
            a.text("RIDGE", 4.0, 9.5, 11.0, cfg["plate_ink"], font="agency", ax="LEFT")
            a.line([(40.0, 5.0), (72.0, 5.0)], 0.6, cfg["plate_acc"])
            a.text(cfg["model"], 72.0, 10.2, 4.6, cfg["plate_acc"], font="agency", ax="RIGHT")
            for i in range(6):
                a.poly([(42 + i * 4.6, 13.8), (44.4 + i * 4.6, 13.8), (42.6 + i * 4.6, 15.4), (40.2 + i * 4.6, 15.4)], cfg["plate_acc"], z=0.3)
        pe = self.marks.swatch(cfg["plate_bg"])
        px, py_ = (99.8 + xr) / 2 + 0.6, (y0 + y1) / 2 + 6.0
        self.bx(self.MT, px, py_, 36.6, 17.0, 76.0, 0.5, bevel=0.15,
                uv=self.top_map(uv, px, py_, 37.1, 76.0, 17.0, up=(1, 0, 0), rest=pe))
        # side accent
        self.bx(cfg["heat2"], 95.6, (y0 + y1) / 2, 8.0, 0.5, y1 - y0 - 30, 1.2)
        self.occupy(95.0, y0, xr, y1)

    # ---------------------------------------------------------------- power connectors
    def minifit(self, cx, cy_, cols, rows, along="y", latch_side=-1, name=None, meta="", label=None):
        """Mini-Fit Jr. header (4.2 mm pitch): a housing with a cell per pin and a tin-plated pin in each.
        cols run along `along`."""
        p = 4.2
        n_a, n_b = cols, rows
        La, Lb = n_a * p + 1.8, n_b * p + 1.6
        H = 12.4
        if along == "y":
            sx, sy = Lb, La
        else:
            sx, sy = La, Lb
        body = "connector_black"
        self.bx(body, cx, cy_, PT, sx, sy, 3.0)
        for i in range(n_a + 1):
            t = -La / 2 + 0.9 + i * p - (0.0 if 0 < i < n_a else 0.0)
            wt = 0.9 if i in (0, n_a) else 0.6
            tt = max(-La / 2 + wt / 2, min(La / 2 - wt / 2, -n_a * p / 2 + i * p))
            if along == "y":
                self.bx(body, cx, cy_ + tt, PT + 3.0, sx, wt, H - 3.0)
            else:
                self.bx(body, cx + tt, cy_, PT + 3.0, wt, sy, H - 3.0)
        for j in range(n_b + 1):
            wt = 0.9 if j in (0, n_b) else 0.6
            tt = max(-Lb / 2 + wt / 2, min(Lb / 2 - wt / 2, -n_b * p / 2 + j * p))
            if along == "y":
                self.bx(body, cx + tt, cy_, PT + 3.0, wt, sy, H - 3.0)
            else:
                self.bx(body, cx, cy_ + tt, PT + 3.0, sx, wt, H - 3.0)
        for i in range(n_a):
            for j in range(n_b):
                ta = -n_a * p / 2 + (i + 0.5) * p
                tb = -n_b * p / 2 + (j + 0.5) * p
                px, py_ = (cx + tb, cy_ + ta) if along == "y" else (cx + ta, cy_ + tb)
                self.cy("solder", px, py_, PT + 3.0, 0.8, 6.5, 8)
        # latch catch on one long side
        if along == "y":
            self.bx(body, cx + latch_side * (sx / 2 + 0.7), cy_, PT + H - 5.0, 1.4, 4.0, 3.0, bevel=0.2)
        else:
            self.bx(body, cx, cy_ + latch_side * (sy / 2 + 0.7), PT + H - 5.0, 4.0, 1.4, 3.0, bevel=0.2)
        self.occupy(cx - sx / 2 - 1.5, cy_ - sy / 2 - 1.5, cx + sx / 2 + 1.5, cy_ + sy / 2 + 1.5)
        self.aframe(cx - sx / 2 - 0.6, cy_ - sy / 2 - 0.6, cx + sx / 2 + 0.6, cy_ + sy / 2 + 0.6, 0.18)
        if name:
            up = (0, latch_side, 0) if along == "x" else (latch_side, 0, 0)
            self.anchor(name, (cx, cy_, PT + H), (sx + 2, sy + 2, 8.0), forward=(0, 0, 1), up=up,
                        meta=f"depth=0.0075,pins={cols * rows},latch=+up" + ("," + meta if meta else ""))

    def power_connectors(self):
        self.minifit(-115.6, 62.0, 12, 2, "y", latch_side=-1, name="A_PORT_ATX24_0", meta="atx=24")
        self.at("ATX_PWR", -108.0, 62.0, 1.8, rot=90)
        ex, ey = 59.5, 145.5
        self.minifit(ex, ey, 4, 2, "x", latch_side=1, name="A_PORT_EPS8_0", meta="split=4+4")
        self.at("CPU_PWR1", ex, ey - 7.6, 1.6)

    # ---------------------------------------------------------------- pin headers
    def pin_header(self, cx, cy_, cols, rows, pitch=2.54, missing=(), ang=0.0, base_h=2.5, pin_len=6.0, fan=False,
                   shroud=False, name=None, meta="", label=None, label_pos=None, base_tag="connector_black"):
        """cols along the local x (rotated by ang about z), rows along local y. Pins are numbered the
        Intel way: pin n -> col (n-1)//2, row (n-1)%2 (odd pins on row 0)."""
        M = pp.rot("z", ang)
        La, Lb = cols * pitch, rows * pitch
        if shroud:
            wall = 0.9
            Lo, Wo = La + 2 * wall + 0.6, Lb + 2 * wall + 0.8
            hh = 8.9
            g = self.k[base_tag]
            pp.box(g, (cx * MM, cy_ * MM, (PT + 1.0) * MM), (Lo * MM, Wo * MM, 2.0 * MM), M)
            for s in (-1, 1):
                o = M @ Vector((0, s * (Wo / 2 - wall / 2), 0))
                if s > 0:
                    # key slot in the middle of one long wall
                    for e in (-1, 1):
                        o2 = M @ Vector((e * (Lo / 4 + 1.2), s * (Wo / 2 - wall / 2), 0))
                        pp.box(g, ((cx + o2.x) * MM, (cy_ + o2.y) * MM, (PT + hh / 2) * MM), ((Lo / 2 - 2.4) * MM, wall * MM, hh * MM), M)
                else:
                    pp.box(g, ((cx + o.x) * MM, (cy_ + o.y) * MM, (PT + hh / 2) * MM), (Lo * MM, wall * MM, hh * MM), M)
                o = M @ Vector((s * (Lo / 2 - wall / 2), 0, 0))
                pp.box(g, ((cx + o.x) * MM, (cy_ + o.y) * MM, (PT + hh / 2) * MM), (wall * MM, Wo * MM, hh * MM), M)
            pin_z0, plen = PT + 2.0, 6.0
            top = PT + hh
            sx, sy = Lo, Wo
        else:
            g = self.k[base_tag]
            pp.box(g, (cx * MM, cy_ * MM, (PT + base_h / 2) * MM), (La * MM, Lb * MM, base_h * MM), M, 0.0002)
            pin_z0, plen = PT + base_h, pin_len
            top = PT + base_h + pin_len
            sx, sy = La, Lb
            if fan:
                # polarising wall with two ramps along the row-1 side
                o = M @ Vector((0, Lb / 2 + 0.5, 0))
                pp.box(g, ((cx + o.x) * MM, (cy_ + o.y) * MM, (PT + 3.2) * MM), (La * MM, 1.0 * MM, 6.4 * MM), M)
                for e in (-1, 1):
                    o = M @ Vector((e * pitch * 0.5, Lb / 2 - 0.2, 0))
                    pp.box(g, ((cx + o.x) * MM, (cy_ + o.y) * MM, (PT + base_h + 2.2) * MM), (0.8 * MM, 0.6 * MM, 4.4 * MM), M)
                sy += 2.0
        n = cols * rows
        for i in range(n):
            pin = i + 1
            if pin in missing:
                continue
            col, row = (i // rows, i % rows) if rows > 1 else (i, 0)
            lx = -La / 2 + (col + 0.5) * pitch
            ly = -Lb / 2 + (row + 0.5) * pitch
            o = M @ Vector((lx, ly, 0))
            pp.box(self.k["gold"], ((cx + o.x) * MM, (cy_ + o.y) * MM, (pin_z0 + plen / 2) * MM), (0.64 * MM, 0.64 * MM, plen * MM), M)
            pp.box(self.k["gold"], ((cx + o.x) * MM, (cy_ + o.y) * MM, (pin_z0 + plen + 0.15) * MM), (0.4 * MM, 0.4 * MM, 0.3 * MM), M)
        w2, h2 = (sx, sy) if abs(math.sin(math.radians(ang))) < 0.5 else (sy, sx)
        self.occupy(cx - w2 / 2 - 1, cy_ - h2 / 2 - 1, cx + w2 / 2 + 1, cy_ + h2 / 2 + 1)
        self.aframe(cx - w2 / 2 - 0.5, cy_ - h2 / 2 - 0.5, cx + w2 / 2 + 0.5, cy_ + h2 / 2 + 0.5, 0.15)
        for i in range(n):
            col, row = (i // rows, i % rows) if rows > 1 else (i, 0)
            o = M @ Vector((-La / 2 + (col + 0.5) * pitch, -Lb / 2 + (row + 0.5) * pitch, 0))
            if i == 0:
                self.ar(cx + o.x - 0.75, cy_ + o.y - 0.75, cx + o.x + 0.75, cy_ + o.y + 0.75, self.cfg["pad"], 0.36)
        if label:
            lx, ly = label_pos or (cx, cy_ + h2 / 2 + 2.0)
            self.at(label, lx, ly, 1.5)
        if name:
            # pin 1 position in the anchor frame (forward +z, up +y: local x = board x)
            col0 = -La / 2 + 0.5 * pitch
            row0 = -Lb / 2 + 0.5 * pitch
            p1 = M @ Vector((col0, row0, 0))
            cstep = M @ Vector((pitch, 0, 0))
            rstep = M @ Vector((0, pitch, 0))
            geo = f"pin1={p1.x * MM:.5f},{p1.y * MM:.5f};colstep={cstep.x * MM:.5f},{cstep.y * MM:.5f};rowstep={rstep.x * MM:.5f},{rstep.y * MM:.5f}"
            self.anchor(name, (cx, cy_, top), (w2 + 2, h2 + 2, 8.0), meta=f"depth={plen * MM:.4f},pins={n - len(missing)};{geo}" + (";" + meta if meta else ""))
        return top

    def headers(self):
        by = -146.6
        cfg = self.cfg
        # CPU fan (top, by the socket) and system fans
        self.pin_header(-26.0, 146.5, 4, 1, fan=True, name="A_PORT_FANCPU_0", meta="fan=cpu,pinout=GND|12V|SENSE|PWM", label="CPU_FAN",
                        label_pos=(-26.0, 141.6))
        self.pin_header(8.0, by, 4, 1, fan=True, ang=180, name="A_PORT_FANSYS_0", meta="fan=sys1", label="SYS_FAN1", label_pos=(8.0, by + 5.4))
        self.pin_header(-117.0, -30.0, 4, 1, fan=True, ang=-90, name="A_PORT_FANSYS_1", meta="fan=sys2", label="SYS_FAN2", label_pos=(-110.0, -30.0))
        self.pin_header(-80.0, 146.5, 4, 1, fan=True, name="A_PORT_FANSYS_2", meta="fan=sys3", label="SYS_FAN3", label_pos=(-80.0, 141.6))
        # ARGB (5V-D-key-G), USB 2.0 x2, USB 3 (box header), HD audio, front panel
        self.pin_header(86.0, by, 4, 1, missing=(3,), name="A_PORT_RGB_0", meta="argb=5v,pinout=5V|D|KEY|GND", label="ARGB_V2", label_pos=(86.0, by + 4.2))
        self.pin_header(66.0, by, 5, 2, missing=(10,), label="USB_E12", label_pos=(66.0, by + 5.0))
        self.pin_header(-14.0, by, 5, 2, missing=(10,), label="USB_E34", label_pos=(-14.0, by + 5.0))
        self.pin_header(36.0, -147.2, 10, 2, pitch=2.0, missing=(20,), shroud=True, name="A_PORT_USB3HDR_0", meta="usb3=19pin,key=+y",
                        label="USB3_1", label_pos=(36.0, -140.6))
        self.pin_header(104.0, by, 5, 2, missing=(8,), name="A_PORT_AUDIOHDR_0", meta="hd_audio=1", label="HD_AUDIO", label_pos=(104.0, by + 5.0))
        fp = self.pin_header(-100.0, by, 5, 2, missing=(10,), name="A_PORT_FPANEL_0",
                             meta="pinout=1:HDD_LED+,2:PLED+,3:HDD_LED-,4:PLED-,5:RESET_GND,6:PWR_SW,7:RESET,8:PWR_GND,9:NC,10:KEY;"
                                  "pwr=6,8;reset=5,7;pled=2,4;hdd=1,3")
        self.fpanel_legend(-100.0, by)
        self.pin_header(-84.0, by, 4, 1, label="SPEAKER", label_pos=(-84.0, by + 3.4))
        # front USB-C header (key-A, right angle) near the 24-pin
        uy = 26.0
        self.bx("connector_black", -116.0, uy, PT, 7.0, 12.4, 5.6, bevel=0.3)
        self.bx("steel", -119.4, uy, PT + 1.0, 0.4, 10.0, 3.6)
        self.bx("black_plastic", -119.0, uy, PT + 2.2, 0.4, 7.6, 1.4)
        self.at("U32G2_C1", -108.4, uy, 1.4, rot=90)
        self.occupy(-120, uy - 7, -112, uy + 7)
        # second front USB 3 header: a right-angle 19-pin box header at the front edge (looks only)
        self.ra_box_header(-116.6, 5.0)
        self.at("U32G1_34", -107.6, 5.0, 1.4, rot=90)
        # CMOS clear jumper
        self.pin_header(0.0, -133.0, 2, 1, label="CLR_CMOS", label_pos=(0.0, -130.0))

    def ra_box_header(self, cx, cy_):
        """Right-angle 2x10 (2.0 mm) box header whose mouth faces the board's front edge (-x)."""
        body = "connector_black"
        L, H, D = 22.4, 9.0, 8.6
        self.bx(body, cx + 1.6, cy_, PT, D - 3.2, L, H, bevel=0.2)
        for s_ in (-1, 1):
            self.bx(body, cx - D / 2 + 1.0, cy_ + s_ * (L / 2 - 0.45), PT, 2.0, 0.9, H)
        self.bx(body, cx - D / 2 + 1.0, cy_, PT, 2.0, L, 0.9)
        self.bx(body, cx - D / 2 + 1.0, cy_ + 5.0, PT + H - 0.9, 2.0, 8.0, 0.9)
        self.bx(body, cx - D / 2 + 1.0, cy_ - 5.0, PT + H - 0.9, 2.0, 8.0, 0.9)
        for i in range(10):
            for j in range(2):
                if i == 9 and j == 1:
                    continue
                y = cy_ - 9.0 + i * 2.0
                z = PT + 3.5 + j * 2.0
                pp.cyl(self.k["gold"], ((cx - 2.0) * MM, y * MM, z * MM), 0.25 * MM, 4.0 * MM, axis="x", seg=4)
        self.occupy(cx - D / 2, cy_ - L / 2, cx + D / 2, cy_ + L / 2)
        self.aframe(cx - D / 2 - 0.4, cy_ - L / 2 - 0.4, cx + D / 2 + 0.4, cy_ + L / 2 + 0.4, 0.15)

    def fpanel_legend(self, cx, cy_):
        """The F_PANEL pinout printed around the header: even pins (row 1) above, odd pins (row 0) below."""
        s_ = self.cfg["silk"]
        p = 2.54
        top_labels = ["PLED+", "PLED-", "PWR", "GND", ""]
        bot_labels = ["HD+", "HD-", "GND", "RST", "NC"]
        for i in range(5):
            x = cx - 2 * p + i * p
            if top_labels[i]:
                self.at(top_labels[i], x, cy_ + 3.3, 0.8, font="narrowbd", fit=2.4)
            self.at(bot_labels[i], x, cy_ - 3.3, 0.8, font="narrowbd", fit=2.4)
        self.aline([(cx - 2 * p - 0.9, cy_ + 4.1), (cx - p + 0.9, cy_ + 4.1)], 0.15, s_)
        self.aline([(cx - 0.9, cy_ + 4.1), (cx + p + 0.9, cy_ + 4.1)], 0.15, s_)
        self.aline([(cx - 2 * p - 0.9, cy_ - 4.1), (cx - p + 0.9, cy_ - 4.1)], 0.15, s_)
        self.aline([(cx - 0.9, cy_ - 4.1), (cx + p + 0.9, cy_ - 4.1)], 0.15, s_)
        self.at("POWER LED", cx - 1.5 * p, cy_ + 4.9, 0.8, font="narrowbd")
        self.at("POWER SW", cx + 0.5 * p, cy_ + 4.9, 0.8, font="narrowbd")
        self.at("HDD LED", cx - 1.5 * p, cy_ - 4.9, 0.8, font="narrowbd")
        self.at("RESET", cx + 0.5 * p, cy_ - 4.9, 0.8, font="narrowbd")
        self.at("F_PANEL", cx, cy_ + 7.2, 1.6)
        self.ac(cx - 2 * p - 2.3, cy_ - 1.27, 0.35, s_, z=0.5)

    # ---------------------------------------------------------------- SATA
    def sata(self):
        names = []
        for si, yc in enumerate((-62.0, -79.0)):
            x_m = -123.0
            w, lvl = 11.6, 6.4
            h = lvl * 2 + 0.6
            body = "connector_black"
            # housing walls around two openings facing -x
            M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
            out = [((yc - w / 2) * MM, PT * MM), ((yc + w / 2) * MM, PT * MM), ((yc + w / 2) * MM, (PT + h) * MM), ((yc - w / 2) * MM, (PT + h) * MM)]
            holes = []
            for lv in range(2):
                zc = PT + 0.3 + lvl * lv + lvl / 2
                holes.append(list(reversed([(p[0] * MM, p[1] * MM) for p in pp.rounded_rect(yc, zc, 9.6, 4.6, 0.3, 1)])))
            pp.prism(self.k[body], [out] + holes, x_m * MM, (x_m + 7.0) * MM, M=M)
            self.bx(body, x_m + 9.5, yc, PT, 5.0, w, h)
            for lv in range(2):
                zc = PT + 0.3 + lvl * lv + lvl / 2
                self.bx("black_plastic", x_m + 7.2, yc, zc - 2.3, 0.4, 9.6, 4.6)
                # L-shaped tongue with 7 contacts
                self.bx(body, x_m + 4.2, yc, zc - 1.2, 5.8, 7.8, 1.1)
                self.bx(body, x_m + 4.2, yc + 3.9, zc - 1.2, 5.8, 1.0, 2.6)
                for j in range(7):
                    pp.quad(self.k["gold"], ((x_m + 3.6) * MM, (yc - 3.2 + j * 1.0) * MM, (zc - 0.09) * MM), (0.0005, 0.0040), normal=(0, 0, 1), up=(1, 0, 0))
                n = si * 2 + lv
                self.anchor(f"A_PORT_SATA_{n}", (x_m, yc, zc), (11.0, 6.0, 12.0), forward=(-1, 0, 0), up=(0, 0, 1),
                            meta=f"depth=0.0050,sata=SATA6G_{n + 1}")
                names.append(n)
            self.occupy(x_m, yc - w / 2, x_m + 12, yc + w / 2)
            self.aframe(-122.4, yc - w / 2 - 0.4, x_m + 12.4, yc + w / 2 + 0.4, 0.15)
            self.at(f"SATA6G_{si * 2 + 1}", -107.5, yc - 2.4, 1.3, font="arialbd", ax="LEFT")
            self.at(f"SATA6G_{si * 2 + 2}", -107.5, yc + 2.4, 1.3, font="arialbd", ax="LEFT")

    # ---------------------------------------------------------------- debug LEDs
    def debug_leds(self):
        tags = [("CPU", "led_red"), ("DRAM", "led_yellow"), ("VGA", "led_white"), ("BOOT", "led_green")]
        for i, (lab, tag) in enumerate(tags):
            x, y = -104.0, 121.0 - i * 6.0
            name = f"A_LED_DEBUG_{lab}_0"
            self.anchor(name, (x, y, PT + 0.8), (4.0, 3.0, 2.0), meta=f"colour={tag[4:]}")
            g = self.piece(tag, name, "led")
            self.bx(None, x, y, PT, 2.0, 1.25, 0.8, bevel=0.15, g=g)
            for s in (-1, 1):
                self.bx("solder", x + s * 1.1, y, PT, 0.35, 1.25, 0.5)
            self.at(lab, x + 3.6, y, 1.4, font="arialbd", ax="LEFT")
            self.occupy(x - 1.6, y - 1.2, x + 10, y + 1.2)
        self.aframe(-107.0, 101.5, -93.5, 124.0, 0.15)

    # ---------------------------------------------------------------- chips and small parts
    def misc(self):
        cfg = self.cfg
        v5 = self.v5
        # Super I/O, BIOS flash, audio codec + caps, LAN, clock gen, PWM controller, USB redrivers
        self.chip(-30.0, -127.0, 14.0, 14.0, 1.4, ["NC6799D-R", "2347JA19", "TAIWAN"], logo="NOVACORE", leads=(32, 0.4, 4), ref="U31")
        self.chip(-6.0, -120.0, 5.3, 5.3, 1.6, ["25Q256JVEQ", "2338"], logo="WINDBRIDGE", leads=(4, 1.27, 2), ref="U17")
        self.at("BIOS", -6.0, -126.0, 1.3)
        self.chip(98.0, -62.0, 7.0, 7.0, 0.9, ["AL897", "C3A41M1", "GB51E"], logo="AUREL", ref="U44")
        self.chip(88.0, 16.0, 9.0, 9.0, 0.9, ["EL8125BG", "C2M95H2", "GG28A"], logo="ETHERLINK", ref="U12")
        self.chip(-40.0, -74.0, 4.0, 4.0, 0.8, ["RC926", "3BX"], ref="U25")
        self.chip(-16.5, 121.0, 5.0, 5.0, 0.8, ["RP2.0", "A23K"], ref="PU1")
        self.chip(90.0, 3.0, 3.0, 3.0, 0.7, ["RD7"], ref="U40")
        self.chip(90.0, -6.0, 3.0, 3.0, 0.7, ["RD7"], ref="U41")
        self.chip(-98.0, -8.0, 4.0, 4.0, 0.8, ["ASM82"], ref="U28")
        # audio: gold-sleeved caps and the isolation line
        for (x, y) in ((86.0, -48.0), (86.0, -76.0), (110.0, -48.0), (110.0, -76.0), (98.0, -90.0), (110.0, -100.0), (86.0, -100.0)):
            self.audio_cap(x, y)
        line = [(80.0, -30.0), (80.0, -112.0), (118.0, -112.0)]
        self.aline(line, 0.5, cfg["accent"], z=0.55)
        self.at("AUDIO", 99.0, -116.0, 1.5, col=cfg["accent"])
        # CMOS battery in its holder
        self.battery(24.0, -127.0)

    def audio_cap(self, x, y):
        prof = [(0, PT), (2.4, PT), (2.5, PT + 0.6), (2.5, PT + 10.4), (2.3, PT + 11.0), (0, PT + 11.0)]
        uv, ctx = self.mark(16.0, 11.0, 10.0, "#c99a2e")
        with ctx as a:
            a.rect(0, 0, 2.0, 11.0, "#2a2a2a", z=0.2)
            a.text("AUDIO", 9.0, 6.6, 1.8, "#3a2a10", font="arialbd")
            a.text("470µF 16V", 9.0, 3.6, 1.4, "#3a2a10", font="arialbd")
        side = pp.Planar(uv, (x * MM, (y + 2.6) * MM, (PT + 5.5) * MM), (0, 1, 0), (0, 0, 1), (16.0 * MM, 11.0 * MM), thresh=-1.1)
        pp.lathe(self.k[self.MT], (x * MM, y * MM, 0), [(a_ * MM, b * MM) for a_, b in prof], seg=20, uv=side)
        self.cy("alu", x, y, PT + 11.0, 2.2, 0.05, 20)
        self.bx("black_plastic", x, y, PT, 5.4, 5.4, 0.4)
        self.occupy(x - 2.8, y - 2.8, x + 2.8, y + 2.8)
        self.ac(x, y, 3.1, self.cfg["silk"], z=0.5)
        self.ac(x, y, 2.95, self.cfg["mask"], z=0.51)

    def battery(self, x, y):
        k = self.k
        pp.tube_ring(k["black_plastic"], (x * MM, y * MM, (PT + 1.5) * MM), 10.2 * MM, 11.6 * MM, 3.0 * MM, seg=32)
        self.bx("black_plastic", x, y - 11.0, PT, 6.0, 3.0, 3.6, bevel=0.3)
        uv, ctx = self.mark(20.0, 20.0, 14.0, "#b9bcc0")
        with ctx as a:
            a.text("CR2032", 10.0, 12.0, 2.6, "#2a2b2e", font="arialbd")
            a.text("3V", 10.0, 8.4, 2.2, "#2a2b2e", font="arialbd")
            a.text("+", 10.0, 4.4, 3.4, "#2a2b2e", font="arialbd")
            a.ring(10.0, 10.0, 9.3, 9.8, "#a2a5aa", z=0.2)
        side = self.marks.swatch("#a9acb0")
        m = self.top_map(uv, x, y, PT + 3.4, 20.0, 20.0, rest=side)
        pp.cyl(k[self.MT], (x * MM, y * MM, (PT + 0.4 + 1.5) * MM), 10.0 * MM, 3.0 * MM, "z", 32, 0.0003, uv=m)
        self.bx("steel", x + 9.0, y, PT + 3.2, 5.0, 4.0, 0.3)
        self.occupy(x - 12, y - 13, x + 12, y + 12)
        self.at("BAT", x, y + 13.8, 1.6)

    def passives(self):
        """SMD capacitors and resistors placed the way real layouts look: short aligned rows of identical
        parts (decoupling arrays), each zone with one preferred orientation."""
        rnd = self.rnd
        zones = [(-26, 20, -2, 112, 80, 90), (-24, -40, -14, -32, 10, 0), (2, -40, 76, -30, 30, 0), (-48, -58, -16, -50, 14, 0),
                 (-45, -100, -18, -82, 16, 90), (-110, -60, -104, -36, 8, 90), (-100, -58, -60, -50, 16, 0), (-108, -122, -46, -114, 20, 0),
                 (-44, -140, -16, -132, 12, 0), (80, -132, 118, -36, 46, 90), (78, -28, 94, 30, 30, 0), (40, -100, 76, -92, 14, 0),
                 (-110, 64, -60, 95, 30, 90), (-110, 128, -60, 140, 18, 0), (-22, 120, -4, 128, 10, 0), (48, 126, 70, 138, 12, 90),
                 (-14, -122, 10, -112, 10, 0), (64, -134, 76, -116, 8, 90), (-96, -136, -60, -130, 12, 0), (-58, 18, -27, 24, 8, 0),
                 (-104, 40, -96, 58, 10, 90), (2, -138, 12, -126, 8, 0)]
        for (x0, y0, x1, y1, n, ang) in zones:
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            placed, tries = 0, 0
            while placed < n and tries < n * 12:
                tries += 1
                big = rnd.random() < 0.3
                L, W, H = (1.6, 0.8, 0.8) if big else (1.0, 0.5, 0.5)
                body = "ceramic" if rnd.random() < 0.7 else "chip_black"
                count = rnd.randint(3, 8)
                pitch = W + (0.55 if big else 0.45)          # parts side by side across their width
                # row direction: perpendicular to the part's length
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
                    for sg in (-1, 1):
                        o = pp.rot("z", ang) @ Vector((sg * (L / 2 - 0.1), 0, 0))
                        pw, ph = (0.5, W + 0.2) if ang == 0 else (W + 0.2, 0.5)
                        self.ar(x + o.x - pw / 2, y + o.y - ph / 2, x + o.x + pw / 2, y + o.y + ph / 2, self.cfg["pad"], 0.36)
                    self.occupy(x - hw, y - hh, x + hw, y + hh, 0.05)
                    placed += 1
                # one designator per row, beside its first part
                fx, fy = spots[0]
                lab = ("C" if body == "ceramic" else "R") + str(rnd.randint(100, 999))
                if ang == 0:
                    self.at(lab, fx - L / 2 - 0.3, fy, 0.7, font="narrowbd", ax="RIGHT", z=0.55)
                else:
                    self.at(lab, fx, fy - L / 2 - 0.25, 0.7, font="narrowbd", ay="TOP", z=0.55)

    # ---------------------------------------------------------------- PCB artwork: traces, vias, print
    def traces(self):
        cfg = self.cfg
        rnd = random.Random(7 if self.v5 else 8)
        tc = cfg["trace"]
        # copper pours (power planes) under the mask
        pour = cfg["pour"]
        self.apoly([(-14, 124), (50, 124), (50, 151), (-14, 151)], pour, z=0.1)
        self.apoly([(64, 28), (98, 28), (98, 130), (64, 130)], pour, z=0.1)
        self.apoly([(-120, 30), (-100, 30), (-100, 96), (-120, 96)], pour, z=0.1)
        self.apoly([(78, -140), (120, -140), (120, -26), (78, -26)], pour, z=0.1)
        # DDR bus: byte lanes from the socket to the DIMMs, with length-matching serpentines
        for lane in range(8):
            y0 = 40.0 + lane * 9.0
            for i in range(8):
                y = y0 + i * 0.6
                pts = [(2.0, y), (-6.0 - (lane % 3) * 2.0, y)]
                if i % 2 == 0 and lane % 2 == 0:
                    xs = -8.0 - (lane % 3) * 2.0
                    for kk in range(4):
                        pts += [(xs - kk * 1.6, y), (xs - kk * 1.6, y + 0.25), (xs - kk * 1.6 - 0.8, y + 0.25), (xs - kk * 1.6 - 0.8, y)]
                pts += [(-26.8, y)]
                self.aline(pts, 0.16, tc, z=0.2, joins=False)
        # PCIe lanes: pairs from the socket down to the x16 slot
        for p in range(16):
            x = 10.0 + p * 2.6
            for d in (0.0, 0.45):
                xx = x + d
                self.aline([(xx, 24.0), (xx, 6.0), (xx - 4.0, 2.0), (xx - 4.0, -40.0)], 0.16, tc, z=0.2, joins=False)
        # chipset uplink and SATA / USB fan-out
        for i in range(10):
            o = i * 0.6
            self.aline([(-6.0, 30.0 - o), (-20.0 - o, 16.0), (-20.0 - o, -36.0), (-48.0 - o, -60.0)], 0.16, tc, z=0.2, joins=False)
        for i in range(8):
            o = i * 0.6
            self.aline([(-102.0, -66.0 - o * 2), (-110.0, -66.0 - o * 2)], 0.16, tc, z=0.2, joins=False)
            self.aline([(-60.0, -112.0 - o), (-60.0, -118.0 - o), (-88.0, -118.0 - o), (-96.0, -130.0 - o * 0.5)], 0.16, tc, z=0.2, joins=False)
        for i in range(12):
            o = i * 0.6
            self.aline([(-50.0, -64.0 - o), (-20.0, -64.0 - o)], 0.16, tc, z=0.2, joins=False)
            self.aline([(76.0, -30.0 - o), (94.0, -30.0 - o), (100.0, -24.0 - o)], 0.16, tc, z=0.2, joins=False)
        # random 45-degree routing fill
        for n in range(900):
            x, y = rnd.uniform(-120, 120), rnd.uniform(-150, 150)
            pts = [(x, y)]
            d = rnd.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
            for s in range(rnd.randint(2, 5)):
                L = rnd.uniform(1.5, 9.0)
                x, y = x + d[0] * L, y + d[1] * L
                x, y = max(-121, min(121, x)), max(-151, min(151, y))
                pts.append((x, y))
                turns = {(1, 0): [(1, 1), (1, -1)], (-1, 0): [(-1, 1), (-1, -1)], (0, 1): [(1, 1), (-1, 1)], (0, -1): [(1, -1), (-1, -1)],
                         (1, 1): [(1, 0), (0, 1)], (1, -1): [(1, 0), (0, -1)], (-1, 1): [(-1, 0), (0, 1)], (-1, -1): [(-1, 0), (0, -1)]}
                d = rnd.choice(turns[d])
                if abs(d[0]) and abs(d[1]):
                    L2 = rnd.uniform(0.6, 3.0)
                    x, y = x + d[0] * L2, y + d[1] * L2
                    pts.append((x, y))
                    d = rnd.choice(turns[d])
            w = rnd.choice([0.15, 0.15, 0.2, 0.3, 0.5])
            self.aline(pts, w, tc, z=0.2)
            if rnd.random() < 0.7:
                self.ac(pts[-1][0], pts[-1][1], 0.35, cfg["via"], z=0.25, seg=8)
                self.ac(pts[0][0], pts[0][1], 0.35, cfg["via"], z=0.25, seg=8)
        # via fields
        for n in range(1800):
            x, y = rnd.uniform(-120, 120), rnd.uniform(-150, 150)
            self.ac(x, y, rnd.choice([0.3, 0.3, 0.35, 0.45]), cfg["via"], z=0.25, seg=8)
        for n in range(160):
            x, y = rnd.uniform(-120, 120), rnd.uniform(-150, 150)
            self.ac(x, y, 0.22, "#8d8f91", z=0.26, seg=8)

    def silkscreen(self):
        cfg = self.cfg
        s = cfg["silk"]
        deco = cfg["deco"]
        # DIMM labels below the slots and a legend
        for i, x in enumerate(DIMM_X):
            dx = {0: 0.0, 1: 1.4, 2: -3.4, 3: 0.0}[i]
            self.at(DIMM_NAMES[i], x + dx, -9.6, 1.6, font="arialbd")
        self.at(f"{cfg['mem']}_DIMM", -64.0, 26.0, 1.6, rot=90)
        self.at("PCIEX16_1", -36.0, PCIE16_Y + 0.0, 1.8, font="arialbd")
        self.at("PCIEX1_1", 40.0, self.slot_ys[1], 1.5, font="arialbd", ax="RIGHT")
        self.at("PCIEX16_2", -36.0, self.slot_ys[2], 1.6, font="arialbd")
        self.at("PCIEX1_2", 40.0, self.slot_ys[3], 1.5, font="arialbd", ax="RIGHT")
        self.at("SOCKET " + cfg["sock"], S[0] - 22.0, S[1] - 39.5 if self.v5 else S[1] - 40.5, 1.6)
        # brand print and decorative graphics in the free area in front of the slots
        bx_, by_ = -72.0, -27.0
        for i in range(14):
            x0 = -112.0 + i * 3.2
            self.apoly([(x0, -50.0), (x0 + 1.2, -50.0), (x0 + 13.2, -16.0), (x0 + 12.0, -16.0)], deco, z=0.3)
        self.at("RIDGE", bx_, by_ + 4.0, 9.0, col=s, font="agency")
        self.at(cfg["model"], bx_, by_ - 6.0, 3.6, col=cfg["accent"], font="agency")
        self.aline([(bx_ - 22, by_ - 10.5), (bx_ + 22, by_ - 10.5)], 0.35, s, z=0.55)
        # angular graphic between the DIMMs and the 24-pin
        for i in range(9):
            y0 = -2.0 + i * 3.0
            self.apoly([(-104.0, y0), (-84.0, y0), (-80.0, y0 + 1.1), (-104.0, y0 + 1.1)], deco, z=0.3)
        self.apoly([(-100.0, 34.0), (-62.0, 34.0), (-62.0, 34.5), (-100.0, 34.5)], deco, z=0.3)
        self.at(cfg["mem"] + " OPTIMISED", -82.0, 37.0, 1.6, col=cfg["accent"], font="arialbd")
        self.at("4 x DIMM  up to " + ("192GB" if self.v5 else "128GB"), -82.0, 31.6, 1.1, font="narrowbd")
        # corner info
        self.at("REV 1.02", 70.0, -151.0, 1.0, font="narrowbd")
        self.at(f"RIDGE {cfg['model']}", -60.0, 150.5, 1.2, font="arialbd")
        self.at("94V-0  E254761", -6.0, -151.2, 0.9, font="narrowbd")
        # hole labels
        for i, (x, y) in enumerate(HOLES):
            pass

    # ---------------------------------------------------------------- hitboxes
    def hit_boxes(self):
        boxes = [((0.0, 0.0, 0.8), (244.0, 305.0, 1.6)), ((45.0, 85.0, 8.0), (120.0, 140.0, 14.0)),
                 ((110.5, 75.0, 19.0), (33.0, 160.0, 38.0)), ((-42.0, 67.3, 5.0), (30.0, 150.0, 9.0)),
                 ((10.0, -85.0, 6.0), (180.0, 130.0, 10.0))]
        for i, (p, s) in enumerate(boxes):
            self.anchor(f"A_HIT_{i}", p, s)

    def films(self):
        """Clear protective films (Logs/UNBOXING.md 1.4; anchors only, the game builds the peel meshes): over the
        I/O cover's logo plate (17 x 76 mm, top z 37.1) and the chipset heatsink's logo plate (30 x 26 mm, top
        PT + 9.5), 0.5 mm bigger all round, 0.02 mm above them."""
        y0 = 22.0 if self.v5 else 30.0          # as io_shroud()
        xr = IO_FACE - 1.7
        self.anchor("A_FILM_IO_0", ((99.8 + xr) / 2 + 0.6, (y0 + 151.5) / 2 + 6.0, 37.12), (18.0, 77.0, 1.0),
                    meta="film=clear,on=io_cover_logo,peel_from=-y")
        self.anchor("A_FILM_CHIPSET_0", (-80.0, -88.0, PT + 9.52), (31.0, 27.0, 1.0),
                    meta="film=clear,on=chipset_logo,peel_from=+x")


class _NormalSwatch:
    def __init__(self, normal, sw):
        self.n = Vector(normal)
        self.sw = sw

    def __call__(self, n, pts):
        return self.sw(n, pts) if n.dot(self.n) > 0.7 else None


class _HoleSwatch:
    """Walls of the mounting holes (faces whose normal points at a hole centre)."""

    def __init__(self, sw):
        self.sw = sw

    def __call__(self, n, pts):
        cxy = sum(pts, Vector()) / len(pts)
        for (x, y) in HOLES:
            if (Vector((x * MM, y * MM, cxy.z)) - cxy).length < HOLE_R * MM * 1.2:
                return self.sw(n, pts)
        return None


def _slope(g, p0, p1, width, thick):
    """A sloped strip (along its run in the y-z plane) from p0 to p1 (mm), width along x."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L = d.length
    mid = (a + b) / 2
    ang = math.degrees(math.atan2(d.z, d.y))
    M = pp.rot("x", ang)
    pp.box(g, (mid.x * MM, mid.y * MM, mid.z * MM), (width * MM, L * MM, thick * MM), M)


def _slope_x(g, p0, p1, width, thick):
    """A sloped strip in the x-z plane, width along y."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L = d.length
    mid = (a + b) / 2
    ang = math.degrees(math.atan2(d.z, d.x))
    M = pp.rot("y", -ang)
    pp.box(g, (mid.x * MM, mid.y * MM, mid.z * MM), (L * MM, width * MM, thick * MM), M)


def _strip(g, p0, p1, z0, width, h):
    a, b = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = b - a
    ang = math.degrees(math.atan2(d.y, d.x))
    mid = (a + b) / 2
    pp.box(g, (mid.x * MM, mid.y * MM, (z0 + h / 2) * MM), (d.length * MM, width * MM, h * MM), pp.rot("z", ang))


def _stadium(yc, zc, w, h, seg=6):
    r = h / 2
    pts = []
    for i in range(seg + 1):
        a = -math.pi / 2 + math.pi * i / seg
        pts.append((yc + w / 2 - r + math.cos(a) * r, zc + math.sin(a) * r))
    for i in range(seg + 1):
        a = math.pi / 2 + math.pi * i / seg
        pts.append((yc - w / 2 + r + math.cos(a) * r, zc + math.sin(a) * r))
    return pts


# ==================================================================== I/O shield

def build_shield(bid, board):
    """A stamped steel plate with the port cut-outs of `board` (a built Board), printed labels and the
    springy edge flange. Frame: board axes, origin at the plate centre."""
    cfg = BOARDS[bid]
    sid = cfg["shield"]
    c.reset()
    yc0, zc0 = (IO_Y0 + IO_Y1) / 2, (IO_Z0 + IO_Z1) / 2
    W, H = 158.75, 44.45
    painted = board.v5
    bg = "#1a1b1e" if painted else "#b9bcc1"
    ink = "#e9e9e9" if painted else "#1c1c1c"
    at = pp.Atlas(1024, 2048, bg=bg)
    # art: the outer face seen from behind the case: image right = +z (component side), up = +y
    r, uv, ctx = at.panel(H, W, 12.5, bg=bg)
    def A(y, z):
        return (z - zc0) + H / 2, (y - yc0) + W / 2
    with ctx as a:
        rnd = random.Random(5)
        if not painted:
            for i in range(240):
                v = rnd.uniform(0, W)
                a.line([(0, v), (H, v)], rnd.uniform(0.05, 0.2), pp.shade(bg, rnd.uniform(0.92, 1.06)), z=0.1, joins=False)
        for kind, outline in board.shield_cuts:
            ys = [p[0] for p in outline]
            zs = [p[1] for p in outline]
            u0, v0 = A(max(ys), min(zs))
            u1, v1 = A(min(ys), max(zs))
            if kind == "rect":
                a.frame_rect(min(u0, u1) - 0.9, min(v0, v1) - 0.9, max(u0, u1) + 0.9, max(v0, v1) + 0.9, 0.25, pp.shade(bg, 0.8 if not painted else 1.6), z=0.2)
        for (y, lab, ztop) in board.shield_labels:
            z0 = min(ztop + 1.6, IO_Z1 - 6.0)
            u, v = A(y, z0)
            a.text(lab, u, v, 1.5, ink, font="arialbd", ax="LEFT", fit=max(4.0, IO_Z1 - 1.0 - z0))
        u, v = A(-1.0, IO_Z1 - 3.0)
        a.text(cfg["model"], u, v, 1.7, ink, font="agency", fit=7.0)
    pp.PREVIEW_TEX[sid] = (0.6, 0.35) if not painted else (0.2, 0.45)
    edge = at.swatch(pp.shade(bg, 0.85))
    at.render(pp.tex_path(sid))
    root = c.root(sid)
    k = pp.Kit(sid)
    T = "tex_" + sid
    t = 0.5
    # plate with holes in the (y, z) plane (local coords relative to the plate centre)
    out = pp.rounded_rect(0, 0, W, H, 1.0, 2)
    loops = [[(p[0] * MM, p[1] * MM) for p in out]]
    for kind, outline in board.shield_cuts:
        pts = [((p[0] - yc0) * MM, (p[1] - zc0) * MM) for p in outline]
        loops.append(pts)
    M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
    mapper = pp.MultiMap([pp.Planar(uv, (t / 2 * MM, 0, 0), (1, 0, 0), (0, 1, 0), (H * MM, W * MM)), edge])
    pp.prism(k[T], loops, -t / 2 * MM, t / 2 * MM, M=M, uv=mapper)
    # flange folded back into the case on all four edges, with spring fingers
    fl = 3.2
    g = k[T]
    for s in (-1, 1):
        pp.box(g, ((-fl / 2) * MM, s * (W / 2 - t / 2) * MM, 0), (fl * MM, t * MM, (H - 1.0) * MM), uv=edge)
        pp.box(g, ((-fl / 2) * MM, 0, s * (H / 2 - t / 2) * MM), (fl * MM, (W - 1.0) * MM, t * MM), uv=edge)
        for j in range(9):
            yy = -W / 2 + 10 + j * (W - 20) / 8
            _slope_x(g, (-fl - 0.2, yy, s * (H / 2 - 0.2)), (-fl - 3.6, yy, s * (H / 2 + 0.8)), 4.0, 0.3)
    # grounding fingers bent inward above the USB and LAN cut-outs
    for kind, outline in board.shield_cuts:
        if kind != "rect":
            continue
        ys = [p[0] for p in outline]
        zs = [p[1] for p in outline]
        wy = max(ys) - min(ys)
        if wy < 9.0:
            continue
        for f in range(2):
            yy = (min(ys) + max(ys)) / 2 - yc0 + (f - 0.5) * wy * 0.45
            zz = max(zs) - zc0
            _slope_x(g, (-0.2, yy, zz - 0.2), (-1.8, yy, zz - 0.9), 2.4, 0.25)
    k.finish(root)
    c.anchor("A_HIT_0", (0, 0, 0), (0.004, W * MM, H * MM), root, meta=f"board_pose={SHIELD_X * MM:.4f},{yc0 * MM:.5f},{zc0 * MM:.5f}")
    c.join_by_tag(root, sid)
    c.export(root, sid)
    pp.report(root)
    pp.preview(root, sid, views=((90, 10), (60, 35)), size=(960, 720), dist=0.3)
    return root


def build(bid, previews=True):
    b = Board(bid)
    root = b.build()
    if previews:
        pp.preview(root, bid, views=((15, 55), (-35, 40), (60, 35)), size=(1280, 960), dist=0.62, zup=True)
        pp.preview(root, bid, views=((-25, 50),), size=(1280, 960), dist=0.2, target=(0.03, 0.06, 0.01), start=3, zup=True)
        pp.preview(root, bid, views=((50, 30),), size=(1280, 960), dist=0.2, target=(0.1, 0.07, 0.015), start=4, zup=True)
        pp.preview(root, bid, views=((-60, 45),), size=(1280, 960), dist=0.2, target=(-0.08, -0.1, 0.005), start=5, zup=True)
        pp.preview(root, bid, views=((-110, 40),), size=(1280, 960), dist=0.16, target=(-0.07, 0.11, 0.008), start=6, zup=True)
        pp.preview(root, bid, views=((30, 40),), size=(1280, 960), dist=0.16, target=(0.03, -0.03, 0.006), start=7, zup=True)
        pp.preview(root, bid, views=((-20, 35),), size=(1280, 960), dist=0.14, target=(0.0, -0.14, 0.004), start=8, zup=True)
        pp.preview(root, bid, views=((-100, 20),), size=(1280, 960), dist=0.12, target=(-0.115, -0.07, 0.006), start=9, zup=True)
    build_shield(bid, b)
    return root


def main(ids=None):
    for bid in ids or list(BOARDS):
        build(bid)


if __name__ == "__main__":
    main(c.args() or None)
