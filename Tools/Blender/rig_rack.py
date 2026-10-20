"""
rig_rack: the packaging rigs of the rack gear (catalogue 19, a rig module of build_boxes.py; report
docs/reports/cat_boxes_rack.md). It boxes the catalogue rack devices (box_catalog kind oem_rack), the task-01
data-centre gear (hand-written ITEMS below: server_1u, server_2u, switch_24, patch_panel_24, pdu_1u, ups_2u,
ups_tower, pdu_0u), the two racks and the through-the-wall AC (ac_12k, replacing the old 4-flap box_ac_12k).

Rig designs (all follow rig_products' conventions: origin at the bottom centre, +z the front, closed pose):
  * build_carton (kinds oem_rack and ac): a taped regular slotted carton (rig_products.rsc_box) with the device
    lying in it between two foam end caps that come out with it (with=A_ITEM_PART_0), in its bag; a top layer
    between the caps (rail-kit box, cords, hardware bags, look-only kit pieces) and the papers in a pile on top.
    One design per size class (CLASSES: 1u, 2u, 4u, the thin panel class, the AC), scaled to the measured part:
    the class sets the board, the foam, the cap ends and pockets; the device's own facts (RIGCFG) set what is in the
    top layer. The device's longest horizontal side runs along the box x, so the flaps meet across the short side
    as on a real carton.
  * build_flatpack (kind rack_flatpack, rack_12u_open): the open frame flat-packed in a long kraft carton: the
    bottom and top frames, a divider between them, the posts and tie bar nested in the top frame, the castors and
    the cage-nut and screw bags on top. The members are look pieces on A_ITEM_KIT_n; the game spawns the assembled
    rack at A_ITEM_PART_0 (in front of the carton) once every member is out.
  * build_pallet (kind rack_pallet, rack_42u): the rack standing on a wooden EUR pallet (the rig body), wrapped in
    stretch film sheets A_INSERT_WRAP_n, with cardboard corner posts and a top cap A_INSERT_CARD_n, strapping bands
    A_STRAP_n over the top and round the posts, the door keys in a bag taped to the front door.

Every printed face comes from build_boxes (compose_oem for the OEM boxes, compose for the AC carton); ART adds an
extra atlas tex_box_<id>_kit (the rail-kit label, the UPS battery warning tag) or the pallet's own atlas.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import rig_common as RC  # noqa: E402
import rig_products as RP  # noqa: E402
from mathutils import Matrix  # noqa: E402
from rig_common import F, Rig, X, Y, Z, NX, NY, NZ  # noqa: E402

DEG = math.pi / 180.0
NOTES = {}


def _bb():
    """build_boxes as the running script (it runs as __main__) or imported."""
    m = sys.modules.get("__main__")
    if m is not None and hasattr(m, "compose_oem"):
        return m
    import build_boxes
    return build_boxes


def up5(x):
    return round(math.ceil(x / 0.005 - 1e-6) * 0.005, 3)


# ---------------------------------------------------------------- the items

import box_catalog as BC  # noqa: E402

LIGHT = dict(bg0=(0.95, 0.95, 0.94), bg1=(0.86, 0.87, 0.88), text=(0.08, 0.08, 0.09))
LOOK = {"STRATA": dict(LIGHT, accent=(0.0, 0.42, 0.62), font="seguibl.ttf"),
        "LINKWAVE": dict(LIGHT, accent=(0.02, 0.45, 0.70), font="seguibl.ttf"),
        "AMPERE": dict(LIGHT, accent=(0.10, 0.48, 0.20), font="FRAMDCN.TTF")}

# per part: the size class, the bag, what lies in the top layer (rail kit, cords, hardware bags), the battery tag.
# cords: (kind, count); hw: labels; tag: (x, y, z) on the part (its own frame) where the battery warning tag sits.
RIGCFG = {
    # catalogue rack devices
    "srv_strata_sg840_4u": dict(cls="4u", bag="antistatic_pink", rails=True, cords=[("c19", 4)], line="4U GPU SERVER"),
    "srv_strata_sr224_2u": dict(cls="2u", bag="antistatic_pink", rails=True, cords=[("c13", 2)], line="2U STORAGE SERVER"),
    "srv_linkwave_ls4804x": dict(cls="1u", bag="antistatic_pink", cords=[("c13", 1), ("console", 1)],
                                 hw=["RACK SCREWS M6 + CAGE NUTS", "RUBBER FEET"], line="48-PORT MANAGED SWITCH"),
    "srv_linkwave_ls1600x": dict(cls="1u", bag="antistatic_pink", cords=[("c13", 2)], hw=["RACK SCREWS M6 + CAGE NUTS"],
                                 line="10G SFP+ AGGREGATION SWITCH"),
    "srv_strata_shelf_1u": dict(cls="1u", bag="clear", base="white", hw=["4 x M6 + CAGE NUTS"], line="1U CANTILEVER SHELF"),
    "srv_strata_blank_1u": dict(cls="panel", bag="clear", base="white", orient="up", hw=["4 x M6 + CAGE NUTS"],
                                line="1U BLANKING PANEL"),
    "srv_strata_blank_2u": dict(cls="panel", bag="clear", base="white", orient="up", hw=["4 x M6 + CAGE NUTS"],
                                line="2U BLANKING PANEL"),
    "srv_strata_cma": dict(cls="panel", bag="clear", base="white", hw=["CABLE STRAPS"], line="CABLE MANAGEMENT ARM"),
    "srv_strata_kvm_1u": dict(cls="1u", bag="antistatic_pink", rails=False, cords=[("c13", 1), ("kvm", 1)],
                              hw=["REAR BRACKETS + M6 SCREWS"], line="1U LCD CONSOLE DRAWER"),
    # task-01 gear
    "server_1u": dict(cls="1u", bag="antistatic_pink", rails=True, cords=[("c13", 2)], line="1U RACK SERVER"),
    "server_2u": dict(cls="2u", bag="antistatic_pink", rails=True, keys=True, cords=[("c13", 2)], line="2U RACK SERVER"),
    "switch_24": dict(cls="1u", bag="antistatic_pink", cords=[("c13", 1), ("console", 1)],
                      hw=["RACK SCREWS M6 + CAGE NUTS", "RUBBER FEET"], line="24-PORT MANAGED SWITCH"),
    "patch_panel_24": dict(cls="panel", bag="clear", base="white", hw=["RACK SCREWS M6 + CAGE NUTS", "CABLE TIES"],
                           line="CAT 6 PATCH PANEL"),
    "pdu_1u": dict(cls="1u", bag="clear", base="white", hw=["RACK SCREWS M6 + CAGE NUTS"], line="1U RACK PDU"),
    "ups_2u": dict(cls="2u", bag="clear", cords=[("c19", 1), ("usb", 1)], hw=["RACK SCREWS M6 + CAGE NUTS"],
                   tag=(-0.052, 0.0445, 0.0334), line="2U RACK UPS"),
    "ups_tower": dict(cls="2u", bag="clear", cords=[("usb", 1)], tag=(0.0, 0.095, 0.2200), line="TOWER UPS"),
    "pdu_0u": dict(cls="1u", bag="clear", orient="pdu", hw=["CABLE RETENTION CLIPS"], line="ZERO-U METERED PDU"),
    "ac_12k": dict(cls="ac", bag="clear", hw=["MOUNTING HARDWARE"], kit=["wall_trim"], line="THROUGH-THE-WALL AC"),
}


def _oem(pid, brand, model, name, line, cat, docs, specs, base="kraft", kind="oem_rack", **kw):
    """A hand-written item in box_catalog.item()'s shape: plain OEM print, the part's papers, its rig config."""
    it = dict(cat=cat, brand=brand, model=model, name=name, line=line, label_line=line, specs=specs, badges=[],
              style="oem", oem_base=base, kind=kind, model_id=pid, docs=docs, pose=((0, 0, 1), (0, 1, 0), (24, 22)),
              rig=RIGCFG.get(pid))
    it.update(LOOK[brand])
    it.update(kw)
    return it


ITEMS = {
    "server_1u": _oem("server_1u", "STRATA", "SR110", "Strata SR110 1U Rack Server", "1U RACK SERVER", "Server",
                      ["quick-start", "manual", "warranty", "safety"],
                      ["2 sockets, 16 DIMM slots", "8 x 2.5\" hot-swap bays", "2 x 800 W Platinum PSUs", "4 x 10 GbE"]),
    "server_2u": _oem("server_2u", "STRATA", "SR220", "Strata SR220 2U Rack Server", "2U RACK SERVER", "Server",
                      ["quick-start", "manual", "warranty", "safety"],
                      ["2 sockets, 16 DIMM slots", "12 x 3.5\" hot-swap bays", "2 x 800 W Platinum PSUs", "4 x 10 GbE"]),
    "switch_24": _oem("switch_24", "LINKWAVE", "LS-2804X", "Linkwave LS-2804X 24-Port Gigabit Switch",
                      "24-PORT MANAGED SWITCH", "Network", ["quick-start", "warranty", "safety"],
                      ["24 x 1 GbE RJ45", "4 x 10G SFP+ uplinks", "Managed, 1U rack mount"], base="white"),
    "patch_panel_24": _oem("patch_panel_24", "LINKWAVE", "PP-24C6", "Linkwave 24-Port Cat 6 Patch Panel",
                           "CAT 6 PATCH PANEL", "Network", ["quick-start", "warranty"],
                           ["24 x Cat 6 keystone jacks", "110 IDC, T568A/B", "1U, cable management bar"], base="white"),
    "pdu_1u": _oem("pdu_1u", "AMPERE", "RP-8C13", "Ampere 1U Rack PDU 8 x C13", "1U RACK PDU", "Server",
                   ["quick-start", "warranty", "safety"], ["8 x IEC C13 outlets", "Lit power switch", "C20 input cord 2.5 m"],
                   base="white"),
    "ups_2u": _oem("ups_2u", "AMPERE", "SMART 2200 RM", "Ampere Smart 2200 RM 2U Rack UPS", "2U RACK UPS", "Server",
                   ["quick-start", "manual", "warranty", "safety"],
                   ["2200 VA / 1980 W line-interactive", "Hot-swap battery pack", "C20 input"]),
    "ups_tower": _oem("ups_tower", "AMPERE", "SMART 1500", "Ampere Smart 1500 Tower UPS", "TOWER UPS", "Server",
                      ["quick-start", "manual", "warranty", "safety"],
                      ["1500 VA / 1000 W line-interactive", "8 x NEMA 5-15R outlets", "USB monitoring"]),
    "pdu_0u": _oem("pdu_0u", "AMPERE", "MP-24C13", "Ampere Metered Zero-U PDU 24 x C13 + 4 x C19",
                   "ZERO-U METERED PDU", "Server", ["quick-start", "warranty", "safety"],
                   ["24 x C13 + 4 x C19 outlets", "Bank breakers, amp meter", "L6-30P input cord 3 m"]),
    "rack_12u_open": _oem("rack_12u_open", "STRATA", "OF-12", "Strata OF-12 12U Open Frame Rack", "12U OPEN FRAME RACK",
                          "Server", ["manual", "warranty"], ["12U, 4 posts, EIA-310", "Square holes, M6 cage nuts",
                                                             "Castors included", "Flat-packed: assembly required"],
                          kind="rack_flatpack", label_line="12U OPEN FRAME RACK - FLAT PACK",
                          pose=((0, 0, 1), (0, 1, 0), (30, 18))),
    "rack_42u": _oem("rack_42u", "STRATA", "SRK-4260", "Strata SRK-4260 42U Enclosure", "42U RACK ENCLOSURE", "Server",
                     ["manual", "warranty"], ["42U, 600 x 1070 mm", "Perforated doors, side panels", "Static load 1360 kg"],
                     kind="rack_pallet", pose=((0, 0, 1), (0, 1, 0), (28, 12))),
    "ac_12k": dict(cat="Other", brand="FROSTLINE", model="TW-12K", name="12,000 BTU Through-the-Wall Air Conditioner",
                   line="THROUGH-THE-WALL AIR CONDITIONER",
                   specs=["12,000 BTU/h cooling", "115 V, 15 A plug", "Fits a 26 x 18 in wall sleeve",
                          "Remote-ready digital controls", "Wall trim and hardware included"],
                   badges=[], style="carton", ink=(0.07, 0.20, 0.36), accent=(0.0, 0.55, 0.80), font="segoeuib.ttf",
                   kind="ac", model_id="ac_12k", docs=["manual", "warranty"], bg0=(0.96, 0.96, 0.95),
                   bg1=(0.86, 0.88, 0.90), text=(0.07, 0.08, 0.10), pose=((0, 0, 1), (0, 1, 0), (-30, 12)),
                   rig=RIGCFG["ac_12k"]),
}


def item(pid, it):
    """The catalogue rack devices: plain OEM print (kraft for the big cartons), their rig config."""
    cfg = RIGCFG[pid]
    it["rig"] = cfg
    it["style"] = "oem"
    it["oem_base"] = cfg.get("base", "kraft")
    it["label_line"] = cfg["line"]
    it["line"] = cfg["line"]
    it["specs"] = [it["part"]["desc"]]
    it["pose"] = ((0, 0, 1), (0, 1, 0), (24, 22))
    it.update({k: v for k, v in LOOK.get(it["brand"], {}).items() if k != "font"})


# ---------------------------------------------------------------- carton layout (shared by SIZE and the builder)

# the size classes: board t, cap foam, cap end (wall to part), pocket depth, side wall of the caps, lip under the part
CLASSES = {
    "1u": dict(t=0.004, cap="pe_foam", end=0.030, Dp=0.040, side=0.012, lip=0.010, tape="tape_brown"),
    "2u": dict(t=0.005, cap="eps_foam", end=0.035, Dp=0.045, side=0.014, lip=0.012, tape="tape_brown"),
    "4u": dict(t=0.007, cap="eps_foam", end=0.045, Dp=0.055, side=0.018, lip=0.016, tape="tape_brown"),
    "panel": dict(t=0.003, cap="pe_foam", end=0.015, Dp=0.020, side=0.030, lip=0.004, tape="tape_clear"),
    "ac": dict(t=0.005, cap="eps_foam", end=0.035, Dp=0.040, side=0.025, lip=0.015, tape="tape_brown"),
}
# the part's (forward, up) in the box: front to +x (deep devices), front to +z (wide ones), lying face up (panels),
# the zero-U PDU lying along x with its outlets up
ORIENT = {"x": (X, Y), "z": (Z, Y), "up": (Y, NZ), "pdu": (Y, X)}

CORD = {"c13": (0.125, 0.095, 0.022), "c19": (0.140, 0.105, 0.028), "usb": (0.100, 0.075, 0.014),
        "console": (0.100, 0.075, 0.014), "kvm": (0.130, 0.100, 0.024)}
CORD_LABEL = {"c13": "C13 power cord", "c19": "C19 power cord", "usb": "USB cable", "console": "console cable",
              "kvm": "VGA + USB console cable"}
RAILBOX = (0.660, 0.115, 0.044)       # w along x, d along z, h


def orient_of(it):
    cfg = it["rig"]
    if cfg.get("orient"):
        return cfg["orient"]
    lo, hi = it["bounds"]
    return "x" if (hi[2] - lo[2]) > (hi[0] - lo[0]) else "z"


def rotated_bounds(it, o=None):
    lo, hi = it["bounds"]
    fwd, up = ORIENT[o or orient_of(it)]
    fr = F((0, 0, 0), fwd, up)
    pts = [fr.p(a, b, cc) for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for cc in (lo[2], hi[2])]
    rlo = tuple(min(p[i] for p in pts) for i in range(3))
    rhi = tuple(max(p[i] for p in pts) for i in range(3))
    return rlo, rhi


def layer_list(it):
    """The top layer's loose items: [(key, (w along x, d along z, h))], the rail-kit box first."""
    cfg = it["rig"]
    small = cfg["cls"] == "panel"
    out = []
    if cfg.get("rails"):
        out.append(("railbox", RAILBOX))
    for k in cfg.get("kit", []):
        if k == "wall_trim":
            out.append(("kit:wall_trim", (0.480, 0.680, 0.0085)))
    for kind, n in cfg.get("cords", []):
        w, d, h = CORD[kind]
        if n > 2:
            w, d, h = w + 0.02, d + 0.02, h + 0.012
        out.append((f"cord:{kind}:{n}", (w, d, h)))
    for lab in cfg.get("hw", []):
        out.append((f"hw:{lab}", (0.060, 0.050, 0.008) if small else (0.075, 0.100, 0.010)))
    return out


