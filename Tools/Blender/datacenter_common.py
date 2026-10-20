"""
datacenter_common: shared helpers for the data-centre gear (build_datacenter.py).

Builds on parts_c (P: frames, slabs with holes, lathe, quads, Art, finalize, beauty). Everything is in Unity
coordinates. Rack devices share one frame (docs/tasks/01-datacentre-gear.md):
  origin = the centre of the front mounting plane (the front face of the rack's front rails), at the bottom of
  the device's U space; +Z out of the front, +Y up; the chassis extends towards -Z. So a device installs at a
  rack's A_RACKU_<n> pose directly (A_RACKU_n is at the bottom of U n+1, see datacenter_rack).

Conventions used by every model here (same as the PC parts):
  * A_PORT_<KIND>_<n>: the mouth plane of the port, +Z = where the plug comes from, meta depth=<m> (how far
    the plug face travels in). RJ45 jacks: the anchor's +Y points at the latch slot (meta latch=+up).
  * LEDs: an A_LED_<NAME>_<n> anchor carries its LED mesh (tag led_*), so the game can light each one.
  * Buttons: A_BUTTON_<NAME>_<n> carries its cap (moving piece), meta press=-z_local,travel=<m>.
  * Removable pieces (drive trays, PSUs, lids, doors, bezels, rails) are '<name>@<anchor>#tag' moving pieces in
    their closed / installed pose; their anchors keep the model's axes (fwd +Z, up +Y) unless stated, so a
    meta direction like pull=+z or slide=-z reads the same in the model and in the anchor.
"""
import bmesh
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ

U = 0.04445                    # 1 rack unit
EAR_W = 0.4826                 # 19" across the ears
HOLE_X = 0.46510 / 2           # EIA-310 hole centres, 18.312" apart
RAIL_OPEN = 0.450              # clear opening between the rails (17.72")
HOLES_IN_U = (0.00635, 0.022225, 0.0381)   # EIA-310: holes 1/4", 7/8" and 1 1/2" above the bottom of each U
SQ_HOLE = 0.0095               # square cage-nut hole (0.375")

ROOT = [None]


# ---------------------------------------------------------------- small geometry wrappers

def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rr(x0, x1, y0, y1, r=0.0, seg=4):
    return P.rrect(x1 - x0, y1 - y0, r, (x0 + x1) / 2, (y0 + y1) / 2, seg)


def sheet(name, tag, o, a, b, outline, holes=(), t=0.001, parent=None, **kw):
    """A flat plate: outline (and holes) in absolute coordinates along Unity directions a and b, on the plane
    through o; the thickness t is centred on o along a x b."""
    return P.slab(name, outline, t, tag, P.plane(o, a, b), holes=holes, parent=parent or ROOT[0], **kw)


def box(name, lo, hi, tag, parent=None, bevel=0.0, seg=2, **kw):
    """An axis-aligned box from its Unity min / max corners."""
    lo, hi = P.vec(lo), P.vec(hi)
    ctr = (lo + hi) * 0.5
    size = hi - lo
    return P.cube(name, tuple(ctr), (abs(size.x), abs(size.y), abs(size.z)), tag, P.WORLD, parent or ROOT[0], bevel, seg, **kw)


def fbox(name, fr, lo, hi, tag, parent=None, bevel=0.0, seg=2, **kw):
    """A box in a frame's local axes from its local min / max corners."""
    ctr = tuple((a + b) / 2 for a, b in zip(lo, hi))
    size = tuple(abs(b - a) for a, b in zip(lo, hi))
    return P.cube(name, ctr, size, tag, fr, parent or ROOT[0], bevel, seg, **kw)


def zslab(name, tag, outline, z0, z1, holes=(), parent=None, **kw):
    """A plate facing +Z: outline in (x, y), from z0 to z1."""
    return sheet(name, tag, (0, 0, (z0 + z1) / 2), X, Y, outline, holes, abs(z1 - z0), parent, **kw)


