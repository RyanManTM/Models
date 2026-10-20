"""
rig_oem: the plain OEM packaging rigs of the server parts (docs/tasks/catalog/19-boxes.md, "server parts"). Called by
build_boxes.py (RIG_MODULES). Same conventions and helpers as rig_products: the box frame has its origin at the bottom
centre, +z the front, y up, closed pose; A_HIT_0 = the outer size.

One rig design per size class, scaled to the part's measured bounds:
  * oem_cpu (small): a white tuck-top box with two seal stickers; a black PE foam pad with a die-cut window holds the
    black clamshell tray, its clear lid showing the CPU in its carrier; the papers lie on the clamshell.
  * oem_rdimm (small): a white end-tuck carton (seal over the end flap); a clear clamshell slides out with the module
    in its pink anti-static bag; the papers lie on the clamshell lid; a seal on the clamshell.
  * oem_u2, oem_heatsink, oem_card ("foam sandwich"): a taped white slotted carton; a die-cut top foam pad with the
    papers on it; the part (in its bag) and its accessories (low-profile bracket, cables) in pockets of the bottom foam.
  * oem_psu (PSU): a taped white slotted carton, the CRPS module in its bag between two EPS end caps (lifted out
    with it), the papers on top.
  * oem_board (board): a taped brown carton; the board in its silver bag on a PE foam pad on a corrugated tray; under
    the tray the accessory compartment (I/O shield, screw bag, papers).
The print is the plain OEM board (build_boxes.oem_face / oem_label) with the label on the largest face (ART below).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_c as P  # noqa: E402
import rig_common as RC  # noqa: E402
import rig_products as RP  # noqa: E402
from rig_common import F, Rig, X, Y, Z, NX, NY, NZ, rr  # noqa: E402
from rig_products import (PART_BOUNDS, bsize, doc, explode_docs, flat_frame, paper_list, pile, rsc_box,  # noqa: E402
                          seal_rect_flat, seal_round, sub_uv)

NOTES = {}


def up5(x):
    import box_catalog as BC
    return BC.up5(x)


def _num(x):
    return f"{x:g}"


# ---------------------------------------------------------------- the words on the boxes (item hook)

def _name(p):
    n = p["name"]
    return n[len(p["brand"]):].strip() if n.startswith(p["brand"]) else n


def item(pid, it):
    """The catalogue items of the OEM kinds: the plain OEM print, and proper words from the part's specs."""
    p = it["part"]
    s, g = p["specs"], p["game"]
    kind = it["kind"]
    it["style"] = "oem"
    it["oem_base"] = "kraft" if kind == "oem_board" else "white"
    name = _name(p)
    it["model"] = name.upper()
    badges = []
    if kind == "oem_cpu":
        line = "SERVER PROCESSOR"
        it["label_line"] = f"SOCKET {g['socket']} PROCESSOR"
        specs = [f"{s['cores']} cores / {s['threads']} threads", f"{_num(s['base_ghz'])} GHz base, up to {_num(s['boost_ghz'])} GHz",
                 f"{s['l3_mb']} MB L3 cache", f"Socket {g['socket']}", f"{s['tdp_w']} W TDP",
                 f"{s['mem_channels']} DDR5 channels, {s['pcie_lanes']} PCIe lanes"]
        badges = [f"{s['cores']} CORES", f"SOCKET {g['socket']}"]
        it["bag"] = "none"
    elif kind == "oem_rdimm":
        line = "SERVER MEMORY"
        it["label_line"] = f"{g['mem']} RDIMM ECC"
        specs = [f"{g['ram_gb']} GB {g['mem']} registered DIMM", f"{s['speed_mts']} MT/s CL{s['cas']}", "ECC, registered (RCD)",
                 f"Rank: {s['ranks']}", f"{_num(s['voltage'])} V", "Server use only"]
        badges = [f"{g['ram_gb']} GB", g["mem"] + " RDIMM"]
        it["bag"] = "antistatic_pink"
    elif kind == "oem_u2":
        cap = g["storage_gb"]
        line = "ENTERPRISE NVMe SSD"
        it["label_line"] = 'U.2 NVMe SSD'
        specs = [f"{cap / 1000:g} TB", s["form"], s["interface"], f"Up to {s['read_mbs']} MB/s read",
                 f"Up to {s['write_mbs']} MB/s write", f"{s['dwpd']} DWPD" + (", power-loss protection" if s.get("plp") else "")]
        badges = [f"{cap / 1000:g} TB", "U.2"]
        it["bag"] = "antistatic_silver"
    elif kind == "oem_heatsink":
        line = "SERVER CPU HEATSINK"
        it["label_line"] = f"SOCKET {g['socket']} HEATSINK"
        specs = [f"Socket {g['socket']}", f"Up to {g['cooler_max_w']} W", f"Height {s['height_mm']} mm",
                 f"{s['screws']} captive {s['drive']} screws", f"Airflow {s['airflow']}"]
        if s.get("heat_pipes"):
            specs.insert(3, f"{s['heat_pipes']} heat pipes")
        it["bag"] = "none"
    elif kind == "oem_psu":
        line = "CRPS HOT-PLUG POWER SUPPLY"
        it["label_line"] = f"{g['psu_watts']} W CRPS PSU"
        specs = [f"{g['psu_watts']} W", s["efficiency"], f"{s['form_factor']}, {_num(s['width_mm'])} x {s['height_mm']} x "
                 f"{s['depth_mm']} mm", "Hot-swap, redundant", f"{s['fan_mm']} mm fan", "C14 inlet"]
        badges = [f"{g['psu_watts']} W", s["efficiency"].replace("80 PLUS ", "").upper()]
        it["bag"] = "antistatic_pink"
    elif kind == "oem_card":
        if pid.startswith("gpu_"):
            line = "DATA CENTRE ACCELERATOR"
            specs = [f"{s['vram_gb']} GB HBM", f"Boost up to {s['boost_mhz']} MHz", "Passive, needs server airflow",
                     f"Length {s['length_mm']} mm, {s['slots']}-slot", "No display outputs"]
        elif pid.startswith("hba_"):
            line = "RAID CONTROLLER" if s.get("cache_gb") else "HOST BUS ADAPTER"
            specs = [f"{s['internal_ports']} internal ports, {s['connectors']}", f"SAS {s['sas_gbps']} Gb/s, SATA, NVMe",
                     f"PCIe {s['pcie_gen']} x{s['pcie_lanes']}", "Low-profile bracket included"]
            if s.get("cache_gb"):
                specs.insert(1, f"{s['cache_gb']} GB cache, supercap backup")
                specs.insert(2, f"RAID {s['raid_levels']}")
        else:
            line = "NETWORK ADAPTER"
            specs = [f"{s['ports']} x {s['port_kind']}, {s['speed_gbps']} Gb/s", f"PCIe {_num(s['pcie_gen'])} x{s['pcie_lanes']}",
                     f"Card length {s['length_mm']} mm", "Low-profile bracket included"]
        it["label_line"] = line
        it["bag"] = "antistatic_silver"
        if s.get("lp_bracket"):
            it["acc_models"] = [s["lp_bracket"]]       # measured with the part: posed at A_ITEM_ACC
    elif kind == "oem_board":
        line = "SERVER MOTHERBOARD"
        it["label_line"] = f"{s['form']} SERVER BOARD"
        specs = [f"{s['sockets']} x Socket {g['socket']}", f"{s['dimm_slots']} x DDR5 RDIMM, up to {s['max_ram_gb'] // 1024} TB",
                 f"{s['pcie_x16']} x PCIe 5.0 x16" + (f", {s['ocp']} x OCP 3.0" if s.get("ocp") else ""),
                 f"{s['m2_slots']} x M.2, {s['mcio']} x MCIO, {s['sata']} x SATA", f"BMC, {s['lan_gbe']}GbE LAN", s["form"]]
        badges = [f"SOCKET {g['socket']}", "DDR5"]
        it["bag"] = "antistatic_silver"
        it["ink"] = (0.10, 0.09, 0.08)
    else:
        return
    it["line"] = line
    it["specs"] = specs[:6]
    it["badges"] = badges