def pack(items, x0, x1, z0, z1, gap=0.006):
    """Shelf packing of flat items on a floor: rows along x from x0, rows stacked toward +z, tiers upward when the
    floor is full. Returns ({key: (cx, cz, tier_y)}, total height)."""
    pos = {}
    x, z, row_d, y, tier_h, top = x0, z0, 0.0, 0.0, 0.0, 0.0
    for key, (w, d, h) in items:
        if x + w > x1 + 1e-6 and x > x0:
            x, z, row_d = x0, z + row_d + gap, 0.0
        if z + d > z1 + 1e-6 and z > z0:
            x, z, row_d, y, tier_h = x0, z0, 0.0, y + tier_h + 0.001, 0.0
        pos[key] = (x + w / 2, z + d / 2, y)
        x += w + gap
        row_d = max(row_d, d)
        tier_h = max(tier_h, h)
        top = max(top, y + h)
    return pos, top


def papers_of(it, region):
    """The papers in the part's docs order, folded to fit the top layer."""
    class _C:
        docs = it["docs"]
    fit = (min(0.148, region[0] - 0.01), min(0.148, region[1] - 0.01))
    return RP.paper_list(_C, sizes={"quick-start": (0.148, 0.105, 0.0014), "safety": (0.105, 0.148, 0.0006)},
                         fit=fit, booklets_last=True)


