"""
rig_products: the packaging rig of every retail box (UNBOXING.md 3). Owner: Blender agent B. Called by build_boxes.py.

Conventions used by every rig (see rig_common for the meta grammar):
  * The box frame: origin at the bottom centre, +z the front, y up, closed pose. A_HIT_0 = the outer box size.
  * Hinged pieces (A_FLAP, hinged A_LID, A_CLAMLID): the anchor sits ON the hinge line and is rotation-free;
    meta hinge=<x|y|z>, open=<deg> (Unity rotation sense about that local axis).
  * Lifted / slid pieces (A_LID lift, A_SLEEVE, A_INSERT_*): the anchor sits at the piece's bottom (or base) centre;
    meta lift|slide=<+-axis>, dist=<m> (the travel that frees the piece).
  * Content: A_ITEM_PART_<n> = the part model's own frame (size = the space the part and its bag may use, in the
    part's axes). Flat items (A_ITEM_DOC, A_ITEM_HW, A_ITEM_CORD, A_ITEM_POUCH, A_ITEM_ACC with frame=flat): the anchor
    is at the centre of the face resting on its support, local +Z out of the item's top face, local +Y = the top
    edge of its print; size = (w, h, t) and the item occupies z in [0, t].
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import rig_common as RC  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from rig_common import F, Rig, X, Y, Z, NX, NY, NZ, rr, resample  # noqa: E402

DEG = math.pi / 180.0
NOTES = {}

# Part bounds in their own frames (Unity, from the part FBXs): (lo, hi).
PART_BOUNDS = {
    "cpu_arc5": ((-0.02, -0.02, 0.0), (0.02, 0.02, 0.006)),
    "cpu_arc7": ((-0.02, -0.02, 0.0), (0.02, 0.02, 0.006)),
    "cpu_tiron5": ((-0.0188, -0.0225, -0.0005), (0.0188, 0.0225, 0.006)),
    "mb_ridge_b5": ((-0.123, -0.1525, -0.0015), (0.1337, 0.1525, 0.0372)),
    "mb_ridge_z4": ((-0.123, -0.1525, -0.0015), (0.1263, 0.1525, 0.043)),
    "io_ridge_b5": ((-0.0068, -0.0794, -0.0232), (0.0003, 0.0794, 0.0232)),
    "io_ridge_z4": ((-0.0068, -0.0794, -0.0232), (0.0003, 0.0794, 0.0232)),
    "ram_ddr5_16": ((-0.0038, -0.0667, 0.0), (0.0038, 0.0667, 0.0426)),
    "ram_ddr4_8": ((-0.0036, -0.0667, 0.0), (0.0036, 0.0667, 0.0336)),
    "gpu_rx66": ((-0.105, -0.0476, -0.0135), (0.1065, 0.004, 0.1103)),
    "gpu_rx88": ((-0.205, -0.0576, -0.0135), (0.1065, 0.004, 0.1253)),
    "ssd_1tb": ((-0.04, -0.011, 0.0), (0.04, 0.011, 0.0021)),
    "ssd_sata_500": ((-0.05, -0.0036, -0.035), (0.05, 0.0035, 0.035)),
    "psu_450": ((-0.0982, -0.0451, -0.0761), (0.073, 0.0431, 0.0761)),
    "psu_750": ((-0.0704, -0.0451, -0.0761), (0.073, 0.0431, 0.0761)),
    "cooler_stock": ((-0.0506, -0.0506, -0.012), (0.0506, 0.08, 0.0538)),
    "cooler_tower": ((-0.051, -0.0635, -0.012), (0.0389, 0.09, 0.1552)),
    "case_brickhouse": ((-0.2195, -0.008, -0.1061), (0.212, 0.4512, 0.1121)),
    "case_breeze": ((-0.2193, -0.008, -0.1061), (0.212, 0.4512, 0.1121)),
    "usb_stick": ((-0.0093, -0.0041, 0.0), (0.0093, 0.0045, 0.0572)),
    # parts batch D (build_parts_d.py)
    "cpu_arc9": ((-0.02, -0.02, 0.0), (0.02, 0.02, 0.006)),
    "gpu_rx77": ((-0.175, -0.0526, -0.0135), (0.1065, 0.004, 0.1184)),
    "mb_ridge_x5": ((-0.123, -0.1525, -0.0015), (0.1337, 0.1525, 0.0373)),
    "io_ridge_x5": ((-0.0068, -0.0794, -0.0232), (0.0003, 0.0794, 0.0232)),
    "case_aero": ((-0.2193, -0.008, -0.1061), (0.212, 0.4512, 0.1121)),
}

# Where a case's accessory box rides inside it (case-frame height of its floor): on the PSU shroud, or on top of the
# bottom fans lying on the shroud (case_aero).
ACC_SHELF = {"case_aero": 0.1305}


def bsize(mid, pad=0.0):
    lo, hi = PART_BOUNDS[mid]
    return tuple(hi[i] - lo[i] + 2 * pad for i in range(3))


def bcentre(mid):
    lo, hi = PART_BOUNDS[mid]
    return tuple((hi[i] + lo[i]) / 2 for i in range(3))


def sub_uv(u, f0, f1, axis="v"):
    u0, v0, u1, v1 = u
    if axis == "v":
        return (u0, v0 + (v1 - v0) * f0, u1, v0 + (v1 - v0) * f1)
    return (u0 + (u1 - u0) * f0, v0, u0 + (u1 - u0) * f1, v1)


def kind_of(pid, it):
    if it["cat"] == "CPU":
        return "cpu"
    if it["cat"] == "GPU":
        return "gpu"
    if it["cat"] == "Motherboard":
        return "mb"
    if it["cat"] == "RAM":
        return "ram"
    if pid == "ssd_1tb":
        return "ssd_m2"
    if pid == "ssd_sata_500":
        return "ssd_sata"
    if it["cat"] == "PSU":
        return "psu"
    if pid == "cooler_stock":
        return "cooler_stock"
    if pid == "cooler_tower":
        return "cooler_tower"
    if it["cat"] == "Case":
        return "case"
    if pid == "usb_installer":
        return "usb"
    if pid in ("cable_dp", "fan_splitter"):
        return "bag"
    raise KeyError(pid)


# ---------------------------------------------------------------- shared pieces

def notched_outline(w, h, rn, seg=10):
    """A w x h rectangle (centred) with a semicircular thumb notch of radius rn in its top edge (CCW)."""
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (rn, h / 2)]
    for k in range(1, seg):
        a = -math.pi * k / seg
        pts.append((rn * math.cos(a), h / 2 + rn * math.sin(a)))
    pts += [(-rn, h / 2), (-w / 2, h / 2)]
    return pts


def notched_board(R, name, frame, w, h, t, inner, tex, uv, rn, anc=None, e=0.00015):
    """A wall with a thumb notch at the top centre: the board and its print skin share the outline."""
    out = notched_outline(w, h, rn)
    R.slab(name, out, t, inner, frame.sub(0, 0, -t / 2), anc=anc)
    R.slab(name + "_print", out, 0.00004, tex, frame.sub(0, 0, e), anc=anc, uv=uv, uv_bounds=(-w / 2, -h / 2, w / 2, h / 2))


def poly(R, name, frame, pts, tag, anc=None, uv=None, uv_bounds=None, uv_solid=None):
    """A flat single-sided polygon in the frame's XY plane facing +Z."""
    import bmesh
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], p[1], 0.0)) for p in pts]
    f = bm.faces.new(vs)
    bm.normal_update()
    if f.normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=[f])
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    kw = {}
    if uv is not None:
        kw = dict(uv=uv, uv_bounds=uv_bounds)
    elif uv_solid is not None:
        kw = dict(uv_solid=uv_solid)
    return R.emit(name, bm, frame, tag, anc, recalc=False, hint=frame.w, **kw)


def clip_circle(cx, cy, r, keep_below, n=28):
    """The part of a circle below (keep_below) or above the line y=0, as a polygon."""
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    out = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ina = (a[1] <= 0) if keep_below else (a[1] >= 0)
        inb = (b[1] <= 0) if keep_below else (b[1] >= 0)
        if ina:
            out.append(a)
        if ina != inb:
            t = a[1] / (a[1] - b[1])
            out.append((a[0] + (b[0] - a[0]) * t, 0.0))
    return out


def seal_round(R, name, x, edge_y, z_face, d, wrap, order=0, text="SEALED", peel="+y", face="front", under=None):
    """A round clear seal on a box's face, folded over the top edge onto the lid: the anchor covers the part on
    the face (the game's flat peel strip); meta wrap = how far it runs on over the edge (onto the face whose normal
    is the anchor's +Y). A look mesh shows the whole bent seal."""
    on = d - wrap
    if face == "front":
        fr = F((x, edge_y - on / 2, z_face + 0.00012), Z, Y)
        lower = F((x, edge_y, z_face + 0.00012), Z, Y)
        upper = F((x, edge_y + 0.00012, z_face), Y, NZ)
    elif face == "right":   # on the +x end face, folding over its top edge
        fr = F((z_face + 0.00012, edge_y - on / 2, x), X, Y)
        lower = F((z_face + 0.00012, edge_y, x), X, Y)
        upper = F((z_face, edge_y + 0.00012, x), Y, NX)
    else:
        raise ValueError(face)
    R.anchor(name, fr, (d, on, 0.0001), shape="round", peel=peel, wrap=wrap, print=text, order=order,
             label="seal sticker", under=under)
    cy = wrap - d / 2
    poly(R, "seallook", lower, clip_circle(0, cy, d / 2, True), "seal_clear", anc=name)
    poly(R, "seallook", upper, [(p[0], p[1]) for p in clip_circle(0, cy, d / 2, False)], "seal_clear", anc=name)
    return name


def seal_rect_flat(R, name, frame, w, h, order=0, text="SEALED", peel="+y", under=None, parent=None, tag="seal_clear"):
    """A flat rectangular seal (on one face, across a seam)."""
    R.anchor(name, frame, (w, h, 0.0001), parent=parent, shape="rect", peel=peel, print=text, order=order,
             label="seal sticker", under=under)
    R.quad("seallook", frame.sub(0, 0, 0.00005), w, h, tag, anc=name)
    return name


def doc(R, idx, frame, size, kind, form, order, under=None, parent=None, label=None):
    name = f"A_ITEM_DOC_{idx}"
    R.anchor(name, frame, size, parent=parent, doc=kind, form=form, label=label or kind, order=order, under=under)
    return name


def flat_frame(o, normal=(0, 1, 0), top=(0, 0, -1)):
    """A flat item's frame: +Z out of its top face, +Y toward the top edge of its print."""
    return F(o, normal, top)


def lean_stack(items, y_floor, z_wall, deg, gap=0.0004, dx=0.0):
    """Frames for papers standing on the floor, leaning back against a wall at z_wall (covers facing +z), each in
    front of the previous one. items = [(w, h, t), ...]."""
    a = deg * DEG
    fwd = Vector((0, math.sin(a), math.cos(a)))
    up = Vector((0, math.cos(a), -math.sin(a)))
    out = []
    zb = z_wall
    for i, (w, h, t) in enumerate(items):
        if i == 0:
            zb = z_wall + h * math.sin(a)
        o = Vector((dx * (i - (len(items) - 1) / 2), y_floor, zb)) + up * (h / 2)
        out.append(F(tuple(o), tuple(fwd), tuple(up)))
        zb += (t + gap) / math.cos(a)
    return out


# ---------------------------------------------------------------- CPU: printed cube, tuck top, tray, clamshell

def tuck_walls(R, ctx, t, inner, notch_r=0.0):
    """The four printed walls and the bottom of a tuck-top carton (walls up to sy - t; the lid lies on them)."""
    sx, sy, sz = ctx.s
    uv, tex = ctx.uv, ctx.tex
    H = sy - t
    fr = F((0, H / 2, sz / 2), Z, Y)
    if notch_r > 0:
        notched_board(R, "wall_front", fr, sx, H, t, inner, tex, sub_uv(uv["front"], 0, H / sy), notch_r)
    else:
        R.board("wall_front", fr, sx, H, t, inner, tex=tex, uv=sub_uv(uv["front"], 0, H / sy))
    R.board("wall_back", F((0, H / 2, -sz / 2), NZ, Y), sx, H, t, inner, tex=tex, uv=sub_uv(uv["back"], 0, H / sy))
    for sgn, nm, face in ((-1, "wall_left", "left"), (1, "wall_right", "right")):
        fr = F((sgn * sx / 2, H / 2, 0), (sgn, 0, 0), Y)
        R.cube(nm, (0, 0, -t / 2), (sz - 2 * t, H, t), inner, fr)
        R.quad(nm + "_print", fr.sub(0, 0, 0.00015), sz, H, tex, sub_uv(uv[face], 0, H / sy))
    fb = F((0, 0, 0), NY, Z)
    R.cube("bottom", (0, 0, -t / 2), (sx - 2 * t, sz - 2 * t, t), inner, fb)
    R.quad("bottom_print", fb.sub(0, 0, 0.00015), sx, sz, tex, uv["bottom"])
    return H


