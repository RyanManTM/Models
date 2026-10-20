"""
rig_new: the packaging rigs of the new consumer box kinds (catalogue 19, docs/tasks/catalog/19-boxes.md). Called by
build_boxes.py (RIG_MODULES); built like rig_products.py and reusing its helpers.

  * aio       AIO liquid coolers: a taped printed carton, the whole cooler (pump, tubes, radiator with its fans) in a
              moulded pulp tray under a card cover, the mounting kit in an accessory box in the tray's compartment.
  * hdd       3.5" desktop drives: a printed tuck-top box, the drive in an anti-static bag in a moulded pulp tray,
              the screw bag in the tray's second pocket, the papers on top.
  * hdd_bulk  enterprise 3.5" drives: a brown bulk carton with a printed label, the drive in an anti-static bag
              held by two black PE foam end caps.
  * fan_pack  case fans: a printed window box (a clear PET window over the front fan), the fans standing in a die-cut
              card tray, the accessories (screws, adapters, the RGB hub or controller) and papers behind it.
  * psu_sfx   SFX PSUs: the ATX PSU rig (taped printed carton, EPS saddle caps, fabric bag, cable pouch) plus the
              SFX-to-ATX bracket (A_ITEM_ACC, id=psu_bracket_sfx_atx, frame=model) standing in the end compartment.

Conventions as in rig_products (the box frame: origin at the bottom centre, +z the front, y up, closed pose).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_c as P  # noqa: E402
import rig_common as RC  # noqa: E402
import rig_products as RP  # noqa: E402
from rig_common import F, Rig, X, Y, Z, NX, NY, NZ, rr  # noqa: E402
from rig_products import (PART_BOUNDS, bsize, doc, flat_frame, paper_list, pile, floor_papers, explode_docs,  # noqa: E402
                          seal_round, seal_rect_flat, tuck_walls, tuck_lid_top, dust_flaps, rsc_box, accessory_box,
                          formed, blister, eps_cap, sub_uv)

DEG = math.pi / 180.0
NOTES = {}


def up5(x, step=0.005):
    return round(math.ceil(x / step - 1e-6) * step, 3)


def dims(it):
    lo, hi = it["bounds"]
    return [hi[i] - lo[i] for i in range(3)]


def cap_text(gb):
    return f"{gb // 1000} TB" if gb >= 1000 and gb % 1000 == 0 else f"{gb / 1000:g} TB" if gb >= 1000 else f"{gb} GB"


# ---------------------------------------------------------------- catalogue items: the words on the box

def item(pid, it):
    p = it["part"]
    s, g = p["specs"], p["game"]
    kind = it["kind"]
    if kind in ("hdd", "hdd_bulk"):
        cap = cap_text(g["storage_gb"])
        it["model"] = it["name"].upper()
        it["line"] = ("ENTERPRISE HARD DRIVE" if kind == "hdd_bulk" else
                      "NAS HARD DRIVE" if s.get("workload_tby") else '3.5" DESKTOP HARD DRIVE')
        it["specs"] = [f"{cap} capacity", f"{s['rpm']} RPM, {s['cache_mb']} MB cache", f"Up to {s['read_mbs']} MB/s",
                       f"{s['form']} {s['interface']}", f"{s['recording']} recording" + (", helium sealed" if s.get("helium") else "")]
        if s.get("workload_tby"):
            specs = it["specs"]
            specs.append(f"{s['workload_tby']} TB/year workload")
        it["badges"] = [cap, f"{s['rpm']} RPM"] + (["NAS"] if s.get("workload_tby") and kind == "hdd" else [])
        it["pose"] = ((0, 1, 0), (0, 0, 1), (20, 28))      # label up, seen from above
        if kind == "hdd_bulk":
            it["style"] = "oem"
            it["oem_base"] = "kraft"
    elif kind == "fan_pack":
        n = g.get("per_box", 1)
        it["model"] = it["name"].upper()
        it["line"] = (f"{s['size_mm']} MM {'ARGB ' if s.get('argb') else ''}CASE FAN" + (f" {n}-PACK" if n > 1 else "")).upper()
        it["specs"] = [f"{s['size_mm']} x {s['size_mm']} x {s['depth_mm']} mm", f"Up to {s['rpm_max']} RPM",
                       f"{s['airflow_cfm']:g} CFM airflow", f"{s['static_pressure_mmh2o']:g} mmH2O static pressure",
                       f"{s['noise_dba']:g} dB(A)", s["connector"]]
        it["badges"] = ([f"{n} FANS"] if n > 1 else []) + [f"{s['size_mm']} MM"] + (["ARGB"] if s.get("argb") else ["PWM"])
        it["pose"] = ((0, 0, -1), (0, 1, 0), (-22, 14))   # the intake face (hub sticker) toward the camera
    elif kind == "aio":
        it["model"] = it["name"].upper()
        it["line"] = f"{s['radiator_mm']} MM LIQUID CPU COOLER"
        it["specs"] = [f"{s['radiator_mm']} mm radiator, {s['radiator_thickness_mm']} mm thick",
                       f"{s['fans']} x {s['fan_mm']} mm PWM fans", f"Up to {g['cooler_max_w']} W TDP",
                       f"{s['tube_mm']} mm sleeved tubes", "Socket V5 / L17"]
        if s.get("lcd"):
            it["specs"].append(f"{s['lcd']} pump LCD")
        elif p.get("rgb"):
            it["specs"].append("ARGB pump and fans")
        it["badges"] = [f"{s['radiator_mm']} MM", f"{g['cooler_max_w']} W"] + (["LCD"] if s.get("lcd") else ["ARGB"] if p.get("rgb") else [])
        it["pose"] = ((0, 1, 0), (0, 0, 1), (24, 30))      # lying as shipped, seen from above the fans
    elif kind == "psu_sfx":
        it["model"] = it["name"].upper()
        it["line"] = "SFX POWER SUPPLY"
        mod = {"none": "Non-modular cables", "semi": "Semi-modular cables", "full": "Fully modular"}[s["modular"]]
        it["specs"] = [s["efficiency"], mod, f"{s['fan_mm']} mm fan", f"{s['eps8']} x CPU 8-pin, {s['pcie8']} x PCIe 8-pin",
                       f"SFX, {s['width_mm']:g} x {s['height_mm']:g} x {s['depth_mm']:g} mm", "SFX-to-ATX bracket included"]
        it["badges"] = [f"{g['psu_watts']} W", s["efficiency"].upper().replace("80 PLUS ", "80+ "), "SFX"]
        it["acc_models"] = [s.get("bracket", "psu_bracket_sfx_atx")]


# ---------------------------------------------------------------- sizes

def size_psu_sfx(pid, it):
    d = dims(it)              # x the depth (rear +x), y the height (fan -y), z the width
    blo, bhi = PART_BOUNDS[it["part"]["specs"].get("bracket", "psu_bracket_sfx_atx")]
    return (up5(d[0] + 0.094), up5(max(bhi[1] - blo[1] + 0.012, d[1] + 0.034)), up5(max(bhi[2] - blo[2] + 0.016, d[2] + 0.04)))


def size_hdd_bulk(pid, it):
    d = dims(it)              # the drive lying flat between two foam end caps
    return (up5(d[0] + 0.064), up5(d[1] + 0.032), up5(d[2] + 0.030))


def size_hdd(pid, it):
    d = dims(it)              # x 0.147 long, y 0.026 high (label up), z 0.1017 wide
    return (up5(d[0] + 0.068), up5(d[1] + 0.022), up5(d[2] + 0.026))


SIZE = {"hdd": size_hdd, "hdd_bulk": size_hdd_bulk, "psu_sfx": size_psu_sfx}


# ---------------------------------------------------------------- shared pieces

def pockets(R, name, frame, flange, cavities, t, tag, anc, lip=0.0015, n=112):
    """A moulded sheet (pulp, plastic): a flat flange outline (the frame's XY at z=0) with pockets of their own depth,
    cavities = [(outline, profile)], profile = [(inset, z), ...] down from the flange (the last ring is the floor)."""
    R.slab(name + "_flange", flange, t, tag, frame.sub(0, 0, -t / 2), holes=[cv for cv, _ in cavities], anc=anc)
    if lip > 0:
        lp = RC.resample(flange, n)
        R.shell(name + "_lip", [(lp, -lip), (lp, 0.0), (RC.resample(P.poly_offset(flange, -0.001), n), 0.0)], t, tag, frame,
                anc=anc, cap=False, ref=1, up=1)
    for cav, profile in cavities:
        rings = [(RC.resample(P.poly_offset(cav, -inset) if inset else cav, n), z) for inset, z in profile]
        R.shell(name, rings, t, tag, frame, anc=anc, ref=len(rings) - 2, up=1, smooth=35)


# ---------------------------------------------------------------- 3.5" HDD, retail: tuck-top box, pulp tray

def build_hdd(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.0008
    inner = "paper_white"
    lo, hi = PART_BOUNDS[pid]
    H = tuck_walls(R, ctx, t, inner, notch_r=0.010)
    for i, xs in enumerate((-sx * 0.28, sx * 0.28)):
        seal_round(R, f"A_SEAL_{i}", xs, sy, sz / 2, 0.018, 0.006, text=ctx.it["brand"] + " SEALED")
    tuck_lid_top(R, ctx, t, inner, open_deg=-115, under=["A_SEAL_0", "A_SEAL_1"])
    flaps = dust_flaps(R, ctx, t, inner, H, min(0.03, sx * 0.14))
    opened = ["A_FLAP_0"] + flaps
    # the moulded pulp tray: a flange round the top, the drive's pocket at -x, the screw bag's pocket at +x
    xi, zi = sx / 2 - t - 0.0006, sz / 2 - t - 0.0006
    dw, dd = (hi[0] - lo[0]) + 0.006, (hi[2] - lo[2]) + 0.006      # the drive in its bag
    dh = hi[1] - lo[1]
    yb = t + 0.0002                         # tray bottom
    depth = dh + 0.0035                     # pocket depth: the drive's height, its bag and the floor
    yfl = yb + depth                        # the flange's top
    xd = -xi + 0.007 + dw / 2               # the drive pocket's centre
    hw_w = 2 * xi - dw - 0.021
    xh = xi - 0.007 - hw_w / 2
    plist = paper_list(ctx, sizes={"guide": (0.130, 0.090, 0.0012), "warranty": (0.090, 0.058, 0.0004)},
                       fit=(2 * xi - 0.01, 2 * zi - 0.01))
    n = len(plist)
    tp = 0.0015
    names, o_part, ph = floor_papers(R, plist, 0.0, yfl + tp + 0.0002, 0.0, 2 * xi - 0.008, 2 * zi - 0.008, 3, opened)
    tray = R.anchor("A_INSERT_PULP_0", F((0, yb, 0)), (2 * xi, depth + 0.002, 2 * zi), lift="+y", dist=0.06,
                    label="pulp tray", order=o_part + 1, under=["A_ITEM_PART_0", "A_ITEM_HW_0"])
    fr = F((0, yfl, 0), Y, NZ)              # local x = box x, local y = -box z, local z up
    flange = P.rrect(2 * xi - 0.001, 2 * zi - 0.001, 0.004, 0, 0, 6)
    cav_d = P.rrect(dw, dd, 0.006, xd, 0, 6)
    cav_h = P.rrect(hw_w, min(0.072, dd), 0.006, xh, 0, 6)
    pockets(R, "tray", fr, flange, [(cav_d, [(0.0, 0.0), (0.0015, -(depth - 0.004)), (0.004, -depth)]),
                                    (cav_h, [(0.0, 0.0), (0.0015, -0.006), (0.004, -0.009)])], tp, "pulp", tray, lip=0.003)
    # finger scoops on both long sides of the drive pocket
    for sg in (-1, 1):
        R.shell("tray_scoop", [(rr(0.030, 0.014, 0.006, xd, sg * (dd / 2 + 0.004), 40), 0.0),
                               (rr(0.027, 0.011, 0.005, xd, sg * (dd / 2 + 0.004), 40), -depth + 0.006),
                               (rr(0.022, 0.007, 0.0034, xd, sg * (dd / 2 + 0.004), 40), -depth + 0.004)], tp,
                "pulp", fr, anc=tray, ref=1, up=1)
    # the papers lie on the tray; then the drive (label up, connectors to -x) and the screw bag; then the tray
    below = names[-1:] if names else opened
    if len(names) > 1 and R.meta[names[0]]["order"] == R.meta[names[-1]]["order"]:
        below = names                      # side by side: both papers cover the tray
    R.anchor("A_ITEM_PART_0", F((xd, yfl - depth + 0.0012 - lo[1], 0.0), Z, Y), bsize(pid, 0.003), parent=tray,
             bag="antistatic_silver", label='3.5" hard drive', order=o_part, under=below)
    R.anchor("A_ITEM_HW_0", flat_frame((xh, yfl - 0.009 + 0.0012, 0.0)), (hw_w - 0.008, min(0.064, dd - 0.008), 0.005),
             parent=tray, label="4 x 6-32 SCREWS", order=o_part, under=below)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_INSERT_PULP_0": (0, 0.05, 0.10), "A_ITEM_PART_0": (0, 0.06, 0.0), "A_ITEM_HW_0": (0.10, 0.07, 0.02),
                 "A_SEAL_0": (-0.02, 0.03, 0.06), "A_SEAL_1": (0.02, 0.03, 0.06)}
    explode_docs(R, names, (-0.05, 0.13, 0.17), (0.12, 0.01, 0.02))
    R.open_view = (24, 55)
    R.explode_view = (24, 34)
    R.explode_fill = 0.8
    NOTES[pid] = (f'3.5" HDD (retail): two round seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) '
                  f"-> {n} papers lying on the tray (3{'..' + str(2 + n) if n > 1 and len(set(R.meta[x]['order'] for x in names)) > 1 else ''}) "
                  f"-> the drive A_ITEM_PART_0 in its silver anti-static bag and the screw bag A_ITEM_HW_0 ({o_part}) -> the "
                  f"moulded pulp tray A_INSERT_PULP_0 ({o_part + 1}).")
    return R


# ---------------------------------------------------------------- 3.5" HDD, enterprise bulk: brown carton, PE foam end caps

def pe_cap(R, name, anc, x_wall, inward, y0, y1, zw, Lc, pocket, pocket_c, Dp):
    """A black PE foam end cap against the wall at x_wall: a block with a pocket (z, y size, centre) Dp deep for the
    drive's end, and a finger slot at its top."""
    xc = x_wall + inward * Lc / 2
    ob = R.cube(name, (xc, (y0 + y1) / 2, 0), (Lc, y1 - y0, zw), "pe_foam", anc=anc, bevel=0.002)
    pz, py = pocket
    cuts = [RC.tmp_cube((x_wall + inward * (Lc - Dp / 2 + 0.002), pocket_c[1], pocket_c[0]), (Dp + 0.004, py, pz), bevel=0.001),
            RC.tmp_cube((x_wall + inward * (Lc * 0.4), y1, 0.0), (Lc * 0.35, 0.012, zw * 0.45), bevel=0.003)]
    R.cut(ob, cuts)
    return ob


def build_hdd_bulk(ctx):
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.003
    inner = "cardboard"
    rsc_box(R, ctx, t, inner, tape_tag="tape_brown", tape_w=0.048, tape_down=0.04)
    short = ["A_FLAP_2", "A_FLAP_3"]
    lo, hi = PART_BOUNDS[pid]
    xi, zi = sx / 2 - t - 0.0005, sz / 2 - t - 0.0005
    y_in = sy - 2 * t
    dh = hi[1] - lo[1]
    yb = t + (y_in - t - dh) / 2                 # the drive floats in the middle of the caps
    ay = yb - lo[1]
    pocket = ((hi[2] - lo[2]) + 0.004, dh + 0.004)
    pc = (0.0, yb + dh / 2)
    Dp = 0.020
    plist = paper_list(ctx, sizes={"guide": (0.120, 0.085, 0.0012), "warranty": (0.090, 0.058, 0.0004)},
                       fit=(2 * xi - 0.01, 2 * zi - 0.01))
    n = len(plist)
    ytop = y_in + 0.0002 - sum(p_[2][2] + 0.0002 for p_ in plist)   # the papers lie on the caps' tops
    names, h = pile(R, plist, 0.0, ytop, 0.0, 3, short, step=(0.004, -0.004))
    o_part = 3 + n
    caps = []
    for i, inward in enumerate((1, -1)):
        x_wall = -xi * inward
        Lc = (xi - (hi[0] - lo[0]) / 2) + Dp
        nm = f"A_INSERT_FOAM_{i}"
        R.anchor(nm, F((x_wall, t, 0)), (Lc, ytop - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.05,
                 with_="A_ITEM_PART_0", label="foam end cap", order=o_part + 1, under=["A_ITEM_PART_0"])
        pe_cap(R, "cap", nm, x_wall, inward, t + 0.0002, ytop - 0.0002, 2 * zi - 0.001, Lc, pocket, pc, Dp)
        caps.append(nm)
    R.anchor("A_ITEM_PART_0", F((0.0, ay, 0.0), Z, Y), bsize(pid, 0.002), bag="antistatic_silver", label='3.5" hard drive',
             order=o_part, under=names[-1:] or short)
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0, 0.10, 0), caps[0]: (-0.06, 0.10, 0), caps[1]: (0.06, 0.10, 0),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    explode_docs(R, names, (0.0, 0.20, 0.10), (0.03, 0.02, 0.08))
    R.open_view = (22, 55)
    R.explode_fill = 0.78
    NOTES[pid] = (f'3.5" HDD (bulk): tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) '
                  f"-> {n} papers in a pile on the caps (3..{2 + n}) -> the drive in its silver anti-static bag A_ITEM_PART_0, "
                  f"lifted out WITH its two black PE foam end caps ({o_part}) -> caps A_INSERT_FOAM_0/1 pulled off along "
                  f"-x/+x ({o_part + 1}).")
    return R


# ---------------------------------------------------------------- SFX PSU: the ATX PSU rig plus the SFX-to-ATX bracket

def build_psu_sfx(ctx):
    """The fully modular ATX PSU rig (rig_products.build_psu) at SFX size: a taped printed carton, the unit fan up in
    its fabric bag between two EPS saddle caps, the cable pouch on it and the papers on the pouch; the +x end
    compartment holds the power cord, the screw bag and the SFX-to-ATX bracket standing in its clear bag."""
    pid = ctx.pid
    sx, sy, sz = ctx.s
    R = Rig("box_" + pid)
    t = 0.002
    inner = "cardboard"
    rsc_box(R, ctx, t, inner, tape_tag="tape_clear")
    short = ["A_FLAP_2", "A_FLAP_3"]
    spec = ctx.it["part"]["specs"]
    lo, hi = PART_BOUNDS[pid]
    bid = spec.get("bracket", "psu_bracket_sfx_atx")
    blo, bhi = PART_BOUNDS[bid]
    x0 = lo[0]                                 # the modular panel (-x)
    x1 = x0 + spec["depth_mm"] / 1000.0        # the rear face (+x); the switch stands past it
    width = hi[2] - lo[2]
    xi = sx / 2 - t - 0.0005
    zi = sz / 2 - t - 0.0005
    ybot = t + 0.003
    ay = ybot + hi[1]                          # fan up: local -y points up
    ax = -xi + 0.016 - x0
    body_x0, body_x1 = ax + x0, ax + x1
    ytop = ay - lo[1]
    pocket = (width + 0.004, (hi[1] - lo[1]) + 0.004)
    pc = (0.0, (ybot + ytop) / 2)
    Dp = 0.022
    plist = paper_list(ctx, booklets_last=True, fit=(0.105, 0.148))
    npap = len(plist)
    o_pouch = 3 + npap
    o_part = o_pouch + 1
    o_caps = o_part + 1
    caps = []
    xw1 = body_x1 + 0.012                      # the +x cap stands off the unit's rear: the switch sits in its pocket
    for i, (x_wall, inward, xend) in enumerate(((-xi, 1, body_x0), (xw1, -1, body_x1))):
        nm = f"A_INSERT_FOAM_{i}"
        Lc = abs(xend - x_wall) + Dp
        y1 = ytop + 0.0005
        R.anchor(nm, F((x_wall, t, 0)), (Lc, y1 - t, 2 * zi), lift=("-x" if inward > 0 else "+x"), dist=0.06,
                 with_="A_ITEM_PART_0", label="EPS end cap", order=o_caps, under=["A_ITEM_PART_0"])
        eps_cap(R, "cap", nm, x_wall, inward, t + 0.0002, y1, 2 * zi - 0.001, pocket, pc, Lc, Dp, recess=(i == 0))
        caps.append(nm)
    R.anchor("A_ITEM_PART_0", F((ax, ay, 0.0), NZ, NY), bsize(pid, 0.003), bag="fabric", label="SFX power supply",
             order=o_part, under=["A_ITEM_POUCH_0"])
    yp = ytop + 0.0008
    pw = min(0.150, (xw1 + 0.001) - (-xi + 0.002))
    px = (-xi + 0.002 + xw1 + 0.001) / 2
    R.anchor("A_ITEM_POUCH_0", flat_frame((px, yp, 0.0)), (pw, min(0.130, 2 * zi - 0.01), 0.017), label="modular cable pouch",
             order=o_pouch, under=[f"A_ITEM_DOC_{npap - 1}"] if npap else short)
    # the end compartment: the cord coil and the screw bag standing against the cap, the bracket against the end wall
    yf = t + 0.0005
    xc = xw1 + 0.0015
    R.anchor("A_ITEM_CORD_0", F((xc, yf + 0.045, 0.0), X, Y), (0.120, 0.090, 0.016), kind="c13", tie="twist",
             label="power cord", order=3, under=short)
    R.anchor("A_ITEM_HW_0", F((xc + 0.017, yf + 0.035, -0.035), X, Y), (0.050, 0.070, 0.005),
             label="4 x 6-32 SCREWS", order=3, under=short)
    bx = xi - 0.0035 - bhi[0]
    R.anchor("A_ITEM_ACC_0", F((bx, yf + 0.002 - blo[1], 0.0), Z, Y), tuple(bhi[k] - blo[k] + 0.004 for k in range(3)),
             id=bid, bag="clear", frame="model", label="SFX-to-ATX bracket", order=3, under=short)
    yd = yp + 0.0172
    names, _ = pile(R, plist, px, yd, 0.0, 3, short, step=(0.003, -0.003))
    R.anchor("A_HIT_0", F((0, sy / 2, 0)), (sx, sy, sz))
    R.explode = {"A_ITEM_PART_0": (0.0, 0.12, 0), "A_ITEM_CORD_0": (0.10, 0.13, -0.10), "A_ITEM_HW_0": (0.14, 0.13, -0.02),
                 "A_ITEM_ACC_0": (0.15, 0.06, 0.06), "A_ITEM_POUCH_0": (-0.05, 0.20, -0.07),
                 caps[0]: (-0.07, 0.12, 0), caps[1]: (0.06, 0.12, 0),
                 "A_TAPE_0": (-0.03, 0.02, 0), "A_TAPE_1": (0, 0.03, 0), "A_TAPE_2": (0.03, 0.02, 0)}
    explode_docs(R, names, (-0.02, 0.24, 0.08), (0.0, 0.015, 0.07))
    R.open_view = (22, 55)
    R.explode_view = (28, 30)
    R.explode_fill = 0.85
    NOTES[pid] = (f"SFX PSU (fully modular): tape strip 0 (A_TAPE_0..2) (0) -> long flaps (1) -> short flaps (2) -> {npap} papers "
                  f"in a pile on the pouch (3..{2 + npap}), with the power cord A_ITEM_CORD_0, the screw bag A_ITEM_HW_0 and the "
                  f"SFX-to-ATX bracket A_ITEM_ACC_0 (id={bid}, frame=model, clear bag) standing in the +x compartment (3) -> "
                  f"cable pouch A_ITEM_POUCH_0 ({o_pouch}) -> the unit in its fabric bag, lifted out WITH its two EPS saddle "
                  f"caps ({o_part}) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x ({o_caps}).")
    return R


BUILDERS = {"hdd": build_hdd, "hdd_bulk": build_hdd_bulk, "psu_sfx": build_psu_sfx}