def carton_layout(it, s=None):
    """Box size (when s is None) or the layout inside a given size: the device pose, caps, top layer, papers."""
    cfg = it["rig"]
    C = CLASSES[cfg["cls"]]
    o = orient_of(it)
    rlo, rhi = rotated_bounds(it, o)
    dx, dy, dz = (rhi[i] - rlo[i] for i in range(3))
    t = C["t"]
    if s is None:
        sx = up5(dx + 2 * C["end"] + 2 * (t + 0.0005))
        sz = up5(dz + 2 * C["side"] + 2 * (t + 0.0005))
    else:
        sx, sz = s[0], s[2]
    xi, zi = sx / 2 - t - 0.0005, sz / 2 - t - 0.0005
    y_b = t + C["lip"]                       # the part's lowest face
    y_d = y_b + dy + 0.004                   # the top layer's floor (on the bag)
    Dp = min(C["Dp"], dx * 0.2)
    X0, X1 = -(dx / 2 - Dp) + 0.003, (dx / 2 - Dp) - 0.003
    Z0, Z1 = -zi + 0.003, zi - 0.003
    items = layer_list(it)
    pos, lh = pack(items, X0, X1, Z0, Z1)
    papers = papers_of(it, (X1 - X0, Z1 - Z0))
    ph = sum(p[2][2] + 0.0002 for p in papers)
    y_in = y_d + lh + ph + 0.004
    sy = up5(y_in + 2 * t) if s is None else s[1]
    return dict(o=o, rlo=rlo, rhi=rhi, d=(dx, dy, dz), t=t, C=C, xi=xi, zi=zi, y_b=y_b, y_d=y_d, Dp=Dp,
                X=(X0, X1), Z=(Z0, Z1), items=items, pos=pos, lh=lh, papers=papers, ph=ph, size=(sx, sy, sz))


def size_carton(pid, it):
    return carton_layout(it)["size"]


# ---------------------------------------------------------------- pieces

def end_cap(R, name, anc, x_wall, inward, y0, y1, zw, pocket, pocket_c, Lc, Dp, tag):
    """A foam end cap against the wall at x_wall (rig_products.eps_cap with the foam's tag): a block with eased
    edges, the pocket for the part's end, moulded recesses behind and a finger notch at the top of its inner face."""
    yc = (y0 + y1) / 2
    xc = x_wall + inward * Lc / 2
    H = y1 - y0
    ob = R.cube(name, (xc, yc, 0), (Lc, H, zw), tag, anc=anc, bevel=min(0.003, H * 0.05))
    pz, py = pocket
    cuts = [RC.tmp_cube((x_wall + inward * (Lc - Dp / 2 + 0.002), pocket_c[1], pocket_c[0]), (Dp + 0.004, py, pz),
                        bevel=0.0015)]
    rd = min(0.012, (Lc - Dp) * 0.5)
    if rd > 0.006 and H > 0.05:
        for sz_ in (-1, 1):
            cuts.append(RC.tmp_cube((x_wall + inward * rd / 2 - inward * 0.001, yc, sz_ * zw * 0.24),
                                    (rd + 0.002, H * 0.62, zw * 0.30), bevel=0.002))
    if H > 0.06 and Lc - Dp > 0.012:          # a grip notch at the top of the inner face, above the part
        gx = x_wall + inward * Lc
        cuts.append(RC.tmp_cyl(F((gx, y1, 0.0), Y, Z), 0.014, (y1 - pocket_c[1] - py / 2) * 1.6, 24))
    R.cut(ob, cuts)
    return ob


def rail_look(R, anc, o, L, side):
    """A collapsed slide rail lying flat (outer C-channel, the inner member, front and rear brackets, pins) along x,
    its web on the floor at o (box coordinates)."""
    fr = F(o, X, Y)                                      # local z along the box x, local y up
    w, h, t = 0.040, 0.0135, 0.0012
    for nm, path, ln, tag in (("rail_outer", [(-w / 2, h), (-w / 2, 0), (w / 2, 0), (w / 2, h)], L, "steel"),
                              ("rail_inner", [(-w / 2 + 0.004, h - 0.0015), (-w / 2 + 0.004, t + 0.0005),
                                              (w / 2 - 0.004, t + 0.0005), (w / 2 - 0.004, h - 0.0015)], L * 0.92, "steel_dark")):
        ob = P.bent(nm, path, t, ln, tag, fr, parent=R.root)
        R.own(ob, anc, nm)
    for k, sg in enumerate((-1, 1)):                    # end brackets with two pins each and a release tab
        xb = sg * (L / 2 + 0.006)
        R.cube("rail_bracket", (xb, 0.0006 + 0.0005, 0), (0.014, 0.0012, w + 0.012), "steel", F(o, Z, Y), anc=anc)
        R.cube("rail_bracket", (xb + sg * 0.0065, 0.010, 0), (0.0012, 0.020, w + 0.012), "steel", F(o, Z, Y), anc=anc)
        for zz in (-0.012, 0.012):
            R.cylinder("rail_pin", F((o[0] + xb + sg * 0.0065, o[1] + 0.012, o[2] + zz), (sg, 0, 0), Y), 0.0034, 0.008,
                       "nickel", 12, anc=anc, z0=0.0)
    R.cube("rail_tab", (-L * 0.30, h * 0.5, 0), (0.030, 0.004, 0.010), "black_plastic", F(o, Z, Y), anc=anc, bevel=0.001)
    R.cube("rail_tab", (L * 0.42, h * 0.5, 0), (0.020, 0.004, 0.010), "white_plastic", F(o, Z, Y), anc=anc, bevel=0.001)
    return side


def rail_box(R, ctx, name, frame, size, flap_idx, order, under, label="rail kit box"):
    """The rail-kit box: a long white tuck box (rig_products.accessory_box) with its own printed top
    (tex_box_<id>_kit 'rail')."""
    a, fl = RP.accessory_box(R, ctx, name, frame, size, None, flap_idx, order, under, label=label, dist=0.20)
    w, h, d = size
    if getattr(ctx, "kit_uv", None):
        R.quad("rail_print", F(frame.p(0, h + 0.00022, 0), Y, NZ), w * 0.96, d * 0.86, ctx.kit_tex, ctx.kit_uv["rail"],
               anc=fl)
    return a, fl


def keys_look(R, anc, o, fwd=Y, up=NZ):
    """Two small flat keys on a split ring (look only), lying in the anchor's plane."""
    fr = F(o, fwd, up)
    R.emit("key_ring", P.ring_bm(0.011, 0.0095, 0.0012, 20), fr, "nickel", anc=anc)
    for k, a in enumerate((-25.0, 20.0)):
        ra = a * DEG
        dx, dy = math.sin(ra), -math.cos(ra)
        base = fr.p(dx * 0.016, dy * 0.016, 0.0012 + k * 0.0016)
        kf = F(tuple(base), fr.fwd, tuple(fr.d(-dx, -dy, 0)))
        R.cube("key_bow", (0, 0, 0), (0.016, 0.014, 0.0015), "nickel", kf, anc=anc, bevel=0.0005)
        R.cube("key_blade", (0, -0.017, 0), (0.0055, 0.022, 0.0013), "nickel", kf, anc=anc, bevel=0.0003)
        R.cube("key_cap", (0, 0.001, 0.0006), (0.018, 0.016, 0.0011), "black_plastic", kf, anc=anc, bevel=0.0006)


def battery_tag(R, ctx, pf, pos, under, order):
    """The UPS's 'battery disconnected' warning tag stuck on its front bezel (on the part: A_STICKER_0@A_ITEM_PART_0;
    it blocks the bezel until it is peeled off)."""
    w, h = 0.050, 0.068
    o = pf.p(*pos)
    fr = F(tuple(o), pf.fwd, pf.up)
    nm = R.anchor("A_STICKER_0", fr, (w, h, 0.0004), parent="A_ITEM_PART_0", shape="rect", peel="+y",
                  print="BATTERY DISCONNECTED", kind="warning_tag", blocks="A_BEZEL_0", label="battery warning tag",
                  order=order, under=under)
    R.cube("tag", (0, 0, 0.0002), (w, h, 0.0004), "paper_white", fr, anc=nm)
    R.quad("tag_print", fr.sub(0, 0, 0.00045), w, h, ctx.kit_tex, ctx.kit_uv["tag"], anc=nm)
    R.quad("tag_tape", fr.sub(0, h / 2 - 0.004, 0.0006), w * 0.7, 0.016, "tape_clear", anc=nm)
    return nm


def trim_look(R, anc, o):
    """The AC's wall trim frame (0.68 x 0.48, 8.5 mm, off-white) lying flat: long side along z."""
    fr = P.plane((o[0], o[1] + 0.00425, o[2]), X, Z)
    R.slab("trim", P.rrect(0.480, 0.680, 0.012), 0.0085, "white_plastic", fr,
           holes=[P.rrect(0.404, 0.624, 0.004)], anc=anc)


class Seq:
    """The opening sequence, for the report line."""

    def __init__(self):
        self.steps = []

    def add(self, order, text, show=None):
        self.steps.append((order, text, show))

    def text(self, head):
        by, shows = {}, {}
        for o, t, sh in self.steps:
            by.setdefault(o, []).append(t)
            if sh:
                shows[o] = sh
        return head + " -> ".join(f"{', '.join(v)} ({shows.get(k, k)})" for k, v in sorted(by.items())) + "."


# ---------------------------------------------------------------- the carton rig (oem_rack, ac)