def xslab(name, tag, outline_zy, x0, x1, holes=(), parent=None, **kw):
    """A plate facing -X: outline in (z, y) (Unity z along the plate's local x), from x0 to x1."""
    return sheet(name, tag, ((x0 + x1) / 2, 0, 0), Z, Y, outline_zy, holes, abs(x1 - x0), parent, **kw)


def yslab(name, tag, outline_xz, y0, y1, holes=(), parent=None, **kw):
    """A plate facing -Y: outline in (x, z), from y0 to y1."""
    return sheet(name, tag, (0, (y0 + y1) / 2, 0), X, Z, outline_xz, holes, abs(y1 - y0), parent, **kw)


# ---------------------------------------------------------------- print atlases

class Atlas:
    """Named pixel regions of one texture: uv(name) gives the (u0, v0, u1, v1) rect for P.quad."""

    def __init__(self, file, w, h):
        self.file, self.w, self.h = file, w, h
        self.reg = {}

    def add(self, name, x, y, w, h):
        self.reg[name] = (x, y, w, h)
        return (x, y, w, h)

    def uv(self, name):
        x, y, w, h = self.reg[name]
        return (x / self.w, y / self.h, (x + w) / self.w, (y + h) / self.h)

    @property
    def tag(self):
        return "tex_" + self.file


def decal(name, atlas, region, fr, w, h, parent=None):
    """A printed quad (label, legend, logo) facing the frame's +Z, mapped to an atlas region."""
    return P.quad(name, fr, w, h, atlas.tag, parent or ROOT[0], uv=atlas.uv(region))


# ---------------------------------------------------------------- anchors with their little meshes

def led(name, fr, w, h, tag, parent=None, depth=0.0008, round_=False, meta=None, size=None):
    """An LED: the anchor at the lens surface, the lens (tag led_*) attached to it, proud of the face by depth/2."""
    root = parent or ROOT[0]
    a = P.anchor(name, fr, size or (max(w, 0.002), max(h, 0.002), 0.003), root, meta=meta or f"colour={tag[4:]}")
    if round_:
        P.cylinder("led", fr.sub(0, 0, -depth / 2), w / 2, depth, tag, 16, a)
    else:
        P.cube("led", (0, 0, -depth / 2 + 0.0001), (w, h, depth), tag, fr, a)
    return a


def button(name, fr, r, travel=0.001, tag="grey_plastic", parent=None, ring_tag="dark_plastic", meta=None,
           square=None, height=0.0015):
    """A round (or square=(w, h)) push button: a bezel ring in the face and the cap as a moving piece."""
    root = parent or ROOT[0]
    if square:
        w, h = square
        P.slab("btn_ring", P.rrect(w + 0.002, h + 0.002, 0.001), 0.0006, ring_tag, fr.sub(0, 0, 0.0001),
               holes=[P.rrect(w + 0.0004, h + 0.0004, 0.0006)], parent=root)
    else:
        P.lathe("btn_ring", [(r + 0.0002, 0.0004), (r + 0.0011, 0.0004), (r + 0.0011, -0.0004), (r + 0.0002, -0.0004),
                             (r + 0.0002, 0.0004)], ring_tag, fr, 24, root)
    a = P.anchor(name, fr, ((square[0] if square else 2 * r) + 0.003, (square[1] if square else 2 * r) + 0.003, 0.006),
                 root, meta=meta or f"press=-z_local,travel={travel:.4f}")
    if square:
        w, h = square
        P.slab("btn_cap", P.rrect(w, h, min(w, h) * 0.18), height, tag, fr.sub(0, 0, height / 2 - 0.0008), parent=a)
    else:
        P.lathe("btn_cap", [(0, height - 0.0008), (r * 0.85, height - 0.0008), (r, height - 0.0011), (r, -0.0008), (0, -0.0008)],
                tag, fr, 24, a)
    return a