# ---------------------------------------------------------------- print: the plain OEM board, the label on the big face

def oem_art(pid, it, s, hero, kraft):
    """compose_oem with the label where it is seen: on the front and one end of a tall box, on the top of a flat one."""
    import build_boxes as BB
    fw = min(s[0] * 0.3, s[2] * 0.45)
    reg, W, H = BB.layout(s, fw)
    art = P.Art(W, H, bg=(0.5, 0.5, 0.5), name="box_" + pid)
    seed = P.shash(pid) & 0xffff
    big = max(s) > 0.4
    flat = s[1] < 0.5 * min(s[0], s[2])
    for n in ("front", "back", "left", "right"):
        BB.oem_face(BB.Face(art, reg[n]), it, kraft, seed, label=(not flat and n in ("front", "right")), big=big)
    for n in ("bottom", "flapL", "flapR"):
        BB.oem_bg(BB.Face(art, reg[n]), it, kraft)
    T = BB.Face(art, reg["top"])
    if flat:
        BB.oem_face(T, it, kraft, seed, label=True)
    else:
        BB.oem_bg(T, it, kraft)
        BB.logo(T, it, T.X(0.5), T.Y(0.5), T.m * 0.14, it.get("ink", (0.1, 0.1, 0.11)), align="CENTER", valign="CENTER",
                maxw=T.w * 0.6)
    art.render("box_" + pid)
    art.dispose()
    return reg, W, H, fw


# ---------------------------------------------------------------- posing a part model in the box

def posed(lo, hi, fwd, up):
    """The box-space AABB (lo, hi) of a model's bounds posed at the origin with the frame (fwd, up)."""
    fr = F((0, 0, 0), fwd, up)
    pts = [fr.p(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))


def place(mid, fwd, up, centre_x, y_bottom, centre_z, b=None):
    """The frame that puts model mid (pose fwd/up) with its AABB centred on (centre_x, centre_z), bottom at y_bottom.
    Returns (frame, box lo, box hi)."""
    lo, hi = b or PART_BOUNDS[mid]
    plo, phi = posed(lo, hi, fwd, up)
    o = (centre_x - (plo[0] + phi[0]) / 2, y_bottom - plo[1], centre_z - (plo[2] + phi[2]) / 2)
    return F(o, fwd, up), tuple(o[i] + plo[i] for i in range(3)), tuple(o[i] + phi[i] for i in range(3))


def bounds_of(ctx_or_it):
    it = ctx_or_it.it if hasattr(ctx_or_it, "it") else ctx_or_it
    return it["bounds"]