def tuck_lid_top(R, ctx, t, inner, open_deg=-115, order=1, under=None, tongue=0.015, label="tuck flap"):
    """The tuck-top lid: hinged along the back top edge, its tongue tucked inside the front wall."""
    sx, sy, sz = ctx.s
    H = sy - t
    a = R.anchor("A_FLAP_0", F((0, H, -sz / 2 + t / 2)), (sx, t, sz), hinge="x", open=open_deg, tuck=1, label=label,
                 order=order, under=under)
    R.board("lid", F((0, sy, 0), Y, NZ), sx, sz, t, inner, anc=a, tex=ctx.tex, uv=ctx.uv["top"])
    # the tongue folds down inside the front wall (with a rounded fold at the lid's front edge)
    R.cube("lid_tongue", (0, H - tongue / 2 - 0.0006, sz / 2 - t - t / 2 - 0.0003), (sx - 2 * t - 0.004, tongue, t * 0.9),
           inner, anc=a)
    R.cube("lid_fold", (0, H - 0.0004, sz / 2 - t - 0.0002), (sx - 2 * t - 0.004, 0.0012, t * 1.2), inner, anc=a, bevel=0.0003)
    return a


def dust_flaps(R, ctx, t, inner, y_top, fw, order=2, under=("A_FLAP_0",), first=1, end_gap=0.006):
    """Two dust flaps hinged on the side walls' top edges, folded in under the lid (printed side up)."""
    sx, sy, sz = ctx.s
    names = []
    for i, sgn in enumerate((-1, 1)):
        nm = f"A_FLAP_{first + i}"
        xh = sgn * (sx / 2 - t)
        R.anchor(nm, F((xh, y_top, 0)), (fw, t, sz - 2 * t), hinge="z", open=-95 * sgn, label="dust flap", order=order,
                 under=list(under))
        zh = sz / 2 - t - 0.0012
        zt = sz / 2 - t - end_gap
        x0, x1 = xh, xh - sgn * fw
        out = [(x0, -zh), (x1, -zt), (x1, zt), (x0, zh)]
        if sgn > 0:
            out = list(reversed(out))
        fr = P.plane((0, y_top - t / 2 - 0.0002, 0), X, Z)
        R.slab("dust", out, t, inner, fr, anc=nm)
        R.slab("dust_print", out, 0.00004, ctx.tex, P.plane((0, y_top - 0.00015, 0), X, Z),
               anc=nm, uv=ctx.uv["flapL" if sgn < 0 else "flapR"], uv_bounds=(min(x0, x1), -zh, max(x0, x1), zh))
        names.append(nm)
    return names


def clamshell(R, ctx, centre, cav, depth_ledge, depth_pocket, flange, parent, order_lid, order_clam, under_lid,
              under_clam, base_tag="black_plastic", lid_tag="smoke_plastic", dome=0.0048, idx=0, part_pad=0.0018,
              lid_open=-170, label="clamshell"):
    """A CPU clamshell: a moulded base (flange, a ledge for the substrate, a pocket that keeps the pads off the
    plastic) and a hinged dome lid with a pull tab and snap bosses. centre = the flange's top surface centre."""
    cx, cy, cz = centre
    fw, fd = flange
    cw, cd = cav
    clam = R.anchor(f"A_INSERT_CLAM_{idx}", F((cx, cy - 0.0012, cz)), (fw, depth_pocket + 0.008, fd), parent=parent,
                    lift="+y", dist=0.05, label=label, order=order_clam, under=under_clam)
    fr = F((cx, cy, cz), Y, NZ)    # local z up, local y toward the back
    n = 64
    t = 0.0005
    rings = [(rr(fw, fd, 0.004, n=n), -0.0012), (rr(fw, fd, 0.004, n=n), 0.0),
             (rr(cw + 2 * part_pad + 0.002, cd + 2 * part_pad + 0.002, 0.003, n=n), 0.0),
             (rr(cw + 2 * part_pad, cd + 2 * part_pad, 0.0025, n=n), -depth_ledge),
             (rr(cw - 0.006, cd - 0.006, 0.002, n=n), -depth_ledge),
             (rr(cw - 0.0075, cd - 0.0075, 0.0018, n=n), -depth_pocket)]
    R.shell("clam_base", rings, t, base_tag, fr, anc=clam, ref=1, up=1, smooth=30)
    # snap bosses on the front corners
    for sx_ in (-1, 1):
        R.cylinder("clam_snap", fr.sub(sx_ * (fw / 2 - 0.0055), -(fd / 2 - 0.0055), 0.0), 0.0022, 0.0014, base_tag, 16,
                   anc=clam, z0=0.0, r2=0.0016)
    lid = R.anchor(f"A_CLAMLID_{idx}", F((cx, cy + 0.0005, cz - fd / 2)), (fw, dome + 0.002, fd), parent=clam,
                   hinge="x", open=lid_open, label=label + " lid", order=order_lid, under=under_lid)
    lr = [(rr(fw, fd, 0.004, n=n), 0.001), (rr(cw + 2 * part_pad + 0.0025, cd + 2 * part_pad + 0.0025, 0.003, n=n), 0.001),
          (rr(cw + 2 * part_pad + 0.0005, cd + 2 * part_pad + 0.0005, 0.0028, n=n), dome),
          (rr(cw - 0.004, cd - 0.004, 0.0025, n=n), dome + 0.0007)]
    R.shell("clam_lid", lr, t, lid_tag, fr, anc=lid, ref=0, up=1, smooth=30)
    R.slab("clam_tab", rr(0.016, 0.007, 0.0025, 0, -(fd / 2 + 0.0025)), t, lid_tag, fr.sub(0, 0, 0.00075), anc=lid)
    for sx_ in (-1, 1):
        R.cylinder("clam_snapcap", fr.sub(sx_ * (fw / 2 - 0.0055), -(fd / 2 - 0.0055), 0.0011), 0.0027, 0.0016, lid_tag, 16,
                   anc=lid, z0=0.0, r2=0.0021)
    return clam, lid


def build_cpu(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0008
    inner = "paper_white"
    H = tuck_walls(R, ctx, t, inner, notch_r=0.009)
    # two round clear seals over the tuck flap's front edge
    for i, xs in enumerate((-0.030, 0.030)):
        seal_round(R, f"A_SEAL_{i}", xs, sy, sz / 2, 0.016, 0.005, text=ctx.it["brand"] + " SEALED")
    tuck_lid_top(R, ctx, t, inner, open_deg=-115, under=["A_SEAL_0", "A_SEAL_1"])
    flaps = dust_flaps(R, ctx, t, inner, H, 0.026)
    opened = ["A_FLAP_0"] + flaps
    # the black cardboard tray: a deck with a window for the clamshell on four folded legs
    tt = 0.0008
    zf = sz / 2 - t - 0.0018
    zb = -0.030
    tw = sx - 2 * t - 0.0016
    td = zf - zb
    zc = (zf + zb) / 2
    yd = 0.050
    tray = R.anchor("A_INSERT_CARD_0", F((0, t, zc)), (tw, yd - t, td), lift="+y", dist=0.10, label="cardboard tray",
                    order=3, under=opened)
    lo, hi = PART_BOUNDS[pid]
    cw, cd = hi[0] - lo[0], hi[1] - lo[1]
    fsw = ctx.sw["field"]
    R.slab("tray_deck", P.rrect(tw, td, 0.0008), tt, ctx.tin, P.plane((0, yd - tt / 2, zc), X, NZ),
           holes=[P.rrect(cw + 0.0066, cd + 0.0066, 0.003, 0, 0)], anc=tray, uv_solid=fsw)
    legh = yd - tt - t
    lip = 0.010
    for nm, cen, siz in (("tray_leg", (0, yd - tt - lip / 2, zf - tt / 2), (tw, lip, tt)),
                         ("tray_leg", (0, t + legh / 2, zb + tt / 2), (tw, legh, tt)),
                         ("tray_leg", (-(tw / 2 - tt / 2), t + legh / 2, zc), (tt, legh, td - 2 * tt)),
                         ("tray_leg", (tw / 2 - tt / 2, t + legh / 2, zc), (tt, legh, td - 2 * tt))):
        R.cube(nm, cen, siz, ctx.tin, anc=tray, uv_solid=fsw)
    # a printed band on the deck's front edge
    R.quad("tray_print", F((0, yd + 0.0001, zf - 0.0065), Y, NZ), 0.06, 0.012, ctx.tin, sub_uv(ctx.iuv["end"], 0.3, 0.7), anc=tray)
    # the clamshell on the deck
    clam, lid = clamshell(R, ctx, (0, yd + 0.0012, zc), (cw, cd), 0.003, 0.0068, (cw + 0.026, cd + 0.026), tray,
                          order_lid=4, order_clam=6, under_lid=[tray], under_clam=["A_ITEM_PART_0"])
    R.anchor("A_ITEM_PART_0", F((0, yd + 0.0012 - 0.003, zc), Y, NZ), bsize(pid, 0.0005), parent=clam, bag="none",
             label="CPU", order=5, under=[lid])
    # papers standing behind the tray, covers facing the front
    zwall = -sz / 2 + t
    docs = [("guide", "leaflet", (0.096, 0.062, 0.0012), "quick install guide"),
            ("warranty", "card", (0.088, 0.056, 0.0004), "warranty card"),
            ("sticker", "sheet", (0.064, 0.044, 0.0006), "case badge sticker")]
    frs = lean_stack([d[2] for d in docs], t + 0.0003, zwall + 0.0003, 5.0, dx=0.004)
    for i, (k, form, size, lab) in enumerate(docs):
        doc(R, i, frs[i], size, k, form, 3, under=opened, label=lab)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_CARD_0": (0, 0.11, 0.0), "A_INSERT_CLAM_0": (0, 0.03, 0.0), "A_ITEM_PART_0": (0, 0.03, 0.0),
                 "A_ITEM_DOC_0": (0.13, 0.02, 0.04), "A_ITEM_DOC_1": (0.12, 0.0, 0.07), "A_ITEM_DOC_2": (0.11, -0.02, 0.10),
                 "A_SEAL_0": (0, 0.02, 0.03), "A_SEAL_1": (0, 0.02, 0.03)}
    NOTES[pid] = ("CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers "
                  "behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6).")
    return R


# ---------------------------------------------------------------- thermoformed trays (blisters with several cavities)

def blister(R, name, frame, flange, cavities, depth, t, tag, anc, lip=0.0012, dome=False, r_flange=0.004,
            floor_inset=0.0016):
    """A thermoformed sheet: a flat flange (w, d) in the frame's XY plane at z=0 with cavities (w, d, r, cx, cy)
    going down by depth (or domes going up when dome=True), a small turned-down lip around the flange."""
    fw, fd = flange
    holes = [P.rrect(cw, cd, cr, cx, cy, 6) for cw, cd, cr, cx, cy in cavities]
    sgn = 1.0 if dome else -1.0
    R.slab(name + "_flange", P.rrect(fw, fd, r_flange, 0, 0, 6), t, tag, frame.sub(0, 0, -t / 2 if not dome else t / 2),
           holes=holes, anc=anc)
    if lip > 0:
        n = 64
        R.shell(name + "_lip", [(rr(fw, fd, r_flange, n=n), -lip), (rr(fw, fd, r_flange, n=n), 0.0),
                                (rr(fw - 0.002, fd - 0.002, r_flange, n=n), 0.0)], t, tag, frame, anc=anc, cap=False,
                ref=1, up=1)
    for cw, cd, cr, cx, cy in cavities:
        n = 56
        dr = 0.0006   # draft
        rings = [(rr(cw, cd, cr, cx, cy, n), 0.0),
                 (rr(cw - 2 * dr, cd - 2 * dr, max(0.0008, cr - dr), cx, cy, n), sgn * (depth - 0.0012)),
                 (rr(cw - 2 * dr - floor_inset, cd - 2 * dr - floor_inset, max(0.0006, cr - dr - floor_inset / 2), cx, cy, n),
                  sgn * depth)]
        R.shell(name, rings, t, tag, frame, anc=anc, ref=1, up=1, smooth=35)


def formed(R, name, frame, flange, cavities, profile, t, tag, anc, lip=0.0012, n=112):
    """A thermoformed sheet with free-form cavities: a flat flange outline (CCW, the frame's XY at z=0) with holes,
    each cavity skinned through profile = [(inset, z), ...] (inset from the hole outline, z down < 0 or up > 0),
    the last ring capped. The flange is a separate flat slab, so cavities of any shape stay clean."""
    R.slab(name + "_flange", flange, t, tag, frame.sub(0, 0, -t / 2 if profile[-1][1] < 0 else t / 2), holes=cavities, anc=anc)
    if lip > 0:
        lp = resample(flange, n)
        R.shell(name + "_lip", [(lp, -lip), (lp, 0.0), (resample(P.poly_offset(flange, -0.001), n), 0.0)], t, tag, frame,
                anc=anc, cap=False, ref=1, up=1)
    for cav in cavities:
        rings = [(resample(P.poly_offset(cav, -inset) if inset else cav, n), z) for inset, z in profile]
        R.shell(name, rings, t, tag, frame, anc=anc, ref=len(rings) - 2, up=1, smooth=35)