def power_icon(name, fr, r, w, tag, parent=None, depth=0.00012, z=0.0):
    """The IEC power symbol as a raised print."""
    root = parent or ROOT[0]
    pts_o = P.arc(0, 0, r, math.radians(120), math.radians(420), 20)
    pts_i = P.arc(0, 0, r - w, math.radians(420), math.radians(120), 20)
    P.slab(name, pts_o + pts_i, depth, tag, fr.sub(0, 0, z + depth / 2), parent=root)
    P.slab(name, P.rrect(w, r * 1.1, w * 0.45, 0, r * 0.5), depth, tag, fr.sub(0, 0, z + depth / 2), parent=root)


# ---------------------------------------------------------------- port mouths (outlines in a face's local x, y)

RJ45_W, RJ45_H = 0.0118, 0.0084


def rj45_outline(cx=0.0, cy=0.0, latch_up=True):
    """The RJ45 jack mouth with its latch slot (the slot on +y if latch_up)."""
    w, h = RJ45_W, RJ45_H
    sw, sh = 0.0060, 0.0018   # latch slot
    s = 1 if latch_up else -1
    y0, y1 = -h / 2, h / 2
    if latch_up:
        pts = [(-w / 2, y0), (w / 2, y0), (w / 2, y1), (sw / 2, y1), (sw / 2, y1 + sh), (-sw / 2, y1 + sh), (-sw / 2, y1), (-w / 2, y1)]
    else:
        pts = [(-w / 2, y1), (-w / 2, y0), (-sw / 2, y0), (-sw / 2, y0 - sh), (sw / 2, y0 - sh), (sw / 2, y0), (w / 2, y0), (w / 2, y1)]
        pts = list(reversed(pts))
    return [(cx + x, cy + y) for (x, y) in pts]


def c14_outline(cx=0.0, cy=0.0, scale=1.0):
    """IEC C14 inlet mouth (takes a C13 plug): 24.5 x 16.4 mm with the two keyed corners on top."""
    w, h, ch = 0.0246 * scale, 0.0164 * scale, 0.0042 * scale
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - ch), (w / 2 - ch, h / 2), (-w / 2 + ch, h / 2), (-w / 2, h / 2 - ch)]
    return [(cx + x, cy + y) for (x, y) in pts]


def c20_outline(cx=0.0, cy=0.0):
    """IEC C20 inlet mouth (takes a C19 plug): about 30 x 21 mm, rounded."""
    return P.rrect(0.0300, 0.0215, 0.0025, cx, cy, 3)


def usba_outline(cx=0.0, cy=0.0):
    return P.rrect(0.0125, 0.0051, 0.0004, cx, cy, 2)


def vga_outline(cx=0.0, cy=0.0):
    """D-sub DE-15 shell mouth (trapezoid, wide edge on top)."""
    wt, wb, h, r = 0.0166, 0.0144, 0.0068, 0.0012
    return [(cx - wb / 2, cy - h / 2), (cx + wb / 2, cy - h / 2), (cx + wt / 2, cy + h / 2), (cx - wt / 2, cy + h / 2)]


SFP_W, SFP_H = 0.0140, 0.0098


def sfp_outline(cx=0.0, cy=0.0):
    return rect(cx - SFP_W / 2, cx + SFP_W / 2, cy - SFP_H / 2, cy + SFP_H / 2)


# ---------------------------------------------------------------- port insides (behind a face that has the holes)

def comb_outline(n, pitch, tooth_w, y0, y1, bar):
    """n teeth (width tooth_w, at pitch) from y0 + bar to y1, joined by a bar from y0 to y0 + bar (CCW)."""
    xs = [(k - (n - 1) / 2) * pitch for k in range(n)]
    pts = [(xs[0] - tooth_w / 2, y0), (xs[-1] + tooth_w / 2, y0)]
    for x in reversed(xs):
        pts += [(x + tooth_w / 2, y0 + bar), (x + tooth_w / 2, y1), (x - tooth_w / 2, y1), (x - tooth_w / 2, y0 + bar)]
    return pts


