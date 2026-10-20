"""
cat_server_unbox: the protective bits of catalogue 18 and the task-01 gear (docs/tasks/catalog/README.md, "The
unboxing on every part"): the cap models, the film anchors, and where each sits.

Cap models (convention of extras_caps.py: the model's local +Z is the pull-off direction, its origin is the seat it
is placed at; A_HIT_0 meta remove=+z,travel=..,blocks=..; A_GRIP_0 at the pull tab, forward = the pull):
  cap_sfp     black dust plug for an SFP / SFP+ / SFP28 cage, a ribbed pull tab.     On: A_PORT_SFP_n, identity.
  cap_qsfp    the same for a QSFP28 cage.                                            On: A_PORT_QSFP_n, identity.
  cap_pcie4   clear U-channel over a card's x4 edge (39 mm), key rib, pull tab.      On: the card root, pull = card -Z.
  cap_pcie8   the same for an x8 edge (56 mm).                                       On: the card root, pull = card -Z.
  (x16 cards take the existing cap_pcie16, which fits the GPU contract's x16 edge they share.)

Films: anchors A_FILM_<NAME>_<n>, XY = the film surface, +Z out, size = (w, h, thickness), meta
film=clear,peel=<dir>,tab=<corner>. add_films(root, mid) adds the ones of a task-01 model; build_datacenter.py calls
it through its optional hook just before a model is finished (anchors only, nothing else changes).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import datacenter_common as D  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ
CLEAR = "clear_plastic"
FILM_T = 0.0001


# ====================================================================== films

def anchor_named(root, name):
    for o in c.descendants(root):
        if o.type == "EMPTY" and o.name == name:
            return o
    raise KeyError(name)


def film(name, fr, w, h, parent, peel="-x", tab="+x+y", extra=""):
    """A film anchor on the surface fr (its +Z out), lifted 0.05 mm off it."""
    return P.anchor(name, fr.sub(0, 0, 0.00005), (w, h, FILM_T), parent,
                    meta=f"film=clear,peel={peel},tab={tab}" + (("," + extra) if extra else ""))


def film_on_anchor(root, name, anchor, w, h, dz=0.0002, parent=None, **kw):
    """A film in an existing anchor's frame (a screen), dz out along its +Z; parented like that anchor's piece."""
    a = anchor_named(root, anchor)
    fr = P.anchor_frame(a)
    return film(name, fr.sub(0, 0, dz), w, h, parent if parent is not None else a.parent, **kw)


def ear_films(root, yb, yt, zf=0.030, xb=0.217):
    """The glossy control-panel covers on the two ears of the STRATA servers (datacenter_server.front)."""
    for k, sx in enumerate((-1, 1)):
        x = sx * (xb + D.EAR_W / 2) / 2
        film(f"A_FILM_EAR_{k}", P.Frame((x, (yb + yt) / 2, zf), Z, Y), D.EAR_W / 2 - xb - 0.0016, yt - yb - 0.0016, root,
             peel="-y", tab=("-x" if sx < 0 else "+x") + "+y")


def add_films(root, mid):
    """The task-01 gear (docs/tasks/catalog/18-server.md, retrofit): anchors only."""
    if mid == "server_1u":
        ear_films(root, 0.000425, 0.000425 + 0.0436)
    elif mid == "server_2u":
        ear_films(root, 0.0008, 0.0008 + 0.0873)
        bz = anchor_named(root, "A_BEZEL_0")
        fr = P.anchor_frame(bz)
        film("A_FILM_BEZEL_0", fr, 0.430, 0.0857, bz, peel="-x", tab="+x+y", extra="on=bezel")
    elif mid == "ups_2u":
        film_on_anchor(root, "A_FILM_SCREEN_0", "A_SCREEN_0", 0.062, 0.030, tab="+x+y")
        bz = anchor_named(root, "A_BEZEL_0")
        film("A_FILM_BEZEL_0", P.anchor_frame(bz), 0.320, 0.0813, bz, peel="-x", tab="+x+y", extra="on=bezel")
    elif mid == "ups_tower":
        film_on_anchor(root, "A_FILM_SCREEN_0", "A_SCREEN_0", 0.054, 0.024, tab="+x+y")
        bz = anchor_named(root, "A_BEZEL_0")
        film("A_FILM_BEZEL_0", P.anchor_frame(bz), 0.166, 0.145, bz, peel="-y", tab="+x+y", extra="on=bezel")
    elif mid == "pdu_0u":
        film_on_anchor(root, "A_FILM_SCREEN_0", "A_SCREEN_0", 0.027, 0.013, tab="+x+y")


# where the caps sit: model -> [(cap model, parent anchor or "<root>", local position, forward, up)]
def placements():
    out = {}
    for cid, n, kind, lanes in (("nic_linkwave_350t2", 0, None, 4), ("nic_linkwave_710da2", 2, "sfp", 8),
                                ("nic_melnet_strand6_25g", 2, "sfp", 8), ("nic_melnet_strand6_100g", 2, "qsfp", 16),
                                ("hba_broadline_9500_16i", 0, None, 8), ("hba_broadline_9560_16i", 0, None, 8)):
        out[cid] = [(f"cap_pcie{lanes}", "<root>", (0, 0, 0), (0, 0, -1), (0, 1, 0))]
        out[cid] += [(f"cap_{kind}", f"A_PORT_{kind.upper()}_{k}", (0, 0, 0), (0, 0, 1), (0, 1, 0)) for k in range(n)]
    for mid, n in (("srv_linkwave_ls4804x", 4), ("srv_linkwave_ls1600x", 16), ("switch_24", 4)):
        out[mid] = [("cap_sfp", f"A_PORT_SFP_{k}", (0, 0, 0), (0, 0, 1), (0, 1, 0)) for k in range(n)]
    return out


FILMS = {   # every film anchor this family adds, per model (for the report and the catalogue JSON)
    "server_1u": ["A_FILM_EAR_0", "A_FILM_EAR_1"],
    "server_2u": ["A_FILM_EAR_0", "A_FILM_EAR_1", "A_FILM_BEZEL_0@A_BEZEL_0"],
    "ups_2u": ["A_FILM_SCREEN_0", "A_FILM_BEZEL_0@A_BEZEL_0"],
    "ups_tower": ["A_FILM_SCREEN_0", "A_FILM_BEZEL_0@A_BEZEL_0"],
    "pdu_0u": ["A_FILM_SCREEN_0"],
    "srv_strata_sg840_4u": ["A_FILM_EAR_0", "A_FILM_EAR_1"],
    "srv_strata_sr224_2u": ["A_FILM_EAR_0", "A_FILM_EAR_1"],
    "srv_strata_kvm_1u": ["A_FILM_SCREEN_0@A_LID_0@A_DRAWER_0"],
}


# ====================================================================== cap models

def _grip_and_hit(root, hit_c, hit_s, meta, grip_c, grip_s):
    P.anchor("A_HIT_0", hit_c, hit_s, root, meta=meta)
    P.anchor("A_GRIP_0", P.Frame(grip_c, Z, Y), grip_s, root, meta="pull=+z")


SFP_PLUG = {"cap_sfp": (D.SFP_W, D.SFP_H, 0.012, "sfp"), "cap_qsfp": (0.0184, 0.0090, 0.014, "qsfp")}


def build_port_plug(mid):
    """A cage dust plug in the port anchor's frame: the hollow insert (snug in the cage mouth, 0.1 mm clearance),
    a head on the cage's gasket lip, a pull tab standing out of the head with grip ridges."""
    w, h, depth, kind = SFP_PLUG[mid]
    P.reset()
    root = c.root(mid)
    D.ROOT[0] = root
    iw, ih = w - 0.0002, h - 0.0002
    z_lip = 0.0006                        # the gasket's front face (datacenter_common.sfp_cage)
    P.slab("plug_insert", P.rrect(iw, ih, 0.0006), depth, "rubber", P.Frame((0, 0, z_lip - depth / 2), Z, Y),
           holes=[P.rrect(iw - 0.0016, ih - 0.0016, 0.0004)], parent=root)
    P.slab("plug_floor", P.rrect(iw - 0.0010, ih - 0.0010, 0.0004), 0.0006, "rubber", P.Frame((0, 0, z_lip - depth + 0.0003), Z, Y), parent=root)
    hw, hh = w + 0.0034, h + 0.0034
    P.slab("plug_head", P.rrect(hw, hh, 0.0012), 0.0012, "rubber", P.Frame((0, 0, z_lip + 0.0006), Z, Y), parent=root)
    # pull tab: a fin in the x-z plane with a rounded end, ribs each side
    tl = 0.0075 if kind == "sfp" else 0.0085
    tw = w * 0.55
    tab = [(-tw / 2, 0.0), (tw / 2, 0.0), (tw / 2, tl - tw / 2)] + \
          [(tw / 2 * math.cos(math.radians(a)), tl - tw / 2 + tw / 2 * math.sin(math.radians(a))) for a in range(15, 180, 15)] + [(-tw / 2, tl - tw / 2)]
    tf = P.Frame((0, 0, z_lip + 0.0012), Y, Z)          # local x = card x, local y = +z (out), thin along y
    P.slab("plug_tab", tab, 0.0010, "rubber", tf, parent=root)
    P.slab("plug_tab_hole", P.circle(0.0012, 0, tl - tw / 2, 12), 0.0002, "dark_plastic", tf.sub(0, 0, 0.0006), parent=root)
    for z in (0.0020, 0.0032):
        for sgn in (-1, 1):
            P.cube("plug_rib", (0, sgn * 0.00055, z_lip + 0.0012 + z), (tw * 0.8, 0.0002, 0.0004), "rubber", P.WORLD, root)
    _grip_and_hit(root, (0, 0, (z_lip - depth + z_lip + 0.0012 + tl) / 2), (hw, hh, depth + 0.0012 + tl),
                  f"remove=+z,travel={depth:.3f},port={kind},blocks=plug", (0, 0, z_lip + 0.0012 + tl * 0.6), (tw, 0.002, tl * 0.8))
    extra = f"frame: the port anchor (A_PORT_{kind.upper()}_n): +z out of the cage, +y the cage top; insert {depth * 1000:.0f} mm deep"
    return D.finish(root, mid, preview_views=((30, 25), (150, 25)), beauty_views=((35, 20),), size=(700, 600), samples=32, extra=extra)