def build_carton(ctx):
    pid, it = ctx.pid, ctx.it
    s = ctx.s
    sx, sy, sz = s
    L = carton_layout(it, s)
    cfg, C = it["rig"], L["C"]
    t = L["t"]
    R = Rig("box_" + pid)
    seq = Seq()
    covers = RP.rsc_box(R, ctx, t, "cardboard", tape_tag=C["tape"], tape_w=0.048 if t >= 0.004 else 0.036,
                        tape_down=min(0.06, sy * 0.45))
    short = covers[2:]
    seq.add(0, "tape A_TAPE_0..2")
    seq.add(1, "long flaps A_FLAP_0/1")
    seq.add(2, "short flaps A_FLAP_2/3")
    mid = it.get("model_id", pid)
    rlo, rhi = L["rlo"], L["rhi"]
    dx, dy, dz = L["d"]
    fwd, up = ORIENT[L["o"]]
    ax = -(rlo[0] + rhi[0]) / 2
    ay = L["y_b"] - rlo[1]
    az = -(rlo[2] + rhi[2]) / 2
    pf = F((ax, ay, az), fwd, up)
    xi, zi, y_in = L["xi"], L["zi"], sy - 2 * t
    # papers on top of the layer, in a pile at the layer's centre (the first one on top)
    X0, X1 = L["X"]
    Z0, Z1 = L["Z"]
    plist = L["papers"]
    n = len(plist)
    if L["items"]:                           # on the first (the largest) layer item, else on the bag
        k0, (w0, d0, h0) = L["items"][0]
        px, pz, ty0 = L["pos"][k0]
        ytop = L["y_d"] + ty0 + h0 + 0.0004
    else:
        px, pz, ytop = (X0 + X1) / 2, (Z0 + Z1) / 2, L["y_d"] + 0.0004
    names, _ = RP.pile(R, plist, px + 0.004, ytop, pz, 3, short, step=(0.004, -0.003))
    if n:
        seq.add(3, f"{n} papers in a pile, the first on top", f"3..{2 + n}" if n > 1 else None)
    o_l = 3 + n
    over = [names[-1]] if names else short
    layer, inside = [], []
    hw_i, cord_i, kit_i = 0, 0, 0
    o_part = o_l + 1
    exp = {}
    for key, (w, d, h) in L["items"]:
        cx, cz, ty = L["pos"][key]
        y0 = L["y_d"] + ty
        if key == "railbox":
            acc, fl = rail_box(R, ctx, "A_INSERT_ACCBOX_0", F((cx, y0, cz)), (w, h, d), 4, o_l, over)
            layer.append(acc)
            seq.add(o_l, "rail-kit box A_INSERT_ACCBOX_0")
            seq.add(o_l + 1, "its tuck flap A_FLAP_4")
            yb = y0 + 0.0007
            bags = []
            nmb = f"A_ITEM_HW_{hw_i}"
            hw_i += 1
            R.anchor(nmb, RP.flat_frame((cx + w / 2 - 0.075, yb + 0.0136, cz)), (0.080, 0.060, 0.008), parent=acc,
                     label="RAIL SCREWS M5 / M6", order=o_l + 2, under=[fl])
            bags.append(nmb)
            if cfg.get("keys"):
                nmk = f"A_ITEM_HW_{hw_i}"
                hw_i += 1
                R.anchor(nmk, RP.flat_frame((cx - w / 2 + 0.06, yb + 0.0136, cz)), (0.050, 0.070, 0.006), parent=acc,
                         kind="keys", label="BEZEL KEYS", look=1, order=o_l + 2, under=[fl])
                keys_look(R, nmk, (cx - w / 2 + 0.06, yb + 0.0136 + 0.0006, cz))
                bags.append(nmk)
            hw_r = []
            for k, (side, zz) in enumerate((("l", cz - d / 2 + 0.030), ("r", cz - d / 2 + 0.078))):
                nm = f"A_ITEM_HW_{hw_i}"
                hw_i += 1
                hw_r.append(nm)
                R.anchor(nm, F((cx, yb, zz), Y, NZ), (0.62, 0.040, 0.016), parent=acc, kind="rail", side=side,
                         len=0.62, label=f"SLIDE RAIL {side.upper()}", look=1, order=o_l + 3, under=[fl] + bags)
                rail_look(R, nm, (cx - 0.004, yb, zz), 0.60, side)
            seq.add(o_l + 2, ("rail screws" + (" and bezel keys" if cfg.get("keys") else "")) + " in the box")
            seq.add(o_l + 3, "slide rails A_ITEM_HW (kind=rail, look meshes)")
            exp[acc] = (0.0, 0.42, -0.12)
            for k, nm in enumerate(hw_r + bags):
                exp[nm] = (0.0, 0.10 + 0.05 * k, 0.12 + 0.05 * k)
        elif key.startswith("kit:"):
            nm = f"A_ITEM_KIT_{kit_i}"
            kit_i += 1
            member = key[4:]
            R.anchor(nm, RP.flat_frame((cx, y0, cz)), (w, d, h), kit=mid, member=member, label=member.replace("_", " "),
                     look=1, lift="+y", dist=0.10, order=o_l, under=over)
            if member == "wall_trim":
                trim_look(R, nm, (cx, y0, cz))
            layer.append(nm)
            seq.add(o_l, f"{member.replace('_', ' ')} {nm} (look piece)")
            exp[nm] = (0.0, 0.40, 0.0)
        elif key.startswith("cord:"):
            _, kind, cnt = key.split(":")
            nm = f"A_ITEM_CORD_{cord_i}"
            cord_i += 1
            R.anchor(nm, RP.flat_frame((cx, y0, cz)), (w, d, h), kind=kind, tie="twist", n=int(cnt),
                     label=("%s x " % cnt if int(cnt) > 1 else "") + CORD_LABEL[kind], order=o_l, under=over)
            layer.append(nm)
            exp[nm] = (0.0, 0.30, 0.10 + 0.06 * cord_i)
        else:
            nm = f"A_ITEM_HW_{hw_i}"
            hw_i += 1
            R.anchor(nm, RP.flat_frame((cx, y0, cz)), (w, d, h), label=key[3:], order=o_l, under=over)
            layer.append(nm)
            exp[nm] = (0.0, 0.32, -0.08 - 0.05 * hw_i)
    cords = [a for a in layer if a.startswith("A_ITEM_CORD_")]
    hws = [a for a in layer if a.startswith("A_ITEM_HW_")]
    if cords:
        seq.add(o_l, ", ".join(f"{R.meta[a]['label']} {a}" for a in cords))
    if hws:
        seq.add(o_l, "hardware bag" + ("s " if len(hws) > 1 else " ") + "/".join(hws))
    # the part in its bag, lifted out with its end caps
    bag = cfg.get("bag", "antistatic_pink")
    meta = dict(bag=bag, label=it["name"], order=o_part, under=layer or over)
    if cfg.get("tag"):
        meta["battery"] = "disconnected"
    R.anchor("A_ITEM_PART_0", pf, RP.bsize(mid, 0.003), **meta)
    seq.add(o_part, f"the {RIG_WORD.get(cfg['cls'], 'device')} in its {bag.replace('_', ' ')} bag, lifted out WITH its end caps")
    caps = []
    pocket = (dz + 0.004, dy + 0.004)
    pc = (0.0, L["y_b"] + dy / 2)
    for i, (x_wall, inward, xend) in enumerate(((-xi, 1, -dx / 2), (xi, -1, dx / 2))):
        nm = f"A_INSERT_FOAM_{i}"
        Lc = abs(xend - x_wall) + L["Dp"]
        R.anchor(nm, F((x_wall, t, 0)), (Lc, y_in - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.10,
                 with_="A_ITEM_PART_0", label=("PE" if C["cap"] == "pe_foam" else "EPS") + " end cap", order=o_part + 1,
                 under=["A_ITEM_PART_0"])
        end_cap(R, "cap", nm, x_wall, inward, t + 0.0002, y_in - 0.0004, 2 * zi - 0.001, pocket, pc, Lc, L["Dp"], C["cap"])
        caps.append(nm)
    seq.add(o_part + 1, "end caps A_INSERT_FOAM_0/1 pulled off along -x/+x")
    if cfg.get("tag"):
        battery_tag(R, ctx, pf, cfg["tag"], ["A_ITEM_PART_0"], o_part + 1)
        seq.add(o_part + 1, "the battery warning tag A_STICKER_0@A_ITEM_PART_0 on the bezel (blocks A_BEZEL_0: peel it, "
                            "take the bezel off, connect the battery)")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    exp.update({"A_ITEM_PART_0": (0, 0.20, 0), caps[0]: (-0.10, 0.20, 0), caps[1]: (0.10, 0.20, 0),
                "A_TAPE_0": (-0.04, 0.03, 0), "A_TAPE_1": (0, 0.04, 0), "A_TAPE_2": (0.04, 0.03, 0)})
    R.explode = exp
    RP.explode_docs(R, names, (0.0, 0.55, 0.10 + sz * 0.3), (0.03, 0.02, 0.10))
    R.open_view = (24, 56)
    R.explode_fill = 0.78
    R.explode_view = (30, 30)
    word = {"1u": "1U", "2u": "2U", "4u": "4U", "panel": "Panel", "ac": "AC"}[cfg["cls"]]
    NOTES[pid] = seq.text(f"{word} carton ({C['cap'].replace('_', ' ')} end caps, {L['o']}-facing): ")
    return R


RIG_WORD = {"1u": "device", "2u": "device", "4u": "server", "panel": "panel", "ac": "AC unit"}


# ---------------------------------------------------------------- the extra print: rail-kit label, battery tag

KIT_REG = {"rail": (0, 384, 1024, 128), "tag": (0, 0, 256, 368), "key": (256, 0, 256, 128)}


def kit_art(pid, it):
    """tex_box_<pid>_kit: the rail-kit box's top label and the UPS battery warning tag."""
    W, H = 1024, 512
    a = P.Art(W, H, bg=(0.95, 0.95, 0.94), name="kit_" + pid)
    ink = (0.06, 0.06, 0.07)
    acc = it.get("accent", (0.0, 0.42, 0.62))
    x, y, w, h = KIT_REG["rail"]
    a.rect(x, y, w, h, (0.96, 0.96, 0.95))
    a.rect(x, y + h - 22, w, 22, acc)
    a.text(it["brand"], x + 24, y + h - 64, 40, acc, it.get("font", "arialbd.ttf"), maxw=w * 0.3)
    a.text("SLIDE RAIL KIT", x + 24, y + 24, 30, ink, "arialbd.ttf", spacing=1.2, maxw=w * 0.32)
    a.text("For " + it["name"], x + w * 0.36, y + h - 58, 22, ink, "arialbd.ttf", maxw=w * 0.40)
    a.text("Sliding rails, square-hole and round-hole racks. Tool-less install.", x + w * 0.36, y + 52, 17, ink,
           "arial.ttf", maxw=w * 0.40)
    pn = _bb().part_number(dict(it, name=it["name"] + " rails"))
    a.text("P/N " + pn, x + w * 0.36, y + 22, 18, ink, "consola.ttf", maxw=w * 0.4)
    a.code128ish(P.shash(pid + "rails") & 0xffff, x + w * 0.78, y + 30, w * 0.19, 70, ink)
    # the battery warning tag: yellow, black band, the text
    x, y, w, h = KIT_REG["tag"]
    yel = (0.98, 0.80, 0.06)
    a.rect(x, y, w, h, yel)
    a.rect(x, y + h - 74, w, 74, (0.05, 0.05, 0.05))
    a.poly([(x + 30, y + h - 66), (x + 76, y + h - 66), (x + 53, y + h - 20)], yel)
    a.text("!", x + 53, y + h - 58, 32, (0.05, 0.05, 0.05), "arialbd.ttf", align="CENTER")
    a.text("WARNING", x + 150, y + h - 46, 34, yel, "arialbd.ttf", align="CENTER", valign="CENTER", maxw=150)
    lines = ["BATTERY", "DISCONNECTED", "FOR SHIPPING", "", "Remove the front", "bezel and connect", "the battery before",
             "use."]
    for i, ln in enumerate(lines):
        big = i < 3
        a.text(ln, x + w / 2, y + h - 110 - i * (34 if big else 28) - (0 if big else 10), 30 if big else 21, (0.05, 0.05, 0.05),
               "arialbd.ttf" if big else "arial.ttf", align="CENTER", maxw=w - 20)
    a.circle(x + w / 2, y + 16, 7, (0.4, 0.4, 0.4))
    a.render("box_" + pid + "_kit")
    a.dispose()
    return {k: (r[0] / W, r[1] / H, (r[0] + r[2]) / W, (r[1] + r[3]) / H) for k, r in KIT_REG.items()}


def art_oem(pid, it, s, hero, kraft):
    BB = _bb()
    fw = min(s[0] * 0.3, s[2] * 0.45)
    if it["style"] == "carton":
        ink_shot = BB.line_art(hero, pid + "_ink", it["ink"])
        reg, W, H = BB.compose(pid, it, s, fw, hero, ink_shot, kraft)
    else:
        reg, W, H = BB.compose_oem(pid, it, s, fw, hero, kraft)
    cfg = it.get("rig") or {}
    if cfg.get("rails") or cfg.get("tag"):
        KIT_UV[pid] = kit_art(pid, it)
    return reg, W, H, fw


KIT_UV = {}


def _with_kit(fn):
    """Gives the builder's ctx the kit atlas (tex_box_<id>_kit) when its ART made one."""
    def wrapped(ctx):
        ctx.kit_uv = KIT_UV.get(ctx.pid)
        ctx.kit_tex = "tex_box_" + ctx.pid + "_kit"
        return fn(ctx)
    return wrapped


BUILDERS = {"oem_rack": _with_kit(build_carton), "ac": _with_kit(build_carton)}
SIZE = {"oem_rack": size_carton, "ac": size_carton}
ART = {"oem_rack": art_oem, "ac": art_oem}


# ---------------------------------------------------------------- previews

def add_contents(rig, ctx):
    """rig_products.add_contents, without stand-ins for anchors that carry their own look meshes (look=1)."""
    saved = rig.meta
    rig.meta = {a: m for a, m in saved.items() if not m.get("look")}
    try:
        RP.add_contents(rig, ctx)
    finally:
        rig.meta = saved


def previews(rig, ctx):
    """rig_products.previews, plus: anchors in rig.open_hide are hidden in the opened view (the pallet's film,
    straps and posts), and look-only anchors get no stand-ins."""
    if not P.PREVIEW[0]:
        return
    bid = rig.bid
    root = rig.root
    views = getattr(rig, "views", ((28, 24), (-150, 26)))
    P.beauty(root, bid, views=views, size=(1100, 850), samples=48, start_index=0, fill=getattr(rig, "closed_fill", 1.0))
    add_contents(rig, ctx)
    seals = [o for o in c.descendants(root) if o.type == "MESH" and ("@A_SEAL_" in o.name or "@A_TAPE_" in o.name)]
    hidden = []
    for a in getattr(rig, "open_hide", ()):
        hidden += RC.objects_of(rig, a)
    RC.hide(seals, True)
    RC.hide(hidden, True)
    undo = RC.apply_pose(rig, RP.opened_moves(rig))
    P.beauty(root, bid, views=(getattr(rig, "open_view", (20, 52)),), size=(1100, 850), samples=48, start_index=2,
             fill=getattr(rig, "open_fill", 0.9))
    RC.undo_pose(undo)
    RC.hide(hidden, False)
    undo = RC.apply_pose(rig, RP.exploded_moves(rig))
    RC.hide(seals, False)
    P.beauty(root, bid, views=(getattr(rig, "explode_view", (30, 28)),), size=(1200, 900), samples=48, start_index=3,
             fill=getattr(rig, "explode_fill", 0.82))
    RC.undo_pose(undo)
    RC.clear_extras(rig)


# ---------------------------------------------------------------- rack_12u_open: the flat pack

# the open frame's members (datacenter_rack.frame_open / rail): frames 0.788 deep x 0.56 wide x 0.035, posts
# C-profile 0.045 x 0.0285 x 0.549 long, the tie bar 0.504 x 0.020 x 0.005, four plate castors
FP = dict(fl=0.788, fw=0.560, fh=0.035, plate=0.004, div=0.003, post=(0.549, 0.045, 0.0285), layer=0.066)


def size_flatpack(pid, it):
    t = 0.005
    sx = up5(FP["fl"] + 0.024 + 2 * (t + 0.0005))
    sz = up5(FP["fw"] + 0.024 + 2 * (t + 0.0005))
    plist = papers_of(it, (0.3, 0.3))
    ph = sum(p[2][2] + 0.0002 for p in plist)
    sy = up5(t + FP["plate"] + 2 * FP["fh"] + FP["div"] + FP["layer"] + ph + 0.006 + 2 * t)
    return (sx, sy, sz)


def frame_look(R, anc, y0, plates=False):
    """One open-frame rectangle lying flat (its depth along the box x): two box-section side rails and two cross
    members; the bottom frame has the four castor mounting plates under its corners."""
    fl, fw, fh = FP["fl"], FP["fw"], FP["fh"]
    yb = y0 + (FP["plate"] if plates else 0.0)
    for sg in (-1, 1):
        R.cube("frame_side", (0, yb + fh / 2, sg * (fw / 2 - 0.0135)), (fl, fh, 0.027), "paint_black", anc=anc, bevel=0.002, seg=1)
        R.cube("frame_cross", (sg * (fl / 2 - 0.028), yb + fh / 2, 0), (0.024, fh - 0.008, fw - 0.054), "paint_black", anc=anc,
               bevel=0.002, seg=1)
        if plates:
            for sz_ in (-1, 1):
                R.cube("caster_mount", (sg * (fl / 2 - 0.025), y0 + FP["plate"] / 2, sz_ * (fw / 2 - 0.0135)), (0.060, FP["plate"], 0.060),
                       "steel", anc=anc)
    for sg in (-1, 1):                                  # gussets in the corners where the posts stand
        for sz_ in (-1, 1):
            R.cube("frame_gusset", (sg * (fl / 2 - 0.055), yb + fh - 0.0015, sz_ * (fw / 2 - 0.045)), (0.040, 0.003, 0.040),
                   "paint_black", anc=anc)


def post_look(R, anc, o):
    """A C-profile rack post lying on its back along x (the 19" flange up)."""
    L, w, h = FP["post"]
    fr = F(o, X, Y)
    path = [(-w / 2 + 0.012, h), (-w / 2, h), (-w / 2, 0), (w / 2, 0), (w / 2, h), (w / 2 - 0.012, h)]
    R.own(P.bent("post", path, 0.002, L, "paint_black", fr, parent=R.root), anc, "post")
    for k in range(12):                                 # the square cage-nut holes, as dark plugs in the web
        for hh in (0.00635, 0.022225, 0.0381):
            xx = -L / 2 + 0.008 + k * 0.04445 + hh
            R.cube("post_hole", (xx, 0.0021, 0.0085), (0.0095, 0.0004, 0.0095), "dark_plastic", F(o, Z, Y), anc=anc)


def castor_look(R, anc, o):
    """A plate castor standing on its wheel (datacenter_rack.caster)."""
    x, y, z = o
    h, wr = 0.061, 0.022
    R.cube("castor_plate", (x, y + h - 0.002, z), (0.060, 0.004, 0.060), "steel", anc=anc)
    R.cylinder("castor_swivel", F((x, y + h - 0.008, z), Y, Z), 0.018, 0.008, "steel", 16, anc=anc, z0=-0.004)
    R.cube("castor_yoke", (x, y + wr + 0.012, z + 0.003), (0.026, 0.030, 0.026), "steel", anc=anc)
    R.cylinder("castor_wheel", F((x, y + wr, z + 0.003), X, Y), wr, 0.020, "rubber", 18, anc=anc)
    R.cylinder("castor_hub", F((x, y + wr, z + 0.003), X, Y), wr * 0.45, 0.0215, "grey_plastic", 12, anc=anc)


def build_flatpack(ctx):
    pid, it = ctx.pid, ctx.it
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    seq = Seq()
    t = 0.005
    covers = RP.rsc_box(R, ctx, t, "cardboard", tape_tag="tape_brown", tape_w=0.048, tape_down=0.06)
    short = covers[2:]
    seq.add(0, "tape A_TAPE_0..2")
    seq.add(1, "long flaps A_FLAP_0/1")
    seq.add(2, "short flaps A_FLAP_2/3")
    xi, zi = sx / 2 - t - 0.0005, sz / 2 - t - 0.0005
    y1 = t + 0.0005                                     # bottom frame (on its plates)
    y2 = y1 + FP["plate"] + FP["fh"]                    # divider
    y3 = y2 + FP["div"] + 0.0003                        # top frame
    y4 = y3 + FP["fh"] + 0.0005                         # the top layer
    plist = papers_of(it, (0.3, 0.3))
    n = len(plist)
    o_l = 3 + n
    # the top layer: castors in their bag at -x, the two hardware bags at +x with the papers on them
    names, _ = RP.pile(R, plist, 0.13, y4 + 0.0125, 0.0, 3, short, step=(0.004, -0.003))
    hw = []
    for k, (lab, xx) in enumerate((("CAGE NUTS M6 x 40", 0.06), ("SCREWS M6 x 16 + WASHERS x 40", 0.20))):
        nm = f"A_ITEM_HW_{k}"
        R.anchor(nm, RP.flat_frame((xx, y4, 0.08 if k else -0.08)), (0.090, 0.120, 0.012), label=lab, order=o_l,
                 under=[names[-1]] if names else short)
        hw.append(nm)
    if n:
        seq.add(3, f"{n} papers on the hardware bags", f"3..{2 + n}" if n > 1 else None)
    kit = []

    def kit_anchor(member, fr, size, order, under, lab=None, **kw):
        nm = f"A_ITEM_KIT_{len(kit)}"
        R.anchor(nm, fr, size, kit=pid, member=member, label=lab or member.replace("_", " "), look=1, lift="+y",
                 dist=0.25, order=order, under=under, **kw)
        kit.append(nm)
        return nm

    cas = kit_anchor("castors", F((-0.24, y4, 0.0)), (0.13, 0.065, 0.13), o_l, short, lab="4 castors", bag="clear")
    for dx_ in (-0.034, 0.034):
        for dz_ in (-0.034, 0.034):
            castor_look(R, cas, (-0.24 + dx_, y4, dz_))
    seq.add(o_l, f"castor bag {cas}, cage nuts A_ITEM_HW_0 and screws A_ITEM_HW_1")
    top_l = [cas] + hw
    posts = []
    for k, zz in enumerate((-0.165, -0.095, 0.095, 0.165)):
        nm = kit_anchor("post", F((-0.03, y3, zz)), FP["post"][:1] + (FP["post"][2], FP["post"][1]), o_l + 1, top_l,
                        n=k)
        post_look(R, nm, (-0.03, y3, zz))
        posts.append(nm)
    tie = kit_anchor("tie_bar", F((0.0, y3, 0.0)), (0.504, 0.005, 0.020), o_l + 1, top_l, lab="cable tie bar")
    R.cube("tie_bar", (0.0, y3 + 0.0025, 0.0), (0.504, 0.005, 0.020), "steel", anc=tie)
    for k in range(9):
        R.cube("tie_slot", (-0.2 + k * 0.05, y3 + 0.0052, 0.0), (0.008, 0.0005, 0.011), "dark_plastic", anc=tie)
    topf = kit_anchor("top_frame", F((0, y3, 0)), (FP["fl"], FP["fh"], FP["fw"]), o_l + 1, top_l, lab="top frame")
    frame_look(R, topf, y3)
    seq.add(o_l + 1, f"4 posts {posts[0]}..{posts[-1][-1]}, tie bar {tie} and the top frame {topf}")
    div = R.anchor("A_INSERT_CARD_0", F((0, y2, 0)), (2 * xi, FP["div"], 2 * zi), lift="+y", dist=0.18, label="divider",
                   order=o_l + 2, under=posts + [tie, topf])
    R.cube("divider", (0, y2 + FP["div"] / 2, 0), (2 * xi - 0.002, FP["div"], 2 * zi - 0.002), "cardboard", anc=div)
    seq.add(o_l + 2, "cardboard divider A_INSERT_CARD_0")
    botf = kit_anchor("bottom_frame", F((0, y1, 0)), (FP["fl"], FP["fh"] + FP["plate"], FP["fw"]), o_l + 3, [div],
                      lab="bottom frame")
    frame_look(R, botf, y1, plates=True)
    seq.add(o_l + 3, f"bottom frame {botf}")
    # the assembled rack: spawned standing in front of the carton once every member is out
    lo, hi = RP.PART_BOUNDS[it["model_id"]]
    zf = sz / 2 + 0.05 - lo[2]
    R.anchor("A_ITEM_PART_0", F((-(lo[0] + hi[0]) / 2, 0.0, zf)), RP.bsize(it["model_id"], 0.0), bag="none", kit=1,
             spawn="assembled", label=it["name"], order=o_l + 4, under=kit)
    seq.add(o_l + 4, "assembly: the rack A_ITEM_PART_0 spawns standing in front of the carton (spawn=assembled), the "
                     "KIT look pieces go")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_TAPE_0": (-0.04, 0.03, 0), "A_TAPE_1": (0, 0.04, 0), "A_TAPE_2": (0.04, 0.03, 0),
                 cas: (-0.25, 0.55, 0.0), hw[0]: (0.05, 0.55, -0.12), hw[1]: (0.25, 0.55, 0.12), topf: (0, 0.30, 0),
                 tie: (0, 0.42, -0.02), div: (0, 0.18, 0), botf: (0, 0.06, 0), "A_ITEM_PART_0": (0, 0, 0.3)}
    for k, nm in enumerate(posts):
        R.explode[nm] = (0, 0.36 + 0.03 * k, 0)
    RP.explode_docs(R, names, (0.15, 0.68, 0.0), (0.03, 0.02, 0.06))
    R.open_view = (22, 50)
    R.open_hide = ["A_ITEM_PART_0"]
    R.explode_view = (24, 26)
    NOTES[pid] = seq.text("12U open frame, flat-packed: ")
    return R