# ---------------------------------------------------------------- GPU: printed sleeve, black inner box, PE foam

def build_gpu(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    uv, tex, tin, sw = ctx.uv, ctx.tex, ctx.tin, ctx.sw
    ts, tl, tb = 0.0006, 0.0015, 0.0015
    # --- the printed sleeve (open at both ends), slides off along +x
    sl = R.anchor("A_SLEEVE_0", F((0, 0, 0)), (sx, sy, sz), slide="+x", dist=sx + 0.03, label="sleeve", order=0)
    R.board("sleeve_top", F((0, sy, 0), Y, NZ), sx, sz, ts, "paper_white", anc=sl, tex=tex, uv=uv["top"])
    R.board("sleeve_bottom", F((0, 0, 0), NY, Z), sx, sz, ts, "paper_white", anc=sl, tex=tex, uv=uv["bottom"])
    for nm, z_, fwd, face in (("sleeve_front", sz / 2, Z, "front"), ("sleeve_back", -sz / 2, NZ, "back")):
        fr = F((0, sy / 2, z_), fwd, Y)
        R.cube(nm, (0, 0, -ts / 2), (sx, sy - 2 * ts, ts), "paper_white", fr, anc=sl)
        R.quad(nm + "_print", fr.sub(0, 0, 0.00015), sx, sy, tex, uv[face], anc=sl)
    # --- the rigid black inner box: a base and a lift-off lid with a ribbon pull tab
    Lz = sz - 2 * ts
    y0, y1 = ts, sy - ts
    ds = 0.034
    blk = sw["field"]
    lid = R.anchor("A_LID_0", F((0, y1 - ds, 0)), (sx, ds, Lz), lift="+y", dist=0.08, label="lid", order=1,
                   under=[sl])
    R.cube("lid_top", (0, y1 - tl / 2, 0), (sx, tl, Lz), tin, anc=lid, uv_solid=blk)
    R.quad("lid_logo", F((0, y1 + 0.00012, 0), Y, NZ), 0.13, 0.13 * 0.5, tin, sub_uv(ctx.iuv["logo"], 0.25, 0.75), anc=lid)
    for sg in (-1, 1):
        R.cube("lid_skirt", (0, y1 - ds / 2 - tl / 2, sg * (Lz / 2 - tl / 2)), (sx, ds - tl, tl), tin, anc=lid, uv_solid=blk)
        R.cube("lid_skirt", (sg * (sx / 2 - tl / 2), y1 - ds / 2 - tl / 2, 0), (tl, ds - tl, Lz - 2 * tl), tin, anc=lid,
               uv_solid=blk)
        R.quad("lid_end", F((sg * (sx / 2 + 0.00012), y1 - ds / 2 - tl / 2, 0), (sg, 0, 0), Y), Lz * 0.7, (ds - tl) * 0.7,
               tin, sub_uv(ctx.iuv["end"], 0.1, 0.9), anc=lid)
    # ribbon tab: a loop hanging from the lid's front skirt over the base wall
    rib = sw["ribbon"]
    zr = Lz / 2 - tl - 0.0008
    R.cube("ribbon", (0, y1 - ds - 0.006, zr + 0.0004), (0.014, 0.016, 0.0006), tin, anc=lid, uv_solid=rib)
    R.cube("ribbon", (0, y1 - ds - 0.0138, zr + 0.0001), (0.014, 0.0012, 0.0010), tin, anc=lid, uv_solid=rib, bevel=0.0004)
    # base
    bx, bz = sx - 2 * tl - 0.0006, Lz - 2 * tl - 0.0006
    hb = y1 - tl - y0
    R.cube("base_floor", (0, y0 + tb / 2, 0), (bx, tb, bz), tin, uv_solid=blk)
    for sg in (-1, 1):
        R.cube("base_wall", (0, y0 + hb / 2, sg * (bz / 2 - tb / 2)), (bx, hb, tb), tin, uv_solid=blk)
        R.cube("base_wall", (sg * (bx / 2 - tb / 2), y0 + hb / 2, 0), (tb, hb, bz - 2 * tb), tin, uv_solid=blk)
        R.quad("base_end", F((sg * (bx / 2 + 0.00012), y0 + (hb - ds) / 2 + 0.002, 0), (sg, 0, 0), Y), bz * 0.62,
               (hb - ds) * 0.62, tin, sub_uv(ctx.iuv["end"], 0.05, 0.95))
    # --- the card's pose: fans up, bracket at +x, top edge to the back, centred, on the foam floor
    lo, hi = PART_BOUNDS[pid]
    yf = y0 + tb + 0.0022 + 0.012            # top of the foam's floor layer (papers under the foam)
    ax = -(lo[0] + hi[0]) / 2
    az = (lo[2] + hi[2]) / 2
    ay = yf + hi[1] + 0.0004
    # --- the black PE foam cradle: laminated die-cut layers, a pocket of the card's outline, finger notches
    fx, fz = bx - 2 * tb - 0.001, bz - 2 * tb - 0.001
    fy0 = y0 + tb + 0.0022
    fy1 = min(ay - lo[1] - 0.010, y1 - tl - 0.012)
    foam = R.anchor("A_INSERT_FOAM_0", F((0, fy0, 0)), (fx, fy1 - fy0, fz), lift="+y", dist=0.09, label="foam cradle",
                    order=3, under=["A_ITEM_PART_0"])
    pad = 0.006
    pw, pd = (hi[0] - lo[0]) + 2 * pad, (hi[2] - lo[2]) + 2 * pad
    pcx = ax + (lo[0] + hi[0]) / 2
    pcz = az - (lo[2] + hi[2]) / 2
    layers = [(fy0, yf)]
    h_up = (fy1 - yf)
    nl = 3
    for k in range(nl):
        layers.append((yf + h_up * k / nl + 0.00025, yf + h_up * (k + 1) / nl))
    for k, (ya, yb) in enumerate(layers):
        fr = P.plane((0, (ya + yb) / 2, 0), X, NZ)
        if k == 0:
            R.slab("foam", P.rrect(fx, fz, 0.002), yb - ya, "pe_foam", fr, anc=foam)
        else:
            hole = P.rrect(pw, pd, 0.004, pcx, -pcz, 6)
            ob = R.slab("foam", P.rrect(fx, fz, 0.002), yb - ya, "pe_foam", fr, holes=[hole], anc=foam)
            cuts = [RC.tmp_cyl(F((pcx + dx_, (ya + yb) / 2, pcz + sg * pd / 2), Y, Z), 0.017, (yb - ya) + 0.004, 24)
                    for sg in (-1, 1) for dx_ in (-pw * 0.22, pw * 0.22)]
            R.cut(ob, cuts)
    # the card in its anti-static bag
    R.anchor("A_ITEM_PART_0", F((ax, ay, az), NZ, NY), bsize(pid, 0.004), parent=foam, bag="antistatic_silver",
             label="graphics card", order=2, under=[lid])
    # papers under the foam, on the base floor
    yd = y0 + tb + 0.0001
    papers = [("guide", "leaflet", (0.170, 0.115, 0.0016), (-0.075, -0.004), "quick install guide"),
              ("driver", "card", (0.120, 0.080, 0.0004), (0.080, 0.010), "driver note"),
              ("sticker", "sheet", (0.070, 0.050, 0.0006), (0.105, -0.035), "case badge sticker")]
    for i, (k, form, size, (px, pz), lab) in enumerate(papers):
        doc(R, i, flat_frame((px, yd + (0.0005 if i == 2 else 0.0), pz)), size, k, form, 4, under=[foam], label=lab)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_SLEEVE_0": (sx + 0.06, 0, 0), "A_LID_0": (0, 0.20, -0.20), "A_INSERT_FOAM_0": (0, 0.10, 0),
                 "A_ITEM_PART_0": (0, 0.09, 0), "A_ITEM_DOC_0": (0, 0.0, 0.20), "A_ITEM_DOC_1": (0.02, 0.0, 0.21),
                 "A_ITEM_DOC_2": (0.0, 0.0, 0.24)}
    R.open_view = (24, 50)
    NOTES[pid] = ("GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) "
                  "-> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4).")
    return R


# ---------------------------------------------------------------- motherboard: hinged shoulder box, tray, pad, compartment

def build_mb(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    uv, tex, tin, sw = ctx.uv, ctx.tex, ctx.tin, ctx.sw
    t = 0.0015
    inner = "cardboard"
    ds = 0.022              # the lid's skirt
    hs = sy - ds            # the shoulder
    H = sy - t
    blk = sw["field"]
    # base: the printed outer walls up to the shoulder (the back wall to the top), a black neck above the shoulder
    R.board("wall_front", F((0, hs / 2, sz / 2), Z, Y), sx, hs, t, inner, tex=tex, uv=sub_uv(uv["front"], 0, hs / sy))
    R.board("wall_back", F((0, H / 2, -sz / 2), NZ, Y), sx, H, t, inner, tex=tex, uv=sub_uv(uv["back"], 0, H / sy))
    for sg, face in ((-1, "left"), (1, "right")):
        fr = F((sg * sx / 2, hs / 2, 0), (sg, 0, 0), Y)
        R.cube("wall_side", (0, 0, -t / 2), (sz - 2 * t, hs, t), inner, fr)
        R.quad("wall_side_print", fr.sub(0, 0, 0.00015), sz, hs, tex, sub_uv(uv[face], 0, hs / sy))
    fb = F((0, 0, 0), NY, Z)
    R.cube("bottom", (0, 0, -t / 2), (sx - 2 * t, sz - 2 * t, t), inner, fb)
    R.quad("bottom_print", fb.sub(0, 0, 0.00015), sx, sz, tex, uv["bottom"])
    yn0, yn1 = hs - 0.010, H - 0.0004
    hn = yn1 - yn0
    R.cube("neck", (0, yn0 + hn / 2, sz / 2 - t - t / 2 - 0.0002), (sx - 2 * t, hn, t), tin, uv_solid=blk)
    for sg in (-1, 1):
        R.cube("neck", (sg * (sx / 2 - t - t / 2 - 0.0002), yn0 + hn / 2, -t / 2), (t, hn, sz - 3 * t - 0.0004), tin,
               uv_solid=blk)
    # seals across the lid/base seam on both sides
    for i, sg in enumerate((-1, 1)):
        seal_rect_flat(R, f"A_SEAL_{i}", F((sg * (sx / 2 + 0.00025), hs, 0.07), (sg, 0, 0), Y), 0.012, 0.030, text="SEALED")
    # the flip-top lid with skirts on three sides, hinged at the back top edge
    lid = R.anchor("A_LID_0", F((0, H, -sz / 2 + t / 2)), (sx, ds, sz), hinge="x", open=-105, label="lid", order=1,
                   under=["A_SEAL_0", "A_SEAL_1"])
    R.board("lid_top", F((0, sy, 0), Y, NZ), sx, sz, t, inner, anc=lid, tex=tex, uv=uv["top"])
    frf = F((0, sy - t - (ds - t) / 2, sz / 2), Z, Y)
    R.cube("lid_skirt_front", (0, 0, -t / 2), (sx, ds - t, t), inner, frf, anc=lid)
    R.quad("lid_skirt_front_print", F((0, sy - ds / 2, sz / 2 + 0.00015), Z, Y), sx, ds, tex,
           sub_uv(uv["front"], hs / sy, 1.0), anc=lid)
    for sg, face in ((-1, "left"), (1, "right")):
        fr = F((sg * sx / 2, sy - t - (ds - t) / 2, -t / 2), (sg, 0, 0), Y)
        R.cube("lid_skirt_side", (0, 0, -t / 2), (sz - 3 * t, ds - t, t), inner, fr, anc=lid)
        R.quad("lid_skirt_print", F((sg * (sx / 2 + 0.00015), sy - ds / 2, 0), (sg, 0, 0), Y), sz, ds, tex,
               sub_uv(uv[face], hs / sy, 1.0), anc=lid)
    # the board's pose: component side up, top edge to -x, rear I/O to the back
    lo, hi = PART_BOUNDS[pid]
    y_floor = t
    ycomp = 0.0135                       # accessory compartment height
    td = 0.0015
    yd1 = y_floor + ycomp + td           # deck top
    pad_t = 0.0045
    yb = yd1 + pad_t + 0.0004 - lo[2]    # board origin (PCB bottom); the solder side rests on the pad
    az = (lo[0] + hi[0]) / 2
    # the corrugated tray (a deck on folded legs) with two finger holes
    tw, tdp = sx - 2 * t - 0.0016, sz - 2 * t - 0.0016
    tray = R.anchor("A_INSERT_CARD_0", F((0, y_floor, 0)), (tw, yd1 - y_floor, tdp), lift="+y", dist=0.08,
                    label="cardboard tray", order=4, under=["A_INSERT_FOAM_0"])
    holes = [P.stadium(0.014, 0.030, sg * (tw / 2 - 0.014), 0) for sg in (-1, 1)]
    R.slab("tray_deck", P.rrect(tw, tdp, 0.001), td, inner, P.plane((0, yd1 - td / 2, 0), X, NZ), holes=holes, anc=tray)
    for sg in (-1, 1):
        R.cube("tray_leg", (0, y_floor + ycomp / 2, sg * (tdp / 2 - td / 2)), (tw, ycomp, td), inner, anc=tray)
        R.cube("tray_leg", (sg * (tw / 2 - td / 2), y_floor + ycomp / 2, 0), (td, ycomp, tdp - 2 * td), inner, anc=tray)
    # the white foam pad on the tray
    pw, pdp = 0.300, 0.250
    foam = R.anchor("A_INSERT_FOAM_0", F((0, yd1, 0)), (pw, pad_t, pdp), parent=tray, lift="+y", dist=0.06,
                    label="foam pad", order=3, under=["A_ITEM_PART_0"])
    R.cube("pad", (0, yd1 + pad_t / 2, 0), (pw, pad_t, pdp), "eps_foam", anc=foam, bevel=0.0012)
    R.anchor("A_ITEM_PART_0", F((0, yb, az), Y, NX), bsize(pid, 0.003), parent=foam, bag=ctx.it.get("bag", "antistatic_pink"),
             label="motherboard", order=2, under=[lid])
    # the accessory compartment under the tray
    yc = y_floor + 0.0001
    under_t = [tray]
    io = "io_" + pid[3:]
    R.anchor("A_ITEM_ACC_0", F((0.060, yc + 0.0068 + 0.0006, 0.075), NZ, X), bsize(io, 0.004), id=io, bag="clear",
             frame="model", label="I/O shield", order=5, under=under_t)
    R.anchor("A_ITEM_CORD_0", flat_frame((0.085, yc, -0.040)), (0.120, 0.075, 0.012), kind="sata", tie="twist",
             label="SATA cables", order=5, under=under_t)
    R.anchor("A_ITEM_HW_0", flat_frame((-0.005, yc, -0.075)), (0.050, 0.070, 0.004), label="M.2 SCREW", order=5,
             under=under_t)
    doc(R, 0, flat_frame((-0.075, yc, 0.020)), (0.148, 0.210, 0.0035), "manual", "booklet", 6, under=["A_ITEM_DOC_1"],
        label="user manual")
    doc(R, 1, flat_frame((-0.072, yc + 0.0036, 0.016)), (0.140, 0.200, 0.0016), "guide", "leaflet", 5, under=under_t,
        label="quick install poster")
    doc(R, 2, flat_frame((0.010, yc, 0.060)), (0.090, 0.060, 0.0004), "warranty", "card", 5, under=under_t, label="warranty card")
    doc(R, 3, flat_frame((0.010, yc, -0.005)), (0.070, 0.050, 0.0006), "sticker", "sheet", 5, under=under_t,
        label="case badge sticker")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.11, 0), "A_INSERT_FOAM_0": (0, 0.05, 0), "A_INSERT_CARD_0": (0, 0.10, 0),
                 "A_SEAL_0": (-0.03, 0, 0), "A_SEAL_1": (0.03, 0, 0),
                 "A_ITEM_ACC_0": (0.03, 0.0, 0.26), "A_ITEM_CORD_0": (0.06, 0.0, 0.40), "A_ITEM_HW_0": (0.10, 0.0, 0.40),
                 "A_ITEM_DOC_0": (-0.10, 0.0, 0.30), "A_ITEM_DOC_1": (-0.05, 0.02, 0.32), "A_ITEM_DOC_2": (0.10, 0.0, 0.24),
                 "A_ITEM_DOC_3": (0.15, 0.0, 0.32)}
    R.explode_fill = 0.7
    R.open_view = (16, 55)
    R.explode_view = (24, 32)
    NOTES[pid] = ("MB: side seals (0) -> hinged lid A_LID_0 (1) -> board in its bag (2, on the pad) -> foam pad (3) -> tray (4) "
                  "-> compartment: I/O shield A_ITEM_ACC_0, SATA cables A_ITEM_CORD_0, M.2 screw bag A_ITEM_HW_0, poster, "
                  "warranty, sticker (5) -> manual under the poster (6).")
    return R