def rj45_jack(fr, parent=None, latch_up=True, depth=0.0145, body_tag="black_plastic", contacts=True, shield=True):
    """The jack behind a face hole at fr (fr at the mouth plane, +Z out): the cavity walls (a block with the
    mouth cut through), a dark floor, the 8 gold contacts on the far side of the latch, the shield lip."""
    root = parent or ROOT[0]
    w, h = RJ45_W, RJ45_H
    mouth = rj45_outline(0, 0, latch_up)
    P.slab("rj45_body", P.rrect(w + 0.0024, h + 0.0042, 0.0005), depth, body_tag, fr.sub(0, 0, -depth / 2 - 0.0002),
           holes=[mouth], parent=root)
    P.slab("rj45_floor", P.rrect(w + 0.0010, h + 0.0030, 0.0003), 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=root)
    if contacts:
        s = -1 if latch_up else 1   # the 8 contacts sit on the side away from the latch
        cf = P.Frame(fr.p(0, s * (h / 2 - 0.0009), -depth * 0.5), fr.v, fr.w)   # local y runs out of the mouth
        P.slab("rj45_pins", comb_outline(8, 0.00102, 0.00042, -0.0045, 0.0050, 0.0012), 0.0003, "gold", cf, parent=root)
    if shield:
        P.slab("rj45_shield", P.rrect(w + 0.0016, h + 0.0034, 0.0004), 0.0003, "nickel", fr.sub(0, 0, 0.00005),
               holes=[P.rrect(w + 0.0002, h + 0.0004, 0.0002)], parent=root)


def cavity(fr, outline, depth, parent=None, wall_tag="black_plastic", floor_tag="dark_plastic", margin=0.0015):
    """A generic port cavity behind a face hole: walls (the outline cut through a block) and a floor."""
    root = parent or ROOT[0]
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    P.slab("cav_wall", P.rrect(w + 2 * margin, h + 2 * margin, 0.0005, cx, cy), depth, wall_tag,
           fr.sub(0, 0, -depth / 2 - 0.0001), holes=[outline], parent=root)
    P.slab("cav_floor", P.rrect(w + margin, h + margin, 0.0004, cx, cy), 0.0005, floor_tag, fr.sub(0, 0, -depth + 0.0002), parent=root)


def c14_inlet(fr, parent=None, depth=0.010):
    """A C14 inlet behind its face hole: the moulded cavity and the three male pins."""
    root = parent or ROOT[0]
    cavity(fr, c14_outline(), depth, root, margin=0.002)
    for (x, y, ww, hh) in ((-0.007, -0.002, 0.0009, 0.0042), (0.007, -0.002, 0.0009, 0.0042), (0.0, 0.0042, 0.0042, 0.0009)):
        P.cube("c14_pin", (x, y, -depth + 0.0045), (ww, hh, 0.0075), "nickel", fr, root)


def c20_inlet(fr, parent=None, depth=0.012):
    root = parent or ROOT[0]
    cavity(fr, c20_outline(), depth, root, margin=0.002)
    for (x, y, ww, hh) in ((-0.0075, -0.0025, 0.0048, 0.0011), (0.0075, -0.0025, 0.0048, 0.0011), (0.0, 0.0045, 0.0011, 0.0050)):
        P.cube("c20_pin", (x, y, -depth + 0.0050), (ww, hh, 0.0085), "nickel", fr, root)


def c13_outlet(fr, parent=None, depth=0.008, tag="black_plastic"):
    """A C13 outlet (takes a C14 plug): a keyed boss with three contact slots in a recess round it.
    fr is at the outlet face (the face of the boss)."""
    root = parent or ROOT[0]
    boss = c14_outline(0, 0, 0.92)
    recess = c14_outline(0, 0, 1.22)
    # recess: a dark moat round the boss
    P.slab("c13_moat", recess, 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=root)
    P.slab("c13_boss", boss, depth - 0.0006, tag, fr.sub(0, 0, -(depth - 0.0006) / 2),
           holes=[rect(-0.0075, -0.0063, -0.0045, 0.0005), rect(0.0063, 0.0075, -0.0045, 0.0005), rect(-0.0021, 0.0021, 0.0026, 0.0040)],
           parent=root)
    P.slab("c13_slots", P.rrect(0.018, 0.010, 0.0005, 0, -0.0005), 0.0004, "dark_plastic", fr.sub(0, 0, -depth + 0.0012), parent=root)