# ---------------------------------------------------------------- rack_42u: on a pallet

PAL = dict(w=0.800, l=1.200, h=0.144)


def pallet_frame(it):
    """The rack's pose on the pallet and the wrap envelope (the corner posts, the cap, the film)."""
    lo, hi = it["bounds"]
    y_roof = PAL["h"] + hi[1] - lo[1]
    ex, ez = max(-lo[0], hi[0]), max(-lo[2], hi[2])
    y_top = y_roof + 0.014                              # the cap's underside (papers and a hardware bag on the roof)
    return dict(ax=-(lo[0] + hi[0]) / 2, ay=PAL["h"] - lo[1], az=-(lo[2] + hi[2]) / 2, y_roof=y_roof, ex=ex, ez=ez,
                y_top=y_top, Ex=ex + 0.005 + 0.0025 + 0.0065, Ez=ez + 0.005 + 0.0025 + 0.0065)


def size_pallet(pid, it):
    pf = pallet_frame(it)
    return (PAL["w"], round(pf["y_top"] + 0.004 + 0.0012 + 0.0012, 4), PAL["l"])


PAL_REG = {"wood": (0, 0, 1024, 1024), "post": (1024, 0, 256, 1024), "cap": (1280, 512, 768, 512),
           "stamp": (1280, 256, 384, 256), "label": (1664, 256, 384, 256), "keys": (1280, 0, 384, 256)}