# ---------------------------------------------------------------- tuck-end cartons (RAM, SSDs)

def end_tuck_box(R, ctx, t, inner, tongue=0.008, seal=None, order0=0):
    """A flat carton whose +x end is a tuck flap: hinged at the BOTTOM edge of the end, its tongue tucked inside
    along the top panel (a seal can then sit across the flap's free top edge), with two dust flaps behind it.
    Returns the anchor names that cover the inside."""
    sx, sy, sz = ctx.s
    uv, tex = ctx.uv, ctx.tex
    xe = sx / 2 - t                         # the inside face of the end flap
    R.board("top", F((-t / 2, sy, 0), Y, NZ), sx - t, sz, t, inner, tex=tex, uv=sub_uv(uv["top"], 0.0, 1.0 - t / sx, "u"))
    R.board("bottom", F((-t / 2, 0, 0), NY, Z), sx - t, sz, t, inner, tex=tex, uv=sub_uv(uv["bottom"], 0.0, 1.0 - t / sx, "u"))
    for nm, z_, fwd, face in (("front", sz / 2, Z, "front"), ("back", -sz / 2, NZ, "back")):
        fr = F((0, sy / 2, z_), fwd, Y)
        R.cube(nm, (t / 2 if z_ > 0 else -t / 2, 0, -t / 2), (sx - t, sy - 2 * t, t), inner, fr)
        R.quad(nm + "_print", fr.sub(0, 0, 0.00015), sx, sy, tex, uv[face])
    frl = F((-sx / 2, sy / 2, 0), NX, Y)
    R.cube("end_left", (0, 0, -t / 2), (sz - 2 * t, sy - 2 * t, t), inner, frl)
    R.quad("end_left_print", frl.sub(0, 0, 0.00015), sz, sy, tex, uv["left"])
    under = [seal] if seal else None
    flap = R.anchor("A_FLAP_0", F((xe + t / 2, t, 0)), (t, sy, sz), hinge="z", open=-92, tuck=1, label="end flap",
                    order=order0 + 1, under=under)
    fr = F((sx / 2, sy / 2 + t / 2, 0), X, Y)
    R.cube("flap", (0, 0, -t / 2), (sz - 2 * t - 0.0004, sy - t - 0.0002, t), inner, fr, anc=flap)
    R.quad("flap_print", fr.sub(0, -t / 2, 0.00015), sz, sy, tex, uv["right"], anc=flap)
    R.cube("flap_tongue", (xe - tongue / 2, sy - t - t / 2 - 0.0002, 0), (tongue, t * 0.9, sz - 2 * t - 0.004), inner, anc=flap)
    R.cube("flap_fold", (xe - 0.0004, sy - t - 0.0006, 0), (0.0012, 0.0014, sz - 2 * t - 0.004), inner, anc=flap, bevel=0.0003)
    names = []
    dw = min(0.016, sz * 0.18)
    xd = xe - t / 2 - 0.0003
    for i, sg in enumerate((1, -1)):
        nm = f"A_FLAP_{1 + i}"
        zh = sg * (sz / 2 - t)
        R.anchor(nm, F((xd, sy / 2, zh)), (t, sy - 2 * t, dw), hinge="y", open=-95 * sg, label="dust flap",
                 order=order0 + 2, under=[flap])
        hy0, hy1 = sy / 2 - t - 0.0006, sy / 2 - t - 0.003
        out = [(zh, -hy0), (zh - sg * dw, -hy1), (zh - sg * dw, hy1), (zh, hy0)]
        R.slab("dust", out, t, inner, P.plane((xd, sy / 2, 0), Z, Y), anc=nm)
        names.append(nm)
    return [flap] + names


def build_ram(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0007
    inner = "paper_white"
    covers = end_tuck_box(R, ctx, t, inner, tongue=0.008)
    lo, hi = PART_BOUNDS[pid]
    sh = hi[2] - lo[2]                       # stick height (lies along z)
    sth = hi[0] - lo[0]
    flw, fld = 0.148, sz - 2 * t - 0.004
    bxc = -sx / 2 + t + 0.0008 + flw / 2
    depth = 0.0090
    yfl = t + 0.0004 + depth                  # flange top
    bl = R.anchor("A_INSERT_BLISTER_0", F((bxc, t, 0)), (flw, 0.017, fld), lift="+x", dist=0.17, label="blister tray",
                  order=3, under=covers)
    cav_w = 0.1365
    cav_d = sh + 0.0030
    zc = [fld / 4 + 0.0005, -fld / 4 - 0.0005]
    fr = F((bxc, yfl, 0), Y, NZ)              # local x = box x, local y = -box z, local z up
    blister(R, "blister", fr, (flw, fld), [(cav_w, cav_d, 0.003, 0, -z_) for z_ in zc], depth, 0.0005, "clear_plastic",
            bl, lip=0.0010)
    lidn = R.anchor("A_CLAMLID_0", F((bxc, yfl + 0.0005, -fld / 2 + 0.006)), (flw, 0.008, fld - 0.006), parent=bl,
                    hinge="x", open=-165, label="blister lid", order=5, under=["A_SEAL_0", "A_ITEM_DOC_0"])
    frl = F((bxc, yfl + 0.0005, 0.003), Y, NZ)
    blister(R, "blister_lid", frl, (flw, fld - 0.006), [(cav_w + 0.001, cav_d + 0.001, 0.003, 0, -(z_ - 0.003)) for z_ in zc],
            0.0050, 0.0005, "clear_plastic", lidn, lip=0.0, dome=True)
    # seal on the lid's front edge, onto the base flange's front tab
    seal_rect_flat(R, "A_SEAL_0", F((bxc, yfl + 0.0011, fld / 2 - 0.006), Y, Z), 0.014, 0.012, order=4, peel="+y",
                   under=[bl], parent=bl)
    # the two sticks, gold fingers to the front, label side up
    for i, z_ in enumerate(zc):
        zf = z_ + sh / 2
        R.anchor(f"A_ITEM_PART_{i}", F((bxc, yfl - depth + 0.0005 + sth / 2 + 0.0004, zf), NZ, X), bsize(pid, 0.0012),
                 parent=bl, bag="none", guard=1, label="memory stick", order=6, under=[lidn])
    # the installation card lying on the blister lid
    doc(R, 0, flat_frame((bxc + 0.004, yfl + 0.0056, 0.0), Y, NZ), (0.120, 0.085, 0.0004), "guide", "card", 4, under=[bl],
        parent=bl, label="installation card")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_BLISTER_0": (0.22, 0.03, 0), "A_ITEM_DOC_0": (0, 0.05, 0), "A_SEAL_0": (0, 0.02, 0.02),
                 "A_ITEM_PART_0": (0, 0.03, 0.02), "A_ITEM_PART_1": (0, 0.03, -0.02)}
    R.open_view = (40, 48)
    R.explode_view = (35, 35)
    R.open_extra = {"A_INSERT_BLISTER_0": (0.12, 0, 0)}
    NOTES[pid] = ("RAM: end tuck flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> blister tray A_INSERT_BLISTER_0 slides out +x (3), "
                  "then on it: installation card A_ITEM_DOC_0 and the blister seal A_SEAL_0 (4) -> blister lid A_CLAMLID_0 (5) "
                  "-> sticks A_ITEM_PART_0/1 (6, guard=1).")
    return R


# ---------------------------------------------------------------- SSDs: tuck-end cartons with a blister or a tray