def c19_outlet(fr, parent=None, depth=0.009, tag="black_plastic"):
    """A C19 outlet (takes a C20 plug): a rectangular boss with two horizontal slots and the earth slot."""
    root = parent or ROOT[0]
    P.slab("c19_moat", P.rrect(0.0330, 0.0245, 0.003), 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=root)
    P.slab("c19_boss", P.rrect(0.0280, 0.0190, 0.002), depth - 0.0006, tag, fr.sub(0, 0, -(depth - 0.0006) / 2),
           holes=[rect(-0.0100, -0.0050, -0.0032, -0.0018), rect(0.0050, 0.0100, -0.0032, -0.0018), rect(-0.0007, 0.0007, 0.0020, 0.0065)],
           parent=root)
    P.slab("c19_slots", P.rrect(0.024, 0.014, 0.0005), 0.0004, "dark_plastic", fr.sub(0, 0, -depth + 0.0012), parent=root)


def usba_port(fr, parent=None, depth=0.010, tongue="black_plastic", horizontal_tongue_up=True):
    root = parent or ROOT[0]
    out = usba_outline()
    P.slab("usb_shell", P.rrect(0.0131, 0.0057, 0.0005), depth, "nickel", fr.sub(0, 0, -depth / 2),
           holes=[out], parent=root)
    s = 1 if horizontal_tongue_up else -1
    P.cube("usb_tongue", (0, s * 0.0011, -depth * 0.55), (0.0112, 0.0018, depth * 0.85), tongue, fr, root)
    P.slab("usb_floor", out, 0.0004, "dark_plastic", fr.sub(0, 0, -depth + 0.0002), parent=root)


def vga_port(fr, parent=None, depth=0.006):
    root = parent or ROOT[0]
    P.slab("vga_shell", P.rrect(0.031, 0.0125, 0.0008), 0.0005, "nickel", fr.sub(0, 0, 0.0002),
           holes=[vga_outline()], parent=root)
    P.slab("vga_insert", vga_outline(), depth, "dark_plastic", fr.sub(0, 0, -depth / 2 - 0.0008), parent=root)
    P.slab("vga_face", [(x * 0.9, y * 0.82) for (x, y) in vga_outline()], 0.0004, "black_plastic",
           fr.sub(0, 0, -0.0012), holes=[P.circle(0.00045, (k - 2) * 0.00277 + dx, y, 6)
                                        for (y, dx, n) in ((0.0022, 0, 5), (0.0, 0.0014, 5), (-0.0022, 0, 5))
                                        for k in range(n) if abs((k - 2) * 0.00277 + dx) < 0.0072], parent=root)
    for sx in (-1, 1):
        P.cylinder("vga_jackscrew", fr.sub(sx * 0.0125, 0, 0.0018), 0.0021, 0.0032, "nickel", 6, root)
        P.cylinder("vga_jackscrew_hole", fr.sub(sx * 0.0125, 0, 0.0035), 0.0010, 0.0002, "dark_plastic", 8, root)


def sfp_cage(fr, parent=None, depth=0.046):
    """An SFP+ cage behind its face hole: the metal cage (with the EMI spring fingers at the mouth) and the
    host connector at the back."""
    root = parent or ROOT[0]
    out = sfp_outline()
    P.slab("sfp_cage", P.rrect(SFP_W + 0.0012, SFP_H + 0.0012, 0.0003), depth, "nickel", fr.sub(0, 0, -depth / 2),
           holes=[out], parent=root)
    # EMI gasket fingers round the mouth
    P.slab("sfp_gasket", P.rrect(SFP_W + 0.0034, SFP_H + 0.0034, 0.0005), 0.0006, "steel", fr.sub(0, 0, 0.0003),
           holes=[P.rrect(SFP_W + 0.0004, SFP_H + 0.0004, 0.0002)], parent=root)
    P.slab("sfp_back", out, 0.0006, "dark_plastic", fr.sub(0, 0, -depth + 0.0003), parent=root)
    P.cube("sfp_conn", (0, -0.0018, -depth + 0.006), (0.0105, 0.0026, 0.010), "black_plastic", fr, root)