# ---------------------------------------------------------------- small class: the server CPU (tuck box, clamshell)

CPU_T = 0.0008


def cpu_plan(lo, hi):
    cw, cd = hi[0] - lo[0], hi[1] - lo[1]
    fl = (cw + 0.026, cd + 0.026)
    hf = 0.009                                  # the foam pad
    dl, dp = 0.003, 0.0072                      # ledge, pocket depth of the clamshell
    dome = (hi[2] + 0.0009 - dl) + 0.0012       # the lid clears the carrier
    return dict(cw=cw, cd=cd, fl=fl, hf=hf, dl=dl, dp=dp, dome=dome)


def size_cpu(pid, it):
    lo, hi = it["bounds"]
    q = cpu_plan(lo, hi)
    t = CPU_T
    sx = up5(q["fl"][0] + 0.010 + 2 * t)
    sz = up5(q["fl"][1] + 0.010 + 2 * t)
    sy = up5(t + 0.0002 + q["hf"] + q["dome"] + 0.0012 + 0.004 + 0.006 + t)
    return (sx, max(0.03, sy), sz)


def build_cpu(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = CPU_T
    inner = "paper_white"
    lo, hi = PART_BOUNDS[ctx.it.get("model_id", pid)]
    q = cpu_plan(lo, hi)
    H = RP.tuck_walls(R, ctx, t, inner, notch_r=0.009)
    xs = min(0.030, sx * 0.25)
    for i, x_ in enumerate((-xs, xs)):
        seal_round(R, f"A_SEAL_{i}", x_, sy, sz / 2, 0.016, 0.005, text="SEALED")
    RP.tuck_lid_top(R, ctx, t, inner, open_deg=-115, under=["A_SEAL_0", "A_SEAL_1"])
    flaps = RP.dust_flaps(R, ctx, t, inner, H, min(0.026, sx * 0.2))
    opened = ["A_FLAP_0"] + flaps
    # the PE foam pad with a die-cut window: the clamshell's pocket sits in it
    y0 = t + 0.0002
    fx, fz = sx - 2 * t - 0.002, sz - 2 * t - 0.002
    cy = y0 + q["hf"]
    plist = paper_list(ctx, sizes={"leaflet": (0.100, 0.070, 0.0012), "card": (0.088, 0.056, 0.0004),
                                   "booklet": (0.090, 0.064, 0.0025)}, fit=(fx - 0.006, fz - 0.006))
    n = len(plist)
    o_foam = 3 + n
    foam = R.anchor("A_INSERT_FOAM_0", F((0, y0, 0)), (fx, q["hf"], fz), lift="+y", dist=0.06, label="foam pad",
                    order=o_foam, under=[f"A_ITEM_DOC_{n - 1}"] if n else opened)
    pad = 0.0018
    win = P.rrect(q["cw"] + 2 * pad + 0.004, q["cd"] + 2 * pad + 0.004, 0.003)
    R.slab("foam", P.rrect(fx, fz, 0.002), q["hf"], "pe_foam", P.plane((0, y0 + q["hf"] / 2, 0), X, NZ), holes=[win],
           anc=foam)
    # the clamshell on the foam: a black base, a clear lid so the carrier shows
    clam, lid = RP.clamshell(R, ctx, (0, cy, 0), (q["cw"], q["cd"]), q["dl"], q["dp"], q["fl"], foam,
                             order_lid=o_foam + 1, order_clam=o_foam + 3, under_lid=[foam], under_clam=["A_ITEM_PART_0"],
                             base_tag="black_plastic", lid_tag="clear_plastic", dome=q["dome"], part_pad=pad,
                             label="clamshell tray")
    yc = (lo[1] + hi[1]) / 2
    xc = (lo[0] + hi[0]) / 2
    R.anchor("A_ITEM_PART_0", F((-xc, cy - q["dl"] + 0.0009, yc), Y, NZ), bsize(ctx.it.get("model_id", pid), 0.0005),
             parent=clam, bag="none", label="CPU in its carrier", order=o_foam + 2, under=[lid])
    # the papers on the clamshell lid
    yd = cy + 0.0005 + q["dome"] + 0.0007 + 0.0003
    names, _ = pile(R, plist, 0.0, yd, 0.0, 3, opened, step=(0.003, -0.003))
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_FOAM_0": (0, 0.06, 0), "A_INSERT_CLAM_0": (0, 0.03, 0), "A_ITEM_PART_0": (0, 0.035, 0),
                 "A_SEAL_0": (0, 0.02, 0.03), "A_SEAL_1": (0, 0.02, 0.03)}
    explode_docs(R, names, (0.0, 0.13, 0.10), (0.0, 0.015, 0.05))
    R.open_view = (22, 58)
    R.explode_view = (28, 34)
    R.explode_fill = 0.8
    NOTES[pid] = (f"Server CPU: 2 seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> {n} papers on "
                  f"the clamshell, top first (3..{2 + n}) -> PE foam pad A_INSERT_FOAM_0 lifted out with the clamshell "
                  f"({o_foam}) -> clear clamshell lid A_CLAMLID_0 ({o_foam + 1}) -> CPU in its carrier, bag=none ({o_foam + 2}) "
                  f"-> clamshell base A_INSERT_CLAM_0 ({o_foam + 3}).")
    return R


# ---------------------------------------------------------------- small class: the RDIMM (end tuck box, clamshell)