def build_ssd_m2(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0007
    inner = "paper_white"
    seal_round(R, "A_SEAL_0", 0.0, sy, sx / 2, 0.015, 0.005, text="QUILL SEALED", face="right")
    covers = end_tuck_box(R, ctx, t, inner, tongue=0.007, seal="A_SEAL_0")
    lo, hi = PART_BOUNDS[pid]
    # papers on the floor, under the blister
    yc = t + 0.0001
    doc(R, 0, flat_frame((-0.004, yc, 0.002)), (0.090, 0.060, 0.0004), "guide", "card", 4, under=["A_INSERT_BLISTER_0"],
        label="installation card")
    doc(R, 1, flat_frame((-0.002, yc + 0.0005, -0.002)), (0.088, 0.058, 0.0004), "warranty", "card", 4,
        under=["A_INSERT_BLISTER_0"], label="warranty card")
    flw, fld = 0.098, sz - 2 * t - 0.006
    bxc = -sx / 2 + t + 0.0008 + flw / 2
    depth = 0.0042
    yb0 = yc + 0.0011
    yfl = yb0 + depth
    bl = R.anchor("A_INSERT_BLISTER_0", F((bxc, yb0, 0)), (flw, 0.010, fld), lift="+x", dist=0.12, label="blister tray",
                  order=3, under=covers)
    cw, cd = (hi[0] - lo[0]) + 0.0035, (hi[1] - lo[1]) + 0.0035
    fr = F((bxc, yfl, 0), Y, NZ)
    blister(R, "blister", fr, (flw, fld), [(cw, cd, 0.002, 0, 0)], depth, 0.0005, "clear_plastic", bl, lip=0.0010)
    # a finger notch at the front of the cavity so the drive can be lifted out
    R.shell("blister_notch", [(rr(0.014, 0.010, 0.004, 0, -cd / 2 - 0.002, 40), 0.0),
                               (rr(0.012, 0.008, 0.0035, 0, -cd / 2 - 0.002, 40), -depth + 0.0012),
                               (rr(0.010, 0.006, 0.0028, 0, -cd / 2 - 0.002, 40), -depth)], 0.0005, "clear_plastic", fr,
            anc=bl, ref=1, up=1)
    lid = R.anchor("A_CLAMLID_0", F((bxc, yfl + 0.0005, -fld / 2)), (flw, 0.005, fld), parent=bl, hinge="x", open=-170,
                   label="blister lid", order=4, under=[bl])
    blister(R, "blister_lid", F((bxc, yfl + 0.0005, 0), Y, NZ), (flw, fld), [(cw + 0.001, cd + 0.001, 0.002, 0, 0)], 0.0028,
            0.0005, "clear_plastic", lid, lip=0.0, dome=True)
    R.anchor("A_ITEM_PART_0", F((bxc, yfl - depth + 0.0001, 0), Y, NZ), bsize(pid, 0.001), parent=bl, bag="none",
             label="M.2 SSD", order=5, under=[lid])
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_BLISTER_0": (0.15, 0.02, 0), "A_ITEM_PART_0": (0, 0.02, 0), "A_SEAL_0": (0.03, 0.01, 0),
                 "A_ITEM_DOC_0": (0.0, 0.0, 0.10), "A_ITEM_DOC_1": (0.0, 0.0, 0.17)}
    R.open_view = (40, 50)
    R.explode_view = (32, 38)
    R.open_extra = {"A_INSERT_BLISTER_0": (0.08, 0, 0)}
    NOTES[pid] = ("SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> "
                  "blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the "
                  "blister (4) -> SSD (5).")
    return R


def build_ssd_sata(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0007
    inner = "paper_white"
    seal_round(R, "A_SEAL_0", 0.0, sy, sx / 2, 0.016, 0.005, text="QUILL SEALED", face="right")
    covers = end_tuck_box(R, ctx, t, inner, tongue=0.008, seal="A_SEAL_0")
    lo, hi = PART_BOUNDS[pid]
    flw, fld = 0.128, sz - 2 * t - 0.004
    bxc = -sx / 2 + t + 0.0008 + flw / 2
    depth = 0.0105
    yb0 = t + 0.0002
    yfl = yb0 + depth
    tray = R.anchor("A_INSERT_BLISTER_0", F((bxc, yb0, 0)), (flw, depth + 0.002, fld), lift="+x", dist=0.15,
                    label="plastic tray", order=3, under=covers)
    cw, cd = (hi[0] - lo[0]) + 0.0080, (hi[2] - lo[2]) + 0.0080
    fr = F((bxc, yfl, 0), Y, NZ)
    blister(R, "tray", fr, (flw, fld), [(cw, cd, 0.003, 0, 0)], depth, 0.0007, "black_plastic", tray, lip=0.0015)
    # finger scoops at both long sides
    for sg in (-1, 1):
        R.shell("tray_scoop", [(rr(0.022, 0.012, 0.0055, 0, sg * (cd / 2 + 0.003), 40), 0.0),
                               (rr(0.020, 0.010, 0.0048, 0, sg * (cd / 2 + 0.003), 40), -depth + 0.003),
                               (rr(0.017, 0.007, 0.0034, 0, sg * (cd / 2 + 0.003), 40), -depth + 0.0018)], 0.0007,
                "black_plastic", fr, anc=tray, ref=1, up=1)
    R.anchor("A_ITEM_PART_0", F((bxc, yfl - depth + 0.0006 - lo[1] + 0.0004, 0), NZ, Y), bsize(pid, 0.0035), parent=tray, bag="clear",
             label="2.5in SSD", order=5, under=["A_ITEM_DOC_0"])
    doc(R, 0, flat_frame((bxc, yfl + 0.0002, 0.0)), (0.120, 0.080, 0.0004), "guide", "card", 4, under=[tray], parent=tray,
        label="installation card")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_BLISTER_0": (0.19, 0.02, 0), "A_ITEM_PART_0": (0, 0.03, 0), "A_ITEM_DOC_0": (0, 0.07, 0),
                 "A_SEAL_0": (0.03, 0.01, 0)}
    R.open_view = (40, 50)
    R.explode_view = (32, 38)
    R.open_extra = {"A_INSERT_BLISTER_0": (0.10, 0, 0), "A_ITEM_DOC_0": (0.0, 0.0, 0.12)}
    NOTES[pid] = ("SSD SATA: seal (0) -> end flap (1) -> dust flaps (2) -> black tray A_INSERT_BLISTER_0 slides out +x (3) -> "
                  "installation card lying on it (4) -> drive in its clear bag (5).")
    return R


# ---------------------------------------------------------------- corrugated cartons with top flaps and tape

def rsc_box(R, ctx, t, inner, fw=None, tape_tag="tape_clear", tape_w=0.048, tape_down=0.05, open_long=215, open_short=200):
    """A regular slotted carton: four printed walls, two long top flaps (hinged on the front and back walls) over
    two short ones, and a tape strip across the seam and down both ends (3 A_TAPE segments, strip 0).
    Returns the names of the covers (long + short flaps)."""
    sx, sy, sz = ctx.s
    uv, tex = ctx.uv, ctx.tex
    fw = fw or ctx.fw
    bodyH = sy - 2 * t
    e = 0.0003
    hF = bodyH + t

    def suv(u, f0, f1):
        return sub_uv(u, f0, f1)

    R.cube("wall_front", (0, hF / 2, sz / 2 - t / 2 - e), (sx - 2 * e, hF, t), inner)
    R.cube("wall_back", (0, hF / 2, -sz / 2 + t / 2 + e), (sx - 2 * e, hF, t), inner)
    for sg in (-1, 1):
        R.cube("wall_side", (sg * (sx / 2 - t / 2 - e), bodyH / 2, 0), (t, bodyH, sz - 2 * t - 2 * e), inner)
    R.cube("floor", (0, t / 2 + e, 0), (sx - 2 * t, t, sz - 2 * t), inner)
    R.quad("print_front", F((0, hF / 2, sz / 2), Z, Y), sx, hF, tex, suv(uv["front"], 0, hF / sy))
    R.quad("print_back", F((0, hF / 2, -sz / 2), NZ, Y), sx, hF, tex, suv(uv["back"], 0, hF / sy))
    R.quad("print_left", F((-sx / 2, bodyH / 2, 0), NX, Y), sz, bodyH, tex, suv(uv["left"], 0, bodyH / sy))
    R.quad("print_right", F((sx / 2, bodyH / 2, 0), X, Y), sz, bodyH, tex, suv(uv["right"], 0, bodyH / sy))
    R.quad("print_bottom", F((0, 0, 0), NY, Z), sx, sz, tex, uv["bottom"])
    # tape: up the left end, across the seam (along x), down the right end
    L0 = tape_down
    tapes = []
    segs = [(F((-sx / 2 - 0.0002, sy - L0 / 2, 0), NX, Y), (tape_w, L0, 0.0001)),
            (F((0, sy + 0.0002, 0), Y, X), (tape_w, sx, 0.0001)),
            (F((sx / 2 + 0.0002, sy - L0 / 2, 0), X, NY), (tape_w, L0, 0.0001))]
    for i, (fr, size) in enumerate(segs):
        nm = f"A_TAPE_{i}"
        R.anchor(nm, fr, size, strip=0, seg=i, peel="+y", order=0, label="tape")
        uvw = min(1.0, size[1] / 0.6)
        R.quad("tapelook", fr.sub(0, 0, 0.00005), size[0], size[1] + (0.0004 if i == 1 else 0.0), tape_tag, anc=nm,
               uv=(0, 0, 1, uvw) if tape_tag.startswith("tex_") else (0, 0, 1, 1))
        tapes.append(nm)
    # flaps
    yl = bodyH + t
    zf = sz / 2
    gap = 0.0006
    R.anchor("A_FLAP_0", F((0, yl, -zf)), (sx, t, zf), hinge="x", open=-open_long, label="top flap", order=1, under=tapes)
    R.cube("flap", (0, yl + t / 2, -zf / 2 - gap / 2), (sx - 2 * e, t, zf - gap - e), inner, anc="A_FLAP_0")
    R.quad("flap_print", F((0, sy + 0.00015, -zf / 2 - gap / 2), Y, NZ), sx, zf - gap, tex,
           sub_uv(uv["top"], 0.5 + gap / sz / 2, 1.0), anc="A_FLAP_0")
    R.anchor("A_FLAP_1", F((0, yl, zf)), (sx, t, zf), hinge="x", open=open_long, label="top flap", order=1, under=tapes)
    R.cube("flap", (0, yl + t / 2, zf / 2 + gap / 2), (sx - 2 * e, t, zf - gap - e), inner, anc="A_FLAP_1")
    R.quad("flap_print", F((0, sy + 0.00015, zf / 2 + gap / 2), Y, NZ), sx, zf - gap, tex,
           sub_uv(uv["top"], 0.0, 0.5 - gap / sz / 2), anc="A_FLAP_1")
    zs = sz / 2 - t - e - 0.0005
    for i, sg in enumerate((-1, 1)):
        nm = f"A_FLAP_{2 + i}"
        R.anchor(nm, F((sg * sx / 2, bodyH, 0)), (fw, t, sz), hinge="z", open=-open_short * sg, label="top flap", order=2,
                 under=["A_FLAP_0", "A_FLAP_1"])
        xc = sg * (sx / 2 - fw / 2)
        R.cube("flap", (xc, bodyH + t / 2, 0), (fw - e, t, 2 * zs), inner, anc=nm)
        R.quad("flap_print", F((xc, bodyH + t + 0.00012, 0), Y, NZ), fw - e, 2 * zs, tex, uv["flapL" if sg < 0 else "flapR"],
               anc=nm)
    return ["A_FLAP_0", "A_FLAP_1", "A_FLAP_2", "A_FLAP_3"]


def pulp_cap(R, name, anc, x_wall, inward, y0, y1, zw, pocket, pocket_c, Lc, Dp, holes=()):
    """A moulded pulp end cap against the wall at x_wall, open behind (egg-carton style), its face toward the part
    with a pocket of the part's section. pocket = (z, y) size, pocket_c = (z, y) centre in box coordinates."""
    yc = (y0 + y1) / 2
    fr = F((x_wall, yc, 0), (inward, 0, 0), Y)       # local x = -z*inward... (up x fwd)
    hx = fr.u.z                                       # +1 or -1: local x along box z
    pz, py = pocket
    pcx, pcy = pocket_c[0] * hx, pocket_c[1] - yc
    H = y1 - y0
    n = 64
    rings = [(rr(zw, H, 0.008, n=n), 0.0),
             (rr(zw - 0.002, H - 0.002, 0.007, n=n), Lc),
             (rr(pz + 0.0015, py + 0.0015, 0.005, pcx, pcy, n), Lc),
             (rr(pz - 0.0005, py - 0.0005, 0.004, pcx, pcy, n), Lc - Dp + 0.003),
             (rr(pz - 0.004, py - 0.004, 0.003, pcx, pcy, n), Lc - Dp)]
    ob = R.shell(name, rings, 0.0022, "pulp", fr, anc=anc, ref=1, up=1, smooth=30)
    # moulded stiffening dimples on the face band and the hole for a cable stub
    cuts = [RC.tmp_cyl(F(fr.p(hz * 1.0, hy, Lc - Dp), fr.fwd, fr.up), r, 0.03, 20) for (hz, hy, r) in holes]
    if cuts:
        R.cut(ob, cuts)
    return ob


def eps_cap(R, name, anc, x_wall, inward, y0, y1, zw, pocket, pocket_c, Lc, Dp, recess=True):
    """A white EPS end cap: a block with chamfered edges, a pocket for the part's end and moulded recesses behind."""
    yc = (y0 + y1) / 2
    xc = x_wall + inward * Lc / 2
    ob = R.cube(name, (xc, yc, 0), (Lc, y1 - y0, zw), "eps_foam", anc=anc, bevel=0.003)
    pz, py = pocket
    cuts = [RC.tmp_cube((x_wall + inward * (Lc - Dp / 2 + 0.002), pocket_c[1], pocket_c[0]), (Dp + 0.004, py, pz), bevel=0.0015)]
    if recess:
        rd = min(0.012, (Lc - Dp) * 0.5)
        for sz_ in (-1, 1):
            cuts.append(RC.tmp_cube((x_wall + inward * rd / 2 - inward * 0.001, yc, sz_ * zw * 0.24), (rd + 0.002, (y1 - y0) * 0.62,
                                                                                                   zw * 0.30), bevel=0.002))
    R.cut(ob, cuts)
    return ob