# ---------------------------------------------------------------- rack ears

def ear_holes_y(units, slots=None):
    """Hole heights (above the device origin) for a device of `units` U: by default the bottom and top holes
    of each U pair (hole 1 of the first U, hole 3 of the last U) and the middle of 1U."""
    if slots is not None:
        return slots
    if units == 1:
        return [HOLES_IN_U[1]]
    return [HOLES_IN_U[0], (units - 1) * U + HOLES_IN_U[2]]


def ears(root, units, z_face, tag, body_w=0.440, t=0.0020, h=None, depth=0.020, slots=None, anchors=True, screw_kind="M6"):
    """Two flat 19" ears bent forward from the side walls: the plate sits on the rack's mounting plane (its back
    face at z = 0, front at z = t), from body_w/2 to EAR_W/2, with oval holes on the EIA-310 positions; the
    side flange runs back along the body by `depth`. Anchors A_SCREW_RACK_<n> at each hole (forward +z)."""
    hgt = h if h is not None else units * U - 0.0008
    y0 = (units * U - hgt) / 2
    ys = ear_holes_y(units, slots)
    out = []
    n = 0
    for sx in (-1, 1):
        x_in, x_out = body_w / 2, EAR_W / 2
        holes = [P.stadium(0.0100, 0.0068, sx * HOLE_X, y) for y in ys]
        if sx > 0:
            outline = rect(x_in - 0.0005, x_out, y0, y0 + hgt)
        else:
            outline = rect(-x_out, -x_in + 0.0005, y0, y0 + hgt)
        outline = rr(min(p[0] for p in outline), max(p[0] for p in outline), y0, y0 + hgt, 0.0015)
        zslab("ear", tag, outline, 0.0, t, holes, root)
        # the flange back along the side wall (bent edge)
        xs = sx * (x_in + t / 2)
        xslab("ear_flange", tag, rr(z_face - depth, z_face + 0.0005, y0 + 0.0015, y0 + hgt - 0.0015, 0.001), xs - t / 2, xs + t / 2, (), root)
        if z_face > t:   # ears set back from the front face: a gusset joins them
            xslab("ear_gusset", tag, rect(t, z_face, y0 + 0.0015, y0 + hgt - 0.0015), xs - t / 2, xs + t / 2, (), root)
        if anchors:
            for y in ys:
                out.append(P.anchor(f"A_SCREW_RACK_{n}", P.Frame((sx * HOLE_X, y, t), Z, Y), (0.012, 0.010, 0.006), root,
                                    meta=f"thread={screw_kind},cage=1,side={'r' if sx > 0 else 'l'}"))
                n += 1
    return out


# ---------------------------------------------------------------- a low-poly server fan