def art_pallet(pid, it, s, hero, kraft):
    """tex_box_rack_42u: the pallet wood, the corner posts' and top cap's print, the ISPM stamp and the product label."""
    import random
    W, H = 2048, 1024
    a = P.Art(W, H, bg=(0.5, 0.5, 0.5), name="pallet")
    rnd = random.Random(42)
    x, y, w, h = PAL_REG["wood"]
    a.rect(x, y, w, h, (0.80, 0.67, 0.47))
    for k in range(240):                                # the grain: thin streaks along u
        yy = y + rnd.random() * h
        a.rect(x, yy, w, 0.6 + rnd.random() * 2.2, (0.58, 0.44, 0.28) if rnd.random() < 0.5 else (0.88, 0.76, 0.56),
               alpha=0.18 + rnd.random() * 0.3)
    for k in range(14):                                 # knots
        cx, cy, r = x + rnd.random() * w, y + rnd.random() * h, 5 + rnd.random() * 9
        a.circle(cx, cy, r * 1.8, (0.66, 0.50, 0.32), alpha=0.5)
        a.circle(cx, cy, r, (0.40, 0.27, 0.15), alpha=0.85)
    ink = (0.10, 0.09, 0.08)
    for reg in ("post", "cap"):
        x, y, w, h = PAL_REG[reg]
        a.image(kraft, x, y, w, h)
    x, y, w, h = PAL_REG["post"]
    a.text("STRATA", x + w * 0.55, y + 140, 78, ink, "seguibl.ttf", rot=math.pi / 2, maxw=h * 0.4)
    a.text("THIS SIDE UP  ↑  HANDLE WITH CARE", x + w * 0.20, y + 520, 26, ink, "arialbd.ttf", rot=math.pi / 2, maxw=h * 0.46)
    a.rect(x + w * 0.88, y, w * 0.06, h, it["accent"])
    x, y, w, h = PAL_REG["cap"]
    a.text("STRATA", x + 40, y + h - 110, 86, ink, "seguibl.ttf", maxw=w * 0.5)
    a.text("SRK-4260  42U RACK ENCLOSURE", x + 40, y + h - 160, 30, ink, "arialbd.ttf", maxw=w * 0.6)
    a.text("DO NOT STACK", x + w / 2, y + 150, 64, (0.75, 0.08, 0.06), "arialbd.ttf", align="CENTER", maxw=w * 0.8)
    a.text("GROSS WEIGHT 162 kg   -   FORKLIFT OR PALLET JACK ONLY", x + w / 2, y + 80, 22, ink, "arialbd.ttf",
           align="CENTER", maxw=w * 0.9)
    BB = _bb()
    BB.arrows(a, x + w - 170, y + h - 170, 130, ink)
    x, y, w, h = PAL_REG["stamp"]
    a.rect(x, y, w, h, (0.80, 0.67, 0.47), alpha=0.0)
    for (x0, y0, x1, y1) in ((0, 0, w, 6), (0, h - 6, w, h), (0, 0, 6, h), (w - 6, 0, w, h)):
        a.rect(x + x0, y + y0, x1 - x0, y1 - y0, ink, alpha=0.85)
    a.text("IPPC", x + 30, y + h - 70, 40, ink, "arialbd.ttf", alpha=0.85)
    a.text("NL - 049217", x + 30, y + h - 130, 34, ink, "arialbd.ttf", alpha=0.85)
    a.text("HT   EPAL", x + 30, y + 50, 50, ink, "arialbd.ttf", alpha=0.85)
    x, y, w, h = PAL_REG["label"]
    BB.oem_label(BB.Face(a, (x, y, w, h)), it, x + 8, y + 8, w - 16, h - 16, P.shash(pid) & 0xffff)
    x, y, w, h = PAL_REG["keys"]
    a.rect(x, y, w, h, (0.97, 0.97, 0.95))
    a.text("DOOR KEYS", x + w / 2, y + h * 0.62, 46, ink, "arialbd.ttf", align="CENTER", maxw=w * 0.9)
    a.text("front door + side panels", x + w / 2, y + h * 0.34, 24, ink, "arial.ttf", align="CENTER", maxw=w * 0.9)
    a.render("box_" + pid)
    a.dispose()
    return PAL_REG, W, H, None