DIMM_T = 0.0007


def dimm_plan(lo, hi):
    sh = hi[2] - lo[2]                        # the module height (lies along the box z)
    th = hi[0] - lo[0]
    cav_w = (hi[1] - lo[1]) + 0.0050          # the bag's margin
    cav_d = sh + 0.0060
    depth = th + 0.0045
    flw, fld = cav_w + 0.014, cav_d + 0.014
    return dict(sh=sh, th=th, cav_w=cav_w, cav_d=cav_d, depth=depth, flw=flw, fld=fld, dome=0.0030)


def size_rdimm(pid, it):
    lo, hi = it["bounds"]
    q = dimm_plan(lo, hi)
    t = DIMM_T
    sx = up5(q["flw"] + 2 * t + 0.006)
    sz = up5(q["fld"] + 2 * t + 0.004)
    sy = up5(t + 0.0004 + q["depth"] + q["dome"] + 0.0005 + 0.003 + 0.002 + t)
    return (sx, max(0.025, sy), sz)


def build_rdimm(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = DIMM_T
    inner = "paper_white"
    mid = ctx.it.get("model_id", pid)
    lo, hi = PART_BOUNDS[mid]
    q = dimm_plan(lo, hi)
    seal_round(R, "A_SEAL_0", 0.0, sy, sx / 2, 0.015, 0.005, text="SEALED", face="right")
    covers = RP.end_tuck_box(R, ctx, t, inner, tongue=0.008, seal="A_SEAL_0")
    flw, fld, depth = q["flw"], q["fld"], q["depth"]
    bxc = -sx / 2 + t + 0.0008 + flw / 2
    yfl = t + 0.0004 + depth
    bl = R.anchor("A_INSERT_BLISTER_0", F((bxc, t, 0)), (flw, depth + q["dome"] + 0.001, fld), lift="+x", dist=sx,
                  label="clamshell", order=3, under=covers)
    fr = F((bxc, yfl, 0), Y, NZ)
    RP.blister(R, "clam", fr, (flw, fld), [(q["cav_w"], q["cav_d"], 0.003, 0, 0)], depth, 0.0005, "clear_plastic", bl,
               lip=0.0010)
    # the papers on the clamshell lid (inside the carton), then the seal, then the lid
    plist = paper_list(ctx, sizes={"guide": (0.120, 0.045, 0.0004), "warranty": (0.100, 0.045, 0.0004),
                                   "safety": (0.120, 0.045, 0.0004)}, forms={"guide": "card", "safety": "card"},
                       fit=(flw - 0.004, fld - 0.004))
    n = len(plist)
    o_lid = 4 + max(1, n)
    seal_rect_flat(R, "A_SEAL_1", F((bxc, yfl + 0.0011, fld / 2 - 0.006), Y, Z), 0.014, 0.012, order=4, peel="+y",
                   under=[bl], parent=bl)
    lid = R.anchor("A_CLAMLID_0", F((bxc, yfl + 0.0005, -fld / 2 + 0.004)), (flw, q["dome"] + 0.001, fld - 0.004), parent=bl,
                   hinge="x", open=-165, label="clamshell lid", order=o_lid,
                   under=["A_SEAL_1"] + ([f"A_ITEM_DOC_{n - 1}"] if n else []))
    RP.blister(R, "clam_lid", F((bxc, yfl + 0.0005, 0.002), Y, NZ), (flw, fld - 0.004),
               [(q["cav_w"] + 0.001, q["cav_d"] + 0.001, 0.003, 0, 0.002)], q["dome"], 0.0005, "clear_plastic", lid,
               lip=0.0, dome=True)
    # the module: label side up, gold fingers to the front, in its pink bag
    frp, _, _ = place(mid, NZ, X, bxc, yfl - depth + 0.0016, 0.0)
    R.anchor("A_ITEM_PART_0", frp, bsize(mid, 0.002), parent=bl,
             bag=ctx.it.get("bag", "antistatic_pink"), guard=1, label="server memory module", order=o_lid + 1, under=[lid])
    names, _ = pile(R, plist, bxc + 0.003, yfl + 0.0005 + q["dome"] + 0.0003, 0.0, 4, [bl], parent=bl,
                    frame_fn=lambda o: flat_frame(o, Y, NZ), step=(0.003, -0.002))
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_BLISTER_0": (0.20, 0.03, 0), "A_SEAL_0": (0.03, 0.01, 0), "A_SEAL_1": (0, 0.02, 0.02),
                 "A_ITEM_PART_0": (0, 0.035, 0.0)}
    explode_docs(R, names, (-0.02, 0.10, 0.11), (0.0, 0.012, 0.05))
    R.open_view = (40, 48)
    R.explode_view = (32, 40)
    R.explode_fill = 0.9
    R.open_extra = {"A_INSERT_BLISTER_0": (0.10, 0, 0)}
    NOTES[pid] = (f"RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> "
                  f"clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the {n} papers, "
                  f"top first (4..{3 + n}) -> clamshell lid A_CLAMLID_0 ({o_lid}) -> module in its pink bag, guard=1 "
                  f"({o_lid + 1}).")
    return R


# ---------------------------------------------------------------- "foam sandwich" class: U.2, heatsinks, cards

FS_T = 0.002          # corrugated board
M = 0.012             # foam around the pockets
GAP = 0.010           # foam between pockets
PAPERS_UP = 0.006     # the papers' room above the top foam