def server_fan(anchor, size, depth, blades=5, frame_tag="black_plastic", blade_tag="fan_black", hub_tag=None, parent=None,
               segs=20, spin=1):
    """A square server fan (40 mm / 60 mm / 80 mm) in a light-weight build: the frame with its round bore and
    corner holes, three stator struts and the motor at the back (static), and the rotor (hub + swept blades) as
    the moving piece of `anchor` (spins about the anchor's +Z, the airflow side). anchor is an A_FAN_<n>."""
    root = parent or c.top_of(anchor)
    fr = P.anchor_frame(anchor)
    s = size
    rb = s / 2 - max(0.0012, s * 0.03)
    holes = [P.circle(rb, 0, 0, segs)] + [P.circle(0.0018 if s < 0.05 else 0.0022, sx * s * 0.41, sy * s * 0.41, 8)
                                           for sx in (-1, 1) for sy in (-1, 1)]
    P.slab("fan_frame", P.rrect(s, s, s * 0.06), depth, frame_tag, fr, holes=holes, parent=root)
    # stator: motor cup and struts at the back face
    rh = s * 0.20
    P.cylinder("fan_motor", fr.sub(0, 0, -depth / 2 + 0.003), rh * 0.95, 0.006, frame_tag, 16, root)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        mid = (rh + rb) / 2
        P.cube("fan_strut", (0, 0, 0), ((rb - rh) + 0.001, 0.0022, 0.0022), frame_tag,
               P.Frame(fr.p(math.cos(a) * mid, math.sin(a) * mid, -depth / 2 + 0.0012), fr.w, fr.d(-math.sin(a), math.cos(a), 0)),
               root)
    # rotor: the hub cup and pitched blades, all one moving piece
    ht = hub_tag or blade_tag
    P.lathe("rotor", [(0, depth / 2 - 0.0012), (rh * 0.88, depth / 2 - 0.0012), (rh, depth / 2 - 0.0028),
                      (rh, -depth / 2 + 0.0065), (0, -depth / 2 + 0.0065)], ht, fr, 16, anchor)
    r0, r1 = rh * 0.95, rb - 0.0008
    zc = 0.0008
    span = depth - 0.0085
    for k in range(blades):
        a0 = 2 * math.pi * k / blades
        pts = []
        # a swept, pitched blade: 3 stations from root to tip, leading and trailing edges at different z
        st = 3
        for i in range(st + 1):
            t = i / st
            r = r0 + (r1 - r0) * t
            chord = (0.95 - 0.25 * t) * (2 * math.pi * r / blades) * 0.78
            sweep = 0.35 * t * spin
            pts.append((r, a0 + sweep, chord))
        bm = bmesh.new()
        rows = []
        for (r, a, ch) in pts:
            da = ch / r / 2
            le = (r * math.cos(a + da * spin), r * math.sin(a + da * spin), zc + span / 2)
            te = (r * math.cos(a - da * spin), r * math.sin(a - da * spin), zc - span / 2)
            row = [bm.verts.new((le[0], le[1], le[2] + 0.0004)), bm.verts.new((te[0], te[1], te[2] + 0.0004)),
                   bm.verts.new((te[0], te[1], te[2] - 0.0004)), bm.verts.new((le[0], le[1], le[2] - 0.0004))]
            rows.append(row)
        for ra, rb_ in zip(rows, rows[1:]):
            for j in range(4):
                j2 = (j + 1) % 4
                bm.faces.new((ra[j], ra[j2], rb_[j2], rb_[j]))
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
        P.emit("blade", bm, fr, blade_tag, anchor, smooth=60)
    return anchor


# ---------------------------------------------------------------- perforation textures

def hex_perf_texture(file, w_px, h_px, w_m, h_m, pitch, hole_r, web=(0.06, 0.06, 0.065), hole=(0.01, 0.01, 0.012),
                     border_px=0, round_holes=False):
    """A perforated sheet (holes alpha 0, dark, so it reads right opaque too), at real scale: w_m x h_m metres
    of sheet on w_px x h_px pixels, a staggered grid of hexagonal (or round) holes."""
    import numpy as np
    yy, xx = np.mgrid[0:h_px, 0:w_px].astype(np.float32)
    X_ = (xx + 0.5) * (w_m / w_px)
    Y_ = (yy + 0.5) * (h_m / h_px)
    dy = pitch * math.sqrt(3) / 2
    best = np.full(X_.shape, 1e9, dtype=np.float32)
    row0 = np.floor(Y_ / dy + 0.5)
    for drow in (-1, 0, 1):
        r2 = row0 + drow
        cy2 = r2 * dy
        off2 = (r2 % 2) * pitch / 2
        cx2 = np.floor((X_ - off2) / pitch + 0.5) * pitch + off2
        ddx, ddy = np.abs(X_ - cx2), np.abs(Y_ - cy2)
        if round_holes:
            d = np.sqrt(ddx * ddx + ddy * ddy)
        else:
            d = np.maximum(ddy, ddy * 0.5 + ddx * math.sqrt(3) / 2)
        best = np.minimum(best, d)
    is_hole = best < hole_r
    edge = np.clip((best - hole_r) / (pitch * 0.12), 0, 1)
    arr = np.zeros((h_px, w_px, 4), dtype=np.float32)
    shade = 0.75 + 0.25 * edge
    for k in range(3):
        arr[..., k] = np.where(is_hole, hole[k], web[k] * shade)
    arr[..., 3] = np.where(is_hole, 0.0, 1.0)
    if border_px:
        b = border_px
        for sl in ((slice(0, b), slice(None)), (slice(-b, None), slice(None)), (slice(None), slice(0, b)), (slice(None), slice(-b, None))):
            arr[sl[0], sl[1], :3] = web
            arr[sl[0], sl[1], 3] = 1
    return P.save_png(arr, file)