def build_psu(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.002
    inner = "cardboard"
    rsc_box(R, ctx, t, inner, tape_tag="tape_clear")
    short = ["A_FLAP_2", "A_FLAP_3"]
    lo, hi = PART_BOUNDS[pid]
    gold = pid == "psu_750"
    xi = sx / 2 - t - 0.0005                  # inner wall faces at +-xi
    zi = sz / 2 - t - 0.0005
    ybot = t + (0.003 if pid == "psu_750" else 0.008)   # the PSU's lowest face; the pulp caps need a thicker floor
    ay = ybot + hi[1]                          # fan up: local -y points up, so the bottom is local +y
    if gold:
        ax = -0.016 - (-0.0704 + 0.073) / 2    # pushed to -x: an accessory compartment at the +x end
    else:
        ax = 0.010 - (-0.0704 + 0.073) / 2     # body a bit to +x: the cable stub reaches into the -x cap
    body_x0, body_x1 = ax - 0.0704, ax + 0.073
    ytop = ay - lo[1]                          # top of the PSU (the fan grille)
    pocket = (0.1521 + 0.004, (hi[1] - lo[1]) + 0.004)
    pc = (0.0, (ybot + ytop) / 2)
    capk = "FOAM" if gold else "PULP"
    caps = []
    Dp = 0.022
    for i, (x_wall, inward, xend) in enumerate(((-xi, 1, body_x0), (xi, -1, body_x1))):
        nm = f"A_INSERT_{capk}_{i}"
        if gold and i == 1:
            x_wall = body_x1 + 0.012          # the +x cap stands off the wall: the compartment is behind it
        Lc = abs(xend - x_wall) + Dp
        y1 = ytop + 0.0005 if gold else 2 * pc[1] - (t + 0.0002)   # EPS: saddle caps flush with the top; pulp: cups
        R.anchor(nm, F((x_wall, t, 0)), (Lc, y1 - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.06,
                 with_="A_ITEM_PART_0", label=("EPS end cap" if gold else "pulp end cap"), order=7, under=["A_ITEM_PART_0"])
        if gold:
            eps_cap(R, "cap", nm, x_wall, inward, t + 0.0002, y1, 2 * zi - 0.001, pocket, pc, Lc, Dp, recess=(i == 0))
        else:
            holes = [(0.030, (ay - 0.024) - (t + 0.0002 + y1) / 2, 0.018)] if i == 0 else []
            pulp_cap(R, "cap", nm, x_wall, inward, t + 0.0002, y1, 2 * zi - 0.001, pocket, pc, Lc, Dp, holes=holes)
        caps.append(nm)
    if gold:
        # the cable pouch on the PSU and the caps, the papers on the pouch; cord and screws in the +x compartment
        R.anchor("A_ITEM_PART_0", F((ax, ay, 0.0), NZ, NY), bsize(pid, 0.003), bag="fabric", label="power supply", order=6,
                 under=["A_ITEM_POUCH_0"])
        yp = ytop + 0.0008
        R.anchor("A_ITEM_POUCH_0", flat_frame((ax, yp, 0.0)), (0.150, 0.130, 0.017), label="modular cable pouch",
                 order=5, under=["A_ITEM_DOC_0"])
        yd = yp + 0.0172
        xc = (body_x1 + 0.012 + xi) / 2
        R.anchor("A_ITEM_CORD_0", F((xc - 0.008, t + 0.0005 + 0.045, 0.022), X, Y), (0.120, 0.090, 0.016), kind="c13",
                 tie="twist", label="power cord", order=3, under=short)
        R.anchor("A_ITEM_HW_0", F((xc + 0.009, t + 0.0005 + 0.035, -0.050), X, Y), (0.050, 0.070, 0.005),
                 label="4 x 6-32 SCREWS", order=3, under=short)
    else:
        # the power cord and the screw bag on the PSU between the caps, the papers across the caps
        R.anchor("A_ITEM_PART_0", F((ax, ay, 0.0), NZ, NY), bsize(pid, 0.003), bag="clear", label="power supply", order=6,
                 under=["A_ITEM_CORD_0", "A_ITEM_HW_0"])
        yp = ytop + 0.0003
        xm = (body_x0 + body_x1) / 2 + 0.004
        R.anchor("A_ITEM_CORD_0", flat_frame((xm, yp, -0.030)), (0.090, 0.075, 0.014), kind="c13", tie="twist",
                 label="power cord", order=5, under=["A_ITEM_DOC_0"])
        R.anchor("A_ITEM_HW_0", flat_frame((xm, yp, 0.050)), (0.050, 0.045, 0.004), label="4 x 6-32 SCREWS", order=5,
                 under=["A_ITEM_DOC_0"])
        yd = max(yp + 0.0143, 2 * pc[1] - (t + 0.0002) + 0.0003)
    doc(R, 0, flat_frame((ax - 0.010, yd, 0.004)), (0.105, 0.148, 0.003), "manual", "booklet", 4, under=["A_ITEM_DOC_1"],
        label="user manual")
    doc(R, 1, flat_frame((ax - 0.006, yd + 0.0031, -0.002)), (0.105, 0.148, 0.0006), "safety", "sheet", 3, under=short,
        label="safety sheet")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.16, 0), "A_ITEM_DOC_0": (0, 0.36, 0.12), "A_ITEM_DOC_1": (0, 0.38, 0.22),
                 "A_ITEM_CORD_0": (0.0, 0.30, -0.16), "A_ITEM_HW_0": (0.12, 0.30, -0.10), "A_ITEM_POUCH_0": (0, 0.30, 0),
                 caps[0]: (-0.07, 0.16, 0), caps[1]: (0.07, 0.16, 0),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    R.open_view = (22, 55)
    R.explode_fill = 0.75
    if gold:
        NOTES[pid] = ("PSU 750: tape strip 0 (A_TAPE_0..2) (0) -> long flaps (1) -> short flaps (2) -> safety sheet, and the power "
                      "cord + screw bag standing in the +x compartment (3) -> manual (4) -> cable pouch A_ITEM_POUCH_0 (5) -> PSU in "
                      "its fabric bag, lifted out WITH its two EPS saddle caps (6) -> caps A_INSERT_FOAM_0/1 pulled off along "
                      "-x/+x (7).")
    else:
        NOTES[pid] = ("PSU 450: tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> safety sheet (3) -> manual (4) -> power cord "
                      "and screw bag on the PSU (5) -> PSU in its clear bag, lifted out WITH its pulp caps (6) -> caps "
                      "A_INSERT_PULP_0/1 pulled off along -x/+x (7). Cap 0 has a hole for the cable bundle stub.")
    return R


# ---------------------------------------------------------------- coolers

def polar_outline(base_r, lobes, n=96, cx=0.0, cy=0.0):
    """A star-shaped outline: a circle of radius base_r with smooth lobes (angle, radius, half width)."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = base_r
        for (la, lr, lw) in lobes:
            d = math.atan2(math.sin(a - la), math.cos(a - la))
            if abs(d) < lw:
                k = 0.5 + 0.5 * math.cos(math.pi * d / lw)
                r = max(r, base_r + (lr - base_r) * min(1.0, k * 1.6))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def chaikin(pts, iters=2, k=0.22):
    """Rounds the corners of a closed polygon (corner cutting)."""
    for _ in range(iters):
        out = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            out.append((a[0] + (b[0] - a[0]) * (1 - k), a[1] + (b[1] - a[1]) * (1 - k)))
        pts = out
    return pts


def build_cooler_stock(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0008
    inner = "paper_white"
    H = tuck_walls(R, ctx, t, inner, notch_r=0.010)
    tuck_lid_top(R, ctx, t, inner, open_deg=-115, order=1)
    flaps = dust_flaps(R, ctx, t, inner, H, 0.028)
    opened = ["A_FLAP_0"] + flaps
    lo, hi = PART_BOUNDS[pid]
    # the leaflet on the floor, under the clamshell
    yc = t + 0.0001
    doc(R, 0, flat_frame((0.004, yc, 0.004)), (0.100, 0.070, 0.0015), "guide", "leaflet", 4, under=["A_INSERT_CLAM_0"],
        label="quick install guide")
    # the cooler: fan up, its fan cable and plug toward the back (they stick out 30 mm past the shroud)
    yb = yc + 0.0016 + 0.0006                    # clamshell floor
    ay = yb - lo[2] + 0.0002
    flz = 0.020                                  # the clamshell's parting line, in cooler z
    yfl = ay + flz
    wx, wz = sx - 2 * t - 0.0016, sz - 2 * t - 0.0016
    bm = 0.0019                                  # cavity margin around the shroud
    half = hi[0] + bm
    tab_end = hi[1] + 0.003                      # past the plug
    span = 2 * half + (tab_end - hi[0])
    yb0 = -span / 2                              # cavity front edge, in the clam frame (local y = -box z)
    az = -(yb0 + half)                           # cooler centre (box z)
    cy = -az
    body = [(-half, cy - half), (half, cy - half), (half, cy + half), (0.030, cy + half), (0.030, cy + tab_end),
            (-0.010, cy + tab_end), (-0.010, cy + half), (-half, cy + half)]
    outline = chaikin(body, 2)
    clam = R.anchor("A_INSERT_CLAM_0", F((0, yb, 0)), (wx, (hi[2] - lo[2]) + 0.006, wz), lift="+y", dist=0.10,
                    label="clamshell", order=3, under=opened)
    fr = F((0, yfl, 0), Y, NZ)
    base_depth = yfl - yb
    flange = P.rrect(wx, wz, 0.004, 0, 0, 6)
    formed(R, "clam_base", fr, flange, [outline], [(0.0, 0.0), (0.0008, -(base_depth - 0.003)), (0.0030, -base_depth)],
           0.0005, "clear_plastic", clam, lip=0.0015)
    top_h = (ay + hi[2]) - yfl + 0.003
    lid = R.anchor("A_CLAMLID_0", F((0, yfl + 0.0005, -wz / 2)), (wx, top_h, wz), parent=clam, hinge="x", open=-170,
                   label="clamshell lid", order=4, under=[clam])
    lsq = chaikin([(-half, cy - half), (half, cy - half), (half, cy + half), (-half, cy + half)], 2, 0.12)
    formed(R, "clam_lid", fr.sub(0, 0, 0.0005), flange, [lsq], [(0.0, 0.0), (0.0012, top_h - 0.004), (0.0060, top_h)], 0.0005,
           "clear_plastic", lid, lip=0.0)
    R.slab("clam_tab", rr(0.018, 0.008, 0.003, 0, -(wz / 2 + 0.003)), 0.0005, "clear_plastic", fr.sub(0, 0, 0.00075), anc=lid)
    R.anchor("A_ITEM_PART_0", F((0, ay, az), Y, NZ), bsize(pid, 0.002), parent=clam, bag="none", label="CPU cooler", order=5,
             under=[lid])
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_CLAM_0": (0, 0.12, 0), "A_ITEM_PART_0": (0, 0.07, 0), "A_ITEM_DOC_0": (0.14, 0.0, 0.05)}
    R.open_view = (20, 55)
    NOTES[pid] = ("Stock cooler: tuck lid A_FLAP_0 (1) -> dust flaps (2) -> clear clamshell A_INSERT_CLAM_0 lifted out (3) -> "
                  "clamshell lid A_CLAMLID_0 and the leaflet under the clamshell (4) -> cooler (5). Box depth 0.15 (was 0.12): "
                  "the model's fan plug sits 30 mm past the shroud, so the clamshell has a pocket for it behind the cooler.")
    return R


def accessory_box(R, ctx, name, frame, size, parent, flap_idx, order, under, lift="+y", dist=0.14, inside=None,
                  label="accessory box"):
    """A small white tuck box (the accessory box). frame: its bottom centre, local axes = the box axes; the tuck
    flap is on its top (local +y), hinged at the top back edge."""
    w, h, d = size
    t = 0.0006
    meta = dict(lift=lift, dist=dist, label=label, order=order, under=under)
    if inside:
        meta["inside"] = inside
    a = R.anchor(name, frame, size, parent=parent, **meta)
    sw = ctx.sw["white"]
    acc = ctx.iuv["acc"]
    for sg in (-1, 1):
        R.cube("acc_wall", frame.p(0, h / 2 - t / 2, sg * (d / 2 - t / 2)), (w, h - t, t), ctx.tin, anc=a, uv_solid=sw)
        R.cube("acc_wall", frame.p(sg * (w / 2 - t / 2), h / 2 - t / 2, 0), (t, h - t, d - 2 * t), ctx.tin, anc=a, uv_solid=sw)
    R.cube("acc_floor", frame.p(0, t / 2, 0), (w - 2 * t, t, d - 2 * t), ctx.tin, anc=a, uv_solid=sw)
    big = max(w, d)
    # the printed face: the larger of the front and the top
    if h >= d:
        R.quad("acc_print", F(frame.p(0, h / 2, d / 2 + 0.0001), frame.fwd, frame.up), w * 0.96, h * 0.9, ctx.tin, acc, anc=a)
    fl = f"A_FLAP_{flap_idx}"
    R.anchor(fl, F(frame.p(0, h - t, -d / 2 + t / 2), frame.fwd, frame.up), (w, t, d), parent=a, hinge="x", open=-120,
             tuck=1, label="accessory box flap", order=order + 1, under=[a])
    R.cube("acc_lid", frame.p(0, h - t / 2, 0), (w, t, d), ctx.tin, anc=fl, uv_solid=sw)
    if h < d:
        R.quad("acc_print", F(frame.p(0, h + 0.0001, 0), (0, 1, 0), (0, 0, -1)), w * 0.96, d * 0.9, ctx.tin, acc, anc=fl)
    R.cube("acc_tongue", frame.p(0, h - t - 0.006, d / 2 - t - t / 2 - 0.0002), (w - 2 * t - 0.002, 0.012, t), ctx.tin, anc=fl,
           uv_solid=sw)
    return a, fl


def build_cooler_tower(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.002
    inner = "cardboard"
    rsc_box(R, ctx, t, inner, tape_tag="tape_clear")
    short = ["A_FLAP_2", "A_FLAP_3"]
    lo, hi = PART_BOUNDS[pid]
    xi, zi = sx / 2 - t - 0.0005, sz / 2 - t - 0.0005
    y_in = sy - 2 * t
    # the cooler stands upright: local z up, local y toward +x (fan plug side), local x toward the front
    ax = -(lo[1] + hi[1]) / 2
    az = -0.0135
    ay = t + 0.008 - lo[2]
    bf_top = ay + 0.016                           # bottom foam's top face
    tf_bot = ay + 0.142                           # top foam's underside
    fw_ = 2 * xi - 0.001
    fd_ = 2 * zi - 0.001
    # bottom EPS: pocket for the base and the screws, a channel for the fan plug
    fb = R.anchor("A_INSERT_FOAM_1", F((0, t, 0)), (fw_, bf_top - t, fd_), lift="+y", dist=0.07, label="bottom foam",
                  order=5, under=["A_ITEM_PART_0", "A_INSERT_ACCBOX_0"])
    ob = R.cube("foam_bottom", (0, (t + bf_top) / 2 + 0.0001, 0), (fw_, bf_top - t - 0.0002, fd_), "eps_foam", anc=fb, bevel=0.002)
    cuts = [RC.tmp_cube((ax, (bf_top + ay - 0.0125) / 2 + 0.002, az), (0.085, bf_top - (ay - 0.0125) + 0.004, 0.085), bevel=0.002),
            RC.tmp_cube((ax + 0.062, bf_top - 0.006, az - 0.034), (0.060, 0.016, 0.018), bevel=0.002)]
    R.cut(ob, cuts)
    # top EPS: a pocket for the fin stack and fan tops, finger notches at both ends
    ft = R.anchor("A_INSERT_FOAM_0", F((0, tf_bot, 0)), (fw_, y_in - tf_bot, fd_), lift="+y", dist=0.07, label="top foam",
                  order=3, under=short)
    ob = R.cube("foam_top", (0, (tf_bot + y_in) / 2, 0), (fw_, y_in - tf_bot - 0.0004, fd_), "eps_foam", anc=ft, bevel=0.002)
    pk_h = (ay + hi[2]) - tf_bot + 0.002
    cuts = [RC.tmp_cube((ax, tf_bot + pk_h / 2 - 0.001, az + (lo[0] + hi[0]) / 2), (0.131, pk_h + 0.002, (hi[0] - lo[0]) + 0.004),
                        bevel=0.0015)]
    for sg in (-1, 1):
        cuts.append(RC.tmp_cyl(F((sg * xi, (tf_bot + y_in) / 2, 0.0), Y, Z), 0.016, y_in - tf_bot + 0.01, 24))
    R.cut(ob, cuts)
    R.anchor("A_ITEM_PART_0", F((ax, ay, az), Y, X), bsize(pid, 0.002), parent=fb, bag="none", label="tower cooler", order=4,
             under=[ft])
    # the accessory box stands in front of the cooler, between the foams
    zb0 = az + hi[0] + 0.004
    d_acc = zi - zb0 - 0.0015
    acc, accflap = accessory_box(R, ctx, "A_INSERT_ACCBOX_0", F(((0.0, bf_top + 0.0005, zb0 + d_acc / 2))),
                                 (0.140, tf_bot - bf_top - 0.003, d_acc), None, 4, 4, [ft])
    ya = bf_top + 0.0005 + 0.0007
    za = zb0 + 0.0008
    R.anchor("A_ITEM_HW_0", F((-0.030, ya + 0.050, za + 0.0003), Z, Y), (0.070, 0.100, 0.012), parent=acc,
             label="MOUNTING KIT V5/L17", order=6, under=[accflap])
    R.anchor("A_ITEM_HW_1", F((0.040, ya + 0.040, za + 0.0023), Z, Y), (0.012, 0.075, 0.009), parent=acc, kind="syringe",
             label="THERMAL PASTE", order=6, under=[accflap])
    # the syringe (a look: the game's paste is a bench tool): barrel, plunger, cap
    sf = F((0.040, ya + 0.040, za + 0.0023 + 0.0045), Y, Z)
    R.cylinder("syringe", sf.sub(0, 0, -0.030), 0.0042, 0.050, "white_plastic", 20, anc="A_ITEM_HW_1", z0=0.0)
    R.cylinder("syringe", sf.sub(0, 0, 0.020), 0.0015, 0.010, "grey_plastic", 16, anc="A_ITEM_HW_1", z0=0.0, r2=0.0009)
    R.cylinder("syringe", sf.sub(0, 0, -0.037), 0.0030, 0.008, "grey_plastic", 16, anc="A_ITEM_HW_1", z0=0.0)
    R.cylinder("syringe", sf.sub(0, 0, -0.039), 0.0065, 0.0015, "grey_plastic", 20, anc="A_ITEM_HW_1", z0=0.0)
    doc(R, 0, F((0.0, ya + 0.062, za + 0.013), Z, Y),
        (0.120, 0.120, 0.0025), "manual", "booklet", 6, under=[accflap], parent=acc, label="manual")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_FOAM_0": (0, 0.20, 0), "A_ITEM_PART_0": (0, 0.06, -0.20), "A_INSERT_ACCBOX_0": (0.0, 0.08, 0.20),
                 "A_ITEM_HW_0": (-0.04, 0.12, 0.05), "A_ITEM_HW_1": (0.06, 0.12, 0.05), "A_ITEM_DOC_0": (0.0, 0.18, 0.08),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    R.open_view = (22, 58)
    R.explode_fill = 0.72
    R.open_extra = {"A_INSERT_FOAM_0": (-0.22, -tf_bot + t, 0.0)}
    NOTES[pid] = ("Tower cooler: tape (0) -> long flaps (1) -> short flaps (2) -> top EPS A_INSERT_FOAM_0 (3) -> cooler A_ITEM_PART_0 "
                  "and the accessory box A_INSERT_ACCBOX_0 standing in front of it (4) -> bottom EPS A_INSERT_FOAM_1 and the "
                  "accessory box's tuck flap A_FLAP_4 (5) -> mounting kit A_ITEM_HW_0, paste syringe A_ITEM_HW_1 (kind=syringe, "
                  "a look mesh on its anchor), manual A_ITEM_DOC_0 (6).")
    return R


# ---------------------------------------------------------------- case: brown printed carton, EPS caps, bag

def build_case(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0045
    inner = "cardboard"
    rsc_box(R, ctx, t, inner, tape_tag="tex_box_tape", tape_w=0.048, tape_down=0.07)
    short = ["A_FLAP_2", "A_FLAP_3"]
    lo, hi = PART_BOUNDS[pid]
    xi, zi = sx / 2 - t - 0.0005, sz / 2 - t - 0.0005
    y_in = sy - 2 * t
    lip = 0.040
    ax = -(lo[0] + hi[0]) / 2
    az = -(lo[2] + hi[2]) / 2
    ay = t + lip - lo[1]
    R.anchor("A_ITEM_PART_0", F((ax, ay, az)), bsize(pid, 0.004), bag="clear", label="PC case", order=3, under=short)
    # the two EPS end caps hold the case's front and rear ends; they come out with it
    pocket_y = (hi[1] - lo[1]) + 0.004
    pocket_z = (hi[2] - lo[2]) + 0.004
    yc = (t + y_in) / 2
    for i, (x_wall, inward, xend, lab) in enumerate(((-xi, 1, ax + lo[0], "front EPS cap"), (xi, -1, ax + hi[0], "rear EPS cap"))):
        nm = f"A_INSERT_FOAM_{i}"
        Dp = 0.045
        Lc = abs(xend - x_wall) + Dp
        R.anchor(nm, F((x_wall, t, 0)), (Lc, y_in - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.10,
                 with_="A_ITEM_PART_0", label=lab, order=4, under=["A_ITEM_PART_0"])
        ob = R.cube("cap", (x_wall + inward * Lc / 2, yc, 0), (Lc, y_in - t - 0.002, 2 * zi - 0.002), "eps_foam", anc=nm, bevel=0.006)
        cuts = [RC.tmp_cube((x_wall + inward * (Lc - Dp / 2 + 0.002), ay + (lo[1] + hi[1]) / 2, az + (lo[2] + hi[2]) / 2),
                            (Dp + 0.004, pocket_y, pocket_z), bevel=0.003)]
        # moulded relief: two deep pockets behind (toward the wall) and a hand grip slot near the top
        for sy_ in (-1, 1):
            cuts.append(RC.tmp_cube((x_wall + inward * 0.012, yc + sy_ * 0.13, 0), (0.026, 0.16, 0.20), bevel=0.006))
        cuts.append(RC.tmp_cube((x_wall + inward * (Lc - Dp) / 2, y_in - 0.030, 0), (0.026, 0.024, 0.12), bevel=0.008))
        R.cut(ob, cuts)
    # the accessory box rides inside the case on the PSU shroud (or on the bottom fans), behind the glass (case frame offsets)
    shroud = ACC_SHELF.get(pid, 0.1045)
    ab = F((ax + 0.020, ay + shroud, az + 0.015))
    acc, accflap = accessory_box(R, ctx, "A_INSERT_ACCBOX_0", ab, (0.160, 0.034, 0.110), "A_ITEM_PART_0", 4, 5,
                                 ["A_ITEM_PART_0"], lift="+z", dist=0.18, inside="A_PANEL_SIDE_0")
    ya = ay + shroud + 0.0007
    R.anchor("A_ITEM_DOC_0", flat_frame((ax + 0.020, ya, az + 0.015)), (0.148, 0.105, 0.003), parent=acc, doc="manual",
             form="booklet", label="manual", order=8, under=["A_ITEM_ACC_0", "A_ITEM_HW_0", "A_ITEM_HW_1"])
    R.anchor("A_ITEM_ACC_0", flat_frame((ax - 0.030, ya + 0.0031, az + 0.012)), (0.050, 0.070, 0.010), parent=acc, id="standoff_bag",
             bag="clear", frame="flat", label="standoffs", order=7, under=[accflap])
    R.anchor("A_ITEM_HW_0", flat_frame((ax + 0.030, ya + 0.0031, az + 0.030)), (0.050, 0.070, 0.008), parent=acc,
             label="SCREWS 6-32 / M3", order=7, under=[accflap])
    R.anchor("A_ITEM_HW_1", flat_frame((ax + 0.070, ya + 0.0031, az - 0.005)), (0.040, 0.090, 0.006), parent=acc,
             label="CABLE TIES", order=7, under=[accflap])
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.62, 0), "A_INSERT_FOAM_0": (-0.12, 0.0, 0), "A_INSERT_FOAM_1": (0.12, 0.0, 0),
                 "A_INSERT_ACCBOX_0": (0.0, 0.0, 0.32), "A_ITEM_DOC_0": (0, 0.0, 0.12), "A_ITEM_ACC_0": (0, 0.06, 0.12),
                 "A_ITEM_HW_0": (0.0, 0.06, 0.14), "A_ITEM_HW_1": (0, 0.06, 0.16),
                 "A_TAPE_0": (-0.05, 0.03, 0), "A_TAPE_1": (0, 0.05, 0), "A_TAPE_2": (0.05, 0.03, 0)}
    R.views = ((28, 22), (-150, 24))
    R.open_view = (22, 50)
    R.explode_fill = 0.75
    NOTES[pid] = ("Case: printed tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> the case in its clear bag, lifted out by "
                  "the foam (3) -> front/rear EPS caps A_INSERT_FOAM_0/1, with=A_ITEM_PART_0, pulled off along -x/+x (4). "
                  "Accessory box A_INSERT_ACCBOX_0@A_ITEM_PART_0 sits INSIDE the case on the "
                  + ("bottom fans" if pid in ACC_SHELF else "PSU shroud") + " (case-frame pose "
                  "relative to A_ITEM_PART_0), inside=A_PANEL_SIDE_0: take it out of the side opening (+z) once the glass panel "
                  "is off (5) -> its tuck flap A_FLAP_4 (6) -> standoff bag A_ITEM_ACC_0 (id=standoff_bag, frame=flat), "
                  "screws A_ITEM_HW_0, cable ties A_ITEM_HW_1 (6) -> manual A_ITEM_DOC_0 (7).")
    return R


# ---------------------------------------------------------------- USB installer: blister card

def build_usb(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    tex = ctx.tex
    ct = 0.0007
    hole_y = sz / 2 - 0.012
    card = P.rrect(sx, sz, 0.004)
    hole = P.stadium(0.026, 0.006, 0, hole_y)
    fr = P.plane((0, ct / 2, 0), X, NZ)       # local y = -z: the hang hole at the back
    R.slab("card", card, ct, "paper_white", fr, holes=[hole])
    R.slab("card_print", card, 0.00004, tex, P.plane((0, ct + 0.00003, 0), X, NZ), holes=[hole],
           uv=(8 / 1024, 8 / 1024, 508 / 1024, 1016 / 1024), uv_bounds=(-sx / 2, -sz / 2, sx / 2, sz / 2))
    R.slab("card_back", card, 0.00004, tex, P.plane((0, -0.00003, 0), X, Z), holes=[P.stadium(0.026, 0.006, 0, -hole_y)],
           uv=(516 / 1024, 8 / 1024, 1016 / 1024, 1016 / 1024), uv_bounds=(-sx / 2, -sz / 2, sx / 2, sz / 2))
    # the blister bubble, hinged at its back edge (heat-sealed flange)
    bw, bl, bh = 0.034, 0.078, 0.016
    bz = 0.016                                # blister centre (box z)
    lid = R.anchor("A_CLAMLID_0", F((0, ct, bz - bl / 2 - 0.004)), (bw + 0.01, bh, bl + 0.01), hinge="x", open=-150,
                   label="blister", order=1, under=["A_SEAL_0"])
    frb = F((0, ct + 0.0002, bz), Y, NZ)
    n = 64
    rings = [(rr(bw + 0.010, bl + 0.010, 0.006, n=n), 0.0), (rr(bw, bl, 0.008, n=n), 0.0),
             (rr(bw - 0.002, bl - 0.002, 0.0075, n=n), bh * 0.75), (rr(bw - 0.006, bl - 0.005, 0.0062, n=n), bh)]
    R.shell("blister", rings, 0.0004, "clear_plastic", frb, anc=lid, ref=0, up=1, smooth=40)
    # the seal across the blister's front flange onto the card
    seal_rect_flat(R, "A_SEAL_0", F((0, ct + 0.0007, bz + bl / 2 + 0.006), Y, Z), 0.020, 0.014, order=0, text="SEALED")
    R.anchor("A_ITEM_PART_0", F((0, ct + 0.0012 + 0.0041, bz + 0.026), NZ, Y), bsize("usb_stick", 0.001), bag="none",
             label="installer USB stick", order=2, under=[lid])
    doc(R, 0, flat_frame((0, ct + 0.0002, bz)), (0.030, 0.070, 0.0004), "guide", "card", 3, under=["A_ITEM_PART_0"],
        label="quick start card")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.05, 0), "A_ITEM_DOC_0": (0.07, 0.0, 0.0), "A_SEAL_0": (0, 0.02, 0.03)}
    R.open_view = (25, 55)
    NOTES[pid] = ("USB installer: seal A_SEAL_0 across the blister's front flange (0) -> the blister A_CLAMLID_0 swings open on "
                  "its back edge (1; no parent: the card is the rig body) -> stick (2) -> quick start card under it (3).")
    return R


# ---------------------------------------------------------------- cable items: a clear zip bag with a header card

def build_bag(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    dp = pid == "cable_dp"
    hl = 0.050 if dp else 0.040               # header card length (at the back, -z)
    bw = sx
    blen = sz - hl + 0.012                    # the bag runs up under the header
    bz0 = sz / 2 - blen / 2                   # bag centre z
    hgt = sy - 0.004                          # puffed by the coil
    # the bag: a pillow of two clear films with a sealed rim
    secs = []
    for k, (inset, y) in enumerate(((0.020, 0.0012), (0.006, hgt * 0.30), (0.002, hgt * 0.5), (0.006, hgt * 0.72),
                                    (0.020, hgt - 0.0005))):
        secs.append((rr(bw - 2 * inset, blen - 2 * inset, 0.010, 0, -bz0, 64), y))
    R.loft("bag", secs, "bag_clear", F((0, 0, 0), Y, NZ), smooth=60)
    R.slab("bag_seam", P.rrect(bw, blen, 0.004, 0, -bz0), 0.0004, "bag_clear", P.plane((0, hgt * 0.5, 0), X, NZ),
           holes=[P.rrect(bw - 0.008, blen - 0.008, 0.008, 0, -bz0)])
    # the zip track across the bag just below the header
    zz = sz / 2 - blen + 0.020
    for k in range(2):
        R.cube("zip", (0, hgt * 0.5 + 0.0008, zz + k * 0.003), (bw - 0.006, 0.0012, 0.0016),
               "grey_plastic", bevel=0.0004)
    # the header card folded over the top of the bag, stapled
    hz = -sz / 2 + hl / 2
    ht = 0.0006
    hy = hgt * 0.5
    R.cube("header", (0, hy + ht / 2 + 0.0008, hz), (bw, ht, hl), "paper_white")
    R.cube("header", (0, hy - ht / 2 - 0.0008, hz), (bw, ht, hl), "paper_white")
    R.cube("header_fold", (0, hy, -sz / 2 + 0.0005), (bw, 0.0028, 0.001), "paper_white", bevel=0.0004)
    hole = P.stadium(0.024, 0.0065, 0, sz / 2 - 0.009)
    R.slab("header_print", P.rrect(bw, hl, 0.0015, 0, sz / 2 - hl / 2), 0.00004, ctx.tex,
           P.plane((0, hy + ht + 0.0009, 0), X, NZ), holes=[hole], uv=(0, 0.5, 1, 1),
           uv_bounds=(-bw / 2, sz / 2 - hl, bw / 2, sz / 2))
    R.slab("header_print", P.rrect(bw, hl, 0.0015, 0, -(sz / 2 - hl / 2)), 0.00004, ctx.tex,
           P.plane((0, hy - ht - 0.0009, 0), X, Z), holes=[P.stadium(0.024, 0.0065, 0, -(sz / 2 - 0.009))], uv=(0, 0, 1, 0.5),
           uv_bounds=(-bw / 2, -sz / 2, bw / 2, -(sz / 2 - hl)))
    for sg in (-1, 1):
        R.cube("staple", (sg * bw * 0.3, hy + ht + 0.0012, hz + hl * 0.25), (0.010, 0.0005, 0.0008), "steel")
    # the zip lip opens: the top film between the zip and the header lifts
    fl = R.anchor("A_FLAP_0", F((0, hy, zz)), (bw, 0.002, 0.016), hinge="x", open=-55, label="zip", order=0)
    R.cube("zip_lip", (0, hy + 0.0011, zz - 0.007), (bw - 0.008, 0.0004, 0.014), "bag_clear", anc=fl)
    R.cube("zip_lip", (0, hy + 0.0016, zz - 0.0005), (bw - 0.006, 0.0012, 0.0016), "grey_plastic", anc=fl, bevel=0.0004)
    coil = (0.115, 0.115, 0.020) if dp else (0.070, 0.080, 0.012)
    R.anchor("A_ITEM_PART_0", flat_frame((0, 0.0016, sz / 2 - blen / 2 + 0.006)), coil, bag="none", frame="flat",
             coil=("dp" if dp else "fan_splitter"), tie="twist", label=("DisplayPort cable" if dp else "fan splitter"),
             order=1, under=[fl])
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.05, 0)}
    R.views = ((20, 40), (-150, 30))
    R.open_view = (15, 55)
    NOTES[pid] = ("Cable bag: zip A_FLAP_0 (0) -> the coiled item A_ITEM_PART_0 (1; frame=flat, coil=" + ("dp" if dp else "fan_splitter")
                  + ", tie=twist: the game spawns the coiled cable with its twist tie). The bag and its stapled header card are the "
                  "rig body (trash once empty).")
    return R


# ---------------------------------------------------------------- previews

def _item_model(rig, anc, ctx):
    m = rig.meta.get(anc, {})
    if anc.startswith("A_ITEM_PART_"):
        mid = {"usb_installer": "usb_stick"}.get(ctx.pid, ctx.pid)
        return mid if mid in PART_BOUNDS else None
    if anc.startswith("A_ITEM_ACC_") and m.get("frame") == "model":
        return m.get("id")
    return None


BAG_TAGS = {"antistatic_pink": "antistatic_pink", "antistatic_silver": "antistatic_silver", "clear": "bag_clear",
            "fabric": "fabric_black"}


def add_contents(rig, ctx):
    """Preview stand-ins for everything the game spawns: the part models, papers, bags, cords, pouches."""
    for anc, m in rig.meta.items():
        if not anc.startswith("A_ITEM_"):
            continue
        mid = _item_model(rig, anc, ctx)
        if mid:
            RC.place_model(rig, mid, anc)
            bag = m.get("bag")
            if bag and bag != "none" and mid in PART_BOUNDS:
                s = rig.sizes[anc]
                RC.stand_in(rig, anc, BAG_TAGS.get(bag, "bag_clear"), center=bcentre(mid), size=s, bevel=0.003)
            continue
        if anc.startswith("A_ITEM_PART_"):
            RC.stand_in(rig, anc, "rubber", bevel=0.004)
        elif anc.startswith("A_ITEM_DOC_"):
            RC.stand_in(rig, anc, "paper_white", bevel=0.0002)
        elif anc.startswith("A_ITEM_HW_"):
            RC.stand_in(rig, anc, "bag_clear", bevel=0.002)
        elif anc.startswith("A_ITEM_CORD_"):
            RC.stand_in(rig, anc, "rubber", bevel=0.006)
        elif anc.startswith("A_ITEM_POUCH_"):
            RC.stand_in(rig, anc, "fabric_black", bevel=0.004)
        elif anc.startswith("A_ITEM_ACC_"):
            RC.stand_in(rig, anc, "bag_clear", bevel=0.002)


def _is_cover(name):
    return name.startswith(("A_FLAP_", "A_LID_", "A_SLEEVE_", "A_CLAMLID_"))


def opened_moves(rig):
    """Covers open: hinges swung open, sleeves slid off, lift-off lids set down behind the box."""
    moves = {}
    sz = rig.sizes.get("A_HIT_0", (0.2, 0.1, 0.2))[2]
    for a, m in rig.meta.items():
        if not _is_cover(a):
            continue
        if a.startswith("A_LID_") and "lift" in m and "hinge" not in m:
            moves[a] = Matrix.Translation(c.conv((0, 0, -(sz + 0.03))))
        else:
            moves[a] = RC.anchor_motion(rig, a)
    for a, d in getattr(rig, "open_extra", {}).items():
        moves[a] = Matrix.Translation(c.conv(d)) @ moves.get(a, Matrix.Identity(4))
    return moves


def exploded_moves(rig):
    moves = {}
    ex = getattr(rig, "explode", {})
    for a, m in rig.meta.items():
        if a.startswith(("A_HIT_",)):
            continue
        if a in ex:
            base = RC.anchor_motion(rig, a, 1.0) if _is_cover(a) and ("hinge" in m) else Matrix.Identity(4)
            moves[a] = Matrix.Translation(c.conv(ex[a])) @ base
        elif _is_cover(a) or a.startswith("A_INSERT_"):
            moves[a] = RC.anchor_motion(rig, a, 1.0)
    return moves


def previews(rig, ctx):
    if not P.PREVIEW[0]:
        return
    bid = rig.bid
    root = rig.root
    views = getattr(rig, "views", ((28, 24), (-150, 26)))
    P.beauty(root, bid, views=views, size=(1100, 850), samples=48, start_index=0)
    # opened: covers open, contents in place
    add_contents(rig, ctx)
    seals = [o for o in c.descendants(root) if o.type == "MESH" and ("@A_SEAL_" in o.name or "@A_TAPE_" in o.name)]
    RC.hide(seals, True)
    undo = RC.apply_pose(rig, opened_moves(rig))
    P.beauty(root, bid, views=(getattr(rig, "open_view", (20, 52)),), size=(1100, 850), samples=48, start_index=2,
             fill=getattr(rig, "open_fill", 0.9))
    RC.undo_pose(undo)
    undo = RC.apply_pose(rig, exploded_moves(rig))
    RC.hide(seals, False)
    P.beauty(root, bid, views=(getattr(rig, "explode_view", (30, 28)),), size=(1200, 900), samples=48, start_index=3,
             fill=getattr(rig, "explode_fill", 0.82))
    RC.undo_pose(undo)
    RC.clear_extras(rig)


BUILDERS = {"cpu": build_cpu, "gpu": build_gpu, "mb": build_mb, "ram": build_ram, "ssd_m2": build_ssd_m2,
            "ssd_sata": build_ssd_sata, "psu": build_psu, "cooler_stock": build_cooler_stock,
            "cooler_tower": build_cooler_tower, "case": build_case, "usb": build_usb, "bag": build_bag}