def sandwich_spec(pid, it):
    """The part's pose and its accessories: {fwd, up, bag, pad, accs: [(name, mid or None, (w, h, t) or bounds, meta)]}"""
    kind = it["kind"]
    s = it["part"]["specs"]
    if kind == "oem_u2":
        return dict(fwd=Z, up=Y, pad=0.004, accs=[], label="U.2 SSD")
    if kind == "oem_heatsink":
        return dict(fwd=Y, up=NZ, pad=0.002, accs=[], label="heatsink")
    accs = []
    if s.get("lp_bracket"):
        accs.append(("bracket", s["lp_bracket"]))
    if pid.startswith("hba_"):
        accs.append(("cord", "sff8654"))
    if pid == "gpu_verdia_t100":
        accs.append(("cord", "12v2x6"))
    return dict(fwd=NZ, up=NY, pad=0.004, accs=accs,
                label="accelerator card" if pid.startswith("gpu_") else "network card" if pid.startswith("nic_")
                else "storage controller")


CORD_SIZE = {"sff8654": (0.100, 0.080, 0.016), "12v2x6": (0.090, 0.070, 0.014)}
BRACKET_POSE = (X, Z)                 # lying flat: the bracket's long axis along the box x, its tab up


def acc_dims(a):
    kind, ref = a
    if kind == "bracket":
        lo, hi = PART_BOUNDS[ref]
        plo, phi = posed(lo, hi, *BRACKET_POSE)
        return tuple(phi[i] - plo[i] for i in range(3))
    w, h, tt = CORD_SIZE[ref]
    return (w, tt, h)                  # (x, y, z) in the box


def sandwich_plan(pid, it, s=None):
    """Everything about the layout in box space. With s (the box size) the foam fills the carton."""
    sp = sandwich_spec(pid, it)
    lo, hi = it["bounds"]
    plo, phi = posed(lo, hi, sp["fwd"], sp["up"])
    pd = [phi[i] - plo[i] + 2 * sp["pad"] for i in range(3)]          # the part's pocket (x, y, z)
    accs = [(a, acc_dims(a)) for a in sp["accs"]]
    acc_w = sum(d[0] for _, d in accs) + GAP * max(0, len(accs) - 1)
    acc_d = max([d[2] for _, d in accs] + [0.0])
    acc_h = max([d[1] for _, d in accs] + [0.0])
    inX = max(pd[0], acc_w) + 2 * M
    inZ = pd[2] + (acc_d + GAP if accs else 0.0) + 2 * M
    fb = 0.008                                                        # foam under the deepest pocket
    ysplit = fb + max(pd[1] * 0.55, acc_h + 0.002)                    # the split between the two foams (over the floor)
    ytop = max(fb + pd[1], ysplit) + 0.010
    t = FS_T
    if s is None:
        s = (up5(inX + 2 * t + 0.001), up5(t + 0.0004 + ytop + PAPERS_UP + t + 0.002), up5(inZ + 2 * t + 0.001))
    sx, sy, sz = s
    inX, inZ = sx - 2 * t - 0.001, sz - 2 * t - 0.001
    y0 = t + 0.0004
    # the part's pocket at the back (or centred without accessories), the accessories in a row in front of it
    z_part = (-inZ / 2 + M + pd[2] / 2) if accs else 0.0
    z_acc = z_part + pd[2] / 2 + GAP + acc_d / 2
    x = -acc_w / 2
    acc_pos = []
    for a, d in accs:
        acc_pos.append((a, d, (x + d[0] / 2, z_acc)))
        x += d[0] + GAP
    return dict(sp=sp, pd=pd, plo=plo, phi=phi, accs=acc_pos, y0=y0, yfloor=y0 + fb, ysplit=y0 + ysplit, ytop=y0 + ytop,
                inX=inX, inZ=inZ, z_part=z_part, s=s)


def size_sandwich(pid, it):
    return sandwich_plan(pid, it)["s"]