def tiled_quads(name, tag, fr, w, h, tile_w, tile_h, parent=None, back=True):
    """Covers a w x h area (centred on fr, facing +Z) with quads of one texture tile each (UV 0..1 per tile), so a
    real-scale perforation repeats without UVs outside 0..1. The last row / column use a part of the tile.
    back=True adds the same quads facing -Z (a sheet seen from both sides)."""
    root = parent or ROOT[0]
    nx = max(1, int(math.ceil(w / tile_w - 1e-6)))
    ny = max(1, int(math.ceil(h / tile_h - 1e-6)))
    x0, y0 = -w / 2, -h / 2
    for i in range(nx):
        for j in range(ny):
            xa, xb = x0 + i * tile_w, min(x0 + (i + 1) * tile_w, w / 2)
            ya, yb = y0 + j * tile_h, min(y0 + (j + 1) * tile_h, h / 2)
            uvr = (0, 0, (xb - xa) / tile_w, (yb - ya) / tile_h)
            P.quad(name, fr.sub((xa + xb) / 2, (ya + yb) / 2, 0), xb - xa, yb - ya, tag, root, uv=uvr, flip_u=False)
            if back:
                bf = P.Frame(fr.p((xa + xb) / 2, (ya + yb) / 2, -0.00005), fr.w * -1, fr.v)
                P.quad(name, bf, xb - xa, yb - ya, tag, root, uv=uvr, flip_u=True)


# ---------------------------------------------------------------- build plumbing

def bounds(root, skip=()):
    """Unity-space bounds (min, max) of every mesh vertex under root (skip: name fragments to leave out)."""
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for o in c.descendants(root):
        if o.type != "MESH" or any(k in o.name for k in skip):
            continue
        mw = o.matrix_world
        for v in o.data.vertices:
            b = mw @ v.co
            u = (-b.x, b.z, -b.y)
            for i in range(3):
                lo[i] = min(lo[i], u[i])
                hi[i] = max(hi[i], u[i])
    return lo, hi


def finish(root, mid, preview_views=((30, 20), (150, 25)), beauty_views=((28, 15), (150, 20)), size=(1000, 750),
           samples=40, extra=None, beauty_kw=None, more_beauty=()):
    """finalize, export, report, previews (Workbench) and beauty renders (Cycles) of one model."""
    P.finalize(root, mid)
    c.export(root, mid)
    lo, hi = bounds(root)
    line = "bounds min=(%.4f, %.4f, %.4f) max=(%.4f, %.4f, %.4f) size=(%.4f, %.4f, %.4f)" % (*lo, *hi, *(hi[i] - lo[i] for i in range(3)))
    tris, meshes = P.write_report(root, mid, line + ("\n" + extra if extra else ""))
    P.preview(root, mid, views=preview_views, size=size)
    n = len(preview_views)
    P.beauty(root, mid, views=beauty_views, size=size, samples=samples, start_index=n, **(beauty_kw or {}))
    k = n + len(beauty_views)
    for views, kw in more_beauty:
        P.beauty(root, mid, views=views, size=size, samples=samples, start_index=k, **kw)
        k += len(views)
    return tris, meshes