def board(R, ctx, name, centre, size, along_z, k):
    """One pallet board or block with the wood print (grain along its length; a different strip of the atlas each)."""
    u0, v0, u1, v1 = ctx.uv["wood"]
    f0 = (k * 0.137) % 0.85
    uv = (u0, v0 + (v1 - v0) * f0, u1, v0 + (v1 - v0) * (f0 + 0.12))
    L_, H_, W_ = (size[2], size[1], size[0]) if along_z else (size[0], size[1], size[2])
    fr = P.plane(centre, Z, X) if along_z else P.plane(centre, X, Z)
    R.cube(name, (0, 0, 0), (L_, W_, H_), ctx.tex, fr, uv=uv)


def build_pallet(ctx):
    pid, it = ctx.pid, ctx.it
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    seq = Seq()
    pf = pallet_frame(it)
    # the EUR pallet (the rig body): 3 bottom boards, 9 blocks, 3 cross boards, 5 top deck boards
    k = 0
    for xx, ww in ((-0.3275, 0.100), (0.0, 0.145), (0.3275, 0.100)):
        board(R, ctx, "pallet_bottom", (xx, 0.011, 0), (ww, 0.022, PAL["l"]), True, k)
        k += 1
        for zz, dd in ((-0.5275, 0.145), (0.0, 0.145), (0.5275, 0.145)):
            board(R, ctx, "pallet_block", (xx, 0.061, zz), (ww, 0.078, dd), False, k)
            k += 1
    for zz in (-0.5275, 0.0, 0.5275):
        board(R, ctx, "pallet_cross", (0, 0.111, zz), (PAL["w"], 0.022, 0.145), False, k)
        k += 1
    for xx, ww in ((-0.3275, 0.145), (-0.165, 0.100), (0.0, 0.145), (0.165, 0.100), (0.3275, 0.145)):
        board(R, ctx, "pallet_deck", (xx, 0.133, 0), (ww - 0.002, 0.022, PAL["l"]), True, k)
        k += 1
    for xx in (-0.3275, 0.0, 0.3275):                  # the stamps on the front blocks
        R.quad("pallet_stamp", F((xx, 0.061, PAL["l"] / 2 + 0.00015), Z, Y), 0.09, 0.06, ctx.tex, ctx.uv["stamp"])
    # the rack standing on the deck
    R.anchor("A_ITEM_PART_0", F((pf["ax"], pf["ay"], pf["az"])), RP.bsize(it["model_id"], 0.0), bag="none",
             label=it["name"], order=4, under=["A_INSERT_CARD_0", "A_INSERT_CARD_1", "A_INSERT_CARD_2", "A_INSERT_CARD_3"])
    ex, ez, y0, yt = pf["ex"], pf["ez"], PAL["h"], pf["y_top"]
    tp = 0.005
    # corner posts (cardboard L angles), printed outside
    for i, (sgx, sgz) in enumerate(((-1, 1), (1, 1), (1, -1), (-1, -1))):
        nm = f"A_INSERT_CARD_{i}"
        sides = {(-1, 1): ("A_INSERT_WRAP_0", "A_INSERT_WRAP_3"), (1, 1): ("A_INSERT_WRAP_0", "A_INSERT_WRAP_1"),
                 (1, -1): ("A_INSERT_WRAP_2", "A_INSERT_WRAP_1"), (-1, -1): ("A_INSERT_WRAP_2", "A_INSERT_WRAP_3")}[(sgx, sgz)]
        R.anchor(nm, F((sgx * ex, y0, sgz * ez)), (0.05, yt - y0, 0.05), lift=("+x" if sgx > 0 else "-x"), dist=0.12,
                 label="corner post", order=3, under=["A_INSERT_CARD_4", *sides])
        H = yt - y0
        xo, zo = sgx * (ex + tp / 2), sgz * (ez + tp / 2)
        R.cube("post", (xo, y0 + H / 2, sgz * (ez + tp - 0.025)), (tp, H, 0.05), "cardboard", anc=nm)
        R.cube("post", (sgx * (ex + tp - 0.025), y0 + H / 2, zo), (0.05 - tp, H, tp), "cardboard", anc=nm)
        R.quad("post_print", F((sgx * (ex + tp + 0.0002), y0 + H / 2, sgz * (ez + tp - 0.025)), (sgx, 0, 0), Y), 0.05, H,
               ctx.tex, ctx.uv["post"], anc=nm)
        R.quad("post_print", F((sgx * (ex + tp - 0.025), y0 + H / 2, sgz * (ez + tp + 0.0002)), (0, 0, sgz), Y), 0.05, H,
               ctx.tex, ctx.uv["post"], anc=nm)
    seq.add(3, "corner posts A_INSERT_CARD_0..3")
    # the top cap: a corrugated tray upside down over the rack's roof and the post tops
    cx_, cz_ = ex + tp + 0.0025, ez + tp + 0.0025
    cap = R.anchor("A_INSERT_CARD_4", F((0, yt - 0.07, 0)), (2 * cx_, 0.074, 2 * cz_), lift="+y", dist=0.20,
                   label="top cap", order=2, under=["A_INSERT_WRAP_4", "A_STRAP_0", "A_STRAP_1"])
    R.cube("cap", (0, yt + 0.002, 0), (2 * cx_, 0.004, 2 * cz_), "cardboard", anc=cap)
    R.quad("cap_print", F((0, yt + 0.0042, 0), Y, NZ), 2 * cx_, 2 * cz_ * 0.7, ctx.tex, ctx.uv["cap"], anc=cap)
    for sg in (-1, 1):
        R.cube("cap_skirt", (sg * (cx_ - 0.00125), yt - 0.035, 0), (0.0025, 0.07, 2 * cz_), "cardboard", anc=cap)
        R.cube("cap_skirt", (0, yt - 0.035, sg * (cz_ - 0.00125)), (2 * cx_ - 0.005, 0.07, 0.0025), "cardboard", anc=cap)
    seq.add(2, "top cap A_INSERT_CARD_4")
    # on the roof, under the cap: the papers and the cage-nut kit (they travel with the rack)
    plist = papers_of(it, (0.5, 0.4))
    names, _ = RP.pile(R, plist, 0.0, pf["y_roof"] + 0.0003, -0.25, 3, [cap], parent="A_ITEM_PART_0")
    R.anchor("A_ITEM_HW_0", RP.flat_frame((0.0, pf["y_roof"] + 0.0003, 0.22)), (0.090, 0.120, 0.012), parent="A_ITEM_PART_0",
             label="CAGE NUTS + SCREWS M6 x 50", order=3, under=[cap])
    seq.add(3, f"on the roof: {len(names)} papers (3..{2 + len(names)}) and the cage-nut kit A_ITEM_HW_0")
    # the keys in a small bag taped to the front door, by the handle
    lo, hi = it["bounds"]
    zd = pf["az"] + 0.5355
    ko = (pf["ax"] + 0.150, pf["ay"] + 1.06, zd)
    tape = R.anchor("A_TAPE_0", F((ko[0], ko[1], zd + 0.0072)), (0.048, 0.110, 0.0001), parent="A_ITEM_PART_0", strip=0,
                    seg=0, peel="+y", label="tape", order=2, under=["A_INSERT_WRAP_0"])
    R.quad("tapelook", F((ko[0], ko[1], zd + 0.0073)), 0.048, 0.110, "tape_clear", anc=tape)
    keys = R.anchor("A_ITEM_HW_1", F(ko), (0.060, 0.080, 0.007), parent="A_ITEM_PART_0", kind="keys", label="DOOR KEYS",
                    look=1, bag="clear", order=3, under=[tape])
    keys_look(R, keys, (ko[0], ko[1], zd + 0.0005), fwd=Z, up=Y)
    R.quad("keys_label", F((ko[0], ko[1] - 0.030, zd + 0.0066)), 0.050, 0.030, ctx.tex, ctx.uv["keys"], anc=keys)
    seq.add(2, "the tape A_TAPE_0 over the keys on the front door")
    seq.add(3, "the door keys A_ITEM_HW_1 (kind=keys, for the front door lock)")
    # stretch film: one sheet per side and one over the top (cut and peeled in big sheets)
    Ex, Ez = cx_ + 0.001, cz_ + 0.001
    Hf = yt + 0.004 - (y0 + 0.004)
    ym = y0 + 0.004 + Hf / 2
    tf = 0.0004
    films = [("A_INSERT_WRAP_0", (0, ym, Ez + tf / 2), (2 * Ex + 2 * tf, Hf, tf), "+z", ["A_STRAP_0", "A_STRAP_1", "A_STRAP_2", "A_STRAP_3"]),
             ("A_INSERT_WRAP_1", (Ex + tf / 2, ym, 0), (tf, Hf, 2 * Ez), "+x", ["A_STRAP_2", "A_STRAP_3"]),
             ("A_INSERT_WRAP_2", (0, ym, -Ez - tf / 2), (2 * Ex + 2 * tf, Hf, tf), "-z", ["A_STRAP_0", "A_STRAP_1", "A_STRAP_2", "A_STRAP_3"]),
             ("A_INSERT_WRAP_3", (-Ex - tf / 2, ym, 0), (tf, Hf, 2 * Ez), "-x", ["A_STRAP_2", "A_STRAP_3"]),
             ("A_INSERT_WRAP_4", (0, yt + 0.004 + tf / 2 + 0.0001, 0), (2 * Ex + 2 * tf, tf, 2 * Ez + 2 * tf), "+y", ["A_STRAP_0", "A_STRAP_1"])]
    wraps = []
    for nm, cen, siz, d, und in films:
        R.anchor(nm, F((cen[0], cen[1] - (siz[1] / 2 if d != "+y" else 0), cen[2])), siz, lift=d, dist=0.25, kind="stretch_film",
                 peel="+y", label="stretch film", order=1, under=und)
        R.cube("film", cen, siz, "film_clear", anc=nm)
        wraps.append(nm)
    seq.add(1, "stretch film in five sheets A_INSERT_WRAP_0..4 (front, +x, back, -x, top)")
    # strapping bands: two over the top and through the pallet (along z), two round the posts
    ts, ws = 0.0008, 0.012
    Zp, yl, yd = PAL["l"] / 2 + 0.001, 0.0985, PAL["h"] + 0.0006
    Zl, yT = Ez + 0.0012 + ts, yt + 0.004 + 0.0012 + ts
    for i, xx in enumerate((-0.2, 0.2)):
        nm = f"A_STRAP_{i}"
        R.anchor(nm, F((xx, yT, 0)), (ws, ts, 2 * Zl), kind="pp_band", cut=1, label="strapping band", order=0)
        cl = [(-Zp, yl), (Zp, yl), (Zp, yd), (Zl, yd), (Zl, yT), (-Zl, yT), (-Zl, yd), (-Zp, yd)]
        R.slab("strap", P.poly_offset(cl, ts / 2), ws, "black_plastic", P.plane((xx, 0, 0), Z, Y),
               holes=[P.poly_offset(cl, -ts / 2)], anc=nm)
        R.cube("strap_seal", (xx, yT + ts, 0.0), (0.016, 0.0016, 0.030), "nickel", anc=nm)
    Xs, Zs = Ex + 0.0015 + ts, Ez + 0.0015 + ts
    for i, yy in enumerate((0.62, 1.62)):
        nm = f"A_STRAP_{2 + i}"
        R.anchor(nm, F((0, yy, Zs)), (2 * Xs, ws, ts), kind="pp_band", cut=1, label="strapping band", order=0)
        cl = [(-Xs, -Zs), (Xs, -Zs), (Xs, Zs), (-Xs, Zs)]
        R.slab("strap", P.poly_offset(cl, ts / 2), ws, "black_plastic", P.plane((0, yy, 0), X, Z),
               holes=[P.poly_offset(cl, -ts / 2)], anc=nm)
        R.cube("strap_seal", (0.0, yy, Zs + ts), (0.030, 0.016, 0.0016), "nickel", anc=nm)
    seq.add(0, "strapping bands A_STRAP_0..3 (cut)")
    seq.add(4, "the rack A_ITEM_PART_0 rolls off the pallet")
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_STRAP_0": (-0.25, 0.25, 0), "A_STRAP_1": (0.25, 0.25, 0), "A_STRAP_2": (0, 0.0, 0.55),
                 "A_STRAP_3": (0, 0.0, 0.70), "A_INSERT_WRAP_0": (0, 0, 0.35), "A_INSERT_WRAP_1": (0.35, 0, 0),
                 "A_INSERT_WRAP_2": (0, 0, -0.35), "A_INSERT_WRAP_3": (-0.35, 0, 0), "A_INSERT_WRAP_4": (0, 0.55, 0),
                 cap: (0, 0.35, 0), "A_TAPE_0": (0.05, 0.0, 0.20), keys: (0.15, 0.0, 0.25), "A_ITEM_HW_0": (0, 0.12, 0.2),
                 "A_INSERT_CARD_0": (-0.18, 0, 0.18), "A_INSERT_CARD_1": (0.18, 0, 0.18),
                 "A_INSERT_CARD_2": (0.18, 0, -0.18), "A_INSERT_CARD_3": (-0.18, 0, -0.18)}
    RP.explode_docs(R, names, (0.0, 0.10, -0.2), (0.04, 0.02, 0.05))
    R.open_hide = wraps + ["A_STRAP_0", "A_STRAP_1", "A_STRAP_2", "A_STRAP_3", "A_INSERT_CARD_0", "A_INSERT_CARD_1",
                           "A_INSERT_CARD_2", "A_INSERT_CARD_3", "A_INSERT_CARD_4", "A_TAPE_0"]
    R.views = ((30, 18), (-150, 20))
    R.closed_fill = 0.72
    R.open_fill = 0.75
    R.open_view = (28, 22)
    R.explode_view = (32, 22)
    R.explode_fill = 0.75
    NOTES[pid] = seq.text("42U rack on a pallet: ")
    return R


BUILDERS.update({"rack_flatpack": build_flatpack, "rack_pallet": _with_kit(build_pallet)})
SIZE.update({"rack_flatpack": size_flatpack, "rack_pallet": size_pallet})
ART["rack_pallet"] = art_pallet