def build_sandwich(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = FS_T
    mid = ctx.it.get("model_id", pid)
    q = sandwich_plan(pid, ctx.it, ctx.s)
    sp = q["sp"]
    rsc_box(R, ctx, t, "cardboard", tape_tag="tape_clear", tape_w=0.036 if sx < 0.2 else 0.048, tape_down=min(0.05, sy * 0.55))
    short = ["A_FLAP_2", "A_FLAP_3"]
    inX, inZ, y0 = q["inX"] - 0.001, q["inZ"] - 0.001, q["y0"]
    ys, yt, yf = q["ysplit"], q["ytop"], q["yfloor"]
    # papers on the top foam, top first
    plist = paper_list(ctx, fit=(inX - 0.008, inZ - 0.008), booklets_last=True)
    n = len(plist)
    names, _ = pile(R, plist, 0.0, yt + 0.0002, 0.0, 3, short, step=(0.004, -0.004))
    o_top = 3 + n
    o_part = o_top + 1
    o_bot = o_part + 1
    # the top foam: a die-cut pad over the part (a pocket for its top)
    top = R.anchor("A_INSERT_FOAM_1", F((0, ys, 0)), (inX, yt - ys, inZ), lift="+y", dist=0.08, label="top foam",
                   order=o_top, under=[names[-1]] if names else short)
    ob = R.cube("foam_top", (0, (ys + yt) / 2, 0), (inX, yt - ys, inZ), "pe_foam", anc=top, bevel=0.0015)
    pd = q["pd"]
    pcen = (0.0, q["z_part"])
    ypb = yf                                                    # the pocket floor = the bag's bottom
    ypt = yf + pd[1]
    cuts = []
    if ypt > ys:
        cuts.append(RC.tmp_cube((pcen[0], (ys + ypt) / 2 - 0.0005, pcen[1]), (pd[0], ypt - ys + 0.001, pd[2]), bevel=0.001))
    if cuts:
        R.cut(ob, cuts)
    # the bottom foam: the part's pocket, finger notches, the accessories' pockets
    bot = R.anchor("A_INSERT_FOAM_0", F((0, y0, 0)), (inX, ys - y0, inZ), lift="+y", dist=0.08, label="bottom foam",
                   order=o_bot, under=["A_ITEM_PART_0"] + [f"A_ITEM_{'ACC' if k == 'bracket' else 'CORD'}_{i}"
                                                             for i, ((k, _), _, _) in enumerate(q["accs"])])
    ob = R.cube("foam_bottom", (0, (y0 + ys) / 2, 0), (inX, ys - y0, inZ), "pe_foam", anc=bot, bevel=0.0015)
    cuts = [RC.tmp_cube((pcen[0], (ypb + ys) / 2 + 0.0005, pcen[1]), (pd[0], ys - ypb + 0.001, pd[2]), bevel=0.001)]
    nr = min(0.014, pd[2] * 0.25)
    for xo in (-pd[0] * 0.25, pd[0] * 0.25) if pd[0] > 0.16 else (0.0,):
        cuts.append(RC.tmp_cyl(F((pcen[0] + xo, ys, pcen[1] - pd[2] / 2), Y, Z), nr, 2 * (ys - ypb) - 0.002, 24))
    for (k, ref), d, (ax, az) in q["accs"]:
        cuts.append(RC.tmp_cube((ax, ys - (d[1] + 0.002) / 2 + 0.0005, az), (d[0] + 0.003, d[1] + 0.003, d[2] + 0.003),
                                bevel=0.0008))
    R.cut(ob, cuts)
    # the part in its bag in the pocket
    fr, blo, bhi = place(mid, sp["fwd"], sp["up"], pcen[0], ypb + sp["pad"], pcen[1])
    R.anchor("A_ITEM_PART_0", fr, bsize(mid, sp["pad"] * 0.75), parent=bot, bag=ctx.it.get("bag", "antistatic_silver"),
             label=sp["label"], order=o_part, under=[top])
    # the accessories in their pockets
    ia, ic = 0, 0
    acc_names = []
    for (k, ref), d, (ax, az) in q["accs"]:
        yb = ys - d[1] - 0.002 + 0.0005
        if k == "bracket":
            fra, _, _ = place(ref, BRACKET_POSE[0], BRACKET_POSE[1], ax, yb, az)
            nm = f"A_ITEM_ACC_{ia}"
            R.anchor(nm, fra, bsize(ref, 0.0015), parent=bot, id=ref, bag="clear", frame="model",
                     label="low-profile bracket", order=o_part, under=[top])
            ia += 1
        else:
            w, h, tt = CORD_SIZE[ref]
            nm = f"A_ITEM_CORD_{ic}"
            R.anchor(nm, flat_frame((ax, yb, az)), (w, h, tt), parent=bot, kind=ref, tie="twist",
                     label={"sff8654": "SFF-8654 cable", "12v2x6": "auxiliary power cable"}[ref], order=o_part, under=[top])
            ic += 1
        acc_names.append(nm)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_FOAM_1": (0, 0.10 + sy, 0), "A_ITEM_PART_0": (0, 0.06 + sy * 0.6, 0), "A_INSERT_FOAM_0": (0, 0.0, 0),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    for i, nm in enumerate(acc_names):
        R.explode[nm] = (0.0, 0.05 + sy * 0.4, sz * 0.6 + 0.03 * i)
    explode_docs(R, names, (0.0, 0.16 + sy * 1.2, 0.06), (0.0, 0.02, 0.06))
    R.open_view = (24, 55)
    R.explode_view = (26, 32)
    R.explode_fill = 0.78
    acc_txt = ""
    if acc_names:
        acc_txt = " and " + ", ".join(f"{a} ({k})" for a, ((k, _), _, _) in zip(acc_names, q["accs"]))
    NOTES[pid] = (f"OEM foam carton ({ctx.it['kind']}): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps "
                  f"A_FLAP_2/3 (2) -> {n} papers on the top foam, top first (3..{2 + n}) -> top foam A_INSERT_FOAM_1 ({o_top}) "
                  f"-> {sp['label']} in its bag (bag={ctx.it.get('bag')}){acc_txt} in their pockets ({o_part}) -> bottom foam "
                  f"A_INSERT_FOAM_0 ({o_bot}).")
    return R


# ---------------------------------------------------------------- PSU class: CRPS between EPS end caps

PSU_T = 0.002
PSU_LC = 0.014        # the caps' wall beyond the part's ends
PSU_DP = 0.024        # the caps' pocket depth


def psu_plan(lo, hi):
    d = [hi[i] - lo[i] for i in range(3)]
    return dict(d=d, bag=0.003)


def size_psu(pid, it):
    lo, hi = it["bounds"]
    d = [hi[i] - lo[i] for i in range(3)]
    t = PSU_T
    sx = up5(d[0] + 2 * PSU_LC + 2 * t + 0.002)
    sz = up5(d[2] + 2 * 0.012 + 2 * t + 0.002)
    sy = up5(t + 0.003 + d[1] + 0.003 + 0.006 + 0.004 + t)
    return (sx, sy, sz)


def build_psu(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = PSU_T
    mid = ctx.it.get("model_id", pid)
    lo, hi = PART_BOUNDS[mid]
    rsc_box(R, ctx, t, "cardboard", tape_tag="tape_clear", tape_w=0.048, tape_down=min(0.05, sy * 0.55))
    short = ["A_FLAP_2", "A_FLAP_3"]
    xi = sx / 2 - t - 0.0005
    zi = sz / 2 - t - 0.0005
    ybot = t + 0.003
    # the module lies flat (its own frame = the box axes), centred
    fr, blo, bhi = place(mid, Z, Y, 0.0, ybot, 0.0)
    ytop = bhi[1]
    plist = paper_list(ctx, booklets_last=True, fit=(sx - 0.03, sz - 0.012))
    n = len(plist)
    o_part = 3 + n
    o_caps = o_part + 1
    pocket = ((bhi[2] - blo[2]) + 0.005, (bhi[1] - blo[1]) + 0.005)
    pc = ((blo[2] + bhi[2]) / 2, (blo[1] + bhi[1]) / 2)
    caps = []
    y1 = ytop + 0.002
    for i, (x_wall, inward, xend) in enumerate(((-xi, 1, blo[0]), (xi, -1, bhi[0]))):
        nm = f"A_INSERT_FOAM_{i}"
        Lc = abs(xend - x_wall) + PSU_DP
        R.anchor(nm, F((x_wall, t, 0)), (Lc, y1 - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.06,
                 with_="A_ITEM_PART_0", label="EPS end cap", order=o_caps, under=["A_ITEM_PART_0"])
        RP.eps_cap(R, "cap", nm, x_wall, inward, t + 0.0002, y1, 2 * zi - 0.001, pocket, pc, Lc, PSU_DP, recess=True)
        caps.append(nm)
    R.anchor("A_ITEM_PART_0", fr, bsize(mid, 0.003), bag=ctx.it.get("bag", "antistatic_pink"), label="CRPS power supply",
             order=o_part, under=[f"A_ITEM_DOC_{n - 1}"] if n else short)
    names, _ = pile(R, plist, 0.0, y1 + 0.0003, 0.0, 3, short, step=(0.004, -0.003))
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.12, 0), caps[0]: (-0.07, 0.12, 0), caps[1]: (0.07, 0.12, 0),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    explode_docs(R, names, (0.0, 0.20, sz + 0.06), (0.0, 0.02, 0.07))
    R.open_view = (24, 55)
    R.explode_fill = 0.78
    NOTES[pid] = (f"CRPS PSU: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> {n} papers in a pile, top "
                  f"first (3..{2 + n}) -> the module in its pink bag, lifted out WITH its two EPS end caps ({o_part}) -> caps "
                  f"A_INSERT_FOAM_0/1 pulled off along -x/+x ({o_caps}).")
    return R


# ---------------------------------------------------------------- board class: brown carton, tray, foam pad, compartment

MB_T = 0.002
MB_COMP = 0.014       # the accessory compartment under the tray
MB_DECK = 0.0015
MB_PAD = 0.006


def size_board(pid, it):
    lo, hi = it["bounds"]
    d = [hi[i] - lo[i] for i in range(3)]
    t = MB_T
    sx = up5(d[0] + 0.012 + 2 * t + 0.002)
    sz = up5(d[1] + 0.012 + 2 * t + 0.002)
    sy = up5(t + MB_COMP + MB_DECK + MB_PAD + 0.002 + d[2] + 0.006 + t)
    return (sx, sy, sz)


def build_board(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = MB_T
    mid = ctx.it.get("model_id", pid)
    lo, hi = PART_BOUNDS[mid]
    rsc_box(R, ctx, t, "cardboard", tape_tag="tape_brown", tape_w=0.048, tape_down=min(0.05, sy * 0.6))
    short = ["A_FLAP_2", "A_FLAP_3"]
    y_floor = t + 0.0004
    yd1 = y_floor + MB_COMP + MB_DECK
    tw, tdp = sx - 2 * t - 0.002, sz - 2 * t - 0.002
    # the board: component side up, rear I/O to the back (its local x along the box x, local y to the back)
    fr, blo, bhi = place(mid, Y, NZ, 0.0, yd1 + MB_PAD + 0.0004, 0.0)
    o_part, o_pad, o_tray, o_comp = 3, 4, 5, 6
    tray = R.anchor("A_INSERT_CARD_0", F((0, y_floor, 0)), (tw, yd1 - y_floor, tdp), lift="+y", dist=0.10,
                    label="cardboard tray", order=o_tray, under=["A_INSERT_FOAM_0"])
    holes = [P.stadium(0.014, 0.034, sg * (tw / 2 - 0.016), 0) for sg in (-1, 1)]
    R.slab("tray_deck", P.rrect(tw, tdp, 0.001), MB_DECK, "cardboard", P.plane((0, yd1 - MB_DECK / 2, 0), X, NZ), holes=holes,
           anc=tray)
    for sg in (-1, 1):
        R.cube("tray_leg", (0, y_floor + MB_COMP / 2, sg * (tdp / 2 - MB_DECK / 2)), (tw, MB_COMP, MB_DECK), "cardboard", anc=tray)
        R.cube("tray_leg", (sg * (tw / 2 - MB_DECK / 2), y_floor + MB_COMP / 2, 0), (MB_DECK, MB_COMP, tdp - 2 * MB_DECK),
               "cardboard", anc=tray)
    pw, pdp = (bhi[0] - blo[0]) + 0.004, (bhi[2] - blo[2]) + 0.004
    foam = R.anchor("A_INSERT_FOAM_0", F((0, yd1, 0)), (pw, MB_PAD, pdp), parent=tray, lift="+y", dist=0.06,
                    label="foam pad", order=o_pad, under=["A_ITEM_PART_0"])
    R.cube("pad", (0, yd1 + MB_PAD / 2, 0), (pw, MB_PAD, pdp), "pe_foam", anc=foam, bevel=0.0012)
    R.anchor("A_ITEM_PART_0", fr, bsize(mid, 0.003), parent=foam, bag=ctx.it.get("bag", "antistatic_silver"),
             label="server board", order=o_part, under=short)
    # the compartment under the tray: the I/O shield, a screw bag and the papers
    yc = y_floor + 0.0001
    under_t = [tray]
    spec = ctx.it["part"]["specs"]
    io = spec.get("io_shield")
    xL, xR = -tw / 2 + 0.006, tw / 2 - 0.006
    zB, zF = -tdp / 2 + 0.006, tdp / 2 - 0.006
    if io and not spec.get("io_preattached") and io in PART_BOUNDS:
        ilo, ihi = PART_BOUNDS[io]
        plo, phi = posed(ilo, ihi, X, Z)
        w_io = phi[0] - plo[0]
        fra, _, _ = place(io, X, Z, xR - 0.004 - w_io / 2, yc + 0.0006, 0.0)
        R.anchor("A_ITEM_ACC_0", fra, bsize(io, 0.003), id=io, bag="clear", frame="model", label="I/O shield",
                 order=o_comp, under=under_t)
        xR -= w_io + 0.014
    R.anchor("A_ITEM_HW_0", flat_frame((xR - 0.030, yc, zF - 0.040)), (0.050, 0.070, 0.004), label="M.2 SCREWS",
             order=o_comp, under=under_t)
    # the manual on the floor, the quick-start poster folded on it, the small cards beside them
    plist = paper_list(ctx)
    k_man = next((i for i, p_ in enumerate(plist) if p_[1] == "booklet"), None)
    k_big = next((i for i, p_ in enumerate(plist) if p_[1] == "leaflet"), None)
    small = [i for i in range(len(plist)) if i not in (k_man, k_big)]
    xb = xL + 0.110
    for i, (k, form, size, lab) in enumerate(plist):
        if i == k_man:
            doc(R, i, flat_frame((xb, yc, -0.02)), (0.148, 0.210, 0.0035), k, "booklet", o_comp + (1 if k_big is not None else 0),
                under=[f"A_ITEM_DOC_{k_big}"] if k_big is not None else under_t, label=lab)
        elif i == k_big:
            doc(R, i, flat_frame((xb + 0.004, yc + (0.0037 if k_man is not None else 0.0), -0.024)), (0.140, 0.200, 0.0016), k,
                "leaflet", o_comp, under=under_t, label="quick start poster")
        else:
            j = small.index(i)
            doc(R, i, flat_frame((xR - 0.050, yc, zB + 0.045 + j * 0.07)), (0.090, 0.060, size[2]), k, form, o_comp,
                under=under_t, label=lab)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.16, 0), "A_INSERT_FOAM_0": (0, 0.09, 0), "A_INSERT_CARD_0": (0, 0.05, 0),
                 "A_ITEM_ACC_0": (0.06, 0.0, sz * 0.75), "A_ITEM_HW_0": (0.16, 0.0, sz * 0.70),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    explode_docs(R, [f"A_ITEM_DOC_{i}" for i in range(len(plist))], (-0.12, 0.0, sz * 0.8), (0.07, 0.003, 0.03))
    R.explode_fill = 0.72
    R.open_view = (18, 55)
    R.explode_view = (24, 32)
    NOTES[pid] = (f"Server board: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> board in its silver bag "
                  f"({o_part}, on the pad) -> PE foam pad A_INSERT_FOAM_0 ({o_pad}) -> cardboard tray A_INSERT_CARD_0 ({o_tray}) "
                  f"-> compartment: I/O shield A_ITEM_ACC_0, screw bag A_ITEM_HW_0, quick-start poster and warranty card "
                  f"({o_comp}) -> manual under the poster ({o_comp + 1}).")
    return R


# ---------------------------------------------------------------- registry

BUILDERS = {"oem_cpu": build_cpu, "oem_rdimm": build_rdimm, "oem_u2": build_sandwich, "oem_heatsink": build_sandwich,
            "oem_card": build_sandwich, "oem_psu": build_psu, "oem_board": build_board}
SIZE = {"oem_cpu": size_cpu, "oem_rdimm": size_rdimm, "oem_u2": size_sandwich, "oem_heatsink": size_sandwich,
        "oem_card": size_sandwich, "oem_psu": size_psu, "oem_board": size_board}
ART = {k: oem_art for k in BUILDERS}
