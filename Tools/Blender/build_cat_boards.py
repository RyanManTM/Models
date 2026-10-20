r"""
build_cat_boards.py - catalogue 12: motherboards (8 desktop ATX boards and 2 server boards) and their I/O shields.

    blender -b --factory-startup -P Tools/Blender/build_cat_boards.py -- [ids...] [--nopreview]

Desktop boards: build_board.Board subclassed for looks only (CatBoard), as build_parts_d.py did for mb_ridge_x5. No
method that creates an anchor is overridden, so every anchor is the layout sibling's by construction:
  Socket V5 + DDR5 (mb_ridge_b5's layout)   mb_aegis_b650_bulwark, mb_aegis_x870e_vanguard, mb_mako_b650_harpoon,
                                             mb_kestrel_b650_glide
  Socket L17 + DDR5 (mb_ridge_z4's layout, DDR5 notch)
                                             mb_aegis_z790_keystone, mb_mako_z790_riptide, mb_kestrel_z790_talon
  Socket L17 + DDR4 (mb_ridge_z4's layout)  mb_ridge_b760_d4
Each board also builds its I/O shield io_<board without the mb_ prefix>.

Server boards (new contracts, SSI-EEB 330 x 305 mm; see docs/reports/cat_boards.md): built by server_boards.py.

With no ids it builds all of them. Each model writes Assets/Resources/Models/<id>.fbx, its textures, previews
Logs/ModelPreviews/<id>_<n>.png and Logs/ModelPreviews/<id>_report.txt; the whole run appends to
Logs/ModelPreviews/cat_boards_report.txt.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import parts_pcb as pp  # noqa: E402
import build_board as BB  # noqa: E402
from mathutils import Vector  # noqa: E402

PREVIEW = [True]
PT, MM = BB.PT, BB.MM

# ---------------------------------------------------------------- configs
# cfg keys are build_board's (mask/trace/... colours, plain tags for heat/heat2/latch/shroud) plus "style", which
# only CatBoard reads. Colours in a style are a plain material tag or '#rrggbb' (painted through the marks atlas).

_DARK_PCB = dict(mask="#141517", trace="#1d2024", pour="#181a1d", via="#2a2e33", pad="#b6a982")

BOARDS = {
    # ---- Socket V5 + DDR5 (mb_ridge_b5 layout)
    "mb_aegis_b650_bulwark": dict(
        sock="V5", mem="DDR5", model="B650-PLUS", chipset="AB650", shield="io_aegis_b650_bulwark",
        **_DARK_PCB, silk="#e3dccb", deco="#6f6446", accent="#c8a862", heat="paint_black", heat2="alu_dark",
        latch="connector_black", shroud="paint_black", plate_bg="#1a1b1c", plate_ink="#d9c48f", plate_acc="#c8a862",
        style=dict(brand="AEGIS", series="BULWARK", full="BULWARK GAMING B650-PLUS WIFI", logo_font="impact",
                   heat="#2b2c2d", trim="#b49a62", dark="#151617", vrm="armour", vrm_h=(30.0, 34.0),
                   io="armour", io_rgb=False, chip="armour", armour="x16", armour_col="steel", slot="connector_black",
                   dimm=("connector_black", "connector_black"), silk="tactical", m2_trim="#b49a62", m2b=False,
                   shield_painted=True, preattached=False)),
    "mb_aegis_x870e_vanguard": dict(
        sock="V5", mem="DDR5", model="X870E-E", chipset="AX870E", shield="io_aegis_x870e_vanguard",
        mask="#0f1012", trace="#181a1e", pour="#131518", via="#262a30", pad="#b6a982", silk="#cfd3d8",
        deco="#2c3036", accent="#e0304a", heat="paint_black", heat2="alu",
        latch="connector_black", shroud="paint_black", plate_bg="#111214", plate_ink="#eceef2", plate_acc="#e0304a",
        style=dict(brand="AEGIS", series="VANGUARD", full="VANGUARD X870E-E GAMING WIFI", logo_font="agency",
                   heat="#1c1d20", trim="alu", dark="#0c0d0e", vrm="armour", vrm_h=(34.0, 37.0),
                   io="rgb", io_rgb=True, chip="slab", armour="both", armour_col="steel", slot="connector_black",
                   dimm=("connector_black", "connector_black"), silk="angular", m2_trim="alu", m2b=True,
                   shield_painted=True, preattached=True)),
    "mb_mako_b650_harpoon": dict(
        sock="V5", mem="DDR5", model="B650 HARPOON", chipset="MB650", shield="io_mako_b650_harpoon",
        **_DARK_PCB, silk="#d6d8dc", deco="#3a3d42", accent="#9ea3aa", heat="steel_dark", heat2="alu",
        latch="connector_black", shroud="paint_black", plate_bg="#202225", plate_ink="#e4e6ea", plate_acc="#9ea3aa",
        style=dict(brand="MAKO", series="HARPOON", full="HARPOON B650 WIFI", logo_font="bahn",
                   heat="#4a4d52", trim="#26282b", dark="#17181a", vrm="slab", vrm_h=(31.0, 35.0),
                   io="slab", io_rgb=False, chip="slab", armour="x16", armour_col="steel", slot="connector_black",
                   dimm=("connector_black", "connector_black"), silk="lines", m2_trim="#26282b", m2b=True,
                   shield_painted=True, preattached=True)),
    "mb_kestrel_b650_glide": dict(
        sock="V5", mem="DDR5", model="B650 GLIDE G", chipset="KB650", shield="io_kestrel_b650_glide",
        mask="#e6e7e8", trace="#dcdee0", pour="#e0e2e4", via="#c3c6ca", pad="#b6a982", silk="#3b3f45",
        deco="#cfd2d6", accent="#8a9099", heat="paint_white", heat2="alu",
        latch="white_plastic", shroud="white_plastic", plate_bg="#f2f3f4", plate_ink="#2a2d32", plate_acc="#8a9099",
        style=dict(brand="KESTREL", series="GLIDE", full="B650 GLIDE G", logo_font="agency",
                   heat="paint_white", trim="alu", dark="#bfc3c8", vrm="fins", vrm_h=(31.0, 35.0),
                   io="slab", io_rgb=True, chip="plate", armour="x16", armour_col="alu", slot="white_plastic",
                   dimm=("white_plastic", "white_plastic"), silk="dots", m2_trim="alu", m2b=True,
                   shield_painted=False, preattached=True)),
    # ---- Socket L17 + DDR5 (mb_ridge_z4 layout with the DDR5 DIMM notch)
    "mb_aegis_z790_keystone": dict(
        sock="L17", mem="DDR5", model="Z790-A", chipset="AZ790", shield="io_aegis_z790_keystone",
        **_DARK_PCB, silk="#eceef0", deco="#3d4248", accent="#c9ced5", heat="alu", heat2="paint_white",
        latch="white_plastic", shroud="paint_white", plate_bg="#eef0f2", plate_ink="#202327", plate_acc="#8d949c",
        style=dict(brand="AEGIS", series="KEYSTONE", full="KEYSTONE Z790-A WIFI", logo_font="arialbd",
                   heat="alu", trim="paint_white", dark="#2a2d31", vrm="slab", vrm_h=(28.0, 33.0),
                   io="slab", io_rgb=False, chip="plate", armour="x16", armour_col="alu", slot="connector_black",
                   dimm=("white_plastic", "grey_plastic"), silk="circuit", m2_trim="paint_white", m2b=True,
                   shield_painted=False, preattached=True, chip_rgb=True)),
    "mb_mako_z790_riptide": dict(
        sock="L17", mem="DDR5", model="Z790 RIPTIDE", chipset="MZ790", shield="io_mako_z790_riptide",
        mask="#d3d6d9", trace="#c8cbcf", pour="#cdd0d4", via="#a9aeb4", pad="#b6a982", silk="#2c3036",
        deco="#b9bdc3", accent="#5a6068", heat="paint_white", heat2="alu",
        latch="white_plastic", shroud="paint_white", plate_bg="#f0f1f2", plate_ink="#22252a", plate_acc="#7c838c",
        style=dict(brand="MAKO", series="RIPTIDE", full="RIPTIDE Z790 WIFI", logo_font="bahn",
                   heat="paint_white", trim="alu", dark="#a9aeb4", vrm="slab", vrm_h=(31.0, 35.0),
                   io="rgb", io_rgb=True, chip="slab", armour="both", armour_col="alu", slot="white_plastic",
                   dimm=("white_plastic", "white_plastic"), silk="lines", m2_trim="alu", m2b=True,
                   shield_painted=False, preattached=True)),
    "mb_kestrel_z790_talon": dict(
        sock="L17", mem="DDR5", model="Z790 TALON", chipset="KZ790", shield="io_kestrel_z790_talon",
        **_DARK_PCB, silk="#e2e2e2", deco="#5a3418", accent="#f07a1e", heat="steel_dark", heat2="alu_dark",
        latch="connector_black", shroud="paint_black", plate_bg="#141516", plate_ink="#f0f0f0", plate_acc="#f07a1e",
        style=dict(brand="KESTREL", series="TALON", full="Z790 TALON ELITE AX", logo_font="agency",
                   heat="#2a2b2e", trim="#f07a1e", dark="#121314", vrm="fins", vrm_h=(32.0, 36.0),
                   io="armour", io_rgb=True, chip="armour", armour="x16", armour_col="steel", slot="connector_black",
                   dimm=("connector_black", "connector_black"), silk="angular", m2_trim="#f07a1e", m2b=True,
                   shield_painted=True, preattached=True)),
    # ---- Socket L17 + DDR4 (mb_ridge_z4 layout)
    "mb_ridge_b760_d4": dict(
        sock="L17", mem="DDR4", model="B760 PRO D4", chipset="RB760", shield="io_ridge_b760_d4",
        **_DARK_PCB, silk="#e8e8e6", deco="#30343a", accent="#9aa2ad", heat="paint_black", heat2="alu",
        latch="connector_black", shroud="black_plastic", plate_bg="#141517", plate_ink="#e8e8e6", plate_acc="#9aa2ad",
        style=dict(brand="RIDGE", series="PRO", full="B760 PRO D4", logo_font="agency",
                   heat="#202225", trim="alu", dark="#101112", vrm="budget", vrm_h=(20.0, 24.0),
                   io="budget", io_rgb=False, chip="low", armour="none", armour_col="steel", slot="connector_black",
                   dimm=("connector_black", "grey_plastic"), silk="stripes", m2_trim="alu", m2b=False,
                   shield_painted=False, preattached=False)),
}

SIBLING = {bid: ("mb_ridge_b5" if cfg["sock"] == "V5" else "mb_ridge_z4") for bid, cfg in BOARDS.items()}
BB.BOARDS.update(BOARDS)


# ---------------------------------------------------------------- the styled board

class CatBoard(BB.Board):
    """A layout sibling's Board with a catalogue look. Overrides only look methods (vrm, chipset, io_shroud,
    silkscreen, dimm_slot, pcie_slot) and extends m2 (super first); none of them creates an anchor."""

    def __init__(self, bid):
        super().__init__(bid)
        self.st = self.cfg["style"]
        # short texture names: "<prefix>_<tag>#<tag>" must stay under Blender's 63-character name limit
        self.tkey = bid[3:]
        self.MT = "tex_" + self.tkey + "_mk"
        self.PCBT = "tex_" + self.tkey + "_pcb"

    def build(self):
        """build_board.Board.build with the short texture names and mesh prefix."""
        c.reset()
        self.pcb = pp.Art(BB.BW, BB.BH, 2048, 2560, bg=self.cfg["mask"])
        self.marks = pp.Atlas(2048, 2048, bg="#101010")
        self.root = c.root(self.bid)
        for step in ("pcb_swatches", "mount_holes", "socket", "vrm", "dimms", "pcie", "m2", "chipset", "rear_io",
                     "power_connectors", "headers", "sata", "debug_leds", "misc", "passives", "traces", "silkscreen",
                     "pcb_mesh"):
            getattr(self, step)()
        self.pcb.render(pp.tex_path(self.tkey + "_pcb"))
        self.marks.render(pp.tex_path(self.tkey + "_mk"))
        pp.PREVIEW_TEX[self.tkey + "_pcb"] = (0.0, 0.5)
        pp.PREVIEW_TEX[self.tkey + "_mk"] = (0.0, 0.42)
        self.k.finish(self.root)
        for g, an, base in self.moving:
            g.obj(base, self.anchors[an])
        self.hit_boxes()
        self.films()
        c.join_by_tag(self.root, "mb")
        c.export(self.root, self.bid)
        pp.report(self.root)
        return self.root

    # ------------------------------------------------ painting primitives (colour = tag or '#rrggbb')
    def paint(self, col):
        if col.startswith("#"):
            return self.k[self.MT], self.marks.swatch(col)
        return self.k[col], None

    def pbox(self, col, cx, cy_, z0, sx, sy, h, bevel=0.0, ang=0.0):
        g, uv = self.paint(col)
        self.bx(None, cx, cy_, z0, sx, sy, h, bevel, uv=uv, ang=ang, g=g)

    def pcyl(self, col, cx, cy_, z0, r, h, seg=16, bevel=0.0):
        g, uv = self.paint(col)
        pp.cyl(g, (cx * MM, cy_ * MM, (z0 + h / 2) * MM), r * MM, h * MM, "z", seg, bevel * MM, uv=uv)

    def pplan(self, col, pts, z0, z1, bevel=0.0):
        """A plan-view outline (board mm) extruded from z0 to z1 with a rounded top rim."""
        g, uv = self.paint(col)
        pp.prism_bevel(g, [(x * MM, y * MM) for x, y in pts], z0 * MM, z1 * MM, bevel * MM, seg=1, uv=uv)

    def yz_shape(self, col, pts, x0, x1, hole=None):
        """A (y, z) outline (board mm) extruded along x from x0 to x1, optionally with a hole."""
        g, uv = self.paint(col)
        M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
        loops = [[(a * MM, b * MM) for a, b in pts]]
        if hole:
            loops.append([(a * MM, b * MM) for a, b in reversed(hole)])
        pp.prism(g, loops, x0 * MM, x1 * MM, M=M, uv=uv)

    def pslope(self, col, p0, p1, width, thick, along):
        """A strip from p0 to p1 (board mm, both on the same a = const line); width along `along` ('x' or 'y')."""
        g, uv = self.paint(col)
        a, b = Vector(p0), Vector(p1)
        d = b - a
        mid = (a + b) / 2
        if along == "x":
            M = pp.rot("x", math.degrees(math.atan2(d.z, d.y)))
            size = (width * MM, d.length * MM, thick * MM)
        else:
            M = pp.rot("y", -math.degrees(math.atan2(d.z, d.x)))
            size = (d.length * MM, width * MM, thick * MM)
        pp.box(g, (mid.x * MM, mid.y * MM, mid.z * MM), size, M, uv=uv)

    # ------------------------------------------------ heatsink frame: a runs along the long axis, b across it
    # (b = 0 on the side that faces the socket). zone = (a0, a1, base, D, along): along 'x' (top heatsink:
    # x = a, y = base + b) or 'y' (rear heatsink: x = base + b, y = a).
    def lbox(self, col, z, a0, a1, b0, b1, z0, z1, bevel=0.0):
        A0, A1, base, D, along = z
        if along == "x":
            self.pbox(col, (a0 + a1) / 2, base + (b0 + b1) / 2, z0, a1 - a0, b1 - b0, z1 - z0, bevel)
        else:
            self.pbox(col, base + (b0 + b1) / 2, (a0 + a1) / 2, z0, b1 - b0, a1 - a0, z1 - z0, bevel)

    def lprof(self, col, z, pts, a0, a1, bevel=0.5):
        """A cross-section (b, height) extruded along the long axis from a0 to a1, both ends rounded."""
        A0, A1, base, D, along = z
        g, uv = self.paint(col)
        if along == "x":
            M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
        else:
            M = pp.frame(x=(1, 0, 0), y=(0, 0, 1), z=(0, 1, 0))
        out = [((base + b) * MM, h * MM) for b, h in pts]
        pp.prism_bevel(g, out, a0 * MM, a1 * MM, bevel * MM, seg=1, M=M, uv=uv, bottom_bevel=bevel * MM)

    def lslope(self, col, z, a0, a1, p0, p1, thick=0.4):
        A0, A1, base, D, along = z
        am = (a0 + a1) / 2
        if along == "x":
            self.pslope(col, (am, base + p0[0], p0[1]), (am, base + p1[0], p1[1]), a1 - a0, thick, "x")
        else:
            self.pslope(col, (base + p0[0], am, p0[1]), (base + p1[0], am, p1[1]), a1 - a0, thick, "y")

    def lplate(self, z, am, bm, top, w, h, draw, bg):
        """A printed plate lying on a heatsink top: w along the long axis, h across; draw(a, w, h) paints it."""
        A0, A1, base, D, along = z
        uv, ctx = self.mark(w, h, 20.0, bg)
        with ctx as a:
            draw(a, w, h)
        pe = self.marks.swatch(bg)
        if along == "x":
            x, y = am, base + bm
            self.bx(self.MT, x, y, top, w, h, 0.5, bevel=0.15, uv=self.top_map(uv, x, y, top + 0.5, w, h, rest=pe))
            # the clear protective film on the top heatsink's printed plate (only the top heatsink has one)
            self.anchor("A_FILM_VRM_0", (x, y, top + 0.52), (w + 1.0, h + 1.0, 1.0),
                        meta="film=clear,on=vrm_logo,peel=+x,tab=-x+y")
        else:
            x, y = base + bm, am
            self.bx(self.MT, x, y, top, h, w, 0.5, bevel=0.15, uv=self.top_map(uv, x, y, top + 0.5, w, h, up=(1, 0, 0), rest=pe))

    # ------------------------------------------------ VRM
    def chokes_and_caps(self):
        """The sibling's chokes, polymer caps, heat pipe (V5) and memory VRM: same parts, same places."""
        v5, cfg = self.v5, self.cfg
        uv, ctx = self.mark(7.6, 7.6, 16.0, "#2e2f33")
        with ctx as a:
            a.text("R22", 3.8, 4.4, 1.6, "#b8b8b8", font="arialbd")
            a.text("2346", 3.8, 2.4, 0.9, "#8a8a8a", font="arialbd")
        choke_side = self.marks.swatch("#2a2b2e")
        top_row = [-6.0 + i * 9.5 for i in range(6)] if v5 else [-2.0 + i * 9.5 for i in range(5)]
        rear_x = 72.0 if v5 else 78.0
        rear_col = [40.0 + i * 9.5 for i in range(9)] if v5 else [46.0 + i * 9.5 for i in range(7)]
        for n, (x, y) in enumerate([(x, 129.5) for x in top_row] + [(rear_x, y) for y in rear_col]):
            if y > 125.0:
                self.at(f"PL{n + 1}", x, y - 5.3, 0.9, font="narrowbd")
            else:
                self.at(f"PL{n + 1}", x - 5.2, y, 0.9, font="narrowbd", rot=90)
            self.bx(self.MT, x, y, PT, 7.6, 7.6, 5.4, bevel=0.35, uv=self.top_map(uv, x, y, PT + 5.4, 7.6, 7.6, rest=choke_side))
            for s in (-1, 1):
                self.ar(x + s * 2.6 - 1.2, y - 3.2, x + s * 2.6 + 1.2, y + 3.2, cfg["pad"], 0.35)
            self.occupy(x - 4.2, y - 4.2, x + 4.2, y + 4.2)
        if v5:
            pts = [(30.0, 140.0, 3.4), (46.0, 139.5, 3.4), (58.0, 134.6, 3.4), (70.5, 126.5, 3.4), (80.0, 119.0, 3.4), (86.0, 110.0, 3.4)]
            c.tube("heatpipe", [(p[0] * MM, p[1] * MM, p[2] * MM) for p in pts], 1.6 * MM, "nickel", self.root, verts=12)
        caps = [(74.5, 145.0, 3.15, 8.0), (74.5, 137.4, 3.15, 8.0), (-17.5, 129.0, 2.5, 6.0), (-17.5, 136.0, 2.5, 6.0)]
        if v5:
            caps += [(70.0, 33.5, 2.5, 6.0), (63.5, 21.0, 2.5, 6.0), (70.0, 21.0, 2.5, 6.0)]
        else:
            caps += [(75.0, 36.0, 2.5, 6.0), (76.0, 26.0, 2.5, 6.0), (69.0, 26.0, 2.5, 6.0), (2.0, 120.0, 2.5, 6.0), (10.0, 120.0, 2.5, 6.0)]
        for (x, y, rr, h) in caps:
            self.solid_cap(x, y, rr, h)
        for y in (133.0, 123.0):
            self.small_choke(-70.0, y)
            self.mosfet(-81.0, y)
        self.solid_cap(-89.0, 132.0, 2.5, 6.0)
        self.solid_cap(-89.0, 124.0, 2.5, 6.0)

    def vrm_zones(self):
        """(top zone, rear zone): kept clear of the cooler keep-out the way the siblings' heatsinks are."""
        ht, hr = self.st["vrm_h"]
        if self.v5:
            top = (-14.0, 48.0, 133.6, 17.0, "x")
            rear = (26.0, 131.0, 77.4, 18.0, "y")
        else:
            top = (-13.0, 46.0, 133.6, 17.0, "x")
            rear = (32.0, 131.0, 82.6, 12.8, "y")
        if self.st["vrm"] == "budget":
            top = (top[0] + 6.0, top[1] - 4.0, top[2], 14.8, "x")
            rear = (rear[0] + 8.0, rear[1] - 6.0, rear[2], rear[3], "y")
        return (top, ht), (rear, hr)

    def vrm(self):
        self.chokes_and_caps()
        (top, ht), (rear, hr) = self.vrm_zones()
        kind = self.st["vrm"]
        for z, H, is_top in ((top, ht, True), (rear, hr, False)):
            getattr(self, "hs_" + kind)(z, H, is_top)
            A0, A1, base, D, along = z
            if along == "x":
                self.occupy(A0, base, A1, base + D)
            else:
                self.occupy(base, A0, base + D, A1)

    def brand_plate(self, a, w, h, sub=None):
        st, cfg = self.st, self.cfg
        a.text(st["brand"], 1.6, h * 0.5, h * 0.62, cfg["plate_ink"], font=st["logo_font"], ax="LEFT", fit=w * 0.55)
        if sub:
            a.text(sub, w - 1.6, h * 0.5, h * 0.26, cfg["plate_acc"], font="agencyr", ax="RIGHT", fit=w * 0.4)

    def hs_armour(self, z, H, is_top):
        """A solid machined block with a long chamfer toward the socket, cut lines, a trim inlay and slotted fins
        on the socket face (TUF / ROG / AORUS style)."""
        st = self.st
        A0, A1, base, D, along = z
        heat, trim, dark = st["heat"], st["trim"], st["dark"]
        ch = min(10.0, H * 0.34)
        prof = [(0.0, PT + 1.0), (D, PT + 1.0), (D, H), (D * 0.42, H), (0.0, H - ch)]
        self.lprof(heat, z, prof, A0, A1, 0.6)
        # fin slots on the socket face (dark recesses)
        n = int((A1 - A0 - 6) / 3.2)
        for i in range(n):
            a = A0 + 3.0 + i * (A1 - A0 - 6) / max(1, n - 1)
            self.lbox(dark, z, a - 0.5, a + 0.5, -0.08, 0.25, PT + 3.0, H - ch - 2.5)
        # angled cut lines across the top and a trim inlay strip along it
        for f in (0.22, 0.5, 0.78):
            a = A0 + (A1 - A0) * f
            self.lbox(dark, z, a - 0.35, a + 0.35, D * 0.42, D - 0.6, H - 0.05, H + 0.08)
        self.lbox(trim, z, A0 + 3.0, A1 - 3.0, D - 3.4, D - 1.6, H - 0.05, H + 0.35)
        self.lslope(trim, z, A0 + 4.0, A1 - 4.0, (0.9, H - ch + 1.0 + 0.25), (D * 0.42 - 0.6, H - 0.2 + 0.25), 0.35)
        # a stepped block on the far end, the brand armour look
        self.lbox(heat, z, A1 - 9.0, A1 - 1.0, D * 0.5, D - 0.4, H, H + 2.6, 0.5)
        self.lbox(trim, z, A1 - 8.4, A1 - 1.6, D * 0.5 + 0.6, D - 1.0, H + 2.6, H + 2.75)
        if is_top:
            w = min(36.0, A1 - A0 - 16.0)
            self.lplate(z, A0 + 3.0 + w / 2, D * 0.71, H, w, 6.0, lambda a, w, h: self.brand_plate(a, w, h, st["series"]),
                        self.cfg["plate_bg"])

    def hs_slab(self, z, H, is_top):
        """Layered slabs: a finned lower block, a contrasting band, and an upper block with a socket-side
        chamfer and a brushed inlay (MAG / Prime / MPG style)."""
        st = self.st
        A0, A1, base, D, along = z
        heat, trim, dark = st["heat"], st["trim"], st["dark"]
        h1 = PT + (H - PT) * 0.5
        self.lbox(heat, z, A0, A1, 0.0, D, PT + 1.0, h1, 0.5)
        for j in range(4):
            zz = PT + 3.0 + j * (h1 - PT - 4.5) / 3
            self.lbox(dark, z, A0 + 1.0, A1 - 1.0, -0.08, 0.3, zz, zz + 0.9)
        self.lbox(trim, z, A0 + 0.6, A1 - 0.6, 0.8, D - 0.4, h1, h1 + 1.4)
        prof = [(1.2, h1 + 1.4), (D, h1 + 1.4), (D, H), (D * 0.55, H), (1.2, H - 5.0)]
        self.lprof(heat, z, prof, A0 + 1.0, A1 - 1.0, 0.6)
        # diagonal accent lines on the chamfer and a brushed inlay on the top
        self.lbox(trim, z, A0 + 4.0, A1 - 14.0, D * 0.6, D - 1.4, H - 0.05, H + 0.3)
        for i in range(5):
            a = A1 - 12.5 + i * 2.2
            self.lbox(dark, z, a, a + 1.0, D * 0.6, D - 1.4, H - 0.05, H + 0.1)
        self.lslope(dark, z, A0 + 3.0, A1 - 3.0, (1.4, H - 5.0 + 1.2 + 0.2), (D * 0.55 - 0.4, H - 0.4 + 0.2), 0.3)
        if is_top:
            w = min(34.0, A1 - A0 - 22.0)
            self.lplate(z, A0 + 5.0 + w / 2, D * 0.33 + 1.0, H - 3.0, w, 5.0,
                        lambda a, w, h: self.brand_plate(a, w, h, None), self.cfg["plate_bg"])

    def hs_fins(self, z, H, is_top):
        """An exposed fin stack under a cover with a chamfered lip (AORUS / AERO style)."""
        st = self.st
        A0, A1, base, D, along = z
        heat, trim = st["heat"], st["trim"]
        fin = "alu" if trim == "alu" else heat
        self.lbox(heat, z, A0, A1, 0.0, D, PT + 1.0, PT + 6.0, 0.5)
        n = int((A1 - A0 - 2) / 2.4)
        for i in range(n):
            a = A0 + 1.4 + i * (A1 - A0 - 2.8) / (n - 1)
            self.lbox(fin, z, a - 0.45, a + 0.45, 0.6, D - 0.4, PT + 6.0, H - 6.0)
        capz = H - 6.0
        self.lbox(heat, z, A0 - 0.3, A1 + 0.3, 4.0, D, capz, H - 2.0, 0.5)
        self.lslope(heat, z, A0 - 0.3, A1 + 0.3, (4.0, capz + 2.0), (0.2, capz - 2.4), 2.8)
        self.lbox(heat, z, A0 + 2.0, A1 - 2.0, 6.0, D - 1.0, H - 2.0, H, 0.6)
        # the accent line along the cap lip and a slash pattern on the far end
        self.lbox(trim, z, A0 + 1.0, A1 - 1.0, 4.0, 4.9, H - 2.05, H - 1.7)
        for i in range(4):
            a = A1 - 4.0 - i * 2.0
            self.lbox(trim, z, a - 0.5, a + 0.5, 7.0, D - 2.0, H - 0.05, H + 0.25)
        if is_top:
            w = min(34.0, A1 - A0 - 20.0)
            self.lplate(z, A0 + 4.0 + w / 2, (6.0 + D - 1.0) / 2, H, w, 6.0,
                        lambda a, w, h: self.brand_plate(a, w, h, st["series"]), self.cfg["plate_bg"])

    def hs_budget(self, z, H, is_top):
        """A small extruded aluminium heatsink with open fins and a printed stripe (entry boards)."""
        st = self.st
        A0, A1, base, D, along = z
        heat, trim = st["heat"], st["trim"]
        self.lbox(heat, z, A0, A1, 0.0, D, PT + 1.0, PT + 4.5, 0.4)
        n = int((A1 - A0 - 2) / 3.0)
        for i in range(n):
            a = A0 + 1.5 + i * (A1 - A0 - 3.0) / (n - 1)
            self.lbox(heat, z, a - 0.6, a + 0.6, 0.0, D, PT + 4.5, H - 2.0)
        self.lbox(heat, z, A0, A1, 1.5, D, H - 2.0, H, 0.4)
        self.lbox(trim, z, A0 + 2.0, A1 - 2.0, D - 3.0, D - 2.0, H - 0.05, H + 0.2)
        if is_top:
            w = min(26.0, A1 - A0 - 12.0)
            self.lplate(z, A0 + 3.0 + w / 2, (1.5 + D - 3.5) / 2, H, w, 5.0,
                        lambda a, w, h: self.brand_plate(a, w, h, None), self.cfg["plate_bg"])

    # ------------------------------------------------ slots
    def dimm_slot(self, x, body, notch_y):
        i = BB.DIMM_X.index(x)
        super().dimm_slot(x, self.st["dimm"][i % 2], notch_y)

    def pcie_slot(self, xa, xb, yc, armour):
        """build_board's slot with the body colour and armour of the style."""
        k = self.k
        st = self.st
        ch, top, floor = 0.9, PT + 10.5, 6.6
        L, xm = xb - xa, (xa + xb) / 2
        body = st["slot"]
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
        full = L > 50.0
        if full and (st["armour"] == "both" or (st["armour"] == "x16" and armour)):
            a = st["armour_col"]
            for s in (-1, 1):
                self.pbox(a, xm + 0.5, yc + s * 3.95, PT + 0.6, L + 1.0, 0.4, top - PT - 0.3)
                self.pbox(a, xm + 0.5, yc + s * (ch + 3.15) / 2 + s * 0.2, top - 0.1, L + 1.0, 3.25 - ch + 0.6, 0.35)
                for j in range(4):
                    self.pbox(a, xa + 6 + j * 26.0, yc + s * 4.1, PT - 0.6, 2.0, 0.3, 1.4)
            self.pbox(a, xb + 1.2, yc, PT + 0.6, 0.4, 8.3, top - PT - 0.3)
            self.pbox(a, xa - 0.4, yc, top - 0.1, 0.8, 8.3, 0.35)
        self.aframe(xa - 0.6, yc - 4.6, xb + 0.6, yc + 4.6, 0.15)
        self.occupy(xa - 7, yc - 4.6, xb + 1.0, yc + 4.6)

    # ------------------------------------------------ M.2
    def m2(self):
        super().m2()
        st, cfg = self.st, self.cfg
        # a trim stripe on the M.2 heatsink (moves with A_COVER_M2_0)
        g = self.piece(self.MT, "A_COVER_M2_0", "trim")
        sw = self.marks.swatch(st["m2_trim"]) if st["m2_trim"].startswith("#") else None
        if sw is not None:
            for i in range(3):
                self.bx(None, 6.0 + i * 3.0, BB.M2_Y - 9.6, 9.8, 1.4, 4.0, 0.1, uv=sw, g=g)
            self.bx(None, 30.0, BB.M2_Y + 11.0, 9.75, 100.0, 1.2, 0.08, uv=sw, g=g)
        else:
            gm = self.piece(st["m2_trim"], "A_COVER_M2_0", "trim2")
            self.bx(None, 30.0, BB.M2_Y + 11.0, 9.75, 100.0, 1.2, 0.08, g=gm)
            for i in range(3):
                self.bx(None, 6.0 + i * 3.0, BB.M2_Y - 9.6, 9.8, 1.4, 4.0, 0.1, g=gm)
        if not st["m2b"]:
            return
        # a second (fixed, looks only) M.2 heatsink over M2_2, as on mb_ridge_x5
        yc = BB.M2B_Y
        for px in (-20.0, 78.0):
            pp.cyl(self.k["steel"], (px * MM, yc * MM, (PT + (7.2 - PT) / 2) * MM), 2.6 * MM, (7.2 - PT) * MM, "z", 6)
        self.bx(cfg["heat"], 29.0, yc, 7.2, 106.0, 24.0, 2.4, bevel=0.8)
        for i in range(7):
            pp.box(self.k[cfg["heat2"]], ((-14.0 + i * 7.0) * MM, yc * MM, 9.8 * MM), (1.6 * MM, 22.0 * MM, 0.5 * MM), pp.rot("z", 28), 0.0002)
        for px in (-20.0, 78.0):
            pp.tube_ring(self.k["steel"], (px * MM, yc * MM, 9.65 * MM), 1.2 * MM, 2.2 * MM, 0.2 * MM, seg=16)
        uv, ctx = self.mark(30.0, 12.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text("M.2_2", 15.0, 7.4, 4.6, cfg["plate_ink"], font="agency")
            a.line([(3.0, 2.6), (27.0, 2.6)], 0.5, cfg["plate_acc"])
        pe = self.marks.swatch(cfg["plate_bg"])
        self.bx(self.MT, 62.0, yc, 9.6, 30.0, 12.0, 0.5, bevel=0.2, uv=self.top_map(uv, 62.0, yc, 10.1, 30.0, 12.0, rest=pe))
        self.anchor("A_FILM_M2_1", (62.0, yc, 10.12), (31.0, 13.0, 1.0), meta="film=clear,on=m2_2_logo,peel=-x,tab=+x+y")
        self.occupy(-24.0, yc - 12.0, 82.0, yc + 12.0)

    # ------------------------------------------------ chipset (the logo plate stays where A_FILM_CHIPSET_0 is)
    def chipset(self):
        st, cfg = self.st, self.cfg
        heat, trim, dark = st["heat"], st["trim"], st["dark"]
        x0, x1, y0, y1 = -102.0, -50.0, -112.0, -62.0
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        kind = st["chip"]
        top = PT + 8.9
        if kind == "armour":
            self.pbox(heat, xm, ym, PT + 1.0, x1 - x0, y1 - y0, 4.2, 0.8)
            pts = [(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x1 - 1, y1 - 14), (x1 - 15, y1 - 1), (x0 + 1, y1 - 1)]
            self.pplan(heat, pts, PT + 5.2, top, 0.8)
            self.pplan(trim, [(x1 - 2.0, y1 - 15.5), (x1 - 2.0, y1 - 12.0), (x1 - 12.0, y1 - 2.0), (x1 - 15.5, y1 - 2.0)], top - 0.1, top + 0.3)
            for i in range(6):
                self.pbox(dark, x0 + 4.0 + i * 2.2, ym, top - 0.05, 0.8, (y1 - y0) - 8.0, 0.12)
        elif kind == "slab":
            self.pbox(heat, xm, ym, PT + 1.0, x1 - x0, y1 - y0, 3.4, 0.8)
            self.pbox(trim, xm, ym, PT + 4.4, x1 - x0 - 2.0, y1 - y0 - 2.0, 1.0)
            pts = [(x0 + 1.5, y0 + 1.5), (x1 - 1.5, y0 + 1.5), (x1 - 1.5, y1 - 1.5), (x0 + 10.0, y1 - 1.5), (x0 + 1.5, y1 - 10.0)]
            self.pplan(heat, pts, PT + 5.4, top, 0.8)
            for i in range(8):
                self.pplan(dark, [(x0 + 3.0 + i * 2.4, y0 + 3.0), (x0 + 4.0 + i * 2.4, y0 + 3.0), (x0 + 12.0 + i * 2.4, y0 + 11.0),
                                  (x0 + 11.0 + i * 2.4, y0 + 11.0)], top - 0.05, top + 0.08)
        elif kind == "plate":
            self.pbox(heat, xm, ym, PT + 1.0, x1 - x0, y1 - y0, 6.0, 0.8)
            self.pbox(trim, xm, ym, PT + 7.0, x1 - x0 - 3.0, y1 - y0 - 3.0, top - PT - 7.0, 0.6)
            self.pbox(dark, x0 + 1.6, ym, PT + 3.0, 0.3, y1 - y0 - 8.0, 2.0)
        else:   # low
            self.pbox(heat, xm + 4.0, ym, PT + 1.0, x1 - x0 - 12.0, y1 - y0 - 10.0, 3.0, 0.5)
            n = 9
            for i in range(n):
                self.pbox(heat, x0 + 9.0 + i * 4.4, ym, PT + 4.0, 1.4, y1 - y0 - 10.0, top - PT - 4.0)
            self.pbox(heat, xm - 4.0, ym - 1.0, top - 2.0, 32.0, 28.0, 2.0, 0.4)
        if st.get("chip_rgb"):
            pp.box(self.k["rgb"], ((x0 + 0.4) * MM, ym * MM, (PT + 4.0) * MM), (0.8 * MM, (y1 - y0 - 10) * MM, 1.2 * MM))
        uv, ctx = self.mark(30.0, 26.0, 20.0, cfg["plate_bg"])
        with ctx as a:
            a.text(st["brand"], 15.0, 17.5, 6.4, cfg["plate_ink"], font=st["logo_font"], fit=26.0)
            a.line([(4.0, 12.6), (26.0, 12.6)], 0.4, cfg["plate_acc"])
            a.text(st["series"], 15.0, 8.6, 3.6, cfg["plate_acc"], font="agency", fit=26.0)
            a.text(cfg["model"], 15.0, 4.4, 1.8, cfg["plate_ink"], font="arialbd", fit=26.0)
        pe = self.marks.swatch(cfg["plate_bg"])
        px, py_ = xm - 4.0, ym - 1.0
        self.bx(self.MT, px, py_, top, 30.0, 26.0, 0.6, bevel=0.3, uv=self.top_map(uv, px, py_, top + 0.6, 30.0, 26.0, rest=pe))
        for (ex, ey) in ((x0 + 4, y0 + 4), (x1 - 4, y1 - 4)):
            self.cy("steel", ex, ey, top - 0.2, 1.6, 0.6, 12, bevel=0.2)
        self.occupy(x0, y0, x1, y1)
        self.aframe(x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.15)

    # ------------------------------------------------ I/O cover (the logo plate stays where A_FILM_IO_0 is)
    def io_shroud(self):
        st, cfg = self.st, self.cfg
        kind = st["io"]
        heat, trim, dark = st["heat"], st["trim"], st["dark"]
        y0, y1 = (22.0, 151.5) if self.v5 else (30.0, 151.5)
        xr = BB.IO_FACE - 1.7
        ym = (y0 + y1) / 2
        g, uv = self.paint(heat)
        M = pp.frame(x=(1, 0, 0), y=(0, 0, 1), z=(0, 1, 0))
        if kind == "budget":
            # a low plastic cover over the rear of the I/O stack only, with its plate on top
            wall = [(99.0, 30.0), (101.4, 30.0), (101.4, 34.4), (99.0, 34.4)]
            for ya, yb in ((y0, y0 + 2.0), (y1 - 2.0, y1)):
                pp.prism_bevel(g, [(p[0] * MM, p[1] * MM) for p in [(99.0, PT), (xr, PT), (xr, 36.6), (99.0, 36.6)]], ya * MM, yb * MM, 0.4 * MM, seg=1, M=M, uv=uv)
            pp.prism_bevel(g, [(p[0] * MM, p[1] * MM) for p in wall], y0 * MM, y1 * MM, 0.4 * MM, seg=1, M=M, uv=uv)
            self.pbox(heat, (99.0 + xr) / 2, ym, 34.4, xr - 99.0, y1 - y0, 2.2, 0.5)
            self.pbox(trim, 99.2, ym, 30.4, 0.4, y1 - y0 - 30.0, 1.0)
        else:
            if kind == "armour":
                wall = [(95.8, PT), (98.4, PT), (98.4, 22.0), (102.6, 34.4), (100.0, 36.6), (95.8, 24.0)]
            else:
                wall = [(95.8, PT), (98.0, PT), (98.0, 26.2), (101.4, 34.4), (99.4, 36.6), (95.8, 27.0)]
            pp.prism_bevel(g, [(p[0] * MM, p[1] * MM) for p in wall], y0 * MM, y1 * MM, 0.5 * MM, seg=1, M=M, uv=uv)
            self.pbox(heat, (99.8 + xr) / 2, ym, 34.4, xr - 99.8, y1 - y0, 2.2, 0.5)
            cap = [(95.8, PT), (xr, PT), (xr, 36.6), (99.4, 36.6), (95.8, 27.0)]
            for ya, yb in ((y0, y0 + 2.0), (y1 - 2.0, y1)):
                pp.prism_bevel(g, [(p[0] * MM, p[1] * MM) for p in cap], ya * MM, yb * MM, 0.4 * MM, seg=1, M=M, uv=uv)
            self.bx("black_plastic", 103.0, ym, 30.0, 6.0, y1 - y0 - 4.0, 4.4)
            if kind == "armour":
                # stepped armour plates on the socket-side face, a trim slash and cut lines
                for j, (ya, yb) in enumerate(((y0 + 4.0, y0 + 44.0), (y0 + 48.0, y1 - 40.0), (y1 - 36.0, y1 - 4.0))):
                    self.pbox(heat, 95.2, (ya + yb) / 2, 6.0 + j * 2.0, 1.4, yb - ya, 12.0, 0.4)
                    self.pbox(dark, 94.45, (ya + yb) / 2, 6.0 + j * 2.0 + 5.6, 0.1, yb - ya - 4.0, 0.6)
                self.pbox(trim, 95.0, ym, 24.4, 0.4, y1 - y0 - 24.0, 1.0)
                for f in (0.2, 0.62):
                    self.pbox(dark, (99.8 + xr) / 2, y0 + (y1 - y0) * f, 36.55, xr - 99.8 - 2.0, 0.6, 0.1)
            elif kind == "slab":
                # a contrasting band and diagonal grooves on the socket-side face
                self.pbox(trim, 95.4, ym, 13.0, 0.6, y1 - y0 - 6.0, 2.0)
                for i in range(10):
                    yy = y0 + 10.0 + i * 3.0
                    self.pbox(dark, 95.45, yy, 17.0, 0.12, 1.0, 7.0)
                self.pbox(st["trim"], 95.6, ym, 6.0, 0.5, y1 - y0 - 30.0, 1.2)
            elif kind == "rgb":
                # a lit emblem on the cover top, beside the logo plate (the socket-side face is hidden behind the
                # rear VRM heatsink): an RGB plate under a dark grille with the brand's shield cut out, framed in the
                # trim colour
                ex0, ex1 = 101.0, xr - 1.0
                ey0, ey1 = y0 + 3.5, ym + 6.0 - 38.0 - 2.0
                ec, eyc = (ex0 + ex1) / 2, (ey0 + ey1) / 2
                pp.box(self.k["rgb"], (ec * MM, eyc * MM, 36.7 * MM), ((ex1 - ex0) * MM, (ey1 - ey0) * MM, 0.2 * MM))
                self.anchor("A_FILM_RGB_0", (ec, eyc, 37.12), (ex1 - ex0 + 1.0, ey1 - ey0 + 3.0, 1.0),
                            meta="film=clear,on=io_rgb_emblem,peel=+y,tab=-x-y")
                for k_ in range(9):
                    yy = ey0 + 1.0 + k_ * (ey1 - ey0 - 2.0) / 8
                    if abs(yy - eyc) < 8.0:
                        continue
                    self.pbox(dark, ec, yy, 36.8, ex1 - ex0, 1.4, 0.3)
                sh = [(ec - 7.0, eyc - 6.0), (ec - 7.0, eyc + 6.0), (ec + 3.0, eyc + 6.0), (ec + 8.0, eyc), (ec + 3.0, eyc - 6.0)]
                self.pplan(trim, sh, 36.7, 37.0, 0.15)
                self.pplan(dark, [(ec - 5.0, eyc - 3.6), (ec - 5.0, eyc + 3.6), (ec + 2.0, eyc + 3.6), (ec + 5.0, eyc), (ec + 2.0, eyc - 3.6)], 37.0, 37.05)
                for yy in (ey0 - 0.6, ey1 + 0.6):
                    self.pbox(trim, ec, yy, 36.6, ex1 - ex0, 1.0, 0.5)
                self.pbox(trim, 95.6, ym, 3.0, 0.5, y1 - y0 - 30.0, 1.2)
        if st["io_rgb"]:
            pp.box(self.k["rgb"], (100.4 * MM, (ym + 2) * MM, 36.9 * MM), (1.4 * MM, (y1 - y0 - 10) * MM, 0.7 * MM), bevel=0.0002)
        # logo plate on the top, reading along +y (as build_board's, under A_FILM_IO_0)
        uv, ctx = self.mark(76.0, 17.0, 14.0, cfg["plate_bg"])
        with ctx as a:
            a.text(st["brand"], 4.0, 9.5, 10.0, cfg["plate_ink"], font=st["logo_font"], ax="LEFT", fit=38.0)
            a.line([(44.0, 5.0), (72.0, 5.0)], 0.6, cfg["plate_acc"])
            a.text(st["series"], 72.0, 10.4, 4.6, cfg["plate_acc"], font="agency", ax="RIGHT", fit=28.0)
            if kind == "armour":
                for i in range(5):
                    a.poly([(46 + i * 5, 13.6), (49 + i * 5, 13.6), (47 + i * 5, 15.4), (44 + i * 5, 15.4)], cfg["plate_acc"], z=0.3)
        pe = self.marks.swatch(cfg["plate_bg"])
        px, py_ = (99.8 + xr) / 2 + 0.6, ym + 6.0
        self.bx(self.MT, px, py_, 36.6, 17.0, 76.0, 0.5, bevel=0.15, uv=self.top_map(uv, px, py_, 37.1, 76.0, 17.0, up=(1, 0, 0), rest=pe))
        self.occupy(95.0, y0, xr, y1)

    # ------------------------------------------------ silkscreen
    def silkscreen(self):
        st, cfg = self.st, self.cfg
        s, deco, acc = cfg["silk"], cfg["deco"], cfg["accent"]
        for i, x in enumerate(BB.DIMM_X):
            dx = {0: 0.0, 1: 1.4, 2: -3.4, 3: 0.0}[i]
            self.at(BB.DIMM_NAMES[i], x + dx, -9.6, 1.6, font="arialbd")
        self.at(f"{cfg['mem']}_DIMM", -64.0, 26.0, 1.6, rot=90)
        self.at("PCIEX16_1", -36.0, BB.PCIE16_Y, 1.8, font="arialbd")
        self.at("PCIEX1_1", 40.0, self.slot_ys[1], 1.5, font="arialbd", ax="RIGHT")
        self.at("PCIEX16_2", -36.0, self.slot_ys[2], 1.6, font="arialbd")
        self.at("PCIEX1_2", 40.0, self.slot_ys[3], 1.5, font="arialbd", ax="RIGHT")
        self.at("SOCKET " + cfg["sock"], BB.S[0] - 22.0, BB.S[1] - 39.5 if self.v5 else BB.S[1] - 40.5, 1.6)
        bx_, by_ = -72.0, -27.0
        kind = st["silk"]
        if kind == "tactical":
            # hazard stripes and a stencil block
            for i in range(9):
                x0 = -112.0 + i * 5.0
                self.apoly([(x0, -50.0), (x0 + 2.4, -50.0), (x0 + 6.4, -44.0), (x0 + 4.0, -44.0)], acc, z=0.3)
            self.ar(-114.0, -14.0, -30.0, -13.2, deco, z=0.3)
            self.ar(-114.0, -42.0, -30.0, -41.2, deco, z=0.3)
            for i in range(6):
                self.apoly([(-104.0 + i * 4.0, -2.0), (-101.6 + i * 4.0, -2.0), (-104.0 + i * 4.0, 24.0), (-106.4 + i * 4.0, 24.0)], deco, z=0.3)
            self.at(st["series"], bx_, by_ + 4.0, 8.0, col=acc, font="impact", fit=60.0)
        elif kind == "angular":
            for i in range(5):
                y0 = -48.0 + i * 6.5
                self.apoly([(-114.0, y0), (-62.0 + i * 5.0, y0), (-58.0 + i * 5.0, y0 + 2.6), (-114.0, y0 + 2.6)], deco, z=0.3)
            self.apoly([(-50.0, -18.0), (-32.0, -18.0), (-38.0, -14.0), (-56.0, -14.0)], acc, z=0.35)
            self.at(st["series"], bx_, by_ + 4.0, 8.0, col=s, font="agency", fit=60.0)
        elif kind == "lines":
            for i in range(16):
                y0 = -50.0 + i * 2.2
                self.aline([(-114.0, y0), (-60.0 - (i % 4) * 6.0, y0), (-52.0 - (i % 4) * 6.0, y0 + 8.0)], 0.25, deco, z=0.3)
            self.at(st["series"], bx_, by_ + 4.0, 8.0, col=s, font="bahn", fit=60.0)
        elif kind == "dots":
            for i in range(14):
                for j in range(8):
                    if (i + j) % 3:
                        self.ac(-112.0 + i * 3.4, -48.0 + j * 3.4, 0.6 + 0.08 * j, deco, z=0.3, seg=10)
            self.at(st["series"], bx_, by_ + 4.0, 8.0, col=s, font="agency", fit=60.0)
        elif kind == "circuit":
            for i in range(10):
                y0 = -50.0 + i * 3.6
                pts = [(-114.0, y0), (-90.0 + (i % 3) * 4.0, y0), (-84.0 + (i % 3) * 4.0, y0 + 6.0), (-60.0, y0 + 6.0)]
                self.aline(pts, 0.3, deco, z=0.3)
                self.aring(-60.0, y0 + 6.0, 0.4, 0.9, deco, z=0.31)
            self.at(st["series"], bx_, by_ + 4.0, 8.0, col=s, font="arialbd", fit=60.0)
        else:   # stripes (build_board's)
            for i in range(14):
                x0 = -112.0 + i * 3.2
                self.apoly([(x0, -50.0), (x0 + 1.2, -50.0), (x0 + 13.2, -16.0), (x0 + 12.0, -16.0)], deco, z=0.3)
            self.at(st["brand"], bx_, by_ + 4.0, 9.0, col=s, font="agency", fit=60.0)
        self.at(st["brand"] + " " + cfg["model"], bx_, by_ - 6.0, 3.4, col=acc, font="agency", fit=60.0)
        self.aline([(bx_ - 22, by_ - 10.5), (bx_ + 22, by_ - 10.5)], 0.35, s, z=0.55)
        for i in range(9):
            y0 = -2.0 + i * 3.0
            self.apoly([(-104.0, y0), (-84.0, y0), (-80.0, y0 + 1.1), (-104.0, y0 + 1.1)], deco, z=0.3)
        self.apoly([(-100.0, 34.0), (-62.0, 34.0), (-62.0, 34.5), (-100.0, 34.5)], deco, z=0.3)
        self.at(cfg["mem"] + " READY", -82.0, 37.0, 1.6, col=acc, font="arialbd")
        self.at("4 x DIMM  up to 192GB" if cfg["mem"] == "DDR5" else "4 x DIMM  up to 128GB", -82.0, 31.6, 1.1, font="narrowbd")
        self.at("REV 1.01", 70.0, -151.0, 1.0, font="narrowbd")
        self.at(f"{st['brand']} {st['full']}", -60.0, 150.5, 1.2, font="arialbd", fit=70.0)
        self.at("94V-0  E254761", -6.0, -151.2, 0.9, font="narrowbd")


# ---------------------------------------------------------------- I/O shield

def build_shield(bid, board, painted):
    """build_board.build_shield with a short mesh prefix ("io") and the paint chosen by the style."""
    import random
    cfg = BB.BOARDS[bid]
    sid = cfg["shield"]
    c.reset()
    yc0, zc0 = (BB.IO_Y0 + BB.IO_Y1) / 2, (BB.IO_Z0 + BB.IO_Z1) / 2
    W, H = 158.75, 44.45
    bg = "#1a1b1e" if painted else "#b9bcc1"
    ink = "#e9e9e9" if painted else "#1c1c1c"
    at = pp.Atlas(1024, 2048, bg=bg)
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
                a.frame_rect(min(u0, u1) - 0.9, min(v0, v1) - 0.9, max(u0, u1) + 0.9, max(v0, v1) + 0.9, 0.25,
                             pp.shade(bg, 0.8 if not painted else 1.6), z=0.2)
        for (y, lab, ztop) in board.shield_labels:
            z0 = min(ztop + 1.6, BB.IO_Z1 - 6.0)
            u, v = A(y, z0)
            a.text(lab, u, v, 1.5, ink, font="arialbd", ax="LEFT", fit=max(4.0, BB.IO_Z1 - 1.0 - z0))
        u, v = A(-1.0, BB.IO_Z1 - 3.0)
        a.text(cfg["model"], u, v, 1.7, ink, font="agency", fit=7.0)
    pp.PREVIEW_TEX[sid] = (0.6, 0.35) if not painted else (0.2, 0.45)
    edge = at.swatch(pp.shade(bg, 0.85))
    at.render(pp.tex_path(sid))
    root = c.root(sid)
    k = pp.Kit(sid)
    T = "tex_" + sid
    t = 0.5
    out = pp.rounded_rect(0, 0, W, H, 1.0, 2)
    loops = [[(p[0] * MM, p[1] * MM) for p in out]]
    for kind, outline in board.shield_cuts:
        loops.append([((p[0] - yc0) * MM, (p[1] - zc0) * MM) for p in outline])
    M = pp.frame(x=(0, 1, 0), y=(0, 0, 1), z=(1, 0, 0))
    mapper = pp.MultiMap([pp.Planar(uv, (t / 2 * MM, 0, 0), (1, 0, 0), (0, 1, 0), (H * MM, W * MM)), edge])
    pp.prism(k[T], loops, -t / 2 * MM, t / 2 * MM, M=M, uv=mapper)
    fl = 3.2
    g = k[T]
    for s in (-1, 1):
        pp.box(g, ((-fl / 2) * MM, s * (W / 2 - t / 2) * MM, 0), (fl * MM, t * MM, (H - 1.0) * MM), uv=edge)
        pp.box(g, ((-fl / 2) * MM, 0, s * (H / 2 - t / 2) * MM), (fl * MM, (W - 1.0) * MM, t * MM), uv=edge)
        for j in range(9):
            yy = -W / 2 + 10 + j * (W - 20) / 8
            BB._slope_x(g, (-fl - 0.2, yy, s * (H / 2 - 0.2)), (-fl - 3.6, yy, s * (H / 2 + 0.8)), 4.0, 0.3)
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
            BB._slope_x(g, (-0.2, yy, zz - 0.2), (-1.8, yy, zz - 0.9), 2.4, 0.25)
    k.finish(root)
    c.anchor("A_HIT_0", (0, 0, 0), (0.004, W * MM, H * MM), root,
             meta=f"board_pose={BB.SHIELD_X * MM:.4f},{yc0 * MM:.5f},{zc0 * MM:.5f}")
    c.join_by_tag(root, "io")
    c.export(root, sid)
    pp.report(root)
    if PREVIEW[0]:
        pp.preview(root, sid, views=((90, 10), (60, 35)), size=(960, 720), dist=0.3)
    return root


# ---------------------------------------------------------------- build runners

def _previews(root, bid):
    pp.preview(root, bid, views=((15, 55), (-35, 40), (60, 35)), size=(1280, 960), dist=0.62, zup=True)
    pp.preview(root, bid, views=((-25, 50),), size=(1280, 960), dist=0.2, target=(0.03, 0.06, 0.01), start=3, zup=True)
    pp.preview(root, bid, views=((50, 30),), size=(1280, 960), dist=0.2, target=(0.1, 0.07, 0.015), start=4, zup=True)
    pp.preview(root, bid, views=((-60, 45),), size=(1280, 960), dist=0.2, target=(-0.08, -0.1, 0.005), start=5, zup=True)


def build_desktop(bid):
    cfg = BOARDS[bid]
    b = CatBoard(bid)
    root = b.build()
    P.write_report(root, bid, f"frame and layout: as {SIBLING[bid]} (origin at the PCB centre, +z component side, +x rear I/O)"
                   + ("; DIMM slots with the DDR5 notch of mb_ridge_b5" if cfg["sock"] == "L17" and cfg["mem"] == "DDR5" else ""))
    if PREVIEW[0]:
        _previews(root, bid)
    sroot = build_shield(bid, b, cfg["style"]["shield_painted"])
    P.write_report(sroot, cfg["shield"], f"frame: as io_{SIBLING[bid][3:]} (origin at the plate centre, board axes, outer face +x)")
    return root


def jobs():
    j = {bid: (lambda b=bid: build_desktop(b)) for bid in BOARDS}
    try:
        import server_boards
        j.update(server_boards.JOBS)
    except ImportError:
        pass
    return j


def main(argv):
    if "--nopreview" in argv:
        PREVIEW[0] = False
        P.PREVIEW[0] = False
        pp.preview = lambda *a, **k: []
    J = jobs()
    ids = [a for a in argv if not a.startswith("--")] or list(J)
    t0 = time.time()
    for pid in ids:
        t = time.time()
        J[pid]()
        print(f"BUILT {pid} in {time.time() - t:.1f}s")
    rep = os.path.join(c.PREVIEWS, "cat_boards_report.txt")
    with open(rep, "w", encoding="utf-8") as fh:
        for pid in sorted(J):
            for n in (pid, BB.BOARDS[pid]["shield"]):
                p = os.path.join(c.PREVIEWS, f"{n}_report.txt")
                if os.path.exists(p):
                    with open(p, encoding="utf-8") as f:
                        fh.write(f.read() + "\n")
    print(f"BUILD_CAT_BOARDS done: {len(ids)} jobs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(c.args())