LONG_PINS = {4: 21, 8: 38}


def build_edge_cap(mid):
    """A clear PET U-channel over a card's gold fingers (cap_pcie16's design, cut to the x4 / x8 edge): 0.45 mm
    walls round the 1.6 mm board, closed ends 0.5 mm past the edge, a key rib in the notch, a pull tab with a finger
    hole off the far end. Built in the card frame through CF (model +Z = card -z, +Y = card +y)."""
    lanes = int(mid.replace("cap_pcie", ""))
    xe = 0.0300 - (LONG_PINS[lanes] - 1) * 0.001 - 0.0045
    P.reset()
    root = c.root(mid)
    D.ROOT[0] = root
    CF = P.Frame((0, 0, 0), (0, 0, -1), (0, 1, 0))      # card coordinates -> cap model
    yi0, yi1 = -0.00192, -0.00008
    yo0, yo1 = -0.00237, 0.00037
    zf, zb, zt = -0.0056, -0.0061, -0.0004
    x0, x1 = xe - 0.0010, 0.0450
    # the channel: floor, two walls (in card coordinates through CF)
    D.fbox("cap_floor", CF, (x0, yo0, zb), (x1, yo1, zf), CLEAR, root)
    D.fbox("cap_wall", CF, (x0, yo0, zf), (x1, yi0, zt), CLEAR, root)
    D.fbox("cap_wall", CF, (x0, yi1, zf), (x1, yo1, zt), CLEAR, root)
    for xa in (x0 - 0.0005, x1):
        D.fbox("cap_end", CF, (xa, yo0, zb), (xa + 0.0005, yo1, zt), CLEAR, root)
    D.fbox("cap_key", CF, (0.0313, yi0, zf), (0.0325, yi1, -0.0042), CLEAR, root)
    for y in (yo0 + 0.0004, yo1 - 0.0004):
        D.fbox("cap_rib", CF, (x0 + 0.001, y - 0.00012, zb - 0.00012), (x1 - 0.001, y + 0.00012, zb), CLEAR, root)
    # pull tab off the far end, in the board plane, with a finger hole
    tx = x0 - 0.0005 - 0.0036
    tab_fr = P.Frame(CF.p(0, -0.00135, 0), CF.d(0, -1, 0), CF.d(0, 0, 1))      # local x = card x, local y = card z
    P.slab("cap_tab", P.rrect(0.0072, 0.0040, 0.0012, tx, -0.0041), 0.0007, CLEAR, tab_fr,
           holes=[P.circle(0.0011, tx - 0.0010, -0.0041, 16)], parent=root)
    lo, hi = CF.p(x1 + 0.0005, yo1, zt), CF.p(tx - 0.0036, yo0, zb - 0.00012)
    cen = tuple((a + b) / 2 for a, b in zip(lo, hi))
    size = tuple(abs(a - b) for a, b in zip(lo, hi))
    _grip_and_hit(root, cen, size, f"remove=+z,travel=0.0015,part=card,blocks=install,edge={0.0445 - xe:.3f},lanes={lanes}",
                  tuple(CF.p(tx, -0.001, -0.0041)), (0.0072, 0.0015, 0.0040))
    extra = f"frame: the card frame turned so +z = the pull (card -z): sits at the card root, forward (0,0,-1), up (0,1,0); edge x {xe:.4f}..0.0445"
    return D.finish(root, mid, preview_views=((30, 30), (-150, 30)), beauty_views=((30, 25),), size=(900, 500), samples=32, extra=extra)
